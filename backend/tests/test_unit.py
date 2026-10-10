from datetime import timedelta
from pathlib import Path
import json
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

import sqlalchemy as sa
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic.script import ScriptDirectory
from backend.infrastructure.database import DatabaseConfig, create_engine, check_connection, DatabaseUnavailable
from backend.infrastructure.uow import UnitOfWork
from backend.infrastructure.repositories import Repository
from backend.infrastructure.collector import delete_collected, ProtectedDeletion
from backend.infrastructure.locks import OrderedLocks, LockOrderViolation
from backend.models.baseline import metadata, SNAPSHOT, Grade, ContentPage, StudentProfile, User, utc_now
import backend.models.protocol
from backend.migrations.upgrade import fresh, upgrade_profile
from backend.migrations.schema import SchemaMismatch


class UnitTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(DatabaseConfig(URL.create('sqlite+pysqlite', database=':memory:'), True))
        with self.engine.begin() as connection:
            fresh(connection)

    def tearDown(self):
        self.engine.dispose()

    def test_single_chain(self):
        config = Config('backend/alembic.ini')
        script = ScriptDirectory.from_config(config)
        self.assertEqual(script.get_heads(), ['v01_0002'])
        self.assertEqual([x.revision for x in script.walk_revisions()], ['v01_0002','v01_0001'])

    def test_snapshot_exact_frozen_copy_and_field_mapping(self):
        source = Path('specs/migration/r02-v1/schema-mapping-v1.json').read_bytes()
        self.assertEqual(source, Path('backend/models/baseline-v1.json').read_bytes())
        for model in SNAPSHOT['models']:
            table = metadata.tables[model['table']]
            self.assertEqual(set(table.c.keys()), {f['column'] for f in model['fields']})
            for f in model['fields']:
                self.assertEqual(table.c[f['column']].nullable, f['null'])
                self.assertIsNone(table.c[f['column']].server_default if not f['primary_key'] else None)

    def test_b01_addendum_changes_only_three_pk_types(self):
        from sqlalchemy.dialects.postgresql import dialect
        from backend.models.baseline import COMPATIBILITY, sql_type
        self.assertEqual(COMPATIBILITY['source_sha'], '8d958aeeb17da46839722441425ccbb5889e2ab7')
        allowed = {'auth_group_permissions', 'auth_user_groups', 'auth_user_user_permissions'}
        changes = set()
        for model in SNAPSHOT['models']:
            for field in model['fields']:
                compiled = str(sql_type(field, model['table']).compile(dialect=dialect())).lower()
                expected = field['db_type'].replace('timestamp with time zone', 'timestamp(6) with time zone')
                if compiled != expected:
                    changes.add((model['table'], field['column'], compiled))
        self.assertEqual(changes, {(name, 'id', 'bigint') for name in allowed})
        for name in allowed:
            table = metadata.tables[name]
            self.assertEqual(str(table.c.id.type.compile(dialect=dialect())), 'BIGINT')
            for column in table.c:
                if column.name.endswith('_id'):
                    self.assertEqual(str(column.type.compile(dialect=dialect())), 'INTEGER')

    def test_no_django_import_in_target_fresh(self):
        script = "import sys; from sqlalchemy.engine import URL; from backend.infrastructure.database import *; from backend.migrations.upgrade import fresh; e=create_engine(DatabaseConfig(URL.create('sqlite+pysqlite',database=':memory:'),True)); c=e.connect(); fresh(c); assert not any(m=='django' or m.startswith('django.') for m in sys.modules)"
        self.assertEqual(subprocess.run([sys.executable, '-c', script], capture_output=True).returncode, 0)

    def test_uow_commit_rollback_and_savepoints(self):
        with UnitOfWork(self.engine) as uow:
            uow.repository(Grade).add(Grade(title='Synthetic', slug='g'))
        with Session(self.engine) as s:
            self.assertEqual(s.scalar(sa.select(sa.func.count()).select_from(Grade)), 0)
        with UnitOfWork(self.engine) as uow:
            repo = uow.repository(Grade)
            repo.add(Grade(title='Synthetic', slug='g'))
            uow.session.flush()
            with self.assertRaises(sa.exc.IntegrityError):
                with uow.session.begin_nested():
                    repo.add(Grade(title='Duplicate', slug='g'))
                    uow.session.flush()
            uow.commit()
        with Session(self.engine) as s:
            self.assertEqual(s.scalar(sa.select(sa.func.count()).select_from(Grade)), 1)

    def test_defaults_and_explicit_timestamps(self):
        old = utc_now() - timedelta(days=2)
        with UnitOfWork(self.engine) as uow:
            repo = uow.repository(ContentPage)
            page = ContentPage(title='Synthetic', slug='p', updated_at=old)
            repo.add(page)
            uow.session.flush()
            self.assertEqual(page.page_type, 'topic')
            self.assertEqual(page.body_html, '')
            self.assertEqual(page.order, 0)
            self.assertGreater(page.updated_at.replace(tzinfo=old.tzinfo), old)
            # QuerySet.update/Core import deliberately preserves explicit dates.
            repo.bulk_update([page.id], {'updated_at': old})
            uow.session.refresh(page)
            page.title = 'Saved'
            page.body_html = 'Excluded dirty value'
            repo.save(page, fields={'title'})
            self.assertEqual(page.body_html, '')
            self.assertEqual(page.updated_at.replace(tzinfo=old.tzinfo), old)
            repo.bulk_update([page.id], {'title':'Bulk'})
            uow.session.refresh(page)
            self.assertEqual(page.updated_at.replace(tzinfo=old.tzinfo), old)
            repo.save(page, fields={'updated_at'})
            self.assertGreater(page.updated_at.replace(tzinfo=old.tzinfo), old)
            uow.commit()

    def test_protect_preflights_whole_bulk(self):
        with UnitOfWork(self.engine) as uow:
            a,b = User(username='a'),User(username='b')
            uow.session.add_all([a,b]); uow.session.flush()
            uow.session.add(StudentProfile(user_id=b.id)); uow.session.flush()
            with self.assertRaises(ProtectedDeletion):
                delete_collected(uow.session,'auth_user',[a.id,b.id])
            self.assertIsNotNone(uow.session.get(User,a.id))
            self.assertIsNotNone(uow.session.get(User,b.id))

    def test_collector_cascade_setnull(self):
        from backend.models.baseline import Subject, Section, LessonPublication, MediaAsset
        with UnitOfWork(self.engine) as uow:
            g=Grade(title='G',slug='g'); uow.session.add(g); uow.session.flush()
            subject=Subject(title='S',slug='s',grade_id=g.id); uow.session.add(subject); uow.session.flush()
            section=Section(title='C',slug='c',subject_id=subject.id); uow.session.add(section); uow.session.flush()
            page=ContentPage(title='P',slug='p',grade_id=g.id,subject_id=subject.id,section_id=section.id)
            uow.session.add(page); uow.session.flush()
            uow.session.add_all([LessonPublication(page_id=page.id,source_path='synthetic',published_digest='0'*64),MediaAsset(file='synthetic.png',related_page_id=page.id)])
            uow.session.flush()
            delete_collected(uow.session,'content_grade',[g.id])
            uow.session.expire_all()
            self.assertIsNone(page.grade_id); self.assertIsNone(page.subject_id); self.assertIsNone(page.section_id)
            delete_collected(uow.session,'content_contentpage',[page.id])
            uow.session.expire_all()
            self.assertEqual(uow.session.scalar(sa.select(sa.func.count()).select_from(LessonPublication)),0)
            self.assertIsNone(uow.session.scalar(sa.select(MediaAsset)).related_page_id)
            uow.commit()

    def test_sqlite_explicit_no_postgres_fallback(self):
        with patch.dict(os.environ, {'MATHSTART_DB_BACKEND':'postgresql','MATHSTART_DATABASE_URL':'sqlite:///should-not-exist.sqlite'}, clear=True):
            with self.assertRaises(ValueError): DatabaseConfig.from_environment()
        with self.assertRaises(ValueError): create_engine(DatabaseConfig(URL.create('sqlite',database=':memory:')))
        engine=create_engine(DatabaseConfig(URL.create('postgresql+psycopg',username='synthetic',host='127.0.0.1',port=1,database='synthetic')))
        try:
            with self.assertRaises(DatabaseUnavailable) as error: check_connection(engine)
            self.assertNotIn('synthetic',str(error.exception))
            self.assertEqual(engine.dialect.name,'postgresql')
        finally: engine.dispose()
        with self.engine.begin() as c:
            with self.assertRaises(SchemaMismatch): upgrade_profile(c,'B',reviewed=True)

    def test_lock_order_and_sqlite_not_lock_proof(self):
        with Session(self.engine) as s:
            locks=OrderedLocks(s)
            locks._advance((6,0,(1,)))
            with self.assertRaises(LockOrderViolation): locks._advance((3,0,(2,)))
            with self.assertRaises(RuntimeError): OrderedLocks(s).rows(metadata.tables['auth_user'],[1])

    def test_unique_check_fk_and_nullability(self):
        with self.engine.begin() as c:
            g=metadata.tables['content_grade']
            c.execute(sa.insert(g).values(title='G',slug='g'))
            for statement in [sa.insert(g).values(title='Duplicate',slug='g'),
                              sa.insert(g).values(title='Bad',slug='bad',order=-1),
                              sa.insert(g).values(title=None,slug='null')]:
                with self.assertRaises(sa.exc.IntegrityError):
                    with c.begin_nested(): c.execute(statement)
        # The preserved Django FK is DEFERRABLE INITIALLY DEFERRED: failure is
        # checked at transaction completion, not at the inner savepoint.
        with self.assertRaises(sa.exc.IntegrityError):
            with self.engine.begin() as c:
                c.execute(sa.insert(metadata.tables['content_subject']).values(title='S',slug='s',grade_id=999))


if __name__ == '__main__': unittest.main()
