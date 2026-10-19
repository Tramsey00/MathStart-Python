"""Actual Django session serialization oracle; target verifier imports no Django."""
from scripts.legacy_oracle import oracle_root, oracle_environment

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest

from backend.infrastructure.http.signing import Signer
from backend.users.legacy_proof import registration_proof, transfer_digest
from backend.users.security import auth_hash

KEY = 'synthetic-cutover-proof-key'
OLD_KEY = 'synthetic-retained-session-key'
NOW = datetime(2026, 10, 17, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[3]


class LegacyProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = SimpleNamespace(id=701, is_active=True, password='pbkdf2_sha256$synthetic$source$hash')
        cls.data = {'_auth_user_id': '701', '_auth_user_backend': 'django.contrib.auth.backends.ModelBackend',
                    '_auth_user_hash': auth_hash(cls.user, OLD_KEY), 'identity_registration_scope': 'bootstrap:' + 'a' * 64}
        code = '''
import json,sys
from django.conf import settings
settings.configure(SECRET_KEY=sys.argv[1], SECRET_KEY_FALLBACKS=[], INSTALLED_APPS=[])
from django.contrib.sessions.backends.db import SessionStore
from django.core import signing
data=json.load(sys.stdin)
print(json.dumps([SessionStore().encode(data),signing.dumps(data,key=sys.argv[1],salt='django.contrib.sessions.SessionStore',compress=False)]))
'''
        env = dict(os.environ); env.pop('PYTHONPATH', None)
        result = subprocess.run([os.environ['MATHSTART_LEGACY_PYTHON'], '-c', code, OLD_KEY],
                                input=json.dumps(cls.data), text=True, capture_output=True, timeout=30, cwd=oracle_root(), env=oracle_environment(env))
        if result.returncode:
            raise RuntimeError('Independent legacy session oracle failed')
        cls.vectors = json.loads(result.stdout)
        if len(cls.vectors) != 2:
            raise RuntimeError('Nonempty compressed/uncompressed session oracle required')

    def session(self, raw=None, *, expires=None):
        return SimpleNamespace(session_key='s' * 32, session_data=raw or self.vectors[0], expire_date=expires or NOW + timedelta(days=1))

    def test_real_legacy_compressed_plain_keyring_and_owner_binding(self):
        for vector in self.vectors:
            proof = registration_proof(self.session(vector), self.user, [KEY, OLD_KEY], NOW)
            self.assertIsNotNone(proof)
            self.assertEqual(proof.original_scope, self.data['identity_registration_scope'])
            self.assertEqual(proof.owner_user_id, self.user.id)
            self.assertEqual(proof.bootstrap_fingerprint, 'a' * 64)
            self.assertEqual(proof.transfer_binding_digest, transfer_digest('s' * 32, self.user, KEY))
            self.assertIsNone(registration_proof(self.session(vector), self.user, [KEY], NOW))

    def test_signature_expiry_inactive_owner_and_changed_auth_hash_fail_closed(self):
        self.assertIsNone(registration_proof(self.session(self.vectors[0] + 'x'), self.user, [KEY, OLD_KEY], NOW))
        self.assertIsNone(registration_proof(self.session(expires=NOW), self.user, [KEY, OLD_KEY], NOW))
        self.assertIsNone(registration_proof(self.session(), SimpleNamespace(**{**vars(self.user), 'is_active': False}), [KEY, OLD_KEY], NOW))
        changed = SimpleNamespace(**{**vars(self.user), 'password': 'new-reviewed-hash'})
        self.assertIsNone(registration_proof(self.session(), changed, [KEY, OLD_KEY], NOW))
        self.assertNotEqual(transfer_digest('s' * 32, self.user, KEY), transfer_digest('s' * 32, changed, KEY))
        self.assertIsNone(registration_proof(self.session(), SimpleNamespace(**{**vars(self.user), 'id': 702}), [KEY, OLD_KEY], NOW))

    def test_signed_foreign_backend_scope_and_id_coercions_cannot_create_proof(self):
        for values in [[], {**self.data, '_auth_user_id': 701}, {**self.data, '_auth_user_id': '0701'},
                       {**self.data, '_auth_user_backend': 'foreign.backend'}, {**self.data, 'identity_registration_scope': None},
                       {**self.data, 'identity_registration_scope': 'user:701'}, {**self.data, '_auth_user_hash': []},
                       {**self.data, '_auth_user_hash': '\u2603'}]:
            with self.subTest(kind=type(values).__name__):
                token = Signer(OLD_KEY).dumps(values, 'django.contrib.sessions.SessionStore', compress=True)
                self.assertIsNone(registration_proof(self.session(token), self.user, [KEY, OLD_KEY], NOW))

    def test_empty_keyring_naive_time_and_malformed_storage_are_not_authority(self):
        with self.assertRaises(ValueError):
            registration_proof(self.session(), self.user, [], NOW)
        self.assertIsNone(registration_proof(self.session(), self.user, [KEY, OLD_KEY], NOW.replace(tzinfo=None)))
        for raw in ['unsigned', '{}', 'x' * 131073]:
            self.assertIsNone(registration_proof(self.session(raw), self.user, [KEY, OLD_KEY], NOW))
        invalid = self.session(); invalid.session_key = '../outside'
        self.assertIsNone(registration_proof(invalid, self.user, [KEY, OLD_KEY], NOW))


if __name__ == '__main__':
    unittest.main()
