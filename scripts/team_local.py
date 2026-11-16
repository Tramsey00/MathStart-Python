"""Explicit, checkout-owned local installation. Never called by API/dev startup.

Uses the ordinary schema and Content CLIs, not synthetic fixtures. Private
configuration and stage logs stay in ignored var/local/team. No global env file,
existing database, operator account or saved runner is needed.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
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
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / 'var/local/team'
STATE = LOCAL / 'installation.json'
LEGACY_PRIVATE = ROOT / 'var/local/lesson-preview/private-env.json'
POSTGRES = 'postgres@sha256:efedf3595f1d6f415c08568ba171029bf54052e754cc9f030e3f2412b21f3d67'
SERVING = None


@contextmanager
def installation_paths(local, private, state, serving):
    """Reuse the host operator orchestration in one locked container operation."""
    global LOCAL, PRIVATE, STATE, SERVING
    previous = LOCAL, PRIVATE, STATE, SERVING
    LOCAL, PRIVATE, STATE, SERVING = local, private, state, serving
    try:
        yield
    finally:
        LOCAL, PRIVATE, STATE, SERVING = previous


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def private_configuration():
    if not STATE.is_file():
        return LOCAL / 'private-env.json'
    layout = read_json(STATE).get('runtime_config', 'legacy')
    if layout not in {'legacy', 'team'}:
        raise RuntimeError('Unsupported local runtime configuration layout')
    return LOCAL / 'private-env.json' if layout == 'team' else LEGACY_PRIVATE


PRIVATE = private_configuration()


def require_windows_long_paths():
    if os.name != 'nt':
        return
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r'SYSTEM\CurrentControlSet\Control\FileSystem') as key:
            enabled = winreg.QueryValueEx(key, 'LongPathsEnabled')[0]
    except OSError:
        enabled = 0
    if enabled != 1:
        raise RuntimeError('Enable Windows LongPathsEnabled=1 and restart Windows before host-dev preparation/start. See docs/local-development-host.md')


def environment(values=None):
    result = {k: v for k, v in os.environ.items()
              if not k.startswith(('MATHSTART_', 'DJANGO_')) and k != 'PYTHONPATH'}
    result.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONUNBUFFERED='1')
    result.update(values or {})
    return result


def run(command, stage, values=None, timeout=180):
    # Child failures may contain DBAPI details: capture privately, redact known
    # secrets, and show only the stage name. Never echo environment or SQL.
    try:
        result = subprocess.run(list(map(str, command)), cwd=ROOT, env=environment(values),
                                capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        partial = (exc.stdout or b'') + (exc.stderr or b'')
        write_stage_log(stage, partial, f'\nStage {stage} timed out after {timeout} seconds.\n')
        raise
    write_stage_log(stage, result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError('Stage failed: ' + stage + '; see ignored var/local/team/logs')
    return result.stdout.decode('utf-8').strip()


def write_stage_log(stage, raw, diagnostic=''):
    if LOCAL.exists():
        output = raw.decode('utf-8', errors='replace') + diagnostic
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


def set_database_running(state, running):
    if owned_container(state)['State']['Running'] == running:
        return False
    action = 'start' if running else 'stop'
    run(['docker', action, state['container_id']], 'db-' + action, timeout=30)
    return True


def local_database_url(state, role):
    password = state['passwords'][role]
    return f"postgresql+psycopg://local_{role}:{password}@127.0.0.1:{state['pg_port']}/mathstart_dev"


def init(port):
    require_windows_long_paths()
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
             'release': 'local-' + owner[:12], 'publisher': str(uuid.uuid4()),
             'runtime_config': 'team'}
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
    values = {'MATHSTART_DB_BACKEND': 'postgresql',
        'MATHSTART_DATABASE_URL': local_database_url(state, 'runtime'),
        'MATHSTART_HTTP_SIGNING_KEY': secrets.token_urlsafe(48),
        'MATHSTART_PUBLIC_ORIGIN': 'http://127.0.0.1:8131',
        'MATHSTART_RELEASE_ROOT': 'var/local/team/serving/releases',
        'MATHSTART_PUBLIC_ARTIFACT_ROOT': 'var/local/team/serving/frontend',
        'MATHSTART_PUBLIC_ARTIFACT_DIGESTS': '{}'}
    write_json(PRIVATE, values)
    write_json(LOCAL / 'schema-env.json', {**values,
        'MATHSTART_DATABASE_URL': local_database_url(state, 'schema'),
        'MATHSTART_SCHEMA_SIGNING_KEY': secrets.token_urlsafe(48)})
    print('Created checkout-owned PostgreSQL, separate schema/runtime roles and private config. No app schema or users yet.')


def roots():
    serving = SERVING or LOCAL / 'serving'
    return ['--input-root', str(LOCAL / 'inputs'), '--output-root', str(LOCAL / 'output'),
            '--release-root', str(serving / 'releases'),
            '--artifact-root', str(serving / 'frontend')]


def schema_apply(values, reviewed):
    marker = LOCAL / 'schema-apply-pending.json'
    if marker.exists():
        raise RuntimeError('Prior schema apply requires operator review; do not rerun DDL')
    write_json(marker, {'reviewed_plan_sha256': reviewed})
    cli('backend.release_migrate', ['apply', '--maintenance', '--plan-file', str(LOCAL / 'schema.json'),
        '--reviewed-plan-sha256', reviewed], 'schema-apply', values)
    finish_schema_privileges(values, reviewed)


def finish_schema_privileges(values, reviewed):
    """Finish only the ACL stage of a known, committed local schema apply."""
    from backend.release_migrate import code_digest, database_fact, plan_digest, signed
    from backend.migrations.runtime_privileges import grant_runtime_privileges
    from backend.infrastructure.database import DatabaseConfig, create_engine
    from sqlalchemy.engine import make_url
    import psycopg

    marker = LOCAL / 'schema-apply-pending.json'
    plan = read_json(LOCAL / 'schema.json')
    receipt = read_json(LOCAL / 'logs/schema-apply.log')
    if (read_json(marker) != {'reviewed_plan_sha256': reviewed}
            or receipt != {'status': 'APPLIED', 'head': plan['target_head'], 'reviewed_plan_sha256': reviewed}
            or not secrets.compare_digest(plan_digest(plan), reviewed)
            or plan['profile'] != 'FRESH' or plan['code_digest'] != code_digest()
            or not secrets.compare_digest(plan['signature'], signed(values['MATHSTART_SCHEMA_SIGNING_KEY'],
                'schema.plan.v1', {k: v for k, v in plan.items() if k != 'signature'}))):
        raise RuntimeError('ACL completion requires the exact reviewed plan and APPLIED receipt')
    url = make_url(values['MATHSTART_DATABASE_URL'])
    engine = create_engine(DatabaseConfig(url))
    try:
        with engine.connect() as connection:
            if database_fact(connection) != plan['database']:
                raise RuntimeError('ACL completion database/role binding changed')
    finally:
        engine.dispose()
    # Physical compatibility must be established before opening the ACL transaction.
    print(cli('backend.release_migrate', ['check'], 'schema-check', values))
    try:
        with psycopg.connect(url.set(drivername='postgresql').render_as_string(hide_password=False)) as connection:
            grant_runtime_privileges(connection)
    except Exception:
        raise RuntimeError('Schema APPLIED; runtime ACL completion failed. Retain the receipt and pending marker.') from None



def content(values, state):
    if (LOCAL / 'schema-apply-pending.json').exists():
        raise RuntimeError('Schema apply pending review; Content preparation is blocked')
    require_windows_long_paths()
    source_sha = run(['git', 'rev-parse', 'HEAD'], 'source-sha')
    # The ordinary preparation verifies committed source bytes itself.
    prepared = json.loads(cli('backend.content.publish', ['prepare-bootstrap', '--source-root', '.',
        '--source-sha', source_sha, '--release-id', state['release'], '--input-root', str(LOCAL / 'inputs'),
        '--changes', str(LOCAL / 'edition.json')], 'prepare-content', values, 600))
    built = json.loads(cli('frontend.build_public', ['--input-root', str(LOCAL / 'inputs'),
        '--release-id', state['release'], '--manifest-digest', prepared['manifest_digest'],
        '--receipt-digest', prepared['input_receipt_digest'], '--output', str(LOCAL / 'output'),
        '--origin', values['MATHSTART_PUBLIC_ORIGIN']], 'build-content', values, 900).splitlines()[-1])
    planned = json.loads(cli('backend.content.publish', ['plan', '--changes', str(LOCAL / 'edition.json'),
        '--plan', str(LOCAL / 'publication.json'), '--origin', values['MATHSTART_PUBLIC_ORIGIN'],
        '--output-digest', built['output_manifest_digest'], *roots()], 'plan-content', values, 300))
    runtime = read_json(PRIVATE)
    runtime['MATHSTART_PUBLIC_ARTIFACT_DIGESTS'] = json.dumps({**json.loads(runtime['MATHSTART_PUBLIC_ARTIFACT_DIGESTS']), state['release']: built['output_manifest_digest']})
    PRIVATE.write_text(json.dumps(runtime, indent=2) + '\n', encoding='utf-8')
    print('Prepared source SHA ' + source_sha + '; ' + str(built['pages']) + ' pages.')
    print('Review local publication plan var/local/team/publication.json (initial install, previous=null).')
    print('Publication plan SHA256 ' + planned['plan_digest'])


def finish_cold_publication(values, state):
    """One bounded recovery, only after a proven committed/activated own plan.

    Windows cold DTO validation can outlast the publisher's unchanged 5s HTTP
    guard. Warm the read cache, then repeat the real fenced acknowledgement;
    never repeat a domain update or infer completion from warmup alone.
    """
    observed = json.loads(cli('backend.content.publish', ['status'], 'publication-status', values))
    operation, active = observed['operation'], observed['active']
    if (not operation or not active or operation['phase'] != 'RECOVERY_REQUIRED'
            or operation['db_committed'] is not True or operation['activation_status'] != 'APPLIED'
            or operation['error_code'] != 'PUBLIC_VERIFICATION_FAILED'
            or operation['owner_id'] != state['publisher'] or active['release_id'] != state['release']
            or active['operation_id'] != operation['operation_id']
            or active['fence_generation'] != operation['generation']):
        raise RuntimeError('Publication state needs operator review; automatic recovery refused')
    owner = ['--operation-id', operation['operation_id'], '--owner', state['publisher'],
             '--generation', str(operation['generation'])]
    cli('backend.content.publish', ['renew', *owner], 'renew-before-warmup', values)
    import httpx
    expected = (LOCAL / 'inputs' / state['release'] / 'index.json').read_bytes()
    tick = time.monotonic()
    with httpx.Client(trust_env=False, timeout=60, follow_redirects=False) as client:
        response = client.get(values['MATHSTART_PUBLIC_ORIGIN'] + '/_content/index.json')
    if (response.status_code != 200 or response.content != expected
            or response.headers.get('cache-control') != 'no-store'):
        raise RuntimeError('Read-only publication warmup did not match exact immutable index')
    write_json(LOCAL / 'logs/cold-warmup.json', {'seconds': round(time.monotonic() - tick, 3),
        'index_bytes': len(expected), 'result': 'EXACT_INDEX_ONLY_NOT_PUBLICATION_ACK'})
    cli('backend.content.publish', ['renew', *owner], 'renew-after-warmup', values)
    print('Own committed/activated journal verified; read cache warmed. Resuming ordinary fenced HTTP acknowledgement.', flush=True)
    return cli('backend.content.publish', ['resume', *owner, *roots()], 'resume-content', values, 900)


def publication_gateway_port(plan, values, runtime_values):
    origin = plan.get('origin')
    if not isinstance(origin, str) or any(
            config.get('MATHSTART_PUBLIC_ORIGIN') != origin for config in (values, runtime_values)):
        raise RuntimeError('Publication plan and gateway origin must match')
    port = urlsplit(origin).port
    if not port or origin != f'http://127.0.0.1:{port}':
        raise RuntimeError('Publication requires an explicit loopback HTTP origin')
    return port


def publish(values, state, reviewed):
    if (LOCAL / 'schema-apply-pending.json').exists():
        raise RuntimeError('Schema apply pending review; Content publication is blocked')
    require_windows_long_paths()
    plan_path = LOCAL / 'publication.json'
    # Same canonical digest used by the domain publisher; do not re-encode differently.
    sys.path.insert(0, str(ROOT))
    from backend.content.participant import digest
    plan = read_json(plan_path)
    if not secrets.compare_digest(digest(plan), reviewed):
        raise RuntimeError('Reviewed publication plan digest mismatch')
    runtime_values = read_json(PRIVATE)
    port = publication_gateway_port(plan, values, runtime_values)
    free_port(port)
    log_path = LOCAL / 'logs/publication-server.log'
    with log_path.open('w', encoding='utf-8') as log:
        options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}
        server = subprocess.Popen([sys.executable, str(ROOT / 'scripts/lesson_server.py'), '--env-file', str(PRIVATE)],
            cwd=ROOT, env=environment(), stdout=log, stderr=log, **options)
        try:
            for _ in range(100):
                if server.poll() is not None:
                    raise RuntimeError('Temporary publication gateway exited')
                with socket.socket() as client:
                    if client.connect_ex(('127.0.0.1', port)) == 0:
                        break
                time.sleep(.2)
            else:
                raise RuntimeError('Temporary publication gateway did not start')
            publisher_values = {**values, **{k: v for k, v in runtime_values.items()
                                          if k != 'MATHSTART_DATABASE_URL'}}
            try:
                result = cli('backend.content.publish', ['publish', '--plan', str(plan_path),
                    '--key', state['release'], '--owner', state['publisher'], *roots()],
                    'publish-content', publisher_values, 900)
            except RuntimeError:
                result = finish_cold_publication(publisher_values, state)
            print(result)
        finally:
            server.terminate()
            try:
                server.wait(timeout=15)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
    print('Publication complete; temporary gateway stopped.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'schema-preview', 'schema-apply', 'finish-acl', 'content', 'publish', 'db-start', 'db-stop'])
    parser.add_argument('--pg-port', type=int, default=55449)
    parser.add_argument('--reviewed-plan-sha256')
    args = parser.parse_args()
    os.chdir(ROOT)
    try:
        if args.action == 'init':
            init(args.pg_port)
            return 0
        state = installation()
        if args.action in ('db-start', 'db-stop'):
            set_database_running(state, args.action == 'db-start')
            print('Local PostgreSQL is ' + ('running' if args.action == 'db-start' else 'stopped'))
            return 0
        owned_container(state)
        values = read_json(LOCAL / 'schema-env.json')
        if args.action == 'schema-preview':
            print(cli('backend.release_migrate', ['preview', '--profile', 'FRESH', '--plan-file', str(LOCAL / 'schema.json')], 'schema-preview', values))
            print('Review profile=FRESH, table_count=0, target_head, database/role binding in var/local/team/schema.json; apply within 30 minutes.')
        elif args.action in ('schema-apply', 'finish-acl', 'publish'):
            if not re.fullmatch('[a-f0-9]{64}', args.reviewed_plan_sha256 or ''):
                raise RuntimeError('Explicit --reviewed-plan-sha256 required after reviewing the plan')
            if args.action == 'schema-apply':
                schema_apply(values, args.reviewed_plan_sha256)
                (LOCAL / 'schema-apply-pending.json').unlink()
            elif args.action == 'finish-acl':
                finish_schema_privileges(values, args.reviewed_plan_sha256)
                (LOCAL / 'schema-apply-pending.json').unlink()
            else:
                publish(values, state, args.reviewed_plan_sha256)
                print('Start npm.cmd --prefix frontend run dev:host.')
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
