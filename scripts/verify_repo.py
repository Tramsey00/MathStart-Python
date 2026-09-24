#!/usr/bin/env python
"""
MathStart repository verification entry point.

R01 / Harness v1 baseline.

This script intentionally runs only checks that are already part of the current
MathStart repository workflow. It does not pretend that future tooling
(Ruff, mypy, pytest, PostgreSQL smoke, architecture validators, etc.) is already
configured.

Exit code:
    0 - all enabled checks passed
    1 - one or more checks failed
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
MANAGE_PY = ROOT / "manage.py"


@dataclass(frozen=True)
class Check:
    name: str
    command: tuple[str, ...]
    group: str


CHECKS: tuple[Check, ...] = (
    Check(
        name="Django system check",
        command=(sys.executable, "manage.py", "check"),
        group="backend",
    ),
    Check(
        name="Migration consistency",
        command=(
            sys.executable,
            "manage.py",
            "makemigrations",
            "--check",
            "--dry-run",
        ),
        group="database",
    ),
    Check(
        name="Lesson source validation",
        command=(
            sys.executable,
            "manage.py",
            "check_lesson_sources",
            "--all",
        ),
        group="content",
    ),
    Check(
        name="Content quality",
        command=(
            sys.executable,
            "manage.py",
            "check_content_quality",
        ),
        group="content",
    ),
    Check(
        name="Site integrity",
        command=(
            sys.executable,
            "manage.py",
            "check_site_integrity",
        ),
        group="content",
    ),
    Check(
        name="Django test suite",
        command=(
            sys.executable,
            "manage.py",
            "test",
        ),
        group="tests",
    ),
)


def run_command(command: Sequence[str]) -> int:
    print(f"$ {' '.join(command)}", flush=True)
    completed = subprocess.run(
        list(command),
        cwd=ROOT,
        check=False,
    )
    return completed.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run MathStart Harness verification checks."
    )
    parser.add_argument(
        "--group",
        action="append",
        choices=("backend", "database", "content", "tests"),
        help=(
            "Run only selected verification group(s). "
            "May be supplied more than once."
        ),
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List checks without executing them.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip the Django test suite for a faster local verification pass.",
    )
    return parser.parse_args()


def select_checks(args: argparse.Namespace) -> list[Check]:
    selected = list(CHECKS)

    if args.group:
        groups = set(args.group)
        selected = [check for check in selected if check.group in groups]

    if args.skip_tests:
        selected = [check for check in selected if check.group != "tests"]

    return selected


def main() -> int:
    args = parse_args()

    if not MANAGE_PY.is_file():
        print(
            f"ERROR: manage.py not found at expected repository root: {MANAGE_PY}",
            file=sys.stderr,
        )
        return 1

    selected = select_checks(args)

    if args.list:
        for check in selected:
            print(
                f"[{check.group}] {check.name}: "
                f"{' '.join(check.command)}"
            )
        return 0

    if not selected:
        print("No checks selected.")
        return 0

    results: list[tuple[Check, int]] = []

    print("MathStart Harness verification")
    print(f"Repository: {ROOT}")
    print()

    for index, check in enumerate(selected, start=1):
        print("=" * 78)
        print(f"[{index}/{len(selected)}] {check.name} [{check.group}]")
        print("=" * 78)
        code = run_command(check.command)
        results.append((check, code))
        print()
        if code != 0:
            print(f"FAILED: {check.name} (exit code {code})")
        else:
            print(f"PASSED: {check.name}")
        print()

    print("=" * 78)
    print("Verification summary")
    print("=" * 78)

    failed = 0
    for check, code in results:
        status = "PASS" if code == 0 else "FAIL"
        print(f"{status:4}  [{check.group}] {check.name}")
        failed += int(code != 0)

    print()
    if failed:
        print(
            f"RESULT: FAIL ({failed} of {len(results)} checks failed).",
            file=sys.stderr,
        )
        return 1

    print(f"RESULT: PASS ({len(results)} checks passed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
