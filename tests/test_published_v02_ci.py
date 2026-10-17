"""Orchestration guards only; synthetic inputs never prove V02 publication."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('published_v02_ci', ROOT/'scripts/published_v02_ci.py')
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


class PublishedV02GuardTests(unittest.TestCase):
    def setUp(self):
        self.input = dict(format='r03-v02-published-candidate-v1', task_id='MS7-MIG-V02',
                          status='PINNED_PUBLISHED_CANDIDATE', pr_url='https://github.com/Tramsey00/MathStart-Python/pull/999',
                          implementation_sha='a'*40, control_revision=ci.CONTROL,
                          anchor_sha256=ci.ANCHOR, owner_confirmation_sha256=ci.CONFIRMATION_SHA)
        self.validated = ci.candidate_input(json.dumps(self.input).encode())
        self.pr = dict(number=999, state='open', merged=False, title='MS7-MIG-V02: synthetic guard fixture',
                       user={'login': 'VladimirFrolov777'},
                       head={'sha': 'a'*40, 'repo': {'full_name': ci.REPOSITORY}},
                       base={'sha': ci.BASE, 'ref': 'ms7-mig-react-fastapi', 'repo': {'full_name': ci.REPOSITORY}})
        self.commit = dict(sha='a'*40, parents=[{'sha': ci.BASE}], tree={'sha': ci.TREE})

    def test_confirmed_human_artifact_and_byte_tamper(self):
        raw = (ROOT/ci.CONFIRMATION_PATH).read_bytes()
        self.assertTrue(ci.confirmation(raw)['publication_authorized'])
        with self.assertRaisesRegex(RuntimeError, 'HUMAN_CONFIRMATION_DIGEST'):
            ci.confirmation(raw+b'\n')

    def test_missing_short_or_surrogate_sha_cannot_be_implementation(self):
        for value in (None, '', 'a'*7, ci.BASE, ci.TREE, ci.CONTROL):
            with self.subTest(value=value):
                candidate = dict(self.input, implementation_sha=value)
                with self.assertRaises(RuntimeError):
                    ci.candidate_input(json.dumps(candidate).encode())

    def test_trust_pins_cannot_be_changed_by_candidate(self):
        for key in ('control_revision', 'anchor_sha256', 'owner_confirmation_sha256'):
            with self.subTest(key=key):
                with self.assertRaisesRegex(RuntimeError, 'CANDIDATE_CANNOT_OVERRIDE_TRUST_PINS'):
                    ci.candidate_input(json.dumps(dict(self.input, **{key: 'b'*64})).encode())

    def test_unknown_override_and_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'CANDIDATE_INPUT_SCHEMA'):
            ci.candidate_input(json.dumps(dict(self.input, verifier_path='candidate/verifier.py')).encode())
        with self.assertRaisesRegex(RuntimeError, 'DUPLICATE_JSON_KEY'):
            ci.decode(b'{"implementation_sha":"a","implementation_sha":"b"}')

    def test_repository_pr_url_is_exact(self):
        for url in ('https://github.com/other/repo/pull/999', 'https://example.org/999',
                    self.input['pr_url']+'?head=other', self.input['pr_url']+'/files'):
            with self.subTest(url=url):
                with self.assertRaisesRegex(RuntimeError, 'EXACT_REPOSITORY_PR_URL_REQUIRED'):
                    ci.candidate_input(json.dumps(dict(self.input, pr_url=url)).encode())

    def test_valid_pr_and_commit_are_metadata_checks_only(self):
        ci.validate_pr(self.pr, self.validated)
        ci.validate_commit(self.commit, self.validated)

    def test_live_head_change_is_rejected_including_after_gate(self):
        changed = copy.deepcopy(self.pr)
        changed['head']['sha'] = 'b'*40
        with self.assertRaisesRegex(RuntimeError, 'LIVE_PR_HEAD_CHANGED'):
            ci.validate_pr(changed, self.validated)

    def test_live_base_owner_repository_and_closed_pr(self):
        for kind, reason in [('base', 'LIVE_PR_BASE_CHANGED'), ('owner', 'V02_OWNER_TASK_PR_REQUIRED'),
                             ('repo', 'CANDIDATE_REPOSITORY_BASE'), ('closed', 'CURRENT_OPEN_PR_REQUIRED')]:
            changed = copy.deepcopy(self.pr)
            if kind == 'base':
                changed['base']['sha'] = 'b'*40
            elif kind == 'owner':
                changed['user']['login'] = 'other'
            elif kind == 'repo':
                changed['head']['repo']['full_name'] = 'other/fork'
            else:
                changed['state'] = 'closed'
            with self.subTest(kind=kind), self.assertRaisesRegex(RuntimeError, reason):
                ci.validate_pr(changed, self.validated)

    def test_multiple_parents_or_different_tree_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'IMPLEMENTATION_SINGLE_BASE_PARENT'):
            ci.validate_commit(dict(self.commit, parents=[{'sha': ci.BASE}, {'sha': 'b'*40}]), self.validated)
        with self.assertRaisesRegex(RuntimeError, 'IMPLEMENTATION_TREE_PIN'):
            ci.validate_commit(dict(self.commit, tree={'sha': 'b'*40}), self.validated)

    def test_executable_replacement_is_rejected_before_import(self):
        with tempfile.TemporaryDirectory(prefix='r03-published-owner-probe-', dir=ROOT.parent) as directory:
            owner = Path(directory).resolve()
            self.assertTrue(owner.is_relative_to(ROOT.parent))
            (owner/'scripts').mkdir()
            (owner/'scripts/v02_publication_gate.py').write_bytes(b'raise SystemExit(0)\n')
            with self.assertRaisesRegex(RuntimeError, 'APPROVED_OWNER_EXECUTABLE_DIGEST'):
                ci.checked_owner_module(owner)

    def test_absent_candidate_stops_before_owner_import_or_network(self):
        with tempfile.TemporaryDirectory(prefix='r03-published-input-probe-', dir=ROOT.parent) as directory:
            isolated = Path(directory).resolve()
            self.assertTrue(isolated.is_relative_to(ROOT.parent))
            target = isolated/ci.CONFIRMATION_PATH
            target.parent.mkdir(parents=True)
            target.write_bytes((ROOT/ci.CONFIRMATION_PATH).read_bytes())
            with patch.object(ci, 'ROOT', isolated), patch.object(ci, 'checked_owner_module') as load_owner, patch.object(ci, 'fetch_json') as network:
                with self.assertRaisesRegex(RuntimeError, 'NOT_RUN_PUBLISHED_PR_AND_IMPLEMENTATION_SHA_NOT_RECEIVED'):
                    ci.execute(isolated.parent/'unused-owner', isolated/'output', 'b'*40)
                load_owner.assert_not_called()
                network.assert_not_called()

    def test_bytecode_cannot_bypass_the_approved_source_digest(self):
        with tempfile.TemporaryDirectory(prefix='r03-published-bytecode-probe-', dir=ROOT.parent) as directory:
            owner = Path(directory).resolve()
            self.assertTrue(owner.is_relative_to(ROOT.parent))
            (owner/'scripts/__pycache__').mkdir(parents=True)
            for path in ci.OWNER_FILES:
                (owner/path).write_bytes((ROOT/path).read_bytes())
            (owner/'scripts/__pycache__/unapproved.pyc').write_bytes(b'unapproved cache')
            with self.assertRaisesRegex(RuntimeError, 'UNAPPROVED_OWNER_BYTECODE'):
                ci.checked_owner_module(owner)
            (owner/'scripts/__pycache__/unapproved.pyc').unlink()
            (owner/'scripts/__pycache__').rmdir()
            module = ci.checked_owner_module(owner)
            self.assertEqual(module.REPO, owner)
            self.assertEqual(module.BASE, ci.BASE)


if __name__ == '__main__':
    unittest.main()
