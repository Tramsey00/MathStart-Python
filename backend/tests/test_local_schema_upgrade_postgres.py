"""Reviewed local upgrade and ACL recovery through host-dev and Compose."""
from contextlib import ExitStack, contextmanager
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from alembic import command
import sqlalchemy as sa

from backend import release_migrate
from backend.migrations import runtime_privileges
from backend.migrations.upgrade import HEAD, configuration
from backend.tests import test_postgres as disposable
from scripts import container_dev as compose, team_local as host


READ_TABLES = ('knowledge_skill', 'knowledge_skill_dependency', 'content_topic_skill',
               'assessment_exercise', 'assessment_exercise_version', 'assessment_exercise_skill')
ROOT = Path(__file__).resolve().parents[2]
TEMP = ROOT / 'var' / 'tmp'
ORIGIN = 'http://127.0.0.1:8131'


class LocalSchemaUpgradeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TEMP.mkdir(parents=True, exist_ok=True)
        disposable.PostgreSQLTests.setUpClass()
        cls.fixture = disposable.PostgreSQLTests()
        cls.addClassCleanup(disposable.PostgreSQLTests.tearDownClass)
        with cls.fixture.admin.connect() as connection:
            for role in ('local_schema', 'local_runtime'):
                connection.exec_driver_sql(f'CREATE ROLE {role} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE')
                cls.addClassCleanup(cls.drop_role, role)

    @classmethod
    def drop_role(cls, role):
        with cls.fixture.admin.connect() as connection:
            connection.exec_driver_sql(f'DROP ROLE {role}')

    @contextmanager
    def installed_database(self, source_head):
        with self.fixture.database() as admin:
            with self.fixture.admin.connect() as connection:
                name = connection.dialect.identifier_preparer.quote(admin.url.database)
                connection.exec_driver_sql(f'ALTER DATABASE {name} OWNER TO local_schema')
            schema_url = admin.url.set(username='local_schema')
            runtime_url = admin.url.set(username='local_runtime')
            schema = sa.create_engine(schema_url, poolclass=sa.pool.NullPool, hide_parameters=True)
            runtime = sa.create_engine(runtime_url, poolclass=sa.pool.NullPool, hide_parameters=True)
            try:
                with schema.begin() as connection:
                    command.upgrade(configuration(connection), source_head)
                    installed_tables = set(sa.inspect(connection).get_table_names())
                    previous = {name: grants for name, grants in runtime_privileges.TABLE_PRIVILEGES.items()
                                if name in installed_tables}
                    # Rehearse the privileges of the installed pre-N009 schema,
                    # before new row-lock/reveal column grants are introduced.
                    old_locks = {name: column for name, column in runtime_privileges.LOCK_COLUMNS.items()
                                 if name in installed_tables and name != 'assessment_exercise_version'}
                    with (patch.dict(runtime_privileges.TABLE_PRIVILEGES, previous, clear=True),
                          patch.dict(runtime_privileges.LOCK_COLUMNS, old_locks, clear=True),
                          patch.dict(runtime_privileges.READ_COLUMNS, {}, clear=True)):
                        runtime_privileges.grant_runtime_privileges(connection.connection.driver_connection)
                    connection.exec_driver_sql("INSERT INTO auth_user (username, password, is_superuser, first_name, "
                                               "last_name, email, is_staff, is_active, date_joined) "
                                               "VALUES ('retained', '', false, '', '', '', false, true, now())")
                values = {'MATHSTART_DB_BACKEND': 'postgresql', 'MATHSTART_PUBLIC_ORIGIN': ORIGIN,
                          'MATHSTART_DATABASE_URL': schema_url.render_as_string(hide_password=False),
                          'MATHSTART_SCHEMA_SIGNING_KEY': 'synthetic-local-upgrade-test-only-key'}
                yield schema, runtime, values
            finally:
                schema.dispose()
                runtime.dispose()

    def assert_head(self, schema, expected):
        with schema.connect() as connection:
            self.assertEqual(connection.exec_driver_sql('SELECT version_num FROM alembic_version').scalar_one(), expected)

    def assert_installed_acl(self, schema, runtime):
        self.assert_head(schema, HEAD)
        with runtime.connect() as connection:
            self.assertEqual(connection.exec_driver_sql('SELECT username FROM auth_user').scalar_one(), 'retained')
            for table in READ_TABLES:
                self.assertEqual(connection.exec_driver_sql(f'SELECT count(*) FROM {table}').scalar_one(), 0)
                with self.assertRaises(sa.exc.ProgrammingError) as denied, connection.begin_nested():
                    connection.exec_driver_sql(f'DELETE FROM {table}')
                self.assertEqual(denied.exception.orig.sqlstate, '42501')

    def assert_awaiting_acl(self, schema, runtime):
        self.assert_head(schema, HEAD)
        with runtime.connect() as connection, self.assertRaises(sa.exc.ProgrammingError) as denied:
            connection.exec_driver_sql('SELECT count(*) FROM knowledge_skill')
        self.assertEqual(denied.exception.orig.sqlstate, '42501')

    @contextmanager
    def host_setup(self, local, values):
        state = local / 'installation.json'
        private = local / 'private-env.json'
        host.write_json(state, {'checkout': str(ROOT)})
        host.write_json(local / 'schema-env.json', values)
        historical_plan = local / 'schema.json'
        historical_plan.write_text('{}', encoding='utf-8')
        with host.installation_paths(local, private, state, None), patch.object(host, 'owned_container'):
            yield
        self.assertEqual(historical_plan.read_text(encoding='utf-8'), '{}')

    @staticmethod
    def host_command(action, digest=None, *, profile='TARGET_0003'):
        args = [action, '--profile', profile]
        if digest is not None:
            args += ['--reviewed-plan-sha256', digest]
        return host.main(args)

    def test_host_dev_review_apply_and_runtime_reads(self):
        for source_head, profile in (('v01_0004', 'TARGET_0004'), ('v01_0005', 'TARGET_0005')):
            with (self.subTest(profile=profile), self.installed_database(source_head) as (schema, runtime, values),
                  TemporaryDirectory(dir=TEMP) as directory):
                local = Path(directory)
                filename = f"schema-{profile.lower().replace('_', '-')}.json"
                with self.host_setup(local, values):
                    self.assertEqual(self.host_command('schema-preview', profile=profile), 0)
                    plan = host.read_json(local / filename)
                    self.assertEqual(plan['profile'], profile)
                    self.assertEqual(self.host_command('schema-apply', '0' * 64, profile=profile), 1)
                    self.assertFalse((local / 'schema-apply-pending.json').exists())
                    self.assert_head(schema, source_head)
                    self.assertEqual(self.host_command('schema-apply', release_migrate.plan_digest(plan),
                                                       profile=profile), 0)
                    self.assertFalse((local / 'schema-apply-pending.json').exists())
                self.assert_installed_acl(schema, runtime)

    def test_host_dev_resume_from_applied_receipt_without_ddl(self):
        with self.installed_database('v01_0003') as (schema, runtime, values), TemporaryDirectory(dir=TEMP) as directory:
            local = Path(directory)
            with self.host_setup(local, values):
                self.assertEqual(self.host_command('schema-preview'), 0)
                digest = release_migrate.plan_digest(host.read_json(local / 'schema-target-0003.json'))
                with patch.object(host, 'finish_schema_privileges', side_effect=RuntimeError('Interrupted before ACL')):
                    self.assertEqual(self.host_command('schema-apply', digest), 1)
                self.assert_awaiting_acl(schema, runtime)
                marker = local / 'schema-apply-pending.json'
                receipt = local / 'logs/schema-target-0003-apply.log'
                plan_path = local / 'schema-target-0003.json'
                schema_config = local / 'schema-env.json'
                original = receipt.read_bytes()
                self.assertEqual(host.read_json(receipt)['status'], 'APPLIED')
                with patch.object(host, 'cli', wraps=host.cli) as cli:
                    self.assertEqual(self.host_command('schema-apply', digest), 1)
                    self.assertEqual(self.host_command('finish-acl', '0' * 64), 1)
                    original_plan = plan_path.read_bytes()
                    bad_plan = {**host.read_json(plan_path), 'signature': '0' * 64}
                    plan_path.unlink()
                    host.write_json(plan_path, bad_plan)
                    self.assertEqual(self.host_command('finish-acl', release_migrate.plan_digest(bad_plan)), 1)
                    plan_path.write_bytes(original_plan)
                    original_config = schema_config.read_bytes()
                    schema_config.unlink()
                    host.write_json(schema_config, {**values,
                        'MATHSTART_DATABASE_URL': runtime.url.render_as_string(hide_password=False)})
                    self.assertEqual(self.host_command('finish-acl', digest), 1)
                    schema_config.write_bytes(original_config)
                    receipt.write_text('{}', encoding='utf-8')
                    self.assertEqual(self.host_command('finish-acl', digest), 1)
                    receipt.write_bytes(original)
                    self.assertEqual(self.host_command('finish-acl', digest), 0)
                    self.assertEqual([call.args[1] for call in cli.call_args_list], [['check']])
                self.assertEqual(receipt.read_bytes(), original)
                self.assertFalse(marker.exists())
            self.assert_installed_acl(schema, runtime)

    @contextmanager
    def compose_setup(self, local, values, source_head):
        state = local / 'state.json'
        schema = local / 'schema-env.json'
        private = local / 'api-env.json'
        secrets = local / 'secrets.json'
        review = local / 'review.json'
        runtime_work = local / 'runtime-work'
        runtime_work.mkdir()
        host.write_json(schema, values)
        host.write_json(private, {'MATHSTART_PUBLIC_ORIGIN': ORIGIN})
        host.write_json(secrets, {})
        migrations = compose.migration_files()
        previous = {name: digest for name, digest in migrations.items()
                    if Path(name).name.split('_', 2)[:2] <= source_head.split('_')}
        installed = {'version': 1, 'schema_code': 'previous-schema-code', 'applied_migrations': previous,
                     'release': 'dev-retained', 'content_digest': 'retained-content',
                     'dev_content_digest': 'retained-dev-content', 'work': None}
        host.write_json(state, installed)
        with ExitStack() as stack:
            stack.enter_context(patch.multiple(compose, LOCAL=local, STATE=state, SCHEMA=schema,
                                PRIVATE=private, SECRETS=secrets, REVIEW=review, RUNTIME_WORK=runtime_work))
            if os.name == 'nt':
                # Docker creates the log link on Linux. A native Windows test runner may lack that privilege.
                stack.enter_context(patch.object(Path, 'symlink_to', autospec=True,
                    side_effect=lambda link, *args, **kwargs: link.mkdir()))
            compose.check_public_origin()
            yield installed, migrations

    def assert_compose_complete(self, installed, migrations):
        current = compose.read(compose.STATE)
        self.assertEqual(current['schema_code'], release_migrate.code_digest())
        self.assertEqual(current['applied_migrations'], migrations)
        for key in ('release', 'work', 'content_digest', 'dev_content_digest'):
            self.assertEqual(current[key], installed[key])
        self.assertFalse(compose.REVIEW.exists())
        self.assertEqual(compose.pending_schema_work(current), [])

    def test_compose_review_apply_and_runtime_reads(self):
        for source_head, profile in (('v01_0004', 'TARGET_0004'), ('v01_0005', 'TARGET_0005')):
            with (self.subTest(profile=profile), self.installed_database(source_head) as (schema, runtime, values),
                  TemporaryDirectory(dir=TEMP) as directory):
                with self.compose_setup(Path(directory), values, source_head) as (installed, migrations):
                    self.assertEqual(compose.schema_update(SimpleNamespace(schema_digest=None)), 42)
                    review = compose.read(compose.REVIEW)
                    self.assertEqual(review['summary']['profile'], profile)
                    self.assertEqual(compose.schema_update(SimpleNamespace(schema_digest='0' * 64)), 42)
                    self.assert_head(schema, source_head)
                    self.assertEqual(compose.schema_update(SimpleNamespace(schema_digest=review['digest'])), 0)
                    self.assert_compose_complete(installed, migrations)
                self.assert_installed_acl(schema, runtime)

    def test_compose_resume_updates_installer_metadata_without_ddl(self):
        with self.installed_database('v01_0003') as (schema, runtime, values), TemporaryDirectory(dir=TEMP) as directory:
            with self.compose_setup(Path(directory), values, 'v01_0003') as (installed, migrations):
                self.assertEqual(compose.schema_update(SimpleNamespace(schema_digest=None)), 42)
                args = SimpleNamespace(schema_digest=compose.read(compose.REVIEW)['digest'])
                with patch.object(host, 'finish_schema_privileges', side_effect=RuntimeError('Interrupted before ACL')):
                    with self.assertRaisesRegex(RuntimeError, 'Interrupted before ACL'):
                        compose.schema_update(args)
                self.assert_awaiting_acl(schema, runtime)
                current = compose.read(compose.STATE)
                self.assertEqual(current['schema_code'], installed['schema_code'])
                self.assertEqual(current['applied_migrations'], installed['applied_migrations'])
                receipt = Path(current['schema_work']['path']) / 'logs/schema-apply.log'
                self.assertEqual(compose.read(receipt)['status'], 'APPLIED')
                original = receipt.read_bytes()
                with patch.object(host, 'cli', wraps=host.cli) as cli:
                    with self.assertRaisesRegex(RuntimeError, 'pending; use finish-acl'):
                        compose.schema_update(args)
                    with self.assertRaisesRegex(RuntimeError, 'exact reviewed plan'):
                        compose.finish_acl(SimpleNamespace(schema_digest='0' * 64))
                    self.assertEqual(compose.finish_acl(args), 0)
                    self.assertEqual([call.args[1] for call in cli.call_args_list], [['check']])
                self.assertEqual(receipt.read_bytes(), original)
                self.assert_compose_complete(installed, migrations)
            self.assert_installed_acl(schema, runtime)
