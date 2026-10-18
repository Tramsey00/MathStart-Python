"""Full backend suites, isolated in newly created marked PostgreSQL databases."""
from contextlib import contextmanager
import importlib.util
import json
import os
import secrets
from pathlib import Path
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sqlalchemy as sa
from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.migrations.upgrade import fresh


def prepare_content_runtime(engine, evidence):
    from hashlib import sha256
    import subprocess
    from backend.content.synthetic_setup import prepare, activate_initial
    from frontend.build_public import build_public
    source_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    key = secrets.token_urlsafe(48)
    origin = 'http://127.0.0.1:8121'
    runtime = evidence / 'runtime'
    output = evidence / 'artifact'
    release_id = 'backend-' + uuid.uuid4().hex
    os.environ.update(MATHSTART_DATABASE_URL=engine.url.render_as_string(hide_password=False),
        MATHSTART_HTTP_SIGNING_KEY=key, MATHSTART_PUBLIC_ORIGIN=origin)
    prepared = prepare(engine, ROOT, runtime, release_id, source_sha, key)
    build_public(runtime / 'releases', release_id, prepared['manifest_digest'], output, origin, prepared['receipt_digest'])
    artifact_digest = sha256((output / 'output-manifest.json').read_bytes()).hexdigest()
    activate_initial(engine, runtime / 'releases', release_id, prepared['receipt_digest'], output, artifact_digest, origin)
    os.environ.update(MATHSTART_V04_DATABASE_URL=engine.url.render_as_string(hide_password=False),
        MATHSTART_STAFF_COOKIE_FILE=str(runtime / 'private-staff-cookie.json'),
        MATHSTART_RELEASE_ROOT=str(runtime / 'releases'), MATHSTART_PUBLIC_ARTIFACT_ROOT=str(output),
        MATHSTART_PUBLIC_ARTIFACT_DIGESTS=json.dumps({release_id: artifact_digest}))


@contextmanager
def owned_database(admin, url, label):
    name = 'test_ms7_mig_v01_' + label + '_' + uuid.uuid4().hex
    quote = admin.dialect.identifier_preparer.quote(name)
    owned_oid = None
    engine = None
    try:
        with admin.connect() as c:
            c.execute(sa.text('CREATE DATABASE ' + quote))
            owned_oid = c.scalar(sa.text('SELECT oid FROM pg_database WHERE datname=:name'), {'name': name})
            c.execute(sa.text('COMMENT ON DATABASE ' + quote + " IS 'MS7-MIG-V01 disposable synthetic test database'"))
        engine = create_engine(DatabaseConfig(url.set(database=name)))
        yield engine
    finally:
        if engine is not None:
            engine.dispose()
        if owned_oid is not None:
            with admin.connect() as c:
                if c.scalar(sa.text('SELECT oid FROM pg_database WHERE datname=:name'), {'name': name}) != owned_oid:
                    raise RuntimeError('Owned database identity changed; cleanup refused')
                # Never terminate unrelated sessions to manufacture cleanup PASS.
                c.execute(sa.text('DROP DATABASE ' + quote))


def execute(modules, *, case_ids=None):
    suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
    if suite.countTestCases() == 0:
        raise RuntimeError('Backend suite is empty')
    def identifiers(node):
        if isinstance(node, unittest.TestSuite):
            return [identity for child in node for identity in identifiers(child)]
        return [node.id()]
    planned = identifiers(suite)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped or result.testsRun != len(planned):
        raise RuntimeError('Backend tests failed or skipped')
    if case_ids is not None:
        case_ids.extend(planned)
    return result.testsRun


