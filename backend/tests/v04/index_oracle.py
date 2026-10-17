"""Actual legacy INDEX generation against owned rows and copied source files."""
import base64
import json
import os
from pathlib import Path
import shutil
import tempfile


def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    from django.db import connection
    if (connection.vendor != 'postgresql' or connection.settings_dict['HOST'] != '127.0.0.1'
            or str(connection.settings_dict['PORT']) != '55441'
            or not connection.settings_dict['NAME'].startswith('test_ms7_mig_v01_')):
        raise RuntimeError('Only owned disposable oracle database allowed')
    with connection.cursor() as cursor:
        cursor.execute("SELECT shobj_description(oid, 'pg_database') FROM pg_database WHERE datname=current_database()")
        if cursor.fetchone() != ('MS7-MIG-V01 disposable synthetic test database',):
            raise RuntimeError('Owned database marker required')
    from content.services.lesson_sources import write_lesson_index
    root = Path(__file__).resolve().parents[3]
    try:
        with tempfile.TemporaryDirectory(prefix='index-oracle-') as directory:
            copied = Path(directory) / 'curriculum'
            shutil.copytree(root / 'curriculum', copied)
            count = write_lesson_index(copied)
            raw = (copied / 'INDEX.md').read_bytes()
            print(json.dumps({'indexed': count, 'payload': base64.b64encode(raw).decode('ascii')}))
    finally:
        connection.close()


if __name__ == '__main__':
    main()
