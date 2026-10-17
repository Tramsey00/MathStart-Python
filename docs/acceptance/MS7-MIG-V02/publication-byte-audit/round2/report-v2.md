# MS7-MIG-V02 — Publication Gate Remediation Report v2

**READY FOR INDEPENDENT RE-AUDIT; OWNER EXCEPTION APPROVAL PENDING.**
`tested_implementation_sha=null`; `publication_status=PENDING_PUBLICATION`.
This Round2 is evidence-only. No commit/push/merge/rebase/reset/clean/PR.

## 1. Source/index state before remediation

Branch ms7-mig-v02-content; HEAD/base/merge-base
`0c03197e23f69a233c0fcf8bdffa336feca20b92`. Initially128 staged additions,
no unstaged drift, no existing baseline modification. Intake pins every initial
working SHA256, raw Git-blob SHA256/OID/size. Original128 files are unchanged.

## 2. Original P01/P02/P03 findings

P01/P2: mutable exception list could be expanded/reduced while rebinding a nearby
manifest. P02/P2: historical Windows working hashes rejected legitimate LF clean
checkout; OID/size/attributes were not enforced. P03/P3:73 raw preservation paths
were unnecessarily all exempt; only40 require whitespace exceptions.
The auditor also noted P3 stale runtime status: positive F01/F02 re-audit exists.
Original negative publication verdict remains CHANGES REQUIRED at that snapshot.

## 3. Exact changed files

Only11 new append-only files below `publication-byte-audit/round2/`:
exception-policy.json; source-imports.json; intake.json; verify_publication_v2.py;
test_publication_v2.py; report-v2.md; owner-handoff.md; verification.json;
publication-manifest-v2.json; probe-results.json; checkout-results.json.
Previous128 files, v1 verifier, historical reports/manifests/acceptance, runtime,
tests, .gitattributes, frontend, V01 and root CI remain unchanged.

## 4. Allowlist integrity mechanism

Unchanged v2 code pins the exact proposal policy byte SHA256 09fff1895df489f707000f4a1fec8f6ddd62d1666d2b1c44c94b16ca8ae1741f.
Any added/removed/reordered/changed entry, including mutable report introduction
or changed blob SHA256, fails before mutable manifest rebinding can help.
It enforces exact73 raw preservation entries, exact40 whitespace entries, fixed
139 publication paths and unchanged original128 blobs. Unknown diagnostics fail.
Checks use explicit GateError, not optimization-removable Python assertions.

## 5. External owner trust-anchor requirement

The local code pin is proposal integrity, not an independent trust boundary.
Concurrent replacement of code and policy cannot be proven safe by local code.
Default invocation blocks publication with exit3 OWNER_EXCEPTION_APPROVAL_PENDING.
`--local-proposal` may return0 only for technical conformance and reports the same
pending owner status. No approved external anchor has been provided or created.
Ruslan must independently pin/execute reviewed code outside mutable task scope,
pin the policy and final manifest digests in protected R03/CI/config, and approve
the exception separately. Exact handoff is in owner-handoff.md. Root CI untouched.

## 6. Clean checkout reproduction

Separate Git root under a different path, source objects through read-only
alternates, copied index, actual `git checkout-index --all --force` using real
attributes. No source index/object/ref mutation during probes and no commit.
`core.autocrlf=false`, true and input: all PASS technical proposal conformance.
Working LF→CRLF on a normal text report also PASS; raw bytes remain strict.
Git tree representation via `write-tree`/`--ref`: PASS, tree OID is not a commit.
Historical workspace hashes are observations only; they do not constrain a new
normalized checkout. Cross-OS execution NOT RUN; actual probes used Windows.

## 7. Git attributes and EOL policy

Root and V02-local .gitattributes are unchanged. Raw73 stay -text and are checked
byte-for-byte against pinned blobs. Other current files use text=auto/eol=lf and
CRLF→LF equivalence. Index/tree and working attributes must agree. No diff or
whitespace suppression is permitted. Frozen original CRLF blobs stay pinned by
raw Git SHA256; normalized working representation does not rewrite those blobs.

## 8. 73→40 exception reconciliation

Fresh full staged Git check independently produced40 distinct diagnostic paths,
not a filtered result derived from the old list. Each offending line was checked
for a CR suffix and absence of trailing space/tab before CR. The remaining33
paths have0 diagnostics; all remain raw/hash-pinned but are no longer excluded.
Intake retains old73, full new40 and exact removed33; policy gives per-path raw
reason, blob OID/SHA256/size and allowed ordinary/cr-at-eol lines and reasons.
No active code/tests, mutable report or current manifest is exempt.

## 9. Fresh negative probes

15 unit probes PASS/0skips.19 Git/scenario cases produced expected outcomes:
five checkout/normalization/tree positives; default gate exit3; policy additions,
removal/hash changes exit1 even after manifest rebinding; raw working/staged
mutations exit1; added/removed files exit1; OID/size/attribute errors exit1;
new non-exempt whitespace exit1. One case is explicitly a synthetic external
before-execution pin simulation for joint verifier/policy substitution.
It does not prove deployed independent protection. These are owner-executed
fresh probes, not a new independent auditor verdict. Actual argv/exits/errors,
unit output and log hashes are retained in probe-results.json/checkout-results.json.

