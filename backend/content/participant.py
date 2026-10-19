"""Prepared content/React handoff for the fenced PostgreSQL publisher.

An operator supplies reviewed immutable inputs and an exact content edition.
Construction only reads/verifies artifacts. All staging effects follow claim;
DB callbacks use cached verified metadata and never run Node, filesystem or HTTP.
"""
from hashlib import sha256
import os
from pathlib import Path
import re
from types import SimpleNamespace
import uuid
from xml.etree import ElementTree

import httpx
import sqlalchemy as sa

from backend.content.artifacts import verify_public_artifacts
from backend.content.build import encoded
from backend.content.editions import snapshot, fingerprint, project_updates, apply_updates
from backend.content.projection import build_index_candidate
from backend.content.publication import PublicationConflict, WorkReceipt, frozen
from backend.content.releases import Descriptor, ReleaseStore, inside
from backend.infrastructure.http.transport import timestamp
from backend.models.baseline import ContentPage


def digest(value):
    return sha256(encoded(value)).hexdigest()


def check_database(session, release):
    """Compare the complete DB publication projection with verified metadata."""
    rows = list(session.scalars(sa.select(ContentPage).where(ContentPage.is_published.is_(True)).order_by(ContentPage.id)))
    if {row.id for row in rows} != set(release.pages):
        raise PublicationConflict('EDITION_CONFLICT')
    for row in rows:
        page = release.pages[row.id]
        if (any(getattr(row, key) != page[key] for key in ('slug', 'title', 'page_type', 'body_html',
                'grade_id', 'subject_id', 'section_id', 'order', 'is_published'))
                or any(timestamp(getattr(row, key)) != page[key] for key in ('created_at', 'updated_at'))):
            raise PublicationConflict('EDITION_CONFLICT')
        for key, suffix in [('page_css', 'css'), ('page_js', 'js')]:
            asset = release.assets.get(f'/static/mathstart/pages/{row.slug}/page.{suffix}')
            if getattr(row, key).encode('utf-8') != (asset[1] if asset else b''):
                raise PublicationConflict('EDITION_CONFLICT')
    # Includes DB collation/order, catalogue parents, SEO, aliases and redirects.
    index = build_index_candidate(SimpleNamespace(session=session), release.descriptor.release_id, release.pages)
    if encoded(index) != release.index_raw:
        raise PublicationConflict('EDITION_CONFLICT')


class NoDomainWork:
    """Read/lease/terminal controls grant no domain or artifact capability."""
    def refused(self, *args):
        raise PublicationConflict('INVALID_PHASE')

    check_admission = apply = stage = verify_stage = verify_public = check_complete = refused


class PrecommitProof(NoDomainWork):
    """Abort can prove unchanged DB/previous release after candidate loss."""
    def __init__(self, plan, release_root):
        self.plan = frozen(plan)
        previous = plan['previous']
        self.previous = ReleaseStore(release_root).load(Descriptor(**previous)) if previous else None

    def check_admission(self, session, plan):
        if plan != self.plan:
            raise PublicationConflict('PLAN_CONFLICT')
        before = snapshot(session, lock=True)
        if digest(before) != plan['before_digest']:
            raise PublicationConflict('SOURCE_CONFLICT')
        if digest(project_updates(before, plan['changes'])) != plan['after_digest']:
            raise PublicationConflict('EDITION_CONFLICT')
        if self.previous:
            check_database(session, self.previous)

