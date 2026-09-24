# EXEC PLAN R02: Exercise Architecture

- **Status:** Completed
- **Owner:** Руслан
- **Created:** 2026-09-24
- **Last updated:** 2026-09-24
- **Related issue:** https://github.com/Tramsey00/MathStart-Python/issues/4
- **Related spec:** `specs/exercises/R02-exercise-architecture.md`
- **Related ADR:** `docs/adr/ADR-0002-exercise-contract-architecture.md`
- **Dependency:** R01 completed
- **Target milestone:** M0 — Agent-ready foundation
- **Planned window:** 2026-10-02 — 2026-10-08
- **Estimated effort:** 20 hours
- **Priority:** P0
- **Human gate required:** Yes
- **Human gate:** Accepted by Ruslan on 2026-09-24

---

## 1. Objective

Produce approved exercise schemas/invariants and mock contracts that allow backend and frontend development to proceed independently.

R02 is complete when the repository has an accepted exercise architecture and first R02 trace.

No product implementation is part of this task.

---

## 2. Preconditions

- [x] R01 Harness v1 completed
- [x] branch start commit `0a5398d6d8428e54498f6252f873c6bb3276e246`
  matches the current `main` baseline after R01
- [x] branch `R02-exercise-architecture` is active
- [x] GitHub Issue R02 created: https://github.com/Tramsey00/MathStart-Python/issues/4
- [x] R02 spec added
- [x] ADR-0002 added
- [x] coding-agent architecture audit completed
- [x] mock contracts prepared and agent-reviewed
- [x] verification passes
- [x] R02 trace created
- [x] human gate completed

---

## 3. Scope

### In scope

- four interaction modes;
- public/server exercise split;
- public `ExerciseDTO`;
- server `ExerciseValidation`;
- `SolutionStep`;
- `input_schema`;
- `step_schema`;
- parser statuses/profile semantics;
- hint/reveal semantics;
- contract versioning;
- mock examples/fixtures;
- ADR/spec consistency.

### Out of scope

- Django models;
- migrations;
- API implementation;
- serializers/views;
- parser implementation;
- validators;
- Progress implementation;
- Solution Analyzer implementation;
- frontend implementation;
- new dependencies.

---

## 4. Architecture boundaries

Affected domains:

- Content
- Assessment
- Validation
- Progress (semantic boundary only)
- Solution Analyzer (semantic boundary only)
- frontend contract surface
- Harness/docs

Dependency rules that must remain intact:

```text
Content -> Knowledge (mappings)
Assessment -> Validation
Assessment -> SolutionAnalyzer
SolutionAnalyzer -> Validation
SolutionAnalyzer -> LLMProvider
SolutionAnalyzer -> Progress (validated analysis/evidence only)
Progress -> Knowledge
```

Forbidden shortcuts:

- frontend receives answer keys;
- exercise DTO updates mastery;
- wrong final answer creates a specific misconception automatically;
- Solution Analyzer mutates `UserSkillState`;
- interaction mode becomes a skill;
- R02 introduces implementation-specific schema migrations.

---

## 5. Planned steps

### Step 1 — Create R02 issue/branch identity

Branch:

```text
R02-exercise-architecture
```

Issue:

```text
R02 — Exercise architecture
```

Use one issue = one branch = one PR.

### Step 2 — Review baseline contracts

Read root docs, ADR-0001, Progress baseline, R02 spec/ADR, and current legacy exercise rendering only for compatibility constraints.

Do not refactor legacy content.

### Step 3 — Audit the four modes

For each mode verify:

- student input;
- public schema;
- validation path;
- reveal/hint behavior;
- evidence semantics;
- unsupported behavior.

### Step 4 — Audit public/server split

Confirm that public examples do not contain:

- `answer_key`
- `validation_spec`
- `canonical_solution`
- secret accepted variants

Confirm reveal is explicit and recorded before canonical answer/solution is returned.

### Step 5 — Audit `SolutionStep`

Confirm fields:

- `step_no`
- `step_type`
- `payload`
- `raw_text`
- `normalized_repr`
- `parse_status`

Confirm baseline types:

- `MATH_EXPRESSION`
- `EQUATION_STATE`
- `STRUCTURED_FIELDS`
- `FINAL_STATEMENT`

### Step 6 — Prepare mock contracts

Ensure the spec or dedicated fixtures provide mock payloads for all four modes plus reveal, final-answer submission, and step submission.

Dedicated JSON fixtures, if used, belong under:

```text
specs/exercises/fixtures/
```

They are specification artifacts, not runtime seed data.

### Step 7 — Agent audit

Run a bounded Codex task.

Allowed changes:

