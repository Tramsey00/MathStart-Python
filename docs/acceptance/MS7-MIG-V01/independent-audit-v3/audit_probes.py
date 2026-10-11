"""Independent read-only source review probes; writes only new disposable DBs.
Run from this external audit copy with the isolated admin URL in environment.
"""
import concurrent.futures
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import sqlalchemy as sa
from backend.tests.test_postgres import PostgreSQLTests, data_digest
from backend.infrastructure.collector import delete_collected
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import Grade, ContentPage, metadata
import backend.migrations.upgrade as upgrade
from backend.migrations.schema import assert_baseline, inventory
from backend.migrate import main

results = {}
PostgreSQLTests.setUpClass()
try:
    results['PostgreSQL'] = PostgreSQLTests.server_version
    with PostgreSQLTests().database('B') as engine:
        old = datetime(2000, 1, 1, tzinfo=timezone.utc)
        env = {**os.environ, 'DJANGO_SETTINGS_MODULE': 'config.settings',
            'DJANGO_DB_BACKEND': 'postgresql', 'DJANGO_DB_HOST': '127.0.0.1',
            'DJANGO_DB_PORT': '55441', 'DJANGO_DB_NAME': engine.url.database,
            'DJANGO_DB_USER': engine.url.username, 'DJANGO_DB_PASSWORD': engine.url.password,
            'DJANGO_SECRET_KEY': 'independent-synthetic-only',
            'DJANGO_RUNTIME_ROOT': str(Path('audit-django-runtime').resolve())}
        code = "import django;django.setup();from datetime import datetime,timezone;from content.models import Grade,ContentPage;old=datetime(2000,1,1,tzinfo=timezone.utc);g=Grade.objects.create(title='D',slug='d',created_at=old);p=ContentPage.objects.create(title='D',slug='d',created_at=old,updated_at=old);import json;print(json.dumps([g.created_at==old,p.created_at==old,p.updated_at==old]))"
        process = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True)
        assert process.returncode == 0, 'Django comparison subprocess failed'
        django_result = json.loads(process.stdout)
        with UnitOfWork(engine) as uow:
            grade = Grade(title='T', slug='t', created_at=old)
            page = ContentPage(title='T', slug='t', created_at=old, updated_at=old)
            uow.repository(Grade).add(grade); uow.repository(ContentPage).add(page)
            uow.session.flush()
            target_result = [grade.created_at == old, page.created_at == old, page.updated_at == old]
            uow.commit()
        assert django_result == [False]*3 and target_result == [True]*3
        results['F1_timestamp_parity'] = {'django_preserves_explicit_old_time': django_result, 'target_preserves_explicit_old_time': target_result}

    with PostgreSQLTests().database() as engine:
        with engine.begin() as connection:
            upgrade.fresh(connection)
            connection.execute(sa.insert(metadata.tables['content_grade']), [{'id':1,'title':'G1','slug':'g1'}, {'id':2,'title':'G2','slug':'g2'}])
            connection.execute(sa.insert(metadata.tables['content_subject']), [{'id':1,'title':'S1','slug':'s1','grade_id':1}, {'id':2,'title':'S2','slug':'s2','grade_id':2}])
            connection.execute(sa.insert(metadata.tables['content_contentpage']), [{'id':1,'title':'P1','slug':'p1','grade_id':1,'subject_id':2}, {'id':2,'title':'P2','slug':'p2','grade_id':2,'subject_id':1}])
        barrier = threading.Barrier(2); errors = []
        @sa.event.listens_for(engine, 'after_cursor_execute')
        def synchronize(connection, cursor, statement, parameters, context, executemany):
            if statement.startswith('UPDATE content_contentpage SET grade_id='):
                barrier.wait(timeout=10)
        @sa.event.listens_for(engine, 'handle_error')
        def capture(context):
            errors.append(getattr(context.original_exception, 'sqlstate', None))
        def remove(identity):
            try:
                with UnitOfWork(engine) as uow:
                    delete_collected(uow.session, 'content_grade', [identity]); uow.commit()
                return 'COMMIT'
            except Exception as error:
                return type(error).__name__
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            outcomes = list(pool.map(remove, [1,2]))
        assert '40P01' in errors and sorted(outcomes) == ['COMMIT','DatabaseUnavailable']
        results['F2_collector_deadlock'] = {'outcomes': outcomes, 'sqlstates': errors, 'rows_are_valid_under_baseline_constraints': True}

    with PostgreSQLTests().database('B') as engine:
        with engine.begin() as connection:
            connection.execute(sa.text('CREATE TABLE alembic_version (version_num varchar(32), unexpected text)'))
        with engine.begin() as connection:
            outcome = upgrade.upgrade_profile(connection, 'B', reviewed=True)
            assert_baseline(connection, 'B', allow_protocol=True, require_history=False)
            columns = [(row['name'], row['nullable']) for row in sa.inspect(connection).get_columns('alembic_version')]
            primary_key = sa.inspect(connection).get_pk_constraint('alembic_version')['constrained_columns']
            connection.execute(sa.text("UPDATE alembic_version SET version_num='unknown_revision'"))
        old_env = {name:os.environ.get(name) for name in ['MATHSTART_DB_BACKEND','MATHSTART_DATABASE_URL']}
        os.environ['MATHSTART_DB_BACKEND'] = 'postgresql'
        os.environ['MATHSTART_DATABASE_URL'] = engine.url.render_as_string(hide_password=False)
        try:
            check_exit = main(['check', '--disposable'])
        finally:
            for name, value in old_env.items():
                if value is None: os.environ.pop(name,None)
                else: os.environ[name]=value
        assert primary_key == [] and check_exit == 0
        results['F3_alembic_tracking_drift'] = {'upgrade':outcome,'columns':columns,'primary_key':primary_key,'unknown_head_check_exit':check_exit}

    for failure in ['ddl','backfill','protocol']:
        with PostgreSQLTests().database('A') as engine:
            PostgreSQLTests().seed(engine,'A')
            try:
                with engine.begin() as connection:
                    upgrade.upgrade_profile(connection,'A',reviewed=True,failure_at=failure)
            except RuntimeError: pass
            with engine.begin() as connection:
                results['retry_after_'+failure] = upgrade.upgrade_profile(connection,'A',reviewed=True)

    with PostgreSQLTests().database('A') as engine:
        PostgreSQLTests().seed(engine,'A')
        with engine.connect() as connection:
            before=inventory(connection); before_data=data_digest(connection,omit_grade_time=True)
        original_advance=upgrade.advance_sequences
        def disconnect_after_setval(connection):
            original_advance(connection)
            pid=connection.scalar(sa.text('SELECT pg_backend_pid()'))
            with PostgreSQLTests.admin.connect() as admin:
                admin.scalar(sa.text('SELECT pg_terminate_backend(:pid)'),{'pid':pid})
        upgrade.advance_sequences=disconnect_after_setval
        disconnected=False
        try:
            try:
                with engine.begin() as connection: upgrade.upgrade_profile(connection,'A',reviewed=True)
            except sa.exc.DBAPIError: disconnected=True
        finally: upgrade.advance_sequences=original_advance
        with engine.connect() as connection:
            after=inventory(connection)
            data_ok=before_data==data_digest(connection,omit_grade_time=True)
            schema_ok=all(before[key]==after[key] for key in ['tables','columns','constraints','indexes','migrations'])
        assert disconnected and data_ok and schema_ok
        with engine.begin() as connection: retry=upgrade.upgrade_profile(connection,'A',reviewed=True)
        results['post_setval_precommit_disconnect']={'detected':disconnected,'data_unchanged':data_ok,'schema_history_unchanged':schema_ok,'retry':retry,'commit_ack_loss_not_simulated':True}
finally:
    PostgreSQLTests.tearDownClass()
Path('audit-probes-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
