# MS7-MIG-V01 INDEPENDENT AUDIT REPORT

Дата: 09.10.2026, Europe/Moscow. Независимый технический аудит Codex, не human Task Approval от Руслана.

**Вердикт: NOT READY как завершённая V01 для commit/push/PR. Три воспроизведённых P2.** Материалы готовы для рассмотрения findings Русланом. Исправления, commits, push, merge и PR не выполнялись. Источники и evidence в рабочем дереве не изменены.

## 1. Actual state

Worktree `C:/Projects/MathStart-Python-V01`, branch `ms7-mig-v01-schema`, HEAD и accepted integration input `8d958aeeb17da46839722441425ccbb5889e2ab7`. Immutable MIG_BASE_SHA отдельно `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`. Tracked diff пуст; dirty: 53 untracked файла, 434246 bytes. Нет staged изменений. Appendix A перечисляет каждый файл; input-hash snapshot проверен повторно, изменений байтов нет.

## 2. Scope и источники

Прочитаны AGENTS, PRODUCT, ARCHITECTURE, ADR0001/0006, README/content architecture, verification skill, V01 card/ownership, R01/R02 handoff, platform/schema/auth/publication/bridge/storage contracts, реальные content/users models и migrations, target models/migrations/infrastructure/tests, V01 reports v1/v2, verification v1/v2, B01/addendum, CHECK investigation, CI handoff, active plan/trace и historical adapters. Исторические PROPOSED статусы R02 не переписаны; accepted input используется по прямому указанию пользователя.

Все 53 untracked файла прочитаны; Python AST/JSON parsing проверены. Reports прошлой разработки использованы как предмет аудита, не как доказательство текущего PASS. Git-object R02 digest manifest сверён независимо: zero mismatches. Snapshot baseline-v1.json byte-identical frozen R02 mapping; SHA256 `4faf862e8810e817d241b9134a2f52a2d62a8236b491bdc7c658e588a863f588`.

## 3. V01 coverage matrix

| Требование карточки V01 | Реализация / доказательство | Статус |
|---|---|---|
| 1: 20 baseline tables, names/types/constraints/history | baseline.py + frozen snapshot; legacy_fixture создаёт реальную Django PG схему; строгий catalog comparison | PASS physical |
| 2: repos/UoW/defaults/timestamps/collector/locks/SQLite | repositories.py, uow.py, collector.py, locks.py, database.py; 11 unit + PG assertions | FAIL: F1/F2 |
| 3: fresh без Django + A/B/C + Grade epoch/backfill | v01_0001 → v01_0002, upgrade.py; target suite + 10 target-only CLI calls | PASS supported fixtures |
| 4: DDL ownership, schema proof до stamp, migration history | disposable guards, reviewed flag, complete history comparison, exclusive table locks | FAIL: F3 tracking schema/head blind spot |
| 5: locks/dependencies/config/isolation/drift | pinned runtime/test locks, pip check, explicit PG/SQLite; new marked UUID DBs, drift negatives | PARTIAL: known F2/F3; Linux/clean reinstall NOT VERIFIED |
| 6 / §17: MS6-V01, MS7-V02, grades adaptation and historical links | old-to-new index, unchanged source migrations, current fresh/upgrade evidence | PASS known sources; distinct MS6-V02 NOT IDENTIFIED |
| Negative cases | unknown legacy heads, CHECK(true), column/table/index/FK/sequence/view/schema drift; failed PG no fallback | PASS listed cases; FAIL unknown target head on CLI check |
| Failure/backfill twice | DDL/backfill/protocol injections, digests/history, independent retries and post-setval disconnect | PASS tested boundaries; COMMIT acknowledgement loss NOT VERIFIED |
| Exact target delivery SHA/CI/human gates | untracked delivery pinned by file-manifest; HEAD contains only accepted input | PENDING, no false acceptance |

## 4. Schema/model parity

**Physical 20 baseline + 7 additive tables: PASS on PostgreSQL 16.15 disposable schemas. Application/ORM parity: FAIL (F1/F2).** Appendix B lists every table and reflected columns/constraints/indexes. Baseline: 114 columns, 67 constraints, 70 indexes. Additive: 61 columns, 35 constraints, 17 indexes.

