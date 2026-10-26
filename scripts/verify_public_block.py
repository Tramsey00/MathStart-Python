"""Reproduce the I02/I03 synthetic PostgreSQL, SSG and browser block.

Dependencies and browser binaries must be installed from the documented locks.
The operator supplies a new empty disposable PostgreSQL database. This command
uses only marked disposable data. The publisher rehearsal creates/drops its own
uniquely named child database and builds synthetic React editions. It does not
deploy or establish final migration/publication acceptance.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.public_block_process import owned_http_service, run_browser_check, start_owned_process, _stop


def legacy_executable(path):
    # A POSIX virtualenv executable is a symlink to the base interpreter.
    # Preserve its invocation path so Python discovers that venv's pyvenv.cfg.
    return str(Path(path).absolute())


def npm_command(script):
    if script not in {'typecheck', 'test', 'test:full', 'build', 'test:e2e', 'test:i02', 'test:identity', '--version'}:
        raise ValueError('Unknown frontend check')
    npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')
    if not npm:
        raise ValueError('npm is unavailable')
    if os.name == 'nt':
        # Invoke the installed CLI directly: list2cmdline escaping is not cmd /c
        # escaping, especially when npm.cmd lives under Program Files.
        node = shutil.which('node')
        cli = Path(npm).parent / 'node_modules/npm/bin/npm-cli.js'
        if not node or not cli.is_file():
            raise ValueError('Installed Node/npm CLI is unavailable')
        return [node, str(cli), *(['--version'] if script == '--version' else ['run', script])]
    return [npm, '--version'] if script == '--version' else [npm, 'run', script]


def source_snapshot(repository):
    def git(*arguments):
        return subprocess.check_output(['git',*arguments],cwd=repository)
    untracked = {}
    for relative in git('ls-files','--others','--exclude-standard','-z').decode('utf-8').split('\0'):
        if not relative:
            continue
        path = repository / relative
        raw = os.readlink(path).encode('utf-8') if path.is_symlink() else path.read_bytes()
        untracked[relative] = sha256(raw).hexdigest()
    return {'head':git('rev-parse','HEAD').decode().strip(),
            'tree':git('log','-1','--format=%T').decode().strip(),
            'dirty_paths':git('status','--porcelain','--untracked-files=normal').decode('utf-8').splitlines(),
            'tracked_diff_sha256':sha256(git('diff','HEAD','--binary','--no-ext-diff')).hexdigest(),
            'untracked_sha256':untracked}


def assert_source_unchanged(expected, repository):
    actual = source_snapshot(repository)
    if actual != expected:
        raise RuntimeError('Candidate source changed during public block verification')
    return actual


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-root', type=Path, required=True)
    parser.add_argument('--legacy-python', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8111)
    parser.add_argument('--legacy-port', type=int, default=8112)
    parser.add_argument('--scope', choices=['i02', 'identity', 'combined'], default='combined')
    parser.add_argument('--allow-dirty', action='store_true', help='Development only; receipt remains DIRTY_SOURCE')
    args = parser.parse_args(argv)
    root = args.runtime_root.resolve()
    if not root.is_relative_to(ROOT / 'var') or root.exists():
        parser.error('A new owned directory under this checkout var/ is required')
    if args.port == args.legacy_port or any(not 1024 <= p <= 65535 for p in (args.port, args.legacy_port)):
        parser.error('Distinct unprivileged loopback ports are required')
    if not args.legacy_python.is_file():
        parser.error('A separate installed legacy interpreter is required')
    if os.environ.get('MATHSTART_DISPOSABLE') != '1' or not os.environ.get('MATHSTART_DATABASE_URL'):
        parser.error('Explicit disposable PostgreSQL configuration required')
    if importlib.util.find_spec('django') or importlib.util.find_spec('rest_framework'):
        parser.error('The target interpreter must not have Django or DRF installed')
    source_before = source_snapshot(ROOT)
    dirty = source_before['dirty_paths']
    if dirty and not args.allow_dirty:
        parser.error('Commit the reviewable source first; dirty development runs need --allow-dirty')
    root.mkdir(parents=True)
    report = {'version':'i02-i03-public-block-run-v1', 'status':'IN_PROGRESS',
              'started_at':datetime.now(timezone.utc).isoformat(),
              'implementation_sha':source_before['head'], 'tree_sha':source_before['tree'],
              'source_before':source_before,
              'dirty_paths':dirty, 'scope':args.scope,
              'scope_description':'I02 public/staff-read checks; final cross-browser/visual matrix remains I05' if args.scope == 'i02' else 'I02 + identity narrow Chrome checks; final matrix pending' if args.scope == 'identity' else 'I02/I03 combined matrix',
              'full_V03_V04_R03':'NOT_VERIFIED', 'formal_acceptance':'HUMAN_PENDING', 'stages':[]}
    env = os.environ.copy()
    # Keys are private in-memory fixtures. Never echo the environment or cookies.
    env['MATHSTART_HTTP_SIGNING_KEY'] = secrets.token_urlsafe(48)
    env['MATHSTART_PUBLIC_ORIGIN'] = f'http://127.0.0.1:{args.port}'
    env['MATHSTART_PYTHON'] = sys.executable
    env['MATHSTART_LEGACY_PYTHON'] = legacy_executable(args.legacy_python)
    env['PYTHONUNBUFFERED'] = '1'
    env['MATHSTART_V04_DATABASE_URL'] = env['MATHSTART_DATABASE_URL']
    release_id = 'public-' + uuid4().hex
    setup_root = root / 'runtime'
    frontend = ROOT / 'frontend'

    def stage(name, command, cwd=ROOT, timeout=540):
        assert_source_unchanged(source_before,ROOT)
        logfile = root / (name + '.log')
        started = time.monotonic()
        entry = {'id':name,'argv':command,'cwd':str(cwd.relative_to(ROOT)) or '.',
                 'log':logfile.name, 'exit_code':None}
        report['stages'].append(entry)
        with logfile.open('wb') as log:
            child = start_owned_process(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                        stdout=log, stderr=subprocess.STDOUT)
            try:
                entry['exit_code'] = child.wait(timeout=timeout)
            finally:
                _stop(child)
                entry['elapsed_seconds'] = round(time.monotonic() - started, 3)
        if entry['exit_code']:
            raise RuntimeError('Required stage failed: ' + name)
        assert_source_unchanged(source_before,ROOT)
        print('PASS: ' + name, flush=True)

    try:
        stage('legacy-interpreter-regression', [sys.executable,'-m','unittest','discover',
            '-s','tests','-p','test_legacy_interpreter.py','-v'])
        stage('target-lock', [sys.executable,'-m','pip','check'])
        stage('python-version', [sys.executable,'--version'])
        stage('node-version', [shutil.which('node') or 'node','--version'])
        stage('npm-version', npm_command('--version'))
        stage('postgres-version', [sys.executable,'-c',
            "from backend.infrastructure.database import DatabaseConfig,create_engine; "
            "from sqlalchemy import text; e=create_engine(DatabaseConfig.from_environment()); "
            "c=e.connect(); print(c.scalar(text('SHOW server_version'))); c.close(); e.dispose()"])
        stage('synthetic-prepare', [sys.executable,'-m','backend.content.synthetic_setup','prepare','--disposable',
            '--runtime-root',str(setup_root),'--release-id',release_id,'--source-sha',report['implementation_sha']])
        prepared = json.loads((setup_root / 'prepare-result.json').read_text(encoding='utf-8'))
        config = {key:prepared[key] for key in ('input_root','release_id','manifest_digest','receipt_digest')}
        config.update(output=str(root / 'artifact'), origin=env['MATHSTART_PUBLIC_ORIGIN'])
        config_path = root / 'build-config.json'
        config_path.write_text(json.dumps(config),encoding='utf-8')
        env['MATHSTART_BUILD_CONFIG'] = str(config_path)
        env['MATHSTART_STAFF_COOKIE_FILE'] = str(setup_root / 'private-staff-cookie.json')
        stage('frontend-typecheck', npm_command('typecheck'), frontend)
        stage('frontend-unit', npm_command('test:full'), frontend)
        stage('frontend-build', npm_command('build'), frontend)
        artifact_digest = sha256((root / 'artifact/output-manifest.json').read_bytes()).hexdigest()
        stage('initial-synthetic-activation', [sys.executable,'-m','backend.content.synthetic_setup','activate-initial',
            '--disposable','--runtime-root',str(setup_root),'--release-id',release_id,
            '--receipt-digest',prepared['receipt_digest'],'--artifact-root',str(root / 'artifact'),
            '--artifact-digest',artifact_digest])
        env['MATHSTART_RELEASE_ROOT'] = str(setup_root / 'releases')
        env['MATHSTART_PUBLIC_ARTIFACT_ROOT'] = str(root / 'artifact')
        env['MATHSTART_PUBLIC_ARTIFACT_DIGESTS'] = json.dumps({release_id:artifact_digest})
        env['MATHSTART_STATIC_ROOTS'] = json.dumps([str(ROOT / 'static')])
        env['MATHSTART_MEDIA_ROOT'] = str(ROOT / 'site_content/media')
        for check in ('system', 'migrations', 'lesson-sources', 'site-integrity'):
            stage('target-' + check, [sys.executable, 'scripts/target_check.py', check])
        env['MATHSTART_PUBLIC_VIEW'] = str(frontend / '.cache' / ('public-view-' + release_id + '.json'))
        env['MATHSTART_LEGACY_BASE_URL'] = f'http://127.0.0.1:{args.legacy_port}'
        stage('source-render-and-read-runtime', [sys.executable,'-m','unittest',
            'backend.tests.v04.test_build','backend.tests.v04.test_read_runtime',
            'backend.tests.v04.test_content_checks',
            'backend.tests.v04.test_publication',
            'backend.tests.v04.test_editions',
            'backend.tests.v04.test_preparation',
            'backend.tests.v04.test_artifacts',
            'backend.tests.v04.test_verified_release_cache',
            'frontend.tests.test_public_artifact','frontend.tests.test_legacy_comparator','-v'])
        stage('prepared-publication-recovery', [sys.executable,'scripts/run_unittest.py',
            '--start','backend/tests/v04','--pattern','test_participant.py'])
        legacy_argv = [sys.executable,'-m','frontend.legacy_comparator','--build-config',str(config_path),
            '--legacy-python',legacy_executable(args.legacy_python),'--runtime-root',str(root / 'legacy'),
            '--port',str(args.legacy_port)]
        target_argv = [sys.executable,'-m','uvicorn','backend.content.public_runtime:application',
            '--factory','--host','127.0.0.1','--port',str(args.port),'--no-access-log','--no-proxy-headers']
        with owned_http_service(target_argv, base_url=env['MATHSTART_PUBLIC_ORIGIN'],
                                cwd=ROOT,evidence_root=root / 'quality-service',environment=env):
            stage('target-content-quality', [sys.executable, 'scripts/target_check.py', 'content-quality'])
        # Target and comparator have separately owned process trees and logs.
        with owned_http_service(legacy_argv,base_url=env['MATHSTART_LEGACY_BASE_URL'],
                                cwd=ROOT,evidence_root=root / 'legacy-service',environment=env):
            browser_env = dict(env)
            browser_env['MATHSTART_CHECK_ID'] = {'i02':'frontend-i02','identity':'frontend-identity','combined':'frontend-e2e'}[args.scope]
            browser_env['MATHSTART_CHECK_RESULT'] = str(root / 'browser-receipt.json')
            # npm requires frontend cwd; the server module needs repository cwd.
            browser_command = [sys.executable,str(ROOT / 'scripts/public_frontend_command.py'),
                               {'i02':'test:i02','identity':'test:identity','combined':'test:e2e'}[args.scope]]
            browser = run_browser_check(target_argv,browser_command,base_url=env['MATHSTART_PUBLIC_ORIGIN'],
                cwd=ROOT,evidence_root=root / 'target-service',environment=browser_env,check_timeout=7200)
        report['browser_lifecycle'] = browser
        if browser != {'startup':'PASS','browser_exit':0,'cleanup':'PASS'}:
            raise RuntimeError('Browser check or service lifecycle failed')
        receipt = json.loads((root / 'browser-receipt.json').read_text(encoding='utf-8'))
        if receipt.get('status') != 'PASS' or receipt.get('skipped') != 0 or receipt.get('assertions',0) < 1:
            raise RuntimeError('Missing nonempty unskipped browser proof')
        report['source_after'] = assert_source_unchanged(source_before,ROOT)
        report.update(status='PASS' if not dirty else 'PASS_DIRTY_SOURCE_ONLY', release_id=release_id,
            input_manifest_digest=prepared['manifest_digest'],input_receipt_digest=prepared['receipt_digest'],
            output_manifest_digest=artifact_digest,browser_receipt='browser-receipt.json')
        return 0
    except Exception as error:
        report.update(status='FAIL', failure_class=type(error).__name__)
        print('FAIL: public block verification; inspect the named stage logs.',file=sys.stderr)
        return 1
    finally:
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        (root / 'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    raise SystemExit(main())
