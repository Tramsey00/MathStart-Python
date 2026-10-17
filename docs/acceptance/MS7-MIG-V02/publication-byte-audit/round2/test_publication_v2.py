"""Fresh P01/P02/P03 negatives; no backend test or domain implementation edits."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('v02_publication_checker', HERE / 'verify_publication_v2.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class PolicyNegatives(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (HERE / 'exception-policy.json').read_bytes()
        cls.policy = checker.validate_policy(cls.raw)

    def rejected_policy(self, mutate):
        candidate = deepcopy(self.policy)
        mutate(candidate)
        raw = (json.dumps(candidate, ensure_ascii=False, indent=2) + '\n').encode()
        with self.assertRaisesRegex(checker.GateError, 'POLICY_DIGEST_MISMATCH'):
            checker.validate_policy(raw)

    def test_original_exact_proposed_policy(self):
        self.assertEqual(len(checker.validate_policy(self.raw)['whitespace_exceptions']), 40)

    def test_add_mutable_report_exception_fails(self):
        self.rejected_policy(lambda p: p['whitespace_exceptions'].append({
            **p['whitespace_exceptions'][0], 'path': checker.PREFIX + 'report-v2.md'}))

    def test_modify_allowed_blob_sha256_fails(self):
        self.rejected_policy(lambda p: p['whitespace_exceptions'][0].update(blob_sha256='0' * 64))

    def test_remove_required_exception_fails(self):
        self.rejected_policy(lambda p: p['whitespace_exceptions'].pop())

    def test_add_unapproved_exception_fails(self):
        self.rejected_policy(lambda p: p['whitespace_exceptions'].append({
            **p['whitespace_exceptions'][0], 'path': 'new/unapproved.txt'}))

    def test_replace_same_count_exception_fails(self):
        self.rejected_policy(lambda p: p['whitespace_exceptions'][0].update(path=checker.PREFIX + 'report-v2.md'))

    def test_reorder_policy_requires_new_review(self):
        self.rejected_policy(lambda p: p['whitespace_exceptions'].reverse())

    def test_local_policy_cannot_self_approve(self):
        self.rejected_policy(lambda p: p.update(approval_status='APPROVED'))

    def test_new_whitespace_outside_allowlist_fails(self):
        ordinary = {'exit_code': 2, 'count': 3888, 'by_path': {
            x['path']: x['ordinary'] for x in self.policy['whitespace_exceptions']}}
        ordinary['by_path'][checker.PREFIX + 'report-v2.md'] = [{'line': 1, 'reason': 'trailing whitespace'}]
        cr = {'exit_code': 2, 'count': 6, 'by_path': {x['path']: x['cr_at_eol'] for x in self.policy['whitespace_exceptions'] if x['cr_at_eol']}}
        with self.assertRaisesRegex(checker.GateError, 'UNKNOWN_OR_CHANGED_WHITESPACE_DIAGNOSTICS'):
            checker.validate_diagnostics(self.policy, ordinary, cr)

    def test_unknown_diagnostic_in_existing_exception_fails(self):
        ordinary = {'exit_code': 2, 'count': 3887, 'by_path': {
            x['path']: deepcopy(x['ordinary']) for x in self.policy['whitespace_exceptions']}}
        ordinary['by_path'][self.policy['whitespace_exceptions'][0]['path']][0]['reason'] = 'space before tab in indent'
        cr = {'exit_code': 2, 'count': 6, 'by_path': {x['path']: x['cr_at_eol'] for x in self.policy['whitespace_exceptions'] if x['cr_at_eol']}}
        with self.assertRaises(checker.GateError):
            checker.validate_diagnostics(self.policy, ordinary, cr)

    def test_crlf_lf_working_text_normalization_is_equivalent(self):
        attrs = {'text': 'auto', 'eol': 'lf', 'diff': 'unspecified', 'whitespace': 'unspecified'}
        self.assertEqual(checker.canonical_work(b'one\r\ntwo\r\n', attrs), b'one\ntwo\n')
        self.assertEqual(checker.canonical_work(b'one\ntwo\n', attrs), b'one\ntwo\n')

    def test_raw_crcrlf_must_not_be_normalized(self):
        attrs = {'text': 'unset', 'eol': 'lf', 'diff': 'unspecified', 'whitespace': 'unspecified'}
        original = b'one\r\r\n'
        self.assertEqual(checker.canonical_work(original, attrs), original)
        self.assertNotEqual(checker.canonical_work(original, attrs), b'one\n')

    def test_frozen_historical_crlf_blob_can_match_lf_checkout(self):
        attrs = {'text': 'auto', 'eol': 'lf', 'diff': 'unspecified', 'whitespace': 'unspecified'}
        self.assertEqual(checker.canonical_work(b'{"historical":true}\r\n', attrs),
                         checker.canonical_work(b'{"historical":true}\n', attrs))

    def test_no_whitespace_or_diff_suppression(self):
        for field in ('diff', 'whitespace'):
            attrs = {'text': 'auto', 'eol': 'lf', 'diff': 'unspecified', 'whitespace': 'unspecified'}
            attrs[field] = 'unset'
            with self.assertRaisesRegex(checker.GateError, 'SUPPRESSION_ATTRIBUTE'):
                checker.canonical_work(b'one\n', attrs)

    def test_external_runner_pin_rejects_verifier_and_policy_joint_substitution(self):
        # Model an independent runner's before-execution pin; this fixture is NOT
        # evidence of deployed R03/CI enforcement or real owner approval.
        reviewed = (HERE / 'verify_publication_v2.py').read_bytes()
        reviewed_digest = sha256(reviewed).hexdigest()
        replacement = b'print("invented PASS")\n'
        candidate_policy = deepcopy(self.policy)
        candidate_policy['whitespace_exceptions'].append({'path': 'mutable/report.md'})
        self.assertNotEqual(sha256(replacement).hexdigest(), reviewed_digest)
        with self.assertRaisesRegex(checker.GateError, 'TRUSTED_RUNNER_VERIFIER_PIN'):
            checker.require(sha256(replacement).hexdigest() == reviewed_digest, 'TRUSTED_RUNNER_VERIFIER_PIN')
        self.assertEqual(self.policy['approval_status'], checker.OWNER_PENDING)


if __name__ == '__main__':
    unittest.main(verbosity=2)
