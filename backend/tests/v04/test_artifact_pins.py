"""Real PostgreSQL row-version checks; a digest alone never authorizes reuse."""
from datetime import datetime, timezone
from hashlib import sha256
import os
import re
import unittest
import uuid
from unittest.mock import patch

import sqlalchemy as sa

from backend.content.artifact_pins import PublicationArtifactPins
from backend.content.build import encoded
from backend.migrations.upgrade import fresh, require_disposable
from backend.models.protocol import journal
from backend.verification_suite import owned_database


class ArtifactPinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = sa.create_engine(os.environ['MATHSTART_V04_DATABASE_URL'], hide_parameters=True)
        with cls.parent.connect() as c:
            require_disposable(c)
        cls.admin = sa.create_engine(cls.parent.url.set(database='postgres'), isolation_level='AUTOCOMMIT', hide_parameters=True)

    @classmethod
    def tearDownClass(cls):
        cls.admin.dispose(); cls.parent.dispose()

    def setUp(self):
        self.owned = owned_database(self.admin, self.parent.url, 'artifactpins')
        self.engine = self.owned.__enter__()
        self.addCleanup(self.owned.__exit__, None, None, None)
        with self.engine.begin() as c:
            fresh(c)
        self.plan = {'version': 'prepared-publication-v1', 'release_id': 'pin-r1',
                     'manifest_digest': '1' * 64, 'output_manifest_digest': '2' * 64}
        self.pin = {key: self.plan[key] for key in ('release_id', 'manifest_digest')}
        self.id = uuid.uuid4()
        instant = datetime.now(timezone.utc)
        with self.engine.begin() as c:
            c.execute(sa.insert(journal).values(id=self.id, namespace='public', key_digest='3' * 64,
                plan_digest=sha256(encoded(self.plan)).hexdigest(), plan=self.plan, release_id=self.pin['release_id'],
                manifest_digest=self.pin['manifest_digest'], owner_id=uuid.uuid4(), fence_generation=1,
                lease_until=instant, phase='ACTIVATED', db_committed=True, activation_status='APPLIED',
                created_at=instant, updated_at=instant))
        self.pins = PublicationArtifactPins(self.engine, {})

    def update(self, **values):
        with self.engine.begin() as c:
            c.execute(sa.update(journal).where(journal.c.id == self.id).values(**values))

    def test_hit_checks_metadata_but_does_not_transfer_site_sized_plan(self):
        with patch.object(self.pins, '_verify', wraps=self.pins._verify) as verify:
            self.assertEqual(self.pins(self.pin), '2' * 64)
            statements = []
            def captured(connection, cursor, statement, parameters, context, executemany):
                statements.append(statement)
            sa.event.listen(self.engine, 'before_cursor_execute', captured)
            try:
                self.assertEqual(self.pins(self.pin), '2' * 64)
            finally:
                sa.event.remove(self.engine, 'before_cursor_execute', captured)
            self.assertTrue(any('row_xid' in statement for statement in statements))
            self.assertFalse(any(re.search(r'\btarget_publication_journal\.plan\b', statement) for statement in statements))
            self.assertEqual(verify.call_count, 1)
            self.update(updated_at=datetime.now(timezone.utc))
            self.assertEqual(self.pins(self.pin), '2' * 64)
            self.assertEqual(verify.call_count, 2)

    def test_same_digest_changed_plan_cannot_reuse_verified_output(self):
        self.assertEqual(self.pins(self.pin), '2' * 64)
        self.update(plan={**self.plan, 'output_manifest_digest': '4' * 64})
        with self.assertRaises(Exception):
            self.pins(self.pin)

    def test_applied_and_manifest_authority_is_checked_even_when_cached(self):
        for values in ({'activation_status': 'INTENT'}, {'manifest_digest': '4' * 64}):
            self.update(activation_status='APPLIED', manifest_digest='1' * 64)
            self.assertEqual(self.pins(self.pin), '2' * 64)
            self.update(**values)
            with self.assertRaises(Exception):
                self.pins(self.pin)

    def test_expired_verification_and_changed_initial_trust_require_revalidation(self):
        self.assertEqual(self.pins(self.pin), '2' * 64)
        with patch('backend.content.artifact_pins.monotonic', return_value=10**12), patch.object(
                self.pins, '_verify', wraps=self.pins._verify) as verify:
            self.assertEqual(self.pins(self.pin), '2' * 64)
            self.assertEqual(verify.call_count, 1)
        self.pins.initial[self.pin['release_id']] = '4' * 64
        with self.assertRaises(Exception):
            self.pins(self.pin)


if __name__ == '__main__':
    unittest.main()