Compared exact names, varchar lengths, int2/int4/int8/uuid/jsonb/timestamptz, timestamp precision, PK/FK/UNIQUE/CHECK, index names and operator classes, nullability/SQL defaults, identity kind and owned sequences, sequence type/min/max/increment/cycle/cache. Django physical FKs remain DEFERRABLE INITIALLY DEFERRED / NO ACTION; SQL cascades were not substituted for collector semantics. Sequence last_value is excluded only from structural equality and separately tested as mutable deployment data. All CHECK comparisons remain exact.

Protocol schema is reviewed against logical required facts: namespace/key/release uniqueness, ownership/fence/lease/pending fields, active descriptor references, journal phases/commit checks, session owner/digest/lineage/epoch, bridge scope/owner/session/cutover binding, state/counter/retention checks, durable cutover provenance/history. Cross-row CAS, no revival, monotonic transitions, signatures and lifecycle writers are expressly future V03/V04 obligations; metadata does not falsely implement them. The generated protocol catalog is proposed DDL, not human acceptance.

## 5. B01 — FIXED

Only auth_group_permissions.id, auth_user_groups.id, auth_user_user_permissions.id are BIGINT in PostgreSQL metadata and actual fresh DDL. Adjacent user_id/group_id/permission_id remain INTEGER. Upgrade emits no narrowing ALTER/cast for these columns. Existing IDs > int4, assignment FKs/UNIQUEs, data digests and sequence ownership survive A/B/C. Extra independent checks used actual INSERT RETURNING, not merely nextval: generated IDs were respectively 2147484651, 2147484650, 2147484652 on FRESH/A/B/C. Existing ahead/empty/uncalled sequence cases pass.

Compatibility addendum records the exact three-column authorization, accepted input and user-reported owner provenance without inventing a retrieved signature. Current audit request independently states that decision. Frozen bytes/digests unchanged.

## 6. CHECK canonicalization — FIXED

Original failure was users_consistent_onboarding. Frozen PostgreSQL deparse has `= ANY ((ARRAY[...::character varying])::text[])`; reparsing that deparse prints per-element text casts instead. Emitting original Django `IN ('START_ZERO','DIAGNOSTIC','SELF_REPORT')` reproduces the exact frozen pg_get_constraintdef. Independent investigation: 42 PostgreSQL truth-table combinations, zero mismatches. CHECK(true) replacement is rejected before stamp and database inventory unchanged. No global expression normalization/ignore was added. Invalid baseline data still fails constraints.

Original verification.json remains BLOCKED_INCOMPLETE and explicitly records B/C subcases inside an overall failing historical run. Those subcases are not counted as current PASS. Current complete target suite independently passed.

## 7. Fresh PostgreSQL ×2

PASS in separate new disposable databases; one revision head v01_0002 and chain v01_0001 → v01_0002. Runtime-only interpreter has no Django installed/imported; both fresh/check pairs exit 0. Raw Alembic/offline operations guarded; destructive downgrade refused.

## 8. Upgrade A/B/C

PASS independently, with actual Django-generated source fixtures. A: complete auth/admin/contenttypes/sessions baseline heads + content0001, no users/Grade timestamp. B: full current schema/history with missing synthetic user profile. C: populated profile/roles/receipts/login window. Full expected migration history checked before stamp; unknown history refused. B/C have identical schema/history, C supplies populated evidence; caller chooses profile rather than automatic data classification.

Adapter: proof → ACCESS EXCLUSIVE table locks → repeat proof → additive A DDL → missing-profile backfill → proof/history comparison → stamp baseline → protocol migration → proof → immediate deferred-constraint validation → forward sequence adjustment → caller COMMIT. Existing django_migrations rows are not synthesized or rewritten. No production path authorized. F3 exposes one exception in accepted tracking-table shape.

## 9. IDs/FK/constraints/defaults/timestamps/sequences

PASS preservation on synthetic rows, including >int4 join IDs, UUID profiles/receipts, content/grade IDs, user roles/assignments/password bytes, UTC microseconds and complete historical migration rows. Extra audit sets is_superuser=True and verifies it survives all profiles. Password algorithm usability is V03 scope; only byte preservation is proven here. Existing actual production rows were never read.

Normal app defaults vs SQL defaults correctly separated; raw SQL missing required default-less fields rejected. Unique, invalid FK, CHECK, nullability and SQL-vs-JSON null cases tested. Collector PROTECT/CASCADE/SET_NULL works in sequential cases. New-row timestamp semantics differ from Django (F1); collector lock coverage differs from contract (F2).

