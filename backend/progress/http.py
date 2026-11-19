"""Closed Progress HTTP surface. Clients cannot submit events, facts or mastery."""
from decimal import Decimal
import json
from starlette.responses import Response
from starlette.concurrency import run_in_threadpool
from fastapi import Request
from backend.infrastructure.http import transport as wire
from backend.infrastructure.http.contracts import validate, validator
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import User
from backend.users.service import validate_current, receipt_digest, receipt_key
from .models import receipt
from .service import ProgressService, locks
from ._r03_v1 import ContractError, IdentityConflict
from .reads import list_progress
import sqlalchemy as sa
from jsonschema import Draft202012Validator, FormatChecker
from backend.infrastructure.http.contracts import document


def decimal_json(value):
    """JSON decimal number tokens without an intermediate binary float."""
    if isinstance(value, Decimal):
        if not value.is_finite(): raise ValueError('Non-finite number')
        return format(value, 'f')
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(k) + ':' + decimal_json(v) for k, v in value.items()) + '}'
    if isinstance(value, list): return '[' + ','.join(map(decimal_json, value)) + ']'
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def response(value, schema):
    bundle = document('specs/progress/schemas/read-v1.schema.json')
    check = Draft202012Validator({'$defs': bundle['$defs'], '$ref': '#/$defs/' + schema}, format_checker=FormatChecker())
    if not check.is_valid(value): raise wire.unavailable()
    return Response(decimal_json(value), headers={'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'private, no-store'})


def install(app, identity, signer):
    service = ProgressService()

    def operate(auth, action, params, body=None, key=None, request_id=None):
        with UnitOfWork(identity.engine) as uow:
            session = uow.session
            if action != 'self-reports': session.connection(execution_options={'isolation_level': 'REPEATABLE READ'})
            user = session.get(User, auth.user_id)
            if user is None or not user.is_active: raise wire.authentication_required()
            validate_current(session, auth, user, identity.security.keys)
            if action != 'self-reports':
                data, pagination = list_progress(session, user.id, action, params, signer)
                result = {'data': data, 'meta': {'request_id': request_id, 'version': 'http-v1', 'pagination': pagination}}
                return result
            if not isinstance(key, str) or not 1 <= len(key) <= 256 or any(c in key for c in '\r\n\0'):
                raise wire.invalid()
            hashed = receipt_key(key)
            digest = receipt_digest(user.id, 'create_self_report', '/api/v1/progress/self-reports/', body)
            locks(session, ['-1:receipt:' + str(user.id) + ':' + hashed])
            old = session.execute(sa.select(receipt).where(receipt.c.user_id == user.id, receipt.c.key_digest == hashed)).first()
            if old:
                if old.request_digest != digest: raise IdentityConflict('Self-report key conflict')
                return old.response
            try:
                service.skills(session, set(body['skill_codes']))
            except ContractError:
                raise wire.invalid() from None
            data = service.self_report(session, user.id, set(body['skill_codes']))
            result = {'data': data, 'meta': {'request_id': request_id, 'version': 'http-v1'}}
            validate(result, 'SelfReportResultResponse')
            session.execute(receipt.insert().values(user_id=user.id, key_digest=hashed, request_digest=digest, response=result))
            uow.commit()
            return result

    def handler(action):
        async def endpoint(request: Request):
            auth = await run_in_threadpool(identity.authenticated, request)
            mutation = action == 'self-reports'
            if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
                identity.security.require_csrf(request)
            if request.method != ('POST' if mutation else 'GET'): raise wire.invalid()
            body = await wire.parse_request(request, 'SelfReportRequest') if mutation else None
            if mutation: wire.singleton_query(request.query_params, set())
            try:
                result = await run_in_threadpool(operate, auth, action, request.query_params, body,
                    request.headers.get('idempotency-key'), wire.request_id(request))
            except IdentityConflict:
                raise wire.APIError(409, 'IDEMPOTENCY_CONFLICT', 'Request conflicts with saved source.') from None
            except ContractError:
                raise wire.APIError(409, 'STATE_CONFLICT', 'Progress state does not allow this request.') from None
            return response(result, {'skills': 'SkillProgressListResponse', 'topics': 'TopicProgressListResponse',
                'events': 'ProgressEventListResponse', 'completions': 'CompletionHistoryListResponse',
                'self-reports': 'SelfReportResultResponse'}[action])
        return endpoint

    for action in ('skills', 'topics', 'events', 'completions', 'self-reports'):
        path = f'/api/v1/progress/{action}/'
        app.add_api_route(path, handler(action), methods=['GET','HEAD','POST','PUT','PATCH','DELETE','OPTIONS','TRACE'], include_in_schema=False)
        app.state.implemented_routes.append({'path': path, 'method': 'POST' if action == 'self-reports' else 'GET',
            'operation_id': 'create_self_report' if action == 'self-reports' else 'list_progress_' + action})
