"""Read-only existing-source candidate preparation against real PostgreSQL."""
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import sqlalchemy as sa

from backend.content.build import write_build_inputs, verify_build_inputs
from backend.content.editions import snapshot, fingerprint
from backend.content.preparation import prepare_sources, source_changes
from backend.content.projection import catalogue_candidate, catalogue_from_snapshot
from backend.content.publication import PublicationConflict
from backend.content.sources import load_sources, SourceError
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import require_disposable

ROOT = Path(__file__).resolve().parents[3]


class SourcePreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sa.create_engine(os.environ['MATHSTART_V04_DATABASE_URL'], hide_parameters=True)
        with cls.engine.begin() as c:
            require_disposable(c)
        cls.sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        cls.bundles = load_sources(ROOT)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def state(self):
        with UnitOfWork(self.engine) as uow:
            return snapshot(uow.session)

    def test_full_prepared_manifest_matches_baseline_builder_without_database_writes(self):
        before = self.state()
        statements = []
        def watch(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement.lstrip().upper())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sa.event.listen(self.engine, 'before_cursor_execute', watch)
            try:
                result = prepare_sources(self.engine, ROOT, root / 'prepared', 'prepared-full', self.sha, all_lessons=True)
            finally:
                sa.event.remove(self.engine, 'before_cursor_execute', watch)
            self.assertEqual(result['changes'], [])
            self.assertTrue(statements)
            self.assertTrue(all(statement.startswith(('SELECT', 'WITH', 'SET TRANSACTION')) for statement in statements))
            prepared = verify_build_inputs(root / 'prepared', result['release_id'], result['input_receipt_digest'])
            with UnitOfWork(self.engine) as uow:
                uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
                descriptor, _ = write_build_inputs(uow, ROOT, root / 'baseline', 'prepared-full', self.sha)
            self.assertEqual(prepared.descriptor.manifest_digest, descriptor.manifest_digest)
            self.assertEqual(len(prepared.pages), 279)
            with self.assertRaises(SourceError):
                prepare_sources(self.engine, ROOT, root / 'prepared', 'prepared-full', self.sha, all_lessons=True)
        self.assertEqual(self.state(), before)

    def test_real_postgresql_collation_orders_captured_catalogue_exactly(self):
        with UnitOfWork(self.engine) as uow:
            uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
            state = snapshot(uow.session)
            self.assertEqual(catalogue_from_snapshot(uow.session, state), catalogue_candidate(uow))

    def test_changed_react_document_requires_explicit_selection_and_publication_binding(self):
        pilot = next(bundle for bundle in self.bundles if bundle.renderer_version == 'react-v1')
        document = deepcopy(pilot.lesson_document)
        document['subtitle'] += ' Синтетическая проверка публикации.'
        files = deepcopy(pilot.files)
        record = next(row for row in files if row['path'].endswith('/content.json'))
        record['sha256'] = sha256(document['subtitle'].encode()).hexdigest()
        changed = replace(pilot, lesson_document=document, files=files)
        bundles = [changed if bundle is pilot else bundle for bundle in self.bundles]
        other = next(bundle for bundle in bundles if bundle.snapshot['slug'] != pilot.snapshot['slug'])
        before = self.state()
        with tempfile.TemporaryDirectory() as temporary:
            with patch('backend.content.preparation.load_sources', return_value=bundles):
                with self.assertRaises(PublicationConflict) as error:
                    prepare_sources(self.engine, ROOT, Path(temporary) / 'unselected', 'unselected-doc', self.sha,
                                    slugs=[other.snapshot['slug']])
                self.assertEqual(error.exception.code, 'SOURCE_CONFLICT')
                # The selected document updates its publication binding explicitly.
                result = prepare_sources(self.engine, ROOT, Path(temporary) / 'selected', 'selected-doc', self.sha,
                                         slugs=[pilot.snapshot['slug']])
                self.assertEqual([row['table'] for row in result['changes']], ['content_lessonpublication'])
            with patch('backend.content.build.load_sources', return_value=bundles), UnitOfWork(self.engine) as uow:
                uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
                with self.assertRaisesRegex(SourceError, 'explicitly published'):
                    write_build_inputs(uow, ROOT, Path(temporary) / 'baseline', 'stale-document', self.sha)
        self.assertEqual(self.state(), before)

    def test_source_update_preserves_identity_and_refuses_unreviewed_runtime_edits(self):
        before = self.state()
        bundle = next(b for b in self.bundles if b.snapshot['page_type'] == 'topic')
        changed = replace(bundle, snapshot={**bundle.snapshot, 'title': bundle.snapshot['title'] + ' (synthetic update)'})
        instant = '2026-10-17T00:00:00.000000+00:00'
        changes = source_changes(before, [changed], [bundle.snapshot['slug']], instant)
        self.assertEqual({c['table'] for c in changes}, {'content_contentpage', 'content_lessonpublication'})
        page = next(c for c in changes if c['table'] == 'content_contentpage')
        for key in ('id', 'slug', 'grade_id', 'subject_id', 'section_id', 'created_at'):
            self.assertEqual(page['before'][key], page['after'][key])
        self.assertEqual(page['after']['updated_at'], instant)
        stale = deepcopy(before)
        next(r for r in stale['content_contentpage'] if r['id'] == page['before']['id'])['title'] = 'Retained runtime edit'
        with self.assertRaises(PublicationConflict) as error:
            source_changes(stale, [changed], [bundle.snapshot['slug']], instant)
        self.assertEqual(error.exception.code, 'SOURCE_CONFLICT')
        self.assertEqual(self.state(), before)

    def test_unpublish_candidate_omits_page_and_topic_but_keeps_database_row(self):
        before = self.state()
        targets = {row['new_path'] for row in before['content_redirect'] if row['is_active']}
        bundle = next(b for b in self.bundles if b.snapshot['page_type'] == 'topic' and '/' + b.snapshot['slug'] + '/' in targets)
        slug = bundle.snapshot['slug']
        pk = next(row['id'] for row in before['content_contentpage'] if row['slug'] == slug)
        with tempfile.TemporaryDirectory() as temporary:
            result = prepare_sources(self.engine, ROOT, temporary, 'prepared-unpublish', self.sha, slugs=[slug], unpublish=True)
            release = verify_build_inputs(temporary, result['release_id'], result['input_receipt_digest'])
            self.assertNotIn(pk, release.pages)
            self.assertNotIn(pk, {row['id'] for row in release.index['catalogue']['topics']})
            self.assertEqual(len(release.pages), 278)
            self.assertEqual(len(release.index['catalogue']['topics']), 262)
            self.assertNotIn('/' + slug + '/', {row['new_path'] for row in release.index['redirects']})
            retired = [change for change in result['changes'] if change['table'] == 'content_redirect']
            self.assertTrue(retired)
            self.assertTrue(all(change['before']['is_active'] and not change['after']['is_active'] for change in retired))
        self.assertEqual(self.state(), before)

    def test_dry_run_does_not_touch_files_rows_or_sequences_and_registration_is_explicit(self):
        before = self.state()
        with self.engine.connect() as c:
            sequences = list(c.execute(sa.text("SELECT sequencename,last_value FROM pg_sequences WHERE schemaname='public' ORDER BY sequencename")))
        with tempfile.TemporaryDirectory() as temporary:
            result = prepare_sources(self.engine, ROOT, temporary, 'dry-preparation', self.sha, all_lessons=True, dry_run=True)
            self.assertEqual(result['effects'], 'NONE')
            self.assertEqual(result['changes'], 0)
            self.assertEqual(list(Path(temporary).iterdir()), [])
        self.assertEqual(self.state(), before)
        with self.engine.connect() as c:
            self.assertEqual(list(c.execute(sa.text("SELECT sequencename,last_value FROM pg_sequences WHERE schemaname='public' ORDER BY sequencename"))), sequences)
        with self.assertRaises(PublicationConflict) as error:
            source_changes(before, self.bundles, ['missing-synthetic-source'], '2026-10-17T00:00:00.000000+00:00')
        self.assertEqual(error.exception.code, 'SOURCE_REGISTRATION_REQUIRED')


if __name__ == '__main__':
    unittest.main()
