"""Read-only PostgreSQL inventory and strict baseline/profile compatibility."""
from copy import deepcopy
import json
from pathlib import Path
import sqlalchemy as sa
from alembic.config import Config
from alembic.script import ScriptDirectory
from backend.models.baseline import SNAPSHOT


class SchemaMismatch(RuntimeError):
    pass


def assert_revision_graph():
    try:
        script = ScriptDirectory.from_config(Config(str(Path(__file__).parents[1] / 'alembic.ini')))
        if script.get_heads() != ['v01_0002'] or {
                revision.revision: revision.down_revision for revision in script.walk_revisions()
        } != {'v01_0001': None, 'v01_0002': 'v01_0001'}:
            raise SchemaMismatch('Unknown/ambiguous Alembic revision graph')
    except SchemaMismatch:
        raise
    except Exception as error:
        raise SchemaMismatch('Invalid Alembic revision graph') from error


def assert_tracking(connection, actual, *, require_target_head):
    """Exact tracking shape plus cardinality/state; never repair or adopt drift."""
    assert_revision_graph()
    if 'alembic_version' not in actual['tables']:
        if require_target_head:
            raise SchemaMismatch('Missing Alembic tracking table/head')
        return
    expected = {
        'columns': [{'table_name': 'alembic_version', 'column_name': 'version_num',
                     'data_type': 'character varying', 'udt_name': 'varchar', 'is_nullable': 'NO',
                     'column_default': None, 'character_maximum_length': 32, 'datetime_precision': None}],
        'constraints': [{'table_name': 'alembic_version', 'name': 'alembic_version_pkc',
                         'type': 'p', 'definition': 'PRIMARY KEY (version_num)'}],
        'indexes': [{'tablename': 'alembic_version', 'indexname': 'alembic_version_pkc',
                     'indexdef': 'CREATE UNIQUE INDEX alembic_version_pkc ON public.alembic_version USING btree (version_num)'}],
        'identity_columns': [],
    }
    for key, table_key in [('columns', 'table_name'), ('constraints', 'table_name'),
                           ('indexes', 'tablename'), ('identity_columns', 'table_name')]:
        observed = [row for row in actual[key] if row[table_key] == 'alembic_version']
        if sorted(observed, key=str) != sorted(expected[key], key=str):
            raise SchemaMismatch('Alembic tracking schema drift: ' + key)
    revisions = list(connection.scalars(sa.text('SELECT version_num FROM alembic_version ORDER BY version_num')))
    # An unmanaged legacy fixture may have a canonical empty tracking table.
    # Target schema proof requires exactly its owning chain's current head.
    expected_revisions = ['v01_0002'] if require_target_head else []
    if revisions != expected_revisions:
        raise SchemaMismatch('Unknown/ambiguous/inapplicable Alembic tracking state')


def inventory(connection):
    if connection.dialect.name != 'postgresql':
        raise SchemaMismatch('Upgrade/schema acceptance requires PostgreSQL')
    queries = {
        'columns': """SELECT table_name,column_name,data_type,udt_name,is_nullable,column_default,
            character_maximum_length,datetime_precision FROM information_schema.columns
            WHERE table_schema='public' ORDER BY table_name,ordinal_position""",
        'constraints': """SELECT t.relname table_name,c.conname name,c.contype type,
            pg_get_constraintdef(c.oid) definition FROM pg_constraint c
            JOIN pg_class t ON t.oid=c.conrelid JOIN pg_namespace n ON n.oid=t.relnamespace
            WHERE n.nspname='public' ORDER BY t.relname,c.conname""",
        'indexes': """SELECT tablename,indexname,indexdef FROM pg_indexes
            WHERE schemaname='public' ORDER BY tablename,indexname""",
        'identity_columns': """SELECT t.relname table_name,a.attname column_name,a.attidentity identity_kind,
            pg_get_serial_sequence('public.'||t.relname,a.attname) owned_sequence
            FROM pg_class t JOIN pg_namespace n ON n.oid=t.relnamespace
            JOIN pg_attribute a ON a.attrelid=t.oid
            WHERE n.nspname='public' AND t.relkind='r' AND a.attnum>0 AND NOT a.attisdropped
            AND (a.attidentity<>'' OR pg_get_serial_sequence('public.'||t.relname,a.attname) IS NOT NULL)
            ORDER BY t.relname,a.attname""",
        'sequences': """SELECT schemaname,sequencename,data_type,start_value,min_value,max_value,
            increment_by,cycle,cache_size,last_value FROM pg_sequences
            WHERE schemaname='public' ORDER BY sequencename""",
        'unexpected_objects': """SELECT 'schema' kind,nspname name FROM pg_namespace
            WHERE nspname NOT IN ('public','information_schema') AND nspname NOT LIKE 'pg_%'
            UNION ALL SELECT 'relation',c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname='public' AND c.relkind IN ('v','m','f')
            UNION ALL SELECT 'trigger',t.tgname FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND NOT t.tgisinternal
            UNION ALL SELECT 'routine',p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
            WHERE n.nspname='public' ORDER BY kind,name""",
    }
    result = {key: [dict(row) for row in connection.execute(sa.text(query)).mappings()] for key, query in queries.items()}
    result['tables'] = sorted(sa.inspect(connection).get_table_names(schema='public'))
    result['migrations'] = []
    if 'django_migrations' in result['tables']:
        result['migrations'] = [dict(row) for row in connection.execute(sa.text('SELECT app,name FROM django_migrations ORDER BY app,name')).mappings()]
    return result


