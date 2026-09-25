from __future__ import annotations

from typing import Protocol, runtime_checkable

from harness.contracts.adapter import (
    AdapterCapabilities,
    AdapterIdentity,
    ModelEvent,
    ModelRequest,
    ToolResult,
)


@runtime_checkable
class ModelAdapter(Protocol):
    @property
    def identity(self) -> AdapterIdentity:
        ...

    @property
    def capabilities(self) -> AdapterCapabilities:
        ...

    def start(
        self,
        request: ModelRequest,
    ) -> ModelEvent:
        ...

    def continue_with_tool_result(
        self,
        result: ToolResult,
    ) -> ModelEvent:
        ...

    def cancel(self) -> None:
        ...