- R02 ADR/spec/exec plan;
- spec fixtures;
- R02 trace;
- minimal Harness-link corrections directly required by R02.

Forbidden changes:

- application code;
- models;
- migrations;
- templates/static UI;
- dependencies;
- database data;
- APIs.

### Step 8 — Verification

```bash
python scripts/verify_repo.py
git diff --check
```

Manually inspect public contract examples for secret leakage.

### Step 9 — Trace

Create:

```text
docs/agent-traces/R02-exercise-architecture.md
```

### Step 10 — Human gate

Ruslan reviews ADR-0002, R02 spec, mock contracts, trace, diff, and verification.

Only after acceptance may R02 be marked completed and merged.

---

## 6. Audit findings and corrections

The architecture audit found and corrected these contract gaps:

- versioned mock files required by R02 were absent;
- the client/server ownership of `normalized_repr` and `parse_status` in step
  submission was ambiguous;
- historical attempt interpretation was required but attempt-to-contract
  version binding was not explicit;
- hint wording did not explicitly require `CORRECT_AFTER_HINT` after hint use;
- legacy authored `<details>` self-check answers needed an explicit
  compatibility boundary from the target server-reveal contract.

The corrected ADR/spec and JSON fixtures now define the public/server split,
all four interaction modes, submission/reveal exchanges, server-authored parse
results, and `contract_version` binding. No persistence or API implementation
shape is selected by these specification artifacts.

Human review on 2026-09-24 accepted the core architecture conceptually and
requested four correction groups before the final gate: M0/window alignment,
official Issue and branch-baseline evidence, precise single-version semantics,
and the FR-08 `STRUCTURED_SOLUTION` split between `input_schema` and
`step_schema`. These corrections are recorded in the R02 trace.

---

## 7. DB / migration plan

No schema change.

No migrations may be added in R02.

---

## 8. API/UI impact

No implementation.

R02 defines contract shapes that later API/UI tasks must implement.

---

## 9. Tests / verification

```bash
python scripts/verify_repo.py
git diff --check
```

Additional review:

- no secret fields in public examples;
- no contradictory mode semantics;
- no product code diff.

Audit result on 2026-09-24:

- `scripts/verify_repo.py`: PASS, 6 of 6 configured checks;
- Django test suite: PASS, 15 tests;
- seven fixtures parse as JSON;
- fixture scan for `answer_key`, `validation_spec`, `canonical_solution`, and
  `accepted_variants`: PASS, no matches;
- `git diff --check`: PASS.

---

## 10. Risks

| Risk | Mitigation |
| --- | --- |
| Contract becomes too generic | keep only v3.1-required abstractions |
| Public payload leaks answers | explicit public/server split + manual review |
| Frontend/backend interpret schemas differently | versioned examples/fixtures |
| Step types proliferate | spec/ADR + validator contract required |
| Reveal creates false positive evidence | explicit attempt/reveal rule |
| FINAL_ANSWER over-diagnoses mistakes | weak wrong evidence only |

---

## 11. Acceptance criteria

- [x] Issue R02 exists.
- [x] branch convention is correct.
- [x] ADR-0002 accepted.
- [x] R02 spec accepted.
- [x] four modes are defined.
- [x] public/server split is defined.
- [x] `STRUCTURED_SOLUTION` keeps the FR-08 `input_schema` UI/form contract
  separate from typed-step `step_schema`.
- [x] `SolutionStep` is defined.
- [x] hint/reveal semantics are defined.
- [x] versioning semantics are defined.
- [x] mocks support parallel backend/frontend work.
- [x] ordinary DTO mocks contain no server-only answer secrets; the explicit
  reveal response exposes content only after recorded reveal.
- [x] no product implementation is introduced.
- [x] verification passes.
- [x] trace exists.
- [x] human gate completed.

---

## 12. Definition of Done

R02 is Done only when all acceptance criteria pass, architecture/spec/ADR agree, mock contracts are reviewable, verification is green, no unrelated product code changed, human gate is accepted, and the branch is ready for a coherent PR.

---

## 13. Completion summary

Architecture audit, mock contracts, verification, and the R02 trace are
complete. The configured verification entry point passed all six checks and 15
Django tests; JSON parsing, secret-field scan, and `git diff --check` also
passed. The official Issue is
https://github.com/Tramsey00/MathStart-Python/issues/4, and branch start commit
`0a5398d6d8428e54498f6252f873c6bb3276e246` matches the confirmed current
`main` baseline after R01. Corrections requested in the first human review are
applied. Ruslan accepted ADR-0002, the R02 spec, and the mock contracts at the
final human gate on 2026-09-24. R02 is complete and the plan is archived under
`docs/exec-plans/completed/`.
