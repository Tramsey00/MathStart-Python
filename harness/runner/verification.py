"""Fixed R04 check registry and bounded local verification evidence."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from harness.contracts.checks import (
    HARNESS_CLI_SMOKE,
    HARNESS_UNIT,
    KNOWN_CHECKS,
    REPO_BASELINE,
)


CHECK_COMMANDS: dict[str, tuple[str, ...]] = {
    REPO_BASELINE: ("scripts/verify_repo.py",),
    HARNESS_UNIT: (
        "-m", "unittest", "discover", "-s", "tests/harness", "-t", ".", "-v",
    ),
    HARNESS_CLI_SMOKE: (
        "-m", "unittest", "discover", "-s", "tests/harness", "-t", ".",
        "-p", "test_cli_smoke.py", "-v",
    ),
}
if frozenset(CHECK_COMMANDS) != KNOWN_CHECKS:
    raise RuntimeError("R04 check registry differs from contract IDs")
MAX_DIAGNOSTIC_CHARS = 16_384
SECRET_LINE = re.compile(
    r"(?i)(api[_-]?key|secret|password|authorization|bearer\s|token\s*[:=])"
)


@dataclass(frozen=True)
class VerificationOutcome:
    checks: list[dict[str, object]]
    artifacts: list[dict[str, str]]
    budget_exceeded: bool = False

    @property
    def status(self) -> str:
        return "PASS" if not self.budget_exceeded and self.checks and all(
            check["status"] == "PASS" for check in self.checks
        ) else "FAIL"


def _safe_diagnostic(value: str) -> str:
    lines = (
        "[redacted sensitive line]\n" if SECRET_LINE.search(line) else line
        for line in value.splitlines(keepends=True)
    )
    content = "".join(lines)
    if len(content) > MAX_DIAGNOSTIC_CHARS:
        return content[:MAX_DIAGNOSTIC_CHARS] + "\n[output truncated]\n"
    return content


def _artifact(run_path: Path, check_id: str, stream: str, value: str) -> dict[str, str]:
    relative_path = f"checks/{check_id}.{stream}.txt"
    path = run_path / relative_path
    path.write_text(_safe_diagnostic(value), encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "kind": f"check-{stream}",
        "path": relative_path,
        "digest": f"sha256:{digest}",
    }


def run_required_checks(
    repo_root: Path,
    run_path: Path,
    check_ids: list[str],
    *,
    deadline: float,
    checks_out: list[dict[str, object]] | None = None,
    artifacts_out: list[dict[str, str]] | None = None,
) -> VerificationOutcome:
    unknown = [check_id for check_id in check_ids if check_id not in CHECK_COMMANDS]
    if unknown:
        raise ValueError(f"unknown required check: {', '.join(unknown)}")

    (run_path / "checks").mkdir(exist_ok=True)
    checks: list[dict[str, object]] = checks_out if checks_out is not None else []
    artifacts: list[dict[str, str]] = (
        artifacts_out if artifacts_out is not None else []
    )
    budget_exceeded = False

    for check_id in check_ids:
        command = [sys.executable, *CHECK_COMMANDS[check_id]]
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            budget_exceeded = True
            check_status = "NOT_RUN"
            exit_code = None
            stdout = ""
            stderr = "Verification wall-time limit exceeded before check started.\n"
        else:
            try:
                completed = subprocess.run(
                    command,
                    cwd=repo_root,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    shell=False,
                    check=False,
                    timeout=remaining,
                )
                exit_code = completed.returncode
                check_status = "PASS" if exit_code == 0 else "FAIL"
                stdout = completed.stdout
                stderr = completed.stderr
            except subprocess.TimeoutExpired as exc:
                budget_exceeded = True
                check_status = "FAIL"
                exit_code = None
                stdout = (
                    exc.stdout.decode("utf-8", "replace")
                    if isinstance(exc.stdout, bytes)
                    else (exc.stdout or "")
                )
                stderr = "Verification check timed out.\n"
            except OSError as exc:
                check_status = "FAIL"
                exit_code = None
                stdout = ""
                stderr = f"Verification process could not start: {exc}\n"

        checks.append({
            "id": check_id,
            "status": check_status,
            "exit_code": exit_code,
        })
        artifacts.append(_artifact(run_path, check_id, "stdout", stdout))
        artifacts.append(_artifact(run_path, check_id, "stderr", stderr))

    return VerificationOutcome(
        checks=checks,
        artifacts=artifacts,
        budget_exceeded=budget_exceeded or time.monotonic() >= deadline,
    )