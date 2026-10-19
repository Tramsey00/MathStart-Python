"""Install a real fresh release from an independent clean clone and locked tools.

Creates only an owned var/ clone, venv, local images, loopback ports and labelled
containers/networks. No legacy fixture bootstrap, old venv, copied build output
or synthetic activation helper is used for schema/operator/publication startup.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.verify_public_block import source_snapshot, assert_source_unchanged


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--disposable', action='store_true', required=True)
    parser.add_argument('--runtime-root', type=Path, required=True)
    parser.add_argument('--docker', default=shutil.which('docker'))
    parser.add_argument('--pg-port', type=int, default=55443)
    parser.add_argument('--port', type=int, default=18125)
    args = parser.parse_args(argv)
    root = args.runtime_root.resolve()
    if not args.docker or root.exists() or not root.is_relative_to(ROOT / 'var'):
        parser.error('Docker and a new owned root under checkout var/ required')
    if args.pg_port == args.port or any(not 1024 <= value <= 65535 for value in (args.pg_port, args.port)):
        parser.error('Distinct unprivileged loopback ports required')
    for port in (args.pg_port, args.port):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', port))
    root.mkdir(parents=True)
    before = source_snapshot(ROOT)
    run_id = uuid.uuid4().hex[:12]
    label = 'disposable-clean-install'
    names = {kind: 'migration-install-' + kind + '-' + run_id for kind in ('db', 'api', 'edge', 'network', 'permissions', 'builder', 'publisher', 'public')}
    owned, network, public_volume, private_files = {}, None, None, []
    clone, runtime = root / 'checkout', root / 'runtime'
    clone_python = clone / 'var/target-env' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    password, signing, operator_password = secrets.token_urlsafe(32), secrets.token_urlsafe(48), secrets.token_urlsafe(32)
    origin = 'http://127.0.0.1:' + str(args.port)
    env = {**{key: value for key, value in os.environ.items() if not key.startswith(('MATHSTART_', 'DJANGO_')) and key != 'PYTHONPATH'},
           'PYTHONIOENCODING': 'utf-8', 'PYTHONUNBUFFERED': '1'}
    report = {'status': 'IN_PROGRESS', 'scope': 'Fresh clean-clone ordinary operator/schema/build/publication flow; not final QA',
              'started_at': datetime.now(timezone.utc).isoformat(), 'source_before': before, 'stages': [], 'assertions': []}

    def run(identity, command, *, cwd=None, environment=None, timeout=120, expected=0):
        item = {'id': identity, 'argv': list(map(str, command)), 'cwd': str(cwd or ROOT)}
        report['stages'].append(item)
        tick = time.monotonic()
        result = subprocess.run(item['argv'], cwd=cwd or ROOT, env=environment or env,
                                capture_output=True, timeout=timeout)
        output = (result.stdout + result.stderr).decode('utf-8', errors='replace')
        for secret in (password, signing, operator_password):
            output = output.replace(secret, '[REDACTED]')
        path = root / (f'{len(report["stages"]):02d}-' + identity + '.log')
        path.write_text(output, encoding='utf-8', newline='\n')
        item.update(exit_code=result.returncode, seconds=round(time.monotonic() - tick, 3),
                    log=path.name, log_sha256=sha256(path.read_bytes()).hexdigest())
        if result.returncode != expected:
            raise RuntimeError('Required installation stage failed: ' + identity)
        return result.stdout.decode('utf-8').strip()

    def docker(identity, command, **kwargs):
        return run(identity, [args.docker, *command], **kwargs)

    def check(condition, identity):
        if not condition:
            raise RuntimeError(identity)
        report['assertions'].append(identity)

    def child(identity, arguments, timeout=120):
        return run(identity, [clone_python, *arguments], cwd=clone, environment=env, timeout=timeout)

    try:
        run('clone', ['git', '-c', 'core.autocrlf=false', 'clone', '--local', '--no-hardlinks', '--no-checkout', str(ROOT), str(clone)], timeout=180)
        # This belongs only to the new disposable clone, never the user's Git
        # globals. Existing curriculum paths exceed Win32's legacy MAX_PATH.
        for setting, value in [('core.longpaths', 'true'), ('core.autocrlf', 'false'), ('core.filemode', 'false')]:
            run('clone-config-' + setting, ['git', 'config', setting, value], cwd=clone)
        run('checkout', ['git', '-c', 'core.autocrlf=false', '-c', 'core.filemode=false', 'checkout', '--detach', before['head']], cwd=clone)
        actual = run('clone-head', ['git', 'rev-parse', 'HEAD'], cwd=clone)
        check(actual == before['head'] and not run('clone-clean-before', ['git', 'status', '--porcelain'], cwd=clone), 'independent_exact_clean_clone')
        report['clone_sha'] = actual
        run('new-target-venv', [sys.executable, '-m', 'venv', str(clone / 'var/target-env')], timeout=120)
        child('locked-target-install', ['-m', 'pip', '--disable-pip-version-check', 'install', '--no-deps', '-r', 'backend/infrastructure/http/requirements.lock'], timeout=300)
        child('target-pip-check', ['-m', 'pip', 'check'])
        versions = child('target-no-django', ['-c', "import sys,importlib.util,json; assert sys.version_info>=(3,12); assert not importlib.util.find_spec('django'); assert not importlib.util.find_spec('rest_framework'); print(json.dumps({'python':sys.version,'prefix':sys.prefix}))"])
        report['new_target_environment'] = json.loads(versions)
        images = {kind: 'mathstart-' + kind + ':install-' + run_id for kind in ('api', 'edge', 'frontend-builder')}
        for kind, tag in images.items():
            docker('build-' + kind, ['build', '-f', 'deploy/Dockerfile', '--target', kind, '--label',
                   'org.opencontainers.image.revision=' + actual, '-t', tag, '.'], cwd=clone, timeout=600)
        report['images'] = {kind: json.loads(docker('inspect-' + kind, ['image', 'inspect', tag]))[0]['Id'] for kind, tag in images.items()}
        check(all(docker('image-source-' + kind, ['image', 'inspect', '--format', '{{index .Config.Labels "org.opencontainers.image.revision"}}', tag]) == actual
                  for kind, tag in images.items()), 'actual_images_bound_to_clone_sha')
        runtime.mkdir()
        serving = runtime / 'serving'
        for path in (serving / 'releases', serving / 'frontend', runtime / 'output'):
            path.mkdir(parents=True)
        pg_env, api_env = runtime / 'private-postgres.env', runtime / 'private-api.env'
        for path, text in [(pg_env, 'POSTGRES_USER=install_test\nPOSTGRES_PASSWORD=' + password + '\nPOSTGRES_DB=install_test\n'),
                           (api_env, 'MATHSTART_DATABASE_URL=postgresql+psycopg://install_test:' + password + '@db:5432/install_test\nMATHSTART_DB_BACKEND=postgresql\nMATHSTART_HTTP_SIGNING_KEY=' + signing + '\nMATHSTART_PUBLIC_ORIGIN=' + origin + '\nMATHSTART_PUBLIC_ARTIFACT_DIGESTS={}\nMATHSTART_RELEASE_ROOT=/runtime/releases\nMATHSTART_PUBLIC_ARTIFACT_ROOT=/runtime/frontend\n')]:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as output:
                output.write(text)
            private_files.append(path)
        network = docker('network-create', ['network', 'create', '--label', 'mathstart.purpose=' + label, names['network']])
        occupied = subprocess.run([args.docker, 'volume', 'inspect', names['public']], capture_output=True, timeout=10)
        if occupied.returncode == 0:
            raise RuntimeError('Owned public volume name already exists')
        public_volume = docker('public-volume-create', ['volume', 'create', '--label', 'mathstart.purpose=' + label, names['public']])
        owned['db'] = docker('postgres-start', ['run', '--detach', '--name', names['db'], '--label', 'mathstart.purpose=' + label,
            '--network', names['network'], '--network-alias', 'db', '--tmpfs', '/var/lib/postgresql/data',
            '--publish', '127.0.0.1:' + str(args.pg_port) + ':5432', '--env-file', str(pg_env),
            'postgres@sha256:efedf3595f1d6f415c08568ba171029bf54052e754cc9f030e3f2412b21f3d67'])
        for _ in range(60):
            state = subprocess.run([args.docker, 'exec', owned['db'], 'pg_isready', '-U', 'install_test', '-d', 'install_test'], capture_output=True, timeout=10)
            if state.returncode == 0:
                break
            time.sleep(.5)
        else:
            raise RuntimeError('Owned fresh PostgreSQL did not start')
        env.update(MATHSTART_DATABASE_URL='postgresql+psycopg://install_test:' + password + '@127.0.0.1:' + str(args.pg_port) + '/install_test',
                   MATHSTART_DB_BACKEND='postgresql', MATHSTART_HTTP_SIGNING_KEY=signing,
                   MATHSTART_SCHEMA_SIGNING_KEY=secrets.token_urlsafe(48), MATHSTART_PUBLIC_ORIGIN=origin,
                   MATHSTART_OPERATOR_USERNAME='initial_' + run_id, MATHSTART_OPERATOR_PASSWORD=operator_password)
        preview = child('schema-preview', ['-m', 'backend.release_migrate', 'preview', '--profile', 'FRESH', '--plan-file', str(runtime / 'schema.json')])
        match = re.fullmatch(r'REVIEW_REQUIRED: plan SHA256 ([a-f0-9]{64})', preview)
        check(match is not None, 'actual_reviewable_schema_plan')
        child('schema-apply', ['-m', 'backend.release_migrate', 'apply', '--maintenance', '--plan-file', str(runtime / 'schema.json'), '--reviewed-plan-sha256', match.group(1)])
        child('schema-check', ['-m', 'backend.release_migrate', 'check'])
        child('initial-operator', ['-m', 'backend.users.operator', '--maintenance', '--from-environment'])
        release = 'initial-' + run_id
        prepared = json.loads(child('prepare-bootstrap', ['-m', 'backend.content.publish', 'prepare-bootstrap', '--source-root', '.',
            '--source-sha', actual, '--release-id', release, '--input-root', str(runtime / 'inputs'), '--changes', str(runtime / 'edition.json')], timeout=180))
        # Give only the newly owned empty builder output to its documented UID.
        owned['permissions'] = docker('builder-output-permissions', ['run', '--detach', '--name', names['permissions'],
            '--label', 'mathstart.purpose=' + label, '--network', 'none', '--no-healthcheck', '--user', '0',
            '--mount', 'type=bind,source=' + str(runtime / 'output') + ',target=/output',
            '--mount', 'type=volume,source=' + public_volume + ',target=/published', '--entrypoint', 'python', images['api'],
            '-c', "import os; os.chown('/output',10001,10001); os.chmod('/output',0o755); [os.mkdir('/published/'+p) for p in ('releases','frontend')]; [os.chown('/published/'+p,10001,10001) for p in ('releases','frontend')]; os.chown('/published',10001,10001)"])
        check(docker('builder-permissions-wait', ['wait', owned['permissions']]) == '0', 'actual_builder_output_permissions')
        docker('builder-permissions-remove', ['rm', owned['permissions']]); del owned['permissions']
        owned['builder'] = docker('locked-node-prerender', ['run', '--detach', '--name', names['builder'],
            '--label', 'mathstart.purpose=' + label, '--network', 'none', '--mount', 'type=bind,source=' + str(runtime / 'inputs') + ',target=/inputs,readonly',
            '--mount', 'type=bind,source=' + str(runtime / 'output') + ',target=/output', images['frontend-builder'],
            '--input-root', '/inputs', '--release-id', release, '--manifest-digest', prepared['manifest_digest'],
            '--receipt-digest', prepared['input_receipt_digest'], '--output', '/output/site', '--origin', origin], timeout=600)
        check(docker('locked-node-prerender-wait', ['wait', owned['builder']], timeout=600) == '0', 'actual_clean_node_build')
        docker('locked-node-prerender-logs', ['logs', owned['builder']])
        docker('locked-node-prerender-remove', ['rm', owned['builder']]); del owned['builder']
        artifact = runtime / 'output/site'
        output_digest = sha256((artifact / 'output-manifest.json').read_bytes()).hexdigest()
        options = ['--input-root', str(runtime / 'inputs'), '--output-root', str(artifact),
                   '--release-root', str(serving / 'releases'), '--artifact-root', str(serving / 'frontend')]
        child('publication-plan', ['-m', 'backend.content.publish', 'plan', '--changes', str(runtime / 'edition.json'),
            '--plan', str(runtime / 'publication.json'), '--origin', origin, '--output-digest', output_digest, *options])
        owned['api'] = docker('api-start', ['run', '--detach', '--name', names['api'], '--label', 'mathstart.purpose=' + label,
            '--network', names['network'], '--network-alias', 'api', '--read-only', '--cap-drop', 'ALL',
            '--tmpfs', '/tmp:rw,nosuid,noexec,size=32m', '--env-file', str(api_env),
            '--mount', 'type=volume,source=' + public_volume + ',target=/runtime,readonly', images['api']])
        owned['edge'] = docker('edge-start', ['run', '--detach', '--name', names['edge'], '--label', 'mathstart.purpose=' + label,
            '--network', names['network'], '--network-alias', 'edge', '--read-only', '--cap-drop', 'ALL',
            '--tmpfs', '/tmp:rw,nosuid,noexec,size=16m,uid=101,gid=101', '--publish', '127.0.0.1:' + str(args.port) + ':8080', images['edge']])
        # No proxy headers are needed by this initial local API; production-style
        # exact trusted peers are independently exercised by verify_images.py.
        child('initial-gateway-unready', ['-c', "import httpx,time; url=" + repr(origin) + "; result=None\nfor _ in range(60):\n try:\n  result=httpx.get(url+'/',trust_env=False,timeout=5)\n  if result.status_code==503:break\n except httpx.RequestError:pass\n time.sleep(.5)\nassert result is not None and result.status_code==503\nprint('EXPECTED_UNREADY_503')"], timeout=90)
        # The local canonical origin is a loopback IP. Only this disposable
        # publisher process routes that exact public-origin socket to the real
        # edge peer. HTTP URL/Host, all bytes/assertions and5s timeout stay intact.
        # Ordinary production publisher CLI needs no such routing when its real
        # public DNS/ingress is reachable. No global hosts file is modified.
        publisher_code = '''import collections,httpx,json,runpy,socket,sys,time
original=socket.getaddrinfo
def resolve(host,port,*args,**kwargs):
 return original('edge',8080,*args,**kwargs) if host=='127.0.0.1' and int(port)==PUBLIC_PORT else original(host,port,*args,**kwargs)
socket.getaddrinfo=resolve
send=httpx.Client.send
recent=collections.deque(maxlen=5); measured={'requests':0,'maximum_seconds':0}
def observed(client,request,*args,**kwargs):
 tick=time.monotonic(); item={'path':request.url.path}
 try:
  response=send(client,request,*args,**kwargs); item.update(status=response.status_code,cache=response.headers.get('cache-control')); return response
 except Exception as error:
  item['failure_class']=type(error).__name__; raise
 finally:
  item['seconds']=round(time.monotonic()-tick,3); measured['requests']+=1; measured['maximum_seconds']=max(measured['maximum_seconds'],item['seconds']); recent.append(item)
httpx.Client.send=observed
sys.argv=['backend.content.publish',*sys.argv[1:]]
try:runpy.run_module('backend.content.publish',run_name='__main__')
finally:print(json.dumps({'public_probe_trace':{**measured,'last':list(recent)}}),flush=True)
'''.replace('PUBLIC_PORT', str(args.port))
        owned['publisher'] = docker('publication-publisher-start', ['run', '--detach', '--name', names['publisher'],
            '--label', 'mathstart.purpose=' + label, '--network', names['network'], '--no-healthcheck', '--read-only',
            '--cap-drop', 'ALL', '--tmpfs', '/tmp:rw,nosuid,noexec,size=32m', '--env-file', str(api_env),
            '--mount', 'type=bind,source=' + str(runtime / 'inputs') + ',target=/inputs,readonly',
            '--mount', 'type=bind,source=' + str(artifact) + ',target=/output,readonly',
            '--mount', 'type=bind,source=' + str(runtime / 'publication.json') + ',target=/plan.json,readonly',
            '--mount', 'type=volume,source=' + public_volume + ',target=/runtime', images['api'],
            'python', '-c', publisher_code, 'publish', '--plan', '/plan.json', '--key', 'initial-' + run_id,
            '--owner', str(uuid.uuid4()), '--input-root', '/inputs', '--output-root', '/output',
            '--release-root', '/runtime/releases', '--artifact-root', '/runtime/frontend'])
        published_exit = docker('publication-publisher-wait', ['wait', owned['publisher']], timeout=1800)
        lines = docker('publication-publisher-logs', ['logs', owned['publisher']]).splitlines()
        values = []
        for line in lines:
            try:
                values.append(json.loads(line))
            except ValueError:
                continue
        report['public_probe_trace'] = next((value['public_probe_trace'] for value in values if 'public_probe_trace' in value), None)
        check(published_exit == '0', 'actual_publication_process_exit')
        published = next(value for value in values if value.get('phase') == 'COMPLETE')
        docker('publication-publisher-remove', ['rm', owned['publisher']]); del owned['publisher']
        check(published['phase'] == 'COMPLETE', 'ordinary_publication_cli_completed')
        child('actual-image-readiness', ['-c', "import subprocess; r=subprocess.run(" + repr([args.docker, 'exec', owned['api'], 'python', '-m', 'backend.health']) + ",capture_output=True); assert r.returncode==0 and r.stdout.strip()==b'READY'; print('READY')"])
        # Real network login to the image, no synthesized cookie or fixture user.
        child('actual-operator-login', ['-c', "import os,httpx; origin=os.environ['MATHSTART_PUBLIC_ORIGIN']; c=httpx.Client(trust_env=False,timeout=10); r=c.get(origin+'/'); assert r.status_code==200 and b'</html>' in r.content; t=c.get(origin+'/api/v1/auth/csrf/').json()['data']['csrf_token']; r=c.post(origin+'/api/v1/auth/login/',json={'username':os.environ['MATHSTART_OPERATOR_USERNAME'],'password':os.environ['MATHSTART_OPERATOR_PASSWORD']},headers={'Origin':origin,'X-CSRFToken':t}); assert r.status_code==200; assert c.get(origin+'/api/v1/users/me/').status_code==200; r=c.get(origin+'/admin/auth/user/'); assert r.status_code==200 and 'no-store' in r.headers['cache-control']; c.close(); print('REAL_OPERATOR_LOGIN_AND_PRIVATE_SHELL')"])
        child('actual-lesson-sources', ['-m', 'backend.cli', 'check-lesson-sources', '--source-root', '.', '--all'], timeout=120)
        repeated = json.loads(child('repeat-bootstrap-preview', ['-m', 'backend.content.publish', 'prepare-bootstrap', '--source-root', '.',
            '--source-sha', actual, '--release-id', 'repeat-' + run_id, '--input-root', str(runtime / 'absent-inputs'),
            '--changes', str(runtime / 'absent-edition.json'), '--dry-run'], timeout=120))
        check(repeated['changes'] == 0 and not (runtime / 'absent-inputs').exists() and not (runtime / 'absent-edition.json').exists(), 'repeat_bootstrap_is_pure_zero_change')
        check(not run('clone-clean-after', ['git', 'status', '--porcelain'], cwd=clone), 'clone_source_unchanged')
        report.update(status='PASS', release_id=release, output_manifest_digest=output_digest,
                      input_manifest_digest=prepared['manifest_digest'], input_receipt_digest=prepared['input_receipt_digest'])
    except Exception as error:
        report.update(status='FAIL', failure_class=type(error).__name__)
        if isinstance(error, RuntimeError):
            report['failure_check'] = str(error)
    finally:
        failures = []
        for kind in ('publisher', 'builder', 'permissions', 'edge', 'api', 'db'):
            if kind not in owned:
                continue
            try:
                state = json.loads(docker('inspect-owned-' + kind, ['container', 'inspect', owned[kind]]))[0]
                if state['Id'] != owned[kind] or state['Name'] != '/' + names[kind] or state['Config']['Labels'].get('mathstart.purpose') != label:
                    raise RuntimeError('Owned container identity mismatch')
                docker('logs-' + kind, ['logs', owned[kind]])
                docker('stop-' + kind, ['stop', owned[kind]], timeout=30)
                docker('remove-' + kind, ['rm', owned[kind]], timeout=30)
            except Exception as error:
                failures.append(type(error).__name__)
        if network:
            try:
                state = json.loads(docker('inspect-network', ['network', 'inspect', network]))[0]
                if state['Labels'].get('mathstart.purpose') != label:
                    raise RuntimeError('Owned network identity mismatch')
                docker('remove-network', ['network', 'rm', network])
            except Exception as error:
                failures.append(type(error).__name__)
        if public_volume:
            try:
                state = json.loads(docker('inspect-public-volume', ['volume', 'inspect', public_volume]))[0]
                if state['Name'] != names['public'] or state['Labels'].get('mathstart.purpose') != label:
                    raise RuntimeError('Owned public volume identity mismatch')
                docker('remove-public-volume', ['volume', 'rm', public_volume])
            except Exception as error:
                failures.append(type(error).__name__)
        for path in private_files:
            path.unlink(missing_ok=True)
        try:
            report['source_after'] = assert_source_unchanged(before, ROOT)
        except Exception:
            failures.append('SourceChanged')
        report['cleanup'] = 'FAIL' if failures else 'PASS'
        report['cleanup_errors'] = failures
        if failures:
            report['status'] = 'FAIL'
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        (root / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(json.dumps({'status': report['status'], 'failure_class': report.get('failure_class'), 'cleanup': report['cleanup'], 'result': str(root / 'result.json')}))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