def expected_profile(profile):
    result = deepcopy(SNAPSHOT['physical_baseline'])
    result['identity_columns'] = deepcopy(SNAPSHOT['fresh_disposable_sequence_evidence']['identity_columns'])
    result['sequences'] = deepcopy(SNAPSHOT['fresh_disposable_sequence_evidence']['sequences'])
    if profile == 'A':
        result['columns'] = [x for x in result['columns'] if not x['table_name'].startswith('users_')
                             and (x['table_name'], x['column_name']) != ('content_grade', 'created_at')]
        result['constraints'] = [x for x in result['constraints'] if not x['table_name'].startswith('users_')]
        result['indexes'] = [x for x in result['indexes'] if not x['tablename'].startswith('users_')]
        result['migrations'] = [x for x in result['migrations'] if x['app'] != 'users'
                                and (x['app'], x['name']) != ('content', '0002_grade_created_at')]
    elif profile not in {'B', 'C', 'FRESH'}:
        raise SchemaMismatch('Unknown upgrade profile')
    result['tables'] = sorted({x['table_name'] for x in result['columns']})
    return result


def normalized(record, key):
    value = dict(record)
    if key == 'sequences':
        value.pop('last_value', None)  # deployment data, not structural equality
    return value


def assert_baseline(connection, profile, *, allow_protocol=False, require_history=True):
    expected, actual = expected_profile(profile), inventory(connection)
    assert_tracking(connection, actual, require_target_head=allow_protocol)
    baseline_tables = set(expected['tables'])
    allowed = baseline_tables | {'alembic_version'}
    if allow_protocol:
        from backend.models.protocol import PROTOCOL_TABLES
        allowed |= {t.name for t in PROTOCOL_TABLES}
    if actual['unexpected_objects']:
        raise SchemaMismatch('Unknown schema objects')
    if set(actual['tables']) - allowed or baseline_tables - set(actual['tables']):
        raise SchemaMismatch('Unknown/missing table set')
    for key, table_key in [('columns', 'table_name'), ('constraints', 'table_name'), ('indexes', 'tablename'), ('identity_columns', 'table_name')]:
        observed = [x for x in actual[key] if x[table_key] in baseline_tables]
        # Catalog output is canonical PostgreSQL SQL. Keep expressions/actions/
        # nullability/precision exact rather than hiding drift in autogenerate.
        if sorted(observed, key=str) != sorted(expected[key], key=str):
            raise SchemaMismatch('Baseline schema drift: ' + key)
    names = {x['sequencename'] for x in expected['sequences']}
    observed = [normalized(x, 'sequences') for x in actual['sequences'] if x['sequencename'] in names]
    wanted = [normalized(x, 'sequences') for x in expected['sequences']]
    if sorted(observed, key=str) != sorted(wanted, key=str):
        raise SchemaMismatch('Baseline sequence drift')
    if require_history and actual['migrations'] != expected['migrations']:
        raise SchemaMismatch('Unknown or incomplete Django migration head/history')
    allowed_sequences = names
    if allow_protocol:
        target = json.loads(Path(__file__).with_name('protocol-schema-v1.json').read_text(encoding='utf-8'))
        target_tables = set(target['tables'])
        if not target_tables <= set(actual['tables']):
            raise SchemaMismatch('Missing additive protocol tables')
        for key, table_key in [('columns', 'table_name'), ('constraints', 'table_name'),
                               ('indexes', 'tablename'), ('identity_columns', 'table_name')]:
            observed = [row for row in actual[key] if row[table_key] in target_tables]
            if sorted(observed, key=str) != sorted(target[key], key=str):
                raise SchemaMismatch('Additive protocol schema drift: ' + key)
        target_sequences = {row['sequencename'] for row in target['sequences']}
        observed = [normalized(row, 'sequences') for row in actual['sequences'] if row['sequencename'] in target_sequences]
        if sorted(observed, key=str) != sorted(target['sequences'], key=str):
            raise SchemaMismatch('Additive protocol sequence drift')
        allowed_sequences |= target_sequences
    if {row['sequencename'] for row in actual['sequences']} != allowed_sequences:
        raise SchemaMismatch('Unknown/missing sequence set')
    return actual
