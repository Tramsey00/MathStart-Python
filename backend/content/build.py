"""Write and verify immutable, public-only publisher build inputs.

The operator supplies a reviewed source checkout; HTTP callers cannot attest
trust or select files. No active descriptor or publication state is changed.
"""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

import sqlalchemy as sa

from backend.content.sources import SourceError, file_inside, load_sources, read_json, publication_digest
from backend.content.projection import ReviewedSource, delivery_candidate, build_index_candidate
from backend.content.releases import Descriptor, ReleaseStore, safe_public_path, inside
from backend.models.baseline import ContentPage, LessonPublication
from backend.infrastructure.http.contracts import validate


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def verify_source_checkout(root, source_sha):
    paths = ['curriculum', 'site_content', 'static']
    commands = [
        ['git', '-C', str(root), 'rev-parse', '--verify', source_sha + '^{commit}'],
        ['git', '-C', str(root), 'diff', '--quiet', source_sha, '--', *paths],
        ['git', '-C', str(root), 'ls-files', '--others', '--exclude-standard', '--', *paths],
    ]
    for index, command in enumerate(commands):
        result = subprocess.run(command, capture_output=True, timeout=30)
        if result.returncode or index == 2 and result.stdout:
            raise SourceError('Reviewed source commit does not match checkout')


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
    react = bundle.renderer_version == 'react-v1'
    css = [] if react else ['site.css', 'lesson.css', 'lesson-math.css', 'lesson-components.css', 'lesson-diagrams.css', 'lesson-contents.css']
    scripts = [] if react else ['lesson-diagrams.js']
    if not react and page['page_type'] != 'topic':
        css.append('site-pages.css')
    if not react and page['slug'] == 'karta-sajta':
        css += ['ui/tokens.css', 'catalogue.css']
    if not react and page['slug'] in {'glavnaya', 'o-proekte', 'kontakty'}:
        css.append('ui/tokens.css')
    if not react and 'data-lesson-widget="power-functions"' in page['body_html']:
        css.append('widgets/power-functions.css')
    elif not react and 'ms-graph-layout' in page['body_html']:
        css.append('widgets/function-graphs.css')
    rows = []
    for item in css:
        path = 'static/mathstart/css/' + item
        rows.append((path, '/' + path, 'style', file_inside(root, path).read_bytes()))
    if page['page_css'] and not react:
        path = f'static/mathstart/pages/{page["slug"]}/page.css'
        rows.append((path, '/' + path, 'style', page['page_css'].encode('utf-8')))
    for item in scripts:
        path = 'static/mathstart/js/' + item
        rows.append((path, '/' + path, 'script', file_inside(root, path).read_bytes()))
    if page['page_js'] and not react:
        path = f'static/mathstart/pages/{page["slug"]}/page.js'
        rows.append((path, '/' + path, 'script', page['page_js'].encode('utf-8')))
    scripts = [] if react else ['lesson-navigation.js']
    if not react and 'data-lesson-widget="power-functions"' in page['body_html']:
        scripts += ['math.js', 'widgets/power-functions.js']
    for item in scripts:
        path = 'static/mathstart/js/' + item
        rows.append((path, '/' + path, 'script', file_inside(root, path).read_bytes()))
    # Authored direct asset references are reviewed source bytes, never client input.
    urls = set(re.findall(r'''(?:src|href)\s*=\s*["']((?:/static/|/media/)[^"'?#]+)''', page['body_html']))
    urls.update(re.findall(r'''url\(\s*["']?((?:/static/|/media/)[^\s)"'?#]+)''', page['page_css']))
    if react:
        urls.update(_lesson_document_asset_urls(bundle.lesson_document))
    # Reviewed public uploads remain addressable even when no current document
    # links them. The home delivery anchors this retained public-media inventory;
    # no runtime upload directory, private row or arbitrary file is exported.
    if page['page_type'] == 'home':
        media = read_json(root / 'site_content/media.json')
        if set(media) != {'schema_version', 'assets'} or media['schema_version'] != 1:
            raise SourceError('Invalid reviewed media manifest')
        seen = set()
        for item in media['assets']:
            if (set(item) != {'title', 'file', 'alt_text', 'related_page', 'sha256'}
                    or not isinstance(item['file'], str) or item['file'] in seen):
                raise SourceError('Invalid/duplicate reviewed media identity')
            seen.add(item['file'])
            urls.add('/media/' + item['file'])
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
              'order': order, 'lifecycle': 'full_document' if kind == 'script' and not react else 'none'}, raw)
            for order, (key, url, kind, raw) in enumerate(rows)]


def _lesson_document_asset_urls(document):
    urls = set()
    def visit(value):
        if isinstance(value, dict):
            attrs = value.get('attrs')
            if isinstance(attrs, dict):
                for key in ('src', 'href', 'xlink:href'):
                    target = attrs.get(key)
                    if isinstance(target, str) and target.startswith(('/static/', '/media/')):
                        urls.add(target.split('?', 1)[0].split('#', 1)[0])
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(document)
    return urls


