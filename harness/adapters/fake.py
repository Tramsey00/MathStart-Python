from __future__ import annotations

from harness.contracts.adapter import (
    ADAPTER_PROTOCOL_VERSION,
    AdapterCapabilities,
    AdapterIdentity,
    ErrorEvent,
    FinishedEvent,
    ModelEvent,
    ModelRequest,
    ToolRequest,
    ToolResult,
)


class FakeAdapter:
    """
    Deterministic, network-free adapter used by MS6-R04.

    Supported scenarios:

    happy
        read PRODUCT.md -> write fixture -> FINISHED

    error
        return a deterministic adapter error

    loop
        keep requesting read_file calls until Runner
        enforces max_turns

    Cancellation is simulated through cancel().
    """

    def __init__(
        self,
        scenario: str = "happy",
    ) -> None:
        if scenario not in {
            "happy",
            "error",
            "loop",
        }:
            raise ValueError(
                f"unsupported FakeAdapter scenario: {scenario}"
            )

        self._scenario = scenario
        self._step = 0
        self._cancelled = False
        self._started = False

    @property
    def identity(self) -> AdapterIdentity:
        return AdapterIdentity(
            name="fake",
            version="1",
        )

    @property
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            tool_calls=True,
            tool_call_interception=True,
            usage_reporting=True,
            cancellation=True,
            structured_output=True,
            streaming=False,
            resume=False,
        )

    def start(
        self,
        request: ModelRequest,
    ) -> ModelEvent:
        if self._started:
            return ErrorEvent(
                code="PROTOCOL_STATE",
                message=(
                    "FakeAdapter.start() may only be "
                    "called once."
                ),
            )

        self._started = True

        if (
            request.protocol_version
            != ADAPTER_PROTOCOL_VERSION
        ):
            return ErrorEvent(
                code="PROTOCOL_VERSION",
                message=(
                    "Unsupported adapter protocol version: "
                    f"{request.protocol_version}"
                ),
            )

        return self._next_event()

    def continue_with_tool_result(
        self,
        result: ToolResult,
    ) -> ModelEvent:
        if not self._started:
            return ErrorEvent(
                code="PROTOCOL_STATE",
                message=(
                    "FakeAdapter.start() must be called "
                    "before tool results are supplied."
                ),
            )

        if self._cancelled:
            return self._cancelled_event()

        if self._scenario == "happy":
            if self._step == 1:
                if result.call_id != "call-001":
                    return ErrorEvent(
                        code="CALL_ID_MISMATCH",
                        message=(
                            "Expected tool result for "
                            "call-001."
                        ),
                    )

                if result.status != "OK":
                    return ErrorEvent(
                        code="TOOL_FAILED",
                        message=(
                            "read_file did not complete "
                            "successfully."
                        ),
                    )

            elif self._step == 2:
                if result.call_id != "call-002":
                    return ErrorEvent(
                        code="CALL_ID_MISMATCH",
                        message=(
                            "Expected tool result for "
                            "call-002."
                        ),
                    )

                if result.status != "OK":
                    return ErrorEvent(
                        code="TOOL_FAILED",
                        message=(
                            "write_fixture did not complete "
                            "successfully."
                        ),
                    )

        return self._next_event()

    def cancel(self) -> None:
        self._cancelled = True

    def _next_event(self) -> ModelEvent:
        if self._cancelled:
            return self._cancelled_event()

        if self._scenario == "error":
            self._step += 1

            return ErrorEvent(
                code="FAKE_ADAPTER_ERROR",
                message=(
                    "Deterministic FakeAdapter error."
                ),
                retryable=False,
            )

        if self._scenario == "loop":
            self._step += 1

            return ToolRequest(
                call_id=f"loop-{self._step:03d}",
                tool_name="read_file",
                arguments={
                    "path": "PRODUCT.md",
                },
            )

        self._step += 1

        if self._step == 1:
            return ToolRequest(
                call_id="call-001",
                tool_name="read_file",
                arguments={
                    "path": "PRODUCT.md",
                },
            )

        if self._step == 2:
            return ToolRequest(
                call_id="call-002",
                tool_name="write_fixture",
                arguments={
                    "path": (
                        "tests/harness/fixtures/"
                        "fake-run-output.txt"
                    ),
                    "content": (
                        "MathStart FakeAdapter fixture\n"
                    ),
                },
            )

        if self._step == 3:
            return FinishedEvent(
                summary="fixture complete",
            )

        return ErrorEvent(
            code="PROTOCOL_STATE",
            message=(
                "FakeAdapter advanced beyond the "
                "expected happy-path script."
            ),
        )

    @staticmethod
    def _cancelled_event() -> ErrorEvent:
        return ErrorEvent(
            code="ADAPTER_CANCELLED",
            message="FakeAdapter was cancelled.",
            retryable=False,
        )