"""Private, one-way identity import. Never authenticates a legacy session.

The operator first disables and drains the configured sole legacy writer role.
This module only verifies that fact; it never alters roles or deletes history.
All target identity writers share the outer advisory lock with the importer.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import re
import uuid

import sqlalchemy as sa

from backend.infrastructure.http.transport import APIError
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import IdentityReceipt, LegacySession, User, metadata
from backend.models.protocol import CutoverCheckpoint, ReceiptBridge, TargetSession

LOCK = int.from_bytes(hashlib.sha256(b'identity\0!cutover').digest()[:8], 'big', signed=True)
SOURCE_TABLES = ('auth_user', 'auth_group', 'auth_permission', 'auth_user_groups',
                 'auth_user_user_permissions', 'auth_group_permissions', 'users_studentprofile',
                 'users_identityreceipt', 'django_session', 'target_session', 'target_receipt_bridge')


def unavailable():
    return APIError(503, 'SERVICE_UNAVAILABLE', 'Identity writer provenance requires reconciliation.')


def outer_lock(session, *, exclusive=False):
    if session.bind.dialect.name != 'postgresql':
        raise unavailable()
    function = 'pg_advisory_xact_lock' if exclusive else 'pg_advisory_xact_lock_shared'
    session.execute(sa.text('SELECT ' + function + '(:key)'), {'key': LOCK})


def _normal(value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise unavailable()
        return value.astimezone(timezone.utc).isoformat(timespec='microseconds')
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, dict):
        return {key: _normal(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_normal(item) for item in value]
    return value


def _digest(key, domain, value):
    raw = json.dumps(_normal(value), sort_keys=True, ensure_ascii=False,
                     separators=(',', ':'), allow_nan=False)
    return hmac.new(key.encode(), (domain + '\0' + raw).encode(), hashlib.sha256).hexdigest()


def writer_fact(session, role):
    # NOLOGIN alone is insufficient: members can SET ROLE and existing sessions
    # survive ALTER ROLE. Reject both, including indirect membership (the first
    # incoming edge already makes a role reachable).
    if not isinstance(role, str) or not role:
        raise unavailable()
    fact = session.execute(sa.text('''
        SELECT r.oid, r.rolname, r.rolcanlogin, r.rolsuper,
               current_database() AS database, d.oid AS database_oid,
               (r.rolname = current_user OR r.rolname = session_user) AS is_current,
               EXISTS(SELECT 1 FROM pg_auth_members m WHERE m.roleid = r.oid) AS has_members,
               EXISTS(SELECT 1 FROM pg_stat_activity a WHERE a.usename = r.rolname) AS connected
        FROM pg_roles r CROSS JOIN pg_database d
        WHERE r.rolname = :role AND d.datname = current_database()
    '''), {'role': role}).mappings().one_or_none()
    if fact is None or any(fact[name] for name in ('rolcanlogin', 'rolsuper', 'is_current', 'has_members', 'connected')):
        raise unavailable()
    return dict(fact)


def source_digest(session, key):
    snapshot = {}
    for name in SOURCE_TABLES:
        table = metadata.tables[name]
        snapshot[name] = [dict(row) for row in session.execute(sa.select(table).order_by(*table.primary_key)).mappings()]
    return _digest(key, 'identity.cutover.source.v1', snapshot)


def checkpoint_digest(key, checkpoint_id, source, provenance):
    return _digest(key, 'identity.cutover.checkpoint.v1', [str(checkpoint_id), source, provenance])


def guard(session, keys, *, expected=None, legacy_role=None):
    """First operation in every identity write UoW, before any row lock."""
    outer_lock(session)
    checkpoints = list(session.scalars(sa.select(CutoverCheckpoint)))
    if checkpoints:
        if len(checkpoints) != 1 or not expected or not hmac.compare_digest(checkpoints[0].checkpoint_digest, expected):
            raise unavailable()
        fact = writer_fact(session, legacy_role)
        if not any(hmac.compare_digest(checkpoints[0].provenance_digest,
                   _digest(key, 'identity.cutover.writer.v1', fact)) for key in keys):
            raise unavailable()
    else:
        # Fresh targets have neither legacy sessions nor orphan legacy scopes.
        # A configured but absent checkpoint also fails closed.
        orphan = sa.select(IdentityReceipt.id).where(IdentityReceipt.operation == 'register',
            IdentityReceipt.scope.like('bootstrap:%'), ~sa.exists(sa.select(ReceiptBridge.id).where(
                ReceiptBridge.original_scope == IdentityReceipt.scope)))
        if expected or session.scalar(sa.select(sa.exists(sa.select(LegacySession.session_key)))) or session.scalar(sa.select(sa.exists(orphan))):
            raise unavailable()


class CutoverImport:
    def __init__(self, engine, keys, legacy_role):
        self.engine, self.keys, self.legacy_role = engine, tuple(keys), legacy_role
        if not self.keys or any(not isinstance(key, str) or not key for key in self.keys):
            raise ValueError('Explicit retained verifier keys required')

    def preview(self, checkpoint_id):
        checkpoint_id = uuid.UUID(str(checkpoint_id))
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            outer_lock(s, exclusive=True)
            if s.scalar(sa.select(sa.exists(sa.select(CutoverCheckpoint.id)))):
                raise unavailable()
            provenance = _digest(self.keys[0], 'identity.cutover.writer.v1', writer_fact(s, self.legacy_role))
            source = source_digest(s, self.keys[0])
            return {'checkpoint_id': str(checkpoint_id), 'source_digest': source,
                    'provenance_digest': provenance,
                    'checkpoint_digest': checkpoint_digest(self.keys[0], checkpoint_id, source, provenance)}

    def apply(self, plan):
        if set(plan) != {'checkpoint_id', 'source_digest', 'provenance_digest', 'checkpoint_digest'}:
            raise unavailable()
        checkpoint_id = uuid.UUID(plan['checkpoint_id'])
        if any(not isinstance(plan[name], str) or not re.fullmatch('[a-f0-9]{64}', plan[name])
               for name in ('source_digest', 'provenance_digest', 'checkpoint_digest')):
            raise unavailable()
        signing_key = next((key for key in self.keys if hmac.compare_digest(plan['checkpoint_digest'],
            checkpoint_digest(key, checkpoint_id, plan['source_digest'], plan['provenance_digest']))), None)
        if signing_key is None:
            raise unavailable()
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            outer_lock(s, exclusive=True)
            fact = writer_fact(s, self.legacy_role)
            if not hmac.compare_digest(plan['provenance_digest'], _digest(signing_key, 'identity.cutover.writer.v1', fact)):
                raise unavailable()
            checkpoints = list(s.scalars(sa.select(CutoverCheckpoint)))
            if checkpoints:
                if (len(checkpoints) != 1 or checkpoints[0].id != checkpoint_id
                        or checkpoints[0].checkpoint_digest != plan['checkpoint_digest']
                        or checkpoints[0].provenance_digest != plan['provenance_digest']):
                    raise unavailable()
                # Crucially do not repeat detach/revoke after a target rebind.
                return {'checkpoint_digest': plan['checkpoint_digest'], 'repeated': True}
            if not hmac.compare_digest(source_digest(s, signing_key), plan['source_digest']):
                raise unavailable()
            users = {row.id: row for row in s.scalars(sa.select(User).order_by(User.id).with_for_update())}
            receipts = list(s.scalars(sa.select(IdentityReceipt).where(IdentityReceipt.operation == 'register',
                IdentityReceipt.scope.like('bootstrap:%')).order_by(IdentityReceipt.scope,
                    IdentityReceipt.operation, IdentityReceipt.key_digest).with_for_update()))
            bridge_rows = list(s.scalars(sa.select(ReceiptBridge).order_by(ReceiptBridge.id).with_for_update()))
            bridges = {row.original_scope: row for row in bridge_rows}
            if len(bridges) != len(bridge_rows) or any(not re.fullmatch('bootstrap:[a-f0-9]{64}', row.original_scope)
                    or row.bootstrap_fingerprint != row.original_scope[10:] for row in bridge_rows):
                raise unavailable()
            sessions = list(s.scalars(sa.select(TargetSession).order_by(TargetSession.id).with_for_update()))
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            from backend.users.legacy_proof import registration_proof, session_owner
            # Derive proof only from independently verified session data. A
            # receipt owner or receipt key cannot manufacture this mapping.
            proofs = {}
            for old in s.scalars(sa.select(LegacySession).order_by(LegacySession.session_key)):
                user = users.get(session_owner(old, self.keys))
                proof = registration_proof(old, user, self.keys, now) if user else None
                if proof:
                    proofs.setdefault(proof.original_scope, set()).add((proof.owner_user_id, proof.transfer_binding_digest))
            grouped = {}
            for receipt in receipts:
                if not re.fullmatch('bootstrap:[a-f0-9]{64}', receipt.scope):
                    raise unavailable()
                grouped.setdefault(receipt.scope, []).append(receipt)
            for scope, rows in grouped.items():
                owners = {row.user_id for row in rows}
                if len(owners) != 1:
                    raise unavailable()
                owner = owners.pop()
                for row in rows:
                    if row.status is not None and (row.status != 201 or owner is None
                            or not isinstance(row.response, dict) or not isinstance(row.response.get('data'), dict)
                            or row.response['data'].get('id') != owner):
                        raise unavailable()
                bridge = bridges.get(scope)
                if bridge is not None and (bridge.owner_user_id != owner or bridge.bootstrap_fingerprint != scope[10:]):
                    raise unavailable()
                if bridge is None:
                    created = min(row.created_at for row in rows)
                    bridge = ReceiptBridge(id=uuid.uuid4(), original_scope=scope, bootstrap_fingerprint=scope[10:],
                        owner_user_id=owner, state='DETACHED', session_id=None, session_lineage_id=None,
                        revocation_epoch=0, created_at=created,
                        replay_until=max([created + timedelta(days=7), *[row.expires_at for row in rows]]),
                        ticket_version=0, ticket_expires_at=None, ticket_revoked_at=None,
                        transfer_binding_digest=None, cutover_checkpoint_id=checkpoint_id)
                    s.add(bridge)
                    bridges[scope] = bridge
                candidates = proofs.get(scope, set())
                if len(candidates) > 1 or any(user_id != owner for user_id, _ in candidates):
                    raise unavailable()
                if bridge.state not in {'REVOKED', 'EXPIRED'}:
                    bridge.transfer_binding_digest = next(iter(candidates))[1] if candidates else None
            for bridge in bridges.values():
                bridge.cutover_checkpoint_id = checkpoint_id
                if bridge.state not in {'REVOKED', 'EXPIRED'}:
                    invalid_owner = bridge.owner_user_id is not None and (
                        bridge.owner_user_id not in users or not users[bridge.owner_user_id].is_active)
                    bridge.state = 'REVOKED' if invalid_owner else 'EXPIRED' if bridge.replay_until <= now else 'DETACHED'
                    bridge.session_id = None
                    bridge.revocation_epoch += 1
                    bridge.ticket_version += 1
                    bridge.ticket_revoked_at = now
                    if bridge.state in {'EXPIRED', 'REVOKED'}:
                        bridge.transfer_binding_digest = None
            for row in sessions:
                if row.revoked_at is None:
                    row.revoked_at, row.revocation_epoch = now, row.revocation_epoch + 1
            s.add(CutoverCheckpoint(id=checkpoint_id, checkpoint_digest=plan['checkpoint_digest'],
                                   provenance_digest=plan['provenance_digest'], verified_at=now))
            uow.commit()
            return {'checkpoint_digest': plan['checkpoint_digest'], 'repeated': False}
