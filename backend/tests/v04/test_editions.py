"""Real PG content fingerprint/update guards; no user or source files changed."""
from copy import deepcopy
from hashlib import sha256
import os
import unittest
import uuid

import sqlalchemy as sa

from backend.content.build import encoded
from backend.content.editions import snapshot, fingerprint, apply_updates, project_updates
from backend.content.publication import PublicationConflict
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import require_disposable
from backend.models.baseline import Grade


class PostgreSQLEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sa.create_engine(os.environ['MATHSTART_V04_DATABASE_URL'], hide_parameters=True)
        with cls.engine.begin() as connection:
            require_disposable(connection)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        with UnitOfWork(self.engine) as uow:
            grade = Grade(title='Original edition', slug='edition-' + uuid.uuid4().hex, order=99)
            uow.session.add(grade); uow.session.flush()
            self.id = grade.id
            uow.commit()

    def tearDown(self):
        with self.engine.begin() as connection:
            connection.execute(sa.delete(Grade).where(Grade.id == self.id))

    def fixture(self, session):
        before = snapshot(session)
        row = next(r for r in before['content_grade'] if r['id'] == self.id)
        after = deepcopy(before)
        next(r for r in after['content_grade'] if r['id'] == self.id)['title'] = 'Prepared edition'
        change = {'table': 'content_grade', 'before': row, 'after': {**row, 'title': 'Prepared edition'}}
        return before, after, change

    def test_full_snapshot_update_preserves_identity_timestamps_and_rolls_back_by_default(self):
        with UnitOfWork(self.engine) as uow:
            before, after, change = self.fixture(uow.session)
            expected = sha256(encoded(after)).hexdigest()
            apply_updates(uow.session, [change], sha256(encoded(before)).hexdigest(), expected)
            self.assertEqual(fingerprint(uow.session), expected)
            result = next(r for r in snapshot(uow.session)['content_grade'] if r['id'] == self.id)
            self.assertEqual({k: v for k, v in result.items() if k != 'title'}, {k: v for k, v in change['before'].items() if k != 'title'})
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(Grade.title).where(Grade.id == self.id)), 'Original edition')

    def test_stale_full_database_fingerprint_refuses_without_overwrite(self):
        with UnitOfWork(self.engine) as uow:
            before, after, change = self.fixture(uow.session)
            with self.engine.begin() as c:
                c.execute(sa.update(Grade).where(Grade.id == self.id).values(title='Concurrent edit'))
            with self.assertRaises(PublicationConflict) as error:
                apply_updates(uow.session, [change], sha256(encoded(before)).hexdigest(), sha256(encoded(after)).hexdigest())
            self.assertEqual(error.exception.code, 'SOURCE_CONFLICT')
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(Grade.title).where(Grade.id == self.id)), 'Concurrent edit')

    def test_auth_table_unknown_columns_primary_key_and_boolean_coercion_refused(self):
        with UnitOfWork(self.engine) as uow:
            before, after, change = self.fixture(uow.session)
            bad = [
                {**change, 'table': 'auth_user'},
                {**change, 'after': {**change['after'], 'unknown': 'field'}},
                {**change, 'after': {**change['after'], 'id': self.id + 1}},
                {**change, 'after': {**change['after'], 'order': True}},
                {**change, 'after': {**change['after'], 'created_at': '2026-10-17T00:00:00'}},
            ]
            for value in bad:
                with self.subTest(kind=list(value)), self.assertRaises(PublicationConflict) as error:
                    apply_updates(uow.session, [value], sha256(encoded(before)).hexdigest(), sha256(encoded(after)).hexdigest())
                self.assertEqual(error.exception.code, 'INVALID_EDITION')
            self.assertEqual(snapshot(uow.session), before)

    def test_duplicate_patch_and_changed_before_row_are_rejected(self):
        with UnitOfWork(self.engine) as uow:
            before, after, change = self.fixture(uow.session)
            for changes in [[change, change], [{**change, 'before': {**change['before'], 'title': 'Unproven revision'}}]]:
                with self.assertRaises(PublicationConflict):
                    apply_updates(uow.session, changes, sha256(encoded(before)).hexdigest(), sha256(encoded(after)).hexdigest())
                self.assertEqual(snapshot(uow.session), before)

    def test_wrong_next_digest_rolls_back_even_after_domain_sql_was_flushed(self):
        with UnitOfWork(self.engine) as uow:
            before, _, change = self.fixture(uow.session)
            with self.assertRaises(PublicationConflict) as error:
                apply_updates(uow.session, [change], sha256(encoded(before)).hexdigest(), '0' * 64)
            self.assertEqual(error.exception.code, 'EDITION_CONFLICT')
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(sa.select(Grade.title).where(Grade.id == self.id)), 'Original edition')

    def test_database_session_timezone_does_not_change_edition_identity(self):
        with UnitOfWork(self.engine) as uow:
            expected = fingerprint(uow.session)
            original = snapshot(uow.session)
            uow.session.execute(sa.text("SET LOCAL TIME ZONE 'Europe/Moscow'"))
            self.assertEqual(fingerprint(uow.session), expected)
            self.assertEqual(snapshot(uow.session), original)

    def test_pure_projection_isolated_and_empty_patch_does_not_allocate_or_write(self):
        with UnitOfWork(self.engine) as uow:
            before, after, change = self.fixture(uow.session)
            projected = project_updates(before, [change])
            self.assertEqual(projected, after)
            self.assertNotEqual(before, projected)
            self.assertEqual(snapshot(uow.session), before)
            projected['content_grade'][0]['title'] = 'Caller mutation'
            self.assertEqual(snapshot(uow.session), before)
            apply_updates(uow.session, [], sha256(encoded(before)).hexdigest(), sha256(encoded(before)).hexdigest())
            self.assertEqual(snapshot(uow.session), before)
            with self.assertRaises(PublicationConflict):
                project_updates(before, [change, change])

    def test_prepared_insert_consumes_no_sequence_until_apply_and_never_rewinds(self):
        inserted_id = None
        try:
            with UnitOfWork(self.engine) as uow:
                before = snapshot(uow.session)
                inserted_id = max(row['id'] for row in before['content_grade']) + 10
                template = next(row for row in before['content_grade'] if row['id'] == self.id)
                new = {**template, 'id': inserted_id, 'slug': 'insert-' + uuid.uuid4().hex, 'title': 'Prepared insertion'}
                change = {'table': 'content_grade', 'before': None, 'after': new}
                uow.session.execute(sa.text("SELECT setval('content_grade_id_seq', :ahead, true)"), {'ahead': inserted_id + 1000})
                sequence = uow.session.scalar(sa.text("SELECT pg_sequence_last_value('content_grade_id_seq')"))
                after = project_updates(before, [change])
                self.assertEqual(uow.session.scalar(sa.text("SELECT pg_sequence_last_value('content_grade_id_seq')")), sequence)
                self.assertEqual(snapshot(uow.session), before)
                apply_updates(uow.session, [change], sha256(encoded(before)).hexdigest(), sha256(encoded(after)).hexdigest())
                self.assertEqual(snapshot(uow.session), after)
                self.assertGreaterEqual(uow.session.scalar(sa.text("SELECT pg_sequence_last_value('content_grade_id_seq')")), sequence)
                uow.commit()
            with UnitOfWork(self.engine) as uow:
                ordinary = Grade(title='Later ordinary insertion', slug='ordinary-' + uuid.uuid4().hex, order=99)
                uow.session.add(ordinary); uow.session.flush()
                self.assertGreater(ordinary.id, inserted_id)
        finally:
            if inserted_id is not None:
                with self.engine.begin() as c:
                    c.execute(sa.delete(Grade).where(Grade.id == inserted_id))

    def test_insert_collision_and_duplicate_are_refused_before_domain_sql(self):
        with UnitOfWork(self.engine) as uow:
            before = snapshot(uow.session)
            existing = next(row for row in before['content_grade'] if row['id'] == self.id)
            collided = {'table': 'content_grade', 'before': None, 'after': existing}
            new = {**existing, 'id': max(row['id'] for row in before['content_grade']) + 1,
                   'slug': 'duplicate-' + uuid.uuid4().hex}
            inserted = {**collided, 'after': new}
            for changes in ([collided], [inserted, inserted]):
                with self.assertRaises(PublicationConflict):
                    apply_updates(uow.session, changes, sha256(encoded(before)).hexdigest(), '0' * 64)
                self.assertEqual(snapshot(uow.session), before)

    def test_insert_wrong_digest_rolls_back_without_advancing_sequence(self):
        with self.engine.connect() as c:
            original_sequence = c.scalar(sa.text("SELECT pg_sequence_last_value('content_grade_id_seq')"))
        with UnitOfWork(self.engine) as uow:
            before = snapshot(uow.session)
            existing = next(row for row in before['content_grade'] if row['id'] == self.id)
            new = {**existing, 'id': max(row['id'] for row in before['content_grade']) + 1,
                   'slug': 'rollback-' + uuid.uuid4().hex}
            with self.assertRaises(PublicationConflict):
                apply_updates(uow.session, [{'table': 'content_grade', 'before': None, 'after': new}],
                              sha256(encoded(before)).hexdigest(), '0' * 64)
        with self.engine.connect() as c:
            self.assertIsNone(c.scalar(sa.select(Grade.id).where(Grade.slug == new['slug'])))
            self.assertEqual(c.scalar(sa.text("SELECT pg_sequence_last_value('content_grade_id_seq')")), original_sequence)


if __name__ == '__main__':
    unittest.main()
