"""Execute a reviewed R03 command handoff, with a bounded fail-closed outcome.

No command is guessed from an absent backend. V/I owners supply their concrete
entry points in the R03-owned command handoff during integration review.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "specs/migration/r03-v1/runtime-commands.json"
BACKEND_CHECKS = frozenset({"system", "migrations", "lesson-sources", "content-quality",
                            "site-integrity", "backend-tests", "fresh-install",
                            "upgrade-A", "upgrade-B", "upgrade-C"})
FRONTEND_SCRIPTS = {"frontend-typecheck": "typecheck", "frontend-tests": "test",
                    "frontend-build": "build", "frontend-e2e": "test:e2e"}


def validate_result(path, check):
    """A successful process must supply nonempty, unskipped target evidence."""
    result = json.loads(path.read_text(encoding="utf-8"))
    if (result.get("check_id") != check or result.get("status") != "PASS"
            or result.get("evidence_class") != "TARGET_RUNTIME"
            or type(result.get("assertions")) is not int or result["assertions"] < 1
            or type(result.get("skipped")) is not int or result["skipped"] != 0):
        raise ValueError("missing/nonpassing target assertions")
    if check == "lesson-sources" and result["assertions"] < 263:
        raise ValueError("all263 sources required")
    if check in {"migrations", "backend-tests", "fresh-install", "upgrade-A", "upgrade-B", "upgrade-C"}:
        if result.get("database_vendor") != "postgresql" or type(result.get("postgresql_major")) is not int or result["postgresql_major"] < 16:
            raise ValueError("PostgreSQL16 evidence required; SQLite/skip is not proof")
    return result


def command_for(check, root=ROOT):
    """Return only reviewed Python argv or the four prescribed npm script names."""
    if check in FRONTEND_SCRIPTS:
        directory = (root / "frontend").resolve()
        if not directory.is_relative_to(root.resolve()):
            raise ValueError("frontend resolves outside checkout")
        for filename in ("package.json", "package-lock.json"):
            if not (directory / filename).is_file():
                raise ValueError("missing frontend lock/package handoff (I01/I02)")
        script = FRONTEND_SCRIPTS[check]
        package = json.loads((directory / "package.json").read_text(encoding="utf-8"))
        if not package.get("scripts", {}).get(script):
            raise ValueError("missing required frontend script: " + script)
        # .cmd launch needs cmd.exe on Windows; subprocess's shell=True is never used.
        npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
        if not npm:
            raise ValueError("npm tool unavailable")
        argv = [npm, "run", script]
        if os.name == "nt":
            # Only the resolved tool path and closed script allowlist enter cmd.exe.
            argv = [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/s", "/c",
                    '""' + npm + '" run ' + script + '"']
        return argv, directory
    if check not in BACKEND_CHECKS:
        raise ValueError("unknown required check")
    path = root / HANDOFF.relative_to(ROOT)
    handoff = json.loads(path.read_text(encoding="utf-8"))
    entry = handoff.get("commands", {}).get(check)
    if not entry or handoff.get("status") != "REVIEWED":
        raise ValueError("missing reviewed backend command handoff: " + check + " (V01/V02/V04)")
    if set(entry) != {"script", "args"}:
        raise ValueError("invalid command handoff fields")
    relative = Path(entry["script"])
    script = (root / relative).resolve()
    backend_root = (root / "backend").resolve()
    if (relative.is_absolute() or ".." in relative.parts
            or not backend_root.is_relative_to(root.resolve())
            or not script.is_relative_to(backend_root)
            or not script.is_file() or script.suffix != ".py"):
        raise ValueError("backend entry point missing or outside backend")
    args = entry["args"]
    if not isinstance(args, list) or any(not isinstance(arg, str) or "\x00" in arg for arg in args):
        raise ValueError("invalid command argv")
    return [sys.executable, str(script), *args], root


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", choices=sorted(BACKEND_CHECKS | FRONTEND_SCRIPTS.keys()))
    parser.add_argument("--disposable", action="store_true")
    args = parser.parse_args(argv)
    if args.check in {"fresh-install", "upgrade-A", "upgrade-B", "upgrade-C"}:
        if not args.disposable or os.environ.get("MATHSTART_DISPOSABLE") != "1":
            print("FAIL: disposable rehearsal requires --disposable and MATHSTART_DISPOSABLE=1.")
            return 1
    try:
        command, directory = command_for(args.check)
        environment = os.environ.copy()
        receipt = None
        if args.check in BACKEND_CHECKS:
            receipt = ROOT / "var/target-checks" / (args.check + "-" + uuid4().hex) / "result.json"
            receipt.parent.mkdir(parents=True, exist_ok=False)
            environment["MATHSTART_CHECK_RESULT"] = str(receipt)
        result = subprocess.run(command, cwd=directory, shell=False, check=False,
                                capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=540, env=environment)
    except (ValueError, OSError, KeyError, TypeError):
        print("FAIL: required command/tool/handoff unavailable or invalid: " + args.check)
        return 1
    except subprocess.TimeoutExpired:
        print("FAIL: required check timed out: " + args.check)
        return 124
    # Share Harness's bounded redaction policy; never echo raw exceptions/env/DSN.
    sys.path.insert(0, str(ROOT))
    from harness.runner.verification import _safe_diagnostic
    print(_safe_diagnostic(result.stdout), end="")
    print(_safe_diagnostic(result.stderr), end="", file=sys.stderr)
    if result.returncode == 0 and receipt is not None:
        try:
            validate_result(receipt, args.check)
        except (ValueError, OSError, TypeError, KeyError):
            print("FAIL: missing/empty/skipped/non-PostgreSQL target result: " + args.check)
            return 1
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