def write_build_inputs(uow, source_root, output_root, release_id, source_sha):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,120}', release_id) or not re.fullmatch(r'[a-f0-9]{40}', source_sha):
        raise SourceError('Explicit release identity and source commit required')
    source_root, output_root = Path(source_root).resolve(), Path(output_root).resolve()
    target = output_root / release_id
    if target.exists():
        raise SourceError('Immutable release already exists')
    verify_source_checkout(source_root, source_sha)
    if (uow.session.bind.dialect.name == 'postgresql'
            and uow.session.scalar(sa.text('SHOW transaction_isolation')) not in {'repeatable read', 'serializable'}):
        raise SourceError('Build requires one repeatable PostgreSQL snapshot')
    bundles = {b.snapshot['slug']: b for b in load_sources(source_root)}
    routes = load_material_routes(source_root, bundles)
    pages = list(uow.session.scalars(sa.select(ContentPage).where(ContentPage.is_published.is_(True)).order_by(ContentPage.id)))
    deliveries, files = {}, {}
    for page in pages:
        bundle = bundles.get(page.slug)
        if bundle is None or any(getattr(page, k) != bundle.snapshot[k] for k in
                ['slug', 'page_type', 'title', 'order', 'seo_title', 'seo_description', 'body_html', 'page_css', 'page_js', 'is_published']):
            raise SourceError('Published DB edition differs from reviewed source; explicit publication required')
        if any((getattr(page, key).slug if getattr(page, key) is not None else None) != bundle.snapshot[key]
               for key in ['grade', 'subject', 'section']):
            raise SourceError('Published catalogue identity differs from reviewed source')
        if ((page.subject is not None and page.subject.grade_id != page.grade_id)
                or (page.section is not None and page.section.subject_id != page.subject_id)):
            raise SourceError('Published catalogue parents differ from reviewed source identity')
        if bundle.renderer_version == 'react-v1':
            publication = uow.session.scalar(sa.select(LessonPublication).where(LessonPublication.page_id == page.id))
            if (publication is None or publication.source_path != bundle.path.removeprefix('curriculum/')
                    or publication.published_digest != publication_digest(bundle, bundle.snapshot)):
                raise SourceError('React document differs from explicitly published source')
        assets = assets_for(source_root, bundle)
        for asset, raw in assets:
            previous = files.setdefault(asset['storage_key'], raw)
            if previous != raw:
                raise SourceError('Asset identity conflict')
        route = routes.get(page.slug)
        reviewed = ReviewedSource(bundle.path, bundle.source_digest, tuple(a for a, _ in assets),
            bundle.renderer_version, bundle.lesson_document,
            '/materials' if page.slug == 'karta-sajta' else route['path'] if route and route['renderer_version'] == 'react-v1' else None)
        deliveries[page.id] = delivery_candidate(uow, page.slug, reviewed)
        files[f'pages/{page.id}.json'] = encoded(deliveries[page.id])
    index = build_index_candidate(uow, release_id, deliveries)
    apply_material_redirects(index, routes)
    index = validate(index, 'PublicBuildIndex', True)
    files['index.json'] = encoded(index)
    descriptor = Descriptor(uuid.uuid4(), release_id, sha256(files['index.json']).hexdigest(), 1)
    inventory = [{'path': path, 'sha256': sha256(raw).hexdigest(), 'size': len(raw)} for path, raw in sorted(files.items())]
    receipt = {'version': 'build-input-receipt-v1', 'source_sha': source_sha, 'release_id': release_id,
               'manifest_digest': descriptor.manifest_digest, 'pages': len(pages),
               'topics': len(index['catalogue']['topics']), 'assets': len(files) - len(pages) - 1,
               'files': inventory, 'source_files': [f for b in bundles.values() for f in b.files]
                   + [source_file_record(source_root, path) for path in
                      ('site_content/material-routes.json', 'site_content/material-subjects.json')],
               'activation': 'NOT_PERFORMED'}
    install_build_inputs(output_root, release_id, descriptor, receipt, files)
    return descriptor, receipt


def load_material_subject_codes(source_root):
    data = read_json(file_inside(source_root, 'site_content/material-subjects.json'))
    if (type(data) is not dict or set(data) != {'version', 'codes'}
            or type(data['version']) is not int or data['version'] != 1 or type(data['codes']) is not dict):
        raise SourceError('Invalid material subject registry')
    codes = data['codes']
    public_codes = {'algebra', 'geometry', 'statistics', 'math'}
    if (len(codes) != len(public_codes)
            or any(not isinstance(identity, str) or not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', identity)
                   or not isinstance(code, str) or code not in public_codes for identity, code in codes.items())
            or set(codes.values()) != public_codes):
        raise SourceError('Invalid material subject codes')
    return codes