## 10. Grade epoch/backfill

PASS: A gets 2026-10-04T00:00:00Z for newly added Grade time; B/C keep existing timestamps. Missing profiles inserted; existing populated C profile mode/grade/state/UUID untouched. Backfill twice preserves digests. No credential/role overwrite.

## 11. Rollback/failure injection

PASS for after DDL, after backfill, after protocol/stamp: schema/data/history restored. Additional independent retries after each failure succeed. Added real pg_terminate_backend on the audit-owned connection immediately after setval, BEFORE COMMIT: disconnect reported OperationalError, data/schema/history unchanged, sequences move only forward, retry succeeds.

Lost acknowledgement AFTER COMMIT is NOT VERIFIED. Current guarded code refuses an existing Alembic head on retry, preventing blind duplicate migration; an operational reconcile procedure/test still needs explicit owner agreement before production/cutover. This is a bounded test/reconciliation gap rather than an observed destructive upgrade defect. No broad acceptance or follow-up approval is inferred.

## 12. Repository/UoW/locks

SQLAlchemy2 synchronous sessions; per-UoW session, autoflush=False, explicit commit/default rollback/finally close; nested savepoint coverage. PG defaults to installed SQLAlchemy/psycopg READ COMMITTED behavior; no automatic in-transaction retry. Timeouts/pre_ping and safe error messages provided. Receipt stable-key/User/profile/publication lock tests pass. Collector omits SET_NULL targets and consequently deadlocks (F2).

## 13. PostgreSQL/SQLite behavior

PASS explicit configuration: PostgreSQL psycopg URL required, SQLite requires opt-in path/compatibility flag, PG connection failure remains PG and raises safe error. SQLite used only in-memory non-concurrency unit tests. Upgrade profiles require PG. Imports read snapshots/build metadata without connecting or issuing SQL writes; connection check SELECT1 only. No production target writer behavior is implemented.

## 14. Frozen contracts/ownership/history

PASS local preservation: no tracked edits, frozen contracts/Django migrations/runtime APIs/root docs/CI/frontend unchanged. Root CI remains Ruslan-owned; no patch applied. Backend writable chain is scoped to Vladimir and disposable rehearsals. Known historical original_result records and local links retained. No distinct MS6-V02 record located. Live GitHub historical approval/URL/CI status was not independently fetched and is NOT VERIFIED; user-supplied accepted input is not rewritten.

## 15. Audit of claimed test counts

Current independent target suite: 22 collected / 22 passed / 0 failed / 0 skipped, 29.401s, exit0 (11 unit + 11 PG methods; subcases exceed method count). Target-only CLI: 10/10 exit0. Canonical verify_repo: 8/8 exit0; Django 129 collected / 118 executed / 11 skipped; R03 18/18; Harness 73/73. R02 migration 63/63; R02A30/30; R03A41/41. Baseline's 11 skips are all target PG methods, independently executed in explicit 22-test run. They do not prove PG by themselves.

Initial audit-copy baseline gave 7/8, exit1, Harness73 with 21 errors because copy lacked Git context. This is an audit-environment failure, not V01 defect. Added external shared read-only Git object context and index (no commit/reset/source change), reran and obtained 8/8. Both outputs retained externally.

Green tests omit the three reproduced cases; timestamp unit test even asserts preservation of old supplied updated_at on creation, unlike Django. No existing tests were weakened or changed during audit.

## 16. CI handoff readiness

Proposed patch applicability PASS with git apply --check --ignore-space-change. It adds target runtime dependencies to both jobs and explicit 22-test PG command/reserved55441 service mapping to migration workflow. This is sufficient configuration to repeat target fresh/upgrade tests without platform-specific runtime helper. Linux execution/current PR CI NOT VERIFIED. Existing root-lock-only workflow would fail backend imports; owner handoff correctly documents this. Separate clean target-only CLI/absence-of-Django isolation is not run by this proposed patch and remains distinct evidence. No workflow modifications made.

## 17. Security/secrets/backups

53 commit-candidate files: no credential/private-key/token signature hits, no dumps/backups/.env files, no >1MB files. Largest baseline JSON ~208KB. Synthetic fixture password/hash literals are explicitly test-only. Pattern scan is not a mathematical guarantee of no secret.

