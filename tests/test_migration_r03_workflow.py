"""Reject corrupt queue dependencies and unreviewed preservation changes."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.check_migration_preservation import WORKFLOW_SOURCE, workflow_changes
from scripts.check_workflow_docs import validate_queue


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.queue = {'tasks': [
            {'id': 'MS-N000', 'order': 0, 'status': 'READY_FOR_REVIEW', 'dependencies': [], 'acceptance': 'review'},
            {'id': 'MS-N001', 'order': 1, 'status': 'PLANNED', 'dependencies': ['MS-N000'], 'acceptance': 'decision', 'legacy_ids': ['MS7-V03']},
        ]}
        self.source = {'rows': [{'id': 'MS7-V03', 'workflow_disposition': 'ADAPTED',
                                 'workflow_tasks': ['MS-N001'], 'workflow_reason': 'preserve scope'}]}

    def test_valid_graph_and_bidirectional_source_mapping(self):
        self.assertEqual(len(validate_queue(self.queue, self.source)), 2)

    def test_missing_self_forward_cycle_and_retired_dependency_rejected(self):
        for dependency in ['unknown', 'MS-N001']:
            queue = copy.deepcopy(self.queue)
            queue['tasks'][1]['dependencies'] = [dependency]
            with self.assertRaises(ValueError):
                validate_queue(queue, self.source)
        queue = copy.deepcopy(self.queue)
        queue['tasks'][0]['dependencies'] = ['MS-N001']
        with self.assertRaises(ValueError):
            validate_queue(queue, self.source)
        queue = copy.deepcopy(self.queue)
        queue['tasks'][0]['status'] = 'REMOVED_FROM_PLAN'
        with self.assertRaises(ValueError):
            validate_queue(queue, self.source)

    def test_removed_harness_task_cannot_be_completed_or_required(self):
        source = copy.deepcopy(self.source)
        source['rows'][0]['id'] = 'MS7-R05'
        source['rows'][0]['workflow_disposition'] = 'COMPLETED_BASELINE'
        source['rows'][0]['workflow_tasks'] = []
        with self.assertRaises(ValueError):
            validate_queue(self.queue, source)

    def test_missing_reverse_mapping_rejected(self):
        queue = copy.deepcopy(self.queue)
        queue['tasks'][1]['legacy_ids'] = []
        with self.assertRaises(ValueError):
            validate_queue(queue, self.source)

    def test_preservation_checks_before_after_and_exact_retirement_path(self):
        before = b'original\n'
        after = b'current\n'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / 'specs/maintenance/docs-workflow-dispositions.json'
            manifest.parent.mkdir(parents=True)
            target = root / 'guide.md'
            target.write_bytes(after)
            row = {'path': 'guide.md', 'action': 'updated', 'before_bytes': len(before),
                   'before_sha256': hashlib.sha256(before).hexdigest(),
                   'after_sha256': hashlib.sha256(after).hexdigest(), 'reason': 'explicit task'}
            data = {'base_sha': WORKFLOW_SOURCE, 'authority': 'user task', 'files': [row]}
            def save():
                manifest.write_text(json.dumps(data), encoding='utf-8')
            save()
            with patch('scripts.check_migration_preservation._historical_batch',
                       return_value={(WORKFLOW_SOURCE, 'guide.md'): before}):
                self.assertIn('guide.md', workflow_changes(root))
                target.write_bytes(b'unreviewed')
                with self.assertRaises(ValueError):
                    workflow_changes(root)
                target.unlink()
                with self.assertRaises(ValueError):
                    workflow_changes(root)
                row['action'] = 'removed'
                save()
                with self.assertRaisesRegex(ValueError, 'outside explicitly retired'):
                    workflow_changes(root)
                row['before_sha256'] = '0' * 64
                save()
                with self.assertRaisesRegex(ValueError, 'original bytes'):
                    workflow_changes(root)


if __name__ == '__main__':
    unittest.main()
