"""Snapshot-bound analysis and the atomic Assessment/Progress write."""
from dataclasses import asdict, dataclass
import logging
from types import MappingProxyType
from uuid import UUID, uuid5

import sqlalchemy as sa

from backend.infrastructure.database import DatabaseUnavailable
from backend.infrastructure.http import transport as wire
from backend.infrastructure.uow import UnitOfWork
from backend.knowledge.graph import PilotGraphRead
from backend.knowledge.repository import read_pilot_graph
from backend.progress.contracts import Delivery
from backend.progress.service import ProgressService
from backend.solution_analyzer.deterministic import AnalysisUnavailable
from backend.solution_analyzer.model import SubmittedSolution, SubmittedStep, Verdict

from .analysis import ExerciseValidation, analyze_submission
from .attempt_models import analysis_record, attempt, completion_fact, exposure
from .attempts import conflict, identifier, ordered_steps, snapshot_digest, timestamp
from .checker_spec import CheckerSpecError
from .completion_read import SkillMapping, mapped_skills
from .models import validation, version


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class EvaluationInput:
    submission: SubmittedSolution
    exercise: ExerciseValidation
    graph: PilotGraphRead | None
    snapshot_digest: str
    exercise_digest: str
    checker_digest: str
    difficulty: int
    skills: tuple[SkillMapping, ...]


def load_input(session, row, v):
    steps = ordered_steps(session, row.id)
    if snapshot_digest(row, v, steps, row.revision) != row.snapshot_digest:
        raise conflict('STATE_CONFLICT')
    if v.mode == 'SELF_CHECK' or v.status not in ('PUBLISHED', 'ARCHIVED'):
        raise conflict('VERSION_CONFLICT')
    mappings = mapped_skills(session, row.version_id)
    if sum(m.role == 'PRIMARY' for m in mappings) != 1:
        raise wire.unavailable()
    codes = frozenset(m.code for m in mappings)
    private = session.execute(sa.select(
        validation.c.checker_type, validation.c.checker_version, validation.c.answer_key,
        validation.c.accepted_variants, validation.c.validation_spec, validation.c.digest,
    ).where(validation.c.version_id == row.version_id)).one_or_none()
    if private is None:
        raise wire.unavailable()
    checker = ExerciseValidation.from_storage(
        version_id=v.id, schema_code=v.schema_code, checker_type=private.checker_type,
        checker_version=private.checker_version, validation_spec=private.validation_spec,
        answer_key=private.answer_key, accepted_variants=private.accepted_variants, skill_codes=codes,
    )
    submission = SubmittedSolution(
        row.id, v.id, MappingProxyType(row.draft['payload']),
        tuple(SubmittedStep(UUID(s['step_id']), s['step_no'], s['step_type'],
                            MappingProxyType(s['payload']), s['raw_text']) for s in steps),
    )
    return EvaluationInput(submission, checker, read_pilot_graph(session), row.snapshot_digest,
                           v.digest, private.digest, v.difficulty, mappings)


def analysis_payload(result):
    """Store validated evidence identities and versions without private checker input."""
    data = asdict(result)
    if result.blocking_step_id is not None:
        data['blocking_step_id'] = str(result.blocking_step_id)
    for ref in data['evidence_refs']:
        for key in ('attempt_id', 'exercise_version_id', 'step_id', 'previous_step_id'):
            if ref[key] is not None:
                ref[key] = str(ref[key])
    return data


def record_decision(work, row, exposure_row, analysis, completed_at):
    outcome = analysis.verdict
    hinted = bool(exposure_row.max_help_level)
    revealed = exposure_row.revealed_at is not None
    if outcome == Verdict.UNSUPPORTED:
        reason = 'UNSUPPORTED_INPUT'
    elif outcome != Verdict.CORRECT:
        reason = 'NOT_CORRECT'
    elif revealed:
        reason = 'REVEAL_EXPOSURE'
    elif exposure_row.positive_credit_used:
        reason = 'ALREADY_CREDITED'
    else:
        reason = 'HINT_EXPOSURE' if hinted else 'ELIGIBLE'
    awarded = reason in ('ELIGIBLE', 'HINT_EXPOSURE')
    decision = {'independent': reason == 'ELIGIBLE', 'positive_credit_eligible': awarded, 'reason': reason}
    feedback = analysis.safe_feedback
    if (analysis.prefix_status is not None and outcome == Verdict.INDETERMINATE
            and work.exercise.initial_state is None):
        if analysis.final_verdict == Verdict.CORRECT:
            feedback = 'Итоговый ответ верен. Место ошибки в шагах определить не удалось.'
        elif analysis.final_verdict == Verdict.WRONG:
            feedback = 'Итоговый ответ неверен. Место ошибки в шагах определить не удалось.'
    first_error = analysis.first_error_step_id
    result = {'outcome': outcome, 'safe_feedback': feedback, 'service_state': 'NORMAL',
              'first_error_step_id': str(first_error) if first_error else None,
              'misconception_code': analysis.misconception_code}
    progress_event = None
    if awarded or (outcome == Verdict.WRONG and not revealed):
        primary = next(m.code for m in work.skills if m.role == 'PRIMARY')
        code = analysis.misconception_code
        kind = ('CORRECT_AFTER_HINT' if hinted else 'CORRECT_FIRST_TRY') if awarded else (
            'MISCONCEPTION_DETECTED' if code else 'WRONG_ATTEMPT')
        time = timestamp(completed_at)
        progress_event = dict(event_id=str(uuid5(row.operation_id, 'progress-event')), user_id=str(row.user_id),
            skill_id=analysis.skill_codes[0] if code else primary, attempt_id=str(row.id), event_kind=kind,
            occurred_at=time, completed_at=time, policy_version='progress-v1', evidence_ref=str(row.operation_id),
            difficulty=work.difficulty, hint_used=hinted, reveal_used=revealed)
        if code:
            progress_event.update(misconception_code=code, confirmed=True, source_kind='STEP')
    return result, decision, awarded, progress_event


