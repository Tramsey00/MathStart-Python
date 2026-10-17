"""Pinned public release and private forms over verified React artifacts.

The read factory retains its explicit read-only contract. The normal ASGI entry
point supplies the identity service. Publication remains separately owned.
"""
from hashlib import sha256
import hmac
import json
import mimetypes
import os
from pathlib import Path
import re
import string
from urllib.parse import urlsplit

import sqlalchemy as sa
from starlette.responses import Response
from starlette.concurrency import run_in_threadpool

from backend.content.releases import ReleaseStore, active_release, inside
from backend.content.verified_release_cache import VerifiedReleaseStore
from backend.content.projection import seo
from backend.infrastructure.database import DatabaseConfig, create_engine, check_connection
from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.http import transport as wire
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import User, ContentPage
from backend.models.protocol import TargetSession, PublicationGate
from backend.staff.authorization import AuthenticatedIdentity


def keyed(salt, value, key):
    derived = sha256((salt + key).encode()).digest()
    return hmac.new(derived, value.encode(), 'sha256').hexdigest()


def session_digest(token, key):
    return keyed('mathstart.target.session', token, key)


def user_auth_hash(password_hash, key):
    return keyed('django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash', password_hash, key)


def public_csrf_check(request, origin):
    """Accepted Django cookie/masked-token and same-origin policy for public POST."""
    alphabet = string.ascii_letters + string.digits
    def unmask(token):
        if not isinstance(token, str) or len(token) not in {32, 64} or any(c not in alphabet for c in token):
            return None
        if len(token) == 32:
            return token
        return ''.join(alphabet[(alphabet.index(a) - alphabet.index(b)) % len(alphabet)]
                       for a, b in zip(token[32:], token[:32]))
    supplied_origin = request.headers.get('origin')
    if supplied_origin is not None and supplied_origin != origin:
        return False
    if supplied_origin is None and origin.startswith('https:'):
        try:
            referer = urlsplit(request.headers.get('referer', ''))
        except ValueError:
            return False
        trusted = urlsplit(origin)
        if referer.scheme != 'https' or referer.netloc != trusted.netloc:
            return False
    cookie, token = unmask(request.cookies.get('csrftoken')), unmask(request.headers.get('x-csrftoken'))
    return cookie is not None and token is not None and hmac.compare_digest(cookie, token)


class ReadSessionAuthenticator:
    """Read-only opaque session validation; roles always rechecked by V02."""
    def __init__(self, engine, key, fallback_keys=()):
        self.engine, self.keys = engine, (key, *fallback_keys)

    def __call__(self, request):
        token = request.cookies.get('sessionid')
        if not token or len(token) > 256:
            return None
        with UnitOfWork(self.engine) as uow:
            if self.engine.dialect.name != 'postgresql':
                raise wire.unavailable()
            uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
            now = uow.session.scalar(sa.select(sa.func.clock_timestamp()))
            row = uow.session.scalar(sa.select(TargetSession).where(TargetSession.token_digest.in_(
                [session_digest(token, key) for key in self.keys])))
            if row is None or row.revoked_at is not None or row.expires_at <= now:
                return None
            user = uow.session.get(User, row.user_id)
            if user is None or not user.is_active or not any(
                    hmac.compare_digest(row.auth_hash, user_auth_hash(user.password, key)) for key in self.keys):
                return None
            return AuthenticatedIdentity(user.id)


def artifact_for(root, digests, release):
    root = Path(root).resolve()
    base = root if (root / 'output-manifest.json').is_file() else inside(root, release.descriptor.release_id)
    raw = inside(base, 'output-manifest.json').read_bytes()
    if sha256(raw).hexdigest() != digests.get(release.descriptor.release_id):
        raise wire.unavailable()
    manifest = wire.decode_json(raw)
    if (manifest['release_id'] != release.descriptor.release_id
            or manifest['input_manifest_digest'] != release.descriptor.manifest_digest):
        raise wire.unavailable()
    return base, manifest


def artifact_bytes(root, manifest, relative):
    matches = [item for item in manifest['files'] if item['path'] == relative]
    if len(matches) != 1:
        raise wire.missing()
    item = matches[0]
    raw = inside(root, relative).read_bytes()
    if len(raw) != item['size'] or sha256(raw).hexdigest() != item['sha256']:
        raise wire.unavailable()
    return raw


PRIVATE_READ = re.compile(r'^(?:/account/|/admin/(?:password_change/|(?:content/(?:grade|subject|section|contentpage|lessonpublication|mediaasset|redirect)|auth/(?:user|group))/(?:add/|[1-9][0-9]*/(?:change/|history/|password/|delete/))?)?)$')


