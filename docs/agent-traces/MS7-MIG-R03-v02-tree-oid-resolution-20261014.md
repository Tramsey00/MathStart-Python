# TRACE MS7-MIG-R03: V02 tree OID transcription resolution

- Date:2026-10-14 Europe/Moscow; owner Руслан / Tramsey00.
- PR49; Issue30, related35; starting R03 SHA f73f2d5a97e60e107de2bab87968ea93cfd25bd1.
- Current accepted input0c03197e23f69a233c0fcf8bdffa336feca20b92 and immutable
  MIG_BASE60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7 unchanged after fetch.
- Gate NOT_READY, R03 INCOMPLETE. Tree transcription blocker resolved by user.

## Request and sources

User states correct tree dbad1e853dff354c5d3255755afb5cc32e0ad279 remains the existing
R03/auditor pin; new inventory.json/REPORT.md expected fields contain a typo.
User permits Владимир to resume unchanged snapshot packaging. After archive
receipt verify real blobs/metadata/tree and continue gate; until then NOT_READY.
Read both source documents, prior published intake/bindings/receipts and current
verification skill/plan. Existing mandatory repository context and ADR-0006 remain
applicable. Available worktrees and existing source files were preserved.

## Observable verification

Read-only Git ls-tree at actual BASE1672 entries. A new standalone R03 checker
encodes Git trees independently and validates its encoder against actual Git BASE
tree1ff96bde5c938b1d00159e9ee1349f5db1f44d9a. Adding151 inventory declarations gives
1823 paths and correct pinned tree dbad1e853dff354c5d3255755afb5cc32e0ad279.
No Git object/index/ref writes. Inventory blob OIDs are declarations; missing
source blob contents are not independently proven by tree hashing.

Checked four nonbaseline control tuples against previous five-input bindings;
BASE root .gitattributes remains previously verified. All40 Appendix B exception
SHA256/OID/size tuples match inventory and are a subset of73 raw declarations.
Actual bytes of three previously received documents match their inventory blob
SHA256/SHA1 OID/size. Normal78/raw73 profiles and20 declared normal CRLF/LF
working differences are consistent; actual snapshot attributes still NOT_RUN.

Inventory-only negative controls (changed OID, Git mode, duplicate path, unknown
full attribute, raw working hash) each rejected. These are not substantial
publication-v3 negative evidence. New checker imports only stdlib, invokes Git
read commands with timeout and never executes candidate code. No live product
runtime/LLM/database/frontend or existing root CI tests were rerun.

Preserved the two new documents byte-for-byte in a ZIP and retained their wrong
expected OIDs unchanged. Document reference archive is clearly distinguished from
missing151-file snapshot. Updated current intake/plan/handoff and added resolution
packet, inventory tree receipt, document crosscheck receipt and this trace.
Source imports are diagnostic evidence, not an approval artifact or regenerated
candidate trust pins. No V02-owned file or existing evidence changed.

| Check | Result |
| --- | --- |
| Actual BASE Git tree vs independent encoder | PASS |
| BASE +151 declared entries vs previously pinned tree | PASS_INVENTORY_ONLY |
| Four control tuples,40 exceptions,73 declared raw profiles | PASS_DOCUMENTARY |
| Three received document bytes vs inventory SHA/OID/size | PASS_DOCUMENT_BLOBS_ONLY |
| Five inventory-checker negative controls | EXPECTED_REJECTION |
| New reference archive round-trip / JSON / links / scoped diff whitespace | PASS before publication |
| Actual151 archive/blobs/metadata/tree reconstruction | NOT_RUN_ARCHIVE_MISSING |
| Trusted v3/owner anchor, substantive gate negatives, Linux CI | NOT_RUN_ARCHIVE_MISSING |

Tools: Python3.12.10, Git2.47.0.windows.1. Wrong expected transcription is an
externally supplied document error resolved by explicit user instruction and
unchanged existing trust pin. No source normalization, silent repin, policy
reapproval, synthetic anchor, V02 Task Approval, merge or Issue closure.

Next: convey correct unchanged pin to Владимир for packaging, receive immutable
archive, perform actual source reconciliation, implement/review independent R03
gate and retain negative/Linux evidence. Whole R03 remains INCOMPLETE.

Correct unchanged pin, independent inventory result and user's permission to resume
packaging were sent to Владимир under continuing source-handoff authorization:
[PR49 comment6171700860](https://github.com/Tramsey00/MathStart-Python/pull/49#issuecomment-6171700860).
This conveys packaging permission only; no source snapshot reply or Task Approval
is claimed.
