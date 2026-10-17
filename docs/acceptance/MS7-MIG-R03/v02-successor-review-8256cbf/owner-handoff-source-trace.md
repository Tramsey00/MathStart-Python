# MS7-MIG-V02 — P2/P3 Remediation Report

Local recommendation: **READY FOR INDEPENDENT RE-AUDIT**. This record is not an
independent approval, an R03 gate result, Task CI, or final Task Approval.

## Authority and source snapshot

User request: **Fix Independent Audit P2/P3 Before Follow-up Commit**, attachment
`04fa1464-37cf-494d-90c6-e6e80de09248`, 2026-10-15. Owner Vladimir; reviewer Ruslan;
I02 renderer consumer Ilya. No commit, push, merge, rebase or PR update authorized.

Branch `ms7-mig-v02-content`; unchanged HEAD
`76d8eac6387a5fde5432a0e8130a881cb6d7ba82`; unchanged candidate tree
`dbad1e853dff354c5d3255755afb5cc32e0ad279`.

Before editing, intake.json retained exact paths and SHA256 for 1850 files:
1823 tracked files, including five already modified by the approved HOME/context
follow-up, and 27 untracked prior evidence records. It also retained the complete
prior diff as base64, SHA256
`51659b0eec5269f05c8320d96423576784bc6bdc16db7d16a9b0b149bdf89a7c`.
The source index byte SHA256 remains
`f447b1c3be057553da5f591ebcfccf1ac4ea15f9f27cb3e02d96a5893c03c791`;
there are zero staged changes.

The original Independent-Audit-Report.md remains unchanged, verdict
**CHANGES REQUIRED**, SHA256
`76d7596a411de9828b86437a7666b116144126296cb719a17546e2e9160dce27`.
Its exact bytes are retained in intake.json as base64. Local remediation does not
rewrite that verdict or any prior approval record.

## P2: mutable page boundary

The HTTP adapter passed the page object returned by Release.page_path directly
to the renderer. That object belongs to validated Release.pages. Context was
already deeply copied; the page and its nested SEO/source/asset values were not.

The production change in this round is an import of copy.deepcopy and the call
`render_page(deepcopy(page), context, public_origin + page['seo']['canonical_path'])`.
The README documents both isolated arguments. No route, public DTO, canonical
calculation, callback signature, active-descriptor selection or database query
was added. Existing release/context/HOME implementation is byte-identical to intake.

Three new ASGI regressions failed before this fix (3 FAIL, exit1), then passed
(3 PASS, exit0). Tests deliberately reuse the exact same validated Release object
across requests, so fresh allocations by the loader cannot hide shared references.
They cover top-level title mutation; nested SEO and source dictionaries; mutation
and append/clear of asset lists; simultaneous page/context/pinned identity mutation;
the next API and HTML request; original canonical URL; safe503 without exception
details after a mutating renderer throws; and unchanged Release.pages/Release.index.
The complete suite also reruns the existing R1-to-R2 switch test: each request has
one selection and coherent page/context/pinned identity; invalid R2 fails503 with
no fallback to retained R1. HOME alias positive/negative, no-HOME, int64, F01/F02,
asset, authorization and HTTP security regressions remain enabled.

## P3: exact byte reconciliation and new guard

The two helper sources are ignored var files, with no staged representation.
The prior writer hashes read_bytes(), stores raw.decode() (UTF-8 by default), and
writes UTF-8 JSON. Explicit UTF-8 decoding of the original raw-command-receipts.json
produces source_utf8 values whose UTF-8 bytes match the physical files and declared
SHA256. The original JSON SHA256 is
`0d871440f0b35320fdb7dc249afba18a35a155ec9474954f8675db78b6a4eea6`;
the independently copied JSON has the same exact bytes.

| Helper under var/ | Raw bytes | LF / CR / BOM | Correct raw and UTF-8 SHA256 |
| --- | ---: | --- | --- |
| i02_handoff_full_content.py | 4364 | 71 / 0 / absent | c6e5840c9f6a7a7f4b99746126922c9199d523eb95a0399f4689943ae9546704 |
| i02_handoff_finalize.py | 18714 | 261 / 0 / absent | dedc2f1e73d6312af4a6bf4a6fe61a0fc2216c5fbebf0a0388ddd7cc8ccff2c5 |

Both reported bad digests reproduce exactly when the SAME JSON bytes are decoded
as CP1251 before parsing, then the resulting source text is encoded as UTF-8:

- full_content: `3a10fc80fe13e3965931f11d2e168f4352bd96e89504cdf3f6cb60b9af8aa28d`.
- finalize: `0d45e3ef0ba0654f0e16e8e7e715fe7bfc66c1fc433c6fd26d639472d88b69d3`.

Re-encoding that misread text as CP1251 recovers the original bytes. There is no
BOM, CRLF conversion or double UTF-8 encoding in these physical sources. The
available report does not establish which auditor command selected CP1251; the
exact hash reproduction establishes the decoding mechanism, not that command.
The earlier evidence seal checked raw command-output base64, but did not
independently verify helper source_utf8 round trips. That guard gap is corrected.

New helper-sources-v2.json uses ASCII-escaped JSON transported as UTF-8/LF, explicit
source_encoding, exact raw base64, its own raw digest/size, separate UTF-8 text
digest and byte profile. No normalization is performed. verify_helper_sources.py
checks all five original source paths against intake pins, strict UTF-8 and base64,
raw/text byte equality and two physical reads of every original source. Its actual
CLI run passes5sources/10reads, exit0. Four regressions reject corrupted text,
jointly rehashed text/raw data, wrong encoding/base64/BOM profile, reproduced CP1251
mojibake and independently corrupted physical source bytes. Tests reconstruct
temporary fixtures from retained raw bytes, so ignored local var scripts are not
required to run them on a clean source copy. The CLI receipt verifies original
physical files separately. No historical hash or helper file was changed.

