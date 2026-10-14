"""V02 FastAPI factory. Canonical OAS stays authoritative and unchanged."""
from contextlib import contextmanager
import mimetypes
import re
from urllib.parse import quote, unquote_to_bytes
from xml.etree.ElementTree import Element, SubElement, tostring

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from starlette.routing import Match
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException
from starlette.responses import Response

from backend.infrastructure.database import DatabaseUnavailable
from backend.infrastructure.uow import UnitOfWork
from backend.infrastructure.http import transport as wire
from backend.infrastructure.http.contracts import validate
from backend.content.grades import list_grades
from backend.content.releases import active_release, safe_public_path
from backend.content.releases import Descriptor
from backend.models.protocol import PublicationJournal
from backend.staff.authorization import authorize
from backend.staff import reads
from backend.staff.publication import observe
from backend.models.baseline import Group, Permission, User
import sqlalchemy as sa


class AllMethodRoute(APIRoute):
    """Legacy public views accept arbitrary verbs; adapters validate their family."""
    def matches(self, scope):
        match, child = super().matches(scope)
        return (Match.FULL if match == Match.PARTIAL else match), child

    async def handle(self, scope, receive, send):
        await self.app(scope, receive, send)


def public_redirect_or_missing(release, path):
    """Fallback only for eligible public404, from this request's pinned registry."""
    if not safe_public_path(path):
        raise wire.missing()
    redirect = release.redirect(path)
    if redirect is None:
        raise wire.missing()
    target = redirect['new_path']
    if target == path or not safe_public_path(target):
        raise wire.unavailable()
    # Same URI serialization as Django iri_to_uri; existing escapes stay intact.
    return Response(status_code=301 if redirect['is_permanent'] else 302,
                    headers={'Location': quote(target, safe="/#%[]=:;$&()+,!?*@'~")})


