"""Durable, monotone P2 expiry facts, independent of a request's outcome.

Readers/recovery take the owner row before bridge/session rows, as do identity
and staff mutations. A rejected replay must not roll these facts back with its
request transaction. Receipts are never changed or deleted here.
"""
import hmac
import sqlalchemy as sa

from backend.infrastructure.uow import UnitOfWork
from backend.infrastructure.locks import OrderedLocks
from backend.models.baseline import User
from backend.models.protocol import ReceiptBridge, TargetSession


def reconcile_expiry(engine, *, user_id=None, scope=None, auth_keys=()):
    if (user_id is None) == (scope is None):
        raise ValueError('Exactly one bridge owner selector is required')
    for _ in range(3):
        if _reconcile_expiry(engine, user_id=user_id, scope=scope, auth_keys=auth_keys):
            return
    raise RuntimeError('Bridge authority changed repeatedly during cleanup')


def _reconcile_expiry(engine, *, user_id, scope, auth_keys):
    with UnitOfWork(engine) as uow:
        s = uow.session
        query = sa.select(ReceiptBridge).where(ReceiptBridge.state.in_(['ACTIVE', 'DETACHED']))
        query = query.where(ReceiptBridge.owner_user_id == user_id) if user_id is not None else query.where(ReceiptBridge.original_scope == scope)
        observed = list(s.execute(query.with_only_columns(ReceiptBridge.original_scope, ReceiptBridge.session_lineage_id, ReceiptBridge.owner_user_id)))
        owner_ids = [user_id] if user_id is not None else [row.owner_user_id for row in observed]
        namespaces = {row.original_scope for row in observed} | {'lineage:' + str(row.session_lineage_id) for row in observed if row.session_lineage_id is not None}
        namespaces |= {'lineage:' + str(lineage) for lineage in s.scalars(sa.select(TargetSession.lineage_id).where(
            TargetSession.user_id.in_(owner_ids), TargetSession.revoked_at.is_(None)))}
        locks = OrderedLocks(s)
        for namespace in sorted(namespaces):
            locks.namespace('identity', namespace)
        users = {u.id: u for u in s.scalars(sa.select(User).where(User.id.in_(owner_ids)).order_by(User.id).with_for_update())}
        bridges = list(s.scalars(query.order_by(ReceiptBridge.id).with_for_update()))
        current_namespaces = {b.original_scope for b in bridges} | {'lineage:' + str(b.session_lineage_id) for b in bridges if b.session_lineage_id is not None}
        current_namespaces |= {'lineage:' + str(lineage) for lineage in s.scalars(sa.select(TargetSession.lineage_id).where(
            TargetSession.user_id.in_(owner_ids), TargetSession.revoked_at.is_(None)))}
        if not current_namespaces.issubset(namespaces):
            # A rebind completed before owner acquisition. Restart at the outer
            # boundary instead of acquiring a lower-rank namespace after rows.
            return False
        sessions = {row.id: row for row in s.scalars(sa.select(TargetSession).where(
            TargetSession.user_id.in_(owner_ids))
            .order_by(TargetSession.id).with_for_update())}
        # Sample time only after locks: a competing rebind/revocation may have
        # waited until expiry while we waited for the owner.
        now = s.scalar(sa.select(sa.func.clock_timestamp()))
        from backend.users.security import auth_hash
        for current in sessions.values():
            user = users.get(current.user_id)
            invalid = user is None or not user.is_active or bool(auth_keys) and not any(
                hmac.compare_digest(current.auth_hash, auth_hash(user, key)) for key in auth_keys)
            if invalid and current.revoked_at is None:
                current.revoked_at = now
                current.revocation_epoch += 1
        for bridge in bridges:
            current = sessions.get(bridge.session_id)
            user = users.get(bridge.owner_user_id)
            invalid_auth = user is None or not user.is_active or bridge.state == 'ACTIVE' and (
                current is None or current.revoked_at is not None or bool(auth_keys) and not any(
                    hmac.compare_digest(current.auth_hash, auth_hash(user, key)) for key in auth_keys))
            if invalid_auth or now >= bridge.replay_until:
                # Auth-hash invalidation is security revocation, never a
                # recoverable natural expiry. Explicit terminal facts win.
                bridge.state, bridge.session_id = 'REVOKED' if invalid_auth else 'EXPIRED', None
                bridge.revocation_epoch += 1
                bridge.ticket_version += 1
                bridge.ticket_revoked_at = now
                bridge.transfer_binding_digest = None
                if invalid_auth and current is not None and current.revoked_at is None:
                    current.revoked_at = now
                    current.revocation_epoch += 1
            elif bridge.state == 'ACTIVE':
                if now >= current.expires_at:
                    bridge.state, bridge.session_id = 'DETACHED', None
                    bridge.revocation_epoch += 1
                    # Natural expiry retains ticket verifier/expiry and lineage
                    # for an explicit same-owner recovery or later revocation.
        uow.commit()
        return True
