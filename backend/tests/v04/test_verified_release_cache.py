"""Byte tampering and edition isolation for the I02 serving optimization."""
from dataclasses import replace
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
import unittest
import uuid

from backend.content.verified_release_cache import VerifiedReleaseStore
from backend.infrastructure.http.transport import APIError
from backend.tests.v02.fixtures import release_files


class VerifiedReleaseCacheTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        _, self.descriptor, _, _ = release_files(self.directory.name)
        self.root = Path(self.directory.name) / self.descriptor.release_id
        self.store = VerifiedReleaseStore(self.directory.name)

    def test_index_page_asset_tamper_and_missing_fail_closed_even_same_mtime_size(self):
        self.store.load(self.descriptor)
        for relative in ['index.json', 'pages/302.json', 'assets/theme.css']:
            with self.subTest(relative=relative):
                path = self.root / relative
                original, stat = path.read_bytes(), path.stat()
                changed = bytearray(original)
                changed[-1] ^= 1
                try:
                    path.write_bytes(changed)
                    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
                    with self.assertRaises(APIError) as error:
                        self.store.load(self.descriptor)
                    self.assertEqual(error.exception.status, 503)
                    path.unlink()
                    with self.assertRaises(APIError):
                        self.store.load(self.descriptor)
                finally:
                    path.write_bytes(original)
                self.assertEqual(self.store.load(self.descriptor).descriptor, self.descriptor)

    def test_cached_objects_never_escape_as_shared_mutable_state(self):
        first = self.store.load(self.descriptor)
        first.pages[302]['title'] = 'Untrusted caller edit'
        first.index['catalogue']['topics'].clear()
        first.assets.clear()
        again = self.store.load(self.descriptor)
        self.assertEqual(again.pages[302]['title'], 'Сумма Straße')
        self.assertEqual(len(again.index['catalogue']['topics']), 1)
        self.assertEqual(len(again.assets), 1)

    def test_descriptor_changes_revalidate_and_entries_are_bounded(self):
        self.store.load(self.descriptor)
        for fence in [True, 1.0, 0, -1]:
            with self.assertRaises(APIError):
                self.store.load(replace(self.descriptor, fence_generation=fence))
        bad = replace(self.descriptor, manifest_digest='f' * 64)
        with self.assertRaises(APIError):
            self.store.load(bad)
        raw = json.loads((self.root / 'index.json').read_bytes())
        raw['redirects'][0]['old_path'] = '/different-old.html'
        encoded = json.dumps(raw, ensure_ascii=False).encode()
        (self.root / 'index.json').write_bytes(encoded)
        new = replace(self.descriptor, manifest_digest=sha256(encoded).hexdigest())
        self.assertEqual(self.store.load(new).index['redirects'][0]['old_path'], '/different-old.html')
        with self.assertRaises(APIError):
            self.store.load(self.descriptor)
        for fence in range(2, 5):
            edition = replace(new, operation_id=uuid.uuid4(), fence_generation=fence)
            self.assertEqual(self.store.load(edition).descriptor, edition)
            self.assertLessEqual(len(self.store._editions), 2)


if __name__ == '__main__':
    unittest.main()
