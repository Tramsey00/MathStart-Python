"""SQLAlchemy storage for stable Knowledge identities and directed edges."""
import sqlalchemy as sa

from backend.models.baseline import metadata


skill = sa.Table(
    'knowledge_skill', metadata,
    sa.Column('id', sa.Uuid, primary_key=True),
    sa.Column('code', sa.String(64), nullable=False, unique=True),
    sa.Column('name', sa.String(160), nullable=False),
    sa.Column('description', sa.Text),
    sa.Column('grade_min', sa.SmallInteger),
    sa.Column('grade_max', sa.SmallInteger),
    sa.Column('active', sa.Boolean, nullable=False),
    sa.Column('graph_version', sa.String(32), nullable=False),
    sa.CheckConstraint("length(code) > 0 AND length(name) > 0 AND length(graph_version) > 0",
                       name='knowledge_skill_nonempty'),
    sa.CheckConstraint('(grade_min IS NULL AND grade_max IS NULL) OR '
                       '(grade_min IS NOT NULL AND grade_max IS NOT NULL AND '
                       'grade_min >= 1 AND grade_min <= grade_max AND grade_max <= 11)',
                       name='knowledge_skill_grades'),
)

skill_dependency = sa.Table(
    'knowledge_skill_dependency', metadata,
    sa.Column('id', sa.Uuid, primary_key=True),
    sa.Column('prerequisite_id', sa.Uuid, sa.ForeignKey(skill.c.id, ondelete='RESTRICT'), nullable=False),
    sa.Column('dependent_id', sa.Uuid, sa.ForeignKey(skill.c.id, ondelete='RESTRICT'), nullable=False, index=True),
    sa.Column('weight', sa.Numeric(), nullable=False),
    sa.UniqueConstraint('prerequisite_id', 'dependent_id', name='knowledge_dependency_pair'),
    sa.CheckConstraint('prerequisite_id <> dependent_id', name='knowledge_dependency_no_self'),
    sa.CheckConstraint('weight > 0 AND weight <= 1', name='knowledge_dependency_weight'),
)

KNOWLEDGE_TABLES = (skill, skill_dependency)
