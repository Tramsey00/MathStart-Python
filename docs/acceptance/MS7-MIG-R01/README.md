# MS7-MIG-R01 records

This package records the accepted Django snapshot and R01-only post-merge handoff.
**MIG_BASE_SHA = 60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7; R01 ACCEPTED_SNAPSHOT / POST_MERGE_RECORDS_REVIEW_PENDING.**
Canonical application input remains `8c11edadc8debc81432d1db1145feac504f09061`.
[Actual merged PR46](https://github.com/Tramsey00/MathStart-Python/pull/46),
[post-merge provenance](post-merge-provenance-20261008.json),
[current acceptance](acceptance.md) and [R02 input handoff](R02-input-handoff.md)
distinguish original reviews, owner-reported e510744 confirmation, actual resulting
commit, CI and current amendment review. Integration starts exactly at resulting SHA.
[Record manifest](record-manifest.json) hashes exact Git blobs, excluding itself.

- [Source manifest](source-manifest.json): exact tracked input Git bytes,
  sizes/SHA256/counts and original/candidate checkout byte differences.
- [Local delta](local-delta.json): no source/code delta; unchanged recovery trace
  intake; preserved output/tmp; runtime excluded.
- [Sanitized working DB manifest](runtime-data-manifest.json): verified read-only
  transaction/rollback, schema and aggregates without PII or secret values.
- [Rendered/runtime digests](rendered-runtime-digests.json): separate renderer
  and DB snapshots; exact line-ending drift retained.
- [Inventory](inventory.md), [file/command/test list](file-inventory.json) and
  [admin metadata](admin-inventory.json): implemented vs planned surface.
- [Live GitHub audit](github-audit.json): main/branches/PR/reviews/comments/CI,
  ADR numbers and collaborator permissions.
- [18 Issue / branch / owner / dependency map](issue-branch-owner-map.json):
  actual assigned Issues, DAG and reserved-only future isolation paths.
- [D08 reconciliation receipt](acceptance-reconciliation-20261007.json): verified original contract heads/author/comment hashes; D08 CLOSED, other human gates pending.
- [Old-to-new evidence](old-to-new-evidence.json): R01/ADR0001, current
  remote/local, R02A/R03A/grades; no historical approval rewriting.
- [Historical output paths](historical-output-links.json): on-disk existence and
  file hashes, including missing/pattern references.
- [Verification](verification.md) and [trace](../../agent-traces/MS7-MIG-R01.md):
  actual commands, versions, exit codes and limitations.
- [Human acceptance / decision list](acceptance.md): merged snapshot accepted; new post-merge amendment review/intake pending.
- [ADR accepted on reviewed revision](../../adr/ADR-0006-react-fastapi-migration.md),
  [active plan](../../exec-plans/active/MS7-MIG-R01.md),
  [exact specification provenance](../../../specs/migration/README.md).

`tools/audit.py` and `tools/runtime_readonly.py` reproduce R01 facts with the
existing interpreter; original checkout is a separate argument. They do not
replace Harness/verify, introduce target dependencies or authorize DB writes.
Preservation QA and disposable credentials/log files live outside the committed
package. Input manifest excludes its own digest and new R01 records; record
hashes, when used, are calculated separately to avoid circular self-digests.

The first candidate CI failed on two R01-owned edits to historically pinned root documents. PRODUCT/ARCHITECTURE are restored to exact input bytes, preserving MS6-R04 pins/Harness; see [first CI facts](ci-first-head.json). Corrected final head checks are in PR46, distinct from this historical failure.

## Historical participant import stage — scoped decision at daf4e603

[Ilya evidence index](ilya-20261007/README.md) provides byte-exact package reports,
screenshots, provenance and three separate runtime sources. [Current D02/D03
receipt](ilya-20261007/current-decision.json) records Ilya's own limited acceptance
and owner source-freeze choice; [F01–F04](ilya-20261007/follow-up-F01-F04.md)
require later target follow-up, with assignments PENDING. Final R01/MIG-G0/ADR
acceptance remains PENDING; historical snapshots and source manifest unchanged.

## Current final human records — 08.10.2026

[Final acceptance receipt](final-human-acceptance-20261008.json) records three
baseline/ADR decisions and two independent Task Approvals at daf4e603.
[Current acceptance](acceptance.md) supersedes earlier partial/PENDING status
paragraphs in this preparation history. [Exact former acceptance snapshot](acceptance-at-daf4e603.md)
and imported materials preserved. F01–F04 assigned13baybars for I03/I05, no
fixes performed. [Reviewer amendment list](final-review-changes.md) requires
new exact HEAD confirmation; MIG_BASE_SHA/snapshot merge remain PENDING.

## Current post-merge records

[Provenance](post-merge-provenance-20261008.json) supersedes earlier current-status
PENDING paragraphs in this chronological package. Original final-human receipt,
pre-merge [acceptance](acceptance-at-e510744.md)/[snapshot record](snapshot-review-at-e510744.json),
source/runtime/initial GitHub/frozen/imported evidence remain unchanged.
F01–F04 assigned13baybars, not implemented; ordinary-scale F04 readability
mandatory. No separate Vladimir F04 consent. All18 Issues OPEN; no later task.

Published post-merge amendment: [draft task PR47](https://github.com/Tramsey00/MathStart-Python/pull/47) → integration, independent review/intake pending. No direct main push.
