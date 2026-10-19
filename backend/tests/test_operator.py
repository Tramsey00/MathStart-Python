"""Required fresh operator CLI and preservation refusals on owned PostgreSQL."""
from datetime import timedelta
import os
import subprocess
import sys
import unittest
import uuid

import sqlalchemy as sa
from starlette.testclient import TestClient

from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.schema import SchemaMismatch
from backend.migrations.schema import inventory
from backend.release_migrate import source_digest
from backend.migrations.upgrade import fresh
from backend.models.baseline import User, StudentProfile, IdentityReceipt, metadata
from backend.tests import test_postgres as fixtures
from backend.users.operator import create_initial
from backend.users.passwords import verify
from backend.users.security import Security
from backend.users.service import IdentityService


class InitialOperatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.PostgreSQLTests.setUpClass()
        cls.fixture = fixtures.PostgreSQLTests()

    @classmethod
    def tearDownClass(cls):
        fixtures.PostgreSQLTests.tearDownClass()

    def install(self, engine):
        with engine.begin() as connection:
            fresh(connection)

    def test_actual_cli_creates_hash_profile_and_real_staff_login_then_refuses_replay(self):
        with self.fixture.database() as engine:
            self.install(engine)
            username, password = 'operator_' + uuid.uuid4().hex[:12], 'S7!' + uuid.uuid4().hex
            env = {**os.environ, 'MATHSTART_DATABASE_URL': engine.url.render_as_string(hide_password=False),
                   'MATHSTART_DB_BACKEND': 'postgresql', 'MATHSTART_OPERATOR_USERNAME': username,
                   'MATHSTART_OPERATOR_PASSWORD': password}
            engine.dispose()
            argv = [sys.executable, '-m', 'backend.users.operator', '--maintenance', '--from-environment']
            completed = subprocess.run(argv, env=env, capture_output=True, timeout=60)
            self.assertEqual(completed.returncode, 0, completed.stderr.decode())
            self.assertNotIn(password.encode(), completed.stdout + completed.stderr)
            self.assertNotIn(username.encode(), completed.stdout + completed.stderr)
            with UnitOfWork(engine) as uow:
                user = uow.session.scalar(sa.select(User))
                self.assertTrue(user.is_active and user.is_staff and user.is_superuser)
                self.assertTrue(verify(password, user.password))
                self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
                profile = uow.session.scalar(sa.select(StudentProfile))
                self.assertEqual(profile.user_id, user.id)
                self.assertFalse(profile.onboarding_complete)
                self.assertIsNone(profile.onboarding_mode)
                self.assertIsNone(profile.selected_grade_id)
            key, origin = 'synthetic-operator-test-key-only', 'https://operator.example'
            app = create_app(engine, Signer(key), identity_service=IdentityService(Security(engine, key, origin)), public_origin=origin)
            with TestClient(app, base_url=origin) as client:
                token = client.get('/api/v1/auth/csrf/').json()['data']['csrf_token']
                login = client.post('/api/v1/auth/login/', json={'username': username, 'password': password},
                                    headers={'Origin': origin, 'X-CSRFToken': token})
                self.assertEqual(login.status_code, 200)
                self.assertEqual(client.get('/api/v1/users/me/').status_code, 200)
            with engine.connect() as connection:
                before = fixtures.data_digest(connection)
                private_before = source_digest(connection, key, inventory(connection))
            engine.dispose()
            repeated = subprocess.run(argv, env={**env, 'MATHSTART_OPERATOR_USERNAME': 'different_operator'}, capture_output=True, timeout=60)
            self.assertNotEqual(repeated.returncode, 0)
            with engine.connect() as connection:
                self.assertEqual(before, fixtures.data_digest(connection))
                self.assertEqual(private_before, source_digest(connection, key, inventory(connection)))

    def test_invalid_credentials_or_missing_maintenance_do_not_seed_or_write(self):
        with self.fixture.database() as engine:
            self.install(engine)
            with engine.connect() as connection:
                before = fixtures.data_digest(connection)
            for username, password, email, maintenance in [('bad user', 'Good7!' + uuid.uuid4().hex, '', True),
                    ('new_operator', '12345678', '', True), ('new_operator', 'password', '', True),
                    ('new_operator', 'Good7!' + uuid.uuid4().hex, 'invalid', True),
                    ('new_operator', 'Good7!' + uuid.uuid4().hex, '', False)]:
                with self.assertRaises(ValueError):
                    create_initial(engine, username, password, email, maintenance=maintenance)
            with engine.connect() as connection:
                self.assertEqual(before, fixtures.data_digest(connection))

    def test_pending_identity_or_legacy_history_blocks_even_without_users(self):
        for retained in ('pending', 'history'):
            with self.subTest(retained=retained), self.fixture.database() as engine:
                self.install(engine)
                with engine.begin() as connection:
                    if retained == 'history':
                        connection.execute(sa.insert(metadata.tables['django_migrations']).values(app='legacy', name='retained_history'))
                    else:
                        now = connection.scalar(sa.text('SELECT clock_timestamp()'))
                        connection.execute(sa.insert(metadata.tables['users_identityreceipt']).values(scope='anonymous:retained',
                            operation='register', key_digest='a' * 64, request_digest='b' * 64, expires_at=now + timedelta(days=1)))
                    before = fixtures.data_digest(connection)
                with self.assertRaises(SchemaMismatch):
                    create_initial(engine, 'new_operator', 'Good7!' + uuid.uuid4().hex, maintenance=True)
                with engine.connect() as connection:
                    self.assertEqual(before, fixtures.data_digest(connection))

    def test_other_database_client_blocks_fresh_operator(self):
        with self.fixture.database() as engine:
            self.install(engine)
            with engine.connect() as other:
                other.execute(sa.text('SELECT 1'))
                with self.assertRaises(SchemaMismatch):
                    create_initial(engine, 'new_operator', 'Good7!' + uuid.uuid4().hex, maintenance=True)
                self.assertEqual(other.scalar(sa.select(sa.func.count()).select_from(User)), 0)
