"""Read a single authoritative release; no DB/files publication or activation."""
from dataclasses import dataclass
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import re
from urllib.parse import unquote

from backend.infrastructure.http.contracts import validate
from backend.infrastructure.http.transport import decode_json, unavailable, missing
from backend.models.protocol import ActiveReleaseDescriptor, PublicationGate, PublicationJournal


def safe_public_path(path):
    if not isinstance(path, str) or not path.startswith('/') or path.startswith('//'):
        return False
    decoded = path
    for _ in range(3):
        next_value = unquote(decoded)
        if next_value == decoded:
            break
        decoded = next_value
    return (not any(c in decoded for c in '\\?#') and '://' not in decoded
            and not decoded.startswith('//') and '%' not in decoded
            and not any(ord(c) <= 32 or ord(c) == 127 for c in decoded)
            and not any(part in {'.', '..'} for part in decoded.split('/'))
            and not re.match(r'^/(?:admin|account|api|__ui__|_private)(?:/|$)', decoded))


def inside(root, relative):
    return _inside_resolved(Path(root).resolve(), relative)


def _inside_resolved(root, relative):
    """Internal fast path: root was resolved and confined by this operation.

    Every child is still resolved on every read, so replaced symlinks and path
    escapes are rejected. Avoid resolving the same root for every release file.
    """
    if (not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative
            or '%' in relative or relative.startswith('/') or any(ord(c) < 32 for c in relative)
            or any(p in ('.', '..', '') for p in relative.split('/'))):
        raise unavailable()
    target = (root / relative).resolve()
    if not target.is_relative_to(root):
        raise unavailable()
    return target


@dataclass(frozen=True)
class Descriptor:
    operation_id: object
    release_id: str
    manifest_digest: str
    fence_generation: int


