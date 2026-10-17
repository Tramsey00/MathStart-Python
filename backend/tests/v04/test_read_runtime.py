"""PG read-session authorization without importing the deferred identity service."""
from datetime import timedelta
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest
import string
import asyncio
import threading
import time
from unittest.mock import patch

import httpx

import sqlalchemy as sa
from starlette.requests import Request
from starlette.testclient import TestClient

from backend.content.public_runtime import ReadSessionAuthenticator
from backend.content.public_runtime import create_public_app
from backend.content.public_runtime import public_csrf_check
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import require_disposable
from backend.models.baseline import User
from backend.models.protocol import TargetSession


class PublicCsrfTests(unittest.TestCase):
    secret = 'aB3d' * 8

    def masked(self, secret):
        alphabet, mask = string.ascii_letters + string.digits, 'zY7w' * 8
        return mask + ''.join(alphabet[(alphabet.index(a) + alphabet.index(b)) % 62]
                              for a, b in zip(secret, mask))

    def request(self, cookie=None, token=None, origin=None, referer=None):
        headers = {name: value for name, value in [('cookie', 'csrftoken=' + cookie if cookie else None),
                   ('x-csrftoken', token), ('origin', origin), ('referer', referer)] if value is not None}
        return Request({'type': 'http', 'headers': [(k.encode(), v.encode()) for k, v in headers.items()]})

    def test_raw_and_masked_tokens_accept_only_matching_secrets(self):
        for cookie in [self.secret, self.masked(self.secret)]:
            for token in [self.secret, self.masked(self.secret)]:
                self.assertTrue(public_csrf_check(self.request(cookie, token, 'http://localhost'), 'http://localhost'))
        for token in [None, '', 'a' * 31, 'a' * 33, 'a' * 63, 'a' * 65, '!' * 32, 'b' * 32]:
            self.assertFalse(public_csrf_check(self.request(self.secret, token), 'http://localhost'))
        self.assertFalse(public_csrf_check(self.request(None, self.secret), 'http://localhost'))

    def test_origin_and_https_referer_are_required_and_exact(self):
        for origin in ['http://evil.example', 'null', 'http://localhost:81', 'http://localhost.evil.example']:
            self.assertFalse(public_csrf_check(self.request(self.secret, self.secret, origin), 'http://localhost'))
        self.assertTrue(public_csrf_check(self.request(self.secret, self.secret), 'http://localhost'))
        for referer in [None, 'http://localhost/path', 'https://evil.example/', 'https://[invalid']:
            self.assertFalse(public_csrf_check(self.request(self.secret, self.secret, referer=referer), 'https://localhost'))
        self.assertTrue(public_csrf_check(self.request(self.secret, self.secret,
                        referer='https://localhost/path?q=1'), 'https://localhost'))


class AuxiliaryConcurrencyTests(unittest.IsolatedAsyncioTestCase):
    async def test_asset_verification_does_not_block_other_requests(self):
        started, release = threading.Event(), threading.Event()
        def slow_release(*args):
            started.set()
            release.wait(3)
            return object()
        with patch('backend.content.public_runtime.UnitOfWork'), \
             patch('backend.content.public_runtime.active_release', side_effect=slow_release), \
             patch('backend.content.public_runtime.artifact_for', return_value=(Path('.'), {})), \
             patch('backend.content.public_runtime.artifact_bytes', return_value=b'body'):
            app = create_public_app(object(), Signer('synthetic-concurrency-key'),
                    release_root=Path('.'), artifact_root=Path('.'), artifact_digests={}, origin='http://localhost')
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://localhost') as client:
                pending = asyncio.create_task(client.get('/assets/slow.js'))
                try:
                    self.assertTrue(await asyncio.to_thread(started.wait, 5))
                    before = time.monotonic()
                    response = await client.get('/', headers={'Host': 'untrusted.example'})
                    self.assertEqual(response.status_code, 400)
                    self.assertLess(time.monotonic() - before, 1)
                    self.assertFalse(pending.done())
                finally:
                    release.set()
                    result = await pending
                self.assertEqual(result.status_code, 200)
                self.assertEqual(result.content, b'body')


class ReadSessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DatabaseConfig.from_environment())
        with cls.engine.begin() as connection:
            require_disposable(connection)
        cls.key = os.environ['MATHSTART_HTTP_SIGNING_KEY']
        cls.auth = ReadSessionAuthenticator(cls.engine, cls.key)
        data = json.loads(Path(os.environ['MATHSTART_STAFF_COOKIE_FILE']).read_text(encoding='utf-8'))
        cls.token = data['cookies'][0]['value']

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def request(self, token=None):
        raw = b'' if token is None else ('sessionid=' + token).encode()
        return Request({'type': 'http', 'headers': [(b'cookie', raw)]})

    def test_current_opaque_session_and_no_sql_writes(self):
        statements = []
        def observe(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement)
        sa.event.listen(self.engine, 'before_cursor_execute', observe)
        try:
            identity = self.auth(self.request(self.token))
            self.assertIsNotNone(identity)
            self.assertTrue(all(s.lstrip().upper().startswith(('SELECT', 'SET TRANSACTION READ ONLY')) for s in statements))
        finally:
            sa.event.remove(self.engine, 'before_cursor_execute', observe)

    def test_missing_wrong_and_oversize_tokens_refused(self):
        for token in [None, 'incorrect-opaque-token', 'x' * 257]:
            self.assertIsNone(self.auth(self.request(token)))

    def test_expiry_revocation_and_auth_hash_mismatch_refused(self):
        with self.engine.connect() as c:
            row = c.execute(sa.select(TargetSession)).mappings().one()
        for change in [{'expires_at': row['created_at'] - timedelta(seconds=1)},
                       {'revoked_at': row['created_at']}, {'auth_hash': '0' * 64}]:
            try:
                with self.engine.begin() as c:
                    c.execute(sa.update(TargetSession).where(TargetSession.id == row['id']).values(**change))
                self.assertIsNone(self.auth(self.request(self.token)))
            finally:
                with self.engine.begin() as c:
                    c.execute(sa.update(TargetSession).where(TargetSession.id == row['id']).values(**{k: row[k] for k in change}))

    def test_inactive_user_refused_and_keyring_verified(self):
        identity = self.auth(self.request(self.token))
        try:
            with self.engine.begin() as c:
                c.execute(sa.update(User).where(User.id == identity.user_id).values(is_active=False))
            self.assertIsNone(self.auth(self.request(self.token)))
        finally:
            with self.engine.begin() as c:
                c.execute(sa.update(User).where(User.id == identity.user_id).values(is_active=True))
        self.assertIsNotNone(ReadSessionAuthenticator(self.engine, 'synthetic-new-key', [self.key])(self.request(self.token)))
        self.assertIsNone(ReadSessionAuthenticator(self.engine, 'synthetic-wrong-key')(self.request(self.token)))

    def client(self):
        app = create_public_app(self.engine, Signer(self.key),
                release_root=Path(os.environ['MATHSTART_STAFF_COOKIE_FILE']).parent / 'releases',
                artifact_root=Path('var/unused-artifact-in-api-tests'), artifact_digests={},
                origin='http://127.0.0.1:8121')
        client = TestClient(app, base_url='http://127.0.0.1:8121')
        client.cookies.set('sessionid', self.token, domain='127.0.0.1', path='/')
        return client

    def test_real_nine_staff_lists_details_history_are_private_read_only(self):
        statements = []
        def observe(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement)
        sa.event.listen(self.engine, 'before_cursor_execute', observe)
        try:
            with self.client() as client:
                for resource in ['grades', 'subjects', 'sections', 'pages', 'publications', 'media_assets', 'redirects', 'users', 'groups']:
                    response = client.get(f'/api/v1/staff/{resource}/?page_size=1')
                    self.assertEqual(response.status_code, 200, resource)
                    self.assertEqual(response.headers['cache-control'], 'private, no-store')
                    self.assertTrue(response.json()['data'], resource)
                    identity = response.json()['data'][0]['id']
                    for suffix in ['', 'history/']:
                        result = client.get(f'/api/v1/staff/{resource}/{identity}/' + suffix)
                        self.assertEqual(result.status_code, 200, resource + suffix)
                        self.assertEqual(result.headers['cache-control'], 'private, no-store')
            self.assertTrue(all(s.lstrip().upper().startswith(('SELECT', 'SET TRANSACTION READ ONLY')) for s in statements))
        finally:
            sa.event.remove(self.engine, 'before_cursor_execute', observe)

    def test_staff_api_anonymous_nonstaff_bad_host_and_mutations_fail_closed(self):
        with self.client() as client:
            client.cookies.clear()
            self.assertEqual(client.get('/api/v1/staff/users/').status_code, 401)
            client.cookies.set('sessionid', self.token, domain='127.0.0.1', path='/')
            identity = self.auth(self.request(self.token))
            try:
                with self.engine.begin() as c:
                    c.execute(sa.update(User).where(User.id == identity.user_id).values(is_staff=False))
                self.assertEqual(client.get('/api/v1/staff/users/').status_code, 403)
            finally:
                with self.engine.begin() as c:
                    c.execute(sa.update(User).where(User.id == identity.user_id).values(is_staff=True))
            self.assertEqual(client.get('/api/v1/staff/users/', headers={'Host': 'untrusted.example'}).status_code, 400)
            self.assertEqual(client.post('/api/v1/staff/pages/', json={}).status_code, 403)
            self.assertEqual(client.post('/api/v1/staff/users/', json={}).status_code, 400)

    def test_public_unsafe_csrf_wiring_preserves_read_and_error_precedence(self):
        secret = PublicCsrfTests.secret
        with self.client() as client:
            client.cookies.set('csrftoken', secret, domain='127.0.0.1', path='/')
            headers = {'X-CSRFToken': PublicCsrfTests().masked(secret), 'Origin': 'http://127.0.0.1:8121'}
            for path, expected in [('/robots.txt', 200), ('/sitemap.xml', 200),
                                   ('/absent-csrf-test-page/', 404), ('/', 503)]:
                for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    with self.subTest(path=path, method=method):
                        self.assertEqual(client.request(method, path, headers=headers).status_code, expected)
                        rejected = client.request(method, path)
                        self.assertEqual(rejected.status_code, 403)
                        self.assertEqual(rejected.json()['error']['code'], 'CSRF_FAILED')
            self.assertEqual(client.post('/robots.txt', headers={**headers, 'Origin': 'http://evil.example'}).status_code, 403)
            self.assertEqual(client.post('/robots.txt', headers={**headers, 'Host': 'evil.example'}).status_code, 400)


