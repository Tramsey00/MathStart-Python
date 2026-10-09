# MS7-MIG-V01 — F1/F2/F3 Remediation Report

**F1 FIXED / F2 FIXED / F3 FIXED locally. Independent re-audit pending.**
This report supersedes the v2 implementation status, preserving its evidence.
The [independent audit](independent-audit-v3/MS7-MIG-V01-INDEPENDENT-AUDIT-REPORT.md)
remains unchanged, including its original NOT READY verdict.

## Actual state and preservation

Worktree `C:/Projects/MathStart-Python-V01`; branch `ms7-mig-v01-schema`;
starting/final local HEAD `8d958aeeb17da46839722441425ccbb5889e2ab7`.
Distinct immutable MIG_BASE_SHA `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
Tracked diff/staging remain empty; delivery files remain untracked.
All53 intake files were present, with all52 v2 manifest hashes matching.
Original bytes were preserved under ignored `var/ms7-mig-v01-remediation-input`.
[Delta](continuation-delta-v3.json) lists intentional edits and retained hashes;
[manifest](file-manifest-v3.json) records current delivery bytes. No reset/clean,
commit/push/PR, frozen edit, historical migration edit or production/shared DB use.

## F1 — FIXED: ordinary pre-save vs historical timestamps

Cause: SQLAlchemy column defaults run only when a value is absent; explicit old
dates bypassed them. The unchanged initial probe reproduced real Django
`[false,false,false]` versus target `[true,true,true]` for preservation of old
Grade/page creation dates. This was a target application parity defect.

Ordinary ORM insertion now replaces all supplied auto_now_add/auto_now fields
using mapper pre-insert events. Full ordinary updates apply auto_now only.
Restricted repository saves suppress autoflush, include auto_now only when
requested, and discard excluded dirty attributes. Bulk/Core updates preserve
explicit values. `Repository.import_historical` requires supplied PK and all
auto timestamps, uses Core insert and intentionally preserves them; no global
ban on explicit dates or session-wide bypass was added. Migration/backfill
already uses Core and does not run ordinary ORM hooks.

The [differential result](f1-timestamp-parity-v3.json) compares the real Django
baseline on disposable PostgreSQL to target behavior for all7 fields:
Grade.created_at; ContentPage.created_at/updated_at; Publication.published_at;
MediaAsset.created_at; StudentProfile.created_at; IdentityReceipt.created_at.
Ordinary creation overrides old dates for all7; historical import preserves
all7 exactly. Full/restricted/included-field saves, page/publication updates,
bulk writes, transient save and an autoflush-enabled Session are exercised.

## F2 — FIXED: complete ordered collector lock plan

Cause: SET_NULL target rows were absent from the deletion/CASCADE plan, so
mutations acquired page locks outside the promised total order. Initial probe
reproduced PostgreSQL40P01 and COMMIT + DatabaseUnavailable on valid crossed
Grade/Subject/Page references. No FK forbids that source schema.

The new plan separates deleted IDs and per-column SET_NULL target IDs, then
builds the lock union and complete FK reference closure before any row lock.
The closure is necessary: merely adding ordered Page locks still reproduced
40P01 with crossed parent locks; that unsuccessful fix is retained in raw logs.
All participants follow the existing R02 table/stable-key order. Every mutation
targets planned PKs. Under locks, PROTECT/RESTRICT and dependency sets are
rechecked: mutation sets must be unchanged and current lock needs must fit the
actually acquired superset, using rows returned by FOR UPDATE rather than
requested IDs. Removing an unneeded reference is safe; new needed locks or
changed mutation sets require rollback/restart outside the transaction.

[Concurrency evidence](f2-concurrency-v3.json) forces both plans to meet before
the first shared Grade lock, using the audit's crossed references (plus crossed
Sections). Both deletions **COMMIT**, no40P01; Grade/Subject/Section rows are
deleted, both pages survive with all three FKs NULL, publication rows survive.
Lock tokens are monotonic and Page IDs1/2 are locked in order. Additional
two-connection cases unlink/retarget a dependency before lock acquisition,
introduce PROTECT evidence, and verify conflict/rollback without collector
partial writes. SET_NULL failure injection preserves all baseline row digests;
subsequent page deletion validates publication CASCADE. An additional case removes
and recreates a referenced PK after its lock request returned no row; it requires
outer restart, proving that a requested ID is not mistaken for an acquired lock.
Explicit outer retries
succeed. No SKIP LOCKED, FK weakening or catch-and-retry workaround was used.
No change to the frozen R02 lock protocol/order was required.

## F3 — FIXED: tracking schema/head proof

Cause: alembic_version was allowed by name and excluded from physical proof.
Initial probe adopted nullable/no-PK/extra-column tracking, then CLI check
returned0 for unknown_revision. These failures remain historical evidence.

Proof now requires exactly version_num varchar(32) NOT NULL without default,
the named single-column PK/index and no extra columns/constraints/indexes/
identity drift. The owning revision graph is exactly v01_0001 -> v01_0002;
target proof requires precisely one v01_0002 row. Legacy adoption permits an
absent or fully canonical empty table; known target heads are not silently
readopted. Validation precedes Alembic reads/stamp, and CLI check uses the same
strict proof. Invalid state is refused rather than repaired or ignored.

Regressions cover missing PK, nullable version, extra/missing columns, wrong
type/length/default, extra index, unknown/multiple/empty/base-only heads, missing
tracking table, valid-head baseline drift, and an ambiguous script graph.
Fourteen negative database cases also invoke the actual CLI subprocess and
return exit1. Inventory, data digests and tracking contents are unchanged after
failed proof/adoption/check. Positive controls include clean legacy schema,
canonical empty tracking, target fresh twice and upgrades A/B/C.

## Verification and regression status

| Actually executed check | Exact result |
| --- | --- |
| Initial independent probes against unchanged implementation | exit0, F1/F2/F3 reproduced; not acceptance |
| First remediation9 methods | 8 pass / 1 error, remaining40P01 |
| Two focused F2 diagnostics | FAIL / FAIL,40P01 retained |
| Second remediation9 methods | 8 pass / 1 fail, DeletionPlanChanged; no40P01 |
| Subsequent remediation10 methods | 10 pass / 0 fail / 0 skip,29.566s |
| First complete target suite | 33 pass / 0 fail / 0 skip,57.787s (retained) |
| Additional acquired-lock regressions | 2/2 PASS |
| Final target suite | **34 pass / 0 fail / 0 skip**,62.914s |
| Target-only runtime CLI | **10/10 exit0**, Django absent/not imported |
| Disposable baseline setup | migrate/bootstrap twice/collectstatic PASS |
| Unchanged verify_repo | **8/8 PASS** |
| First baseline Django discovery | 140 collected / 118 executed / 22 target PG skips (retained) |
| Final baseline Django discovery | 141 collected / 118 executed / 23 target PG skips |
| R03 / Harness | 18/18 and73/73 PASS |
| R02 migration suite | 63/63 PASS |
| R02A / R03A | 30/30 and41/41 PASS |
| Both environment pip checks | PASS |
| Frozen digests, tracked diff/check, AST/JSON/hash audit | PASS |

Target34 comprises11 explicit in-memory SQLite unit compatibility methods and
23 real PostgreSQL methods, all PG databases freshly created/marked/removed.
Baseline target-PG skips are explicit evidence separation; the separate34-test
run executes all23 PG methods without skips. No SQLite locking/upgrade proof
or production-data claim is inferred.

Fresh twice and A/B/C preserve IDs, roles/superuser flags, encoded password
bytes, FK/data digests, Grade epoch/microseconds and complete Django history.
B01 generated INSERT RETURNING join IDs exceed int4 and prior max on fresh/A/B/C;
adjacent FK types remain INTEGER. Exact CHECK canonicalization/42-case parity,
CHECK(true) refusal, constraints/defaults/sequences, no rewind, backfill twice,
unknown schema/head and rollback injection all pass. A real post-setval
connection termination **before COMMIT** rolls back schema/data/history while
sequences only advance; the explicit retry succeeds. No AFTER-COMMIT lost
acknowledgement reconciliation was simulated.

Python3.12.10, Django5.2.16, SQLAlchemy2.0.46, Alembic1.18.4, psycopg3.3.6,
PostgreSQL16.15; Windows execution. Existing pinned environments reused, with
pip checks. Details, commands/raw-log hashes and cleanup are in
[verification v3](verification-v3.json); old-to-new links in
[evidence index v3](old-to-new-evidence-v3.json).

## Updated files, open gates and review readiness

Existing target files intentionally updated: baseline mapping hooks, repository,
collector/actual row-lock results, schema proof/upgrade guard, two existing test modules, runtime/baseline
helper output paths, active plan and trace. New files: Django differential probe,
remediation tests, v3 evidence/report/manifest/delta/index/cleanup/CI proposal and
unchanged copies of the original independent audit. Exact scope is in the delta.
All prior v1/v2 acceptance artifacts remain byte-identical.

No known F1/F2/F3 code blocker remains within tested scenarios. Ready for
independent re-audit; human Task Approval and GitHub CI are **PENDING**.
[R03 handoff v3](r03-ci-handoff-v3.md) proposes the explicit34-test command and
backend dependencies without modifying root workflows. Applicability passes;
patch not applied, CI not executed. Container cleanup is recorded separately.

NOT VERIFIED: Linux/GitHub CI, independent re-audit/Task Approval, deployed
legacy variants/data, AFTER-COMMIT acknowledgement loss, exhaustive collector/
V02–V04 lifecycle races, distinct historical MS6-V02 source, live historical
GitHub approvals and production/cutover. F2 reference closure may lock additional
related rows; canonical order and fail-closed revalidation provide the tested
behavior, with contention/scaling beyond these fixtures still unmeasured.
