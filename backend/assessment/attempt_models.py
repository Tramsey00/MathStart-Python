"""Assessment-owned learner history. No Progress or mathematical evaluation."""
import sqlalchemy as sa

from backend.models.baseline import metadata, User
from .models import JSON_VALUE, version

exposure = sa.Table(
    'assessment_exposure', metadata,
    sa.Column('user_id', User.__table__.c.id.type, sa.ForeignKey('auth_user.id', ondelete='RESTRICT'), primary_key=True),
    sa.Column('version_id', sa.Uuid, sa.ForeignKey(version.c.id, ondelete='RESTRICT'), primary_key=True),
    sa.Column('max_help_level', sa.SmallInteger, nullable=False),
    sa.Column('revealed_at', sa.DateTime(timezone=True)),
    sa.Column('positive_credit_used', sa.Boolean, nullable=False),
    sa.CheckConstraint('max_help_level BETWEEN 0 AND 3', name='assessment_exposure_level'),
)

attempt = sa.Table(
    'assessment_attempt', metadata,
    sa.Column('id', sa.Uuid, primary_key=True),
    sa.Column('user_id', User.__table__.c.id.type, nullable=False),
    sa.Column('version_id', sa.Uuid, nullable=False),
    sa.Column('previous_attempt_id', sa.Uuid),
    sa.Column('revision', sa.Integer, nullable=False),
    sa.Column('state', sa.String(12), nullable=False),
    sa.Column('draft', JSON_VALUE, nullable=False),
    sa.Column('snapshot_digest', sa.String(64)),
    sa.Column('operation_id', sa.Uuid, unique=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('submitted_at', sa.DateTime(timezone=True)),
    sa.Column('completed_at', sa.DateTime(timezone=True)),
    sa.ForeignKeyConstraint(['user_id', 'version_id'], [exposure.c.user_id, exposure.c.version_id], ondelete='RESTRICT'),
    sa.UniqueConstraint('id', 'user_id', 'version_id', name='assessment_attempt_binding'),
    sa.ForeignKeyConstraint(['previous_attempt_id', 'user_id', 'version_id'],
                           ['assessment_attempt.id', 'assessment_attempt.user_id', 'assessment_attempt.version_id'],
                           ondelete='RESTRICT'),
    sa.CheckConstraint('revision >= 1', name='assessment_attempt_revision'),
    sa.CheckConstraint("state IN ('STARTED','SUBMITTED','REVIEWED','ABANDONED')", name='assessment_attempt_state'),
    sa.CheckConstraint("(state = 'SUBMITTED' AND snapshot_digest IS NOT NULL AND operation_id IS NOT NULL "
                       "AND submitted_at IS NOT NULL) OR (state <> 'SUBMITTED' AND snapshot_digest IS NULL "
                       "AND operation_id IS NULL AND submitted_at IS NULL)", name='assessment_attempt_snapshot'),
    sa.CheckConstraint("(state = 'REVIEWED') = (completed_at IS NOT NULL)", name='assessment_attempt_reviewed_time'),
    sa.CheckConstraint('previous_attempt_id IS NULL OR previous_attempt_id <> id', name='assessment_attempt_previous'),
    sa.Index('ix_assessment_attempt_owner_order', 'user_id', 'created_at', 'id'),
)

step = sa.Table(
    'assessment_solution_step', metadata,
    sa.Column('id', sa.Uuid, primary_key=True),
    sa.Column('attempt_id', sa.Uuid, sa.ForeignKey(attempt.c.id, ondelete='RESTRICT'), nullable=False),
    sa.Column('step_no', sa.Integer, nullable=False),
    sa.Column('step_type', sa.String(20), nullable=False),
    sa.Column('payload', JSON_VALUE, nullable=False),
    sa.Column('raw_text', sa.Text),
    sa.Column('normalized_repr', sa.Text),
    sa.Column('parse_status', sa.String(12), nullable=False),
    sa.UniqueConstraint('attempt_id', 'step_no', name='assessment_step_order'),
    sa.CheckConstraint('step_no BETWEEN 1 AND 40', name='assessment_step_number'),
    sa.CheckConstraint("step_type IN ('MATH_EXPRESSION','EQUATION_STATE','STRUCTURED_FIELDS','FINAL_STATEMENT')",
                       name='assessment_step_type'),
    sa.CheckConstraint("parse_status IN ('OK','UNSUPPORTED','INVALID','NOT_REQUIRED')", name='assessment_step_parse'),
)

action = sa.Table(
    'assessment_action', metadata,
    sa.Column('id', sa.Uuid, primary_key=True),
    sa.Column('user_id', User.__table__.c.id.type, nullable=False),
    sa.Column('version_id', sa.Uuid, nullable=False),
    sa.Column('attempt_id', sa.Uuid, nullable=False),
    sa.Column('operation', sa.String(24), nullable=False),
    sa.Column('key_digest', sa.String(64), nullable=False),
    sa.Column('request_digest', sa.String(64), nullable=False),
    sa.Column('response', JSON_VALUE, nullable=False),
    sa.Column('status', sa.SmallInteger, nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['attempt_id', 'user_id', 'version_id'],
                           [attempt.c.id, attempt.c.user_id, attempt.c.version_id], ondelete='RESTRICT'),
    sa.UniqueConstraint('user_id', 'operation', 'key_digest', name='assessment_action_identity'),
)

event = sa.Table(
    'assessment_attempt_event', metadata,
    sa.Column('id', sa.Uuid, primary_key=True),
    sa.Column('attempt_id', sa.Uuid, sa.ForeignKey(attempt.c.id, ondelete='RESTRICT'), nullable=False),
    sa.Column('action_id', sa.Uuid, sa.ForeignKey(action.c.id, ondelete='RESTRICT'), nullable=False, unique=True),
    sa.Column('type', sa.String(24), nullable=False),
    sa.Column('help_level', sa.SmallInteger),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('request_id', sa.Uuid, nullable=False),
)

hint = sa.Table(
    'assessment_reviewed_hint', metadata,
    sa.Column('version_id', sa.Uuid, sa.ForeignKey(version.c.id, ondelete='RESTRICT'), primary_key=True),
    sa.Column('level', sa.SmallInteger, primary_key=True),
    sa.Column('text', sa.Text, nullable=False),
    sa.Column('reviewed_digest', sa.String(64), nullable=False),
    sa.CheckConstraint('level BETWEEN 1 AND 3', name='assessment_hint_level'),
    sa.CheckConstraint('length(text) BETWEEN 1 AND 512', name='assessment_hint_text'),
)

ATTEMPT_TABLES = (exposure, attempt, step, action, event, hint)
