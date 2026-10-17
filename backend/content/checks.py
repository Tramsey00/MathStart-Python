"""Read-only content inspections; reports are an explicit filesystem effect.

These checks inspect the current DB edition and public HTTP responses. Source
validation alone is deliberately not represented as DB/HTTP parity.
"""
from collections import Counter
from pathlib import Path, PurePosixPath
import html
import re
from urllib.parse import unquote, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError

import sqlalchemy as sa
from bs4 import BeautifulSoup

from backend.content.sources import SourceError, load_sources
from backend.models.baseline import ContentPage, MediaAsset, Redirect
from content.quality import inspect_html

ATTRIBUTES = [('a', 'href'), ('img', 'src'), ('script', 'src'), ('link', 'href'),
              ('source', 'src'), ('iframe', 'src'), ('video', 'src'), ('video', 'poster'),
              ('audio', 'src'), ('object', 'data')]


def verify_lesson_sources(session, root, *, slugs=None, all_lessons=False):
    if bool(slugs) == bool(all_lessons) or slugs and len(slugs) != len(set(slugs)):
        raise SourceError('Choose all lessons or distinct explicit slugs')
    bundles = [b for b in load_sources(root) if b.snapshot['page_type'] == 'topic']
    pages = {p.slug: p for p in session.scalars(sa.select(ContentPage).where(ContentPage.page_type == 'topic'))}
    by_slug = {b.snapshot['slug']: b for b in bundles}
    selected = set(by_slug) if all_lessons else set(slugs)
    if not selected or not selected.issubset(by_slug) or (all_lessons and set(pages) != selected):
        raise SourceError('Incomplete lesson source/database inventory')
    for slug in sorted(selected):
        page, snapshot = pages.get(slug), by_slug[slug].snapshot
        if page is None:
            raise SourceError('Lesson is absent from database')
        for field, value in snapshot.items():
            actual = getattr(page, field)
            if field in {'grade', 'subject', 'section'}:
                actual = actual.slug if actual is not None else None
            if actual != value:
                raise SourceError('Lesson source/database mismatch: ' + slug + '/' + field)
    return {'verified': len(selected)}


def normalize_internal_path(raw_url):
    value = html.unescape(str(raw_url or '')).strip()
    if not value or value.startswith('#'):
        return None
    parsed = urlparse('https:' + value if value.startswith('//') else value)
    scheme = parsed.scheme.lower()
    if scheme in {'http', 'https'}:
        if (parsed.hostname or '').lower() not in {'localhost', '127.0.0.1'}:
            return None
    elif scheme:
        return None
    path = re.sub(r'/+', '/', unquote(parsed.path or '').replace('\\', '/'))
    return '/' + path.lstrip('/') if path else '/'


def normalize_page_path(path):
    return path if path == '/' or PurePosixPath(path).suffix else '/' + path.strip('/') + '/'


def css_urls(text):
    return [m.group(2).strip() for m in re.finditer(r'url\(\s*([\'\"]?)(.*?)\1\s*\)', text or '', re.I) if m.group(2).strip()]


def references(page):
    soup = BeautifulSoup(page.body_html or '', 'html.parser')
    result = [{'kind': f'{tag}[{attribute}]', 'url': element.get(attribute, '')}
              for tag, attribute in ATTRIBUTES for element in soup.find_all(tag, attrs={attribute: True})]
    for element in soup.find_all(attrs={'srcset': True}):
        for candidate in element.get('srcset', '').split(','):
            url = candidate.strip().split(' ')[0]
            if url:
                result.append({'kind': 'srcset', 'url': url})
    result += [{'kind': 'style:url', 'url': url} for element in soup.find_all('style') for url in css_urls(element.get_text('\n'))]
    result += [{'kind': 'page_css:url', 'url': url} for url in css_urls(page.page_css)]
    return result


def confined_file(root, relative):
    root = Path(root).resolve()
    target = (root / relative).resolve()
    return target.is_relative_to(root) and target.is_file()


