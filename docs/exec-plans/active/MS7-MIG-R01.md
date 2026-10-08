# MS7-MIG-R01 — Baseline snapshot, architecture and ownership

- Status: **Accepted snapshot / post-merge record amendment review pending — active only for final integration intake**
- Owner: Руслан / Tramsey00
- Independent Reviewers / Task Approvers: Владимир / VladimirFrolov777 and Илья / 13baybars
- Issue: [#28](https://github.com/Tramsey00/MathStart-Python/issues/28)
- Gate: MIG-G0; separate baseline/ADR records from all three participants
- Window/deadline: 07.10.2026, Europe/Moscow, including checks/review; deadline is not acceptance
- Spec: [exact migration v1.1](../../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md), §§2–11, R01 §14, adaptation §17
- ADR: [ADR-0006 accepted decision on reviewed revision](../../adr/ADR-0006-react-fastapi-migration.md)
- Evidence: [R01 records](../../acceptance/MS7-MIG-R01/README.md), [trace](../../agent-traces/MS7-MIG-R01.md)

## 1. Objective and scope

Prepare a reproducible current Django snapshot with source/runtime/admin/route/
command/test inventory, reviewed delta, exact input hashes, disposable baseline
checks, proposed platform decision, ownership and 18 registered canonical Issues.
Prepare concrete mandatory acceptance; never sign for participants. Preserve
original source/runtime/user QA files and frozen contracts/history.

R01 authorizes records, snapshot commit/push/draft PR, read-only working DB and
disposable Django checks. Registration of the other 17 Issues is organizational
only. R02–R06/V01–V06/I01–I06 execution, React/FastAPI scaffolds, new dependencies,
SQLAlchemy/Alembic, target CI/Harness rewrites, main-spec revision, redesign,
publication to working DB and deployment are excluded. No agents are delegated.

## 2. Inputs, preconditions and current state

Mandatory repository/spec/ADR/README/architecture/verification skill and relevant
plans/traces/contracts/code/tests/migrations were inspected. GitHub live API and
fresh fetch establish remote/local main input
`8c11edadc8debc81432d1db1145feac504f09061`, zero ahead/behind and no staged or
unstaged source changes. Previous fixes are already merged in PR27. Untracked
recovery trace is the sole local intake; output/tmp are preserved and excluded.
Source totals: 1,026 tracked input files, 263 lessons, 97 local CSS, seven local JS,
16 structural page.json, 13 templates. Preservation is not content/visual approval.

Working PostgreSQL schema is audited in an explicit REPEATABLE READ READ ONLY
transaction, checks mode/isolation, SELECTs only and ROLLBACK. Current content/
users migrations are applied; 281 pages/279 published, two retained retired rows.
Source/render/runtime digests are separate. Structural CRLF/LF drift is recorded,
not overwritten. Current Django remains the working/accepted platform until the
new platform gate is actually accepted; all target implementation is pending.

## 3. Workflow and concrete isolation

Preparation uses `ms7-mig-baseline` from **fresh origin/main**, input 8c11eda,
at `C:/Projects/MathStart-Python/tmp/ms7-mig-r01/snapshot`. The original checkout
stays on main at `C:/Projects/MathStart-Python`. Do not merge a whole local branch,
reset/clean, overwrite existing QA, force-push or reuse working DB credentials.
The only transferred local file is hashed/reviewed recovery evidence.

R01 baseline snapshot PR targets main and contains substantive manifests/records,
not duplicate PR27 fixes. Its actual candidate head and CI/tested merge-ref are
recorded with the PR. `MIG_BASE_SHA = PENDING` until accepted snapshot merge;
the resulting main SHA becomes MIG_BASE_SHA only then. After this gate, create
`ms7-mig-react-fastapi` from that SHA and task `ms7-mig-r01-baseline` from current
accepted integration. Neither branch is created during pre-acceptance R01.
Documents prepared on snapshot do not claim accepted integration status.

Actual disposable R01 PostgreSQL: container `ms7-mig-r01-pg-20261007`, localhost
port **55437**, runtime DB `ms6_v01_smoke_ms7_mig_r01_20261007`, separate test DB
`test_ms7_mig_r01_20261007`; runtime root
`C:/Projects/MathStart-Python/tmp/ms7-mig-r01/qa/runtime`; optional R01 HTTP
port **8017** reserved for baseline only. Working DB port5432/dev port8000 are
untouched. Existing Python `.venv312/Scripts/python.exe` is used with unchanged
installed lock; no package installation/new dependency. Disposable credentials
are synthetic and remain outside Git. Runtime media/static/reports are isolated.

Future per-task worktree/runtime/port/DB reservations are in
[issue-branch-owner-map.json](../../acceptance/MS7-MIG-R01/issue-branch-owner-map.json).
They are names/paths only, not created environments. They must be rechecked for
availability before each later task. Follow accepted exact upstream and personal
queue order; all dependency kinds enter cycle verification.

## 4. Ownership and calendar

| Area | Owner | Independent reviewer / approver |
| --- | --- | --- |
| R01 snapshot, ADR, root docs, verify/CI/Harness | Tramsey00 | VladimirFrolov777 and 13baybars |
| Backend/schema/Alembic chain/backend lock/auth/staff authorization | VladimirFrolov777 | Tramsey00; 13baybars consumer handoff when applicable |
| Frontend/routes/lock/tokens/UI/lesson lifecycle/private export | 13baybars | Tramsey00 UX/integration and VladimirFrolov777 API/security |
| Integration intake/release assembly | Tramsey00 | VladimirFrolov777 and 13baybars, separate release gate |
| Current live schema and writes | Django migrations/services only | No R01 ownership transfer or live migration |

One writable Alembic owner; never concurrent Django/Alembic ownership of tables.
Shared files require owner-agreed patch/PR, not simultaneous worktree edits.
R01 record work changes no API/domain/schema/LLM semantics.

Calendar is copied as forecast from §11, **Europe/Moscow**: MIG-G0 07.10 18:00;
MIG-G1 09.10 21:00; MIG-G2 11.10 21:00; MIG-G3 12.10 22:00; MIG-G4 13.10 23:59.
On 13.10 backend/frontend handoff12:00, candidate15:00, review18:00. Individual
deadlines/queues are in the map: R(07,08,10,12,12,13), V(08,09,10,11,12,13),
I(08,09,10,11,12,13). These are not permission to start later tasks or evidence
of on-time completion. Missing checks/review keeps the gate pending; forecast
recalculation belongs to the owner without reducing scope or tests.

## 5. Steps and verification

1. Read/inspect live remote and original tree; audit local delta and old output
   paths. Preserve tracked input and recovery trace, capture source and frozen
   digests. Record line-ending differences distinctly from semantic delta.
2. Audit working DB in verified read-only transaction, schema/aggregate only;
   enumerate all admin/route/command/asset families. Record drift and open scope
   decisions. No original DB setup/repair is performed.
3. Prepare candidate in isolated snapshot, exact canonical Markdown input and
   manifests; write proposed ADR, current-status links and active plan.
4. Register/reuse 18 Issues after canonical-ID search; actual assignments and
   dependency URLs, DAG and reserved isolation map. Do not modify historical
   Issues/PR or execute downstream work.
5. Run unchanged `python scripts/fresh_install_smoke.py --disposable` and
   `python scripts/verify_repo.py` on explicit disposable PG; existing R02A,
   R03A and UI/reference suites; pip check/versions; route/static/redirect smoke,
   frozen pins, manifest/source/delta/links/secrets checks, `git diff --check`.
   Capture exact commands/exit codes and sanitized logs. Classify failures per
   `skills/verification/SKILL.md`; no skip to obtain green.
6. Commit explicit allowlist, push snapshot, create/reuse draft PR→main, attach
   PR, check CI at actual head/tested merge-ref, save evidence. Prepare independent
   acceptance records and decision list. Do not self-merge.

No schema/API/UI/seed/LLM change or new implementation tests are planned. Inventory
scripts are task evidence utilities, not a replacement verification entry point.
Run existing meaningful tests; audit manifests/dependency/link completeness.
Fresh migrations/bootstrap run **only on the disposable DB**.

## 6. Human gates, blockers and rollback

The [acceptance record](../../acceptance/MS7-MIG-R01/acceptance.md) names exact
decisions and separates Task Approval, snapshot merge and MIG-G0. Required:
three participant records for baseline/ADR, independent Владимир and Илья R01
approvals, current snapshot CI, reviewed scope/visual/byte policy. R02A/R03A acceptance reconciliation D08 CLOSED by verified VladimirFrolov777 comments of 07.10.2026; no earlier approval inferred. Grades approval was located, not fabricated.
Production host/staging-only boundary and auth re-login are proposed decisions.

If rejected, revise task-owned docs with additive commits; leave original tree,
runtime evidence, output/tmp, old Issues/PR/traces and frozen pins intact. R01
rollback affects only proposed snapshot/docs. No data restore/drop/stamp occurs.
Keep this plan active until actual human acceptance; no automatic completed move.

## 7. Completion checklist

- [x] Live input and preserved local delta identified; source/runtime manifests separate
- [x] Working schema read-only and admin/route/command/source inventory captured
- [x] Exact migration input imported; proposed ADR and §17 index prepared
- [x] 18 Issues assigned with real URLs and acyclic dependencies; later tasks PLANNED
- [x] Independent reviewed-head approvals and explicit owner report of both e510744 confirmations; PR/main CI PASS
- [x] Snapshot draft PR46 prepared and attached; first head CI failure preserved, own frozen-document edits restored; corrected local baseline8/8/Harness73 PASS; current-head CI external PR evidence
- [x] Snapshot independently approved at daf4e603, e510744 confirmation owner-reported; PR46 merged, resulting MIG_BASE_SHA established
- [x] Integration/R01 task branches created from exact accepted resulting baseline; no later branch
- [x] Separate MIG-G0 records from all three participants at reviewed daf4e603
- [x] Independent R01 Task Approvals by Владимир and Илья at reviewed daf4e603
- [ ] Complete/move plan after new post-merge records task PR review and accepted integration intake

Preparation is reviewable; dependent steps stay PENDING. R01 stops at the
required human gate and does not execute another migration task.

## Participant evidence follow-up — 2026-10-08 Europe/Moscow

Import [Ilya package](../../acceptance/MS7-MIG-R01/ilya-20261007/README.md) into
same ms7-mig-baseline worktree/PR46 from prior candidate43b4fa10aec2af589c51857d037e973215557255.
Canonical application8c11edad remains unchanged; no new runtime/branch/later task.
Live own comment supplies partial D02/D03 UI/content acceptance, with final
Task Approval explicitly deferred to new exact HEAD review+green CI. Owner's
direct D02 choice freezes source with F01–F04 and mandatory follow-up.
Three runtime evidence sources are separated; original HOLD/PENDING reports
remain exact historical exports. [F01–F04 map](../../acceptance/MS7-MIG-R01/ilya-20261007/follow-up-F01-F04.md)
proposes existing R02#29/I03#42/I05#44 follow-up; tracking owner Tramsey00,
specific implementation/verifier assignment and calendar PENDING. No task starts.

Byte/hashes/source/historical preservation and links validated; record manifest
regenerated. Current containing HEAD/tested merge-ref/CI in PR46. R01 remains
INCOMPLETE, MIG-G0/MIG_BASE_SHA PENDING; D08 CLOSED is retained, collective
D02/D03 and D01/D04–D07/D09 plus both final Task Approvals remain pending.

## Final human acceptance reconciliation — 08.10.2026 Europe/Moscow

[Three own records and two Task Approvals](../../acceptance/MS7-MIG-R01/final-human-acceptance-20261008.json)
verified live at exact daf4e6038761f8d1bf1c60f0976473d987cce230;
CI37688709748 SUCCESS/tested merged9dcc3381a2c9a0721d546065387f9f7f7b45af4.
D01–D09 human conditions recorded in participant scopes; Vladimir D09 agreement
reported by Ruslan's direct message, not a fabricated Vladimir comment.
R01 planned07.10, actual acceptance08.10; delay retained. Remaining calendar
targets, including MIG-G4 13.10.2026 23:59 Moscow, unchanged; no reduced scope/checks.
F01–F04 assigned13baybars, correct no later than I03, verify I05; F04 readable
at ordinary scale, no clipping/overlap, enlargement alone insufficient.
Optional separate independent Vladimir F04 review agreement PENDING/not given.

New documentation-only commit requires [reviewer confirmation](../../acceptance/MS7-MIG-R01/final-review-changes.md)
at exact new HEAD/current CI. Old approvals not transferred. Keep plan active;
snapshot merge/MIG_BASE_SHA/integration and task branch steps PENDING. No later
task execution, working DB/app change or Issue closure. Earlier partial/pending
sections above are chronological preparation history, superseded only by these
current human records.

## Current post-merge phase — 08.10.2026 Europe/Moscow

Snapshot PR46 merged at01:47:59 Moscow: accepted PR head `e510744fcd87a22956aa71d5e22f20235e2af1c1`,
actual resulting commit/MIG_BASE_SHA `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
Live PR metadata, commit parent/tree, both CI and three human sources in
[post-merge provenance](../../acceptance/MS7-MIG-R01/post-merge-provenance-20261008.json).
Owner explicitly reports both reviewers confirmed the e510744 documentation in
their chat; GitHub approvals stay daf4e603, merge itself not treated as approval.

Integration `ms7-mig-react-fastapi` created remotely exactly at resulting SHA;
`ms7-mig-r01-baseline` input same SHA, worktree
C:/Projects/MathStart-Python/tmp/ms7-mig-r01/post-merge. Only R01 post-merge
records; task PR→integration Refs #28, no direct main push. Core R01 snapshot
accepted / MIG-G0 accepted for that snapshot; active plan retained only pending
post-merge amendment review/intake, no automatic acceptance of this new HEAD.

Fresh verification uses a new disposable R01 PostgreSQL container
ms7-mig-r01-postmerge-pg-20261008, localhost55438, runtime DB
ms6_v01_smoke_ms7_mig_r01_postmerge_20261008, test DB
test_ms7_mig_r01_postmerge_20261008, runtime root
C:/Projects/MathStart-Python/tmp/ms7-mig-r01/qa/postmerge-runtime.
Working5432/8000 untouched; no following task environment created.
Remaining calendar and mandatory assigned F01–F04 I03/I05 unchanged.
Original plan sections above describe historical preparation, not current
pending snapshot/branch state. [R02 handoff inputs](../../acceptance/MS7-MIG-R01/R02-input-handoff.md)
are records only. All18 Issues stay OPEN, no R02/I01 execution.

Current post-merge amendment: [draft task PR47](https://github.com/Tramsey00/MathStart-Python/pull/47) → ms7-mig-react-fastapi, Refs #28. First published head77d8c81dcb777cc29d6b50ed92e65a1a25bcfbd4; final containing head/validation in live PR. Independent record amendment review/intake pending; no approval inferred for either new record commit.

## Narrow CI trigger extension and pin conflict — 08.10.2026

Owner explicitly authorizes two existing ci.yml branch filters to include
ms7-mig-react-fastapi while preserving main, existing jobs/locks/PostgreSQL/checks.
This enables §9 task PR→integration and integration push baseline verification;
full target platform verification remains R03, not started.

Input PR47 head9fde3e53deba29b08574c41539e68b4d43e7a6b4, live base/integration
60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7, PR OPEN/ready (owner had removed draft).
MIG_BASE_SHA unchanged. No local/working DB use; unchanged CI creates disposable PG.

[Exact trigger delta/conflict](../../acceptance/MS7-MIG-R01/ci-trigger-adjustment-20261008.json):
jobs byte-identical, but MS7-R02A candidate-manifest pins the whole ci.yml.
Existing strict R02A test now fails1/30 with expected old/current digests.
Preserve manifest, tests and historical evidence; do not regenerate pin for green,
skip/relax check or silently classify the contract as compatible.
CI current-head run required, actual outcome recorded in PR47. Acceptance blocked
until separate human decision resolves this pin compatibility and required CI passes.
Active plan retained; original baseline/ADR acceptance unaffected.
[Reviewer delta](../../acceptance/MS7-MIG-R01/pr47-review-delta.md).

Observed first integration CI run37701885197 on e64d9a4: FAIL R02A1/30,
baseline8/8 and fresh PG smoke PASS, R03A NOT RUN after failure.
Actual tested checkout4a62032c033543ef4a282981a8d97585a579ca33.
[Sanitized receipt](../../acceptance/MS7-MIG-R01/ci-integration-trigger-first-run.json).
Final record head needs a new actual run; final evidence external PR47.
Human pin compatibility decision and authorized corrective scope remain required,
followed by successful exact-head checks and independent amendment acceptance.
No weakened checks/pin regeneration to manufacture PASS. Plan remains active.

## Current separate migration workflow correction — 08.10.2026

Owner authorizes restoring ci.yml exactly from MIG_BASE_SHA and adding separate
migration-ci.yml, name Migration baseline verification, only integration PR/push.
Old main-only ci.yml SHA2561edf8fc5023a171d6bd4c173b7a30e717b197a4d939649729b16054bf48e3ea7
again matches the untouched R02A pin. New workflow full jobs block byte-identical
to accepted ci.yml; no reusable conversion, locks/checks/PG/env/Python change.
[Correction record](../../acceptance/MS7-MIG-R01/migration-ci-correction-20261008.json).

Failed filter variant above remains historical: e64d9a4/run37701885197 and
f0c913e/run37702653809 FAIL R02A. Both receipts/old PR description preserved.
Pin incompatibility corrected through exact restoration, not pin/test edits.
Local Python3.12.10 pip check PASS, R02A30/I02frozen-upstream7/R03A41 PASS/exit0.
Actual new-head migration workflow CI and independent amendment review required.
MIG_BASE_SHA/integration60b341f unchanged. No working DB/target dependencies/
API contracts or R02/I01/R03 implementation. Scope is existing baseline checks,
full target verification remains R03. Active plan retained until final intake.