class CompiledArtifactTests(unittest.TestCase):
    """Output hashes and live authority protect UI assets without lesson loading."""
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DatabaseConfig.from_environment())
        with cls.engine.begin() as connection:
            require_disposable(connection)
        cls.artifact_root = Path(os.environ['MATHSTART_PUBLIC_ARTIFACT_ROOT'])
        cls.digests = json.loads(os.environ['MATHSTART_PUBLIC_ARTIFACT_DIGESTS'])
        cls.manifest = json.loads((cls.artifact_root / 'output-manifest.json').read_bytes())
        cls.app = create_public_app(cls.engine, Signer('synthetic-ui-artifact-test-key'),
            release_root=Path(os.environ['MATHSTART_STAFF_COOKIE_FILE']).parent / 'releases',
            artifact_root=cls.artifact_root, artifact_digests=cls.digests, origin='http://127.0.0.1:8121')

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def test_ui_shell_and_compiled_asset_check_output_not_unrelated_lesson_dtos(self):
        from backend.content.verified_release_cache import VerifiedReleaseStore
        item = next(row for row in self.manifest['files'] if row['path'].startswith('assets/') and row['path'].endswith('.js'))
        with patch.object(VerifiedReleaseStore, 'load', side_effect=AssertionError('UI asset does not consume lesson DTOs')):
            with TestClient(self.app, base_url='http://127.0.0.1:8121') as client:
                result = client.get('/' + item['path'])
                self.assertEqual(result.status_code, 200)
                self.assertEqual(sha256(result.content).hexdigest(), item['sha256'])
                private = client.get('/account/')
                self.assertEqual(private.status_code, 200)
                self.assertEqual(private.headers['cache-control'], 'private, no-store')
                self.assertNotIn('canonical_url', private.text)

    def test_compiled_asset_corruption_still_fails_closed(self):
        item = next(row for row in self.manifest['files'] if row['path'].startswith('assets/') and row['path'].endswith('.js'))
        path = self.artifact_root / item['path']
        raw = path.read_bytes()
        try:
            path.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
            with TestClient(self.app, base_url='http://127.0.0.1:8121') as client:
                result = client.get('/' + item['path'])
                self.assertEqual(result.status_code, 503)
                self.assertEqual(result.json()['error']['code'], 'SERVICE_UNAVAILABLE')
        finally:
            path.write_bytes(raw)


if __name__ == '__main__':
    unittest.main()
