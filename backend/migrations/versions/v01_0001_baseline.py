"""Django-independent baseline; existing DBs use the guarded upgrade adapter."""
from alembic import op
import sqlalchemy as sa
from backend.models.baseline import metadata, SNAPSHOT

revision = 'v01_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    existing = set(sa.inspect(connection).get_table_names()) - {'alembic_version'}
    if existing:
        raise RuntimeError('Fresh install requires an empty database; use reviewed upgrade profiles')
    metadata.create_all(connection, tables=[metadata.tables[m['table']] for m in SNAPSHOT['models']], checkfirst=False)


def downgrade():
    raise RuntimeError('Evidence-preserving migrations require additive forward repair')
