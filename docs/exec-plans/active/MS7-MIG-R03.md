# EXEC PLAN MS7-MIG-R03: Target verification and Harness adapters

- Status: ACTIVE / INCOMPLETE; integration and independent approval pending
- Owner: Руслан / Tramsey00; reviewers: Владимир and Илья in their assigned zones
- Date: 2026-10-09 Europe/Moscow; deadline: 2026-10-10 including review/integration
- Issue: https://github.com/Tramsey00/MathStart-Python/issues/30
- Branch: ms7-mig-r03-verification -> ms7-mig-react-fastapi; Refs #30
- Accepted input: `8d958aeeb17da46839722441425ccbb5889e2ab7`
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
