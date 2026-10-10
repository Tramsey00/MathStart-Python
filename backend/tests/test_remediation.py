"""F1/F2/F3 regressions on freshly created, marked PostgreSQL databases only."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Session
from . import test_postgres as fixtures
from backend.infrastructure.collector import delete_collected, plan_collection, DeletionPlanChanged, ProtectedDeletion
from backend.infrastructure.locks import OrderedLocks
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import metadata, Grade, ContentPage, LessonPublication, MediaAsset, User, StudentProfile, IdentityReceipt, utc_now
from backend.migrations.schema import assert_baseline, inventory, SchemaMismatch
from backend.migrations.upgrade import fresh, upgrade_profile, advance_sequences, HEAD
from backend.migrate import main as cli


def write_evidence(name, result):
    # Fresh verification must not overwrite the committed historical evidence.
    directory = Path(os.environ.get('MATHSTART_V01_EVIDENCE_DIR', 'var/ms7-mig-v01-evidence'))
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')


@unittest.skipUnless(fixtures.ADMIN_URL, 'NOT RUN: explicit reserved disposable PostgreSQL admin URL required')
class RemediationTests(unittest.TestCase):
    database = fixtures.PostgreSQLTests.database
    seed = fixtures.PostgreSQLTests.seed

    @classmethod
    def setUpClass(cls):
        fixtures.PostgreSQLTests.setUpClass()
        cls.admin = fixtures.PostgreSQLTests.admin

    @classmethod
    def tearDownClass(cls):
        cls.admin.dispose()

    def test_f1_all_auto_timestamps_match_real_django_and_historical_import(self):
        old = datetime(2000, 1, 1, tzinfo=timezone.utc)
        with self.database('B') as engine:
            env = {**os.environ, 'DJANGO_DB_BACKEND': 'postgresql', 'DJANGO_DB_HOST': '127.0.0.1',
                   'DJANGO_DB_PORT': '55441', 'DJANGO_DB_NAME': engine.url.database,
                   'DJANGO_DB_USER': engine.url.username, 'DJANGO_DB_PASSWORD': engine.url.password or 'synthetic-local-only',
                   'DJANGO_SECRET_KEY': 'synthetic-f1-only',
                   'DJANGO_RUNTIME_ROOT': str(Path('var/ms7-mig-v01-f1-runtime').resolve())}
            process = subprocess.run([sys.executable, '-m', 'backend.tests.django_timestamp_probe'],
                                     env=env, capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, 'Real Django timestamp probe failed')
            django = json.loads(process.stdout)
            with UnitOfWork(engine) as uow:
                grade = Grade(title='Target', slug='target-time', created_at=old)
                page = ContentPage(title='Target', slug='target-time', created_at=old, updated_at=old)
                uow.repository(Grade).add(grade); repo = uow.repository(ContentPage); repo.add(page)
                uow.session.flush()
                publication = LessonPublication(page_id=page.id, source_path='synthetic/target', published_digest='0'*64, published_at=old)
                media = MediaAsset(file='synthetic/target.svg', created_at=old)
                user = User(username='target-time')
                # Direct ORM creation shares the ordinary pre-save rules.
                uow.session.add_all([publication, media, user]); uow.session.flush()
                profile = StudentProfile(user_id=user.id, created_at=old)
                receipt = IdentityReceipt(scope='synthetic-target', operation='register', key_digest='0'*64,
                          request_digest='1'*64, created_at=old, expires_at=old+timedelta(days=7))
                uow.session.add_all([profile, receipt]); uow.session.flush()
                records = [(grade, 'created_at'), (page, 'created_at'), (page, 'updated_at'),
                           (publication, 'published_at'), (media, 'created_at'), (profile, 'created_at'), (receipt, 'created_at')]
                target = {'insert_preserves_old': {sa.inspect(obj).mapper.local_table.name+'.'+field:
                            getattr(obj, field) == old for obj, field in records}}
                self.assertTrue(all(getattr(obj, field).tzinfo is not None for obj, field in records))
                repo.bulk_update([page.id], {'created_at': old, 'updated_at': old}); uow.session.refresh(page)
                page.title = 'Restricted'; repo.save(page, fields={'title'})
                target['restricted_save_preserves_auto_now'] = page.updated_at == old
                repo.save(page)
                target['full_save_preserves_auto_now_add'] = page.created_at == old
                target['full_save_preserves_auto_now'] = page.updated_at == old
                page.updated_at = old; repo.save(page, fields={'updated_at'})
                target['included_auto_now_preserves_old'] = page.updated_at == old
                repo.bulk_update([page.id], {'updated_at': old}); uow.session.refresh(page)
                target['bulk_update_preserves_explicit_old'] = page.updated_at == old
                publication_repo=uow.repository(LessonPublication)
                publication_repo.bulk_update([publication.id],{'published_at':old}); uow.session.refresh(publication)
                publication.published_digest='1'*64; publication_repo.save(publication,fields={'published_digest'})
                target['publication_restricted_save_preserves_auto_now'] = publication.published_at == old
                publication_repo.save(publication)
                target['publication_full_save_preserves_auto_now'] = publication.published_at == old
                publication.published_at=old; publication_repo.save(publication,fields={'published_at'})
                target['publication_included_auto_now_preserves_old'] = publication.published_at == old
                # A new ordinary save also overrides explicit values.
                new = ContentPage(title='Save', slug='save-time', created_at=old, updated_at=old)
                repo.save(new)
                self.assertNotEqual(new.created_at, old); self.assertNotEqual(new.updated_at, old)
                self.assertEqual(target, django)
                self.assertEqual(set(target['insert_preserves_old'].values()), {False})
                self.assertTrue(target['restricted_save_preserves_auto_now'])
                self.assertFalse(target['full_save_preserves_auto_now'])
                self.assertFalse(target['included_auto_now_preserves_old'])
                # Explicit historical Core import preserves every auto timestamp.
                history = [
                    (Grade, {'id':801,'title':'History','slug':'history-time','created_at':old}),
                    (ContentPage, {'id':802,'title':'History','slug':'history-time','created_at':old,'updated_at':old}),
                    (LessonPublication, {'id':803,'page_id':802,'source_path':'synthetic/history','published_digest':'0'*64,'published_at':old}),
                    (MediaAsset, {'id':804,'file':'synthetic/history.svg','created_at':old}),
                    (User, {'id':805,'username':'history-time','date_joined':old}),
                    (StudentProfile, {'id':uuid.uuid4(),'user_id':805,'created_at':old}),
                    (IdentityReceipt, {'id':uuid.uuid4(),'scope':'synthetic-history','operation':'register','key_digest':'0'*64,
                        'request_digest':'1'*64,'created_at':old,'expires_at':old+timedelta(days=7)})]
                preserved = {}
                for model, values in history:
                    key = uow.repository(model).import_historical(values)
                    imported = uow.session.get(model, key)
                    for column in sa.inspect(model).columns:
                        field = column.info.get('baseline_field', {})
                        if field.get('auto_now_add') or field.get('auto_now'):
                            preserved[sa.inspect(model).local_table.name+'.'+column.name] = getattr(imported, column.name) == old
                self.assertEqual(len(preserved), 7); self.assertTrue(all(preserved.values()))
                with self.assertRaises(ValueError): repo.import_historical({'id':999,'title':'Missing time','slug':'missing-time'})
                self.assertIsNone(uow.session.get(ContentPage,999))
                uow.commit()
            # A regular autoflush-enabled Session still respects update_fields.
            with Session(engine) as session:
                from backend.infrastructure.repositories import Repository
                page = session.get(ContentPage,802); page.title='Autoflush-safe'; page.updated_at=old-timedelta(days=1)
                Repository(session, ContentPage).save(page, fields={'title'}); session.commit()
                self.assertEqual(page.updated_at,old)
            write_evidence('f1-timestamp-parity.json',
                {'status':'PASS','Django':django,'target':target,'historical_auto_timestamps_preserved':preserved})

    def crossed_catalog(self, engine):
        with engine.begin() as c:
            fresh(c)
            for identity in (1,2):
                c.execute(sa.insert(metadata.tables['content_grade']).values(id=identity,title='G',slug='g'+str(identity)))
                c.execute(sa.insert(metadata.tables['content_subject']).values(id=identity,title='S',slug='s',grade_id=identity))
                c.execute(sa.insert(metadata.tables['content_section']).values(id=identity,title='C',slug='c',subject_id=identity))
                c.execute(sa.insert(metadata.tables['content_contentpage']).values(id=identity,title='P',slug='p'+str(identity),
                           grade_id=identity,subject_id=3-identity,section_id=3-identity))
                c.execute(sa.insert(metadata.tables['content_lessonpublication']).values(id=identity,page_id=identity,
                           source_path='synthetic/p'+str(identity),published_digest='0'*64))

    def test_f2_crossed_setnull_two_sessions_canonical_locks_no_deadlock(self):
        with self.database() as engine:
            self.crossed_catalog(engine)
            barrier = threading.Barrier(2)
            states = []; tokens = {}; details=[]; guard = threading.Lock()

            @sa.event.listens_for(engine,'before_cursor_execute')
            def interleave(connection,cursor,statement,parameters,context,executemany):
                # Both plans are discovered before competing for their first
                # shared FK-parent lock; pages retain the audit's crossed links.
                if 'FROM content_grade' in statement and 'FOR UPDATE' in statement and not connection.info.get('f2_barrier'):
                    connection.info['f2_barrier'] = True
                    barrier.wait(timeout=10)

            @sa.event.listens_for(engine,'handle_error')
            def capture(context):
                with guard:
                    states.append(getattr(context.original_exception,'sqlstate',None))
                    diagnostic=getattr(context.original_exception,'diag',None)
                    details.append({'statement':context.statement,
                        'detail':getattr(diagnostic,'message_detail',None),'context':getattr(diagnostic,'context',None)})

            class RecordingLocks(OrderedLocks):
                def __init__(self,session): super().__init__(session); self.tokens=[]
                def _advance(self,token): super()._advance(token); self.tokens.append(token)

            def remove(identity):
                locks = None
                try:
                    with UnitOfWork(engine) as uow:
                        locks = RecordingLocks(uow.session)
                        delete_collected(uow.session,'content_grade',[identity],locks=locks)
                        uow.commit()
                    return 'COMMIT'
                except Exception as error:
                    return type(error).__name__
                finally:
                    if locks: tokens[identity] = locks.tokens

            try:
                with ThreadPoolExecutor(2) as pool:
                    futures=[pool.submit(remove,identity) for identity in (1,2)]
                    outcomes=[future.result(timeout=20) for future in futures]
            finally:
                sa.event.remove(engine,'before_cursor_execute',interleave)
                sa.event.remove(engine,'handle_error',capture)
            self.assertEqual(outcomes,['COMMIT','COMMIT'], {'sqlstates':states,'tokens':tokens,'details':details}); self.assertNotIn('40P01',states)
            for sequence in tokens.values():
                self.assertEqual(sequence,sorted(sequence))
                self.assertEqual([token for token in sequence if token[:2]==(7,0)],[(7,0,(1,)),(7,0,(2,))])
            with engine.connect() as c:
                for name in ('content_grade','content_subject','content_section'):
                    self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(metadata.tables[name])),0)
                pages=[tuple(row) for row in c.execute(sa.text('SELECT id,grade_id,subject_id,section_id FROM content_contentpage ORDER BY id'))]
                self.assertEqual(pages,[(1,None,None,None),(2,None,None,None)])
                self.assertEqual(c.scalar(sa.text('SELECT count(*) FROM content_lessonpublication')),2)
            write_evidence('f2-concurrency.json', {
                'status':'PASS','forced_interleaving':'both FK-closure plans discovered before first common Grade FOR UPDATE',
                'outcomes':outcomes,'sqlstates':states,'lock_tokens':tokens,'page_foreign_keys':pages,
                'initial_40P01_evidence':'independent-audit-v3/audit-probes-results.json'})

    def test_f2_changed_setnull_plan_conflicts_before_mutations(self):
        with self.database() as engine:
            self.crossed_catalog(engine)
            changed = []
            @sa.event.listens_for(engine,'before_cursor_execute')
            def change_dependency(connection,cursor,statement,parameters,context,executemany):
                if 'FROM content_grade' in statement and 'FOR UPDATE' in statement and not changed:
                    changed.append(True)
                    with engine.begin() as other:
                        other.execute(sa.text('UPDATE content_contentpage SET grade_id=NULL WHERE id=1'))
            try:
                with self.assertRaises(DeletionPlanChanged):
                    with UnitOfWork(engine) as uow: delete_collected(uow.session,'content_grade',[1]); uow.commit()
            finally: sa.event.remove(engine,'before_cursor_execute',change_dependency)
            self.assertTrue(changed)
            with engine.connect() as c:
                self.assertEqual(c.scalar(sa.text('SELECT count(*) FROM content_grade')),2)
                self.assertEqual(c.scalar(sa.text('SELECT count(*) FROM content_subject')),2)
                self.assertEqual(c.execute(sa.text('SELECT grade_id,subject_id,section_id FROM content_contentpage WHERE id=1')).one(),(None,2,2))
                self.assertEqual(c.execute(sa.text('SELECT grade_id,subject_id,section_id FROM content_contentpage WHERE id=2')).one(),(2,1,1))
            with UnitOfWork(engine) as uow: delete_collected(uow.session,'content_grade',[1]); uow.commit()

    def test_f2_new_protect_dependency_rechecked_under_locks(self):
        with self.database() as engine:
            self.crossed_catalog(engine)
            with engine.begin() as c: c.execute(sa.insert(metadata.tables['auth_user']).values(id=1,username='protect-race'))
            changed=[]
            @sa.event.listens_for(engine,'before_cursor_execute')
            def insert_protection(connection,cursor,statement,parameters,context,executemany):
                if 'FROM content_grade' in statement and 'FOR UPDATE' in statement and not changed:
                    changed.append(True)
                    with engine.begin() as other:
                        other.execute(sa.insert(metadata.tables['users_studentprofile']).values(user_id=1,selected_grade_id=1))
            try:
                with self.assertRaises(ProtectedDeletion):
                    with UnitOfWork(engine) as uow: delete_collected(uow.session,'content_grade',[1]); uow.commit()
            finally: sa.event.remove(engine,'before_cursor_execute',insert_protection)
            with engine.connect() as c:
                self.assertEqual(c.scalar(sa.text('SELECT count(*) FROM content_grade')),2)
                self.assertEqual(c.scalar(sa.text('SELECT count(*) FROM content_subject')),2)
                self.assertEqual(c.scalar(sa.text('SELECT selected_grade_id FROM users_studentprofile')),1)
                self.assertEqual(c.execute(sa.text('SELECT grade_id,subject_id,section_id FROM content_contentpage WHERE id=1')).one(),(1,2,2))

    def test_f2_new_referenced_parent_requires_outer_restart(self):
        with self.database() as engine:
            self.crossed_catalog(engine)
            with engine.begin() as c:
                c.execute(sa.insert(metadata.tables['content_grade']).values(id=3,title='G3',slug='g3'))
                c.execute(sa.insert(metadata.tables['content_subject']).values(id=3,title='S3',slug='s3',grade_id=3))
                c.execute(sa.insert(metadata.tables['content_section']).values(id=3,title='C3',slug='c3',subject_id=3))
            changed=[]
            @sa.event.listens_for(engine,'before_cursor_execute')
            def retarget(connection,cursor,statement,parameters,context,executemany):
                if 'FROM content_grade' in statement and 'FOR UPDATE' in statement and not changed:
                    changed.append(True)
                    with engine.begin() as other:
                        other.execute(sa.text('UPDATE content_contentpage SET subject_id=3,section_id=3 WHERE id=1'))
            try:
                with self.assertRaises(DeletionPlanChanged):
                    with UnitOfWork(engine) as uow: delete_collected(uow.session,'content_grade',[1]); uow.commit()
            finally: sa.event.remove(engine,'before_cursor_execute',retarget)
            with engine.connect() as c:
                self.assertEqual(c.scalar(sa.text('SELECT count(*) FROM content_grade')),3)
                self.assertEqual(c.scalar(sa.text('SELECT count(*) FROM content_subject')),3)
                self.assertEqual(c.execute(sa.text('SELECT grade_id,subject_id,section_id FROM content_contentpage WHERE id=1')).one(),(1,3,3))
                self.assertEqual(c.execute(sa.text('SELECT grade_id,subject_id,section_id FROM content_contentpage WHERE id=2')).one(),(2,1,1))
            with UnitOfWork(engine) as uow: delete_collected(uow.session,'content_grade',[1]); uow.commit()

    def test_f2_setnull_failure_rolls_back_cascade_and_data(self):
        with self.database() as engine:
            self.crossed_catalog(engine)
            with engine.connect() as c: before=fixtures.data_digest(c)
            @sa.event.listens_for(engine,'after_cursor_execute')
            def fail(connection,cursor,statement,parameters,context,executemany):
                if statement.startswith('UPDATE content_contentpage SET '): raise RuntimeError('Synthetic SET_NULL failure')
            try:
                with self.assertRaises(RuntimeError):
                    with UnitOfWork(engine) as uow: delete_collected(uow.session,'content_grade',[1]); uow.commit()
            finally: sa.event.remove(engine,'after_cursor_execute',fail)
            with engine.connect() as c: self.assertEqual(before,fixtures.data_digest(c))
            with UnitOfWork(engine) as uow:
                delete_collected(uow.session,'content_contentpage',[1]); uow.commit()
            with engine.connect() as c:
                self.assertEqual(c.scalar(sa.text('SELECT count(*) FROM content_lessonpublication')),1)

    def test_f2_reused_reference_pk_is_not_a_falsely_acquired_lock(self):
        with self.database() as engine:
            self.crossed_catalog(engine)
            removed=[]; recreated=[]
            @sa.event.listens_for(engine,'before_cursor_execute')
            def remove_reference(connection,cursor,statement,parameters,context,executemany):
                if 'FROM content_grade' in statement and 'FOR UPDATE' in statement and not removed:
                    removed.append(True)
                    with UnitOfWork(engine) as other:
                        delete_collected(other.session,'content_grade',[1]); other.commit()
            @sa.event.listens_for(engine,'after_cursor_execute')
            def reuse_reference(connection,cursor,statement,parameters,context,executemany):
                if 'FROM content_grade' in statement and 'FOR UPDATE' in statement and cursor.rowcount==0 and not recreated:
                    recreated.append(True)
                    with engine.begin() as other:
                        other.execute(sa.insert(metadata.tables['content_grade']).values(id=1,title='Reused synthetic PK',slug='reused-g1'))
                        other.execute(sa.text('UPDATE content_contentpage SET grade_id=1 WHERE id=1'))
            try:
                with self.assertRaises(DeletionPlanChanged):
                    with UnitOfWork(engine) as uow: delete_collected(uow.session,'content_grade',[2]); uow.commit()
            finally:
                sa.event.remove(engine,'before_cursor_execute',remove_reference)
                sa.event.remove(engine,'after_cursor_execute',reuse_reference)
            self.assertTrue(recreated)
            with engine.connect() as c:
                self.assertEqual(c.scalar(sa.text('SELECT count(*) FROM content_grade')),2)
                self.assertEqual(c.scalar(sa.text('SELECT count(*) FROM content_subject')),1)
                self.assertEqual(c.execute(sa.text('SELECT grade_id,subject_id,section_id FROM content_contentpage WHERE id=1')).one(),(1,2,2))
            with UnitOfWork(engine) as uow: delete_collected(uow.session,'content_grade',[2]); uow.commit()

    def tracking_snapshot(self, connection):
        if 'alembic_version' not in sa.inspect(connection).get_table_names(): return None
        return list(connection.execute(sa.text('SELECT * FROM alembic_version')).all())

    def assert_cli_refused(self, engine, profile=None, *, subprocess_check=True):
        env={'MATHSTART_DB_BACKEND':'postgresql','MATHSTART_DATABASE_URL':engine.url.render_as_string(hide_password=False)}
        arguments=['check','--disposable']+(['--profile',profile] if profile else [])
        with patch.dict(os.environ,env), redirect_stderr(StringIO()), redirect_stdout(StringIO()):
            self.assertEqual(cli(arguments),1)
        if subprocess_check:
            process=subprocess.run([sys.executable,'-m','backend.migrate',*arguments],
                                   env={**os.environ,**env},capture_output=True,text=True)
            self.assertEqual(process.returncode,1)
            self.assertNotIn(engine.url.render_as_string(hide_password=False),process.stderr)

    def test_f3_malformed_empty_tracking_refused_before_stamp(self):
        defects={
            'missing_PK':'CREATE TABLE alembic_version (version_num varchar(32) NOT NULL)',
            'nullable':'CREATE TABLE alembic_version (version_num varchar(32), CONSTRAINT alembic_version_pkc UNIQUE(version_num))',
            'extra_column':'CREATE TABLE alembic_version (version_num varchar(32) NOT NULL CONSTRAINT alembic_version_pkc PRIMARY KEY, unexpected text)',
            'wrong_type':'CREATE TABLE alembic_version (version_num text NOT NULL CONSTRAINT alembic_version_pkc PRIMARY KEY)',
            'wrong_length':'CREATE TABLE alembic_version (version_num varchar(64) NOT NULL CONSTRAINT alembic_version_pkc PRIMARY KEY)',
            'missing_column':'CREATE TABLE alembic_version (wrong varchar(32) NOT NULL PRIMARY KEY)',
            'default':'CREATE TABLE alembic_version (version_num varchar(32) DEFAULT \'v01_0002\' NOT NULL CONSTRAINT alembic_version_pkc PRIMARY KEY)',
        }
        for defect,ddl in defects.items():
            with self.subTest(defect=defect), self.database('B') as engine:
                self.seed(engine,'B')
                with engine.begin() as c: c.execute(sa.text(ddl))
                with engine.connect() as c: before=inventory(c); data=fixtures.data_digest(c); tracking=self.tracking_snapshot(c)
                with self.assertRaises(SchemaMismatch):
                    with engine.begin() as c: upgrade_profile(c,'B',reviewed=True)
                self.assert_cli_refused(engine)
                with engine.connect() as c:
                    self.assertEqual(before,inventory(c)); self.assertEqual(data,fixtures.data_digest(c)); self.assertEqual(tracking,self.tracking_snapshot(c))

    def test_f3_unknown_ambiguous_empty_and_inapplicable_target_heads_fail_closed(self):
        for defect in ('unknown','multiple','empty','base_only','schema_with_valid_head','missing_table','extra_index'):
            with self.subTest(defect=defect), self.database() as engine:
                with engine.begin() as c:
                    fresh(c)
                    sql={'unknown':"UPDATE alembic_version SET version_num='unknown_revision'",
                         'multiple':"INSERT INTO alembic_version VALUES ('v01_0001')",
                         'empty':'DELETE FROM alembic_version',
                         'base_only':"UPDATE alembic_version SET version_num='v01_0001'",
                         'schema_with_valid_head':'ALTER TABLE content_grade ADD COLUMN unexpected text',
                         'missing_table':'DROP TABLE alembic_version',
                         'extra_index':'CREATE INDEX unexpected_tracking_idx ON alembic_version(version_num)'}[defect]
                    c.execute(sa.text(sql))
                with engine.connect() as c: before=inventory(c); data=fixtures.data_digest(c); tracking=self.tracking_snapshot(c)
                with self.assertRaises(SchemaMismatch):
                    with engine.connect() as c: assert_baseline(c,'FRESH',allow_protocol=True,require_history=False)
                self.assert_cli_refused(engine)
                with self.assertRaises(SchemaMismatch):
                    with engine.begin() as c: upgrade_profile(c,'B',reviewed=True)
                with engine.connect() as c:
                    self.assertEqual(before,inventory(c)); self.assertEqual(data,fixtures.data_digest(c)); self.assertEqual(tracking,self.tracking_snapshot(c))

    def test_f3_revision_graph_and_clean_empty_tracking_positive_controls(self):
        with self.database('B') as engine:
            with engine.begin() as c:
                assert_baseline(c,'B')
                c.execute(sa.text('CREATE TABLE alembic_version (version_num varchar(32) NOT NULL CONSTRAINT alembic_version_pkc PRIMARY KEY)'))
                assert_baseline(c,'B')
            with engine.connect() as c: before=inventory(c)
            with patch('backend.migrations.schema.ScriptDirectory.from_config') as mocked:
                mocked.return_value.get_heads.return_value=['v01_0002','ambiguous_head']
                with self.assertRaises(SchemaMismatch):
                    with engine.begin() as c: upgrade_profile(c,'B',reviewed=True)
                self.assert_cli_refused(engine,subprocess_check=False)
            with engine.connect() as c: self.assertEqual(before,inventory(c))
            with engine.begin() as c: upgrade_profile(c,'B',reviewed=True)
            env={'MATHSTART_DB_BACKEND':'postgresql','MATHSTART_DATABASE_URL':engine.url.render_as_string(hide_password=False)}
            with patch.dict(os.environ,env), redirect_stdout(StringIO()): self.assertEqual(cli(['check','--disposable']),0)
            with engine.connect() as c: self.assertEqual(self.tracking_snapshot(c),[(HEAD,)])

    def test_sequence_disconnect_before_commit_preserves_data_and_retry(self):
        import backend.migrations.upgrade as adapter
        with self.database('A') as engine:
            self.seed(engine,'A')
            with engine.connect() as c: before=inventory(c); data=fixtures.data_digest(c,omit_grade_time=True)
            original=adapter.advance_sequences
            def disconnect(connection):
                original(connection)
                pid=connection.scalar(sa.text('SELECT pg_backend_pid()'))
                with self.admin.connect() as admin: self.assertTrue(admin.scalar(sa.text('SELECT pg_terminate_backend(:pid)'),{'pid':pid}))
            with patch.object(adapter,'advance_sequences',disconnect):
                with self.assertRaises(sa.exc.DBAPIError):
                    with engine.begin() as c: upgrade_profile(c,'A',reviewed=True)
            with engine.connect() as c:
                after=inventory(c)
                for key in ('tables','columns','constraints','indexes','migrations'): self.assertEqual(before[key],after[key])
                self.assertEqual(data,fixtures.data_digest(c,omit_grade_time=True))
            with engine.begin() as c: upgrade_profile(c,'A',reviewed=True)
            with engine.connect() as c:
                maximum=c.scalar(sa.text('SELECT max(id) FROM auth_user_groups'))
                self.assertGreater(c.scalar(sa.text("SELECT nextval('auth_user_groups_id_seq')")),maximum)

    def test_b01_actual_generated_join_ids_and_superuser_preservation(self):
        for profile in (None,'A','B','C'):
            with self.subTest(profile=profile or 'FRESH'), self.database(profile) as engine:
                if not profile:
                    with engine.begin() as c: fresh(c)
                self.seed(engine,profile or 'C')
                with engine.begin() as c:
                    if profile: upgrade_profile(c,profile,reviewed=True)
                    else: advance_sequences(c)
                    self.assertTrue(c.scalar(sa.text('SELECT is_superuser FROM auth_user WHERE id=901')))
                    c.execute(sa.insert(metadata.tables['auth_user']).values(id=902,username='new-role'))
                    c.execute(sa.insert(metadata.tables['auth_group']).values(id=62,name='New role'))
                    assignments={'auth_user_groups':{'user_id':902,'group_id':61},
                                 'auth_group_permissions':{'group_id':62,'permission_id':51},
                                 'auth_user_user_permissions':{'user_id':902,'permission_id':51}}
                    for name,values in assignments.items():
                        table=metadata.tables[name]
                        maximum=c.scalar(sa.select(sa.func.max(table.c.id)))
                        generated=c.scalar(sa.insert(table).values(**values).returning(table.c.id))
                        self.assertGreater(generated,maximum)
                        self.assertGreater(generated,2**31)


if __name__ == '__main__': unittest.main()
