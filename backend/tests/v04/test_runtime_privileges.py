import unittest
from unittest.mock import Mock

from backend.migrations.runtime_privileges import (
    TABLE_PRIVILEGES, TABLE_RIGHTS, check_runtime_privileges, grant_runtime_privileges,
)


class RuntimePrivilegesTests(unittest.TestCase):
    def connection(self, *, safe_role=True, extra_table_right=None, extra_column_right=None, sequence=False):
        connection = Mock()
        tables = [*TABLE_PRIVILEGES, 'alembic_version', 'target_publication_history']
        rights = [(table, right, right in TABLE_PRIVILEGES.get(table, '').split(', ')
                   or (table, right) == extra_table_right)
                  for table in tables for right in TABLE_RIGHTS]
        columns = [('django_content_type', 'model', 'UPDATE', True),
                   ('auth_permission', 'name', 'UPDATE', True),
                   ('django_migrations', 'id', 'UPDATE', extra_column_right == 'django_migrations'),
                   ('auth_permission', 'id', 'UPDATE', extra_column_right == 'auth_permission'),
                   ('django_content_type', 'id', 'UPDATE', extra_column_right == 'django_content_type')]
        connection.execute.side_effect = [Mock(fetchone=Mock(return_value=(safe_role,))), rights, columns,
                                          Mock(fetchone=Mock(return_value=(sequence,)))]
        return connection

    def test_accepts_effective_least_privilege_policy(self):
        check_runtime_privileges(self.connection())
        self.assertEqual(TABLE_PRIVILEGES['django_migrations'], 'SELECT')
        self.assertNotIn('alembic_version', TABLE_PRIVILEGES)
        self.assertNotIn('target_publication_history', TABLE_PRIVILEGES)
        self.assertEqual(TABLE_PRIVILEGES['target_active_release'], 'SELECT')
        self.assertEqual(TABLE_PRIVILEGES['target_publication_journal'], 'SELECT')

    def test_rejects_ddl_and_migration_history_writes(self):
        cases = [
            ({'safe_role': False}, 'DDL privileges'),
            ({'extra_table_right': ('alembic_version', 'DELETE')}, 'alembic_version DELETE'),
            ({'extra_table_right': ('django_migrations', 'TRUNCATE')}, 'django_migrations TRUNCATE'),
            ({'extra_column_right': 'django_migrations'}, 'django_migrations.id UPDATE'),
            ({'extra_column_right': 'auth_permission'}, 'auth_permission.id UPDATE'),
            ({'extra_column_right': 'django_content_type'}, 'django_content_type.id UPDATE'),
            ({'sequence': True}, 'sequence privilege'),
        ]
        for options, error in cases:
            with self.subTest(options=options), self.assertRaisesRegex(RuntimeError, error):
                check_runtime_privileges(self.connection(**options))

    def test_emits_scoped_grants_before_effective_acl_checks(self):
        from unittest.mock import patch
        connection = Mock()
        connection.info.dbname = 'mathstart_dev'
        with patch('backend.migrations.runtime_privileges.check_runtime_privileges') as verify:
            grant_runtime_privileges(connection)
        verify.assert_called_once_with(connection)
        statements = [call.args[0].as_string() for call in connection.execute.call_args_list]
        self.assertEqual(statements[0], 'REVOKE TEMPORARY ON DATABASE "mathstart_dev" FROM PUBLIC')
        self.assertEqual(len(statements), 1 + len(TABLE_PRIVILEGES) + 2)
        self.assertFalse(any('ALL TABLES' in sql or 'ALL SEQUENCES' in sql or 'alembic_version' in sql
                             for sql in statements))
