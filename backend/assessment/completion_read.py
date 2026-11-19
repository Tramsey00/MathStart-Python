"""Assessment's immutable native completion authority for Progress."""
from dataclasses import dataclass

import sqlalchemy as sa
from uuid import UUID
from backend.progress._r03_v1 import ContractError
from backend.progress.contracts import CompletedAttempt, Delivery
from .attempt_models import analysis_record, attempt, completion_fact
from .attempts import timestamp
from .models import version, exercise_skill
from backend.knowledge.models import skill


@dataclass(frozen=True, slots=True)
class SkillMapping:
    id: UUID
    code: str
    role: str


def mapped_skills(session, version_id):
    rows = session.execute(sa.select(skill.c.id, skill.c.code, exercise_skill.c.role).select_from(
        exercise_skill.join(skill, exercise_skill.c.skill_id == skill.c.id)
    ).where(exercise_skill.c.version_id == version_id).order_by(skill.c.code))
    return tuple(SkillMapping(*row) for row in rows)


def read_completed_attempt(session, attempt_id):
    row = session.execute(sa.select(attempt).where(attempt.c.id == UUID(attempt_id))).first()
    if row is None or row.state != 'COMPLETED':
        raise ContractError('Attempt is not durably finalized')
    record = session.execute(sa.select(analysis_record).where(
        analysis_record.c.operation_id == row.operation_id, analysis_record.c.attempt_id == row.id,
        analysis_record.c.snapshot_digest == row.snapshot_digest,
    )).one_or_none()
    if record is None:
        raise ContractError('Missing frozen Assessment analysis')
    mode = session.scalar(sa.select(version.c.mode).where(version.c.id == row.version_id))
    mappings = mapped_skills(session, row.version_id)
    facts = dict(session.execute(sa.select(completion_fact.c.skill_id, completion_fact.c.payload)
                                .where(completion_fact.c.attempt_id == row.id)).all())
    if facts.keys() != {m.id for m in mappings}:
        raise ContractError('Stored completion facts disagree with the version mapping')
    outcome, independent = record.result['outcome'], record.eligibility['independent']
    completed_at = timestamp(row.completed_at)
    for m in mappings:
        fact = facts[m.id]
        expected = {'attempt_id': attempt_id, 'user_id': str(row.user_id), 'skill_id': m.code,
                    'completed_at': completed_at, 'outcome': outcome, 'independent_correct': independent}
        if any(fact.get(key) != value for key, value in expected.items()):
            raise ContractError('Stored completion fact disagrees with the Attempt result')
    return CompletedAttempt(attempt_id, row.user_id, str(row.version_id), mode, row.state, completed_at,
        tuple((m.code, outcome, independent) for m in mappings),
        Delivery(events=[record.progress_event] if record.progress_event else [], facts=[facts[m.id] for m in mappings]))


def verify_exercise_mapping(session, source):
    """Immutable exercise version and mapped skills, shared by source adapters."""
    v = session.execute(sa.select(version.c.mode).where(version.c.id == UUID(source.version_id))).first()
    if v is None or v.mode != source.mode or v.mode == 'SELF_CHECK':
        raise ContractError('Completion is not bound to an assessed version')
    mapped = set(session.scalars(sa.select(skill.c.code).join(exercise_skill,
        exercise_skill.c.skill_id == skill.c.id).where(exercise_skill.c.version_id == UUID(source.version_id))))
    if not {code for code, _, _ in source.skills} <= mapped:
        raise ContractError('Completed skill is not mapped to the bound exercise version')


def verify_version_skills(session, source):
    """Native authority must refer to an existing, durably completed owned attempt."""
    verify_exercise_mapping(session, source)
    row = session.execute(sa.select(attempt.c.user_id, attempt.c.version_id, attempt.c.state)
                          .where(attempt.c.id == UUID(source.attempt_id))).first()
    if row is None or row.user_id != source.user_id or str(row.version_id) != source.version_id or row.state != 'COMPLETED':
        raise ContractError('Completion disagrees with the stored attempt owner/version/state')
