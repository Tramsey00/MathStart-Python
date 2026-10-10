# EXEC PLAN MS7-MIG-V01 — SQLAlchemy, Alembic and upgrade profiles

- Status: **F1/F2/F3 and CI discovery locally fixed / v4 verified / CI integration and review pending**
- Owner: Владимир; reviewer / Task Approver: Руслан
- Created / updated: 2026-10-09, Europe/Moscow
- Issue: https://github.com/Tramsey00/MathStart-Python/issues/34
- Spec: [migration v1.1](../../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md), [R02](../../../specs/migration/r02-v1/README.md)
- ADR: [0006](../../adr/ADR-0006-react-fastapi-migration.md)
- Human gate required: Yes; pending. No commit/push/PR authorized.

## Objective and intake

One Django-independent SQLAlchemy2/Alembic persistence chain that preserves the
baseline and passes fresh twice, upgrades A/B/C, preservation, constraint,
sequence, rollback, negative schema/head and no-fallback tests on disposable PG.
Worktree `C:/Projects/MathStart-Python-V01`, branch `ms7-mig-v01-schema`, initially
clean, starting/current HEAD `8d958aeeb17da46839722441425ccbb5889e2ab7`.
MIG_BASE_SHA separately `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
User identifies this input as accepted; historical PROPOSED records stay intact.

## Read/discovery and boundaries

AGENTS/PRODUCT/ARCHITECTURE, README/content architecture, verification skill,
ADR0001/0006, R01 ownership/inventory, V01 card, R02 platform/schema/protocol/
auth/adapter/handoff and old-to-new evidence inspected. Existing content/users
models and additive migrations, MS6-V01/MS7-V02/grades historical traces read.
No distinct MS6-V02 record was found by repository text search; historical
MS6-V02-specific evidence is NOT VERIFIED, not invented.

Writable scope: backend persistence/config/migrations/dependency locks/tests,
this V01 plan, trace and dedicated acceptance evidence. Root CI/README/verify,
frontend/I01/R03 files, frozen contracts and historical records are excluded.
Content/Users persistence only; no educational domains, HTTP/login/publisher,
product/UI/LLM behavior or production writes. Until cutover Django owns live
DDL/writes. V03/V04 own bridge/session/publication lifecycle enforcement.

## Implementation sequence

1. Compare physical baseline to model semantics and historical migrations.
2. Frozen local schema snapshot, SQLAlchemy types/defaults/relationships,
   collector, sessions/UoW/repositories and ordered PostgreSQL locks.
3. Alembic v01_0001 baseline -> v01_0002 protocol facts; no downgrade DROP.
4. Guarded disposable upgrade A/B/C; exact schema/head inspection before stamp,
   additive Grade epoch/users backfill, retain history, never rewind sequences.
5. Test fresh twice, profiles, preservation, constraints, rollback at three
   injection points, twice backfill, unknown/drift refusal, no SQLite fallback.
6. Baseline verification on a separately prepared disposable runtime; frozen
   preservation, diff/secrets/scope audit, evidence and independent Ruslan gate.

## Current execution status

### PR51 CI integration continuation v4

New authorized intake: branch `ms7-mig-v01-schema`, published/local HEAD
`d5dc9a4e130d3901c26894aa01e30a935dac84b6`; clean worktree. Existing commits and
all v1/v2/v3 evidence retained. Snapshot102 affected/frozen/history/CI files
under ignored `var/ms7-mig-v01-ci-input-v4` before edits.

Root-lock legacy CI lacks SQLAlchemy/Alembic; default Django discovery traverses
all regular packages and eagerly imports backend.models and three target tests.
Reproduced all4 ImportErrors and a pre-fix failing discovery regression. Minimal
runtime fix: standard package `backend.load_tests` stops implicit target recursion
and loads only two dependency-independent regressions. Target suites remain
explicit, fail on missing dependencies, and retain public metadata/Alembic imports.
No exception suppression/global skip or persistence/contract change. New
[testing guide](../../../backend/TESTING.md), root cause and v4 evidence document
the two environments. Diagnostic output directories avoid historical overwrite.

Target34/34/zero skips (68.507s), both discovery regressions in both environments,
target-only CLI10/10 and first PG legacy109/109/zero skips (174.181s) pass.
Final root-lock verify_repo8/8 passes, repeating109/109/zero skips (170.744s);
R03/Harness18/73, R02 migration63, R02A30 and R03A41 all pass without target deps.
The10-command legacy helper passes; zero owned test DBs remain and the validated
container is stopped. Exact evidence is in the [v4 report](../../acceptance/MS7-MIG-V01/implementation-report-v4.md)
and [verification](../../acceptance/MS7-MIG-V01/verification-v4.json).
Frozen/history/CI/locks/old evidence digest checks pass. The
[v4 R03 handoff](../../acceptance/MS7-MIG-V01/r03-ci-handoff-v4.md) supersedes the
unapplied v3 proposal and puts explicit target suites in a separate CI venv;
root workflow installation remains unchanged. Proposal only; owner integration
and actual GitHub CI/PR re-review/human approval remain pending. No commit,
push/merge, production/shared database or frozen edits authorized/performed.

### Historical remediation v3

Independent audit reproduced three P2 blockers after the v2 run: ordinary
creation timestamps (F1), omitted SET_NULL collector locks/deadlock 40P01 (F2),
and unchecked Alembic tracking schema/head (F3). All 53 intake files and v2
manifest hashes were verified and byte-copied under ignored
`var/ms7-mig-v01-remediation-input`. Original audit/probes/results are copied
unchanged to `docs/acceptance/MS7-MIG-V01/independent-audit-v3/`.

Remediation: reproduce initial defects; restore Django ordinary pre-save rules
with separate historical Core import; collect/revalidate deletion and SET_NULL
lock union under the existing R02 total order; strictly prove Alembic tracking
shape/revision before operations. Add differential PG/concurrency/drift tests,
then repeat full target/runtime/baseline checks and write separate v3 evidence.
Previous local PASS does not supersede these findings or imply Task Approval.

Current v3 result: F1 differential comparison passes for all seven auto timestamp
fields, normal full/restricted saves and explicit historical import. F2 includes
deleted/CASCADE/SET_NULL participants plus FK reference closure before acquiring
the unchanged R02 total order. Both crossed-reference deletions COMMIT without
40P01. Revalidation accepts only unchanged mutations and a safe held lock superset;
new dependencies require outer rollback/restart. The held row set is taken from
actual FOR UPDATE results, not requested IDs; a disappeared/reused reference PK
requires restart rather than a false proof. New PROTECT and conflict/failure
tests pass. F3 strictly proves tracking columns/type/nullability/PK/index/default/
identity and exactly one owning head; malformed/unknown/ambiguous states fail
schema proof, adoption and CLI check without mutations.

Final target34/34/zero skips, runtime-only CLI10/10, repeated baseline verify_repo8/8
and R02 migration63/63 pass. Final Django discovery141 has118 executed/23 explicit
target-PG skips; all23 PG methods pass separately. First baseline140/118/22skips
is retained with its raw logs. Exact final results are in v3 evidence.
See [v3 report](../../acceptance/MS7-MIG-V01/implementation-report-v3.md) and
[v3 verification](../../acceptance/MS7-MIG-V01/verification-v3.json). Initial
audit/FAIL and unsuccessful partial F2 fixes are retained. The
[CI handoff v3](../../acceptance/MS7-MIG-V01/r03-ci-handoff-v3.md) is proposed only;
root files, frozen contracts, historical migrations and all v1/v2 evidence stay
unchanged. Independent re-audit/human Task Approval/GitHub CI remain pending.

### Historical v2 local verification

Continuation on 2026-10-09: user directly reports Ruslan's written R02-owner
approval for BIGINT on precisely the three B01 auth M2M PKs. The scoped
[compatibility addendum v1.0.0](../../acceptance/MS7-MIG-V01/compatibility-addendum-v1.0.0.md)
records source SHA/provenance; frozen R02 remains unchanged. Initial33 files
were present and prior manifest hashes matched before edits, with a local
preservation snapshot. Implementation continued from those files.

B01 is implemented and tested with IDs above int4; all related FK types remain
integer. CHECK investigation reproduced the cast deparse issue and the original
IN expression now yields exactly the frozen PostgreSQL catalog definition.
The comparator remains strict. Current target suite22/22/zero skips, target-only
fresh twice/A/B/C/check CLI10/10 with no Django installed, root verify_repo8/8,
R02 migration63 and R02A/R03A71 pass locally. Full results in
[verification v2](../../acceptance/MS7-MIG-V01/verification-v2.json).

The additive protocol catalog is captured separately as proposed V01 DDL; both
baseline and target constraints/types/indexes/identity/sequence drift are checked.
Unknown schema objects are refused. Ordered receipt/profile/publication locks
use their R02 stable keys; real two-connection blocking is tested.

R03 must apply/review the [concrete CI handoff](../../acceptance/MS7-MIG-V01/r03-ci-handoff-v2.md),
including target dependencies and explicit PG command. Root files were not edited.
CI/Linux, actual deployed profile variants and independent DDL/Task Approval remain
NOT VERIFIED/PENDING. This local run does not authorize commit/push/PR/cutover.

### Historical initial stop

Partial steps 2–5 exist, but fresh/A tests exposed the **B01** inconsistent ID
types in the accepted R02 mapping. Implementation stopped, as requested. See
[finding and proposed minimal decision](../../acceptance/MS7-MIG-V01/finding-B01.md).
Independent DDL/task review has not occurred. Rehearsal boolean flags used by
tests are synthetic guard exercises, not a record of human approval.

Profile A fixture currently assumes full baseline auth/admin/contenttypes/session
heads plus content0001, no users/no Grade timestamp. Smaller/different legacy
schemas are refused. Deployed profile variants still need owner review.

## Verification and history protection

Use `skills/verification/SKILL.md`. Dedicated Python3.12.10 venv and resolved
backend test lock; root locks untouched. PostgreSQL16.15 in newly created
`ms7-mig-v01-pg-20261009`, localhost55441, tmpfs and task label. Tests create only
new UUID-suffixed marked databases; clean up only the DB they created. No existing
DB inventory, production/shared environment or user credentials inspected.

Initial-session checks/results and remaining work were recorded in
[verification](../../acceptance/MS7-MIG-V01/verification.json) and
[trace](../../agent-traces/MS7-MIG-V01.md). Required broad verify_repo NOT RUN:
implementation stopped at B01 and no baseline runtime was bootstrapped then.
The continuation subsequently prepared a different disposable baseline runtime
and ran the unchanged entry point successfully; see verification-v2.json.
Frozen files and existing Django migrations have no Git changes.

Sequence setval is nontransactional. The adapter runs it last after immediate FK
validation, only advances, never rewinds; rollback injections are before setval.
Commit-time connection-loss/reconciliation after setval remains NOT VERIFIED.
Production stamp/cutover is unavailable and requires later reviewed ownership.

## Completion checklist

- [x] Exact input/scope/owners and required sources inspected
- [x] Partial target implementation and meaningful disposable test harness
- [x] Blocker surfaced, proposed minimal resolution, trace/evidence added
- [x] B01 resolved through user's direct report of owner approval, scope recorded
- [x] Fresh/A repair and full test rerun
- [x] Target protocol drift checks and PostgreSQL collector/two-connection row lock tests
- [x] Backend-only fresh venv/CLI and required local verification
- [x] Independent F1/F2/F3 reproduced and scoped remediation/regressions verified locally
- [ ] Independent remediation re-audit
- [ ] Final independent DDL/Task Approval, exact accepted-SHA/CI evidence
- [ ] Independent Ruslan DDL/Task Approval; CI/PR only after user authorization

Plan remains active until human acceptance. Local result is ready for independent
review; no Task Approval/program acceptance or downstream task start claimed.
