# MS7-MIG-V02 — Approved I02 handoff follow-up

Parent candidate: `76d8eac6387a5fde5432a0e8130a881cb6d7ba82`; original tree `dbad1e853dff354c5d3255755afb5cc32e0ad279`.
Owner Vladimir; reviewer Ruslan; renderer consumer Ilya. Authority: user supplied **Implement Approved I02 Consumer Handoff Fixes**, relaying the approved scope and agreed context on 2026-10-15. No commit/push/PR/merge/rebase permission.

Only five approved tracked files changed. ReleaseStore now requires the exact HOME slug/page_id/status200/canonical-root alias. Existing duplicate/reference checks and prohibition of extra HOME aliases remain. A release without HOME remains valid. Invalid active release fails503, including when a previous valid edition is retained.

Release.renderer_context provides pinned_release{release_id,manifest_digest} for every public HTML page; karta-sajta additionally receives catalogue_full{grades,subjects,sections,topics} plus the unchanged seven filtered fields. All context rows are deep-copied. There is no second descriptor/database catalogue read, new public DTO/endpoint, or canonical change. Python int64 values stay exact Python integers; Node/JS lossless bridge representation still requires consumer-boundary agreement. HTML renderer remains Ilya's responsibility.

Plan executed: regressions first, old HOME behavior reproduced with valid recomputed digests; minimal implementation; real SQLite/PG HTTP, contract/baseline/runtime verification; byte/scope/preservation checks. Before fix, two regressions failed with seven assertions/subtests (loader accepted missing alias; HTTP returned200/301). Final V02 runs pass108 tests, including47 PostgreSQL and22 executions of15 new methods, with zero skips. R1→R2 switches are exercised before context construction and verified per request; corrupt activeR2 cannot fall back to retained validR1.

| Verification | Actual result |
| --- | --- |
| V02 unit/SQLite/PG16/F01/F02 | PASS108,0skips;47PG |
| V01 unchanged Linux suites | PASS34,0skips |
| R02 migration contracts | PASS63,0skips |
| R02A / R03A | PASS30 / PASS41,0skips |
| Fresh disposable PG smoke | PASS |
| verify_repo | PASS8/8; nested Django109, R03 contract18, Harness73 |
| Full Content + changed loader/context | PASS279pages/263topics; read-only SQL; no activation |
| Target runtime without Django | PASS actual localhost HTTP smoke8routes; correct HTML503 when renderer absent |
| Test and runtime package dependencies | PASS; runtime pip invoked using --python |
| Worktree and cached whitespace, ordinary/cr-at-eol | PASS0,0,0,0 |
| Protected tracked files | All1818 unchanged; source index/HEAD/original candidate tree unchanged |

See verification.json, test-inventory.json, changed-bytes.json, source-diff.json, preservation.json and whitespace.json. Raw stdout/stderr and baseline combined logs are retained losslessly as base64 in raw-command-receipts.json, with exact SHA256 and helper sources for reproduction. Base64 avoids modifying CRLF/CRCRLF capture bytes or introducing whitespace exceptions. Historical manifests/policy/40-path exceptions/raw evidence are untouched. The old v3 verifier has not been repinned to accept new bytes.

Resolved tooling attempts are preserved honestly: sandbox Windows socketpair blocked HTTP startup, fixed by running authorized tests outside sandbox; the first smoke helper lacked the repository import path, corrected only in var; runtime venv has no pip, so its successful dependency check used pip --python. These are not hidden as passing invocations.

Disposable tests used only reserved localhost15441/55441 PG16 and new marked UUID databases. Baseline/runtime artifacts are retained in var for review. No production data or publisher activation was used.

Recommendation: READY FOR INDEPENDENT REVIEW of the uncommitted working tree. NOT VERIFIED: I02 HTML/no-JS/SSG/browser; lossless JS consumer bridge; production activation/cutover; new SHA R03/Task CI/Task Approval. Publication needs separate user instruction and new owner approval; existing candidate approval is not transferred.
