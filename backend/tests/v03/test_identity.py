"""Real PostgreSQL identity/CSRF/receipt lifecycle and concurrent replay tests."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess
import unittest

import sqlalchemy as sa
from starlette.testclient import TestClient

from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import require_disposable
from backend.models.baseline import User, Grade, IdentityReceipt, StudentProfile, metadata
from backend.models.protocol import ReceiptBridge, TargetSession
from backend.users import passwords
from backend.users.security import Security, csrf_secret, mask
from backend.users.service import IdentityService

ORIGIN = 'https://mathstart.example'
KEY = 'synthetic-identity-test-key-not-production'
PASSWORD = 'Sample:mathematics!8592'


class PasswordTests(unittest.TestCase):
    def test_legacy_django_hashes_all_algorithms_unicode_old_iterations(self):
        legacy = os.environ['MATHSTART_LEGACY_PYTHON']
        script = '''
from django.conf import settings
settings.configure(USE_I18N=False)
from django.contrib.auth.hashers import PBKDF2PasswordHasher,PBKDF2SHA1PasswordHasher,Argon2PasswordHasher,BCryptSHA256PasswordHasher,ScryptPasswordHasher
import json
password='Sample:пароль!8592'
rows=[]
for klass in [PBKDF2PasswordHasher,PBKDF2SHA1PasswordHasher,Argon2PasswordHasher,BCryptSHA256PasswordHasher,ScryptPasswordHasher]:
 h=klass()
 if h.algorithm.startswith('pbkdf2'):
  encoded=h.encode(password,'synthetic-salt',iterations=12000)
 elif h.algorithm=='bcrypt_sha256':
  h.rounds=4
  encoded=h.encode(password,h.salt())
 else:
  encoded=h.encode(password,'synthetic-salt')
 rows.append([h.algorithm,encoded])
print(json.dumps(rows))
'''
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        result = subprocess.run([legacy, '-c', script], env=env, capture_output=True, timeout=60, check=True)
        vectors = json.loads(result.stdout)
        self.assertEqual(len(vectors), 5)
        for algorithm, encoded in vectors:
            with self.subTest(algorithm=algorithm):
                self.assertTrue(passwords.verify('Sample:пароль!8592', encoded))
                self.assertFalse(passwords.verify('incorrect-password', encoded))
        for encoded in ['!', '!unusable', 'unknown$encoded', 'pbkdf2_sha256$bad$salt$hash']:
            self.assertFalse(passwords.verify(PASSWORD, encoded))

    def test_validators_preserve_no_trim_similarity_common_numeric(self):
        user = User(username='syntheticStudent', first_name='Alexandra', last_name='Example', email='study@example.test')
        for value in ['short', '123456789', 'password', 'syntheticStudent', 'Alexandra']:
            self.assertFalse(passwords.validate_password(value, user))
        self.assertTrue(passwords.validate_password(PASSWORD, user))
        encoded = passwords.encode(' ' + PASSWORD + ' ')
        self.assertTrue(passwords.verify(' ' + PASSWORD + ' ', encoded))
        self.assertFalse(passwords.verify(PASSWORD, encoded))


class PostgreSQLIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sa.create_engine(os.environ['MATHSTART_V03_DATABASE_URL'], hide_parameters=True)
        with cls.engine.begin() as c:
            require_disposable(c)
            if c.scalar(sa.text('SHOW server_version_num')) < '160000':
                raise RuntimeError('PostgreSQL16 required')
        cls.security = Security(cls.engine, KEY, ORIGIN, secure=True)
        cls.service = IdentityService(cls.security)
        cls.app = create_app(cls.engine, Signer(KEY), identity_service=cls.service, public_origin=ORIGIN)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        with self.engine.begin() as c:
            c.execute(sa.text('TRUNCATE target_receipt_bridge,target_session,users_identityreceipt,users_studentprofile,users_loginwindow,auth_user RESTART IDENTITY CASCADE'))
            if not c.scalar(sa.select(sa.func.count()).select_from(metadata.tables['content_grade'])):
                c.execute(sa.insert(metadata.tables['content_grade']).values(id=73, title='5 класс', slug='5-klass', order=5))
        self.client = TestClient(self.app, base_url=ORIGIN)

    def tearDown(self):
        self.client.close()

    def headers(self, client=None, **extra):
        client = client or self.client
        token = client.get('/api/v1/auth/csrf/').json()['data']['csrf_token']
        return {'X-CSRFToken': token, 'Origin': ORIGIN, **extra}

    def register(self, username='syntheticStudent', client=None, key='register-key'):
        client = client or self.client
        return client.post('/api/v1/auth/register/', json={'username': username, 'password': PASSWORD},
                           headers=self.headers(client, **{'Idempotency-Key': key}))

    def test_register_login_rotation_profile_all_modes_logout(self):
        result = self.register()
        self.assertEqual(result.status_code, 201, result.text)
        self.assertEqual(result.headers['cache-control'], 'private, no-store')
        self.assertIn('HttpOnly', result.headers.get_list('set-cookie')[0])
        self.assertIn('Secure', result.headers.get_list('set-cookie')[0])
        before = self.client.cookies.get('sessionid')
        self.assertEqual(self.client.get('/api/v1/users/me/').json()['data']['id'], result.json()['data']['id'])
        for mode in ['START_ZERO', 'DIAGNOSTIC', 'SELF_REPORT']:
            body = {'selected_grade_id': 73, 'mode': mode}
            response = self.client.post('/api/v1/onboarding/complete/', json=body,
                         headers=self.headers(**{'Idempotency-Key': mode}))
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()['data']['onboarding_mode'], mode)
        response = self.client.patch('/api/v1/users/me/', json={'selected_grade_id': '73'}, headers=self.headers())
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/api/v1/auth/login/', json={'username': 'syntheticStudent', 'password': PASSWORD}, headers=self.headers())
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotEqual(before, self.client.cookies.get('sessionid'))
        self.assertEqual(self.client.post('/api/v1/auth/logout/', json={}, headers=self.headers()).status_code, 200)
        self.assertEqual(self.client.get('/api/v1/users/me/').status_code, 401)
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(uow.session.scalar(sa.select(sa.func.count()).select_from(User)), 1)
            self.assertEqual(set(uow.session.scalars(sa.select(ReceiptBridge.state))), {'REVOKED'})

    def test_implemented_canonical_route_metadata_matches_exact_eight_operation_set(self):
        document = json.loads(Path('specs/migration/r02-v1/implemented-routes-v1.json').read_text(encoding='utf-8'))
        expected = {(row['path'], row['method'].upper(), row['operation_id']) for row in document['operations']
                    if row['baseline_state'] == 'IMPLEMENTED'}
        canonical = {row['path'] for row in document['operations']}
        actual = {(row['path'], row['method'], row['operation_id']) for row in self.app.state.implemented_routes
                  if row['path'] in canonical}
        self.assertEqual(len(expected), 8)
        self.assertEqual(actual, expected)

    def test_exact_registration_and_onboarding_replay_conflict(self):
        first = self.register()
        cookie = self.client.cookies.get('sessionid')
        repeated = self.register()
        self.assertEqual(repeated.content, first.content)
        self.assertEqual(self.client.cookies.get('sessionid'), cookie)
        response = self.client.post('/api/v1/auth/register/', json={'username': 'changed', 'password': PASSWORD},
                      headers=self.headers(**{'Idempotency-Key': 'register-key'}))
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['error']['code'], 'IDEMPOTENCY_CONFLICT')
        body = {'selected_grade_id': 73, 'mode': 'SELF_REPORT'}
        first = self.client.post('/api/v1/onboarding/complete/', json=body, headers=self.headers(**{'Idempotency-Key': 'onboard-key'}))
        repeated = self.client.post('/api/v1/onboarding/complete/', json=body, headers=self.headers(**{'Idempotency-Key': 'onboard-key'}))
        self.assertEqual(first.content, repeated.content)
        response = self.client.post('/api/v1/onboarding/complete/', json={**body, 'mode': 'START_ZERO'}, headers=self.headers(**{'Idempotency-Key': 'onboard-key'}))
        self.assertEqual(response.status_code, 409)

    def test_lost_body_and_cookies_recovers_with_original_bootstrap_proof(self):
        headers = self.headers(**{'Idempotency-Key': 'lost-key'})
        old_csrf = self.client.cookies.get('csrftoken')
        body = {'username': 'lostResponse', 'password': PASSWORD}
        first = self.client.post('/api/v1/auth/register/', json=body, headers=headers)
        old_session = self.client.cookies.get('sessionid')
        self.client.cookies.clear()
        self.client.cookies.set('csrftoken', old_csrf, domain='mathstart.example', path='/')
        response = self.client.post('/api/v1/auth/register/', json=body, headers=self.headers(**{'Idempotency-Key': 'lost-key'}))
        self.assertEqual(response.content, first.content, response.text)
        self.assertNotEqual(self.client.cookies.get('sessionid'), old_session)
        self.assertEqual(self.client.get('/api/v1/users/me/').status_code, 200)
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(uow.session.scalar(sa.select(sa.func.count()).select_from(User)), 1)

    def test_revoked_original_proof_never_resurrects_registration(self):
        self.headers()
        original = self.client.cookies.get('csrftoken')
        self.assertEqual(self.register(key='revoke-key').status_code, 201)
        self.assertEqual(self.client.post('/api/v1/auth/logout/', json={}, headers=self.headers()).status_code, 200)
        self.client.cookies.clear()
        self.client.cookies.set('csrftoken', original, domain='mathstart.example', path='/')
        response = self.register(key='revoke-key')
        self.assertEqual(response.status_code, 409, response.text)
        self.assertEqual(self.client.get('/api/v1/users/me/').status_code, 401)

    def test_revoked_proof_cannot_reveal_digest_conflict_for_a_changed_body(self):
        self.headers()
        original = self.client.cookies.get('csrftoken')
        self.assertEqual(self.register(key='revoked-digest').status_code, 201)
        self.assertEqual(self.client.post('/api/v1/auth/logout/', json={}, headers=self.headers()).status_code, 200)
        self.client.cookies.clear()
        self.client.cookies.set('csrftoken', original, domain='mathstart.example', path='/')
        response = self.client.post('/api/v1/auth/register/', json={'username': 'changed', 'password': PASSWORD},
                         headers=self.headers(**{'Idempotency-Key': 'revoked-digest'}))
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['error']['code'], 'STATE_CONFLICT')

    def test_anonymous_wrong_password_is_not_authorized_to_observe_digest_conflict(self):
        self.headers()
        original = self.client.cookies.get('csrftoken')
        self.assertEqual(self.register(key='password-proof').status_code, 201)
        self.client.cookies.clear()
        self.client.cookies.set('csrftoken', original, domain='mathstart.example', path='/')
        response = self.client.post('/api/v1/auth/register/', json={'username': 'syntheticStudent', 'password': 'incorrect'},
                         headers=self.headers(**{'Idempotency-Key': 'password-proof'}))
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['error']['code'], 'STATE_CONFLICT')

    def test_csrf_host_origin_and_auth_precedence_before_json(self):
        self.assertEqual(self.client.patch('/api/v1/users/me/', content=b'bad').status_code, 401)
        self.assertEqual(self.client.post('/api/v1/auth/register/', content=b'bad').status_code, 403)
        headers = self.headers()
        self.assertEqual(self.client.post('/api/v1/auth/login/', content=b'bad', headers={**headers, 'Origin': 'https://evil.example'}).status_code, 403)
        self.assertEqual(self.client.get('/api/v1/auth/csrf/', headers={'Host': 'evil.example'}).status_code, 400)
        self.assertEqual(self.client.head('/api/v1/auth/csrf/').status_code, 400)
        self.assertEqual(self.client.post('/api/v1/auth/login', follow_redirects=False).status_code, 301)

    def test_strict_mutation_json_unknown_duplicate_nonfinite_and_size(self):
        headers = {**self.headers(), 'Content-Type': 'application/json', 'Idempotency-Key': 'strict'}
        for raw in [b'{"username":"a","password":"x","unknown":1}', b'{"username":"a","username":"b","password":"x"}', b'{"username":NaN,"password":"x"}', b'[]', b'\xff']:
            with self.subTest(raw_type=type(raw).__name__):
                self.assertEqual(self.client.post('/api/v1/auth/register/', content=raw, headers=headers).status_code, 400)
        response = self.client.post('/api/v1/auth/register/', content=b' ' * 65537, headers=headers)
        self.assertEqual(response.json()['error']['code'], 'LIMIT_EXCEEDED')

    def test_shared_pg_login_budget_and_forwarded_spoofing(self):
        headers = self.headers()
        for i in range(10):
            response = self.client.post('/api/v1/auth/login/', json={'username': 'absent', 'password': PASSWORD},
                        headers={**headers, 'X-Forwarded-For': f'192.0.2.{i}'})
            self.assertEqual(response.status_code, 401)
        response = self.client.post('/api/v1/auth/login/', json={'username': 'absent', 'password': PASSWORD}, headers=headers)
        self.assertEqual(response.status_code, 429)
        self.assertGreaterEqual(int(response.headers['retry-after']), 1)

    def test_concurrent_same_proof_registration_one_account_exact_receipt(self):
        secret = csrf_secret()
        headers = {'Origin': ORIGIN, 'X-CSRFToken': mask(secret), 'Idempotency-Key': 'concurrent-key'}
        def worker(_):
            with TestClient(self.app, base_url=ORIGIN) as client:
                client.cookies.set('csrftoken', secret, domain='mathstart.example', path='/')
                result = client.post('/api/v1/auth/register/', json={'username': 'concurrentStudent', 'password': PASSWORD}, headers=headers)
                return result.status_code, result.content
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(worker, range(2)))
        self.assertEqual([r[0] for r in results], [201, 201])
        self.assertEqual(results[0][1], results[1][1])
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(uow.session.scalar(sa.select(sa.func.count()).select_from(User)), 1)
            self.assertEqual(uow.session.scalar(sa.select(sa.func.count()).select_from(IdentityReceipt)), 1)

    def test_expired_session_is_denied_but_original_bootstrap_can_recover_within_window(self):
        self.headers()
        original = self.client.cookies.get('csrftoken')
        first = self.register(key='expiry-key')
        with self.engine.begin() as connection:
            connection.execute(sa.update(TargetSession).values(expires_at=sa.func.clock_timestamp() - sa.text("interval '1 second'")))
        self.assertEqual(self.client.get('/api/v1/users/me/').status_code, 401)
        self.client.cookies.clear()
        self.client.cookies.set('csrftoken', original, domain='mathstart.example', path='/')
        recovered = self.register(key='expiry-key')
        self.assertEqual(recovered.content, first.content)
        self.assertEqual(self.client.get('/api/v1/users/me/').status_code, 200)

    def test_replay_window_expiry_refuses_original_bootstrap_and_preserves_receipt(self):
        self.headers()
        original = self.client.cookies.get('csrftoken')
        self.assertEqual(self.register(key='window-key').status_code, 201)
        with self.engine.begin() as connection:
            connection.execute(sa.update(ReceiptBridge).values(
                created_at=sa.func.clock_timestamp() - sa.text("interval '8 days'"),
                replay_until=sa.func.clock_timestamp() - sa.text("interval '1 day'")))
        self.client.cookies.clear()
        self.client.cookies.set('csrftoken', original, domain='mathstart.example', path='/')
        self.assertEqual(self.register(key='window-key').status_code, 409)
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(uow.session.scalar(sa.select(sa.func.count()).select_from(IdentityReceipt)), 1)

    def test_account_switch_revokes_old_bootstrap_and_never_transfers_to_foreign_owner(self):
        self.headers()
        original = self.client.cookies.get('csrftoken')
        self.assertEqual(self.register(key='switch-key').status_code, 201)
        with TestClient(self.app, base_url=ORIGIN) as other:
            second = self.register(username='syntheticOther', client=other, key='other-key')
            self.assertEqual(second.status_code, 201)
        response = self.client.post('/api/v1/auth/login/', json={'username': 'syntheticOther', 'password': PASSWORD}, headers=self.headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['id'], second.json()['data']['id'])
        self.client.cookies.clear()
        self.client.cookies.set('csrftoken', original, domain='mathstart.example', path='/')
        self.assertEqual(self.register(key='switch-key').status_code, 409)

    def test_two_profile_writes_are_serialized_without_duplicate_profile_or_mastery(self):
        self.assertEqual(self.register().status_code, 201)
        cookie = self.client.cookies.get('sessionid')
        secret = self.client.cookies.get('csrftoken')
        def worker(mode):
            with TestClient(self.app, base_url=ORIGIN) as client:
                client.cookies.set('sessionid', cookie, domain='mathstart.example', path='/')
                client.cookies.set('csrftoken', secret, domain='mathstart.example', path='/')
                return client.post('/api/v1/onboarding/complete/', json={'selected_grade_id': 73, 'mode': mode},
                    headers={'Origin': ORIGIN, 'X-CSRFToken': mask(secret), 'Idempotency-Key': mode}).status_code
        with ThreadPoolExecutor(max_workers=2) as executor:
            self.assertEqual(list(executor.map(worker, ['START_ZERO', 'SELF_REPORT'])), [200, 200])
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(uow.session.scalar(sa.select(sa.func.count()).select_from(StudentProfile)), 1)


if __name__ == '__main__':
    unittest.main()