def run():
    if os.environ.get('MATHSTART_DISPOSABLE') != '1':
        raise RuntimeError('Disposable backend verification required')
    if importlib.util.find_spec('django') is not None or importlib.util.find_spec('rest_framework') is not None:
        raise RuntimeError('No-Django target interpreter required')
    config = DatabaseConfig.from_environment()
    url = config.url
    if url.drivername != 'postgresql+psycopg' or url.host != '127.0.0.1' or url.port != 55441:
        raise RuntimeError('Dedicated reserved PostgreSQL endpoint required')
    from backend.tests.legacy_tools import legacy_python
    legacy_python()  # Explicit legacy oracle is mandatory, never skip.
    admin = sa.create_engine(url.set(database='postgres'), isolation_level='AUTOCOMMIT', hide_parameters=True,
                             connect_args={'connect_timeout': 5, 'options': '-c statement_timeout=30000'})
    saved = dict(os.environ)
    try:
        with admin.connect() as c:
            major = int(c.scalar(sa.text('SHOW server_version_num'))) // 10000
            if major < 16:
                raise RuntimeError('PostgreSQL16 required')
        os.environ['MATHSTART_V01_TEST_ADMIN_URL'] = url.set(database='postgres').render_as_string(hide_password=False)
        os.environ['MATHSTART_V02_TEST_ADMIN_URL'] = os.environ['MATHSTART_V01_TEST_ADMIN_URL']
        os.environ['MATHSTART_V01_EVIDENCE_DIR'] = str(Path(os.environ['MATHSTART_CHECK_RESULT']).parent / 'schema')
        case_ids = []
        count = execute(['backend.tests.test_unit', 'backend.tests.test_health', 'backend.tests.test_postgres',
                         'backend.tests.test_release_migrate',
                         'backend.tests.test_operator',
                         'backend.tests.test_remediation', 'backend.tests.test_discovery'], case_ids=case_ids)
        count += execute(['backend.tests.v02.test_unit', 'backend.tests.v02.test_http',
                          'backend.tests.v02.test_postgres', 'backend.tests.v02.test_asset_regressions'], case_ids=case_ids)
        with owned_database(admin, url, 'identity') as engine:
            with engine.begin() as c:
                fresh(c)
            os.environ['MATHSTART_V03_DATABASE_URL'] = engine.url.render_as_string(hide_password=False)
            count += execute(['backend.tests.v03.test_legacy_proof', 'backend.tests.v03.test_cutover',
                              'backend.tests.v03.test_identity', 'backend.tests.v03.test_staff_writes'], case_ids=case_ids)
        with owned_database(admin, url, 'content') as engine:
            prepare_content_runtime(engine, Path(os.environ['MATHSTART_CHECK_RESULT']).parent)
            count += execute(['backend.tests.v04.test_build', 'backend.tests.v04.test_read_runtime',
                'backend.tests.v04.test_content_checks', 'backend.tests.v04.test_indexing', 'backend.tests.v04.test_publication',
                'backend.tests.v04.test_editions', 'backend.tests.v04.test_preparation', 'backend.tests.v04.test_registration',
                'backend.tests.v04.test_bootstrap_plan', 'backend.tests.v04.test_public_update',
                'backend.tests.v04.test_artifacts', 'backend.tests.v04.test_artifact_pins', 'backend.tests.v04.test_verified_release_cache',
                'backend.tests.v04.test_participant'], case_ids=case_ids)
        if any(name == 'django' or name.startswith('django.') for name in sys.modules):
            raise RuntimeError('Django imported by target suite')
        return {'check_id': 'backend-tests', 'status': 'PASS', 'evidence_class': 'TARGET_RUNTIME',
                'assertions': count, 'case_ids': case_ids, 'skipped': 0,
                'database_vendor': 'postgresql', 'postgresql_major': major}
    finally:
        admin.dispose()
        os.environ.clear()
        os.environ.update(saved)


def main():
    path = None
    try:
        if os.environ.get('MATHSTART_CHECK_ID') != 'backend-tests':
            raise RuntimeError('Explicit backend check identity required')
        path = Path(os.environ['MATHSTART_CHECK_RESULT'])
        result = run()
    except Exception as error:
        result = {'check_id': 'backend-tests', 'status': 'FAIL', 'evidence_class': 'TARGET_RUNTIME',
                  'assertions': 0, 'skipped': 0, 'failure_class': type(error).__name__}
    if path is not None:
        with path.open('x', encoding='utf-8', newline='\n') as output:
            output.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
