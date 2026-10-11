# R03 frontend CI handoff for PR50

Date: 2026-10-11 Europe/Moscow. Refs #30; consumer PR #50 / I01.
This is a scoped R03/root CI increment, not I01 Task Approval or acceptance.

## Inputs and ownership

I01 candidate HEAD is `150279e6ca7f1c82a6f23d8899e50992cf358f55`, based on
accepted integration `8d958aeeb17da46839722441425ccbb5889e2ab7`.
R03 starts from its existing `379411422d7ec7096dd03c98730f3fb52d77ec6a`.
Immutable MIG_BASE_SHA remains `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
No change is made to I01's branch, implementation, lock, tests, historical
captures, or approval HEAD. No frontend feature or P3 follow-up is implemented.

Live review receipts on this candidate:

- [Vladimir API/security approval](https://github.com/Tramsey00/MathStart-Python/pull/50#pullrequestreview-5483318464).
- [Publication corrections closed by Ruslan](https://github.com/Tramsey00/MathStart-Python/pull/50#issuecomment-6110165810).
- [Separate owner clean local report](https://github.com/Tramsey00/MathStart-Python/pull/50#issuecomment-6109301800): historical local evidence, not this CI.

Manual hover and Ruslan UX/integration approval remain separate gates. I01 and
R03 remain unaccepted; no merge, Issue closure, deployment or working DB writes.

## Execution contract

Separate `.github/workflows/frontend-ci.yml` uses two clean checkouts: R03
workflow implementation and exact pinned PR50 candidate. It runs on R03 pushes
and applicable integration PRs. Explicit pins are in
`specs/migration/r03-v1/frontend-ci-pr50.json`; a changed live PR head or base
fails intake and requires an explicit reviewed pin update. No automatic latest
branch checkout or approval transfer. This run is linked to PR50 as external
candidate evidence; it is not represented as a PR50-event branch status check.

`scripts/frontend_ci.py` records live PR head/base and observed merge-ref
separately from actual candidate checkout SHA/tree, R03 workflow checkout,
event SHA/ref, run ID/attempt and URL. Existing `ci_provenance.py` verifies the
R03 event checkout; the candidate is independently verified against the pins.
The observed PR merge-ref is not claimed to have been tested.

Node24.21.0 / npm11.19.0 are required; Python3.12 runs the stdlib adapter. A clean
`npm ci --no-fund` precedes the unchanged I01 `verify:foundation` runner. Its
ten commands perform generation/17+24 pins, typecheck/contracts/route types,
native ESM/Unicode/fixture validators, frontend tests, historical dispatcher,
production build/graph/payload/export guards, dependency tree and audit at low
severity. The outer adapter requires complete successful raw receipts, at least
112 frontend and5 dispatcher PASS with no skips, clean before/after source,
84 unchanged historical captures and unchanged baseline workflow blobs.

Each command has a bounded deadline; missing tools/failure/timeout remain
nonzero. API token is available only to intake, never candidate scripts; both
checkouts disable persisted Git credentials. Artifact upload runs on failure.
New JSON/logs go only under ignored R03 `var/frontend-ci` and candidate
`frontend/.cache`; existing output is never refreshed. Neither historical
record-evidence script is executed. Both frozen baseline workflows remain
unchanged in I01; frozen `ci.yml` and R03's existing migration-ci remain untouched
by this increment.

## Current results

Configuration and adapter verification are recorded in the R03 trace. Actual
workflow/candidate SHA, run, raw evidence and final outcome will be attached to
PR49's R03 handoff after execution. The current candidate's existing baseline
[run38057300258](https://github.com/Tramsey00/MathStart-Python/actions/runs/38057300258)
is SUCCESS; it did not run frontend checks and is not relabelled.

This job proves the checked frontend foundation only. It does not establish
hover/visual parity, live target API, full session/receipt lifecycle, PostgreSQL
fresh/upgrade or I02–I06 delivery. Full R03 integration gates remain in the
active plan. Pin changes and new implementation commits require new applicable
checks; no independent approval is invented here.
