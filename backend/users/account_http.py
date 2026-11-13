"""Strict MS-T009 extension DTOs. Identity remains the only auth authority."""
from fastapi import Request, BackgroundTasks
from starlette.concurrency import run_in_threadpool
from backend.infrastructure.http import transport as wire

FIELDS = {'state': set(), 'email': {'current_password', 'email'},
          'password': {'current_password', 'new_password'}, 'sessions': {'current_password'},
          'recover': {'username'}, 'verify': {'token'}, 'reset': {'token', 'new_password'}}

def install(app, service):
    security, account = service.security, service.account
    def handler(action):
        async def endpoint(request: Request):
            expected = 'GET' if action == 'state' else 'POST'
            wire.singleton_query(request.query_params, set())
            if request.method != expected:
                from starlette.responses import Response
                return Response(status_code=405, headers={'Allow': expected, 'Cache-Control': 'private, no-store'})
            identity = await run_in_threadpool(security.authenticate, request)
            private = action in {'state', 'email', 'password', 'sessions', 'verify'}
            if private and identity is None:
                raise wire.authentication_required()
            if action == 'state':
                return wire.success(request, await run_in_threadpool(account.state, identity))
            security.require_csrf(request)
            # Bounded raw JSON including chunked requests, strict closed DTO.
            if request.headers.get('content-type', '').split(';')[0] != 'application/json':
                raise wire.invalid()
            raw = bytearray()
            async for chunk in request.stream():
                raw.extend(chunk)
                if len(raw) > 8192:
                    raise wire.APIError(400, 'LIMIT_EXCEEDED', 'Body too large.')
            try:
                body = wire.decode_json(raw)
            except (ValueError, UnicodeError, RecursionError):
                raise wire.invalid() from None
            if not isinstance(body, dict) or set(body) != FIELDS[action] or any(not isinstance(v, str) for v in body.values()):
                raise wire.invalid()
            limits = {'current_password': 4096, 'new_password': 512, 'email': 254, 'username': 600, 'token': 128}
            try:
                if any(len(v.encode('utf-8')) > limits[k] for k, v in body.items()) or len(body.get('username','')) > 150:
                    raise wire.invalid()
            except UnicodeError:
                raise wire.invalid() from None
            remote = security.remote(request)
            budget = 'recover' if action == 'recover' else 'consume' if action in {'verify', 'reset'} else 'sensitive'
            await run_in_threadpool(account.budget, budget, remote, body.get('username', str(identity.user_id) if identity else ''))
            if action == 'recover':
                background = BackgroundTasks()
                result = await run_in_threadpool(account.recover, body['username'], defer=background.add_task)
            elif action in {'verify', 'reset'}:
                result = await run_in_threadpool(account.consume, action, body, identity)
            else:
                result = await run_in_threadpool(account.action, identity, action, body)
            response = wire.success(request, result)
            if action == 'recover':
                response.background = background
            if action in {'password', 'sessions', 'reset'}:
                response.delete_cookie('sessionid', path='/', secure=security.secure, httponly=True, samesite='lax')
            return response
        return endpoint
    for action in FIELDS:
        app.add_api_route('/api/v1/account/' + action + '/', handler(action),
                         methods=['GET'] if action == 'state' else ['POST'], include_in_schema=False)
