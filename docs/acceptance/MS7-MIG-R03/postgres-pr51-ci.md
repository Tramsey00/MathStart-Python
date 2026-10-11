# R03 PostgreSQL target CI for PR51

Date: 2026-10-11 Europe/Moscow. Issue #30; V01 consumer PR #51.
This R03 increment supplies candidate CI evidence for Independent Task Approval.
It does not grant that approval or accept integration.

## Exact input

Live PR51 candidate pinned before execution:
`393d98890649c6c7c47908424ba0d076b5b5e56e`, base accepted integration
`8d958aeeb17da46839722441425ccbb5889e2ab7`. Reviewed implementation
`1f97d762c4089efb2e4ef6d8c7ebe0bdcbe161f4`; backend diff to candidate is empty.
Immutable MIG_BASE_SHA `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7` remains unchanged.
The handoff is PR51's `docs/acceptance/MS7-MIG-V01/r03-ci-handoff-v5.md`.
Lock, handoff, runner and 34-case inventory hashes are explicitly pinned in
`specs/migration/r03-v1/postgres-ci-pr51.json`.

## Separate CI contract

`.github/workflows/postgres-ci.yml` runs on R03 pushes and applicable integration
PR events, with separate R03 workflow and exact PR51 candidate checkouts. It is
external candidate evidence linked to PR51, not a PR51-event status check.
Intake re-reads the live PR head/base and rejects a stale pin. It records live PR
head, observed merge ref, actual candidate checkout/tree, actual R03 workflow
checkout and event/run metadata separately. The observed merge ref is not tested.

An owned GitHub job service `postgres:16-bookworm`, port55441, synthetic
`mathstart_v01_ci` credentials and admin database `postgres` is used. Exact service
ID comes only from `job.services.postgres.id`; image/port/health are verified.
Data uses an explicitly verified tmpfs mount, with no Docker volume.
No shared/local working database, container or persisted volume is used.
Actual server major must equal16 and the initial/final non-template database
inventory must be empty. The service is stopped even after command failure;
GitHub's post-job service cleanup removes the container; tmpfs needs no volume removal.
Raw container diagnostics and service identity/stop results are retained.

Python3.12 creates a new `candidate/var/v01-target-ci` venv. Only the complete
`backend/requirements-test.lock` is installed with `pip install --no-deps`; pip
check, freeze and installed metadata verify all22 exact packages. Django in this
test lock generates historical fixtures and F1 parity evidence; target runtime
ownership is unchanged. Root locks and legacy environments are untouched.

R03 executes the unchanged owner v5 runner, which directly loads the explicit
unit/PostgreSQL/remediation modules and requires34 unique cases,23 PostgreSQL
cases, no skips/expected failures/unexpected successes. The R03 observer delegates
all unittest callbacks and database contexts while recording per-case results,
successful/failed subtests and actual fixture database/profile/cleanup events.
It neither edits test assertions nor changes migration behavior. R03 independently
requires the exact case inventory, all PASS, two distinct fresh databases and
upgrade profiles A/B/C, complete marked-database cleanup, and the owner's exact
PASS summary. F1/F2 diagnostic JSON uses a new ignored output directory.

Negative schema/head/stamp/review/rollback/constraints/locking/sequence tests are
the unchanged owner cases; raw test IDs and subtests identify their execution.
No `continue-on-error`, shell failure suppression or skipped PostgreSQL success.
API credentials are available only to intake, not test execution. Every source,
backend lock and historical V01 evidence hash is compared before/after, and both
candidate baseline workflows remain byte-identical to accepted input. R03 frozen
`ci.yml`, its existing `migration-ci.yml` and frontend job remain unchanged.

## Result and human gate

Execution is pending at initial publication. Record raw artifact contents and
run URL below after execution; configuration and observer unit tests do not prove
PostgreSQL acceptance. Owner implementation/tests/locks and historical acceptance
records are not edited. No V02/V03/V04 implementation or helper P3 follow-up.
I01 manual hover and Ruslan UX/integration review remain independent pending gates.
Final V01 Independent Task Approval must be explicitly issued by its designated
human reviewer on the exact candidate. No merge, Issue closure or R03 completion
is authorized; the wider R03 dependencies remain open.

Initial workflow run38155735994 failed before job execution due to R03 context
placement; corrected. First executing run38155839568 succeeded (34/23, fresh2,
ABC,57 databases cleaned). Its18 raw artifact files are retained separately with
ZIP/member digests. It is qualified as superseded storage proof: the PG image
default anonymous volume was stopped, but GitHub's actual post-job removal used
docker rm --force without --volumes. The final workflow instead uses verified
tmpfs with no volume; final run evidence follows after that execution.
