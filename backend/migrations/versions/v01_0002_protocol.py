"""R02 additive protocol facts only. V03/V04 own lifecycle/domain behavior."""
from alembic import op
from backend.models.baseline import metadata
from backend.models.protocol import PROTOCOL_TABLES

revision = 'v01_0002'
down_revision = 'v01_0001'
branch_labels = None
depends_on = None


def upgrade():
    metadata.create_all(op.get_bind(), tables=PROTOCOL_TABLES, checkfirst=False)


def downgrade():
    raise RuntimeError('Evidence-preserving migrations require additive forward repair')
