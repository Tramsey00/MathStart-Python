from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from harness.adapters.base import ModelAdapter
from harness.adapters.fake import FakeAdapter
from harness.contracts.adapter import (
    ErrorEvent,
    FinishedEvent,
    MessageEvent,
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


def execute_bootstrap_run(
    repo_root: Path,
    manifest: dict[str, Any],
    adapter: ModelAdapter | None = None,
) -> tuple[dict[str, Any], int]:
    started_perf = time.monotonic()
    started_at = utc_now()

    workspace = create_run_workspace(
        repo_root
    )

    if adapter is None:
        adapter = FakeAdapter(scenario="happy")

    artifacts: list[dict[str, str]] = []
    check_artifacts: list[dict[str, str]] = []
    verification_checks: list[dict[str, object]] = []
    events: list[dict[str, Any]] = []
    patches: list[str] = []
    turns_used = 0

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

        capabilities = _capabilities_dict(
            adapter
        )

        if not (
            capabilities["tool_calls"]
            and capabilities[
                "tool_call_interception"
            ]
        ):
            return _finish_run(
                repo_root=repo_root,
                manifest=manifest,
                workspace=workspace,
                started_at=started_at,
                started_perf=started_perf,
                adapter=adapter,
                artifacts=artifacts,
                turns_used=0,
                status="BLOCKED_CONFIGURATION",
                blockers=[
                    {
                        "code": (
                            "ADAPTER_INTERCEPTION_REQUIRED"
                        ),
                        "message": (
                            "Configured adapter cannot "
                            "intercept tool calls."
                        ),
                    }
                ],
                final_patch="",
                events=[],
                verification_status="NOT_RUN",
                exit_code=2,
            )

        max_turns = manifest["limits"][
            "max_turns"
        ]

        wall_limit_seconds = manifest[
            "limits"
        ]["wall_time_seconds"]

        def wall_time_exceeded() -> bool:
            return (
                time.monotonic()
                - started_perf
                >= wall_limit_seconds
            )

        def before_model_step() -> (
            tuple[str, int] | None
        ):
            nonlocal turns_used

            if wall_time_exceeded():
                return (
                    "BUDGET_EXCEEDED",
                    4,
                )

            if turns_used >= max_turns:
                return (
                    "BUDGET_EXCEEDED",
                    4,
                )

            turns_used += 1
            return None

        limit_result = before_model_step()

        if limit_result is not None:
            status, exit_code = limit_result

            return _finish_run(
                repo_root=repo_root,
                manifest=manifest,
                workspace=workspace,
                started_at=started_at,
                started_perf=started_perf,
                adapter=adapter,
                artifacts=artifacts,
                turns_used=turns_used,
                status=status,
                blockers=[
                    {
                        "code": "MODEL_LIMIT_EXCEEDED",
                        "message": (
                            "Model step could not start "
                            "within configured limits."
                        ),
                    }
                ],
                final_patch="",
                events=events,
                verification_status="NOT_RUN",
                exit_code=exit_code,
            )

        event = adapter.start(
            ModelRequest(
                run_id=workspace.run_id,
                task_id=manifest["task_id"],
                turn=turns_used,
            )
        )

        while True:
            events.append(
                {
                    "turn": turns_used,
                    "type": event.type,
                }
            )

            if isinstance(
                event,
                ToolRequest,
            ):
                execution = execute_basic_tool(
                    repo_root,
                    manifest,
                    event,
                )

                events[-1].update(
                    {
                        "call_id": event.call_id,
                        "tool_name": event.tool_name,
                        "tool_status": (
                            execution.result.status
                        ),
                    }
                )

                if execution.patch:
                    patches.append(
                        execution.patch
                    )

                if (
                    execution.result.status
                    != "OK"
                ):
                    return _finish_run(
                        repo_root=repo_root,
                        manifest=manifest,
                        workspace=workspace,
                        started_at=started_at,
                        started_perf=started_perf,
                        adapter=adapter,
                        artifacts=artifacts,
                        turns_used=turns_used,
                        status="FAIL",
                        blockers=[
                            {
                                "code": (
                                    "TOOL_EXECUTION_FAILED"
                                ),
                                "message": (
                                    f"{event.tool_name}: "
                                    f"{execution.result.output}"
                                ),
                            }
                        ],
                        final_patch="".join(
                            patches
                        ),
                        events=events,
                        verification_status=(
                            "NOT_RUN"
                        ),
                        exit_code=1,
                    )

                limit_result = (
                    before_model_step()
                )

                if limit_result is not None:
                    status, exit_code = (
                        limit_result
                    )

                    return _finish_run(
                        repo_root=repo_root,
                        manifest=manifest,
                        workspace=workspace,
                        started_at=started_at,
                        started_perf=started_perf,
                        adapter=adapter,
                        artifacts=artifacts,
                        turns_used=turns_used,
                        status=status,
                        blockers=[
                            {
                                "code": (
                                    "MODEL_LIMIT_EXCEEDED"
                                ),
                                "message": (
                                    "Next model step "
                                    "would exceed "
                                    "configured limits."
                                ),
                            }
                        ],
                        final_patch="".join(
                            patches
                        ),
                        events=events,
                        verification_status=(
                            "NOT_RUN"
                        ),
                        exit_code=exit_code,
                    )

                event = (
                    adapter
                    .continue_with_tool_result(
                        execution.result
                    )
                )
                continue

            if isinstance(
                event,
                FinishedEvent,
            ):
                events[-1]["summary"] = event.summary

                verification = run_required_checks(
                    repo_root,
                    workspace.path,
                    manifest["required_checks"],
                    deadline=started_perf + wall_limit_seconds,
                    checks_out=verification_checks,
                    artifacts_out=check_artifacts,
                )
                verification_checks = verification.checks
                artifacts.extend(verification.artifacts)
                failed_checks = [
                    check["id"] for check in verification.checks
                    if check["status"] == "FAIL"
                ]
                checks_complete = [
                    check["id"] for check in verification.checks
                ] == manifest["required_checks"]
                verification_passed = verification.status == "PASS" and checks_complete
                blockers = [
                    {
                        "code": "REQUIRED_CHECK_FAILED",
                        "message": f"Required check failed: {check_id}",
                    }
                    for check_id in failed_checks
                ]
                if not checks_complete:
                    blockers.append({
                        "code": "REQUIRED_CHECKS_INCOMPLETE",
                        "message": "Verification did not record every required check.",
                    })
                if verification.budget_exceeded:
                    blockers.append({
                        "code": "WALL_TIME_EXCEEDED",
                        "message": "Run wall-time limit was exhausted during verification.",
                    })
                final_status = (
                    "BUDGET_EXCEEDED" if verification.budget_exceeded
                    else "READY_FOR_REVIEW" if verification_passed
                    else "FAIL"
                )

                return _finish_run(
                    repo_root=repo_root,
                    manifest=manifest,
                    workspace=workspace,
                    started_at=started_at,
                    started_perf=started_perf,
                    adapter=adapter,
                    artifacts=artifacts,
                    turns_used=turns_used,
                    status=final_status,
                    blockers=blockers,
                    final_patch="".join(patches),
                    events=events,
                    verification_status="PASS" if verification_passed else "FAIL",
                    verification_checks=verification.checks,
                    next_gate="HUMAN_REVIEW" if verification_passed else None,
                    exit_code=4 if verification.budget_exceeded else 0 if verification_passed else 1,
                )

            if isinstance(
                event,
                ErrorEvent,
            ):
                events[-1].update(
                    {
                        "code": event.code,
                        "retryable": (
                            event.retryable
                        ),
                    }
                )

                status = (
                    "INTERRUPTED"
                    if event.code
                    == "ADAPTER_CANCELLED"
                    else "FAIL"
                )

                exit_code = (
                    4
                    if status == "INTERRUPTED"
                    else 1
                )

                return _finish_run(
                    repo_root=repo_root,
                    manifest=manifest,
                    workspace=workspace,
                    started_at=started_at,
                    started_perf=started_perf,
                    adapter=adapter,
                    artifacts=artifacts,
                    turns_used=turns_used,
                    status=status,
                    blockers=[
                        {
                            "code": event.code,
                            "message": event.message,
                        }
                    ],
                    final_patch="".join(
                        patches
                    ),
                    events=events,
                    verification_status=(
                        "NOT_RUN"
                    ),
                    exit_code=exit_code,
                )

            if isinstance(
                event,
                MessageEvent,
            ):
                return _finish_run(
                    repo_root=repo_root,
                    manifest=manifest,
                    workspace=workspace,
                    started_at=started_at,
                    started_perf=started_perf,
                    adapter=adapter,
                    artifacts=artifacts,
                    turns_used=turns_used,
                    status="FAIL",
                    blockers=[
                        {
                            "code": (
                                "UNSUPPORTED_MESSAGE_FLOW"
                            ),
                            "message": (
                                "R04 runner does not "
                                "support intermediate MESSAGE "
                                "events."
                            ),
                        }
                    ],
                    final_patch="".join(
                        patches
                    ),
                    events=events,
                    verification_status=(
                        "NOT_RUN"
                    ),
                    exit_code=1,
                )

            return _finish_run(
                repo_root=repo_root,
                manifest=manifest,
                workspace=workspace,
                started_at=started_at,
                started_perf=started_perf,
                adapter=adapter,
                artifacts=artifacts,
                turns_used=turns_used,
                status="FAIL",
                blockers=[
                    {
                        "code": (
                            "UNKNOWN_ADAPTER_EVENT"
                        ),
                        "message": (
                            "Adapter returned an "
                            "unsupported event."
                        ),
                    }
                ],
                final_patch="".join(
                    patches
                ),
                events=events,
                verification_status="NOT_RUN",
                exit_code=1,
            )

    except KeyboardInterrupt:
        artifacts.extend(item for item in check_artifacts if item not in artifacts)
        return _finish_run(
            repo_root=repo_root,
            manifest=manifest,
            workspace=workspace,
            started_at=started_at,
            started_perf=started_perf,
            adapter=adapter,
            artifacts=artifacts,
            turns_used=turns_used,
            status="INTERRUPTED",
            blockers=[{
                "code": "KEYBOARD_INTERRUPT",
                "message": "Run was interrupted by the user.",
            }],
            final_patch="".join(patches),
            events=events,
            verification_status="FAIL" if verification_checks else "NOT_RUN",
            verification_checks=verification_checks,
            exit_code=4,
        )


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

    validate_run_result(
        repo_root,
        result,
    )

    write_json(
        workspace.result_path,
        result,
    )

    return result, exit_code