"""Unchanged Django fresh smoke + verify_repo on a new marked disposable DB."""
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

import sqlalchemy as sa
from sqlalchemy.engine import make_url


def main():
    url = make_url(os.environ['MATHSTART_V02_TEST_ADMIN_URL'])
    if (url.drivername, url.host, url.port, url.database) != ('postgresql+psycopg', '127.0.0.1', 15441, 'postgres'):
        raise RuntimeError('Refusing non-V02 disposable endpoint')
    suffix = uuid.uuid4().hex
    name = 'ms6_v01_smoke_v02_' + suffix
    runtime = Path('var/v02-baseline-' + suffix).resolve()
    runtime.mkdir(parents=True)
    engine = sa.create_engine(url, isolation_level='AUTOCOMMIT', hide_parameters=True)
    quoted = engine.dialect.identifier_preparer.quote(name)
    with engine.connect() as connection:
        connection.execute(sa.text('CREATE DATABASE ' + quoted))
        connection.execute(sa.text("COMMENT ON DATABASE " + quoted + " IS 'MS7-MIG-V02 disposable baseline verification'"))
    environment = {**os.environ, 'DJANGO_DB_BACKEND': 'postgresql', 'DJANGO_DB_HOST': '127.0.0.1',
        'DJANGO_DB_PORT': '15441', 'DJANGO_DB_NAME': name, 'DJANGO_DB_USER': 'postgres',
        'DJANGO_DB_PASSWORD': 'synthetic-local-only', 'DJANGO_SECRET_KEY': 'synthetic-v02-baseline-only',
        'DJANGO_DEBUG': '0', 'DJANGO_RUNTIME_ROOT': str(runtime), 'PYTHONIOENCODING': 'utf-8'}
    results = []
    commands = [[sys.executable, 'scripts/fresh_install_smoke.py', '--disposable'],
                [sys.executable, 'scripts/verify_repo.py'],
                [sys.executable, 'scripts/version_report.py'],
                [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_r02a_contract.py', '-v'],
                [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_r03a_contract.py', '-v']]
    for index, argv in enumerate(commands):
        log = runtime / f'check-{index}.log'
        with log.open('w', encoding='utf-8') as stream:
            result = subprocess.run(argv, env=environment, stdout=stream, stderr=subprocess.STDOUT, timeout=600)
        results.append({'argv': argv, 'exit_code': result.returncode, 'log': str(log)})
        print(json.dumps(results[-1]), flush=True)
        if result.returncode and index == 0:
            break
    # Preserve this run's baseline/runtime for review; no destructive cleanup.
    record = {'database': name, 'runtime': str(runtime), 'disposable': True, 'commands': results,
              'implementation_sha': None, 'publication': 'PENDING_PUBLICATION'}
    (runtime / 'results.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    engine.dispose()
    return 0 if len(results) == len(commands) and all(r['exit_code'] == 0 for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
