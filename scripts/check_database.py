"""Bounded DB diagnostic. Never print connection values or driver exceptions."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def probe():
    sys.path.insert(0, str(ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        import django
        django.setup()
    except Exception:
        print("Database configuration invalid. Check DJANGO_SECRET_KEY and DJANGO_DB_*; "
              "backend, required fields, port and timeout must be valid.")
        return 1
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            if cursor.fetchone() != (1,):
                return 1
            if connection.vendor == "postgresql":
                cursor.execute("SHOW server_version_num")
                version = int(cursor.fetchone()[0])
                if version < 160000:
                    print("PostgreSQL 16+ required.")
                    return 1
                print(f"PostgreSQL connection OK; server_version_num={version}")
            else:
                print("SQLite compatibility connection OK (not PostgreSQL verification).")
        connection.close()
        return 0
    except Exception:
        print("Database connection failed. Check PostgreSQL service/health, "
              "DJANGO_DB_HOST/PORT/NAME/USER/PASSWORD and access permissions. "
              "No SQLite fallback was attempted.")
        return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("legacy", "target"), default="legacy")
    parser.add_argument("--probe", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.profile == "target":
        sys.path.insert(0, str(ROOT))
        from scripts.target_database import main as target_main
        return target_main()
    if args.probe:
        return probe()
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--probe"],
            cwd=ROOT, capture_output=True, text=True, timeout=35,
        )
    except subprocess.TimeoutExpired:
        print("Database diagnostic timed out after 35 seconds. Check service/network/DNS.")
        return 1
    # Child output is generated exclusively by probe; stderr is never forwarded.
    print(result.stdout.strip() or "Database diagnostic failed; check Python dependencies.")
    return 0 if result.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
