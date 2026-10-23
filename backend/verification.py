"""Real read-only target checks; incomplete command maps still fail closed."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sqlalchemy as sa

from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.schema import assert_baseline
from backend.content.checks import verify_lesson_sources, inspect_site, inspect_public_quality, active_quality_release

CHECKS = ('system', 'migrations', 'lesson-sources', 'site-integrity', 'content-quality')


def system_check():
    from starlette.testclient import TestClient
    from backend.content.public_runtime import application
    origin = os.environ['MATHSTART_PUBLIC_ORIGIN']
    app = application()
    try:
        with TestClient(app, base_url=origin) as client:
            checks = [('/api/v1/grades/', 200), ('/api/v1/users/me/', 401),
                      ('/api/v1/staff/users/', 401), ('/api/v1/auth/csrf/', 200)]
            for path, status in checks:
                response = client.get(path)
                if response.status_code != status or response.headers.get('cache-control') != 'private, no-store':
                    raise RuntimeError('Target route/security check failed')
            if client.post('/api/v1/auth/login/', content='{}').status_code != 403:
                raise RuntimeError('CSRF gate failed')
            if client.patch('/api/v1/users/me/', content='malformed').status_code != 401:
                raise RuntimeError('Private authentication precedence failed')
            if client.get('/api/v1/grades/', headers={'Host': 'foreign.invalid'}).status_code != 400:
                raise RuntimeError('Trusted host gate failed')
        return 7
    finally:
        # Public application owns its engine; close it after this diagnostic.
        engine = getattr(app.state, 'database_engine', None)
        if engine is not None:
            engine.dispose()


def run(check):
    if importlib.util.find_spec('django') is not None or importlib.util.find_spec('rest_framework') is not None:
        raise RuntimeError('Target interpreter must exclude Django/DRF')
    engine = create_engine(DatabaseConfig.from_environment())
    try:
        with UnitOfWork(engine) as uow:
            s = uow.session
            s.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
            major = int(s.scalar(sa.text('SHOW server_version_num'))) // 10000
            if major < 16:
                raise RuntimeError('PostgreSQL16 required')
            if check == 'system':
                count = system_check()
            elif check == 'migrations':
                inventory = assert_baseline(s.connection(), 'B', allow_protocol=True, require_history=False)
                from backend.migrations.upgrade import HEAD
                if list(s.scalars(sa.text('SELECT version_num FROM alembic_version'))) != [HEAD]:
                    raise RuntimeError('Unknown Alembic head')
                count = sum(len(inventory[name]) for name in ('columns', 'constraints', 'indexes', 'sequences')) + 1
            elif check == 'lesson-sources':
                count = verify_lesson_sources(s, ROOT, all_lessons=True)['verified']
                if count != 263:
                    raise RuntimeError('Full frozen lesson inventory required')
            elif check == 'site-integrity':
                roots = json.loads(os.environ['MATHSTART_STATIC_ROOTS'])
                if not isinstance(roots, list) or not roots or any(not isinstance(path, str) or not Path(path).is_dir() for path in roots):
                    raise RuntimeError('Explicit real static roots required')
                media = Path(os.environ['MATHSTART_MEDIA_ROOT'])
                if not media.is_dir():
                    raise RuntimeError('Explicit media root required')
                report, errors = inspect_site(s, static_roots=roots, media_root=media)
                if errors or report['summary']['pages_total'] != 279 or report['summary']['topics_total'] != 263:
                    raise RuntimeError('Full content/asset integrity failed')
                count = report['summary']['pages_total'] + report['summary']['checked_references']
            else:
                release = active_quality_release(uow, os.environ.get('MATHSTART_RELEASE_ROOT'))
                report, errors = inspect_public_quality(s, os.environ['MATHSTART_PUBLIC_ORIGIN'], release=release)
                if errors or report['pages_checked'] != 279:
                    raise RuntimeError('Full public HTTP quality failed')
                count = report['pages_checked']
        if any(name == 'django' or name.startswith('django.') for name in sys.modules):
            raise RuntimeError('Django imported in normal target check')
        return {'check_id': check, 'status': 'PASS', 'evidence_class': 'TARGET_RUNTIME',
                'assertions': count, 'skipped': 0, 'database_vendor': 'postgresql', 'postgresql_major': major}
    finally:
        engine.dispose()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=CHECKS)
    args = parser.parse_args(argv)
    path = None
    try:
        if os.environ.get('MATHSTART_CHECK_ID') != args.check:
            raise RuntimeError('Check identity mismatch')
        path = Path(os.environ['MATHSTART_CHECK_RESULT'])
        result = run(args.check)
    except Exception as error:
        result = {'check_id': args.check, 'status': 'FAIL', 'evidence_class': 'TARGET_RUNTIME',
                  'assertions': 0, 'skipped': 0, 'failure_class': type(error).__name__}
    if path is not None:
        with path.open('x', encoding='utf-8', newline='\n') as output:
            output.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
