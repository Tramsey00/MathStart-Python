"""Explicit privileges for the isolated local runtime after a reviewed schema apply."""
from psycopg import sql

ROLE = 'local_runtime'
TABLE_PRIVILEGES = {
    # Staff manage users, groups, and their relationship rows.
    **dict.fromkeys(('auth_user', 'auth_group'), 'SELECT, INSERT, UPDATE, DELETE'),
    **dict.fromkeys(('auth_user_groups', 'auth_user_user_permissions', 'auth_group_permissions',
                     'django_admin_log'), 'SELECT, INSERT, DELETE'),
    # The staff deletion collector locks referenced permission and content-type
    # rows with SELECT FOR UPDATE, which needs UPDATE on at least one column.
    # Grant only a non-PK field on each table; keep the original lock strength.
    'auth_permission': 'SELECT',
    'django_content_type': 'SELECT',
    # Runtime writes use row locks, including idempotency and login throttling.
    **dict.fromkeys(('users_studentprofile', 'users_identityreceipt', 'users_loginwindow',
                     'target_receipt_bridge'), 'SELECT, INSERT, UPDATE'),
    'target_session': 'SELECT, INSERT, UPDATE, DELETE',
    # The publication authority uses the separate schema role for writes.
    **dict.fromkeys(('content_grade', 'content_subject', 'content_section', 'content_contentpage',
                     'content_lessonpublication', 'content_mediaasset', 'content_redirect',
                     'target_publication_journal', 'target_publication_gate', 'target_active_release',
                     'target_identity_cutover', 'django_session', 'django_migrations'), 'SELECT'),
}
LOCK_COLUMNS = {'auth_permission': 'name', 'django_content_type': 'model'}
TABLE_RIGHTS = ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'REFERENCES', 'TRIGGER')
SEQUENCE_RIGHTS = ('USAGE', 'SELECT', 'UPDATE')


def grant_runtime_privileges(connection):
    # PostgreSQL identity columns generate values as part of INSERT and do not
    # require an independent sequence grant. This also denies nextval/setval.
    connection.execute(sql.SQL('REVOKE TEMPORARY ON DATABASE {} FROM PUBLIC').format(
        sql.Identifier(connection.info.dbname)))
    for table, privileges in TABLE_PRIVILEGES.items():
        connection.execute(sql.SQL('GRANT {} ON TABLE public.{} TO {}').format(
            sql.SQL(privileges), sql.Identifier(table), sql.Identifier(ROLE)))
    for table, column in LOCK_COLUMNS.items():
        connection.execute(sql.SQL('GRANT UPDATE ({}) ON TABLE public.{} TO {}').format(
            sql.Identifier(column), sql.Identifier(table), sql.Identifier(ROLE)))
    check_runtime_privileges(connection)


def check_runtime_privileges(connection):
    allowed, = connection.execute("""
        SELECT NOT (r.rolsuper OR r.rolcreatedb OR r.rolcreaterole OR r.rolreplication
                    OR r.rolbypassrls)
           AND NOT EXISTS (SELECT 1 FROM pg_auth_members WHERE member = r.oid)
           AND NOT EXISTS (SELECT 1 FROM pg_database WHERE datdba = r.oid)
           AND NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspowner = r.oid)
           AND NOT EXISTS (SELECT 1 FROM pg_class WHERE relowner = r.oid)
           AND NOT has_database_privilege(r.oid, current_database(), 'CREATE')
           AND NOT has_database_privilege(r.oid, current_database(), 'TEMP')
           AND NOT EXISTS (SELECT 1 FROM pg_namespace WHERE has_schema_privilege(r.oid, oid, 'CREATE'))
           AND has_database_privilege(r.oid, current_database(), 'CONNECT')
           AND has_schema_privilege(r.oid, 'public', 'USAGE')
        FROM pg_roles r WHERE r.rolname = %s
    """, (ROLE,)).fetchone()
    if not allowed:
        raise RuntimeError('Unsafe local_runtime role, ownership or DDL privileges')
    tables = connection.execute("""
        SELECT c.relname, p.right, has_table_privilege(%s, c.oid, p.right)
        FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        CROSS JOIN unnest(%s::text[]) AS p(right)
        WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
    """, (ROLE, list(TABLE_RIGHTS)))
    seen = set()
    for table, right, actual in tables:
        seen.add(table)
        if actual != (right in TABLE_PRIVILEGES.get(table, '').split(', ')):
            raise RuntimeError(f'Unexpected local_runtime table privilege: {table} {right}')
    if TABLE_PRIVILEGES.keys() - seen or 'alembic_version' not in seen:
        raise RuntimeError('Missing tables in local_runtime privilege audit')
    columns = connection.execute("""
        SELECT c.relname, a.attname, p.right, has_column_privilege(%s, c.oid, a.attnum, p.right)
        FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum > 0 AND NOT a.attisdropped
        CROSS JOIN unnest(ARRAY['INSERT','UPDATE','REFERENCES']) AS p(right)
        WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
    """, (ROLE,))
    for table, column, right, actual in columns:
        expected = right in TABLE_PRIVILEGES.get(table, '').split(', ')
        expected |= right == 'UPDATE' and LOCK_COLUMNS.get(table) == column
        if actual != expected:
            raise RuntimeError(f'Unexpected local_runtime column privilege: {table}.{column} {right}')
    sequences, = connection.execute("""
        SELECT EXISTS (
            SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            CROSS JOIN unnest(%s::text[]) AS p(right)
            WHERE n.nspname = 'public' AND c.relkind = 'S' AND has_sequence_privilege(%s, c.oid, p.right)
        )
    """, (list(SEQUENCE_RIGHTS), ROLE)).fetchone()
    if sequences:
        raise RuntimeError('Unexpected local_runtime sequence privilege')
