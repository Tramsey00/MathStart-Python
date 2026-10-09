"""Disposable rehearsal adapter; stamp only after a complete compatibility check.

The application does not acquire production DDL ownership with this command.
No history row is synthesized or rewritten to claim Django applied target DDL.
"""
from pathlib import Path
import uuid
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from backend.models.baseline import metadata, SNAPSHOT, GRADE_EPOCH, utc_now
from backend.models.protocol import PROTOCOL_TABLES
from .schema import assert_baseline, assert_revision_graph, SchemaMismatch, inventory

HEAD = 'v01_0002'
BASE = 'v01_0001'


def configuration(connection):
    assert_revision_graph()
    config = Config(str(Path(__file__).parents[1] / 'alembic.ini'))
    config.attributes['connection'] = connection
    config.attributes['v01_checked'] = True
    if ScriptDirectory.from_config(config).get_heads() != [HEAD]:
        raise SchemaMismatch('Unknown/multiple Alembic chain heads')
    return config


def require_disposable(connection):
    if connection.dialect.name == 'postgresql':
        name = connection.scalar(sa.text('SELECT current_database()'))
        marker = connection.scalar(sa.text("SELECT shobj_description(oid,'pg_database') FROM pg_database WHERE datname=current_database()"))
        if not name.startswith('test_ms7_mig_v01_') or marker != 'MS7-MIG-V01 disposable synthetic test database':
            raise SchemaMismatch('Disposable V01 database name and reservation marker required')
    elif connection.dialect.name != 'sqlite':
        raise SchemaMismatch('Unsupported rehearsal backend')


def fresh(connection):
    require_disposable(connection)
    if sa.inspect(connection).get_table_names():
        raise SchemaMismatch('Fresh install requires an empty disposable database')
    command.upgrade(configuration(connection), HEAD)
    if connection.dialect.name == 'postgresql':
        assert_baseline(connection, 'FRESH', allow_protocol=True, require_history=False)


def backfill(connection):
    # Call only after schema validation within the exclusive migration transaction.
    profile = metadata.tables['users_studentprofile']
    users = metadata.tables['auth_user']
    missing = connection.scalars(sa.select(users.c.id).where(~sa.exists(sa.select(profile.c.id).where(profile.c.user_id == users.c.id))))
    for user_id in missing:
        connection.execute(sa.insert(profile).values(id=uuid.uuid4(), user_id=user_id,
            onboarding_complete=False, onboarding_mode=None, selected_grade_id=None, created_at=utc_now()))


def advance_sequences(connection):
    # setval is NOT transactional. Run as the last migration action, never move
    # backwards; aborting later cannot undo it. nextval gaps are acceptable.
    quote = connection.dialect.identifier_preparer.quote
    for item in SNAPSHOT['fresh_disposable_sequence_evidence']['identity_columns']:
        table, column, seq = item['table_name'], item['column_name'], item['owned_sequence']
        maximum = connection.scalar(sa.text(f'SELECT max({quote(column)}) FROM {quote(table)}'))
        schema_name, seq_name = seq.split('.')
        last, called = connection.execute(sa.text(f'SELECT last_value,is_called FROM {quote(schema_name)}.{quote(seq_name)}')).one()
        if maximum is not None and (maximum > last or maximum == last and not called):
            connection.execute(sa.text('SELECT setval(CAST(:sequence AS regclass),:value,true)'), {'sequence': seq, 'value': max(last, maximum)})


def upgrade_profile(connection, profile, *, reviewed=False, failure_at=None):
    require_disposable(connection)
    if connection.dialect.name != 'postgresql':
        raise SchemaMismatch('Upgrade profiles require PostgreSQL')
    if not reviewed:
        raise SchemaMismatch('Independent schema/stamp review is required even for rehearsal')
    # Prove tracking structure/state before Alembic reads/stamps it. Existing
    # target heads remain inapplicable to legacy adoption, even when known.
    before = assert_baseline(connection, profile)
    # LOCK tables excludes concurrent legacy DDL/data writers during the rehearsal.
    tables = ','.join(connection.dialect.identifier_preparer.quote(t) for t in before['tables'])
    connection.execute(sa.text('LOCK TABLE ' + tables + ' IN ACCESS EXCLUSIVE MODE'))
    assert_baseline(connection, profile)
    if profile == 'A':
        connection.execute(sa.text('ALTER TABLE content_grade ADD COLUMN created_at timestamptz NULL'))
        connection.execute(sa.text('UPDATE content_grade SET created_at=:epoch WHERE created_at IS NULL'), {'epoch': GRADE_EPOCH})
        connection.execute(sa.text('ALTER TABLE content_grade ALTER COLUMN created_at SET NOT NULL'))
        metadata.create_all(connection, tables=[metadata.tables[m['table']] for m in SNAPSHOT['models'] if m['table'].startswith('users_')], checkfirst=False)
    if failure_at == 'ddl':
        raise RuntimeError('Synthetic failure after additive DDL')
    backfill(connection)
    if failure_at == 'backfill':
        raise RuntimeError('Synthetic failure after backfill')
    # Historical Django records deliberately still describe the original profile.
    assert_baseline(connection, 'B', require_history=False)
    after_history = inventory(connection)['migrations']
    if after_history != before['migrations']:
        raise SchemaMismatch('Django migration history changed')
    config = configuration(connection)
    command.stamp(config, BASE)
    command.upgrade(config, HEAD)
    if failure_at == 'protocol':
        raise RuntimeError('Synthetic failure after protocol DDL/stamp')
    assert_baseline(connection, 'B', allow_protocol=True, require_history=False)
    connection.execute(sa.text('SET CONSTRAINTS ALL IMMEDIATE'))
    advance_sequences(connection)
    return {'source_profile': profile, 'head': HEAD, 'historical_migrations_preserved': True}