Ignored inventory: 11461 entries, primarily existing venvs/runtime/__pycache__; existing var/ms7-mig-v01-resume-input contains33 historical backup files and is ignored. No ignored .sql/.dump/.sqlite3/.bak paths found. Ignored files were not staged, deleted or altered. New tests ran solely in external copy with PYTHONDONTWRITEBYTECODE=1.

Audit container: newly created `ms7-v01-independent-audit-20261009`, ID063c5aded3285a7283b1de8f425ccced5ecbd84d43e86fae0c79ab2c3268789e, label mathstart.audit=independent-v01, localhost55441, tmpfs. All DBs new UUID + reservation marker. Final query: zero test_ms7_mig_v01_% databases. Only this container removed; pre-existing containers untouched. No DB migrations/mutations on production/shared databases.

## 18. Actually executed commands/environment

All tests from this external copy, unchanged source. P = C:/Projects/MathStart-Python-V01/var/ms7-mig-v01-venv/Scripts/python.exe. T = target-only var/ms7-mig-v01-runtime-venv/Scripts/python.exe (external junction to existing interpreter, read-only).

- P -m pip check; T -m pip check: exit0.
- P -m unittest backend.tests.test_unit backend.tests.test_postgres -v: exit0,22/22.
- P -m backend.tests.runtime_verification: exit0,10 CLI subprocesses using T.
- P -m backend.tests.baseline_verification: initial environment exit1; corrected environment exit0.
  Runs manage.py migrate --noinput, bootstrap_site ×2, collectstatic --noinput, scripts/verify_repo.py, and 3 R02 migration modules.
- P -m unittest discover -s tests -p test_r02a_contract.py: exit0,30.
- P -m unittest discover -s tests -p test_r03a_contract.py: exit0,41.
- P audit_probes.py: exit0; asserts REPRODUCTION of F1/F2/F3, not acceptance PASS; retries and precommit disconnect evidence.
- Extra disposable fresh/A/B/C actual INSERT RETURNING/superuser preservation probes: exit0.
- git diff --check; proposed patch applicability; untracked AST/JSON; manifest hashes; Git-object frozen digest manifest: exit0/zero mismatches.

Actual Python3.12.10, Django5.2.16, SQLAlchemy2.0.46, Alembic1.18.4, psycopg3.3.6, PostgreSQL16.15 (Debian16.15-1.pgdg12+2), Docker client/server29.8.0, Compose5.5.1, Windows execution. Existing pinned environments reused and independently checked; new clean dependency installation not claimed.

## 19. NOT RUN / NOT VERIFIED

Linux/GitHub CI, independent human DDL/Task Approval, actual deployed source profile variations/data, live GitHub historical reviews/links, distinct MS6-V02, clean lock reinstallation, lost COMMIT acknowledgement after commit, exhaustive collector/lifecycle races, V02–V04 auth/signer/session/bridge/publication runtime and production/cutover. These limits are separate from the concrete defects below.

## 20. Findings

### F1 — P2: auto_now_add/auto_now creation differs from Django

[backend/models/baseline.py:55](C:/Projects/MathStart-Python-V01/backend/models/baseline.py:55), columns default at :79; [repositories.py:21](C:/Projects/MathStart-Python-V01/backend/infrastructure/repositories.py:21).

SQLAlchemy Column(default=utc_now) runs only when value absent. Repository.add leaves explicitly supplied old Grade.created_at and ContentPage.created_at/updated_at unchanged. Real Django DateTimeField.pre_save overrides all three during ordinary creation. Probe at old=2000-01-01: Django preservation [false,false,false], target [true,true,true]. Existing test_unit.py:96–106 misses/endorses the difference.

Violates V01 scope2 defaults/timestamps/ORM equivalence and R02 platform-v1.md:34–36. Risk: V02 ordering/content timestamps and V04 freshness/audit times differ for new writes; V03 auto_now_add receipt/profile creation has the same mapping pattern. Existing imported rows are not damaged by this finding.

Minimal fix: ordinary creation/save adapter applies Django pre-save timestamp rules even when caller supplied value, with an explicit separate historical-import/Core insertion path preserving evidence times. Add differential Django/target creation assertions; retain update_fields/bulk behavior. No fix applied.

