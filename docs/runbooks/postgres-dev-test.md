# MS6-V01: PostgreSQL development and verification

This is dev/test infrastructure, not production hosting. Python 3.12+,
PostgreSQL 16+ and Docker Compose v2 with `up --wait` are required for the
container path. PostgreSQL is the documented primary dev/test path. The local
Docker/PostgreSQL fresh-install smoke, Harness, publication locking regressions,
database diagnostic and version report passed user-executed verification.
See the [V01 trace](../agent-traces/MS6-V01-postgres-ci.md) for evidence.
Real GitHub Actions execution and human review/acceptance remain pending.

## Configuration

Copy `.env.example` to ignored `.env`. Replace the local-only password and
Django secret placeholder. Never commit `.env`, print `docker compose config`
with resolved credentials into a trace, or put secrets in Docker build args.

| Variable | Behavior |
| --- | --- |
| `DJANGO_DB_BACKEND` | Defaults to `postgresql`; only explicit `sqlite` selects legacy mode |
| `DJANGO_DB_NAME/USER/PASSWORD/HOST` | Required, nonblank for PostgreSQL |
| `DJANGO_DB_PORT` | Integer 1..65535; defaults to 5432 |
| `DJANGO_DB_CONNECT_TIMEOUT` | Integer 2..30 seconds; defaults to 5 |
| `DJANGO_DB_TEST_NAME` | Defaults to `test_` + database name; cannot equal runtime DB |
| `DJANGO_RUNTIME_ROOT` | Absolute directory recommended; contains media, staticfiles, var/reports and var/backups; defaults to repository root for legacy compatibility |
| `DJANGO_DB_PATH` | Used only for explicitly selected SQLite |

Process environment overrides `.env`. Compose injects only named variables,
uses host `db` and port 5432 inside containers, and exposes services only on
localhost. Its PostgreSQL role is a disposable dev/CI role with database-creation
privileges for Django tests, not a production role. No database fallback occurs
after configuration or connection errors.

## Docker development

From the repository root after preparing `.env`:

```text
docker compose build app
docker compose up -d --wait db
docker compose run --rm app python scripts/check_database.py
docker compose run --rm app python manage.py migrate --noinput
docker compose run --rm app python manage.py bootstrap_site
docker compose run --rm app python manage.py collectstatic --noinput
docker compose up app
```

Open http://localhost:8000. The app uses Django runserver, not a production
application server. Source files are copied into the image; rebuild after edits.
Named volumes keep database and generated runtime files separate from sources.
Changing `.env` credentials does not reinitialize an existing PostgreSQL volume.
Do not delete a development volume to repair schema; use migrations.

## Host Python development

Use an activated Python 3.12+ virtual environment. A working user `.venv` needs
no replacement because another execution surface cannot launch it.

```text
python --version
python -m pip install --no-deps -r requirements.lock
python -m pip check
docker compose up -d --wait db
python scripts/check_database.py
python manage.py migrate --noinput
python manage.py bootstrap_site
python manage.py collectstatic --noinput
python manage.py runserver
```

Host `.env` uses `DJANGO_DB_HOST=127.0.0.1` and the published port. Choose an
isolated `DJANGO_RUNTIME_ROOT` for test work. PostgreSQL service may instead be
provided locally; it must be 16+ and use a dedicated database/role.

## Disposable fresh-install smoke (PowerShell)

Run in a separate shell to avoid changing the developer's environment. Prepare
`.env` first. Pick an unused local port if 55432 is occupied.

```powershell
$smokeProject = "ms6-v01-" + [guid]::NewGuid().ToString("N")
$env:DJANGO_DB_NAME = "ms6_v01_smoke_" + [guid]::NewGuid().ToString("N")
$env:DJANGO_DB_PORT = "55432"
$env:DJANGO_DEBUG = "False"
docker compose -p $smokeProject build app
docker compose -p $smokeProject up -d --wait db
docker compose -p $smokeProject run --rm app python scripts/fresh_install_smoke.py --disposable
docker compose -p $smokeProject run --rm app python scripts/version_report.py
docker compose -p $smokeProject run --rm app python scripts/verify_repo.py
docker compose -p $smokeProject run --rm -e DJANGO_DB_PORT=1 app python scripts/check_database.py
```

