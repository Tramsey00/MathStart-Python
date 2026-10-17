"""I01 isolated SQLite compatibility verification, not PostgreSQL/target acceptance."""
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
ISOLATED = ROOT / "var" / "i01-final-20261009"
RUNTIME = ISOLATED / "runtime"
DATABASE = RUNTIME / "verification.sqlite3"
PYTHON_ENV = ISOLATED / "python"
PYTHON = PYTHON_ENV / "Scripts" / "python.exe"
RESULTS = []
def now():
    return datetime.now(timezone.utc).isoformat()
def save():
    (EVIDENCE / "repository-commands.json").write_text(json.dumps({
        "source_input": "8d958aeeb17da46839722441425ccbb5889e2ab7",
        "profile": "EXPLICIT_SQLITE_COMPATIBILITY",
        "postgresql_verification": "NOT_RUN: Docker Linux daemon unavailable",
        "results": RESULTS}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def run(name, argv, *, cwd=ROOT):
    started = now()
    p = subprocess.run([str(x) for x in argv], cwd=cwd, env=ENV, text=True,
                       encoding="utf-8", errors="replace", capture_output=True, timeout=900)
    RESULTS.append({"name": name, "command": [str(x) for x in argv], "cwd": str(cwd),
                    "started_at": started, "finished_at": now(), "exit_code": p.returncode,
                    "stdout": p.stdout, "stderr": p.stderr})
    save()
    print(f"{name}: {p.returncode}", flush=True)
    return p.returncode
if ROOT.name != "MathStart-Python" or ROOT.parent.name != "ms7-mig-i01-foundation":
    raise SystemExit("Wrong task worktree")
if (ROOT / ".env").exists() or DATABASE.exists() or PYTHON_ENV.exists():
    raise SystemExit("Requires fresh I01 verification paths; no .env or existing DB/env is used")
ENV = {k: v for k, v in os.environ.items()
       if not k.startswith(("DJANGO_", "PG", "PIP_")) and k != "DATABASE_URL"}
ISOLATED.mkdir(parents=True, exist_ok=True)
RUNTIME.mkdir()
(ISOLATED / "tmp").mkdir()
ENV.update({
    "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
    "PIP_CONFIG_FILE": os.devnull, "PIP_INDEX_URL": "https://pypi.org/simple",
    "PIP_CACHE_DIR": str(ISOLATED / "pip-cache"), "PIP_DISABLE_PIP_VERSION_CHECK": "1",
    "TEMP": str(ISOLATED / "tmp"), "TMP": str(ISOLATED / "tmp"),
    "DJANGO_SECRET_KEY": secrets.token_urlsafe(48),
    "DJANGO_DEBUG": "False", "DJANGO_ALLOWED_HOSTS": "127.0.0.1,localhost,testserver",
    "DJANGO_SETTINGS_MODULE": "config.settings", "DJANGO_DB_BACKEND": "sqlite",
    "DJANGO_DB_PATH": str(DATABASE), "DJANGO_RUNTIME_ROOT": str(RUNTIME),
})
for name, argv in [
    ("create-isolated-python-env", [sys.executable, "-B", "-m", "venv", PYTHON_ENV]),
    ("install-locked-python-dependencies", [PYTHON, "-B", "-m", "pip", "install", "--no-deps", "-r", ROOT / "requirements.lock"]),
    ("python-version", [PYTHON, "-B", "--version"]),
    ("pip-check", [PYTHON, "-B", "-m", "pip", "check"]),
]:
    if run(name, argv):
        raise SystemExit(1)
guard = """
import json
from pathlib import Path
from django.conf import settings
expected = Path(__import__('os').environ['DJANGO_DB_PATH']).resolve()
runtime = Path(__import__('os').environ['DJANGO_RUNTIME_ROOT']).resolve()
assert settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
assert Path(settings.DATABASES['default']['NAME']).resolve() == expected
assert not expected.exists()
assert settings.RUNTIME_ROOT == runtime
assert settings.MEDIA_ROOT.is_relative_to(runtime)
assert settings.STATIC_ROOT.is_relative_to(runtime)
print(json.dumps({'engine': settings.DATABASES['default']['ENGINE'], 'database_path': str(expected),
'runtime_path': str(runtime), 'database_initially_absent': True,
'postgres_connection_configuration': 'NOT_USED', 'test_database': 'Django SQLite in-memory default'}))
"""
if run("assert-runtime-and-db-isolation-before-writes", [PYTHON, "-B", "-c", guard]):
    raise SystemExit(1)
def material_hashes():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for directory in ("curriculum", "site_content", "templates", "static")
            for p in sorted((ROOT / directory).rglob("*")) if p.is_file()}
before = material_hashes()
# Only the new task-local compatibility DB/runtime below can receive setup writes.
for name, args in [
    ("fresh-sqlite-migrate", ["manage.py", "migrate", "--noinput"]),
    ("fresh-sqlite-bootstrap", ["manage.py", "bootstrap_site"]),
    ("fresh-sqlite-collectstatic", ["manage.py", "collectstatic", "--noinput"]),
]:
    if run(name, [PYTHON, "-B", *args]):
        raise SystemExit(1)
code = run("verify-repo-full-entrypoint-sqlite", [PYTHON, "-B", "scripts/verify_repo.py"])
after = material_hashes()
(EVIDENCE / "repository-isolation.json").write_text(json.dumps({
    "profile": "SQLite compatibility only; PostgreSQL locking/concurrency is NOT verified",
    "python": str(PYTHON), "database": str(DATABASE), "runtime": str(RUNTIME),
    "existing_db_used": False, "working_db_accessed": False, "r01_baseline_used": False,
    "dotenv_created_or_copied": False, "source_material_count": len(before),
    "source_materials_unchanged": before == after,
    "requirements_lock_sha256": hashlib.sha256((ROOT / "requirements.lock").read_bytes()).hexdigest(),
    "verify_repo_exit_code": code}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if before != after:
    raise SystemExit("Source materials changed")
raise SystemExit(code)
