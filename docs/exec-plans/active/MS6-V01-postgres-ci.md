# EXEC PLAN MS6-V01: PostgreSQL dev/test and CI

- **Status:** Active
- **Owner:** Vladimir
- **Created:** 2026-09-26
- **Last updated:** 2026-09-28
- **Related issue:** [#13](https://github.com/Tramsey00/MathStart-Python/issues/13)
- **Related PR / implementation:** [#14](https://github.com/Tramsey00/MathStart-Python/pull/14), commit `5092685`
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
- [x] Existing Issue #13 and PR #14 supplied by the user; no remote operations required.
- [ ] Exact NFR-10/NFR-11 text supplied; do not invent their definitions.

## 3. Scope

Configuration, dependency lock, Docker dev/test, PostgreSQL CI, diagnostics, smoke and documentation. No production/staging deployment, future product apps, content rewrite or historical-data migration.

## 4. Initial state (historical)

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
- [x] Published pre-R04 GitHub Actions run 36272397590: SUCCESS (user-supplied evidence).
- [x] Post-R04 PostgreSQL fresh smoke passed in the user's rebuilt Docker image.
- [x] Canonical Docker verification with checkout-context overlay: PASS 8/8, including 73 Harness tests (user-executed; section 23).
- [x] Integrated PostgreSQL publication locking regression and positive connection diagnostic (user-executed; section 23).
- [ ] Merge completion/commit and push.
- [ ] New post-push GitHub Actions run.
- [x] Trace and runbook updated.
- [x] R04 dependency/manifest reconciliation and local canonical verification (8/8, SQLite compatibility); see section 20.
- [ ] Human gate accepted.

## 17. Completion summary

Historical implementation verification: SQLite Harness 7/7
passed (24 Django tests including two PostgreSQL-only skips, 18 R03 tests).
User-executed PostgreSQL/Docker verification now passes; it is not represented
as agent-executed evidence. Published pre-R04 GitHub Actions run 36272397590
subsequently succeeded; section 20 separates integration verification and gates.
After user-supplied PostgreSQL reproduction, publishing now scopes the page
lock to `of=("self",)` while keeping separate publication-row locks and the
transactional conflict recheck. Two real-transaction regressions cover fresh
creation/update/idempotency and page/publication locks on a separate connection.
No schema or source-material changes were made. PostgreSQL rerun passed.
See docs/agent-traces/MS6-V01-postgres-ci.md for exact commands and versions.
At that historical snapshot, status remained Active with integration verification
and human acceptance pending; section 23 records later local verification.

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

Historical pre-publication snapshot; later CI evidence is recorded in section 20.

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

## 20. Post-publication evidence and R04 reconciliation (2026-09-28)

The user supplied Issue #13, PR #14, implementation commit `5092685` and
[Actions run 36272397590](https://github.com/Tramsey00/MathStart-Python/actions/runs/36272397590)
with result SUCCESS. This supersedes the earlier CI pending status for the
published pre-R04 implementation only; earlier snapshots remain historical.
R04 PR #10 is merged into origin/main at `9f705b0`. The existing merge has
HEAD `5092685`, MERGE_HEAD/origin/main `9f705b0`; the agent did not initiate or
complete it, stage files or perform remote operations.

Requirements now retain both V01 psycopg[binary] and R04 jsonschema. The lock
was regenerated by the repository script from real pip resolution, preserving
all prior pins; five R04-related packages were added. Windows installation,
pip check, Linux wheel resolution and direct/lock/installed version comparison
passed. The auto-merged verification skill preserves both V01 PostgreSQL
requirements and R04 canonical Harness instructions without further edits.

The first Harness run exposed an ARCHITECTURE.md digest mismatch in the R04
manifest. Updating only that reference digest fixed it; validation and tests
were not weakened. No application code, migrations, publishing, settings,
Docker or CI changes were needed during reconciliation.

Agent-executed verification on isolated SQLite compatibility paths passed:
clean migrate, two bootstraps (second creates/changes zero objects), collectstatic,
canonical verify_repo 8/8 (24 Django tests with 2 PostgreSQL skips, 18 R03 tests,
73 Harness tests), version report and the expected nonzero PostgreSQL port-1
connection diagnostic. Content: 263 lessons, 281 pages, 840 SVG, zero problems.
Exact commands, versions and initial failures are recorded in trace section 22.

Gates at the initial reconciliation snapshot (superseded by section 21):

- Local available integration verification: PASS, with explicit SQLite scope.
- Integrated-state PostgreSQL fresh smoke, positive connection and locking
  regressions: NOT VERIFIED; Docker/psql unavailable in the agent environment.
  Prior user PostgreSQL PASS remains valid pre-integration evidence only.
- New post-push GitHub Actions: PENDING; no run initiated or claimed.
- Final Ruslan human review/acceptance: PENDING; plan remains active.
- Merge index still reports requirements.txt as UU until the user stages the
  resolved working file; no conflict markers remain in its contents.

## 21. Post-R04 Docker Git dependency defect

User-executed evidence: the rebuilt integrated V01 + R04 image passed fresh
PostgreSQL smoke. Its canonical verify_repo then passed seven checks and failed
the Harness check with FileNotFoundError for `git` from repository.py.
This establishes post-integration PostgreSQL smoke PASS and canonical Docker
verification FAIL before the correction; it is not agent-executed evidence.

Dockerfile had no Git installation and Compose did not supply an executable.
The minimal correction installs only Git and apt-required dependencies with
--no-install-recommends, checks git --version during build and removes apt
indexes in the same layer. Python, PostgreSQL, non-root runtime, requirements,
Harness code/tests and CI remain unchanged. Debian patch versions follow the
existing Bookworm image policy; no exact package version was invented.

Current gates: user rebuild and full Docker verification after this fix PENDING;
new post-push Actions PENDING; final human acceptance PENDING. Plan stays active.
Agent cannot rebuild: Docker executable remains unavailable. See trace section
23 for available local checks and user rerun instructions in the runbook.

## 22. Post-R04 Docker checkout context defect

After the Git-enabled image was rebuilt, the user reported `git --version`
available and fresh PostgreSQL smoke PASS. Canonical `verify_repo.py` again
passed seven checks but failed Harness: 73 tests, 21 errors, with
`RepositoryError: fatal: not a git repository (or any of the parent directories): .git`.
This is user-executed post-fix evidence; section 21's earlier missing-executable
failure remains a separate historical result.

Dockerfile copies `/app` from a context that excludes `.git`; the base Compose
configuration mounts only database and runtime volumes. R04 uses Git for actual
checkout identity, branch/HEAD, refs, status and diffs. CI runs natively in an
`actions/checkout` workspace with `.git`; Docker verification lacked that context.

Added `compose.verify.yaml` for local verification only: read-only bind of the
existing checkout's `.git` to `/app/.git`, with `safe.directory=/app` scoped to
that invocation for the non-root image user and optional index writes disabled.
No Git history is copied into an
image or included in routine app runs; normal Compose and CI remain unchanged.
R04 production Git semantics and all tests/checks remain intact. The runbook
provides Windows-compatible Compose commands using the same disposable project.

New Docker verification with this overlay: PENDING user rebuild/run; the agent
has no Docker executable. Post-push GitHub Actions and Ruslan acceptance remain
PENDING. Keep this plan active and the existing merge unresolved in the index.

## 23. Final local integrated-state verification (user-executed)

The user rebuilt the current Git-enabled app image and ran verification with
`compose.verify.yaml`. Inside that container, `git rev-parse --show-toplevel`
confirmed the real checkout; the ordinary image/Compose path still excludes
`.git`. The disposable PostgreSQL fresh-install smoke passed on integrated
V01/R04: clean migrations, `makemigrations --check --dry-run` reported No changes
detected, initial bootstrap created 6 classes, 12 subjects, 63 sections,
18 pages, 280 redirects, 263 lessons and 29 media; the second bootstrap
created/changed zero catalogue, pages, redirects, lessons and media.

Smoke also passed identity/content/media preservation, collectstatic (140 files,
420 post-processed), lesson-source matching (263), content quality (281 pages,
840 SVG, zero problems) and site integrity (281 materials, 263 topics,
29 media, 1685 references, all error counters zero). Canonical
`python scripts/verify_repo.py` inside the current Docker verification
environment passed all eight checks, including 73 Harness tests. PostgreSQL
publication regression passed two tests. Positive database diagnostic reported
`server_version_num=160015`. Exact user-reported evidence is in trace section 25.
These results supersede sections 20-22's pending/failed local verification
states without rewriting those historical snapshots.

Current local integrated-state acceptance: PASS. Remaining gates: finish the
unresolved merge and commit, push, observe a new post-push GitHub Actions run,
then final human review/acceptance by Ruslan. The published pre-R04 Actions run
36272397590 remains SUCCESS only for its earlier state. Plan stays ACTIVE.
