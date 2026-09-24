# TRACE R02: Exercise Architecture

- **Date:** 2026-09-24
- **Task ID:** R02
- **Owner:** Ruslan
- **Coding agent / surface:** Codex desktop
- **Related issue:** https://github.com/Tramsey00/MathStart-Python/issues/4
- **Related spec:** `specs/exercises/R02-exercise-architecture.md`
- **Related exec plan:** `docs/exec-plans/completed/R02-exercise-architecture.md`
- **Related ADR:** `docs/adr/ADR-0002-exercise-contract-architecture.md`
- **PR / commit:** none; no commit, push, or merge performed
- **Human review status:** Accepted

---

## 1. Task

Audit and complete the R02 exercise architecture contracts for parallel backend
and frontend work without implementing product code, persistence, APIs,
validators, or UI.

---

## 2. Inputs used

- `AGENTS.md`
- `PRODUCT.md`
- `ARCHITECTURE.md`
- `docs/adr/ADR-0001-preserve-django.md`
- `docs/adr/ADR-0002-exercise-contract-architecture.md`
- `specs/exercises/R02-exercise-architecture.md`
- `specs/progress/BASELINE-v1.md`
- `docs/exec-plans/completed/R02-exercise-architecture.md`
- `skills/verification/SKILL.md`
- `scripts/verify_repo.py`
- `content/models.py`
- `content/services/lesson_components.py`
- `content/services/lesson_sources.py`
- `templates/lessons/components/exercise.html`
- representative authored exercise markup under `curriculum/`
- R02 task prompt and repository scope restrictions

---

## 3. Initial repository state

```text
Branch: R02-exercise-architecture
Start commit: 0a5398d6d8428e54498f6252f873c6bb3276e246
Working tree: ADR-0002 and the R02 exec plan were staged additions;
              specs/exercises/R02-exercise-architecture.md was untracked.
Fixture directory: absent.
R02 trace: absent.
```

The current Django site used authored lesson HTML and
`templates/lessons/components/exercise.html` to render self-check answers in a
native `<details>` element. No intelligent Assessment attempt or server-reveal
implementation was present or changed.

---

## 4. Files changed

### Added

- `specs/exercises/fixtures/self-check.exercise-v1.json`
- `specs/exercises/fixtures/final-answer.exercise-v1.json`
- `specs/exercises/fixtures/step-by-step.exercise-v1.json`
- `specs/exercises/fixtures/structured-solution.exercise-v1.json`
- `specs/exercises/fixtures/reveal.exchange-v1.json`
- `specs/exercises/fixtures/final-answer-submission.exchange-v1.json`
- `specs/exercises/fixtures/step-submission.exchange-v1.json`
- `docs/agent-traces/R02-exercise-architecture.md`

### Modified

- `docs/adr/ADR-0002-exercise-contract-architecture.md`
- `specs/exercises/R02-exercise-architecture.md`
- `docs/exec-plans/completed/R02-exercise-architecture.md`

### Deleted

- none

---

## 5. Commands / tools executed

```text
git branch --show-current
git rev-parse HEAD
git status --short
rg searches over R02 documents, architecture, Django code, templates, and curriculum
PowerShell ConvertFrom-Json over specs/exercises/fixtures/*.json
rg -n -i "answer_key|validation_spec|canonical_solution|accepted_variants" specs/exercises/fixtures
python --version
.\.venv\Scripts\python.exe --version
py --version
python scripts/verify_repo.py
<bundled Python 3.12.14> scripts/verify_repo.py
git diff --check
git diff --cached --check
```

The full verification entry point was executed with the local Codex bundled
Python 3.12.14 and the existing project `.venv` site-packages on the process
`PYTHONPATH`. No dependency, environment file, or repository configuration was
modified.

---

## 6. Implementation summary

- defined the ordinary public `ExerciseDTO` boundary separately from
  server-only validation data;
- retained the four baseline interaction modes and all baseline step/parse
  enums;
- distinguished client-authored `SolutionStepSubmission` fields from
  server-authored normalization and parse results;
- bound historical attempts to `contract_version` while deferring the concrete
  snapshot/version persistence strategy;
- defined `contract_version` as the logical name of the single baseline
  `version`, with the server-side attempt version authoritative and the client
  value used only as a checked compatibility precondition;
