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

Corrected workflow299eb3c runs38155839568 (PR49 event) and38155836305 (push)
both SUCCESS. First run records34 PASS,23 PostgreSQL with0 skips, actualfresh2,
upgradeABC,57 marked databases cleaned,40 successful subtests, Python3.12.15 and
PG16.15. Actual workflow mergecheckout e871b319, candidate393d988. Artifact
11707964088 ZIP SHA256bc7b50b3 matches Actions digest;18 exact files preserved
under postgres-pr51-ci/run-38155839568 with a derived manifest.

Lifecycle log inspection found GitHub's actual docker rm uses --force without
--volumes; the default PG image data mount is an anonymous volume. The runner
is disposable, but the previous description of explicit volume removal was
incorrect. Supersede this storage proof with a tmpfs mount and reject any Docker
volume at intake/cleanup; rerun target unchanged. Historical run/artifact retained
with this qualification. No V01 code or assertion changed. Added regression for
persistent/missing mounts. Final applicable target CI still pending here.

Before storage-fix commit, staged whitespace check identified CRLF in the new
derived manifest and original timestamped blank log lines. Derived manifest
written LF; raw logs retain exact artifact bytes (all18 hashes checked). Source/
document whitespace check excludes only raw .log members; no raw evidence trimmed.
Local final evidence regressions11 PASS.

Storage-changee85b1dc run38156256304 failed at intake; target was NOT_RUN.
Docker creates the intended tmpfs but exposes --tmpfs in HostConfig.Tmpfs,
not Mounts. Corrected the adapter to verify the actual field and reject all
volume/bind mounts. Same-shape negative regression updated. GitHub automatic
Stop containers succeeded. Raw decoded failure excerpts retained separately;
no PostgreSQL tests skipped-to-success or V01 edits. Local11 regressions PASS.
