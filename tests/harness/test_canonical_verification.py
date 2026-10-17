from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from harness.runner.verification import CHECK_COMMANDS
from scripts import verify_repo


class CanonicalVerificationTests(unittest.TestCase):
    def test_default_selection_runs_harness_suite(self) -> None:
        checks = verify_repo.select_checks(verify_repo.parse_args([]))
        harness = [check for check in checks if check.group == "harness"]
        self.assertEqual(len(harness), 1)
        self.assertIn("tests/harness", harness[0].command)
        self.assertEqual(len(checks), 8)

    def test_nested_baseline_excludes_harness_and_preserves_prior_checks(self) -> None:
        command = CHECK_COMMANDS["repo-baseline"]
        self.assertEqual(command[0], "scripts/verify_repo.py")
        checks = verify_repo.select_checks(verify_repo.parse_args(command[1:]))
        self.assertNotIn("harness", {check.group for check in checks})
        self.assertEqual(len(checks), 15)
        self.assertIn("tests/harness", CHECK_COMMANDS["harness-unit"])
        # Neither nested baseline nor Harness suite invokes execute CLI.
        self.assertFalse(any("harness" in check.command for check in checks))
        self.assertNotIn("execute", CHECK_COMMANDS["harness-unit"])

    def test_harness_failure_fails_canonical_entry_point_used_by_ci(self) -> None:
        harness_command = next(check.command for check in verify_repo.CHECKS
                               if check.group == "harness")
        with (
            patch.object(verify_repo, "run_command",
                         side_effect=lambda command: 1 if command == harness_command else 0) as run,
            redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(verify_repo.main([]), 1)
        self.assertIn(harness_command, [call.args[0] for call in run.call_args_list])

    def test_list_and_selected_harness_group(self) -> None:
        output = io.StringIO()
        with patch.object(verify_repo, "run_command") as run, redirect_stdout(output):
            self.assertEqual(verify_repo.main(["--group", "harness", "--list"]), 0)
        self.assertIn("[harness] Harness test suite", output.getvalue())
        run.assert_not_called()

    def test_skip_tests_excludes_all_test_suites(self) -> None:
        checks = verify_repo.select_checks(verify_repo.parse_args(["--skip-tests"]))
        self.assertEqual({check.group for check in checks}, {"backend", "database", "content"})


if __name__ == "__main__":
    unittest.main()
