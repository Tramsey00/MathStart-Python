"""Private subprocess configuration for an owned marked V02 database."""
import os
from pathlib import Path


def comparator_environment(url, name, runtime_root):
    if (url.drivername != 'postgresql+psycopg' or url.host != '127.0.0.1'
            or url.port not in {15441, 55441} or not name.startswith('test_ms7_mig_v01_v02_')):
        raise RuntimeError('Only reserved owned comparator databases allowed')
    return {**os.environ, 'DJANGO_DB_BACKEND': 'postgresql', 'DJANGO_DB_HOST': url.host,
            'DJANGO_DB_PORT': str(url.port), 'DJANGO_DB_NAME': name, 'DJANGO_DB_USER': url.username,
            'DJANGO_DB_PASSWORD': url.password or '', 'DJANGO_SECRET_KEY': 'synthetic-v02-comparator',
            'DJANGO_DEBUG': '0', 'DJANGO_RUNTIME_ROOT': str(Path(runtime_root).resolve()),
            'PYTHONIOENCODING': 'utf-8'}


def require_comparator_database(connection):
    if (connection.vendor != 'postgresql' or connection.settings_dict['HOST'] != '127.0.0.1'
            or str(connection.settings_dict['PORT']) not in {'15441', '55441'}
            or not connection.settings_dict['NAME'].startswith('test_ms7_mig_v01_v02_')):
        raise RuntimeError('Only disposable V02 comparator fixture is allowed')
    with connection.cursor() as cursor:
        cursor.execute("SELECT shobj_description(oid, 'pg_database') FROM pg_database WHERE datname=current_database()")
        if cursor.fetchone() != ('MS7-MIG-V01 disposable synthetic test database',):
            raise RuntimeError('Owned disposable database marker required')
