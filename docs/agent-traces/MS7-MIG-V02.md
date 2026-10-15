# MS7-MIG-V02 agent trace

- Owner Vladimir; Reviewer/Task Approver Ruslan; Issue35; MIG-G1 pending.
- Surface bootstrap Codex, no subagents/live Product LLM.
- Input/base/current HEAD/merge-base0c03197e23f69a233c0fcf8bdffa336feca20b92;
  branch ms7-mig-v02-content, initial clean. MIG_BASE_SHA60b341f historical.
- Human status PENDING; result uncommitted/PENDING_PUBLICATION.

## Task and inputs

User authorizes complete V02 implementation only, no commit/push/PR/merge.
Earlier read-only intake stopped for missing114-page v7.1. User then supplied
v7.1 SECTION20 and migration v1.1 PDFs; actual hashes/readable page counts checked.
Required source hash matches e477bf8c...acd; no older G0 edition substituted.
Repository source recovery follows AGENTS/PRODUCT/ARCHITECTURE/ADR0001/0006,
R01 inventories, accepted R02/R02A and V01 foundation, real Django code/tests.
Concrete plan shown before code and recorded in active/MS7-MIG-V02.md.

## Observable actions / files

Created V02 content read/projection/release services, staff guards/reads/observer,
strict HTTP factory/parser/signer/runtime, scoped dependency locks and tests.
No existing file modifications, no DDL/model replacement, no shared CI/registry edits.
Exact list/purpose/hash: docs/acceptance/MS7-MIG-V02/files.md/workspace-manifest.json.
Prepared report, acceptance draft, frozen/ownership record, §17 index and test matrix.

## Incidents and corrections

| Observation | Disposition |
| --- | --- |
| Initial Python venv ensurepip denied Windows sandbox temp path | Used task-local var temp; installed pinned deps in isolated env |
| Sandbox network/Docker pipe denied; Docker CLI launcher registry missing | Authorized tool escalation; launched installed Desktop hidden, existing containers untouched |
| Windows excluded55351–55450 blocks host55441 | New disposable PG on15441/internal55441; V01 runs in separate network-sharing Python container |
| New V02 PG names rejected by V01 fresh guard | Preserve V01 prefix/marker for newly owned fixture DBs; no guard/migration edits |
| Initial fixture omitted executemany superuser column, and SQLite loses timestamp TZ | Correct fixture columns and explicit SQLite compatibility timestamp handling |
| Native Django oracle found bool-keyset503 and MediaAsset multi-sort mismatch | Correct SQL comparator/default-queryset distinction; full oracle passes |
| One negative test expected redundant permission assignment to change effective scope | Added separate positive redundant-assignment and negative actual-revocation tests |
| Quoted search required native embedded quote/escape semantics | Independent tokenizer parity plus real admin search checks |
| Automatic permission review timed out for parity command | One permitted retry executed successfully; no unsafe conclusion inferred |

## Verification and provenance

Actual commands/logs/exit results in verification.json; named test matrix in test-matrix.json.
Final V0241PASS/0skips (PG17); V0134PASS/0skips including23PG;
R0263PASS; full disposable Django fresh smoke PASS; verify_repo8/8 PASS
(Django109/R0318/Harness73); frozen R02A30/R03A41 PASS.
Full target read projection279pages/263topics matches Django SEO/catalogue and uses
real source file hashes with READ ONLY SQL. No activation/asset-family/browser claim.
Test/runtime pip check, runtime import/factory with Django absent, compileall and
git diff --check pass. Ruff/mypy/formatter NOT CONFIGURED, not reportedPASS.
Windows Python3.12.10; V01 container Python3.12.15; PG16.15; Docker29.8.0/Compose5.5.1.

All DB writes were explicit disposable fixture/smoke preparation; V02 GET SELECT-only.
Production/working DB untouched. Baseline runtime/early failed setup DBs retained;
successful UUID test DBs cleaned only by their owning fixtures. No broad cleanup.
HEAD never becomes an implementation SHA; current file hashes bind uncommitted work.
No old report/approval/pin refreshed, no remote action performed.

## Remaining scope boundaries / human gate

Default V03 identity/CSRF, I02/V05 HTML renderer and V04 edition/release producers are
fail-closed. Tests prove V02 guards and contracts with marked synthetic adapters;
they do not prove real session/SSG/activation/browser deployment. Handoffs in report17.
Independent Ruslan approval, future publication binding/current CI and downstream
integration remain pending. V02 backend submitted for independent review;
overall status **INCOMPLETE pending human/publication/integration gates**, not ACCEPTED.

## F01/F02 remediation — 2026-10-13 Moscow

User authorized scoped remediation of original independent **CHANGES REQUIRED**.
Verified branch/base HEAD, all47 audited files and empty tracked differences.
Preserved original47 bytes and external audit/source snapshot before edits.
Two real ASGI probes reproduced F01 503vs200 and F02 404vs301 before fixing.
Patched only runtime shared identity comparison and eligible public404 fallback;
added45 named regressions and extended the real rollback-only Django comparator.
Final V0286/0skips includes all byte-unchanged original41. V0134 (PG23),
R0263/R02A30/R03A41, disposable PG fresh smoke, Content279pages/263topics,
verify_repo8/8, normal runtime without Django, pip checks, compileall and
tracked/frozen ownership checks PASS. Eight Django/ASGI status+Location pairs match.
409 is explicitly fault-injected fallback precedence coverage. Disabled OpenAPI
was initially used by an ancillary route-count probe; corrected the probe to
the actual32-operation registry without changing application code.
Exact logs/tests/hashes in remediation-f01-f02/; run `MS7-MIG-V02-F01-F02-f5cac30e92044cb99c11b0907b931fa1`.
Recomputed current manifest; historical47 archive/audit pins untouched.
No commit/push/PR/merge/reset/clean/rebase. tested_implementation_sha=null;
PENDING_PUBLICATION. Owner recommendation READY FOR INDEPENDENT RE-AUDIT;
positive independent review and human acceptance PENDING. Prior initial
readiness statement does not override the preserved negative audit.
