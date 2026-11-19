"""Append-only Progress evidence/mirror and exact rebuildable projection."""
from alembic import op
from backend.progress.models import PROGRESS_TABLES

revision = 'v01_0008'
down_revision = 'v01_0007'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    for table in PROGRESS_TABLES:
        table.create(connection, checkfirst=False)
    if connection.dialect.name != 'postgresql':
        return
    op.execute("""
        CREATE FUNCTION public.progress_guard_history() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public AS $$
        BEGIN
            RAISE EXCEPTION 'Progress source history is immutable' USING ERRCODE = '23514';
        END;
        $$
    """)
    for table in PROGRESS_TABLES:
        if table.name != 'progress_user_skill_state':
            op.execute(f'CREATE TRIGGER {table.name}_history_guard BEFORE UPDATE OR DELETE ON public.{table.name} '
                       'FOR EACH ROW EXECUTE FUNCTION public.progress_guard_history()')
        op.execute(f'CREATE TRIGGER {table.name}_truncate_guard BEFORE TRUNCATE ON public.{table.name} '
                   'FOR EACH STATEMENT EXECUTE FUNCTION public.progress_guard_history()')


def downgrade():
    raise RuntimeError('Progress history requires additive forward repair')
