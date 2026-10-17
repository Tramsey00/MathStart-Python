"""Current identity operations with durable owner-bound receipts and sessions."""
from datetime import timedelta
import hashlib
import hmac
import json
import math
import uuid

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert

from backend.infrastructure.uow import UnitOfWork
from backend.infrastructure.locks import OrderedLocks
from backend.infrastructure.http import transport as wire
from backend.models.baseline import User, Grade, StudentProfile, IdentityReceipt, LoginWindow, metadata
from backend.models.protocol import TargetSession, ReceiptBridge
from backend.users import passwords
from backend.users.security import salted_hmac, unmask, revoke_lineage, auth_hash


def conflict(code='STATE_CONFLICT'):
    return wire.APIError(409, code, 'Request conflicts with current state.')


def envelope(request_id, data):
    return {'data': data, 'meta': {'request_id': request_id, 'version': 'http-v1'}}


def user_data(session, user):
    profile = session.scalar(sa.select(StudentProfile).where(StudentProfile.user_id == user.id))
    return {'id': user.id, 'username': user.username,
            'selected_grade_id': profile.selected_grade_id if profile else None,
            'onboarding_mode': profile.onboarding_mode if profile else None,
            'onboarding_complete': profile.onboarding_complete if profile else False}


def profile_for(session, user):
    profile = session.scalar(sa.select(StudentProfile).where(StudentProfile.user_id == user.id).with_for_update())
    if profile is None:
        profile = StudentProfile(user_id=user.id)
        session.add(profile)
        session.flush()
    return profile


def selected_grade(session, value):
    if isinstance(value, str):
        if not value.isascii() or not value.isdecimal() or len(value) > 19:
            raise wire.invalid()
        value = int(value)
    if type(value) is not int or not 0 < value < 2**63 or session.get(Grade, value) is None:
        raise wire.invalid()
    return value


