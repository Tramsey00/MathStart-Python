"""Complete immutable submitted attempts and add Assessment result authority."""
from alembic import op
from backend.assessment.attempt_models import FINALIZATION_TABLES

revision = 'v01_0009'
down_revision = 'v01_0008'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    with op.batch_alter_table('assessment_attempt') as batch:
        for name in ('state', 'snapshot', 'reviewed_time'):
            batch.drop_constraint(f'assessment_attempt_{name}', type_='check')
        batch.create_check_constraint('assessment_attempt_state',
            "state IN ('STARTED','SUBMITTED','COMPLETED','REVIEWED','ABANDONED')")
        batch.create_check_constraint('assessment_attempt_snapshot',
            "(state IN ('SUBMITTED','COMPLETED') AND snapshot_digest IS NOT NULL AND operation_id IS NOT NULL "
            "AND submitted_at IS NOT NULL) OR (state NOT IN ('SUBMITTED','COMPLETED') AND snapshot_digest IS NULL "
            "AND operation_id IS NULL AND submitted_at IS NULL)")
        batch.create_check_constraint('assessment_attempt_terminal_time',
            "(state IN ('REVIEWED','COMPLETED')) = (completed_at IS NOT NULL) "
            "AND (state <> 'COMPLETED' OR completed_at >= submitted_at)")
    for table in FINALIZATION_TABLES:
        table.create(connection, checkfirst=False)
    if connection.dialect.name != 'postgresql':
        return
    op.execute("""
        CREATE OR REPLACE FUNCTION public.assessment_guard_attempt() RETURNS trigger
        LANGUAGE plpgsql SET search_path = pg_catalog, public AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                IF NEW.state = 'STARTED' AND NEW.revision = 1 AND NEW.snapshot_digest IS NULL
                   AND NEW.operation_id IS NULL AND NEW.submitted_at IS NULL AND NEW.completed_at IS NULL
                   THEN RETURN NEW; END IF;
            ELSIF TG_OP = 'UPDATE' AND NEW.id = OLD.id AND NEW.user_id = OLD.user_id
                AND NEW.version_id = OLD.version_id AND NEW.created_at = OLD.created_at
                AND NEW.previous_attempt_id IS NOT DISTINCT FROM OLD.previous_attempt_id THEN
                IF OLD.state = 'STARTED' THEN
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
                ELSIF OLD.state = 'SUBMITTED' AND NEW.state = 'COMPLETED'
                    AND NEW.revision = OLD.revision AND NEW.draft = OLD.draft
                    AND NEW.snapshot_digest = OLD.snapshot_digest AND NEW.operation_id = OLD.operation_id
                    AND NEW.submitted_at = OLD.submitted_at
                    AND EXISTS (
                        SELECT 1 FROM public.assessment_analysis_record
                        WHERE attempt_id = OLD.id AND operation_id = OLD.operation_id AND snapshot_digest = OLD.snapshot_digest
                    ) THEN
                    RETURN NEW;
                END IF;
            END IF;
            RAISE EXCEPTION 'Invalid Attempt mutation' USING ERRCODE = '23514';
        END;
        $$
    """)
    for table in FINALIZATION_TABLES:
        op.execute(f'CREATE TRIGGER {table.name}_guard BEFORE UPDATE OR DELETE ON public.{table.name} '
                   'FOR EACH ROW EXECUTE FUNCTION public.assessment_guard_history()')
        op.execute(f'CREATE TRIGGER {table.name}_truncate_guard BEFORE TRUNCATE ON public.{table.name} '
                   'FOR EACH STATEMENT EXECUTE FUNCTION public.assessment_guard_truncate()')


def downgrade():
    raise RuntimeError('Finalized Assessment history requires additive forward repair')