class FinalizationService:
    def __init__(self, attempts):
        self.attempts = attempts
        self.progress = ProgressService()

    def resume(self, identity, accepted):
        """After the durable 202, attempt to finish. An exact submit retry can resume."""
        attempt_id = identifier(accepted['id'])
        operation_id = identifier(accepted['operation_id'])
        try:
            self.finalize(identity, attempt_id, operation_id, accepted['snapshot_digest'])
        except (wire.APIError, DatabaseUnavailable, AnalysisUnavailable, CheckerSpecError,
                sa.exc.OperationalError, sa.exc.InterfaceError) as error:
            # A log entry carries no session, student work or private configuration.
            logger.info('Submitted analysis remains recoverable (%s)', type(error).__name__)

    def finalize(self, identity, attempt_id, operation_id, frozen_digest):
        # One database session owns the operation across the two short transactions.
        # Closing the physical session releases its advisory lock even after a crash.
        with self.attempts.engine.connect() as connection:
            try:
                claimed = connection.scalar(sa.text(
                    "SELECT pg_try_advisory_lock(hashtextextended(:operation, 0))"
                ), {'operation': f'assessment:analyze:{operation_id}'})
                connection.commit()
                if claimed:
                    self._finalize_claimed(connection, identity, attempt_id, operation_id, frozen_digest)
            finally:
                # Never return a session with a session-level lock to the pool.
                if not connection.invalidated:
                    connection.detach()

    def _finalize_claimed(self, connection, identity, attempt_id, operation_id, frozen_digest):
        attempts = self.attempts
        with UnitOfWork(connection) as uow:
            session = uow.session
            owner = attempts.current(session, identity)
            row = attempts.owned(session, owner, attempt_id)
            if (row.operation_id, row.snapshot_digest) != (operation_id, frozen_digest):
                raise conflict()
            if row.state == 'COMPLETED':
                return
            if row.state != 'SUBMITTED':
                raise conflict()
            work = load_input(session, row, attempts.version(session, row.version_id))

        analysis = analyze_submission(work.exercise, work.submission, graph=work.graph, retry_worker_failure=True)
        if any(not ref.belongs_to(work.submission) for ref in analysis.evidence_refs):
            raise wire.unavailable()

        with UnitOfWork(connection) as uow:
            session = uow.session
            owner = attempts.current(session, identity)
            v = session.execute(sa.select(version).where(
                version.c.id == work.submission.exercise_version_id).with_for_update(read=True)).one()
            e = attempts.exposure(session, owner, v.id, lock=True)
            row = attempts.owned(session, owner, attempt_id, lock=True)
            if (row.operation_id, row.snapshot_digest, row.version_id) != (operation_id, frozen_digest, v.id):
                raise conflict()
            if row.state == 'COMPLETED':
                return
            if row.state != 'SUBMITTED' or work != load_input(session, row, v):
                raise conflict()
            completed_at = max(row.submitted_at, session.scalar(sa.select(sa.func.clock_timestamp())))
            result, eligibility, awarded, progress_event = record_decision(work, row, e, analysis, completed_at)
            session.execute(analysis_record.insert().values(
                operation_id=operation_id, attempt_id=row.id, user_id=owner, version_id=v.id,
                snapshot_digest=frozen_digest, exercise_digest=work.exercise_digest, checker_digest=work.checker_digest,
                checker_version=work.exercise.checker_version, analysis=analysis_payload(analysis),
                result=result, eligibility=eligibility, positive_credit_awarded=awarded, progress_event=progress_event,
            ))
            session.execute(attempt.update().where(attempt.c.id == row.id).values(
                state='COMPLETED', completed_at=completed_at))
            if awarded:
                session.execute(exposure.update().where(exposure.c.user_id == owner,
                    exposure.c.version_id == v.id).values(positive_credit_used=True))

            facts = []
            for mapping in work.skills:
                fact_id = uuid5(operation_id, f'completion:{mapping.code}')
                fact = dict(completion_id=str(fact_id), attempt_id=str(row.id), user_id=str(owner),
                    skill_id=mapping.code, completed_at=timestamp(completed_at), outcome=result['outcome'],
                    independent_correct=eligibility['independent'], policy_version='progress-v1.1')
                session.execute(completion_fact.insert().values(
                    completion_id=fact_id, attempt_id=row.id, skill_id=mapping.id, payload=fact))
                facts.append(fact)
            self.progress.ingest(session, Delivery(events=[progress_event] if progress_event else [], facts=facts))
            uow.commit()
