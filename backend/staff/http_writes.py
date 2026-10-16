"""Staff write wire adapters; Content resources remain view-only."""
from fastapi import Request
from starlette.concurrency import run_in_threadpool

from backend.infrastructure.http import transport as wire
from backend.infrastructure.uow import UnitOfWork
from backend.staff.authorization import authorize, AuthenticatedIdentity
from backend.staff.writes import StaffWrites, permission


async def context(request, service, resource, action=None):
    identity = await run_in_threadpool(service.authenticated, request)
    def check():
        with UnitOfWork(service.engine) as uow:
            scope = authorize(uow, AuthenticatedIdentity(identity.user_id))
            if action:
                permission(scope, resource, action)
    await run_in_threadpool(check)
    if request.method not in {'GET', 'HEAD', 'OPTIONS', 'TRACE'}:
        service.security.require_csrf(request)
    return identity


async def mutate(request, service, signer, resource, action):
    creating = action == 'list'
    identity = await context(request, service, resource, 'add' if creating else 'change')
    if request.method != ('POST' if creating else 'PUT') or action not in {'list', 'detail'}:
        raise wire.invalid()
    schema = ('StaffUserCreateRequest' if creating else 'StaffUserUpdateRequest') if resource == 'users' else 'StaffGroupWriteRequest'
    body = await wire.parse_request(request, schema, delivery=True)
    pk = None if creating else wire.identity(request.path_params['id'])
    data = await run_in_threadpool(StaffWrites(service, signer).mutate, identity, resource, 'create' if creating else 'update', body, pk)
    response = wire.success(request, data, delivery=True,
                            schema='StaffUserDTOResponse' if resource == 'users' else 'StaffGroupDTOResponse')
    response.status_code = 201 if creating else 200
    return response


def install_special(app, service, signer):
    def delete_handler(resource, bulk):
        async def endpoint(request: Request):
            identity = await context(request, service, resource, 'delete')
            if request.method not in {'GET', 'POST'}:
                raise wire.invalid()
            pk = None if bulk else wire.identity(request.path_params['id'])
            if request.method == 'GET':
                if set(request.query_params) - ({'ids'} if bulk else set()):
                    raise wire.invalid()
                ids = [wire.identity(v) for v in request.query_params.getlist('ids')] if bulk else [pk]
                data = await run_in_threadpool(StaffWrites(service, signer).delete, identity, resource, ids)
                return wire.success(request, data, delivery=True, schema='DeletionPreviewDTOResponse')
            body = await wire.parse_request(request, 'DeleteConfirmationRequest', delivery=True)
            if not bulk and body['ids'] != [pk]:
                raise wire.invalid()
            data = await run_in_threadpool(StaffWrites(service, signer).delete, identity, resource, body['ids'], token=body['confirmation_token'])
            return wire.success(request, data, schema='AcknowledgementResponse')
        return endpoint

    methods = ['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'TRACE']
    for resource in ['users', 'groups']:
        for bulk, path in [(True, f'/api/v1/staff/{resource}/delete_selected/'), (False, f'/api/v1/staff/{resource}/{{id}}/delete/')]:
            app.add_api_route(path, delete_handler(resource, bulk), methods=methods, include_in_schema=False)

    def password_handler(own):
        async def endpoint(request: Request):
            identity = await context(request, service, 'users', None if own else 'change')
            if request.method != 'POST':
                raise wire.invalid()
            body = await wire.parse_request(request, 'OwnPasswordChangeRequest' if own else 'PasswordChangeRequest', delivery=True)
            pk = identity.user_id if own else wire.identity(request.path_params['id'])
            cookies = await run_in_threadpool(StaffWrites(service, signer).change_password, identity, pk, body, own=own)
            response = wire.success(request, {'completed': True}, schema='AcknowledgementResponse')
            return service.security.cookies(response, *cookies) if cookies else response
        return endpoint

    app.add_api_route('/api/v1/staff/password_change/', password_handler(True), methods=methods, include_in_schema=False)
    app.add_api_route('/api/v1/staff/users/{id}/password/', password_handler(False), methods=methods, include_in_schema=False)
