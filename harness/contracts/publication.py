"""Local READY publication receipt, separate from the RunResult v1 schema."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any


READY_COMMIT_VERSION = "harness-ready-commit-v1"


def ready_commit_path(result_path: Path) -> Path:
    return result_path.with_name("result.ready-commit.json")


def validate_ready_commit(receipt: Any, run_id: str, canonical_bytes: bytes) -> None:
    if not isinstance(receipt, dict):
        raise ValueError("commit receipt must be a JSON object")
    if receipt.get("schema_version") != READY_COMMIT_VERSION:
        raise ValueError("unsupported commit receipt version")
    if receipt.get("run_id") != run_id:
        raise ValueError("commit receipt run_id mismatch")
    if receipt.get("status") != "READY_FOR_REVIEW":
        raise ValueError("invalid commit receipt status")
    if receipt.get("result_sha256") != hashlib.sha256(canonical_bytes).hexdigest():
        raise ValueError("commit receipt digest mismatch")
    for field in ("published_monotonic", "deadline_monotonic"):
        value = receipt.get(field)
        if type(value) not in (int, float) or (
            isinstance(value, float) and not math.isfinite(value)
        ):
            raise ValueError(f"commit receipt {field} must be a finite number")
    if receipt["published_monotonic"] >= receipt["deadline_monotonic"]:
        raise ValueError("canonical replace was not confirmed before the deadline")


def build_ready_commit(run_id: str, canonical_bytes: bytes,
                       published_monotonic: float, deadline_monotonic: float) -> dict[str, Any]:
    receipt = {
        "schema_version": READY_COMMIT_VERSION,
        "run_id": run_id,
        "result_sha256": hashlib.sha256(canonical_bytes).hexdigest(),
        "published_monotonic": published_monotonic,
        "deadline_monotonic": deadline_monotonic,
        "status": "READY_FOR_REVIEW",
    }
    validate_ready_commit(receipt, run_id, canonical_bytes)
    return receipt
