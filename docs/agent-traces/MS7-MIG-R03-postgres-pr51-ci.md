# MS7-MIG-R03: PR51 separate target PostgreSQL CI

Date: 2026-10-11 Europe/Moscow. Scope: root CI wiring/evidence, Issue #30.
Status: IN_PROGRESS; Independent Task Approval NOT_DECLARED.

## Intake

Read repository instructions, product/architecture, accepted ADR0006 alongside
historical ADR0001, migration task cards, R03 active plan, verification skill,
PR51 v5 handoff/runner/case inventory, test locks and V01 test/fixture boundaries.
Fresh fetched refs confirm accepted input8d958ae and PR51 currenthead393d988.
Existing clean R03 worktree5b1c5c7 is reused; new detached candidate checkout
393d988 is clean, backend unchanged from reviewed1f97d762. Existing branches,
worktrees, original user-modified AGENTS and local recovery files are preserved.
PR50 run38150620957 is user-confirmed candidate evidence only; hover/UX pending.

## Change

Separate R03 PostgreSQL workflow, exact PR51 pin/hash config, bounded adapter,
observational test/fixture recorder and evidence regressions. Own PostgreSQL16
job service, exact context-owned container ID, port55441 and synthetic credentials.
Separate test-lock venv; unchanged v5 runner; all34/23 without skips, actualfresh2
andupgradeABC, marked DB cleanup and empty final inventory enforced. All historical
V01/backend hashes and frozen workflows compared. No owner implementation change,
historical overwrite, helper follow-up, automatic acceptance, merge or Issue close.

## Verification

Local and CI execution results pending at initial publication. Local interpreter
is bundled Python3.12.14; old repository venv's registered interpreter is missing.
Actual CI tooling versions and checkout SHAs must come from raw receipts. The
verification skill requires failures to remain visible; full R03 target pipeline
is still blocked by external V02/I02 owner inputs and cannot inherit V01 PASS.

Local stdlib evidence regressions:10 PASS on bundled Python3.12.14. Candidate
Git snapshot:clean393d988/tree4a9dde54;106 backend/historical files hashed;
both baseline workflows match accepted input. R03 preservation1370/1370 PASS;
git diff --check PASS. These are intake/parser checks, not PostgreSQL execution.

Initial R03 workflow publicationc00e1eb produced run38155735994 FAILURE before
job execution (workflow configuration). job.services was placed in job-level
env where the job context is unavailable. Moved exact service-ID expression
to intake/cleanup step env; no candidate change or test execution in this run.
Run: https://github.com/Tramsey00/MathStart-Python/actions/runs/38155735994
