"""Explicit reviewed schema installation/adoption, separate from API startup.

Preview reads a maintenance snapshot and writes a private signed plan. Apply
requires its reviewed digest, the same database/role/code, unchanged full input
and a drained legacy writer. There is no downgrade, automatic stamp or retry
after an uncertain commit. Disposable rehearsal wrappers retain their guards.
"""
import argparse
from datetime import timedelta
import hashlib
import hmac
import json
import os
from pathlib import Path
import sys

import sqlalchemy as sa

from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.migrations.schema import SchemaMismatch, assert_baseline, inventory
from backend.migrations.upgrade import HEAD, _fresh, _upgrade_profile
from backend.users.cutover import LOCK, _normal, writer_fact

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'reviewed-schema-plan-v1'


def encoded(value):
    return (json.dumps(_normal(value), sort_keys=True, ensure_ascii=False,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def plan_digest(plan):
    return hashlib.sha256(encoded(plan)).hexdigest()


def signed(key, domain, value):
    if not isinstance(key, str) or len(key) < 32:
        raise SchemaMismatch('A separate schema signing key of at least32 characters is required')
    return hmac.new(key.encode(), domain.encode() + b'\0' + encoded(value), hashlib.sha256).hexdigest()


def code_digest():
    paths = [Path(__file__), ROOT / 'backend/users/bootstrap.py']
    for directory in ('backend/migrations', 'backend/models'):
        paths.extend(p for p in (ROOT / directory).rglob('*') if p.suffix in {'.py', '.json'})
    return hashlib.sha256(encoded({p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(set(paths))})).hexdigest()


def database_fact(connection):
    if connection.dialect.name != 'postgresql':
        raise SchemaMismatch('Release schema operations require PostgreSQL16+')
    fact = dict(connection.execute(sa.text('''
        SELECT d.oid AS database_oid, d.datname AS database_name,
               r.oid AS role_oid, r.rolname AS role_name,
               current_setting('server_version_num')::int / 10000 AS major
        FROM pg_database d CROSS JOIN pg_roles r
        WHERE d.datname=current_database() AND r.rolname=current_user
    ''')).mappings().one())
    if fact['major'] < 16:
        raise SchemaMismatch('PostgreSQL16+ required')
    return fact


def validate_source(connection, profile):
    if profile == 'FRESH':
        state = inventory(connection)
        if state['tables'] or state['sequences'] or state['unexpected_objects']:
            raise SchemaMismatch('Fresh release installation requires an empty database')
        return state
    return assert_baseline(connection, profile)


def source_digest(connection, key, state):
    # Never persist raw rows, legacy sessions, password hashes or private receipts.
    # Include is_called: nextval/setval drift must also invalidate a reviewed plan.
    quote = connection.dialect.identifier_preparer.quote
    rows = {}
    for name in state['tables']:
        values = [dict(row) for row in connection.execute(sa.text('SELECT * FROM public.' + quote(name))).mappings()]
        rows[name] = sorted(values, key=encoded)
    sequences = {}
    for item in state['sequences']:
        name = quote(item['schemaname']) + '.' + quote(item['sequencename'])
        sequences[name] = dict(connection.execute(sa.text('SELECT last_value,is_called FROM ' + name)).mappings().one())
    return signed(key, 'schema.input.v1', {'schema': state, 'rows': rows, 'sequences': sequences})


def preview(engine, key, profile, legacy_role=None):
    if profile not in {'FRESH', 'A', 'B', 'C'} or (profile == 'FRESH') != (legacy_role is None):
        raise SchemaMismatch('Legacy adoption requires the sole drained writer role; fresh has no legacy role')
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as connection, connection.begin():
        connection.execute(sa.text('SET TRANSACTION READ ONLY'))
        fact = database_fact(connection)
        state = validate_source(connection, profile)
        # writer_fact is shared with cutover; NOLOGIN alone is not a drain proof.
        writer = writer_fact(connection, legacy_role) if legacy_role else None
        now = connection.scalar(sa.text('SELECT clock_timestamp()'))
        plan = {'version': VERSION, 'profile': profile, 'target_head': HEAD,
                'database': fact, 'legacy_role': legacy_role, 'legacy_writer': writer,
                'created_at': now.isoformat(), 'expires_at': (now + timedelta(minutes=30)).isoformat(),
                'code_digest': code_digest(), 'source_digest': source_digest(connection, key, state),
                'table_count': len(state['tables'])}
        return {**plan, 'signature': signed(key, 'schema.plan.v1', plan)}


def apply(engine, key, plan, reviewed_digest, *, maintenance=False):
    if not maintenance or not hmac.compare_digest(plan_digest(plan), reviewed_digest):
        raise SchemaMismatch('Explicit maintenance and exact reviewed plan digest required')
    unsigned = {k: v for k, v in plan.items() if k != 'signature'}
    if not hmac.compare_digest(signed(key, 'schema.plan.v1', unsigned), plan.get('signature', '')):
        raise SchemaMismatch('Schema plan signature mismatch')
    if (plan.get('version') != VERSION or plan.get('target_head') != HEAD
            or plan.get('code_digest') != code_digest() or plan.get('profile') not in {'FRESH', 'A', 'B', 'C'}):
        raise SchemaMismatch('Unknown or stale schema plan/code')
    with engine.begin() as connection:
        fact = database_fact(connection)
        if fact != plan['database']:
            raise SchemaMismatch('Plan belongs to a different database/role')
        connection.execute(sa.text('SELECT pg_advisory_xact_lock(:key)'), {'key': LOCK})
        if connection.scalar(sa.text('''SELECT EXISTS(SELECT 1 FROM pg_stat_activity
                WHERE datid=(SELECT oid FROM pg_database WHERE datname=current_database())
                AND pid<>pg_backend_pid() AND backend_type='client backend')''')):
            raise SchemaMismatch('Maintenance requires all other database clients disconnected')
        # Also serialize fresh installers, including when no tables exist yet.
        connection.execute(sa.text("SELECT pg_advisory_xact_lock(hashtextextended('mathstart.schema.release',0))"))
        now = connection.scalar(sa.text('SELECT clock_timestamp()'))
        from datetime import datetime
        if now >= datetime.fromisoformat(plan['expires_at']):
            raise SchemaMismatch('Schema plan expired')
        legacy = writer_fact(connection, plan['legacy_role']) if plan['legacy_role'] else None
        if legacy != plan['legacy_writer']:
            raise SchemaMismatch('Legacy writer provenance changed')
        state = validate_source(connection, plan['profile'])
        if state['tables']:
            quote = connection.dialect.identifier_preparer.quote
            connection.execute(sa.text('LOCK TABLE ' + ','.join('public.' + quote(t) for t in state['tables'])
                                       + ' IN ACCESS EXCLUSIVE MODE'))
            state = validate_source(connection, plan['profile'])
        if not hmac.compare_digest(source_digest(connection, key, state), plan['source_digest']):
            raise SchemaMismatch('Reviewed schema/data/sequences changed')
        if plan['profile'] == 'FRESH':
            _fresh(connection)
            from backend.users.bootstrap import seed_permissions
            from sqlalchemy.orm import Session
            with Session(bind=connection, join_transaction_mode='rollback_only') as session:
                seed_permissions(session)
                session.flush()
        else:
            _upgrade_profile(connection, plan['profile'])
        assert_baseline(connection, 'B', allow_protocol=True, require_history=False)
    # A lost COMMIT response raises above. Never manufacture success or replay.
    return {'status': 'APPLIED', 'head': HEAD, 'reviewed_plan_sha256': reviewed_digest}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preview', 'apply', 'check'])
    parser.add_argument('--profile', choices=['FRESH', 'A', 'B', 'C'])
    parser.add_argument('--legacy-role')
    parser.add_argument('--plan-file', type=Path)
    parser.add_argument('--reviewed-plan-sha256')
    parser.add_argument('--maintenance', action='store_true')
    args = parser.parse_args(argv)
    engine = None
    try:
        engine = create_engine(DatabaseConfig.from_environment())
        if args.action == 'check':
            with engine.begin() as connection:
                connection.execute(sa.text('SET TRANSACTION READ ONLY'))
                database_fact(connection)
                assert_baseline(connection, 'B', allow_protocol=True, require_history=False)
            print('CHECKED: physical target schema; this does not reconcile an uncertain prior apply')
        else:
            key = os.environ['MATHSTART_SCHEMA_SIGNING_KEY']
            if args.plan_file is None:
                parser.error('--plan-file is required')
            if args.action == 'preview':
                if args.profile is None:
                    parser.error('--profile is required for preview')
                plan = preview(engine, key, args.profile, args.legacy_role)
                # Explicit private artifact; no overwrite or implicit directory creation.
                descriptor = os.open(args.plan_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(descriptor, 'wb') as output:
                    output.write(encoded(plan))
                    output.flush()
                    os.fsync(output.fileno())
                print('REVIEW_REQUIRED: plan SHA256 ' + plan_digest(plan))
            else:
                plan = json.loads(args.plan_file.read_text(encoding='utf-8'))
                if not args.reviewed_plan_sha256:
                    parser.error('--reviewed-plan-sha256 is required')
                result = apply(engine, key, plan, args.reviewed_plan_sha256, maintenance=args.maintenance)
                print(json.dumps(result))
        return 0
    except Exception as error:
        # Includes uncertain commit, permission and signature failures. Never log
        # DBAPI parameters, rows, credentials or plan contents.
        print('SCHEMA_REFUSED_OR_UNCERTAIN: ' + type(error).__name__, file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