def create_public_app(engine, signer, *, release_root, artifact_root, artifact_digests, origin, identity_service=None):
    from frontend.rendering import PublicRenderer
    store = VerifiedReleaseStore(release_root)
    renderer = PublicRenderer(artifact_root, artifact_digests)
    authenticate = ReadSessionAuthenticator(engine, signer.key, signer.fallback_keys)

    def initial_edition(uow, page_id):
        gate_row = uow.session.get(PublicationGate, 'public')
        if gate_row is None or gate_row.pending_operation_id is not None:
            raise wire.unavailable()
        release = active_release(uow, store, 'public')
        row, page = uow.session.get(ContentPage, page_id), release.pages.get(page_id)
        if row is None or page is None or not row.is_published or any(getattr(row, key) != page[key]
                for key in ['title', 'slug', 'page_type', 'body_html', 'grade_id', 'subject_id', 'section_id', 'order']):
            raise wire.unavailable()
        if any(wire.timestamp(getattr(row, key)) != page[key] for key in ['created_at', 'updated_at']):
            raise wire.unavailable()
        if seo(row) != page['seo']:
            raise wire.unavailable()
        for field, suffix in [('page_css', 'css'), ('page_js', 'js')]:
            artifact = release.assets.get(f'/static/mathstart/pages/{row.slug}/page.{suffix}')
            if getattr(row, field).encode('utf-8') != (artifact[1] if artifact else b''):
                raise wire.unavailable()
        edition = {'release_id': release.descriptor.release_id, 'manifest_digest': release.descriptor.manifest_digest,
                   'page_published': True, 'page_digest': sha256(release.page_raw[page_id]).hexdigest(),
                   'canonical_path': page['seo']['canonical_path']}
        return {'page_id': page_id, 'observed_at': wire.timestamp(uow.session.scalar(sa.select(sa.func.clock_timestamp()))),
                'state': 'IN_SYNC', 'active': edition, 'db_edition': edition.copy(), 'pending': None}

    app = create_app(engine, signer, release_store=store, authenticate=authenticate,
                     render_page=renderer, public_origin=origin, observe_publication=initial_edition,
                     csrf_check=lambda request: public_csrf_check(request, origin), identity_service=identity_service)
    trusted_host = urlsplit(origin).netloc.lower()

    def auxiliary_response(request, private):
        with UnitOfWork(engine) as uow:
            uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
            release = active_release(uow, store, 'public')
        root, manifest = artifact_for(artifact_root, artifact_digests, release)
        relative = '_private/shell.html' if private else request.url.path.lstrip('/')
        raw = artifact_bytes(root, manifest, relative)
        mime = 'text/html' if private else mimetypes.guess_type(relative)[0] or 'application/octet-stream'
        return Response(raw if request.method == 'GET' else b'', media_type=mime,
                        headers={'Cache-Control': 'private, no-store' if private else 'no-cache',
                                 'X-Content-Type-Options': 'nosniff'})

    @app.middleware('http')
    async def verified_auxiliary(request, call_next):
        try:
            if request.headers.get('host', '').lower() != trusted_host:
                return wire.error_response(request, wire.invalid())
            path = request.url.path
            private = PRIVATE_READ.fullmatch(path) is not None
            if private or path.startswith('/assets/'):
                if request.method != 'GET' and not (path.startswith('/assets/') and request.method == 'HEAD'):
                    return Response(status_code=405, headers={'Allow': 'GET', 'Cache-Control': 'private, no-store'})
                return await run_in_threadpool(auxiliary_response, request, private)
            return await call_next(request)
        except wire.APIError as error:
            return wire.error_response(request, error)
        except Exception:
            return wire.error_response(request, wire.unavailable())

    app.state.database_engine = engine
    return app


def application():
    key, origin = os.environ['MATHSTART_HTTP_SIGNING_KEY'], os.environ['MATHSTART_PUBLIC_ORIGIN']
    fallbacks = json.loads(os.environ.get('MATHSTART_HTTP_SIGNING_FALLBACK_KEYS', '[]'))
    digests = json.loads(os.environ['MATHSTART_PUBLIC_ARTIFACT_DIGESTS'])
    if not isinstance(fallbacks, list) or any(not isinstance(k, str) or not k for k in fallbacks):
        raise ValueError('Explicit verifier key ring required')
    if not isinstance(digests, dict) or any(not re.fullmatch(r'[a-f0-9]{64}', d) for d in digests.values()):
        raise ValueError('Trusted artifact digests required')
    engine = create_engine(DatabaseConfig.from_environment())
    check_connection(engine)
    from backend.users.security import Security
    from backend.users.service import IdentityService
    identity = IdentityService(Security(engine, key, origin, fallback_keys=fallbacks,
                                        secure=origin.startswith('https:')))
    return create_public_app(engine, Signer(key, fallbacks), release_root=os.environ['MATHSTART_RELEASE_ROOT'],
            artifact_root=os.environ['MATHSTART_PUBLIC_ARTIFACT_ROOT'], artifact_digests=digests, origin=origin,
            identity_service=identity)
