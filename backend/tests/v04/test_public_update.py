"""Scoped installed-site update through real prepared publication and HTTP."""
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
from hashlib import sha256
import io
import json
import os
import socket
import threading
import time
import unittest
import uuid
from unittest.mock import patch

import httpx
import sqlalchemy as sa
import uvicorn

from backend.content.bootstrap_plan import bootstrap_changes
from backend.content.editions import snapshot, apply_updates
from backend.content.participant import PreparedPublication
from backend.content.preparation import prepare_sources, related, source_snapshot
from backend.content.public_update import PUBLIC_PAGES, POWER_LESSON, POWER_PDF, RETIRED_PATHS
from backend.content.publication import PublisherAuthority, PublicationConflict
from backend.content.public_runtime import create_public_app
from backend.content.publish import finish, main
from backend.content.sources import load_sources, digest
from backend.infrastructure.http.signing import Signer
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import metadata
from backend.tests.v04 import test_bootstrap_plan as fixtures
ROOT = fixtures.ROOT
from backend.users.security import Security
from backend.users.service import IdentityService
from frontend.build_public import build_public


class PublicUpdateTests(unittest.TestCase):
    setUpClass = classmethod(fixtures.BootstrapPlanTests.setUpClass.__func__)
    tearDownClass = classmethod(fixtures.BootstrapPlanTests.tearDownClass.__func__)
    setUp = fixtures.BootstrapPlanTests.setUp
    private = fixtures.BootstrapPlanTests.private
    state = fixtures.BootstrapPlanTests.state
    sequences = fixtures.BootstrapPlanTests.sequences

    def install(self):
        with UnitOfWork(self.engine) as uow:
            before = snapshot(uow.session)
            changes = bootstrap_changes(before, load_sources(ROOT), ROOT, '2020-01-01T00:00:00.000000+00:00')
            from backend.content.editions import project_updates
            apply_updates(uow.session, changes, digest(before), digest(project_updates(before, changes)))
            uow.commit()
        table = metadata.tables['content_contentpage']
        with self.engine.begin() as c:
            for slug in PUBLIC_PAGES:
                c.execute(sa.update(table).where(table.c.slug == slug).values(title='Previously installed public title'))
            c.execute(sa.update(metadata.tables['content_grade']).values(title='Preserved runtime catalogue title'))
            c.execute(sa.update(metadata.tables['content_mediaasset']).where(
                metadata.tables['content_mediaasset'].c.file == POWER_PDF).values(title='Previously installed PDF title'))
            for number, slug in enumerate(('materialy', 'pamyatki'), 50001):
                c.execute(sa.insert(table).values(id=number, slug=slug, title='Retained retired page', page_type='static',
                    order=0, body_html='Retained body', page_css='', page_js='', seo_title='', seo_description='',
                    is_published=True, created_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
                    updated_at=datetime(2021, 1, 1, tzinfo=timezone.utc)))
            c.execute(sa.update(table).where(table.c.slug == POWER_LESSON).values(title='Previously published power lesson'))
        state = self.state()
        lesson = next(row for row in state['content_contentpage'] if row['slug'] == POWER_LESSON)
        with self.engine.begin() as c:
            publication = metadata.tables['content_lessonpublication']
            c.execute(sa.update(publication).where(publication.c.page_id == lesson['id']).values(
                published_digest=digest(source_snapshot(lesson, related(state)))))

    def prepare(self, *, dry_run=False):
        return prepare_sources(self.engine, ROOT, self.root / 'inputs', 'public-update-' + uuid.uuid4().hex,
                               self.sha, public_update=True, public_backup_path=self.root / 'before.json', dry_run=dry_run)

    def test_scoped_dry_run_and_cli_have_no_file_row_sequence_or_private_effects(self):
        self.install()
        before, private, sequences = self.state(), self.private(), self.sequences()
        preview = self.prepare(dry_run=True)
        self.assertEqual(preview['selected'], 5)
        self.assertGreater(preview['changes'], 5)
        self.assertEqual(preview['effects'], 'NONE')
        env = {'MATHSTART_DATABASE_URL': self.engine.url.render_as_string(hide_password=False), 'MATHSTART_DB_BACKEND': 'postgresql'}
        with patch.dict(os.environ, env), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(['prepare-public-update', '--dry-run', '--source-sha', self.sha,
                                  '--release-id', 'scoped-cli-preview']), 0)
        self.assertEqual(json.loads(output.getvalue())['selected'], 5)
        self.assertEqual(self.state(), before)
        self.assertEqual(self.private(), private)
        self.assertEqual(self.sequences(), sequences)
        self.assertFalse((self.root / 'inputs').exists())
        self.assertFalse((self.root / 'before.json').exists())

    def test_missing_lesson_conflict_and_existing_backup_refuse_before_effects(self):
        with self.assertRaises(PublicationConflict) as missing:
            self.prepare()
        self.assertEqual(missing.exception.code, 'SOURCE_REGISTRATION_REQUIRED')
        self.assertFalse((self.root / 'before.json').exists())
        self.install()
        backup = self.root / 'before.json'
        backup.write_bytes(b'retained backup')
        with self.assertRaises(FileExistsError):
            self.prepare()
        self.assertEqual(backup.read_bytes(), b'retained backup')
        self.assertFalse((self.root / 'inputs').exists())
        backup.unlink()
        with self.engine.begin() as c:
            table = metadata.tables['content_contentpage']
            c.execute(sa.update(table).where(table.c.slug == POWER_LESSON).values(title='Unpublished conflicting runtime edit'))
        before, private, sequences = self.state(), self.private(), self.sequences()
        with self.assertRaises(PublicationConflict) as conflict:
            self.prepare()
        self.assertEqual(conflict.exception.code, 'SOURCE_CONFLICT')
        self.assertEqual(self.state(), before)
        self.assertEqual(self.private(), private)
        self.assertEqual(self.sequences(), sequences)
        self.assertFalse(backup.exists())
        self.assertFalse((self.root / 'inputs').exists())

    def test_real_scoped_publication_backup_pdf_redirects_and_unrelated_private_preservation(self):
        self.install()
        before, private = self.state(), self.private()
        env = {'MATHSTART_DATABASE_URL': self.engine.url.render_as_string(hide_password=False), 'MATHSTART_DB_BACKEND': 'postgresql'}
        with patch.dict(os.environ, env), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(['prepare-public-update', '--source-sha', self.sha, '--release-id', 'scoped-live',
                '--input-root', str(self.root / 'inputs'), '--changes', str(self.root / 'edition.json'),
                '--backup', str(self.root / 'before.json')]), 0)
        prepared = json.loads(output.getvalue())
        prepared['changes'] = json.loads((self.root / 'edition.json').read_text(encoding='utf-8'))['changes']
        backup = json.loads((self.root / 'before.json').read_text(encoding='utf-8'))
        self.assertEqual(backup['version'], 'public-records-before-update-v1')
        self.assertEqual(backup['before_digest'], digest(before))
        self.assertEqual(set(backup['records']), {'content_contentpage','content_lessonpublication','content_mediaasset','content_redirect'})
        self.assertEqual(len(backup['records']['content_contentpage']), 7)
        self.assertEqual(self.state(), before)
        listener = socket.socket(); listener.bind(('127.0.0.1', 0)); self.addCleanup(listener.close)
        origin = 'http://127.0.0.1:' + str(listener.getsockname()[1])
        output_root = self.root / 'output'
        build_public(self.root / 'inputs', prepared['release_id'], prepared['manifest_digest'], output_root,
                     origin, prepared['input_receipt_digest'])
        plan = {'version': 'prepared-publication-v1', 'kind': 'publish', 'previous': None, 'origin': origin,
                **{key: prepared[key] for key in ('release_id','manifest_digest','input_receipt_digest','before_digest','after_digest','changes')},
                'output_manifest_digest': sha256((output_root / 'output-manifest.json').read_bytes()).hexdigest()}
        releases, artifacts = self.root / 'releases', self.root / 'artifacts'
        participant = PreparedPublication(plan,input_root=self.root / 'inputs',output_root=output_root,release_root=releases,artifact_root=artifacts)
        security = Security(self.engine, self.key, origin, secure=False)
        app = create_public_app(self.engine, Signer(self.key), release_root=releases, artifact_root=artifacts,
                                artifact_digests={}, origin=origin, identity_service=IdentityService(security))
        server = uvicorn.Server(uvicorn.Config(app, log_level='error', proxy_headers=False))
        thread = threading.Thread(target=server.run, kwargs={'sockets':[listener]}, daemon=True); thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started and time.monotonic() < deadline: time.sleep(.05)
            self.assertTrue(server.started)
            authority = PublisherAuthority(self.engine, participant, lease_seconds=120)
            token, _ = authority.claim('public','scoped-update',plan,uuid.uuid4())
            self.assertEqual(finish(authority, token), 'COMPLETE')
            after = self.state()
            allowed_pages = set(PUBLIC_PAGES) | {POWER_LESSON,'materialy','pamyatki'}
            for name, rows in before.items():
                for row in rows:
                    selected = (name == 'content_contentpage' and row['slug'] in allowed_pages or
                                name == 'content_lessonpublication' and row['page_id'] in
                                {p['id'] for p in before['content_contentpage'] if p['slug'] == POWER_LESSON} or
                                name == 'content_mediaasset' and row['file'] == POWER_PDF or
                                name == 'content_redirect' and row['old_path'] in RETIRED_PATHS)
                    actual = next(item for item in after[name] if item['id'] == row['id'])
                    if not selected: self.assertEqual(actual, row)
                    elif name == 'content_contentpage' and row['slug'] in {'materialy','pamyatki'}:
                        self.assertEqual(actual,{**row,'is_published':False})
                    elif 'created_at' in row: self.assertEqual(actual['created_at'],row['created_at'])
            self.assertEqual(self.private(),private)
            sequences = self.sequences()
            self.assertEqual(self.prepare(dry_run=True)['changes'],0)
            self.assertEqual(self.state(),after); self.assertEqual(self.sequences(),sequences)
            with httpx.Client(trust_env=False) as client:
                for path in ('/','/karta-sajta/','/o-proekte/','/kontakty/','/'+POWER_LESSON+'/'):
                    self.assertEqual(client.get(origin+path).status_code,200,path)
                for path in RETIRED_PATHS:
                    response = client.get(origin+path)
                    self.assertEqual(response.status_code,301,path)
                    self.assertEqual(response.headers['location'],'/karta-sajta/' if 'materialy' in path else '/'+POWER_LESSON+'/')
                pdf = client.get(origin+'/media/'+POWER_PDF)
                self.assertEqual(pdf.status_code,200)
                self.assertEqual(sha256(pdf.content).hexdigest(),sha256((ROOT/'site_content/media'/POWER_PDF).read_bytes()).hexdigest())
                media = json.loads((ROOT/'site_content/media.json').read_text(encoding='utf-8'))['assets']
                for item in media:
                    response = client.get(origin+'/media/'+item['file'])
                    self.assertEqual(response.status_code,200,item['file'])
                    self.assertEqual(sha256(response.content).hexdigest(),item['sha256'])

            self.assertEqual(self.private(),private)
        finally:
            server.should_exit=True; thread.join(timeout=10)
            if thread.is_alive(): raise RuntimeError('Owned scoped HTTP runtime survived cleanup')


if __name__ == '__main__': unittest.main()
