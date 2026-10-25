"""Explicit, checkout-owned local installation. Never called by API/dev startup.

Uses the ordinary schema and Content CLIs, not synthetic fixtures. Private
configuration and stage logs stay in ignored var/local/team. No global env file,
existing database, operator account or saved runner is needed.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / 'var/local/team'
STATE = LOCAL / 'installation.json'
PRIVATE = ROOT / 'var/local/lesson-preview/private-env.json'
POSTGRES = 'postgres@sha256:efedf3595f1d6f415c08568ba171029bf54052e754cc9f030e3f2412b21f3d67'


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def environment(values=None):
    result = {k: v for k, v in os.environ.items()
              if not k.startswith(('MATHSTART_', 'DJANGO_')) and k != 'PYTHONPATH'}
    result.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONUNBUFFERED='1')
    result.update(values or {})
    return result


def run(command, stage, values=None, timeout=180):
    # Child failures may contain DBAPI details: capture privately, redact known
    # secrets, and show only the stage name. Never echo environment or SQL.
    result = subprocess.run(list(map(str, command)), cwd=ROOT, env=environment(values),
                            capture_output=True, timeout=timeout)
    output = (result.stdout + result.stderr).decode('utf-8', errors='replace')
    if LOCAL.exists():
        sensitive = []
        for path in (LOCAL / 'schema-env.json', PRIVATE):
            if path.exists():
                sensitive.extend(v for k, v in read_json(path).items()
                                 if any(word in k for word in ('KEY', 'URL', 'PASSWORD')))
        if STATE.exists():
            sensitive.extend(read_json(STATE).get('passwords', {}).values())
        for value in sorted(sensitive, key=len, reverse=True):
            if value:
                output = output.replace(value, '[REDACTED]')
        logs = LOCAL / 'logs'
        logs.mkdir(exist_ok=True)
        (logs / (stage + '.log')).write_text(output, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Stage failed: ' + stage + '; see ignored var/local/team/logs')
    return result.stdout.decode('utf-8').strip()


def cli(module, arguments, stage, values, timeout=180):
    return run([sys.executable, '-m', module, *arguments], stage, values, timeout)


def free_port(port):
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', port))


def installation():
    state = read_json(STATE)
    if state['checkout'] != str(ROOT):
        raise RuntimeError('Installation belongs to another checkout; do not copy var/')
    return state


def owned_container(state):
    data = json.loads(run(['docker', 'container', 'inspect', state['container_id']], 'inspect-db'))[0]
    if (data['Name'] != '/' + state['name']
            or data['Config']['Labels'].get('mathstart.local-owner') != state['owner']
            or not any(m.get('Name') == state['volume'] and m['Destination'] == '/var/lib/postgresql/data'
                       for m in data['Mounts'])):
        raise RuntimeError('Database ownership mismatch')
    return data


def init(port):
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError('Use Python 3.12 for the documented locked environment')
    if LOCAL.exists() or PRIVATE.exists():
        raise RuntimeError('Local configuration already exists; it will not be overwritten')
    if not 1024 <= port <= 65535 or port in (8131, 8132):
        raise RuntimeError('Choose a distinct unprivileged PostgreSQL loopback port')
    free_port(port)
    run(['docker', 'version', '--format', '{{.Server.Version}}'], 'docker-version')
    owner = uuid.uuid4().hex
    name = 'mathstart-dev-' + owner[:12]
    passwords = {k: secrets.token_urlsafe(36) for k in ('admin', 'schema', 'runtime')}
    state = {'version': 1, 'checkout': str(ROOT), 'owner': owner, 'name': name,
             'volume': name + '-data', 'pg_port': port, 'passwords': passwords,
             'release': 'local-' + owner[:12], 'publisher': str(uuid.uuid4())}
    write_json(STATE, state)
    pg_env = LOCAL / 'postgres.env'
    pg_env.write_text('POSTGRES_USER=local_admin\nPOSTGRES_DB=mathstart_dev\nPOSTGRES_PASSWORD='
                      + passwords['admin'] + '\n', encoding='utf-8')
    run(['docker', 'volume', 'create', '--label', 'mathstart.local-owner=' + owner,
         state['volume']], 'create-volume')
    state['container_id'] = run(['docker', 'run', '--detach', '--name', name,
        '--label', 'mathstart.local-owner=' + owner, '--publish', f'127.0.0.1:{port}:5432',
        '--env-file', pg_env, '--mount', 'type=volume,source=' + state['volume']
        + ',target=/var/lib/postgresql/data', POSTGRES], 'create-db')
    STATE.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    import psycopg
    from psycopg import sql
    connection = None
    for _ in range(90):
        try:
            connection = psycopg.connect(host='127.0.0.1', port=port, dbname='mathstart_dev',
                                        user='local_admin', password=passwords['admin'], autocommit=True)
            break
        except psycopg.OperationalError:
            time.sleep(.5)
    if connection is None:
        raise RuntimeError('New PostgreSQL did not start; configuration retained for diagnosis')
    with connection:
        for role, key in (('local_schema', 'schema'), ('local_runtime', 'runtime')):
            connection.execute(sql.SQL('CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD {}')
                               .format(sql.Identifier(role), sql.Literal(passwords[key])))
        connection.execute('ALTER DATABASE mathstart_dev OWNER TO local_schema')
        connection.execute('REVOKE CREATE ON SCHEMA public FROM PUBLIC')
        connection.execute('GRANT USAGE, CREATE ON SCHEMA public TO local_schema')
        connection.execute('GRANT CONNECT ON DATABASE mathstart_dev TO local_runtime')
        connection.execute('GRANT USAGE ON SCHEMA public TO local_runtime')
    def dsn(role, key):
        return f'postgresql+psycopg://{role}:{passwords[key]}@127.0.0.1:{port}/mathstart_dev'
    values = {'MATHSTART_DB_BACKEND': 'postgresql',
        'MATHSTART_DATABASE_URL': dsn('local_runtime', 'runtime'),
        'MATHSTART_HTTP_SIGNING_KEY': secrets.token_urlsafe(48),
        'MATHSTART_PUBLIC_ORIGIN': 'http://127.0.0.1:8131',
        'MATHSTART_RELEASE_ROOT': 'var/local/team/serving/releases',
        'MATHSTART_PUBLIC_ARTIFACT_ROOT': 'var/local/team/serving/frontend',
        'MATHSTART_PUBLIC_ARTIFACT_DIGESTS': '{}'}
    write_json(PRIVATE, values)
    write_json(LOCAL / 'schema-env.json', {**values,
        'MATHSTART_DATABASE_URL': dsn('local_schema', 'schema'),
        'MATHSTART_SCHEMA_SIGNING_KEY': secrets.token_urlsafe(48)})
    print('Created checkout-owned PostgreSQL, separate schema/runtime roles and private config. No app schema or users yet.')


def roots():
    return ['--input-root', str(LOCAL / 'inputs'), '--output-root', str(LOCAL / 'output'),
            '--release-root', str(LOCAL / 'serving/releases'),
            '--artifact-root', str(LOCAL / 'serving/frontend')]


def schema_apply(values, reviewed):
    cli('backend.release_migrate', ['apply', '--maintenance', '--plan-file', str(LOCAL / 'schema.json'),
        '--reviewed-plan-sha256', reviewed], 'schema-apply', values)
    # Only schema CLI does DDL. Runtime has DML permissions, never DDL ownership.
    import psycopg
    url = values['MATHSTART_DATABASE_URL'].replace('postgresql+psycopg:', 'postgresql:', 1)
    with psycopg.connect(url) as connection:
        connection.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO local_runtime')
        connection.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO local_runtime')
    print(cli('backend.release_migrate', ['check'], 'schema-check', values))


def content(values, state):
    source_sha = run(['git', 'rev-parse', 'HEAD'], 'source-sha')
    # The ordinary preparation verifies committed source bytes itself.
    prepared = json.loads(cli('backend.content.publish', ['prepare-bootstrap', '--source-root', '.',
        '--source-sha', source_sha, '--release-id', state['release'], '--input-root', str(LOCAL / 'inputs'),
        '--changes', str(LOCAL / 'edition.json')], 'prepare-content', values, 300))
    built = json.loads(cli('frontend.build_public', ['--input-root', str(LOCAL / 'inputs'),
        '--release-id', state['release'], '--manifest-digest', prepared['manifest_digest'],
        '--receipt-digest', prepared['input_receipt_digest'], '--output', str(LOCAL / 'output'),
        '--origin', values['MATHSTART_PUBLIC_ORIGIN']], 'build-content', values, 900).splitlines()[-1])
    planned = json.loads(cli('backend.content.publish', ['plan', '--changes', str(LOCAL / 'edition.json'),
        '--plan', str(LOCAL / 'publication.json'), '--origin', values['MATHSTART_PUBLIC_ORIGIN'],
        '--output-digest', built['output_manifest_digest'], *roots()], 'plan-content', values, 300))
    runtime = read_json(PRIVATE)
    runtime['MATHSTART_PUBLIC_ARTIFACT_DIGESTS'] = json.dumps({state['release']: built['output_manifest_digest']})
    PRIVATE.write_text(json.dumps(runtime, indent=2) + '\n', encoding='utf-8')
    print('Prepared source SHA ' + source_sha + '; ' + str(built['pages']) + ' pages.')
    print('Review local publication plan var/local/team/publication.json (initial install, previous=null).')
    print('Publication plan SHA256 ' + planned['plan_digest'])


def publish(values, state, reviewed):
    plan_path = LOCAL / 'publication.json'
    # Same canonical digest used by the domain publisher; do not re-encode differently.
    sys.path.insert(0, str(ROOT))
    from backend.content.participant import digest
    if not secrets.compare_digest(digest(read_json(plan_path)), reviewed):
        raise RuntimeError('Reviewed publication plan digest mismatch')
    free_port(8131)
    log_path = LOCAL / 'logs/publication-server.log'
    with log_path.open('w', encoding='utf-8') as log:
        options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}
        server = subprocess.Popen([sys.executable, str(ROOT / 'scripts/lesson_server.py')],
            cwd=ROOT, env=environment(), stdout=log, stderr=log, **options)
        try:
            for _ in range(100):
                if server.poll() is not None:
                    raise RuntimeError('Temporary publication gateway exited')
                with socket.socket() as client:
                    if client.connect_ex(('127.0.0.1', 8131)) == 0:
                        break
                time.sleep(.2)
            else:
                raise RuntimeError('Temporary publication gateway did not start')
            print(cli('backend.content.publish', ['publish', '--plan', str(plan_path),
                '--key', state['release'], '--owner', state['publisher'], *roots()],
                'publish-content', {**values, **{k: v for k, v in read_json(PRIVATE).items()
                if k != 'MATHSTART_DATABASE_URL'}}, 900))
        finally:
            server.terminate()
            try:
                server.wait(timeout=15)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
    print('Publication complete; temporary gateway stopped. Start npm --prefix frontend run dev.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'schema-preview', 'schema-apply', 'content', 'publish', 'db-start', 'db-stop'])
    parser.add_argument('--pg-port', type=int, default=55449)
    parser.add_argument('--reviewed-plan-sha256')
    args = parser.parse_args()
    os.chdir(ROOT)
    try:
        if args.action == 'init':
            init(args.pg_port)
            return 0
        state = installation()
        owned_container(state)
        if args.action in ('db-start', 'db-stop'):
            print(run(['docker', 'start' if args.action == 'db-start' else 'stop', state['container_id']], args.action))
            return 0
        values = read_json(LOCAL / 'schema-env.json')
        if args.action == 'schema-preview':
            print(cli('backend.release_migrate', ['preview', '--profile', 'FRESH', '--plan-file', str(LOCAL / 'schema.json')], 'schema-preview', values))
            print('Review profile=FRESH, table_count=0, target_head, database/role binding in var/local/team/schema.json; apply within 30 minutes.')
        elif args.action in ('schema-apply', 'publish'):
            if not re.fullmatch('[a-f0-9]{64}', args.reviewed_plan_sha256 or ''):
                raise RuntimeError('Explicit --reviewed-plan-sha256 required after reviewing the plan')
            if args.action == 'schema-apply':
                schema_apply(values, args.reviewed_plan_sha256)
            else:
                publish(values, state, args.reviewed_plan_sha256)
        else:
            content(values, state)
        return 0
    except Exception as error:
        # Avoid DBAPI errors/DSNs/SQL parameters in terminal output.
        message = str(error) if isinstance(error, RuntimeError) else type(error).__name__
        print('LOCAL_SETUP_STOPPED: ' + message + '. State retained; do not blindly repeat a failed apply/publish.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
