"""Full real built artifact boundary, including deliberately repinned negatives."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest

from backend.content.artifacts import verify_public_artifacts
from backend.content.sources import SourceError


class PublicArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release_root = Path(os.environ['MATHSTART_RELEASE_ROOT'])
        cls.root = Path(os.environ['MATHSTART_PUBLIC_ARTIFACT_ROOT'])
        cls.pins = json.loads(os.environ['MATHSTART_PUBLIC_ARTIFACT_DIGESTS'])
        cls.path = cls.root / 'output-manifest.json'
        cls.raw = cls.path.read_bytes()
        cls.manifest = json.loads(cls.raw)
        cls.release_id = cls.manifest['release_id']
        cls.digest = cls.pins[cls.release_id]
        if sha256(cls.raw).hexdigest() != cls.digest:
            raise RuntimeError('Real artifact fixture pin mismatch')
        cls.receipt = cls.manifest['input_receipt_digest']
        cls.origin = cls.manifest['origin']

    def verify(self, pin=None):
        return verify_public_artifacts(self.release_root, self.release_id, self.receipt,
                                       self.root, pin or self.digest, self.origin)

    def test_complete_real_built_release_preserves_all_authored_pages_and_assets(self):
        release, root, manifest = self.verify()
        self.assertEqual(len(release.pages), 279)
        self.assertEqual(len(release.index['catalogue']['topics']), 263)
        self.assertEqual(root, self.root.resolve())
        self.assertEqual(manifest['private_exports'], [])

    def test_unlisted_private_output_is_refused(self):
        path = self.root / 'private-export-negative.json'
        self.assertFalse(path.exists())
        try:
            path.write_bytes(b'{"private_export":"SYNTHETIC_CANARY"}')
            with self.assertRaisesRegex(SourceError, 'Unlisted'):
                self.verify()
        finally:
            path.unlink()

    def test_changed_public_file_is_refused_with_unchanged_manifest_pin(self):
        item = next(row for row in self.manifest['files'] if row['url'] == '/')
        path = self.root / item['path']; raw = path.read_bytes()
        try:
            path.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
            with self.assertRaisesRegex(SourceError, 'integrity'):
                self.verify()
        finally:
            path.write_bytes(raw)

    def test_repinned_incomplete_duplicate_or_private_manifest_does_not_gain_trust(self):
        missing_alias = deepcopy(self.manifest)
        missing_alias['public_urls'].remove('/glavnaya/')
        duplicate = deepcopy(self.manifest)
        duplicate['files'].append(deepcopy(duplicate['files'][0]))
        private = {**deepcopy(self.manifest), 'private_exports': ['private.json']}
        wrong_semantic = deepcopy(self.manifest)
        wrong_semantic['page_semantic_digests']['/'] = '0' * 64
        for value in [missing_alias, duplicate, private, wrong_semantic]:
            with self.subTest(keys=list(value)), self.assertRaises(SourceError):
                try:
                    raw = json.dumps(value, ensure_ascii=False).encode('utf-8')
                    self.path.write_bytes(raw)
                    self.verify(sha256(raw).hexdigest())
                finally:
                    self.path.write_bytes(self.raw)

    def test_repinned_asset_cannot_disagree_with_reviewed_input(self):
        manifest = deepcopy(self.manifest)
        item = next(row for row in manifest['files'] if row['url'] and row['url'].startswith('/static/'))
        path = self.root / item['path']; original = path.read_bytes()
        try:
            altered = original + b'\n/* repinned output disagreement */'
            path.write_bytes(altered)
            item.update(size=len(altered), sha256=sha256(altered).hexdigest())
            raw = json.dumps(manifest, ensure_ascii=False).encode('utf-8')
            self.path.write_bytes(raw)
            with self.assertRaisesRegex(SourceError, 'asset mismatch'):
                self.verify(sha256(raw).hexdigest())
        finally:
            path.write_bytes(original)
            self.path.write_bytes(self.raw)


if __name__ == '__main__':
    unittest.main()
