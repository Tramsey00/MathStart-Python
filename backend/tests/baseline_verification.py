"""Run unchanged verify_repo in a newly created disposable Django runtime."""
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from backend.tests.test_postgres import PostgreSQLTests


def main():
    runtime = Path('var/ms7-mig-v01-baseline-' + uuid.uuid4().hex).resolve()
    runtime.mkdir(parents=True)
    results = []
    PostgreSQLTests.setUpClass()
    try:
        with PostgreSQLTests().database() as engine:
            env = {**os.environ, 'DJANGO_DB_BACKEND': 'postgresql', 'DJANGO_DB_HOST': '127.0.0.1',
                   'DJANGO_DB_PORT': '55441', 'DJANGO_DB_NAME': engine.url.database,
                   'DJANGO_DB_TEST_NAME': 'test_ms7_mig_v01_django_' + uuid.uuid4().hex,
                   'DJANGO_DB_USER': engine.url.username, 'DJANGO_DB_PASSWORD': engine.url.password or 'synthetic-local-only',
                   'DJANGO_RUNTIME_ROOT': str(runtime), 'DJANGO_SECRET_KEY': 'synthetic-test-only-not-production',
                   'DJANGO_DEBUG': '0', 'DJANGO_ALLOWED_HOSTS': 'localhost,127.0.0.1,testserver'}
            # Target PG suite has its own explicit invocation/evidence. Root
            # verification reads this isolated baseline and owns its own test DB.
            env.pop('MATHSTART_V01_TEST_ADMIN_URL', None)
            commands = [('migrate', ['manage.py','migrate','--noinput']),
                        ('bootstrap-1', ['manage.py','bootstrap_site']),
                        ('bootstrap-2', ['manage.py','bootstrap_site']),
                        ('collectstatic', ['manage.py','collectstatic','--noinput']),
                        ('verify-repo', ['scripts/verify_repo.py']),
                        ('r02-migration', ['-m','unittest','tests.test_migration_r02_contract',
                                          'tests.test_migration_r02_review','tests.test_migration_r02_protocols','-v'])]
            for label, arguments in commands:
                logfile = runtime / (label + '.txt')
                with logfile.open('wb') as stream:
                    process = subprocess.run([sys.executable, *arguments], env=env, stdout=stream, stderr=subprocess.STDOUT)
                results.append({'command': arguments, 'exit_code': process.returncode,
                                'log': logfile.relative_to(Path.cwd()).as_posix()})
                print(label + ': exit ' + str(process.returncode), flush=True)
                if process.returncode:
                    print(logfile.read_text(encoding='utf-8',errors='replace')[-4000:], flush=True)
                    break
    finally:
        PostgreSQLTests.tearDownClass()
    output = {'status': 'PASS' if results and len(results) == 6 and all(r['exit_code'] == 0 for r in results) else 'FAIL',
              'runtime_root': runtime.relative_to(Path.cwd()).as_posix(), 'checks': results}
    Path('docs/acceptance/MS7-MIG-V01/baseline-verification-v3.json').write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0 if output['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
