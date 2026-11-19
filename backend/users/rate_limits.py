"""Shared PostgreSQL admission for Assessment actions, learning requirements §16.

Caller authenticates/authorizes and checks permanent replay first. Admission is
committed atomically with the new domain action, never for a replay or rollback.
Use the existing Users-owned request counters; no worker-local limit state.
"""
import math

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from backend.infrastructure.http import transport as wire
from backend.models.identity import window
from .security import salted_hmac

ASSESSMENT_LIMITS = {'submit_attempt': (30, 60), 'reveal_attempt': (10, 60)}


def assessment_budget_key(user_id, operation, signing_key):
    if operation not in ASSESSMENT_LIMITS:
        raise ValueError('Unknown Assessment rate policy')
    return salted_hmac('assessment.budget.' + operation, str(user_id), signing_key)


def admit_assessment_action(session, user_id, operation, signing_key):
    maximum, seconds = ASSESSMENT_LIMITS[operation]
    key = assessment_budget_key(user_id, operation, signing_key)
    session.execute(insert(window).values(key=key, started_at=sa.func.clock_timestamp(), count=0)
                    .on_conflict_do_nothing())
    row = session.execute(sa.select(window).where(window.c.key == key).with_for_update()).mappings().one()
    # Read DB time after acquiring the row lock, including any concurrency wait.
    now = session.scalar(sa.select(sa.func.clock_timestamp()))
    elapsed = (now - row['started_at']).total_seconds()
    expired = elapsed >= seconds
    count = 0 if expired else row['count']
    if count >= maximum:
        error = wire.APIError(429, 'RATE_LIMITED', 'Try again later.')
        error.retry_after = max(1, math.ceil(seconds - elapsed))
        raise error
    session.execute(window.update().where(window.c.key == key).values(
        count=count + 1, started_at=now if expired else row['started_at']))
