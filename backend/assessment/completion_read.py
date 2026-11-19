"""Fail-closed N012 boundary; durable finalization/outcome authority belongs to N013."""
import sqlalchemy as sa
from uuid import UUID
from backend.progress._r03_v1 import ContractError
from .attempt_models import attempt
from .models import version, exercise_skill
from backend.knowledge.models import skill


def read_completed_attempt(session, attempt_id):
    row = session.execute(sa.select(attempt).where(attempt.c.id == UUID(attempt_id))).first()
    if row is None or row.state != 'COMPLETED':
        raise ContractError('Attempt is not durably finalized')
    # N009 cannot contain COMPLETED, outcome or frozen eligibility. N013 must
    # extend this reader together with its authoritative CompletionFact storage.
    raise ContractError('Finalized Assessment authority has not been installed by N013')


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
