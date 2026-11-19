"""Owner-scoped projections; reads never initialize state or write evidence."""
from decimal import Decimal, ROUND_HALF_UP
import sqlalchemy as sa
from backend.knowledge.models import skill
from backend.content.topic_skill_model import topic_skill
from backend.infrastructure.http import transport as wire
from .models import event, state, completion
from ._r03_v1 import ASSESSED_KINDS


def stamp(value):
    return wire.timestamp(value).replace('+00:00', 'Z') if value else None


def skill_projection(session, owner, sid, code):
    row = session.execute(sa.select(state).where(state.c.user_id == owner, state.c.skill_id == sid)).first()
    reported = session.scalar(sa.select(sa.exists(sa.select(event.c.event_id).where(
        event.c.user_id == owner, event.c.skill_id == sid, event.c.event_kind == 'SELF_REPORTED_KNOWN'))))
    return dict(skill_code=code, mastery=row.mastery if row else Decimal('0.00'),
        confidence=row.confidence if row else Decimal('0.00'), evidence_count=row.evidence_count if row else 0,
        status=row.status if row else 'NOT_STARTED', last_updated=stamp(row.last_updated) if row else None,
        reducer_version='progress-v1.1', self_reported=bool(reported))


def list_progress(session, owner, kind, params, signer, *, topic_catalogue=None):
    query = wire.singleton_query(params, {'page_size', 'cursor'})
    size = wire.page_size(query.get('page_size', '20'))
    scope = {'owner': owner, 'kind': kind, 'page_size': size}
    salt = 'progress.reads.n012.v1'
    after = None
    if 'cursor' in query:
        value = signer.loads(query['cursor'], salt)
        if not isinstance(value, dict) or set(value) != {'scope', 'key'} or value['scope'] != scope or not isinstance(value['key'], str):
            raise wire.invalid()
        after = value['key']
    if kind == 'skills':
        statement = sa.select(skill.c.id, skill.c.code).where(skill.c.active.is_(True)).order_by(skill.c.code)
        if after: statement = statement.where(skill.c.code > after)
        rows = session.execute(statement.limit(size + 1)).all()
        keys = [row.code for row in rows]
        data = [skill_projection(session, owner, row.id, row.code) for row in rows[:size]]
    elif kind in ('events', 'completions'):
        if kind == 'completions':
            statement = sa.select(completion).where(completion.c.user_id == owner).order_by(completion.c.received_at, completion.c.completion_id)
            if after:
                try:
                    time, cid = after.split('|', 1)
                    from uuid import UUID
                    from .service import instant
                    statement = statement.where(sa.tuple_(completion.c.received_at, completion.c.completion_id) > (instant(time), UUID(cid)))
                except (ValueError, TypeError): raise wire.invalid() from None
            rows = session.execute(statement.limit(size + 1)).all()
            keys = [stamp(row.received_at) + '|' + str(row.completion_id) for row in rows]
            data = [{k: row.payload[k] for k in ('completion_id','attempt_id','outcome','independent_correct','completed_at','policy_version')}
                    | {'skill_code': row.payload['skill_id']} for row in rows[:size]]
            more = len(rows) > size
            cursor = signer.dumps({'scope': scope, 'key': keys[size - 1]}, salt) if more else None
            return data, {'next_cursor': cursor, 'has_more': more, 'page_size': size}
        # Stable ingestion order; the immutable event's mathematical order remains occurred_at/event_id/policy.
        statement = sa.select(event).where(event.c.user_id == owner).order_by(event.c.received_at, event.c.event_id)
        if after:
            try:
                time, eid = after.split('|', 1)
                from .service import instant
                statement = statement.where(sa.tuple_(event.c.received_at, event.c.event_id) > (instant(time), eid))
            except (ValueError, TypeError): raise wire.invalid() from None
        rows = session.execute(statement.limit(size + 1)).all()
        keys = [stamp(row.received_at) + '|' + row.event_id for row in rows]
        data = [dict(event_id=row.event_id, skill_code=row.payload['skill_id'], event_kind=row.event_kind,
            occurred_at=row.payload['occurred_at'], attempt_id=row.attempt_id,
            evidence_ref=row.evidence_ref or 'self-report', policy_version=row.policy_version) for row in rows[:size]]
    elif kind == 'topics':
        if topic_catalogue is None: raise wire.unavailable()
        # The pinned Content edition owns public topic identity, not mutable source rows.
        linked = set(session.scalars(sa.select(topic_skill.c.content_page_id).join(skill,
            skill.c.id == topic_skill.c.skill_id).where(skill.c.active.is_(True))))
        rows = sorted((row for row in topic_catalogue if row['id'] in linked
                       and (not after or row['slug'] > after)), key=lambda row: row['slug'])[:size + 1]
        keys = [row['slug'] for row in rows]
        data = []
        for row in rows[:size]:
            mappings = session.execute(sa.select(topic_skill, skill.c.code).join(skill, skill.c.id == topic_skill.c.skill_id)
                .where(topic_skill.c.content_page_id == row['id'], skill.c.active.is_(True))).all()
            weighted = [(m, skill_projection(session, owner, m.skill_id, m.code)) for m in mappings]
            total = sum((m.importance for m, _ in weighted), Decimal(0))
            def average(field):
                return (sum((m.importance * p[field] for m, p in weighted), Decimal(0)) / total).quantize(
                    Decimal('.01'), rounding=ROUND_HALF_UP) if total else Decimal('0.00')
            primary = [m for m in mappings if m.role == 'PRIMARY']
            assessed = sum(bool(session.scalar(sa.select(sa.exists(sa.select(event.c.event_id).where(
                event.c.user_id == owner, event.c.skill_id == m.skill_id, event.c.event_kind.in_(ASSESSED_KINDS)))))) for m in primary)
            data.append(dict(topic={'id': row['id'], 'slug': row['slug']}, mastery=average('mastery'), confidence=average('confidence'),
                assessed_skill_count=assessed, total_skill_count=len(primary)))
    else: raise wire.invalid()
    more = len(rows) > size
    cursor = signer.dumps({'scope': scope, 'key': keys[size - 1]}, salt) if more else None
    return data, {'next_cursor': cursor, 'has_more': more, 'page_size': size}
