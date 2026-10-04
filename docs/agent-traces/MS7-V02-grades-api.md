# TRACE MS7-V02 follow-up: Grades API (Issue 23)

- **Date:** 2026-10-04
- **Owner:** Владимир
- **Coding agent / surface:** Codex desktop
- **Issue:** https://github.com/Tramsey00/MathStart-Python/issues/23
- **Plan:** [active grades API plan](../exec-plans/active/MS7-V02-grades-api.md)
- **Contract:** accepted R02A OpenAPI/DTO/policy (unchanged)
- **Human reviewer:** Руслан; I03 consumer Илья
- **Runtime spec:** [Grade mapping](../../specs/api/MS7-V02-grades-runtime.md)
- **Status:** INCOMPLETE; local verification PASS, human review and merge pending

## Task and inputs

User requested closing the catalogue integration gap and creating an Issue and
local branch first, then supplied Issue 23. Read that Issue through GitHub and
the required repository sources, relevant Content/Users code/tests/migrations,
README, content pipeline, ADR-0001/0004 and verification skill.

## Initial state and actions

Initial branch `main`, commit `150e569` (V02 PR 19 merged). `git fetch origin main`
succeeded; local main equaled origin/main. Created `codex/ms7-v02-grades-api`.
Existing unrelated untracked audit/correction docs and `output/`, `tmp/` retained.
No developer data or source-material changes made.

User explicitly agreed on 2026-10-04 to adding `created_at` and verifying its
additive migration before schema implementation. Added the Content read API,
migration, tests, runtime adapter spec, active plan and trace.

## Discovery and incidents

R02A requires `(created_at,id)` ordering; legacy Grade has no `created_at`.
Issue 23 explicitly requires agreement before an unexpected migration. Asked the
user to choose an additive timestamp migration or separately approved catalogue
ordering exception; user chose the migration.

Normal sandbox shell and node kernel fail during sandbox startup with
`apply deny-read ACLs`; scoped shell reads ran via approved escalation.
Initially Docker daemon connection failed (DockerDesktopLinuxEngine pipe absent)
and the configured PostgreSQL diagnostic returned exit 1, redacted. Started the
installed Docker Desktop with `Start-Process -WindowStyle Hidden`; then started
only the new disposable Compose project's db service. Connection to that isolated
PostgreSQL passed. These initial environment failures were resolved; no test
failure was suppressed and no SQLite result is used as PostgreSQL evidence.

## Implementation and files

Added:

- `config/api_http.py`: existing safe wire primitives moved to infrastructure.
- `content/api_urls.py`, `content/api_views.py`: anonymous GET-only Content API.
- `content/services/grade_catalogue.py`: canonical slug -> number, real PK,
  bounded `(created_at,id)` query and signed public-route/page-size-bound cursor.
- `content/migrations/0002_grade_created_at.py`: additive auto_now_add timestamp,
  deterministic shared legacy tracking epoch, existing IDs/references preserved.
- `content/test_grades_api.py`, `content/test_grade_migrations.py`: 11 tests for
  catalogue, cursor integrity, safe failures, no writes, onboarding and upgrade.
- `specs/api/MS7-V02-grades-runtime.md`, this trace and active plan.

Modified:

- `config/urls.py`: mount Content API before existing Identity API.
- `content/models.py`: Grade.created_at; old ordering/fields preserved.
- `content/test_bootstrap.py`: verify timestamps survive repeated bootstrap.
- `users/http.py`: compatibility exports preserve V02 imports/transport bytes.
- `users/tests/test_migrations.py`: use actual current Content state for the
  Users-only upgrade drill; retain all existing preservation assertions.

Deleted: none. No dependencies, applied migrations, frozen R02A files, curriculum,
site sources, UI, Progress or LLM behavior changed.

## Reproducible environment and commands

