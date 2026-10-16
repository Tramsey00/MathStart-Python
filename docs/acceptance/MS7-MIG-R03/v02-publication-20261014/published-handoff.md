# Confirmed gate and authorized V02 publication: R03 handoff

Current 2026-10-15: **PUBLISHED_COMMIT_GATE_PASS / TECHNICAL_CHECKS_PASS /
INDEPENDENT_TASK_APPROVAL_PENDING**. PR53 HEAD76d8eac was checked on fresh Linux
with confirmed controls1b75c6e in published run38637910883; actual task checks and
complete raw artifact reconciliation PASS in run38642117604.
[Current technical review packet](../v02-review-20261015/review-packet.md) and
[concrete service/CLI/consumer handoff](../v02-review-20261015/service-cli-consumer-handoff.md)
record the received implementation and current receipts. The dated intake below
is preserved as history. No V02 Task Approval, draft promotion, merge or closure.

Historical 2026-10-14 intake: **GATE_AND_ANCHOR_CONFIRMED / AWAITING_PUBLISHED_CANDIDATE**.
R03 remains **INCOMPLETE**. [Human decision](owner-confirmation.json) records the
user's confirmation of run38596739924, review-packet PR49 HEAD5511284, concrete
anchor and trusted controls. Its SHA256 is
`0a872e5f2c15fd6e6e031c87c97e6ca41323db4bdfa84da60383978319e3a8f4`.
The earlier staged/tree results, readiness packet, raw evidence and anchor bytes
are preserved; the human confirmation is a separate artifact.

## Authorized scope and current execution state

Vladimir may publish the unchanged candidate with exactly one parent
`0c03197e23f69a233c0fcf8bdffa336feca20b92` and tree
`dbad1e853dff354c5d3255755afb5cc32e0ad279`.
Trusted control revision stays `1b75c6e58ecdcb4bb172d4df979e9b9efa7dde68`;
concrete anchor SHA256 stays
`5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7`.
MIG_BASE remains `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.

Live PR/ref discovery at intake found no migration V02 PR or branch. Legacy
MS7-V02 PR19/24 and branch codex/ms7-v02-grades-api are not this candidate.
Implementation PR/SHA and published gate run/artifact are therefore **null**;
the exact published-commit verification is **NOT_RUN**. Staged/tree run38596739924
is confirmed source evidence and is not substituted for that missing execution.

## Exact published-commit execution

The new R03 workflow
[published-v02-ci.yml](../../../../.github/workflows/published-v02-ci.yml) uses
separate orchestration and fixed owner checkouts. It runs only on a newly pinned
published-candidate input or explicit dispatch. This handoff does not create a
placeholder input or trigger the original staged/tree suite.

After receipt of the PR URL and full implementation SHA:

1. Check current open V02 PR owner/repository/base/head and Git commit metadata.
   Reject a stale HEAD, additional/different parent or different tree. Do not
   fabricate a commit or relabel BASE/tree as implementation.
2. Record that exact PR/SHA in R03-owned
   `specs/migration/r03-v1/v02-published-candidate.json`, in a Git revision used by
   the workflow. It has exactly these fields; the uppercase values below are
   documentation placeholders, not an executable candidate configuration:

```json
{
  "format": "r03-v02-published-candidate-v1",
  "task_id": "MS7-MIG-V02",
  "status": "PINNED_PUBLISHED_CANDIDATE",
  "pr_url": "EXACT_V02_PR_URL",
  "implementation_sha": "FULL_PUBLISHED_IMPLEMENTATION_SHA",
  "control_revision": "1b75c6e58ecdcb4bb172d4df979e9b9efa7dde68",
  "anchor_sha256": "5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7",
  "owner_confirmation_sha256": "0a872e5f2c15fd6e6e031c87c97e6ca41323db4bdfa84da60383978319e3a8f4"
}
```

3. The launcher checks the human-record/controller digests, Git ownership of the
   input revision and both approved owner scripts before import/execution. It
   reads live PR HEAD and commit parent/tree, then fetches only that exact SHA
   into a new disposable Git repository. No candidate code, hook, filter,
   installer or database is used during this publication gate.
4. On the fresh Linux checkout it runs the **confirmed** bootstrap from fixed
   owner revision, with no edits to the approved controls:

```text
python -I -B OWNER/scripts/v02_publication_gate.py published --owner-revision 1b75c6e58ecdcb4bb172d4df979e9b9efa7dde68 --root CLEAN_CHECKOUT --ref EXACT_IMPLEMENTATION_SHA --output NEW_EVIDENCE_DIRECTORY
```

The bootstrap executes the mandatory external v3 command with the confirmed
anchor/digest, preserves full FAIL/2 streams and requires both scoped PASS/0.
It checks a real commit, exact HEAD/index/tree and single BASE parent. The
launcher then rechecks live PR HEAD; a later change fails the current evidence
envelope instead of transferring approval. Only `published` is used here.

5. Retain workflow/event/orchestrator SHA, fixed control revision, implementation
   SHA, actual checkout SHA/tree/parents, before/after PR raw JSON, source input
   digest, argv/stdout/stderr/exits/versions, artifact digest and raw streams.
   Download/verify the artifact and publish an exact-head V02 review packet.

The unchanged older bootstrap/verifier labels (including historical pending
publication and their generic authorization=false fields) remain source evidence.
Current human authorization is this separate confirmation; current execution
and live-head provenance are recorded in `published-result.json` by R03.
No original V02 evidence or trusted script is rewritten to alter those labels.

## Task-specific checks still required for V02 review

The publication gate proves approved source bytes/metadata at a real commit.
It does not grant the following runtime/human gates:

- Current-candidate V02 unit/contract/HTTP/PG evidence on locked owner environments,
  with explicit case inventory and0 skips. Source remediation records report86
  V02 tests; re-confirm the inventory/count on the actual implementation SHA.
- F01 shared asset identity/page-local order and F02 pinned-release404 comparator
  regressions; ContentDelivery DTO/manifest/export/digest negatives and safe errors.
- Grade IDs/keyset/legacy-signing parity, query bounds and read-only transactions;
  catalogue Unicode/query/filter/order parity; public route/method/redirect/media/
  sitemap/robots/resource/error precedence and trusted origin checks.
- Seven Content model and User/Group staff reads/history/selectors; DB-derived
  flags/permissions, auth-before-lookup, revision-bound cursors and exact DTOs.
  Session/CSRF writers remain V03 scope; this task does not implement them.
- Unchanged V01 regression34/all23 PG cases, fresh PG smoke, applicable historical
  R0263/R02A30/R03A41 and §17 source/runtime mappings. Retain earlier successful
  evidence separately from exact-candidate results and failures.
- Full Content parity279/263, scoped source/frozen ownership and a separate
  runtime-without-Django check with the exact owner runtime/test locks. Legacy
  comparators may use their isolated Django environment; the target runtime may not.
- Concrete V02 CLI/service/receipt handoff for R03 and I02 consumer review where
  applicable. Synthetic renderer evidence does not establish I02 browser/SSG
  parity; V04 activation/content CLI and I02 delivery remain their own tasks.
- Ruslan's final Independent V02 Task Approval at the reviewed current HEAD,
  after named blocking findings are closed and applicable CI is current.

No new V02 implementation, Task Approval, merge or Issue closure is performed by
this handoff. Issues34/40 stay open. Wider R03 still needs accepted V02/I02 inputs,
reviewed10-backend/4-frontend commands including V04 content CLI, full combined
target/PG/browser pipeline and independent Vladimir/Ilya R03 approvals.
