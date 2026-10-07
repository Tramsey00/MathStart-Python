# R01 [reviewer] — isolated baseline preflight

Status: isolated empty PostgreSQL created; awaiting the user's confirmation
before any migrate/bootstrap/publication. No I01/target-stack implementation.

Source: 8c11edadc8debc81432d1db1145feac504f09061, obtained by exact git archive
into ./source.
Generated runtime is a separate sibling directory, runtime/.
The archive has no .env; no existing .env was changed or copied.

## Proven separation

| Property | Existing working instance | Disposable instance |
| --- | --- | --- |
| Database | mathstart | ms6_v01_smoke_ilya_r01_20261007_8c11edad |
| Host port | 127.0.0.1:5432 | 127.0.0.1:55447 |
| Container | mathstart-python-db-1 | ms7-r01-ilya-20261007-8c11edad-db-1 |
| Container ID | f72c80d7d67a764f1d7e7b16efb4c754f39d98889fb5d493da7497e2e5792738 | a5d1546726b824dea3d1c06eddf73d35f4d372a7c20dc48b72e701ea6a4de8f2 |
| Docker volume | mathstart-python_database | ms7-r01-ilya-20261007-8c11edad_database |
| App URL | http://127.0.0.1:8001/ | http://127.0.0.1:8002/ planned; NOT STARTED |

Disposable SELECT current_database()/current_user() returned the exact intended
DB and ms7_r01_ilya. PostgreSQL 16.15; cluster system identifier
7694003449677013030; server-side port 5432 (container internal).
Public table count 0; cluster contains only the intended DB plus
postgres/template0/template1. The probe itself was READ ONLY and rolled back.

The app child environment removes inherited DJANGO_*, PG*, COMPOSE_* and
POSTGRES_* variables, explicitly sets every disposable connection setting,
and uses its own generated credentials/secret retained in process memory.
Compose --env-file NUL and the source archive's absent .env prevent fallback to
working credentials. Separate container/cluster/volume/port were inspected.
No mount points at working runtime/source; no shared database volume.

Working DB fingerprint before/after preflight is identical across all 20 public
tables (row counts and canonical row hashes), columns/indexes and sequence
states. Only hashes/counts were saved, not records/PII/passwords. Both probes
were verified READ ONLY transactions with rollback. This establishes preservation
over this observed interval, not control over independent concurrent writers.
git status is main...origin/main with no tracked/untracked source changes;
all generated evidence is inside the existing ignored var/ directory.

## Commands actually completed

All successful controller commands and stdout/stderr logs are in commands.json
and command-01.log through command-06.log, including exact absolute paths.

| Command/check | Exit/result |
| --- | --- |
| docker version / docker image ls / docker ps (authorized read-only retry) | 0 |
| docker compose version --short | 0; 5.5.1 |
| python -B .../working_fingerprint.py before | 0 |
| git rev-parse HEAD | 0; exact required SHA |
| docker ps / volume ls with unique project label | 0; none existed |
| docker image inspect postgres:16-bookworm | 0; existing image, no pull |
| git archive --format=zip <exact SHA> (memory -> new source directory) | 0 |
| docker compose --env-file NUL -p ms7-r01-ilya-20261007-8c11edad -f <source>/compose.yaml up --pull never -d --wait db | 0 |
| docker compose ... ps -q db / filtered container inspection | 0 |
| disposable readonly identity/emptiness query | PASS |
| python -B .../working_fingerprint.py after | 0; unchanged |
| filtered working/disposable docker inspect | 0; separate mounts/ports |
| git status -sb / git diff --exit-code | 0; clean |

Initial sandbox Docker access was denied by the local pipe permission; the
authorized read-only retry succeeded. No service repair or working DB action.

## Exact next command, only after user confirmation

Working directory:
./source

```powershell
& SOURCE_AT_8c11edad/.venv/Scripts/python.exe -B scripts/fresh_install_smoke.py --disposable
```

It will run under the already verified disposable environment through the
waiting controller, not under an ordinary shell that might load working .env.
The unchanged existing smoke guards the DB prefix, empty schema and isolated
runtime, then runs existing migrations, bootstrap twice (including normal lesson
publication), collectstatic and source/content/integrity checks. It creates its
documented sentinel user only in the disposable DB. Source material hashes are
checked in finally. No separate update_public_pages command is needed on fresh
bootstrap. Any failure/drift is reported and not silently repaired.

Then a read-only source/published comparison must cover all mapped source pages
and explicitly the six user-required routes. Screenshots cannot begin until
parity passes. Server will be localhost:8002, bytecode/autoreload disabled,
default_transaction_read_only=on for page review. Planned browser review and
screenshots: 360/768/1440, required six routes, exact browser/version/state/URL
logged, plus keyboard/widgets/content/layout findings. Those steps have NOT run.

No commit/push, shared [coordinator] R01 document edit, PR46 final review or approval
performed. D02/D03 remain human decisions; no acceptance recommendation yet
because fresh parity and visual review are still pending.
