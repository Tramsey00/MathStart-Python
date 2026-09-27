from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from harness.adapters.fake import FakeAdapter
from harness.cli.main import main
from harness.runner.engine import _finish_run
from harness.runner.lifecycle import RunWorkspace, create_run_id, utc_now
from tests.harness.test_cli import VALID_MANIFEST


ROOT = Path(__file__).resolve().parents[2]


class SimulatedCrash(BaseException):
    pass


class ReadyPublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        path = Path(self.temp.name)
        self.workspace = RunWorkspace(create_run_id(), path, path / "result.json")
        self.receipt_path = path / "result.ready-commit.json"
        self.staged_path = path / "result.staged.json"
        self.now = 0.0
        self.manifest = {**VALID_MANIFEST, "limits": {
            **VALID_MANIFEST["limits"], "wall_time_seconds": 1,
        }}

    def finish(self):
        with (
            patch("harness.runner.engine.time.monotonic", side_effect=lambda: self.now),
            patch("harness.runner.engine.working_tree_status", return_value=""),
        ):
            return _finish_run(
                repo_root=ROOT, manifest=self.manifest, workspace=self.workspace,
                started_at=utc_now(), started_perf=0.0, adapter=FakeAdapter("happy"),
                artifacts=[], turns_used=1, status="READY_FOR_REVIEW", blockers=[],
                final_patch="", events=[], verification_status="PASS",
                verification_checks=[{"id": check, "status": "PASS", "exit_code": 0}
                                     for check in self.manifest["required_checks"]],
                next_gate="HUMAN_REVIEW", exit_code=0,
            )

    def status(self):
        output = io.StringIO()
        with (
            patch("harness.cli.status.repository_root", return_value=ROOT),
            patch("harness.cli.status.load_run_workspace", return_value=self.workspace),
            redirect_stdout(output),
        ):
            code = main(["status", self.workspace.run_id])
        return code, output.getvalue()

    def assert_uncommitted(self):
        code, output = self.status()
        self.assertEqual(code, 2)
        self.assertIn("BLOCKED_CONFIGURATION", output)
        self.assertIn("UNCOMMITTED_RESULT", output)
        self.assertNotIn("READY_FOR_REVIEW", output)

    def test_crash_after_canonical_replace_before_receipt_is_not_ready(self):
        replace_path = Path.replace

        def crash_after_replace(source, destination):
            published = replace_path(source, destination)
            if source == self.staged_path and destination == self.workspace.result_path:
                raise SimulatedCrash()
            return published

        with patch.object(Path, "replace", autospec=True, side_effect=crash_after_replace):
            with self.assertRaises(SimulatedCrash):
                self.finish()
        canonical = json.loads(self.workspace.result_path.read_text(encoding="utf-8"))
        self.assertEqual(canonical["status"], "READY_FOR_REVIEW")
        self.assertFalse(self.receipt_path.exists())
        self.assert_uncommitted()

    def test_happy_path_has_matching_receipt_and_status_is_ready(self):
        result, code = self.finish()
        self.assertEqual((result["status"], code), ("READY_FOR_REVIEW", 0))
        self.assertEqual(result["verification"]["status"], "PASS")
        self.assertEqual(result["next_gate"], "HUMAN_REVIEW")
        canonical_bytes = self.workspace.result_path.read_bytes()
        self.assertEqual(json.loads(canonical_bytes), result)
        self.assertFalse(self.staged_path.exists())
        receipt = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(receipt["schema_version"], "harness-ready-commit-v1")
        self.assertEqual(receipt["run_id"], result["run_id"])
        self.assertEqual(receipt["status"], "READY_FOR_REVIEW")
        self.assertEqual(receipt["result_sha256"], hashlib.sha256(canonical_bytes).hexdigest())
        self.assertLess(receipt["published_monotonic"], receipt["deadline_monotonic"])
        status_code, output = self.status()
        self.assertEqual(status_code, 0)
        self.assertIn("READY_FOR_REVIEW", output)

    def test_missing_or_corrupt_receipt_blocks_ready(self):
        self.finish()
        for receipt_bytes in (None, b"{", b"[]", b"", b"\xff"):
            with self.subTest(receipt=receipt_bytes):
                if receipt_bytes is None:
                    self.receipt_path.unlink(missing_ok=True)
                else:
                    self.receipt_path.write_bytes(receipt_bytes)
                self.assert_uncommitted()

    def test_receipt_digest_mismatch_blocks_ready(self):
        result, code = self.finish()
        canonical_bytes = self.workspace.result_path.read_bytes()
        self.workspace.result_path.write_bytes(canonical_bytes + b"\n")
        self.assertEqual(json.loads(self.workspace.result_path.read_bytes()), result)
        self.assert_uncommitted()

    def test_invalid_receipt_identity_or_deadline_blocks_ready(self):
        self.finish()
        receipt = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        mutations = [
            ("schema_version", "unknown"), ("run_id", "wrong-run"), ("status", "FAIL"),
            ("published_monotonic", 1.0), ("published_monotonic", 2.0),
            ("published_monotonic", float("nan")), ("deadline_monotonic", float("inf")),
            ("published_monotonic", False), ("deadline_monotonic", "1"),
            ("published_monotonic", None), ("result_sha256", None),
        ]
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                self.receipt_path.write_text(json.dumps({**receipt, field: value}), encoding="utf-8")
                self.assert_uncommitted()

    def test_receipt_replace_failure_returns_non_success(self):
        replace_path = Path.replace

        def fail_receipt(source, destination):
            if destination == self.receipt_path:
                self.assertTrue(source.is_file())
                self.assert_uncommitted()
                raise OSError("receipt publication failed")
            return replace_path(source, destination)

        with patch.object(Path, "replace", autospec=True, side_effect=fail_receipt):
            result, code = self.finish()
        self.assertEqual((result["status"], code), ("BLOCKED_CONFIGURATION", 2))
        self.assertEqual(result["verification"]["status"], "FAIL")
        self.assertIsNone(result["next_gate"])
        self.assertEqual(result["blockers"][0]["code"], "READY_COMMIT_FAILED")
        self.assertFalse(self.receipt_path.exists())
        self.assertEqual(json.loads(self.workspace.result_path.read_bytes()), result)
        status_code, output = self.status()
        self.assertEqual(status_code, 2)
        self.assertNotIn("READY_FOR_REVIEW", output)

    def test_receipt_and_diagnostic_write_failure_leave_ready_uncommitted(self):
        from harness.runner.lifecycle import write_json

        def fail_publication(path, value):
            if path in (self.receipt_path, self.workspace.result_path):
                raise OSError("storage unavailable")
            write_json(path, value)

        with patch("harness.runner.engine.write_json", side_effect=fail_publication):
            result, code = self.finish()
        self.assertEqual((result["status"], code), ("BLOCKED_CONFIGURATION", 2))
        self.assertEqual(result["verification"]["status"], "FAIL")
        self.assertIsNone(result["next_gate"])
        self.assertEqual([item["code"] for item in result["blockers"]],
                         ["READY_COMMIT_FAILED", "RESULT_PERSISTENCE_FAILED"])
        self.assertEqual(json.loads(self.workspace.result_path.read_bytes())["status"],
                         "READY_FOR_REVIEW")
        self.assertFalse(self.receipt_path.exists())
        self.assert_uncommitted()

    def test_ambiguous_receipt_commit_recovers_ready_when_cleanup_and_rewrite_fail(self):
        from harness.runner.lifecycle import write_json

        replace_path = Path.replace
        unlink_path = Path.unlink
        attempted = []

        def report_error_after_receipt_replace(source, destination):
            published = replace_path(source, destination)
            if destination == self.receipt_path:
                attempted.append("receipt-replace")
                raise OSError("replace committed but reported failure")
            return published

        def fail_receipt_cleanup(path, *, missing_ok=False):
            if path == self.receipt_path:
                attempted.append("receipt-cleanup")
                raise OSError("receipt cleanup failed")
            return unlink_path(path, missing_ok=missing_ok)

        def fail_diagnostic_write(path, value):
            if path == self.workspace.result_path and value["status"] == "BLOCKED_CONFIGURATION":
                attempted.append("diagnostic-write")
                raise OSError("diagnostic rewrite failed")
            write_json(path, value)

        with (
            patch.object(Path, "replace", autospec=True,
                         side_effect=report_error_after_receipt_replace),
            patch.object(Path, "unlink", autospec=True, side_effect=fail_receipt_cleanup),
            patch("harness.runner.engine.write_json", side_effect=fail_diagnostic_write),
        ):
            result, code = self.finish()

        self.assertEqual(attempted,
                         ["receipt-replace", "receipt-cleanup", "diagnostic-write"])
        # The committed files and the returned result must have one outcome.
        self.assertEqual(self.status()[0], 0)
        self.assertEqual((result["status"], code), ("READY_FOR_REVIEW", 0))
        self.assertEqual(result["verification"]["status"], "PASS")
        self.assertEqual(result["next_gate"], "HUMAN_REVIEW")
        self.assertEqual(json.loads(self.workspace.result_path.read_bytes()), result)

    def test_receipt_may_finish_after_deadline_for_timely_canonical_replace(self):
        replace_path = Path.replace

        def delay_receipt(source, destination):
            if source == self.staged_path and destination == self.workspace.result_path:
                published = replace_path(source, destination)
                self.now = 0.5
                return published
            if destination == self.receipt_path:
                self.now = 2.0
                self.assertTrue(source.is_file())  # A valid temp receipt is not committed.
                self.assert_uncommitted()
            return replace_path(source, destination)

        with patch.object(Path, "replace", autospec=True, side_effect=delay_receipt):
            result, code = self.finish()
        self.assertEqual((result["status"], code), ("READY_FOR_REVIEW", 0))
        receipt = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(receipt["published_monotonic"], 0.5)
        self.assertEqual(receipt["deadline_monotonic"], 1.0)
        self.assertEqual(self.now, 2.0)
        self.assertEqual(self.status()[0], 0)

    def test_status_during_expired_final_replace_never_exposes_ready(self):
        replace_path = Path.replace

        def expire_during_replace(source, destination):
            published = replace_path(source, destination)
            if source == self.staged_path and destination == self.workspace.result_path:
                self.now = 2.0
                self.assert_uncommitted()
            return published

        with patch.object(Path, "replace", autospec=True, side_effect=expire_during_replace):
            result, code = self.finish()
        self.assertEqual((result["status"], code), ("BUDGET_EXCEEDED", 4))
        self.assertEqual(result["verification"]["status"], "FAIL")
        self.assertIsNone(result["next_gate"])
        self.assertEqual(sum(item["code"] == "WALL_TIME_EXCEEDED" for item in result["blockers"]), 1)
        self.assertEqual(result["execution"]["wall_time_ms"], 2000)
        self.assertEqual(result["budget"]["wall_time_ms"], 2000)
        self.assertFalse(self.receipt_path.exists())
        self.assertEqual(json.loads(self.workspace.result_path.read_bytes()), result)
        status_code, output = self.status()
        self.assertEqual(status_code, 4)
        self.assertIn("BUDGET_EXCEEDED", output)
        self.assertNotIn("READY_FOR_REVIEW", output)

    def test_non_ready_results_do_not_require_receipt(self):
        result, code = self.finish()
        self.receipt_path.write_bytes(b"corrupt receipt")
        for status, expected_exit in (("FAIL", 1), ("BLOCKED_CONFIGURATION", 2),
                                      ("NEEDS_HUMAN", 3), ("INTERRUPTED", 4),
                                      ("BUDGET_EXCEEDED", 4)):
            with self.subTest(status=status):
                result["status"] = status
                result["verification"]["status"] = "FAIL"
                result["next_gate"] = None
                self.workspace.result_path.write_text(json.dumps(result), encoding="utf-8")
                status_code, output = self.status()
                self.assertEqual(status_code, expected_exit)
                self.assertIn(status, output)
                self.assertNotIn("UNCOMMITTED_RESULT", output)
