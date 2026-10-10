"""Repeat root-lock CI on a new, marked PostgreSQL DB without V01 imports.

Run in the legacy venv: python -m backend.tests.legacy_ci_verification --disposable
The endpoint is the reserved local V01 container, never an environment DB URL.
"""
import argparse
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

import psycopg
from psycopg import sql


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--disposable', action='store_true', required=True)
    parser.parse_args()
    for name in ('sqlalchemy', 'alembic'):
        if importlib.util.find_spec(name) is not None:
            raise RuntimeError('Legacy absence proof requires an environment without ' + name)
    installed = {item.metadata['Name'].lower().replace('_', '-'): item.version
                 for item in importlib.metadata.distributions()}
    for line in Path('requirements.lock').read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        name, version = line.split('==')
        name = name.split('[')[0].lower().replace('_', '-')
        if installed.get(name) != version:
            raise RuntimeError('Legacy lock mismatch: ' + name)
    suffix = uuid.uuid4().hex
    name = 'test_ms7_mig_v01_ci_' + suffix
    test_name = 'test_ms7_mig_v01_django_' + suffix
    runtime = Path('var/ms7-mig-v01-ci-v4-' + suffix).resolve()
    runtime.mkdir(parents=True)
    checks = []
    admin = psycopg.connect(host='127.0.0.1', port=55441, dbname='postgres',
                           user='postgres', password='synthetic-local-only',
                           connect_timeout=5, autocommit=True)
    created = False
    try:
        with admin.cursor() as cursor:
            server = cursor.execute('SHOW server_version').fetchone()[0]
            if int(server.split('.')[0]) < 16:
                raise RuntimeError('PostgreSQL 16+ required')
            if cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (test_name,)).fetchone():
                raise RuntimeError('Refusing an existing Django test database')
            cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
            created = True
            cursor.execute(sql.SQL('COMMENT ON DATABASE {} IS {}').format(
                sql.Identifier(name), sql.Literal('MS7-MIG-V01 disposable CI compatibility verification')))
        env = {**os.environ, 'DJANGO_DB_BACKEND': 'postgresql', 'DJANGO_DB_HOST': '127.0.0.1',
               'DJANGO_DB_PORT': '55441', 'DJANGO_DB_NAME': name, 'DJANGO_DB_TEST_NAME': test_name,
               'DJANGO_DB_USER': 'postgres', 'DJANGO_DB_PASSWORD': 'synthetic-local-only',
               'DJANGO_RUNTIME_ROOT': str(runtime), 'DJANGO_SECRET_KEY': 'synthetic-ci-v4-only',
               'DJANGO_DEBUG': '0', 'DJANGO_ALLOWED_HOSTS': 'localhost,127.0.0.1,testserver'}
        env.pop('MATHSTART_V01_TEST_ADMIN_URL', None)
        commands = [
            ('pip-check', ['-m', 'pip', 'check']),
            ('migrate', ['manage.py', 'migrate', '--noinput']),
            ('bootstrap-1', ['manage.py', 'bootstrap_site']),
            ('bootstrap-2', ['manage.py', 'bootstrap_site']),
            ('collectstatic', ['manage.py', 'collectstatic', '--noinput']),
            ('django-tests', ['manage.py', 'test', '--noinput', '-v', '2']),
            ('verify-repo', ['scripts/verify_repo.py']),
            ('r02-migration', ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_migration_r02*.py', '-v']),
            ('r02a', ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_r02a_contract.py', '-v']),
            ('r03a', ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_r03a_contract.py', '-v']),
        ]
        for label, arguments in commands:
            logfile = runtime / (label + '.txt')
            with logfile.open('wb') as stream:
                result = subprocess.run([sys.executable, *arguments], env=env,
                                        stdout=stream, stderr=subprocess.STDOUT)
            checks.append({'command': arguments, 'exit_code': result.returncode,
                           'log': logfile.relative_to(Path.cwd()).as_posix()})
            print(label + ': exit ' + str(result.returncode), flush=True)
            if result.returncode:
                print(logfile.read_text(encoding='utf-8', errors='replace')[-4000:], flush=True)
                break
    finally:
        if created:
            with admin.cursor() as cursor:
                cursor.execute(sql.SQL('DROP DATABASE {} WITH (FORCE)').format(sql.Identifier(name)))
        admin.close()
    output = {'status': 'PASS' if len(checks) == 10 and all(c['exit_code'] == 0 for c in checks) else 'FAIL',
              'dependency_lock': 'requirements.lock', 'SQLAlchemy_installed': False, 'Alembic_installed': False,
              'PostgreSQL': server, 'runtime_root': runtime.relative_to(Path.cwd()).as_posix(),
              'checks': checks, 'owned_database_removed': created}
    Path('docs/acceptance/MS7-MIG-V01/legacy-ci-verification-v4.json').write_text(
        json.dumps(output, indent=2)+'\n', encoding='utf-8')
    return 0 if output['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
