"""Actual disposable fresh/upgrade entry points with preservation receipts."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sqlalchemy as sa
from backend.infrastructure.database import DatabaseConfig
from backend.migrations.schema import assert_baseline
from backend.migrations.upgrade import HEAD
from backend.verification_suite import owned_database, prepare_content_runtime


def cli(engine, *arguments):
    env = {**os.environ, 'MATHSTART_DATABASE_URL': engine.url.render_as_string(hide_password=False)}
    result = subprocess.run([sys.executable, '-m', 'backend.migrate', *arguments], cwd=ROOT,
                            env=env, capture_output=True, timeout=60)
    if result.returncode:
        raise RuntimeError('Actual schema CLI refused/failed')


def verify_head(engine):
    with engine.connect() as c:
        state = assert_baseline(c, 'B', allow_protocol=True, require_history=False)
        if list(c.scalars(sa.text('SELECT version_num FROM alembic_version'))) != [HEAD]:
            raise RuntimeError('Unknown target migration head')
        return sum(len(state[key]) for key in ('columns', 'constraints', 'indexes', 'sequences')) + 1


def fresh_install(admin, url, evidence):
    from backend.content.artifacts import verify_public_artifacts
    from backend.content.editions import fingerprint
    from backend.infrastructure.uow import UnitOfWork
    from backend.models.baseline import metadata
    from backend.verification import system_check
    count = 0
    for attempt in range(2):
        with owned_database(admin, url, 'fresh') as engine:
            prepare_content_runtime(engine, evidence / ('fresh-' + str(attempt + 1)))
            count += verify_head(engine)
            expected = {'content_grade': 6, 'content_subject': 12, 'content_section': 63,
                'content_contentpage': 279, 'content_lessonpublication': 263,
                'content_mediaasset': 29, 'content_redirect': 282}
            with UnitOfWork(engine) as uow:
                for table, total in expected.items():
                    if uow.session.scalar(sa.select(sa.func.count()).select_from(metadata.tables[table])) != total:
                        raise RuntimeError('Incomplete fresh inventory')
                    count += 1
                before = fingerprint(uow.session)
                users = [dict(row) for row in uow.session.execute(sa.select(metadata.tables['auth_user']).order_by('id')).mappings()]
            # The normal target bootstrap command must also remain idempotent
            # over the installed edition and must not modify existing users.
            env = {**os.environ, 'MATHSTART_DATABASE_URL': engine.url.render_as_string(hide_password=False)}
            result = subprocess.run([sys.executable, '-m', 'backend.cli', 'bootstrap', '--disposable'],
                                    cwd=ROOT, env=env, capture_output=True, timeout=120)
            if result.returncode:
                raise RuntimeError('Target bootstrap CLI failed')
            with UnitOfWork(engine) as uow:
                if fingerprint(uow.session) != before or users != [dict(row) for row in
                    uow.session.execute(sa.select(metadata.tables['auth_user']).order_by('id')).mappings()]:
                    raise RuntimeError('Repeat bootstrap changed installed content/users')
                count += 2
            root = Path(os.environ['MATHSTART_PUBLIC_ARTIFACT_ROOT'])
            manifest = json.loads((root / 'output-manifest.json').read_text(encoding='utf-8'))
            pins = json.loads(os.environ['MATHSTART_PUBLIC_ARTIFACT_DIGESTS'])
            release, _, verified = verify_public_artifacts(os.environ['MATHSTART_RELEASE_ROOT'], manifest['release_id'],
                manifest['input_receipt_digest'], root, pins[manifest['release_id']], manifest['origin'])
            if len(release.pages) != 279 or len(release.index['catalogue']['topics']) != 263:
                raise RuntimeError('Incomplete fresh compiled release')
            count += len(verified['files']) + 2
            count += system_check()
            cli(engine, 'check', '--disposable')
            count += 1
    return count


def upgrade(profile, admin_url):
    os.environ['MATHSTART_V01_TEST_ADMIN_URL'] = admin_url.render_as_string(hide_password=False)
    from backend.tests.test_postgres import PostgreSQLTests, data_digest
    from backend.models.baseline import GRADE_EPOCH, metadata, SNAPSHOT
    PostgreSQLTests.setUpClass()
    count = 0
    try:
        fixture = PostgreSQLTests()
        with fixture.database(profile) as engine:
            instant = fixture.seed(engine, profile)
            with engine.connect() as c:
                before = data_digest(c, omit_grade_time=profile == 'A')
                history = list(c.execute(sa.text('SELECT * FROM django_migrations ORDER BY id')))
            cli(engine, 'upgrade', '--profile', profile, '--disposable', '--reviewed-rehearsal')
            count += verify_head(engine)
            with engine.connect() as c:
                after = data_digest(c, omit_grade_time=profile == 'A')
                for table, digest in before.items():
                    if table != 'users_studentprofile' or profile == 'C':
                        if after[table] != digest:
                            raise RuntimeError('Upgrade changed retained data')
                        count += 1
                if history != list(c.execute(sa.text('SELECT * FROM django_migrations ORDER BY id'))):
                    raise RuntimeError('Upgrade changed historical migration records')
                if c.scalar(sa.text('SELECT created_at FROM content_grade WHERE id=701')) != (GRADE_EPOCH if profile == 'A' else instant):
                    raise RuntimeError('Grade epoch changed')
                count += 2
                for item in SNAPSHOT['fresh_disposable_sequence_evidence']['identity_columns']:
                    table = metadata.tables[item['table_name']]
                    maximum = c.scalar(sa.select(sa.func.max(table.c.id))) or 0
                    value = c.scalar(sa.text('SELECT nextval(CAST(:sequence AS regclass))'), {'sequence': item['owned_sequence']})
                    if value <= maximum:
                        raise RuntimeError('Upgrade sequence can collide')
                    count += 1
                once = data_digest(c)
            cli(engine, 'check', '--disposable')
            with engine.connect() as c:
                if once != data_digest(c):
                    raise RuntimeError('Read-only check changed upgraded data')
                count += 1
    finally:
        PostgreSQLTests.tearDownClass()
    return count


def run(check, evidence):
    if os.environ.get('MATHSTART_DISPOSABLE') != '1' or importlib.util.find_spec('django') is not None:
        raise RuntimeError('Explicit no-Django disposable target required')
    url = DatabaseConfig.from_environment().url
    if url.drivername != 'postgresql+psycopg' or url.host != '127.0.0.1' or url.port != 55441:
        raise RuntimeError('Dedicated PostgreSQL endpoint required')
    saved = dict(os.environ)
    admin = sa.create_engine(url.set(database='postgres'), isolation_level='AUTOCOMMIT', hide_parameters=True)
    try:
        with admin.connect() as c:
            major = int(c.scalar(sa.text('SHOW server_version_num'))) // 10000
            if major < 16:
                raise RuntimeError('PostgreSQL16 required')
        count = fresh_install(admin, url, evidence) if check == 'fresh-install' else upgrade(check[-1], url.set(database='postgres'))
        if any(name == 'django' or name.startswith('django.') for name in sys.modules):
            raise RuntimeError('Django imported by target installation')
        return {'check_id': check, 'status': 'PASS', 'evidence_class': 'TARGET_RUNTIME',
                'assertions': count, 'skipped': 0, 'database_vendor': 'postgresql', 'postgresql_major': major}
    finally:
        admin.dispose()
        os.environ.clear()
        os.environ.update(saved)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=['fresh-install', 'upgrade-A', 'upgrade-B', 'upgrade-C'])
    args = parser.parse_args(argv)
    path = None
    try:
        if os.environ.get('MATHSTART_CHECK_ID') != args.check:
            raise RuntimeError('Check identity mismatch')
        path = Path(os.environ['MATHSTART_CHECK_RESULT'])
        result = run(args.check, path.parent)
    except Exception as error:
        result = {'check_id': args.check, 'status': 'FAIL', 'evidence_class': 'TARGET_RUNTIME',
                  'assertions': 0, 'skipped': 0, 'failure_class': type(error).__name__}
    if path is not None:
        with path.open('x', encoding='utf-8', newline='\n') as output:
            output.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
