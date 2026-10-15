"""HTTP/security integration; SQLite compatibility, explicitly not PG proof."""
from datetime import timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import uuid

import sqlalchemy as sa
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.http.contracts import validator
from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.migrations.upgrade import fresh
from backend.models.baseline import metadata, Grade
from backend.staff.authorization import AuthenticatedIdentity
from backend.tests.v02.fixtures import seed, release_files, activate_fixture, KEY, STAMP


class HTTPAssertions:
    def prepare(self):
        self.files = tempfile.TemporaryDirectory(dir='var')
        self.store, self.descriptor, self.index, self.deliveries = release_files(self.files.name)
        with self.engine.begin() as c:
            fresh(c)
        seed(self.engine)
        activate_fixture(self.engine, self.descriptor)
        self.actor = None
        self.signer = Signer(KEY)
        self.client = TestClient(create_app(self.engine, self.signer, release_store=self.store,
            authenticate=lambda request: AuthenticatedIdentity(self.actor) if self.actor is not None else None,
            csrf_check=lambda request: request.headers.get('x-csrftoken') == 'synthetic-verified',
            render_page=lambda page, context, canonical: page['body_html']), raise_server_exceptions=False)

    def finish(self):
        self.client.close()
        self.files.cleanup()

    def response(self, response, status=200, schema=None, delivery=False):
        self.assertEqual(response.status_code, status, response.text[:400])
        if schema:
            validator(schema, delivery).validate(response.json())
            self.assertEqual(response.headers['content-type'], 'application/json; charset=utf-8')
            self.assertEqual(response.headers['cache-control'], 'private, no-store')
        return response.json() if schema else response

    def error(self, response, status=400, code='INVALID_REQUEST'):
        self.assertEqual(response.status_code, status, response.text[:400])
        data = response.json()['error']
        self.assertEqual(set(data), {'code', 'message', 'field_errors', 'retryable', 'request_id'})
        self.assertEqual(data['code'], code)
        self.assertEqual(data['field_errors'], {})
        self.assertEqual(data['retryable'], status in (429, 503))
        uuid.UUID(data['request_id'])
        return data

    def test_grade_real_ids_numbers_no_private_fields_and_body_ignored(self):
        response = self.client.request('GET', '/api/v1/grades/', content=b'{broken', headers={'content-type': 'text/plain'})
        body = self.response(response, schema='GradeListResponse')
        self.assertEqual(body['data'], [{'id': 30, 'number': 10, 'title': '10 класс'},
                                      {'id': 70, 'number': 5, 'title': '5 класс'},
                                      {'id': 50, 'number': 6, 'title': '6 класс'}])
        self.assertFalse(response.cookies)

    def test_grade_keyset_delete_edit_insert_consistency(self):
        first = self.response(self.client.get('/api/v1/grades/?page_size=1'), schema='GradeListResponse')
        cursor = first['meta']['pagination']['next_cursor']
        with self.engine.begin() as c:
            c.execute(sa.delete(Grade).where(Grade.id == 30))
            c.execute(sa.update(Grade).where(Grade.id == 70).values(title='Пятый класс', order=0))
            c.execute(sa.insert(Grade).values(id=80, slug='7-klass', title='7 класс', created_at=STAMP + timedelta(seconds=2)))
        ids = [30]
        while cursor:
            body = self.response(self.client.get('/api/v1/grades/', params={'page_size': 1, 'cursor': cursor}), schema='GradeListResponse')
            ids += [g['id'] for g in body['data']]
            cursor = body['meta']['pagination']['next_cursor']
        self.assertEqual(ids, [30, 70, 50, 80])

    def test_grade_signed_cursor_wrong_scope_types_size_and_tampering(self):
        body = self.response(self.client.get('/api/v1/grades/?page_size=1'), schema='GradeListResponse')
        cursor = body['meta']['pagination']['next_cursor']
        self.error(self.client.get('/api/v1/grades/', params={'page_size': 2, 'cursor': cursor}))
        self.error(self.client.get('/api/v1/grades/', params={'page_size': 1, 'cursor': cursor + 'x'}))
        value = self.signer.loads(cursor, 'content.grades.http-v1.cursor')
        for change in [{'scope': 'foreign'}, {'id': True}, {'id': 2**63}, {'page_size': True}, {'created_at': '2026-10-04T00:00:00'}, {'extra': 'x'}]:
            forged = self.signer.dumps({**value, **change}, 'content.grades.http-v1.cursor')
            self.error(self.client.get('/api/v1/grades/', params={'page_size': 1, 'cursor': forged}))
        for query in ['page_size=0', 'page_size=101', 'page_size=true', 'page_size=1&page_size=2', 'foreign=x']:
            self.error(self.client.get('/api/v1/grades/?' + query))

    def test_grade_unsupported_row_and_database_failure_safe(self):
        with self.engine.begin() as c:
            c.execute(sa.update(Grade).where(Grade.id == 70).values(slug='PRIVATE-UNSUPPORTED'))
        response = self.client.get('/api/v1/grades/')
        self.error(response, 503, 'SERVICE_UNAVAILABLE')
        self.assertNotIn('PRIVATE-UNSUPPORTED', response.text)
        with patch('backend.infrastructure.http.app.list_grades', side_effect=RuntimeError('SQL PASSWORD DSN private path')):
            response = self.client.get('/api/v1/grades/')
            self.error(response, 503, 'SERVICE_UNAVAILABLE')
            self.assertNotIn('PASSWORD', response.text)

    def test_exact_routes_methods_slashless_unknown_and_no_307_422(self):
        for method in ['HEAD', 'POST', 'OPTIONS', 'PUT', 'DELETE']:
            response = self.client.request(method, '/api/v1/grades/')
            self.assertEqual(response.status_code, 400)
        for method in ['GET', 'POST', 'HEAD']:
            response = self.client.request(method, '/api/v1/grades?x=1', follow_redirects=False)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response.headers['location'], '/api/v1/grades/?x=1')
        for path in ['/api/v1/topics/', '/api/v1/nope/', '/openapi.json', '/docs', '/api/v1/content/pages/bad%20slug/']:
            response = self.client.get(path)
            self.assertIn(response.status_code, [400, 404])
            self.assertNotIn(response.status_code, [200, 307, 422])

    def test_public_delivery_visibility_and_manifest(self):
        body = self.response(self.client.get('/api/v1/content/pages/topic/'), schema='ContentDeliveryResponse', delivery=True)
        self.assertEqual(body['data'], self.deliveries[302])
        self.error(self.client.get('/api/v1/content/pages/draft/'), 404, 'NOT_FOUND')
        self.response(self.client.get('/_content/index.json'))
        self.assertEqual(self.client.get('/_content/releases/synthetic-v02/pages/302.json').json(), self.deliveries[302])
        self.error(self.client.get('/_content/releases/foreign/pages/302.json'), 404, 'NOT_FOUND')
        self.error(self.client.get('/_content/releases/synthetic-v02/pages/303.json'), 404, 'NOT_FOUND')

    def test_routing_redirect_precedence_seo_sitemap_and_media(self):
        self.assertEqual(self.client.get('/topic/').status_code, 200)
        self.assertEqual(self.client.get('/glavnaya/').status_code, 200)
        for path, status in [('/old.html', 301), ('/старое.html', 302)]:
            response = self.client.get(path, follow_redirects=False)
            self.assertEqual(response.status_code, status)
            self.assertEqual(response.headers['location'], '/topic/')
        for path in ['/unknown/', '/draft/', '/static/missing.css', '/media/private.pdf', '/a/%252e%252e/secret']:
            self.assertEqual(self.client.get(path).status_code, 404)
        sitemap = self.client.get('/sitemap.xml')
        self.assertEqual(sitemap.status_code, 200)
        self.assertNotIn('/draft/', sitemap.text)
        self.assertNotIn('/glavnaya/', sitemap.text)
        self.assertIn('https://mathstart.example/topic/', sitemap.text)
        self.assertIn('Disallow: /admin/', self.client.get('/robots.txt').text)
        asset = self.client.get('/static/theme.css')
        self.assertEqual(asset.status_code, 200)
        self.assertEqual(self.client.get('/static/theme.css', headers={'if-none-match': asset.headers['etag']}).status_code, 304)
        self.assertEqual(self.client.head('/static/theme.css').content, b'')

    def test_public_methods_csrf_resolved_missing_and_unresolved_redirect(self):
        for path in ['/', '/topic/', '/draft/', '/sitemap.xml', '/robots.txt']:
            self.error(self.client.post(path), 403, 'CSRF_FAILED')
        for path in ['/', '/topic/', '/sitemap.xml', '/robots.txt']:
            self.assertEqual(self.client.post(path, headers={'x-csrftoken': 'synthetic-verified'}).status_code, 200)
            self.assertEqual(self.client.options(path).status_code, 200)
            self.assertEqual(self.client.head(path).content, b'')
        self.assertEqual(self.client.post('/old.html', follow_redirects=False).status_code, 301)
        self.error(self.client.request('PURGE', '/topic/'), 403, 'CSRF_FAILED')
        self.assertEqual(self.client.request('PURGE', '/topic/', headers={'x-csrftoken': 'synthetic-verified'}).status_code, 200)

    def test_staff_anonymous_inactive_nonstaff_no_permission_before_lookup(self):
        for actor, status, code in [(None, 401, 'AUTHENTICATION_REQUIRED'), (904, 401, 'AUTHENTICATION_REQUIRED'),
                                    (903, 403, 'FORBIDDEN')]:
            self.actor = actor
            for pk in ['302', '99999', 'bad']:
                self.error(self.client.get('/api/v1/staff/pages/' + pk + '/'), status, code)
        self.actor = 905
        self.error(self.client.get('/api/v1/staff/grades/70/'), 403, 'FORBIDDEN')
        self.actor = None
        self.error(self.client.get('/api/v1/staff/pages/', headers={'x-role': 'superuser', 'x-user-id': '902'}), 401, 'AUTHENTICATION_REQUIRED')

    def test_staff_all_nine_dtos_history_and_no_password_leak(self):
        self.actor = 902
        ids = {'grades': 70, 'subjects': 101, 'sections': 201, 'pages': 303, 'users': 901, 'groups': 61,
               'publications': 401, 'media_assets': 501, 'redirects': 601}
        from backend.staff.reads import RESOURCES
        for resource, (_, schema, _) in RESOURCES.items():
            self.response(self.client.get(f'/api/v1/staff/{resource}/'), schema=schema + 'ListResponse', delivery=True)
            if resource in ids:
                self.response(self.client.get(f'/api/v1/staff/{resource}/{ids[resource]}/'), schema=schema + 'Response', delivery=True)
        self.actor = 901
        body = self.response(self.client.get('/api/v1/staff/pages/302/history/'), schema='StaffHistoryDTOListResponse', delivery=True)
        self.assertEqual(body['data'][0]['action'], 'CHANGE')
        self.assertNotIn('PASSWORD-SENTINEL', json.dumps(body))
        self.error(self.client.post('/api/v1/staff/pages/303/'), 403, 'FORBIDDEN')
        self.actor = 902
        response = self.client.get('/api/v1/staff/users/902/')
        self.assertNotIn('SECRET-ENCODED-PASSWORD', response.text)

    def test_staff_filters_sort_mixed_nulls_binding_and_permission_revision(self):
        self.actor = 901
        first = self.response(self.client.get('/api/v1/staff/pages/?sort=-grade,title&page_size=1'), schema='StaffPageDTOListResponse', delivery=True)
        cursor = first['meta']['pagination']['next_cursor']
        self.assertIsNotNone(cursor)
        assignment = metadata.tables['auth_user_user_permissions']
        with self.engine.begin() as c:
            c.execute(sa.insert(assignment).values(id=76, user_id=901, permission_id=51))
        # A redundant direct permission already inherited from a group does not
        # change the contract's effective permission-code digest.
        self.assertEqual(self.client.get('/api/v1/staff/pages/', params={
            'sort': '-grade,title', 'page_size': 1, 'cursor': cursor}).status_code, 200)
        with self.engine.begin() as c:
            c.execute(sa.delete(assignment).where(assignment.c.id == 73))
        self.error(self.client.get('/api/v1/staff/pages/', params={'sort': '-grade,title', 'page_size': 1, 'cursor': cursor}))
        with self.engine.begin() as c:
            c.execute(sa.delete(assignment).where(assignment.c.id == 76))
            c.execute(sa.insert(assignment).values(id=73, user_id=901, permission_id=52))
        for change in [{'sort': 'title'}, {'q': 'new'}, {'filter__is_published': 'true'}, {'page_size': 2}]:
            params = {'sort': '-grade,title', 'page_size': 1, 'cursor': cursor, **change}
            self.error(self.client.get('/api/v1/staff/pages/', params=params))
        self.actor = 905
        self.error(self.client.get('/api/v1/staff/pages/', params={'sort': '-grade,title', 'page_size': 1, 'cursor': cursor}))
        self.actor = 901
        ids = [first['data'][0]['id']]
        while cursor:
            body = self.response(self.client.get('/api/v1/staff/pages/', params={'sort': '-grade,title', 'page_size': 1, 'cursor': cursor}), schema='StaffPageDTOListResponse', delivery=True)
            ids += [r['id'] for r in body['data']]
            cursor = body['meta']['pagination']['next_cursor']
        self.assertEqual(len(ids), 4)
        self.assertEqual(len(set(ids)), 4)
        self.assertEqual(ids[-1], 302)
        for query in ['sort=title,-title', 'sort=body_html', 'filter__is_published=1', 'filter__is_published=True', 'sort=+title', 'q=x&q=y']:
            self.error(self.client.get('/api/v1/staff/pages/?' + query))

    def test_selectors_and_publication_observer_fail_closed(self):
        self.actor = 901
        self.response(self.client.get('/api/v1/staff/users/902/group_choices/'), schema='StaffGroupChoiceListResponse', delivery=True)
        self.error(self.client.get('/api/v1/staff/groups/61/'), 403, 'FORBIDDEN')
        self.error(self.client.get('/api/v1/staff/pages/302/publication_state/'), 503, 'SERVICE_UNAVAILABLE')
        self.error(self.client.get('/api/v1/staff/pages/999/publication_state/'), 404, 'NOT_FOUND')
        self.actor = 905
        self.error(self.client.get('/api/v1/staff/users/901/group_choices/'), 403, 'FORBIDDEN')

    def test_all_gets_no_dml_no_profile_or_evidence_and_safe_uow(self):
        self.actor = 902
        queries = []
        def capture(connection, cursor, statement, params, context, many):
            queries.append(statement)
        with self.engine.connect() as c:
            counts = {name: c.scalar(sa.select(sa.func.count()).select_from(t)) for name, t in metadata.tables.items()}
        sa.event.listen(self.engine, 'before_cursor_execute', capture)
        try:
            for path in ['/api/v1/grades/', '/api/v1/content/pages/topic/', '/api/v1/staff/pages/',
                         '/api/v1/staff/users/902/', '/api/v1/staff/pages/302/history/', '/_content/index.json', '/sitemap.xml']:
                self.assertEqual(self.client.get(path).status_code, 200)
        finally:
            sa.event.remove(self.engine, 'before_cursor_execute', capture)
        self.assertTrue(all(q.lstrip().upper().startswith(('SELECT', 'SET TRANSACTION READ ONLY')) for q in queries))
        with self.engine.connect() as c:
            self.assertEqual(counts, {name: c.scalar(sa.select(sa.func.count()).select_from(t)) for name, t in metadata.tables.items()})

    def test_active_snapshot_never_mixes_pending_db_fields(self):
        table = metadata.tables['content_contentpage']
        with self.engine.begin() as c:
            c.execute(sa.update(table).where(table.c.id == 302).values(title='NEW-DB-TITLE', body_html='PRIVATE-PENDING-BODY', is_published=False))
        response = self.client.get('/api/v1/content/pages/topic/')
        body = self.response(response, schema='ContentDeliveryResponse', delivery=True)
        self.assertEqual(body['data'], self.deliveries[302])
        self.assertNotIn('PRIVATE-PENDING-BODY', response.text)
        self.assertNotIn('NEW-DB-TITLE', self.client.get('/_content/index.json').text)
        # No raw DB fallback if the active artifact is unavailable/corrupt.
        (Path(self.files.name) / self.descriptor.release_id / 'pages/302.json').write_text('{}', encoding='utf-8')
        self.error(self.client.get('/api/v1/content/pages/topic/'), 503, 'SERVICE_UNAVAILABLE')

    def test_unverifiable_active_descriptor_fails_closed_without_redirect(self):
        from backend.models.protocol import journal
        with self.engine.begin() as c:
            c.execute(sa.update(journal).where(journal.c.id == self.descriptor.operation_id).values(manifest_digest='f' * 64))
        self.error(self.client.get('/api/v1/content/pages/topic/'), 503, 'SERVICE_UNAVAILABLE')
        self.error(self.client.get('/old.html', follow_redirects=False), 503, 'SERVICE_UNAVAILABLE')

    def rewrite_active_index(self, index):
        from backend.models.protocol import active, journal
        raw = json.dumps(index, ensure_ascii=False).encode('utf-8')
        (Path(self.files.name) / self.descriptor.release_id / 'index.json').write_bytes(raw)
        digest = sha256(raw).hexdigest()
        with self.engine.begin() as c:
            c.execute(sa.update(active).where(active.c.namespace == 'public').values(manifest_digest=digest))
            c.execute(sa.update(journal).where(journal.c.id == self.descriptor.operation_id).values(manifest_digest=digest))
        self.descriptor = replace(self.descriptor, manifest_digest=digest)

    def renderer_client(self, renderer):
        return TestClient(create_app(self.engine, self.signer, release_store=self.store,
            render_page=renderer), raise_server_exceptions=False)

    def test_i02_home_missing_alias_fails_closed_without_renderer_or_redirect(self):
        index = deepcopy(self.index)
        index['aliases'] = []
        index['redirects'].append({'old_path': '/glavnaya/', 'new_path': '/topic/', 'is_permanent': True})
        self.rewrite_active_index(index)
        rendered = []
        with self.renderer_client(lambda *args: rendered.append(args) or 'unexpected') as client:
            for path in ['/', '/glavnaya/', '/old.html', '/_content/index.json', '/api/v1/content/pages/glavnaya/']:
                with self.subTest(path=path):
                    response = client.get(path, follow_redirects=False)
                    self.error(response, 503, 'SERVICE_UNAVAILABLE')
                    self.assertNotIn('location', response.headers)
        self.assertEqual(rendered, [])
        raw = (Path(self.files.name) / self.descriptor.release_id / 'index.json').read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), self.descriptor.manifest_digest)

    def test_i02_valid_home_alias_canonical_and_identity_on_all_html_pages(self):
        rendered = []
        with self.renderer_client(lambda *args: rendered.append(deepcopy(args)) or 'synthetic renderer') as client:
            for path in ['/', '/glavnaya/', '/topic/', '/karta-sajta/?q=none']:
                self.assertEqual(client.get(path).status_code, 200)
                page, context, canonical = rendered[-1]
                self.assertEqual(context['pinned_release'], {'release_id': self.descriptor.release_id,
                    'manifest_digest': self.descriptor.manifest_digest})
                self.assertEqual(canonical, 'https://mathstart.example' + page['seo']['canonical_path'])
                self.assertNotIn('?', canonical)
                self.assertEqual('catalogue_full' in context, page['slug'] == 'karta-sajta')
            self.assertEqual(rendered[0][2], 'https://mathstart.example/')
            self.assertEqual(rendered[1][2], 'https://mathstart.example/')
            self.assertEqual(rendered[-1][1]['catalogue_count'], 0)
            self.assertEqual(rendered[-1][1]['catalogue_full'], self.index['catalogue'])

    def test_i02_catalogue_fields_filters_and_no_new_public_dto_or_routes(self):
        from backend.content.releases import active_release
        from backend.infrastructure.uow import UnitOfWork
        with UnitOfWork(self.engine) as uow:
            release = active_release(uow, self.store, 'public')
        rendered = []
        with self.renderer_client(lambda *args: rendered.append(deepcopy(args)) or 'synthetic renderer') as client:
            for query in ['q=none', 'q=miss&q=Stra%C3%9Fe&grade=unknown&ignored=x',
                          'grade=5-klass&subject=matematika', 'q=%20STRASSE%20']:
                self.assertEqual(client.get('/karta-sajta/?' + query).status_code, 200)
                from starlette.datastructures import QueryParams
                expected = release.catalogue(QueryParams(query))
                context = rendered[-1][1]
                self.assertEqual({k: context[k] for k in expected}, expected)
                self.assertEqual(context['catalogue_full'], self.index['catalogue'])
            self.assertEqual(client.get('/_content/index.json').json(), self.index)
            body = client.get('/api/v1/content/pages/karta-sajta/').json()['data']
            self.assertEqual(body, self.deliveries[304])
            self.assertNotIn('catalogue_full', body)
            self.assertNotIn('pinned_release', body)
            self.assertEqual(client.get('/api/v1/content/renderer-context/').status_code, 404)
            self.assertEqual(client.get('/sitemap.xml').status_code, 200)

    def test_i02_catalogue_without_home_remains_available(self):
        index = deepcopy(self.index)
        index['pages'] = [p for p in index['pages'] if p['page_type'] != 'home']
        index['aliases'] = []
        self.rewrite_active_index(index)
        rendered = []
        with self.renderer_client(lambda *args: rendered.append(deepcopy(args)) or 'synthetic renderer') as client:
            self.assertEqual(client.get('/karta-sajta/?q=none').status_code, 200)
            self.assertEqual(rendered[-1][1]['catalogue_count'], 0)
            self.assertEqual(rendered[-1][1]['catalogue_full'], index['catalogue'])
            self.assertEqual(rendered[-1][1]['pinned_release']['manifest_digest'], self.descriptor.manifest_digest)
            self.error(client.get('/'), 404, 'NOT_FOUND')
            self.assertEqual(client.get('/topic/').status_code, 200)

    def test_i02_renderer_mutations_cannot_change_pinned_release_index(self):
        loaded = []
        load = self.store.load
        def capture(descriptor):
            release = load(descriptor)
            loaded.append(release)
            return release
        def render(page, context, canonical):
            context['catalogue_full']['grades'][0]['title'] = 'mutated'
            context['catalogue_full']['sections'].clear()
            context['catalogue_topics'][0]['title'] = 'mutated topic'
            context['catalogue_subjects'].clear()
            context['pinned_release']['manifest_digest'] = 'f' * 64
            return 'synthetic renderer'
        with patch.object(self.store, 'load', side_effect=capture), self.renderer_client(render) as client:
            self.assertEqual(client.get('/karta-sajta/').status_code, 200)
        self.assertEqual(loaded[0].index, self.index)
        self.assertEqual(loaded[0].descriptor, self.descriptor)
        self.assertEqual(self.client.get('/_content/index.json').json(), self.index)

    def test_i02_renderer_failure_uses_safe_existing_503(self):
        def render(*args):
            raise RuntimeError('PRIVATE-PATH PASSWORD SQL renderer failure')
        with self.renderer_client(render) as client:
            response = client.get('/karta-sajta/?q=strasse')
            self.error(response, 503, 'SERVICE_UNAVAILABLE')
            self.assertNotIn('PASSWORD', response.text)
            self.assertNotIn('PRIVATE-PATH', response.text)

    def test_p2_renderer_top_level_page_mutation_cannot_change_validated_release(self):
        release = self.store.load(self.descriptor)
        original_pages, original_index = deepcopy(release.pages), deepcopy(release.index)
        def render(page, context, canonical):
            self.assertEqual(context['pinned_release']['manifest_digest'], release.descriptor.manifest_digest)
            self.assertEqual(canonical, 'https://mathstart.example/karta-sajta/')
            page['title'] = 'MUTATED BY RENDERER'
            return 'synthetic renderer'
        # Reuse the very same validated object to test the boundary independently
        # of the ordinary loader's fresh allocation on the next request.
        with patch.object(self.store, 'load', return_value=release), self.renderer_client(render) as client:
            self.assertEqual(client.get('/karta-sajta/').status_code, 200)
            response = client.get('/api/v1/content/pages/karta-sajta/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['data'], original_pages[304])
        self.assertEqual(release.pages, original_pages)
        self.assertEqual(release.index, original_index)

    def test_p2_nested_page_and_context_mutations_preserve_data_and_next_http_request(self):
        release = self.store.load(self.descriptor)
        original_pages, original_index = deepcopy(release.pages), deepcopy(release.index)
        canonical_urls = []
        identities = []
        def render(page, context, canonical):
            canonical_urls.append(canonical)
            identities.append(deepcopy(context['pinned_release']))
            page['seo']['canonical_path'] = '/mutated/'
            page['source']['source_digest'] = 'f' * 64
            page['assets'][0]['url'] = '/static/mutated.css'
            page['assets'].append({**page['assets'][0], 'order': 1})
            context['catalogue_full']['sections'].clear()
            context['catalogue_topics'][0]['title'] = 'mutated context'
            context['pinned_release']['release_id'] = 'foreign'
            return 'synthetic renderer'
        with patch.object(self.store, 'load', return_value=release), self.renderer_client(render) as client:
            self.assertEqual(client.get('/karta-sajta/').status_code, 200)
            response = client.get('/api/v1/content/pages/karta-sajta/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['data'], original_pages[304])
            self.assertEqual(client.get('/karta-sajta/').status_code, 200)
        self.assertEqual(canonical_urls, ['https://mathstart.example/karta-sajta/'] * 2)
        self.assertEqual(identities, [{'release_id': self.descriptor.release_id,
            'manifest_digest': self.descriptor.manifest_digest}] * 2)
        self.assertEqual(release.pages, original_pages)
        self.assertEqual(release.index, original_index)

    def test_p2_mutating_renderer_failure_is_safe_and_leaves_release_intact(self):
        release = self.store.load(self.descriptor)
        original_pages, original_index = deepcopy(release.pages), deepcopy(release.index)
        def render(page, context, canonical):
            page['title'] = 'mutated before failure'
            page['seo']['title'] = 'mutated nested SEO'
            page['assets'].clear()
            context['catalogue_full']['topics'].clear()
            raise RuntimeError('PRIVATE-PATH PASSWORD renderer failure')
        with patch.object(self.store, 'load', return_value=release), self.renderer_client(render) as client:
            response = client.get('/karta-sajta/')
            self.error(response, 503, 'SERVICE_UNAVAILABLE')
            self.assertNotIn('PASSWORD', response.text)
            self.assertNotIn('PRIVATE-PATH', response.text)
            self.assertEqual(client.get('/api/v1/content/pages/karta-sajta/').json()['data'], original_pages[304])
        self.assertEqual(release.pages, original_pages)
        self.assertEqual(release.index, original_index)

    def test_i02_release_switch_before_context_does_not_mix_r1_and_r2(self):
        from backend.content.releases import Release, active_release
        from backend.models.protocol import active, gate, journal
        release_id = 'synthetic-r2'
        root = Path(self.files.name) / release_id
        (root / 'pages').mkdir(parents=True)
        (root / 'assets').mkdir()
        (root / 'assets/theme.css').write_bytes(
            (Path(self.files.name) / self.descriptor.release_id / 'assets/theme.css').read_bytes())
        index = deepcopy(self.index)
        index['release_id'] = release_id
        for kind in ['grades', 'subjects', 'sections', 'topics']:
            index['catalogue'][kind][0]['title'] = 'R2 ' + index['catalogue'][kind][0]['title']
        for pk, data in deepcopy(self.deliveries).items():
            if pk == 304:
                data['title'] = 'R2 catalogue title'
            if pk == 302:
                data['title'] = index['catalogue']['topics'][0]['title']
                data['seo']['title'] = 'R2 topic title'
            (root / f'pages/{pk}.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        raw = json.dumps(index, ensure_ascii=False).encode('utf-8')
        (root / 'index.json').write_bytes(raw)
        digest = sha256(raw).hexdigest()
        provider = Release.renderer_context
        switched = False
        def switch_before_context(release, page, params):
            nonlocal switched
            if not switched:
                switched = True
                # Synthetic authority switch only: no production V04 publisher is invoked.
                with self.engine.begin() as c:
                    previous = dict(c.execute(sa.select(journal).where(
                        journal.c.id == self.descriptor.operation_id)).mappings().one())
                    operation_id = uuid.uuid4()
                    previous.update(id=operation_id, release_id=release_id, manifest_digest=digest,
                                    fence_generation=2, key_digest='4' * 64, plan_digest='5' * 64)
                    c.execute(sa.insert(journal).values(**previous))
                    c.execute(sa.update(gate).where(gate.c.namespace == 'public').values(fence_generation=2))
                    c.execute(sa.update(active).where(active.c.namespace == 'public').values(
                        operation_id=operation_id, release_id=release_id, manifest_digest=digest, fence_generation=2))
            return provider(release, page, params)
        rendered = []
        with patch('backend.infrastructure.http.app.active_release', wraps=active_release) as selected, \
             patch.object(Release, 'renderer_context', switch_before_context), \
             self.renderer_client(lambda *args: rendered.append(deepcopy(args)) or 'synthetic renderer') as client:
            self.assertEqual(client.get('/karta-sajta/').status_code, 200)
            self.assertEqual(selected.call_count, 1)
            self.assertEqual(client.get('/karta-sajta/').status_code, 200)
            self.assertEqual(selected.call_count, 2)
            # R1 remains valid on disk and in its committed journal. An invalid
            # R2 must fail closed instead of falling back to that old release.
            index_without_alias = deepcopy(index)
            index_without_alias['aliases'] = []
            broken = json.dumps(index_without_alias, ensure_ascii=False).encode('utf-8')
            (root / 'index.json').write_bytes(broken)
            with self.engine.begin() as c:
                c.execute(sa.update(active).where(active.c.namespace == 'public').values(
                    manifest_digest=sha256(broken).hexdigest()))
                c.execute(sa.update(journal).where(journal.c.release_id == release_id).values(
                    manifest_digest=sha256(broken).hexdigest()))
            self.error(client.get('/karta-sajta/'), 503, 'SERVICE_UNAVAILABLE')
            self.assertEqual(selected.call_count, 3)
            self.assertEqual(len(rendered), 2)
        self.assertEqual(rendered[0][1]['catalogue_full'], self.index['catalogue'])
        self.assertEqual(rendered[0][0], self.deliveries[304])
        self.assertEqual(rendered[0][1]['catalogue_topics'], self.index['catalogue']['topics'])
        self.assertEqual(rendered[0][1]['pinned_release'], {
            'release_id': self.descriptor.release_id, 'manifest_digest': self.descriptor.manifest_digest})
        self.assertEqual(rendered[1][1]['catalogue_full'], index['catalogue'])
        self.assertEqual(rendered[1][0]['title'], 'R2 catalogue title')
        self.assertEqual(rendered[1][1]['catalogue_topics'], index['catalogue']['topics'])
        self.assertEqual(rendered[1][1]['pinned_release'], {'release_id': release_id, 'manifest_digest': digest})


class SQLiteHTTPTests(HTTPAssertions, unittest.TestCase):
    def setUp(self):
        # Explicit, synthetic non-concurrency compatibility environment only.
        self.engine = sa.create_engine('sqlite+pysqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        self.prepare()

    def tearDown(self):
        self.finish()
        self.engine.dispose()
