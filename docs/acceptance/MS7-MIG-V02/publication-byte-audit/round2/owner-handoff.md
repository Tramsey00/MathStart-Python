# Ruslan handoff — V02 publication exception v2

Status: OWNER_EXCEPTION_APPROVAL_PENDING. No root CI/workflow was changed.
This is a concrete proposal for owner review, not evidence of owner approval.

The candidate policy preserves73 raw files but exempts only40 exact paths,
with pinned blob OID/SHA256/size and all allowed line/reason diagnostics.
New paths, removed entries, changed hashes or policy bytes fail an unchanged v2
checker. Existing128 blobs and all139 publication paths are pinned by the proposal.

Candidate policy SHA256: 09fff1895df489f707000f4a1fec8f6ddd62d1666d2b1c44c94b16ca8ae1741f
Candidate verifier canonical Git-blob SHA256: 3c3c797a0ae5a039ad8a5e8a47eb7693171b3fe6690991137904b692d0e92b42
Manifest digest must be measured independently after final staging; it cannot be
embedded in a file that the manifest itself hashes without a circular dependency.

Required owner action:

1. Independently review policy composition40/73, line diagnostics, blob manifest,
   clean-checkout probes and v2 source. Decide whether the full FAIL/2 is permitted
   with this exact residual raw exception. Task Approval remains a separate gate.
2. Pin reviewed verifier code and policy digest outside the mutable V02 task
   scope: e.g. owner-controlled R03/CI tool or protected artifact/config. The
   executable is standard-library-only and imports no code from the candidate.
   Before execution verify its digest independently. Copying this file into CI
   without pinning it independently does not establish a trust boundary.
3. Pin the final manifest Git-blob SHA256 externally as the reviewed candidate.
   Read exact bytes with a Python subprocess, not PowerShell text pipelines.
4. In that separately controlled scope issue an approval anchor JSON with fields
   owner=Ruslan, decision=APPROVED, policy_blob_sha256, verifier_blob_sha256,
   manifest_blob_sha256; independently pin the anchor's own digest. No such
   approved artifact is supplied or fabricated here.
5. Invoke the owner-controlled executable with --root CHECKOUT,
   --owner-anchor OWNER_CONTROLLED_JSON --owner-anchor-sha256 EXTERNAL_PIN.
   The anchor path must be outside CHECKOUT. --ref REVIEWED_COMMIT_OR_TREE is
   available for a published Git representation. No implementation commit exists.

Ordinary invocation without owner anchor returns exit3 OWNER_EXCEPTION_APPROVAL_PENDING
after local checks. --local-proposal returns exit0 only for technical conformance;
it does not approve the exception. Full Git whitespace checks always report their
actual FAIL/2. Local pins cannot prove resistance to simultaneous replacement of
the verifier and policy; a synthetic external-pin negative is a simulation only.

Reject a new/rebound policy unless separately reviewed and repinned. An in-scope
report, allowlist, generated manifest or exit0 self-check is never an approval anchor.
If this exception is rejected, choose another explicitly approved lossless evidence
packaging/publication procedure. Do not normalize preserved historical bytes.

The original v1 verifier/report remain immutable historical records of the
rejected proposal. They are not the current publication gate. Use only the v2
entry point after independent review and externally pin its code before execution.
