"""Exact-commit V02 task evidence in three isolated locked environments."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import published_v02_ci as publication
from v02_publication_intake import Runner, save, sha, require, ARCHIVE_SHA


def lock_records(candidate, path, seen=None):
    seen = set() if seen is None else seen
    path = path.resolve()
    require(path.is_relative_to(candidate) and path not in seen, 'LOCK_PATH_OR_CYCLE')
    seen.add(path)
    result = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('-r '):
            result.update(lock_records(candidate, path.parent/line[3:], seen))
        else:
            match = re.fullmatch(r'([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+-]+)', line)
            require(match is not None, 'UNLOCKED_REQUIREMENT')
            name, version = match.groups()
            key = re.sub(r'[-_.]+', '-', name.lower())
            require(key not in result or result[key] == version, 'CONFLICTING_LOCK')
            result[key] = version
    return result


def check_service(identity, port, output):
    require(re.fullmatch('[0-9a-f]{64}', identity or '') is not None, 'OWNED_SERVICE_ID')
    raw = subprocess.check_output(['docker', 'inspect', identity], timeout=30)
    d = json.loads(raw)[0]
    require(d['Id'] == identity and d['Config']['Image'] == 'postgres:16-bookworm' and
            d['State']['Running'] and d['State']['Health']['Status'] == 'healthy', 'OWNED_HEALTHY_PG16')
    ports = d['HostConfig']['PortBindings']['5432/tcp']
    require(len(ports) == 1 and ports[0]['HostPort'] == port and
            d['HostConfig']['Tmpfs'] == {'/var/lib/postgresql/data': 'rw'} and
            all(m['Type'] == 'tmpfs' for m in d['Mounts']), 'OWNED_PORT_TMPFS')
    save(output/('service-'+port+'.json'), dict(id=identity, image_id=d['Image'], image='postgres:16-bookworm',
                                             ports=ports, tmpfs=d['HostConfig']['Tmpfs'], state=d['State']))


def main(candidate, output):
    candidate = candidate.resolve()
    require(not output.exists() and not output.is_relative_to(candidate), 'NEW_EXTERNAL_EVIDENCE_DIRECTORY')
    output.mkdir(parents=True)
    runner = Runner(output/'raw')
    runner.env.update(PYTHONDONTWRITEBYTECODE='1', PGPASSWORD='synthetic-local-only',
                      MATHSTART_V02_TEST_ADMIN_URL='postgresql+psycopg://postgres:synthetic-local-only@127.0.0.1:15441/postgres',
                      MATHSTART_V01_TEST_ADMIN_URL='postgresql+psycopg://postgres:synthetic-local-only@127.0.0.1:55441/postgres',
                      MATHSTART_V01_EVIDENCE_DIR=str(output/'v01-owner-evidence'))
    runner.run('python-version', [sys.executable, '--version'], ROOT)
    runner.git(ROOT, '--version')
    data = publication.candidate_input((ROOT/publication.INPUT_PATH).read_bytes())
    publication.confirmation((ROOT/publication.CONFIRMATION_PATH).read_bytes())
    require(runner.git(candidate, 'rev-parse', 'HEAD').decode().strip() == data['implementation_sha'], 'EXACT_CANDIDATE_HEAD')
    tree = runner.git(candidate, 'rev-parse', 'HEAD^{tree}').decode().strip()
    parents = runner.git(candidate, 'show', '-s', '--format=%P', 'HEAD').decode().strip().split()
    publication.validate_commit(dict(sha=data['implementation_sha'], tree={'sha': tree}, parents=[{'sha': p} for p in parents]), data)
    pr = publication.fetch_json('pulls/'+str(data['pr_number']), output, 'pr-before')
    publication.validate_pr(pr, data)
    require(not runner.git(candidate, 'status', '--porcelain'), 'CANDIDATE_NOT_CLEAN')
    check_service(os.environ.get('R03_V02_SERVICE_ID'), '15441', output)
    check_service(os.environ.get('R03_V01_SERVICE_ID'), '55441', output)
    runner.env['R03_TASK_SERVICE_ACK'] = 'VERIFIED_GITHUB_DISPOSABLE_POSTGRES16'
    source = ROOT/'docs/acceptance/MS7-MIG-R03/v02-source-snapshot-20261014.zip'
    require(sha(source.read_bytes()) == ARCHIVE_SHA, 'APPROVED_SOURCE_ARCHIVE')
    with zipfile.ZipFile(source) as z:
        original = {r['path']: r for r in json.loads(z.read('transport/inventory.json'))['files']}
    paths = ['backend/infrastructure/http/requirements.lock', 'backend/tests/v02/requirements.lock',
             'docs/acceptance/MS7-MIG-V02/remediation-f01-f02/test-matrix.json']
    for path in paths:
        require(sha((candidate/path).read_bytes()) == original[path]['sha256'], 'APPROVED_OWNER_INPUT: '+path)
    v01 = json.loads((ROOT/'specs/migration/r03-v1/postgres-ci-pr51.json').read_bytes())['input_sha256']
    for path, digest in v01.items():
        require(sha((candidate/path).read_bytes()) == digest, 'ACCEPTED_V01_INPUT: '+path)
    require(not runner.git(candidate, 'diff', publication.BASE, 'HEAD', '--diff-filter=DMRT', '--', 'backend'), 'V01_EXISTING_BACKEND_MUTATION')
    save(output/'source-provenance.json', dict(implementation_sha=data['implementation_sha'], actual_checkout_sha=data['implementation_sha'],
         checkout_tree=tree, parents=parents, pr_head_before=pr['head']['sha'], control_revision=publication.CONTROL,
         anchor_sha256=publication.ANCHOR, workflow_sha=os.environ.get('GITHUB_WORKFLOW_SHA'),
         actual_orchestrator_sha=runner.git(ROOT, 'rev-parse', 'HEAD').decode().strip(),
         baseline_evidence_run=38635496099, baseline_run_does_not_execute_v02=True))
    (candidate/'var').mkdir(exist_ok=True)
    worker = ROOT/'scripts/v02_task_worker.py'
    envs, results = {}, {}

    def phase(name, operation):
        try:
            operation()
            results[name] = {'result': 'PASS'}
        except Exception as error:
            results[name] = {'result': 'FAIL', 'error': str(error)}
        save(output/'phases.json', results)

    def install(name, lock):
        venv = output/('venv-'+name)
        runner.run(name+'-venv', [sys.executable, '-I', '-B', '-m', 'venv', venv], candidate)
        python = venv/'bin/python'
        runner.run(name+'-install', [python, '-I', '-m', 'pip', 'install', '--no-deps', '-r', candidate/lock], candidate, timeout=600)
        runner.run(name+'-pip-check', [python, '-I', '-m', 'pip', 'check'], candidate)
        expected = lock_records(candidate, candidate/lock)
        code = "import importlib.metadata,json,re; print(json.dumps({re.sub(r'[-_.]+','-',d.metadata['Name'].lower()):d.version for d in importlib.metadata.distributions()}))"
        installed = json.loads(runner.run(name+'-installed', [python, '-I', '-B', '-c', code], candidate).stdout)
        require(all(installed.get(k) == v for k, v in expected.items()), 'INSTALLED_LOCK_PINS: '+name)
        require(set(installed)-set(expected) <= {'pip','setuptools','wheel'}, 'EXTRA_UNPINNED_PACKAGE: '+name)
        save(output/(name+'-lock.json'), dict(lock=lock, expected=expected, installed=installed))
        envs[name] = python

    for name, lock in [('v02', 'backend/tests/v02/requirements.lock'), ('v01', 'backend/requirements-test.lock'),
                       ('runtime', 'backend/infrastructure/http/requirements.lock')]:
        phase('install-'+name, lambda name=name, lock=lock: install(name, lock))

    def worker_run(name, kind, directory=None, db_command=None):
        require(name in envs, 'ENVIRONMENT_INSTALL_NOT_READY: '+name)
        dest = output/(directory or kind)
        args = [envs[name], '-I', '-B', worker, kind, '--candidate', candidate, '--output', dest]
        if db_command:
            args += ['--db-command', db_command]
        return runner.run((directory or kind), args, candidate, timeout=1200)

    for name, port in [('v02', '15441'), ('v01', '55441')]:
        runner.env['R03_DB_PORT'] = port
        phase(name+'-pg-before', lambda name=name: worker_run(name, 'db', name+'-pg-before', 'before'))
        def guarded_suite(name=name):
            require(results[name+'-pg-before']['result'] == 'PASS', 'SERVICE_PRECONDITION_FAILED')
            worker_run(name, name)
        phase(name+'-suite', guarded_suite)
        phase(name+'-pg-after', lambda name=name: worker_run(name, 'db', name+'-pg-after', 'after'))
    for kind in ('r02', 'r02a', 'r03a'):
        phase(kind, lambda kind=kind: worker_run('v02', kind))

    name = 'ms6_v01_smoke_v02_'+uuid.uuid4().hex
    runner.env.update(R03_DB_PORT='15441', R03_PROFILE_DB=name, DJANGO_DB_BACKEND='postgresql',
                      DJANGO_DB_HOST='127.0.0.1', DJANGO_DB_PORT='15441', DJANGO_DB_NAME=name,
                      DJANGO_DB_USER='postgres', DJANGO_DB_PASSWORD='synthetic-local-only',
                      DJANGO_SECRET_KEY='synthetic-v02-ci-profile', DJANGO_DEBUG='0',
                      DJANGO_RUNTIME_ROOT=str(output/'legacy-runtime'), MATHSTART_DB_BACKEND='postgresql',
                      MATHSTART_DATABASE_URL='postgresql+psycopg://postgres:synthetic-local-only@127.0.0.1:15441/'+name,
                      MATHSTART_HTTP_SIGNING_KEY='synthetic-v02-ci-key', MATHSTART_PUBLIC_ORIGIN='https://mathstart.example')
    def create_profile():
        require(results['v02-pg-before']['result'] == 'PASS', 'SERVICE_PRECONDITION_FAILED')
        worker_run('v02', 'db', 'content-profile-create', 'create')
    phase('content-profile-create', create_profile)
    phase('content-profile-fresh', lambda: runner.run('fresh-profile', [envs['v02'], '-B', candidate/'scripts/fresh_install_smoke.py', '--disposable'], candidate, timeout=1200))
    def content_parity():
        require(results['content-profile-fresh']['result'] == 'PASS', 'COMPLETE_CONTENT_PROFILE_REQUIRED')
        p = runner.run('content-parity', [envs['v02'], '-B', '-m', 'backend.tests.v02.public_baseline_projection'], candidate, timeout=180)
        record = json.loads(p.stdout)
        require(record['pages'] == 279 and record['topics'] == 263 and
                record['source_identity_mapping'] == record['seo_vs_django'] == record['catalogue_order_vs_django'] == record['read_only_sql'] == 'PASS', 'CONTENT_PARITY_COUNTS_OR_ASSERTIONS')
        save(output/'content-parity.json', record)
    phase('content-parity', content_parity)
    phase('runtime-no-django', lambda: worker_run('runtime', 'runtime'))
    phase('runtime-service', lambda: runtime_service(runner, envs['runtime'], candidate, output))
    def drop_profile():
        require(results['content-profile-create']['result'] == 'PASS', 'ONLY_THIS_RUN_CREATED_PROFILE_CAN_BE_DROPPED')
        worker_run('v02', 'db', 'content-profile-drop', 'drop')
    phase('content-profile-drop', drop_profile)
    phase('final-v02-pg-empty', lambda: worker_run('v02', 'db', 'final-v02-pg-empty', 'after'))
    phase('published-source-unchanged', lambda: require(not runner.git(candidate, 'status', '--porcelain'), 'TRACKED_CANDIDATE_MUTATION'))
    pr_after = publication.fetch_json('pulls/'+str(data['pr_number']), output, 'pr-after')
    publication.validate_pr(pr_after, data)
    index = json.loads((candidate/'docs/acceptance/MS7-MIG-V02/old-to-new-evidence.json').read_bytes())
    require(index['input_sha'] == publication.BASE and index['implementation_sha'] is None, 'HISTORICAL_SECTION17_LABELS')
    for row in index['records']:
        for path in [row['original_result_source'], *row['target_evidence']['paths']]:
            require((candidate/path).is_file(), 'SECTION17_LINK: '+path)
    save(output/'section17.json', dict(result='PASS_LINKS_AND_FROZEN_HISTORY', records=len(index['records']),
        historical_pending_labels_preserved=True, current_implementation_sha=data['implementation_sha'],
        current_test_evidence=['v02','v01','r02','r02a','r03a','content-parity','runtime-no-django']))
    for p in (candidate/'var').glob('ms7-mig-v02-f02-probes-*.json'):
        (output/p.name).write_bytes(p.read_bytes())
    record = dict(result='PASS' if all(v['result']=='PASS' for v in results.values()) else 'FAIL',
                  implementation_sha=data['implementation_sha'], checkout_tree=tree, live_pr_head_after=pr_after['head']['sha'],
                  workflow_sha=os.environ.get('GITHUB_WORKFLOW_SHA'), control_revision=publication.CONTROL,
                  phases=results, v02_task_approval=False, r03_status='INCOMPLETE')
    save(output/'task-result.json', record)
    print(json.dumps(record, indent=2))
    require(record['result'] == 'PASS', 'V02_TASK_CHECKS_FAILED')


def runtime_service(runner, python, candidate, output):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 8202))
    code = "import runpy,sys; sys.path.insert(0,sys.argv[1]); runpy.run_module('backend.infrastructure.http.runtime',run_name='__main__')"
    argv = list(map(str, [python, '-I', '-B', '-c', code, candidate]))
    with (output/'runtime-service.stdout').open('wb') as stdout, (output/'runtime-service.stderr').open('wb') as stderr:
        process = subprocess.Popen(argv, cwd=candidate, env=runner.env, stdout=stdout, stderr=stderr)
        try:
            deadline = time.monotonic()+30
            probes = []
            while True:
                require(process.poll() is None, 'OWNED_RUNTIME_EXITED')
                try:
                    urllib.request.urlopen('http://127.0.0.1:8202/api/v1/grades/', timeout=2).close()
                    break
                except (urllib.error.URLError, TimeoutError):
                    require(time.monotonic()<deadline, 'RUNTIME_HEALTH_TIMEOUT')
                    time.sleep(0.2)
            for path, expected in [('/api/v1/grades/',200), ('/api/v1/staff/pages/',401), ('/',503)]:
                try:
                    response = urllib.request.urlopen('http://127.0.0.1:8202'+path, timeout=5)
                except urllib.error.HTTPError as error:
                    response = error
                with response:
                    raw = response.read()
                    (output/('runtime-http-'+str(len(probes))+'.body')).write_bytes(raw)
                    require(response.status == expected, 'REAL_RUNTIME_HTTP_STATUS: '+path)
                    if path.startswith('/api/'):
                        require(response.headers.get('Cache-Control') == 'private, no-store', 'RUNTIME_PRIVATE_CACHE')
                    probes.append(dict(path=path,status=response.status,sha256=sha(raw),bytes=len(raw),headers=dict(response.headers)))
            save(output/'runtime-service.json', dict(result='PASS', argv=argv, pid=process.pid, probes=probes,
                bind='127.0.0.1:8202', auth_port='default deny', renderer_port='absent503', deadline_seconds=30))
        finally:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=5)
            save(output/'runtime-service-cleanup.json', dict(pid=process.pid, stopped=True, exit_code=process.returncode))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        main(args.candidate, args.output.resolve())
    finally:
        if args.output.exists():
            rows = [dict(path=p.relative_to(args.output.resolve()).as_posix(), sha256=sha(p.read_bytes()), bytes=p.stat().st_size)
                    for p in args.output.resolve().rglob('*') if p.is_file() and not any(x.startswith('venv-') for x in p.relative_to(args.output.resolve()).parts)]
            save(args.output.resolve()/'evidence-manifest.json', rows)
