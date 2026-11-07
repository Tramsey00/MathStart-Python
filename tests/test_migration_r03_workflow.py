"""Reject corrupt queue dependencies and unreviewed preservation changes."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.check_migration_preservation import WORKFLOW_SOURCE, workflow_changes
from scripts.check_workflow_docs import validate_queue, validate_workflow


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.queue = {'tasks': [
            {'id': 'MS-T000', 'title': 'Preparation', 'order': 0, 'status': 'READY_FOR_REVIEW', 'dependencies': [], 'acceptance': 'review'},
            {'id': 'MS-T001', 'title': 'Pilot', 'order': 1, 'status': 'PLANNED', 'dependencies': ['MS-T000'], 'acceptance': 'decision', 'legacy_ids': ['MS7-V03']},
        ]}
        self.source = {'rows': [{'id': 'MS7-V03', 'workflow_disposition': 'ADAPTED',
                                 'workflow_tasks': ['MS-T001'], 'workflow_reason': 'preserve scope'}]}

    def test_valid_current_task_graph(self):
        self.assertEqual(len(validate_queue(self.queue, self.source)), 2)

    def test_missing_self_forward_cycle_and_retired_dependency_rejected(self):
        for dependency in ['unknown', 'MS-T001']:
            queue = copy.deepcopy(self.queue)
            queue['tasks'][1]['dependencies'] = [dependency]
            with self.assertRaises(ValueError):
                validate_queue(queue, self.source)
        queue = copy.deepcopy(self.queue)
        queue['tasks'][0]['dependencies'] = ['MS-T001']
        with self.assertRaises(ValueError):
            validate_queue(queue, self.source)
        queue = copy.deepcopy(self.queue)
        queue['tasks'][0]['status'] = 'REMOVED_FROM_PLAN'
        with self.assertRaises(ValueError):
            validate_queue(queue, self.source)

    def test_duplicate_id_order_dependency_and_missing_acceptance_rejected(self):
        for mutate in [
            lambda q: q['tasks'][1].update(id='MS-T000'),
            lambda q: q['tasks'][1].update(order=9),
            lambda q: q['tasks'][1].update(dependencies=['MS-T000', 'MS-T000']),
            lambda q: q['tasks'][1].pop('acceptance'),
        ]:
            q = copy.deepcopy(self.queue)
            mutate(q)
            with self.assertRaises((ValueError, KeyError)):
                validate_queue(q)

    def test_previous_prep_and_visual_cards_not_required_as_first_id(self):
        self.assertEqual(validate_queue(self.queue)[0]['id'], 'MS-T000')

    def test_bootstrap_exception_and_team_handoff_are_bounded(self):
        root = Path(__file__).resolve().parents[1]
        queue = json.loads((root / 'docs/tasks/registry.json').read_text(encoding='utf-8'))
        validate_workflow(queue)
        for mutate in [
            lambda q: q['workflow']['bootstrap']['tasks'].append('MS-T003'),
            lambda q: q['workflow']['bootstrap'].update(branch='main'),
            lambda q: q['workflow']['regular'].update(issue_required=False),
            lambda q: next(r for r in q['tasks'] if r['id'] == 'MS-T003').update(dependencies=['MS-T002']),
        ]:
            changed = copy.deepcopy(queue)
            mutate(changed)
            with self.assertRaises(ValueError):
                validate_workflow(changed)

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
