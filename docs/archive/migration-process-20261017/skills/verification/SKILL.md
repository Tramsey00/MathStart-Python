# Verification Skill

## Current migration adapter (MS7-MIG-R03)

For migration acceptance use `python scripts/verify_repo.py --profile target`.
The explicit `--profile pure` runs only portable domain/model/Harness checks,
with `specs/migration/r03-v1/verification.lock`; it does not establish runtime
or PG/browser parity. The transitional default remains legacy for frozen ci.yml.
Absent owner locks/commands, empty suites, skips and timeout are failures.
See [current adapter contract](../../specs/migration/r03-v1/README.md),
[active plan](../../docs/exec-plans/active/MS7-MIG-R03.md) and
[trace](../../docs/agent-traces/MS7-MIG-R03.md). Final default cutover and full
target evidence remain pending accepted integration; historical guidance below
describes the preserved Django baseline, not target acceptance.

## Purpose

Use this skill when a coding-agent task reaches its verification phase.

The objective is to run the checks that are relevant to the changed area, report
observable results, fix failures that are inside task scope, and never declare a
task complete while a blocking check is failing.

---

## Inputs

Before verification, inspect:

1. `AGENTS.md`
2. the active spec
3. the active exec plan
4. the changed files
5. relevant tests/migrations

Do not guess which checks are required when the task documents already define
them.

---

## Baseline command

Run from the repository root with the project virtual environment activated
and dependencies installed with `python -m pip install --no-deps -r requirements.lock`;
then run `python -m pip check`. See `README.md` for setup.
Confirm `python --version` and record the actual interpreter in the trace.
The accepted v3.1 target is Python 3.12+; an older local environment must be
reported and does not establish verification on that target.

Content checks read the configured local database and runtime media. They
require an already migrated, bootstrapped site. They write diagnostic reports
under `DJANGO_RUNTIME_ROOT/var/reports` (repository `var/reports` by default);
Django tests use a separate test database.
The verification script does not migrate or bootstrap the local database.
If setup is missing, report it rather than changing data during an audit that
forbids database changes.

The entry point runs runtime checks and the Harness suite, including manifest
digest validation. Audit wider document links and human acceptance separately.

The Harness verification entry point is:

```bash
python scripts/verify_repo.py
```

`.github/workflows/ci.yml` runs this same entry point for pull requests to
`main` and pushes to `main`. The MS6-V01 workflow installs the full version lock,
uses an isolated PostgreSQL 16 service, reports actual versions, checks a failed
connection and runs `python scripts/fresh_install_smoke.py --disposable` before
the Harness. Smoke migrates an empty PostgreSQL database, bootstraps twice,
collects static, verifies content/media/identities and unchanged source materials.
A green CI job is required before merge; configuration alone is not a passing run.
See `docs/runbooks/postgres-dev-test.md` for disposable environment commands.

For a faster pass without the Django, R03, and Harness test suites:

```bash
python scripts/verify_repo.py --skip-tests
```

To run selected groups:

```bash
python scripts/verify_repo.py --group backend
python scripts/verify_repo.py --group database
python scripts/verify_repo.py --group content
python scripts/verify_repo.py --group tests
python scripts/verify_repo.py --group harness
```

Multiple groups may be combined. Default selection runs 8 checks across 5 groups.
`--list` shows selected argv commands; `--exclude-group` removes a group.
The runner's nested `repo-baseline` uses `--exclude-group harness` (7 checks),
while its separate `harness-unit` runs the Harness suite. This prevents recursive
verification. Normal CI keeps the default selection including Harness tests.

---

## Configured verification groups

### Backend

```bash
python manage.py check
```

### Database consistency

```bash
python manage.py makemigrations --check --dry-run
```

This does not replace the PostgreSQL fresh-database migration smoke.

### Existing content

```bash
python manage.py check_lesson_sources --all
python manage.py check_content_quality
python manage.py check_site_integrity
```

### Tests

```bash
python manage.py test
python -m unittest discover -s tests -p test_r03_contract.py
```

The second command is the R03 contract/reference suite. It uses only the Python
standard library and specification JSON fixtures; it does not need Django
models, a database, PostgreSQL, or a live LLM. `scripts/verify_repo.py` runs it
under the `tests` group after the Django suite. A passing contract suite proves
the documented graph/projection reference behavior, not runtime persistence.

---

### Harness

```bash
python -m unittest discover -s tests/harness -t . -v
```

This group uses deterministic adapters and mocked runner verification; no live
LLM or task-branch checkout is required. The CLI smoke dry-run uses a fixture.
Production TaskManifest branch enforcement is tested separately and retained.

## Future checks

MathStart v3.1 also requires additional verification as the corresponding
subsystems are implemented.

Examples:

- Ruff
- mypy
- pytest / pytest-django
- persisted knowledge graph validation after the Django Knowledge app exists
- exercise contract validation
- public exercise DTO secret-leak regression
- frontend lint/unit checks
- Playwright E2E
- LLM structured-output validation
- Solution Analyzer golden eval subset
- architecture/dependency guardrails

Do not report these as passing until the repository actually configures and
executes them.

When a new check becomes real project tooling, add it to the appropriate
verification workflow in a dedicated reviewed change.

---

## Workflow

For MS6-V01 also run `python scripts/check_database.py`,
`python scripts/version_report.py`, and the disposable PostgreSQL smoke described
above. A failed connection must return nonzero without credentials; the diagnostic
has a 35-second deadline. Record Docker/Compose versions separately.
`content.test_postgres_publication` includes real transaction/connection tests;
SQLite skips do not establish PostgreSQL locking correctness. The current V01
trace records whether those checks have actually run. Do not use
`bootstrap_site --dry-run` as evidence that no SQL writes occurred.

1. Determine the affected areas.
2. Run narrow checks first when useful.
3. If a relevant check fails, inspect the failure.
4. Fix failures introduced by the task when they are in scope.
5. Re-run the failed check.
6. Run the broader required verification before completion.
7. Record final observable results in the task trace.

Do not suppress or skip a failing check merely to obtain a green result.

---

## Failure classification

When a check fails, classify it as one of:

- introduced by this task;
- pre-existing repository failure;
- environment/configuration failure;
- missing/not-yet-configured tooling;
- external dependency failure.

Record the classification in the trace.

A pre-existing or environment failure must still be reported; it must not be
presented as a pass.

---

## Trace output

For a significant task, the trace should contain a concise verification table,
for example:

```text
python manage.py check                       PASS
python manage.py makemigrations --check     PASS
python manage.py check_content_quality       PASS
python manage.py check_site_integrity        PASS
python manage.py test                        PASS
```

Use `N/A` only when a check genuinely does not apply.

Never invent command results.

---

## Done rule

Verification is complete only when:

- all blocking checks relevant to the task have passed; or
- a blocking external/pre-existing issue has been explicitly surfaced and the
  task is marked `BLOCKED`/`INCOMPLETE` rather than `COMPLETE`.

The verification skill does not override human gates defined by `AGENTS.md`,
specs, exec plans, or ADRs.
