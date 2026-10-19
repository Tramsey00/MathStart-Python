# Historical R03 external V02 publication controls — retired gate

**HISTORICAL / RETIRED.** This document describes the old fixed-candidate gate,
not the current runtime or a pending implementation task. Current technical
completion and HUMAN_PENDING status are in [MIGRATION.md](../../../../MIGRATION.md).
Approved controls and their hashes remain unchanged.

These controls belong to the historical R03 stage. They record Ruslan's already approved **exact40**
exception decision after independent reconstruction of the original151 files.
They do not grant V02 Task Approval or permission to publish/merge.

- Accepted BASE: `0c03197e23f69a233c0fcf8bdffa336feca20b92`.
- Immutable MIG_BASE: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
- Verified staged tree: `dbad1e853dff354c5d3255755afb5cc32e0ad279`.
- Source ZIP SHA256: `57cad8b19e75bda674ce1ac9ddcf9c92a6b57daa2a3b4bd1f39e528c1a77cd0a`.
- Exception-set SHA256: `fa62cf5f4c9b3aaf91864b9face548a5f45759390fb7bedd9cdef5ae6e7c2e18`.
- Owner anchor: `owner-approval-v3.json`, SHA256
  `5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7`.
- Approved pins SHA256:
  `eb32a3245275649e9a69c67ea17001cfd4b8ff0cd7a30e63bcac325692c9c591`.
- Exact verifier v3 SHA256:
  `54da54d7a54f9ca714a393577a31a74e948c373bbee4c92045110958c59a56a5`.

`trusted-controls.zip` preserves all six source control files byte-for-byte,
including historical whitespace/pending labels. The retired gate materialized these in
an external owner directory and checked every digest immediately before execution.
The pins digest and concrete anchor digest are constants in the R03 bootstrap.
Neither is recomputed from a candidate. The standalone JSON anchor is a real
record of the user's limited policy decision, without a synthetic `_fixture`.
The original artifact/gate readiness review belonged to that historical stage.

## Historical replay and restoration

This gate and its dedicated workflows/controllers were retired in cleanup467866e.
There is no current command to run the deleted controllers from this checkout.
For historical investigation, recover the required chain at
`1d9e4d39aa103ccc049dd9569c2354893af30a75`, the last source tree before retirement,
using the existing [restoration index](../../../../docs/acceptance/migration-execution/cleanup-20261019/restoration-index.json).
Its original 65 entries identify the removed controllers/source snapshot by that
SHA. Additional artifact entries use cleanup467866e as their own source SHA.
Restore only the required historical paths in a separate investigation checkout,
then follow the [original gate description at its source revision](https://github.com/Tramsey00/MathStart-Python/blob/1d9e4d39aa103ccc049dd9569c2354893af30a75/specs/migration/r03-v1/v02-publication/README.md).
Verify each restored blob against its indexed canonical size/SHA256. This is
recovery guidance, not an instruction to restart publication or migration.

The original replay used a separate pinned owner checkout and isolated candidate,
standard-library Python3.12/Git and no DB. It rejected changed executable/config/
attributes/alternates before execution. The original staged representation kept
HEAD at BASE and implementation_sha null; later published-commit checks bound
one exact parent/tree. Full ordinary/cr-at-eol whitespace results remained FAIL/2,
scoped checks PASS/0 with exactly40 exclusions, and all73 raw files were pinned.
These are historical observations and trust boundaries, not new approvals.

## Negative evidence

The suite attacks the real reconstructed package. It restores original bytes
and the approved index between cases. The production bootstrap rejects changed
trees first. Separate lower-layer probes run the unchanged external verifier on
mutated trees solely to establish the precise rejection reason; they cannot
issue production approval. Executable/control replacements are rejected before
verifier spawn, with an execution marker checked absent. New whitespace also
has its actual scoped FAIL/2 raw output retained.

The result, argv, stdout/stderr, exits, mutation hashes, versions and evidence
manifest are retained even on failure. A clean positive is repeated after all
attacks. The old INCOMPLETE label described prerequisites at that date. It is not the
current migration status: full target/recovery/combined and independent technical
review subsequently passed at the exact SHAs recorded in MIGRATION.md. Human
acceptance remains pending.
