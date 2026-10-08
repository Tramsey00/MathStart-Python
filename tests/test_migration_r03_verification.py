"""R03 failure routing and historical preservation; no runtime success simulation."""
from contextlib import redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import verify_repo, target_check, target_database, run_unittest
from scripts.check_migration_preservation import verify
from harness.runner.verification import CHECK_COMMANDS, VerificationOutcome


class TargetRegistryTests(unittest.TestCase):
    def test_preserved_input_and_frozen_manifest_bytes(self):
        result = verify()
        self.assertEqual(result["preserved_files"], 1370)

    def test_target_selection_contains_named_equivalents_and_pure_suites(self):
        checks = verify_repo.select_checks(verify_repo.parse_args(["--profile", "target"]))
        self.assertEqual(len(checks), 16)
        self.assertEqual({c.group for c in checks}, set(verify_repo.GROUPS))
        text = repr([c.command for c in checks])
        self.assertNotIn("manage.py", text)
        for marker in ("test_r03_contract.py", "test_r02a_contract.py", "test_r03a_contract.py", "frontend-e2e"):
            self.assertIn(marker, text)

    def test_nested_target_registry_is_nonrecursive(self):
        args = verify_repo.parse_args(CHECK_COMMANDS["repo-baseline"][1:])
        self.assertEqual(args.profile, "target")
        self.assertNotIn("harness", {c.group for c in verify_repo.select_checks(args)})

    def test_group_semantics_and_empty_is_failure(self):
        args = verify_repo.parse_args(["--profile", "target", "--group", "content"])
        self.assertEqual(len(verify_repo.select_checks(args)), 3)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(verify_repo.main(["--profile", "target", "--group", "tests", "--exclude-group", "tests"]), 1)

    def test_pure_is_explicit_subset_not_full_target(self):
        checks = verify_repo.select_checks(verify_repo.parse_args(["--profile", "pure"]))
        self.assertEqual(len(checks), 6)
        self.assertFalse(any("scripts/target_check.py" in c.command for c in checks))

    def test_timeout_and_missing_tool_nonzero(self):
        for error, code in [(subprocess.TimeoutExpired(["x"], 600), 124), (FileNotFoundError(), 127)]:
            with patch.object(verify_repo.subprocess, "run", side_effect=error), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(verify_repo.run_command(["missing"]), code)

    def test_failed_check_cannot_make_canonical_pass(self):
        with patch.object(verify_repo, "run_command", return_value=9), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(verify_repo.main(["--profile", "target", "--group", "backend"]), 1)

    def test_empty_and_skipped_unittest_are_failure(self):
        result = unittest.TestResult(); result.skipped = [("required", "tool missing")]
        result.testsRun = 1
        for count in (0, 1):
            suite = unittest.TestSuite()
            with patch.object(unittest.defaultTestLoader, "discover", return_value=suite), patch.object(suite, "countTestCases", return_value=count), patch.object(unittest.TextTestRunner, "run", return_value=result), redirect_stdout(io.StringIO()):
                self.assertEqual(run_unittest.main(["--start", "tests", "--pattern", "missing.py"]), 1)

    def test_missing_handoff_and_frontend_package_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(OSError): target_check.command_for("system", root)
            with self.assertRaises(ValueError): target_check.command_for("frontend-build", root)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(target_check.main(["system"]), 1)

    def test_reviewed_handoff_requires_real_backend_file_and_rejects_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); path = root / target_check.HANDOFF.relative_to(target_check.ROOT)
            path.parent.mkdir(parents=True); (root / "backend").mkdir()
            script = root / "backend/check.py"; script.write_text("raise SystemExit(0)\n")
            for name, valid in [("backend/check.py", True), ("../outside.py", False), ("backend/missing.py", False)]:
                path.write_text(json.dumps({"status": "REVIEWED", "commands": {"system": {"script": name, "args": ["--check"]}}}))
                if valid:
                    command, cwd = target_check.command_for("system", root)
                    self.assertEqual(command, [sys.executable, str(script.resolve()), "--check"])
                    self.assertEqual(cwd, root)
                else:
                    with self.assertRaises(ValueError): target_check.command_for("system", root)

    def test_frontend_missing_script_and_missing_npm_are_failures(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); frontend = root / "frontend"; frontend.mkdir()
            (frontend / "package-lock.json").write_text("{}")
            package = frontend / "package.json"; package.write_text('{"scripts": {}}')
            with self.assertRaises(ValueError): target_check.command_for("frontend-e2e", root)
            package.write_text('{"scripts": {"test:e2e": "playwright test"}}')
            with patch.object(target_check.shutil, "which", return_value=None):
                with self.assertRaises(ValueError): target_check.command_for("frontend-e2e", root)

    def test_wrapper_timeout_and_output_redaction(self):
        command = ([sys.executable, "synthetic.py"], target_check.ROOT)
        with patch.object(target_check, "command_for", return_value=command):
            with patch.object(target_check.subprocess, "run", side_effect=subprocess.TimeoutExpired([], 540)), redirect_stdout(io.StringIO()):
                self.assertEqual(target_check.main(["system"]), 124)
            output = io.StringIO()
            done = subprocess.CompletedProcess([], 7, "password=synthetic-sensitive\n", "")
            with patch.object(target_check.subprocess, "run", return_value=done), redirect_stdout(output):
                self.assertEqual(target_check.main(["system"]), 7)
            self.assertNotIn("synthetic-sensitive", output.getvalue())

    def test_rehearsals_require_explicit_disposable_guard(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(target_check, "command_for") as resolve, redirect_stdout(io.StringIO()):
            self.assertEqual(target_check.main(["fresh-install", "--disposable"]), 1)
            self.assertEqual(target_check.main(["upgrade-C"]), 1)
            resolve.assert_not_called()

    def test_database_configuration_does_not_fallback_to_sqlite(self):
        with patch.dict(os.environ, {"DJANGO_DB_BACKEND": "sqlite"}, clear=True), redirect_stdout(io.StringIO()):
            self.assertEqual(target_database.probe(), 1)

    def test_database_timeout_and_sensitive_child_errors_not_forwarded(self):
        output = io.StringIO()
        for completed in (subprocess.CompletedProcess([], 1, "", "postgresql://secret"),):
            with patch.object(target_database.subprocess, "run", return_value=completed), redirect_stdout(output):
                self.assertEqual(target_database.main([]), 1)
        self.assertNotIn("secret", output.getvalue())
        with patch.object(target_database.subprocess, "run", side_effect=subprocess.TimeoutExpired([], 15)), redirect_stdout(io.StringIO()):
            self.assertEqual(target_database.main([]), 1)

    def test_not_run_never_ready(self):
        self.assertEqual(VerificationOutcome([{"status": "NOT_RUN"}], []).status, "FAIL")
        self.assertEqual(VerificationOutcome([], []).status, "FAIL")

    def test_runtime_receipt_requires_nonempty_unskipped_pg_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "result.json"
            good = {"check_id": "backend-tests", "status": "PASS", "assertions": 1,
                    "skipped": 0, "evidence_class": "TARGET_RUNTIME",
                    "database_vendor": "postgresql", "postgresql_major": 16}
            path.write_text(json.dumps(good))
            self.assertEqual(target_check.validate_result(path, "backend-tests"), good)
            for change in ({"assertions": 0}, {"assertions": True}, {"skipped": 1},
                           {"database_vendor": "sqlite"}, {"postgresql_major": 15},
                           {"evidence_class": "MODEL_SYNTHETIC"}, {"check_id": "other"}):
                path.write_text(json.dumps({**good, **change}))
                with self.assertRaises(ValueError): target_check.validate_result(path, "backend-tests")

    def test_success_exit_without_required_runtime_receipt_is_failure(self):
        with patch.object(target_check, "command_for", return_value=([sys.executable, "synthetic.py"], target_check.ROOT)), patch.object(target_check.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")), redirect_stdout(io.StringIO()):
            self.assertEqual(target_check.main(["backend-tests"]), 1)

    def test_ci_linkage_rejects_old_checkout_and_wrong_merge_parents(self):
        from scripts.ci_provenance import collect
        sha = "a" * 40; base = "b" * 40; head = "c" * 40
        with patch("scripts.ci_provenance.git", side_effect=[sha]):
            with self.assertRaises(ValueError): collect({}, {"GITHUB_SHA": head})
        event = {"pull_request": {"base": {"sha": base}, "head": {"sha": head}}}
        with patch("scripts.ci_provenance.git", side_effect=[sha, base + " " + sha, "tree"]):
            with self.assertRaises(ValueError): collect(event, {"GITHUB_SHA": sha})
        with patch("scripts.ci_provenance.git", side_effect=[sha, base + " " + head, "tree", "headtree"]):
            result = collect(event, {"GITHUB_SHA": sha, "GITHUB_REF": "refs/pull/49/merge"})
        self.assertEqual(result["parents"], [base, head])

    def test_dsn_and_session_headers_are_redacted_before_evidence(self):
        from harness.runner.verification import _safe_diagnostic
        for value in ("postgresql://synthetic:private@localhost/test", "Set-Cookie: sessionid=private", "dsn=private"):
            self.assertNotIn("private", _safe_diagnostic(value))

    def test_six_historical_chains_preserve_original_results_and_references(self):
        root = target_check.ROOT
        old = json.loads((root / "docs/acceptance/MS7-MIG-R01/old-to-new-evidence.json").read_text(encoding="utf-8"))
        preserved = {r["original_result"]["id"]: r["original_result"] for r in old["records"]}
        new = json.loads((root / "docs/acceptance/MS7-MIG-R03/old-to-new-evidence.json").read_text(encoding="utf-8"))
        self.assertEqual({r["original_result"]["id"] for r in new["records"]}, {"R01", "R03", "MS6-R04", "MS6-V01", "MS7-R02A", "MS7-R03A"})
        for record in new["records"]:
            name = record["original_result"]["id"]
            if name in preserved:
                self.assertEqual(record["original_result"], preserved[name])
            self.assertEqual(record["migration_follow_up"]["id"], "MS7-MIG-R03")
            for field in ("trace", "verification"):
                self.assertTrue((root / record["target_evidence"][field]).is_file())
            self.assertIn("NOT_RUN", record["target_evidence"]["runtime_equivalents"])


if __name__ == "__main__":
    unittest.main()
