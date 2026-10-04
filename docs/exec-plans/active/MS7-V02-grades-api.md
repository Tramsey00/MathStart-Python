# EXEC PLAN MS7-V02 follow-up: Grades API for I03 (Issue 23)

- **Status:** Active; local verification PASS, ready for human review; remote CI pending
- **Owner:** Владимир
- **Reviewer / Task Approver:** Руслан
- **Integration consumer:** Илья, MS7-I03
- **Created / Updated:** 2026-10-04
- **Issue:** https://github.com/Tramsey00/MathStart-Python/issues/23
- **Branch:** `codex/ms7-v02-grades-api`
- **PR:** https://github.com/Tramsey00/MathStart-Python/pull/24 (OPEN)
- **Implementation SHA:** `1b1ded8817a328fa191952af5b8272dbfa1e653b`
- **Remote verification:** [PR checks](https://github.com/Tramsey00/MathStart-Python/pull/24/checks),
  initial [run 37202939137](https://github.com/Tramsey00/MathStart-Python/actions/runs/37202939137)
  observed IN_PROGRESS on implementation SHA; inspect current PR head for merge.
- **Baseline:** `150e569`, verified equal to fetched `origin/main`
- **Contract:** [accepted R02A](../../../specs/api/MS7-R02A-http-eligibility.md),
  [OpenAPI](../../../specs/api/openapi-v1.json),
  [DTOs](../../../specs/api/schemas/dto-v1.schema.json),
  [HTTP policy](../../../specs/api/http-policy-v1.json)
- **Runtime adapter:** [Grade mapping](../../../specs/api/MS7-V02-grades-runtime.md)
- **ADRs:** ADR-0001 and ADR-0004; no ownership or wire-contract change proposed
- **Human gate:** Required, Руслан review and I03 handoff pending
- **Trace:** [MS7-V02 grades API](../../agent-traces/MS7-V02-grades-api.md)

## Objective and scope

Implement anonymous, read-only `GET /api/v1/grades/` in Content using existing
`Grade` identities. Return `GradeListResponse` so I03 supplies an actual catalogue
ID to the existing V02 onboarding API. This is an integration correction linked
to V02, not a new canonical task ID or a reimplementation of V02.

Only this Content endpoint, its transport support, meaningful tests and records
are in scope. UI, other catalogue endpoints, auth/onboarding semantics, Progress,
LLM, bootstrap sources and frozen R02A files are outside scope.

## Discovery and preconditions

- [x] AGENTS, PRODUCT, ARCHITECTURE, ADR-0001/0004, R02A artifacts, V02 plan,
  README, content-pipeline documentation and verification skill inspected.
- [x] Issue 23 read from GitHub; scope and acceptance criteria confirmed.
- [x] Code, identity/API tests, Content migration and bootstrap inspected.
- [x] Branch created from actual current main; unrelated untracked work retained.
- [x] User explicitly agreed to additive `created_at` and migration verification
  on 2026-10-04 before schema implementation.

`Grade` currently has `id`, `title`, `slug`, `order`, `description`; no creation
timestamp. R02A explicitly requires ascending `(created_at,id)` keyset pagination.
Issue 23 says an unexpected migration must be agreed before implementation.
The user chose additive `created_at` plus migration verification. The migration
sets a common deterministic tracking epoch for existing rows and `auto_now_add`
for new rows; existing IDs, fields, references and profile state are retained.

Existing catalogue slugs encode semantic class numbers (`5-klass` ... `10-klass`).
The proposed DTO adapter uses the canonical numeric slug, not mutable display
order or database ID. Unsupported catalogue rows must produce a safe contract
error rather than fabricate a class number.

## Implementation sequence

1. Record the agreed persistence/ordering choice. Preserve Grade PKs and all
   existing fields, relationships and user evidence. Define legacy timestamp
   backfill and review any additive migration.
2. Add Content API routing, strict bounded query parsing, authenticated opaque
   cursors scoped to this public catalogue/query, DTO mapping and safe envelopes.
   Use shared infrastructure transport helpers without a Content -> Users
   dependency. Retain existing V02 transport behavior and compatibility imports.
3. Add schema/anonymous/empty-catalogue/pagination/error/read-only tests and a
   grades -> onboarding test with `Grade.id != Grade.number`. Test upgrade and
   bootstrap timestamp stability if schema changes are agreed.
4. Run narrow checks, the unchanged R02A contract suite and canonical verification
   in Python 3.12+ with PostgreSQL; verify fresh install/upgrade for any migration.
   Record exact evidence, update this plan and trace, prepare review/handoff.

## API and boundaries

Content owns the read service/DTO adapter and endpoint. Shared HTTP utilities are
in infrastructure; Users retains ownership of auth/session/profile/onboarding.
Content has no Users/Progress/LLM business dependency. GET must create no profile,
onboarding state, receipt, session or domain evidence.

Public fields: `id`, `number`, `title`. Success envelope:
`data`, `meta.request_id`, `meta.version=http-v1`, `meta.pagination` with
`next_cursor`, `page_size`, `has_more`. Default 20, maximum 100; invalid sizes
and cursors return contract 400. Database/invalid-catalogue failures return safe
503. No public timestamps or internal row metadata are added to the DTO.

## Verification and environment

Configured interpreter `.venv312/Scripts/python.exe`: Python 3.12.10;
`pip check`: PASS. Initial Docker-daemon/PostgreSQL connection failure was resolved
by starting installed Docker Desktop hidden. Disposable Compose project
`ms7-grades-23-20261004`, port 55423, database
`ms6_v01_smoke_grades_23_20261004`, test database `test_ms7_grades_23` and runtime
`var/grades-23` isolate verification from developer data. PostgreSQL 16.15
connection passed; Docker engine/client 29.8.1, Compose 5.5.1, Git 2.47.0.windows.1.
No SQLite results are being used as PostgreSQL evidence. Checks:

```text
python manage.py test content.test_grades_api content.test_grade_migrations users --noinput
python -m unittest discover -s tests -p test_r02a_contract.py -v
python scripts/verify_repo.py
python manage.py makemigrations --check --dry-run
```

For any agreed migration, include upgrade preservation and disposable PostgreSQL
fresh-install smoke using the existing runbook and script. Do not migrate or
reset the developer's existing runtime database to make tests pass.

Final local results: targeted catalogue/upgrade/Users tests PASS (61 tests,
55.851 seconds, no skips); R02A PASS (30 tests, all 17 artifact pins);
makemigrations consistency PASS. Disposable PostgreSQL fresh-install smoke PASS
with new migration, two bootstraps, preserved identities/history, static and
content checks. Canonical verification PASS (8/8), including Django 90 tests
(105.087 seconds, no skips), R03 18 and Harness 73. Bootstrapped catalogue GET
also returns schema-valid real IDs distinct from class numbers. Exact commands,
environment and final results are recorded in the trace.

## Completion and human gate

- [x] Agreed scope implemented, identities/history preserved.
- [x] Meaningful tests and required local verification pass.
- [x] Frozen contracts and unrelated work unchanged.
- [x] Trace and reviewable diff prepared.
- [x] Implementation committed/pushed and PR 24 created/attached to this chat.
- [ ] Remote CI on PR head.
- [ ] Руслан Task Approval / migration review.
- [ ] I03 handoff and integration compatibility confirmed.
- [ ] Merge and Issue closure.

Keep this plan active and the task incomplete until required checks and human
acceptance are complete. No approval, merge, CI or handoff is inferred.

Issue 23 migration-impact paragraph was synchronized with the user's explicit
agreement. PR 24 contains the local verification and gate checklist. Changes
after the implementation SHA are evidence/documentation only; current PR checks
remain authoritative for the final head. Do not equate schema-scope agreement
with Руслан's migration review or Илья's handoff acceptance.
