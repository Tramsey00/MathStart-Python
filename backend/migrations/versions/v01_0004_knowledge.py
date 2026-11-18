"""Add Knowledge and the Content-owned topic mapping without importing data."""
from alembic import op

from backend.content.topic_skill_model import topic_skill
from backend.knowledge.models import KNOWLEDGE_TABLES


revision = 'v01_0004'
down_revision = 'v01_0003'
branch_labels = None
depends_on = None


def upgrade():
    for table in (*KNOWLEDGE_TABLES, topic_skill):
        table.create(op.get_bind(), checkfirst=False)


def downgrade():
    raise RuntimeError('Knowledge identities and mappings require additive forward repair')
