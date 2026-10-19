#!/usr/bin/env python
"""
MathStart repository verification entry point.

Current target registry, portable pure subset and explicit pinned legacy oracle.
Target wrappers fail when required owner implementations are absent. The pure
profile proves only portable contracts/model/Harness behavior, never runtime
parity. Historical comparisons require a separate pinned checkout and interpreter.

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
GROUPS = ("backend", "database", "content", "tests", "harness", "frontend")


@dataclass(frozen=True)
class Check:
    name: str
    command: tuple[str, ...]
    group: str


from scripts.target_verification import target_checks
CHECKS: tuple[Check, ...] = tuple(Check(*row) for row in target_checks())


def run_command(command: Sequence[str]) -> int:
    print(f"$ {' '.join(command)}", flush=True)
    # The full backend suite includes schema replays, separate legacy oracles
    # and real React/HTTP publication. Allow its bounded child deadline plus
    # cleanup, while retaining the ordinary command deadline for other checks.
    timeout = ({'backend-tests': 1860, 'frontend-e2e': 7500}.get(command[-1], 600)
               if 'scripts/target_check.py' in command else 600)
    try:
        completed = subprocess.run(list(command), cwd=ROOT, check=False,
                                   shell=False, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"Verification check timed out ({timeout} seconds).", file=sys.stderr)
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
        "--profile", choices=("legacy", "target", "pure"), default="target",
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
        help="Skip backend, contract and Harness test suites for a faster local pass.",
    )
    return parser.parse_args(argv)


def select_checks(args: argparse.Namespace) -> list[Check]:
    if args.profile == "legacy":
        selected = [Check("Pinned historical Django verification",
                          (sys.executable, "scripts/legacy_oracle.py", "--run", "scripts/verify_repo.py"), "tests")]
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
