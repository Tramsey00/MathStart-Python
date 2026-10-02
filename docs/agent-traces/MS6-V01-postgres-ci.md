# TRACE MS6-V01: PostgreSQL dev/test and CI

- **Date:** 2026-09-26
- **Task ID:** MS6-V01
- **Owner:** Vladimir
- **Coding agent / surface:** Codex, Windows execution sandbox
- **Related issue:** [#13](https://github.com/Tramsey00/MathStart-Python/issues/13); no Issue operations performed
- **Related spec:** PRODUCT.md; acceptance in active plan and user task
- **Related exec plan:** docs/exec-plans/completed/MS6-V01-postgres-ci.md
- **Related ADR:** docs/adr/ADR-0001-preserve-django.md
- **PR / commits:** [#14](https://github.com/Tramsey00/MathStart-Python/pull/14) / initial `5092685` / published integration `b3e70a8`
- **Latest reconciliation:** 2026-09-28; sections 1-25 are historical snapshots, section 26 records published integration and post-push CI
- **Human review status:** Final Ruslan approval/acceptance pending

## 1. Task

Implement minimal PostgreSQL dev/test configuration, real dependency lock,
Docker/CI, guarded fresh-install smoke, safe diagnostics/version report and
documentation. Preserve SQLite compatibility and source materials. Do not edit
publishing until its PostgreSQL locking issue is actually reproduced. Do not
create/change Issues, PRs, commits, push or merge.

## 2. Inputs used

AGENTS.md, PRODUCT.md, ARCHITECTURE.md, ADR-0001, R02/R03 contract boundaries,
completed plans/traces, plan/trace templates, verification skill/script, README,
content architecture, settings, requirements, env example, initial migration,
bootstrap/publishing services/commands, static config, CI and existing tests.
The user confirmed their CMD .venv is Python 3.12.10; agent launcher limitations
are not a broken user environment and did not drive the infrastructure design.
Exact NFR-10/NFR-11 text was not supplied and is not invented here.

## 3. Initial repository state

Branch: ms6-v01-postgres-ci. HEAD and local origin/main:
e410a4e29de2eb800b3325667df94b200bdae22b. Working tree clean; no fetch.
Existing direct requirements pinned, SQLite-only settings, seven-check Harness,
SQLite CI, bootstrap/publication tests. No Docker/lock/PostgreSQL driver.

## 4. Files changed

Added: active plan, this trace, runbook; config/database.py; Dockerfile,
compose.yaml, .dockerignore; requirements.lock; lock_dependencies.py,
check_database.py, version_report.py, fresh_install_smoke.py under scripts;
content/test_infrastructure.py and content/test_postgres_publication.py.

Modified: requirements.txt, .env.example, config/settings.py, CI workflow,
two content-check report destinations, README, verification skill and current
architecture/repository-map documentation. No files deleted. Lock generated from
a real pip report. Ignored var/ contains agent-only venv, reports and SQLite
verification runtime. User .venv/.env/database were not modified.

## 5. Commands / tools executed

Read-only git branch/status/HEAD/diff checks and repository reads preceded edits.
Package resolution used this available agent interpreter:

```powershell
$agentPython = 'C:/Users/vladimir/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $agentPython --version
& $agentPython -m pip --version
& $agentPython -m pip install --dry-run --ignore-installed --no-cache-dir --report var/v01-dependency-resolution.json -r requirements.txt 'psycopg[binary]'
& $agentPython -m venv var/v01-venv
& $agentPython scripts/lock_dependencies.py var/v01-dependency-resolution.json
var/v01-venv/Scripts/python.exe -m pip install --no-cache-dir -r requirements.lock
var/v01-venv/Scripts/python.exe -m pip install --dry-run --ignore-installed --only-binary=:all: --platform manylinux2014_x86_64 --python-version 3.12 --implementation cp --abi cp312 --report var/v01-linux-resolution.json -r requirements.lock
```

Initial network resolution was blocked by sandbox WinError 10013; the same
resolution was retried through approved escalation and succeeded. Installation
and Linux-target resolution likewise used approved network access. No fake lock
or inferred package versions were used.

Verification environment (process only):

```powershell
$env:DJANGO_DB_BACKEND='sqlite'
$env:DJANGO_DB_PATH=(Join-Path (Get-Location) 'var/v01-verification.sqlite3')
$env:DJANGO_SECRET_KEY='v01-agent-check-only'
$env:DJANGO_DEBUG='False'
$env:DJANGO_RUNTIME_ROOT=(Join-Path (Get-Location) 'var/v01-runtime')
var/v01-venv/Scripts/python.exe --version
var/v01-venv/Scripts/python.exe -m pip check
var/v01-venv/Scripts/python.exe manage.py test content.test_infrastructure --noinput
var/v01-venv/Scripts/python.exe manage.py check
var/v01-venv/Scripts/python.exe manage.py makemigrations --check --dry-run
var/v01-venv/Scripts/python.exe manage.py migrate --noinput
var/v01-venv/Scripts/python.exe manage.py bootstrap_site
var/v01-venv/Scripts/python.exe manage.py collectstatic --noinput
var/v01-venv/Scripts/python.exe scripts/verify_repo.py
var/v01-venv/Scripts/python.exe scripts/version_report.py
var/v01-venv/Scripts/python.exe scripts/fresh_install_smoke.py --disposable
var/v01-venv/Scripts/python.exe manage.py bootstrap_site
```

The smoke invocation deliberately used SQLite and correctly refused with exit 1.
It is a guard check, not successful PostgreSQL smoke. Bootstrap was repeated after
the full Harness and reported zero new catalogue/content/media rows/files.
Infrastructure tests were rerun after the smoke guard correction and passed.

Negative connection check used process-only PostgreSQL configuration, localhost
port 1, disposable database/user names and a sentinel fake password. Both
`scripts/check_database.py` and `scripts/version_report.py` returned exit 1 with
readable connection diagnostics, without printing the sentinel or DSN. This
tests the failure path only; no successful PostgreSQL connection is claimed.

`Get-Command docker,psql -ErrorAction SilentlyContinue` found neither tool on the
agent PATH; inspected standard installation directories were absent. No Docker
daemon/PostgreSQL server was provisioned. No GitHub CLI is required or used.

## 6. Implementation summary

PostgreSQL is explicit/default with required fields, validated port/timeout and
separate test DB; SQLite is opt-in and never a fallback. Runtime paths isolate
media/static/reports/backups. Diagnostic child process has a 35-second deadline,
suppresses raw driver errors, and verifies server version >=16 on successful PG
connections. Version reporting enumerates installed locked packages only.

Compose uses PostgreSQL 16 healthcheck, local-only ports and project-scoped
volumes. Container is a non-root development server; secrets are runtime-only.
CI installs the lock with --no-deps, checks dependencies, reports versions,
tests connection failure, then runs fresh PostgreSQL smoke and unchanged Harness.

Smoke refuses wrong/nonempty targets before migration, runs two real bootstraps,
compares counts, PK/FK/content/media and an existing user, collects the manifest,
runs content checks and hashes source materials before/after. No fake migrations,
schema SQL, global resets, domain apps, LLM calls or production setup were added.

## 7. Observable failures / incidents

| Failure | Classification | Impact |
| --- | --- | --- |
| pip sandbox network WinError 10013 | Environment/network restriction | Resolved by approved retry; lock resolution completed |
| First infrastructure test teardown: function has no attribute wrapped | Introduced test fixture error | Patched DB proxy method conflicted with SimpleTestCase guard |
| PostgreSQL/Docker tools unavailable on agent PATH | Environment/tooling limitation | Runtime PostgreSQL/Docker/CI acceptance NOT VERIFIED |

## 8. Root cause summary

The test patched connection.cursor directly while SimpleTestCase wraps it to
prohibit DB access. Restoration conflicted with the wrapper teardown.
PostgreSQL nullable outer-join select_for_update remains a code-inspection risk,
not a reproduced failure in this execution environment.

## 9. Corrections made

Mocked the connection proxy instead; all seven infrastructure tests then passed.
Smoke now rejects wrong backend/name/runtime before opening a database, avoiding
SQLite file creation as a side effect of an invalid target. PostgreSQL contender
test explicitly orders by PK to avoid adding nullable ordering joins itself.
Publishing implementation remains untouched per the reproduction prerequisite.

## 10. Initial agent verification results and version report (historical snapshot)

| Check | Actual result |
| --- | --- |
| Agent Python / resolver pip | 3.12.14 / 26.2.1 |
| Isolated verification Python / pip | 3.12.14 / 25.0.1 |
| Actual installed Django / psycopg / psycopg-binary | 5.2.16 / 3.3.6 / 3.3.6 |
| Remaining resolved versions | asgiref 3.12.1, beautifulsoup4 4.15.0, python-dotenv 1.2.2, soupsieve 2.10, sqlparse 0.6.0, typing-extensions 4.16.0, tzdata 2026.3, whitenoise 6.12.0 |
| Windows lock install and Linux cp312 x86-64 wheel resolution | PASS |
| pip check | PASS, no broken requirements |
| Django check | PASS on explicit SQLite |
| makemigrations --check --dry-run | PASS, no changes detected |
| SQLite fresh migrate/bootstrap | PASS; 263 lessons, 29 media |
| SQLite repeated bootstrap | PASS; all creation/copy counters zero |
| collectstatic DEBUG=False | PASS; 140 copied, 420 post-processed |
| Harness | PASS 7/7 on SQLite compatibility path |
| Django suite | 24 tests, OK with 2 PostgreSQL-only skips (not PG passes) |
| R03 contract suite | PASS, 18 tests |
| check_lesson_sources | PASS, 263 |
| check_content_quality | PASS, 281 pages / 840 SVGs / zero issues |
| check_site_integrity | PASS, 1685 references / zero issues |
| SQLite smoke rejection | PASS, expected exit 1 |
| Failed PostgreSQL connection diagnostic/report | PASS failure path, expected exit 1, no sentinel secret |
| Version report on SQLite | PASS; explicitly labels SQLite compatibility |
| Fresh PostgreSQL migration/bootstrap/content/static smoke | NOT VERIFIED |
| PostgreSQL transaction/locking regressions | NOT VERIFIED, skipped on SQLite |
| Docker build/Compose startup | NOT VERIFIED |
| GitHub Actions execution | NOT VERIFIED; no push/PR authorized |
| git diff --check | PASS |
| Final AST parse of seven new Python files | PASS |
| Windows/Linux resolved package-name/version sets | Identical |
| Source/migration/publishing diff | Empty |

## 11. Initial implementation diff summary (historical snapshot)

Infrastructure/config/docs/tests only, plus relocation of generated content
reports. Existing content sources, templates/static, models, migrations,
publishing implementation and scripts/verify_repo.py are preserved.
Final git status: 11 modified tracked files and 14 new untracked files. Tracked
git diff --stat: 11 files changed, 126 insertions, 49 deletions; ordinary diff
--stat does not include the 14 untracked additions. No staging or commits.

## 12. Acceptance criteria result

| Criterion | Result | Evidence |
| --- | --- | --- |
| Python 3.12+ and real dependency lock | PASS | Agent execution and pip resolution/install |
| Safe env, explicit backend, bounded redacted diagnostics | PASS for tested configuration/failure paths | Seven unit tests and negative process check |
| Clean PostgreSQL restore from repo | PASS | User-executed clean-volume smoke, section 19 |
| Second PostgreSQL bootstrap has no duplicates and stable identities/content/media | PASS | User-executed smoke and zero new objects, section 19 |
| Existing source materials preserved | PASS | Empty source-material diff |
| PostgreSQL publication conflicts/real locks | PASS | User PostgreSQL Harness and two targeted regressions, section 19 |
| Local Docker/PostgreSQL path | PASS | User clean-volume smoke |
| Real GitHub Actions run | NOT VERIFIED | Not executed |
| NFR-10/NFR-11 exact mapping | NOT VERIFIED | Definitions not supplied |
| Human acceptance | PENDING | Working-tree review pending |

## 13. Remaining risks / follow-ups

The original PostgreSQL locking failure, minimal correction and successful
user rerun are recorded in sections 17 and 19. Local Docker/PostgreSQL verification
is complete; real GitHub CI and human acceptance remain pending. Lock pins versions
but not artifact hashes; image tags track patch releases. Production backups,
hosting and future applications remain outside scope.

## 14. Harness improvement

Added safe smoke guards, explicit PostgreSQL locking regressions and documented
the difference between SQLite compatibility evidence and PostgreSQL acceptance.

## 15. Human review

Reviewer: project reviewer. Status: Pending. No commit/PR requested or created.

## 16. Initial implementation status (superseded by follow-up below)

INCOMPLETE: implementation prepared in working tree; PostgreSQL/Docker/CI runtime
acceptance and conditional publication correction remain outstanding. Keep the
plan active. Do not claim MS6-V01 complete from SQLite verification.

## 17. PostgreSQL outer-join failure: user reproduction and patch

The user supplied VERIFIED reproduction from their Windows CMD, with a healthy
PostgreSQL 16 Docker container, using:

```text
docker compose -p ms6-v01-smoke run --rm app python scripts/fresh_install_smoke.py --disposable
```

Smoke reached `manage.py bootstrap_site`, then `site_bootstrap.py` ->
`publish_lessons` -> `publication_plan`, failing during iteration of page_query
(approximately line 304 before this patch):

```text
django.db.utils.NotSupportedError: FOR UPDATE cannot be applied to the nullable side of an outer join
```

Evidence attribution: user-executed reproduction, not executed by the agent.
This supersedes earlier statements that the issue was only a theoretical risk.
ContentPage grade/subject/section FKs are nullable; select_related and related
ordering introduce outer joins. An unqualified FOR UPDATE attempts to lock the
nullable joined tables as well as ContentPage.

Minimal correction in content/services/publishing.py:
`page_query.select_for_update(of=("self",))`. Keep the same read joins and lock
ContentPage rows until transaction end. Separate LessonPublication state and
source-owner locks remain unchanged, as do transactional plan rebuild, digest
conflicts, identity checks, unique constraints and SQLite backup/compatibility.
No public publishing semantics, schema or source-material change.

Updated content/test_postgres_publication.py:

- Fresh creation starts without a ContentPage row, exercising the same outer-join
  locking query as fresh bootstrap; then update and idempotent replay are checked.
- A separate thread/connection must receive PostgreSQL SQLSTATE 55P03 for NOWAIT
  attempts to lock either ContentPage or LessonPublication while the plan's
  transaction holds locks, and must acquire both after transaction completion.

Only publishing.py, this regression test, the active plan and this trace changed
in this follow-up. All earlier working-tree changes remain untouched.

## 18. Agent post-patch verification (superseded by final user evidence below)

Using the same process-only SQLite environment and isolated interpreter documented
in section 5, actually executed:

```text
var/v01-venv/Scripts/python.exe --version
var/v01-venv/Scripts/python.exe -m pip check
var/v01-venv/Scripts/python.exe scripts/verify_repo.py
git diff --check
git diff --stat
```

Results: Python 3.12.14; pip check PASS; Harness PASS 7/7. Django check PASS;
makemigrations --check --dry-run reported no changes; source check 263 lessons;
quality check 281 pages/840 SVGs with zero issues; integrity 1685 references with
zero issues; Django suite 24 tests OK with two PostgreSQL-only skips (19.950s);
R03 18 tests PASS. SQLite publishing/conflict/bootstrap tests remain green.

Agent Docker/psql command discovery still found no executable on PATH.
Post-patch PostgreSQL regression, Docker fresh-install smoke and PostgreSQL
Harness: NOT VERIFIED. The user will rebuild the app image and rerun with a new
disposable database/runtime; the failed smoke already applied migrations, and
the smoke correctly refuses a nonempty database. No reset/schema workaround is
part of this patch. No commit, push, merge or PR operation was performed.

Current status: patch prepared; MS6-V01 remains INCOMPLETE pending real
PostgreSQL rerun and human acceptance. Initial failure reproduction is VERIFIED;
successful PostgreSQL execution after the patch is not yet verified.

## 19. Final user-executed PostgreSQL verification

Evidence attribution: the following results were supplied by the user from
Windows CMD through Docker Compose, not executed by the agent. This final
evidence supersedes PostgreSQL NOT VERIFIED entries in the earlier snapshots.

The user additionally executed:

```text
docker compose -p ms6-v01-smoke run --rm app python manage.py test content.test_postgres_publication --noinput
```

Reported result: Found 2 test(s), System check identified no issues, Ran 2 tests,
OK. The test database was created and deleted normally. This verifies both
PostgreSQL-specific publication regressions after the page-only FOR UPDATE fix.

The user's final report also confirms:

| Check | User-reported result |
| --- | --- |
| Fresh disposable PostgreSQL smoke on clean volume | PASS |
| Existing migrations, no manual/fake repair | PASS |
| makemigrations --check --dry-run | No changes detected |
| First bootstrap | Full catalogue/content created |
| Second bootstrap | 0 new catalogue/pages/redirects/lessons/media objects |
| Smoke stable identities/content/media and unchanged repository materials | PASS within the reported smoke |
| collectstatic | PASS |
| Lesson source check | PASS: 263 lessons |
| Content quality | PASS: 281 pages, 840 SVG, 0 problems |
| Site/content integrity | PASS: duplicate/broken/empty counters all 0 |
| python scripts/verify_repo.py on PostgreSQL | RESULT PASS 7/7 |
| check_database.py | PostgreSQL connection OK; server_version_num=160015 |
| version_report.py | Python 3.12.14, Django 5.2.16, psycopg/psycopg-binary 3.3.6, PostgreSQL connection OK; no secrets/DSN/password printed |
| Targeted PostgreSQL publication tests | 2 tests, OK, normal test DB lifecycle |

No new functional change was made in this final recording/review turn. Only this
trace and the active exec plan were updated. Runtime suites were not rerun for
these documentation-only changes. Earlier agent SQLite/failure-path evidence
remains separately attributed in sections 5, 10 and 18.

## 20. Cumulative diff review and remaining gates

Reviewed tracked cumulative diffs and all 14 untracked additions, including
configuration, containers, CI, lock/scripts, tests, runbook and task records.
No unrelated domain/app/schema/content rewrite, production deployment, real
credential, generated runtime output or tracked .env/database/media/staticfiles/
var artifact was found in the proposed changes. CI credentials are explicitly
disposable job-local values; env example and tests contain placeholders/sentinels.
Docker build excludes .env and generated runtime paths. Existing source
materials and migrations remain unchanged. The generated dependency lock is an
intentional deliverable, not an accidental runtime artifact.

The earlier README/runbook stale PostgreSQL pending wording was corrected in the
final documentation cleanup. Exact NFR-number mapping was not invented.

No new functional blocker identified. Real GitHub Actions run remains
NOT VERIFIED and human acceptance remains PENDING. Status: ready for CI/human
review, not COMPLETE. Plan stays active; no commit, push, merge or PR operation.

## 21. Final documentation cleanup and pre-commit audit

Only README.md, docs/runbooks/postgres-dev-test.md, the active plan and this trace
were updated. Setup documentation now reflects successful local Docker/PostgreSQL
verification; earlier agent-only results remain labelled historical snapshots.
No code, tests, dependencies, migrations, database settings, containers or CI
configuration changed in this cleanup. No runtime suite was rerun for these edits.

User-executed commands recorded across the reports (not agent execution):

```text
docker compose -p ms6-v01-smoke run --rm app python scripts/fresh_install_smoke.py --disposable
python manage.py makemigrations --check --dry-run
python scripts/verify_repo.py
python scripts/check_database.py
python scripts/version_report.py
docker compose -p ms6-v01-smoke run --rm app python manage.py test content.test_postgres_publication --noinput
```

The first smoke reproduced the nullable outer-join FOR UPDATE failure; after
`select_for_update(of=("self",))`, a new clean-volume smoke passed completely.
The detailed successful results are in section 19. These do not imply a GitHub
Actions run or completed human review.

Cumulative audit includes all untracked V01 deliverables, not only tracked diff.
Repository .gitignore excludes .env, .venv, var/, runtime media/staticfiles and
Python caches. Agent venv/reports/SQLite verification files live under ignored
var/. Docker volumes are outside the checkout; .dockerignore excludes local
env/runtime/cache inputs while retaining .env.example. No tracked .env, runtime
database, cache, virtualenv, volume data or temporary report is part of the diff.
Explicit CI-only credentials and test sentinels are not production secrets.
No unrelated changes or new functional blocker were identified. Final gates
remain real GitHub Actions execution and human review/acceptance; plan stays active.

## 22. Post-publication evidence and R04 reconciliation (2026-09-28)

Publication metadata supplied by the user: Issue #13, PR #14, implementation
commit `5092685`; [Actions run 36272397590](https://github.com/Tramsey00/MathStart-Python/actions/runs/36272397590)
result SUCCESS. No API query or Actions execution by the agent is implied.
This is separate post-publication evidence, not a rewrite of the earlier
NOT VERIFIED snapshots. R04 #10 was merged into main at `9f705b0`.

Initial commands: `git branch --show-current`, `git status`,
`git diff --name-only --diff-filter=U`, `git diff -- requirements.txt`,
`git rev-parse HEAD MERGE_HEAD origin/main`, and inspection of index stages
`:2:requirements.txt` / `:3:requirements.txt`.
Observed branch `ms6-v01-postgres-ci`, HEAD
`5092685968eff4c9bcab44b92f2ecb017f653e80`, MERGE_HEAD and origin/main
`9f705b0eb161b411cae56111cfb48ff6826b6a45`; only requirements.txt unmerged.
The merge was already in progress. Incoming R04 and I01 files are main's
changes, not new V01 scope introduced by this agent.

The working requirements file keeps all five common pins plus
`psycopg[binary]==3.3.6` (V01) and `jsonschema==4.26.0` (R04 contracts).
No duplicate entries or conflict markers remain. Lock regeneration added
attrs 26.1.0, jsonschema 4.26.0, jsonschema-specifications 2025.9.1,
referencing 0.37.0 and rpds-py 2026.6.3; all previous versions were retained.

Actual dependency commands used Python 3.12.14 from
`C:/Users/vladimir/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`
(pip 26.2.1) for resolution/generation. Direct use of requirements.lock as a
constraint failed because pip rejects extras in constraints. An ignored copy
`var/v01-r04-constraints.txt` replaced only `psycopg[binary]` with `psycopg`.
The first network attempt failed with WinError 10013 in the sandbox; the
approved retry against the package index succeeded. No failed report was used
to fabricate a lock. Successful commands:

```text
python -m pip install --dry-run --ignore-installed --no-cache-dir --report var/v01-r04-resolution.json -r requirements.txt -c var/v01-r04-constraints.txt
python scripts/lock_dependencies.py var/v01-r04-resolution.json
var/v01-venv/Scripts/python.exe -m pip install --no-deps --no-cache-dir -r requirements.lock
var/v01-venv/Scripts/python.exe -m pip install --dry-run --ignore-installed --only-binary=:all: --platform manylinux2014_x86_64 --python-version 3.12 --implementation cp --abi cp312 --report var/v01-r04-linux-resolution.json -r requirements.lock
var/v01-venv/Scripts/python.exe -m pip check
```

All successful commands above exited 0. The verification venv uses Python
3.12.14 / pip 25.0.1. A read-only assertion compared the 7 direct pins, all
16 lock pins, installed metadata and both resolution reports: PASS.

Full semantic comparison of skills/verification/SKILL.md against HEAD and
origin/main found both V01 database/setup/smoke requirements and R04's canonical
8-check workflow retained. No manual skill change was needed. CI still runs
the default verify_repo entry point, now including Harness; nested Harness
verification retains its recursion guard. No CI check was removed.

Initial `python -m unittest discover -s tests/harness -t . -v`: FAIL,
73 tests, one error: the checked-in R04 manifest expected the pre-V01
ARCHITECTURE.md digest. The only manifest correction replaces that digest with
the current file's SHA-256 `eabea31580574b8f1cc5e3d38222e404be81f37837c2eb04988c60bb2bcbb42c`.
The existing reference-bytes regression then passed within canonical verification.
No functional application code or tests changed; publication retains
`select_for_update(of=("self",))` and the separate publication locks.

Agent runtime checks used `var/v01-venv/Scripts/python.exe`, explicit
DJANGO_DB_BACKEND=sqlite, DJANGO_DB_PATH pointing to the new isolated
`var/v01-r04-verification.sqlite3`, DJANGO_RUNTIME_ROOT pointing to
`var/v01-r04-runtime`, DJANGO_DEBUG=False and a disposable diagnostic-only
secret. No user's database or runtime was used.

| Command / check after correction | Actual result |
| --- | --- |
| python manage.py migrate --noinput | PASS, full migration chain on empty SQLite DB |
| python manage.py bootstrap_site (twice) | PASS; first populated catalogue/content/media; second created/changed 0 |
| python manage.py collectstatic --noinput | PASS, 140 copied / 420 post-processed |
| python scripts/verify_repo.py | PASS, 8/8 canonical checks |
| Included: python manage.py check | PASS, no issues |
| Included: python manage.py makemigrations --check --dry-run | PASS, No changes detected |
| Included: python manage.py check_lesson_sources --all | PASS, 263 lessons |
| Included: python manage.py check_content_quality | PASS, 281 pages / 840 SVG / 0 problems |
| Included: python manage.py check_site_integrity | PASS, duplicate/broken/empty counters 0 |
| Included: python manage.py test | PASS, 24 tests, 2 PostgreSQL-specific skips |
| Included: python -m unittest discover -s tests -p test_r03_contract.py | PASS, 18 tests |
| Included: python -m unittest discover -s tests/harness -t . -v | PASS, 73 tests |
| python scripts/version_report.py | PASS, Python 3.12.14, Django 5.2.16, psycopg/binary 3.3.6, all 16 packages installed; explicitly SQLite connection OK |
| python scripts/check_database.py with PostgreSQL, 127.0.0.1:1, timeout 2 and disposable sentinel credentials | PASS expected failure: exit 1, readable diagnostic, no credential values or fallback; command elapsed about 3.2 seconds |
| New PostgreSQL fresh smoke / positive diagnostic / locking regressions | NOT VERIFIED: Docker and psql not available in agent PATH; standard Docker executable path absent |

Logs/reports and runtime are ignored under var/. No Docker project/volume was
created, so no Docker cleanup was performed. Earlier user-executed PostgreSQL
smoke and two locking tests remain historical PASS, not a rerun of this merge.

Review audit compared the V01 cumulative diff against origin/main and incoming
merge changes against HEAD. Source materials and migrations have no changes.
No new runtime, cache, virtualenv, tracked .env, credentials or unrelated agent
edits were found. Explicit CI-only values and test sentinels remain nonproduction.
.gitignore and .dockerignore exclude the generated runtime paths. README's
setup text already links to separate evidence/statuses and needed no edit.

Current pending gates: integrated PostgreSQL revalidation, future post-push
Actions run, and final Ruslan acceptance. Pre-R04 Actions is SUCCESS, not pending.
Plan stays active. Git diff --check passed; the working requirements contents
are resolved, but index requirements.txt remains UU intentionally. No git add,
commit, push, merge completion, rebase, Issue or PR operations were performed.

## 23. Post-R04 Docker verification: missing Git executable

Evidence supplied by the user after rebuilding the integrated image:
fresh PostgreSQL smoke PASS; canonical Docker verify_repo ran eight checks,
passed seven and failed the Harness suite. The reported traceback ends in
FileNotFoundError: [Errno 2] No such file or directory: 'git', through
harness/runner/repository.py subprocess.run. These are user-executed results,
not agent Docker execution. The supplied report did not give a new Actions run.

Inspection confirmed Dockerfile installed only the locked Python packages;
Compose supplied no Git executable. R04 calls the real Git CLI, including in
temporary-repository tests. This is a V01 image dependency omission exposed by
R04, not a reason to mock Git or weaken canonical verification.

Correction: immediately after the existing Python Bookworm FROM, one RUN layer
performs apt-get update, apt-get install -y --no-install-recommends git,
git --version and removal of /var/lib/apt/lists/*. Only Git is explicitly
requested; apt installs its required dependencies. The version follows the
existing Debian Bookworm patch stream, not an invented version pin or a claim
of bit-for-bit reproducibility. Git version is checked during build and recorded
with a separate runbook command. version_report.py retains its Python/package/DB
contract. No application code, tests, Compose, requirements/lock, R04 manifest,
database settings or CI configuration changed in this correction.

Files changed this follow-up: Dockerfile, PostgreSQL runbook, active V01 plan,
and this trace. Earlier evidence remains historical. The runbook now distinguishes
successful integrated PostgreSQL smoke from the failed pre-fix canonical run.

Agent checks:
- Docker discovery: Get-Command docker returned no executable; Test-Path of
  C:/Program Files/Docker/Docker/resources/bin/docker.exe returned False.
- var/v01-venv/Scripts/python.exe -m unittest discover -s tests/harness -t . -v:
  PASS, 73 tests, 5.302 seconds; host execution only. Ignored log:
  var/v01-r04-git-fix-harness.log.
- Dockerfile/Compose/Harness call-site review: Git installation was missing;
  existing Python/PostgreSQL/non-root semantics and verification remain intact.
- git diff --check: PASS. Merge still has requirements.txt unmerged in the index;
  resolved working content is unchanged and contains no conflict markers.

Rebuild and full canonical Docker verification after the correction remain
NOT VERIFIED until user execution. Rebuild app, run git --version and
python scripts/verify_repo.py in the same already bootstrapped disposable
Compose project. Fresh smoke requires a new isolated project/database/runtime,
not the already populated smoke volume. No agent Docker volumes were created.
New post-push GitHub Actions and final human acceptance remain PENDING;
the earlier published run 36272397590 remains SUCCESS for its original state.
No git add, commit, merge completion, push, rebase or GitHub action was performed.

## 24. Post-R04 Docker verification: checkout context missing

User-executed follow-up evidence after rebuilding the Git-enabled image:
`git --version` was available; fresh PostgreSQL smoke PASS; canonical
`verify_repo.py` passed seven of eight checks, but Harness failed with 21 errors
among 73 tests. Reported error:
`harness.runner.repository.RepositoryError: fatal: not a git repository (or any of the parent directories): .git`.
This result is separate from section 23's earlier missing-executable failure.
The agent did not execute Docker or independently verify its output.

Inspection showed `WORKDIR /app` and `COPY . .` in Dockerfile, while
`.dockerignore` excludes `.git`. The normal Compose file has only database and
runtime named volumes; it does not bind the checkout. R04 Git calls read real
repository root, branch, HEAD, refs/ancestry, working status and diffs.
Tests intentionally cover real checkout behavior; test fixtures only mock the
specific boundaries under test. GitHub Actions runs `verify_repo.py` directly
after `actions/checkout`, which supplies `.git` there.

Added verification-only `compose.verify.yaml`. It augments `app` with a
read-only bind of this checkout's `.git` directory at `/app/.git`, refusing to
create a missing source. It sets command-scope `safe.directory=/app` for the
non-root image user and `GIT_OPTIONAL_LOCKS=0` to avoid optional index writes.
The ordinary app build and Compose services remain unchanged; no repository
history enters the image or normal app runtime. The source files inside `/app`
remain the ones copied at build, so the runbook requires rebuilding before
canonical verification. The current checkout's `.git` is a directory; linked
worktree gitfile layouts are outside this recipe's stated scope.

Agent checks performed after adding the overlay:
- `git rev-parse --git-dir` returned `.git`; hidden-directory inspection
  confirmed the source is a directory. The host's core.filemode is false.
- Host Git under the agent's different Windows user read the checkout with
  command-scope safe.directory set to its exact host path; without that
  setting Git reported dubious ownership. This supports the need for the
  overlay setting but is not a Linux container test.
- `var/v01-venv/Scripts/python.exe -m unittest discover -s tests/harness -t . -v`:
  PASS, 73 tests in 5.335 seconds, on the host only.
- Docker/Compose config and mounted verification: NOT VERIFIED in the agent
  environment because Docker executable is unavailable. PyYAML is not
  installed locally; no substitute YAML parser result is claimed.

The runbook gives the exact Compose overlay commands for a disposable
PostgreSQL project. The prior integrated fresh smoke remains PASS from user
execution; overlay Docker canonical verification, the new post-push Actions
run and final Ruslan acceptance remain PENDING. Active plan stays in active/.
No staging, commit, merge completion, rebase, push or GitHub actions performed.

## 25. Final integrated V01 + R04 Docker/PostgreSQL evidence

Evidence source: the user's final manual Docker Desktop/PostgreSQL verification
report after rebuilding the current app image with Git CLI. The agent did not
run these Docker commands. The verification-only `compose.verify.yaml` mounted
the current checkout's `.git` read-only at `/app/.git`; inside the verification
container `git rev-parse --show-toplevel` confirmed a Git checkout. The ordinary
app image/Compose configuration did not include `.git`.

| User-executed check in current integrated state | Reported result |
| --- | --- |
| Fresh disposable PostgreSQL smoke | PASS: migrations, bootstrap idempotency, identities/content/media, static and content checks |
| `python manage.py makemigrations --check --dry-run` | PASS: No changes detected |
| Initial bootstrap | 6 classes, 12 subjects, 63 sections, 18 pages, 280 redirects, 263 lessons, 29 media |
| Second bootstrap | 0 new/changed catalogue, pages, redirects, lessons or media |
| `collectstatic` | PASS: 140 copied, 420 post-processed |
| Lesson sources | PASS: 263 lessons match database |
| Content quality | PASS: 281 pages, 840 SVG, 0 problems |
| Site integrity | PASS: 281 materials, 263 topics, 29 media, 1685 references; all error counters 0 |
| `python scripts/verify_repo.py` in Docker verification environment | PASS: 8/8 (Django check, migration consistency, three content checks, Django tests, R03 suite, Harness suite) |
| Harness suite within canonical verification | PASS: 73 tests |
| `python manage.py test content.test_postgres_publication --noinput` | PASS: Found 2 tests, Ran 2 tests, OK |
| `python scripts/check_database.py` | PASS: PostgreSQL connection OK, server_version_num=160015 |

The initial post-R04 Docker canonical failure from missing Git CLI (section 23)
and the next failure from missing `/app/.git` (section 24) remain factual,
separate earlier runs. Git installation and the verification-only Compose
overlay addressed them; the subsequent complete canonical run is PASS.

At that stage, integrated local PostgreSQL acceptance was PASS based on user execution.
Pre-R04 published Actions run 36272397590 remains SUCCESS as separate evidence.
At that stage, merge completion/commit, push, a new post-push GitHub Actions
run and final Ruslan human acceptance were PENDING. The plan remained active/.

## 26. Published integration and successful post-push CI

Evidence source: Ruslan's subsequent PR #14 review and the user's supplied
publication details. Local `git rev-parse --short HEAD` returned `b3e70a8`,
and `git log -1` showed `fix(v01): reconcile R04 Docker verification and record
PostgreSQL acceptance`. The integration commit was pushed. Ruslan reported
[GitHub Actions run 36362335237](https://github.com/Tramsey00/MathStart-Python/actions/runs/36362335237)
SUCCESS and no conflicts with main. The agent did not perform a push, run
Actions or change the PR.

The reviewed integrated state retains the user-executed PostgreSQL smoke PASS,
canonical `verify_repo.py` PASS 8/8, Harness PASS 73 tests, publication locking
regression PASS 2 tests, and positive PostgreSQL connection PASS at
`server_version_num=160015`. Ruslan requested no further technical changes.
The pre-R04 Actions run 36272397590 is separate earlier SUCCESS evidence.
Sections 23-24 preserve both historical Docker Harness failures and their
corrections; older NOT VERIFIED/PENDING snapshots remain dated evidence, not
the current status.

Current status: integration committed and pushed; post-push CI SUCCESS; no
base-branch conflicts reported. Only final Ruslan human approval/acceptance
and PR #14 merge remain PENDING. The exec plan stays ACTIVE until acceptance.
