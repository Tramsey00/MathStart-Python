# MS7-MIG-R03 review and integration handoff

Status: **INCOMPLETE / draft increment**, not ACCEPTED_INTEGRATION.
Owner Tramsey00; independent reviewers/Task Approvers VladimirFrolov777 and13baybars.
[Issue30](https://github.com/Tramsey00/MathStart-Python/issues/30) remains open.
Input8d958aeeb17da46839722441425ccbb5889e2ab7; unchanged
MIG_BASE_SHA60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7.
R01/R02 accepted integration facts and external owner receipt remain authoritative;
historical PENDING snapshots are retained.

## Reviewable result

- scripts/verify_repo.py has legacy/target/pure profiles, group semantics and
  bounded fail-closed execution.16 target checks; pure6 is explicitly partial.
- Harness fixed registry retains3 IDs with target repo-baseline and no recursion;
  failure/timeout/NOT_RUN cannot reach READY. Frozen lifecycle/contracts preserved.
- Target check wrappers require concrete reviewed owner Python entrypoints, an
  unskipped nonempty runtime receipt and real PG16 evidence where required.
- Standalone psycopg PG diagnostic and version/fresh/upgrade CLI adapters; no
  Django/SQLite fallback in target commands. Missing runtime owner inputs fail.
- Migration CI triggers task/integration/main; pure environment excludes Django/
  DRF, unchanged R02 suite63 runs historically, target job is mandatory and fails
  today at owner prerequisites. Exact checkout/head/base/merge-ref/tree evidence
  is uploaded. Frozen ci.yml whole-file pin remains valid.
- §17 index has six original_result -> R03 -> target_evidence chains; contracts,
  schemas, tests, historical traces/approvals and authored sources remain preserved.

Commands and receipt interface: [r03-v1](../../../specs/migration/r03-v1/README.md).
Observable evidence: [verification](verification.json), [intake](intake.json),
[trace](../../agent-traces/MS7-MIG-R03.md), [plan](../../exec-plans/active/MS7-MIG-R03.md).

## Blocking integration inputs

1. V02 Issue35 and I02 Issue41 have no accepted results at input; live Issues
   remain PLANNED and remote branches absent at intake. Acquire reviewed exact
   SHA intake, never silently update8d958ae or start those tasks in R03.
2. V01/I01 locks, concrete backend command handoff (including V04 content CLI),
   metadata/rehearsals and React package scripts are absent. Resolve these with
   owner deliverables; [runtime-commands](../../../specs/migration/r03-v1/runtime-commands.json)
   stays PENDING, no fabricated endpoints/implementation.
3. Real target PG fresh/upgrades A/B/C, all263 source/quality/integrity, API/staff
   suites, frontend typecheck/test/build/browser and runtime R02 equivalent
   assertions must pass. Historical63/model32 are not substitutes.
4. Transitional default legacy must be cut over to target after reviewed inputs;
   no full final no-Django verification claim before this is done.
5. Current-head applicable CI and tested PR merge-ref must pass after integration;
   independent Vladimir/Ilya approvals at that exact HEAD and owner intake remain
   separate. Current target job failure is reported, never suppressed for green CI.

No merge/deploy/Issue closure occurred. No messages were sent to other owners.
No V/I/R04 task, DDL or working database operation was performed. Keep the plan
active and PR draft; reviewers can assess infrastructure now, acceptance awaits
the above conditions. Preserve previous working DB and R01/R02 runtime roots.