Stop on any unexpected nonzero exit. The final connection-failure command must
exit nonzero with a readable message. It does not stop PostgreSQL or alter data.
The diagnostic has a 35-second parent-process deadline, including DNS/setup.
Errors suppress raw driver exception text and never print password/DSN values.

Smoke refuses SQLite, database names without `ms6_v01_smoke_`, any existing
tables/views, unsafe source-overlapping runtime paths and nonempty media/static.
It never drops a database, flushes data or uses fake migrations/manual schema SQL.
It applies existing migrations, runs two real bootstraps, checks exact counts
(6/12/63/281/263/29/280), stable PK/FK/content snapshots, media hashes and an
existing user; collects the manifest, runs all three content checks and compares
source-material hashes even after a failure. Auto-update timestamps are excluded
from the idempotency snapshot. `bootstrap_site --dry-run` is not a read-only SQL
guarantee and is not used here.

After inspecting evidence, remove **only this disposable project's** volumes:

```powershell
docker compose -p $smokeProject down --volumes
```

Never substitute the normal development project in this cleanup command.
For another fresh run use a new project/name, not a reset of historical data.

## Verification and reports

```text
python manage.py test content.test_infrastructure content.test_postgres_publication --noinput
python scripts/verify_repo.py
python scripts/version_report.py
docker version
docker compose version
```

The Harness retains Django check, missing migrations check, three content checks,
the complete Django suite and the R03 pure contract suite. Content checks require
migration/bootstrap/collectstatic first. PostgreSQL tests use a separate database;
never point `DJANGO_DB_TEST_NAME` at an existing application database.
The two locking regressions skip on SQLite and must pass on PostgreSQL.
Version report prints Python, pip, locked package runtime versions and actual
PostgreSQL server version number. Capture Docker/Compose versions separately.
Reports live under `DJANGO_RUNTIME_ROOT/var/reports`. CI uses a fresh PostgreSQL
service, disposable credentials and this same smoke/Harness sequence.

## Dependency lock maintenance

`requirements.txt` declares direct pins; `requirements.lock` pins the entire
resolved closure, including psycopg-binary. Lock versions were resolved with pip,
not transcribed from assumptions. Artifact hashes are not currently enforced.
Image tags follow Python 3.12 and PostgreSQL 16 patch updates; record actual
image/runtime versions when reproducing a run.

After an intentional direct dependency update, use Python 3.12 in a disposable
environment, resolve from the real package index and review the resulting diff:

```text
python -m pip install --dry-run --ignore-installed --report var/v01-dependency-resolution.json -r requirements.txt
python scripts/lock_dependencies.py var/v01-dependency-resolution.json
python -m pip install --no-deps -r requirements.lock
python -m pip check
python -m pip install --dry-run --ignore-installed --only-binary=:all: --platform manylinux2014_x86_64 --python-version 3.12 --implementation cp --abi cp312 --report var/v01-linux-resolution.json -r requirements.lock
```

Create ignored `var/` first if absent. Pip reports may contain index metadata;
do not commit them or publish credentials from private index configuration.
The lock generator copies only names/versions. Revalidate Windows and Linux
resolution and full verification; a failed/offline resolution cannot produce a
new accepted lock.

## Compatibility and known limits

SQLite remains explicit (`DJANGO_DB_BACKEND=sqlite`, `DJANGO_DB_PATH=...`), with
existing SQLite-only publication backups. PostgreSQL does not get SQLite file
backups; production backup strategy is out of scope. Bootstrap has multiple
transaction/filesystem phases, so a failure need not roll back all earlier
phases. Rerun only after diagnosing the conflict; do not bypass conflict checks.
No content, migration, user evidence or future domain app is recreated to make
this infrastructure work. Local Docker/PostgreSQL smoke and locking checks have
passed; SQLite success alone is insufficient evidence for them. Final V01
completion still requires a real GitHub Actions run and human acceptance.
