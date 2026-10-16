# R03 external V02 publication controls

These controls belong to R03. They record Ruslan's already approved **exact40**
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
including historical whitespace/pending labels. The gate materializes these in
an external owner directory and checks every digest immediately before execution.
The pins digest and concrete anchor digest are constants in the R03 bootstrap.
Neither is recomputed from a candidate. The standalone JSON anchor is a real
record of the user's limited policy decision, without a synthetic `_fixture`.
Its concrete artifact and this gate are still submitted for readiness review.

## Execution and trust boundary

Check out the exact reviewed R03 control revision into a separate clean owner
directory. Use a clean, isolated candidate repository, not a developer worktree.
The dedicated workflow pins that owner revision separately from its event SHA.
No candidate code, dependency installer, hook, filter, package restorer or auditor
probe is executed. Runtime dependencies are Python3.12 standard library and Git.
No database is used. Git's system/global config/attributes are disabled; local
executable/include config, info attributes and object alternates are rejected.

Before publication:

```text
python -I -B scripts/v02_publication_gate.py suite --owner-revision OWNER_REVISION_SHA --output NEW_EVIDENCE_DIRECTORY
```

This restores the exact source package without creating an implementation
commit. HEAD remains BASE, index/tree represents all151 additions, and the
receipt explicitly sets `implementation_sha: null`. Full ordinary/cr-at-eol
whitespace results stay **FAIL/2**, with exact original raw output. Both scoped
checks must be **PASS/0** with exactly40 literal exclusions. All73 raw files,
including33 without exceptions, remain pinned.

After separate owner confirmation, Vladimir publishes unchanged source. Pin the
actual full implementation commit SHA (single parent BASE and exact approved
tree), create a clean checkout of it, and run from the pinned owner checkout:

```text
python -I -B scripts/v02_publication_gate.py published --owner-revision OWNER_REVISION_SHA --root CLEAN_CHECKOUT --ref REVIEWED_CANDIDATE_SHA --output NEW_EVIDENCE_DIRECTORY
```

The bootstrap verifies clean HEAD/index/tree/provenance/effective metadata,
then invokes the mandatory command using the materialized owner controls:

```text
python -I -B OWNER_CONTROLLED/verify_publication_v3.py --root CLEAN_CHECKOUT --ref REVIEWED_CANDIDATE_SHA --owner-anchor OWNER_CONTROLLED/owner-approval-v3.json --owner-anchor-sha256 5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7
```

Any different tree, even a seemingly harmless documentation change, requires
independent reconciliation and owner review. This implementation does not
automatically accept new pins. `--local-proposal` is not exposed by the bootstrap.

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
attacks. The overall R03 task remains INCOMPLETE pending the full target pipeline
on accepted V02/I02 inputs, V04 CLI deliverables and independent approvals.
