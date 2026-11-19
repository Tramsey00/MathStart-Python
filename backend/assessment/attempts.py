"""Short atomic lifecycle transactions; lock order action key -> Exposure -> Attempt.

No parser, evaluator, provider or Progress writer is invoked here. SUBMITTED is
durable pending work for N013, never a fabricated mathematical outcome.
"""
from copy import deepcopy
from datetime import datetime
import json
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from backend.infrastructure.http import transport as wire
from backend.infrastructure.http.contracts import validate, validator
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import User, utc_now
from backend.users.service import receipt_digest, receipt_key, validate_current
from backend.users.rate_limits import admit_assessment_action
from .attempt_models import action, attempt, event, exposure, hint, step
from .models import exercise, validation, version
from .package import digest
from .reads import public_rows, UUID_PATTERN
from .templates import TEMPLATES, matches_public_contract

CURSOR_SALT = 'assessment.attempts.http-v1.cursor'


def conflict(code='STATE_CONFLICT', row=None):
    error = wire.APIError(409, code, 'Attempt conflicts with canonical state.')
    if code == 'REVISION_CONFLICT':
        error.details = {'current_revision': row.revision, 'reload_url': f'/api/v1/attempts/{row.id}/'}
    return error


def identifier(value):
    if not isinstance(value, str) or not UUID_PATTERN.fullmatch(value):
        raise wire.invalid()
    return UUID(value)


def timestamp(value):
    return wire.timestamp(value).replace('+00:00', 'Z') if value is not None else None


def exposure_dto(row):
    return {'exercise_version_id': str(row.version_id), 'max_help_level': row.max_help_level,
            'revealed_at': timestamp(row.revealed_at), 'positive_credit_used': row.positive_credit_used}


def eligibility(v, e, state):
    reason = ('SELF_CHECK' if v.mode == 'SELF_CHECK' else
              'PENDING' if state != 'STARTED' else
              'REVEAL_EXPOSURE' if e.revealed_at else
              'ALREADY_CREDITED' if e.positive_credit_used else
              'HINT_EXPOSURE' if e.max_help_level else 'ELIGIBLE')
    return {'independent': reason == 'ELIGIBLE',
            'positive_credit_eligible': reason in ('ELIGIBLE', 'HINT_EXPOSURE'), 'reason': reason}


def shape_payload(payload, fields, *, complete):
    if not isinstance(payload, dict) or payload.keys() - set(fields):
        raise wire.invalid()
    if complete and payload.keys() != set(fields):
        raise wire.invalid()
    if any(not isinstance(value, str) or len(value) > 512 or '\0' in value
           or (complete and not value.strip()) for value in payload.values()):
        raise wire.invalid()


def validate_draft(draft, v, *, complete=False):
    """Serialization only, against immutable public shape. Partial drafts are allowed."""
    if not validator('AttemptDraft').is_valid(draft):
        raise wire.invalid()
    template = TEMPLATES.get(v.schema_code)
    if template is None or not matches_public_contract(template, v.public_schema) or template.mode != v.mode:
        raise wire.unavailable()
    fields = [name for name, _ in template.fields]
    shape_payload(draft['payload'], fields, complete=complete and bool(fields))
    steps = draft['steps']
    if not template.step_type and steps:
        raise wire.invalid()
    if complete and template.step_type and not steps:
        raise wire.invalid()
    for number, item in enumerate(steps, 1):
        if item['step_no'] != number or item['step_type'] not in (template.step_type, 'FINAL_STATEMENT'):
            raise wire.invalid()
        raw = item['raw_text']
        if raw is not None and (len(raw) > 512 or '\0' in raw):
            raise wire.invalid()
        if template.mode == 'STRUCTURED_SOLUTION':
            names = fields[:-1] if item['step_type'] == template.step_type else fields[-1:]
        else:
            # Frozen R02 uses payload.expression for both expressions and equations.
            names = ['expression'] if item['step_type'] in ('MATH_EXPRESSION', 'EQUATION_STATE') else ['answer']
        shape_payload(item['payload'], names, complete=complete)
    if complete and template.mode == 'STRUCTURED_SOLUTION':
        # Serialization consistency only: exact raw values, no mathematical truth
        # or normalization. Each published part occurs once in published order.
        parts = v.public_schema['step_schema']['serialization']
        if len(steps) != len(parts):
            raise wire.invalid()
        for item, part in zip(steps, parts):
            if item['step_type'] != part['step_type'] or item['payload'] != {
                    name: draft['payload'][name] for name in part['payload_fields']}:
                raise wire.invalid()


