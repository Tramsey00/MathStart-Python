from __future__ import annotations

from pathlib import Path

from harness.contracts.result import (
    RunResultValidationError,
    load_and_validate_run_result,
)
from harness.runner.lifecycle import (
    load_run_workspace,
)
from harness.runner.repository import (
    RepositoryError,
    repository_root,
)


STATUS_EXIT_CODES = {
    "READY_FOR_REVIEW": 0,
    "FAIL": 1,
    "BLOCKED_CONFIGURATION": 2,
    "NEEDS_HUMAN": 3,
    "INTERRUPTED": 4,
    "BUDGET_EXCEEDED": 4,
}


def status_command(
    run_id: str,
) -> int:
    try:
        repo_root = repository_root(
            Path.cwd()
        )

        workspace = load_run_workspace(
            repo_root,
            run_id,
        )

        result = load_and_validate_run_result(
            repo_root,
            workspace.result_path,
        )

    except (
        RepositoryError,
        RunResultValidationError,
        FileNotFoundError,
        ValueError,
    ) as exc:
        print("Status: BLOCKED_CONFIGURATION")

        if isinstance(
            exc,
            RunResultValidationError,
        ):
            for error in exc.errors:
                print(f"- {error}")
        else:
            print(f"- {exc}")

        return 2

    print("MathStart Harness Run Status")
    print()

    print(
        f"Run ID:            "
        f"{result['run_id']}"
    )

    parent_run_id = (
        result["parent_run_id"]
        if result["parent_run_id"] is not None
        else "-"
    )

    print(
        f"Parent Run ID:     "
        f"{parent_run_id}"
    )

    print(
        f"Task:              "
        f"{result['task_id']}"
    )

    print(
        f"Status:            "
        f"{result['status']}"
    )

    print(
        f"Base SHA:          "
        f"{result['repository']['base_sha']}"
    )

    print(
        f"Head SHA:          "
        f"{result['repository']['head_sha']}"
    )

    print(
        f"Branch:            "
        f"{result['repository']['branch']}"
    )

    adapter = result["adapter"]

    if adapter is None:
        adapter_text = "-"
    else:
        adapter_text = (
            f"{adapter['name']}@"
            f"{adapter['version']}"
        )

    print(
        f"Adapter:           "
        f"{adapter_text}"
    )

    print(
        f"Turns:             "
        f"{result['execution']['turns_used']}/"
        f"{result['budget']['turns_limit']}"
    )

    print(
        f"Verification:      "
        f"{result['verification']['status']}"
    )

    print(
        f"Artifacts:         "
        f"{len(result['artifacts'])}"
    )

    print(
        f"Blockers:          "
        f"{len(result['blockers'])}"
    )

    next_gate = (
        result["next_gate"]
        if result["next_gate"] is not None
        else "-"
    )

    print(
        f"Next gate:         "
        f"{next_gate}"
    )

    return STATUS_EXIT_CODES[
        result["status"]
    ]