#!/usr/bin/env python
"""Run fast lesson/UI checks without invoking managed runtime QA."""
from __future__ import annotations

import subprocess
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str], cwd: Path) -> int:
    print(f"\n== {label} ==", flush=True)
    print("$ " + " ".join(command), flush=True)
    try:
        return subprocess.run(command, cwd=cwd, check=False, shell=False, timeout=180).returncode
    except subprocess.TimeoutExpired:
        print(f"FAIL: {label} timed out after 180 seconds", file=sys.stderr)
        return 124
    except OSError:
        print(f"FAIL: {label} command unavailable", file=sys.stderr)
        return 127


def main() -> int:
    frontend = ROOT / "frontend"
    commands = [
        ("frontend lesson unit tests", [shutil.which("npm") or "npm", "run", "test:lesson"], frontend),
        ("frontend typecheck", [shutil.which("npm") or "npm", "run", "typecheck"], frontend),
        ("lesson document and navigation contracts", [sys.executable, "-m", "unittest",
            "backend.tests.v04.test_lesson_document", "backend.tests.v04.test_lesson_navigation", "-v"], ROOT),
        ("current UI contract", [sys.executable, "-m", "unittest", "tests.test_i02_ui_contract", "-v"], ROOT),
        ("product source gate", [sys.executable, "scripts/check_product_source.py"], ROOT),
        ("workflow documentation gate", [sys.executable, "scripts/check_workflow_docs.py"], ROOT),
        ("migration preservation gate", [sys.executable, "scripts/check_migration_preservation.py"], ROOT),
    ]
    for label, command, cwd in commands:
        code = run(label, command, cwd)
        if code:
            print(f"\nRESULT: FAIL ({label}, exit {code})", file=sys.stderr)
            return code
    print("\nRESULT: PASS (fast lesson/UI checks only; no PostgreSQL, browser matrix, managed install, or recovery QA)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
