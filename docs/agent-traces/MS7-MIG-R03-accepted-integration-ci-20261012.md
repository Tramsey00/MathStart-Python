# R03 accepted integration CI follow-up — 2026-10-12

Scope: record externally granted I01/V01 acceptance and verify their combined
input in R03 CI. No implementation expansion, merge, Issue closure or task delegation.

Verified human receipts5484114333/I01 and5484103844/V01 at their exact approved
heads; verified external merges0c03197 and4a1b8b0 and the squash-parent chain.
Baseline38157082399 SUCCESS has actual checkout0c03197. Issues34/40 are OPEN.
Retained I01 fixture-banner accepted limitation and both separate follow-ups.

Fetched live refs, reused the existing R03 worktree/PR49, and merged accepted
input0c03197 locally with no conflicts (merge6e22a906). Created a detached
integration-input checkout0c03197. Historical8d958 and immutable MIG_BASE60b341
remain separate provenance. Attached migration Markdown equals the canonical
file at0c03197 byte-for-byte (SHA256c5a554e3911bdb43db28d67fd02d26e38d50b2820e1154a272d89ecb44b1faae).

Changed only R03 CI adapters/workflows/tests and current records. Added strict
human-receipt/merge-chain/source/tree/ref validation; both owner suites now use
the same pinned integration checkout. Explicit event-SHA root checkout fixes
the dynamic merge-ref race without weakening `ci_provenance.py`.

Local Python3.12.14 checks: frontend adapter8 PASS; PostgreSQL adapter11 PASS;
shared accepted-input negatives8 PASS. First PostgreSQL adapter invocation
encountered Windows sandbox temporary-directory access failure; rerun with
workspace TEMP/TMP passed unchanged. Source verification1662 files,84 captures,
106 backend/history files PASS; historical workflow/source pins preserved.
One initial overly broad doc diff rejected R03-added dated receipts; scope was
corrected to permit additional records while still rejecting any alteration or
deletion of accepted evidence and all implementation changes.

Joint frontend/PostgreSQL execution and raw receipts: SUCCESS;
see [current handoff](../acceptance/MS7-MIG-R03/accepted-integration-ci-20261012.md).
R03 remains INCOMPLETE pending task-card dependencies, reviewed runtime command
handoff/full target evidence, default cutover and independent Task Approval.

Initial local pure profile returned FAIL because the bundled interpreter has no
jsonschema. Classification: unconfigured local tooling, not a domain regression.
A fresh locked tooling venv and CI pure job will provide the configured checks.

Configured local verification: fresh9-package verification.lock venv, pip check
PASS, pure6/6 PASS. CI pure6/6 and baseline8/8 + unchanged historical R02 suite63
PASS in run38250865462; wider target FAILURE at reviewed command prerequisite,
following stages NOT_RUN. Classification: outstanding owner runtime handoff.

Dedicated frontend38250865546 and PostgreSQL38250865494 SUCCESS, both actual
input0c03197. Workflow checkoutb8cca88 (parents0c03197/8ee33ac) differs from approved
I01 head150279e6 and V01 head393d988; recorded separately. Frontend112+5/all10
commands PASS. PG34/23,0 skips,fresh2/ABC,40 subtests,57 DB cleanup,22-package
exact lock PASS. Actual Python3.12.15/PG16.15; tmpfs stop0 and automatic removal
SUCCESS. Independently verified24 raw artifact files, archive and per-file SHA256,
Git blob/history before-after integrity and absence of credential patterns.

Raw archives downloaded after one transient network EOF; retry succeeded and
archive digests matched GitHub. Frozen ci.yml unchanged. Historical successful
candidate runs and late strict-provenance FAILURE/NOT_RUN kept separately.
Final publication contains records only; its Git head must not be reported as the
workflow checkout of the earlier joint evidence runs. R03 stays INCOMPLETE.
