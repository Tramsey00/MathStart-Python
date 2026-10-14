"""Independent-audit F01/F02 regressions through real FastAPI ASGI routes."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import sqlalchemy as sa
from sqlalchemy.pool import StaticPool

from backend.models.protocol import active, journal
from backend.tests.v02.test_http import HTTPAssertions
from backend.tests.v02 import test_postgres as postgres_fixture

ADMIN = postgres_fixture.ADMIN


class AssetRegressions:
    prepare = HTTPAssertions.prepare
    finish = HTTPAssertions.finish
    response = HTTPAssertions.response
    error = HTTPAssertions.error

    def direct(self, path, method='GET'):
        return self.client.request(method, path, follow_redirects=False)

    def page_assets(self, page_id, assets):
        path = Path(self.files.name) / self.descriptor.release_id / f'pages/{page_id}.json'
        page = json.loads(path.read_text(encoding='utf-8'))
        page['assets'] = deepcopy(assets)
        path.write_text(json.dumps(page, ensure_ascii=False), encoding='utf-8')
        return page

    def asset(self, key, url, raw, kind, order, lifecycle='none'):
        path = Path(self.files.name) / self.descriptor.release_id / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return {'storage_key': key, 'url': url, 'sha256': sha256(raw).hexdigest(),
                'kind': kind, 'order': order, 'lifecycle': lifecycle}

    def redirects(self, rules):
        index = deepcopy(self.index)
        index['redirects'] = rules
        raw = json.dumps(index, ensure_ascii=False).encode('utf-8')
        (Path(self.files.name) / self.descriptor.release_id / 'index.json').write_bytes(raw)
        digest = sha256(raw).hexdigest()
        with self.engine.begin() as connection:
            connection.execute(sa.update(active).where(active.c.namespace == 'public').values(manifest_digest=digest))
            connection.execute(sa.update(journal).where(journal.c.id == self.descriptor.operation_id).values(manifest_digest=digest))

    def test_f01_shared_asset_same_order_release_available(self):
        for slug in ['glavnaya', 'topic', 'karta-sajta']:
            body = self.response(self.direct(f'/api/v1/content/pages/{slug}/'), schema='ContentDeliveryResponse', delivery=True)
            self.assertEqual(body['data']['assets'][0]['order'], 0)
        self.assertEqual(self.direct('/static/theme.css').status_code, 200)

    def test_f01_shared_asset_different_page_order_preserved_over_http(self):
        asset = deepcopy(self.deliveries[302]['assets'][0])
        asset['order'] = 1
        self.page_assets(302, [asset])
        topic = self.response(self.direct('/api/v1/content/pages/topic/'), schema='ContentDeliveryResponse', delivery=True)
        home = self.response(self.direct('/api/v1/content/pages/glavnaya/'), schema='ContentDeliveryResponse', delivery=True)
        self.assertEqual(topic['data']['assets'][0], asset)
        self.assertEqual(home['data']['assets'][0]['order'], 0)
        self.assertEqual(self.direct('/static/theme.css').status_code, 200)
        self.assertEqual(self.direct('/_content/index.json').status_code, 200)

    def test_f01_shared_asset_different_valid_digests_fail_closed(self):
        asset = self.asset('assets/other.css', '/static/theme.css', b'body { color: red; }', 'style', 0)
        self.page_assets(302, [asset])
        self.error(self.direct('/api/v1/content/pages/topic/'), 503, 'SERVICE_UNAVAILABLE')
        self.error(self.direct('/static/theme.css'), 503, 'SERVICE_UNAVAILABLE')

    def test_f01_shared_asset_different_storage_same_bytes_fail_closed(self):
        asset = self.asset('assets/alias.css', '/static/theme.css', b'body { color: black; }', 'style', 0)
        self.page_assets(302, [asset])
        self.error(self.direct('/api/v1/content/pages/topic/'), 503, 'SERVICE_UNAVAILABLE')

    def test_f01_shared_asset_incompatible_kind_lifecycle_fail_closed(self):
        for changes in [{'kind': 'script'}, {'lifecycle': 'full_document'}]:
            with self.subTest(changes=changes):
                asset = {**self.deliveries[302]['assets'][0], **changes}
                self.page_assets(302, [asset])
                self.error(self.direct('/api/v1/content/pages/topic/'), 503, 'SERVICE_UNAVAILABLE')

    def test_f01_shared_script_valid_but_different_lifecycle_fail_closed(self):
        script = self.asset('assets/shared.js', '/static/shared.js', b'/* reviewed */', 'script', 1, 'full_document')
        self.page_assets(301, [self.deliveries[301]['assets'][0], script])
        self.page_assets(302, [self.deliveries[302]['assets'][0], {**script, 'lifecycle': 'mount_dispose'}])
        self.error(self.direct('/api/v1/content/pages/topic/'), 503, 'SERVICE_UNAVAILABLE')

    def test_f01_multiple_css_js_page_orders_and_unique_union(self):
        first = deepcopy(self.deliveries[301]['assets'][0])
        second = self.asset('assets/second.css', '/static/second.css', b'p { color: blue; }', 'style', 1)
        script = self.asset('assets/widget.js', '/static/widget.js', b'/* reviewed synthetic widget */', 'script', 2, 'full_document')
        home_assets = [first, second, script]
        topic_assets = [{**second, 'order': 0}, {**script, 'order': 1}, {**first, 'order': 2}]
        self.page_assets(301, home_assets)
        self.page_assets(302, topic_assets)
        for slug, expected in [('glavnaya', home_assets), ('topic', topic_assets)]:
            body = self.response(self.direct(f'/api/v1/content/pages/{slug}/'), schema='ContentDeliveryResponse', delivery=True)
            self.assertEqual(body['data']['assets'], expected)
        for asset in home_assets:
            response = self.direct(asset['url'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(sha256(response.content).hexdigest(), asset['sha256'])
        from backend.content.releases import active_release
        from backend.infrastructure.uow import UnitOfWork
        with UnitOfWork(self.engine) as uow:
            release = active_release(uow, self.store, 'public')
        self.assertEqual(set(release.assets), {'/static/theme.css', '/static/second.css', '/static/widget.js'})
        self.assertEqual(len(self.direct('/_content/index.json').json()['pages']), 3)

    def test_f01_missing_and_damaged_asset_still_fail_closed(self):
        asset = deepcopy(self.deliveries[302]['assets'][0])
        asset['storage_key'] = 'assets/missing.css'
        self.page_assets(302, [asset])
        self.error(self.direct('/api/v1/content/pages/topic/'), 503, 'SERVICE_UNAVAILABLE')
        self.page_assets(302, self.deliveries[302]['assets'])
        (Path(self.files.name) / self.descriptor.release_id / 'assets/theme.css').write_bytes(b'damaged')
        self.error(self.direct('/api/v1/content/pages/topic/'), 503, 'SERVICE_UNAVAILABLE')

    def test_f02_missing_static_permanent_redirect_get_and_head(self):
        self.redirects([{'old_path': '/static/old.css', 'new_path': '/static/theme.css', 'is_permanent': True}])
        for method in ['GET', 'HEAD']:
            response = self.direct('/static/old.css', method)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response.headers['location'], '/static/theme.css')
            self.assertEqual(response.content, b'')

    def test_f02_missing_static_temporary_redirect(self):
        self.redirects([{'old_path': '/static/old.css', 'new_path': '/static/theme.css', 'is_permanent': False}])
        response = self.direct('/static/old.css')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['location'], '/static/theme.css')

    def test_f02_missing_media_redirect_get_and_head(self):
        media = self.asset('assets/diagram.png', '/media/diagram.png', b'\x89PNG\r\n\x1a\nsynthetic', 'media', 1)
        self.page_assets(302, [self.deliveries[302]['assets'][0], media])
        self.redirects([{'old_path': '/media/old.png', 'new_path': '/media/diagram.png', 'is_permanent': True}])
        for method in ['GET', 'HEAD']:
            response = self.direct('/media/old.png', method)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response.headers['location'], '/media/diagram.png')
        self.assertEqual(self.direct('/media/diagram.png').status_code, 200)

    def test_f02_working_asset_precedes_conflicting_redirect_and_method405(self):
        self.redirects([{'old_path': '/static/theme.css', 'new_path': '/topic/', 'is_permanent': True}])
        self.assertEqual(self.direct('/static/theme.css').status_code, 200)
        self.assertEqual(self.direct('/static/theme.css', 'HEAD').status_code, 200)
        self.assertEqual(self.direct('/static/theme.css', 'HEAD').content, b'')
        response = self.direct('/static/theme.css', 'POST')
        self.assertEqual(response.status_code, 405)
        self.assertNotIn('location', response.headers)

    def test_f02_missing_asset_without_active_rule404(self):
        from backend.content.projection import build_index_candidate, delivery_candidate, ReviewedSource
        from backend.infrastructure.uow import UnitOfWork
        from backend.models.baseline import ContentPage, Redirect
        with self.engine.begin() as connection:
            connection.execute(sa.insert(Redirect).values(id=603, old_path='/media/inactive.png',
                new_path='/static/theme.css', is_active=False, is_permanent=True))
        with UnitOfWork(self.engine) as uow:
            pages = uow.session.scalars(sa.select(ContentPage).where(ContentPage.is_published.is_(True)))
            deliveries = {p.id: delivery_candidate(uow, p.slug, ReviewedSource(
                f'site_content/pages/{p.slug}/page.json', '1' * 64, ())) for p in pages}
            rules = build_index_candidate(uow, 'candidate', deliveries)['redirects']
        self.assertNotIn('/media/inactive.png', [r['old_path'] for r in rules])
        self.redirects(rules)
        for path in ['/static/missing.css', '/media/inactive.png']:
            response = self.direct(path)
            self.assertEqual(response.status_code, 404)
            self.assertNotIn('location', response.headers)

    def test_f02_unsafe_redirect_targets_fail_closed(self):
        for target in ['https://evil.test/x', '//evil.test/x', '/admin/secret/', '/media/../secret', '/static/%252e%252e/secret']:
            with self.subTest(target=target):
                self.redirects([{'old_path': '/static/old.css', 'new_path': target, 'is_permanent': True}])
                response = self.direct('/static/old.css')
                self.error(response, 503, 'SERVICE_UNAVAILABLE')
                self.assertNotIn('location', response.headers)

    def test_f02_traversal_invalid_encoding_private_paths_never_redirect(self):
        self.redirects([{'old_path': '/static/old.css', 'new_path': '/static/theme.css', 'is_permanent': True},
                        {'old_path': '/static/\ufffd.css', 'new_path': '/static/theme.css', 'is_permanent': True}])
        for path in ['/static/%2e%2e/secret', '/media/%252e%252e/secret', '/media/a%5csecret',
                     '/static/%FF.css', '/static/%ZZ.css', '/admin/secret/', '/api/v1/unknown/']:
            with self.subTest(path=path):
                response = self.direct(path)
                self.assertEqual(response.status_code, 404)
                self.assertNotIn('location', response.headers)

    def test_f02_missing_active_release503_not_redirect(self):
        self.redirects([{'old_path': '/static/old.css', 'new_path': '/static/theme.css', 'is_permanent': True}])
        with self.engine.begin() as connection:
            connection.execute(sa.delete(active).where(active.c.namespace == 'public'))
        response = self.direct('/static/old.css')
        self.error(response, 503, 'SERVICE_UNAVAILABLE')
        self.assertNotIn('location', response.headers)

    def test_f02_corrupt_index503_not_redirect(self):
        self.redirects([{'old_path': '/static/old.css', 'new_path': '/static/theme.css', 'is_permanent': True}])
        (Path(self.files.name) / self.descriptor.release_id / 'index.json').write_bytes(b'corrupt index')
        response = self.direct('/static/old.css')
        self.error(response, 503, 'SERVICE_UNAVAILABLE')
        self.assertNotIn('location', response.headers)

    def test_f02_private_storage_restriction503_not_bypassed(self):
        private = self.asset('private/secret.png', '/media/secret.png', b'private synthetic bytes', 'media', 1)
        self.page_assets(302, [self.deliveries[302]['assets'][0], private])
        self.redirects([{'old_path': '/media/old.png', 'new_path': '/media/secret.png', 'is_permanent': True}])
        response = self.direct('/media/old.png')
        self.error(response, 503, 'SERVICE_UNAVAILABLE')
        self.assertNotIn('location', response.headers)

    def test_f02_asset_integrity_failure503_not_hidden_by_redirect(self):
        self.redirects([{'old_path': '/static/old.css', 'new_path': '/static/theme.css', 'is_permanent': True}])
        (Path(self.files.name) / self.descriptor.release_id / 'assets/theme.css').write_bytes(b'corrupt')
        response = self.direct('/static/old.css')
        self.error(response, 503, 'SERVICE_UNAVAILABLE')
        self.assertNotIn('location', response.headers)

    def test_f02_unicode_and_percent_encoded_location_preserved(self):
        rules = [{'old_path': '/static/старый.css', 'new_path': '/static/theme%2Ecss', 'is_permanent': True},
                 {'old_path': '/media/старый.pdf', 'new_path': '/media/карта.pdf', 'is_permanent': False}]
        self.redirects(rules)
        for path, status, location in [('/static/старый.css', 301, '/static/theme%2Ecss'),
                                       ('/media/старый.pdf', 302, '/media/%D0%BA%D0%B0%D1%80%D1%82%D0%B0.pdf')]:
            response = self.direct(path)
            self.assertEqual(response.status_code, status)
            self.assertEqual(response.headers['location'], location)

    def test_f02_non404_private_and_csrf_errors_not_redirected(self):
        self.redirects([{'old_path': '/topic/', 'new_path': '/', 'is_permanent': True}])
        self.error(self.direct('/topic/', 'POST'), 403, 'CSRF_FAILED')
        self.error(self.direct('/api/v1/staff/pages/302/'), 401, 'AUTHENTICATION_REQUIRED')

    def test_f02_non404_resolver_errors_and_internal_failure_not_redirected(self):
        from backend.infrastructure.http.transport import APIError
        self.redirects([{'old_path': '/topic/', 'new_path': '/', 'is_permanent': True}])
        faults = [(APIError(409, 'STATE_CONFLICT', 'State conflict.'), 409, 'STATE_CONFLICT'),
                  (APIError(503, 'SERVICE_UNAVAILABLE', 'Service temporarily unavailable.'), 503, 'SERVICE_UNAVAILABLE'),
                  (RuntimeError('INTERNAL-SENTINEL SQL/path/DSN'), 503, 'SERVICE_UNAVAILABLE')]
        for fault, status, code in faults:
            with self.subTest(status=status, type=type(fault).__name__), patch(
                    'backend.content.releases.Release.page_path', side_effect=fault):
                response = self.direct('/topic/')
                self.error(response, status, code)
                self.assertNotIn('location', response.headers)
                self.assertNotIn('INTERNAL-SENTINEL', response.text)


class SQLiteAssetTests(AssetRegressions, unittest.TestCase):
    def setUp(self):
        self.engine = sa.create_engine('sqlite+pysqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        self.prepare()

    def tearDown(self):
        self.finish()
        self.engine.dispose()


@unittest.skipUnless(ADMIN, 'NOT RUN: dedicated disposable PostgreSQL URL is required')
class PostgreSQLAssetTests(AssetRegressions, unittest.TestCase):
    setUpClass = classmethod(postgres_fixture.PostgreSQLHTTPTests.setUpClass.__func__)
    tearDownClass = classmethod(postgres_fixture.PostgreSQLHTTPTests.tearDownClass.__func__)
    setUp = postgres_fixture.PostgreSQLHTTPTests.setUp
    tearDown = postgres_fixture.PostgreSQLHTTPTests.tearDown

    def test_f02_actual_django_static_media_redirect_comparator(self):
        # Real baseline WhiteNoise/Django static serving + Redirect ORM/middleware,
        # isolated rows and files; comparator rolls its rule writes back.
        cases = [
            {'old_path': '/static/old.css', 'new_path': '/static/theme.css', 'is_permanent': True, 'method': 'GET'},
            {'old_path': '/static/old.css', 'new_path': '/static/theme.css', 'is_permanent': False, 'method': 'HEAD'},
            {'old_path': '/media/old.png', 'new_path': '/static/theme.css', 'is_permanent': True, 'method': 'GET'},
            {'old_path': '/static/theme.css', 'new_path': '/topic/', 'is_permanent': True, 'method': 'GET'},
            {'old_path': '/static/theme.css', 'new_path': '/topic/', 'is_permanent': True, 'method': 'POST'},
            {'old_path': '/static/old.css', 'new_path': '/static/theme.css', 'is_permanent': True, 'method': 'POST'},
            {'old_path': '/static/старый.css', 'new_path': '/static/theme%2Ecss', 'is_permanent': True, 'method': 'GET'},
            {'old_path': '/media/старый.pdf', 'new_path': '/media/карта.pdf', 'is_permanent': False, 'method': 'HEAD'}]
        environment = {**os.environ, 'DJANGO_DB_BACKEND': 'postgresql', 'DJANGO_DB_HOST': '127.0.0.1',
            'DJANGO_DB_PORT': '15441', 'DJANGO_DB_NAME': self.name, 'DJANGO_DB_USER': 'postgres',
            'DJANGO_DB_PASSWORD': 'synthetic-local-only', 'DJANGO_SECRET_KEY': 'synthetic-f02-comparator',
            'DJANGO_DEBUG': '0', 'DJANGO_RUNTIME_ROOT': str(Path(self.files.name).resolve()), 'PYTHONIOENCODING': 'utf-8'}
        result = subprocess.run([sys.executable, '-m', 'backend.tests.v02.legacy_comparator'],
            input=json.dumps([{'resource': '__asset_redirect', **case} for case in cases]).encode(),
            env=environment, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace')[-1500:])
        probes = []
        for oracle in json.loads(result.stdout):
            case = oracle['case']
            rule = {k: case[k] for k in ['old_path', 'new_path', 'is_permanent']}
            self.redirects([rule])
            response = self.direct(case['old_path'], case['method'])
            with self.subTest(case=case):
                self.assertEqual(response.status_code, oracle['status'])
                self.assertEqual(response.headers.get('location'), oracle['location'])
                probes.append({'case': case, 'django': {'status': oracle['status'], 'location': oracle['location']},
                               'fastapi': {'status': response.status_code, 'location': response.headers.get('location')}})
        Path('var', 'ms7-mig-v02-f02-probes-' + self.name + '.json').write_text(
            json.dumps({'database': self.name, 'disposable': True, 'probes': probes}, ensure_ascii=False, indent=2), encoding='utf-8')
