"""Real release CLI and maintenance/drift refusals on owned PostgreSQL fixtures."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch

import sqlalchemy as sa

from backend import release_migrate as release
from backend.migrations.schema import SchemaMismatch, assert_baseline, inventory
from backend.infrastructure.http.transport import APIError
from backend.models.baseline import metadata, GRADE_EPOCH
from backend.tests import test_postgres as fixtures


class ReleaseMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Required suite fails when infrastructure is absent; it never skips.
        fixtures.PostgreSQLTests.setUpClass()
        cls.fixture = fixtures.PostgreSQLTests()

    @classmethod
    def tearDownClass(cls):
        fixtures.PostgreSQLTests.tearDownClass()

    @contextmanager
    def legacy_role(self):
        role = 'migration_legacy_' + uuid.uuid4().hex
        with self.fixture.admin.connect() as connection:
            connection.execute(sa.text('CREATE ROLE ' + role + ' NOLOGIN'))
            oid = connection.scalar(sa.text('SELECT oid FROM pg_roles WHERE rolname=:name'), {'name': role})
        try:
            yield role
        finally:
            with self.fixture.admin.connect() as connection:
                self.assertEqual(connection.scalar(sa.text('SELECT oid FROM pg_roles WHERE rolname=:name'), {'name': role}), oid)
                connection.execute(sa.text('DROP ROLE ' + role))

    def cli(self, engine, *args):
        env = {**os.environ, 'MATHSTART_DATABASE_URL': engine.url.render_as_string(hide_password=False),
               'MATHSTART_DB_BACKEND': 'postgresql', 'MATHSTART_SCHEMA_SIGNING_KEY': 'synthetic-schema-key-' * 3}
        return subprocess.run([sys.executable, '-m', 'backend.release_migrate', *args], env=env,
                              capture_output=True, timeout=60)

    def test_actual_fresh_cli_review_apply_check_and_refuse_replay(self):
        with self.fixture.database() as engine, tempfile.TemporaryDirectory(dir='var') as temp:
            planfile = Path(temp) / 'schema-plan.json'
            result = self.cli(engine, 'preview', '--profile', 'FRESH', '--plan-file', str(planfile))
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            plan = json.loads(planfile.read_text(encoding='utf-8'))
            with engine.connect() as connection:
                self.assertEqual(sa.inspect(connection).get_table_names(), [])
            engine.dispose()  # Real operator CLI requires every other client drained.
            args = ('apply', '--plan-file', str(planfile), '--maintenance',
                    '--reviewed-plan-sha256', release.plan_digest(plan))
            result = self.cli(engine, *args)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertEqual(json.loads(result.stdout)['status'], 'APPLIED')
            self.assertEqual(self.cli(engine, 'check').returncode, 0)
            with engine.connect() as connection:
                self.assertGreater(connection.scalar(sa.select(sa.func.count()).select_from(metadata.tables['auth_permission'])), 0)
                before = fixtures.data_digest(connection)
            self.assertNotEqual(self.cli(engine, *args).returncode, 0)
            with engine.connect() as connection:
                self.assertEqual(before, fixtures.data_digest(connection))

    def test_reviewed_populated_a_b_c_keep_data_history_epoch_sequences(self):
        key = 'synthetic-schema-key-' * 3
        for profile in ('A', 'B', 'C'):
            with self.subTest(profile=profile), self.fixture.database(profile) as engine, self.legacy_role() as role:
                instant = self.fixture.seed(engine, profile)
                with engine.connect() as connection:
                    before = fixtures.data_digest(connection, omit_grade_time=profile == 'A')
                    history = list(connection.execute(sa.text('SELECT * FROM django_migrations ORDER BY id')))
                    state = inventory(connection)
                plan = release.preview(engine, key, profile, role)
                with engine.connect() as connection:
                    self.assertEqual(state, inventory(connection))  # Read-only preview, including sequence positions.
                result = release.apply(engine, key, plan, release.plan_digest(plan), maintenance=True)
                self.assertEqual(result['status'], 'APPLIED')
                with engine.connect() as connection:
                    assert_baseline(connection, 'B', allow_protocol=True, require_history=False)
                    after = fixtures.data_digest(connection, omit_grade_time=profile == 'A')
                    for table, digest in before.items():
                        if table != 'users_studentprofile' or profile == 'C':
                            self.assertEqual(digest, after[table], table)
                    self.assertEqual(history, list(connection.execute(sa.text('SELECT * FROM django_migrations ORDER BY id'))))
                    self.assertEqual(connection.scalar(sa.text('SELECT created_at FROM content_grade WHERE id=701')),
                                     GRADE_EPOCH if profile == 'A' else instant)
                    maximum = connection.scalar(sa.text('SELECT max(id) FROM auth_user'))
                    self.assertGreater(connection.scalar(sa.text("SELECT nextval('auth_user_id_seq')")), maximum)

    def test_signature_review_database_code_and_expiry_refuse_before_ddl(self):
        key = 'synthetic-schema-key-' * 3
        with self.fixture.database() as engine, self.fixture.database() as other:
            plan = release.preview(engine, key, 'FRESH')
            for bad, signing, digest, maintenance, target in [
                (plan, key, '0' * 64, True, engine), (plan, key, release.plan_digest(plan), False, engine),
                (plan, 'different-schema-key-' * 3, release.plan_digest(plan), True, engine),
                (plan, key, release.plan_digest(plan), True, other),
                ({**plan, 'profile': 'A'}, key, release.plan_digest({**plan, 'profile': 'A'}), True, engine),
            ]:
                with self.assertRaises(SchemaMismatch):
                    release.apply(target, signing, bad, digest, maintenance=maintenance)
            expired = {k: v for k, v in plan.items() if k != 'signature'}
            expired['expires_at'] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
            expired['signature'] = release.signed(key, 'schema.plan.v1', dict(expired))
            with self.assertRaises(SchemaMismatch):
                release.apply(engine, key, expired, release.plan_digest(expired), maintenance=True)
            with patch.object(release, 'code_digest', return_value='changed-code'):
                with self.assertRaises(SchemaMismatch):
                    release.apply(engine, key, plan, release.plan_digest(plan), maintenance=True)
            with engine.connect() as connection:
                self.assertEqual(sa.inspect(connection).get_table_names(), [])

    def test_other_connected_client_blocks_maintenance(self):
        key = 'synthetic-schema-key-' * 3
        with self.fixture.database() as engine:
            plan = release.preview(engine, key, 'FRESH')
            with engine.connect() as other:
                other.execute(sa.text('SELECT 1'))
                with self.assertRaises(SchemaMismatch):
                    release.apply(engine, key, plan, release.plan_digest(plan), maintenance=True)
                self.assertEqual(sa.inspect(other).get_table_names(), [])

    def test_data_sequence_schema_and_writer_drift_refuse_without_stamp(self):
        key = 'synthetic-schema-key-' * 3
        for defect in ('data', 'sequence', 'schema', 'writer'):
            with self.subTest(defect=defect), self.fixture.database('B') as engine, self.legacy_role() as role:
                self.fixture.seed(engine, 'B')
                plan = release.preview(engine, key, 'B', role)
                with engine.begin() as connection:
                    statement = {'data': "UPDATE auth_user SET password='!changed' WHERE id=901",
                                 'sequence': "SELECT nextval('auth_user_id_seq')",
                                 'schema': 'ALTER TABLE content_grade ADD COLUMN unreviewed text',
                                 'writer': 'ALTER ROLE ' + role + ' LOGIN'}[defect]
                    connection.execute(sa.text(statement))
                with self.assertRaises((SchemaMismatch, APIError)):
                    release.apply(engine, key, plan, release.plan_digest(plan), maintenance=True)
                with engine.connect() as connection:
                    self.assertNotIn('target_session', sa.inspect(connection).get_table_names())
                    if 'alembic_version' in sa.inspect(connection).get_table_names():
                        self.assertEqual(list(connection.scalars(sa.text('SELECT version_num FROM alembic_version'))), [])

    def test_failure_rolls_back_ddl_rows_and_historical_tracking(self):
        key = 'synthetic-schema-key-' * 3
        with self.fixture.database('A') as engine, self.legacy_role() as role:
            self.fixture.seed(engine, 'A')
            plan = release.preview(engine, key, 'A', role)
            with engine.connect() as connection:
                schema, data = inventory(connection), fixtures.data_digest(connection, omit_grade_time=True)
            real = release._upgrade_profile
            def fail(connection, profile):
                return real(connection, profile, failure_at='protocol')
            with patch.object(release, '_upgrade_profile', side_effect=fail), self.assertRaises(RuntimeError):
                release.apply(engine, key, plan, release.plan_digest(plan), maintenance=True)
            with engine.connect() as connection:
                self.assertEqual(schema, inventory(connection))
                self.assertEqual(data, fixtures.data_digest(connection, omit_grade_time=True))
