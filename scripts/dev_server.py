"""One browser origin with Vite HMR and a private loopback FastAPI process."""
from __future__ import annotations

import argparse
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
    deadline = time.monotonic() + 15
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, default=ROOT / 'var/local/lesson-preview/private-env.json')
    parser.add_argument('--api-port', type=int, default=8132)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--stop', action='store_true')
    parser.add_argument('--container', action='store_true', help='Bind Vite to the container interface; public origin stays loopback')
    args = parser.parse_args()
    dev = ROOT / 'var/local/dev'
    if args.stop:
        return request_stop(dev)
    settings_path = args.env_file.resolve()
    settings = json.loads(settings_path.read_text(encoding='utf-8'))
    if not isinstance(settings, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in settings.items()):
        raise ValueError('Expected private string environment mapping')
    origin = urlsplit(settings['MATHSTART_PUBLIC_ORIGIN'])
    if (origin.scheme != 'http' or origin.hostname != '127.0.0.1' or not origin.port
            or origin.path not in ('', '/') or origin.query or origin.fragment or origin.username or origin.password
            or not 1 <= args.api_port <= 65535 or args.api_port == origin.port):
        raise ValueError('Distinct explicit loopback ports required')
    dev.mkdir(parents=True, exist_ok=True)
    if not args.prepare_only and (port_open(origin.port) or port_open(args.api_port)):
        parser.error(f'Порт {origin.port} или {args.api_port} занят. Свой dev-режим остановите через npm --prefix frontend run dev -- --stop; чужой процесс не завершается автоматически.')
    view = dev / 'public-view.json'
    prepare_view(settings, view)
    (dev / 'runner.json').write_text(json.dumps({'python': sys.executable}), encoding='utf-8')
    if args.prepare_only:
        print('Development view prepared; no build, publication or database writes', flush=True)
        return 0
    node = shutil.which('node')
    if node is None:
        raise RuntimeError('Node 24 and locked frontend dependencies required')
    # Private credentials belong only to the Python backend, never the Vite child.
    node_env = {k: v for k, v in os.environ.items() if not k.startswith('MATHSTART_')}
    node_env.update(NODE_ENV='development', MATHSTART_PUBLIC_VIEW=str(view), MATHSTART_DEV_MODE='1',
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
    try:
        backend = subprocess.Popen([sys.executable, str(ROOT / 'scripts/lesson_server.py'), '--env-file', str(settings_path), '--port', str(args.api_port)], cwd=ROOT, stdout=sys.stdout, stderr=sys.stderr, **options)
        children.append(backend)
        deadline = time.monotonic() + 25
        while not port_open(args.api_port):
            if backend.poll() is not None or time.monotonic() >= deadline:
                raise RuntimeError('Internal FastAPI did not start')
            time.sleep(.2)
        frontend = subprocess.Popen([node, str(ROOT / 'frontend/node_modules/@react-router/dev/bin.js'), 'dev', '--host', '0.0.0.0' if args.container else '127.0.0.1', '--port', str(origin.port)], cwd=ROOT / 'frontend', env=node_env, stdout=sys.stdout, stderr=sys.stderr, **options)
        children.append(frontend)
        (dev / 'processes.json').write_text(json.dumps({'owner': str(ROOT), 'instance': instance, 'supervisor': os.getpid(),
            'backend': backend.pid, 'frontend': frontend.pid, 'origin': settings['MATHSTART_PUBLIC_ORIGIN']}), encoding='utf-8')
        print('Разработка с HMR: ' + settings['MATHSTART_PUBLIC_ORIGIN'] + ' (Ctrl+C — остановить оба процесса)', flush=True)
        while all(child.poll() is None for child in children):
            if stop_request.exists():
                return 0
            time.sleep(.4)
        return next((child.returncode for child in children if child.returncode), 1)
    except KeyboardInterrupt:
        return 0
    finally:
        for child in reversed(children):
            stop_child(child)
        stop_request.unlink(missing_ok=True)
        manifest = dev / 'processes.json'
        if manifest.exists() and json.loads(manifest.read_text(encoding='utf-8')).get('instance') == instance:
            manifest.unlink()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        print('Development startup failed: ' + type(error).__name__ + '. See docs/local-development.md; private configuration is not logged.', file=sys.stderr)
        raise SystemExit(1) from None