class AttemptService:
    def __init__(self, identity_service, signer, *, public_release=None):
        self.identity = identity_service
        self.engine = identity_service.engine
        self.signer = signer
        self.public_release = public_release

    def current(self, session, identity):
        user = session.get(User, identity.user_id)
        if user is None or not user.is_active:
            raise wire.authentication_required()
        # Serialize against logout/rotation before entering domain locks.
        validate_current(session, identity, user, self.identity.security.keys)
        return user.id

    def owned(self, session, owner, pk, *, lock=False):
        query = sa.select(attempt).where(attempt.c.id == pk, attempt.c.user_id == owner)
        row = session.execute(query.with_for_update() if lock else query).first()
        if row is None:
            raise wire.missing()
        return row

    def version(self, session, version_id):
        row = session.execute(sa.select(version).where(version.c.id == version_id)).one()
        return row

    def exposure(self, session, owner, version_id, *, lock=False):
        query = sa.select(exposure).where(exposure.c.user_id == owner, exposure.c.version_id == version_id)
        return session.execute(query.with_for_update() if lock else query).one()

    def dto(self, session, row, v=None, e=None):
        v = v or self.version(session, row.version_id)
        e = e or self.exposure(session, row.user_id, row.version_id)
        steps = session.execute(sa.select(step).where(step.c.attempt_id == row.id).order_by(step.c.step_no)).all()
        data = {'id': str(row.id), 'exercise_version': {'id': str(v.id), 'exercise_id': str(v.exercise_id),
                'version': v.version, 'contract_version': v.version, 'status': v.status},
                'previous_attempt_id': str(row.previous_attempt_id) if row.previous_attempt_id else None,
                'interaction_mode': v.mode, 'revision': row.revision, 'state': row.state,
                'draft': row.draft, 'steps': [{key: getattr(s, key) for key in
                    ('step_no', 'step_type', 'payload', 'raw_text', 'normalized_repr', 'parse_status')}
                    | {'step_id': str(s.id)} for s in steps],
                'snapshot_digest': row.snapshot_digest, 'operation_id': str(row.operation_id) if row.operation_id else None,
                'result': None, 'exposure': exposure_dto(e), 'eligibility': eligibility(v, e, row.state),
                'created_at': timestamp(row.created_at), 'submitted_at': timestamp(row.submitted_at),
                'completed_at': timestamp(row.completed_at)}
        return validate(data, 'Attempt')

    def get(self, identity, raw_id):
        with UnitOfWork(self.engine) as uow:
            # One coherent row/draft/steps/exposure view across concurrent tabs.
            uow.session.connection(execution_options={'isolation_level': 'REPEATABLE READ'})
            owner = self.current(uow.session, identity)
            return self.dto(uow.session, self.owned(uow.session, owner, identifier(raw_id)))

    def list(self, identity, params):
        query = wire.singleton_query(params, {'cursor', 'page_size'})
        size = wire.page_size(query.get('page_size', '20'))
        with UnitOfWork(self.engine) as uow:
            session = uow.session
            session.connection(execution_options={'isolation_level': 'REPEATABLE READ'})
            owner = self.current(session, identity)
            scope = {'owner': owner, 'page_size': size}
            statement = sa.select(attempt).where(attempt.c.user_id == owner)
            if 'cursor' in query:
                value = self.signer.loads(query['cursor'], CURSOR_SALT)
                try:
                    if set(value) != {'scope', 'created_at', 'id'} or value['scope'] != scope:
                        raise ValueError()
                    key = datetime.fromisoformat(value['created_at']), UUID(value['id'])
                    if key[0].utcoffset() is None:
                        raise ValueError()
                except (KeyError, ValueError, TypeError, AttributeError):
                    raise wire.invalid() from None
                statement = statement.where(sa.tuple_(attempt.c.created_at, attempt.c.id) > key)
            rows = session.execute(statement.order_by(attempt.c.created_at, attempt.c.id).limit(size + 1)).all()
            more, rows = len(rows) > size, rows[:size]
            cursor = self.signer.dumps({'scope': scope, 'created_at': timestamp(rows[-1].created_at),
                                       'id': str(rows[-1].id)}, CURSOR_SALT) if more else None
            return [self.dto(session, row) for row in rows], {'page_size': size, 'has_more': more, 'next_cursor': cursor}

    def mutate(self, identity, operation, route, body, key, request_id, raw_id=None):
        schemas = {'create_attempt': 'CreateAttemptRequest', 'update_draft': 'DraftUpdateRequest',
                   'submit_attempt': 'SubmitRequest', 'abandon_attempt': 'AbandonRequest',
                   'request_hint': 'HintRequest', 'reveal_attempt': 'RevealRequest'}
        if operation not in schemas or not validator(schemas[operation]).is_valid(body):
            raise wire.invalid()
        # Also protect non-HTTP callers from unbounded or non-JSON input.
        try:
            if len(json.dumps(body, ensure_ascii=False, allow_nan=False).encode('utf-8')) > 65536:
                raise wire.invalid()
        except (ValueError, UnicodeError, TypeError, RecursionError):
            raise wire.invalid() from None
        with UnitOfWork(self.engine) as uow:
            session = uow.session
            owner = self.current(session, identity)
            row = self.owned(session, owner, identifier(raw_id)) if raw_id is not None else None
            permanent = operation != 'update_draft'
            if permanent:
                if not isinstance(key, str) or not 1 <= len(key) <= 256 or any(c in key for c in '\r\n\0'):
                    raise wire.invalid()
                key_hash = receipt_key(key)
                request_hash = receipt_digest(owner, operation, route, body)
                session.execute(sa.text('SELECT pg_advisory_xact_lock(hashtextextended(:identity, 0))'),
                    {'identity': f'assessment:{owner}:{operation}:{key_hash}'})
                saved = session.execute(sa.select(action).where(action.c.user_id == owner,
                    action.c.operation == operation, action.c.key_digest == key_hash)).first()
                if saved:
                    if saved.request_digest != request_hash:
                        raise conflict('IDEMPOTENCY_CONFLICT')
                    return deepcopy(saved.response), saved.status
            now, action_id = utc_now(), uuid4()
            if operation == 'create_attempt':
                if body['version'] != body['contract_version']:
                    raise conflict('VERSION_CONFLICT')
                previous_id = body.get('previous_attempt_id')
                previous = self.owned(session, owner, identifier(previous_id)) if previous_id else None
                # Shared version lock serializes archive against new attempts.
                v = session.execute(sa.select(version).where(version.c.exercise_id == identifier(body['exercise_id']),
                    version.c.version == body['version']).with_for_update(read=True)).first()
                if v is None or v.status != 'PUBLISHED':
                    raise conflict('VERSION_CONFLICT')
                if previous and (previous.version_id != v.id or previous.state == 'STARTED'):
                    raise conflict()
                published = session.execute(public_rows().where(version.c.id == v.id)).first()
                if published is None:
                    raise wire.missing()
                if self.public_release is None:
                    raise wire.unavailable()
                page = self.public_release(uow).page(published.slug)
                if page['id'] != published.topic_id or page['page_type'] != 'topic':
                    raise wire.unavailable()
                session.execute(insert(exposure).values(user_id=owner, version_id=v.id,
                    max_help_level=0, revealed_at=None, positive_credit_used=False).on_conflict_do_nothing())
                self.exposure(session, owner, v.id, lock=True)
                pk = uuid4()
                session.execute(attempt.insert().values(id=pk, user_id=owner, version_id=v.id,
                    previous_attempt_id=previous.id if previous else None, revision=1, state='STARTED',
                    draft={'payload': {}, 'steps': []}, created_at=now))
                row = self.owned(session, owner, pk)
                data, status, schema = self.dto(session, row), 201, 'AttemptResponse'
            else:
                self.exposure(session, owner, row.version_id, lock=True)
                row = self.owned(session, owner, row.id, lock=True)
                v = self.version(session, row.version_id)
                if body['contract_version'] != v.version:
                    raise conflict('VERSION_CONFLICT')
                if operation in ('update_draft', 'submit_attempt', 'abandon_attempt'):
                    if row.state != 'STARTED':
                        raise conflict()
                    if body['expected_revision'] != row.revision:
                        raise conflict('REVISION_CONFLICT', row)
                    if operation == 'update_draft':
                        validate_draft(body['draft'], v)
                        self.replace_steps(session, row, body['draft']['steps'])
                        session.execute(attempt.update().where(attempt.c.id == row.id).values(
                            draft=deepcopy(body['draft']), revision=row.revision + 1))
                    elif operation == 'abandon_attempt':
                        session.execute(attempt.update().where(attempt.c.id == row.id).values(
                            state='ABANDONED', revision=row.revision + 1))
                    else:
                        if v.mode == 'SELF_CHECK':
                            raise conflict()
                        validate_draft(row.draft, v, complete=True)
                        admit_assessment_action(session, owner, operation, self.identity.security.key)
                        snapshot = {'attempt_id': str(row.id), 'version_id': str(v.id), 'contract_version': v.version,
                                    'revision': row.revision + 1, 'draft': row.draft,
                                    'steps': self.dto(session, row, v)['steps']}
                        session.execute(attempt.update().where(attempt.c.id == row.id).values(
                            state='SUBMITTED', revision=row.revision + 1, snapshot_digest=digest(snapshot),
                            operation_id=action_id, submitted_at=now))
                    row = self.owned(session, owner, row.id)
                    data = self.dto(session, row, v)
                    status, schema = (202 if operation == 'submit_attempt' else 200), 'AttemptResponse'
                else:
                    if row.state == 'ABANDONED':
                        raise conflict()
                    if operation == 'request_hint':
                        data = self.record_hint(session, row, v, body['level'], action_id)
                        schema = 'HintResultResponse'
                    else:
                        admit_assessment_action(session, owner, operation, self.identity.security.key)
                        data = self.record_reveal(session, row, v, now, action_id)
                        schema = 'RevealResultResponse'
                    status = 200
            response = {'data': data, 'meta': {'request_id': request_id, 'version': 'http-v1'}}
            validate(response, schema)
            if permanent:
                session.execute(action.insert().values(id=action_id, user_id=owner, version_id=row.version_id,
                    attempt_id=row.id, operation=operation, key_digest=key_hash, request_digest=request_hash,
                    response=response, status=status, created_at=now))
                session.execute(event.insert().values(id=uuid4(), attempt_id=row.id, action_id=action_id,
                    type=operation, help_level=body.get('level'), occurred_at=now, request_id=UUID(request_id)))
            # The response (including reveal text) cannot leave before this commit.
            uow.commit()
            return response, status

    def replace_steps(self, session, row, items):
        old = dict(session.execute(sa.select(step.c.step_no, step.c.id).where(step.c.attempt_id == row.id)).all())
        session.execute(step.delete().where(step.c.attempt_id == row.id))
        for item in items:
            session.execute(step.insert().values(id=old.get(item['step_no'], uuid4()), attempt_id=row.id,
                **deepcopy(item), normalized_repr=None, parse_status='NOT_REQUIRED'))

    def record_hint(self, session, row, v, level, action_id):
        template = TEMPLATES.get(v.schema_code)
        if template is None or not matches_public_contract(template, v.public_schema):
            raise wire.unavailable()
        if 'HINT' not in v.public_schema.get('allowed_help_actions', []):
            raise conflict()
        policy = v.public_schema.get('hint_policy', {})
        if not policy.get('allowed') or level not in policy.get('levels', []):
            raise conflict()
        bank = session.execute(sa.select(hint).where(hint.c.version_id == v.id, hint.c.level == level)).first()
        if (bank is None or not bank.text.strip() or len(bank.text) > 512 or '\0' in bank.text
                or digest({'version_id': str(v.id), 'level': level, 'text': bank.text}) != bank.reviewed_digest):
            raise wire.unavailable()
        e = self.exposure(session, row.user_id, v.id)
        if e.revealed_at:
            raise conflict()
        session.execute(exposure.update().where(exposure.c.user_id == row.user_id, exposure.c.version_id == v.id)
                        .values(max_help_level=max(level, e.max_help_level)))
        return {'action_id': str(action_id), 'level': level, 'text': bank.text,
                'exposure': exposure_dto(self.exposure(session, row.user_id, v.id)), 'service_state': 'NORMAL'}

    def record_reveal(self, session, row, v, now, action_id):
        if 'REVEAL' not in v.public_schema.get('allowed_help_actions', []) or not v.public_schema['reveal_policy']['allowed']:
            raise conflict()
        private = session.execute(sa.select(validation.c.answer_key, validation.c.canonical_solution)
                                  .where(validation.c.version_id == v.id)).one()
        answer = private.answer_key
        content = {'answer': answer if isinstance(answer, str) else json.dumps(answer, ensure_ascii=False, sort_keys=True),
                   'steps': private.canonical_solution}
        e = self.exposure(session, row.user_id, v.id)
        session.execute(exposure.update().where(exposure.c.user_id == row.user_id, exposure.c.version_id == v.id)
                        .values(revealed_at=e.revealed_at or now))
        if v.mode == 'SELF_CHECK' and row.state == 'STARTED':
            session.execute(attempt.update().where(attempt.c.id == row.id).values(state='REVIEWED', completed_at=now))
        e = self.exposure(session, row.user_id, v.id)
        return {'action_id': str(action_id), 'reveal_recorded_at': timestamp(e.revealed_at),
                'revealed_content': content, 'exposure': exposure_dto(e),
                'attempt': self.dto(session, self.owned(session, row.user_id, row.id), v, e)}
