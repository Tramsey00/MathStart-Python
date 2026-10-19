"""Retirement must never hide a current contract/data edit behind historical bytes."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.check_migration_preservation import SOURCE, MAINTENANCE_SOURCE, dispositions
from scripts.historical_sources import retired_bytes


class HistoricalSourceBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw = b'original historical receipt\n'
        self.row = {'path': 'old/receipt.json', 'action': 'removed',
                    'source_sha': MAINTENANCE_SOURCE, 'bytes': len(self.raw),
                    'sha256': hashlib.sha256(self.raw).hexdigest()}
        self.manifest = self.root / 'specs/migration/post-django-preservation.json'
        self.manifest.parent.mkdir(parents=True)
        self.write()

    def write(self):
        self.manifest.write_text(json.dumps({'source_sha': SOURCE,
            'accepted_input': '8d958aeeb17da46839722441425ccbb5889e2ab7', 'files': [self.row]}))

    def test_current_file_has_no_historical_fallback(self):
        path = self.root / 'current-contract.json'
        path.write_bytes(b'changed current contract')
        with patch('scripts.check_migration_preservation._historical_blob') as git:
            with self.assertRaisesRegex(ValueError, 'Not an explicitly retired'):
                retired_bytes('current-contract.json', self.root)
            git.assert_not_called()

    def test_actual_git_bytes_must_match_original_digest_and_size(self):
        for raw in [self.raw, b'altered historical receipt']:
            with patch('scripts.check_migration_preservation._historical_blob', return_value=raw) as git:
                if raw == self.raw:
                    self.assertEqual(retired_bytes(self.row['path'], self.root), self.raw)
                    git.assert_called_once_with(str(self.root), MAINTENANCE_SOURCE, self.row['path'])
                else:
                    with self.assertRaisesRegex(ValueError, 'Historical provenance'):
                        retired_bytes(self.row['path'], self.root)

    def test_reintroduced_original_refuses_before_git_read(self):
        path = self.root / self.row['path']
        path.parent.mkdir()
        path.write_bytes(self.raw)
        with patch('scripts.check_migration_preservation._historical_blob') as git:
            with self.assertRaisesRegex(ValueError, 'reintroduced'):
                retired_bytes(self.row['path'], self.root)
            git.assert_not_called()

    def test_floating_or_unknown_pin_and_duplicate_path_are_rejected(self):
        for pin in ['main', '0' * 40]:
            self.row['source_sha'] = pin
            self.write()
            with self.assertRaisesRegex(ValueError, 'Unreviewed historical source'):
                dispositions(self.root)
        self.row['source_sha'] = MAINTENANCE_SOURCE
        self.write()
        data = json.loads(self.manifest.read_text())
        data['files'].append(self.row)
        self.manifest.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            dispositions(self.root)
