"""R03 target check routing; no Django imports and no implicit runtime fallback."""
from __future__ import annotations

import sys


def target_checks():
    py = sys.executable
    wrapper = "scripts/target_check.py"
    rows = [
        ("FastAPI system/routes/security check", (py, wrapper, "system"), "backend"),
        ("Metadata/Alembic consistency", (py, wrapper, "migrations"), "database"),
        ("Lesson source validation", (py, wrapper, "lesson-sources"), "content"),
        ("Content quality", (py, wrapper, "content-quality"), "content"),
        ("Site integrity", (py, wrapper, "site-integrity"), "content"),
        ("PostgreSQL API/service suite", (py, wrapper, "backend-tests"), "tests"),
    ]
    for name, pattern in [
        ("R03 contract suite", "test_r03_contract.py"),
        ("R02A contract suite", "test_r02a_contract.py"),
        ("R03A contract suite", "test_r03a_contract.py"),
        ("R02 protocol models (synthetic)", "test_migration_r02_protocols.py"),
        ("R03 verification adapter suite", "test_migration_r03*.py"),
    ]:
        rows.append((name, (py, "scripts/run_unittest.py", "--start", "tests",
                            "--pattern", pattern), "tests"))
    rows.extend([
        ("Harness test suite", (py, "-m", "unittest", "discover", "-s",
                                "tests/harness", "-t", ".", "-v"), "harness"),
        ("Frontend typecheck", (py, wrapper, "frontend-typecheck"), "frontend"),
        ("Frontend tests", (py, wrapper, "frontend-tests"), "frontend"),
        ("Frontend build", (py, wrapper, "frontend-build"), "frontend"),
        ("Frontend browser smoke", (py, wrapper, "frontend-e2e"), "frontend"),
    ])
    return rows