## 10. Full and scoped Git whitespace checks

| Check | Before | Current proposal |
| --- | --- | --- |
| Full ordinary | FAIL/2,3887 diagnostics on40 paths | FAIL/2,3887 on40 |
| Full cr-at-eol | FAIL/2,6 diagnostics on3 paths | FAIL/2,6 on3 |
| Scoped ordinary | PASS/0 outside73 | PASS/0 outside40 |
| Scoped cr-at-eol | PASS/0 outside73 | PASS/0 outside40 |

No full FAIL is renamed PASS. Diagnostic line/reason sets are exactly pinned.
Unknown path, extra/missing diagnostic or new whitespace outside40 fails.

## 11. Current publication manifest

publication-manifest-v2.json binds138 canonical Git-blob entries plus self,
139 total files. Every OID, raw blob SHA256, raw size, mode, attributes and path
is checked. Workspace SHA256/size are separately labelled observations, not a
mandatory Windows representation. Manifest self is compared with canonical
working bytes; independent approved manifest digest must be pinned externally
to avoid circular self-hashing. No implementation commit SHA is invented.

## 12. Historical byte preservation

All previous128 working bytes and Git blobs remain identical. All47 initial
archive files, two original negative-audit copies, raw24 current command logs
and frozen evidence stay unchanged. Historical manifests are never refreshed.
New source-imports.json preserves the original publication audit and positive
runtime report/snapshot losslessly as base64 plus escaped verbatim UTF-8, with
source path, size and SHA256; decoding yields exact original bytes. This avoids
introducing new raw CRLF copies requiring additional whitespace exceptions.
It does not normalize original data or hide existing Git diagnostic streams.

Publication audit original SHA256:
`839e327ce53021596084a962fbf6b17bb86b0b7c40f70eb967d6760413ee53dd`.
Positive runtime audit original SHA256:
`105057ee4ab4380b728a997d56781f278b11b4e4986e9efd443ef01472e16b5c`.
Positive123-file snapshot SHA256:
`bd3d12753513ccb2ba0c8771b7c28dd75d58db0e8baa62f193fc6fdcde56082a`.

## 13. F01/F02 runtime unchanged verification

All28 active production/source/test files match positive independent re-audit
SHA256, sizes, working bytes and indexed bytes. `releases.py`:
`26b11598b287ab063273e3ffe393fbd40da34be1cbc00fdb005125a8439853b4`;
`app.py`: `1228cb796b594852cc80c2427766c8f0627c2d5fc8a9fb5e18022fb6ceb718e7`.
That independent report explicitly closes F01 and F02, blocking findings0 and
READY FOR PUBLICATION for its runtime snapshot. This provenance resolves the
stale PENDING runtime labels by an additive record, without rewriting history.
Runtime86/V0134/backend/PG/verify_repo tests NOT RERUN this evidence-only round.
Their independent historical PASS are not claimed as new execution.60 frozen
baseline blobs are checked unchanged; no V01/frontend/root ownership changes.

## 14. Required Ruslan decision

Approve/reject the exact residual40-path whitespace exception and deploy an
independently pinned R03/CI checker/policy/manifest anchor. The anchor must be
outside candidate checkout with a separately trusted digest; an adjacent mutable
JSON or author report cannot approve itself. Human Task Approval is separate.
No message or approval on Ruslan's behalf was created. No root workflow changed.

## 15. Outstanding P1/P2/P3

P01: local mutation negatives pass; external owner enforcement/approval pending.
P02: actual clean-checkout/code/attribute/blob portability probes pass; cross-OS
and future real published commit/candidate CI remain NOT VERIFIED.
P03:40 exceptions independently derived;33 removed from exemption, bytes preserved.
Stale provenance P3 resolved by additive positive-audit record. Final independent
closure of publication findings is PENDING; no P1 finding is asserted by this author.
V03/V04/I02/I03/V05 integration, production/performance and deployed root gate
remain NOT VERIFIED. A local self-check cannot close the human/independent gates.

## 16. Recommendation

**READY FOR INDEPENDENT RE-AUDIT; OWNER EXCEPTION APPROVAL PENDING.**
Not Task Approval, not publication success, not permission to commit/push/PR.
Current v2 entry point (v1 is historical rejected proposal evidence):

```powershell
python docs/acceptance/MS7-MIG-V02/publication-byte-audit/round2/verify_publication_v2.py --local-proposal
```

Without --local-proposal and without external approval the gate returns3.
Final document/index binding was followed by actual read-only conformance on
the final index and final clean export: both proposal checks exit0, default owner
gate exit3; final receipts are in verification.json. Exact final results are exposed without fabricating
an implementation commit or an approved waiver.

Final staged139 / unstaged0 / existing baseline changes0. Staged-byte signature
inspection found no secrets; dedicated scanner NOT RUN. No actual independent
Round2 approval or cross-OS/CI execution is claimed.
