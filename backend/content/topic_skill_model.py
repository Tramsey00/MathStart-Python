"""Content-owned mapping to retained lesson identities and Knowledge skills."""
import sqlalchemy as sa

from backend.knowledge.models import skill
from backend.models.baseline import metadata


content_page = metadata.tables['content_contentpage']
topic_skill = sa.Table(
    'content_topic_skill', metadata,
    sa.Column('id', sa.Uuid, primary_key=True),
    sa.Column('content_page_id', content_page.c.id.type,
              sa.ForeignKey(content_page.c.id, ondelete='RESTRICT'), nullable=False),
    sa.Column('skill_id', sa.Uuid, sa.ForeignKey(skill.c.id, ondelete='RESTRICT'), nullable=False, index=True),
    sa.Column('role', sa.String(9), nullable=False),
    sa.Column('importance', sa.Numeric(), nullable=False),
    sa.Column('position', sa.Integer, nullable=False),
    sa.Column('mapping_version', sa.String(32), nullable=False),
    sa.UniqueConstraint('content_page_id', 'skill_id', name='content_topic_skill_pair'),
    sa.CheckConstraint("role IN ('PRIMARY', 'SECONDARY')", name='content_topic_skill_role'),
    sa.CheckConstraint("importance > 0 AND importance < CAST('Infinity' AS NUMERIC)",
                       name='content_topic_skill_importance'),
    sa.CheckConstraint('position >= 0', name='content_topic_skill_position'),
    sa.CheckConstraint('length(mapping_version) > 0', name='content_topic_skill_version'),
    sa.Index('ix_content_topic_skill_page_role', 'content_page_id', 'role'),
)
