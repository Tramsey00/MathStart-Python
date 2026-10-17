"""Durable, monotone P2 expiry facts, independent of a request's outcome.

Readers/recovery take the owner row before bridge/session rows, as do identity
and staff mutations. A rejected replay must not roll these facts back with its
request transaction. Receipts are never changed or deleted here.
"""
import sqlalchemy as sa

from backend.infrastructure.uow import UnitOfWork
from backend.infrastructure.locks import OrderedLocks
from backend.models.baseline import User
from backend.models.protocol import ReceiptBridge, TargetSession


def reconcile_expiry(engine, *, user_id=None, scope=None):
    if (user_id is None) == (scope is None):
        raise ValueError('Exactly one bridge owner selector is required')
    for _ in range(3):
        if _reconcile_expiry(engine, user_id=user_id, scope=scope):
            return
    raise RuntimeError('Bridge authority changed repeatedly during cleanup')


def _reconcile_expiry(engine, *, user_id, scope):
    with UnitOfWork(engine) as uow:
        s = uow.session
        query = sa.select(ReceiptBridge).where(ReceiptBridge.state.in_(['ACTIVE', 'DETACHED']))
        query = query.where(ReceiptBridge.owner_user_id == user_id) if user_id is not None else query.where(ReceiptBridge.original_scope == scope)
        observed = list(s.execute(query.with_only_columns(ReceiptBridge.original_scope, ReceiptBridge.session_lineage_id, ReceiptBridge.owner_user_id)))
        namespaces = {row.original_scope for row in observed} | {'lineage:' + str(row.session_lineage_id) for row in observed if row.session_lineage_id is not None}
        locks = OrderedLocks(s)
        for namespace in sorted(namespaces):
            locks.namespace('identity', namespace)
        owner_ids = [user_id] if user_id is not None else [row.owner_user_id for row in observed]
        list(s.scalars(sa.select(User).where(User.id.in_(owner_ids)).order_by(User.id).with_for_update()))
        bridges = list(s.scalars(query.order_by(ReceiptBridge.id).with_for_update()))
        current_namespaces = {b.original_scope for b in bridges} | {'lineage:' + str(b.session_lineage_id) for b in bridges if b.session_lineage_id is not None}
        if not current_namespaces.issubset(namespaces):
            # A rebind completed before owner acquisition. Restart at the outer
            # boundary instead of acquiring a lower-rank namespace after rows.
            return False
        sessions = {row.id: row for row in s.scalars(sa.select(TargetSession).where(
            TargetSession.id.in_([b.session_id for b in bridges if b.session_id is not None]))
            .order_by(TargetSession.id).with_for_update())}
        # Sample time only after locks: a competing rebind/revocation may have
        # waited until expiry while we waited for the owner.
        now = s.scalar(sa.select(sa.func.clock_timestamp()))
        for bridge in bridges:
            if now >= bridge.replay_until:
                bridge.state, bridge.session_id = 'EXPIRED', None
                bridge.revocation_epoch += 1
                bridge.ticket_version += 1
                bridge.ticket_revoked_at = now
                bridge.transfer_binding_digest = None
            elif bridge.state == 'ACTIVE':
                current = sessions.get(bridge.session_id)
                if current is None or current.revoked_at is not None:
                    # A retired binding is not proof of natural expiry.
                    bridge.state, bridge.session_id = 'REVOKED', None
                    bridge.revocation_epoch += 1
                    bridge.ticket_version += 1
                    bridge.ticket_revoked_at = now
                    bridge.transfer_binding_digest = None
                elif now >= current.expires_at:
                    bridge.state, bridge.session_id = 'DETACHED', None
                    bridge.revocation_epoch += 1
                    # Natural expiry retains ticket verifier/expiry and lineage
                    # for an explicit same-owner recovery or later revocation.
        uow.commit()
        return True
