"""Frozen current identity HTTP routes; strict JSON and explicit retry semantics."""
from fastapi import Request
from starlette.concurrency import run_in_threadpool
from starlette.responses import Response

from backend.infrastructure.http import transport as wire
from backend.users.security import csrf_secret, mask, unmask


def install(app, service):
    security = service.security
    from backend.infrastructure.http.contracts import document
    operations = {(row['path'], row['method'].upper()): row['operation_id'] for row in
                  document('specs/migration/r02-v1/implemented-routes-v1.json')['operations']}

    @app.middleware('http')
    async def trusted_host(request, call_next):
        try:
            security.host_check(request)
        except wire.APIError as error:
            return wire.error_response(request, error)
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        if request.url.path.startswith(('/auth', '/account', '/api/')):
            response.headers['Cache-Control'] = 'private, no-store'
            response.headers['Referrer-Policy'] = 'no-referrer'
            response.headers['X-Frame-Options'] = 'DENY'
            if security.secure and request.url.path.startswith(('/auth', '/account')):
                response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"
        if security.secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        return response

    paths = {
        '/api/v1/auth/csrf/': ('csrf', {'GET'}, None, False),
        '/api/v1/auth/register/': ('register', {'POST'}, 'RegisterRequest', False),
        '/api/v1/auth/login/': ('login', {'POST'}, 'LoginRequest', False),
        '/api/v1/auth/logout/': ('logout', {'POST'}, 'EmptyRequest', True),
        '/api/v1/users/me/': ('me', {'GET', 'PATCH'}, None, True),
        '/api/v1/onboarding/complete/': ('onboarding', {'POST'}, 'OnboardingRequest', True),
    }

    def handler(action, methods, schema, private):
        async def endpoint(request: Request):
            identity = await run_in_threadpool(security.authenticate, request)
            if private and identity is None:
                raise wire.authentication_required()
            if request.method not in {'GET', 'HEAD', 'OPTIONS', 'TRACE'}:
                security.require_csrf(request)
            if request.method not in methods:
                raise wire.invalid()
            if action == 'csrf':
                secret = unmask(request.cookies.get('csrftoken')) or csrf_secret()
                response = wire.success(request, {'csrf_token': mask(secret)}, schema='CsrfTokenResponse')
                response.set_cookie('csrftoken', secret, max_age=31449600, httponly=False,
                                    secure=security.secure, samesite='lax', path='/')
                return response
            if action == 'me' and request.method == 'GET':
                return wire.success(request, await run_in_threadpool(service.get_me, identity), schema='UserResponse')
            if action == 'me':
                schema_name = 'ProfileUpdateRequest'
            else:
                schema_name = schema
            body = await wire.parse_request(request, schema_name)
            try:
                if any(len(value.encode('utf-8')) > 4096 for value in body.values() if isinstance(value, str)):
                    raise wire.invalid()
            except UnicodeError:
                raise wire.invalid() from None
            if action == 'register':
                await run_in_threadpool(service.account.budget, 'register', security.remote(request))
                response, status, cookies = await run_in_threadpool(service.register, body,
                    request.headers.get('idempotency-key'), request.cookies.get('csrftoken'), identity, wire.request_id(request))
                result = wire.json_response(response, status)
                return security.cookies(result, *cookies) if cookies else result
            if action == 'login':
                # Forwarded headers never supply REMOTE_ADDR authority.
                remote = security.remote(request)
                data, cookies = await run_in_threadpool(service.login, body, remote, identity,
                    legacy_session_key=request.cookies.get('sessionid'))
                return security.cookies(wire.success(request, data, schema='UserResponse'), *cookies)
            if action == 'logout':
                await run_in_threadpool(service.logout, identity)
                response = wire.success(request, {'completed': True}, schema='AcknowledgementResponse')
                response.delete_cookie('sessionid', path='/', secure=security.secure, httponly=True, samesite='lax')
                return response
            if action == 'onboarding':
                key = request.headers.get('idempotency-key')
                if not key:
                    raise wire.invalid()
                response, status = await run_in_threadpool(service.update_profile, identity, body, key=key,
                                                         request_id=wire.request_id(request))
                return wire.json_response(response, status)
            return wire.success(request, await run_in_threadpool(service.update_profile, identity, body), schema='UserResponse')
        return endpoint

    for path, (action, methods, schema, private) in paths.items():
        app.add_api_route(path, handler(action, methods, schema, private),
                methods=['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'TRACE'], include_in_schema=False)
        for method in sorted(methods):
            app.state.implemented_routes.append({'path': path, 'method': method,
                                                'operation_id': operations[(path, method)]})

        async def slashless(request: Request):
            query = '?' + request.url.query if request.url.query else ''
            return Response(status_code=301, headers={'Location': request.url.path + '/' + query})
        app.add_api_route(path[:-1], slashless,
                methods=['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'TRACE'], include_in_schema=False)

    from backend.users.account_http import install as install_account
    install_account(app, service)
