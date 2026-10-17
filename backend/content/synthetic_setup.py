"""Guarded initial I02/I03 synthetic setup; not a general publication writer."""
import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import secrets
import sys
import uuid

import sqlalchemy as sa

from backend.content.bootstrap import bootstrap_sources
from backend.content.build import write_build_inputs, verify_build_inputs, encoded
from backend.content.sources import read_json
from backend.content.public_runtime import session_digest, user_auth_hash, artifact_for, artifact_bytes
from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.infrastructure.uow import UnitOfWork
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.http.transport import timestamp
from backend.models.baseline import User, Group, MediaAsset, ContentPage, metadata
from backend.models.protocol import TargetSession, journal, gate, active
from backend.migrations.upgrade import fresh, require_disposable


def prepare(engine, source_root, runtime_root, release_id, source_sha, key):
    with engine.begin() as connection:
        name = connection.scalar(sa.text('SELECT current_database()'))
        major = int(connection.scalar(sa.text('SHOW server_version_num'))) // 10000
        if major < 16 or not name.startswith('test_ms7_mig_v01_') or sa.inspect(connection).get_table_names():
            raise RuntimeError('Only an empty explicitly reserved synthetic V01 database is allowed')
        connection.execute(sa.text('COMMENT ON DATABASE ' + connection.dialect.identifier_preparer.quote(name)
                            + " IS 'MS7-MIG-V01 disposable synthetic test database'"))
        fresh(connection)
    before = None
    for _ in range(2):
        with UnitOfWork(engine) as uow:
            bootstrap_sources(uow.session, source_root)
            current = list(uow.session.execute(sa.select(ContentPage.id, ContentPage.slug, ContentPage.created_at,
                    ContentPage.updated_at, ContentPage.body_html).order_by(ContentPage.id)))
            if before is not None and current != before:
                raise RuntimeError('Repeated bootstrap changed the source edition')
            before = current
            uow.commit()
    token = secrets.token_urlsafe(32)
    with UnitOfWork(engine) as uow:
        now = uow.session.scalar(sa.select(sa.func.clock_timestamp()))
        from backend.users.bootstrap import seed_permissions
        seed_permissions(uow.session)
        staff = User(username='synthetic-read-staff', password='!synthetic-unusable', is_staff=True,
                     is_active=True, is_superuser=True)
        uow.session.add_all([staff, Group(name='Synthetic read group')])
        uow.session.flush()
        uow.session.add(TargetSession(id=uuid.uuid4(), lineage_id=uuid.uuid4(),
                    token_digest=session_digest(token, key), user_id=staff.id,
                    auth_hash=user_auth_hash(staff.password, key), revocation_epoch=0,
                    created_at=now, expires_at=now + timedelta(days=1), revoked_at=None))
        pages = {row.slug: row.id for row in uow.session.scalars(sa.select(ContentPage))}
        for asset in read_json(source_root / 'site_content/media.json')['assets']:
            uow.session.add(MediaAsset(title=asset['title'], file=asset['file'], alt_text=asset['alt_text'],
                                      related_page_id=pages.get(asset['related_page'])))
        uow.commit()
    with UnitOfWork(engine) as uow:
        uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
        descriptor, receipt = write_build_inputs(uow, source_root, runtime_root / 'releases', release_id, source_sha)
    cookies = {'cookies': [{'name': 'sessionid', 'value': token, 'url': os.environ['MATHSTART_PUBLIC_ORIGIN'],
                           'httpOnly': True, 'secure': os.environ['MATHSTART_PUBLIC_ORIGIN'].startswith('https:'),
                           'sameSite': 'Lax'}]}
    runtime_root.mkdir(parents=True, exist_ok=True)
    private = runtime_root / 'private-staff-cookie.json'
    private.write_bytes(encoded(cookies))
    public = {k: v for k, v in receipt.items() if k not in {'files', 'source_files'}}
    public['receipt_digest'] = sha256((runtime_root / 'releases' / release_id / 'receipt.json').read_bytes()).hexdigest()
    public['private_cookie_file'] = str(private)
    public['input_root'] = str(runtime_root / 'releases')
    (runtime_root / 'prepare-result.json').write_bytes(encoded(public))
    return public