def load_material_routes(source_root, bundles):
    """Read the source-controlled stable route registry and bind each entry to a lesson."""
    data = read_json(Path(source_root) / 'site_content/material-routes.json')
    if type(data) is not dict or set(data) != {'version', 'assignments'} or data['version'] != 1 or type(data['assignments']) is not list:
        raise SourceError('Invalid material route registry')
    subject_codes = load_material_subject_codes(source_root)
    result, paths = {}, set()
    for item in data['assignments']:
        if type(item) is not dict or set(item) - {'aliases'} != {'slug', 'grade', 'subject', 'number', 'renderer_version'}:
            raise SourceError('Invalid material route assignment')
        slug, grade, subject, number, renderer = (item[k] for k in ('slug', 'grade', 'subject', 'number', 'renderer_version'))
        if (not isinstance(slug, str) or not isinstance(grade, int) or isinstance(grade, bool) or grade < 1
                or not isinstance(subject, str) or subject not in subject_codes.values()
                or not isinstance(number, int) or isinstance(number, bool) or number < 1
                or not isinstance(renderer, str) or renderer not in {'legacy', 'react-v1'} or slug in result):
            raise SourceError('Invalid/duplicate material route identity')
        path = f'/materials/{grade}-{subject}-{number}'
        if path in paths or not safe_public_path(path):
            raise SourceError('Duplicate/unsafe material route')
        paths.add(path)
        if slug not in bundles:
            raise SourceError('Material route references an unknown lesson')
        bundle = bundles[slug]
        page = bundle.snapshot
        try:
            page_grade = int(page['grade'].split('-', 1)[0])
        except (AttributeError, ValueError):
            raise SourceError('Material route lesson grade mismatch') from None
        if page_grade != grade or subject_codes.get(page['subject']) != subject or bundle.renderer_version != renderer:
            raise SourceError('Material route differs from lesson identity/renderer')
        aliases = item.get('aliases', [])
        if (type(aliases) is not list
                or any(not isinstance(alias, str) or not safe_public_path(alias) or alias in paths for alias in aliases)
                or len(set(aliases)) != len(aliases)):
            raise SourceError('Invalid/duplicate material route alias')
        paths.update(aliases)
        result[slug] = {'slug': slug, 'grade': grade, 'subject': subject, 'number': number,
                        'renderer_version': renderer, 'path': path, 'aliases': aliases}
    if not result:
        raise SourceError('Empty material route registry')
    if {slug for slug, bundle in bundles.items() if bundle.renderer_version == 'react-v1'} - set(result):
        raise SourceError('React lesson has no authoritative material route')
    return result


def source_file_record(root, relative):
    raw = file_inside(root, relative).read_bytes()
    return {'path': relative, 'sha256': sha256(raw).hexdigest(), 'size': len(raw)}


def apply_material_redirects(index, routes):
    """Point all known legacy aliases at the assigned canonical path directly."""
    moved = {old: route['path'] for route in routes.values()
             if route['renderer_version'] == 'react-v1'
             and any(page['slug'] == route['slug'] and page['canonical_path'] == route['path'] for page in index['pages'])
             for old in [f'/{route["slug"]}/', *route.get('aliases', [])]}
    if any(page['slug'] == 'karta-sajta' and page['canonical_path'] == '/materials' for page in index['pages']):
        moved.update({path: '/materials' for path in ('/karta-sajta/', '/materials.html', '/materials/')})
    if not moved:
        return
    existing = {row['old_path']: row for row in index['redirects']}
    for row in index['redirects']:
        target = moved.get(row['new_path'])
        if target is not None:
            row['new_path'] = target
    for old_path, target in moved.items():
        row = existing.get(old_path)
        if row is not None:
            row['new_path'] = target
            row['is_permanent'] = True
        else:
            index['redirects'].append({'old_path': old_path, 'new_path': target, 'is_permanent': True})
    if len({row['old_path'] for row in index['redirects']}) != len(index['redirects']):
        raise SourceError('Material route conflicts with an existing redirect')


def install_build_inputs(output_root, release_id, descriptor, receipt, files):
    """Build-only handoff; does not claim a gate or activate any release."""
    output_root = Path(output_root).resolve()
    target = inside(output_root, release_id)
    if target.exists():
        raise SourceError('Immutable release already exists')
    # Stage under the same filesystem; verification precedes one directory rename.
    stage = output_root / ('.staging-' + uuid.uuid4().hex)
    stage.mkdir(parents=True)
    for path, raw in files.items():
        destination = stage / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    with (stage / 'receipt.json').open('xb') as stream:
        stream.write(encoded(receipt)); stream.flush(); os.fsync(stream.fileno())
    # ReleaseStore resolves by release identity, so validate via the staging name.
    temporary = stage / release_id
    temporary.mkdir()
    for child in list(stage.iterdir()):
        if child != temporary:
            rename_build_path(child, temporary / child.name)
    ReleaseStore(stage).load(descriptor)
    rename_build_path(temporary, target)
    stage.rmdir()


def rename_build_path(source, target):
    """Windows scanners can briefly hold a freshly written build directory."""
    for attempt in range(4):
        try:
            source.rename(target)
            return
        except PermissionError:
            if os.name != 'nt' or attempt == 3:
                raise
            time.sleep(0.2 * (attempt + 1))
