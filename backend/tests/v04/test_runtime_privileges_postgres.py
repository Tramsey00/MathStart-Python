"""Opt-in live ACL checks. Use a dedicated PostgreSQL cluster with an empty V01 fixture DB."""
import os
from pathlib import Path
import secrets
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import sqlalchemy as sa

from backend.migrations.runtime_privileges import check_runtime_privileges, grant_runtime_privileges
from backend.migrations.upgrade import fresh, require_disposable
from backend.release_migrate import plan_digest, preview
from scripts import team_local


@unittest.skipUnless(os.environ.get('MATHSTART_ACL_TEST_DSN'), 'Requires a dedicated disposable PostgreSQL fixture')
class PostgresRuntimePrivilegesTests(unittest.TestCase):
    def setUp(self):
        url = sa.engine.make_url(os.environ['MATHSTART_ACL_TEST_DSN'])
        self.values = {
            'MATHSTART_DATABASE_URL': url.set(drivername='postgresql+psycopg').render_as_string(hide_password=False),
            'MATHSTART_SCHEMA_SIGNING_KEY': secrets.token_urlsafe(48),
        }
        self.engine = sa.create_engine(self.values['MATHSTART_DATABASE_URL'],
                                       poolclass=sa.pool.NullPool, hide_parameters=True)
        self.addCleanup(self.engine.dispose)
        with self.engine.connect() as connection:
            require_disposable(connection)
            self.assertEqual(connection.exec_driver_sql('SHOW server_version_num').scalar_one()[:2], '16')
            self.assertEqual(sa.inspect(connection).get_table_names(), [])

    def test_effective_runtime_contract(self):
        # Real PostgreSQL must parse and execute all three effective ACL queries.
        engine = self.engine
        with engine.connect() as connection, connection.begin() as transaction:
            require_disposable(connection)
            connection.exec_driver_sql('CREATE ROLE local_runtime NOLOGIN')
            fresh(connection)
            raw = connection.connection.driver_connection
            grant_runtime_privileges(raw)
            connection.exec_driver_sql("INSERT INTO django_content_type (id, app_label, model) VALUES (1, 'auth', 'user')")
            connection.exec_driver_sql("INSERT INTO auth_permission (id, name, content_type_id, codename) VALUES (1, 'Test', 1, 'test')")
            connection.exec_driver_sql('SET LOCAL ROLE local_runtime')
            for table in ('auth_permission', 'django_content_type'):
                self.assertEqual(connection.exec_driver_sql(f'SELECT id FROM {table} FOR UPDATE').scalar_one(), 1)
            for table, column in (('auth_permission', 'name'), ('django_content_type', 'model')):
                updated = connection.exec_driver_sql(
                    f"UPDATE {table} SET {column} = 'acl_edited' WHERE id = 1 RETURNING {column}"
                ).scalar_one()
                self.assertEqual(updated, 'acl_edited')
            group_id = connection.exec_driver_sql("INSERT INTO auth_group (name) VALUES ('acl test') RETURNING id").scalar_one()
            self.assertEqual(connection.exec_driver_sql(
                'SELECT name FROM auth_group WHERE id = %s', (group_id,)).scalar_one(), 'acl test')
            self.assertEqual(connection.exec_driver_sql(
                "UPDATE auth_group SET name = 'acl edited' WHERE id = %s RETURNING name", (group_id,)).scalar_one(),
                'acl edited')
            self.assertEqual(connection.exec_driver_sql(
                'DELETE FROM auth_group WHERE id = %s RETURNING id', (group_id,)).scalar_one(), group_id)
            connection.exec_driver_sql('SELECT id FROM django_migrations')
            connection.exec_driver_sql('SELECT release_id FROM target_active_release')
            for statement in (
                'UPDATE auth_permission SET id = 2', 'UPDATE django_content_type SET id = 2',
                'DELETE FROM alembic_version', 'DELETE FROM django_migrations',
                'SELECT * FROM target_publication_history',
                'CREATE TABLE public.acl_forbidden (id integer)', 'CREATE TEMP TABLE acl_forbidden (id integer)',
                'ALTER TABLE auth_group ADD COLUMN forbidden integer',
                "SELECT nextval('auth_group_id_seq')", "SELECT setval('auth_group_id_seq', 99)",
            ):
                with self.subTest(statement=statement), self.assertRaises(sa.exc.ProgrammingError) as error:
                    with connection.begin_nested():
                        connection.exec_driver_sql(statement)
                self.assertEqual(error.exception.orig.sqlstate, '42501')
            transaction.rollback()

    def test_finish_acl_after_committed_schema_and_failed_grant_check(self):
        with self.engine.begin() as connection:
            connection.exec_driver_sql('CREATE ROLE local_runtime NOLOGIN')

        key = self.values['MATHSTART_SCHEMA_SIGNING_KEY']
        plan = preview(self.engine, key, 'FRESH')
        digest = plan_digest(plan)
        with TemporaryDirectory() as directory:
            local = Path(directory)
            config = local / 'schema-env.json'
            team_local.write_json(config, self.values)
            team_local.write_json(local / 'schema.json', plan)
            with team_local.installation_paths(local, config, local / 'installation.json', None):
                marker = local / 'schema-apply-pending.json'
                receipt = local / 'logs/schema-apply.log'
                with patch('backend.migrations.runtime_privileges.check_runtime_privileges',
                           side_effect=RuntimeError('Synthetic ACL check failure')) as failing_check:
                    with self.assertRaisesRegex(RuntimeError, 'Schema APPLIED; runtime ACL completion failed'):
                        team_local.schema_apply(self.values, digest)
                    failing_check.assert_called_once()
                self.assertEqual(team_local.read_json(marker), {'reviewed_plan_sha256': digest})
                applied = team_local.read_json(receipt)
                self.assertEqual(applied, {'status': 'APPLIED', 'head': 'v01_0002', 'reviewed_plan_sha256': digest})
                with self.engine.connect() as connection:
                    revision = connection.exec_driver_sql('SELECT version_num FROM alembic_version').scalar_one()
                    self.assertEqual(revision, 'v01_0002')
                    self.assertFalse(connection.exec_driver_sql(
                        "SELECT has_table_privilege('local_runtime', 'auth_group', 'INSERT')").scalar_one())

                with patch.object(team_local, 'cli', wraps=team_local.cli) as cli:
                    with self.assertRaisesRegex(RuntimeError, 'do not rerun DDL'):
                        team_local.schema_apply(self.values, digest)
                    with self.assertRaisesRegex(RuntimeError, 'exact reviewed plan'):
                        team_local.finish_schema_privileges(self.values, '0' * 64)
                    cli.assert_not_called()
                    team_local.finish_schema_privileges(self.values, digest)
                    cli.assert_called_once_with('backend.release_migrate', ['check'], 'schema-check', self.values)

                self.assertEqual(team_local.read_json(receipt), applied)
                with self.engine.connect() as connection:
                    check_runtime_privileges(connection.connection.driver_connection)
                    self.assertEqual(connection.exec_driver_sql('SELECT version_num FROM alembic_version').scalar_one(),
                                     revision)
