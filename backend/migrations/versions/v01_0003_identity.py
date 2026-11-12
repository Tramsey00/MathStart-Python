"""Add recovery addresses, purpose-bound tokens, budgets and bounded audit events."""
from alembic import op
from backend.models.identity import IDENTITY_TABLES
revision = 'v01_0003'
down_revision = 'v01_0002'
branch_labels = None
depends_on = None

def upgrade():
    for table in IDENTITY_TABLES:
        table.create(op.get_bind(), checkfirst=False)

def downgrade():
    raise RuntimeError('Identity data requires additive forward repair')
