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


@dataclass(frozen=True)
class Bundle:
    path: str
    snapshot: dict
    files: tuple

    @property
    def source_digest(self):
        return digest(list(self.files))


def load_bundle(root, path):
    path = Path(path)
    location = path.resolve().relative_to(Path(root).resolve()).as_posix()
    path = file_inside(root, location)
    data = read_json(path)
    lesson = path.name == 'lesson.json'
    expected = {'schema_version', 'format', 'page'} if lesson else {'schema_version', 'page'}
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
    snapshot = dict(page)
    files = []
    for item in [path] + [file_inside(root, (path.parent / filename).relative_to(root).as_posix())
                              for filename in ['body.html', 'page.css', 'page.js']]:
        if not item.exists() and item.name in {'page.css', 'page.js'}:
            raw = b''
        else:
            raw = item.read_bytes()
            files.append({'path': item.relative_to(root).as_posix(), 'sha256': sha256(raw).hexdigest(), 'size': len(raw)})
        if item.name != path.name:
            snapshot[{'body.html': 'body_html', 'page.css': 'page_css', 'page.js': 'page_js'}[item.name]] = raw.decode('utf-8')
    if lesson and data['format'] != 'html':
        renderer = render_component_lesson if data['format'] == 'component_html' else render_themed_contents
        snapshot['body_html'] = renderer(snapshot['body_html'])
    return Bundle(location, snapshot, tuple(files))


def load_sources(root):
    root = Path(root).resolve()
    bundles = [load_bundle(root, path) for path in sorted((root / 'curriculum').rglob('lesson.json'))]
    bundles += [load_bundle(root, path) for path in sorted((root / 'site_content/pages').glob('*/page.json'))]
    identities = [b.snapshot['slug'] for b in bundles]
    if not bundles or len(identities) != len(set(identities)):
        raise SourceError('Missing sources or duplicate slug')
    return bundles
