"""Actual runtime versions only; no environment dump, DSN or credentials."""
from importlib import metadata
import json
from pathlib import Path
import platform
import subprocess
import sys


def main():
    report = {"python": platform.python_version(), "packages": {}}
    lock = Path(__file__).resolve().parents[1] / "requirements.lock"
    for line in lock.read_text(encoding="utf-8").splitlines():
        if "==" not in line or line.startswith("#"):
            continue
        name = line.split("==", 1)[0].split("[", 1)[0]
        try:
            report["packages"][name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            report["packages"][name] = "NOT INSTALLED"
    report["pip"] = metadata.version("pip")
    result = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("check_database.py"))],
        capture_output=True, text=True, timeout=40,
    )
    report["database"] = result.stdout.strip() or "NOT VERIFIED"
    print(json.dumps(report, indent=2))
    return 0 if result.returncode == 0 and "NOT INSTALLED" not in report["packages"].values() else 1


if __name__ == "__main__":
    raise SystemExit(main())
