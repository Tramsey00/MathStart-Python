"""Add the Assessment bank and its database-enforced lifecycle."""
from alembic import op

from backend.assessment.models import ASSESSMENT_TABLES

revision = 'v01_0005'
down_revision = 'v01_0004'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    for table in ASSESSMENT_TABLES:
        table.create(connection, checkfirst=False)
    if connection.dialect.name == 'sqlite':
        # The existing SQLite rehearsal is schema-only for Assessment.
        return

    op.execute("""
        CREATE FUNCTION public.assessment_guard_exercise() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public AS $$
        BEGIN
            RAISE EXCEPTION 'Assessment exercise identity is retained' USING ERRCODE = '23514';
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER assessment_guard_exercise BEFORE UPDATE OR DELETE ON public.assessment_exercise
        FOR EACH ROW EXECUTE FUNCTION public.assessment_guard_exercise()
    """)
    op.execute("""
        CREATE FUNCTION public.assessment_guard_version() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                IF NEW.status = 'DRAFT' THEN RETURN NEW; END IF;
            ELSIF TG_OP = 'UPDATE' THEN
                IF (to_jsonb(NEW) - 'status') = (to_jsonb(OLD) - 'status') THEN
                    IF OLD.status = 'PUBLISHED' AND NEW.status = 'ARCHIVED' THEN RETURN NEW; END IF;
                    IF OLD.status = 'DRAFT' AND NEW.status = 'PUBLISHED'
                       AND EXISTS (SELECT 1 FROM public.assessment_exercise_validation WHERE version_id = OLD.id)
                       AND EXISTS (SELECT 1 FROM public.assessment_exercise_skill
                                   WHERE version_id = OLD.id AND role = 'PRIMARY') THEN
                        RETURN NEW;
                    END IF;
                END IF;
            END IF;
            RAISE EXCEPTION 'Invalid Assessment version change' USING ERRCODE = '23514';
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER assessment_guard_version BEFORE INSERT OR UPDATE OR DELETE ON public.assessment_exercise_version
        FOR EACH ROW EXECUTE FUNCTION public.assessment_guard_version()
    """)
    op.execute("""
        CREATE FUNCTION public.assessment_guard_version_child() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public AS $$
        DECLARE bound_id uuid;
        BEGIN
            IF TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'Assessment version data is retained' USING ERRCODE = '23514';
            END IF;
            bound_id := NEW.version_id;
            PERFORM 1 FROM public.assessment_exercise_version
                WHERE id = bound_id AND status = 'DRAFT' FOR UPDATE;
            IF NOT FOUND THEN
                RAISE EXCEPTION 'Assessment version is sealed' USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END;
        $$
    """)
    for table in ('assessment_exercise_validation', 'assessment_exercise_skill'):
        op.execute(f"""
            CREATE TRIGGER {table}_guard BEFORE INSERT OR UPDATE OR DELETE ON public.{table}
            FOR EACH ROW EXECUTE FUNCTION public.assessment_guard_version_child()
        """)


def downgrade():
    raise RuntimeError('Assessment history requires additive forward repair')
