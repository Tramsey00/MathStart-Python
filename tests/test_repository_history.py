"""Exact cleanup dispositions never become a wildcard preservation exemption."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.repository_history import MANIFEST, SOURCE, TASK_MANIFEST, TASK_SOURCE, repository_changes, retired_document, verify_document_translations, task_changes


class RepositoryHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.before = b'original documentation\n'
        self.after = b'current documentation\n'
        self.target = self.root / 'guide.md'
        self.target.write_bytes(self.after)
        self.row = dict(path='guide.md', action='updated', reason='explicit user scope',
                        before_bytes=len(self.before), before_sha256=hashlib.sha256(self.before).hexdigest(),
                        after_sha256=hashlib.sha256(self.after).hexdigest())
        self.manifest = self.root / MANIFEST
        self.manifest.parent.mkdir(parents=True)
        originals = {'guide.md': (len(self.before), hashlib.sha256(self.before).hexdigest())}
        self.originals = patch('scripts.repository_history._original_metadata', return_value=originals)
        self.originals.start()
        self.addCleanup(self.originals.stop)
        self.save()

    def save(self, rows=None, source=SOURCE):
        self.manifest.write_text(json.dumps(dict(source_commit=source, authority='user task',
                                                files=rows if rows is not None else [self.row])), encoding='utf-8')

    def test_exact_updated_file_and_original_digest_are_required(self):
        self.assertIn('guide.md', repository_changes(self.root))
        self.target.write_bytes(b'unknown edit')
        with self.assertRaisesRegex(ValueError, 'Unreviewed repository'):
            repository_changes(self.root)
        self.target.write_bytes(self.after)
        self.row['before_sha256'] = '0' * 64
        self.save()
        with self.assertRaisesRegex(ValueError, 'original bytes'):
            repository_changes(self.root)

    def test_removed_file_must_be_absent_and_unknown_path_has_no_fallback(self):
        self.row['action'] = 'removed'
        self.save()
        with self.assertRaisesRegex(ValueError, 'reintroduced'):
            repository_changes(self.root)
        self.target.unlink()
        self.assertIn('guide.md', repository_changes(self.root))
        with self.assertRaisesRegex(ValueError, 'Not an explicitly retired'):
            retired_document('other.md', self.root)
        with patch('scripts.repository_history.subprocess.check_output', return_value=self.before):
            self.assertEqual(retired_document('guide.md', self.root), self.before)

    def test_floating_source_duplicate_and_escape_are_rejected(self):
        self.save(source='main')
        with self.assertRaises(ValueError):
            repository_changes(self.root)
        self.save(rows=[self.row, copy.deepcopy(self.row)])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            repository_changes(self.root)
        escaped = dict(self.row, path='../outside.md')
        self.save(rows=[escaped])
        with self.assertRaisesRegex(ValueError, 'escaped'):
            repository_changes(self.root)

    def test_translated_requirements_keep_exact_source_and_reviewed_working_text(self):
        path = self.root / 'specs/product/learning-requirements.md'
        path.parent.mkdir(parents=True)
        path.write_bytes(self.after)
        data = json.loads(self.manifest.read_text(encoding='utf-8'))
        data['requirements_translation'] = dict(
            path='specs/product/learning-requirements.md', language='ru', source_commit=SOURCE,
            source_path='docs/specifications/technical-spec-v7.2-draft.md',
            sections=[6, 7, 8, 9, 10, 11, 14, 15, 16],
            after_sha256=hashlib.sha256(self.after).hexdigest())
        self.manifest.write_text(json.dumps(data), encoding='utf-8')
        verify_document_translations(self.root)
        path.write_bytes(b'unreviewed changed requirement')
        with self.assertRaisesRegex(ValueError, 'translated requirements text'):
            verify_document_translations(self.root)
        path.write_bytes(self.after)
        data['requirements_translation']['source_commit'] = 'main'
        self.manifest.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'translation source'):
            verify_document_translations(self.root)


class TaskHistoryTests(unittest.TestCase):
    def test_followup_requires_named_source_before_after_and_no_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'guide.md'
            before, after = b'accepted preparation', b'assigned task revision'
            target.write_bytes(after)
            row = dict(path='guide.md', action='updated', reason='explicit task scope', before_bytes=len(before),
                       before_sha256=hashlib.sha256(before).hexdigest(), after_sha256=hashlib.sha256(after).hexdigest())
            manifest = root / TASK_MANIFEST
            manifest.parent.mkdir(parents=True)
            data = dict(source_commit=TASK_SOURCE, task='MS-T001', authority='user assignment', files=[row])
            def save():
                manifest.write_text(json.dumps(data), encoding='utf-8')
            save()
            with patch('scripts.repository_history._task_original', return_value=before):
                self.assertIn('guide.md', task_changes(root))
                target.write_bytes(b'unknown change')
                with self.assertRaisesRegex(ValueError, 'Unreviewed task'):
                    task_changes(root)
                target.write_bytes(after)
                row['before_sha256'] = '0' * 64; save()
                with self.assertRaisesRegex(ValueError, 'Unreviewed task'):
                    task_changes(root)
                row['before_sha256'] = hashlib.sha256(before).hexdigest()
                data['source_commit'] = 'main'; save()
                with self.assertRaisesRegex(ValueError, 'authority'):
                    task_changes(root)
                data['source_commit'] = TASK_SOURCE; row['path'] = '../outside.md'; save()
                with self.assertRaisesRegex(ValueError, 'Invalid task'):
                    task_changes(root)


if __name__ == '__main__':
    unittest.main()
