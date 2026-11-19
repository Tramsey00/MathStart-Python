"""Assessment identities, immutable versions, and server-only validation."""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from backend.content.topic_skill_model import content_page
from backend.knowledge.models import skill
from backend.models.baseline import metadata

JSON_VALUE = sa.JSON().with_variant(JSONB(), 'postgresql')

exercise = sa.Table(
    'assessment_exercise', metadata,
    sa.Column('id', sa.Uuid, primary_key=True),
    sa.Column('code', sa.String(64), nullable=False, unique=True),
    sa.Column('topic_id', content_page.c.id.type,
              sa.ForeignKey(content_page.c.id, ondelete='RESTRICT'), nullable=False, index=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
)

version = sa.Table(
    'assessment_exercise_version', metadata,
    sa.Column('id', sa.Uuid, primary_key=True),
    sa.Column('exercise_id', sa.Uuid, sa.ForeignKey(exercise.c.id, ondelete='RESTRICT'), nullable=False),
    sa.Column('version', sa.Integer, nullable=False),
    sa.Column('status', sa.String(9), nullable=False),
    sa.Column('mode', sa.String(19), nullable=False),
    sa.Column('difficulty', sa.SmallInteger, nullable=False),
    sa.Column('statement', sa.Text, nullable=False),
    sa.Column('public_schema', JSON_VALUE, nullable=False),
    sa.Column('schema_code', sa.String(48), nullable=False),
    sa.Column('provenance', sa.String(255), nullable=False),
    sa.Column('digest', sa.String(64), nullable=False),
    sa.UniqueConstraint('exercise_id', 'version', name='assessment_version_number'),
    sa.CheckConstraint('version > 0', name='assessment_version_positive'),
    sa.CheckConstraint("status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')", name='assessment_version_status'),
    sa.CheckConstraint("mode IN ('SELF_CHECK', 'FINAL_ANSWER', 'STEP_BY_STEP', 'STRUCTURED_SOLUTION')",
                       name='assessment_version_mode'),
    sa.CheckConstraint('difficulty BETWEEN 1 AND 4', name='assessment_version_difficulty'),
    sa.Index('ix_assessment_version_selection', 'status', 'mode', 'difficulty'),
    sa.Index('ix_assessment_version_current', 'exercise_id', unique=True,
             postgresql_where=sa.text("status = 'PUBLISHED'"), sqlite_where=sa.text("status = 'PUBLISHED'")),
)

validation = sa.Table(
    'assessment_exercise_validation', metadata,
    sa.Column('version_id', sa.Uuid, sa.ForeignKey(version.c.id, ondelete='RESTRICT'), primary_key=True),
    sa.Column('checker_type', sa.String(48), nullable=False),
    sa.Column('checker_version', sa.Integer, nullable=False),
    sa.Column('answer_key', JSON_VALUE, nullable=False),
    sa.Column('accepted_variants', JSON_VALUE, nullable=False),
    sa.Column('validation_spec', JSON_VALUE, nullable=False),
    sa.Column('canonical_solution', JSON_VALUE, nullable=False),
    sa.Column('digest', sa.String(64), nullable=False),
    sa.CheckConstraint('checker_version > 0', name='assessment_checker_version'),
)

exercise_skill = sa.Table(
    'assessment_exercise_skill', metadata,
    sa.Column('version_id', sa.Uuid, sa.ForeignKey(version.c.id, ondelete='RESTRICT'), primary_key=True),
    sa.Column('skill_id', sa.Uuid, sa.ForeignKey(skill.c.id, ondelete='RESTRICT'), primary_key=True, index=True),
    sa.Column('role', sa.String(9), nullable=False),
    sa.CheckConstraint("role IN ('PRIMARY', 'SECONDARY')", name='assessment_exercise_skill_role'),
    sa.Index('ix_assessment_version_primary', 'version_id', unique=True,
             postgresql_where=sa.text("role = 'PRIMARY'"), sqlite_where=sa.text("role = 'PRIMARY'")),
)

ASSESSMENT_TABLES = (exercise, version, validation, exercise_skill)
