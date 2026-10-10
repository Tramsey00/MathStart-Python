"""Real migrations against newly created, marked disposable PostgreSQL DBs.

No tests attach to an existing database. Only databases created by this process
are cleaned up. Administration URL must refer to the reserved local container.
"""
from contextlib import contextmanager
from datetime import timedelta
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import uuid

import sqlalchemy as sa
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.infrastructure.collector import delete_collected, ProtectedDeletion
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import metadata, SNAPSHOT, GRADE_EPOCH, utc_now, User, Grade, StudentProfile
from backend.migrations.upgrade import fresh, upgrade_profile, backfill, advance_sequences, HEAD
from backend.migrations.schema import inventory, assert_baseline, SchemaMismatch

ADMIN_URL = os.environ.get('MATHSTART_V01_TEST_ADMIN_URL')


def data_digest(connection, *, omit_grade_time=False):
    result = {}
    present = set(sa.inspect(connection).get_table_names())
    for model in SNAPSHOT['models']:
        name = model['table']
        if name not in present:
            continue
        table = metadata.tables[name]
        columns = [c for c in table.c if not (omit_grade_time and name == 'content_grade' and c.name == 'created_at')]
        rows = [tuple(row) for row in connection.execute(sa.select(*columns).order_by(*table.primary_key.columns))]
        result[name] = sha256(json.dumps(rows,default=str,separators=(',',':')).encode()).hexdigest()
    return result


