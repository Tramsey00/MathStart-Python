#!/usr/bin/env python
"""
MathStart repository verification entry point.

R01/R04 legacy baseline plus explicit MS7-MIG-R03 target/pure profiles.
Target wrappers fail when required owner implementations are absent. The pure
profile proves only portable contracts/model/Harness behavior, never runtime
parity. The legacy default preserves the frozen CI baseline during migration.

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
sys.path.insert(0, str(ROOT))
MANAGE_PY = ROOT / "manage.py"
GROUPS = ("backend", "database", "content", "tests", "harness", "frontend")


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
    Check(
        name="R03 contract suite",
        command=(
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_r03_contract.py",
        ),
        group="tests",
    ),
    Check(
        name="Harness test suite",
        command=(sys.executable, "-m", "unittest", "discover",
                 "-s", "tests/harness", "-t", ".", "-v"),
        group="harness",
    ),
)


def run_command(command: Sequence[str]) -> int:
    print(f"$ {' '.join(command)}", flush=True)
    try:
        completed = subprocess.run(list(command), cwd=ROOT, check=False,
                                   shell=False, timeout=600)
    except subprocess.TimeoutExpired:
        print("Verification check timed out (600 seconds).", file=sys.stderr)
        return 124
    except OSError:
        print("Verification tool unavailable.", file=sys.stderr)
        return 127
    return completed.returncode


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run MathStart Harness verification checks."
    )
    parser.add_argument(
        "--profile", choices=("legacy", "target", "pure"), default="legacy",
        help="Explicit migration profile; target is required for migration acceptance.",
    )
    parser.add_argument(
        "--group",
        action="append",
        choices=GROUPS,
        help=(
            "Run only selected verification group(s). "
            "May be supplied more than once."
        ),
    )
    parser.add_argument(
        "--exclude-group",
        action="append",
        choices=GROUPS,
        help="Exclude a group; nested Harness repo-baseline excludes harness to prevent recursion.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List checks without executing them.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip Django, R03 and Harness test suites for a faster local pass.",
    )
    return parser.parse_args(argv)


def select_checks(args: argparse.Namespace) -> list[Check]:
    if args.profile == "legacy":
        selected = list(CHECKS)
    else:
        # Importing the target registry must never initialize the legacy runtime.
        from scripts.target_verification import target_checks
        selected = [Check(*row) for row in target_checks()]
        if args.profile == "pure":
            selected = [check for check in selected if check.group in {"tests", "harness"}
                        and "scripts/target_check.py" not in check.command]

    if args.group:
        groups = set(args.group)
        selected = [check for check in selected if check.group in groups]

    if args.exclude_group:
        selected = [check for check in selected if check.group not in args.exclude_group]

    if args.skip_tests:
        selected = [check for check in selected if check.group not in {"tests", "harness"}]

    return selected


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    if args.profile == "legacy" and not MANAGE_PY.is_file():
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
        print("ERROR: no checks selected; empty verification is not PASS.", file=sys.stderr)
        return 1

    results: list[tuple[Check, int]] = []

    print("MathStart Harness verification")
    print(f"Profile: {args.profile}; selected checks only, not full target acceptance")
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
