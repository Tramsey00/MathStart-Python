from __future__ import annotations

import difflib
import fnmatch
import hashlib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from harness.contracts.adapter import (
    ToolRequest,
    ToolResult,
)


@dataclass(frozen=True)
class BasicToolExecution:
    result: ToolResult
    changed_path: str | None = None
    patch: str = ""


def _safe_repo_path(
    repo_root: Path,
    relative_path: str,
) -> Path:
    if not relative_path:
        raise ValueError("path must not be empty")

    if "\\" in relative_path:
        raise ValueError(
            "repository paths must use forward slashes"
        )

    pure_path = PurePosixPath(relative_path)

    if pure_path.is_absolute():
        raise ValueError(
            "absolute repository paths are forbidden"
        )

    if ".." in pure_path.parts:
        raise ValueError(
            "path traversal is forbidden"
        )

    if (
        len(relative_path) >= 2
        and relative_path[1] == ":"
    ):
        raise ValueError(
            "Windows absolute paths are forbidden"
        )

    candidate = (
        repo_root
        / Path(*pure_path.parts)
    ).resolve()

    resolved_root = repo_root.resolve()

    if not candidate.is_relative_to(
        resolved_root
    ):
        raise ValueError(
            "path resolves outside repository"
        )

    return candidate


def _matches_any(
    relative_path: str,
    patterns: list[str],
) -> bool:
    return any(
        fnmatch.fnmatchcase(
            relative_path,
            pattern,
        )
        for pattern in patterns
    )


def _make_patch(
    relative_path: str,
    before: str | None,
    after: str,
) -> str:
    before_lines = (
        before.splitlines(keepends=True)
        if before is not None
        else []
    )

    after_lines = after.splitlines(
        keepends=True
    )

    fromfile = (
        relative_path
        if before is not None
        else "/dev/null"
    )

    return "".join(
        difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=fromfile,
            tofile=relative_path,
        )
    )


def execute_basic_tool(
    repo_root: Path,
    manifest: dict,
    request: ToolRequest,
) -> BasicToolExecution:
    if request.tool_name == "read_file":
        return _read_file(
            repo_root,
            request,
        )

    if request.tool_name == "write_fixture":
        return _write_fixture(
            repo_root,
            manifest,
            request,
        )

    return BasicToolExecution(
        result=ToolResult(
            call_id=request.call_id,
            status="ERROR",
            output={
                "message": (
                    "unknown R04 basic tool: "
                    f"{request.tool_name}"
                )
            },
        )
    )


def _read_file(
    repo_root: Path,
    request: ToolRequest,
) -> BasicToolExecution:
    value = request.arguments.get("path")

    if not isinstance(value, str):
        return BasicToolExecution(
            result=ToolResult(
                call_id=request.call_id,
                status="ERROR",
                output={
                    "message": (
                        "read_file.path must be "
                        "a string"
                    )
                },
            )
        )

    try:
        path = _safe_repo_path(
            repo_root,
            value,
        )
    except ValueError as exc:
        return BasicToolExecution(
            result=ToolResult(
                call_id=request.call_id,
                status="DENIED",
                output={
                    "message": str(exc)
                },
            )
        )

    if not path.is_file():
        return BasicToolExecution(
            result=ToolResult(
                call_id=request.call_id,
                status="ERROR",
                output={
                    "message": (
                        f"file does not exist: {value}"
                    )
                },
            )
        )

    try:
        content = path.read_text(
            encoding="utf-8"
        )
    except (OSError, UnicodeError) as exc:
        return BasicToolExecution(
            result=ToolResult(
                call_id=request.call_id,
                status="ERROR",
                output={
                    "message": str(exc)
                },
            )
        )

    return BasicToolExecution(
        result=ToolResult(
            call_id=request.call_id,
            status="OK",
            output={
                "path": value,
                "text": content,
            },
        )
    )


def _write_fixture(
    repo_root: Path,
    manifest: dict,
    request: ToolRequest,
) -> BasicToolExecution:
    relative_path = request.arguments.get(
        "path"
    )
    content = request.arguments.get(
        "content"
    )

    if not isinstance(
        relative_path,
        str,
    ):
        return BasicToolExecution(
            result=ToolResult(
                call_id=request.call_id,
                status="ERROR",
                output={
                    "message": (
                        "write_fixture.path must "
                        "be a string"
                    )
                },
            )
        )

    if not isinstance(content, str):
        return BasicToolExecution(
            result=ToolResult(
                call_id=request.call_id,
                status="ERROR",
                output={
                    "message": (
                        "write_fixture.content must "
                        "be a string"
                    )
                },
            )
        )

    try:
        path = _safe_repo_path(
            repo_root,
            relative_path,
        )
    except ValueError as exc:
        return BasicToolExecution(
            result=ToolResult(
                call_id=request.call_id,
                status="DENIED",
                output={
                    "message": str(exc)
                },
            )
        )

    if not relative_path.startswith(
        "tests/harness/fixtures/"
    ):
        return BasicToolExecution(
            result=ToolResult(
                call_id=request.call_id,
                status="DENIED",
                output={
                    "message": (
                        "R04 write_fixture may only "
                        "write below "
                        "tests/harness/fixtures/"
                    )
                },
            )
        )

    if not _matches_any(
        relative_path,
        manifest["writable_paths"],
    ):
        return BasicToolExecution(
            result=ToolResult(
                call_id=request.call_id,
                status="DENIED",
                output={
                    "message": (
                        "path is outside task "
                        f"writable scope: "
                        f"{relative_path}"
                    )
                },
            )
        )

    if _matches_any(
        relative_path,
        manifest["protected_paths"],
    ):
        return BasicToolExecution(
            result=ToolResult(
                call_id=request.call_id,
                status="DENIED",
                output={
                    "message": (
                        "path is protected: "
                        f"{relative_path}"
                    )
                },
            )
        )

    before = None

    if path.exists():
        try:
            before = path.read_text(
                encoding="utf-8"
            )
        except (OSError, UnicodeError) as exc:
            return BasicToolExecution(
                result=ToolResult(
                    call_id=request.call_id,
                    status="ERROR",
                    output={
                        "message": str(exc)
                    },
                )
            )

    try:
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content,
            encoding="utf-8",
        )
    except OSError as exc:
        return BasicToolExecution(
            result=ToolResult(
                call_id=request.call_id,
                status="ERROR",
                output={
                    "message": str(exc)
                },
            )
        )

    digest = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

    patch = _make_patch(
        relative_path,
        before,
        content,
    )

    return BasicToolExecution(
        result=ToolResult(
            call_id=request.call_id,
            status="OK",
            output={
                "path": relative_path,
                "digest": f"sha256:{digest}",
                "created": before is None,
            },
        ),
        changed_path=relative_path,
        patch=patch,
    )