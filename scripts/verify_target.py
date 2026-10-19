"""Own the disposable DB, build and HTTP lifecycle for the full target registry.

This runs the existing registry commands; it does not substitute cached results.
Group selections are development evidence only. The default also runs all four
install/upgrade rehearsals. Credentials and cookies remain under ignored var/.
"""
from contextlib import ExitStack
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import importlib.util
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.public_block_process import owned_http_service, start_owned_process, _stop
from scripts.verify_public_block import source_snapshot, assert_source_unchanged, legacy_executable
from scripts.verify_repo import Check, GROUPS
from scripts.target_verification import target_checks


def selection(groups):
    """Retain every registry entry exactly once, moving only the build earlier."""
    checks = [Check(*row) for row in target_checks()]
    if groups:
        checks = [check for check in checks if check.group in groups]
    # Runtime consumers always need a real build, even in a selected group run.
    build = next(Check(*row) for row in target_checks() if row[1][-1] == 'frontend-build')
    return [build, *[check for check in checks if check != build]]


def deadline(check):
    # Nine actual browser projects have an explicitly bounded, longer lifecycle.
    return 7500 if check.command[-1] == 'frontend-e2e' else 1860 if check.command[-1] == 'backend-tests' else 600


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-root', type=Path, required=True)
    parser.add_argument('--legacy-python', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8131)
    parser.add_argument('--legacy-port', type=int, default=8132)
    parser.add_argument('--group', action='append', choices=GROUPS)
    parser.add_argument('--allow-dirty', action='store_true')
    args = parser.parse_args(argv)
    root = args.runtime_root.resolve()
    if not root.is_relative_to(ROOT / 'var') or root.exists():
        parser.error('A new owned directory under checkout var/ is required')
    if args.port == args.legacy_port or any(not 1024 <= p <= 65535 for p in (args.port, args.legacy_port)):
        parser.error('Distinct unprivileged loopback ports required')
    if (not args.legacy_python.is_file() or os.environ.get('MATHSTART_DISPOSABLE') != '1'
            or importlib.util.find_spec('django') or importlib.util.find_spec('rest_framework')):
        parser.error('Disposable no-Django target and separate installed legacy interpreter required')
    from backend.infrastructure.database import DatabaseConfig
    from backend.verification_suite import owned_database
    import sqlalchemy as sa
    url = DatabaseConfig.from_environment().url
    if url.host != '127.0.0.1' or url.port != 55441:
        parser.error('Dedicated loopback PostgreSQL endpoint 55441 required')
    source = source_snapshot(ROOT)
    if source['dirty_paths'] and not args.allow_dirty:
        root.mkdir(parents=True)
        (root / 'result.json').write_text(json.dumps({
            'version': 'managed-target-v1', 'status': 'FAIL', 'failure_class': 'DirtySource',
            'source_before': source, 'cleanup': 'NOT_STARTED', 'formal_acceptance': 'HUMAN_PENDING'
        }, indent=2) + '\n', encoding='utf-8', newline='\n')
        print('Dirty source paths: ' + ', '.join(source['dirty_paths'][:10]), file=sys.stderr)
        parser.error('Commit the candidate or explicitly use development --allow-dirty')
    checks = selection(set(args.group or []))
    root.mkdir(parents=True)
    report = {'version': 'managed-target-v1', 'status': 'IN_PROGRESS', 'source_before': source,
              'started_at': datetime.now(timezone.utc).isoformat(), 'groups': args.group,
              'formal_acceptance': 'HUMAN_PENDING', 'stages': [], 'cleanup': 'NOT_RUN'}
    env = dict(os.environ, MATHSTART_HTTP_SIGNING_KEY=secrets.token_urlsafe(48),
               MATHSTART_PUBLIC_ORIGIN=f'http://127.0.0.1:{args.port}', MATHSTART_PYTHON=sys.executable,
               MATHSTART_LEGACY_PYTHON=legacy_executable(args.legacy_python), PYTHONUNBUFFERED='1',
               MATHSTART_E2E_BASE_URL=f'http://127.0.0.1:{args.port}',
               MATHSTART_LEGACY_BASE_URL=f'http://127.0.0.1:{args.legacy_port}')
    # Parent check identity may never leak into nested real check receipts.
    env.pop('MATHSTART_CHECK_ID', None)
    env.pop('MATHSTART_CHECK_RESULT', None)

    def stage(identity, command, timeout=600):
        assert_source_unchanged(source, ROOT)
        entry = {'id': identity, 'argv': list(command), 'cwd': '.', 'exit_code': None}
        report['stages'].append(entry)
        logfile = root / (f'{len(report["stages"]):02d}.log')
        entry['log'] = logfile.name
        started = time.monotonic()
        with logfile.open('wb') as output:
            child = start_owned_process(list(command), cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                        stdout=output, stderr=subprocess.STDOUT)
            try:
                entry['exit_code'] = child.wait(timeout=timeout)
            finally:
                _stop(child)
                entry['elapsed_seconds'] = round(time.monotonic() - started, 3)
                entry['log_sha256'] = sha256(logfile.read_bytes()).hexdigest()
        if entry['exit_code'] != 0:
            raise RuntimeError('Required target command failed')
        assert_source_unchanged(source, ROOT)
        print('PASS: ' + identity, flush=True)

    admin = sa.create_engine(url.set(database='postgres'), isolation_level='AUTOCOMMIT', hide_parameters=True,
                             connect_args={'connect_timeout': 5, 'options': '-c statement_timeout=30000'})
    try:
        # The supplied parent database is never mutated or adopted as our runtime.
        with owned_database(admin, url, 'combined') as engine:
            env['MATHSTART_DATABASE_URL'] = engine.url.render_as_string(hide_password=False)
            env['MATHSTART_V04_DATABASE_URL'] = env['MATHSTART_DATABASE_URL']
            runtime, release = root / 'runtime', 'target-' + uuid.uuid4().hex
            stage('prepare-synthetic-inputs', [sys.executable, '-m', 'backend.content.synthetic_setup', 'prepare',
                  '--disposable', '--runtime-root', str(runtime), '--release-id', release, '--source-sha', source['head']])
            prepared = json.loads((runtime / 'prepare-result.json').read_text(encoding='utf-8'))
            config = {key: prepared[key] for key in ('input_root', 'release_id', 'manifest_digest', 'receipt_digest')}
            config.update(output=str(root / 'artifact'), origin=env['MATHSTART_PUBLIC_ORIGIN'])
            config_path = root / 'build-config.json'
            config_path.write_text(json.dumps(config), encoding='utf-8')
            env.update(MATHSTART_BUILD_CONFIG=str(config_path),
                       MATHSTART_STAFF_COOKIE_FILE=str(runtime / 'private-staff-cookie.json'))
            stage(checks[0].name, checks[0].command, deadline(checks[0]))
            artifact_digest = sha256((root / 'artifact/output-manifest.json').read_bytes()).hexdigest()
            stage('activate-synthetic-fixture', [sys.executable, '-m', 'backend.content.synthetic_setup', 'activate-initial',
                  '--disposable', '--runtime-root', str(runtime), '--release-id', release,
                  '--receipt-digest', prepared['receipt_digest'], '--artifact-root', str(root / 'artifact'),
                  '--artifact-digest', artifact_digest])
            env.update(MATHSTART_RELEASE_ROOT=str(runtime / 'releases'),
                       MATHSTART_PUBLIC_ARTIFACT_ROOT=str(root / 'artifact'),
                       MATHSTART_PUBLIC_ARTIFACT_DIGESTS=json.dumps({release: artifact_digest}),
                       MATHSTART_STATIC_ROOTS=json.dumps([str(ROOT / 'static')]),
                       MATHSTART_MEDIA_ROOT=str(ROOT / 'site_content/media'),
                       MATHSTART_PUBLIC_VIEW=str(ROOT / 'frontend/.cache' / ('public-view-' + release + '.json')))
            with ExitStack() as services:
                services.enter_context(owned_http_service([sys.executable, '-m', 'uvicorn',
                    'backend.content.public_runtime:application', '--factory', '--host', '127.0.0.1',
                    '--port', str(args.port), '--no-access-log', '--no-proxy-headers'],
                    base_url=env['MATHSTART_PUBLIC_ORIGIN'], cwd=ROOT, evidence_root=root / 'target-service', environment=env))
                if any(check.command[-1] == 'frontend-e2e' for check in checks):
                    services.enter_context(owned_http_service([sys.executable, '-m', 'frontend.legacy_comparator',
                        '--build-config', str(config_path), '--legacy-python', legacy_executable(args.legacy_python),
                        '--runtime-root', str(root / 'legacy'), '--port', str(args.legacy_port)],
                        base_url=env['MATHSTART_LEGACY_BASE_URL'], cwd=ROOT,
                        evidence_root=root / 'legacy-service', environment=env))
                for check in checks[1:]:
                    stage(check.name, check.command, deadline(check))
                if not args.group:
                    for identity in ('fresh-install', 'upgrade-A', 'upgrade-B', 'upgrade-C'):
                        stage(identity, [sys.executable, 'scripts/target_check.py', identity, '--disposable'])
            report.update(release_id=release, input_manifest_digest=prepared['manifest_digest'],
                          input_receipt_digest=prepared['receipt_digest'], output_manifest_digest=artifact_digest)
        report['cleanup'] = 'PASS'
        report['source_after'] = assert_source_unchanged(source, ROOT)
        report['status'] = 'PASS_SCOPED_DEVELOPMENT' if args.group or source['dirty_paths'] else 'PASS'
        return 0
    except Exception as error:
        report.update(status='FAIL', failure_class=type(error).__name__)
        print('FAIL: managed target; inspect stage logs.', file=sys.stderr)
        return 1
    finally:
        admin.dispose()
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        (root / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    raise SystemExit(main())