class ReleaseStore:
    """Configured publisher-owned immutable root; validate bytes on every load.

    V04/I02 produce reviewed index/pages/assets. The public JSON schema is never
    expanded with filesystem paths or internal publication authority.
    """
    def __init__(self, root):
        self.root = Path(root).resolve()

    def page_bytes(self, descriptor, page_id):
        if type(page_id) is not int or not 0 < page_id < 2**63:
            raise unavailable()
        try:
            return inside(inside(self.root, descriptor.release_id), f'pages/{page_id}.json').read_bytes()
        except OSError:
            raise unavailable() from None

    def load(self, descriptor):
        try:
            if (not re.fullmatch(r'[A-Za-z0-9_-]+', descriptor.release_id)
                    or not re.fullmatch(r'[a-f0-9]{64}', descriptor.manifest_digest)
                    or type(descriptor.fence_generation) is not int or descriptor.fence_generation <= 0):
                raise unavailable()
            root = inside(self.root, descriptor.release_id)
            index_raw = inside(root, 'index.json').read_bytes()
            if sha256(index_raw).hexdigest() != descriptor.manifest_digest:
                raise unavailable()
            index = validate(decode_json(index_raw), 'PublicBuildIndex', True)
            if index['release_id'] != descriptor.release_id:
                raise unavailable()
            pages, slugs, urls, assets, page_raw = {}, set(), set(), {}, {}
            for entry in index['pages']:
                pk = entry['id']
                if pk in pages or entry['slug'] in slugs or entry['url'] in urls or entry['delivery_path'] != f'pages/{pk}.json':
                    raise unavailable()
                raw = inside(root, entry['delivery_path']).read_bytes()
                page = validate(decode_json(raw), 'ContentDelivery', True)
                canonical = '/' if page['page_type'] == 'home' else f'/{page["slug"]}/'
                if (any(page[f] != entry[f] for f in ['id', 'slug', 'page_type', 'updated_at'])
                        or page['seo']['canonical_path'] != canonical
                        or entry['url'] != canonical or entry['canonical_path'] != canonical
                        or not safe_public_path(canonical)
                        or sha256(page['body_html'].encode('utf-8')).hexdigest() != page['source']['render_digest']):
                    raise unavailable()
                order = [a['order'] for a in page['assets']]
                if order != sorted(order) or len(order) != len(set(order)):
                    raise unavailable()
                for asset in page['assets']:
                    suffix = PurePosixPath(asset['url']).suffix.lower()
                    allowed_suffixes = {'style': {'.css'}, 'script': {'.js'},
                                        'media': {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.pdf'}}
                    if suffix not in allowed_suffixes[asset['kind']]:
                        raise unavailable()
                    if (not safe_public_path(asset['url']) or not asset['url'].startswith(('/static/', '/media/'))
                            or any(p.startswith('.') or p.lower() in {'private', '_private', 'secrets'} for p in PurePosixPath(asset['storage_key']).parts)
                            or asset['storage_key'].startswith('/')):
                        raise unavailable()
                    if asset['kind'] != 'script' and asset['lifecycle'] != 'none':
                        raise unavailable()
                    asset_raw = inside(root, asset['storage_key']).read_bytes()
                    if sha256(asset_raw).hexdigest() != asset['sha256']:
                        raise unavailable()
                    previous = assets.get(asset['url'])
                    if previous is not None:
                        # Load order is local to each page, not shared URL identity.
                        identity = {k: v for k, v in asset.items() if k != 'order'}
                        previous_identity = {k: v for k, v in previous[0].items() if k != 'order'}
                        if previous_identity != identity or previous[1] != asset_raw:
                            raise unavailable()
                    assets.setdefault(asset['url'], (asset, asset_raw))
                pages[pk] = page
                page_raw[pk] = raw
                slugs.add(page['slug']); urls.add(canonical)
            homes = [p for p in pages.values() if p['page_type'] == 'home']
            if len(homes) > 1:
                raise unavailable()
            for alias in index['aliases']:
                page = pages.get(alias['page_id'])
                if (not page or page['page_type'] != 'home' or alias['url'] != f'/{page["slug"]}/'
                        or alias['canonical_path'] != '/' or alias['url'] in urls):
                    raise unavailable()
                urls.add(alias['url'])
            if homes and not any(alias['page_id'] == homes[0]['id']
                    and alias['url'] == f'/{homes[0]["slug"]}/'
                    and alias['status'] == 200 and alias['canonical_path'] == '/'
                    for alias in index['aliases']):
                raise unavailable()
            old_paths = set()
            for redirect in index['redirects']:
                if (not safe_public_path(redirect['old_path']) or not safe_public_path(redirect['new_path'])
                        or redirect['old_path'] == redirect['new_path'] or redirect['old_path'] in old_paths):
                    raise unavailable()
                old_paths.add(redirect['old_path'])
            self.check_catalogue(index['catalogue'], pages)
            return Release(descriptor, index, index_raw, pages, assets, page_raw)
        except (OSError, ValueError, TypeError, KeyError, RecursionError):
            raise unavailable() from None

    @staticmethod
    def check_catalogue(catalogue, pages):
        relations = {}
        for kind in ['grades', 'subjects', 'sections']:
            rows = catalogue[kind]
            relations[kind] = {r['id']: r for r in rows}
            if len(rows) != len(relations[kind]):
                raise unavailable()
        for row in catalogue['subjects']:
            if row['grade_id'] not in relations['grades']:
                raise unavailable()
        for row in catalogue['sections']:
            if row['subject_id'] not in relations['subjects']:
                raise unavailable()
        topic_ids = set()
        for topic in catalogue['topics']:
            page = pages.get(topic['id'])
            if (not page or page['page_type'] != 'topic' or topic['id'] in topic_ids
                    or any(page[f] != topic[f] for f in ['title', 'slug', 'order', 'grade_id', 'subject_id', 'section_id'])
                    or topic['url'] != page['seo']['canonical_path']):
                raise unavailable()
            for kind, field in [('grades', 'grade_id'), ('subjects', 'subject_id'), ('sections', 'section_id')]:
                if topic[field] is not None and topic[field] not in relations[kind]:
                    raise unavailable()
            topic_ids.add(topic['id'])
        if topic_ids != {pk for pk, p in pages.items() if p['page_type'] == 'topic'}:
            raise unavailable()


@dataclass
class Release:
    descriptor: Descriptor
    index: dict
    index_raw: bytes
    pages: dict
    assets: dict
    page_raw: dict

    def page(self, slug):
        for page in self.pages.values():
            if page['slug'] == slug:
                return page
        raise missing()

    def page_path(self, path):
        for page in self.pages.values():
            if page['seo']['canonical_path'] == path:
                return page
        for alias in self.index['aliases']:
            if alias['url'] == path:
                return self.pages[alias['page_id']]
        raise missing()

    def redirect(self, path):
        return next((r for r in self.index['redirects'] if r['old_path'] == path), None)

    def catalogue(self, params):
        catalogue = self.index['catalogue']
        topics = catalogue['topics']
        grades_by_id = {g['id']: g for g in catalogue['grades']}
        subjects_by_id = {s['id']: s for s in catalogue['subjects']}
        grades = {grades_by_id[t['grade_id']]['slug']: grades_by_id[t['grade_id']]
                  for t in topics if t['grade_id'] is not None}
        grade = params.get('grade', '')
        if grade not in grades:
            grade = ''
        available = [t for t in topics if not grade or t['grade_id'] == grades[grade]['id']]
        subjects = {}
        for topic in available:
            if topic['subject_id'] is not None:
                subject = subjects_by_id[topic['subject_id']]
                subjects.setdefault(subject['slug'], subject)
        subject = params.get('subject', '')
        if subject not in subjects:
            subject = ''
        q = params.get('q', '').strip()
        matches = [t for t in available if (not subject or (t['subject_id'] is not None
                  and subjects_by_id[t['subject_id']]['slug'] == subject)) and q.casefold() in t['title'].casefold()]
        return {'catalogue_topics': matches, 'catalogue_grades': list(grades.values()),
                'catalogue_subjects': list(subjects.values()), 'catalogue_grade': grade,
                'catalogue_subject': subject, 'catalogue_query': q, 'catalogue_count': len(matches)}

    def renderer_context(self, page, params):
        """Internal renderer handoff from this pinned release, isolated from its index."""
        context = {'pinned_release': {'release_id': self.descriptor.release_id,
                                     'manifest_digest': self.descriptor.manifest_digest}}
        if page['slug'] == 'karta-sajta':
            context.update(self.catalogue(params))
            context['catalogue_full'] = self.index['catalogue']
        return deepcopy(context)


def active_release(uow, store, namespace):
    if store is None:
        raise unavailable()
    return store.load(active_descriptor(uow, namespace))


def active_descriptor(uow, namespace):
    """Read the same committed authority for content and compiled UI artifacts."""
    row = uow.repository(ActiveReleaseDescriptor).get(namespace)
    if row is None:
        raise unavailable()
    gate = uow.repository(PublicationGate).get(namespace)
    operation = uow.repository(PublicationJournal).get(row.operation_id)
    if (gate is None or operation is None or gate.fence_generation < row.fence_generation
            or operation.namespace != namespace or not operation.db_committed
            or operation.activation_status != 'APPLIED' or operation.release_id != row.release_id
            or operation.manifest_digest != row.manifest_digest):
        raise unavailable()
    return Descriptor(row.operation_id, row.release_id, row.manifest_digest, row.fence_generation)
