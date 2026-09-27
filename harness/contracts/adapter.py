from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


ADAPTER_PROTOCOL_VERSION = "adapter-protocol-v1"


@dataclass(frozen=True)
class AdapterIdentity:
    name: str
    version: str
    protocol_version: str = ADAPTER_PROTOCOL_VERSION


@dataclass(frozen=True)
class AdapterCapabilities:
    tool_calls: bool
    tool_call_interception: bool
    usage_reporting: bool
    cancellation: bool
    structured_output: bool
    streaming: bool
    resume: bool


@dataclass(frozen=True)
class ModelRequest:
    run_id: str
    task_id: str
    turn: int
    messages: tuple[dict[str, Any], ...] = field(
        default_factory=tuple
    )
    protocol_version: str = ADAPTER_PROTOCOL_VERSION


@dataclass(frozen=True)
class MessageEvent:
    content: str
    type: Literal["MESSAGE"] = "MESSAGE"


@dataclass(frozen=True)
class ToolRequest:
    call_id: str
    tool_name: str
    arguments: dict[str, Any]
    type: Literal["TOOL_REQUEST"] = "TOOL_REQUEST"


@dataclass(frozen=True)
class FinishedEvent:
    summary: str
    type: Literal["FINISHED"] = "FINISHED"


@dataclass(frozen=True)
class ErrorEvent:
    code: str
    message: str
    retryable: bool = False
    type: Literal["ERROR"] = "ERROR"


ModelEvent = (
    MessageEvent
    | ToolRequest
    | FinishedEvent
    | ErrorEvent
)


ToolResultStatus = Literal[
    "OK",
    "DENIED",
    "ERROR",
]


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    status: ToolResultStatus
    output: dict[str, Any]