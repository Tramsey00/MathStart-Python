from __future__ import annotations

import json
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUN_ID_PATTERN = re.compile(
    r"^run-[0-9]{8}T[0-9]{12}Z-[0-9a-f]{8}$"
)


@dataclass(frozen=True)
class RunWorkspace:
    run_id: str
    path: Path
    result_path: Path


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def create_run_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    suffix = secrets.token_hex(4)

    return f"run-{timestamp}-{suffix}"


def create_run_workspace(
    repo_root: Path,
) -> RunWorkspace:
    runs_root = (
        repo_root
        / "var"
        / "harness"
        / "runs"
    )

    runs_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    for _ in range(10):
        run_id = create_run_id()
        run_path = runs_root / run_id

        try:
            run_path.mkdir(
                parents=False,
                exist_ok=False,
            )
        except FileExistsError:
            continue

        return RunWorkspace(
            run_id=run_id,
            path=run_path,
            result_path=run_path / "result.json",
        )

    raise RuntimeError(
        "could not allocate a unique run ID"
    )


def validate_run_id(run_id: str) -> None:
    if RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError(
            f"invalid run ID: {run_id}"
        )


def load_run_workspace(
    repo_root: Path,
    run_id: str,
) -> RunWorkspace:
    validate_run_id(run_id)

    run_path = (
        repo_root
        / "var"
        / "harness"
        / "runs"
        / run_id
    )

    if not run_path.is_dir():
        raise FileNotFoundError(
            f"run does not exist: {run_id}"
        )

    return RunWorkspace(
        run_id=run_id,
        path=run_path,
        result_path=run_path / "result.json",
    )


def write_json(
    path: Path,
    value: dict[str, Any],
) -> None:
    temporary_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    temporary_path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary_path.replace(path)


def read_json(
    path: Path,
) -> dict[str, Any]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        value = json.load(file)

    if not isinstance(value, dict):
        raise ValueError(
            f"expected JSON object: {path}"
        )

    return value