"""Actual runtime versions only; no environment dump, DSN or credentials."""
from importlib import metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("legacy", "target", "pure"), default="legacy")
    args = parser.parse_args(argv)
    report = {"python": platform.python_version(), "packages": {}, "lock_mismatches": []}
    root = Path(__file__).resolve().parents[1]
    lock = root / {"legacy": "requirements.lock", "pure": "specs/migration/r03-v1/verification.lock", "target": "backend/requirements.lock"}[args.profile]
    if not lock.is_file():
        print(json.dumps({**report, "profile": args.profile, "error": "required owner lock missing"}, indent=2))
        return 1
    report["profile"] = args.profile
    for line in lock.read_text(encoding="utf-8").splitlines():
        if "==" not in line or line.startswith("#"):
            continue
        name = line.split("==", 1)[0].split("[", 1)[0]
        try:
            report["packages"][name] = metadata.version(name)
            if report["packages"][name] != line.split("==", 1)[1].strip():
                report["lock_mismatches"].append(name)
        except metadata.PackageNotFoundError:
            report["packages"][name] = "NOT INSTALLED"
    report["pip"] = metadata.version("pip")
    if args.profile == "pure":
        print(json.dumps(report, indent=2))
        return 0 if ("NOT INSTALLED" not in report["packages"].values() and not report["lock_mismatches"] and sys.version_info >= (3, 12)) else 1
    command = [sys.executable, str(Path(__file__).with_name("check_database.py"))]
    if args.profile == "target":
        command += ["--profile", "target"]
    result = subprocess.run(
        command,
        capture_output=True, text=True, timeout=40,
    )
    report["database"] = result.stdout.strip() or "NOT VERIFIED"
    print(json.dumps(report, indent=2))
    return 0 if (result.returncode == 0 and "NOT INSTALLED" not in report["packages"].values() and not report["lock_mismatches"] and sys.version_info >= (3, 12)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
