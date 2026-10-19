"""Physical recovery phase of the owned image rehearsal, never an operator restore.

Caller owns every container/volume and performs cleanup. This keeps private rows
inside PostgreSQL/volumes and exports only HMACs, public hashes and measurements.
The restored cluster preserves database/role OIDs required by cutover provenance.
"""
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import os
from pathlib import Path
import statistics
from math import ceil
from threading import Barrier, Lock
import time
import uuid

import httpx
import sqlalchemy as sa

from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import Group, IdentityReceipt, User, metadata
from backend.release_migrate import database_fact, source_digest
from backend.migrations.schema import inventory
from backend.users.cutover import CutoverImport

PG_IMAGE = 'postgres@sha256:efedf3595f1d6f415c08568ba171029bf54052e754cc9f030e3f2412b21f3d67'


def ordinary_api_workload(client, origin, verify):
    """Ten real clients,200 measured GETs per existing API cohort, no retries.

    Warm-up/handshakes are separate. Errors remain in the denominator/latencies;
    callers retain this report before asserting the actual success/SLO criteria.
    Private DTOs/cookies stay in memory and never enter the timing records.
    """
    paths = ('/api/v1/grades/', '/api/v1/users/me/')
    expected = {}
    for path in paths:
        response = client.get(origin + path)
        if response.status_code != 200:
            raise RuntimeError('Ordinary API benchmark prerequisite refused')
        expected[path] = response.json()['data']
    cookies = httpx.Cookies(client.cookies)
    barrier, lock = Barrier(10), Lock()
    flight, peak = 0, 0

    def worker(index):
        nonlocal flight, peak
        records, warm_errors = [], 0
        with httpx.Client(trust_env=False, follow_redirects=False, timeout=10, verify=verify,
                          cookies=httpx.Cookies(cookies)) as active:
            for path in paths:
                try:
                    warm_errors += active.get(origin + path).status_code != 200
                except httpx.RequestError:
                    warm_errors += 1
            barrier.wait(timeout=60)
            for iteration in range(40):
                path = paths[(index + iteration) % len(paths)]
                tick = time.monotonic()
                with lock:
                    flight += 1
                    peak = max(peak, flight)
                record = {'request': index * 40 + iteration, 'path': path}
                try:
                    response = active.get(origin + path)
                    record['status'] = response.status_code
                    body = response.json()
                    record['valid'] = (response.status_code == 200 and body.get('data') == expected[path]
                                       and 'no-store' in response.headers.get('cache-control', ''))
                    correlation = str(uuid.UUID(body['meta']['request_id']))
                    record['correlation'] = correlation  # Removed before exporting.
                except Exception as error:
                    record.update(valid=False, failure_class=type(error).__name__)
                finally:
                    record['milliseconds'] = round((time.monotonic() - tick) * 1000, 3)
                    with lock:
                        flight -= 1
                    records.append(record)
        return records, int(warm_errors)

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=10) as pool:
        parts = list(pool.map(worker, range(10)))
    records = sorted((record for part, _ in parts for record in part), key=lambda row: row['request'])
    correlations = [row.pop('correlation') for row in records if 'correlation' in row]

    def stats(rows):
        ordered = sorted(row['milliseconds'] for row in rows)
        return {'requests': len(rows), 'failures': sum(not row['valid'] for row in rows),
                'p50_ms': round(statistics.median(ordered), 3),
                'p95_ms': ordered[ceil(.95 * len(ordered)) - 1], 'max_ms': max(ordered)}

    return {**stats(records), 'concurrency': 10, 'observed_peak_inflight': peak,
            'warmup_requests': 20, 'warmup_failures': sum(errors for _, errors in parts),
            'cohorts': {path: stats([row for row in records if row['path'] == path]) for path in paths},
            'unique_request_correlations': len(set(correlations)), 'nearest_rank': 'ceil(0.95*n)',
            'elapsed_with_warmup_seconds': round(time.monotonic() - started, 3),
            'transport': origin.split(':', 1)[0], 'network': 'Owned loopback edge, internal two-worker API and PostgreSQL',
            'claim': 'Measured existing ordinary APIs only; no Product AI or production capacity claim',
            'samples': records}


