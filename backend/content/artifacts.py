"""One complete trusted input/SSG verification boundary for publication.

Digests are supplied by a reviewed server-side build handoff, never HTTP input.
Verification selects one immutable release and never reads the active pointer.
"""
from hashlib import sha256
from pathlib import Path
import re

from backend.content.build import encoded, verify_build_inputs
from backend.content.releases import inside
from backend.content.sources import lesson_document_is_rendered
from backend.content.sources import SourceError, read_json

OUTPUT_FIELDS = {'version', 'release_id', 'input_manifest_digest', 'input_receipt_digest', 'origin',
    'pages', 'public_urls', 'redirects', 'files', 'page_digests', 'page_semantic_digests',
    'catalogue_full_digest', 'navigation', 'private_exports', 'anonymous_private_shell', 'build_engine', 'page_ids'}


def html_path(url):
    return url.lstrip('/') + 'index.html' if url.endswith('/') else url.lstrip('/')


def verify_public_artifacts(release_root, release_id, receipt_digest, artifact_root, artifact_digest, origin):
    if not isinstance(artifact_digest, str) or not re.fullmatch(r'[a-f0-9]{64}', artifact_digest):
        raise SourceError('Trusted output digest required')
    release = verify_build_inputs(release_root, release_id, receipt_digest)
    root = Path(artifact_root).resolve()
    if not (root / 'output-manifest.json').is_file():
        root = inside(root, release_id)
    manifest_path = inside(root, 'output-manifest.json')
    if sha256(manifest_path.read_bytes()).hexdigest() != artifact_digest:
        raise SourceError('Output manifest integrity mismatch')
    manifest = read_json(manifest_path)
    if (type(manifest) is not dict or set(manifest) - {'public_design_version'} != OUTPUT_FIELDS
            or ('public_design_version' in manifest and manifest['public_design_version'] != 'approved-public-v1')
            or manifest['version'] != 'frontend-public-output-v1' or manifest['release_id'] != release_id
            or manifest['input_manifest_digest'] != release.descriptor.manifest_digest
            or manifest['input_receipt_digest'] != receipt_digest or manifest['origin'] != origin
            or type(manifest['pages']) is not int or manifest['pages'] != len(release.pages)
            or manifest['navigation'] != 'full_document' or manifest['build_engine'] != 'react-router-framework'
            or manifest['private_exports'] != [] or manifest['anonymous_private_shell'] != '_private/shell.html'):
        raise SourceError('Output identity or public export mismatch')
    canonical = {p['seo']['canonical_path'] for p in release.pages.values()}
    public_urls = canonical | {a['url'] for a in release.index['aliases']} | set(release.index['system_urls'])
    if (type(manifest['public_urls']) is not list or len(manifest['public_urls']) != len(public_urls)
            or set(manifest['public_urls']) != public_urls
            or type(manifest['page_ids']) is not list or len(manifest['page_ids']) != len(release.pages)
            or set(manifest['page_ids']) != {str(pk) for pk in release.pages}
            or set(manifest['page_semantic_digests']) != canonical or manifest['redirects'] != release.index['redirects']
            or manifest['catalogue_full_digest'] != sha256(encoded(release.index['catalogue'])).hexdigest()):
        raise SourceError('Output public inventory mismatch')
    expected_digests = {p['seo']['canonical_path']: sha256(release.page_raw[pk]).hexdigest() for pk, p in release.pages.items()}
    for alias in release.index['aliases']:
        expected_digests[alias['url']] = sha256(release.page_raw[alias['page_id']]).hexdigest()
    if manifest['page_digests'] != expected_digests:
        raise SourceError('Output page byte identity mismatch')
    for page in release.pages.values():
        if manifest['page_semantic_digests'][page['seo']['canonical_path']] != sha256(encoded(page)).hexdigest():
            raise SourceError('Output page semantic identity mismatch')
    paths, urls, payloads = set(), set(), {}
    allowed_urls = public_urls | set(release.assets)
    for item in manifest['files']:
        if type(item) is not dict or set(item) != {'path', 'url', 'size', 'sha256'}:
            raise SourceError('Invalid output file entry')
        path, url = item['path'], item['url']
        if path in paths or type(item['size']) is not int or item['size'] < 0:
            raise SourceError('Duplicate or invalid output file')
        if url is not None:
            if url not in allowed_urls or url in urls or path != html_path(url):
                raise SourceError('Unexpected output URL')
            urls.add(url)
        elif path not in {'_private/shell.html', '404.html'} and not path.startswith('assets/'):
            raise SourceError('Unexpected nonpublic output path')
        if path.endswith('.map') or any(part.startswith('.') for part in path.split('/')):
            raise SourceError('Private/debug output path')
        raw = inside(root, path).read_bytes()
        if len(raw) != item['size'] or sha256(raw).hexdigest() != item['sha256']:
            raise SourceError('Output file integrity mismatch')
        paths.add(path); payloads[path] = raw
    if urls != allowed_urls or not {'_private/shell.html', '404.html'}.issubset(paths):
        raise SourceError('Incomplete output file coverage')
    if {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} != paths | {'output-manifest.json'}:
        raise SourceError('Unlisted output artifact')
    shell = payloads['_private/shell.html'].decode('utf-8')
    if ('window.__reactRouterContext' not in shell
            or any(marker in shell for marker in ('canonical_url', 'data-lesson-host', 'rel="canonical"'))):
        raise SourceError('Private shell contains a publication view')
    for url, (_, raw) in release.assets.items():
        if payloads[url.lstrip('/')] != raw:
            raise SourceError('Source/output asset mismatch')
    from frontend.rendering import PublicRenderer
    renderer = PublicRenderer(root, {release_id: artifact_digest})
    for page in release.pages.values():
        html = renderer(page, release.renderer_context(page, {}), origin + page['seo']['canonical_path'])
        if page.get('renderer_version', 'legacy') == 'react-v1':
            document = page.get('lesson_document')
            if not isinstance(document, dict) or not lesson_document_is_rendered(document, html):
                raise SourceError('Incomplete rendered React lesson document')
        elif manifest.get('public_design_version') == 'approved-public-v1' and page['slug'] in {'glavnaya', 'karta-sajta'}:
            from frontend.public_design import public_design_is_rendered
            if not public_design_is_rendered(page, html):
                raise SourceError('Incomplete approved public design')
        elif page['body_html'] not in html:
            raise SourceError('Incomplete frontend authored HTML')
    return release, root, manifest
