# MS7-MIG-R03 review and integration handoff

Status: **INCOMPLETE / draft increment**, not ACCEPTED_INTEGRATION.
Owner Tramsey00; independent reviewers/Task Approvers VladimirFrolov777 and13baybars.
[Issue30](https://github.com/Tramsey00/MathStart-Python/issues/30) remains open.
Current input0c03197e23f69a233c0fcf8bdffa336feca20b92; historical
input8d958aeeb17da46839722441425ccbb5889e2ab7 preserved; unchanged
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

## Current integration status and remaining gates — 2026-10-12

I01/V01 are ACCEPTED_INTEGRATION by human approvals and external merges.
Their locks, schema rehearsals and frontend foundation exist in current input.
I01 UX approval is received with the accepted banner limitation and two open
follow-ups. Full receipts and joint-suite evidence are in the
[current handoff](accepted-integration-ci-20261012.md).

1. V02 Issue35 and I02 Issue41 are absent from accepted input0c03197. Intake
   their reviewed exact SHAs when accepted; branch existence does not establish acceptance.
2. Concrete reviewed runtime-command handoff, including V04 content CLI, remains
   pending. Do not invent implementations or mark the registry REVIEWED by assumption.
3. Full API/services/staff/content/263-source and integrated browser evidence is
   still required. Schema rehearsals and fixture foundation have narrower coverage.
4. Final default cutover from legacy to target and full no-Django verification.
5. Successful applicable final-head/merge-ref CI and independent Vladimir/Ilya
   R03 Task Approvals. The existing broader target job fails on missing handoff.

No merge/deploy/Issue closure occurred. No messages were sent to other owners.
No V/I/R04 task, DDL or working database operation was performed. Keep the plan
active and PR draft; reviewers can assess infrastructure now, acceptance awaits
the above conditions. Preserve previous working DB and R01/R02 runtime roots.

## CLI/receipt handoff preparation — 2026-10-12

[Concrete owner/review checklist](cli-receipt-handoff-checklist.md) maps all10 backend checks,4 frontend
checks and7 baseline content commands to V02/I02/V04 deliverables and R02 parity
assertions. Accepted V01 schema/foundation evidence remains separate. The new
machine checklist is PREPARED_FOR_OWNER_REVIEW; runtime-commands remains PENDING
with no invented commands. No accepted V02/I02/V04 input is available at intake.
Full target execution awaits accepted exact-SHA inputs and reviewed command
contracts; R03 stays INCOMPLETE until full checks and independent approvals.
