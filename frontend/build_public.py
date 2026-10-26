"""Build React Router public HTML from a verified immutable V04 release.

Node is used only during build. Serving uses the frozen artifact and Python's
pinned-release catalogue projection, never an independently fetched catalogue.
"""
import argparse
from hashlib import sha256
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlsplit
from uuid import UUID

from backend.content.releases import inside
from frontend.build_input import verified_release
from frontend.prepare_public import prepare
from frontend.rendering import esc
from frontend.public_design import VERSION as PUBLIC_DESIGN_VERSION, uses_react_public, public_design_kind, public_design_is_rendered


def html_path(url):
    if url == '/materials':
        return 'materials/index.html'
    return (url.lstrip('/') + 'index.html') if url.endswith('/') else url.lstrip('/')


def build_public(input_root, release_id, manifest_digest, output, origin, receipt_digest):
    parsed = urlsplit(origin)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.path not in ('', '/') or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError('Explicit trusted HTTP origin required')
    origin = origin.rstrip('/')
    release = verified_release(input_root, release_id, manifest_digest, receipt_digest)
    root = Path(__file__).resolve().parent
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('Output must be a new owned directory')
    view = root / '.cache' / ('public-view-' + release_id + '.json')
    prepare(input_root, release_id, manifest_digest, origin, view, receipt_digest)
    environment = dict(os.environ, MATHSTART_PUBLIC_VIEW=str(view))
    command = [shutil.which('npm.cmd') or shutil.which('npm'), 'exec', '--', 'react-router', 'build']
    subprocess.run(command, cwd=root, env=environment, check=True)
    client = Path(environment.get('MATHSTART_ROUTER_BUILD', str(root / 'build'))) / 'client'
    rendered, page_digests, semantic_digests = {}, {}, {}
    for entry in release.index['pages']:
        page = release.pages[entry['id']]
        # Router writes extensionless routes as directories with index.html.
        # The publication gateway's canonical artifact remains an exact URL file.
        prerender = entry['url'].strip('/')
        raw = inside(client, (prerender + '/' if prerender else '') + 'index.html').read_bytes()
        text = raw.decode('utf-8')
        # Framework mode generates complete HTML, including its hydration runtime.
        # Public legacy documents use a reviewed full-document lifecycle; remove
        # only Router-owned scripts/preloads after prerender, preserving authored JS.
        if not uses_react_public(page):
            text = re.sub(r'<script\b[^>]*>.*?</script>', lambda m: '' if ('type="module"' in m[0] or '__reactRouter' in m[0] or 'sessionStorage' in m[0] and 'scroll' in m[0]) else m[0], text, flags=re.S)
            text = re.sub(r'<link\b[^>]*rel="modulepreload"[^>]*>', '', text)
        raw = text.encode('utf-8')
        if not _public_page_content_present(page, text) or '<link rel="canonical" href="' + esc(origin + entry['canonical_path']) + '"' not in text:
            raise ValueError('Incomplete React public prerender')
        if uses_react_public(page):
            if '<script type="module"' not in text or 'window.__reactRouterContext' not in text:
                raise ValueError('React lesson is missing its selective hydration runtime')
        elif '<script type="module"' in text or 'window.__reactRouterContext' in text:
            raise ValueError('Public document must use full navigation')
        rendered[entry['url']] = raw
        page_digests[entry['url']] = sha256(release.page_raw[entry['id']]).hexdigest()
        semantic_digests[entry['url']] = sha256(json.dumps(page, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode()).hexdigest()
    for alias in release.index['aliases']:
        page = release.pages[alias['page_id']]
        alias_text=inside(client, html_path(alias['url'])).read_text(encoding='utf-8')
        if not _public_page_content_present(page, alias_text) or 'href="'+esc(origin+'/')+'"' not in alias_text:
            raise ValueError('Incomplete React home alias prerender')
        raw = rendered[page['seo']['canonical_path']]
        rendered[alias['url']] = raw
        page_digests[alias['url']] = page_digests[page['seo']['canonical_path']]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for entry in release.index['pages']:
        sitemap += f'<url><loc>{esc(origin + entry["canonical_path"])}</loc><lastmod>{esc(entry["updated_at"])}</lastmod><changefreq>{entry["sitemap_changefreq"]}</changefreq><priority>{entry["sitemap_priority"]}</priority></url>'
    rendered['/sitemap.xml'] = (sitemap + '</urlset>').encode('utf-8')
    rendered['/robots.txt'] = f'User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {origin}/sitemap.xml\n'.encode('utf-8')
    output.mkdir(parents=True)
    files = []
    def write(relative, raw, url=None):
        path = inside(output, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        files.append({'path':relative, 'url':url, 'sha256':sha256(raw).hexdigest(), 'size':len(raw)})
    for url, raw in rendered.items():
        write(html_path(url), raw, url)
    for url, (_, raw) in release.assets.items():
        write(url.lstrip('/'), raw, url)
    # Private shell has no loader/user data and is served no-store by ASGI.
    for path in (client / 'assets').rglob('*'):
        if path.is_file():
            if path.suffix in ('.html','.js','.json','.css','.map'):
                text=path.read_text(encoding='utf-8')
                if path.suffix=='.map' or any(marker in text for marker in ('fixture_only_self_check','__ui__/foundation','TEST_PASSWORD_CANARY_DO_NOT_SHIP','synthetic-csrf')):
                    raise ValueError('Private/debug production payload')
            write(path.relative_to(client).as_posix(), path.read_bytes())
    fallback = client / '__spa-fallback.html'
    if not fallback.is_file():
        raise ValueError('Private framework hydration shell is missing')
    fallback_raw = fallback.read_bytes()
    fallback_text = fallback_raw.decode('utf-8')
    if ('window.__reactRouterContext' not in fallback_text
            or any(marker in fallback_text for marker in ('canonical_url', 'data-lesson-host', 'rel="canonical"'))):
        raise ValueError('Private hydration shell contains a public publication view')
    write('_private/shell.html', fallback_raw)
    write('404.html', '<!doctype html><html lang="ru"><meta charset="UTF-8"><title>Страница не найдена | MathStart</title><main><h1>Страница не найдена</h1><a href="/">На главную</a></main></html>'.encode('utf-8'))
    receipt = {'version':'frontend-public-output-v1', 'release_id':release_id,
        'input_manifest_digest':manifest_digest, 'input_receipt_digest':receipt_digest, 'origin':origin, 'pages':len(release.pages),
        'public_urls':list(rendered), 'redirects':release.index['redirects'], 'files':files,
        'page_digests':page_digests, 'page_semantic_digests':semantic_digests,
        'catalogue_full_digest':sha256(json.dumps(release.index['catalogue'],ensure_ascii=False,separators=(',', ':'),sort_keys=True).encode()).hexdigest(),
        'navigation':'full_document', 'private_exports':[], 'anonymous_private_shell':'_private/shell.html',
        'build_engine':'react-router-framework', 'public_design_version': PUBLIC_DESIGN_VERSION,
        'page_ids':[str(pk) for pk in release.pages]}
    # A manifest cannot contain its own hash; its digest is the external receipt.
    inside(output,'output-manifest.json').write_bytes(json.dumps(receipt, ensure_ascii=False, indent=2).encode('utf-8'))
    return receipt


def _public_page_content_present(page, text):
    if public_design_kind(page):
        return public_design_is_rendered(page, text)
    if page.get('renderer_version', 'legacy') != 'react-v1':
        return page['body_html'] in text
    from backend.content.sources import lesson_document_is_rendered
    document = page.get('lesson_document')
    if not isinstance(document, dict) or not isinstance(document.get('sections'), list):
        return False
    return lesson_document_is_rendered(document, text)


def main():
    parser = argparse.ArgumentParser()
    for name in ('input-root', 'release-id', 'manifest-digest', 'output', 'origin', 'receipt-digest'):
        parser.add_argument('--' + name, required=True)
    args=vars(parser.parse_args())
    result = build_public(**args)
    print(json.dumps({'status':'PASS','release_id':result['release_id'],'pages':result['pages'],
        'public_urls':len(result['public_urls']), 'files':len(result['files'])+1,
        'output_manifest_digest':sha256((Path(args['output'])/'output-manifest.json').read_bytes()).hexdigest()}))

if __name__ == '__main__':
    main()
