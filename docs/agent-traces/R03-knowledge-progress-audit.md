# TRACE R03: Knowledge Graph and Progress Contract Audit

- **Date:** 2026-09-24
- **Task ID:** R03 Knowledge Graph and Progress contract package
- **Owner:** Ruslan / MathStart team
- **Coding agent / surface:** Codex desktop
- **Related specs:** `specs/knowledge/R03-knowledge-graph.md`, `specs/progress/R03-progress-contract.md`; numerical baseline `specs/progress/BASELINE-v1.md`
- **Related exec plan:** `docs/exec-plans/active/R03-knowledge-progress-contract.md`
- **Related issue:** https://github.com/Tramsey00/MathStart-Python/issues/6
- **Related ADRs:** ADR-0001, ADR-0002; ADR-0003 Accepted
- **Contract commit:** `961403958b5816071b795a2170f080051dd1bf9f` (`feat(r03): add executable knowledge and progress contracts`)
- **PR:** [#7 — R03: Knowledge Graph and Progress contract phase](https://github.com/Tramsey00/MathStart-Python/pull/7), open
- **Human contract gate:** ACCEPTED; merge pending

## 1. Task and inputs

The user requested an audit and exec plan for the pilot Knowledge Graph and exact Progress contract, preserving R01/R02 and every existing Progress Algorithm v1 number. Read `AGENTS.md`, `PRODUCT.md`, `ARCHITECTURE.md`, accepted ADR-0001/0002, R01/R02 completed plans and traces, Progress baseline, R02 exercise spec and seven JSON fixtures, `content` models/migration/tests/bootstrap, configuration, README, and the verification skill. No implementation was requested for this phase.

## 2. Repository state

The checkout started clean on `R02-exercise-architecture` at `a45ca2c`. Local `main` was `0a5398d`. A remote query and fetch found `origin/main` at `951ad48`, merging R02 as PR #5. `HEAD` and `origin/main` have the same file tree. No Knowledge/Progress app, model, migration, fixture, or test exists. `ContentPage(page_type=topic)` is the current Topic representation.

Subsequent Git normalization fast-forwarded local `main` to `origin/main` at `951ad487f75362081e7ec53f50b2efd9c97055b1` and created `R03-knowledge-progress` from that commit. Both R03 documents remained untracked and unchanged during the branch switch. No R01/R02 commit was rewritten. A repository-wide GitHub issue search found no R03 issue, so Issue #6 was created and linked from the revised plan.

## 3. Files changed

- Added `docs/exec-plans/active/R03-knowledge-progress-contract.md`.
- Added this audit trace.
- Revised the exec plan with the 2026-09-24 human review decisions; updated this trace with observable Git/Issue and review state.
- No product code, schema, seed, baseline spec, R01/R02 artifact, dependency, or database data was changed by the audit.

## 4. Observed checks and findings

| Check | Result |
| --- | --- |
| Fresh `git ls-remote` / `git fetch origin main` | Remote `main` is `951ad48`; R02 is merged |
| `git diff --stat HEAD..origin/main` | Empty; same tree |
| Normal `.venv` Python launcher | ENVIRONMENT FAIL: references absent Python 3.10 |
| Bundled Python version | 3.12.14 |
| `scripts/verify_repo.py` via bundled Python and project packages | PASS: 6/6 checks |
| Django test suite within verification | PASS: 15 tests |
| Graph/Progress specific automated checks | NOT CONFIGURED |

The numerical baseline is recorded in `specs/progress/BASELINE-v1.md`; it leaves exact confidence/evidence-count projection, window membership, repeat streak details, rounding stage, order, and duplicate-penalty resolution open. R02 uses categorical `difficulty` strings; the R03 request adds numeric-level mapping. The plan treats these as review decisions and does not replace the baseline.

## 5. Scope and review

The planning phase produced only a revised plan and audit trace. It did not create models, migrations, services, contract specs, ADR-0003, contract fixtures/tests, C-16 draft, or runtime seed data. The semantic review approved `pilot-v1` and exact Progress rules; the later review approved the revised plan with final corrections: Owner Ruslan, backup Vladimir, W1, 12 hours, milestone R03/W1, and replay ordering by `(occurred_at, event_id, policy_version)`. The user requested an initial planning/audit commit before broader contract work. Contract review remains pending. Do not mark R03 complete or move its plan to `completed/` until accepted contracts, executable verification, and the remaining human gates are complete.

## 6. Approved contract-phase actions

The plan metadata and replay wording were corrected first. Commit `37417a1` then preserved the approved plan and this trace before the contract phase. No R01/R02 history was modified.

Created proposed ADR-0003, the Knowledge Graph and Progress specs, two pilot graph fixtures, Progress golden cases, a pure Python reference implementation, the R03 contract tests, and the C-16 draft. The pilot fixtures contain exactly 10 skills and 13 prerequisite-to-dependent edges, all weighted 1.0; `basic_arithmetic` is an external prerequisite, not a pilot node or edge reference. Updated current normative terminology and templates to the single `ProgressEvent` term, registered the contract suite in the repository verifier, and documented its command in the verification skill. The numerical `BASELINE-v1.md` and completed R01/R02 artifacts were not edited. No Django model, migration, service, runtime seed, PostgreSQL setup, or official submission was created.

## 7. Contract verification

| Check | Actual result |
| --- | --- |
| Interpreter | `C:\Users\Tramsey\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`, Python 3.12.14, with `.venv/Lib/site-packages` on `PYTHONPATH` for the existing Django dependencies |
| `python -m unittest discover -s tests -p test_r03_contract.py` | PASS: 15 tests |
| JSON fixture parsing | PASS: all 10 JSON files under `specs/` parsed |
| `python scripts/verify_repo.py` | PASS: 7/7 checks, including Django check, migration consistency (`No changes detected`), 263 lesson sources, content quality, site integrity, 15 Django tests, and 15 R03 contract tests |
| `git diff --check` | PASS: no whitespace errors; new contract files were included with Git intent-to-add |

The PowerShell verification invocation was:

```powershell
$env:PYTHONPATH=(Resolve-Path '.venv/Lib/site-packages').Path
& 'C:\Users\Tramsey\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p test_r03_contract.py
& 'C:\Users\Tramsey\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/verify_repo.py
```

Fixture parsing used that interpreter and `json.loads` on every `*.json` under `specs/`. Git intent-to-add made the nine new contract files visible to `git diff --check` without staging their content or creating a contract commit. The final diff included 18 modified/new files and no R01/R02 history, baseline, Django model, migration, or runtime seed file.

The pure Python suite checks the approved graph and Progress event semantics; the full Harness additionally checks the existing Django baseline. Neither verifies PostgreSQL, runtime Knowledge/Progress integration, or persistence. Attempt completion for the recent window must be represented by an immutable completion fact available to replay; the later Assessment persistence design must supply that fact. ADR-0003 and the contract package remain subject to human review. R03 stays active and the C-16 official submission remains a separate human gate before 2026-10-09.

## 8. Contract human-review corrections and re-verification

The human reviewer required four semantic corrections before contract approval. The Knowledge spec/reference/tests now provide deterministic `ancestors(skill_id, max_depth=2)`, traversing backward over the unchanged ten-node/thirteen-edge DAG and returning minimum-depth `(skill_code, depth)` results; `linear_parentheses` depth 1 and 2 are asserted literally. Progress now exposes the Technical Specification's six canonical `UserSkillState` fields, including `last_updated` and `reducer_version=progress-v1`; the old `last_evaluated_at` label remains only in the historical baseline transcription. The same-evidence `WRONG_ATTEMPT` plus `MISCONCEPTION_DETECTED` combination now invalidates the ProgressEvent log instead of retaining a non-projecting wrong event. Separate negative units in one attempt require distinct references and the explicit rule on both events. `completed_at` is normalized and checked for same-attempt/skill consistency, with no ordering constraint relative to `occurred_at`. Golden cases now contain all eight event kinds, and tests compare fixtures and reference behavior with independent literal inventories.

| Re-run check | Actual result |
| --- | --- |
| Interpreter | Same bundled Python 3.12.14 executable recorded above; project site-packages supplied for Django checks |
| `python -m unittest discover -s tests -p test_r03_contract.py` | PASS: 18 tests |
| JSON fixture parsing | PASS: all 10 JSON files under `specs/` parsed |
| `git diff --check` | PASS: no whitespace errors, including intent-to-add files |
| `python scripts/verify_repo.py` | PASS: 7/7 checks; Django system check, migration consistency (`No changes detected`), 263 lesson sources, content quality, site integrity, 15 Django tests, and 18 R03 contract tests |

This review round created no commit or PR. The numerical Progress v1 baseline, approved pilot nodes/edges, historical R01/R02 files, Django models/migrations/services, runtime seed and database data remain unchanged. PostgreSQL and runtime Knowledge/Progress persistence were not verified. Final contract human review remains pending; the exec plan stays active.

## 9. Final human acceptance and pre-commit verification

Final human contract gate = **ACCEPTED**. The reviewer accepted depth-2 ancestors, canonical state fields, normalized one-negative-event-per-evidence, independent completion/occurrence timing, and independent literal test expectations. ADR-0003 and both R03 specs are Accepted. The requested replay wording now names `last_updated` and `reducer_version`; no semantic or numerical change was made during this final pass. The earlier pending-review entries above record prior review stages.

Final verification used `C:\Users\Tramsey\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`, Python **3.12.14** (MSC v.1944 64 bit AMD64), with the same commands and project `PYTHONPATH` documented in section 7:

- R03 suite: **PASS, 18 tests** (standalone 0.020s; Harness invocation 0.012s).
- JSON fixture parsing: **PASS, all 10 JSON fixtures** under `specs/`.
- `git diff --check`: **PASS**, including all new files through intent-to-add.
- Full `scripts/verify_repo.py`: **PASS, 7/7 checks**. Django system check passed; migration check reported `No changes detected`; 263 lesson sources passed; content quality and site integrity passed; **15 Django tests** passed in 36.723s; **18 R03 contract tests** passed.

The accepted package is authorized for commit `feat(r03): add executable knowledge and progress contracts` and PR `R03: Knowledge Graph and Progress contract phase`, referencing Issue #6. Keep the plan in `active/` until the PR is merged into main and merge evidence is recorded. This acceptance does not claim PostgreSQL or Django Knowledge/Progress persistence verification. C-16 official submission remains a separate human gate before 2026-10-09.

## 10. PR process gate: repository CI

The process review found that PR #7 initially had no GitHub Actions workflow or CI checks. Issue #6 was updated to reflect the accepted contract, 18 passing R03 tests, open PR #7, pending merge, deferred Django persistence and separate C-16 submission gate. Added `.github/workflows/ci.yml` to run on PRs to `main` and pushes to `main`: Python 3.12, `requirements.txt`, `migrate --noinput`, `bootstrap_site`, then the complete `python scripts/verify_repo.py`. The fresh database and content bootstrap follow `README.md`; the verification skill now identifies this command as the CI gate.

Before pushing CI, a fresh local SQLite database at ignored `var/r03-ci-smoke.sqlite3` was migrated and bootstrapped successfully: 263 lessons and 29 media records were restored. The full Harness then passed **7/7 checks** on that fresh database, including 15 Django tests and 18 R03 tests. The local interpreter was the bundled Python 3.12.14 with the project's site-packages. GitHub Actions result and final merge gate remain pending; PR #7 must not be merged during this process update.
