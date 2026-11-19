"""N008->N009 Compose schema-update/finish-acl on an owned PG server, no Docker."""
from contextlib import contextmanager
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.engine import make_url

from backend import release_migrate
from backend.migrations import runtime_privileges
from backend.tests import test_local_schema_upgrade_postgres as local_checks
from scripts import container_dev as compose, team_local as host

ADMIN = os.getenv('MATHSTART_N009_TEST_ADMIN_URL')
TEMP = local_checks.TEMP


class OwnedDatabases:
    def __init__(self, admin, url):
        self.admin, self.url = admin, url

    @contextmanager
    def database(self):
        name = 'test_ms7_mig_v01_' + uuid4().hex
        with self.admin.connect() as connection:
            connection.exec_driver_sql('CREATE DATABASE ' + name)
            connection.exec_driver_sql("COMMENT ON DATABASE " + name + " IS 'MS7-MIG-V01 disposable synthetic test database'")
        engine = sa.create_engine(self.url.set(database=name), hide_parameters=True)
        try:
            yield engine
        finally:
            engine.dispose()
            with self.admin.connect() as connection:
                connection.exec_driver_sql('DROP DATABASE ' + name + ' WITH (FORCE)')


@unittest.skipUnless(ADMIN, 'Requires explicitly owned MS-N009 PostgreSQL server')
class N009ComposeUpgradeTests(unittest.TestCase):
    # Reuse the actual Compose/host operator fixture, not a reimplementation.
    installed_database = local_checks.LocalSchemaUpgradeTests.installed_database
    compose_setup = local_checks.LocalSchemaUpgradeTests.compose_setup
    assert_head = local_checks.LocalSchemaUpgradeTests.assert_head
    assert_compose_complete = local_checks.LocalSchemaUpgradeTests.assert_compose_complete

    @classmethod
    def setUpClass(cls):
        url = make_url(ADMIN)
        if (url.drivername, url.host, url.database) != ('postgresql+psycopg', '127.0.0.1', 'postgres') or not url.port:
            raise RuntimeError('Refusing unreserved endpoint')
        cls.admin = sa.create_engine(url, isolation_level='AUTOCOMMIT', hide_parameters=True, connect_args={'connect_timeout': 5})
        cls.addClassCleanup(cls.admin.dispose)
        with cls.admin.connect() as connection:
            if connection.scalar(sa.text("SELECT shobj_description(oid,'pg_database') FROM pg_database WHERE datname=current_database()")) != 'MS-N009 disposable PostgreSQL server':
                raise RuntimeError('Missing owned N009 server marker')
            for role in ('local_schema', 'local_runtime'):
                connection.exec_driver_sql(f'CREATE ROLE {role} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE')
                cls.addClassCleanup(cls.drop_role, role)
        cls.fixture = OwnedDatabases(cls.admin, url)
        TEMP.mkdir(parents=True, exist_ok=True)

    @classmethod
    def drop_role(cls, role):
        with cls.admin.connect() as connection:
            connection.exec_driver_sql(f'DROP ROLE {role}')

    def assert_n009_acl(self, schema, runtime):
        self.assert_head(schema, 'v01_0007')
        with schema.begin() as connection:
            runtime_privileges.check_runtime_privileges(connection.connection.driver_connection)
        with runtime.connect() as connection:
            self.assertEqual(connection.exec_driver_sql('SELECT username FROM auth_user').scalar_one(), 'retained')
            for name in ('assessment_attempt', 'assessment_exposure', 'assessment_action', 'assessment_attempt_event',
                         'assessment_solution_step', 'assessment_reviewed_hint'):
                self.assertEqual(connection.exec_driver_sql('SELECT count(*) FROM ' + name).scalar_one(), 0)
            self.assertFalse(connection.scalar(sa.text("SELECT has_column_privilege(current_user,'assessment_exercise_validation','validation_spec','SELECT')")))
            self.assertTrue(connection.scalar(sa.text("SELECT has_column_privilege(current_user,'assessment_exercise_validation','canonical_solution','SELECT')")))
            self.assertFalse(connection.scalar(sa.text("SELECT has_table_privilege(current_user,'assessment_action','UPDATE')")))

    def test_compose_n008_schema_update_review_apply_and_acl(self):
        with self.installed_database('v01_0006') as (schema, runtime, values), TemporaryDirectory(dir=TEMP) as directory:
            with self.compose_setup(Path(directory), values, 'v01_0006') as (installed, migrations):
                self.assertEqual(compose.schema_update(SimpleNamespace(schema_digest=None)), 42)
                review = compose.read(compose.REVIEW)
                self.assertEqual(review['summary']['profile'], 'TARGET_0006')
                self.assertEqual(review['summary']['target_head'], 'v01_0007')
                self.assertEqual(compose.schema_update(SimpleNamespace(schema_digest='0' * 64)), 42)
                self.assert_head(schema, 'v01_0006')
                self.assertEqual(compose.schema_update(SimpleNamespace(schema_digest=review['digest'])), 0)
                self.assert_compose_complete(installed, migrations)
            self.assert_n009_acl(schema, runtime)

    def test_compose_n008_finish_acl_recovers_without_ddl_or_publication(self):
        with self.installed_database('v01_0006') as (schema, runtime, values), TemporaryDirectory(dir=TEMP) as directory:
            with self.compose_setup(Path(directory), values, 'v01_0006') as (installed, migrations):
                self.assertEqual(compose.schema_update(SimpleNamespace(schema_digest=None)), 42)
                args = SimpleNamespace(schema_digest=compose.read(compose.REVIEW)['digest'])
                with patch.object(host, 'finish_schema_privileges', side_effect=RuntimeError('Interrupted before ACL')):
                    with self.assertRaisesRegex(RuntimeError, 'Interrupted before ACL'):
                        compose.schema_update(args)
                self.assert_head(schema, 'v01_0007')
                with runtime.connect() as connection, self.assertRaises(sa.exc.ProgrammingError):
                    connection.exec_driver_sql('SELECT count(*) FROM assessment_attempt')
                current = compose.read(compose.STATE)
                receipt = Path(current['schema_work']['path']) / 'logs/schema-apply.log'
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
            self.assert_n009_acl(schema, runtime)