def create_app(engine, signer, *, release_store=None, namespace='public', authenticate=None,
               csrf_check=None, render_page=None, observe_publication=None, public_origin='https://mathstart.example'):
    if not re.fullmatch(r'https?://[A-Za-z0-9.-]+(?::[0-9]+)?', public_origin):
        raise ValueError('Explicit trusted public origin required')
    app = FastAPI(redirect_slashes=False, openapi_url=None, docs_url=None, redoc_url=None)
    app.router.route_class = AllMethodRoute
    app.state.implemented_routes = []

    @contextmanager
    def operation():
        with UnitOfWork(engine) as uow:
            if engine.dialect.name == 'postgresql':
                uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
            yield uow

    def staff_scope(request, uow, *permissions):
        identity = authenticate(request) if authenticate is not None else None
        return authorize(uow, identity, *permissions)

    @app.exception_handler(wire.APIError)
    async def api_error(request, error):
        return wire.error_response(request, error)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, error):
        return wire.error_response(request, wire.invalid())

    @app.exception_handler(HTTPException)
    async def http_error(request, error):
        return wire.error_response(request, wire.missing() if error.status_code == 404 else wire.invalid())

    @app.exception_handler(Exception)
    async def unexpected(request, error):
        return wire.error_response(request, wire.unavailable())

    def method(request):
        if request.method != 'GET':
            raise wire.invalid()

    def register(path, handler, operation_id):
        # Dispatch all standard methods explicitly so no FastAPI 405/307/422 defaults leak.
        app.add_api_route(path, handler, methods=['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'TRACE'],
                          include_in_schema=False, name=operation_id)
        app.state.implemented_routes.append({'path': path, 'method': 'GET', 'operation_id': operation_id})
        async def slashless(request: Request):
            suffix = '?' + request.url.query if request.url.query else ''
            return Response(status_code=301, headers={'Location': quote(request.url.path + '/', safe='/%') + suffix})
        if path == '/api/v1/grades/':
            app.add_api_route(path[:-1], slashless, methods=['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'TRACE'], include_in_schema=False)

    def grades(request: Request):
        method(request)
        with operation() as uow:
            data, pagination = list_grades(uow, request.query_params, signer)
        return wire.success(request, data, pagination=pagination, schema='GradeListResponse')

    register('/api/v1/grades/', grades, 'list_grades')

    def delivery(request: Request):
        method(request)
        slug = request.path_params['slug']
        if not re.fullmatch(r'[-A-Za-z0-9_]{1,255}', slug):
            raise wire.invalid()
        wire.singleton_query(request.query_params, set())
        with operation() as uow:
            data = active_release(uow, release_store, namespace).page(slug)
        return wire.success(request, data, delivery=True, schema='ContentDeliveryResponse')

    register('/api/v1/content/pages/{slug}/', delivery, 'get_content_page')

    def staff_handler(resource, action):
        def handler(request: Request):
            with operation() as uow:
                scope = staff_scope(request, uow, *reads.view_permissions(resource))
                if request.method != 'GET':
                    raise wire.forbidden() if resource not in ('users', 'groups') else wire.invalid()
                model, schema, _ = reads.RESOURCES[resource]
                if action == 'list':
                    data, pagination = reads.list_records(uow, resource, request.query_params, signer, scope)
                    return wire.success(request, data, pagination=pagination, delivery=True, schema=schema + 'ListResponse')
                pk = wire.identity(request.path_params['id'])
                if action == 'detail':
                    wire.singleton_query(request.query_params, set())
                    return wire.success(request, reads.detail(uow, resource, pk), delivery=True, schema=schema + 'Response')
                data, pagination = reads.history(uow, resource, pk, request.query_params, signer, scope)
                return wire.success(request, data, pagination=pagination, delivery=True, schema='StaffHistoryDTOListResponse')
        return handler

    for resource in reads.RESOURCES:
        register(f'/api/v1/staff/{resource}/', staff_handler(resource, 'list'), f'staff_list_{resource}')
        register(f'/api/v1/staff/{resource}/{{id}}/', staff_handler(resource, 'detail'), f'staff_get_{resource}')
        register(f'/api/v1/staff/{resource}/{{id}}/history/', staff_handler(resource, 'history'), f'staff_history_{resource}')

    def group_choices(request: Request):
        with operation() as uow:
            staff_scope(request, uow, 'auth.change_user')
            method(request)
            wire.singleton_query(request.query_params, set())
            pk = wire.identity(request.path_params['id'])
            if uow.repository(User).get(pk) is None:
                raise wire.missing()
            rows = uow.session.execute(sa.select(Group.id, Group.name).order_by(Group.name))
            data = [{'id': r.id, 'name': r.name} for r in rows]
        return wire.success(request, data, delivery=True, schema='StaffGroupChoiceListResponse')

    register('/api/v1/staff/users/{id}/group_choices/', group_choices, 'staff_group_choices')

    def permission_choices(request: Request):
        with operation() as uow:
            scope = staff_scope(request, uow)
            if not (scope.permits('auth.change_user', 'auth.add_group', 'auth.change_group')):
                raise wire.forbidden()
            method(request)
            wire.singleton_query(request.query_params, set())
            rows = uow.session.scalars(sa.select(Permission).order_by(Permission.content_type_id, Permission.codename))
            data = [{f: getattr(r, f) for f in ['id', 'name', 'codename', 'content_type_id']} for r in rows]
        return wire.success(request, data, delivery=True, schema='PermissionChoiceListResponse')

    register('/api/v1/staff/permission_choices/', permission_choices, 'staff_permission_choices')

    def publication_state(request: Request):
        with operation() as uow:
            staff_scope(request, uow, *reads.view_permissions('pages'))
            method(request)
            wire.singleton_query(request.query_params, set())
            pk = wire.identity(request.path_params['id'])
            # A typed observer belongs to V04's DB edition/activation representation.
            # Never fabricate IN_SYNC from current ContentPage during a pending switch.
            if uow.repository(reads.RESOURCES['pages'][0]).get(pk) is None:
                raise wire.missing()
            data = observe(uow, pk, namespace, observe_publication)
        return wire.success(request, data, delivery=True, schema='PublicationObservableStateResponse')

    register('/api/v1/staff/pages/{id}/publication_state/', publication_state, 'staff_publication_state')

    def public(request: Request):
        path = request.url.path
        if path.startswith('/api/') or path.startswith(('/admin/', '/account/', '/__ui__/')):
            raise wire.missing()
        safe_methods = {'GET', 'HEAD', 'OPTIONS', 'TRACE'}
        resolved = path in ('/', '/sitemap.xml', '/robots.txt') or bool(re.fullmatch(r'/[-A-Za-z0-9_]+/', path))
        if resolved and request.method not in safe_methods and (csrf_check is None or not csrf_check(request)):
            raise wire.APIError(403, 'CSRF_FAILED', 'CSRF validation failed.')
        try:
            raw_path = request.scope.get('raw_path')
            if raw_path is not None:
                unquote_to_bytes(raw_path).decode('utf-8', errors='strict')
        except UnicodeError:
            raise wire.missing() from None
        if not safe_public_path(path) and not path.startswith('/_content/'):
            raise wire.missing()
        immutable = re.fullmatch(r'/_content/releases/([A-Za-z0-9_-]+)/(index\.json|pages/([1-9][0-9]*)\.json)', path)
        with operation() as uow:
            if immutable:
                record = uow.session.scalar(sa.select(PublicationJournal).where(
                    PublicationJournal.namespace == namespace, PublicationJournal.release_id == immutable[1],
                    PublicationJournal.db_committed.is_(True), PublicationJournal.activation_status == 'APPLIED'))
                if record is None:
                    raise wire.missing()
                if release_store is None:
                    raise wire.unavailable()
                release = release_store.load(Descriptor(record.id, record.release_id, record.manifest_digest, record.fence_generation))
            else:
                release = active_release(uow, release_store, namespace)
        if path == '/_content/index.json':
            if request.method not in {'GET', 'HEAD'}:
                raise wire.invalid()
            return Response(release.index_raw if request.method == 'GET' else b'', media_type='application/json', headers={'Cache-Control': 'no-store'})
        if immutable:
            if request.method not in {'GET', 'HEAD'}:
                raise wire.invalid()
            if immutable[2] == 'index.json':
                raw = release.index_raw
            else:
                pk = int(immutable[3])
                if pk not in release.pages:
                    raise wire.missing()
                raw = release.page_raw[pk]
            return Response(raw if request.method == 'GET' else b'', media_type='application/json', headers={'Cache-Control': 'no-store'})
        if path.startswith(('/static/', '/media/')):
            asset = release.assets.get(path)
            if asset is None:
                return public_redirect_or_missing(release, path)
            if request.method not in {'GET', 'HEAD'}:
                return Response(status_code=405, headers={'Allow': 'GET, HEAD'})
            desc, raw = asset
            mime = {'style': 'text/css', 'script': 'text/javascript'}.get(desc['kind'], mimetypes.guess_type(path)[0] or 'application/octet-stream')
            etag = '"' + desc['sha256'] + '"'
            if request.headers.get('if-none-match') == etag:
                return Response(status_code=304, headers={'ETag': etag})
            return Response(raw if request.method == 'GET' else b'', headers={'Content-Type': mime, 'ETag': etag, 'X-Content-Type-Options': 'nosniff'})
        if path == '/robots.txt':
            text = 'User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: ' + public_origin + '/sitemap.xml\n'
            return Response(text if request.method != 'HEAD' else '', headers={'Content-Type': 'text/plain; charset=utf-8'})
        if path == '/sitemap.xml':
            root = Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
            for entry in sorted(release.index['pages'], key=lambda p: p['id']):
                url = SubElement(root, 'url')
                for name, value in [('loc', public_origin + entry['canonical_path']), ('lastmod', entry['updated_at'][:10]),
                                    ('changefreq', entry['sitemap_changefreq']), ('priority', str(entry['sitemap_priority']))]:
                    SubElement(url, name).text = value
            raw = b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding='utf-8')
            return Response(raw if request.method != 'HEAD' else b'', headers={'Content-Type': 'application/xml; charset=utf-8'})
        try:
            page = release.page_path(path)
        except wire.APIError as error:
            if error.status != 404:
                raise
            return public_redirect_or_missing(release, path)
        if render_page is None:
            raise wire.unavailable()
        context = release.catalogue(request.query_params) if page['slug'] == 'karta-sajta' else {}
        html = render_page(page, context, public_origin + page['seo']['canonical_path'])
        return Response(html if request.method != 'HEAD' else '', headers={'Content-Type': 'text/html; charset=utf-8'})

    app.add_api_route('/{path:path}', public, methods=['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'TRACE'], include_in_schema=False)
    return app
