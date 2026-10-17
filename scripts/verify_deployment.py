"""Rehearse Compose and the explicit release schema step on owned empty volumes.

This verifies an uninitialized deployment stays unready. Installed content and
auth are checked separately by verify_images.py. No production attachment,
secret publication, automatic backup deletion or shared-volume adoption.
"""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import secrets
import shutil
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
    parser.add_argument('--api-image', required=True)
    parser.add_argument('--edge-image', required=True)
    parser.add_argument('--docker', default=shutil.which('docker'))
    args = parser.parse_args(argv)
    root = args.runtime_root.resolve()
    if not args.docker or root.exists() or not root.is_relative_to(ROOT / 'var'):
        parser.error('Docker CLI and a new owned runtime directory under checkout var/ required')
    root.mkdir(parents=True)
    project = 'migration-stack-' + uuid.uuid4().hex[:12]
    purpose = 'disposable-stack-rehearsal'
    label = 'mathstart.purpose=' + purpose
    password, key = secrets.token_urlsafe(32), secrets.token_urlsafe(48)
    files, volumes, containers, networks = [], [], [], []
    env = dict(os.environ)
    report = {'status': 'IN_PROGRESS', 'scope': 'Compose/schema installation and uninitialized readiness; not final QA',
              'assertions': [], 'source_before': source_snapshot(ROOT)}

    def command(argv, *, log=None, expected=0, timeout=120):
        result = subprocess.run([args.docker, *argv], env=env, capture_output=True, timeout=timeout)
        output = (result.stdout + result.stderr).decode('utf-8', errors='replace')
        for value in (password, key):
            output = output.replace(value, '[REDACTED]')
        if log:
            (root / log).write_text(output, encoding='utf-8', newline='\n')
        if result.returncode != expected:
            (root / 'failure.log').write_text(output, encoding='utf-8', newline='\n')
            raise RuntimeError('Owned deployment command failed')
        return result.stdout.decode('utf-8').strip()

    def check(condition, identity):
        if not condition:
            raise RuntimeError(identity)
        report['assertions'].append(identity)

    compose = ['compose', '-f', str(ROOT / 'deploy/compose.yaml')]

    def job(command_args, identity, *, service='release'):
        name = project + '-' + identity
        cid = command([*compose, 'run', '--detach', '--no-deps', '--name', name, '--label', label,
                       service, *command_args])
        containers.append(cid)
        check(command(['wait', cid], timeout=120) == '0', identity)
        output = command(['logs', cid], log=identity + '.log')
        command(['rm', cid]); containers.remove(cid)
        return output

    try:
        check(not command(['ps', '--all', '--quiet', '--filter', 'label=com.docker.compose.project=' + project]), 'new_project')
        for reference in (args.api_image, args.edge_image):
            command(['image', 'inspect', reference])  # No implicit mutable pulls.
        existing = command(['network', 'ls', '--quiet']).splitlines()
        ranges = []
        for network in json.loads(command(['network', 'inspect', *existing])) if existing else []:
            ranges.extend(ipaddress.ip_network(item['Subnet']) for item in (network.get('IPAM', {}).get('Config') or []) if item.get('Subnet'))
        subnet = next(ipaddress.ip_network(f'172.26.{number}.0/24') for number in range(240, 255)
                      if all(not ipaddress.ip_network(f'172.26.{number}.0/24').overlaps(item) for item in ranges if item.version == 4))
        postgres, runtime, schema = (root / name for name in ('private-postgres.env', 'private-runtime.env', 'private-schema.env'))
        for path, text in [(postgres, 'POSTGRES_USER=stack_test\nPOSTGRES_PASSWORD=' + password + '\nPOSTGRES_DB=stack_test\n'),
                           (runtime, 'MATHSTART_DATABASE_URL=postgresql+psycopg://stack_test:' + password + '@db:5432/stack_test\nMATHSTART_DB_BACKEND=postgresql\nMATHSTART_HTTP_SIGNING_KEY=' + key + '\nMATHSTART_PUBLIC_ORIGIN=http://127.0.0.1:18124\nMATHSTART_PUBLIC_ARTIFACT_DIGESTS={}\n'),
                           (schema, 'MATHSTART_SCHEMA_SIGNING_KEY=' + key + '\n')]:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as output:
                output.write(text)
            files.append(path)
        plans = root / 'plans'; plans.mkdir(mode=0o770)
        if os.name != 'nt':
            # Keep the image's non-root UID. A supplementary operator group
            # permits creating mode0600 plans in this owned host directory.
            os.chmod(plans, 0o770)
            override = root / 'compose-owned.json'
            override.write_text(json.dumps({'services': {'release': {'group_add': [str(os.getgid())]}}}), encoding='utf-8')
            compose.extend(['-f', str(override)])
        env.update(MATHSTART_STACK=project, MATHSTART_API_IMAGE=args.api_image, MATHSTART_EDGE_IMAGE=args.edge_image,
                   MATHSTART_POSTGRES_ENV_FILE=str(postgres), MATHSTART_RUNTIME_ENV_FILE=str(runtime),
                   MATHSTART_SCHEMA_ENV_FILE=str(schema), MATHSTART_PLAN_DIRECTORY=str(plans),
                   MATHSTART_EDGE_IP=str(subnet.network_address + 10), MATHSTART_INTERNAL_SUBNET=str(subnet),
                   MATHSTART_HTTP_PORT='18124', MATHSTART_DATABASE_VOLUME=project + '-database',
                   MATHSTART_PUBLIC_VOLUME=project + '-public')
        command([*compose, 'config', '--quiet'])
        check(True, 'actual_compose_config')
        for name in (env['MATHSTART_DATABASE_VOLUME'], env['MATHSTART_PUBLIC_VOLUME']):
            occupied = subprocess.run([args.docker, 'volume', 'inspect', name], capture_output=True, timeout=10)
            if occupied.returncode == 0:
                raise RuntimeError('Reserved volume name already exists')
            command(['volume', 'create', '--label', label, name]); volumes.append(name)
        # Only create the two empty serving directories, no automatic DB/bootstrap.
        cid = command(['run', '--detach', '--name', project + '-dirs', '--label', label,
                       '--network', 'none', '--no-healthcheck', '--user', '0',
                       '--mount', 'type=volume,source=' + env['MATHSTART_PUBLIC_VOLUME'] + ',target=/runtime',
                       '--entrypoint', 'python', args.api_image, '-c',
                       "import os; [os.mkdir('/runtime/'+n) for n in ('releases','frontend')]; [os.chown('/runtime/'+n,10001,10001) for n in ('releases','frontend')]"])
        containers.append(cid)
        check(command(['wait', cid]) == '0', 'owned_serving_directories')
        command(['rm', cid]); containers.remove(cid)
        command([*compose, 'up', '--detach', 'db'], log='db-start.log')
        db = command([*compose, 'ps', '--all', '--quiet', 'db']); containers.append(db)
        for _ in range(60):
            state = json.loads(command(['container', 'inspect', db]))[0]
            if state['State']['Health']['Status'] == 'healthy':
                break
            time.sleep(.5)
        else:
            raise RuntimeError('Owned PostgreSQL did not become healthy')
        output = job(['preview', '--profile', 'FRESH', '--plan-file', '/plans/schema.json'], 'preview')
        # The explicit operator review boundary is exercised only for this
        # synthetic empty database; this is not approval of any real DB plan.
        match = re.fullmatch(r'REVIEW_REQUIRED: plan SHA256 ([a-f0-9]{64})', output.strip())
        if match is None:
            raise RuntimeError('Actual preview did not emit its review digest')
        reviewed = match.group(1)
        applied = job(['apply', '--plan-file', '/plans/schema.json', '--maintenance', '--reviewed-plan-sha256', reviewed], 'apply')
        job(['check'], 'schema-check')
        report['schema_head'] = json.loads(applied)['head']
        command([*compose, 'up', '--detach', '--no-deps', 'api'], log='api-start.log')
        api = command([*compose, 'ps', '--all', '--quiet', 'api']); containers.append(api)
        for _ in range(40):
            state = json.loads(command(['container', 'inspect', api]))[0]
            if state['State']['Running']:
                time.sleep(2)
                break
            time.sleep(.5)
        health = command(['exec', api, 'python', '-m', 'backend.health'], expected=1, log='uninitialized-health.log')
        check(health == 'UNREADY', 'missing_publication_is_unready')
        # API startup may read the schema, but may not seed content or migrate.
        query = "import sqlalchemy as s; from backend.infrastructure.database import *; e=create_engine(DatabaseConfig.from_environment()); c=e.connect(); assert c.scalar(s.text('SELECT count(*) FROM content_contentpage'))==0; assert c.scalar(s.text('SELECT count(*) FROM auth_user'))==0; assert c.scalar(s.text('SELECT version_num FROM alembic_version'))=='v01_0002'; c.close(); e.dispose(); print('NO_STARTUP_WRITES')"
        command(['exec', api, 'python', '-c', query], log='startup-rows.log')
        check(True, 'api_startup_no_content_auth_or_schema_writes')
        job(['-t'], 'edge-config', service='edge')
        report['status'] = 'PASS'
    except Exception as error:
        report.update(status='FAIL', failure_class=type(error).__name__)
    finally:
        failures = []
        # Recover a partially created Compose service by our unique project label.
        try:
            containers.extend(command(['ps', '--all', '--no-trunc', '--quiet', '--filter', 'label=com.docker.compose.project=' + project]).splitlines())
            networks = command(['network', 'ls', '--quiet', '--filter', 'label=com.docker.compose.project=' + project]).splitlines()
            for cid in dict.fromkeys(containers):
                state = json.loads(command(['container', 'inspect', cid]))[0]
                labels = state['Config']['Labels'] or {}
                if labels.get('mathstart.purpose') != purpose and labels.get('com.docker.compose.project') != project:
                    raise RuntimeError('Container ownership mismatch')
                command(['stop', cid], timeout=30); command(['rm', cid], timeout=30)
            for nid in networks:
                state = json.loads(command(['network', 'inspect', nid]))[0]
                if state['Labels'].get('com.docker.compose.project') != project:
                    raise RuntimeError('Network ownership mismatch')
                command(['network', 'rm', nid])
            for name in volumes:
                state = json.loads(command(['volume', 'inspect', name]))[0]
                if state['Labels'].get('mathstart.purpose') != purpose:
                    raise RuntimeError('Volume ownership mismatch')
                command(['volume', 'rm', name])
        except Exception as error:
            failures.append(type(error).__name__)
        for path in files:
            path.unlink(missing_ok=True)
        try:
            report['source_after'] = assert_source_unchanged(report['source_before'], ROOT)
        except Exception:
            failures.append('SourceChanged')
        report['cleanup'] = 'FAIL' if failures else 'PASS'
        report['cleanup_errors'] = failures
        if failures:
            report['status'] = 'FAIL'
        (root / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(json.dumps({'status': report['status'], 'cleanup': report['cleanup'], 'assertions': len(report['assertions']),
                          'result': str(root / 'result.json')}))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