def inspect_site(session, *, static_roots, media_root):
    pages = list(session.scalars(sa.select(ContentPage).order_by(ContentPage.id)))
    media = list(session.scalars(sa.select(MediaAsset).order_by(MediaAsset.id)))
    redirects = list(session.scalars(sa.select(Redirect).where(Redirect.is_active.is_(True))))
    if not pages:
        raise SourceError('Site integrity requires a nonempty current database')
    known = {normalize_page_path('/' + p.slug + '/') for p in pages if p.slug} | {'/'}
    known |= {normalize_page_path(path) for r in redirects if (path := normalize_internal_path(r.old_path))}
    counts = Counter(p.slug for p in pages)
    topics = [p for p in pages if p.page_type == 'topic']
    report = {
        'duplicate_slugs': [{'slug': slug, 'total': total} for slug, total in sorted(counts.items()) if total > 1],
        'empty_content_pages': [{'id': p.id, 'title': p.title, 'slug': p.slug} for p in pages if not (p.body_html or '').strip()],
        'empty_slug_pages': [{'id': p.id, 'title': p.title} for p in pages if not (p.slug or '').strip()],
        **{'topics_without_' + field: [p.slug for p in topics if getattr(p, field + '_id') is None] for field in ['grade', 'subject', 'section']},
        'broken_internal_links': [], 'broken_media_references': [], 'broken_static_references': [],
        'missing_media_assets': [], 'unused_media_assets': [],
    }
    used, checked = set(), 0
    for page in pages:
        for reference in references(page):
            path = normalize_internal_path(reference['url'])
            if path is None:
                continue
            checked += 1
            detail = {'page': page.slug, **reference}
            if path.startswith('/media/'):
                relative = path[len('/media/'):].lstrip('/')
                used.add(relative)
                if not confined_file(media_root, relative):
                    report['broken_media_references'].append({**detail, 'expected_file': str(Path(media_root) / relative)})
            elif path.startswith('/static/'):
                if not any(confined_file(root, path[len('/static/'):].lstrip('/')) for root in static_roots):
                    report['broken_static_references'].append(detail)
            elif not path.startswith('/admin/'):
                normalized = normalize_page_path(path)
                if normalized not in known:
                    report['broken_internal_links'].append({**detail, 'normalized_path': normalized})
    for asset in media:
        row = {'id': asset.id, 'title': asset.title, 'file': asset.file or ''}
        if not asset.file or not confined_file(media_root, asset.file):
            report['missing_media_assets'].append(row)
        if asset.file and asset.file not in used:
            report['unused_media_assets'].append(row)
    report['summary'] = {'pages_total': len(pages), 'topics_total': len(topics), 'media_assets_total': len(media),
                         'checked_references': checked, **{key: len(rows) for key, rows in report.items()}}
    report['page_type_counts'] = dict(Counter(p.page_type for p in pages))
    errors = sum(report['summary'][key] for key in report if key not in {'summary', 'page_type_counts', 'unused_media_assets'})
    return report, errors


def inspect_public_quality(session, origin, *, timeout=10):
    parsed = urlparse(origin)
    if (parsed.scheme not in {'http', 'https'} or not parsed.netloc or parsed.username is not None
            or parsed.password is not None or parsed.path or parsed.query or parsed.fragment):
        raise SourceError('Explicit public origin required')
    pages = list(session.scalars(sa.select(ContentPage).where(ContentPage.is_published.is_(True)).order_by(ContentPage.id)))
    if not pages:
        raise SourceError('Content quality requires nonempty published content')
    report = {'pages_checked': 0, 'svg_checked': 0, 'issues': []}
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    opener = build_opener(NoRedirect())
    for page in pages:
        path = '/' if page.page_type == 'home' else '/' + page.slug + '/'
        report['pages_checked'] += 1
        try:
            with opener.open(Request(origin + path, headers={'Accept': 'text/html'}), timeout=timeout) as response:
                raw = response.read(16 * 1024 * 1024 + 1)
                if response.status != 200:
                    report['issues'].append({'page': page.slug, 'kind': 'http_status', 'detail': response.status})
                    continue
                if response.url != origin + path:
                    raise SourceError('Unexpected public page redirect')
                if len(raw) > 16 * 1024 * 1024:
                    raise SourceError('Public page exceeds inspection size limit')
                result = inspect_html(raw.decode('utf-8', errors='strict'))
                report['svg_checked'] += result['svg_count']
                report['issues'].extend({'page': page.slug, **issue} for issue in result['issues'])
        except HTTPError as error:
            report['issues'].append({'page': page.slug, 'kind': 'http_status', 'detail': error.code})
    return report, len(report['issues'])