- aligned R02 to M0 — Agent-ready foundation with the planned window
  2026-10-02 — 2026-10-08;
- separated the `STRUCTURED_SOLUTION` dynamic UI/form `input_schema` from the
  typed ordering/serialization `step_schema` required by FR-08;
- made hint and reveal evidence semantics agree with Progress Algorithm v1;
- documented the compatibility boundary between legacy authored `<details>`
  self-check answers and the target server-reveal contract;
- added seven versioned public contract fixtures for the four modes and the
  reveal, final-answer, and step-submission exchanges.

No product code, model, migration, content, template, static asset, dependency,
database data, API, parser, validator, Progress implementation, Solution
Analyzer implementation, or frontend implementation was changed.

---

## 7. Observable failures / incidents

| Failure / finding | Detection | Impact |
| --- | --- | --- |
| Required versioned mock contracts were absent. | Repository inspection found no `specs/exercises/fixtures/` directory. | Backend/frontend did not have file-based examples for parallel work. |
| Client/server ownership of `normalized_repr` and `parse_status` was ambiguous. | ADR/spec comparison with the requested step-submission boundary. | A client could be interpreted as authoring authoritative parser results. |
| Historical interpretation was stated without explicit attempt-to-version binding. | ADR/spec versioning review. | Later exercise edits could make attempt interpretation ambiguous. |
| Hint wording did not explicitly require `CORRECT_AFTER_HINT`. | Comparison with `specs/progress/BASELINE-v1.md`. | Evidence semantics could diverge between implementations. |
| `python` was unavailable in `PATH`; the existing `.venv` launcher referenced a missing Python 3.10.11 installation, and `py` found no installed interpreter. | Direct version commands. | The configured entry point could not be launched through the inactive project `.venv`; verification used available bundled Python 3.12.14 with existing project packages. |

---

## 8. Root cause summary

The initial R02 documents described the required concepts but did not yet
contain concrete fixture files or enough field-direction and version-binding
detail for independent client/server implementation. The local Python launcher
failure was an environment condition unrelated to R02 documentation changes.

---

## 9. Corrections made

- added four public exercise DTO fixtures and three public exchange fixtures;
- kept all server correctness secrets out of the JSON fixtures;
- made `normalized_repr` and `parse_status` server-authored outputs;
- required one-based ordered steps and unambiguous historical order;
- required attempts to retain the active `contract_version` interpretation;
- made correct work after hint use follow `CORRECT_AFTER_HINT` semantics;
- retained explicit record-before-return reveal ordering and no-evidence reveal
  semantics;
- made the target `SELF_CHECK` reveal rule mandatory for attempt-backed
  intelligent exercises while preserving legacy authored pages as a separate
  compatibility case;
- documented legacy authored self-check markup as compatibility input rather
  than the target intelligent exercise contract;
- removed the unresolved placeholder URL from ADR-0002 and recorded that the
  official R02 Issue is https://github.com/Tramsey00/MathStart-Python/issues/4;
- applied all four correction groups from the 2026-09-24 Changes requested
  review: milestone/window, Issue and branch baseline, version semantics, and
  the FR-08 `STRUCTURED_SOLUTION` contract.

---

## 10. Verification results

Interpreter used for the verification entry point: Python 3.12.14.

### Backend

| Check | Result |
| --- | --- |
| `python manage.py check` through `scripts/verify_repo.py` | PASS |
| `python manage.py test` through `scripts/verify_repo.py` | PASS — 15 tests |

### Database

| Check | Result |
| --- | --- |
| `python manage.py makemigrations --check --dry-run` | PASS — no changes detected |
| Fresh PostgreSQL migrate | NOT CONFIGURED / outside R02 documentation scope |
| Migration smoke | N/A — R02 added no schema change |

### Content

| Check | Result |
| --- | --- |
| `python manage.py check_content_quality` | PASS |
| `python manage.py check_lesson_sources --all` | PASS — 263 sources |
| `python manage.py check_site_integrity` | PASS |

### Domain-specific