Host Windows interpreter `C:/Projects/MathStart-Python/.venv312/Scripts/python.exe`;
Python 3.12.10, pip 26.2.1, Django 5.2.16, DRF 3.18.1, jsonschema 4.26.0,
psycopg/psycopg-binary 3.3.6. Existing lock environment, `pip check` PASS; no package
updates made. Git 2.47.0.windows.1, Docker client/engine 29.8.1, Compose 5.5.1,
PostgreSQL `server_version_num=160015` (16.15).

Verification-only overrides (credentials inherited locally, never printed):

```text
PYTHONUTF8=1
DJANGO_DB_NAME=ms6_v01_smoke_grades_23_20261004
DJANGO_DB_HOST=127.0.0.1
DJANGO_DB_PORT=55423
DJANGO_DB_TEST_NAME=test_ms7_grades_23
DJANGO_RUNTIME_ROOT=C:/Projects/MathStart-Python/var/grades-23
```

```text
git fetch origin main
git switch -c codex/ms7-v02-grades-api
docker compose -p ms7-grades-23-20261004 up -d --wait db
python scripts/check_database.py
python manage.py makemigrations --check --dry-run
python manage.py test content.test_grades_api content.test_grade_migrations users --noinput
python -m unittest discover -s tests -p test_r02a_contract.py -v
python scripts/fresh_install_smoke.py --disposable
python scripts/verify_repo.py
python scripts/version_report.py
git diff --check
```

All Python commands used the above configured interpreter. Existing developer
runtime/database were not migrated/reset. Django tests used disposable test
storage; fresh-install smoke used the initially empty disposable runtime DB.
Local generated logs: ignored `var/grades-23/fresh-smoke.log` and `verify-repo.log`.

## Verification and acceptance

| Check | Actual result |
| --- | --- |
| pip check | PASS; no broken requirements |
| PostgreSQL connection | PASS; server 160015 |
| makemigrations --check --dry-run | PASS; no changes |
| Targeted catalogue/upgrade/Users | PASS; 61 tests, 55.851 s, no skips |
| R02A contract suite | PASS; 30 tests, 2.069 s; 17 frozen artifact pins valid |
| Fresh PostgreSQL smoke | PASS; exit 0; new migration, migrate --check, two bootstraps, content/media identities and user preservation |
| collectstatic in fresh smoke | PASS; 171 copied, 495 post-processed |
| Lesson sources | PASS; 263 match |
| Content quality | PASS; 281 pages, 840 SVG, zero problems |
| Site integrity | PASS; 281 materials, 263 topics, 29 media, 1685 references, zero error counters |
| Canonical verify_repo | PASS; exit 0, 8/8 checks |
| Full Django suite in canonical | PASS; 90 tests, 105.087 s, no skips |
| R03 suite in canonical | PASS; 18 tests, 0.018 s |
| Harness suite in canonical | PASS; 73 tests, 17.749 s |
| Bootstrapped catalogue GET | PASS; schema-valid, ID/number pairs (1,5), (2,6), (3,7), (4,8), (5,9), (6,10) |
| Whitespace / frozen-source diff | PASS; no whitespace errors or changes in frozen artifacts/applied migrations/sources/dependencies |
| Remote CI | PENDING; PR not yet created at time of this evidence update |
| Руслан review / migration approval | PENDING |
| I03 handoff acceptance / merge | PENDING |

Upgrade test preserves Grade fields/PK, Subject FK, user and completed profile.
DTO tests distinguish grade number from PK; cursor tests cover ties, row deletion,
edits, later insertion, tampering, route/page-size binding and invalid parameters.
GET SQL/snapshots show no catalogue/identity writes or missing-profile creation.
Real-CSRF onboarding accepts the returned id for all three modes.

## Remaining gates and handoff

No known blocking implementation/test failure remains. Plans remain active and
final task status INCOMPLETE pending remote CI, Руслан review, I03 handoff and
merge. The runtime spec contains the I03 integration instructions and a synthetic
response; documentation preparation does not claim that Илья accepted it.
No human acceptance or Issue closure is inferred.