def activate_initial(engine, release_root, release_id, receipt_digest, artifact_root, artifact_digest, origin):
    release = verify_build_inputs(release_root, release_id, receipt_digest)
    root, manifest = artifact_for(artifact_root, {release_id: artifact_digest}, release)
    if manifest['origin'] != origin or manifest['input_receipt_digest'] != receipt_digest:
        raise RuntimeError('Artifact origin mismatch')
    for item in manifest['files']:
        artifact_bytes(root, manifest, item['path'])
    if set(manifest['page_ids']) != {str(pk) for pk in release.pages}:
        raise RuntimeError('Incomplete frontend page coverage')
    canonical = {page['seo']['canonical_path'] for page in release.pages.values()}
    public_urls = canonical | {a['url'] for a in release.index['aliases']} | set(release.index['system_urls'])
    if (set(manifest['public_urls']) != public_urls or set(manifest['page_semantic_digests']) != canonical
            or manifest['redirects'] != release.index['redirects'] or manifest['private_exports'] != []):
        raise RuntimeError('Frontend public coverage mismatch')
    from frontend.rendering import PublicRenderer
    renderer = PublicRenderer(artifact_root, {release_id: artifact_digest})
    for page in release.pages.values():
        html = renderer(page, release.renderer_context(page, {}), origin + page['seo']['canonical_path'])
        if page['body_html'] not in html:
            raise RuntimeError('Incomplete frontend authored HTML')
    with engine.begin() as c:
        require_disposable(c)
        # Initial fixture only: never replace a real or preexisting authority.
        for table in (gate, journal, active):
            c.execute(sa.text('LOCK TABLE ' + table.name + ' IN ACCESS EXCLUSIVE MODE'))
            if c.scalar(sa.select(sa.func.count()).select_from(table)):
                raise RuntimeError('Initial synthetic activation requires empty publication authority')
        pages = {r.id: r for r in c.execute(sa.select(metadata.tables['content_contentpage']).where(
            metadata.tables['content_contentpage'].c.is_published.is_(True)))}
        if set(pages) != set(release.pages):
            raise RuntimeError('DB/public page coverage mismatch')
        for pk, delivery in release.pages.items():
            row = pages[pk]
            if any(getattr(row, k) != delivery[k] for k in ['slug', 'title', 'page_type', 'body_html',
                    'grade_id', 'subject_id', 'section_id', 'order']):
                raise RuntimeError('DB/public edition mismatch')
            if any(timestamp(getattr(row, k)) != delivery[k] for k in ['created_at', 'updated_at']):
                raise RuntimeError('DB/public timestamp mismatch')
        now = c.scalar(sa.select(sa.func.clock_timestamp()))
        operation, owner = uuid.uuid4(), uuid.uuid4()
        c.execute(sa.insert(journal).values(id=operation, namespace='public', key_digest=sha256(release_id.encode()).hexdigest(),
                  plan_digest=sha256(encoded({'kind': 'initial-synthetic-i02-i03', 'manifest': release.descriptor.manifest_digest})).hexdigest(),
                  plan={'kind': 'initial-synthetic-i02-i03', 'input_receipt_digest': receipt_digest,
                        'output_manifest_digest': artifact_digest},
                  release_id=release_id, manifest_digest=release.descriptor.manifest_digest, owner_id=owner,
                  fence_generation=1, lease_until=now, phase='COMPLETE', db_committed=True,
                  activation_status='APPLIED', created_at=now, updated_at=now))
        c.execute(sa.insert(gate).values(namespace='public', fence_generation=1))
        c.execute(sa.insert(active).values(namespace='public', operation_id=operation, release_id=release_id,
                                         manifest_digest=release.descriptor.manifest_digest, fence_generation=1))
    return {'release_id': release_id, 'activation': 'INITIAL_SYNTHETIC_ONLY', 'pages': len(release.pages),
            'manifest_digest': release.descriptor.manifest_digest, 'output_digest': artifact_digest}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'activate-initial'])
    parser.add_argument('--disposable', action='store_true', required=True)
    parser.add_argument('--source-root', type=Path, default=Path('.'))
    parser.add_argument('--runtime-root', type=Path, required=True)
    parser.add_argument('--source-sha')
    parser.add_argument('--release-id', required=True)
    parser.add_argument('--receipt-digest')
    parser.add_argument('--artifact-root', type=Path)
    parser.add_argument('--artifact-digest')
    args = parser.parse_args(argv)
    engine = None
    try:
        if os.environ.get('MATHSTART_DISPOSABLE') != '1':
            raise RuntimeError('Explicit disposable environment required')
        if not re.fullmatch(r'https?://[A-Za-z0-9.-]+(?::[0-9]+)?', os.environ['MATHSTART_PUBLIC_ORIGIN']):
            raise RuntimeError('Explicit trusted public origin required')
        root = args.runtime_root.resolve()
        if not root.is_relative_to(Path('var').resolve()):
            raise RuntimeError('Synthetic output must stay under this checkout var/')
        engine = create_engine(DatabaseConfig.from_environment())
        if engine.dialect.name != 'postgresql':
            raise RuntimeError('PostgreSQL16 required')
        if args.action == 'prepare':
            if not args.source_sha:
                raise RuntimeError('Reviewed source commit required')
            result = prepare(engine, args.source_root.resolve(), root, args.release_id, args.source_sha,
                             os.environ['MATHSTART_HTTP_SIGNING_KEY'])
        else:
            if not args.artifact_root or not args.artifact_digest or not args.receipt_digest:
                raise RuntimeError('Trusted input and output artifact identities required')
            result = activate_initial(engine, root / 'releases', args.release_id, args.receipt_digest,
                        args.artifact_root, args.artifact_digest, os.environ['MATHSTART_PUBLIC_ORIGIN'])
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as error:
        print('Synthetic setup refused/failed: ' + type(error).__name__, file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
