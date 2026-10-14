# V02 external publication gate: current review and historical preparation

**Current 2026-10-14: GATE_AND_ANCHOR_CONFIRMED / AWAITING_PUBLISHED_CANDIDATE.
R03 remains INCOMPLETE.**
The user confirmed run38596739924, reviewed PR49 HEAD5511284, the concrete anchor
digest and control revision1b75c6e, and authorized Vladimir to publish the exact
single-parent/tree candidate. [Separate human decision](v02-publication-20261014/owner-confirmation.json)
and [published-commit handoff](v02-publication-20261014/published-handoff.md)
are current. No implementation PR/SHA has been received; the published gate is
NOT_RUN. The approved source/anchor and earlier evidence remain unchanged.

**Earlier preparation: READY_FOR_OWNER_REVIEW.**
The full original source has now been independently verified and the concrete
external gate passed real positive/17 negative checks on Linux. Current
[owner review packet](v02-publication-20261014/review-packet.md),
[machine readiness/intake](v02-publication-20261014/readiness.json) and
[run38596739924](https://github.com/Tramsey00/MathStart-Python/actions/runs/38596739924)
supersede the missing-source status below. Concrete anchor digest and exact
R03 control/workflow revisions are in that packet. Gate confirmation and
publication authorization were pending at that preparation stage; no V02 Task
Approval or merge occurred. The later confirmation above supersedes that status.

## Historical preparation record — 2026-10-13/14

**Historical gate: NOT_READY / REQUIRED_151_FILE_SNAPSHOT_MISSING. R03: INCOMPLETE.**
This is the R03 gate preparation record, not an executable gate, approval anchor,
publication receipt, V02 Task Approval or permission to merge. No verifier v3 was
received or executed. No candidate implementation SHA has been assigned.

## Authority and intake

Руслан's instruction of 2026-10-13 approves the limited publication exception
policy: exactly **40 individually pinned paths**, with **73 raw-preservation paths
retained separately**. That decision is already approved and does not require
repeat approval because documents were initially unavailable. The four documents
are now received and read: owner-handoff, bindings, developer report-v3 and
Independent Round3 Re-Audit Report. Both user-supplied SHA256 checks PASS.
Their exact bytes are retained in the
[four-document reference archive](v02-publication-reference-documents-20261013.zip),
not a151-file snapshot. [Document reconciliation](v02-publication-document-reconciliation-20261013.json)
crosschecks five control tuples and the exact40 paths with the auditor's tables.
It does not independently verify the missing verifier/policy/manifest source.

Current2026-10-14 [transport tree resolution](v02-tree-oid-resolution-20261014.md):
inventory/REPORT expected OID transcription is resolved by the user. Independent
BASE+151 declared-entry hashing reproduces the existing correct tree pin, without
repinning. Full declared151/73 inventories are available; actual source archive,
blobs/effective metadata/verifier/whitespace streams remain missing. Владимир may
resume unchanged snapshot packaging. Packaging permission is not gate readiness.

This document update starts from R03
`428258d4758d95e6d424f4386d2419a3f6ab8142`; the earlier preparation started at609dc92.
Accepted integration remains
`0c03197e23f69a233c0fcf8bdffa336feca20b92`; immutable MIG_BASE_SHA remains
`60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`. The historical input
`8d958aeeb17da46839722441425ccbb5889e2ab7` is retained.

An authorized source request was sent to Владимир / VladimirFrolov777 in
[PR49 comment6141201701](https://github.com/Tramsey00/MathStart-Python/pull/49#issuecomment-6141201701).
Issue35 has no owner comments at the recorded intake; no migration V02 branch or
PR is published. The old `codex/ms7-v02-grades-api` is not this migration task.
The user subsequently provided exact Telegram Desktop paths. The initial
unavailable-documents entry is history, not the current intake status. An
[updated source request6147207245](https://github.com/Tramsey00/MathStart-Python/pull/49#issuecomment-6147207245)
asks Владимир only for original151-file staged snapshot/reconstruction metadata
and raw audit evidence. It explicitly retracts the request for an owner approval
JSON from Владимир: **R03 prepares that artifact after independent source checks**.

The [machine intake record](v02-publication-intake-20261013.json) deliberately
contains document-derived expected tuples and40 approved path identities, with
actual trusted executable/anchor pins still null and source execution NOT_RUN.
The complete declared73 path list is now supplied by transport inventory, with
actual identity/bytes/metadata against policy still pending;40 subset73 and33
non-exempt raw paths are confirmed at document level. It must never be consumed as an
owner approval artifact or substituted for a real binding manifest.

## Owners and review decisions

| Stage | Owner | Review criterion |
| --- | --- | --- |
| Original verified snapshot, handoff, bindings and auditor package | Владимир / VladimirFrolov777 | Immutable source and exact original bytes, complete 40/73 lists, reproducible metadata and raw reports |
| Independent snapshot reconciliation and external executable/control copies | Руслан / R03 | Independently observed bytes/OID/size/mode/attributes match approved bindings and auditor report, without candidate pin regeneration |
| Limited exception policy | Руслан | Already APPROVED by direct user instruction for the exact40 paths in supplied bindings; preserve that decision without requesting it again |
| Owner approval JSON and concrete digest | Руслан / R03 | After independent source verification create schema v3 artifact in R03, bind verified five-input tuples/exact40 set and existing policy decision, compute its actual digest and present with gate for review; not an artifact supplied by Владимир |
| Gate readiness review | Руслан, with Владимир checking the source reconciliation | Trusted v3 and all control pins established, mandatory negatives pass, clean Linux CI proof and raw outputs available |
| Publication after readiness confirmation | Владимир | Candidate contains exactly the reviewed implementation/evidence bytes and metadata; external gate rerun against its exact commit |
| V02 Task Approval / integration / R03 completion | Separate existing task gates | Not granted by publication policy, publication verifier, checklist review or CI success |

## Required source package before executable gate preparation

- [ ] Original151-file snapshot:139 previous +12 Round3 additions, precise
  inventory and original Git blob/working bytes, modes/attributes; accepted BASE
  `0c03197e23f69a233c0fcf8bdffa336feca20b92`. Staged snapshot archive is allowed:
  implementation commit is not required at this stage. Include archive SHA256,
  object format and instructions reconstructing the index/tree on BASE without
  source normalization. Compare reconstructed full tree with auditor-reported
  `dbad1e853dff354c5d3255755afb5cc32e0ad279` (tree OID, not a commit SHA).
- [ ] Original `verify_publication_v3.py` bytes and independently checked SHA256,
  source path/OID/size/mode/attributes, dependencies, exit contract and command
  interface. Inspect the source before any execution, including `--help`.
- [x] Owner-handoff and derived bindings documents: user hashes verified; exact40
  unique explicit exception paths match auditor Appendix B. Report supplies
  SHA256/OID/size and diagnostic counts for all40; full line/reason arrays and
  real mode/attribute/blob reconciliation still require original policy/snapshot.
- [ ] Separate inventory for all 73 raw-preservation paths with the same
  provenance and exact-byte/metadata requirements. Confirm any list intersection
  explicitly from approved data; do not resolve overlaps by weakening retention.
- [ ] Actual policy, manifest, root/V02-local attributes files and verifier v3
  bytes from Владимир. All five expected SHA256/OID/size/mode/13/full-attribute
  tuples now match auditor section13. Only root .gitattributes blob/OID/size/mode
  was also checked against available accepted BASE; the actual snapshot/effective
  metadata are still missing. Expected tuples are not executable trust pins.
- [x] Auditor report and source identity/configuration received. It reports
  manifest mode/attributes P2 CLOSED, P02 CLOSED on Windows, P03 CLOSED and external
  P01 pending. These are external audit receipts, not new R03 executions.
- [ ] Actual full whitespace stdout/stderr/exit **FAIL/2** and scoped receipts,
  original preservation/reconciliation/probe evidence. Reported full ordinary
  3887/40 and cr-at-eol6/3 counts and stream hashes are known; actual streams
  were not among the four attachments and cannot be reconstructed from summaries.

## R03-owned approval artifact after source verification

Do not request this artifact from Владимир and do not create an APPROVED anchor
from documentary crosschecks alone. After independent reconstruction/reconciliation,
prepare an actual JSON in owner-controlled R03 with these handoff v3 fields:

```text
version = MS7-MIG-V02-owner-metadata-anchor-v3
owner = Ruslan
decision = APPROVED
inputs = independently verified five-input tuples
exception_set_sha256 = fa62cf5f4c9b3aaf91864b9face548a5f45759390fb7bedd9cdef5ae6e7c2e18
exception_paths = the exact40 supplied approved paths
```

Each input tuple contains blob_sha256/blob_oid/blob_bytes/mode/attributes/
attributes_all. The concrete schema/parser must be confirmed by inspecting actual
v3 source. No `_fixture`, synthetic anchor or local-proposal approval is used.
Record the user's existing limited policy decision with the independently verified
bindings. Freeze this specific artifact, compute its actual SHA256 and present
that digest together with the executable gate, trust pins and evidence for review.
This does not reopen policy approval or grant V02 Task Approval. Anchor/path/digest
remain null until these source prerequisites are satisfied.

## Trust boundary and required independent comparison

Keep `OWNER_CONTROLLED` outside `CLEAN_CHECKOUT`. It is a separately checked out
immutable **owner-controlled R03 revision**, reviewed independently of V02. The
bootstrap/CI workflow must itself come from that trusted revision. Pin its full
SHA and tree, executable v3 digest, approval JSON digest, policy/manifest/
attributes/bindings digests in reviewed R03 data. Resolve source paths from the
approved R03 package, not candidate arguments or environment assertions.

Before execution, a trusted bootstrap checks its executable/control copies
against those recorded bytes and Git metadata. Reject modified, replaced,
symlinked, missing or candidate-contained copies. No executable path from the
candidate, candidate checkout hooks, installed candidate package, candidate
verifier copy or candidate-computed digest participates in this trust decision.
Run in an owned workspace where the candidate cannot write trusted copies; pin
and recheck immediately before launching the verifier. The replacement negative
must prove refusal before any replacement code executes.

Independent R03 reconciliation uses binary Git object reads and filesystem
reads; never normalize original evidence before hashing. Record SHA256 and size of the original
snapshot bytes, `git cat-file blob` bytes, and materialized checkout bytes
separately. Raw73 must stay exact on every checkout. Normal text materialization
is judged by vetted v3/approved attributes; historical Windows working hashes
must not silently replace exact Git blob pins. Determine OID/object type and Git mode from the actual tree; compute
OID of filesystem bytes without applying Git filters. Windows filesystem execute
bits do not substitute for Git mode; check Linux materialization separately.
Attributes are read from the reviewed Git tree and observed index/checkout under
isolated Git configuration. Global/system/info attributes, filters and checkout
conversion must not silently alter the comparison.

Compare every field with **already approved bindings**, and crosscheck the
auditor report against the actual snapshot. Report disagreement as failure;
never update bindings from candidate observations to make it pass. A changed
trusted revision/control artifact requires a new explicit review and pins.

## Two execution stages and exact command

1. **Before publication:** obtain and independently reconcile the verified
   snapshot; freeze trusted R03 verifier/control copies and anchor digest; prepare
   the clean candidate reconstruction and negative checks on CI's Linux platform.
   This establishes gate readiness only. It cannot assign a not-yet-published
   implementation SHA or produce a post-publication approval receipt.
2. **After Владимир publishes:** inspect current PR head/ref, pin the exact
   reviewed implementation commit and tree independently from the workflow SHA;
   create a fresh clean checkout at that commit; repeat the external gate and
   required scoped checks. A changed head is a new candidate, not approval transfer.

The mandatory post-publication command is exactly:

```text
python -I -B OWNER_CONTROLLED/verify_publication_v3.py --root CLEAN_CHECKOUT --ref REVIEWED_CANDIDATE_SHA --owner-anchor OWNER_CONTROLLED_APPROVAL_JSON --owner-anchor-sha256 INDEPENDENT_APPROVED_ANCHOR_DIGEST
```

These names are placeholders for subsequently reviewed concrete paths/pins;
there is currently no executable v3 or anchor at those paths. The real invocation
and all resolved arguments must be recorded in the receipt. Do not use
`--local-proposal` or a synthetic anchor for readiness/publication approval.
Do not invoke any candidate-installed entry point in place of this command.

## Clean Linux CI checkout and evidence contract

- [ ] Workflow source, R03 control revision, original snapshot SHA, reviewed V02
  implementation SHA, event SHA, actual checkout SHA/tree and merge parents are
  separate fields. A PR merge-ref is not the implementation SHA.
- [ ] Use a fresh owned Git repository/checkout and controlled Git configuration;
  no inherited filters/hooks/global attributes or unreviewed submodules/LFS hooks.
  Checkout only immutable refs. Log actual Python/Git/OS versions and Git config
  affecting content/attributes. Record cleanliness before and after verification.
- [ ] Verify trusted executable/control pins before invoking Python. Use isolated
  mode `-I`, no bytecode `-B`, trusted execution cwd and bounded subprocesses.
  Do not install or execute candidate code merely to perform publication checking.
- [ ] Verify exact objects/checkout bytes/size/mode/attributes for approved 40
  paths and separate 73 raw paths. Preserve raw members byte-for-byte. Reject
  list additions/removals, metadata drift, object-type/path escape and unexpected
  candidate changes outside the reviewed V02 publication scope.
- [ ] Run the **full** whitespace command under the approved configuration and
  retain exact stdout, stderr and exit2/FAIL. Compare diagnostic set with the
  approved original report; no new diagnostics are allowed. Scoped exclusions
  use exactly the approved 40 paths; no directory-wide exclusions. Scoped
  whitespace and other handoff-prescribed scoped checks must exit0/PASS.
- [ ] Upload original and current raw full/scoped/verifier outputs, command argv,
  deadlines/exits, per-file reconciliation, negative-check outputs and CI run URL.
  Hash artifacts and retain FAILURE/NOT_RUN separately from PASS. Redact no
  whitespace diagnostics and do not overwrite original auditor failures.

The auditor specifies original full commands `git diff --cached --check` and
`git -c core.whitespace=cr-at-eol diff --cached --check`; both scoped variants
append exactly40 `:(exclude,literal)<path>` arguments from supplied bindings.
At published commit stage compare accepted BASE to reviewed candidate with the
same explicit diagnostic configuration and exact exclusion list. Bind actual
argv/ref/index to receipts. Original line/reason arrays and raw stdout still
require the snapshot/policy/evidence package.
Publication succeeds only with external verifier exit0, exact approved bytes and
metadata, no new whitespace diagnostics and every required scoped check PASS.
The retained approved full-whitespace FAIL/2 is not rewritten as a full PASS.

## Required negative controls

Each control uses an isolated throwaway reconstruction of the actual reviewed
package. Preserve positive control/result and then mutate one input. Restore from
the immutable source between cases. Synthetic unit fixtures, if later used for
bootstrap tests, cannot serve as these actual-package publication proofs.

| Control | Required result |
| --- | --- |
| Replace trusted v3 executable before execution, including a trivial exit0 script | Trusted bootstrap rejects digest/identity drift before replacement code executes; no false verifier PASS |
| Change trusted anchor/policy/bindings/manifest/attributes | Reject against external approved pins, even if candidate recomputes all local hashes |
| Change manifest Git mode with unchanged bytes | Nonzero failure; content digest alone is insufficient |
| Change effective attributes affecting manifest or another pinned file | Nonzero failure, including root/nested/info/global attributes where applicable; no newline-equivalent waiver |
| Change one byte, OID, size, object type or Git mode on a pinned exception path | Nonzero failure against original approved bindings |
| Change one of 73 preserved raw files, including CRLF/LF-only mutation | Nonzero failure; raw history remains exact |
| Add/remove an exception path or turn an entry into a prefix/wildcard | Nonzero failure; count and identity of all 40 paths enforced |
| Add new whitespace outside the 40 paths | Nonzero failure; retained historical FAIL/2 cannot hide a new diagnostic |
| Change a candidate-local verifier or provide recomputed candidate pins | No trust transfer; trusted external verifier/pins still control result |
| Dirty checkout, different ref/HEAD or executable/control path inside candidate | Nonzero failure before publication receipt |
| Use --local-proposal or a synthetic anchor as approval | Refused as publication/readiness approval, regardless of local exit0 |

All these controls are currently **NOT_RUN**, as is the clean Linux CI snapshot
check. Their future run must retain case IDs, mutation, expected/actual exit,
before/after hashes, proof of nonexecution for executable replacement and raw
stdout/stderr. No result in this packet means PASS on a missing source package.

## Readiness and next available step

The documents and existing limited-policy decision are already available. The
immediate next step is receipt of Владимир's original verified151-file staged
snapshot, inventory/reconstruction instructions and raw evidence. Then R03 can
inspect verifier v3, pin trusted controls, implement/review the concrete bootstrap
and Linux CI wiring in its own paths, repeat real-package negatives and request
gate-readiness confirmation with evidence. Only after that confirmation does
Владимир publish the candidate for exact-SHA post-publication verification.

No V02-owned file, existing frozen workflow, raw evidence, operational command
map or approval state is changed here. No candidate-derived pins, synthetic
approval, V02 Task Approval, merge or Issue closure occurs. The wider R03 gates
remain those in the [CLI/receipt checklist](cli-receipt-handoff-checklist.md).
