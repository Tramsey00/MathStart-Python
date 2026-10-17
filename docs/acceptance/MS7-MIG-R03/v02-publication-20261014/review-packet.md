# R03 external V02 publication gate: owner review packet

Current gate status: **READY_FOR_OWNER_REVIEW**. The original snapshot, concrete
owner anchor and executable gate have real positive/negative Linux evidence.
R03 remains **INCOMPLETE**. Gate-readiness confirmation, authorization for Vladimir
to publish, V02 Task Approval and integration acceptance remain separate gates.

This packet supersedes the missing-source NOT_READY status in the dated
2026-10-13/14 preparation records. Their evidence and V02 historical pending
labels remain unchanged. No V02 implementation commit exists in this packet.

## Exact provenance

| Input / execution identity | Value |
| --- | --- |
| Accepted BASE / actual reconstructed HEAD | `0c03197e23f69a233c0fcf8bdffa336feca20b92` |
| Immutable MIG_BASE | `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7` |
| Historical integration input | `8d958aeeb17da46839722441425ccbb5889e2ab7` |
| Independently verified staged/tree snapshot | `dbad1e853dff354c5d3255755afb5cc32e0ad279` |
| R03 control revision / actual owner checkout | `1b75c6e58ecdcb4bb172d4df979e9b9efa7dde68` |
| R03 workflow revision / event SHA | `21a82d43cd8219338fe83bf6ff73a57c046e4297` |
| V02 implementation SHA | **null / not published** |
| Linux run | [38596739924 — SUCCESS](https://github.com/Tramsey00/MathStart-Python/actions/runs/38596739924) |
| Earlier gate run, separately retained | [38596554853 — SUCCESS](https://github.com/Tramsey00/MathStart-Python/actions/runs/38596554853), controls `6adf10e00518d9c4e48e45afeca24f4e81a89931` |

The clean Linux runner restored the original source ZIP into a new Git repository
with HEAD=BASE and151 staged additions. No scratch implementation commit was
created. BASE commit/tree identity and all2092 imported objects were checked;
Git fsck passed. Actual1672 BASE entries +151 additions =1823 entries reconstruct
the approved tree. The new ZIP inventory has the corrected tree OID; the earlier
transmission typo is preserved in the historical transport archive.

## Verified source and controls

Source archive [v02-source-snapshot-20261014.zip](../v02-source-snapshot-20261014.zip),
SHA256 `57cad8b19e75bda674ce1ac9ddcf9c92a6b57daa2a3b4bd1f39e528c1a77cd0a`:
all234 safe regular members and233 inventory rows match actual bytes. All151
file records match the prior independently received inventory. Three original
handoff documents match losslessly; the independent Round3 auditor report pin
and its five control tuples/40 exception blob tuples were crosschecked.

Real blobs, SHA256, Git OID, size, mode100644, exact path set, working bytes and
13/full index/working effective attributes PASS. The five control tuples match
the earlier bindings. All73 raw-preservation files remain exact, including33
without whitespace exceptions. Original139 inputs and60 frozen files PASS.
The frozen baseline workflow and historical captures were not changed.

Owner-controlled files are in
[specs/migration/r03-v1/v02-publication](../../../../specs/migration/r03-v1/v02-publication/README.md).
`trusted-controls.zip` contains the exact v3 executable, policy, manifest,
bindings and both applicable attributes files. The bootstrap checks these and
the anchor immediately before verifier execution. Candidate-supplied pins are
never adopted. System/global Git config/attributes are disabled; local
executable/include config, info attributes and object alternates are rejected.

Concrete [owner-approval-v3.json](../../../../specs/migration/r03-v1/v02-publication/owner-approval-v3.json)
records Ruslan's previously approved exact40 decision and independently verified
bindings under schema `MS7-MIG-V02-owner-metadata-anchor-v3`:

```text
anchor SHA256:   5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7
pins SHA256:     eb32a3245275649e9a69c67ea17001cfd4b8ff0cd7a30e63bcac325692c9c591
verifier SHA256: 54da54d7a54f9ca714a393577a31a74e948c373bbee4c92045110958c59a56a5
exception set:   fa62cf5f4c9b3aaf91864b9face548a5f45759390fb7bedd9cdef5ae6e7c2e18
```

This actual anchor has no `_fixture`. It is presented for review of the concrete
artifact/gate; it does not add Task Approval or publication authorization.
V02 source pending labels remain byte-identical. Neither `--local-proposal` nor
historical synthetic approvals were used.

## Execution results

Linux Ubuntu24.04.5, Python3.12.15, Git2.55.0; no package dependencies or database.
Exact mandatory external verifier command exit0; repeated positive after all
attacks exit0. Full ordinary whitespace remains **FAIL/2,3887 diagnostics**;
cr-at-eol remains **FAIL/2,6 diagnostics**. Both scoped checks are **PASS/0**.
Their streams match the original raw output exactly; no new diagnostics.

All17 substantial negative cases reject for the intended reason:

| Attack group | Observed rejection |
| --- | --- |
| Replace trusted executable; replace policy/manifest/bindings/both attributes | `OWNER_CONTROL_DIGEST`, verifier not spawned, execution marker absent |
| Replace owner anchor | `OWNER_ANCHOR_DIGEST`, verifier not spawned |
| Candidate policy byte / exception expansion / joint verifier-policy-pins replacement | `POLICY_DIGEST_MISMATCH`; candidate executable never runs |
| Candidate manifest or bindings bytes | `HANDOFF_BINDINGS_CONTENT` |
| Manifest mode100755 with unchanged bytes | `FIXED_MODE` |
| Changed attributes file | its immutable `BLOB_OID` |
| Effective manifest attributes with unchanged tracked bytes/tree | `UNAPPROVED_INFO_ATTRIBUTES` and lower-layer `FIXED_ATTRIBUTES` |
| Pinned raw CRLF/LF byte change | immutable `BLOB_OID` |
| New whitespace outside40 | immutable `BLOB_OID`; real scoped whitespace command also FAIL/2 with new-path diagnostic |

The production bootstrap rejects changed tree provenance before execution.
Lower-layer attack probes invoke the unchanged trusted verifier solely to check
its precise rejection reasons. They cannot transfer approval to mutated trees.
Original bytes/index are restored between attacks and after the final case.

## Retained raw evidence

- [Original GitHub artifact](https://github.com/Tramsey00/MathStart-Python/actions/runs/38596739924/artifacts/11909044256),
  SHA256 `f52fcb18f4a4ecd4343fcf2efe363c23ec7f856b2995f4666b3fdd3717ca3de2`.
- [Repository raw ZIP](linux-38596739924-raw.zip) and
  [artifact reconciliation](38596739924-artifact-reconciliation.json):408 original
  members,397 evidence-manifest rows and192 command receipts independently checked.
  A duplicate55,278,004-byte stdout is mapped by digest to the exact source ZIP
  already in the repository. All original bytes remain available, with no stream
  redaction/newline rewriting. Earlier successful artifact retained separately.
- [Negative receipts](38596739924-negative-results.json),
  [snapshot verification](38596739924-snapshot-verification.json),
  [workflow/checkout provenance](38596739924-provenance.json),
  [result summary](38596739924-result.json) and full verifier diagnostic sets in raw ZIP.
- [Local raw archive](local-raw-evidence.zip) includes failed Windows path-length
  setup, resolved restoration, positive/17 negatives, and both pure-check runs.
  First pure run failed on sandbox Temp permissions; workspace Temp retry passed
  all6 groups/215 tests. Historical preservation PASS1370 files/strict pins.
- [Companion runs](companion-runs-at-workflow-sha.json): accepted I01 frontend
  run38596750664 SUCCESS, accepted V01 PG run38596750682 SUCCESS. Migration
  run38596740077 has verify/pure SUCCESS and target FAILURE; PR counterpart
 38596750672 also FAILURE. These do not replace the dedicated gate result.

Target FAILURE source: [retained job logs](job-logs.zip),
`target-not-run-115965301256.log` with its digest manifest.
Expected command handoff `status=REVIEWED` with all10 commands; actual
`PENDING_OWNER_IMPLEMENTATIONS_AND_REVIEW`, `commands={}`. Target fresh/upgrade/
full registry stages are **NOT_RUN**, not PASS. This pre-existing dependency is
preserved rather than weakening the prerequisite.

## Owner review and next actions

Review the exact source/control provenance, five tuples/40 paths/73 raw scope,
concrete anchor digest, trusted execution boundary, expected negative reasons
and original full/scoped whitespace outputs. Then explicitly confirm gate
readiness and separately authorize candidate publication as requested by owner.

After that confirmation, Vladimir publishes exactly the reviewed source with
BASE parent and approved tree. Pin the full resulting implementation SHA
separately from this staged/tree evidence. R03 makes a fresh Linux checkout,
records HEAD/index/tree/parent and executes the pinned bootstrap's `published`
command, which runs:

```text
python -I -B OWNER_CONTROLLED/verify_publication_v3.py --root CLEAN_CHECKOUT --ref REVIEWED_CANDIDATE_SHA --owner-anchor OWNER_CONTROLLED/owner-approval-v3.json --owner-anchor-sha256 5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7
```

Any change to reviewed bytes/metadata/tree is a named reconciliation blocker,
never automatic candidate repinning. V02 Task Approval and merge remain later.
R03 still needs accepted V02/I02 inputs, reviewed10-backend/4-frontend command
handoff including V04 content CLI, full target/PG/browser evidence on exact
combined SHA, and independent Vladimir/Ilya approvals. Issues34/40 stay open
until final main integration. See [CLI/receipt checklist](../cli-receipt-handoff-checklist.md).
