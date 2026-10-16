# Unified migration execution

Status: IN_PROGRESS. Final human acceptance: HUMAN_PENDING.

## Current authorized block — supersedes the original continuous sequence

The user narrowed this execution on 2026-10-16 to complete I02 then I03, perform
only necessary V04 dependency corrections, verify and independently review the
combined result, publish commits/branches, and stop with MIGRATION_HANDOFF.md.
Do not continue V03, full V04, I04, R05 or the remaining program in this run.
Preserve and publish existing work in those areas as explicitly incomplete WIP
branches. Original acceptance and data/security boundaries remain unchanged.

Future work uses separately initiated blocks of three available tasks, selected
from actual dependency readiness. Each block ends in publication and handoff;
there is no automatic continuation into the next block.

The user explicitly activated MIGRATION_START.md on 2026-10-16 and confirmed
the unified execution process. MIGRATION_AGENT.md, MIGRATION_TASKS.md and
MIGRATION_VERIFICATION.md define scope, dependencies and acceptance. Preserve
R01/R02/V01/V02/I01; implement V04/I02 from zero; inspect R03 before intake.

## Execution sequence

1. Verify live refs and dirty worktrees; isolate execution and copy the ten
   allowlisted package files byte-for-byte with hash receipts.
2. Review R03 at immutable fb39647beb983a4f488ad82d4984d3f96e87b9a8;
   preserve its useful code and provenance without claiming task acceptance.
3. Backend delivers V04 build inputs and V03 identity; frontend implements I02,
   I03 and I04; coordinator continues R03 verification and prepares R05 sources.
4. Integrate independently reviewed candidates, complete V05/I05/R03, and R04
   combined audit. Fix blocking findings with regression evidence.
5. Complete full R05 documentation, V06 rehearsal, I06 freeze, release delta
   review and R06. Run final mandatory checks on the actual combined candidate.

## Ownership and isolation

All paths below are under C:/Projects/MathStart-Python/migration-execution/.
The original dirty main and prior tmp worktrees are untouched.

| Role | Checkout | Writable ownership | Ports / disposable DB prefix |
| --- | --- | --- | --- |
| Coordinator | integration | root scripts, CI, Harness, shared records | 8111–8119 / ms7exec_coord_ |
| Backend | backend | backend, Alembic, backend locks, backend evidence | 8121–8129 / ms7exec_backend_ |
| Frontend | frontend | frontend, frontend lock, browser evidence | 8131–8139 / ms7exec_frontend_ |
| Reviewer | review | review evidence only; application code read-only | 8141–8149 / ms7exec_review_ |

Each checkout uses its own var/ runtime/reports and isolated dependencies.
Only coordinator changes integration refs. No force push, main merge, issue
closure, production writes, deployment, or messages to colleagues/chats.

## Verification and final gate

Use the verification skill and full package matrix: 14 executable handoffs,
40 parity rows, AT-M01–12, real PostgreSQL fresh/upgrade/races/restore, complete
content and browser inventories, negative runner tests, separate review.
READY_FOR_HUMAN_ACCEPTANCE requires actual passing evidence and zero unresolved
blocking findings. Main merge/cutover/issue closure remain HUMAN_PENDING.

## Checkpoint

See MIGRATION_STATE.md and docs/agent-traces/migration-execution.md for actual
commits, command outcomes, limitations and the next available slice.
