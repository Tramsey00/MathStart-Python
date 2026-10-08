# TRACE MS7-MIG-R03: Target verification CI and Harness adapters

- Date:2026-10-09 Europe/Moscow; owner Руслан /Tramsey00
- Surface: Codex desktop bootstrap; no live Product LLM or subagents
- Issue: https://github.com/Tramsey00/MathStart-Python/issues/30
- Spec: canonical migration v1.1 §§9/17 and R03; r03-v1 adapter contract
- Plan: docs/exec-plans/active/MS7-MIG-R03.md; ADR0006
- Status: INCOMPLETE / runtime integration and independent review pending

## Intake and scope

Explicit request: execute only R03; recover repository context, compare attached
migration specification at accepted input, inspect refs/worktrees, preserve
MIG_BASE_SHA and dependencies; no other task or automatic merge.
Read repository required documents, relevant ADRs and frozen contracts, R01/R02
records, verification skill, affected scripts/Harness/tests and existing migration
ownership. Accepted input8d958ae, MIG_BASE60b341f; live remote refs confirmed.
R02 owner receipt6070829593 confirms ACCEPTED_INTEGRATION and exact merged tree.
Attached canonical Markdown byte-equal, SHA256 in intake.json. Old PDF114 pages
hash matches migration specification; migration PDF60 pages read as supporting
context. Its historical Django platform direction does not revoke ADR0006.

Main checkout8c11edad with untracked recovery/output/tmp preserved; separate R03
branch/worktree created from accepted input. R03 branch absent before creation.
Dedicated port55440 PG16 container;5432/55438/55439 untouched. Separate runtime
var/r03-runtime and disposable/test DB names in intake. No working DB writes.

## Changes

Explicit target/pure profiles and bounded checks; transitional legacy profile for
frozen ci.yml.16 target named checks,6 pure subset; no empty PASS. Target Harness
repo-baseline excludes harness; three IDs unchanged. Backend command handoff
requires reviewed existing entrypoints and nonempty/unskipped runtime receipts;
missing implementations fail. Direct psycopg read-only PG diagnostic, target
version/fresh/upgrade wrappers, nonempty unittest wrapper, exact CI provenance.
Migration workflow has pure, historical R02 and mandatory target jobs on prescribed
branches; frozen ci.yml/pins untouched. §17 six-chain index preserves history.
No domain runtime, DDL, product lock, authored content or frontend edits.

## Observed failures and corrections

- Sandbox denied Git metadata/network access; authorized Git operation executed
  through normal escalation. Temporary Harness Git tests similarly needed access.
  These environment failures were not presented as test passes.
- Test discovery initially shadowed harness with tests/harness; fixed search-path
  ordering in new wrapper without changing frozen suites.
- Windows pure dependency check found missing tzdata; added exact accepted version
  to R03 tooling subset and reran pip check successfully.
- Target inputs absent on accepted tree and live dependency Issues35/41 PLANNED.
  This is an integration blocker, not permission to implement another owner's task.

## Verification

Final observable command/results and output hashes in verification.json.

| Execution / evidence class | Result |
| --- | --- |
| Pure pip check / actual versions; no Django/DRF available | PASS, Python3.12.10 |
| Current pure suites: R03 / R02A / R03A / protocol model |18 /30 /41 /32 PASS |
| Current R03 adapters and six historical chains |21 PASS |
| Harness regression including fake dry-run/execute/status/lifecycle |73 PASS |
| Legacy pip/versions |PASS, Django5.2.16 /DRF3.18.1 |
| Legacy fresh PostgreSQL migrations/bootstrap twice/static/content |PASS exit0, PostgreSQL16.15 |
| Required `python scripts/verify_repo.py` transitional legacy |8/8 PASS; Django107/R0318/Harness73;302.44s |
| Unchanged standalone R02 on accepted-input worktree |63 PASS exit0; historical baseline only |
| Target PG read-only diagnostic / failed port |exit0 /exit1; no SQLite fallback |
| Full target registry |FAIL exit1;10 missing runtime checks of16;6 portable checks PASS |
| Target fresh/upgrade wrapper with explicit disposable guard |FAIL exit1, missing owner commands |
| Preservation / frozen pins / local document links / diff whitespace |1370/1370, R02pins24/R02Apins17,11 links/no missing, PASS |

Actual Docker client/server29.8.1, Composev5.5.1, Git2.47.0.windows.1,
pip25.0.1, jsonschema4.26.0, psycopg3.3.6. No frontend browser execution
occurred; Node/browser versions are not reported as verified. Earlier pure run
before final additions is labelled superseded; current adapter/target results
cover21 tests. Locks exactly match installed packages and pip check passes.
Available pure suites and real PG connection/failed-port diagnostic are separate
from unimplemented target fresh/upgrade/content/frontend acceptance.
Unchanged standalone R02 suite63 runs at accepted-input historical worktree;
its Django assertions are never labelled target portability. R02 protocol32
run on current tree without Django. No frozen test/pin/history weakening.

## Human gate and remaining work

No self-approval. Independent Vladimir/Ilya review required at exact final HEAD.
Missing accepted V02/I02, owner locks/runtime commands, target equivalent R02
runtime assertions, PG fresh/upgrade, frontend/build/browser proof and final CI
prevent COMPLETE/ACCEPTED_INTEGRATION. Default verification cutover remains a
reviewed R03 follow-up after owner inputs. Keep plan active, Issue30 open and
draft PR unmerged. PR and final CI linkage are external exact-commit records,
avoiding a self-referential SHA written into its own commit.
