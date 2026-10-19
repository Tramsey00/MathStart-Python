"""Target build input coverage plus independent legacy component golden parity."""
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from backend.tests.legacy_tools import oracle_root, oracle_environment

import sqlalchemy as sa

from backend.content.build import write_build_inputs, verify_build_inputs
from backend.content.releases import ReleaseStore
from backend.content.sources import SourceError, file_inside, load_sources, read_json
from backend.infrastructure.http.transport import APIError
from backend.infrastructure.uow import UnitOfWork
from backend.models.baseline import ContentPage, Grade

ROOT = Path(__file__).resolve().parents[3]
INPUT_SHA = '24d06112bcd6abcd1abad9b052de14a0a7b49e8e'


class SourceTests(unittest.TestCase):
    def test_complete_source_set_and_authored_assets(self):
        bundles = load_sources(ROOT)
        self.assertEqual(len(bundles), 279)
        self.assertEqual(sum(b.snapshot['page_type'] == 'topic' for b in bundles), 263)
        topics = [b for b in bundles if b.snapshot['page_type'] == 'topic']
        self.assertEqual(sum(bool(b.snapshot['page_css']) for b in topics), 97)
        self.assertEqual(sum(bool(b.snapshot['page_js']) for b in topics), 7)
        from backend.content.build import assets_for
        home = next(bundle for bundle in bundles if bundle.snapshot['page_type'] == 'home')
        exported = {asset['url']: (asset, raw) for asset, raw in assets_for(ROOT, home) if asset['kind'] == 'media'}
        reviewed = read_json(ROOT / 'site_content/media.json')['assets']
        self.assertEqual(set(exported), {'/media/' + item['file'] for item in reviewed})
        for item in reviewed:
            asset, raw = exported['/media/' + item['file']]
            self.assertEqual(asset['sha256'], item['sha256'])
            self.assertEqual(sha256(raw).hexdigest(), item['sha256'])
        from unittest.mock import patch
        from copy import deepcopy
        manifest = read_json(ROOT / 'site_content/media.json')
        for attack in ('duplicate', 'traversal', 'wrong-hash'):
            altered = deepcopy(manifest)
            if attack == 'duplicate': altered['assets'].append(altered['assets'][0])
            elif attack == 'traversal': altered['assets'][0]['file'] = '../private.env'
            else: altered['assets'][0]['sha256'] = '0' * 64
            with self.subTest(attack=attack), patch('backend.content.build.read_json', return_value=altered), self.assertRaises(SourceError):
                assets_for(ROOT, home)


    def test_legacy_template_golden_all_lessons(self):
        python = os.environ.get('MATHSTART_LEGACY_PYTHON')
        self.assertIsNotNone(python, 'Independent legacy interpreter must be supplied')
        result = subprocess.run([python, '-m', 'backend.tests.v04.golden_oracle'], cwd=oracle_root(), env=oracle_environment(),
                                capture_output=True, timeout=60, check=True)
        expected = json.loads(result.stdout)
        actual = {b.snapshot['slug']: sha256(b.snapshot['body_html'].encode()).hexdigest()
                  for b in load_sources(ROOT) if b.snapshot['page_type'] == 'topic'}
        self.assertEqual(actual, expected)

    def test_paths_duplicate_json_and_nonfinite_fail_closed(self):
        for path in ['../private', '/absolute', 'C:/private', 'a\\b', 'a//b']:
            with self.subTest(path=path), self.assertRaises(SourceError):
                file_inside(ROOT, path)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.json'
            for raw in [b'{"a":{"x":1,"x":2}}', b'{"a":NaN}', b'\xff']:
                path.write_bytes(raw)
                with self.assertRaises(SourceError):
                    read_json(path)


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sa.create_engine(os.environ['MATHSTART_V04_DATABASE_URL'], hide_parameters=True)
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        with UnitOfWork(cls.engine) as uow:
            uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
            cls.descriptor, cls.receipt = write_build_inputs(uow, ROOT, cls.root, 'test-inputs',
                                                            '24d06112bcd6abcd1abad9b052de14a0a7b49e8e')

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()
        cls.temp.cleanup()

    def test_full_manifest_inventory_and_private_exclusion(self):
        release = ReleaseStore(self.root).load(self.descriptor)
        self.assertEqual(len(release.pages), 279)
        self.assertEqual(len(release.index['catalogue']['topics']), 263)
        for item in self.receipt['files']:
            raw = (self.root / self.descriptor.release_id / item['path']).read_bytes()
            self.assertEqual((len(raw), sha256(raw).hexdigest()), (item['size'], item['sha256']))
            self.assertFalse(any(x in item['path'] for x in ['account', 'auth_user', 'session', 'receipt_bridge']))
        self.assertEqual({a[0]['url'] for a in release.assets.values()},
                         {a['url'] for p in release.pages.values() for a in p['assets']})

    def test_immutable_identity_cannot_be_overwritten(self):
        with UnitOfWork(self.engine) as uow, self.assertRaises(SourceError):
            write_build_inputs(uow, ROOT, self.root, 'test-inputs', INPUT_SHA)

    def test_trusted_receipt_rejects_metadata_edit_and_unlisted_private_export(self):
        base = self.root / self.descriptor.release_id
        receipt_digest = sha256((base / 'receipt.json').read_bytes()).hexdigest()
        self.assertEqual(len(verify_build_inputs(self.root, self.descriptor.release_id, receipt_digest).pages), 279)
        with self.assertRaises(SourceError):
            verify_build_inputs(self.root, self.descriptor.release_id, '0' * 64)
        path = base / 'pages/1.json'
        raw = path.read_bytes()
        try:
            page = json.loads(raw)
            page['title'] = 'Changed metadata'
            path.write_text(json.dumps(page), encoding='utf-8')
            with self.assertRaises(SourceError):
                verify_build_inputs(self.root, self.descriptor.release_id, receipt_digest)
        finally:
            path.write_bytes(raw)
        path = base / 'private.json'
        try:
            path.write_bytes(b'{"session":"PRIVATE-EXPORT-SENTINEL"}')
            with self.assertRaises(SourceError):
                verify_build_inputs(self.root, self.descriptor.release_id, receipt_digest)
        finally:
            path.unlink()

    def test_unreviewed_database_edit_refused_without_overwrite(self):
        with UnitOfWork(self.engine) as uow:
            uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ'))
            page = uow.session.scalar(sa.select(ContentPage).where(ContentPage.slug == 'glavnaya'))
            before = page.body_html
            page.body_html = 'PRIVATE-UNREVIEWED-SENTINEL'
            uow.session.flush()
            with self.assertRaises(SourceError):
                write_build_inputs(uow, ROOT, self.root, 'unreviewed', INPUT_SHA)
            self.assertEqual(page.body_html, 'PRIVATE-UNREVIEWED-SENTINEL')
            self.assertFalse((self.root / 'unreviewed').exists())
        with UnitOfWork(self.engine) as uow:
            self.assertEqual(uow.session.scalar(sa.select(ContentPage.body_html).where(ContentPage.slug == 'glavnaya')), before)

    def test_hbuild_01_coherent_alternate_catalogue_identity_refused(self):
        with UnitOfWork(self.engine) as uow:
            uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ'))
            page = uow.session.scalar(sa.select(ContentPage).where(ContentPage.slug == '10-klass-naturalnye-chisla-povtorenie'))
            page.grade_id, page.subject_id, page.section_id = 1, 1, 1
            uow.session.flush()
            with self.assertRaises(SourceError):
                write_build_inputs(uow, ROOT, self.root, 'relation-conflict', INPUT_SHA)
            self.assertFalse((self.root / 'relation-conflict').exists())

    def test_hbuild_01_same_slug_cross_grade_subject_refused(self):
        with UnitOfWork(self.engine) as uow:
            uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ'))
            page = uow.session.scalar(sa.select(ContentPage).where(ContentPage.slug == '10-klass-naturalnye-chisla-povtorenie'))
            page.subject_id = 3  # algebra exists in both grades; slug alone is insufficient.
            uow.session.flush()
            self.assertEqual(page.subject.slug, 'algebra')
            self.assertNotEqual(page.subject.grade_id, page.grade_id)
            with self.assertRaises(SourceError):
                write_build_inputs(uow, ROOT, self.root, 'cross-grade-conflict', INPUT_SHA)
            self.assertFalse((self.root / 'cross-grade-conflict').exists())

    def test_hbuild_02_read_committed_refused_and_snapshot_pinned(self):
        with UnitOfWork(self.engine) as uow, self.assertRaises(SourceError):
            write_build_inputs(uow, ROOT, self.root, 'mixed-snapshot', INPUT_SHA)
        with UnitOfWork(self.engine) as uow:
            uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
            grade = uow.session.scalar(sa.select(Grade).where(Grade.id == 1))
            original = grade.title
            try:
                with self.engine.begin() as connection:
                    connection.execute(sa.update(Grade).where(Grade.id == 1).values(title='Concurrent edition'))
                descriptor, receipt = write_build_inputs(uow, ROOT, self.root, 'pinned-snapshot', INPUT_SHA)
                release = ReleaseStore(self.root).load(descriptor)
                self.assertEqual(next(g['title'] for g in release.index['catalogue']['grades'] if g['id'] == 1), original)
            finally:
                with self.engine.begin() as connection:
                    connection.execute(sa.update(Grade).where(Grade.id == 1).values(title=original))

    def test_missing_or_corrupt_assets_and_pages_rejected(self):
        release = ReleaseStore(self.root).load(self.descriptor)
        paths = [next(iter(release.assets.values()))[0]['storage_key'], f'pages/{next(iter(release.pages))}.json']
        for relative in paths:
            path = self.root / self.descriptor.release_id / relative
            raw = path.read_bytes()
            try:
                path.unlink()
                with self.assertRaises(APIError):
                    ReleaseStore(self.root).load(self.descriptor)
                path.write_bytes(b'{"private":"SENTINEL"}')
                with self.assertRaises(APIError):
                    ReleaseStore(self.root).load(self.descriptor)
            finally:
                path.write_bytes(raw)


if __name__ == '__main__':
    unittest.main()
