# EXEC PLAN MS7-MIG-I01: React foundation without redesign

- Status: Active; implementation authorized 2026-10-09; checkpoint1 accepted by owner; checkpoint2 accepted; final local verification prepared; task remains INCOMPLETE.
- Owner: Ilya / 13baybars. Independent approvers: Ruslan UX/integration; Vladimir API/security.
- Issue: https://github.com/Tramsey00/MathStart-Python/issues/40
- Spec: [migration v1.1](../../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md)
- ADR: [ADR-0006](../../adr/ADR-0006-react-fastapi-migration.md)
- Human gates: final verification checkpoint accepted; commit/push/PR authorized by owner 2026-10-09; independent task approvals and merge remain pending.

## Inputs and boundaries
Start exact accepted integration8d958aeeb17da46839722441425ccbb5889e2ab7.
MIG_BASE60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7 is provenance, not start ref.
Django source appearance8c11edadc8debc81432d1db1145feac504f09061.
R01/R02 accepted; PR48 merged at start ref, contract manifest24 blobs checked.
Required AGENTS/PRODUCT/ARCHITECTURE/README/ADR0001/0006, migration spec,
R02 contracts/parity, MS6-I01 UX, MS7-I02/UI and MS7-I03 account inspected.
DB/migrations are not affected. Working DB, original checkout and R01 runtime
must remain unchanged. Earlier PLANNED/PENDING frozen markers are historical.

## Scope / sequence
1. Exact locked toolchain, framework routes/type generation and runnable shell.
2. Port approved components/gallery/strict fixture-only dispatcher.
3. Shared typed API/CSRF/error and stale-response foundation, no full account flow.
4. Component/negative/security and real browser checks at360/768/1440.
5. Own old-to-new index, reproducible evidence and independent review.
Checkpoint1 covered the toolchain/shell and initial components/route containers.
Checkpoint2 covers the scoped functional foundation and its evidence; task
acceptance still requires the independent verification/review gates below.

## Preserved behavior and downstream
No UI library/reset/global style change. Import existing CSS in original order.
Native /admin/ path, public/account/debug separation. ssr:false; I02 owns public
SSG/catalogue/metadata/full manifest. No production wildcard200 or private export.
I03 owns lesson/widget migration and F01–F04 fixes; I05 verifies them.
MS6-I01 UX evidence, MS7-I02 dispatcher guard and MS7-I03 identity lifecycle
are inputs; do not rewrite their historical approvals, pins or implementation.

## Verification and failure reporting
Follow [verification skill](../../../skills/verification/SKILL.md).
Record exact versions, command/exit/result; do not count model fixtures as runtime.
npm ci / typecheck / test / build; production debug/private-export guards;
later API generation/security/dispatcher/browser/E2E checks.
Keep historical tests, pin digests and source blobs unchanged.
Full verify_repo requires independently isolated configured verification/CI;
do not run it against working DB or existing R01 baseline.
First checkpoint visual comparison uses archived R01 plus source-derived shell
reference; record that distinction if R01 localhost8002 is unavailable.

## Risks / gates
CSS cascade/font/responsive drift; debug bundle leakage; build-time SSR safety;
API unknown outcomes/stale writes; frozen-byte normalization.
Stop on missing essential or conflicting R02 contracts, do not change semantics.
Historical target deadline08.10 has elapsed; record actual dates and remaining
forecast at checkpoints without changing the accepted calendar.

## Checkpoint2 actual status
Full gallery/strict dispatcher, generated API boundary/CSRF/errors/cancellation/stale
reads and route layout boundaries implemented.88 frontend tests plus5 unchanged
historical JS tests pass; typecheck/native ESM/build/production guards/ls/audit pass.
15 new browser screenshots; three source-derived shell pairs byte-identical; no
overflow; real skip/retry/field-error focus and dispatcher checks pass. Dedicated
hover transition remains unverified. Initial browser access issue resolved.
Own old-to-new mapping/checksums recorded; accepted tracked sources unchanged.
No full verify_repo/CI/commit/push/PR/DB work; independent approvals pending.

## Final verification checkpoint — 2026-10-09

[Final report](../../acceptance/MS7-MIG-I01/final/report.md),
[acceptance matrix](../../acceptance/MS7-MIG-I01/final/requirements-matrix.md),
[§17 mapping](../../acceptance/MS7-MIG-I01/final/old-to-new-evidence.json),
[PR draft/review plan](../../acceptance/MS7-MIG-I01/final/pr-draft.md).
Clean install/generation/typecheck/native validators/88 frontend+5 historical JS/
build/guards/audit all pass; dependency manifests and functional source unchanged
since accepted checkpoint2. verify_repo8/8 PASS using newly isolated SQLite only:
Django99 PASS/8 SKIP,R0318,Harness73. Extra contract/model suites pass.
Three live fresh SQLite Django/React gallery JPEGpairs byte-identical; keyboard/
focus/overflow/CSS isolation pass. Not R01/full-site/target runtime parity.
Dedicated hover and PostgreSQL-only checks remain unverified; Docker unavailable.
No existing DB/main/shared contracts/root CI changed; original snapshots preserved.
Final mapping now includes explicit platform_disposition/current_status required§17.
At verification checkpoint, implementation SHA/CI/tested merge-ref/independent approvals were pending; current binding follows below.
At that checkpoint Git publication permission was pending; now authorized below. Do not move this active plan to completed.

## Publication authorization — 2026-10-09

Owner accepted final verification checkpoint and authorized commit, ordinary push and PR to ms7-mig-react-fastapi (Refs #40). Independent task acceptance remains pending. Fetch confirmed integration unchanged at accepted input8d958aeeb17da46839722441425ccbb5889e2ab7; no conflicting task remote branch/PR; GitHub identity13baybars.

Implementation commit: `c54a98b91195458b22a14aa4a6cbf14c7fe57e28`;175 approved I01 files added, cached whitespace check exit0 and each staged blob equals inventory bytes. Follow-up publication metadata binds current §17/matrix to this tested code SHA; no functional or frozen source change. Final PR HEAD/CI and independent Task Approvals remain separate pending gates.