### F2 — P2: SET_NULL targets omitted from ordered collector locks

[backend/infrastructure/collector.py:63](C:/Projects/MathStart-Python-V01/backend/infrastructure/collector.py:63) and [:75](C:/Projects/MathStart-Python-V01/backend/infrastructure/collector.py:75).

plan_deletion contains only deleted/CASCADE rows, so lock phase omits rows later changed by SET_NULL. Probe deletion of Grade701 locks only grade/subject/section and then updates ContentPage704. Multi-statement un-ordered SET_NULL obtains real row locks outside stable PK ordering/tracker.

Reproduce with grades G1/G2, subjects S1(G1)/S2(G2), schema-valid pages P1(gradeG1,subjectS2), P2(gradeG2,subjectS1). Concurrent delete_collected(G1) and delete_collected(G2), synchronize after each first grade_id=NULL update. PostgreSQL40P01, outcomes COMMIT + DatabaseUnavailable. No constraint forbids these baseline references. Existing sequential collector/single-row lock tests miss it.

Violates R02 total lock order and V01 scope2 locking/collector equivalence. Risk: V02 staff/bulk actions and V04 catalogue/content composition fail/deadlock; V03 composed services cannot rely on declared locks. Tested transaction aborts safely; no committed corruption observed.

Minimal fix: collect SET_NULL target IDs separately from deletion IDs, acquire union in canonical table/stable-row order before mutation, revalidate plan under locks, update/delete only planned IDs; include deterministic two-session test. Preserve PROTECT preflight and rollback; future service retry policy does not replace lock correctness. No fix applied.

### F3 — P2: Alembic tracking table/head excluded from schema proof/check

[backend/migrations/schema.py:80](C:/Projects/MathStart-Python-V01/backend/migrations/schema.py:80) and [:89](C:/Projects/MathStart-Python-V01/backend/migrations/schema.py:89); [backend/migrate.py:30](C:/Projects/MathStart-Python-V01/backend/migrate.py:30).

alembic_version is allowed by name but excluded from baseline/protocol catalog comparisons. On legacy B, CREATE TABLE alembic_version(version_num varchar(32), unexpected text) with nullable version_num/no PK passes get_current_heads(empty), schema proof, stamp and upgrade. Subsequent assert_baseline also PASS. After UPDATE alembic_version SET version_num='unknown_revision', guarded CLI check returns0 and prints completed.

Violates V01 scope4/5 complete proof before stamp/no unexpected drift and requested acceptable-head detection. Risk: V01 corrupt migration bookkeeping silently adopted; V02–V04 cannot safely trust check/stamp state or future revision application.

Minimal fix: refuse any pre-existing Alembic tracking table for legacy adoption, or validate its exact columns/nullability/PK and permissible state; check CLI must validate owning target head/cardinality in addition to physical tables. Add malformed tracking-table and unknown/empty/multiple-head negatives. No fix applied.

P1: none found. P3: none promoted. Missing human/CI gates and future lifecycle implementations are not mislabeled as code defects.

## 21. Verdict

**NOT READY** for delivery as completed V01. F1/F2/F3 are blocking P2 findings. B01 and CHECK findings are FIXED within verified scope. Green22/22,10/10,8/8 results are independently reproduced but do not close these omitted cases or human acceptance. Ruslan can review these findings and proposed DDL; no acceptance, downstream start, commit/push/PR or production authority inferred.

External artifacts: audit_probes.py, audit-probes-results.json, audit-b01-results.json, audit-input-hashes.json; baseline raw logs under var/ms7-mig-v01-baseline-3e777dbf05884973a6c5b75863e39a96/ and initial failed environment logs under var/ms7-mig-v01-baseline-955b73997de64433b6168bc99ea9b5ad/. None resides inside user's Git worktree.

## Appendix A — Full changed/untracked inventory

Tracked changed files: none. Untracked files:

