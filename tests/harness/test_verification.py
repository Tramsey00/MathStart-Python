from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.adapters.fake import FakeAdapter
from harness.contracts.adapter import ToolResult
from harness.runner.engine import _finish_run, execute_bootstrap_run
from harness.runner.lifecycle import RunWorkspace, create_run_id, utc_now
from harness.runner.verification import VerificationOutcome, run_required_checks
from harness.tools.basic import BasicToolExecution

from tests.harness.test_cli import VALID_MANIFEST


ROOT = Path(__file__).resolve().parents[2]
CHECK_IDS = list(VALID_MANIFEST["required_checks"])


class RegistryTests(unittest.TestCase):
    def test_registered_checks_execute_with_fixed_argv_and_store_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_path = Path(directory)
            completed = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="ok\n", stderr="",
            )
            with patch("harness.runner.verification.subprocess.run", return_value=completed) as run:
                outcome = run_required_checks(
                    ROOT, run_path, CHECK_IDS, deadline=time.monotonic() + 60,
                )

            self.assertEqual(outcome.status, "PASS")
            self.assertEqual([c["id"] for c in outcome.checks], CHECK_IDS)
            self.assertEqual([c["exit_code"] for c in outcome.checks], [0, 0, 0])
            self.assertEqual(run.call_count, 3)
            for call in run.call_args_list:
                self.assertFalse(call.kwargs["shell"])
                self.assertEqual(call.args[0][0], __import__("sys").executable)
            self.assertEqual(
                run.call_args_list[0].args[0][1:], ["scripts/verify_repo.py"]
            )
            self.assertTrue((run_path / "checks/repo-baseline.stdout.txt").is_file())
            self.assertEqual(len(outcome.artifacts), 6)

    def test_unknown_check_is_blocked_before_any_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch("harness.runner.verification.subprocess.run") as run:
                with self.assertRaisesRegex(ValueError, "unknown required check"):
                    run_required_checks(
                        ROOT, Path(directory), ["repo-baseline", "arbitrary"],
                        deadline=time.monotonic() + 60,
                    )
                run.assert_not_called()

    def test_failed_exit_code_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.CompletedProcess(
                args=[], returncode=7, stdout="", stderr="failure\n",
            )
            with patch("harness.runner.verification.subprocess.run", return_value=completed):
                outcome = run_required_checks(
                    ROOT, Path(directory), ["harness-unit"],
                    deadline=time.monotonic() + 60,
                )
            self.assertEqual(outcome.status, "FAIL")
            self.assertEqual(outcome.checks[0]["exit_code"], 7)


    def test_timeout_marks_budget_exceeded_and_keeps_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            timeout = subprocess.TimeoutExpired(
                cmd=["python"], timeout=1, output=b"partial\n",
            )
            with patch(
                "harness.runner.verification.subprocess.run", side_effect=timeout,
            ):
                outcome = run_required_checks(
                    ROOT, Path(directory), ["harness-unit"],
                    deadline=time.monotonic() + 60,
                )
            self.assertTrue(outcome.budget_exceeded)
            self.assertEqual(outcome.status, "FAIL")
            self.assertEqual(outcome.checks[0]["exit_code"], None)
            self.assertIn(
                "partial",
                (Path(directory) / "checks/harness-unit.stdout.txt").read_text(
                    encoding="utf-8"
                ),
            )


class ExecuteVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        run_id = create_run_id()
        path = Path(self.temp.name) / run_id
        path.mkdir()
        self.workspace = RunWorkspace(run_id, path, path / "result.json")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _execute(
        self,
        checks: list[dict[str, object]],
        *,
        budget_exceeded: bool = False,
    ) -> tuple[dict, int]:
        def tool_result(repo_root, manifest, request):
            return BasicToolExecution(
                result=ToolResult(
                    call_id=request.call_id,
                    status="OK",
                    output={},
                )
            )

        with (
            patch("harness.runner.engine.create_run_workspace", return_value=self.workspace),
            patch("harness.runner.engine.execute_basic_tool", side_effect=tool_result),
            patch(
                "harness.runner.engine.run_required_checks",
                return_value=VerificationOutcome(
                    checks=checks, artifacts=[], budget_exceeded=budget_exceeded,
                ),
            ) as verify,
        ):
            result, exit_code = execute_bootstrap_run(ROOT, VALID_MANIFEST)
            verify.assert_called_once()
        self.assertEqual(
            json.loads(self.workspace.result_path.read_text(encoding="utf-8"))["verification"],
            result["verification"],
        )
        return result, exit_code

    def _execute_without_verification(
        self,
        adapter: FakeAdapter,
        *,
        max_turns: int = 30,
        interrupt_tool: bool = False,
    ) -> tuple[dict, int]:
        manifest = {**VALID_MANIFEST, "limits": {
            **VALID_MANIFEST["limits"], "max_turns": max_turns,
        }}

        def tool_result(repo_root, manifest, request):
            if interrupt_tool:
                raise KeyboardInterrupt()
            return BasicToolExecution(
                result=ToolResult(call_id=request.call_id, status="OK", output={})
            )

        with (
            patch("harness.runner.engine.create_run_workspace", return_value=self.workspace),
            patch("harness.runner.engine.execute_basic_tool", side_effect=tool_result),
            patch("harness.runner.engine.run_required_checks") as verify,
        ):
            result, exit_code = execute_bootstrap_run(
                ROOT, manifest, adapter=adapter,
            )
            verify.assert_not_called()
        persisted = json.loads(self.workspace.result_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["status"], result["status"])
        self.assertNotEqual(result["status"], "READY_FOR_REVIEW")
        self.assertNotEqual(result["verification"]["status"], "PASS")
        return result, exit_code

    def test_all_required_checks_pass_after_finished(self) -> None:
        checks = [
            {"id": check_id, "status": "PASS", "exit_code": 0}
            for check_id in CHECK_IDS
        ]
        result, exit_code = self._execute(checks)
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["status"], "READY_FOR_REVIEW")
        self.assertEqual(result["verification"], {"status": "PASS", "checks": checks})
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["next_gate"], "HUMAN_REVIEW")
        self.assertEqual(result["execution"]["turns_used"], 3)

    def test_finished_without_all_required_checks_is_not_ready(self) -> None:
        checks = [{"id": CHECK_IDS[0], "status": "PASS", "exit_code": 0}]
        result, exit_code = self._execute(checks)
        self.assertEqual(exit_code, 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertIsNone(result["next_gate"])
        self.assertEqual(result["blockers"][0]["code"], "REQUIRED_CHECKS_INCOMPLETE")

    def test_finalization_cannot_promote_expired_run(self) -> None:
        manifest = {**VALID_MANIFEST, "limits": {
            **VALID_MANIFEST["limits"], "wall_time_seconds": 1,
        }}
        checks = [
            {"id": check_id, "status": "PASS", "exit_code": 0}
            for check_id in CHECK_IDS
        ]
        result, exit_code = _finish_run(
            repo_root=ROOT,
            manifest=manifest,
            workspace=self.workspace,
            started_at=utc_now(),
            started_perf=time.monotonic() - 2,
            adapter=FakeAdapter("happy"),
            artifacts=[],
            turns_used=3,
            status="READY_FOR_REVIEW",
            blockers=[],
            final_patch="",
            events=[],
            verification_status="PASS",
            verification_checks=checks,
            next_gate="HUMAN_REVIEW",
            exit_code=0,
        )
        self.assertEqual((result["status"], exit_code), ("BUDGET_EXCEEDED", 4))
        self.assertEqual(result["verification"]["status"], "FAIL")
        self.assertIsNone(result["next_gate"])
        self.assertTrue(self.workspace.result_path.is_file())

    def test_wall_time_exhausted_during_verification(self) -> None:
        checks = [
            {"id": CHECK_IDS[0], "status": "PASS", "exit_code": 0},
            {"id": CHECK_IDS[1], "status": "FAIL", "exit_code": None},
            {"id": CHECK_IDS[2], "status": "NOT_RUN", "exit_code": None},
        ]
        result, exit_code = self._execute(checks, budget_exceeded=True)
        self.assertEqual((result["status"], exit_code), ("BUDGET_EXCEEDED", 4))
        self.assertEqual(result["verification"], {"status": "FAIL", "checks": checks})
        self.assertIsNone(result["next_gate"])
        self.assertTrue(any(
            blocker["code"] == "WALL_TIME_EXCEEDED" for blocker in result["blockers"]
        ))

    def test_interrupt_during_verification_keeps_partial_evidence(self) -> None:
        def tool_result(repo_root, manifest, request):
            return BasicToolExecution(
                result=ToolResult(call_id=request.call_id, status="OK", output={})
            )

        def interrupt_verification(repo_root, run_path, check_ids, *,
                                   deadline, checks_out, artifacts_out):
            checks_out.append({
                "id": CHECK_IDS[0], "status": "PASS", "exit_code": 0,
            })
            path = run_path / "checks/repo-baseline.stdout.txt"
            path.parent.mkdir(exist_ok=True)
            path.write_text("first check complete\n", encoding="utf-8")
            artifacts_out.append({
                "kind": "check-stdout",
                "path": "checks/repo-baseline.stdout.txt",
                "digest": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
            })
            raise KeyboardInterrupt()

        with (
            patch("harness.runner.engine.create_run_workspace", return_value=self.workspace),
            patch("harness.runner.engine.execute_basic_tool", side_effect=tool_result),
            patch(
                "harness.runner.engine.run_required_checks",
                side_effect=interrupt_verification,
            ),
        ):
            result, exit_code = execute_bootstrap_run(
                ROOT, VALID_MANIFEST, adapter=FakeAdapter("happy"),
            )
        self.assertEqual((result["status"], exit_code), ("INTERRUPTED", 4))
        self.assertEqual(result["verification"]["checks"][0]["id"], CHECK_IDS[0])
        self.assertEqual(result["verification"]["status"], "FAIL")
        self.assertTrue(any(
            item["path"] == "checks/repo-baseline.stdout.txt"
            for item in result["artifacts"]
        ))
        self.assertTrue(self.workspace.result_path.is_file())

    def test_loop_exhausts_runner_turn_budget(self) -> None:
        result, exit_code = self._execute_without_verification(
            FakeAdapter("loop"), max_turns=2,
        )
        self.assertEqual((result["status"], exit_code), ("BUDGET_EXCEEDED", 4))
        self.assertEqual(result["execution"]["turns_used"], 2)

    def test_cancelled_adapter_interrupts_without_verification(self) -> None:
        adapter = FakeAdapter("happy")
        adapter.cancel()
        result, exit_code = self._execute_without_verification(adapter)
        self.assertEqual((result["status"], exit_code), ("INTERRUPTED", 4))
        self.assertEqual(result["blockers"][0]["code"], "ADAPTER_CANCELLED")

    def test_keyboard_interrupt_persists_result(self) -> None:
        result, exit_code = self._execute_without_verification(
            FakeAdapter("happy"), interrupt_tool=True,
        )
        self.assertEqual((result["status"], exit_code), ("INTERRUPTED", 4))
        self.assertEqual(result["blockers"][0]["code"], "KEYBOARD_INTERRUPT")
        self.assertTrue((self.workspace.path / "initial-status.txt").is_file())

    def test_injected_error_adapter_is_used(self) -> None:
        result, exit_code = self._execute_without_verification(
            FakeAdapter("error"),
        )
        self.assertEqual((result["status"], exit_code), ("FAIL", 1))
        self.assertEqual(result["blockers"][0]["code"], "FAKE_ADAPTER_ERROR")

    def test_finished_with_failed_check_is_not_ready(self) -> None:
        checks = [
            {"id": check_id, "status": "FAIL" if check_id == "harness-unit" else "PASS",
             "exit_code": 1 if check_id == "harness-unit" else 0}
            for check_id in CHECK_IDS
        ]
        result, exit_code = self._execute(checks)
        self.assertEqual(exit_code, 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["verification"]["status"], "FAIL")
        self.assertEqual(result["verification"]["checks"], checks)
        self.assertIsNone(result["next_gate"])
        self.assertIn("harness-unit", result["blockers"][0]["message"])


if __name__ == "__main__":
    unittest.main()
