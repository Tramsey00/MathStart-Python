# V02 transport tree OID resolution — 2026-10-14

**Tree transcription discrepancy: RESOLVED. Publication gate: NOT_READY. R03: INCOMPLETE.**

User confirms the pre-existing correct tree pin
`dbad1e853dff354c5d3255755afb5cc32e0ad279`, already published in R03 intake at
`f73f2d5a97e60e107de2bab87968ea93cfd25bd1` and in the original independent auditor
report. The new transport documents mistakenly use
`dbad1e853dff354c5d325575afb5bcc32e0ad279` as their expected OID. Both are40-character
strings; the error is a transcription, not an OID-length validation failure.
The existing trusted expected pin is unchanged. No automatic candidate repin.

Read the supplied `inventory.json` and `REPORT.md`. Their exact bytes and erroneous
expected fields are preserved in an R03-owned
[two-document reference archive](v02-transport-reference-documents-20261014.zip).
This archive contains diagnostic documents, not the151-file snapshot. Measured
input SHA256:

- inventory.json: `0f3854f47309c98ec29942271119a72548a3d5c1975adbdcd24c8bd41d592476`.
- REPORT.md: `a46a269591d4640afe6d9d5238e650a1128b4c95d664a62d9b109ee19624887a`.

## Independent declared-tree reconstruction

[Reproducible R03 checker](check-v02-inventory-tree.py) reads the actual accepted
BASE tree through read-only Git and combines its1672 paths with151 unique new
inventory entries. It independently encodes hierarchical Git tree objects using
Git directory-aware byte ordering and SHA1 object headers, without storing objects,
writing an index/ref or requiring missing candidate blobs. Its encoder also
reproduces the actual Git BASE tree `1ff96bde5c938b1d00159e9ee1349f5db1f44d9a`.

All1823 declared entries yield the correct existing expected tree pin. Receipt:
[inventory tree reconciliation](v02-inventory-tree-reconciliation-20261014.json).
Reproduce from the preserved inventory archive member or the supplied local file:

```text
python -I -B docs/acceptance/MS7-MIG-R03/check-v02-inventory-tree.py --inventory "C:/Users/Tramsey/Downloads/Telegram Desktop/inventory.json"
```

The script uses the pre-existing R03 BASE/tree constants, not inventory's erroneous
`expected_tree_oid`. It checks declarations and returns PASS_DECLARED_TREE only;
it does not prove the availability or contents of151 source blobs.

## Inventory/document crosschecks

[Transport document receipt](v02-transport-document-intake-20261014.json) records:

-151 declared additions, all mode100644;78 normal and73 raw metadata profiles.
- All40 exception SHA256/OID/size tuples equal the prior auditor Appendix B;
  every exception belongs to the73 raw paths, leaving33 non-exempt raw paths.
- Four nonbaseline control tuples match previous bindings; root attributes remain
  pinned to the actual unchanged BASE blob. Five-control trust policy is preserved.
- Actual bytes of the three already received owner-handoff/bindings/report-v3
  documents also match their declared Git SHA1 blob OID/SHA256/size.
-20 declared working/blob differences have normal text=auto,eol=lf and explicit
  CRLF_TO_LF_GIT_TEXT_AUTO_EOL_LF reasons. Raw working/blob SHA256/size declarations
  remain identical. Actual working/source files still await transfer.
- Five inventory-checker mutations reject changed blob OID, mode100755, duplicate
  path, unknown effective attribute and raw working-hash drift. These are only
  inventory validator controls; required real publication-verifier negatives
  remain NOT_RUN.

The complete declared73 path list is now available. Its actual bytes/metadata and
identity against original policy still require archive verification. The old
document-intake statement that the complete list was absent is historical.

## Packaging and remaining gate

The user's permission allows Владимир to resume packaging the **unchanged** staged
snapshot. The source REPORT's STOP due to erroneous expected OID is resolved.
[Confirmed correct pin and requested archive](https://github.com/Tramsey00/MathStart-Python/pull/49#issuecomment-6171700860).
This authorizes transport packaging, not V02 publication or Task Approval.
No snapshot ZIP, implementation commit or post-publication CI is supplied here.

On archive receipt R03 must verify archive/member safety/inventory, actual151 Git
blob bytes/SHA256/OID/size/modes, applicable attributes, raw73 and40 exception
diagnostics; reconstruct actual Git index/tree on accepted BASE and compare with
the unchanged correct pin. Preserve raw full whitespace FAIL/2 and scoped results.
Then inspect/freeze real trusted v3/controls, create the concrete R03 owner anchor
and digest, implement/review external gate, execute substantial negatives and
clean Linux CI evidence. Until those checks: **NOT_READY**. Actual execution pins
remain null; policy approval already stands, Task Approval/merge remain separate.
