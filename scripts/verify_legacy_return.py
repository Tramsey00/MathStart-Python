"""Owned physical legacy return before target admission, then a new cutover.

Runs real Django and target HTTP/CLI processes against a fresh labelled cluster.
This rehearses an operator procedure; it is not a production restore command or
an automatic detector of writes made outside its owned process lifecycle.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
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
import httpx
import sqlalchemy as sa
from sqlalchemy.engine import URL
from psycopg import sql
from backend.migrations.schema import inventory, assert_baseline
from backend.release_migrate import source_digest, database_fact
from backend.users.cutover import writer_fact
from scripts.public_block_process import owned_http_service
from scripts.legacy_oracle import oracle_root, oracle_environment
from scripts.verify_public_block import source_snapshot, assert_source_unchanged, legacy_executable

PG_IMAGE = 'postgres@sha256:efedf3595f1d6f415c08568ba171029bf54052e754cc9f030e3f2412b21f3d67'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--disposable', action='store_true', required=True)
    parser.add_argument('--runtime-root', type=Path, required=True)
    parser.add_argument('--legacy-python', type=Path, required=True)
    parser.add_argument('--docker', default=shutil.which('docker'))
    args = parser.parse_args(argv)
    root = args.runtime_root.resolve()
    if (root.exists() or not root.is_relative_to(ROOT / 'var') or not args.docker
            or not args.legacy_python.is_file() or importlib.util.find_spec('django')):
        parser.error('New owned var root, Docker and separate no-Django/legacy environments required')
    for port in (55444, 18135, 18136):
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', port))
    root.mkdir(parents=True)
    before = source_snapshot(ROOT)
    tag = uuid.uuid4().hex[:12]
    label = 'disposable-legacy-return'
    names = {key: 'migration-return-' + key + '-' + tag for key in ('source', 'returned', 'copy', 'data', 'backup', 'restored')}
    owned, volumes = {}, []
    password, role_password, key, schema_key, account_password = (secrets.token_urlsafe(40) for _ in range(5))
    role, database = 'legacy_return_' + tag, 'test_ms7_mig_v01_return_' + tag
    username = 'return_' + tag
    origin, target_origin = 'http://127.0.0.1:18135', 'http://127.0.0.1:18136'
    pg_env = root / 'private-postgres.env'
    fd = os.open(pg_env, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
        stream.write('POSTGRES_USER=return_admin\nPOSTGRES_PASSWORD=' + password + '\nPOSTGRES_DB=' + database + '\n')
    env = {k: v for k, v in os.environ.items() if not k.startswith(('MATHSTART_', 'DJANGO_')) and k != 'PYTHONPATH'}
    env.update(PYTHONIOENCODING='utf-8', PYTHONUNBUFFERED='1')
    legacy_env = {**env, 'DJANGO_DB_BACKEND': 'postgresql', 'DJANGO_DB_HOST': '127.0.0.1',
        'DJANGO_DB_PORT': '55444', 'DJANGO_DB_NAME': database, 'DJANGO_DB_USER': 'return_admin',
        'DJANGO_DB_PASSWORD': password, 'DJANGO_SECRET_KEY': key, 'DJANGO_DEBUG': '0',
        'DJANGO_ALLOWED_HOSTS': '127.0.0.1', 'DJANGO_RUNTIME_ROOT': str(root / 'legacy'),
        'REHEARSAL_USERNAME': username, 'REHEARSAL_PASSWORD': account_password}
    url = URL.create('postgresql+psycopg', username='return_admin', password=password, host='127.0.0.1', port=55444, database=database)
    target_env = {**env, 'MATHSTART_DB_BACKEND': 'postgresql', 'MATHSTART_DATABASE_URL': url.render_as_string(hide_password=False),
        'MATHSTART_HTTP_SIGNING_KEY': key, 'MATHSTART_SCHEMA_SIGNING_KEY': schema_key,
        'MATHSTART_PUBLIC_ORIGIN': target_origin, 'MATHSTART_LEGACY_WRITER_ROLE': role}
    engine = sa.create_engine(url, hide_parameters=True, connect_args={'connect_timeout': 5})
    report = {'status': 'IN_PROGRESS', 'scope': 'Physical legacy return before target admission and fresh identity recutover; not public SSG or final QA',
        'source_before': before, 'started_at': datetime.now(timezone.utc).isoformat(), 'argv': sys.argv,
        'cwd': str(ROOT), 'assertions': [], 'stages': [], 'cleanup': 'NOT_RUN'}
    admitted = False

    def check(condition, name):
        if not condition:
            raise RuntimeError(name)
        report['assertions'].append(name)

    def run(name, command, *, environment=env, timeout=180):
        started = time.monotonic()
        cwd = oracle_root() if environment is legacy_env else ROOT
        item = {'id': name, 'argv': list(map(str, command)), 'cwd': str(cwd)}
        report['stages'].append(item)
        result = subprocess.run(item['argv'], cwd=cwd, env=oracle_environment(environment), capture_output=True, timeout=timeout)
        output = result.stdout + result.stderr
        for secret in (password, role_password, key, schema_key, account_password):
            output = output.replace(secret.encode(), b'[REDACTED]')
        log = root / (str(len(report['stages'])).zfill(2) + '-' + name + '.log')
        log.write_bytes(output)
        item.update(exit_code=result.returncode, seconds=round(time.monotonic() - started, 3), log=log.name, log_sha256=sha256(output).hexdigest())
        if result.returncode:
            raise RuntimeError('stage_' + name)
        return result.stdout.decode('utf-8').strip()

    def docker(name, command, **kwargs):
        return run(name, [args.docker, *command], **kwargs)

    def volume(kind):
        present = subprocess.run([args.docker, 'volume', 'inspect', names[kind]], capture_output=True, timeout=10)
        check(present.returncode != 0, kind + '_volume_not_adopted')
        docker('create-' + kind, ['volume', 'create', '--label', 'mathstart.purpose=' + label, names[kind]])
        volumes.append(kind)

    def start_db(kind, data):
        owned[kind] = docker('start-' + kind, ['run', '--detach', '--name', names[kind], '--label', 'mathstart.purpose=' + label,
            '--publish', '127.0.0.1:55444:5432', '--env-file', str(pg_env),
            '--mount', 'type=volume,source=' + names[data] + ',target=/var/lib/postgresql/data',
            '--mount', 'type=volume,source=' + names['backup'] + ',target=/backup', PG_IMAGE])
        for _ in range(60):
            try:
                with engine.connect() as c:
                    c.execute(sa.text('SELECT 1'))
                break
            except sa.exc.OperationalError:
                time.sleep(.5)
        else:
            raise RuntimeError('postgres_startup')

    def role_login(enabled):
        engine.dispose()
        with engine.begin() as c:
            c.execute(sa.text('ALTER ROLE ' + role + (' LOGIN' if enabled else ' NOLOGIN')))
            check(c.scalar(sa.text('SELECT count(*) FROM pg_stat_activity WHERE usename=:role'), {'role': role}) == 0, 'legacy_role_connections_drained')

    def facts():
        with engine.connect() as c:
            state = inventory(c)
            return {'database': database_fact(c), 'writer': writer_fact(c, role), 'private_hmac': source_digest(c, key, state)}

    def return_snapshot():
        # This is an owned procedure guard, not a production change-history oracle.
        # No externally admitted writers exist during its controlled lifecycle.
        if admitted:
            raise RuntimeError('TARGET_ALREADY_ADMITTED')
        engine.dispose()
        docker('stop-target-cluster', ['stop', owned['source']], timeout=30)
        state = json.loads(docker('inspect-stopped-source', ['inspect', owned['source']]))[0]
        check(not state['State']['Running'], 'target_cluster_fenced_before_legacy_restore')
        owned['copy'] = docker('copy-physical-pre-snapshot', ['run', '--detach', '--name', names['copy'], '--label', 'mathstart.purpose=' + label,
            '--network', 'none', '--entrypoint', '/bin/sh', '--mount', 'type=volume,source=' + names['backup'] + ',target=/backup,readonly',
            '--mount', 'type=volume,source=' + names['restored'] + ',target=/restored', PG_IMAGE, '-c', 'cp -a /backup/cluster/. /restored/'])
        check(docker('copy-wait', ['wait', owned['copy']]) == '0', 'physical_pre_snapshot_copy')
        docker('copy-remove', ['rm', owned['copy']]); del owned['copy']
        start_db('returned', 'restored')

    def legacy_service(name):
        return owned_http_service([legacy_executable(args.legacy_python), 'manage.py', 'runserver', '127.0.0.1:18135', '--noreload', '--nothreading', '--no-color'],
            base_url=origin, cwd=oracle_root(), evidence_root=root / name, environment=oracle_environment(legacy_env))

    def headers(client, base):
        response = client.get(base + '/api/v1/auth/csrf/')
        check(response.status_code == 200, 'actual_csrf_bootstrap')
        return {'Origin': base, 'X-CSRFToken': response.json()['data']['csrf_token']}

    def adopt(prefix):
        engine.dispose()
        schema = root / (prefix + '-schema.json')
        preview = run(prefix + '-schema-preview', [sys.executable, '-m', 'backend.release_migrate', 'preview', '--profile', 'C', '--legacy-role', role, '--plan-file', str(schema)], environment=target_env)
        digest = re.fullmatch(r'REVIEW_REQUIRED: plan SHA256 ([a-f0-9]{64})', preview)
        check(digest is not None, prefix + '_real_schema_plan')
        run(prefix + '-schema-apply', [sys.executable, '-m', 'backend.release_migrate', 'apply', '--maintenance', '--plan-file', str(schema), '--reviewed-plan-sha256', digest[1]], environment=target_env)
        plan = root / (prefix + '-cutover.json')
        run(prefix + '-cutover-preview', [sys.executable, '-m', 'backend.users.cutover_cli', 'preview', '--checkpoint-id', str(uuid.uuid4()), '--plan', str(plan)], environment=target_env)
        run(prefix + '-cutover-apply', [sys.executable, '-m', 'backend.users.cutover_cli', 'apply', '--plan', str(plan)], environment=target_env)
        return json.loads(plan.read_text(encoding='utf-8'))

    try:
        for kind in ('data', 'backup', 'restored'):
            volume(kind)
        start_db('source', 'data')
        legacy = legacy_executable(args.legacy_python)
        run('legacy-schema', [legacy, 'manage.py', 'migrate', '--noinput'], environment=legacy_env)
        run('legacy-content', [legacy, 'manage.py', 'bootstrap_site'], environment=legacy_env)
        run('legacy-static', [legacy, 'manage.py', 'collectstatic', '--noinput'], environment=legacy_env)
        with engine.begin() as c:
            c.exec_driver_sql(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(role), sql.Literal(role_password)).as_string())
            c.execute(sa.text('GRANT CONNECT ON DATABASE ' + database + ' TO ' + role))
            c.execute(sa.text('GRANT USAGE ON SCHEMA public TO ' + role))
            c.execute(sa.text('GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO ' + role))
            c.execute(sa.text('GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO ' + role))
        legacy_env.update(DJANGO_DB_USER=role, DJANGO_DB_PASSWORD=role_password)
        with legacy_service('legacy-before'), httpx.Client(trust_env=False, timeout=10) as client:
            h = headers(client, origin)
            response = client.post(origin + '/api/v1/auth/register/', json={'username': username, 'password': account_password}, headers={**h, 'Idempotency-Key': 'return-register-' + tag})
            check(response.status_code == 201, 'native_django_registration_and_receipt')
            grades = client.get(origin + '/api/v1/grades/').json()['data']
            check(len(grades) >= 2, 'native_grade_ids_present')
            response = client.post(origin + '/api/v1/onboarding/complete/', json={'selected_grade_id': grades[0]['id'], 'mode': 'SELF_REPORT'}, headers={**headers(client, origin), 'Idempotency-Key': 'return-onboarding-' + tag})
            check(response.status_code == 200, 'native_django_onboarding_receipt')
            expected = client.get(origin + '/api/v1/users/me/').json()['data']
            cookies = httpx.Cookies(client.cookies)
            public = client.get(origin + '/').content
        seed = "import os,uuid; os.environ['DJANGO_SETTINGS_MODULE']='config.settings'; import django; django.setup(); from django.contrib.auth import get_user_model; from django.contrib.auth.models import Group,Permission; from django.contrib.admin.models import LogEntry,CHANGE; from django.contrib.contenttypes.models import ContentType; from django.utils import timezone; from datetime import timedelta; from users.models import IdentityReceipt; u=get_user_model().objects.get(username=os.environ['REHEARSAL_USERNAME']); g=Group.objects.create(name='Return role '+uuid.uuid4().hex); u.groups.add(g); p=Permission.objects.first(); g.permissions.add(p); u.user_permissions.add(p); LogEntry.objects.create(user=u,content_type=ContentType.objects.get_for_model(u),object_id=str(u.pk),object_repr='Synthetic return account',action_flag=CHANGE,change_message='Synthetic before maintenance'); IdentityReceipt.objects.create(scope='anonymous:return-pending',operation='register',key_digest='d'*64,request_digest='e'*64,expires_at=timezone.now()+timedelta(days=7)); print('PRIVATE_FIXTURES_CREATED')"
        run('native-private-fixtures', [legacy, '-c', seed], environment=legacy_env)
        role_login(False)
        with engine.connect() as c:
            assert_baseline(c, 'C')
        baseline = facts()
        report['pre_snapshot_facts'] = baseline
        media = {str(p.relative_to(root / 'legacy/media')): sha256(p.read_bytes()).hexdigest() for p in (root / 'legacy/media').rglob('*') if p.is_file()}
        check(len(media) == 29, 'all29_legacy_media_present')
        shutil.copytree(root / 'legacy/media', root / 'returned-runtime/media')
        shutil.copytree(root / 'legacy/staticfiles', root / 'returned-runtime/staticfiles')
        uid = docker('postgres-uid', ['exec', owned['source'], 'id', '-u', 'postgres'])
        gid = docker('postgres-gid', ['exec', owned['source'], 'id', '-g', 'postgres'])
        docker('backup-permission', ['exec', owned['source'], 'chown', uid + ':' + gid, '/backup'])
        tick = time.monotonic()
        docker('pre-basebackup', ['exec', '--user', 'postgres', owned['source'], 'pg_basebackup', '-U', 'return_admin', '-D', '/backup/cluster', '-X', 'stream', '--checkpoint=fast', '--manifest-checksums=SHA256'])
        docker('pre-verifybackup', ['exec', '--user', 'postgres', owned['source'], 'pg_verifybackup', '/backup/cluster'])
        report['backup_seconds'] = round(time.monotonic() - tick, 3)
        check(facts() == baseline, 'physical_snapshot_retains_full_private_facts_and_oids')
        old_plan = adopt('first')
        check(facts()['private_hmac'] != baseline['private_hmac'], 'controlled_schema_and_import_changes_are_real')
        # No target HTTP process has been started and no target user admitted.
        tick = time.monotonic()
        return_snapshot()
        check(facts() == baseline, 'returned_entire_pre_cluster_schema_rows_sequences_roles_oids_exact')
        legacy_env['DJANGO_RUNTIME_ROOT'] = str(root / 'returned-runtime')
        returned_media = {str(p.relative_to(root / 'returned-runtime/media')): sha256(p.read_bytes()).hexdigest() for p in (root / 'returned-runtime/media').rglob('*') if p.is_file()}
        check(returned_media == media, 'returned_full_media_bytes')
        with engine.connect() as c:
            check('target_identity_cutover' not in sa.inspect(c).get_table_names(), 'legacy_return_has_no_target_schema_history')
            assert_baseline(c, 'C')
        role_login(True)
        with legacy_service('legacy-returned'), httpx.Client(trust_env=False, timeout=10, cookies=cookies) as client:
            check(client.get(origin + '/').content == public, 'returned_actual_django_public_html')
            check(client.get(origin + '/api/v1/users/me/').json()['data'] == expected, 'returned_native_session_and_complete_profile')
            check(client.post(origin + '/api/v1/auth/login/', json={'username': username, 'password': account_password}, headers=headers(client, origin)).status_code == 200, 'returned_actual_password_login')
            cookies = httpx.Cookies(client.cookies)
        report['return_through_legacy_login_seconds'] = round(time.monotonic() - tick, 3)
        role_login(False)
        fresh_plan = adopt('recutover')
        check(fresh_plan['checkpoint_digest'] != old_plan['checkpoint_digest'], 'new_cutover_never_reuses_old_checkpoint')
        target_env['MATHSTART_IDENTITY_CUTOVER_DIGEST'] = fresh_plan['checkpoint_digest']
        with owned_http_service([sys.executable, '-m', 'uvicorn', 'backend.infrastructure.http.runtime:application', '--factory', '--host', '127.0.0.1', '--port', '18136', '--no-access-log', '--no-proxy-headers'],
                base_url=target_origin, readiness_path='/api/v1/grades/', cwd=ROOT, evidence_root=root / 'target-after-return', environment=target_env), httpx.Client(trust_env=False, timeout=10, cookies=cookies) as client:
            admitted = True
            check(client.get(target_origin + '/api/v1/users/me/').status_code == 401, 'old_native_session_requires_one_target_relogin')
            response = client.post(target_origin + '/api/v1/auth/login/', json={'username': username, 'password': account_password}, headers=headers(client, target_origin))
            check(response.status_code == 200 and response.json()['data'] == expected, 'real_f_login_after_new_cutover_preserves_complete_profile')
            response = client.patch(target_origin + '/api/v1/users/me/', json={'selected_grade_id': grades[1]['id']}, headers=headers(client, target_origin))
            check(response.status_code == 200 and response.json()['data']['selected_grade_id'] == grades[1]['id'], 'real_target_profile_write_after_admission')
            persisted = client.get(target_origin + '/api/v1/users/me/').json()['data']
        after_writes = facts()
        try:
            return_snapshot()
        except RuntimeError as error:
            check(str(error) == 'TARGET_ALREADY_ADMITTED', 'owned_return_procedure_refuses_old_snapshot_after_target_admission')
        else:
            raise RuntimeError('unsafe_return_was_admitted')
        check(facts() == after_writes, 'refused_unsafe_return_preserves_current_all_private_facts')
        # The supported alternative after writes is the compatible API switch
        # already measured by verify_images --recovery, never this old snapshot.
        check(persisted['selected_grade_id'] != expected['selected_grade_id'], 'target_write_is_not_a_noop')
        report.update(status='PASS_SCOPED_DEVELOPMENT', media_files=len(media), legacy_return_before_target_admission=True,
            later_snapshot_return='REFUSED_BY_OWNED_PROCEDURE_NOT_A_PRODUCTION_WRITE_ORACLE', target_after_return='REAL_F_LOGIN_AND_PROFILE_WRITE')
    except Exception as error:
        report.update(status='FAIL', failure_class=type(error).__name__)
        if isinstance(error, RuntimeError):
            report['failure_check'] = str(error)
    finally:
        engine.dispose()
        failures = []
        for kind, cid in list(owned.items()):
            try:
                state = json.loads(docker('cleanup-inspect-' + kind, ['inspect', cid]))[0]
                if state['Id'] != cid or state['Name'] != '/' + names[kind] or state['Config']['Labels'].get('mathstart.purpose') != label:
                    raise RuntimeError('ownership_mismatch')
                docker('cleanup-stop-' + kind, ['stop', cid], timeout=30)
                docker('cleanup-remove-' + kind, ['rm', cid], timeout=30)
            except Exception as error:
                failures.append(type(error).__name__)
        for kind in volumes:
            try:
                state = json.loads(docker('cleanup-volume-' + kind, ['volume', 'inspect', names[kind]]))[0]
                if state['Labels'].get('mathstart.purpose') != label or state['Name'] != names[kind]:
                    raise RuntimeError('volume_ownership_mismatch')
                docker('cleanup-remove-volume-' + kind, ['volume', 'rm', names[kind]])
            except Exception as error:
                failures.append(type(error).__name__)
        pg_env.unlink(missing_ok=True)
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
        print(json.dumps({'status': report['status'], 'failure_check': report.get('failure_check'), 'cleanup': report['cleanup'], 'result': str(root / 'result.json')}))
    return 0 if report['status'] == 'PASS_SCOPED_DEVELOPMENT' else 1


if __name__ == '__main__':
    raise SystemExit(main())