```text
backend/__init__.py
backend/alembic.ini
backend/infrastructure/__init__.py
backend/infrastructure/collector.py
backend/infrastructure/database.py
backend/infrastructure/locks.py
backend/infrastructure/repositories.py
backend/infrastructure/uow.py
backend/migrate.py
backend/migrations/__init__.py
backend/migrations/env.py
backend/migrations/protocol-schema-v1.json
backend/migrations/schema.py
backend/migrations/upgrade.py
backend/migrations/versions/v01_0001_baseline.py
backend/migrations/versions/v01_0002_protocol.py
backend/models/__init__.py
backend/models/baseline-v1.json
backend/models/baseline.py
backend/models/compatibility-v1.json
backend/models/protocol.py
backend/requirements-test.lock
backend/requirements.lock
backend/requirements.txt
backend/tests/__init__.py
backend/tests/baseline_verification.py
backend/tests/capture_protocol_schema.py
backend/tests/check_canonicalization.py
backend/tests/legacy_fixture.py
backend/tests/runtime_verification.py
backend/tests/test_postgres.py
backend/tests/test_unit.py
docs/acceptance/MS7-MIG-V01/b01-owner-approval-v1.json
docs/acceptance/MS7-MIG-V01/baseline-verification-v2.json
docs/acceptance/MS7-MIG-V01/check-canonicalization-v1.json
docs/acceptance/MS7-MIG-V01/check-canonicalization-v1.md
docs/acceptance/MS7-MIG-V01/compatibility-addendum-v1.0.0.md
docs/acceptance/MS7-MIG-V01/continuation-delta-v2.json
docs/acceptance/MS7-MIG-V01/disposable-cleanup-v2.json
docs/acceptance/MS7-MIG-V01/file-manifest-v2.json
docs/acceptance/MS7-MIG-V01/file-manifest.json
docs/acceptance/MS7-MIG-V01/finding-B01.md
docs/acceptance/MS7-MIG-V01/implementation-report-v2.md
docs/acceptance/MS7-MIG-V01/implementation-report.md
docs/acceptance/MS7-MIG-V01/old-to-new-evidence-v2.json
docs/acceptance/MS7-MIG-V01/old-to-new-evidence.json
docs/acceptance/MS7-MIG-V01/r03-ci-handoff-v2.md
docs/acceptance/MS7-MIG-V01/r03-ci-handoff-v2.patch
docs/acceptance/MS7-MIG-V01/runtime-verification-v2.json
docs/acceptance/MS7-MIG-V01/verification-v2.json
docs/acceptance/MS7-MIG-V01/verification.json
docs/agent-traces/MS7-MIG-V01.md
docs/exec-plans/active/MS7-MIG-V01.md
```

## Appendix B — Every PostgreSQL table

C/constraints/index counts are reflected catalog counts. Each row physical comparison PASS; F1/F2 affect application behavior. alembic_version is additional bookkeeping outside these27; its blind spot is F3.

| Table | Columns | Constraints | Indexes | Physical parity |
|---|---:|---:|---:|---|
| auth_group | 2 | 2 | 3 | PASS |
| auth_group_permissions | 3 | 4 | 4 | PASS |
| auth_permission | 4 | 3 | 3 | PASS |
| auth_user | 11 | 2 | 3 | PASS |
| auth_user_groups | 3 | 4 | 4 | PASS |
| auth_user_user_permissions | 3 | 4 | 4 | PASS |
| content_contentpage | 16 | 6 | 6 | PASS |
| content_grade | 6 | 3 | 3 | PASS |
| content_lessonpublication | 5 | 4 | 4 | PASS |
| content_mediaasset | 6 | 3 | 4 | PASS |
| content_redirect | 5 | 2 | 3 | PASS |
| content_section | 6 | 4 | 5 | PASS |
| content_subject | 6 | 4 | 5 | PASS |
| django_admin_log | 8 | 4 | 3 | PASS |
| django_content_type | 3 | 2 | 2 | PASS |
| django_migrations | 4 | 1 | 1 | PASS |
| django_session | 3 | 1 | 3 | PASS |
| users_identityreceipt | 10 | 5 | 4 | PASS |
| users_loginwindow | 4 | 4 | 3 | PASS |
| users_studentprofile | 6 | 5 | 3 | PASS |
| target_active_release | 5 | 4 | 1 | PASS |
| target_identity_cutover | 4 | 2 | 2 | PASS |
| target_publication_gate | 5 | 4 | 1 | PASS |
| target_publication_history | 7 | 3 | 1 | PASS |
| target_publication_journal | 16 | 8 | 4 | PASS |
| target_receipt_bridge | 15 | 10 | 4 | PASS |
| target_session | 9 | 4 | 4 | PASS |