## Actual verification after remediation

| Check | PASS | FAIL | SKIP | Exit |
| --- | ---: | ---: | ---: | ---: |
| P2 original behavior, expected negative reproduction | 0 | 3 | 0 | 1 |
| P2 fixed ASGI regressions | 3 | 0 | 0 | 0 |
| P3 final regressions | 4 | 0 | 0 | 0 |
| V02 final, SQLite plus disposable PostgreSQL16 | 118 | 0 | 0 | 0 |
| V02 PostgreSQL subset, included above | 50 | 0 | 0 | 0 |
| V01 unchanged Linux suites | 34 | 0 | 0 | 0 |
| R02 / R02A / R03A | 63 / 30 / 41 | 0 | 0 | 0 |
| verify_repo | 8 checks | 0 | 0 | 0 |
| Nested Django / R03 contract / Harness | 109 / 18 / 73 | 0 | 0 | 0 |
| Fresh disposable PostgreSQL smoke | PASS | 0 | 0 | 0 |
| Full Content projection and changed loader | 279 pages / 263 topics | 0 | 0 | 0 |
| Actual localhost runtime without installed/imported Django | 8 HTTP cases | 0 | 0 | 0 |
| Original-source byte guard | 5 sources / 10 physical reads | 0 | 0 | 0 |
| Test/runtime dependency checks | PASS / PASS | 0 | 0 | 0 |
| Worktree ordinary / cr-at-eol whitespace | PASS / PASS | 0 | 0 | 0 / 0 |
| Cached ordinary / cr-at-eol whitespace | PASS / PASS | 0 | 0 | 0 / 0 |

Seven new methods execute ten times in the full V02 run (three P2 methods on
SQLite and PG; four P3 methods). See test-inventory.json for every named execution.
PostgreSQL tests use only reserved localhost15441/55441 and new marked UUID test
databases. Full Content SQL is read-only; no publisher activation occurred.
The runtime has no HTML renderer and correctly returns503 for HTML requests;
this smoke does not establish an implemented I02 HTML renderer.

All attempts are retained honestly. Three expected pre-fix failures are separate
from one transient task-introduced IndentationError (no tests executed, corrected
before successful runs). An additional run without the PG environment had68PASS
and50SKIP; the final explicitly configured run has118PASS/0SKIP. Windows sandbox
blocks asyncio socketpair; real ASGI/network runs used authorized unsandboxed
execution. These intermediate results are not relabelled as passing coverage.

Raw stdout/stderr and baseline combined logs are retained byte-for-byte in
raw-command-receipts.json as base64 with SHA256, including CRLF/CRCRLF capture
bytes. Only this round's redundant decoded log copies were removed after exact
base64 comparison. Old27 evidence files and all historical raw files are intact.
New evidence uses explicit UTF-8/LF; no new whitespace exceptions are introduced.
New-file no-index checks return1 for file addition with empty diagnostics; these
are not called PASS/0. Original publication FAIL/2 remains historical evidence.

## Scope, preservation and audit handoff

All1818 tracked files outside the five approved paths and all27 prior evidence
records are unchanged (1845 protected files checked). Five original ignored
helpers and the original negative independent report also retain exact hashes.
Frozen R02/R02A/R03A, V01/Alembic, frontend, Django/V04, root CI/R03, historical
manifests,40-path policy and approval pins remain unchanged. Known secret-signature
scan includes the five changed files, new evidence, retained source bytes, decoded
diffs and raw receipts; synthetic test credentials are explicitly test fixtures.
See preservation.json, changed-bytes.json and secrets-scan.json for exact scope.

The five modified tracked paths remain backend/content/releases.py,
backend/infrastructure/http/app.py, backend/tests/v02/test_unit.py,
backend/tests/v02/test_http.py and backend/infrastructure/http/README.md. Since
this round's intake only app.py, README and the two test files changed. All new
versioned evidence is confined to this directory. Exact path/size/hash inventories
are in intake.json (before) and evidence-inventory.json (after); ignored local
verification drivers are retained in reproduction-tools.json.

For the independent read-only re-audit, compare the current five files against
changed-bytes.json; verify every inventory SHA and the protected intake1850;
decode JSON explicitly as UTF-8; inspect the preserved original negative audit;
rerun the byte guard and named P2/P3 tests in an isolated writable test copy. Raw
helpers can be reconstructed there from helper-sources-v2.json base64 without
normalization. Keep the original source index/worktree and all history read-only.
Review the CP1251 counter-reproduction as well as the page mutation/failure probes.
Full reruns need the guarded disposable PG endpoint; the unchanged baseline helper
contains the commands for fresh smoke, verify_repo and R02A/R03A. Reproduction
drivers that write receipts must run in a fresh evidence directory/test copy;
the finalizer deliberately refuses to overwrite a completed verification record.

Remaining P1: none identified in the supplied audit. P2 and P3 are locally fixed;
independent confirmation is pending. NOT VERIFIED: subsequent independent audit;
I02 HTML/no-JS/SSG/browser; lossless int64-to-JS consumer agreement; production
activation/cutover; new SHA R03 gate, Task CI and final Task Approval.

P2 mutable page: **LOCALLY_FIXED**.

P3 source_utf8: **LOCALLY_FIXED** (decoding reconciliation and strict byte guard).

HEAD: **unchanged**.

Commit/push: **NOT PERFORMED**. No merge, rebase or PR update performed.
