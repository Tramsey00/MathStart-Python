"""Opaque PG sessions and same-origin CSRF; no browser credential storage."""
from dataclasses import dataclass
from datetime import timedelta
import hashlib
import hmac
import secrets
import string
import uuid
from urllib.parse import urlsplit

import sqlalchemy as sa

from backend.infrastructure.http import transport as wire
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import User
from backend.models.protocol import TargetSession, ReceiptBridge
from backend.staff.authorization import AuthenticatedIdentity

CHARS = string.ascii_letters + string.digits


def csrf_secret():
    return ''.join(secrets.choice(CHARS) for _ in range(32))


def mask(secret):
    salt = csrf_secret()
    return salt + ''.join(CHARS[(CHARS.index(a) + CHARS.index(b)) % len(CHARS)] for a, b in zip(secret, salt))


def unmask(token):
    if not isinstance(token, str) or len(token) not in {32, 64} or any(c not in CHARS for c in token):
        return None
    if len(token) == 32:
        return token
    return ''.join(CHARS[(CHARS.index(a) - CHARS.index(b)) % len(CHARS)] for a, b in zip(token[32:], token[:32]))


def salted_hmac(salt, value, key):
    derived = hashlib.sha256((salt + key).encode()).digest()
    return hmac.new(derived, value.encode(), hashlib.sha256).hexdigest()


def digest_token(token, key):
    return salted_hmac('mathstart.target.session', token, key)


def auth_hash(user, key):
    return salted_hmac('django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash', user.password, key)


@dataclass(frozen=True)
class SessionIdentity:
    user_id: int
    session_id: uuid.UUID
    lineage_id: uuid.UUID
    revocation_epoch: int


class Security:
    def __init__(self, engine, key, origin, *, fallback_keys=(), secure=True, session_ttl=1209600,
                 cutover_digest=None, legacy_writer_role=None):
        parsed = urlsplit(origin)
        if parsed.scheme not in {'http', 'https'} or not parsed.netloc or parsed.path or parsed.query or parsed.fragment:
            raise ValueError('Trusted origin required')
        self.engine, self.key, self.origin = engine, key, origin
        self.keys = (key, *fallback_keys)
        self.host = parsed.netloc.lower()
        self.secure, self.session_ttl = secure, session_ttl
        self.cutover_digest, self.legacy_writer_role = cutover_digest, legacy_writer_role

    def writer(self, session):
        from backend.users.cutover import guard
        guard(session, self.keys, expected=self.cutover_digest, legacy_role=self.legacy_writer_role)

    def host_check(self, request):
        if request.headers.get('host', '').lower() != self.host:
            raise wire.invalid()

    def csrf_check(self, request):
        self.host_check(request)
        origin = request.headers.get('origin')
        if origin is not None:
            if origin != self.origin:
                return False
        elif self.origin.startswith('https:'):
            referer = request.headers.get('referer', '')
            try:
                parsed = urlsplit(referer)
            except ValueError:
                return False
            if parsed.scheme != 'https' or parsed.netloc.lower() != self.host:
                return False
        secret = unmask(request.cookies.get('csrftoken'))
        supplied = unmask(request.headers.get('x-csrftoken'))
        return secret is not None and supplied is not None and hmac.compare_digest(secret, supplied)

    def require_csrf(self, request):
        if not self.csrf_check(request):
            raise wire.APIError(403, 'CSRF_FAILED', 'CSRF validation failed.')

    def authenticate(self, request):
        self.host_check(request)
        token = request.cookies.get('sessionid', '')
        if not token or len(token) > 256:
            return None
        with UnitOfWork(self.engine) as uow:
            row = uow.session.scalar(sa.select(TargetSession).where(TargetSession.token_digest.in_(
                [digest_token(token, key) for key in self.keys])))
            if row is None or row.revoked_at is not None:
                return None
            owner = row.user_id if row is not None else None
        if owner is None:
            return None
        from backend.users.bridge import reconcile_expiry
        reconcile_expiry(self.engine, user_id=owner, auth_keys=self.keys, writer_check=self.writer)
        with UnitOfWork(self.engine) as uow:
            now = uow.session.scalar(sa.select(sa.func.clock_timestamp()))
            row = uow.session.scalar(sa.select(TargetSession).where(TargetSession.token_digest.in_(
                [digest_token(token, key) for key in self.keys])))
            if row is None or row.revoked_at is not None or row.expires_at <= now:
                return None
            user = uow.session.get(User, row.user_id)
            if user is None or not user.is_active or not any(hmac.compare_digest(row.auth_hash, auth_hash(user, k)) for k in self.keys):
                return None
            return SessionIdentity(user.id, row.id, row.lineage_id, row.revocation_epoch)

    def identity(self, request):
        identity = self.authenticate(request)
        return AuthenticatedIdentity(identity.user_id) if identity else None

    def issue(self, session, user, now, *, previous=None, lineage_id=None):
        token = secrets.token_urlsafe(32)
        lineage_id = lineage_id or (previous.lineage_id if previous else uuid.uuid4())
        if previous is not None:
            previous.revoked_at = now
        row = TargetSession(id=uuid.uuid4(), lineage_id=lineage_id, token_digest=digest_token(token, self.key),
                            user_id=user.id, auth_hash=auth_hash(user, self.key), revocation_epoch=0,
                            created_at=now, expires_at=now + timedelta(seconds=self.session_ttl), revoked_at=None)
        session.add(row)
        session.flush()
        return row, token, csrf_secret()

    def cookies(self, response, token, csrf):
        response.set_cookie('sessionid', token, max_age=self.session_ttl, httponly=True,
                            secure=self.secure, samesite='lax', path='/')
        response.set_cookie('csrftoken', csrf, max_age=31449600, httponly=False,
                            secure=self.secure, samesite='lax', path='/')
        return response


def revoke_lineage(session, lineage, now):
    bridges = list(session.scalars(sa.select(ReceiptBridge).where(ReceiptBridge.session_lineage_id == lineage).order_by(ReceiptBridge.id).with_for_update()))
    rows = list(session.scalars(sa.select(TargetSession).where(TargetSession.lineage_id == lineage).order_by(TargetSession.id).with_for_update()))
    for row in rows:
        if row.revoked_at is None:
            row.revoked_at = now
            row.revocation_epoch += 1
    for bridge in bridges:
        if bridge.state not in {'REVOKED', 'EXPIRED'}:
            bridge.state = 'REVOKED'
            bridge.session_id = None
            bridge.revocation_epoch += 1
            bridge.ticket_version += 1
            bridge.ticket_revoked_at = now
            bridge.transfer_binding_digest = None
