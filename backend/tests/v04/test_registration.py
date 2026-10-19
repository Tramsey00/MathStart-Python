"""Actual new-ID source publication in an owned miniature PG/React runtime."""
from hashlib import sha256
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time
import unittest
import uuid

import httpx
import sqlalchemy as sa
import uvicorn

from backend.content.artifact_pins import PublicationArtifactPins
from backend.content.editions import decoded, snapshot, fingerprint, apply_updates
from backend.content.participant import PreparedPublication, digest
from backend.content.preparation import prepare_sources
from backend.content.publication import PublisherAuthority, PublicationConflict
from backend.content.public_runtime import create_public_app
from backend.content.publish import finish
from backend.content.sources import load_sources
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import fresh, require_disposable, advance_sequences
from backend.models.baseline import ContentPage, Grade, LessonPublication, metadata
from backend.verification_suite import owned_database
from frontend.build_public import build_public

ROOT = Path(__file__).resolve().parents[3]


class RegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = sa.create_engine(os.environ['MATHSTART_V04_DATABASE_URL'], hide_parameters=True)
        with cls.parent.connect() as c:
            require_disposable(c)
        cls.admin = sa.create_engine(cls.parent.url.set(database='postgres'), isolation_level='AUTOCOMMIT', hide_parameters=True)
        with UnitOfWork(cls.parent) as uow:
            cls.original = snapshot(uow.session)
        cls.home = next(row for row in cls.original['content_contentpage'] if row['page_type'] == 'home')
        cls.bundle = min((b for b in load_sources(ROOT) if b.snapshot['page_type'] == 'topic'),
                         key=lambda bundle: len(bundle.snapshot['body_html']))
        cls.sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()

    @classmethod
    def tearDownClass(cls):
        cls.admin.dispose(); cls.parent.dispose()

    def setUp(self):
        self.owned = owned_database(self.admin, self.parent.url, 'registration')
        self.engine = self.owned.__enter__()
        self.addCleanup(self.owned.__exit__, None, None, None)
        self.temp = tempfile.TemporaryDirectory(prefix='registration-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        with self.engine.begin() as c:
            fresh(c)
            for name in ('content_grade', 'content_subject', 'content_section', 'content_contentpage'):
                table = metadata.tables[name]
                rows = [self.home] if name == 'content_contentpage' else self.original[name]
                c.execute(sa.insert(table), [decoded(table, row) for row in rows])
            advance_sequences(c)

    def state(self):
        with UnitOfWork(self.engine) as uow:
            return snapshot(uow.session)

    def sequences(self):
        with self.engine.connect() as c:
            return list(c.execute(sa.text('SELECT sequencename,last_value FROM pg_sequences '
                                         'WHERE schemaname=current_schema() ORDER BY sequencename')))

    def prepare(self, *, dry_run=False):
        return prepare_sources(self.engine, ROOT, self.root / 'inputs', 'registered-' + uuid.uuid4().hex,
            self.sha, slugs=[self.bundle.snapshot['slug']], dry_run=dry_run)

    def test_new_page_preparation_and_dry_run_do_not_create_rows_or_advance_sequences(self):
        before, sequences = self.state(), self.sequences()
        preview = self.prepare(dry_run=True)
        self.assertEqual(preview['effects'], 'NONE')
        self.assertEqual(preview['changes'], 2)
        self.assertFalse((self.root / 'inputs').exists())
        prepared = self.prepare()
        self.assertEqual({change['table'] for change in prepared['changes']},
                         {'content_contentpage', 'content_lessonpublication'})
        self.assertTrue(all(change['before'] is None for change in prepared['changes']))
        self.assertEqual(self.state(), before)
        self.assertEqual(self.sequences(), sequences)

    def test_existing_unregistered_page_requires_exact_source_and_keeps_its_identity(self):
        prepared = self.prepare()
        page = next(change['after'] for change in prepared['changes'] if change['table'] == 'content_contentpage')
        with self.engine.begin() as c:
            c.execute(sa.insert(metadata.tables['content_contentpage']).values(**decoded(metadata.tables['content_contentpage'], page)))
            advance_sequences(c)
        before = self.state()
        registered = self.prepare()
        self.assertEqual(len(registered['changes']), 1)
        self.assertEqual(registered['changes'][0]['table'], 'content_lessonpublication')
        self.assertEqual(registered['changes'][0]['after']['page_id'], page['id'])
        self.assertEqual(self.state(), before)
        with self.engine.begin() as c:
            c.execute(sa.update(ContentPage).where(ContentPage.id == page['id']).values(title='Retained runtime edit'))
        with self.assertRaises(PublicationConflict) as rejected:
            self.prepare()
        self.assertEqual(rejected.exception.code, 'SOURCE_CONFLICT')

    def test_new_source_uses_real_fenced_publish_http_and_later_orm_sequence(self):
        prepared = self.prepare()
        listener = socket.socket(); listener.bind(('127.0.0.1', 0))
        self.addCleanup(listener.close)
        origin = 'http://127.0.0.1:' + str(listener.getsockname()[1])
        output = self.root / 'output'
        build_public(self.root / 'inputs', prepared['release_id'], prepared['manifest_digest'], output,
                     origin, prepared['input_receipt_digest'])
        plan = {'version': 'prepared-publication-v1', 'kind': 'publish', 'previous': None, 'origin': origin,
                **{key: prepared[key] for key in ('release_id', 'manifest_digest', 'input_receipt_digest',
                                                'before_digest', 'after_digest', 'changes')},
                'output_manifest_digest': sha256((output / 'output-manifest.json').read_bytes()).hexdigest()}
        releases, artifacts = self.root / 'releases', self.root / 'artifacts'
        participant = PreparedPublication(plan, input_root=self.root / 'inputs', output_root=output,
                                         release_root=releases, artifact_root=artifacts)
        app = create_public_app(self.engine, Signer('synthetic-registration-publisher'),
            release_root=releases, artifact_root=artifacts, artifact_digests={}, origin=origin)
        server = uvicorn.Server(uvicorn.Config(app, log_level='error', proxy_headers=False))
        thread = threading.Thread(target=server.run, kwargs={'sockets': [listener]}, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started and time.monotonic() < deadline:
                time.sleep(.05)
            self.assertTrue(server.started, 'Owned registration HTTP runtime failed to start')
            authority = PublisherAuthority(self.engine, participant, lease_seconds=120)
            token, phase = authority.claim('public', 'new-source', plan, uuid.uuid4())
            self.assertEqual(finish(authority, token), 'COMPLETE')
            # Lost acknowledgement repeats the same operation without new IDs.
            state, sequences = self.state(), self.sequences()
            _, phase = authority.claim('public', 'new-source', plan, token.owner_id)
            self.assertEqual(phase, 'COMPLETE')
            self.assertEqual(self.state(), state)
            self.assertEqual(self.sequences(), sequences)
            with httpx.Client(trust_env=False) as client:
                response = client.get(origin + '/' + self.bundle.snapshot['slug'] + '/')
                self.assertEqual(response.status_code, 200)
                self.assertIn(self.bundle.snapshot['title'], response.text)
            with UnitOfWork(self.engine) as uow:
                stored = uow.session.scalar(sa.select(ContentPage).where(ContentPage.slug == self.bundle.snapshot['slug']))
                self.assertIsNotNone(uow.session.scalar(sa.select(LessonPublication.id).where(LessonPublication.page_id == stored.id)))
                self.assertEqual(next(row for row in snapshot(uow.session)['content_contentpage'] if row['id'] == self.home['id']), self.home)
                ordinary = ContentPage(title='Later row', slug='later-row', page_type='static')
                uow.session.add(ordinary); uow.session.flush()
                self.assertGreater(ordinary.id, stored.id)
        finally:
            server.should_exit = True
            thread.join(timeout=10)
            if thread.is_alive():
                raise RuntimeError('Owned registration HTTP runtime survived cleanup')


if __name__ == '__main__':
    unittest.main()
