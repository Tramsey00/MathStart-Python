"""Live legacy visual comparator: reserved synthetic PG, enforced read-only.

Uses the original Django startup and source CSS/JS, without any migrations,
bootstrap, accounts or writes. The lifecycle caller owns this child process.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import sqlalchemy as sa
from backend.infrastructure.database import DatabaseConfig,create_engine
from backend.migrations.upgrade import require_disposable
from backend.content.releases import inside
from frontend.build_input import verified_release


def run(config,legacy_python,runtime_root,port):
    if os.environ.get('MATHSTART_DISPOSABLE')!='1':
        raise ValueError('Explicit disposable comparator authorization required')
    repository=Path(__file__).resolve().parent.parent
    runtime=Path(runtime_root).resolve()
    if not runtime.is_relative_to(repository/'var'):
        raise ValueError('Comparator runtime must stay within this checkout var directory')
    db=DatabaseConfig.from_environment()
    if db.url.drivername!='postgresql+psycopg':raise ValueError('Comparator requires reserved synthetic PostgreSQL')
    engine=create_engine(db)
    try:
        with engine.connect() as connection:
            connection.execute(sa.text('SET TRANSACTION READ ONLY'))
            require_disposable(connection)
            if connection.scalar(sa.text('SHOW transaction_read_only'))!='on':raise ValueError('Read-only preflight failed')
    finally:engine.dispose()
    release=verified_release(config['input_root'],config['release_id'],config['manifest_digest'],config['receipt_digest'])
    marker={'version':'i02-readonly-legacy-comparator-v1','release_id':config['release_id'],'manifest_digest':config['manifest_digest'],'port':port}
    if runtime.exists():
        if json.loads((runtime/'comparator.json').read_text())!=marker:raise ValueError('Unrelated comparator runtime')
    else:
        runtime.mkdir(parents=True);(runtime/'comparator.json').write_text(json.dumps(marker))
    for url,(descriptor,raw) in release.assets.items():
        if url.startswith('/media/'):
            path=inside(runtime/'media',url[len('/media/'):]);path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists() and path.read_bytes()!=raw:raise ValueError('Unrelated comparator media')
            path.write_bytes(raw)
            if sha256(path.read_bytes()).hexdigest()!=descriptor['sha256']:raise ValueError('Comparator media integrity failure')
    env=dict(os.environ,DJANGO_SETTINGS_MODULE='config.settings',DJANGO_SECRET_KEY=secrets.token_urlsafe(48),
        DJANGO_DB_BACKEND='postgresql',DJANGO_DB_NAME=db.url.database,DJANGO_DB_USER=db.url.username,
        DJANGO_DB_PASSWORD=db.url.password or 'synthetic-local-trust-unused',DJANGO_DB_HOST=db.url.host,
        DJANGO_DB_PORT=str(db.url.port or 5432),DJANGO_DEBUG='1',DJANGO_RUNTIME_ROOT=str(runtime),
        DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost',PGOPTIONS='-c default_transaction_read_only=on -c statement_timeout=30000')
    # Verify the actual legacy Django connection before exposing HTTP.
    probe="import django;django.setup();from django.db import connection;c=connection.cursor();c.execute('SHOW transaction_read_only');assert c.fetchone()[0]=='on';c.close();print('PASS: legacy Django connection read-only')"
    subprocess.run([str(Path(legacy_python).resolve()),'-c',probe],cwd=repository,env=env,check=True)
    print('Comparator: original Django public GETs; reserved synthetic PostgreSQL; no migrations/bootstrap; read-only',flush=True)
    return subprocess.call([str(Path(legacy_python).resolve()),'manage.py','runserver',f'127.0.0.1:{port}','--noreload'],cwd=repository,env=env)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--build-config',required=True);parser.add_argument('--legacy-python',required=True);parser.add_argument('--runtime-root',required=True);parser.add_argument('--port',type=int,default=8132)
    args=parser.parse_args()
    try:
        config=json.loads(Path(args.build_config).read_text(encoding='utf-8-sig'))
        result=run(config,args.legacy_python,args.runtime_root,args.port)
    except (Exception,KeyboardInterrupt):
        print('Legacy comparator stopped or preflight failed; no database writes authorized',file=sys.stderr);result=1
    raise SystemExit(result)
