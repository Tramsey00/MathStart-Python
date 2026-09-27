from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Callable

from harness.adapters.base import ModelAdapter
from harness.adapters.fake import FakeAdapter
from harness.contracts.adapter import (
    ADAPTER_PROTOCOL_VERSION,
    ErrorEvent,
    FinishedEvent,
    MessageEvent,
    ModelEvent,
    ModelRequest,
    ToolRequest,
)
from harness.contracts.result import (
    validate_run_result,
)
from harness.runner.lifecycle import (
    create_run_workspace,
    utc_now,
    write_json,
)
from harness.runner.repository import (
    current_branch,
    head_sha,
    staged_diff,
    working_tree_diff,
    working_tree_status,
)
from harness.runner.verification import run_required_checks
from harness.tools.basic import (
    execute_basic_tool,
)


def _write_text_artifact(
    run_path: Path,
    filename: str,
    content: str,
) -> tuple[str, str]:
    path = run_path / filename

    path.write_text(
        content,
        encoding="utf-8",
    )

    digest = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

    return (
        filename,
        f"sha256:{digest}",
    )


def _write_json_artifact(
    run_path: Path,
    filename: str,
    value: Any,
) -> tuple[str, str]:
    path = run_path / filename

    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    digest = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

    return (
        filename,
        f"sha256:{digest}",
    )


def _capabilities_dict(
    adapter: ModelAdapter,
) -> dict[str, bool]:
    capabilities = adapter.capabilities

    return {
        "tool_calls": (
            capabilities.tool_calls
        ),
        "tool_call_interception": (
            capabilities.tool_call_interception
        ),
        "usage_reporting": (
            capabilities.usage_reporting
        ),
        "cancellation": (
            capabilities.cancellation
        ),
        "structured_output": (
            capabilities.structured_output
        ),
        "streaming": (
            capabilities.streaming
        ),
        "resume": (
            capabilities.resume
        ),
    }