def rehearse(engine, *, command, check, owned, names, image, directory, label,
             pg_env, api_env, env, origin, verify, edge_ip, release, build, rollback_image=None):
    report = {'status': 'IN_PROGRESS', 'method': 'pg_basebackup stream WAL + pg_verifybackup; private physical/public volumes',
              'scope': 'Synthetic image cluster recovery; not a production backup or destructive rollback authorization'}
    started = time.monotonic()
    source_root = Path(__file__).resolve().parents[1]

    def helper(code, mounts, identity):
        # Root is limited to these owned copy mounts; no network or secrets env.
        owned['copy'] = command(['run', '--detach', '--name', names['copy'], '--label', 'mathstart.purpose=' + label,
            '--network', 'none', '--no-healthcheck', '--user', '0', *mounts, '--entrypoint', 'python', image, '-c', code])
        check(command(['wait', owned['copy']], timeout=180) == '0', identity)
        output = command(['logs', owned['copy']], log=identity + '.log')
        command(['rm', owned['copy']]); del owned['copy']
        return output

    def volume(name):
        # The UUID namespace is ours, but Docker volume create would otherwise
        # adopt an existing volume; inspect before creating and recording it.
        if command(['volume', 'ls', '--quiet', '--filter', 'name=^' + names[name] + '$']):
            raise RuntimeError('Recovery volume name already occupied')
        command(['volume', 'create', '--label', 'mathstart.purpose=' + label, names[name]])
        owned[name] = names[name]

    with engine.connect() as connection:
        staff = connection.execute(sa.select(User.id, User.username).where(User.is_superuser.is_(True))).one()
    # A real successful registration creates a receipt/bridge; retain a genuine
    # pending row as well. They are never serialized into logs or JSON reports.
    registration_password = uuid.uuid4().hex + '!Aa7'
    with httpx.Client(trust_env=False, follow_redirects=False, timeout=10, verify=verify) as client:
        token = client.get(origin + '/api/v1/auth/csrf/').json()['data']['csrf_token']
        response = client.post(origin + '/api/v1/auth/register/',
            json={'username': 'restore_' + uuid.uuid4().hex[:16], 'password': registration_password},
            headers={'Origin': origin, 'X-CSRFToken': token, 'Idempotency-Key': 'physical-' + uuid.uuid4().hex})
        check(response.status_code == 201, 'recovery_real_registration_receipt')
        revoked_cookie = dict(client.cookies)
    command(['stop', owned['edge']], timeout=30)
    command(['stop', owned['api']], timeout=30)
    command(['rm', owned['api']]); del owned['api']
    role = 'physical_legacy_' + uuid.uuid4().hex
    with UnitOfWork(engine) as uow:
        session = uow.session
        group = Group(name='Physical restore role ' + uuid.uuid4().hex)
        session.add(group); session.flush()
        session.execute(sa.insert(metadata.tables['auth_user_groups']).values(user_id=staff.id, group_id=group.id))
        permission = session.scalar(sa.select(metadata.tables['auth_permission'].c.id).order_by('id').limit(1))
        session.execute(sa.insert(metadata.tables['auth_group_permissions']).values(group_id=group.id, permission_id=permission))
        now = session.scalar(sa.select(sa.func.clock_timestamp()))
        session.add(IdentityReceipt(scope='anonymous:physical-pending', operation='register', key_digest='d' * 64,
                                   request_digest='e' * 64, expires_at=now + timedelta(days=1)))
        session.execute(sa.text('CREATE ROLE ' + role + ' NOLOGIN'))
        uow.commit()
    importer = CutoverImport(engine, (env['MATHSTART_HTTP_SIGNING_KEY'],), role)
    plan = importer.preview(uuid.uuid4())
    check(not importer.apply(plan)['repeated'], 'recovery_real_cutover_checkpoint')
    env.update(MATHSTART_IDENTITY_CUTOVER_DIGEST=plan['checkpoint_digest'], MATHSTART_LEGACY_WRITER_ROLE=role)
    api_env.write_text(''.join(k + '=' + v + '\n' for k, v in env.items()), encoding='utf-8', newline='\n')
    with engine.connect() as connection:
        before = source_digest(connection, env['MATHSTART_HTTP_SIGNING_KEY'], inventory(connection))
        fact = database_fact(connection)
        pending = connection.scalar(sa.select(sa.func.count()).select_from(IdentityReceipt).where(IdentityReceipt.status.is_(None)))
        check(pending >= 1, 'recovery_pending_receipt_present')
    engine.dispose()
    pg_uid = int(command(['exec', owned['db'], 'id', '-u', 'postgres']))
    pg_gid = int(command(['exec', owned['db'], 'id', '-g', 'postgres']))
    helper("import os; os.chown('/backup'," + str(pg_uid) + ',' + str(pg_gid) + "); os.chmod('/backup',0o700)",
           ['--mount', 'type=volume,source=' + names['backup'] + ',target=/backup'], 'backup_directory')
    backup_start = time.monotonic()
    command(['exec', '--user', 'postgres', owned['db'], 'pg_basebackup', '-U', engine.url.username,
             '-D', '/backup/cluster', '-X', 'stream', '--checkpoint=fast', '--manifest-checksums=SHA256'],
            timeout=180, log='pg-basebackup.log')
    check(True, 'actual_physical_basebackup_and_wal')
    command(['exec', '--user', 'postgres', owned['db'], 'pg_verifybackup', '/backup/cluster'],
            timeout=120, log='pg-verifybackup.log')
    check(True, 'actual_pg_verifybackup_manifest')
    # Back up the complete public tuple, including media embedded in immutable
    # inputs, compiled frontend and both manifests. No private env/key files.
    hash_code = "import hashlib,json,pathlib; p=pathlib.Path('/published'); print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.rglob('*')) if f.is_file()},sort_keys=True))"
    public_before = json.loads(helper(hash_code,
        ['--mount', 'type=volume,source=' + names['public'] + ',target=/published,readonly'], 'source_public_hashes'))
    helper("import shutil; shutil.copytree('/published','/backup/public')",
        ['--mount', 'type=volume,source=' + names['public'] + ',target=/published,readonly',
         '--mount', 'type=volume,source=' + names['backup'] + ',target=/backup'], 'backup_public_tuple')
    media_entries = json.loads((source_root / 'site_content/media.json').read_text(encoding='utf-8'))['assets']
    media_expected = {item['file']: item['sha256'] for item in media_entries}
    media_hash_code = hash_code.replace('/published', '/media')
    media_before = json.loads(helper(media_hash_code,
        ['--mount', 'type=bind,source=' + str(source_root / 'site_content/media') + ',target=/media,readonly'], 'source_media_hashes'))
    check(all(media_before.get(path) == digest for path, digest in media_expected.items()), 'backup_all29_manifest_media_and_other_existing_files')
    helper("import shutil; shutil.copytree('/media','/backup/media')",
        ['--mount', 'type=bind,source=' + str(source_root / 'site_content/media') + ',target=/media,readonly',
         '--mount', 'type=volume,source=' + names['backup'] + ',target=/backup'], 'backup_full_media_root')
    tuple_bytes = (json.dumps({'database_fact': fact, 'database_hmac': before,
        'public_files': public_before, 'media_files': media_before,
        'cutover_digest': plan['checkpoint_digest'], 'keys_retained_separately': True}, sort_keys=True) + '\n').encode()
    tuple_sha = sha256(tuple_bytes).hexdigest()
    # A site-sized manifest must not be embedded in argv (Windows has a32KiB
    # command-line bound). Copy the private explicit file through a read-only
    # mount; never pass rows or secrets through shell/command substitution.
    manifest_path = directory / 'backup-tuple.json'
    descriptor = os.open(manifest_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as output:
        output.write(tuple_bytes); output.flush(); os.fsync(output.fileno())
    helper("import os,shutil; shutil.copyfile('/tuple.json','/backup/tuple.json'); os.chmod('/backup/tuple.json',0o600); f=open('/backup/tuple.json','rb'); os.fsync(f.fileno()); f.close()",
        ['--mount', 'type=bind,source=' + str(manifest_path) + ',target=/tuple.json,readonly',
         '--mount', 'type=volume,source=' + names['backup'] + ',target=/backup'], 'backup_tuple_manifest')
    report['backup_seconds'] = round(time.monotonic() - backup_start, 3)
    command(['stop', owned['db']], timeout=30)
    command(['rm', owned['db']]); del owned['db']
    restore_start = time.monotonic()
    volume('restored-database'); volume('restored-public'); volume('restored-media')
    copy = "import os,shutil,hashlib; assert hashlib.sha256(open('/backup/tuple.json','rb').read()).hexdigest()==" + repr(tuple_sha) + "; "
    copy += "shutil.copytree('/backup/cluster','/database',dirs_exist_ok=True); shutil.copytree('/backup/public','/published',dirs_exist_ok=True); shutil.copytree('/backup/media','/media',dirs_exist_ok=True); "
    copy += "[(os.chown(p," + str(pg_uid) + ',' + str(pg_gid) + "),[os.chown(os.path.join(p,n)," + str(pg_uid) + ',' + str(pg_gid) + ") for n in ds+fs]) for p,ds,fs in os.walk('/database')]; "
    copy += "[(os.chown(p,10001,10001),[os.chown(os.path.join(p,n),10001,10001) for n in ds+fs]) for base in ('/published','/media') for p,ds,fs in os.walk(base)]"
    helper(copy, ['--mount', 'type=volume,source=' + names['backup'] + ',target=/backup,readonly',
        '--mount', 'type=volume,source=' + names['restored-database'] + ',target=/database',
        '--mount', 'type=volume,source=' + names['restored-public'] + ',target=/published',
        '--mount', 'type=volume,source=' + names['restored-media'] + ',target=/media'], 'restore_physical_public_media_volumes')
    public_after = json.loads(helper(hash_code,
        ['--mount', 'type=volume,source=' + names['restored-public'] + ',target=/published,readonly'], 'restored_public_hashes'))
    check(public_before == public_after and bool(public_before), 'restored_every_public_file_hash')
    report['public_files'] = len(public_after)
    media_after = json.loads(helper(media_hash_code,
        ['--mount', 'type=volume,source=' + names['restored-media'] + ',target=/media,readonly'], 'restored_media_hashes'))
    check(media_after == media_before, 'restore_every_media_file_exact_hash')
    report.update(media_files=len(media_after), manifest_media=len(media_expected), tuple_manifest_sha256=tuple_sha)
    owned['db'] = command(['run', '--detach', '--name', names['db'], '--label', 'mathstart.purpose=' + label,
        '--network', names['front'], '--publish', '127.0.0.1:' + str(engine.url.port) + ':5432',
        '--mount', 'type=volume,source=' + names['restored-database'] + ',target=/var/lib/postgresql/data',
        '--env-file', str(pg_env), PG_IMAGE])
    command(['network', 'connect', '--alias', names['db'], names['net'], owned['db']])
    for _ in range(60):
        try:
            with engine.connect() as connection:
                connection.execute(sa.text('SELECT 1'))
            break
        except sa.exc.OperationalError:
            time.sleep(.5)
    else:
        raise RuntimeError('Restored physical cluster did not become ready')
    with engine.connect() as connection:
        check(database_fact(connection) == fact, 'physical_restore_database_and_role_oids')
        check(source_digest(connection, env['MATHSTART_HTTP_SIGNING_KEY'], inventory(connection)) == before,
              'physical_restore_all_schema_rows_sequences_private_facts')
    def start_api(selected_image):
        owned['api'] = command(['run', '--detach', '--name', names['api'], '--label', 'mathstart.purpose=' + label,
        '--network', names['net'], '--network-alias', 'api', '--read-only', '--cap-drop', 'ALL',
        '--tmpfs', '/tmp:rw,nosuid,noexec,size=32m', '--env-file', str(api_env),
        '--mount', 'type=volume,source=' + names['restored-public'] + ',target=/runtime,readonly', selected_image,
        'python', '-m', 'uvicorn', 'backend.content.public_runtime:application', '--factory', '--host', '0.0.0.0',
        '--port', '8000', '--workers', '2', '--no-access-log', '--proxy-headers', '--forwarded-allow-ips', edge_ip])
    start_api(rollback_image or image)
    command(['start', owned['edge']])
    with httpx.Client(trust_env=False, follow_redirects=False, timeout=10, verify=verify) as client:
        for _ in range(60):
            try:
                response = client.get(origin + '/')
                if response.status_code == 200:
                    break
            except httpx.RequestError:
                pass
            time.sleep(.5)
        else:
            raise RuntimeError('Restored runtime did not become ready')
        check(response.content == (build / 'index.html').read_bytes(), 'restored_exact_compiled_html')
        check(client.get(origin + '/_content/index.json').content == release.index_raw, 'restored_exact_catalogue')
        with httpx.Client(trust_env=False, timeout=10, verify=verify, cookies=revoked_cookie) as old:
            check(old.get(origin + '/api/v1/users/me/').status_code == 401, 'restored_cutover_revoked_session_stays_revoked')

        def switch_api(selected_image):
            command(['stop', owned['edge']], timeout=30)
            command(['stop', owned['api']], timeout=30)
            command(['rm', owned['api']]); del owned['api']
            start_api(selected_image)
            command(['start', owned['edge']])  # Resolve the new API address.
            for _ in range(60):
                try:
                    ready = client.get(origin + '/')
                    if ready.status_code == 200 and ready.content == (build / 'index.html').read_bytes():
                        return
                except httpx.RequestError:
                    pass
                time.sleep(.5)
            raise RuntimeError('Compatible application switch did not become ready')

        if rollback_image:
            with engine.connect() as connection:
                check(source_digest(connection, env['MATHSTART_HTTP_SIGNING_KEY'], inventory(connection)) == before,
                      'prior_compatible_api_before_target_writes_keeps_entire_db')
            switch_api(image)
        token = client.get(origin + '/api/v1/auth/csrf/').json()['data']['csrf_token']
        # Password is the registered student's random value, never exposed.
        with engine.connect() as connection:
            username = connection.scalar(sa.select(User.username).where(User.is_superuser.is_(False)))
        login = client.post(origin + '/api/v1/auth/login/', json={'username': username, 'password': registration_password},
                            headers={'Origin': origin, 'X-CSRFToken': token})
        check(login.status_code == 200, 'restored_password_relogin_with_bound_cutover')
        check(client.get(origin + '/api/v1/users/me/').status_code == 200, 'restored_profile_and_opaque_session')
        check(importer.apply(plan)['repeated'], 'restored_checkpoint_retry_is_readonly')
        check(client.get(origin + '/api/v1/users/me/').status_code == 200, 'restored_checkpoint_retry_preserves_target_session')
        if rollback_image:
            request_ids = set()
            def account_snapshot(identity):
                response = client.get(origin + '/api/v1/users/me/')
                body = response.json()
                check(response.status_code == 200 and set(body) == {'data', 'meta'}
                      and set(body['meta']) == {'request_id', 'version'}
                      and body['meta']['version'] == 'http-v1', identity + '_exact_http_envelope')
                correlation = str(uuid.UUID(body['meta']['request_id']))
                check(correlation not in request_ids, identity + '_fresh_request_correlation')
                request_ids.add(correlation)
                return body['data']
            # HTTP request_id is intentionally new on every request. Compare
            # all persisted DTO fields, while separately enforcing correlation
            # and envelope invariants instead of expecting identical envelopes.
            account = account_snapshot('candidate_before_rollback')
            with engine.connect() as connection:
                written = source_digest(connection, env['MATHSTART_HTTP_SIGNING_KEY'], inventory(connection))
                check(written != before, 'actual_target_writes_before_application_rollback')
            switch_api(rollback_image)
            check(account_snapshot('prior_after_writes') == account, 'prior_api_after_target_writes_preserves_session_profile')
            with engine.connect() as connection:
                check(source_digest(connection, env['MATHSTART_HTTP_SIGNING_KEY'], inventory(connection)) == written,
                      'application_rollback_does_not_restore_or_change_db')
            switch_api(image)
            check(account_snapshot('candidate_after_return') == account, 'forward_application_return_preserves_target_session')
            report['application_rollback'] = {'status': 'PASS', 'prior_image': rollback_image,
                'candidate_image': image, 'database_retained': True, 'before_and_after_target_writes': True,
                'scope': 'Actual compatible API images on the same target head; not a schema downgrade or legacy DB snapshot rollback'}
        else:
            report['application_rollback'] = {'status': 'NOT_RUN', 'reason': 'Distinct prior compatible image not supplied'}
        report['restore_to_authenticated_ready_seconds'] = round(time.monotonic() - restore_start, 3)
        latencies = []
        paths = ('/', '/_content/index.json', '/api/v1/grades/', '/api/v1/users/me/')
        for _ in range(20):
            for path in paths:
                tick = time.monotonic()
                response = client.get(origin + path)
                check(response.status_code == 200, 'measured_restored_request_' + str(len(latencies)) + ':' + path)
                latencies.append((time.monotonic() - tick) * 1000)
        ordered = sorted(latencies)
        report['workload'] = {'requests': len(latencies), 'concurrency': 1, 'cycles': 20, 'paths': paths,
            'transport': origin.split(':', 1)[0], 'workers': 2, 'warm_after_restore': True,
            'p50_ms': round(statistics.median(latencies), 3), 'p95_ms': round(ordered[int(len(ordered) * .95) - 1], 3),
            'max_ms': round(max(latencies), 3), 'total_request_ms': round(sum(latencies), 3),
            'claim': 'Measured synthetic local workload only; no production capacity/SLO claim'}
        with engine.connect() as connection:
            readonly_before = source_digest(connection, env['MATHSTART_HTTP_SIGNING_KEY'], inventory(connection))
            seed_counts = {name: connection.scalar(sa.text('SELECT count(*) FROM ' + connection.dialect.identifier_preparer.quote(name)))
                           for name in inventory(connection)['tables']}
            database_version = connection.scalar(sa.text('SHOW server_version'))
        report['ordinary_api_workload'] = ordinary_api_workload(client, origin, verify)
        measured = report['ordinary_api_workload']
        measured['seed_rows'] = seed_counts
        measured['postgresql'] = database_version
        runtime = command(['exec', owned['api'], 'python', '-c',
            "import json,os,platform,importlib.metadata as m; print(json.dumps({'python':platform.python_version(),'platform':platform.platform(),'logical_cpus':os.cpu_count(),'memory_bytes':os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES'),'packages':{p:m.version(p) for p in ['fastapi','starlette','SQLAlchemy','psycopg','uvicorn']}}))"])
        measured['runtime'] = json.loads(runtime)
        measured['workers'] = 2
        with engine.connect() as connection:
            measured['all_rows_sequences_private_state_unchanged'] = (
                source_digest(connection, env['MATHSTART_HTTP_SIGNING_KEY'], inventory(connection)) == readonly_before)
        # Keep the actual distribution/failures even when its SLO assertion fails.
        with (directory / 'ordinary-api-workload.json').open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(measured, indent=2) + '\n')
        check(measured['requests'] == 400 and all(value['requests'] == 200 for value in measured['cohorts'].values()), 'ordinary_api_at_least200_each_cohort')
        check(measured['observed_peak_inflight'] == 10, 'ordinary_api_ten_real_concurrent_clients')
        check(measured['failures'] == 0 and measured['warmup_failures'] == 0, 'ordinary_api_failures_are_not_omitted')
        check(measured['unique_request_correlations'] == 400, 'ordinary_api_all_request_correlations_are_fresh')
        check(measured['p95_ms'] < 500 and all(value['p95_ms'] < 500 for value in measured['cohorts'].values()), 'ordinary_api_p95_below500ms_in_each_cohort')
        check(measured['all_rows_sequences_private_state_unchanged'],
              'ordinary_api_benchmark_preserves_all_rows_sequences_private_state')
    check(command(['exec', owned['api'], 'python', '-m', 'backend.health']) == 'READY', 'restored_actual_readiness')
    report.update(status='PASS', retained_input_hmac=before, elapsed_seconds=round(time.monotonic() - started, 3),
                  rollback_policy='No older snapshot restore after target writes; preserve current DB and forward recover or use a proven schema-compatible application')
    return report
