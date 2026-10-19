# MS7-MIG-V01 Implementation Report

**BLOCKED / INCOMPLETE. Implementation stopped at contract finding B01.**
Partial code must not be deployed, stamped onto a real database, or accepted as
a completed V01 deliverable. [Finding and proposed resolution](finding-B01.md).

1. **Exact branch / starting SHA / final local HEAD.**
   `ms7-mig-v01-schema`; starting and final local HEAD both
   `8d958aeeb17da46839722441425ccbb5889e2ab7`. Worktree
   `C:/Projects/MathStart-Python-V01`. Distinct MIG_BASE_SHA remains
   `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`. No commit/push/PR.
2. **Changed files.** New `backend/` persistence/models/Alembic/config/locks/tests;
   V01 active plan, trace and dedicated acceptance files. Exact inventory and
   SHA256 in [file manifest](file-manifest.json). Existing tracked files unchanged.
3. **SQLAlchemy models.**20 baseline models: Grade, Subject, Section, ContentPage,
   LessonPublication, MediaAsset, Redirect; User/Group/Permission and3 auth joins;
   StudentProfile/IdentityReceipt/LoginWindow; ContentType/AdminLog/LegacySession/
   DjangoMigration. Seven additive protocol records. B01: three auth join IDs
   incorrectly inherit int4 from conflicting R02 model metadata; physical int8
   repair intentionally awaits the owner decision.
4. **Alembic chain.** `v01_0001` baseline -> `v01_0002` additive P1/P2 records;
   one head. Django-independent schema snapshot. Guarded rehearsal CLI; direct
   Alembic upgrade/stamp refused. Downgrade destructive deletion refused.
   Revision snapshots/DDL are proposed, not independently reviewed/applied live.
5. **Fresh install.** SQLite unit fresh succeeded without importing Django.
   PostgreSQL fresh DDL ran in a new disposable DB but strict comparison failed
   on three auth M2M ID types. The two-fresh test stopped on its first iteration;
   successful second fresh PostgreSQL install is NOT RUN.
6. **Upgrade A/B/C.** A: FAIL on CHECK deparse equality after additive users DDL;
   transaction rolled back. B/C subcases passed focused preservation/backfill/
   sequence assertions in a test method whose overall result was FAIL due to A.
   Full A/B/C acceptance is therefore not PASS. Profile A supported fixture is
   content0001 plus full auth/admin/contenttypes/session heads, no users/time.
7. **IDs/FKs/data preservation.** B/C subcases compared SHA256 of all baseline
   row projections, role joins, hashes, UUID profile/receipt/pending receipt,
   storage/content data, and exact django_migrations rows. Missing B profiles
   were the declared additive change. Production/deployed data NOT VERIFIED.
8. **Constraints/defaults/timestamps/sequences.** Baseline20/114/67/70 mapped;
   deferred NO ACTION preserved, collector preflights PROTECT, application
   defaults separate from SQL defaults, explicit save vs bulk timestamp behavior.
   Unit UNIQUE/CHECK/FK/nullability tests passed after deferred-FK test correction.
   Real PG constraint suite failed during initial setup and was not rerun.
   B/C microsecond timestamps and next-value/already-ahead sequence assertions
   passed; three fresh M2M ID/sequence widths remain blocked.
9. **Grade epoch / users backfill.** A implements only NULL Grade backfill to
   `2026-10-04T00:00:00Z`, not migration time; acceptance not reached because A
   failed. B/C preserve existing Grade instants/profiles/state; missing profiles
   only. B/C backfill twice leaves row digests unchanged.
10. **Failure/rollback.** Three injection-point tests exist (DDL/backfill/protocol)
    but their first execution failed during fixture setup; corrected full rerun
    NOT RUN after B01 stop. Unknown schema/head/column/constraint/index/sequence
    refusal and unknown Alembic head tests likewise need a corrected rerun.
    setval is nontransactional, last and nondecreasing; post-setval commit loss
    reconciliation NOT VERIFIED.
11. **PostgreSQL/SQLite.** Explicit PostgreSQL psycopg URL, bounded connection/
    statement/lock timeouts, redacted error surface, no fallback. SQLite only
    explicit non-concurrency compatibility; not upgrade/lock acceptance. Failed
    PG connection unit assertion passed and retained PostgreSQL backend.
12. **Frozen preservation.** No edits to R02/R03/R02A/R03A, R01/R02 history,
    existing Django migrations, frontend/routes/locks or root CI/README/verify.
    Frozen copied schema snapshot is byte-identical to the checked-out input.
    The final audit records accepted Git digest checks separately from any
    checkout newline conversion; no frozen files were normalized by this task.
13. **Actually executed tests.** Initial unit10:9 pass/1 fail. Subsequent combined
    run16 methods:10 unit methods passed,15 PG error subcases; overall FAIL.
    Focused PG2 methods: fresh error plus A error; B/C subcases completed without
    error. Schema diagnostic exit0 confirmed B01 and the separate CHECK issue.
    pip installation/check and final diff/syntax/scope audits recorded in
    [verification](verification.json). Interpreter Python3.12.10; PG16.15;
    SQLAlchemy2.0.46; Alembic1.18.4; psycopg3.3.6; Docker29.8.0/Compose5.5.1.
14. **NOT RUN / NOT VERIFIED.** Successful fresh twice, successful A, corrected
    full PG suite, complete target protocol schema drift check, real ordered-lock/
    collector races, runtime-only clean install, guarded CLI smoke, canonical
    `python scripts/verify_repo.py`, final CI and independent Task Approval.
    No distinct historical MS6-V02 source was found; its exact reconciliation
    remains open. Actual session/receipt/publication lifecycle is V03/V04 scope.
15. **Blockers and handoff.** B01 requires owner confirmation of physical types
    taking priority over conflicting model metadata, preserving frozen bytes.
    CHECK canonicalization fix is a pending implementation issue. Root CI/verify
    integration remains R03-owner work; no root diff was made. Minimal decision
    and next tests are in [finding](finding-B01.md) and [active plan](../../exec-plans/active/MS7-MIG-V01.md).
16. **Ruslan independent review readiness.** Ready to review B01 and the proposed
    minimal decision. **Not ready for implementation Task Approval** while
    acceptance tests fail and the remaining checks/gates are outstanding.

## Safe resumption after the owner decision

The reserved disposable container was stopped after the final audit. It has a
task label and tmpfs storage; all individually created test databases were cleaned
up. No real credentials are required for its localhost-only synthetic fixture.
Verify its label before starting; never substitute a development/production DB.

```powershell
docker inspect ms7-mig-v01-pg-20261009 --format '{{index .Config.Labels "mathstart.task"}}'
docker start ms7-mig-v01-pg-20261009
$env:MATHSTART_V01_TEST_ADMIN_URL = 'postgresql+psycopg://postgres@127.0.0.1:55441/postgres'
$env:TEMP = 'C:\Projects\MathStart-Python-V01\var\ms7-mig-v01-tmp'
$env:TMP = $env:TEMP
var/ms7-mig-v01-venv/Scripts/python.exe -m unittest backend.tests.test_unit backend.tests.test_postgres -v
```

If the container is absent, recreate only this reserved synthetic environment
with the recorded name/label/port and tmpfs. The suite refuses other endpoints,
creates new random test DB names and markers, and cleans up only those it created.
Broader baseline checks require a separate disposable migrated/bootstrapped
runtime; do not point `verify_repo` at existing user or shared development data.
