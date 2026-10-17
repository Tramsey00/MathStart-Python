"""Private native admin presentation hints; every API keeps its own gate."""
from backend.infrastructure.http.transport import APIError
from backend.staff.authorization import authorize
from backend.staff.reads import RESOURCES, view_permissions


def capabilities(uow, identity):
    try:
        scope = authorize(uow, identity)
    except APIError as error:
        if error.status not in {401, 403}:
            raise
        scope = None
    resources = {}
    for resource, (_, _, dotted) in RESOURCES.items():
        app, model = dotted.split('.')
        editable = resource in {'users', 'groups'}
        permits = lambda action: scope is not None and scope.permits(f'{app}.{action}_{model}')
        resources[resource] = {
            'view': scope is not None and scope.permits(*view_permissions(resource)),
            'add': editable and permits('add') and (resource != 'users' or permits('change')),
            'change': editable and permits('change'),
            'delete': editable and permits('delete'),
        }
    return {'version': 1, 'own_password': scope is not None, 'resources': resources}
