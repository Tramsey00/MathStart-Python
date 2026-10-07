# MS7-MIG-R01 — Baseline snapshot, architecture and ownership

- Status: **Active / INCOMPLETE — human gates pending**
- Owner: Руслан / Tramsey00
- Independent Reviewers / Task Approvers: Владимир / VladimirFrolov777 and Илья / 13baybars
- Issue: [#28](https://github.com/Tramsey00/MathStart-Python/issues/28)
- Gate: MIG-G0; separate baseline/ADR records from all three participants
- Window/deadline: 07.10.2026, Europe/Moscow, including checks/review; deadline is not acceptance
- Spec: [exact migration v1.1](../../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md), §§2–11, R01 §14, adaptation §17
- ADR: [Proposed ADR-0006](../../adr/ADR-0006-react-fastapi-migration.md)
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
approvals, current snapshot CI, reviewed scope/visual/byte policy, R02A/R03A
approval reconciliation. Grades missing approval was located, not fabricated.
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
- [ ] Independent review of final candidate/checks (agent evidence in PR46; human record required)
- [x] Snapshot draft PR46 prepared and attached; first head CI failure preserved, own frozen-document edits restored; corrected local baseline8/8/Harness73 PASS; current-head CI external PR evidence
- [ ] Snapshot independently approved and merged; resulting MIG_BASE_SHA established
- [ ] Integration/task branches created from accepted resulting baseline
- [ ] Separate MIG-G0 records from all three participants
- [ ] Independent R01 Task Approvals by Владимир and Илья
- [ ] Active plan completed only after required acceptance

Preparation is reviewable; dependent steps stay PENDING. R01 stops at the
required human gate and does not execute another migration task.
