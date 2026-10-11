"""R03-owned, pinned PR51 target CI; separate lock, venv and PostgreSQL service."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.frontend_ci import check_identity, git, now
OUTPUT = ROOT / 'var/postgres-ci'
CONFIG = ROOT / 'specs/migration/r03-v1/postgres-ci-pr51.json'
OBSERVER = ROOT / 'scripts/v01_ci_observer.py'


def save(name, value):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / name).open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')


def snapshot(candidate, config):
    if Path(git(candidate, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != candidate:
        raise ValueError('Candidate must be its own checkout')
    head = git(candidate, 'rev-parse', 'HEAD').decode().strip()
    if head != config['pr_head_sha'] or git(candidate, 'status', '--porcelain=v1', '--untracked-files=all'):
        raise ValueError('Candidate is stale or dirty')
    if git(candidate, 'diff', config['implementation_sha'], head, '--', 'backend'):
        raise ValueError('Backend changed since reviewed implementation')
    workflows = {}
    for name in ('.github/workflows/ci.yml', '.github/workflows/migration-ci.yml'):
        before = git(candidate, 'show', config['pr_base_sha'] + ':' + name)
        current = git(candidate, 'show', 'HEAD:' + name)
        if before != current:
            raise ValueError('Frozen baseline workflow changed')
        workflows[name] = hashlib.sha256(current).hexdigest()
    paths = git(candidate, 'ls-files', '-z', 'backend', 'docs/acceptance/MS7-MIG-V01').decode().split('\0')
    hashes = {p: hashlib.sha256((candidate / p).read_bytes()).hexdigest() for p in sorted(paths) if p}
    for p, expected in config['input_sha256'].items():
        if hashes[p] != expected:
            raise ValueError('Pinned lock/handoff/gate/case inventory changed: ' + p)
    return {'checkout_sha': head, 'checkout_tree': git(candidate, 'rev-parse', 'HEAD^{tree}').decode().strip(),
            'dirty': False, 'frozen_workflows': workflows, 'source_and_historical_sha256': hashes}


def inspect_service():
    identity = os.environ.get('R03_POSTGRES_SERVICE_ID', '')
    if not re.fullmatch(r'[0-9a-f]{64}', identity):
        raise ValueError('Exact job.services.postgres.id required; no container discovery/fallback')
    inspected = json.loads(subprocess.check_output(['docker', 'inspect', identity], timeout=30))[0]
    record = {'id': inspected['Id'], 'configured_image': inspected['Config']['Image'],
              'image_id': inspected['Image'], 'labels': inspected['Config']['Labels'],
              'state': inspected['State'], 'ports': inspected['HostConfig']['PortBindings'],
              'tmpfs': inspected['HostConfig'].get('Tmpfs', {}),
              'mounts': [{k: m[k] for k in ('Type', 'Name', 'Destination') if k in m} for m in inspected['Mounts']],
              'ownership': 'GitHub Actions job service; exact ID supplied by workflow context',
              'run_id': os.environ.get('GITHUB_RUN_ID'), 'captured_at': now()}
    validate_service(record, identity)
    return record


def validate_service(record, identity):
    ports = record['ports'].get('5432/tcp', [])
    if (record['id'] != identity or record['configured_image'] != 'postgres:16-bookworm'
            or len(ports) != 1 or ports[0]['HostPort'] != '55441'
            or record['tmpfs'] != {'/var/lib/postgresql/data': 'rw'}
            or any(mount['Type'] != 'tmpfs' for mount in record['mounts'])):
        raise ValueError('Container identity/image/port/tmpfs differs from owned disposable job service')


def intake(candidate, config):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{config['repository']}/pulls/{config['pr_number']}",
        headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'MathStart-R03-CI'})
    if os.environ.get('GITHUB_TOKEN'):
        request.add_header('Authorization', 'Bearer ' + os.environ['GITHUB_TOKEN'])
    with urllib.request.urlopen(request, timeout=30) as response:
        pr = json.load(response)
    before = snapshot(candidate, config)
    check_identity(config, pr, before['checkout_sha'])
    service = inspect_service()
    if not service['state']['Running'] or service['state'].get('Health', {}).get('Status') != 'healthy':
        raise ValueError('Owned PostgreSQL service is not healthy')
    save('service-before.json', service)
    record = {'format': 'r03-v01-target-ci-v1', 'captured_at': now(),
              'pr_number': pr['number'], 'pr_head_sha': pr['head']['sha'], 'pr_base_sha': pr['base']['sha'],
              'pr_merge_ref_sha_observed': pr['merge_commit_sha'], 'candidate_checkout': before,
              'workflow_checkout_sha': git(ROOT, 'rev-parse', 'HEAD').decode().strip(),
              'event_sha': os.environ.get('GITHUB_SHA'), 'event': os.environ.get('GITHUB_EVENT_NAME'),
              'ref': os.environ.get('GITHUB_REF'), 'run_id': os.environ.get('GITHUB_RUN_ID'),
              'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'), 'implementation_sha': config['implementation_sha'],
              'run_url': f"https://github.com/{config['repository']}/actions/runs/{os.environ.get('GITHUB_RUN_ID')}",
              'independent_task_approval': 'NOT_DECLARED'}
    save('candidate-provenance.json', record)
    print('PINNED_PR51_HEAD=' + record['pr_head_sha'])
    print('ACTUAL_CANDIDATE_CHECKOUT=' + before['checkout_sha'])
    print('ACTUAL_WORKFLOW_CHECKOUT=' + record['workflow_checkout_sha'])


def validate_observations(observed, manifest):
    expected = {case['id']: case['environment'] for case in manifest['cases']}
    cases = observed['tests']
    ids = [case['id'] for case in cases]
    if (len(expected) != 34 or len(ids) != 34 or len(set(ids)) != 34 or set(ids) != set(expected)
            or sum(v == 'PostgreSQL' for v in expected.values()) != 23
            or any(case['status'] != 'PASS' or any(s['status'] != 'PASS' for s in case['subtests']) for case in cases)):
        raise ValueError('34 exact successful cases / 23 PostgreSQL cases, no skips or partial results required')
    databases = observed['databases']
    names = [db['database'] for db in databases]
    if (not databases or len(set(names)) != len(names)
            or any(not db['fixture_cleanup_completed'] or not re.fullmatch(r'test_ms7_mig_v01_[0-9a-f]{32}', db['database'] or '') for db in databases)):
        raise ValueError('Every observed fixture must own a distinct marked database and complete cleanup')
    fresh = [db for db in databases if db['test_id'].endswith('.test_fresh_twice_separate_databases_no_django')]
    upgrades = [db for db in databases if db['test_id'].endswith('.test_upgrade_profiles_preserve_data_defaults_epoch_sequences')]
    if len(fresh) != 2 or any(db['profile'] is not None for db in fresh) or [db['profile'] for db in upgrades] != ['A', 'B', 'C']:
        raise ValueError('Actual fresh x2 and upgrade A/B/C fixture events required')
    return {'target_tests_passed': 34, 'postgres_tests_passed': 23, 'unit_tests_passed': 11,
            'skips': 0, 'fresh_install_databases': [db['database'] for db in fresh],
            'upgrade_profiles': [db['profile'] for db in upgrades], 'disposable_databases_cleaned': len(databases)}


def validate_lock(text, installed):
    normalized = lambda name: re.sub(r'[-_.]+', '-', name).lower()
    expected = {}
    for line in text.splitlines():
        if line.strip() and not line.startswith('#'):
            name, version = line.split('==')
            expected[normalized(name)] = version
    actual = {normalized(k): v for k, v in installed.items() if normalized(k) != 'pip'}
    if len(expected) != 22 or expected != actual:
        raise ValueError('Actual target environment differs from the complete 22-package test lock')


def run(candidate, config):
    provenance = json.loads((OUTPUT / 'candidate-provenance.json').read_text())
    before = snapshot(candidate, config)
    if before != provenance['candidate_checkout']:
        raise ValueError('Candidate changed after intake')
    environment = {k: v for k, v in os.environ.items() if k not in ('GITHUB_TOKEN', 'GH_TOKEN', 'PYTHONPATH', 'VIRTUAL_ENV')}
    environment.update(MATHSTART_V01_EXPECTED_HEAD=config['pr_head_sha'],
                       MATHSTART_V01_DISPOSABLE_ACK='OWNED_DISPOSABLE_POSTGRES_16',
                       MATHSTART_V01_TEST_ADMIN_URL='postgresql+psycopg://mathstart_v01_ci:disposable-v01-ci-only@127.0.0.1:55441/postgres',
                       MATHSTART_V01_EVIDENCE_DIR=str(OUTPUT / 'owner-diagnostics'), R03_V01_OUTPUT=str(OUTPUT))
    venv = candidate / 'var/v01-target-ci'
    if venv.exists() or (OUTPUT / 'owner-diagnostics').exists():
        raise ValueError('Locked environment and evidence must be fresh')
    python = venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    result = {'started_at': now(), 'exit_code': 1, 'commands': [], 'venv': str(venv),
              'lock': 'backend/requirements-test.lock', 'independent_task_approval': 'NOT_DECLARED'}
    commands = [('create-target-venv', [sys.executable, '-m', 'venv', str(venv)], 120),
                ('locked-install', [str(python), '-m', 'pip', 'install', '--no-deps', '-r', 'backend/requirements-test.lock'], 600),
                ('pip-check', [str(python), '-m', 'pip', 'check'], 60),
                ('pip-freeze', [str(python), '-m', 'pip', 'freeze', '--all'], 60),
                ('postgres-before', [str(python), str(OBSERVER), 'postgres-before'], 60),
                ('target-suite', [str(python), str(OBSERVER), 'tests'], 1200),
                ('postgres-after', [str(python), str(OBSERVER), 'postgres-after'], 60)]
    try:
        for name, argv, deadline in commands:
            entry = {'name': name, 'command': argv, 'started_at': now(), 'exit_code': None}
            result['commands'].append(entry)
            try:
                with (OUTPUT / (name + '.log')).open('x', encoding='utf-8') as log:
                    process = subprocess.run(argv, cwd=candidate, env=environment, stdout=log,
                                             stderr=subprocess.STDOUT, timeout=deadline)
                entry['exit_code'] = process.returncode
                if process.returncode:
                    raise ValueError('Required command failed: ' + name)
            except subprocess.TimeoutExpired:
                entry['exit_code'] = 124
                raise
            finally:
                entry['finished_at'] = now()
            print(name + ': ' + str(entry['exit_code']), flush=True)
        manifest = json.loads((candidate / 'docs/acceptance/MS7-MIG-V01/target-ci-cases-v5.json').read_text())
        observed = json.loads((OUTPUT / 'test-observations.json').read_text())
        result.update(validate_observations(observed, manifest))
        installed = json.loads((OUTPUT / 'postgres-before.json').read_text())['installed']
        validate_lock((candidate / 'backend/requirements-test.lock').read_text(), installed)
        result['locked_packages_verified'] = 22
        raw = (OUTPUT / 'target-suite.log').read_text()
        summary = f"V01_TARGET: HEAD={config['pr_head_sha']} implementation={config['implementation_sha']} tests=34 PG_collected=23 skips=0 failures=0 errors=0 status=PASS"
        if summary not in raw:
            raise ValueError('Unchanged owner gate did not report complete PASS')
        after = snapshot(candidate, config)
        if before != after:
            raise ValueError('Candidate source or historical evidence changed')
        result.update(exit_code=0, candidate_after=after)
    finally:
        result['finished_at'] = now()
        save('execution.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('candidate_after', 'commands')}, indent=2))


def cleanup():
    # This exact service belongs to this job, not to local/shared infrastructure.
    service = inspect_service()
    record = {'before': service, 'container_stop_exit_code': None, 'after': None,
              'removal_owner': 'GitHub Actions automatic post-job Stop containers (docker rm --force); data is tmpfs'}
    try:
        with (OUTPUT / 'postgres-service.log').open('x', encoding='utf-8') as log:
            subprocess.run(['docker', 'logs', '--timestamps', service['id']], stdout=log,
                           stderr=subprocess.STDOUT, timeout=60, check=True)
    finally:
        # Stop even when diagnostic capture fails. Data is tmpfs, with no Docker volume.
        try:
            process = subprocess.run(['docker', 'stop', '--time', '10', service['id']], timeout=40, check=True)
            record['container_stop_exit_code'] = process.returncode
            record['after'] = inspect_service()
            if record['after']['state']['Running']:
                raise ValueError('Owned service still running')
        finally:
            save('service-cleanup.json', record)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('intake', 'run', 'cleanup'))
    parser.add_argument('--candidate')
    args = parser.parse_args(argv)
    try:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        config = json.loads(CONFIG.read_text())
        if args.action == 'cleanup':
            cleanup()
        else:
            if not args.candidate:
                raise ValueError('Explicit candidate checkout required')
            (intake if args.action == 'intake' else run)(Path(args.candidate).resolve(), config)
        return 0
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        print('FAIL: ' + type(error).__name__ + ': ' + str(error))
        return 1


if __name__ == '__main__':
    # Running as a script still needs the R03 package root, never candidate imports.
    raise SystemExit(main())
