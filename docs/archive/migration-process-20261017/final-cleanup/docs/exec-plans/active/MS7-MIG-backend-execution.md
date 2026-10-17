# MS7-MIG backend execution V03–V06

- Status: Active; first V04 H-BUILD-INPUTS increment under verification.
- Input: `24d06112bcd6abcd1abad9b052de14a0a7b49e8e` on `ms7-mig-backend-execution`.
- Authority: MIGRATION_AGENT/TASKS/VERIFICATION and explicit coordinator assignment.
- Human acceptance: pending; intermediate technical review uses the new execution process.

## Scope and boundaries

Implement current identity/staff/receipt behavior, source rendering/build inputs,
publication/recovery and operational rehearsal. Backend owns backend/**, Alembic
and backend locks. Root scripts/CI/shared documents, frontend and integration
references remain coordinator/consumer owned. No new learning domains or LLM.
Accepted V01/V02 and frozen contracts/evidence remain preserved.

## Ordered increments

1. V04 source validator and deterministic component renderer; fresh PostgreSQL
   bootstrap twice; immutable public manifest/page/assets handoff to I02.
2. V03 compatible passwords, PG opaque sessions, CSRF/host/origin/rates,
   owner-bound receipts/bridge and complete staff write inventory with PG races.
3. V04 full CLI inventory, durable gate/journal/DB edition/activation/recovery
   and combined public HTML verification with I02/I03.
4. V05 reproducible serving/health/storage/proxy/backup/restore/performance.
5. V06 final disposable rehearsal after V05 and independent R04 audit.

## Verification

Use skills/verification/SKILL.md. Run narrow source/golden/build-negative tests,
preserved V01/V02 suites, real PostgreSQL concurrency and failure/recovery
checks. Provide actual executable R03 interfaces with nonempty target receipts.
Normal target environment contains no Django; the legacy oracle is separately
installed and labeled. Coordinator runs final root and combined checks.

## Database and artifact safety

Initial increment has no DDL changes. PostgreSQL16.15 is a task-labeled disposable
container on127.0.0.1:55432. Existing V01 guard requires reserved
`test_ms7_mig_v01_ms7exec_backend_*` names and its exact reservation comment;
these are used instead of changing the accepted migration guard. Runtime
artifacts live under this checkout's ignored var/. Bootstrap fails on runtime
edits and never rewrites Users/receipts/history. Build-inputs performs a read-only
DB transaction and writes a new immutable artifact directory only.

## Remaining gates

V03/V04/V05/V06 are incomplete. First build increment does not establish
publication activation, browser parity, all CLI checks or production readiness.
Reviewer receives exact committed diff/test results. Final human gate remains
with the user; no main merge, public deployment or production writes authorized.
