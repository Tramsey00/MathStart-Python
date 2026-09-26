# EXEC PLAN MS6-V01: PostgreSQL dev/test and CI

- **Status:** Active
- **Owner:** Vladimir
- **Created:** 2026-09-26
- **Last updated:** 2026-09-26
- **Related issue:** MS6-V01 already exists; URL not supplied. Do not create or modify it.
- **Related spec(s):** PRODUCT.md; task acceptance below
- **Related ADR(s):** docs/adr/ADR-0001-preserve-django.md
- **Target milestone:** MS6-V01 infrastructure readiness
- **Human gate required:** Yes; working-tree review pending

## 1. Objective

Provide a reproducible Python 3.12+ / PostgreSQL 16+ dev/test path from repository files, locked dependencies, isolated CI, fresh-install smoke and safe version/connection diagnostics. Preserve content and the existing Harness.

## 2. Preconditions

- [x] AGENTS.md, PRODUCT.md, ARCHITECTURE.md and accepted ADR-0001 inspected.
- [x] Completed R01-R03 plans/traces, relevant contracts, verification skill/scripts inspected.
- [x] Settings, dependencies, migration, bootstrap/publishing, static configuration and tests inspected.
- [x] User authorized implementation only in the working tree; no commit, push, merge, Issue or PR operations.
- [ ] Exact NFR-10/NFR-11 text and existing Issue URL supplied; do not invent their definitions.

## 3. Scope

Configuration, dependency lock, Docker dev/test, PostgreSQL CI, diagnostics, smoke and documentation. No production/staging deployment, future product apps, content rewrite or historical-data migration.

## 4. Current state

Branch ms6-v01-postgres-ci starts clean at e410a4e29de2eb800b3325667df94b200bdae22b. SQLite-only settings; pinned direct requirements; no lock/driver/containers. Existing CI runs Python 3.12, migrate/bootstrap/collectstatic and seven Harness checks. Existing bootstrap and publication tests are retained. User confirms their CMD .venv is Python 3.12.10; agent launcher limitations do not describe the user environment.

## 5. Target state and acceptance

Fresh disposable PostgreSQL database migrates without fake/manual schema SQL, bootstraps twice without duplicate catalogue/content/media or changed identities/content, collects static and passes content/Harness checks. Source materials remain byte-identical. Connection failure is bounded, nonzero and secret-safe. Version report records actual versions without DSN/passwords. PostgreSQL is the documented main dev/test path; explicit SQLite compatibility never acts as fallback.

## 6. Architecture boundaries

Affected: Content infrastructure, CI and Harness/docs. Keep Django ORM/migrations and domain ownership. No user evidence reset. ADR-0001 already authorizes the database direction; no new ADR or domain spec is needed absent a new decision. Operational behavior belongs in this plan and runbook.

## 7. Planned changes

1. Resolve actual dependencies with available package tooling; stop and report a blocker if resolution is unavailable. Never fabricate a lock.
2. Add validated env configuration, explicit SQLite compatibility and isolated runtime paths; safe bounded connection/version scripts and tests.
3. Add Dockerfile/Compose PostgreSQL healthcheck and excluded secret/runtime build inputs.
4. PostgreSQL reproduction and successful post-patch verification received from the user (sections 18-19). Minimal page-only FOR UPDATE scope and both transaction regressions are verified in the user's Docker environment.
5. Add guarded fresh-install smoke and isolated PostgreSQL CI, preserving all Harness/R03 checks.
6. Document implemented behavior, record verification/limitations and leave the entire diff for review.

## 8. Database / migration plan

No schema change planned. Preserve content/migrations/0001_initial.py. Apply the full existing migration chain to disposable PostgreSQL; check makemigrations --check --dry-run. Never reset a user database or edit applied migrations.

## 9. Seed / bootstrap impact

Keep existing sources and bootstrap semantics. Smoke compares counts, natural keys/primary keys, content and media across two real bootstraps; does not use dry-run as proof. Runtime student evidence remains outside bootstrap ownership.

## 10. API / UI plan

No public API, UI, template or exercise contract changes.

## 11. LLM / prompt plan

No LLM/prompt change; verification needs no live provider.

## 12. Tests

Configuration validation, secret-safe diagnostics and smoke guards; existing bootstrap/publication tests on PostgreSQL. Real locking regression only after reproduction, using transaction tests/separate connections where necessary.

## 13. Verification plan

Use skills/verification/SKILL.md. Record exact interpreter/tooling. Run dependency check, Django check/tests, migration consistency, disposable PostgreSQL smoke, connection-failure check and python scripts/verify_repo.py. Preserve the R03 suite. Mark unavailable Docker/PostgreSQL checks NOT VERIFIED, never PASS. Check git diff --check and source-material diff.

