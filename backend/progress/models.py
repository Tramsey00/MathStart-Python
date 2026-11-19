"""Progress-owned persistence; source identities are retained, never cascaded."""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from backend.models.baseline import metadata, User
from backend.knowledge.models import skill

JSON = sa.JSON().with_variant(JSONB(), 'postgresql')


def owner():
    return sa.Column('user_id', User.__table__.c.id.type, sa.ForeignKey('auth_user.id', ondelete='RESTRICT'), nullable=False)


def skill_column():
    return sa.Column('skill_id', sa.Uuid, sa.ForeignKey(skill.c.id, ondelete='RESTRICT'), nullable=False)


attempt_binding = sa.Table('progress_attempt_binding', metadata,
    sa.Column('attempt_id', sa.Text, primary_key=True), owner(),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('version_id', sa.Text, nullable=False))

event = sa.Table('progress_event', metadata,
    sa.Column('event_id', sa.Text, primary_key=True), owner(), skill_column(),
    sa.Column('attempt_id', sa.Text), sa.Column('event_kind', sa.String(32), nullable=False),
    sa.Column('evidence_ref', sa.Text),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('policy_version', sa.String(32), nullable=False),
    sa.Column('payload', JSON, nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.UniqueConstraint('attempt_id', 'skill_id', 'event_kind', 'evidence_ref', name='progress_event_source'),
    sa.CheckConstraint("policy_version = 'progress-v1'", name='progress_event_policy'),
    sa.Index('ix_progress_event_self_report', 'user_id', 'skill_id', unique=True,
        postgresql_where=sa.text("event_kind = 'SELF_REPORTED_KNOWN'"), sqlite_where=sa.text("event_kind = 'SELF_REPORTED_KNOWN'")),
    sa.Index('ix_progress_event_order', 'user_id', 'skill_id', 'occurred_at', 'event_id'))

completion = sa.Table('progress_completion', metadata,
    sa.Column('completion_id', sa.Uuid, primary_key=True), owner(), skill_column(),
    sa.Column('attempt_id', sa.Text, sa.ForeignKey(attempt_binding.c.attempt_id, ondelete='RESTRICT'), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('policy_version', sa.String(32), nullable=False),
    sa.Column('payload', JSON, nullable=False),
    sa.Column('authority', JSON, nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.UniqueConstraint('attempt_id', 'skill_id', name='progress_completion_source'),
    sa.CheckConstraint("policy_version = 'progress-v1.1'", name='progress_completion_policy'),
    sa.Index('ix_progress_completion_order', 'user_id', 'skill_id', 'completed_at', 'attempt_id'))

state = sa.Table('progress_user_skill_state', metadata, owner(), skill_column(),
    sa.Column('mastery', sa.Numeric(5, 2), nullable=False),
    sa.Column('confidence', sa.Numeric(5, 2), nullable=False),
    sa.Column('evidence_count', sa.Integer, nullable=False),
    sa.Column('status', sa.String(12), nullable=False),
    sa.Column('last_updated', sa.DateTime(timezone=True)),
    sa.Column('reducer_version', sa.String(32), nullable=False),
    sa.Column('numerical', JSON, nullable=False), sa.Column('event_digest', sa.String(64), nullable=False),
    sa.Column('result', JSON, nullable=False),
    sa.PrimaryKeyConstraint('user_id', 'skill_id'),
    sa.CheckConstraint('mastery BETWEEN 0 AND 100 AND confidence BETWEEN 0 AND 100 AND evidence_count >= 0', name='progress_state_bounds'),
    sa.CheckConstraint("reducer_version = 'progress-v1.1'", name='progress_state_policy'),
    sa.CheckConstraint("status IN ('NOT_STARTED','LEARNING','WEAK','MASTERED')", name='progress_state_status'))

receipt = sa.Table('progress_self_report_receipt', metadata, owner(),
    sa.Column('key_digest', sa.String(64), nullable=False),
    sa.Column('request_digest', sa.String(64), nullable=False),
    sa.Column('response', JSON, nullable=False),
    sa.PrimaryKeyConstraint('user_id', 'key_digest'))

PROGRESS_TABLES = (attempt_binding, event, completion, state, receipt)
