"""Opt-in live ACL checks. Use a dedicated PostgreSQL cluster with an empty V01 fixture DB."""
import os
import unittest

import psycopg
import sqlalchemy as sa

from backend.migrations.runtime_privileges import grant_runtime_privileges
from backend.migrations.upgrade import fresh, require_disposable


@unittest.skipUnless(os.environ.get('MATHSTART_ACL_TEST_DSN'), 'Requires a dedicated disposable PostgreSQL fixture')
class PostgresRuntimePrivilegesTests(unittest.TestCase):
    def test_effective_runtime_contract(self):
        dsn = os.environ['MATHSTART_ACL_TEST_DSN']
        engine = sa.create_engine(sa.URL.create('postgresql+psycopg'),
                                  creator=lambda: psycopg.connect(dsn), hide_parameters=True)
        self.addCleanup(engine.dispose)
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
            connection.exec_driver_sql("INSERT INTO auth_group (name) VALUES ('acl test')")
            connection.exec_driver_sql("UPDATE auth_group SET name = 'acl edited' WHERE name = 'acl test'")
            connection.exec_driver_sql("DELETE FROM auth_group WHERE name = 'acl edited'")
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
