"""Write and verify immutable, public-only publisher build inputs.

The operator supplies a reviewed source checkout; HTTP callers cannot attest
trust or select files. No active descriptor or publication state is changed.
"""
from hashlib import sha256
import json
from pathlib import Path
import re
import uuid

import sqlalchemy as sa

from backend.content.sources import SourceError, file_inside, load_sources, read_json
from backend.content.projection import ReviewedSource, delivery_candidate, build_index_candidate
from backend.content.releases import Descriptor, ReleaseStore, safe_public_path, inside
from backend.models.baseline import ContentPage


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def verify_build_inputs(root, release_id, receipt_digest):
    """Verify the trusted handoff receipt before any build consumer reads DTOs."""
    base = inside(root, release_id)
    raw = (base / 'receipt.json').read_bytes()
    if sha256(raw).hexdigest() != receipt_digest:
        raise SourceError('Build receipt integrity mismatch')
    receipt = read_json(base / 'receipt.json')
    if receipt['release_id'] != release_id or receipt['activation'] != 'NOT_PERFORMED':
        raise SourceError('Build receipt identity mismatch')
    paths = set()
    for entry in receipt['files']:
        path = entry['path']
        if path in paths:
            raise SourceError('Duplicate artifact path')
        paths.add(path)
        payload = inside(base, path).read_bytes()
        if type(entry['size']) is not int or len(payload) != entry['size'] or sha256(payload).hexdigest() != entry['sha256']:
            raise SourceError('Build artifact integrity mismatch')
    if {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()} != paths | {'receipt.json'}:
        raise SourceError('Unlisted build artifact')
    descriptor = Descriptor(uuid.UUID(int=0), release_id, receipt['manifest_digest'], 1)
    release = ReleaseStore(root).load(descriptor)
    required = {'index.json'} | {f'pages/{pk}.json' for pk in release.pages} | {a['storage_key'] for a, _ in release.assets.values()}
    if paths != required or len(release.pages) != receipt['pages'] or len(release.assets) != receipt['assets']:
        raise SourceError('Build inventory coverage mismatch')
    return release


def assets_for(root, bundle):
    page = bundle.snapshot
    css = ['site.css', 'lesson.css', 'lesson-math.css', 'lesson-components.css', 'lesson-diagrams.css', 'lesson-contents.css']
    scripts = ['lesson-diagrams.js']
    if page['page_type'] != 'topic':
        css.append('site-pages.css')
    if page['slug'] == 'karta-sajta':
        css += ['ui/tokens.css', 'catalogue.css']
    if page['slug'] in {'glavnaya', 'o-proekte', 'kontakty'}:
        css.append('ui/tokens.css')
    if 'data-lesson-widget="power-functions"' in page['body_html']:
        css.append('widgets/power-functions.css')
    elif 'ms-graph-layout' in page['body_html']:
        css.append('widgets/function-graphs.css')
    rows = []
    for item in css:
        path = 'static/mathstart/css/' + item
        rows.append((path, '/' + path, 'style', file_inside(root, path).read_bytes()))
    if page['page_css']:
        path = f'static/mathstart/pages/{page["slug"]}/page.css'
        rows.append((path, '/' + path, 'style', page['page_css'].encode('utf-8')))
    for item in scripts:
        path = 'static/mathstart/js/' + item
        rows.append((path, '/' + path, 'script', file_inside(root, path).read_bytes()))
    if page['page_js']:
        path = f'static/mathstart/pages/{page["slug"]}/page.js'
        rows.append((path, '/' + path, 'script', page['page_js'].encode('utf-8')))
    scripts = ['lesson-navigation.js']
    if 'data-lesson-widget="power-functions"' in page['body_html']:
        scripts += ['math.js', 'widgets/power-functions.js']
    for item in scripts:
        path = 'static/mathstart/js/' + item
        rows.append((path, '/' + path, 'script', file_inside(root, path).read_bytes()))
    # Authored direct asset references are reviewed source bytes, never client input.
    urls = set(re.findall(r'''(?:src|href)\s*=\s*["']((?:/static/|/media/)[^"'?#]+)''', page['body_html']))
    urls.update(re.findall(r'''url\(\s*["']?((?:/static/|/media/)[^\s)"'?#]+)''', page['page_css']))
    known = {r[1] for r in rows}
    for url in sorted(urls - known):
        if not safe_public_path(url) or Path(url).suffix.lower() not in {'.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.pdf'}:
            raise SourceError('Unsupported reviewed asset')
        key = url.lstrip('/')
        suffix = Path(key).suffix.lower()
        kind = 'style' if suffix == '.css' else 'script' if suffix == '.js' else 'media'
        if url.startswith('/media/'):
            manifest = read_json(root / 'site_content/media.json')
            entry = next((a for a in manifest['assets'] if '/media/' + a['file'] == url), None)
            if entry is None:
                raise SourceError('Media is absent from reviewed seed manifest')
            raw = file_inside(root, 'site_content/' + key).read_bytes()
            if sha256(raw).hexdigest() != entry['sha256']:
                raise SourceError('Seed media hash mismatch')
        else:
            raw = file_inside(root, key).read_bytes()
        rows.append((key, url, kind, raw))
    return [({'storage_key': key, 'url': url, 'kind': kind, 'sha256': sha256(raw).hexdigest(),
              'order': order, 'lifecycle': 'full_document' if kind == 'script' else 'none'}, raw)
            for order, (key, url, kind, raw) in enumerate(rows)]


