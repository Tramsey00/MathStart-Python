"""Read-only development projection with byte-keyed local reuse.

Publication, database mutation and runtime validation remain with Content.
The cache only avoids reinterpreting identical inputs on repeated dev startup.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def fingerprint(settings, descriptor):
    from backend.content.releases import inside
    release = inside(settings['MATHSTART_RELEASE_ROOT'], descriptor.release_id)
    files = list(release.rglob('*'))
    for folder in ('backend', 'scripts'):
        files.extend((ROOT / folder).rglob('*.py'))
    files.extend((ROOT / 'frontend').glob('*.py'))
    files.extend((ROOT / 'specs').rglob('*.json'))
    for folder in ('backend',):
        files.extend((ROOT / folder).rglob('requirements*.txt'))
        files.extend((ROOT / folder).rglob('requirements*.lock'))
    files.extend(ROOT.glob('requirements*.txt'))
    files.extend(ROOT.glob('requirements*.lock'))
    # Include concrete locations, configuration and interpreter, never store secrets.
    digest = sha256(json.dumps([settings, str(ROOT), sys.version,
        str(descriptor)], sort_keys=True).encode())
    for path in sorted(set(files)):
        if not path.is_file():
            continue
        digest.update(str(path.resolve()).encode())
        digest.update(b'\0')
        digest.update(sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def reusable(output, key):
    try:
        cache = json.loads(output.with_suffix('.cache.json').read_text(encoding='utf-8'))
        return cache['key'] == key and cache['sha256'] == sha256(output.read_bytes()).hexdigest()
    except (OSError, ValueError, KeyError, TypeError):
        return False


def prepare_view(settings, output):
    from sqlalchemy.engine import make_url
    from backend.infrastructure.database import DatabaseConfig, create_engine
    from backend.infrastructure.uow import UnitOfWork
    from backend.content.releases import active_descriptor
    from backend.content.public_runtime import artifact_for_descriptor
    from frontend.prepare_public import prepare

    config = DatabaseConfig(make_url(settings['MATHSTART_DATABASE_URL']))
    if config.url.drivername != 'postgresql+psycopg':
        raise ValueError('Target PostgreSQL configuration required')
    engine = create_engine(config)
    try:
        with UnitOfWork(engine) as uow:
            import sqlalchemy as sa
            uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
            descriptor = active_descriptor(uow, 'public')
        _, manifest = artifact_for_descriptor(settings['MATHSTART_PUBLIC_ARTIFACT_ROOT'],
            json.loads(settings['MATHSTART_PUBLIC_ARTIFACT_DIGESTS']), descriptor)
        key = fingerprint(settings, descriptor)
        if reusable(output, key):
            print('Dev projection: reused unchanged inputs', flush=True)
            return
        prepare(settings['MATHSTART_RELEASE_ROOT'], descriptor.release_id, descriptor.manifest_digest,
            settings['MATHSTART_PUBLIC_ORIGIN'], output, manifest['input_receipt_digest'])
    finally:
        engine.dispose()
    data = json.loads(output.read_text(encoding='utf-8'))
    legacy = [path for path, view in data['routes'].items()
              if not view.get('public_design') and view['page'].get('renderer_version') != 'react-v1']
    data['backend_paths'] = sorted(set(legacy + [r['old_path'] for r in manifest['redirects']]
        + ['/glavnaya/', '/sitemap.xml', '/robots.txt', '/favicon.ico']))
    curriculum = (ROOT / 'curriculum').resolve()
    paths = []
    for view in data['routes'].values():
        if view['page'].get('renderer_version') != 'react-v1':
            continue
        source = (ROOT / view['page']['source']['path']).resolve()
        if not source.is_relative_to(curriculum) or source.name != 'lesson.json':
            raise ValueError('Development content path escaped curriculum')
        paths.append(str(source.with_name('content.json')))
    data['dev_content_paths'] = sorted(set(paths))
    output.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    # Do not stamp a projection if its inputs changed while it was being built.
    if fingerprint(settings, descriptor) != key:
        raise RuntimeError('Development inputs changed during preparation; retry startup')
    stamp = output.with_suffix('.cache.json')
    pending = stamp.with_suffix('.tmp')
    pending.write_text(json.dumps({'key': key,
        'sha256': sha256(output.read_bytes()).hexdigest()}), encoding='utf-8')
    pending.replace(stamp)