def receipt_digest(owner, operation, route, body):
    raw = json.dumps({'owner': owner, 'operation': operation, 'canonical_route': route, 'body': body,
                      'expected_revision': body.get('expected_revision')}, sort_keys=True,
                     separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def receipt_key(key):
    if not isinstance(key, str) or not key:
        raise wire.invalid()
    return hashlib.sha256(key.encode()).hexdigest()


def receipt(session, scope, operation, key_digest, digest, now, *, verify_digest=True):
    row = session.scalar(sa.select(IdentityReceipt).where(IdentityReceipt.scope == scope,
                IdentityReceipt.operation == operation, IdentityReceipt.key_digest == key_digest).with_for_update())
    if row is None:
        row = IdentityReceipt(scope=scope, operation=operation, key_digest=key_digest,
                              request_digest=digest, expires_at=now + timedelta(days=7))
        session.add(row)
        session.flush()
    if verify_digest and row.request_digest != digest:
        raise conflict('IDEMPOTENCY_CONFLICT')
    return row


def validate_current(session, identity, user, keys, *, lock=True):
    query = sa.select(TargetSession).where(TargetSession.id == identity.session_id)
    row = session.scalar(query.with_for_update() if lock else query)
    now = session.scalar(sa.select(sa.func.clock_timestamp()))
    if (row is None or row.user_id != user.id or row.revoked_at is not None or row.expires_at <= now
            or row.lineage_id != identity.lineage_id or row.revocation_epoch != identity.revocation_epoch
            or not any(hmac.compare_digest(row.auth_hash, auth_hash(user, key)) for key in keys)):
        raise wire.authentication_required()
    return row


class IdentityService:
    def __init__(self, security):
        self.security = security
        self.engine = security.engine
        self.dummy_hash = passwords.encode('synthetic-dummy-not-an-account')

    def authenticated(self, request):
        identity = self.security.authenticate(request)
        if identity is None:
            raise wire.authentication_required()
        return identity

    def budget(self, remote):
        digest = salted_hmac('users.login.ip', remote, self.security.key)
        retry = None
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            s.execute(insert(metadata.tables['users_loginwindow']).values(id=uuid.uuid4(), ip_digest=digest, started_at=now, count=0)
                      .on_conflict_do_nothing(index_elements=['ip_digest']))
            row = s.scalar(sa.select(LoginWindow).where(LoginWindow.ip_digest == digest).with_for_update())
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            elapsed = (now - row.started_at).total_seconds()
            if elapsed >= 300:
                row.started_at, row.count, elapsed = now, 0, 0
            if row.count >= 10:
                retry = max(1, math.ceil(300 - elapsed))
            else:
                row.count += 1
            uow.commit()
        if retry:
            error = wire.APIError(429, 'RATE_LIMITED', 'Too many login requests.')
            error.retry_after = retry
            raise error

    def get_me(self, identity):
        with UnitOfWork(self.engine) as uow:
            user = uow.session.get(User, identity.user_id)
            if user is None or not user.is_active:
                raise wire.authentication_required()
            validate_current(uow.session, identity, user, self.security.keys, lock=False)
            return user_data(uow.session, user)

    def register(self, body, key, csrf, identity, request_id):
        secret = unmask(csrf)
        if secret is None:
            raise conflict()
        fingerprints = [salted_hmac('users.register.bootstrap', secret, key) for key in self.security.keys]
        fingerprint = fingerprints[0]
        scope = 'bootstrap:' + fingerprint
        key_digest = receipt_key(key)
        # S may select only this current session's already-bound original scope.
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            existing = s.scalar(sa.select(ReceiptBridge).where(ReceiptBridge.session_id == identity.session_id,
                    ReceiptBridge.state == 'ACTIVE')) if identity else s.scalar(sa.select(ReceiptBridge).where(
                        ReceiptBridge.bootstrap_fingerprint.in_(fingerprints)))
            if existing is not None:
                scope = existing.original_scope
        from backend.users.bridge import reconcile_expiry
        reconcile_expiry(self.engine, scope=scope)
        with UnitOfWork(self.engine) as uow:
            observed_epoch = uow.session.scalar(sa.select(ReceiptBridge.revocation_epoch).where(
                ReceiptBridge.original_scope == scope))
        digest = receipt_digest(scope, 'register', '/api/v1/auth/register/', body)
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            locks = OrderedLocks(s)
            for namespace in sorted({scope, 'lineage:' + str(identity.lineage_id)} if identity else {scope}):
                locks.namespace('identity', namespace)
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            prior = s.scalar(sa.select(IdentityReceipt).where(IdentityReceipt.scope == scope,
                         IdentityReceipt.operation == 'register', IdentityReceipt.key_digest == key_digest))
            user = None
            if prior is not None and prior.user_id is not None:
                user = s.scalar(sa.select(User).where(User.id == prior.user_id).with_for_update())
            if identity and (user is None or identity.user_id != user.id):
                raise conflict()
            row = receipt(s, scope, 'register', key_digest, digest, now, verify_digest=False)
            bridge = s.scalar(sa.select(ReceiptBridge).where(ReceiptBridge.original_scope == scope).with_for_update())
            if identity:
                validate_current(s, identity, user, self.security.keys)
            if row.status is not None:
                if (bridge is None or bridge.state in {'REVOKED', 'EXPIRED'} or now >= bridge.replay_until
                        or user is None or not user.is_active or bridge.owner_user_id != user.id
                        or observed_epoch is not None and bridge.revocation_epoch != observed_epoch):
                    raise conflict()
                if identity:
                    if bridge.session_id != identity.session_id or bridge.revocation_epoch != identity.revocation_epoch:
                        raise conflict()
                    if row.request_digest != digest:
                        raise conflict('IDEMPOTENCY_CONFLICT')
                    return row.response, row.status, None
                if bridge.bootstrap_fingerprint not in fingerprints or not passwords.verify(body['password'], user.password):
                    raise conflict()
                if row.request_digest != digest:
                    raise conflict('IDEMPOTENCY_CONFLICT')
                previous = s.get(TargetSession, bridge.session_id) if bridge.session_id else None
                issued, token, csrf_next = self.security.issue(s, user, now, previous=previous)
                bridge.state, bridge.session_id, bridge.session_lineage_id = 'ACTIVE', issued.id, issued.lineage_id
                bridge.revocation_epoch += 1
                issued.revocation_epoch = bridge.revocation_epoch
                bridge.ticket_version += 1
                bridge.ticket_revoked_at = now
                uow.commit()
                return row.response, row.status, (token, csrf_next)
            if bridge is not None:
                raise conflict()
            if row.request_digest != digest:
                raise conflict('IDEMPOTENCY_CONFLICT')
            user = User(username=body['username'], email=body.get('email', ''))
            if not passwords.valid_username(user.username) or not passwords.valid_email(user.email) or not passwords.validate_password(body['password'], user):
                raise wire.invalid()
            user.password = passwords.encode(body['password'])
            try:
                with s.begin_nested():
                    s.add(user)
                    s.flush()
            except IntegrityError:
                raise wire.invalid() from None
            profile_for(s, user)
            issued, token, csrf_next = self.security.issue(s, user, now)
            bridge = ReceiptBridge(id=uuid.uuid4(), original_scope=scope, bootstrap_fingerprint=fingerprint,
                        owner_user_id=user.id, state='ACTIVE', session_lineage_id=issued.lineage_id,
                        session_id=issued.id, revocation_epoch=0, created_at=now,
                        replay_until=now + timedelta(days=7), ticket_version=0,
                        ticket_expires_at=None, ticket_revoked_at=None, cutover_checkpoint_id=None,
                        transfer_binding_digest=None)
            s.add(bridge)
            row.user_id, row.response, row.status = user.id, envelope(request_id, user_data(s, user)), 201
            uow.commit()
            return row.response, row.status, (token, csrf_next)

    def login(self, body, remote, identity):
        self.budget(remote)
        with UnitOfWork(self.engine) as uow:
            candidate = uow.session.scalar(sa.select(User).where(User.username == body['username']))
            encoded = candidate.password if candidate else self.dummy_hash
            valid = passwords.verify(body['password'], encoded)
            if candidate is None or not candidate.is_active or not valid:
                raise wire.authentication_required()
            candidate_id, candidate_hash = candidate.id, candidate.password
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            locks = OrderedLocks(s)
            if identity:
                locks.namespace('identity', 'lineage:' + str(identity.lineage_id))
            user_ids = sorted({candidate_id, identity.user_id} if identity else {candidate_id})
            users = {u.id: u for u in s.scalars(sa.select(User).where(User.id.in_(user_ids)).order_by(User.id).with_for_update())}
            user = users[candidate_id]
            if not user.is_active or user.password != candidate_hash:
                raise wire.authentication_required()
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            previous = s.get(TargetSession, identity.session_id) if identity else None
            if previous and previous.revoked_at is not None:
                raise conflict()
            if previous and identity.user_id != user.id:
                revoke_lineage(s, previous.lineage_id, now)
                previous = None
            transfers = list(s.scalars(sa.select(ReceiptBridge).where(ReceiptBridge.session_id == previous.id,
                        ReceiptBridge.state == 'ACTIVE').order_by(ReceiptBridge.id).with_for_update())) if previous else []
            issued, token, csrf = self.security.issue(s, user, now, previous=previous)
            if previous:
                for bridge in transfers:
                    bridge.session_id = issued.id
                    bridge.revocation_epoch += 1
                    bridge.ticket_version += 1
                    bridge.ticket_revoked_at = now
                    issued.revocation_epoch = bridge.revocation_epoch
            user.last_login = now
            profile_for(s, user)
            result = user_data(s, user)
            uow.commit()
            return result, (token, csrf)

    def logout(self, identity):
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            OrderedLocks(s).namespace('identity', 'lineage:' + str(identity.lineage_id))
            user = s.scalar(sa.select(User).where(User.id == identity.user_id).with_for_update())
            validate_current(s, identity, user, self.security.keys, lock=False)
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            revoke_lineage(s, identity.lineage_id, now)
            uow.commit()

    def update_profile(self, identity, body, *, key=None, request_id=None):
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            OrderedLocks(s).namespace('identity', 'lineage:' + str(identity.lineage_id))
            user = s.scalar(sa.select(User).where(User.id == identity.user_id).with_for_update())
            if user is None or not user.is_active:
                raise wire.authentication_required()
            validate_current(s, identity, user, self.security.keys, lock=False)
            row = None
            if key is not None:
                owner = str(user.id)
                row = receipt(s, 'user:' + owner, 'complete_onboarding', receipt_key(key),
                        receipt_digest(owner, 'complete_onboarding', '/api/v1/onboarding/complete/', body),
                        s.scalar(sa.select(sa.func.clock_timestamp())))
                if row.status is not None:
                    validate_current(s, identity, user, self.security.keys)
                    return row.response, row.status
            validate_current(s, identity, user, self.security.keys)
            grade = selected_grade(s, body['selected_grade_id'])
            profile = profile_for(s, user)
            profile.selected_grade_id = grade
            if row is not None:
                profile.onboarding_mode, profile.onboarding_complete = body['mode'], True
            s.flush()
            result = user_data(s, user)
            if row is not None:
                row.user_id, row.status, row.response = user.id, 200, envelope(request_id, result)
            uow.commit()
            return (row.response, 200) if row else result