def write_build_inputs(uow, source_root, output_root, release_id, source_sha):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,120}', release_id) or not re.fullmatch(r'[a-f0-9]{40}', source_sha):
        raise SourceError('Explicit release identity and source commit required')
    source_root, output_root = Path(source_root).resolve(), Path(output_root).resolve()
    target = output_root / release_id
    if target.exists():
        raise SourceError('Immutable release already exists')
    bundles = {b.snapshot['slug']: b for b in load_sources(source_root)}
    pages = list(uow.session.scalars(sa.select(ContentPage).where(ContentPage.is_published.is_(True)).order_by(ContentPage.id)))
    deliveries, files = {}, {}
    for page in pages:
        bundle = bundles.get(page.slug)
        if bundle is None or any(getattr(page, k) != bundle.snapshot[k] for k in
                ['slug', 'page_type', 'title', 'order', 'seo_title', 'seo_description', 'body_html', 'page_css', 'page_js', 'is_published']):
            raise SourceError('Published DB edition differs from reviewed source; explicit publication required')
        assets = assets_for(source_root, bundle)
        for asset, raw in assets:
            previous = files.setdefault(asset['storage_key'], raw)
            if previous != raw:
                raise SourceError('Asset identity conflict')
        reviewed = ReviewedSource(bundle.path, bundle.source_digest, tuple(a for a, _ in assets))
        deliveries[page.id] = delivery_candidate(uow, page.slug, reviewed)
        files[f'pages/{page.id}.json'] = encoded(deliveries[page.id])
    index = build_index_candidate(uow, release_id, deliveries)
    files['index.json'] = encoded(index)
    descriptor = Descriptor(uuid.uuid4(), release_id, sha256(files['index.json']).hexdigest(), 1)
    inventory = [{'path': path, 'sha256': sha256(raw).hexdigest(), 'size': len(raw)} for path, raw in sorted(files.items())]
    receipt = {'version': 'build-input-receipt-v1', 'source_sha': source_sha, 'release_id': release_id,
               'manifest_digest': descriptor.manifest_digest, 'pages': len(pages),
               'topics': len(index['catalogue']['topics']), 'assets': len(files) - len(pages) - 1,
               'files': inventory, 'source_files': [f for b in bundles.values() for f in b.files],
               'activation': 'NOT_PERFORMED'}
    # Stage under the same filesystem; verification precedes one directory rename.
    stage = output_root / ('.staging-' + uuid.uuid4().hex)
    stage.mkdir(parents=True)
    for path, raw in files.items():
        destination = stage / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream:
            stream.write(raw)
            stream.flush()
            import os
            os.fsync(stream.fileno())
    (stage / 'receipt.json').write_bytes(encoded(receipt))
    # ReleaseStore resolves by release identity, so validate via the staging name.
    temporary = stage / release_id
    temporary.mkdir()
    for child in list(stage.iterdir()):
        if child != temporary:
            child.rename(temporary / child.name)
    ReleaseStore(stage).load(descriptor)
    temporary.rename(target)
    stage.rmdir()
    return descriptor, receipt
