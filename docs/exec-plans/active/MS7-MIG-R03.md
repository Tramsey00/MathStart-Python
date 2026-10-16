# EXEC PLAN MS7-MIG-R03: Target verification and Harness adapters

- Status: ACTIVE / INCOMPLETE; integration and independent approval pending
- Owner: Руслан / Tramsey00; reviewers: Владимир and Илья in their assigned zones
- Date: 2026-10-09 Europe/Moscow; deadline: 2026-10-10 including review/integration
- Issue: https://github.com/Tramsey00/MathStart-Python/issues/30
- Branch: ms7-mig-r03-verification -> ms7-mig-react-fastapi; Refs #30
- Current accepted input: `a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6`
- Previous accepted input: `0c03197e23f69a233c0fcf8bdffa336feca20b92` (historical provenance)
- Historical input: `8d958aeeb17da46839722441425ccbb5889e2ab7` (preserved provenance)
- Immutable MIG_BASE_SHA: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`
- HARD R02 and its parity CONTRACT accepted through owner receipt:
  https://github.com/Tramsey00/MathStart-Python/pull/48#issuecomment-6070829593
- INTEGRATION V02 (#35): ACCEPTED_INTEGRATION, Task Approval5538854677 at8256cbf; verified squash a359b0b / parent0c03197 / equal tree74c30145. I02 (#41) full pipeline not accepted; limited source compatibility review received at producer8256cbf / consumer47baaa9.
- Authority: canonical migration v1.1 §§3–11, R03 card, §17;
  ADR-0006; preserved ADR-0001–0005 and r02-v1 parity matrix.

## Objective and inspection

Port verification routing and CI without changing frozen domain semantics or
claiming unimplemented runtime evidence. Read AGENTS, PRODUCT, ARCHITECTURE,
README, docs/architecture, verification skill, relevant ADRs/contracts, R01/R02
plans/handoff/history and the actual scripts/Harness/tests before edits.
Attached migration Markdown equals the canonical input blob byte for byte:
SHA256 `c5a554e3911bdb43db28d67fd02d26e38d50b2820e1154a272d89ecb44b1faae`.
Old v7.1 PDF hash matches the canonical requirement; its platform direction is
superseded in migration scope by accepted ADR-0006, not its domain invariants.

## Scope and boundaries

R03 owns scripts/check wrappers, verification registry, migration CI and Harness
command adapter/tests/docs. Preserve historical check IDs, manifests, original
results, approvals and source/frozen pins. No backend/frontend implementation,
DDL, dependency lock owned by V/I, working database write, product feature,
R04/V/I execution, merge, Issue closure or deployment. No subagents requested.
Normal checks use no live Product LLM. Bootstrap Codex desktop surface remains
explicit; this task does not claim the future full Harness gate.

## Implementation sequence

1. Isolated R03 worktree at accepted input; record live refs and source hashes.
2. Add target/pure routing to verify_repo; keep legacy compatibility explicitly
   for preserved ci.yml, with target Harness repo-baseline and no recursion.
3. Add bounded fail-closed command wrappers, PG diagnostic/version adapters and
   source preservation checks. Runtime command handoff is reviewed separately;
   absent required owner commands fail, never fallback to Django or SQLite.
4. Add pure/Harness and target CI on task/integration/main, accepted-input R02
   historical suite, exact checkout/head/merge-parent/tree evidence and artifacts.
5. Test routing, missing tools/empty suites/failure/timeout/PG negatives and fake
   CLI lifecycle; execute available checks, record absent runtime blockers.
6. Publish a draft PR with trace, §17 evidence index and precise handoff. No merge.

## Verification and gates

Dedicated Python3.12 environment without Django/DRF proves pure/Harness portability.
Separate disposable PG16 service/DB/port; no working DB/bootstrap. Historical R02
63 includes Django baseline assertions and a full HEAD preservation assertion;
run unchanged at accepted input, label historical evidence. Its protocol32 plus
R03/R02A/R03A run on current target tree without Django. Target runtime replacements
for remaining historical assertions require owner implementations and approval.
Frozen ci.yml stays byte-identical. Do not rewrite its manifest pin.

Completion requires accepted V02/I02, real target PG fresh/upgrade/content/frontend
build/browser evidence at final SHA, successful applicable CI and independent
Vladimir/Ilya approvals. Keep plan active while any gate remains outstanding.
The draft PR is a reviewable increment, not ACCEPTED_INTEGRATION or COMPLETE.

## Observable execution result

Implemented registry/wrappers/CI/docs and21 adapter regressions; frozen files
preserved outside the10 scoped adapter paths. Pure R0318/R02A30/R03A41/model32
and Harness73 PASS without Django. Legacy disposable fresh and full8/8 PASS
(Django107/R0318/Harness73); unchanged accepted-input R02 suite63 PASS.
PG16.15 read-only positive/failed-port exits0/1. Full target exits1 because10
runtime checks lack owner inputs; target fresh/upgrade fail explicitly. Results
and versions: docs/acceptance/MS7-MIG-R03/verification.json. Proceed only with
draft publication/current-head CI and independent review; implementation scope
does not authorize V/I delivery or closing integration blockers by assumption.

## Historical frontend CI follow-up — 2026-10-11 (superseded current acceptance)

User authorized only the R03/root CI wiring and execution for reviewed PR50
candidate150279e6, preserving frozen baseline workflows and historical captures.
Separate workflow and bounded stdlib adapter install exact Node/npm, locked
frontend dependencies and invoke the unchanged I01 foundation suite. Separate
R03/candidate checkouts and live PR pins prevent stale SHA or approval transfer.
Execute adapter negatives, preservation, CI and retain raw receipts/run URL;
record final results in a new follow-up trace. No I01 implementation/acceptance,
manual hover or UX/integration approval is included. API/security approval
Vladimir5483318464 is live evidence only for the specified I01 candidate.
Detailed contract/limits: docs/acceptance/MS7-MIG-R03/frontend-pr50-ci.md.

## Historical V01 target PostgreSQL CI follow-up — 2026-10-11

User authorizes R03-only separate target CI per PR51 handoff v5, at explicitly
pinned current candidate393d988 (backend unchanged from reviewed1f97d762).
Create owned disposable PG16 service and separate22-package test-lock venv;
execute unchanged explicit34-case/23-PG gate without skips, observe fresh2,
upgradeABC, negatives and complete cleanup. Record live head vs actual candidate
and R03 workflow checkout, raw outputs and immutable new evidence. Prepare final
Independent Task Approval materials, without granting approval, expanding V01,
merging or closing Issues. Preserve historical evidence and frozen workflows.
Contract/result: docs/acceptance/MS7-MIG-R03/postgres-pr51-ci.md; follow-up trace
docs/agent-traces/MS7-MIG-R03-postgres-pr51-ci.md. Wider R03 completion and I01
hover/UX/integration gates remain pending independently.

V01 CI handoff delivered: run38156436658 SUCCESS at exact candidate393d988;
34/23 PASS without skips, fresh2/ABC,57 cleaned databases and verified tmpfs
service lifecycle. Raw artifact retained and final Independent Task Approval
packet prepared. No human approval or global R03 completion is declared.

Subsequent external receipt5484103844 approved exact V01 candidate393d988 and
external squash merge4a1b8b0 occurred during publication. R03 did not perform
either action; recorded separately in external-state-v7 and packet. Later CI
guard refusal on changed merge-ref/closed PR is not presented as a PASS.
Existing requested input8d958ae/MIG_BASE remain the provenance of this increment;
no wider R03/V02/I02 or post-merge integration work is started by this observation.

## Current accepted integration follow-up — 2026-10-12

I01 and V01 are ACCEPTED_INTEGRATION under human approvals5484114333 and5484103844
and external merges0c03197/4a1b8b0. Current input is0c03197; old8d958 remains
historical. I01 UX/integration approval is received with the accepted fixture
banner limitation and both open follow-ups. Issues34/40 remain open until main.
Current records, joint suites and remaining R03 gates:
[accepted-integration handoff](../../acceptance/MS7-MIG-R03/accepted-integration-ci-20261012.md).
Earlier dated pending snapshots above are history, not current I01/V01 status.
R03 remains ACTIVE / INCOMPLETE; no task acceptance, merge or Issue closure.

## CLI/receipt handoff preparation — 2026-10-12

[Concrete owner/review checklist](../../acceptance/MS7-MIG-R03/cli-receipt-handoff-checklist.md) maps all10 backend checks,4 frontend
checks and7 baseline content commands to V02/I02/V04 deliverables and R02 parity
assertions. Accepted V01 schema/foundation evidence remains separate. The new
machine checklist is PREPARED_FOR_OWNER_REVIEW; runtime-commands remains PENDING
with no invented commands. No accepted V02/I02/V04 input is available at intake.
Full target execution awaits accepted exact-SHA inputs and reviewed command
contracts; R03 stays INCOMPLETE until full checks and independent approvals.

## V02 external publication gate intake — 2026-10-13

User approves only40 pinned publication exception paths and73 separately retained
raw paths. [Gate review packet](../../acceptance/MS7-MIG-R03/v02-external-publication-gate.md)
records the exact isolated external v3 command, trust/data pins, negative controls
and clean Linux CI criteria. Original verified snapshot, actual approved bindings,
auditor raw output, verifier v3 and anchor digest are not yet available. Requested
them from Владимир under explicit authorization. Gate NOT_READY; trusted pins
remain null in the intake record, not synthetic approval. No V02-owned changes,
gate execution/CI proof, V02 Task Approval, merge or Issue closure. R03 INCOMPLETE.

### Received V02 reference documents — 2026-10-13

Four original documents now received and preserved losslessly; both supplied
SHA256 PASS. [Document reconciliation](../../acceptance/MS7-MIG-R03/v02-publication-document-reconciliation-20261013.json)
matches five control tuples and exact40 paths against auditor tables. The user's
limited exception decision is APPROVED; earlier unavailable/pending-policy wording
is historical. R03 creates actual owner metadata anchor v3 and digest after
independent original-source verification, not Владимир. Full151 staged snapshot,
complete73 inventory and raw streams still pending; actual execution pins remain
null. Gate NOT_READY, real negatives/Linux CI NOT_RUN, R03 INCOMPLETE.

### V02 tree transcription resolution — 2026-10-14

[Transport resolution](../../acceptance/MS7-MIG-R03/v02-tree-oid-resolution-20261014.md)
records user-confirmed correct unchanged tree pin and independent BASE+151 inventory
hashing. Expected typo in supplied inventory/REPORT preserved as original evidence;
packaging may resume. Full151/73 declarative inventories known; real archive,
source/effective metadata, trusted v3/anchor/negative/Linux evidence still pending.
Gate NOT_READY; R03 INCOMPLETE, V02 Task Approval/merge separate.

### Original snapshot and executable publication gate — 2026-10-14

User supplied exact original ZIP and authorized R03 implementation/CI in PR49.
Actual151 blobs/metadata, prior bindings/auditor,2092 BASE objects,1672+151=1823
entries and approved tree dbad1e853dff354c5d3255755afb5cc32e0ad279 verified.
Separate owner controls/real schema-v3 anchor pinned; candidate repinning forbidden.
Final control1b75c6e and workflow21a82d4 run38596739924 SUCCESS: positive0,
17 expected negative rejections, restored positive0, full whitespace3887/6
FAIL/2 exact raw and both scoped PASS/0. Earlier success and local setup failures
retained separately. Current gate **READY_FOR_OWNER_REVIEW**, with
[concrete review packet](../../acceptance/MS7-MIG-R03/v02-publication-20261014/review-packet.md).
No implementation commit, V02 publication/Task Approval/merge or Issue closure.

Migration verify/pure and accepted I01/V01 checks pass; full target fails the
unchanged REVIEWED/all10-command prerequisite (actual PENDING/empty commands).
Its subsequent stages remain NOT_RUN. After separate gate confirmation and
publication authorization, verify exact implementation SHA; then accepted V02/I02
and V04 CLI handoff, full target/PG/browser combined-SHA execution and independent
Vladimir/Ilya approvals remain mandatory. R03 stays ACTIVE / INCOMPLETE.

### Human confirmation and published-commit CI handoff — 2026-10-14

The human user confirmed exact run38596739924, PR49 review head5511284, anchor
SHA2565a9a7a65 and control revision1b75c6e. Vladimir is authorized to publish
unchanged source with single parent0c03197 and tree dbad1e853dff354c5d3255755afb5cc32e0ad279.
[Separate decision and execution handoff](../../acceptance/MS7-MIG-R03/v02-publication-20261014/published-handoff.md)
preserves all original source/evidence. Live open PR/ref discovery has no migration
V02 candidate, so implementation PR/SHA and published gate remain NOT_RUN/null.

R03-only published-v02-ci/published_v02_ci orchestration checks confirmed trust
pins, current owner/task PR HEAD before/after, exact parent/tree and fresh Linux
checkout, then invokes unchanged confirmed bootstrap in published mode. It is
triggered by a real committed candidate input after receipt; no synthetic input
or replacement implementation commit is created.12 synthetic guard regressions
PASS, pure6 PASS and frozen/historical preservation PASS. These are not published
V02 evidence. Final V02 review needs exact candidate/runtime/case/consumer evidence
and Ruslan's Task Approval. Merge/Issue closure stay unauthorized; R03 INCOMPLETE.

### Published V02 exact-commit technical review — 2026-10-15

User supplied PR53 implementation76d8eac, unchanged only parent0c03197/tree dbad1e8
and authorized R03 CI/task verification. Live owner/repository/base/HEAD and Git
metadata match. Canonical R03 candidate input pinned; published workflow a743323
run38637910883 SUCCESS on fresh Linux using unchanged confirmed control1b75c6e
and anchor5a9a7a65. Actual HEAD/index/tree, mandatory verifier0, full whitespace
3887/6 FAIL2 and both scoped0 preserved; live HEAD rechecked unchanged.

R03-only separate task CI aefba6a run38642117604 SUCCESS:86 V02/all40 PG and34
V01/all23 PG,0 skips, native F01/F02 comparator8, R0263/R02A30/R03A41, Content
279/263 and real runtime/service without Django/DRF. Separate owner locked venvs,
PG16 tmpfs services, guarded empty before/after and explicit cleanup verified.
Original GitHub ZIP digests and every retained raw byte/manifest/command hash
reconciled. First task run38641371932 successful suites but incomplete hidden
cache upload retained separately; owned upload fix plus strict final rerun closes
that R03 packaging finding. Baseline38635496099 remains separate8-check legacy
evidence, not V02 suite. All V02-owned implementation/locks/tests untouched.

[Technical review packet](../../acceptance/MS7-MIG-R03/v02-review-20261015/review-packet.md),
current §17 overlay and concrete V02 service/CLI/receipt/consumer handoff are
prepared. Human exact-HEAD V02 Task Approval/applicable consumer review pending;
no Task Approval/draft promotion/merge/Issue closure. V02 card's INTEGRATION:-
does not acquire a new global R03 dependency. Full R03 target still fails
PENDING/empty command-map prerequisite, later stages NOT_RUN; accepted V02/I02,
applicable V04 CLI, reviewed10/4 commands, full combined pipeline and independent
Vladimir/Ilya R03 approvals remain outstanding. R03 ACTIVE / INCOMPLETE.

### Authorized V02 direct successor intake — 2026-10-15

User authorizes a narrow additional PR53 commit for HOME alias validation and
pinned-release renderer context, with sole parent76d8eac. Old only-parent-BASE
guard remains unchanged for the old candidate; a separate additive chain/delta
guard checks BASE→76d8eac→new HEAD, independently reviewed patch/blob/metadata/
attributes pins, original raw40/73 and controls preservation, before/after live
HEAD, and fresh Linux actual checkout. It replays unchanged v3 only at original
76d8eac and does not re-anchor that verifier to a different tree. No automatic
new SHA/tree/policy pins or transfer of approval. Original input/control/evidence
files stay unchanged; new pending intake has null successor pins.

Live PR53 still76d8eac; new commit/diff and exact agreed renderer context handoff
are not yet received. Human approval5525315946 by Tramsey00 at76d8eac is observed
and recorded separately; the earlier pending packet is pre-receipt history.
PR open/draft, no merge/ACCEPTED_INTEGRATION claim. Successor gate/task suites
NOT_RUN / NOT_READY; required current-case inventory includes all old86 IDs plus
reviewed new cases/subcases, V01 separate34/all23 PG, F01/F02, Content/contracts,
§17 and target runtime without Django. No V02 implementation/lock/test changes.
[Concrete successor handoff](../../acceptance/MS7-MIG-R03/v02-successor-20261015/handoff.md)
records exact remaining inputs and review sequence. Preparation guard regressions
are synthetic, not evidence for an unpublished successor. R03 INCOMPLETE.

### Published V02 successor8256cbf current review — 2026-10-15

User supplies exact8256cbf/only parent76d8eac/tree74c3014 and confirms five agreed
modifications plus63 acceptance additions and current alias policy. API/Git live
owner/base/HEAD/parent/tree match. Independent source review/AST inventory and
owner evidence/hash claims reconcile; all other1818 predecessor files unchanged.
New R03 scope04a47175 and binary patch2a573fdd pinned before execution, original
input/control/anchor/raw evidence retained. No policy reapproval requested.

R03 observer adapted only to independently pinned118/all50 PG IDs, with old86
retained and full68-file dependency closure including helper verifier/JSON inputs.
Separate fresh Linux gate/task jobs in run38784183591 SUCCESS at R03 control/
workflow0effadc. Original unchanged v3 runs on76d8eac only; new tree verified by
exact chain/delta guard. Current118/all50 PG, separate V0134/all23 PG (fresh2/ABC/
negatives), F01/F02/native8, contracts63/30/41, Content279/263 and actual runtime
without Django/DRF PASS/0 skips. All20 phases, DB/service/PID cleanup verified.
Both delta/scoped whitespace PASS0; original full3887/6 FAIL2 streams preserved.

Downloaded raw artifacts SHA256 verified; gate602 members/601+65 manifest rows/
290 commands, task1067 members/1059 rows/40 commands,0 missing, all expected exits
and every case/subcase PASS. Baseline38760171595 SUCCESS is separate8-check
legacy evidence, not V02 suite. Old workflow38784183577 refuses stale76d8eac
with LIVE_PR_HEAD_CHANGED before tests; global38784183404 verify/pure PASS,
target PENDING-command prerequisite FAIL and later stages NOT_RUN remain separate.
Raw patch context spaces in initial R03 artifact were fixed by byte-exact ZIP
packaging8f6a68e without scope/policy changes; current scoped source is unchanged.

[Current packet](../../acceptance/MS7-MIG-R03/v02-successor-review-8256cbf/review-packet.md)
and service/consumer handoff are prepared. Latest live HEAD8256cbf/open/draft;
only human review5525315946 at76d8eac, no approval transfer. Renewed current-HEAD
Task Approval/applicable consumer review pending; no draft promotion/merge/closure.
Full I02/V04 and combined R03 target remain their own gates; R03 INCOMPLETE.

### Renewed V02 human approval receipt — 2026-10-15

User confirms current8256cbf Task Approval5538854677 and Ilya's consumer source
review at producer8256cbf / consumer47baaa9f79da00c9d96fd880117a0dd064dcfa46.
GitHub review GET independently confirms Tramsey00 APPROVED, submitted
2026-10-15T19:35:07Z, commit8256cbf; its body corroborates the exact consumer pair
and excludes full I02/no-JS/SSG/runtime/browser acceptance. No separate Ilya
GitHub review URL is claimed. Old5525315946 remains historical at76d8eac.

[New receipt and raw API payloads](../../acceptance/MS7-MIG-R03/v02-approval-8256cbf/README.md)
record TASK_APPROVED_AWAITING_VERIFIED_MERGE. Live PR53 open/draft/unmerged with
unchanged8256cbf HEAD and0c03197 base. Vladimir alone has explicit user squash
merge authorization; agent does not merge/promote/close Issues. No additional
suites dispatched; current technical packet/raw archives remain byte-exact.
After actual owner merge, verify receipt/squash commit/integration ancestry and
require tree74c3014516ec3a2110d2cfec13c8e7afb8ae5024 before recording
ACCEPTED_INTEGRATION or changing input0c03197. Immutable MIG_BASE60b341f and
historical8d958 retained. V04 CLI/full I02 and combined R03 command/pipeline and
independent approvals remain their own outstanding gates. R03 INCOMPLETE.

### V02 verified squash and accepted input — 2026-10-15

GitHub PR53 receipt verifies actual owner mergea359b0b at2026-10-15T19:42:03Z,
sole parent0c03197/tree74c30145 exactly equal to approved8256cbf. Human approval
5538854677 and live integration ref independently confirmed; V02 now
ACCEPTED_INTEGRATION. [Receipt, raw metadata and next steps](../../acceptance/MS7-MIG-R03/v02-integration-a359b0b/README.md).
New current inputa359b0b; old0c03197/8d958, MIG_BASE60b341f and candidate/control/
run receipts preserved. Post-merge baseline38796031561 SUCCESS is baseline-only;
old38784183591 remains actual8256cbf execution. Consumer compatibility source
review8256cbf/47baaa9 does not accept full I02. Issue35 remains OPEN.

Synced accepted input into R03 brancha4954ed without changing owner files.
Updated exact frontend/V01 checkouts and current receipt guard to pin new input,
distinguish approver/merger and verify squash parent/tree equivalence. Old
publication/successor scopes stay tree-bound to their historical candidate.
Supplemental local guard/adapters12/8/11 and pure6 groups PASS on actualPython3.10.11;
not target-version acceptance. Real clean new checkout guard PASS1876 files.
Root command map remains PENDING/empty; next review of available V02/V01 adapters,
accepted I02/full browser pipeline, applicable V04 content CLI, reviewed10/4
composition, combined target and independent R03 approvals remain. R03 INCOMPLETE;
no agent PR merge, new approval, draft promotion or Issue closure.

Adapted accepted-input CI final evidence at R03 codeb541bf0: frontend38801486277
SUCCESS112+5/10 commands (actual workflow synthetic2935a86, PR headb541bf0);
V0138801476734 SUCCESS34/all23 PG/0 skips, fresh2/ABC/57 DB cleanup/22 lock,
Python3.12.15/PG16.15, actual workflowb541bf0. Both suite checkouts exacta359b0b.
Original ZIP digests/member streams and complete results independently reconciled.
Initial all-backend snapshot refusal38800500641 and unchanged historical-v5
refusal38800895139 are0-case NOT_RUN records retained with raw output/cleanup;
R03 accepted-input adapter preserves strict source/environment/inventory guards
without editing V01/V02/helper.15 observer guards PASS. Global38801476735
verify/pure PASS; target prerequisite PENDING FAIL and later NOT_RUN retained.
This does not rerun V02 on squash or accept full I02/R03.

### Remaining dependency chain for next planning — 2026-10-16

[Existing checklist](../../acceptance/MS7-MIG-R03/cli-receipt-handoff-checklist.md)
now maps14 generic checks to exact missing deliverables/owners and10 handoffs,
with canonical line links. R03 formal dependencies unchanged; full I02 pending,
V02 accepted. Checked artifact-level V04 CLI/source-renderer/bootstrap/publisher
and I03 LessonHost/lifecycle are needed where assertions use them; full V04/I03
Task Approval is not invented as a new R03 gate. Missing functional coverage
still blocks its checks. Full I03 remains V04 INTEGRATION; R04/V05 require
full V04/I03 and I05 requires full I03/I04 plus V05. Current identity runtime
belongs V03; full account UI/browser acceptance remains I04/I05. Personal
V03-before-V04 and I03-before-I04 queue order distinguished from task HARD.
All40 R02 parity rows and all18 canonical dependency nodes cross-referenced.
Source snapshot/structural validation retained; no task code/commands activated,
CI suite rerun, owner messages, approvals, merge or Issue closure. Current input
a359b0b unchanged. Readiness dates for scoped artifacts, full approvals, owner
capacity and CI/rework are inputs to the next three-queue critical-path review;
no replacement dates or queue reorder approved here. R03 remains INCOMPLETE.

### I02 concrete build-input blocker — 2026-10-16

Direct user clarification: verified release build-input handoff from V04 is the
current concrete I02 build blocker. Added H-BUILD-INPUTS, owner Vladimir/V04,
consumer Ilya/I02. Accepted R02 defines immutable index/pages/assets build
artifact and direct validated DTO consumption. A fully activated release/active
descriptor is not a prerequisite for SSG HTML generation. Separate input byte/
schema/completeness/trust review, I02 HTML build/output QA and later real
activation/publication/failure-recovery evidence. Missing active pointer must
not block valid immutable-input build; build PASS does not imply publication PASS.
Existing14 checks/40 parity obligations and full I02/R03 approvals unchanged;
runtime map stays PENDING. No new delivery PASS, owner message, runtime execution,
Task Approval, merge, Issue closure or deadline change. R03 INCOMPLETE.
