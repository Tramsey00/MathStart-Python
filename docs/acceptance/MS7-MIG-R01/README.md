# MS7-MIG-R01 records

This package prepares the current Django snapshot for independent acceptance.
**R01 INCOMPLETE / MIG-G0 PENDING / MIG_BASE_SHA PENDING.** Input local/remote
main: `8c11edadc8debc81432d1db1145feac504f09061`. Candidate head and its current
CI/tested merge-ref are recorded in the snapshot draft PR; they are not the
accepted integration baseline.

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
- [Old-to-new evidence](old-to-new-evidence.json): R01/ADR0001, current
  remote/local, R02A/R03A/grades; no historical approval rewriting.
- [Historical output paths](historical-output-links.json): on-disk existence and
  file hashes, including missing/pattern references.
- [Verification](verification.md) and [trace](../../agent-traces/MS7-MIG-R01.md):
  actual commands, versions, exit codes and limitations.
- [Human acceptance / decision list](acceptance.md): independent records pending.
- [Proposed ADR](../../adr/ADR-0006-react-fastapi-migration.md),
  [active plan](../../exec-plans/active/MS7-MIG-R01.md),
  [exact specification provenance](../../../specs/migration/README.md).

`tools/audit.py` and `tools/runtime_readonly.py` reproduce R01 facts with the
existing interpreter; original checkout is a separate argument. They do not
replace Harness/verify, introduce target dependencies or authorize DB writes.
Preservation QA and disposable credentials/log files live outside the committed
package. Input manifest excludes its own digest and new R01 records; record
hashes, when used, are calculated separately to avoid circular self-digests.
