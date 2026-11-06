"""One browser origin with Vite HMR and a private loopback FastAPI process."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time
import uuid
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def port_open(port):
    with socket.socket() as connection:
        connection.settimeout(.2)
        return connection.connect_ex(('127.0.0.1', port)) == 0


@contextmanager
def supervisor_lock(dev):
    # The OS releases this lock even if the supervisor is killed.
    with (dev / 'supervisor.lock').open('a+b') as stream:
        try:
            if os.name == 'nt':
                import msvcrt
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise RuntimeError('This checkout already has a dev supervisor') from None
        yield


def prepare_view(settings, output):
    from sqlalchemy.engine import make_url
    from backend.infrastructure.database import DatabaseConfig, create_engine
    from backend.infrastructure.uow import UnitOfWork
    from backend.content.releases import active_descriptor
    from backend.content.public_runtime import artifact_for_descriptor
    from frontend.prepare_public import prepare

    config = DatabaseConfig(make_url(settings['MATHSTART_DATABASE_URL']))
    if config.url.drivername != 'postgresql+psycopg':
        raise ValueError('Target PostgreSQL configuration required')
    engine = create_engine(config)
    try:
        with UnitOfWork(engine) as uow:
            import sqlalchemy as sa
            uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
            descriptor = active_descriptor(uow, 'public')
        _, manifest = artifact_for_descriptor(settings['MATHSTART_PUBLIC_ARTIFACT_ROOT'],
            json.loads(settings['MATHSTART_PUBLIC_ARTIFACT_DIGESTS']), descriptor)
        prepare(settings['MATHSTART_RELEASE_ROOT'], descriptor.release_id, descriptor.manifest_digest,
            settings['MATHSTART_PUBLIC_ORIGIN'], output, manifest['input_receipt_digest'])
    finally:
        engine.dispose()
    data = json.loads(output.read_text(encoding='utf-8'))
    legacy = [path for path, view in data['routes'].items()
              if not view.get('public_design') and view['page'].get('renderer_version') != 'react-v1']
    data['backend_paths'] = sorted(set(legacy + [r['old_path'] for r in manifest['redirects']]
        + ['/glavnaya/', '/sitemap.xml', '/robots.txt', '/favicon.ico']))
    curriculum = (ROOT / 'curriculum').resolve()
    paths = []
    for view in data['routes'].values():
        if view['page'].get('renderer_version') != 'react-v1':
            continue
        source = (ROOT / view['page']['source']['path']).resolve()
        if not source.is_relative_to(curriculum) or source.name != 'lesson.json':
            raise ValueError('Development content path escaped curriculum')
        paths.append(str(source.with_name('content.json')))
    data['dev_content_paths'] = sorted(set(paths))
    output.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')


def stop_child(process):
    if process.poll() is not None:
        return
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True, timeout=10)
    else:
        os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name != 'nt':
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.wait(timeout=5)


def request_stop(dev):
    manifest = dev / 'processes.json'
    if not manifest.exists():
        print('Dev-режим не запущен через этот checkout', flush=True)
        return 0
    current = json.loads(manifest.read_text(encoding='utf-8'))
    if current.get('owner') != str(ROOT):
        raise ValueError('Development instance belongs to another checkout')
    instance = str(uuid.UUID(current['instance']))
    request = dev / ('stop-' + instance + '.request')
    request.write_text('stop', encoding='ascii')
    deadline = time.monotonic() + 60
    while manifest.exists() and time.monotonic() < deadline:
        try:
            running = json.loads(manifest.read_text(encoding='utf-8'))
        except FileNotFoundError:
            break
        if running.get('instance') != instance:
            raise RuntimeError('Development instance changed during stop')
        time.sleep(.2)
    if manifest.exists():
        raise RuntimeError('Supervisor did not acknowledge stop; no foreign process was killed')
    print('Dev-режим остановлен; собранная версия и БД сохранены', flush=True)
    return 0


def wait_for_database(settings, check_running):
    import psycopg

    url = settings['MATHSTART_DATABASE_URL'].replace('postgresql+psycopg:', 'postgresql:', 1)
    deadline = time.monotonic() + 30
    while True:
        check_running()
        try:
            with psycopg.connect(url, connect_timeout=2):
                return
        except psycopg.OperationalError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(.25)


def wait_for_http(client, origin, path, media_type, check_running):
    from httpx import RequestError

    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        check_running()
        try:
            response = client.get(origin + path)
            if response.status_code == 200 and media_type in response.headers.get('content-type', ''):
                check_running()
                return
        except RequestError:
            pass
        time.sleep(.25)
    raise TimeoutError('HTTP readiness timed out')


def backend_sources():
    sources = {}
    for path in (ROOT / 'backend').rglob('*.py'):
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue  # An editor can replace the file between listing and stat.
        sources[path] = (stat.st_mtime_ns, stat.st_size)
    return sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, default=ROOT / 'var/local/lesson-preview/private-env.json')
    parser.add_argument('--api-port', type=int, default=8132)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--stop', action='store_true')
    parser.add_argument('--host-dev', action='store_true', help='Manage the prepared host-dev PostgreSQL and reload FastAPI')
    parser.add_argument('--container', action='store_true', help='Bind Vite to the container interface; public origin stays loopback')
    args = parser.parse_args()
    dev = ROOT / 'var/local/dev'
    if args.stop:
        return request_stop(dev)
    if args.host_dev and (args.container or args.prepare_only
                          or args.env_file.resolve() != ROOT / 'var/local/lesson-preview/private-env.json'):
        parser.error('--host-dev requires the default checkout installation')
    settings_path = args.env_file.resolve()
    if args.host_dev and not settings_path.is_file():
        parser.error('Host-dev is not prepared. See docs/local-development-host.md.')
    settings = json.loads(settings_path.read_text(encoding='utf-8'))
    if not isinstance(settings, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in settings.items()):
        raise ValueError('Expected private string environment mapping')
    origin = urlsplit(settings['MATHSTART_PUBLIC_ORIGIN'])
    if (origin.scheme != 'http' or origin.hostname != '127.0.0.1' or not origin.port
            or origin.path not in ('', '/') or origin.query or origin.fragment or origin.username or origin.password
            or not 1 <= args.api_port <= 65535 or args.api_port == origin.port):
        raise ValueError('Distinct explicit loopback ports required')
    dev.mkdir(parents=True, exist_ok=True)
    if args.host_dev and origin.port != 8131:
        parser.error('Host-dev requires http://127.0.0.1:8131')
    if args.prepare_only:
        prepare_dev_view(settings, dev)
        print('Development view prepared; no build, publication or database writes', flush=True)
        return 0
    with supervisor_lock(dev):
        if port_open(origin.port) or port_open(args.api_port):
            parser.error(f'Порт {origin.port} или {args.api_port} занят. Остановите свой режим его штатной командой.')
        return supervise(args, dev, settings_path, settings, origin)


def prepare_dev_view(settings, dev):
    view = dev / 'public-view.json'
    stage_started = time.monotonic()
    prepare_view(settings, view)
    print(f'TIMING dev projection: {time.monotonic() - stage_started:.3f}s', flush=True)
    (dev / 'runner.json').write_text(json.dumps({'python': sys.executable}), encoding='utf-8')
    return view


def supervise(args, dev, settings_path, settings, origin):
    node = shutil.which('node')
    vite_cli = ROOT / 'frontend/node_modules/@react-router/dev/bin.js'
    if node is None or not vite_cli.is_file():
        raise RuntimeError('Node 24 and locked frontend dependencies required; see docs/local-development-host.md')
    # Private credentials belong only to the Python backend, never the Vite child.
    node_env = {k: v for k, v in os.environ.items() if not k.startswith('MATHSTART_')}
    node_env.update(NODE_ENV='development', MATHSTART_DEV_MODE='1',
        MATHSTART_DEV_ORIGIN=settings['MATHSTART_PUBLIC_ORIGIN'], MATHSTART_DEV_API_ORIGIN=f'http://127.0.0.1:{args.api_port}')
    if args.container:
        node_env['MATHSTART_DEV_CONTAINER'] = '1'
    options = {'creationflags': subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == 'nt' else {'start_new_session': True}
    children = []
    if os.name != 'nt':
        def terminate(_signum, _frame):
            raise KeyboardInterrupt
        signal.signal(signal.SIGTERM, terminate)
    instance = str(uuid.uuid4())
    stop_request = dev / ('stop-' + instance + '.request')
    manifest = dev / 'processes.json'
    pending = dev / 'processes.tmp'
    pending.write_text(json.dumps({'owner': str(ROOT), 'instance': instance, 'supervisor': os.getpid(),
        'origin': settings['MATHSTART_PUBLIC_ORIGIN']}), encoding='utf-8')
    pending.replace(manifest)
    database = None
    stage = 'PostgreSQL'

    def check_running(processes=children):
        if stop_request.exists():
            raise KeyboardInterrupt
        if any(child.poll() is not None for child in processes):
            raise RuntimeError('A development process exited')

    try:
        if args.host_dev:
            from team_local import installation, set_database_running

            stage_started = time.monotonic()
            state = installation()
            try:
                set_database_running(state, True)
            except RuntimeError as error:
                print(str(error), file=sys.stderr)
                raise
            database = state
            wait_for_database(settings, check_running)
            print(f'TIMING host PostgreSQL: {time.monotonic() - stage_started:.3f}s', flush=True)
        stage = 'read-only dev projection'
        node_env['MATHSTART_PUBLIC_VIEW'] = str(prepare_dev_view(settings, dev))
        check_running()
        stage = 'FastAPI startup'
        stage_started = time.monotonic()
        backend_command = [sys.executable, str(ROOT / 'scripts/lesson_server.py'), '--env-file', str(settings_path), '--port', str(args.api_port)]
        sources = backend_sources() if args.host_dev else None
        children.append(subprocess.Popen(backend_command, cwd=ROOT, stdout=sys.stdout, stderr=sys.stderr, **options))
        deadline = time.monotonic() + 25
        while not port_open(args.api_port):
            check_running()
            if time.monotonic() >= deadline:
                raise RuntimeError('Internal FastAPI did not start')
            time.sleep(.2)
        print(f'TIMING internal API socket: {time.monotonic() - stage_started:.3f}s', flush=True)
        stage = 'Vite startup'
        frontend = subprocess.Popen([node, str(vite_cli), 'dev', '--host', '0.0.0.0' if args.container else '127.0.0.1', '--port', str(origin.port)], cwd=ROOT / 'frontend', env=node_env, stdout=sys.stdout, stderr=sys.stderr, **options)
        children.append(frontend)
        if args.host_dev:
            import httpx

            with httpx.Client(trust_env=False, timeout=10) as client:
                for path, media_type in (('/', 'text/html'), ('/api/v1/grades/', 'application/json')):
                    stage = f'HTTP readiness {path}'
                    wait_for_http(client, settings['MATHSTART_PUBLIC_ORIGIN'].rstrip('/'), path, media_type, check_running)
        stage = 'running development processes'
        label = 'Host-dev готов: ' if args.host_dev else 'Разработка с HMR: '
        print(label + settings['MATHSTART_PUBLIC_ORIGIN'] + ' (Ctrl+C — остановить)', flush=True)
        watched_processes = [frontend] if args.host_dev else children
        reported_api_exit = False
        while True:
            check_running(watched_processes)
            if args.host_dev:
                current_sources = backend_sources()
                if current_sources != sources:
                    sources = current_sources
                    # Uvicorn's Windows reload uses console signals, which cannot
                    # reach a child started without a console by this supervisor.
                    print('Python sources changed; restarting FastAPI', flush=True)
                    stop_child(children[0])
                    children[0] = subprocess.Popen(backend_command, cwd=ROOT, stdout=sys.stdout, stderr=sys.stderr, **options)
                    reported_api_exit = False
                if children[0].poll() is not None and not reported_api_exit:
                    print('FastAPI exited. Save a backend Python file to retry.', file=sys.stderr)
                    reported_api_exit = True
            time.sleep(.4)
    except KeyboardInterrupt:
        return 0
    except Exception as error:
        print(f'Development failed at {stage}: {type(error).__name__}. See docs/local-development.md and local stage logs.', file=sys.stderr)
        return 1
    finally:
        for child in reversed(children):
            stop_child(child)
        if database is not None:
            try:
                set_database_running(database, False)
            except Exception:
                raise RuntimeError('PostgreSQL shutdown failed; see var/local/team/logs') from None
        manifest.unlink()
        stop_request.unlink(missing_ok=True)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        detail = str(error) if type(error) is RuntimeError else type(error).__name__
        print('Development failed: ' + detail + '. See docs/local-development.md; private configuration is not logged.', file=sys.stderr)
        raise SystemExit(1) from None