class _BudgetExceeded(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def execute_bootstrap_run(
    repo_root: Path,
    manifest: dict[str, Any],
    adapter: ModelAdapter | None = None,
) -> tuple[dict[str, Any], int]:
    started_perf = time.monotonic()
    started_at = utc_now()
    workspace = create_run_workspace(repo_root)
    if adapter is None:
        adapter = FakeAdapter(scenario="happy")

    artifacts: list[dict[str, str]] = []
    check_artifacts: list[dict[str, str]] = []
    verification_checks: list[dict[str, object]] = []
    events: list[dict[str, Any]] = []
    patches: list[str] = []
    turns_used = 0
    verification_started = False
    deadline = started_perf + manifest["limits"]["wall_time_seconds"]

    def require_wall_time() -> None:
        if time.monotonic() >= deadline:
            raise _BudgetExceeded(
                "WALL_TIME_EXCEEDED", "Run wall-time limit was exhausted.",
            )

    def model_step(invoke: Callable[[], ModelEvent]) -> ModelEvent:
        nonlocal turns_used
        require_wall_time()
        if turns_used >= manifest["limits"]["max_turns"]:
            raise _BudgetExceeded(
                "MODEL_LIMIT_EXCEEDED", "Next model step would exceed max_turns.",
            )
        turns_used += 1
        event = invoke()
        # A blocking adapter call is not preempted. Its returned event must
        # never trigger another action once the shared deadline has expired.
        require_wall_time()
        return event

    def request(messages: tuple[dict[str, Any], ...] = ()) -> ModelRequest:
        return ModelRequest(
            run_id=workspace.run_id, task_id=manifest["task_id"],
            turn=turns_used, messages=messages,
        )

    def finish(status: str, exit_code: int, blockers: list[dict[str, str]],
               verification_status: str = "NOT_RUN",
               next_gate: str | None = None) -> tuple[dict[str, Any], int]:
        for artifact in check_artifacts:
            if artifact not in artifacts:
                artifacts.append(artifact)
        return _finish_run(
            repo_root=repo_root, manifest=manifest, workspace=workspace,
            started_at=started_at, started_perf=started_perf, adapter=adapter,
            artifacts=artifacts, turns_used=turns_used, status=status,
            blockers=blockers, final_patch="".join(patches), events=events,
            verification_status=verification_status,
            verification_checks=verification_checks, next_gate=next_gate,
            exit_code=exit_code,
        )

    try:
        initial_status = working_tree_status(
            repo_root
        )
        initial_diff = working_tree_diff(
            repo_root
        )
        initial_staged_diff = staged_diff(
            repo_root
        )

        status_ref, status_digest = (
            _write_text_artifact(
                workspace.path,
                "initial-status.txt",
                initial_status + (
                    "\n"
                    if initial_status
                    else ""
                ),
            )
        )

        artifacts.append(
            {
                "kind": "git-status",
                "path": status_ref,
                "digest": status_digest,
            }
        )

        diff_ref, diff_digest = (
            _write_text_artifact(
                workspace.path,
                "initial-diff.patch",
                initial_diff,
            )
        )

        artifacts.append(
            {
                "kind": "initial-diff",
                "path": diff_ref,
                "digest": diff_digest,
            }
        )

        staged_ref, staged_digest = (
            _write_text_artifact(
                workspace.path,
                "initial-staged-diff.patch",
                initial_staged_diff,
            )
        )

        artifacts.append(
            {
                "kind": "initial-staged-diff",
                "path": staged_ref,
                "digest": staged_digest,
            }
        )

        if adapter.identity.protocol_version != ADAPTER_PROTOCOL_VERSION:
            return finish("BLOCKED_CONFIGURATION", 2, [{
                "code": "ADAPTER_PROTOCOL_VERSION_UNSUPPORTED",
                "message": (
                    "Unsupported adapter protocol version: "
                    f"{adapter.identity.protocol_version}"
                ),
            }])

        capabilities = _capabilities_dict(adapter)
        if not (capabilities["tool_calls"] and capabilities["tool_call_interception"]):
            return finish("BLOCKED_CONFIGURATION", 2, [{
                "code": "ADAPTER_INTERCEPTION_REQUIRED",
                "message": "Configured adapter cannot intercept tool calls.",
            }])

        event = model_step(lambda: adapter.start(request()))
        while True:
            events.append({"turn": turns_used, "type": event.type})
            if isinstance(event, ToolRequest):
                require_wall_time()
                execution = execute_basic_tool(repo_root, manifest, event)
                events[-1].update({
                    "call_id": event.call_id, "tool_name": event.tool_name,
                    "tool_status": execution.result.status,
                })
                if execution.patch:
                    patches.append(execution.patch)
                require_wall_time()
                if execution.result.status != "OK":
                    return finish("FAIL", 1, [{
                        "code": "TOOL_EXECUTION_FAILED",
                        "message": f"{event.tool_name}: {execution.result.output}",
                    }])
                event = model_step(
                    lambda: adapter.continue_with_tool_result(execution.result)
                )
                continue

            if isinstance(event, MessageEvent):
                events[-1]["content"] = event.content
                messages = ({"role": "assistant", "content": event.content},)
                event = model_step(lambda: adapter.continue_after_message(request(messages)))
                continue

            if isinstance(event, FinishedEvent):
                events[-1]["summary"] = event.summary
                require_wall_time()
                verification_started = True
                verification = run_required_checks(
                    repo_root, workspace.path, manifest["required_checks"],
                    deadline=deadline, checks_out=verification_checks,
                    artifacts_out=check_artifacts,
                )
                verification_checks = verification.checks
                check_artifacts = verification.artifacts
                require_wall_time()
                if verification.budget_exceeded:
                    raise _BudgetExceeded(
                        "WALL_TIME_EXCEEDED",
                        "Run wall-time limit was exhausted during verification.",
                    )
                checks_complete = [check["id"] for check in verification.checks] == manifest["required_checks"]
                verification_passed = verification.status == "PASS" and checks_complete
                blockers = [{
                    "code": "REQUIRED_CHECK_FAILED",
                    "message": f"Required check failed: {check['id']}",
                } for check in verification.checks if check["status"] == "FAIL"]
                if not checks_complete:
                    blockers.append({
                        "code": "REQUIRED_CHECKS_INCOMPLETE",
                        "message": "Verification did not record every required check.",
                    })
                require_wall_time()
                return finish(
                    "READY_FOR_REVIEW" if verification_passed else "FAIL",
                    0 if verification_passed else 1, blockers,
                    "PASS" if verification_passed else "FAIL",
                    "HUMAN_REVIEW" if verification_passed else None,
                )

            if isinstance(event, ErrorEvent):
                events[-1].update({"code": event.code, "retryable": event.retryable})
                interrupted = event.code == "ADAPTER_CANCELLED"
                return finish("INTERRUPTED" if interrupted else "FAIL",
                              4 if interrupted else 1,
                              [{"code": event.code, "message": event.message}])

            return finish("FAIL", 1, [{
                "code": "UNKNOWN_ADAPTER_EVENT",
                "message": "Adapter returned an unsupported event.",
            }])
    except _BudgetExceeded as exc:
        return finish("BUDGET_EXCEEDED", 4,
                      [{"code": exc.code, "message": exc.message}],
                      "FAIL" if verification_started else "NOT_RUN")
    except KeyboardInterrupt:
        return finish("INTERRUPTED", 4, [{
            "code": "KEYBOARD_INTERRUPT", "message": "Run was interrupted by the user.",
        }], "FAIL" if verification_started else "NOT_RUN")


def _finish_run(
    *,
    repo_root: Path,
    manifest: dict[str, Any],
    workspace: Any,
    started_at: str,
    started_perf: float,
    adapter: ModelAdapter,
    artifacts: list[dict[str, str]],
    turns_used: int,
    status: str,
    blockers: list[dict[str, str]],
    final_patch: str,
    events: list[dict[str, Any]],
    verification_status: str,
    exit_code: int,
    verification_checks: list[dict[str, object]] | None = None,
    next_gate: str | None = None,
) -> tuple[dict[str, Any], int]:
    final_status = working_tree_status(
        repo_root
    )

    final_status_ref, final_status_digest = (
        _write_text_artifact(
            workspace.path,
            "final-status.txt",
            final_status + (
                "\n"
                if final_status
                else ""
            ),
        )
    )

    artifacts.append(
        {
            "kind": "final-git-status",
            "path": final_status_ref,
            "digest": final_status_digest,
        }
    )

    final_diff_ref, final_diff_digest = (
        _write_text_artifact(
            workspace.path,
            "final-diff.patch",
            final_patch,
        )
    )

    artifacts.append(
        {
            "kind": "final-diff",
            "path": final_diff_ref,
            "digest": final_diff_digest,
        }
    )

    events_ref, events_digest = (
        _write_json_artifact(
            workspace.path,
            "events.json",
            events,
        )
    )

    artifacts.append(
        {
            "kind": "protocol-events",
            "path": events_ref,
            "digest": events_digest,
        }
    )

    finished_at = utc_now()

    wall_time_ms = int(
        (
            time.monotonic()
            - started_perf
        )
        * 1000
    )

    wall_time_limit_ms = manifest["limits"]["wall_time_seconds"] * 1000
    if (
        verification_status != "NOT_RUN"
        and status in {"READY_FOR_REVIEW", "FAIL"}
        and wall_time_ms >= wall_time_limit_ms
    ):
        status = "BUDGET_EXCEEDED"
        exit_code = 4
        verification_status = "FAIL"
        next_gate = None
        if not any(blocker["code"] == "WALL_TIME_EXCEEDED" for blocker in blockers):
            blockers = [*blockers, {
                "code": "WALL_TIME_EXCEEDED",
                "message": "Run wall-time limit was exhausted during verification.",
            }]

    result: dict[str, Any] = {
        "schema_version": (
            "harness-result-v1"
        ),
        "run_id": workspace.run_id,
        "parent_run_id": None,
        "task_id": manifest["task_id"],
        "repository": {
            "base_sha": (
                manifest["base_sha"]
            ),
            "head_sha": head_sha(
                repo_root
            ),
            "branch": current_branch(
                repo_root
            ),
        },
        "status": status,
        "adapter": {
            "name": (
                adapter.identity.name
            ),
            "version": (
                adapter.identity.version
            ),
        },
        "execution": {
            "started_at": started_at,
            "finished_at": finished_at,
            "turns_used": turns_used,
            "wall_time_ms": wall_time_ms,
        },
        "diff": {
            "initial_ref": (
                "initial-diff.patch"
            ),
            "final_ref": final_diff_ref,
        },
        "artifacts": artifacts,
        "verification": {
            "status": (
                verification_status
            ),
            "checks": verification_checks if verification_checks is not None else [],
        },
        "budget": {
            "turns_used": turns_used,
            "turns_limit": manifest[
                "limits"
            ]["max_turns"],
            "wall_time_ms": wall_time_ms,
            "wall_time_limit_ms": (
                manifest["limits"][
                    "wall_time_seconds"
                ]
                * 1000
            ),
        },
        "blockers": blockers,
        "next_gate": next_gate,
    }

    final_wall_ms = int((time.monotonic() - started_perf) * 1000)
    result["execution"]["wall_time_ms"] = final_wall_ms
    result["budget"]["wall_time_ms"] = final_wall_ms

    def downgrade_expired_ready() -> bool:
        nonlocal exit_code
        if result["status"] != "READY_FOR_REVIEW":
            return False
        now = time.monotonic()
        if now < started_perf + manifest["limits"]["wall_time_seconds"]:
            return False
        final_wall_ms = int((now - started_perf) * 1000)
        result["execution"]["wall_time_ms"] = final_wall_ms
        result["budget"]["wall_time_ms"] = final_wall_ms
        result["status"] = "BUDGET_EXCEEDED"
        result["verification"]["status"] = "FAIL"
        result["next_gate"] = None
        if not any(blocker["code"] == "WALL_TIME_EXCEEDED" for blocker in result["blockers"]):
            result["blockers"].append({
                "code": "WALL_TIME_EXCEEDED",
                "message": "Run wall-time limit was exhausted during finalization.",
            })
        exit_code = 4
        return True

    downgrade_expired_ready()
    validate_run_result(repo_root, result)
    # Validation may consume the remaining budget. Validate any resulting
    # downgrade again so the persisted object has no unvalidated mutations.
    if downgrade_expired_ready():
        validate_run_result(repo_root, result)

    if result["status"] == "READY_FOR_REVIEW":
        staged_path = workspace.result_path.with_name("result.staged.json")
        write_json(staged_path, result)
        # The potentially slow write must finish before checking whether READY
        # may be published to the canonical result path.
        if downgrade_expired_ready():
            staged_path.unlink()
            validate_run_result(repo_root, result)
            write_json(workspace.result_path, result)
        else:
            staged_path.replace(workspace.result_path)
    else:
        write_json(workspace.result_path, result)

    return result, exit_code