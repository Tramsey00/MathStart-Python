# R03: human confirmation and real published-commit CI preparation

Human instruction confirms gate run38596739924 and PR49 review head
`551128497366121acdf6816d4bf8de1aceb75286`, concrete anchor
`5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7` and control
revision `1b75c6e58ecdcb4bb172d4df979e9b9efa7dde68`.
Publication by Vladimir is authorized only for single parent
`0c03197e23f69a233c0fcf8bdffa336feca20b92` and exact tree
`dbad1e853dff354c5d3255755afb5cc32e0ad279`. Task Approval, merge and Issue closure
remain unauthorized; R03 INCOMPLETE. Starting checkout is the reviewed5511284.

## Observable changes and checks

- Separate owner-confirmation JSON records the decision, without modifying the
  approved anchor, controls, original snapshot or prior raw evidence. Digest
  `0a872e5f2c15fd6e6e031c87c97e6ca41323db4bdfa84da60383978319e3a8f4`.
- Live repo PR collection and refs checked twice; only migration PR49 is open.
  No MS7-MIG-V02 PR/branch/implementation SHA. Legacy V02 branches are unrelated.
- New R03 published-commit workflow/controller requires a real committed exact
  PR/SHA input; its file is deliberately absent until that input arrives. It
  checks controller/decision hashes and immutable approved owner scripts before
  load/execute, validates live owner/task PR HEAD and metadata, fetches exact SHA
  into a new Git directory, invokes published (never suite), rechecks live HEAD
  and retains separate provenance/raw/evidence-manifest fields.
-12 meaningful orchestration guard regressions PASS: confirmed-decision byte
  tamper, invalid/surrogate SHA, candidate trust override, duplicate/unknown JSON,
  wrong PR/repository/owner/base/HEAD, multiple parents/tree mismatch, replaced
  approved executable before import, bytecode-cache substitution and absent input
  before owner/network access. Approved intake loads from the actual bytes just
  hashed; no cached bytecode or reopened source can supply that imported module.
- Initial executable-replacement unit fixture accidentally lived inside the
  orchestrator tree and hit the earlier ownership guard. Moved only the temporary
  fixture to a verified sibling directory; intended digest rejection then PASS.
  That initial failure and final test output are retained separately.
- `verify_repo.py --profile pure` PASS6 groups; existing historical/frozen
  preservation PASS1370 files and strict manifest pins. Current scope touches
  only R03 scripts/workflow/tests/records. No V02-owned or frozen baseline changes.

## Execution state and next dependency

Published gate: **NOT_RUN / AWAITING_PUBLISHED_CANDIDATE**. No workflow run or
artifact digest is invented for an unpublished implementation. Confirmed staged
run38596739924 remains its own evidence. Need the publication PR URL and full
implementation SHA; then pin exact input, execute the dedicated Linux job,
download/reconcile raw artifacts and prepare current-HEAD V02 final review.
Remaining V02 task-specific/runtime/consumer checks are listed in the
[published handoff](../acceptance/MS7-MIG-R03/v02-publication-20261014/published-handoff.md).
No new target runtime implementation or cross-owner work is performed.
