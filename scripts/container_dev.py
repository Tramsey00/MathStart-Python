"""Container-only local orchestration around the existing schema/Content CLIs.

The PowerShell entry point owns Compose. This process never calls Docker or Git
mutation commands. Exit 42 means a concrete immutable plan awaits human review.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import team_local as team

LOCAL = ROOT / 'var/compose'
STATE = LOCAL / 'state.json'
PRIVATE = LOCAL / 'api-env.json'
SCHEMA = LOCAL / 'schema-env.json'
SECRETS = LOCAL / 'secrets.json'
REVIEW = LOCAL / 'review.json'
SERVING = Path('/runtime/serving')


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


@contextmanager
def exclusive():
    import fcntl
    # This is an advisory process lock in the Linux-owned runtime volume, not a
    # Windows bind mount. An interrupted command cannot strand a lock file.
    with Path('/runtime/operator.lock').open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def git(*arguments):
    result = subprocess.run(['git', '-c', 'safe.directory=' + str(ROOT), *arguments], cwd=ROOT,
                            capture_output=True, check=True, timeout=180)
    return result.stdout.decode('utf-8').strip()


def fingerprint(paths):
    names = git('ls-files', '-z', '--', *paths).split('\0')
    rows = {}
    for name in names:
        if name and not name.startswith(('frontend/tests/', 'frontend/e2e/', 'frontend/prototypes/')):
            path = ROOT / name
            rows[name] = sha256(path.read_bytes()).hexdigest()
    return sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def dependency_digest():
    return fingerprint(['frontend/package.json', 'frontend/package-lock.json'])


def migration_files():
    return {name: sha256((ROOT / name).read_bytes()).hexdigest()
            for name in git('ls-files', '-z', '--', 'backend/migrations/versions').split('\0') if name}


def content_digest():
    return fingerprint(['curriculum', 'site_content', 'static', 'frontend/src',
        'frontend/public_design.py', 'frontend/rendering.py', 'frontend/build_public.py',
        'frontend/build_input.py', 'frontend/prepare_public.py', 'frontend/vite.config.ts',
        'frontend/react-router.config.ts', 'frontend/package.json', 'frontend/package-lock.json',
        'frontend/scripts/production-boundary.mjs', 'frontend/scripts/shell-reference.mjs',
        'backend/content', 'backend/models', 'backend/infrastructure/http/contracts.py',
        'backend/infrastructure/http/transport.py', 'requirements.lock',
        'backend/requirements.lock', 'backend/infrastructure/http/requirements.lock',
        'deploy/Dockerfile', '.dockerignore',
        'specs/migration/r02-v1'])


def configure():
    if PRIVATE.exists() or SCHEMA.exists() or SECRETS.exists():
        if not all(path.exists() for path in (PRIVATE, SCHEMA, SECRETS, STATE)):
            raise RuntimeError('Partial private configuration; inspect it instead of regenerating credentials')
        return read(STATE)
    import psycopg
    from psycopg import sql
    passwords = {key: secrets.token_urlsafe(36) for key in ('schema', 'runtime')}
    passwords['admin'] = os.environ['POSTGRES_PASSWORD']
    # Only the new Compose DB is addressed; no host DB or external env fallback.
    with psycopg.connect(host='db', dbname='mathstart_dev', user='local_admin',
                        password=passwords['admin'], autocommit=True) as connection:
        if connection.execute("SELECT EXISTS(SELECT 1 FROM pg_tables WHERE schemaname='public')").fetchone()[0]:
            raise RuntimeError('Unowned/nonempty DB: refusing initial setup')
        for role, key in (('local_schema', 'schema'), ('local_runtime', 'runtime')):
            connection.execute(sql.SQL('CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD {}')
                .format(sql.Identifier(role), sql.Literal(passwords[key])))
        connection.execute('ALTER DATABASE mathstart_dev OWNER TO local_schema')
        connection.execute('REVOKE CREATE ON SCHEMA public FROM PUBLIC')
        connection.execute('GRANT USAGE, CREATE ON SCHEMA public TO local_schema')
        connection.execute('GRANT USAGE ON SCHEMA public TO local_runtime')
    values = {'MATHSTART_DB_BACKEND': 'postgresql',
        'MATHSTART_DATABASE_URL': 'postgresql+psycopg://local_runtime:' + passwords['runtime'] + '@db:5432/mathstart_dev',
        'MATHSTART_HTTP_SIGNING_KEY': secrets.token_urlsafe(48),
        'MATHSTART_PUBLIC_ORIGIN': 'http://127.0.0.1:8131',
        'MATHSTART_RELEASE_ROOT': str(SERVING / 'releases'),
        'MATHSTART_PUBLIC_ARTIFACT_ROOT': str(SERVING / 'frontend'),
        'MATHSTART_PUBLIC_ARTIFACT_DIGESTS': '{}'}
    save(SECRETS, {'passwords': passwords})
    save(PRIVATE, values)
    save(SCHEMA, {**values,
        'MATHSTART_DATABASE_URL': 'postgresql+psycopg://local_schema:' + passwords['schema'] + '@db:5432/mathstart_dev',
        'MATHSTART_SCHEMA_SIGNING_KEY': secrets.token_urlsafe(48)})
    state = {'version': 1, 'schema_code': None, 'content_digest': None,
             'release': None, 'work': None}
    save(STATE, state)
    print('Own schema/runtime roles and private configuration created. No users or Content seeded.', flush=True)
    return state


def work_directory(state, key):
    if state.get('work') and state['work']['key'] == key:
        return Path(state['work']['path'])
    work = Path('/runtime/work') / uuid.uuid4().hex
    work.mkdir(parents=True)
    logs = LOCAL / 'logs' / work.name
    logs.mkdir(parents=True)
    (work / 'logs').symlink_to(logs, target_is_directory=True)
    state['work'] = {'key': key, 'path': str(work), 'release': 'dev-' + work.name[:16],
                     'publisher': str(uuid.uuid4())}
    save(STATE, state)
    return work


def require_review(kind, path, digest, summary):
    directory = LOCAL / 'plans' / path.parent.name
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / path.name
    if not destination.exists():
        shutil.copyfile(path, destination)
    elif destination.read_bytes() != path.read_bytes():
        raise RuntimeError('Review copy changed; refusing overwrite')
    save(REVIEW, {'kind': kind, 'digest': digest,
        'path': str(destination.relative_to(ROOT)), 'summary': summary})
    print(json.dumps(read(REVIEW), ensure_ascii=False), flush=True)
    return 42


def prepare(args):
    from backend.release_migrate import code_digest as schema_code, plan_digest
    from backend.content.participant import digest as plan_hash
    state = configure()
    dependencies = dependency_digest()
    marker = ROOT / 'frontend/node_modules/.mathstart-lock'
    if not marker.exists() or marker.read_text() != dependencies:
        print('Installing frontend dependencies from package-lock inside the container.', flush=True)
        log = LOCAL / 'logs'
        log.mkdir(exist_ok=True)
        with team.installation_paths(LOCAL, PRIVATE, SECRETS, SERVING):
            team.run(['npm', '--prefix', 'frontend', 'ci', '--no-audit', '--no-fund', '--maxsockets=1'], 'npm-ci', timeout=900)
        marker.write_text(dependencies)
    else:
        print('Dependency locks unchanged; npm ci skipped.', flush=True)
    current_schema = schema_code()
    current_migrations = migration_files()
    applied = state.get('applied_migrations')
    if applied is not None and any(current_migrations.get(name) != digest for name, digest in applied.items()):
        raise RuntimeError('Applied migration file changed or disappeared; history is never rewritten by update')
    if state['schema_code'] == current_schema and applied is None:
        # Adoption of this metadata-only safeguard is safe only when the exact
        # previously checked schema code digest is still identical.
        state['applied_migrations'] = current_migrations
        save(STATE, state)
    content = content_digest()
    work = work_directory(state, current_schema + ':' + content)
    values = read(SCHEMA)
    with team.installation_paths(work, PRIVATE, SECRETS, SERVING):
        if state['schema_code'] is None:
            plan_path = work / 'schema.json'
            if not plan_path.exists():
                team.cli('backend.release_migrate', ['preview', '--profile', 'FRESH', '--plan-file', str(plan_path)], 'schema-preview', values)
            plan = read(plan_path)
            digest = plan_digest(plan)
            if datetime.now(timezone.utc) >= datetime.fromisoformat(plan['expires_at']):
                # No apply was attempted in this branch. Retain the old plan,
                # create a fresh preview, and require its new digest explicitly.
                state['work'] = None
                save(STATE, state)
                args.schema_digest = None
                print('Unapplied schema preview expired; retaining it and generating a new review plan.', flush=True)
                return prepare(args)
            if args.schema_digest != digest:
                return require_review('schema', plan_path, digest, {key: plan[key] for key in
                    ('profile', 'target_head', 'database', 'table_count', 'expires_at')})
            team.schema_apply(values, digest)
            state['schema_code'] = current_schema
            state['applied_migrations'] = current_migrations
            save(STATE, state)
        elif state['schema_code'] != current_schema:
            # The current canonical chain has only v01_0001/v01_0002 and its
            # release CLI explicitly rejects unknown revisions. Never fall back
            # to fresh/stamp or unreviewed Alembic on an existing local DB.
            team.cli('backend.release_migrate', ['check'], 'schema-existing-check', values)
            state['schema_code'] = current_schema
            save(STATE, state)
            print('Schema code changed; existing physical schema checked compatible. No DDL required.', flush=True)
        else:
            print('Schema inputs unchanged; schema preparation skipped.', flush=True)
        if state['content_digest'] == content:
            status = json.loads(team.cli('backend.content.publish', ['status'], 'unchanged-status', values))
            if status['operation'] or not status['active'] or status['active']['release_id'] != state['release']:
                raise RuntimeError('Publication authority differs from saved completed installation; operator recovery required')
            print('Content/build inputs unchanged; prepare/build/publication skipped.', flush=True)
            REVIEW.unlink(missing_ok=True)
            return 0
        status = json.loads(team.cli('backend.content.publish', ['status'], 'before-content-status', values))
        if status['operation']:
            raise RuntimeError('Pending publication retained. Use reviewed normal status/recovery; no automatic domain replay')
        plan_path = work / 'publication.json'
        operation = state['work']
        if not plan_path.exists():
            dirty = git('status', '--porcelain', '--', 'curriculum', 'site_content', 'static', 'frontend', 'backend')
            if dirty:
                raise RuntimeError('Commit source/build input changes before explicit publication. Dirty files are preserved; ordinary dev/HMR remains available')
            # team.environment deliberately strips inherited MATHSTART_*.
            # Pass this build-only path explicitly; Router deletes its output
            # directory, so it must be below (never the root of) a volume.
            team.content({**values, 'MATHSTART_ROUTER_BUILD': '/runtime/router-build'}, operation)
        plan = read(plan_path)
        digest = plan_hash(plan)
        if args.content_digest != digest:
            from collections import Counter
            summary = {'release': plan['release_id'], 'origin': plan['origin'], 'previous': plan['previous'],
                'changes_by_table': dict(Counter(row['table'] for row in plan['changes'])),
                'input_manifest_digest': plan['manifest_digest'], 'output_manifest_digest': plan['output_manifest_digest']}
            return require_review('content', plan_path, digest, summary)
        team.publish(values, operation, digest)
        state.update(content_digest=content, release=operation['release'])
        save(STATE, state)
        REVIEW.unlink(missing_ok=True)
        print('Local environment prepared; credentials and existing DB rows retained.', flush=True)
    return 0


def ready():
    if not all(path.exists() for path in (STATE, PRIVATE, SCHEMA)):
        raise RuntimeError('Run dev.cmd prepare first')
    state = read(STATE)
    if REVIEW.exists():
        raise RuntimeError('A concrete plan still awaits review; complete prepare/update before start')
    marker = ROOT / 'frontend/node_modules/.mathstart-lock'
    if not state.get('release') or not marker.exists() or marker.read_text() != dependency_digest():
        raise RuntimeError('Preparation/dependency update required; startup never installs dependencies or Content')
    print('Prepared local runtime found. No DDL/seed/publication performed.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'ready', 'serve'])
    parser.add_argument('--schema-digest')
    parser.add_argument('--content-digest')
    args = parser.parse_args()
    os.chdir(ROOT)
    try:
        if os.environ.get('MATHSTART_CONTAINER_DEV') != '1' or str(ROOT) != '/workspace':
            raise RuntimeError('Use the checkout dev.ps1 entry point; this command runs only in its dev container')
        if args.action == 'serve':
            ready()
            # The existing supervisor keeps the API private and strips private
            # MATHSTART values from its Vite child. Only the container bind differs.
            os.execv(sys.executable, [sys.executable, str(ROOT / 'scripts/dev_server.py'),
                '--container', '--env-file', str(PRIVATE)])
        elif args.action == 'ready':
            ready()
            return 0
        with exclusive():
            return prepare(args)
    except Exception as error:
        message = str(error) if type(error) is RuntimeError else type(error).__name__
        print('CONTAINER_DEV_STOPPED: ' + message + '; data/credentials/plans retained.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
