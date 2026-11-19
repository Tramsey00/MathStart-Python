"""Exercise read projection. No query joins or selects the validation table."""
from datetime import datetime
import re
from uuid import UUID

import sqlalchemy as sa

from backend.content.topic_skill_model import content_page
from backend.infrastructure.http import transport as wire
from backend.knowledge.models import skill

from .models import exercise, exercise_skill, version
from .templates import DIFFICULTY_BANDS, TEMPLATES, matches_public_contract

CURSOR_SALT = 'assessment.topic-exercises.http-v1.cursor'
UUID_PATTERN = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')


def public_rows():
    e, v, p = exercise.c, version.c, content_page.c
    return sa.select(e.id, e.code, e.created_at, v.id.label('version_id'), v.version, v.mode,
                     v.difficulty, v.statement, v.schema_code, v.public_schema,
                     p.id.label('topic_id'), p.slug).select_from(
        exercise.join(version, v.exercise_id == e.id).join(content_page, e.topic_id == p.id)
    ).where(v.status == 'PUBLISHED', p.page_type == 'topic', p.is_published.is_(True))


def public_dto(row, codes):
    template = TEMPLATES.get(row.schema_code)
    if template is None or row.mode != template.mode or not codes:
        raise wire.unavailable()
    public_schema = row.public_schema
    if not matches_public_contract(template, public_schema):
        raise wire.unavailable()
    return {
        'id': str(row.id), 'code': row.code, 'topic': {'id': row.topic_id, 'slug': row.slug},
        'statement': row.statement, 'interaction_mode': row.mode, **public_schema,
        'difficulty': DIFFICULTY_BANDS[row.difficulty], 'difficulty_level': row.difficulty,
        'contract_version': row.version, 'version': row.version, 'skill_codes': codes,
        'exercise_version': {'id': str(row.version_id), 'exercise_id': str(row.id), 'version': row.version,
                             'contract_version': row.version, 'status': 'PUBLISHED'},
    }


def project(session, rows):
    if not rows:
        return []
    codes = {row.version_id: [] for row in rows}
    link, node = exercise_skill.c, skill.c
    for link_id, code in session.execute(sa.select(link.version_id, node.code)
        .join(skill, node.id == link.skill_id).where(link.version_id.in_(codes))
        .order_by(link.role, node.code)):
        codes[link_id].append(code)
    return [public_dto(row, codes[row.version_id]) for row in rows]


def get_exercise(session, public_release, raw_id, user_id):
    if not UUID_PATTERN.fullmatch(raw_id):
        raise wire.invalid()
    row = session.execute(public_rows().where(exercise.c.id == UUID(raw_id))).one_or_none()
    if row is None:
        raise wire.authentication_required() if user_id is None else wire.missing()
    if user_id is None and row.mode != 'SELF_CHECK':
        raise wire.authentication_required()
    try:
        topic = public_release().page(row.slug)
    except wire.APIError as error:
        if error.status == 404 and user_id is None:
            raise wire.authentication_required() from None
        raise
    if topic['id'] != row.topic_id or topic['page_type'] != 'topic':
        raise wire.unavailable()
    return project(session, [row])[0]


def list_exercises(session, page, params, signer, user_id):
    query = wire.singleton_query(params, {'page_size', 'cursor'})
    size = wire.page_size(query.get('page_size', '20'))
    scope = {'topic_id': page['id'], 'user_id': user_id, 'page_size': size}
    e = exercise.c
    statement = public_rows().where(e.topic_id == page['id'])
    if user_id is None:
        statement = statement.where(version.c.mode == 'SELF_CHECK')
    if 'cursor' in query:
        value = signer.loads(query['cursor'], CURSOR_SALT)
        try:
            if value['scope'] != scope or set(value) != {'scope', 'created_at', 'id'}:
                raise ValueError()
            key = datetime.fromisoformat(value['created_at']), UUID(value['id'])
            if key[0].utcoffset() is None:
                raise ValueError()
        except (AttributeError, KeyError, TypeError, ValueError):
            raise wire.invalid() from None
        statement = statement.where(sa.tuple_(e.created_at, e.id) > key)
    rows = session.execute(statement.order_by(e.created_at, e.id).limit(size + 1)).all()
    more = len(rows) > size
    rows = rows[:size]
    next_cursor = None
    if more:
        last = rows[-1]
        next_cursor = signer.dumps({'scope': scope, 'created_at': wire.timestamp(last.created_at),
                                    'id': str(last.id)}, CURSOR_SALT)
    return project(session, rows), {'page_size': size, 'has_more': more, 'next_cursor': next_cursor}
