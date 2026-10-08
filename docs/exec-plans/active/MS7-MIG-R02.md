# EXEC PLAN MS7-MIG-R02: Contracts and equivalence

- Status: Active / PROPOSED_RESULT_READY_FOR_REVIEW, not accepted or completed
- Owner: Руслан / Tramsey00; independent reviewers/Task Approvers: Владимир / VladimirFrolov777 and Илья /13baybars
- Created/updated:2026-10-08 Europe/Moscow; original target deadline08.10 including review retained
- Issue:[#29](https://github.com/Tramsey00/MathStart-Python/issues/29)
- Milestone MIG-G1; task branch ms7-mig-r02-contracts -> ms7-mig-react-fastapi
- Human gate: required, both independent decisions pending; no own approval
- Exact accepted input:c133f920fc14ab18a463e039f8e480e064ced81c
- MIG_BASE_SHA:60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7; application source8c11edadc8debc81432d1db1145feac504f09061
- Specs:[canonical migration](../../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md)§§2–11/R02/17,
  [new addenda](../../../specs/migration/r02-v1/README.md); ADR0006 and preserved ADR0001–0005

## Objective and preconditions

Reviewable separately versioned platform/auth/content/staff contracts, route
inventory and independent assertion matrix sufficient for V01–V04/I01–I04.
Read AGENTS, PRODUCT, ARCHITECTURE, README, docs/architecture, verification skill,
relevant ADR/contracts/R01 handoff/inventory/manifests/evidence/acceptance/ownership.
Inspected current URLs/views/services/models/migrations/admin and existing tests.
Live PR46/47 merged; PR47 independent APPROVED at66e9fd8; actual integration
c133f920 equals explicit user accepted input. No newer remote intake at start.
User confirmed full64-character canonical spec digest from R01; source unchanged.

## Scope and boundaries

Add-only new specs/migration/r02-v1, evidence/docs and contract tests. Only
framework-facing references for R02/R03/R02A/R03A; retain historical approvals/
IDs/digests/original_result. No target framework/dependency/scaffold/endpoints,
model/DDL/migration, working DB/bootstrap/publication, R03/V01/I01 task execution,
root platform docs/Harness/frozen tests/pin rewrites, source/UI fixes or deployment.
Content->Knowledge; Progress owns projections; no LLM call. Auth infrastructure
never grants domain evidence. All current staff operations retained.

## Current and target contract state

Current Django has8 API operations out of37 canonical planned, authored/public
pages, account, redirect/SEO/assets and nine admin registrations. New target
adapters remain proposed/not implemented. Contract distinguishes literal
baseline observations, proposed adapter decisions and future verification.
Complete20-table model mapping/114 physical columns/67 constraints/70 indexes/
22 applied migrations plus16 fresh identity sequences; R01 missing sequence
data is not claimed as a deployed inventory. Three baseline runtime sources
remain distinct. F01–F04 assigned13baybars, correction byI03/verificationI05.

## Changes and progression

1. Isolate worktree, exact refs/intake/provenance; preserve original checkout.
2. Derive full route/schema/permission mapping from baseline code and R01 records.
3. Version platform/auth/content/staff/§17 adapters with closed DTO/OAS, receipt
   bridge, lock protocol and publication recovery; explicit target obligations.
4. Independent frozen-baseline synthetic exchange/schema/OAS/digest/DAG tests,
   mutation negatives and real disposable baseline probes/verification.
5. Trace/handoff/contract digests, push scoped task branch, draft PR, exact-head
   integration CI and tested merge-ref; stop for independent human review.

No schema/seed/LLM/UI changes. Disposable test setup is the baseline verification
environment, not execution of V01/schema transfer or R03/toolchain adaptation.

## Verification and safety

Dedicated Python3.12.10 venv: exact requirements.lock --no-deps, pip check.
Fresh separate PG16.15 container ms7-mig-r02-pg-20261008 on127.0.0.1:55439,
DB ms6_v01_smoke_ms7_mig_r02_20261008, test DB test_ms7_mig_r02_20261008,
runtime<worktree>/var/r02-runtime; working5432 and R01 container55438 untouched.
fresh_install_smoke --disposable then full verify_repo, R02A/R03A/I02 suites,
R02 contract suite, safe read-only probes/schema metadata, diff/links/scope review.
Versions/results in [verification](../../acceptance/MS7-MIG-R02/verification.json).
No skipped check passes; target browser/runtime/upgrade/bridge races NOT_RUN.
Existing integration CI is baseline-only; it does not auto-run new R02 standalone
suite. Local new suite command/results are separate; adding target CI belongsR03.

## Risks and handoff

Unsupported deployed password/signing key or absent original bootstrap proof
blocks cutover; no mass reset/receipt deletion. Publication DB/asset split needs
real failure rehearsal inV04. V01 must verify actual source-profile sequences/
identity values. Baseline UserAdmin privilege assignment semantics are explicit;
a stricter policy needs an approved scope change. Synthetic data prove contract
comparisons, not FastAPI/React/PG target correctness. Production remains separate.

## Completion checklist / required gate

- [x] Accepted input/repository/contracts/code/tests inspected, isolation preserved
- [x] Proposed addenda/route/schema/parity/§17 index and F01–F04 criteria prepared
- [x] Baseline fresh/full checks and independent new contract suite passed locally
- [x] Trace and concrete reviewers' handoff prepared
- [ ] Draft PR/final CI disposition — final exact refs/links external in PR
- [ ] Владимир independent exact-head contract/backend/PG/security approval
- [ ] Илья independent exact-head UI/content/adapter approval
- [ ] Owner accepted integration intake after both approvals/current checks

Keep active plan here until actual human acceptance; Issue29 stays open until
final program integration->main workflow. Dependent implementation only after
accepted R02 CONTRACT at exact merged integration input. No automatic start.
