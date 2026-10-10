"""Additive physical representation of R02 P1/P2 facts, for V01 DDL review.

Cross-row monotonicity, lease/CAS and lifecycle writes belong to V03/V04.
No ORM callbacks pretend to enforce a distributed protocol.
"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from .baseline import metadata, mapper_registry, utc_now


def uuid_column(name, nullable=False):
    return sa.Column(name, sa.Uuid(), nullable=nullable)


def timestamp(name, nullable=False):
    return sa.Column(name, sa.DateTime(timezone=True), nullable=nullable)


journal = sa.Table('target_publication_journal', metadata,
    uuid_column('id'), sa.Column('namespace', sa.String(160), nullable=False),
    sa.Column('key_digest', sa.String(64), nullable=False),
    sa.Column('plan_digest', sa.String(64), nullable=False),
    sa.Column('plan', sa.JSON().with_variant(JSONB(), 'postgresql'), nullable=False),
    sa.Column('release_id', sa.String(160), nullable=False),
    sa.Column('manifest_digest', sa.String(64), nullable=False),
    uuid_column('owner_id'), sa.Column('fence_generation', sa.BigInteger(), nullable=False),
    timestamp('lease_until'), sa.Column('phase', sa.String(32), nullable=False),
    sa.Column('db_committed', sa.Boolean(), nullable=False),
    sa.Column('activation_status', sa.String(24), nullable=False),
    sa.Column('error_code', sa.String(64), nullable=True), timestamp('created_at'), timestamp('updated_at'),
    sa.PrimaryKeyConstraint('id', name='target_publication_journal_pkey'),
    sa.UniqueConstraint('namespace', 'key_digest', name='target_publication_key_unique'),
    sa.UniqueConstraint('namespace', 'release_id', name='target_publication_release_unique'),
    sa.UniqueConstraint('id', 'namespace', name='target_journal_namespace_unique'),
    sa.CheckConstraint('fence_generation > 0', name='target_journal_fence_positive'),
    sa.CheckConstraint("phase IN ('VALIDATED','STAGED','DB_COMMITTED','ACTIVATING','ACTIVATED',"
                       "'RECOVERY_REQUIRED','COMPLETE','FAILED_PRECOMMIT')", name='target_journal_phase'),
    sa.CheckConstraint("phase NOT IN ('DB_COMMITTED','ACTIVATING','ACTIVATED','COMPLETE') OR db_committed", name='target_journal_commit_phase'),
    sa.CheckConstraint("phase <> 'FAILED_PRECOMMIT' OR NOT db_committed", name='target_journal_precommit'),
)
gate = sa.Table('target_publication_gate', metadata,
    sa.Column('namespace', sa.String(160), primary_key=True), uuid_column('pending_operation_id', True),
    uuid_column('owner_id', True), sa.Column('fence_generation', sa.BigInteger(), nullable=False), timestamp('lease_until', True),
    sa.ForeignKeyConstraint(['pending_operation_id', 'namespace'], ['target_publication_journal.id', 'target_publication_journal.namespace'],
                            name='target_gate_pending_fk', deferrable=True, initially='DEFERRED'),
    sa.CheckConstraint('fence_generation >= 0', name='target_gate_fence_nonnegative'),
    sa.CheckConstraint('(pending_operation_id IS NULL AND owner_id IS NULL AND lease_until IS NULL) OR '
                       '(pending_operation_id IS NOT NULL AND owner_id IS NOT NULL AND lease_until IS NOT NULL AND fence_generation > 0)',
                       name='target_gate_pending_tuple'),
)
active = sa.Table('target_active_release', metadata,
    sa.Column('namespace', sa.String(160), primary_key=True), uuid_column('operation_id'),
    sa.Column('release_id', sa.String(160), nullable=False), sa.Column('manifest_digest', sa.String(64), nullable=False),
    sa.Column('fence_generation', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['namespace'], ['target_publication_gate.namespace'], name='target_active_gate_fk', deferrable=True, initially='DEFERRED'),
    sa.ForeignKeyConstraint(['operation_id', 'namespace'], ['target_publication_journal.id', 'target_publication_journal.namespace'], name='target_active_journal_fk', deferrable=True, initially='DEFERRED'),
    sa.CheckConstraint('fence_generation > 0', name='target_active_fence_positive'),
)
history = sa.Table('target_publication_history', metadata,
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), sa.Identity(), primary_key=True),
    uuid_column('operation_id'), uuid_column('owner_id'), sa.Column('fence_generation', sa.BigInteger(), nullable=False),
    sa.Column('phase', sa.String(32), nullable=False), timestamp('recorded_at'), sa.Column('error_code', sa.String(64), nullable=True),
    sa.ForeignKeyConstraint(['operation_id'], ['target_publication_journal.id'], name='target_history_journal_fk', deferrable=True, initially='DEFERRED'),
    sa.CheckConstraint('fence_generation > 0', name='target_history_fence_positive'),
)
session = sa.Table('target_session', metadata,
    uuid_column('id'), uuid_column('lineage_id'), sa.Column('token_digest', sa.String(64), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False), sa.Column('auth_hash', sa.String(128), nullable=False),
    sa.Column('revocation_epoch', sa.BigInteger(), nullable=False), timestamp('created_at'), timestamp('expires_at'), timestamp('revoked_at', True),
    sa.PrimaryKeyConstraint('id', name='target_session_pkey'),
    sa.UniqueConstraint('token_digest', name='target_session_token_unique'),
    sa.ForeignKeyConstraint(['user_id'], ['auth_user.id'], name='target_session_user_fk', deferrable=True, initially='DEFERRED'),
    sa.CheckConstraint('revocation_epoch >= 0', name='target_session_epoch_nonnegative'),
)
checkpoint = sa.Table('target_identity_cutover', metadata,
    uuid_column('id'), sa.Column('checkpoint_digest', sa.String(64), nullable=False),
    sa.Column('provenance_digest', sa.String(64), nullable=False), timestamp('verified_at'),
    sa.PrimaryKeyConstraint('id', name='target_cutover_pkey'), sa.UniqueConstraint('checkpoint_digest', name='target_checkpoint_unique'),
)
bridge = sa.Table('target_receipt_bridge', metadata,
    uuid_column('id'), sa.Column('original_scope', sa.String(80), nullable=False),
    sa.Column('bootstrap_fingerprint', sa.String(64), nullable=False), sa.Column('owner_user_id', sa.Integer(), nullable=True),
    sa.Column('state', sa.String(16), nullable=False), uuid_column('session_lineage_id', True), uuid_column('session_id', True),
    sa.Column('revocation_epoch', sa.BigInteger(), nullable=False), timestamp('created_at'), timestamp('replay_until'),
    sa.Column('ticket_version', sa.BigInteger(), nullable=False), timestamp('ticket_expires_at', True), timestamp('ticket_revoked_at', True),
    uuid_column('cutover_checkpoint_id', True), sa.Column('transfer_binding_digest', sa.String(64), nullable=True),
    sa.PrimaryKeyConstraint('id', name='target_bridge_pkey'),
    sa.UniqueConstraint('original_scope', 'bootstrap_fingerprint', name='target_bridge_scope_unique'),
    sa.ForeignKeyConstraint(['owner_user_id'], ['auth_user.id'], name='target_bridge_owner_fk', deferrable=True, initially='DEFERRED'),
    sa.ForeignKeyConstraint(['session_id'], ['target_session.id'], name='target_bridge_session_fk', deferrable=True, initially='DEFERRED'),
    sa.ForeignKeyConstraint(['cutover_checkpoint_id'], ['target_identity_cutover.id'], name='target_bridge_cutover_fk', deferrable=True, initially='DEFERRED'),
    sa.CheckConstraint("state IN ('ACTIVE','DETACHED','REVOKED','EXPIRED')", name='target_bridge_state'),
    sa.CheckConstraint('revocation_epoch >= 0 AND ticket_version >= 0', name='target_bridge_counters'),
    sa.CheckConstraint("(state = 'ACTIVE' AND owner_user_id IS NOT NULL AND session_id IS NOT NULL AND session_lineage_id IS NOT NULL) OR "
                       "(state <> 'ACTIVE' AND session_id IS NULL)", name='target_bridge_binding'),
    sa.CheckConstraint('replay_until >= created_at', name='target_bridge_time_order'),
)
sa.Index('target_session_lineage_idx', session.c.lineage_id)
sa.Index('target_session_expiry_idx', session.c.expires_at)
sa.Index('target_bridge_lineage_idx', bridge.c.session_lineage_id)
sa.Index('target_bridge_expiry_idx', bridge.c.replay_until)
# The retention interval is dialect-specific; SQL alone cannot enforce no revival.
bridge.append_constraint(sa.CheckConstraint("replay_until >= created_at + interval '604800 seconds'", name='target_bridge_min_retention').ddl_if(dialect='postgresql'))


class PublicationJournal: pass
class PublicationGate: pass
class ActiveReleaseDescriptor: pass
class PublicationHistory: pass
class TargetSession: pass
class CutoverCheckpoint: pass
class ReceiptBridge: pass


PROTOCOL_TABLES = [journal, gate, active, history, session, checkpoint, bridge]
for model, table in zip([PublicationJournal, PublicationGate, ActiveReleaseDescriptor, PublicationHistory,
                         TargetSession, CutoverCheckpoint, ReceiptBridge], PROTOCOL_TABLES):
    mapper_registry.map_imperatively(model, table)