| Check | Result |
| --- | --- |
| Knowledge graph validation | NOT CONFIGURED / N/A for R02 |
| Exercise contract validation | NOT CONFIGURED; manual contract coverage and JSON parse PASS |
| Public DTO secret-leak regression | NOT CONFIGURED; manual fixture scan PASS |
| LLM structured-output validation | NOT CONFIGURED / N/A for R02 |
| Golden eval subset | NOT CONFIGURED / N/A for R02 |
| Frontend checks | NOT CONFIGURED / N/A for R02 |
| Playwright critical flow | NOT CONFIGURED / N/A for R02 |

Additional results:

```text
python scripts/verify_repo.py          ENVIRONMENT FAIL (python not in PATH)
scripts/verify_repo.py                 PASS (6 of 6 configured checks)
JSON fixture parsing                   PASS (7 files)
Forbidden fixture-field name scan      PASS (no matches)
git diff --check                       PASS
git diff --cached --check              PASS
```

---

## 11. Final diff summary

- R02 ADR/spec now form one versioned exercise contract with an explicit
  public/server boundary.
- Seven JSON specification fixtures cover all requested modes and exchanges.
- Exec plan records the audit findings, corrections, and verification status.
- Changes remain documentation/specification-only.

---

## 12. Acceptance criteria result

| Acceptance criterion | Result | Evidence |
| --- | --- | --- |
| Four interaction modes defined | PASS | ADR sections 2-3, spec sections 2 and 6-10, four exercise fixtures |
| Public/server boundary defined | PASS | ADR section 4, spec sections 3-5 |
| `SolutionStep`, step types, and parse statuses defined | PASS | ADR sections 5 and 8, spec sections 9 and 11 |
| Public schemas contain no correctness secrets | PASS | Spec section 4 and fixture secret scan |
| FR-08 structured input/step schema split | PASS | Spec section 10 and `structured-solution.exercise-v1.json` |
| Hint/reveal semantics match Progress baseline | PASS | ADR section 7, spec sections 12-13 |
| Wrong final result does not invent a misconception | PASS | Spec invariants/mode behavior and final-answer exchange fixture |
| Historical attempts remain version-interpretable | PASS | ADR section 9 and spec section 14 |
| Required mock contracts exist | PASS | Seven JSON fixtures under `specs/exercises/fixtures/` |
| Product implementation unchanged | PASS | Final changed-file scope inspection |
| Configured repository verification passes | PASS | `scripts/verify_repo.py`: 6 of 6 checks |
| Human gate accepted | PASS | Ruslan accepted R02 on 2026-09-24 |

---

## 13. Remaining risks / follow-ups

- Backend implementation must choose and test an immutable version reference or
  snapshot strategy without changing the accepted contract semantics.
- Automated exercise-contract and secret-leak regression tooling is not yet
  configured; R02 used JSON parsing and manual/static checks.
- Existing legacy lesson answers remain embedded in authored HTML until a later
  scoped conversion.
- The project `.venv` references a missing Python 3.10.11 installation. This is
  a pre-existing environment follow-up and did not block the completed R02
  verification through Python 3.12.14.

---

## 14. Harness improvement

- **No.**

The repository workflow and verification skill were sufficient to scope the
audit, classify the environment issue, and record unconfigured future checks.

---

## 15. Human review

**Reviewer:** Ruslan

**Status:** Accepted

**Date:** 2026-09-24

**Feedback:**

Review history:

- **2026-09-24 — Changes requested by Ruslan.** The core architecture was
  accepted conceptually. Four correction groups were requested before the final
  human gate:
  1. assign R02 to M0 — Agent-ready foundation and record the planned window
     2026-10-02 — 2026-10-08;
  2. record official Issue
     https://github.com/Tramsey00/MathStart-Python/issues/4 and confirm branch
     start commit `0a5398d6d8428e54498f6252f873c6bb3276e246` as the current
     `main` baseline after R01;
  3. define `contract_version` as the one baseline `version`, with an
     authoritative server-side attempt value and a client compatibility check;
  4. make `STRUCTURED_SOLUTION.input_schema` the dynamic UI/form contract and
     reserve `step_schema` for typed-step ordering and serialization.

All four requested correction groups were applied.

- **2026-09-24 — Final human gate Accepted by Ruslan.** ADR-0002, the R02
  specification, mock contracts, trace, and verification evidence were
  accepted without further requested changes.

---

## 16. Final status

`COMPLETE`

Reason:

The architecture audit, contract fixtures, configured verification, requested
corrections, and final human gate are complete. Ruslan accepted R02 on
2026-09-24.
