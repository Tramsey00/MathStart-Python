# Unified migration execution

Status: IN_PROGRESS. Final human acceptance: HUMAN_PENDING.

## Current authorized task

Single primary executor, I02 only; no standing implementation team. One reviewer
only after candidate readiness, using exact base/head/diff, contracts, measured
results and findings. Full cross-browser/visual matrix remains I05. Preserve all
existing code; no automatic I03/V03/V04/R03 or other task work. Necessary verifier
and dependency corrections are in scope. Two failed cycles of one cause require
a checkpoint/blocker. Do not repeat unchanged R03 target or full checks after
only documentation changes. Commit, push, verify remote SHA, handoff, stop.

Continue existing integration; no bootstrap or implementation restart. First
exercise correct POSIX legacy virtualenv invocation, then scoped I02 checks and
affected boundaries. Historical program sequence remains in Git history.

## Ownership and isolation

All paths below are under C:/Projects/MathStart-Python/migration-execution/.
The original dirty main and prior tmp worktrees are untouched.

| Role | Checkout | Writable ownership | Ports / disposable DB prefix |
| --- | --- | --- | --- |
| Coordinator | integration | root scripts, CI, Harness, shared records | 8111–8119 / ms7exec_coord_ |
| Backend | backend | backend, Alembic, backend locks, backend evidence | 8121–8129 / ms7exec_backend_ |
| Frontend | frontend | frontend, frontend lock, browser evidence | 8131–8139 / ms7exec_frontend_ |
| Reviewer | review | review evidence only; application code read-only | 8141–8149 / ms7exec_review_ |

The worktree ownership table records historical isolation, not an active team.
The sole executor now works in integration with its own var/ runtime/reports.
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
