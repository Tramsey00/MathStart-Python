"""PG read-session authorization without importing the deferred identity service."""
from datetime import timedelta
import json
import os
from pathlib import Path
import unittest

import sqlalchemy as sa
from starlette.requests import Request

from backend.content.public_runtime import ReadSessionAuthenticator
from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import require_disposable
from backend.models.baseline import User
from backend.models.protocol import TargetSession


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


if __name__ == '__main__':
    unittest.main()
