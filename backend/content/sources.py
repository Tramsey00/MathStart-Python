"""Strict byte-preserving source ingestion for the target publisher.

No database, settings, template engine, or runtime trust declaration is read.
The repository root is supplied by the operator, never by an HTTP request.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re

from backend.content.components import render_component_lesson, render_themed_contents

FIELDS = {'slug', 'page_type', 'grade', 'subject', 'section', 'title', 'order',
          'seo_title', 'seo_description', 'is_published'}
SLUG = re.compile(r'[A-Za-z0-9_-]+\Z')


class SourceError(ValueError):
    pass


def file_inside(root, relative):
    if '\\' in relative or ':' in relative or any(p in {'', '.', '..'} for p in relative.split('/')):
        raise SourceError('Unsafe source path')
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise SourceError('Source path escapes reviewed root')
    return path


def read_json(path):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise SourceError('Duplicate source JSON member')
            result[key] = value
        return result
    def invalid(_):
        raise SourceError('Nonfinite source number')
    try:
        return json.loads(path.read_bytes().decode('utf-8'), object_pairs_hook=pairs, parse_constant=invalid)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SourceError('Invalid source file') from exc


def digest(snapshot):
    """Preserve the legacy publication snapshot algorithm exactly."""
    return sha256(json.dumps(snapshot, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':')).encode('utf-8')).hexdigest()


def compatibility_assets_digest(page_css, page_js):
    return digest({'page_css': page_css, 'page_js': page_js})


@dataclass(frozen=True)
class Bundle:
    path: str
    snapshot: dict
    files: tuple
    renderer_version: str = 'legacy'
    lesson_document: dict | None = None

    @property
    def source_digest(self):
        return digest(list(self.files))


def publication_digest(bundle, snapshot):
    """Bind React publication state to content.json while retaining legacy hashes."""
    if bundle.renderer_version == 'react-v1':
        return digest({'version': 'react-lesson-publication-v1', 'snapshot': snapshot,
                       'source_files': list(bundle.files)})
    return digest(snapshot)


def load_bundle(root, path):
    path = Path(path)
    location = path.resolve().relative_to(Path(root).resolve()).as_posix()
    path = file_inside(root, location)
    data = read_json(path)
    lesson = path.name == 'lesson.json'
    expected = {'schema_version', 'format', 'page'} if lesson else {'schema_version', 'page'}
    if lesson and type(data) is dict and 'renderer_version' in data:
        expected.add('renderer_version')
    if type(data) is not dict or set(data) != expected or type(data['schema_version']) is not int or data['schema_version'] != (2 if lesson else 1):
        raise SourceError('Invalid source schema')
    if lesson and data['format'] not in {'html', 'component_html', 'themed_html'}:
        raise SourceError('Unsupported lesson format')
    page = data['page']
    if type(page) is not dict or set(page) != FIELDS:
        raise SourceError('Unknown or missing page field')
    if page['page_type'] not in ({'topic'} if lesson else {'home', 'grade', 'subject', 'static'}):
        raise SourceError('Invalid page type')
    for key in ['slug', 'grade', 'subject', 'section']:
        if page[key] is None and key != 'slug' and not lesson:
            continue
        if not isinstance(page[key], str) or not SLUG.fullmatch(page[key]):
            raise SourceError('Invalid page identity')
    if any(not isinstance(page[key], str) for key in ['title', 'seo_title', 'seo_description']):
        raise SourceError('Invalid page text')
    if not page['title'].strip() or type(page['order']) is not int or page['order'] < 0 or type(page['is_published']) is not bool:
        raise SourceError('Invalid page order or visibility')
    renderer_version = data.get('renderer_version', 'legacy') if lesson else 'legacy'
    if not isinstance(renderer_version, str) or renderer_version not in {'legacy', 'react-v1'}:
        raise SourceError('Unsupported renderer version')
    if not lesson and renderer_version != 'legacy':
        raise SourceError('Renderer version is only supported on lesson sources')
    snapshot = dict(page)
    files = []
    content_path = file_inside(root, (path.parent / 'content.json').relative_to(root).as_posix()) if renderer_version == 'react-v1' else None
    source_items = [path] + [file_inside(root, (path.parent / filename).relative_to(root).as_posix())
                              for filename in ['body.html', 'page.css', 'page.js']]
    if content_path is not None:
        source_items.append(content_path)
    for item in source_items:
        if not item.exists() and item.name in {'page.css', 'page.js'}:
            raw = b''
        else:
            raw = item.read_bytes()
            files.append({'path': item.relative_to(root).as_posix(), 'sha256': sha256(raw).hexdigest(), 'size': len(raw)})
        if item.name != path.name and item.name != 'content.json':
            snapshot[{'body.html': 'body_html', 'page.css': 'page_css', 'page.js': 'page_js'}[item.name]] = raw.decode('utf-8')
    lesson_document = read_json(content_path) if content_path is not None else None
    if renderer_version == 'react-v1':
        validate_lesson_document(lesson_document, page['slug'])
        if any(lesson_document[key] != page[key] for key in ('title', 'grade', 'subject', 'section')):
            raise SourceError('React lesson document metadata differs from its source identity')
    if lesson and data['format'] != 'html':
        renderer = render_component_lesson if data['format'] == 'component_html' else render_themed_contents
        snapshot['body_html'] = renderer(snapshot['body_html'])
    return Bundle(location, snapshot, tuple(files), renderer_version, lesson_document)


def validate_lesson_document(document, slug):
    """Fail closed on unsupported React lesson nodes before publication."""
    if (type(document) is not dict or set(document) != {'version', 'slug', 'title', 'subtitle', 'grade', 'subject', 'section', 'sections'}
            or document.get('version') != 'lesson-document-v1' or document.get('slug') != slug
            or any(not isinstance(document.get(key), str) or not document[key].strip()
                   for key in ('title', 'grade', 'subject', 'section'))
            or not isinstance(document.get('subtitle'), str) or type(document.get('sections')) is not list
            or not document['sections']):
        raise SourceError('Invalid React lesson document identity')
    ids = set()
    def nodes(values, depth=0):
        if type(values) is not list or depth > 64:
            raise SourceError('Invalid React lesson node list')
        for node in values:
            if type(node) is not dict or not isinstance(node.get('kind'), str):
                raise SourceError('Invalid React lesson node')
            kind = node['kind']
            if kind == 'text':
                if set(node) != {'kind', 'text'} or not isinstance(node['text'], str):
                    raise SourceError('Invalid text node')
            elif kind == 'interactive':
                if set(node) != {'kind', 'name', 'id'} or node['name'] not in {'linear', 'quadratic'} or not isinstance(node['id'], str) or not node['id']:
                    raise SourceError('Unsupported React interactive')
            elif kind == 'element':
                if set(node) != {'kind', 'tag', 'attrs', 'children'}:
                    raise SourceError('Invalid element node')
                element(node, depth)
            elif kind in {'paragraph', 'note', 'example', 'table', 'figure'}:
                if set(node) != {'kind', 'tag', 'attrs', 'children'}:
                    raise SourceError('Invalid semantic node')
                element(node, depth)
            elif kind == 'selfCheck':
                if (set(node) != {'kind', 'attrs', 'question', 'answer', 'disclosure'}
                        or node['disclosure'] not in {'answer', 'solution'}):
                    raise SourceError('Invalid self-check node')
                element({'tag': 'div', 'attrs': node['attrs'], 'children': []}, depth)
                nodes(node['question'], depth + 1); nodes(node['answer'], depth + 1)
            else:
                raise SourceError('Unknown React lesson node')
    def element(node, depth):
        tag, attrs = node['tag'], node['attrs']
        allowed = {'p','span','strong','em','b','i','u','s','sub','sup','br','a','h2','h3','h4','ul','ol','li','blockquote','div','table','caption','thead','tbody','tr','th','td','figure','figcaption','img','math','mi','mn','mo','mrow','msup','msub','mfrac','msqrt','mroot','mtext','semantics','annotation','svg','g','path','circle','line','polyline','polygon','rect','ellipse','text','tspan','defs','marker'}
        attr_names = {'id','class','title','role','aria-label','aria-labelledby','aria-describedby','href','src','alt','width','height','loading','decoding','colspan','rowspan','scope','start','type','datetime','cite','mathvariant','display','xmlns','viewBox','fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','stroke-dasharray','opacity','d','x','y','x1','y1','x2','y2','cx','cy','r','rx','ry','points','transform','marker-end','marker-start','markerWidth','markerHeight','refX','refY','orient','font-size','font-weight','text-anchor','preserveAspectRatio'}
        if type(attrs) is not dict:
            raise SourceError('Unsupported authored attributes')
        attr_names.update({'font-family', 'style', 'markerUnits', 'dominant-baseline', 'encoding', 'clip-path'})
        if 'clip-path' in attrs and (not isinstance(attrs['clip-path'], str) or not re.fullmatch(r'url\(#[A-Za-z0-9_-]+\)', attrs['clip-path'])):
            raise SourceError('Unsupported authored clipping reference')
        allowed.update({'title', 'desc', 'small', 'clipPath'})
        if 'style' in attrs and (not isinstance(attrs['style'], str) or not re.fullmatch(r'\s*margin-top:\s*\d+(?:px|rem);?\s*', attrs['style'])):
            raise SourceError('Unsupported authored layout style')
        if (not isinstance(tag, str) or tag not in allowed or type(attrs) is not dict
                or any(not isinstance(k, str) or not isinstance(v, (str, int, float)) or isinstance(v, bool)
                       for k, v in attrs.items()) or any(k not in attr_names and not k.startswith(('aria-', 'data-')) for k in attrs)
                or any(k.lower() in {'href','src','xlink:href'} and (not isinstance(v, str) or not _safe_lesson_url(v)) for k,v in attrs.items())):
            raise SourceError('Unsupported authored element/attribute')
        nodes(node['children'], depth + 1)
    for section in document['sections']:
        if (type(section) is not dict or set(section) != {'id', 'title', 'nodes'}
                or not isinstance(section['id'], str) or not section['id'] or section['id'] in ids
                or not isinstance(section['title'], str) or not section['title']):
            raise SourceError('Invalid or duplicate lesson section')
        ids.add(section['id']); nodes(section['nodes'])


def _safe_lesson_url(value):
    value = value.strip()
    lowered = value.lower()
    if lowered.startswith(('javascript:', 'data:', 'vbscript:', '//')) or '\\' in value or any(ord(c) < 32 for c in value):
        return False
    return value.startswith(('/', '#')) or lowered.startswith(('https://', 'mailto:'))


def lesson_document_text(document):
    """Collect source-authored visible text for no-JS prerender evidence."""
    values = [document['title'], document['subtitle']]
    def visit(value):
        if isinstance(value, dict):
            if value.get('kind') == 'text' and value.get('text'):
                values.append(value['text'])
            for key in ('question', 'answer', 'children'):
                if key in value:
                    visit(value[key])
        elif isinstance(value, list):
            for child in value:
                visit(child)
    for section in document['sections']:
        values.append(section['title'])
        visit(section['nodes'])
    return values


def lesson_document_is_rendered(document, html):
    """Check visible lesson content inside the real article, excluding scripts and hydration data."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.select_one('main.lesson-article')
    if article is None:
        return False
    for hidden in article.select('script, style, template'):
        hidden.decompose()
    normalize = lambda value: ' '.join(value.split())
    article_text = normalize(article.get_text(' ', strip=True))
    if any(normalize(value) not in article_text for value in lesson_document_text(document) if normalize(value)):
        return False
    for section in document['sections']:
        rendered = article.find(id=section['id'])
        if rendered is None or normalize(rendered.get_text(' ', strip=True)).find(normalize(section['title'])) < 0:
            return False
    attrs, links, ids = set(), set(), set()
    for element in article.find_all(True):
        for name in ('alt', 'aria-label', 'href', 'src'):
            value = element.get(name)
            if isinstance(value, str):
                attrs.add(normalize(value)); links.add(value) if name in {'href', 'src'} else None
        if element.get('id'):
            ids.add(element.get('id'))
    def visit(value):
        if isinstance(value, dict):
            node_attrs = value.get('attrs', {})
            if isinstance(node_attrs, dict):
                if node_attrs.get('id') and node_attrs['id'] not in ids:
                    return False
                for name in ('alt', 'aria-label'):
                    if node_attrs.get(name) and normalize(str(node_attrs[name])) not in attrs:
                        return False
                for name in ('href', 'src'):
                    target = node_attrs.get(name)
                    if isinstance(target, str) and target not in links:
                        return False
            return all(visit(value[key]) for key in ('question', 'answer', 'children') if key in value)
        if isinstance(value, list):
            return all(visit(child) for child in value)
        return True
    return visit(document['sections'])


def load_sources(root):
    root = Path(root).resolve()
    bundles = [load_bundle(root, path) for path in sorted((root / 'curriculum').rglob('lesson.json'))]
    bundles += [load_bundle(root, path) for path in sorted((root / 'site_content/pages').glob('*/page.json'))]
    identities = [b.snapshot['slug'] for b in bundles]
    if not bundles or len(identities) != len(set(identities)):
        raise SourceError('Missing sources or duplicate slug')
    return bundles
