"""Persist attempts, immutable action responses and cross-attempt exposure."""
from alembic import op
from backend.assessment.attempt_models import ATTEMPT_TABLES

revision = 'v01_0007'
down_revision = 'v01_0006'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    for table in ATTEMPT_TABLES:
        table.create(connection, checkfirst=False)
    if connection.dialect.name == 'sqlite':
        return  # schema rehearsal only; no claim of concurrency parity
    op.execute("""
        CREATE FUNCTION public.assessment_guard_attempt() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                IF NEW.state = 'STARTED' AND NEW.revision = 1 AND NEW.snapshot_digest IS NULL
                   AND NEW.operation_id IS NULL AND NEW.submitted_at IS NULL AND NEW.completed_at IS NULL
                   THEN RETURN NEW; END IF;
            ELSIF TG_OP = 'UPDATE' AND OLD.state = 'STARTED'
                AND NEW.id = OLD.id AND NEW.user_id = OLD.user_id AND NEW.version_id = OLD.version_id
                AND NEW.previous_attempt_id IS NOT DISTINCT FROM OLD.previous_attempt_id
                AND NEW.created_at = OLD.created_at THEN
                IF NEW.state IN ('STARTED','SUBMITTED','ABANDONED') AND NEW.revision = OLD.revision + 1 THEN
                    IF NEW.state = 'STARTED' OR NEW.draft = OLD.draft THEN
                        IF NEW.state <> 'SUBMITTED' OR NOT EXISTS (
                            SELECT 1 FROM public.assessment_exercise_version WHERE id = OLD.version_id AND mode = 'SELF_CHECK'
                        ) THEN RETURN NEW; END IF;
                    END IF;
                ELSIF NEW.state = 'REVIEWED' AND NEW.revision = OLD.revision AND NEW.draft = OLD.draft
                    AND EXISTS (SELECT 1 FROM public.assessment_exercise_version WHERE id = OLD.version_id AND mode = 'SELF_CHECK')
                    AND EXISTS (SELECT 1 FROM public.assessment_exposure WHERE user_id = OLD.user_id
                                AND version_id = OLD.version_id AND revealed_at IS NOT NULL) THEN
                    RETURN NEW;
                END IF;
            END IF;
            RAISE EXCEPTION 'Invalid Attempt mutation' USING ERRCODE = '23514';
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER assessment_attempt_guard BEFORE INSERT OR UPDATE OR DELETE ON public.assessment_attempt
        FOR EACH ROW EXECUTE FUNCTION public.assessment_guard_attempt()
    """)
    op.execute("""
        CREATE FUNCTION public.assessment_guard_step() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public AS $$
        DECLARE parent_id uuid; parent_state text;
        BEGIN
            IF TG_OP = 'UPDATE' AND (NEW.id <> OLD.id OR NEW.attempt_id <> OLD.attempt_id) THEN
                RAISE EXCEPTION 'Step identity is immutable' USING ERRCODE = '23514';
            END IF;
            IF TG_OP = 'DELETE' THEN parent_id := OLD.attempt_id; ELSE parent_id := NEW.attempt_id; END IF;
            SELECT state INTO parent_state FROM public.assessment_attempt WHERE id = parent_id FOR UPDATE;
            IF parent_state IS DISTINCT FROM 'STARTED' THEN
                RAISE EXCEPTION 'Submitted steps are immutable' USING ERRCODE = '23514';
            END IF;
            IF TG_OP = 'DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER assessment_step_guard BEFORE INSERT OR UPDATE OR DELETE ON public.assessment_solution_step
        FOR EACH ROW EXECUTE FUNCTION public.assessment_guard_step()
    """)
    op.execute("""
        CREATE FUNCTION public.assessment_guard_exposure() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public AS $$
        BEGIN
            IF TG_OP = 'UPDATE' AND NEW.user_id = OLD.user_id AND NEW.version_id = OLD.version_id
               AND NEW.max_help_level >= OLD.max_help_level
               AND (OLD.revealed_at IS NULL OR NEW.revealed_at IS NOT DISTINCT FROM OLD.revealed_at)
               AND (NOT OLD.positive_credit_used OR NEW.positive_credit_used) THEN RETURN NEW; END IF;
            RAISE EXCEPTION 'Exposure cannot be reset' USING ERRCODE = '23514';
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER assessment_exposure_guard BEFORE UPDATE OR DELETE ON public.assessment_exposure
        FOR EACH ROW EXECUTE FUNCTION public.assessment_guard_exposure()
    """)
    op.execute("""
        CREATE FUNCTION public.assessment_guard_history() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public AS $$
        BEGIN
            RAISE EXCEPTION 'Assessment action history is immutable' USING ERRCODE = '23514';
        END;
        $$
    """)
    for table in ('assessment_action', 'assessment_attempt_event', 'assessment_reviewed_hint'):
        op.execute(f'CREATE TRIGGER {table}_guard BEFORE UPDATE OR DELETE ON public.{table} '
                   'FOR EACH ROW EXECUTE FUNCTION public.assessment_guard_history()')
    for table in ATTEMPT_TABLES:
        op.execute(f'CREATE TRIGGER {table.name}_truncate_guard BEFORE TRUNCATE ON public.{table.name} '
                   'FOR EACH STATEMENT EXECUTE FUNCTION public.assessment_guard_truncate()')


def downgrade():
    raise RuntimeError('Attempt history requires additive forward repair')
