# EXEC PLAN MS7-MIG-R03: Target verification and Harness adapters

- Status: ACTIVE / INCOMPLETE; integration and independent approval pending
- Owner: Руслан / Tramsey00; reviewers: Владимир and Илья in their assigned zones
- Date: 2026-10-09 Europe/Moscow; deadline: 2026-10-10 including review/integration
- Issue: https://github.com/Tramsey00/MathStart-Python/issues/30
- Branch: ms7-mig-r03-verification -> ms7-mig-react-fastapi; Refs #30
- Current accepted input: `0c03197e23f69a233c0fcf8bdffa336feca20b92`
- Historical input: `8d958aeeb17da46839722441425ccbb5889e2ab7` (preserved provenance)
- Immutable MIG_BASE_SHA: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`
- HARD R02 and its parity CONTRACT accepted through owner receipt:
  https://github.com/Tramsey00/MathStart-Python/pull/48#issuecomment-6070829593
- INTEGRATION V02 (#35) and I02 (#41): absent from input; acceptance pending
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
