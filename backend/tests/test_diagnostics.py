"""Failed backend suites retain safe identities when stdout is bounded."""
from contextlib import redirect_stderr
import io
import json
import unittest
from unittest.mock import patch
from backend.verification_suite import execute, SuiteFailure


class DiagnosticTests(unittest.TestCase):
    def check_result(self, method, field):
        class Probe(unittest.TestCase):
            def runTest(self):
                method(self)
        suite = unittest.TestSuite([Probe()])
        with patch.object(unittest.defaultTestLoader, 'loadTestsFromNames', return_value=suite), redirect_stderr(io.StringIO()):
            with self.assertRaises(SuiteFailure) as caught:
                execute(['explicit-test-suite'])
        diagnostics = caught.exception.diagnostics
        self.assertEqual(diagnostics['tests_run'], 1)
        self.assertEqual(len(diagnostics[field]), 1)
        self.assertNotIn('private probe value', json.dumps(diagnostics))

    def test_failure_identity_without_private_assertion_value(self):
        self.check_result(lambda case: case.fail('private probe value'), 'failed_case_ids')

    def test_error_identity_without_private_exception_value(self):
        def error(case):
            raise ValueError('private probe value')
        self.check_result(error, 'error_case_ids')

    def test_skip_keeps_nonpassing_case_identity(self):
        self.check_result(lambda case: case.skipTest('private probe value'), 'skipped_case_ids')

    def test_subtest_parameter_values_are_not_reported(self):
        def failure(case):
            with case.subTest(payload='private probe value'):
                case.fail('private probe value')
        self.check_result(failure, 'failed_case_ids')
