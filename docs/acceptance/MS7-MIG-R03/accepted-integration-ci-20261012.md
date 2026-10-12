# R03 current accepted input and joint CI — 2026-10-12

R03 status: **INCOMPLETE**. I01 and V01: **ACCEPTED_INTEGRATION** by human
approvals and external squash merges, verified against GitHub receipts. Older
candidate reports and pending-approval snapshots are dated historical evidence.

| Task | Approved PR head | Human approval | External merge |
| --- | --- | --- | --- |
| I01 / PR50 | `150279e6ca7f1c82a6f23d8899e50992cf358f55` | [5484114333](https://github.com/Tramsey00/MathStart-Python/pull/50#pullrequestreview-5484114333) | `0c03197e23f69a233c0fcf8bdffa336feca20b92` |
| V01 / PR51 | `393d98890649c6c7c47908424ba0d076b5b5e56e` | [5484103844](https://github.com/Tramsey00/MathStart-Python/pull/51#pullrequestreview-5484103844) | `4a1b8b05709e7c5485194ca5551aee0824333660` |

Current input and actual test checkout for **both suites**:
`0c03197e23f69a233c0fcf8bdffa336feca20b92`, tree
`1ff96bde5c938b1d00159e9ee1349f5db1f44d9a`.
Immutable MIG_BASE_SHA: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
Historical accepted input: `8d958aeeb17da46839722441425ccbb5889e2ab7`.
Squash chain: historical input → V01 merge4a1b8b0 → I01 merge0c03197.
PR heads are source-approval references; actual suite checkout is the combined
integration SHA. Workflow implementation/event checkouts are recorded separately.

[Baseline38157082399](https://github.com/Tramsey00/MathStart-Python/actions/runs/38157082399)
is SUCCESS at actual checkout0c03197: fresh legacy PostgreSQL smoke and8/8 checks;
Django109, R03 contract18, Harness73, R02A30, R03A41. It runs no frontend suite.

Machine-readable current receipts:
[I01](../MS7-MIG-I01/acceptance-current-20261012.json),
[V01](../MS7-MIG-V01/acceptance-current-20261012.json).
I01 API/security approval5483318464 remains tied to approved head150279e6.
UX/integration approval is now received; there is no current pending UX gate for I01.

## Accepted limitations and follow-ups

I01 accepts variant A: the inherited `.ms-ui-fixture-mark` debug-gallery banner
can overlap content; this approval does not assert that the overlap was fixed.
Both separate follow-ups remain open:

1. Илья keeps fixture-only marking permanently visible and removes overlap with
   headings, labels and fields at360/768/1440; verify before completing I05.
2. The agreed P3 runtime query validator rejects null, arrays and scalars as
   INVALID_REQUEST before fetch, with separate negative regression tests.

V01's nonblocking P3 helper evidence-output follow-up remains open. Its approval
does not authorize production migration. Issues34 and40 remain OPEN until final
integration into main. R03 performs no merge or Issue closure.

## Joint CI contract and current execution

Two separate jobs use pinned input0c03197 and unchanged owner implementations.
Frontend: locked install, exact Node24.21/npm11.19, generation/pins, typecheck,
validators,112 frontend tests,5 historical dispatcher tests, production
build/security guards and audit. V01: separate22-package test-lock environment,
owned disposable PostgreSQL16 with tmpfs, unchanged v5 gate34 tests including
all23 PostgreSQL cases without skips, fresh×2, upgradesA/B/C and negatives.

The shared adapter verifies both specific human reviews, closed/merged PR flags,
approved heads, merge receipts/parents, live integration ref and actual checkout
tree. All1662 accepted files outside10 reviewed R03 adapter paths remain exact;
84 I01 historical captures and106 backend/V01 historical files stay unchanged.
R03 adds new dated receipt records without altering existing owner evidence.
Both frozen candidate workflows match historical input. Root workflow checkout
explicitly uses the event SHA; `ci_provenance.py` still rejects event mismatch or
wrong PR merge parents. Candidate code receives no GitHub token.

New joint CI execution: **AWAITING_RUN**, to be replaced with actual run receipts
and immutable raw artifacts after publication. Local adapter checks are evidence
of the adapter only, not execution of Node or PostgreSQL owner suites.

## Historical evidence kept separately

- Frontend [38150620957](https://github.com/Tramsey00/MathStart-Python/actions/runs/38150620957)
  and [38155839562](https://github.com/Tramsey00/MathStart-Python/actions/runs/38155839562):
  SUCCESS for candidate150279e6,112+5 PASS; not joint-input runs.
- PostgreSQL [38155839568](https://github.com/Tramsey00/MathStart-Python/actions/runs/38155839568)
  and final tmpfs [38156436658](https://github.com/Tramsey00/MathStart-Python/actions/runs/38156436658):
  SUCCESS for candidate393d988,34/23 PASS; existing raw evidence retained.
- [38156256304](https://github.com/Tramsey00/MathStart-Python/actions/runs/38156256304):
  FAILURE / suite NOT_RUN at storage intake, preserved in the existing failure record.
- [38156928889](https://github.com/Tramsey00/MathStart-Python/actions/runs/38156928889):
  FAILURE / suite NOT_RUN on event-versus-checkout mismatch after integration advanced.
- Late old-adapter [frontend38157320317](https://github.com/Tramsey00/MathStart-Python/actions/runs/38157320317)
  and [PostgreSQL38157320311](https://github.com/Tramsey00/MathStart-Python/actions/runs/38157320311):
  FAILURE, not replacements for earlier successful candidate evidence; exact step
  diagnostics are retained separately in the joint intake record.

## Remaining R03 dependencies and next step

HARD R02 and parity CONTRACT remain accepted. Task-card INTEGRATION dependencies
V02 (#35) and I02 (#41) are still absent from accepted input0c03197. Accepted
V01/I01 remove schema/foundation intake blockers, but the broader target gate
still requires reviewed concrete runtime-command handoff (including V04 content
CLI), API/services/staff/content checks,263-source parity and actual integrated
browser smoke. Schema-only fresh×2/ABC and fixture foundation do not establish
the full bootstrap/assets/API/content/browser gate.

Next available R03 step: review and map delivered owner CLI/receipt contracts
to the existing registry, then intake V02/I02 at explicitly approved SHAs and
execute the full target pipeline. Until those deliverables exist, prepare the
command review checklist and the §17 evidence links in R03; do not implement
V02/I02/V04. Runtime command status stays PENDING, failures remain nonzero.
Final default cutover from legacy to target, successful final head/merge-ref CI,
and independent Владимир/Илья R03 Task Approval remain required.