## 14. Risks and fallback

Nullable outer-join row locks, PostgreSQL constraints/order behavior, multi-phase bootstrap, runtime filesystem side effects, dependency index availability, secrets in diagnostics/build context and CI isolation. No silent database fallback or weakened checks. SQLite backup remains explicitly SQLite-only.

## 15. Human gates

Gate owner: project reviewer. Status: Pending. Infrastructure/security diff must be reviewed; no git publication authorized. Keep plan active until acceptance.

## 16. Completion checklist

- [x] Dependencies resolved and lock verified on Windows; Linux wheel resolution checked.
- [x] Implementation and relevant tests complete; user PostgreSQL verification recorded.
- [x] PostgreSQL migration/bootstrap/content/locking verified by user execution.
- [x] Docker dev/test smoke verified by user execution.
- [ ] Real GitHub Actions run verified.
- [x] Trace and runbook updated.
- [ ] Human gate accepted.

## 17. Completion summary

Infrastructure implementation prepared in the working tree; SQLite Harness 7/7
passed (24 Django tests including two PostgreSQL-only skips, 18 R03 tests).
User-executed PostgreSQL/Docker verification now passes; it is not represented
as agent-executed evidence. Real GitHub Actions execution remains NOT VERIFIED.
After user-supplied PostgreSQL reproduction, publishing now scopes the page
lock to `of=("self",)` while keeping separate publication-row locks and the
transactional conflict recheck. Two real-transaction regressions cover fresh
creation/update/idempotency and page/publication locks on a separate connection.
No schema or source-material changes were made. PostgreSQL rerun passed.
See docs/agent-traces/MS6-V01-postgres-ci.md for exact commands and versions.
Status remains Active / ready for CI and human review, not completed or accepted.

## 18. User-confirmed PostgreSQL reproduction and minimal correction

The user ran `docker compose -p ms6-v01-smoke run --rm app python scripts/fresh_install_smoke.py --disposable`
in Windows CMD with a healthy PostgreSQL 16 container. Smoke reached
`manage.py bootstrap_site` -> `publish_lessons` -> `publication_plan`, failing
while evaluating `page_query` with `django.db.utils.NotSupportedError: FOR UPDATE
cannot be applied to the nullable side of an outer join`.
This is VERIFIED reproduction reported by the user, not an agent-executed run.

The nullable ContentPage grade/subject/section joins remain in the read query.
Only ContentPage rows are selected as FOR UPDATE targets; LessonPublication
state and source-owner queries keep their locks. No locking is removed from the
publication write set, and preflight/transactional digest checks are unchanged.
The tests also check lock release after transaction commit. SQLite retains its
existing backend behavior. The user subsequently verified the patch on a new
disposable DB/runtime; see section 19.

## 19. Final user PostgreSQL verification

Evidence source: user's final Windows CMD / Docker Compose report. No additional
runtime execution by the agent is implied.

| Acceptance / check | Result |
| --- | --- |
| Fresh disposable PostgreSQL smoke on clean volume | PASS |
| Migrations without manual schema or fake repair | PASS |
| makemigrations --check --dry-run | PASS: No changes detected |
| Initial bootstrap / second bootstrap | Full catalogue/content created / 0 new catalogue/pages/redirects/lessons/media objects |
| Smoke identities/content/media/material preservation checks | PASS as part of reported fresh smoke |
| collectstatic | PASS |
| Lesson sources | PASS: 263 lessons |
| Content quality | PASS: 281 pages, 840 SVG, 0 problems |
| Site/content integrity | PASS: duplicate/broken/empty counters all 0 |
| python scripts/verify_repo.py on PostgreSQL | RESULT PASS 7/7 |
| check_database.py | PostgreSQL connection OK; server_version_num=160015 |
| version_report.py | Python 3.12.14, Django 5.2.16, psycopg/psycopg-binary 3.3.6, PostgreSQL connection OK; no secrets/DSN/password printed |
| PostgreSQL publication regression | 2 tests, OK; test DB created/deleted normally |
| Real GitHub Actions run | NOT VERIFIED |
| Human acceptance | PENDING |

Exact additional regression command:

```text
docker compose -p ms6-v01-smoke run --rm app python manage.py test content.test_postgres_publication --noinput
```

Reported output: Found 2 test(s); System check identified no issues; Ran 2 tests;
OK. This confirms the PostgreSQL-specific regressions after
`select_for_update(of=("self",))`. Only GitHub CI execution and human review
remain as completion gates. Keep this plan in active/ until human acceptance.

Final documentation cleanup aligns README/runbook with this user-executed
evidence. No functional change or additional runtime verification is claimed.
