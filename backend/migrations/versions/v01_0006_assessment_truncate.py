"""Reject statements that bypass Assessment's row-level history guards."""
from alembic import op

revision = 'v01_0006'
down_revision = 'v01_0005'
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name == 'sqlite':
        return

    op.execute("""
        CREATE FUNCTION public.assessment_guard_truncate() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public AS $$
        BEGIN
            RAISE EXCEPTION 'Assessment history cannot be truncated' USING ERRCODE = '23514';
        END;
        $$
    """)
    for name in ('assessment_exercise', 'assessment_exercise_version',
                 'assessment_exercise_validation', 'assessment_exercise_skill'):
        op.execute(f"""
            CREATE TRIGGER {name}_truncate_guard BEFORE TRUNCATE ON public.{name}
            FOR EACH STATEMENT EXECUTE FUNCTION public.assessment_guard_truncate()
        """)


def downgrade():
    raise RuntimeError('Assessment history requires additive forward repair')