@unittest.skipUnless(ADMIN_URL, 'NOT RUN: set reserved disposable PostgreSQL administration URL')
class PostgreSQLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url=make_url(ADMIN_URL)
        if (url.drivername,url.host,url.port,url.database) != ('postgresql+psycopg','127.0.0.1',55441,'postgres'):
            raise RuntimeError('Refusing unreserved/shared database endpoint')
        cls.admin=sa.create_engine(url,isolation_level='AUTOCOMMIT',hide_parameters=True,connect_args={'connect_timeout':5})
        with cls.admin.connect() as c:
            cls.server_version=c.scalar(sa.text('SHOW server_version'))
            if int(cls.server_version.split('.')[0])<16: raise RuntimeError('PostgreSQL 16+ required')

    @classmethod
    def tearDownClass(cls): cls.admin.dispose()

    @contextmanager
    def database(self, profile=None):
        name='test_ms7_mig_v01_'+uuid.uuid4().hex
        quote=self.admin.dialect.identifier_preparer.quote(name)
        with self.admin.connect() as c:
            c.execute(sa.text('CREATE DATABASE '+quote))
            c.execute(sa.text("COMMENT ON DATABASE "+quote+" IS 'MS7-MIG-V01 disposable synthetic test database'"))
        engine=create_engine(DatabaseConfig(make_url(ADMIN_URL).set(database=name)))
        try:
            if profile:
                env={**os.environ,'DJANGO_DB_BACKEND':'postgresql','DJANGO_DB_HOST':'127.0.0.1',
                     'DJANGO_DB_PORT':'55441','DJANGO_DB_NAME':name,'DJANGO_DB_USER':engine.url.username,
                     'DJANGO_DB_PASSWORD':engine.url.password or 'synthetic-local-only',
                     'DJANGO_RUNTIME_ROOT':str(Path('var/ms7-mig-v01-runtime').resolve()),'DJANGO_SECRET_KEY':'synthetic-test-only-not-production',
                     'DJANGO_DEBUG':'0'}
                process=subprocess.run([sys.executable,'-m','backend.tests.legacy_fixture',profile],env=env,capture_output=True)
                if process.returncode: raise RuntimeError('Legacy fixture setup failed: '+process.stderr.decode(errors='replace')[-1500:])
            yield engine
        finally:
            engine.dispose()
            with self.admin.connect() as c:
                # quote is derived solely from a fresh uuid generated above.
                c.execute(sa.text('DROP DATABASE '+quote+' WITH (FORCE)'))

    def seed(self, engine, profile):
        now=utc_now().replace(microsecond=123456)
        with engine.begin() as c:
            if profile=='A':
                c.execute(sa.text('INSERT INTO content_grade (id,title,slug,"order",description) VALUES (701,\'Synthetic\',\'5-klass\',0,\'\')'))
            else:
                c.execute(sa.insert(metadata.tables['content_grade']).values(id=701,title='Synthetic',slug='5-klass',created_at=now))
            c.execute(sa.insert(metadata.tables['auth_user']).values(id=901,username='synthetic-user',
                password='pbkdf2_sha256$1000$synthetic-fixture$'+sha256(b'synthetic fixture only').hexdigest(),date_joined=now,is_staff=True,is_superuser=True))
            c.execute(sa.insert(metadata.tables['django_content_type']).values(id=41,app_label='synthetic',model='record'))
            c.execute(sa.insert(metadata.tables['auth_permission']).values(id=51,name='Synthetic',content_type_id=41,codename='synthetic'))
            c.execute(sa.insert(metadata.tables['auth_group']).values(id=61,name='Synthetic role'))
            # B01 regression: real join identities exceeding int4 must survive;
            # user/group/permission foreign keys retain the original int4 IDs.
            c.execute(sa.insert(metadata.tables['auth_user_groups']).values(id=2**31+1001,user_id=901,group_id=61))
            c.execute(sa.insert(metadata.tables['auth_group_permissions']).values(id=2**31+1002,group_id=61,permission_id=51))
            c.execute(sa.insert(metadata.tables['auth_user_user_permissions']).values(id=2**31+1003,user_id=901,permission_id=51))
            subject=metadata.tables['content_subject']; section=metadata.tables['content_section']; page=metadata.tables['content_contentpage']
            c.execute(sa.insert(subject).values(id=702,title='S',slug='s',grade_id=701))
            c.execute(sa.insert(section).values(id=703,title='C',slug='c',subject_id=702))
            c.execute(sa.insert(page).values(id=704,title='P',slug='p',grade_id=701,subject_id=702,section_id=703,body_html='<p>Синтетический материал</p>',created_at=now,updated_at=now))
            c.execute(sa.insert(metadata.tables['content_lessonpublication']).values(id=705,page_id=704,source_path='synthetic/topic.json',published_digest='0'*64,published_at=now))
            c.execute(sa.insert(metadata.tables['content_mediaasset']).values(id=706,file='synthetic/asset.svg',related_page_id=704,created_at=now))
            c.execute(sa.insert(metadata.tables['content_redirect']).values(id=707,old_path='/synthetic',new_path='/p/'))
            c.execute(sa.insert(metadata.tables['django_session']).values(session_key='synthetic-session',session_data='synthetic-only',expire_date=now+timedelta(days=1)))
            if profile=='C':
                c.execute(sa.insert(metadata.tables['users_studentprofile']).values(id=uuid.uuid4(),user_id=901,selected_grade_id=701,
                    onboarding_mode='SELF_REPORT',onboarding_complete=True,created_at=now))
                receipt=metadata.tables['users_identityreceipt']
                c.execute(sa.insert(receipt).values(id=uuid.uuid4(),scope='user:901',operation='onboarding',key_digest='1'*64,
                    request_digest='2'*64,user_id=901,response={'synthetic':True},status=200,created_at=now,expires_at=now+timedelta(days=7)))
                c.execute(sa.insert(receipt).values(id=uuid.uuid4(),scope='anonymous:synthetic',operation='register',key_digest='3'*64,
                    request_digest='4'*64,created_at=now,expires_at=now+timedelta(days=7)))
                c.execute(sa.insert(metadata.tables['users_loginwindow']).values(id=uuid.uuid4(),ip_digest='5'*64,started_at=now,count=3))
        return now

    def test_fresh_twice_separate_databases_no_django(self):
        for _ in range(2):
            with self.database() as e:
                with e.begin() as c:
                    fresh(c)
                    assert_baseline(c,'FRESH',allow_protocol=True,require_history=False)
                    self.assertEqual(c.scalar(sa.text('SELECT version_num FROM alembic_version')),HEAD)
                self.seed(e,'C')
                with Session(e) as s:
                    page=s.get(__import__('backend.models.baseline',fromlist=['ContentPage']).ContentPage,704)
                    self.assertEqual(page.grade.id,701)
                    self.assertEqual(s.get(StudentProfile,s.scalar(sa.select(StudentProfile.id))).user.id,901)

    def test_upgrade_profiles_preserve_data_defaults_epoch_sequences(self):
        for profile in ('A','B','C'):
            with self.subTest(profile=profile), self.database(profile) as e:
                now=self.seed(e,profile)
                with e.begin() as c:
                    before=data_digest(c,omit_grade_time=profile=='A')
                    history=list(c.execute(sa.text('SELECT * FROM django_migrations ORDER BY id')))
                    upgrade_profile(c,profile,reviewed=True)
                    after=data_digest(c,omit_grade_time=profile=='A')
                    for table,digest in before.items():
                        if table!='users_studentprofile' or profile=='C': self.assertEqual(digest,after[table],table)
                    self.assertEqual(history,list(c.execute(sa.text('SELECT * FROM django_migrations ORDER BY id'))))
                    self.assertEqual(c.scalar(sa.text('SELECT created_at FROM content_grade WHERE id=701')),GRADE_EPOCH if profile=='A' else now)
                    once=data_digest(c)
                    backfill(c); backfill(c)
                    self.assertEqual(once,data_digest(c))
                    for item in SNAPSHOT['fresh_disposable_sequence_evidence']['identity_columns']:
                        table=metadata.tables[item['table_name']]
                        maximum=c.scalar(sa.select(sa.func.max(table.c.id)))
                        next_value=c.scalar(sa.text('SELECT nextval(CAST(:sequence AS regclass))'),{'sequence':item['owned_sequence']})
                        self.assertGreater(next_value,maximum or 0)
                    # An already-ahead sequence must not be moved backwards.
                    c.execute(sa.text("SELECT setval('content_grade_id_seq',90000,true)"))
                    advance_sequences(c)
                    self.assertEqual(c.scalar(sa.text("SELECT nextval('content_grade_id_seq')")),90001)

    def test_rollback_injection_no_ddl_data_or_history_mutation(self):
        for failure in ('ddl','backfill','protocol'):
            with self.subTest(failure=failure),self.database('A') as e:
                self.seed(e,'A')
                with e.connect() as c: before_schema=inventory(c); before_data=data_digest(c,omit_grade_time=True)
                with self.assertRaises(RuntimeError):
                    with e.begin() as c: upgrade_profile(c,'A',reviewed=True,failure_at=failure)
                with e.connect() as c:
                    self.assertEqual(before_schema,inventory(c))
                    self.assertEqual(before_data,data_digest(c,omit_grade_time=True))

    def test_unknown_head_and_schema_forbid_stamp(self):
        for defect in ('head','column','table','constraint','onboarding_check','index','sequence','orphan_sequence','view','schema'):
            with self.subTest(defect=defect),self.database('B') as e:
                with e.begin() as c:
                    sql={'head':"INSERT INTO django_migrations(app,name,applied) VALUES ('content','9999_unknown',now())",
                         'column':'ALTER TABLE content_grade ADD COLUMN unknown text',
                         'table':'CREATE TABLE unknown (id integer)',
                         'constraint':'ALTER TABLE content_grade DROP CONSTRAINT content_grade_order_check',
                         'onboarding_check':'ALTER TABLE users_studentprofile DROP CONSTRAINT users_consistent_onboarding',
                         'index':'DROP INDEX content_grade_slug_cc0387d6_like',
                         'sequence':'ALTER SEQUENCE content_grade_id_seq INCREMENT BY 2',
                         'orphan_sequence':'CREATE SEQUENCE unexpected_sequence',
                         'view':'CREATE VIEW unexpected_view AS SELECT 1 AS id',
                         'schema':'CREATE SCHEMA unexpected_schema'}[defect]
                    if defect=='index':
                        name=c.scalar(sa.text("SELECT indexname FROM pg_indexes WHERE tablename='content_grade' AND indexname LIKE '%_like'"))
                        sql='DROP INDEX '+c.dialect.identifier_preparer.quote(name)
                    c.execute(sa.text(sql))
                    if defect == 'onboarding_check':
                        c.execute(sa.text('ALTER TABLE users_studentprofile ADD CONSTRAINT users_consistent_onboarding CHECK (true)'))
                with e.connect() as c: before=inventory(c)
                with self.assertRaises(SchemaMismatch):
                    with e.begin() as c: upgrade_profile(c,'B',reviewed=True)
                with e.connect() as c: self.assertEqual(before,inventory(c))

    def test_existing_unknown_alembic_and_no_review_refused(self):
        with self.database('B') as e:
            with self.assertRaises(SchemaMismatch):
                with e.begin() as c: upgrade_profile(c,'B')
            with e.begin() as c:
                c.execute(sa.text('CREATE TABLE alembic_version (version_num varchar(32) PRIMARY KEY)'))
                c.execute(sa.text("INSERT INTO alembic_version VALUES ('unknown')"))
            with self.assertRaises(SchemaMismatch):
                with e.begin() as c: upgrade_profile(c,'B',reviewed=True)

    def test_constraints_jsonnull_deferred_fk_and_protect(self):
        with self.database() as e:
            with e.begin() as c: fresh(c)
            self.seed(e,'C')
            with UnitOfWork(e) as uow:
                with self.assertRaises(ProtectedDeletion): delete_collected(uow.session,'auth_user',[901])
                with self.assertRaises(ProtectedDeletion): delete_collected(uow.session,'content_grade',[701])
                self.assertIsNotNone(uow.session.get(User,901))
            bad=[sa.insert(metadata.tables['content_grade']).values(title='X',slug='5-klass'),
                 sa.insert(metadata.tables['content_grade']).values(title='X',slug='negative',order=-1),
                 sa.insert(metadata.tables['content_grade']).values(title=None,slug='null'),
                 sa.insert(metadata.tables['users_loginwindow']).values(ip_digest='6'*64,started_at=utc_now(),count=11),
                 sa.insert(metadata.tables['users_identityreceipt']).values(scope='synthetic',operation='register',key_digest='7'*64,
                    request_digest='8'*64,response=sa.JSON.NULL,created_at=utc_now(),expires_at=utc_now()+timedelta(days=7)),
                 sa.insert(metadata.tables['users_studentprofile']).values(user_id=901)]
            for statement in bad:
                with self.assertRaises(sa.exc.IntegrityError):
                    with e.begin() as c: c.execute(statement)
            with self.assertRaises(sa.exc.IntegrityError):
                with e.begin() as c:
                    c.execute(sa.insert(metadata.tables['content_subject']).values(title='X',slug='invalid-fk',grade_id=999999))
                    # FK remains initially deferred until transaction commit.
                    self.assertEqual(c.scalar(sa.text('SELECT 1')),1)

    def test_check_canonicalization_exact_and_truth_table(self):
        from .check_canonicalization import investigate
        with self.database('B') as e:
            with e.begin() as c:
                result = investigate(c)
                self.assertTrue(result['original_in_matches_frozen_exactly'])
                self.assertFalse(result['frozen_deparse_roundtrip_matches'])
                self.assertEqual(result['truth_table_cases'], 42)
                self.assertEqual(result['truth_table_mismatches'], [])
                actual = c.scalar(sa.text("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname='users_consistent_onboarding' AND conrelid='users_studentprofile'::regclass"))
                self.assertEqual(actual, result['frozen_catalog_definition'])

    def test_additive_protocol_schema_drift_is_visible(self):
        for defect in ('missing_table','column','check','index','foreign_key','sequence'):
            with self.subTest(defect=defect), self.database() as e:
                with e.begin() as c:
                    fresh(c)
                    sql = {'missing_table':'DROP TABLE target_publication_history',
                           'column':'ALTER TABLE target_session ADD COLUMN unexpected text',
                           'check':'ALTER TABLE target_receipt_bridge DROP CONSTRAINT target_bridge_min_retention',
                           'index':'DROP INDEX target_session_lineage_idx',
                           'foreign_key':'ALTER TABLE target_session DROP CONSTRAINT target_session_user_fk',
                           'sequence':'ALTER SEQUENCE target_publication_history_id_seq INCREMENT BY 2'}[defect]
                    c.execute(sa.text(sql))
                with e.connect() as c:
                    before = inventory(c)
                    with self.assertRaises(SchemaMismatch):
                        assert_baseline(c, 'FRESH', allow_protocol=True, require_history=False)
                    self.assertEqual(before, inventory(c))

    def test_sequence_empty_and_uncalled_semantics(self):
        with self.database() as e:
            with e.begin() as c:
                fresh(c)
                sequences = SNAPSHOT['fresh_disposable_sequence_evidence']['identity_columns']
                def positions():
                    return {item['owned_sequence']: tuple(c.execute(sa.text(
                        'SELECT last_value,is_called FROM '+item['owned_sequence'])).one()) for item in sequences}
                before = positions()
                advance_sequences(c)
                self.assertEqual(before, positions())
                c.execute(sa.insert(metadata.tables['content_grade']).values(id=1,title='Uncalled',slug='uncalled'))
                self.assertEqual(c.execute(sa.text('SELECT last_value,is_called FROM content_grade_id_seq')).one(), (1,False))
                advance_sequences(c)
                self.assertEqual(c.execute(sa.text('SELECT last_value,is_called FROM content_grade_id_seq')).one(), (1,True))
                self.assertEqual(c.scalar(sa.text("SELECT nextval('content_grade_id_seq')")),2)

    def test_postgres_defaults_timestamps_and_collector_cascade(self):
        from backend.models.baseline import Subject, Section, ContentPage, LessonPublication, MediaAsset
        with self.database() as e:
            with e.begin() as c: fresh(c)
            with UnitOfWork(e) as uow:
                grade = Grade(title='Default', slug='default'); uow.session.add(grade); uow.session.flush()
                self.assertEqual(grade.order,0); self.assertEqual(grade.description,'')
                self.assertIsNotNone(grade.created_at.tzinfo)
                subject = Subject(title='S',slug='s',grade_id=grade.id); uow.session.add(subject); uow.session.flush()
                section = Section(title='C',slug='c',subject_id=subject.id); uow.session.add(section); uow.session.flush()
                original_time = utc_now().replace(microsecond=654321) - timedelta(days=1)
                page = ContentPage(title='P',slug='p',grade_id=grade.id,subject_id=subject.id,section_id=section.id,
                                   updated_at=original_time)
                repo = uow.repository(ContentPage); repo.add(page); uow.session.flush()
                self.assertGreater(page.updated_at, original_time)
                repo.bulk_update([page.id], {'updated_at': original_time}); uow.session.refresh(page)
                uow.session.add_all([LessonPublication(page_id=page.id,source_path='synthetic/p',published_digest='0'*64),
                                    MediaAsset(file='synthetic/asset',related_page_id=page.id)]); uow.session.flush()
                page.title='Saved'; repo.save(page,fields={'title'})
                self.assertEqual(page.updated_at,original_time)
                repo.bulk_update([page.id],{'title':'Bulk'}); uow.session.refresh(page)
                self.assertEqual(page.updated_at,original_time)
                repo.save(page,fields={'updated_at'}); self.assertGreater(page.updated_at,original_time)
                delete_collected(uow.session,'content_grade',[grade.id]); uow.session.expire_all()
                self.assertIsNone(page.grade_id); self.assertIsNone(page.subject_id); self.assertIsNone(page.section_id)
                delete_collected(uow.session,'content_contentpage',[page.id]); uow.session.expire_all()
                self.assertEqual(uow.session.scalar(sa.select(sa.func.count()).select_from(LessonPublication)),0)
                self.assertIsNone(uow.session.scalar(sa.select(MediaAsset)).related_page_id)
                uow.commit()
            # Python defaults must not become hidden SQL defaults.
            with self.assertRaises(sa.exc.IntegrityError):
                with e.begin() as c:
                    c.execute(sa.text("INSERT INTO content_grade(title,slug) VALUES ('Missing','missing')"))

    def test_ordered_row_lock_is_real_and_receipts_use_stable_order(self):
        from backend.infrastructure.locks import OrderedLocks, LockOrderViolation
        with self.database() as e:
            with e.begin() as c: fresh(c)
            self.seed(e,'C')
            # Second session has a short local timeout; no indefinite waits.
            with Session(e) as first:
                locks=OrderedLocks(first)
                locks.namespace('identity','synthetic')
                locks.rows(metadata.tables['auth_user'],[901])
                locks.rows(metadata.tables['users_identityreceipt'],list(first.scalars(sa.select(metadata.tables['users_identityreceipt'].c.id))))
                self.assertEqual(locks.previous[2], ('user:901','onboarding','1'*64))
                with self.assertRaises(LockOrderViolation): locks.rows(metadata.tables['auth_user'],[901])
                with self.assertRaises(sa.exc.OperationalError):
                    with e.begin() as second:
                        second.execute(sa.text("SET LOCAL lock_timeout='100ms'"))
                        second.execute(sa.text('UPDATE auth_user SET first_name=first_name WHERE id=901'))
                first.rollback()
            with e.begin() as second:
                second.execute(sa.text("SET LOCAL lock_timeout='100ms'"))
                second.execute(sa.text('UPDATE auth_user SET first_name=first_name WHERE id=901'))


if __name__ == '__main__': unittest.main()
