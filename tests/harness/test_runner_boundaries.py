from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from harness.adapters.fake import FakeAdapter
from harness.contracts.adapter import FinishedEvent, MessageEvent, ToolRequest, ToolResult
from harness.runner.engine import execute_bootstrap_run
from harness.runner.lifecycle import RunWorkspace, create_run_id
from harness.runner.verification import VerificationOutcome
from harness.tools.basic import BasicToolExecution
from tests.harness.adapter_fixtures import ScriptedAdapter, UnsupportedProtocolAdapter
from tests.harness.test_cli import VALID_MANIFEST

ROOT = Path(__file__).resolve().parents[2]
TOOL = ToolRequest("test-tool", "read_file", {"path": "PRODUCT.md"})
FINISHED = FinishedEvent("fixture done")


class RunnerBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        path = Path(self.temp.name)
        self.workspace = RunWorkspace(create_run_id(), path, path / "result.json")
        self.now = 0.0
        self.manifest = {**VALID_MANIFEST, "limits": {
            **VALID_MANIFEST["limits"], "wall_time_seconds": 1,
        }}
        self.checks = [{"id": key, "status": "PASS", "exit_code": 0}
                       for key in VALID_MANIFEST["required_checks"]]

    def tearDown(self) -> None:
        self.temp.cleanup()

    def expire(self, *args) -> None:
        self.now = 2.0

    def tool(self, root, manifest, request):
        return BasicToolExecution(ToolResult(request.call_id, "OK", {}))

    def execute(self, adapter, *, tool=None, verify=None, clock=None, initial_status=None):
        with (
            patch("harness.runner.engine.create_run_workspace", return_value=self.workspace),
            patch("harness.runner.engine.working_tree_status", side_effect=initial_status or (lambda root: "")),
            patch("harness.runner.engine.working_tree_diff", return_value=""),
            patch("harness.runner.engine.staged_diff", return_value=""),
            patch("harness.runner.engine.head_sha", return_value="b" * 40),
            patch("harness.runner.engine.current_branch", return_value="test-branch"),
            patch("harness.runner.engine.time.monotonic", side_effect=clock or (lambda: self.now)),
            patch("harness.runner.engine.execute_basic_tool", side_effect=tool or self.tool) as handler,
            patch("harness.runner.engine.run_required_checks", side_effect=verify,
                  return_value=VerificationOutcome(self.checks, [])) as verifier,
        ):
            result, code = execute_bootstrap_run(ROOT, self.manifest, adapter)
        persisted = json.loads(self.workspace.result_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted, result)
        return result, code, handler, verifier

    def assert_budget(self, result, code):
        self.assertEqual((result["status"], code), ("BUDGET_EXCEEDED", 4))
        self.assertNotEqual(result["verification"]["status"], "PASS")
        self.assertIsNone(result["next_gate"])

    def test_expired_before_initial_model_prevents_start(self) -> None:
        adapter = ScriptedAdapter([TOOL])
        def status(root):
            self.expire()
            return ""
        result, code, tool, verify = self.execute(adapter, initial_status=status)
        self.assert_budget(result, code)
        adapter.start.assert_not_called()
        tool.assert_not_called()
        verify.assert_not_called()

    def test_tool_request_returned_after_deadline_never_executes(self) -> None:
        adapter = ScriptedAdapter([TOOL], self.expire)
        result, code, tool, verify = self.execute(adapter)
        self.assert_budget(result, code)
        tool.assert_not_called()
        verify.assert_not_called()
        adapter.continue_with_tool_result.assert_not_called()

    def test_finished_returned_after_deadline_never_verifies(self) -> None:
        result, code, tool, verify = self.execute(ScriptedAdapter([FINISHED], self.expire))
        self.assert_budget(result, code)
        self.assertEqual(result["verification"]["status"], "NOT_RUN")
        tool.assert_not_called()
        verify.assert_not_called()

    def test_expired_immediately_before_handler_prevents_tool(self) -> None:
        calls = iter([0.0, 0.0, 0.0])  # start time, before model, after model
        result, code, tool, verify = self.execute(
            ScriptedAdapter([TOOL]), clock=lambda: next(calls, 2.0),
        )
        self.assert_budget(result, code)
        tool.assert_not_called()
        verify.assert_not_called()

    def test_expired_after_handler_prevents_next_model(self) -> None:
        adapter = ScriptedAdapter([TOOL, FINISHED])
        def expired_tool(*args):
            execution = self.tool(*args)
            self.expire()
            return execution
        result, code, tool, verify = self.execute(adapter, tool=expired_tool)
        self.assert_budget(result, code)
        self.assertEqual(tool.call_count, 1)
        adapter.continue_with_tool_result.assert_not_called()
        verify.assert_not_called()

    def test_late_tool_continuation_never_executes_next_tool(self) -> None:
        adapter = ScriptedAdapter([TOOL, TOOL], lambda step: self.expire() if step == 2 else None)
        result, code, tool, verify = self.execute(adapter)
        self.assert_budget(result, code)
        self.assertEqual(tool.call_count, 1)
        self.assertEqual(adapter.continue_with_tool_result.call_count, 1)
        verify.assert_not_called()

    def test_late_finished_continuation_never_verifies(self) -> None:
        adapter = ScriptedAdapter([TOOL, FINISHED], lambda step: self.expire() if step == 2 else None)
        result, code, tool, verify = self.execute(adapter)
        self.assert_budget(result, code)
        verify.assert_not_called()

    def test_expired_immediately_before_verification_prevents_it(self) -> None:
        calls = iter([0.0, 0.0, 0.0])
        result, code, tool, verify = self.execute(
            ScriptedAdapter([FINISHED]), clock=lambda: next(calls, 2.0),
        )
        self.assert_budget(result, code)
        verify.assert_not_called()

    def test_verification_overrun_cannot_return_ready(self) -> None:
        def expired_verify(*args, **kwargs):
            self.expire()
            return VerificationOutcome(self.checks, [])
        result, code, tool, verify = self.execute(ScriptedAdapter([FINISHED]), verify=expired_verify)
        self.assert_budget(result, code)
        self.assertEqual(result["verification"]["checks"], self.checks)
        self.assertEqual(verify.call_args.kwargs["deadline"], 1.0)

    def test_expiry_during_result_validation_cannot_publish_ready(self) -> None:
        from harness.contracts.result import validate_run_result
        def validate(root, result):
            validate_run_result(root, result)
            self.expire()
        with patch("harness.runner.engine.validate_run_result", side_effect=validate):
            result, code, tool, verify = self.execute(ScriptedAdapter([FINISHED]))
        self.assert_budget(result, code)

    def test_expiry_during_result_persistence_cannot_publish_ready(self) -> None:
        from harness.runner.lifecycle import write_json
        persisted_paths = []
        canonical_statuses = []
        replace_path = Path.replace

        def publish(source, destination):
            published = replace_path(source, destination)
            if destination == self.workspace.result_path:
                canonical = json.loads(destination.read_text(encoding="utf-8"))
                self.assertNotEqual(canonical["status"], "READY_FOR_REVIEW")
                canonical_statuses.append(canonical["status"])
            return published

        def persist(path, result):
            if not persisted_paths:
                self.assertEqual(self.manifest["limits"]["wall_time_seconds"], 1)
                self.assertEqual(self.now, 0.0)
                self.assertEqual(result["status"], "READY_FOR_REVIEW")
                self.assertFalse(self.workspace.result_path.exists())
                self.expire()
            write_json(path, result)
            persisted_paths.append(path)
            if self.workspace.result_path.exists():
                canonical = json.loads(self.workspace.result_path.read_text(encoding="utf-8"))
                self.assertNotEqual(canonical["status"], "READY_FOR_REVIEW")
            else:
                self.assertNotEqual(path, self.workspace.result_path)

        with (
            patch("harness.runner.engine.write_json", side_effect=persist) as write,
            patch.object(Path, "replace", autospec=True, side_effect=publish),
        ):
            result, code, tool, verify = self.execute(ScriptedAdapter([FINISHED]))
        self.assert_budget(result, code)
        self.assertEqual(sum(blocker["code"] == "WALL_TIME_EXCEEDED"
                             for blocker in result["blockers"]), 1)
        self.assertEqual(write.call_count, 2)
        self.assertNotEqual(persisted_paths[0], self.workspace.result_path)
        self.assertEqual(persisted_paths[0].parent, self.workspace.path)
        self.assertEqual(persisted_paths[1], self.workspace.result_path)
        self.assertEqual(canonical_statuses, ["BUDGET_EXCEEDED"])
        limit_ms = result["budget"]["wall_time_limit_ms"]
        self.assertGreaterEqual(result["execution"]["wall_time_ms"], limit_ms)
        self.assertGreaterEqual(result["budget"]["wall_time_ms"], limit_ms)
        persisted_text = self.workspace.result_path.read_text(encoding="utf-8")
        self.assertEqual(json.loads(persisted_text), result)
        self.assertNotIn("READY_FOR_REVIEW", persisted_text)

    def test_expiry_during_final_result_replace_cannot_return_ready(self) -> None:
        staged_path = self.workspace.result_path.with_name("result.staged.json")
        replace_path = Path.replace
        final_replaces = []

        def delayed_replace(source, destination):
            if source == staged_path and destination == self.workspace.result_path:
                self.assertEqual(self.manifest["limits"]["wall_time_seconds"], 1)
                self.assertEqual(self.now, 0.0)
                self.assertFalse(destination.exists())
                self.assertEqual(json.loads(source.read_text(encoding="utf-8"))["status"],
                                 "READY_FOR_REVIEW")
                published = replace_path(source, destination)
                self.expire()
                final_replaces.append(destination)
                return published
            return replace_path(source, destination)

        with patch.object(Path, "replace", autospec=True, side_effect=delayed_replace):
            result, code, tool, verify = self.execute(ScriptedAdapter([FINISHED]))
        self.assertEqual(final_replaces, [self.workspace.result_path])
        self.assert_budget(result, code)
        self.assertEqual(result["verification"]["status"], "FAIL")
        self.assertEqual(sum(blocker["code"] == "WALL_TIME_EXCEEDED"
                             for blocker in result["blockers"]), 1)
        self.assertEqual(result["execution"]["wall_time_ms"], 2000)
        self.assertEqual(result["budget"]["wall_time_ms"], 2000)
        self.assertGreaterEqual(result["execution"]["wall_time_ms"],
                                result["budget"]["wall_time_limit_ms"])
        self.assertFalse(staged_path.exists())
        persisted_text = self.workspace.result_path.read_text(encoding="utf-8")
        self.assertEqual(json.loads(persisted_text), result)
        self.assertNotIn("READY_FOR_REVIEW", persisted_text)

    def test_unsupported_protocol_blocked_before_any_invocation(self) -> None:
        adapter = UnsupportedProtocolAdapter()
        adapter.start = Mock()
        result, code, tool, verify = self.execute(adapter)
        self.assertEqual((result["status"], code), ("BLOCKED_CONFIGURATION", 2))
        self.assertEqual(result["blockers"][0]["code"], "ADAPTER_PROTOCOL_VERSION_UNSUPPORTED")
        self.assertEqual(result["execution"]["turns_used"], 0)
        adapter.start.assert_not_called()
        tool.assert_not_called()
        verify.assert_not_called()

    def test_message_tool_finished_flow_preserves_content_and_verifies(self) -> None:
        result, code, tool, verify = self.execute(FakeAdapter("message"))
        self.assertEqual((result["status"], code), ("READY_FOR_REVIEW", 0))
        self.assertEqual(result["execution"]["turns_used"], 3)
        events = json.loads((self.workspace.path / "events.json").read_text(encoding="utf-8"))
        self.assertEqual([e["type"] for e in events], ["MESSAGE", "TOOL_REQUEST", "FINISHED"])
        self.assertEqual(events[0]["content"], "Deterministic intermediate message.")
        self.assertEqual(tool.call_count, 1)
        verify.assert_called_once()

    def test_message_alone_exhausts_turns_without_success(self) -> None:
        self.manifest["limits"]["max_turns"] = 2
        result, code, tool, verify = self.execute(FakeAdapter("message-loop"))
        self.assert_budget(result, code)
        self.assertEqual(result["execution"]["turns_used"], 2)
        tool.assert_not_called()
        verify.assert_not_called()

    def test_late_message_prevents_continuation(self) -> None:
        adapter = ScriptedAdapter([MessageEvent("late")], self.expire)
        result, code, tool, verify = self.execute(adapter)
        self.assert_budget(result, code)
        adapter.continue_after_message.assert_not_called()
        verify.assert_not_called()

    def test_late_message_continuation_prevents_tool(self) -> None:
        adapter = ScriptedAdapter([MessageEvent("first"), TOOL],
                                  lambda step: self.expire() if step == 2 else None)
        result, code, tool, verify = self.execute(adapter)
        self.assert_budget(result, code)
        tool.assert_not_called()
        verify.assert_not_called()
        self.assertEqual(adapter.continue_after_message.call_args.args[0].turn, 2)


if __name__ == "__main__":
    unittest.main()
