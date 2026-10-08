"""Standalone bounded PostgreSQL16 diagnostic, no Django and no SQLite fallback."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


def probe():
    try:
        import psycopg
        names = ("HOST", "PORT", "NAME", "USER", "PASSWORD")
        values = {name: os.environ["MATHSTART_DB_" + name] for name in names}
        if not all(values.values()) or not 1 <= int(values["PORT"]) <= 65535:
            raise ValueError("configuration")
        # 5s connect timeout is below the parent deadline. Values never enter argv/logs.
        with psycopg.connect(host=values["HOST"], port=int(values["PORT"]),
                             dbname=values["NAME"], user=values["USER"],
                             password=values["PASSWORD"], connect_timeout=5,
                             options="-c statement_timeout=5000 -c default_transaction_read_only=on") as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                if cursor.fetchone() != (1,):
                    return 1
                cursor.execute("SHOW server_version_num")
                version = int(cursor.fetchone()[0])
                if version < 160000:
                    print("FAIL: PostgreSQL16+ required.")
                    return 1
                print(f"PostgreSQL connection OK; server_version_num={version}")
        return 0
    except Exception:
        print("FAIL: PostgreSQL configuration/dependency/connection unavailable; no fallback.")
        return 1


def main(argv=None):
    if argv == ["--probe"]:
        return probe()
    try:
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--probe"],
                                capture_output=True, text=True, timeout=15, check=False)
    except (subprocess.TimeoutExpired, OSError):
        print("FAIL: PostgreSQL diagnostic unavailable or exceeded 15 seconds.")
        return 1
    print(result.stdout.strip() or "FAIL: PostgreSQL diagnostic produced no evidence.")
    return 0 if result.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
