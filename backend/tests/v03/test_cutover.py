"""Owned PostgreSQL cutover/import/F-login, refusal and lock regressions."""
from scripts.legacy_oracle import oracle_root, oracle_environment

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import timedelta
import json
import os
import subprocess
import unittest
import uuid
from threading import Barrier, local
from unittest.mock import patch

import sqlalchemy as sa
from starlette.testclient import TestClient

from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.http.transport import APIError
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import require_disposable
from backend.models.baseline import IdentityReceipt, LegacySession, User
from backend.models.protocol import ReceiptBridge, TargetSession, CutoverCheckpoint
from backend.users.cutover import CutoverImport, outer_lock, source_digest
from backend.users.security import Security, auth_hash
from backend.users.service import IdentityService
from backend.tests.v03.test_identity import KEY, ORIGIN, PASSWORD


class CutoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sa.create_engine(os.environ['MATHSTART_V03_DATABASE_URL'], hide_parameters=True)
        cls.role = 'test_cutover_' + uuid.uuid4().hex
        with cls.engine.begin() as c:
            require_disposable(c)
            if int(c.scalar(sa.text('SHOW server_version_num'))) < 160000:
                raise RuntimeError('PostgreSQL16 required')
            c.execute(sa.text('CREATE ROLE ' + cls.role + ' NOLOGIN'))

    @classmethod
    def tearDownClass(cls):
        try:
            with cls.engine.begin() as c:
                c.execute(sa.text('DROP ROLE ' + cls.role))
                c.execute(sa.text('TRUNCATE target_receipt_bridge,target_session,target_identity_cutover,django_session,django_migrations,users_identityreceipt,users_studentprofile,users_loginwindow,auth_user RESTART IDENTITY CASCADE'))
        finally:
            cls.engine.dispose()

    def setUp(self):
        with self.engine.begin() as c:
            c.execute(sa.text('TRUNCATE target_receipt_bridge,target_session,target_identity_cutover,django_session,django_migrations,users_identityreceipt,users_studentprofile,users_loginwindow,auth_user RESTART IDENTITY CASCADE'))
        self.security = Security(self.engine, KEY, ORIGIN)
        self.service = IdentityService(self.security)
        self.app = create_app(self.engine, Signer(KEY), identity_service=self.service, public_origin=ORIGIN)
        self.client = TestClient(self.app, base_url=ORIGIN)
        self.addCleanup(self.client.close)
        self.body = {'username': 'cutoverStudent', 'password': PASSWORD}
        headers = self.headers(self.client)
        registered = self.client.post('/api/v1/auth/register/', json=self.body,
                headers={**headers, 'Idempotency-Key': 'original-register-key'})
        self.assertEqual(registered.status_code, 201, registered.text)
        self.response = registered.json()
        self.owner = self.response['data']['id']
        self.old_key = 's' * 32
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            user = s.get(User, self.owner)
            bridge = s.scalar(sa.select(ReceiptBridge))
            self.scope = bridge.original_scope
            data = {'_auth_user_id': str(user.id), '_auth_user_backend': 'django.contrib.auth.backends.ModelBackend',
                    '_auth_user_hash': auth_hash(user, KEY), 'identity_registration_scope': self.scope}
            # Actual separate Django session serializer, not a target-generated
            # fixture. Target interpreter remains Django-free.
            code = '''
import json,sys
from django.conf import settings
settings.configure(SECRET_KEY=sys.argv[1], SECRET_KEY_FALLBACKS=[], INSTALLED_APPS=[])
from django.contrib.sessions.backends.db import SessionStore
print(SessionStore().encode(json.load(sys.stdin)))
'''
            env = dict(os.environ); env.pop('PYTHONPATH', None)
            encoded = subprocess.run([env['MATHSTART_LEGACY_PYTHON'], '-c', code, KEY], input=json.dumps(data),
                cwd=oracle_root(), env=oracle_environment(env), text=True, capture_output=True, timeout=30, check=True).stdout.strip()
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            s.add(LegacySession(session_key=self.old_key, session_data=encoded, expire_date=now + timedelta(days=1)))
            uow.commit()
        self.importer = CutoverImport(self.engine, (KEY,), self.role)

    def headers(self, client):
        return {'Origin': ORIGIN, 'X-CSRFToken': client.get('/api/v1/auth/csrf/').json()['data']['csrf_token']}

    def apply(self):
        plan = self.importer.preview(uuid.uuid4())
        self.assertFalse(self.importer.apply(plan)['repeated'])
        self.security.cutover_digest, self.security.legacy_writer_role = plan['checkpoint_digest'], self.role
        return plan

    def receipt_snapshot(self):
        with self.engine.connect() as c:
            return [dict(row) for row in c.execute(sa.select(IdentityReceipt)).mappings()]

    def login(self, *, key=None, password=PASSWORD):
        client = TestClient(self.app, base_url=ORIGIN)
        self.addCleanup(client.close)
        if key:
            client.cookies.set('sessionid', key)
        response = client.post('/api/v1/auth/login/', json={**self.body, 'password': password}, headers=self.headers(client))
        return client, response

    def test_real_legacy_import_f_login_exact_replay_and_readonly_checkpoint_repeat(self):
        before = self.receipt_snapshot()
        # Exercise creation from a legacy receipt with no pre-existing bridge.
        with self.engine.begin() as c:
            c.execute(sa.delete(ReceiptBridge))
        plan = self.apply()
        self.assertEqual(self.receipt_snapshot(), before)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(ReceiptBridge.state)), 'DETACHED')
            self.assertIsNotNone(c.scalar(sa.select(TargetSession.revoked_at)))
            self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(LegacySession)), 1)
        client, logged = self.login(key=self.old_key)
        self.assertEqual(logged.status_code, 200, logged.text)
        self.assertNotEqual(client.cookies.get('sessionid', domain='mathstart.example', path='/'), self.old_key)
        replay = client.post('/api/v1/auth/register/', json=self.body,
                headers={**self.headers(client), 'Idempotency-Key': 'original-register-key'})
        self.assertEqual(replay.status_code, 201, replay.text)
        self.assertEqual(replay.json(), self.response)
        with UnitOfWork(self.engine) as uow:
            before_repeat = source_digest(uow.session, KEY)
        self.assertTrue(self.importer.apply(plan)['repeated'])
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(source_digest(uow.session, KEY), before_repeat)
        self.assertEqual(self.receipt_snapshot(), before)
        self.assertEqual(client.get('/api/v1/users/me/').status_code, 200)

    def test_missing_unknown_checkpoint_and_legacy_cookie_never_authenticate(self):
        _, logged = self.login(key=self.old_key)
        self.assertEqual(logged.status_code, 503)
        plan = self.apply()
        self.security.cutover_digest = '0' * 64
        _, logged = self.login(key=self.old_key)
        self.assertEqual(logged.status_code, 503)
        self.security.cutover_digest = plan['checkpoint_digest']
        anonymous = TestClient(self.app, base_url=ORIGIN)
        self.addCleanup(anonymous.close)
        anonymous.cookies.set('sessionid', self.old_key)
        self.assertEqual(anonymous.get('/api/v1/users/me/').status_code, 401)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(CutoverCheckpoint)), 1)

    def test_legacy_history_without_sessions_or_receipts_still_requires_cutover(self):
        from backend.models.baseline import metadata
        with self.engine.begin() as c:
            c.execute(sa.delete(ReceiptBridge))
            c.execute(sa.delete(IdentityReceipt))
            c.execute(sa.delete(LegacySession))
            c.execute(sa.insert(metadata.tables['django_migrations']).values(app='sessions', name='0001_initial',
                applied=sa.func.clock_timestamp()))
        with self.assertRaises(APIError) as rejected:
            self.service.budget('synthetic-cutover-client')
        self.assertEqual(rejected.exception.status, 503)
        self.apply()
        _, logged = self.login()
        self.assertEqual(logged.status_code, 200, logged.text)

    def test_password_or_login_alone_cannot_select_original_receipt(self):
        self.apply()
        _, rejected = self.login(key=self.old_key, password='incorrect')
        self.assertEqual(rejected.status_code, 401)
        client, logged = self.login()
        self.assertEqual(logged.status_code, 200)
        replay = client.post('/api/v1/auth/register/', json=self.body,
            headers={**self.headers(client), 'Idempotency-Key': 'original-register-key'})
        self.assertEqual(replay.status_code, 409)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(ReceiptBridge.state)), 'DETACHED')

    def test_changed_source_or_different_checkpoint_refused_without_effects(self):
        plan = self.importer.preview(uuid.uuid4())
        with self.engine.begin() as c:
            c.execute(sa.update(User).values(first_name='Reviewed source changed'))
        with self.assertRaises(APIError):
            self.importer.apply(plan)

        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(CutoverCheckpoint)), 0)
        self.apply()
        with self.assertRaises(APIError):
            self.importer.apply(plan)

    def test_duplicate_scope_bridge_facts_refuse_import_without_changes(self):
        with self.engine.begin() as c:
            bridge = c.execute(sa.select(ReceiptBridge)).mappings().one()
            c.execute(sa.insert(ReceiptBridge).values(**{**dict(bridge), 'id': uuid.uuid4(),
                'bootstrap_fingerprint': '0' * 64}))
        plan = self.importer.preview(uuid.uuid4())
        with UnitOfWork(self.engine) as uow:
            before = source_digest(uow.session, KEY)
        with self.assertRaises(APIError):
            self.importer.apply(plan)
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(source_digest(uow.session, KEY), before)
            self.assertEqual(uow.session.scalar(sa.select(sa.func.count()).select_from(CutoverCheckpoint)), 0)

    def test_unsupported_retained_password_format_blocks_preview_without_reset(self):
        with self.engine.begin() as c:
            c.execute(sa.update(User).values(password='unknown$synthetic-retained-format'))
        with self.assertRaises(APIError):
            self.importer.preview(uuid.uuid4())
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(User.password)), 'unknown$synthetic-retained-format')
            self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(CutoverCheckpoint)), 0)

    def test_draining_login_flag_does_not_hide_an_already_connected_writer(self):
        import secrets
        password = secrets.token_urlsafe(24)
        literal = str(sa.literal(password).compile(dialect=self.engine.dialect, compile_kwargs={'literal_binds': True}))
        connection = None
        legacy = sa.create_engine(self.engine.url.set(username=self.role, password=password), hide_parameters=True)
        try:
            with self.engine.begin() as c:
                c.execute(sa.text('ALTER ROLE ' + self.role + ' LOGIN PASSWORD ' + literal))
            connection = legacy.connect()
            connection.execute(sa.text('SELECT 1'))
            with self.engine.begin() as c:
                c.execute(sa.text('ALTER ROLE ' + self.role + ' NOLOGIN'))
            with self.assertRaises(APIError):
                self.importer.preview(uuid.uuid4())
        finally:
            if connection is not None:
                connection.close()
            legacy.dispose()
            with self.engine.begin() as c:
                c.execute(sa.text('ALTER ROLE ' + self.role + ' NOLOGIN PASSWORD NULL'))

    def test_live_or_member_legacy_role_blocks_import_and_target_writes(self):
        with self.engine.begin() as c:
            c.execute(sa.text('ALTER ROLE ' + self.role + ' LOGIN'))
        try:
            with self.assertRaises(APIError):
                self.importer.preview(uuid.uuid4())
        finally:
            with self.engine.begin() as c:
                c.execute(sa.text('ALTER ROLE ' + self.role + ' NOLOGIN'))
        self.apply()
        with self.engine.begin() as c:
            c.execute(sa.text('GRANT ' + self.role + ' TO CURRENT_USER'))
        try:
            _, logged = self.login(key=self.old_key)
            self.assertEqual(logged.status_code, 503)
        finally:
            with self.engine.begin() as c:
                c.execute(sa.text('REVOKE ' + self.role + ' FROM CURRENT_USER'))

    def test_terminal_bridge_never_revives(self):
        with self.engine.begin() as c:
            c.execute(sa.update(ReceiptBridge).values(state='REVOKED', session_id=None, transfer_binding_digest=None))
        self.apply()
        client, logged = self.login(key=self.old_key)
        self.assertEqual(logged.status_code, 200)
        replay = client.post('/api/v1/auth/register/', json=self.body,
            headers={**self.headers(client), 'Idempotency-Key': 'original-register-key'})
        self.assertEqual(replay.status_code, 409)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(ReceiptBridge.state)), 'REVOKED')

    def test_competing_f_logins_observing_same_epoch_issue_only_one_session(self):
        self.apply()
        barrier, calls = Barrier(2), local()
        original = self.security.writer
        def synchronized(session):
            calls.count = getattr(calls, 'count', 0) + 1
            if calls.count == 2:  # after budget and the F observation, before locks
                barrier.wait(timeout=10)
            return original(session)
        def login(_):
            try:
                self.service.login(self.body, 'synthetic-client', None, legacy_session_key=self.old_key)
                return 200
            except APIError as error:
                return error.status
        with patch.object(self.security, 'writer', synchronized), ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(login, range(2))), [200, 409])
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(sa.func.count()).select_from(TargetSession)), 2)
            self.assertEqual(c.scalar(sa.select(ReceiptBridge.state)), 'ACTIVE')

    def test_expired_or_inactive_legacy_owner_cannot_gain_transfer(self):
        with self.engine.begin() as c:
            c.execute(sa.update(LegacySession).values(expire_date=sa.func.clock_timestamp()))
            c.execute(sa.update(User).values(is_active=False))
        self.apply()
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(ReceiptBridge.state)), 'REVOKED')
            self.assertIsNone(c.scalar(sa.select(ReceiptBridge.transfer_binding_digest)))
        _, response = self.login(key=self.old_key)
        self.assertEqual(response.status_code, 401)

    def test_cutover_cli_plan_is_exclusive_and_apply_is_repeatable(self):
        import tempfile
        from pathlib import Path
        from backend.users.cutover_cli import main
        from contextlib import redirect_stdout
        import io
        environment = {'MATHSTART_DATABASE_URL': self.engine.url.render_as_string(hide_password=False),
            'MATHSTART_DB_BACKEND': 'postgresql', 'MATHSTART_HTTP_SIGNING_KEY': KEY,
            'MATHSTART_HTTP_SIGNING_FALLBACK_KEYS': '[]', 'MATHSTART_LEGACY_WRITER_ROLE': self.role}
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, environment), redirect_stdout(io.StringIO()):
            path = Path(directory) / 'plan.json'
            command = ['preview', '--plan', str(path), '--checkpoint-id', str(uuid.uuid4())]
            self.assertEqual(main(command), 0)
            before = path.read_bytes()
            self.assertEqual(main(command), 1)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(main(['apply', '--plan', str(path)]), 0)
            self.assertEqual(main(['apply', '--plan', str(path)]), 0)

    def test_exclusive_import_waits_for_target_writer_transaction(self):
        with ThreadPoolExecutor(max_workers=1) as pool:
            with UnitOfWork(self.engine) as uow:
                outer_lock(uow.session)
                future = pool.submit(self.importer.preview, uuid.uuid4())
                with self.assertRaises(TimeoutError):
                    future.result(timeout=0.3)
            plan = future.result(timeout=10)
        self.assertFalse(self.importer.apply(plan)['repeated'])


if __name__ == '__main__':
    unittest.main()
