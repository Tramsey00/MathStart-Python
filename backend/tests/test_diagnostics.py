"""Failed backend suites retain safe identities when stdout is bounded."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch
import sqlalchemy as sa
from backend.verification_suite import execute, SuiteFailure, CleanupFailure, owned_database, main, run


class DiagnosticTests(unittest.TestCase):
    def check_result(self, method, field):
        class Probe(unittest.TestCase):
            def runTest(self):
                method(self)
        suite = unittest.TestSuite([Probe()])
        output = io.StringIO()
        with patch.object(unittest.defaultTestLoader, 'loadTestsFromNames', return_value=suite), redirect_stderr(output):
            with self.assertRaises(SuiteFailure) as caught:
                execute(['explicit-test-suite'])
        diagnostics = caught.exception.diagnostics
        self.assertEqual(diagnostics['tests_run'], 1)
        self.assertEqual(len(diagnostics[field]), 1)
        self.assertNotIn('private probe value', json.dumps(diagnostics))
        self.assertNotIn('private probe value', output.getvalue())

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


class CleanupDiagnosticTests(unittest.TestCase):
    def database(self):
        admin = MagicMock()
        admin.dialect.identifier_preparer.quote.side_effect = lambda name: '"' + name + '"'
        connection = admin.connect.return_value.__enter__.return_value
        connection.scalar.return_value = 17
        engine = Mock()
        return admin, connection, engine

    def suite_failure(self):
        result = unittest.TestResult()
        class Probe(unittest.TestCase):
            def runTest(self):
                raise ValueError('private probe value')
        Probe().run(result)
        return SuiteFailure(result)

    def receipt(self, error):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'result.json'
            output = io.StringIO()
            with patch.dict(os.environ, {'MATHSTART_CHECK_ID': 'backend-tests', 'MATHSTART_CHECK_RESULT': str(path)}), \
                 patch('backend.verification_suite.run', side_effect=error), redirect_stdout(output):
                self.assertEqual(main(), 1)
            self.assertEqual(json.loads(output.getvalue()), json.loads(path.read_text()))
            self.assertNotIn('private probe value', output.getvalue())
            return json.loads(path.read_text())

    def test_primary_suite_failure_survives_engine_and_drop_cleanup_errors(self):
        admin, connection, engine = self.database()
        engine.dispose.side_effect = OSError('private probe value')
        def execute(statement):
            if str(statement).startswith('DROP DATABASE'):
                raise RuntimeError('private probe value')
        connection.execute.side_effect = execute
        primary = self.suite_failure()
        with patch('backend.verification_suite.create_engine', return_value=engine):
            with self.assertRaises(SuiteFailure) as caught:
                with owned_database(admin, sa.make_url('postgresql+psycopg://localhost/test'), 'diagnostics'):
                    raise primary
        self.assertIs(caught.exception, primary)
        receipt = self.receipt(primary)
        self.assertEqual(receipt['failure_class'], 'SuiteFailure')
        self.assertEqual(len(receipt['suite_diagnostics']['error_case_ids']), 1)
        self.assertEqual(receipt['cleanup_diagnostics'], [
            {'phase': 'owned_engine_dispose', 'failure_class': 'OSError'},
            {'phase': 'owned_database_drop', 'failure_class': 'RuntimeError'}])
        statements = [str(call.args[0]) for call in connection.execute.call_args_list]
        self.assertEqual(sum(sql.startswith('DROP DATABASE') for sql in statements), 1)
        self.assertFalse(any('terminate' in sql.lower() or 'force' in sql.lower() for sql in statements))

    def test_cleanup_only_failure_is_nonpassing_and_identity_change_refuses_drop(self):
        admin, connection, engine = self.database()
        connection.scalar.side_effect = [17, 18]
        with patch('backend.verification_suite.create_engine', return_value=engine):
            with self.assertRaises(CleanupFailure) as caught:
                with owned_database(admin, sa.make_url('postgresql+psycopg://localhost/test'), 'diagnostics'):
                    pass
        engine.dispose.assert_called_once_with()
        self.assertFalse(any(str(call.args[0]).startswith('DROP DATABASE') for call in connection.execute.call_args_list))
        receipt = self.receipt(caught.exception)
        self.assertEqual(receipt['failure_class'], 'CleanupFailure')
        self.assertNotIn('suite_diagnostics', receipt)
        self.assertEqual(receipt['cleanup_diagnostics'], [
            {'phase': 'owned_database_drop', 'failure_class': 'RuntimeError'}])

    def test_admin_cleanup_preserves_primary_and_restores_environment(self):
        admin, connection, _ = self.database()
        connection.scalar.return_value = 160000
        admin.dispose.side_effect = OSError('private probe value')
        primary = self.suite_failure()
        config = Mock(url=sa.make_url('postgresql+psycopg://127.0.0.1:55441/test'))
        with patch.dict(os.environ, {'MATHSTART_DISPOSABLE': '1', 'MATHSTART_CHECK_RESULT': 'var/owned/result.json'}), \
             patch('backend.verification_suite.DatabaseConfig.from_environment', return_value=config), \
             patch('backend.tests.legacy_tools.legacy_python'), \
             patch('backend.verification_suite.sa.create_engine', return_value=admin), \
             patch('backend.verification_suite.execute', side_effect=primary):
            before = dict(os.environ)
            with self.assertRaises(SuiteFailure) as caught:
                run()
            self.assertEqual(dict(os.environ), before)
        self.assertIs(caught.exception, primary)
        self.assertEqual(primary.cleanup_diagnostics, [{'phase': 'admin_engine_dispose', 'failure_class': 'OSError'}])
