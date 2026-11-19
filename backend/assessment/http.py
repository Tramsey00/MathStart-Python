"""Strict, authenticated Attempt transport; no framework coercion or auto redirects."""
from fastapi import Request
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool

from backend.infrastructure.http import transport as wire
from backend.infrastructure.http.contracts import document
from .attempts import AttemptService, identifier
from .finalization import FinalizationService


def install(app, identity_service, signer, public_release):
    service = AttemptService(identity_service, signer, public_release=public_release)
    finalization = FinalizationService(service)
    operations = [row for row in document('specs/api/http-policy-v1.json')['operations']
                  if row['tag'] == 'Attempts']
    paths = {}
    for operation in operations:
        paths.setdefault(operation['path'], {})[operation['method'].upper()] = operation

    def handler(methods):
        async def endpoint(request: Request):
            identity = await run_in_threadpool(identity_service.authenticated, request)
            if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
                identity_service.security.require_csrf(request)
            config = methods.get(request.method)
            if config is None:
                raise wire.invalid()
            operation = config['operation_id']
            if operation == 'list_attempts':
                data, pagination = await run_in_threadpool(service.list, identity, request.query_params)
                return wire.success(request, data, pagination=pagination, schema=config['response'])
            wire.singleton_query(request.query_params, set())
            raw_id = request.path_params.get('id')
            if operation == 'get_attempt':
                return wire.success(request, await run_in_threadpool(service.get, identity, raw_id), schema=config['response'])
            body = await wire.parse_request(request, config['request'])
            # Reconstruct the canonical route rather than accepting client context.
            route = config['path'].replace('{id}', str(identifier(raw_id))) if raw_id else config['path']
            response, status = await run_in_threadpool(service.mutate, identity, operation, route, body,
                request.headers.get('idempotency-key'), wire.request_id(request), raw_id)
            reply = wire.json_response(response, status)
            if operation == 'submit_attempt' and status == 202:
                reply.background = BackgroundTask(finalization.resume, identity, response['data'])
            return reply
        return endpoint

    for path, methods in paths.items():
        app.add_api_route(path, handler(methods), methods=['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'TRACE'],
                          include_in_schema=False)
        for method, config in methods.items():
            app.state.implemented_routes.append({'path': path, 'method': method, 'operation_id': config['operation_id']})