class PreparedPublication:
    def __init__(self, plan, *, input_root, output_root, release_root, artifact_root):
        self.plan = frozen(plan)
        required = {'version', 'kind', 'release_id', 'manifest_digest', 'previous', 'origin',
                    'input_receipt_digest', 'output_manifest_digest', 'before_digest', 'after_digest', 'changes'}
        if (type(plan) is not dict or set(plan) != required or plan['version'] != 'prepared-publication-v1'
                or plan['kind'] not in {'publish', 'unpublish'}
                or not re.fullmatch(r'[A-Za-z0-9_-]{1,120}', plan['release_id'])
                or not re.fullmatch(r'https?://[A-Za-z0-9.-]+(?::[0-9]+)?', plan['origin'])
                or any(not isinstance(plan[k], str) or not re.fullmatch(r'[a-f0-9]{64}', plan[k]) for k in
                       ('manifest_digest', 'input_receipt_digest', 'output_manifest_digest', 'before_digest', 'after_digest'))):
            raise PublicationConflict('INVALID_PLAN')
        self.plan_digest = digest(self.plan)
        self.input_root, self.output_root = Path(input_root).resolve(), Path(output_root).resolve()
        self.release_root, self.artifact_root = Path(release_root).resolve(), Path(artifact_root).resolve()
        if self.release_root == self.artifact_root:
            raise PublicationConflict('INVALID_ROOTS')
        self.release, self.output, self.manifest = self._verify(self.input_root, self.output_root)
        sources = [inside(self.input_root, plan['release_id']), self.output]
        if any(target.is_relative_to(source) for source in sources for target in (self.release_root, self.artifact_root)):
            raise PublicationConflict('INVALID_ROOTS')
        if self.release.descriptor.manifest_digest != plan['manifest_digest']:
            raise PublicationConflict('INVALID_PLAN')
        self.previous = None
        if plan['previous'] is not None:
            previous = plan['previous']
            if set(previous) != {'operation_id', 'release_id', 'manifest_digest', 'fence_generation'}:
                raise PublicationConflict('INVALID_PLAN')
            self.previous = ReleaseStore(self.release_root).load(Descriptor(**previous))
        # Unpublish is a retained DB row, absent from every next public view.
        if plan['kind'] == 'unpublish':
            changes = plan['changes']
            if any(c.get('before') is None for c in changes):
                raise PublicationConflict('INVALID_UNPUBLISH')
            removed = [c for c in changes if c.get('table') == 'content_contentpage'
                       and c['before']['is_published'] is True and c['after']['is_published'] is False]
            if not removed or any(c['after']['id'] in self.release.pages for c in removed):
                raise PublicationConflict('INVALID_UNPUBLISH')

    def _bound(self, plan):
        if plan != self.plan:
            raise PublicationConflict('PLAN_CONFLICT')

    def _verify(self, inputs, outputs):
        p = self.plan
        return verify_public_artifacts(inputs, p['release_id'], p['input_receipt_digest'],
                                       outputs, p['output_manifest_digest'], p['origin'])

    def check_admission(self, session, plan):
        self._bound(plan)
        before = snapshot(session, lock=True)
        if digest(before) != plan['before_digest']:
            raise PublicationConflict('SOURCE_CONFLICT')
        after = project_updates(before, plan['changes'])
        if digest(after) != plan['after_digest']:
            raise PublicationConflict('EDITION_CONFLICT')
        if self.previous is not None:
            check_database(session, self.previous)

    def apply(self, session, plan):
        self._bound(plan)
        apply_updates(session, plan['changes'], plan['before_digest'], plan['after_digest'])
        # Core updates must not be hidden by an ORM identity map.
        session.expire_all()
        check_database(session, self.release)

    def check_complete(self, session, plan):
        self._bound(plan)
        if fingerprint(session, lock=True) != plan['after_digest']:
            raise PublicationConflict('SOURCE_CONFLICT')
        check_database(session, self.release)

    def _receipt(self, token, plan_digest):
        if plan_digest != self.plan_digest:
            raise PublicationConflict('PLAN_CONFLICT')
        return WorkReceipt(token.operation_id, token.owner_id, token.generation, plan_digest,
                           self.plan['release_id'], self.plan['manifest_digest'],
                           digest({'input': self.plan['input_receipt_digest'], 'output': self.plan['output_manifest_digest']}))

    @classmethod
    def _mkdir(cls, path, *, exist_ok=True):
        missing, current = [], path
        while not current.exists():
            missing.append(current)
            current = current.parent
        path.mkdir(parents=True, exist_ok=exist_ok)
        for created in missing:
            cls._sync_directory(created)
            cls._sync_directory(created.parent)

    @classmethod
    def _copy(cls, source, destination):
        cls._mkdir(destination, exist_ok=False)
        for path in sorted(source.rglob('*')):
            if path.is_symlink():
                raise PublicationConflict('INVALID_ARTIFACT')
            if path.is_file():
                target = inside(destination, path.relative_to(source).as_posix())
                cls._mkdir(target.parent)
                with target.open('xb') as stream:
                    stream.write(path.read_bytes()); stream.flush(); os.fsync(stream.fileno())

    @staticmethod
    def _sync_directory(path):
        # Windows does not support opening directories via os.open. Files are
        # flushed there; POSIX also durably records directory entries.
        if os.name != 'nt':
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)

    @classmethod
    def _install(cls, source, destination):
        """Exclusive immutable file installation, restartable after partial copy.

        No worker replaces or deletes a finalized file. Recovery can finish the
        same byte-identical handoff; a conflicting existing file fails closed.
        The DB descriptor is the sole serving pointer and moves only after full
        verification of both installed trees.
        """
        cls._mkdir(destination)
        for path in sorted(source.rglob('*')):
            if not path.is_file():
                continue
            target = inside(destination, path.relative_to(source).as_posix())
            cls._mkdir(target.parent)
            try:
                os.link(path, target)
            except FileExistsError:
                if target.is_symlink() or target.read_bytes() != path.read_bytes():
                    raise PublicationConflict('ARTIFACT_CONFLICT') from None
            cls._sync_directory(target.parent)
        cls._sync_directory(destination.parent)

    def stage(self, token, plan, plan_digest):
        self._bound(plan)
        self._receipt(token, plan_digest)
        # Each attempt owns its entire staging path, including after takeover.
        identity = f'{token.operation_id}/{token.owner_id}/{token.generation}/{uuid.uuid4().hex}'
        inputs = inside(self.release_root, '.staging/' + identity)
        outputs = inside(self.artifact_root, '.staging/' + identity)
        self._copy(inside(self.input_root, plan['release_id']), inputs / plan['release_id'])
        self._copy(self.output, outputs / plan['release_id'])
        self._verify(inputs, outputs)
        self._install(inputs / plan['release_id'], inside(self.release_root, plan['release_id']))
        self._install(outputs / plan['release_id'], inside(self.artifact_root, plan['release_id']))
        return self.verify_stage(token, plan, plan_digest)

    def verify_stage(self, token, plan, plan_digest):
        self._bound(plan)
        self._verify(self.release_root, self.artifact_root)
        return self._receipt(token, plan_digest)

    def verify_public(self, token, plan, plan_digest):
        self._bound(plan)
        release, root, manifest = self._verify(self.release_root, self.artifact_root)
        from frontend.rendering import PublicRenderer
        renderer = PublicRenderer(root, {plan['release_id']: plan['output_manifest_digest']})
        # No proxy/environment credentials, redirects or cookie persistence.
        with httpx.Client(timeout=5, follow_redirects=False, trust_env=False) as client:
            def get(path, status=200):
                client.cookies.clear()
                response = client.get(plan['origin'] + path, headers={'Cache-Control': 'no-cache'})
                if response.status_code != status:
                    raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
                return response
            identity = get('/_content/index.json')
            if identity.content != release.index_raw or identity.headers.get('cache-control') != 'no-store':
                raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
            for url in manifest['public_urls']:
                response = get(url)
                if response.headers.get('cache-control') != 'no-cache':
                    raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
                if url in release.index['system_urls']:
                    continue
                page = release.page_path(url)
                expected = renderer(page, release.renderer_context(page, {}), plan['origin'] + page['seo']['canonical_path'])
                if response.content != expected.encode('utf-8'):
                    raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
            for url, (_, raw) in release.assets.items():
                response = get(url)
                if (response.content != raw or response.headers.get('cache-control') != 'no-cache'
                        or response.headers.get('etag') != '"' + sha256(raw).hexdigest() + '"'):
                    raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
                if client.get(plan['origin'] + url, headers={'If-None-Match': response.headers['etag']}).status_code != 304:
                    raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
            sitemap = get('/sitemap.xml')
            locations = [node.text for node in ElementTree.fromstring(sitemap.content).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            if locations != [plan['origin'] + p['canonical_path'] for p in sorted(release.index['pages'], key=lambda p: p['id'])]:
                raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
            robots = 'User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: ' + plan['origin'] + '/sitemap.xml\n'
            if get('/robots.txt').text != robots:
                raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
            public_paths = set(manifest['public_urls']) | set(release.assets)
            targets = {row['old_path']: row['new_path'] for row in release.index['redirects']}
            for redirect in release.index['redirects']:
                if redirect['old_path'] in public_paths:
                    continue  # Public page/asset takes precedence, as baseline.
                response = get(redirect['old_path'], 301 if redirect['is_permanent'] else 302)
                from urllib.parse import quote
                if (response.headers.get('location') != quote(redirect['new_path'], safe="/#%[]=:;$&()+,!?*@'~")
                        or response.headers.get('cache-control') != 'no-cache'):
                    raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
                target = redirect['new_path']
                seen = set()
                while target not in public_paths:
                    if target in seen or target not in targets:
                        raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
                    seen.add(target); target = targets[target]
            if self.previous:
                previous_paths = ({p['seo']['canonical_path'] for p in self.previous.pages.values()}
                                  | {a['url'] for a in self.previous.index['aliases']} | set(self.previous.assets))
                removed = previous_paths - public_paths
                redirects = {r['old_path'] for r in release.index['redirects']}
                for url in removed - redirects:
                    get(url, 404)
            if get('/_content/index.json').content != release.index_raw:
                raise PublicationConflict('PUBLIC_VERIFICATION_FAILED')
        return self._receipt(token, plan_digest)
