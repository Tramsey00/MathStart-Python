from __future__ import annotations

import unittest

from harness.adapters.base import ModelAdapter
from harness.adapters.fake import FakeAdapter
from harness.contracts.adapter import (
    FinishedEvent,
    ModelRequest,
    ToolRequest,
    ToolResult,
)


class FakeAdapterTests(unittest.TestCase):
    def test_fake_adapter_implements_protocol(self) -> None:
        adapter = FakeAdapter()

        self.assertIsInstance(
            adapter,
            ModelAdapter,
        )

    def test_happy_scenario(self) -> None:
        adapter = FakeAdapter(
            scenario="happy"
        )

        first = adapter.start(
            ModelRequest(
                run_id="run-test",
                task_id="MS6-R04",
                turn=1,
            )
        )

        self.assertIsInstance(
            first,
            ToolRequest,
        )
        self.assertEqual(
            first.call_id,
            "call-001",
        )
        self.assertEqual(
            first.tool_name,
            "read_file",
        )

        second = (
            adapter.continue_with_tool_result(
                ToolResult(
                    call_id="call-001",
                    status="OK",
                    output={
                        "text": "PRODUCT",
                    },
                )
            )
        )

        self.assertIsInstance(
            second,
            ToolRequest,
        )
        self.assertEqual(
            second.call_id,
            "call-002",
        )
        self.assertEqual(
            second.tool_name,
            "write_fixture",
        )

        third = (
            adapter.continue_with_tool_result(
                ToolResult(
                    call_id="call-002",
                    status="OK",
                    output={
                        "path": (
                            "tests/harness/fixtures/"
                            "fake-run-output.txt"
                        ),
                    },
                )
            )
        )

        self.assertIsInstance(
            third,
            FinishedEvent,
        )
        self.assertEqual(
            third.summary,
            "fixture complete",
        )

    def test_error_scenario(self) -> None:
        adapter = FakeAdapter(
            scenario="error"
        )

        event = adapter.start(
            ModelRequest(
                run_id="run-test",
                task_id="MS6-R04",
                turn=1,
            )
        )

        self.assertEqual(
            event.type,
            "ERROR",
        )
        self.assertEqual(
            event.code,
            "FAKE_ADAPTER_ERROR",
        )

    def test_cancelled_adapter_never_finishes(self) -> None:
        adapter = FakeAdapter()

        adapter.cancel()

        event = adapter.start(
            ModelRequest(
                run_id="run-test",
                task_id="MS6-R04",
                turn=1,
            )
        )

        self.assertEqual(
            event.type,
            "ERROR",
        )
        self.assertEqual(
            event.code,
            "ADAPTER_CANCELLED",
        )

    def test_loop_scenario_keeps_requesting_tools(self) -> None:
        adapter = FakeAdapter(
            scenario="loop"
        )

        first = adapter.start(
            ModelRequest(
                run_id="run-test",
                task_id="MS6-R04",
                turn=1,
            )
        )

        self.assertIsInstance(
            first,
            ToolRequest,
        )

        second = (
            adapter.continue_with_tool_result(
                ToolResult(
                    call_id=first.call_id,
                    status="OK",
                    output={
                        "text": "PRODUCT",
                    },
                )
            )
        )

        self.assertIsInstance(
            second,
            ToolRequest,
        )
        self.assertNotEqual(
            first.call_id,
            second.call_id,
        )


if __name__ == "__main__":
    unittest.main()