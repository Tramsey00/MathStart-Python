# SPEC R02: Exercise Architecture

- **Status:** Accepted
- **Owner:** Ruslan
- **Related issue:** https://github.com/Tramsey00/MathStart-Python/issues/4
- **Related ADR:** `docs/adr/ADR-0002-exercise-contract-architecture.md`
- **Related exec plan:** `docs/exec-plans/completed/R02-exercise-architecture.md`
- **Target milestone:** M0 — Agent-ready foundation
- **Planned window:** 2026-10-02 — 2026-10-08
- **Last updated:** 2026-09-24
- **Human gate:** Accepted by Ruslan on 2026-09-24

---

## 1. Goal

Define a stable, versioned exercise contract that allows backend and frontend work to proceed independently without leaking server-side answers or mixing weak evidence with confirmed misconceptions.

R02 is architecture/specification only.

It does not implement Django models, migrations, APIs, validators, or UI.

---

## 2. Product baseline

MathStart supports four exercise interaction modes:

1. `SELF_CHECK`
2. `FINAL_ANSWER`
3. `STEP_BY_STEP`
4. `STRUCTURED_SOLUTION`

Every exercise declares one interaction mode.

The interaction mode controls UX, student payload shape, validation path, reveal/hint behavior, and evidence semantics.

---

## 3. Non-negotiable invariants

1. Public exercise payloads MUST NOT contain `answer_key`.
2. Public exercise payloads MUST NOT contain `validation_spec`.
3. Public exercise payloads MUST NOT contain `canonical_solution`.
4. Secret accepted variants MUST remain server-side.
5. Reveal MUST be explicit and recorded before the canonical answer/solution is returned.
6. A fully revealed attempt MUST NOT create `CORRECT_FIRST_TRY`.
7. Wrong `FINAL_ANSWER` alone MUST NOT create a specific misconception.
8. Raw student input MUST be preserved separately from normalized representation.
9. `UNSUPPORTED` parse status MUST NOT be converted into an invented misconception.
10. AI/LLM output is not the source of mathematical truth.
11. Interaction mode is not a skill.
12. Progress ownership remains in the Progress domain.

---

## 4. Public exercise contract

Conceptual DTO:

```json
{
  "id": "exercise-id",
  "code": "linear_parentheses_001",
  "topic": {
    "id": "topic-id",
    "slug": "linear-equations"
  },
  "statement": "Solve: 2(x+3)=10",
  "interaction_mode": "STEP_BY_STEP",
  "input_schema": null,
  "step_schema": {
    "allowed_step_types": ["EQUATION_STATE"]
  },
  "parser_profile": "algebra_linear_v1",
  "difficulty": "medium",
  "reveal_policy": {
    "allowed": true,
    "confirmation_required": true
  },
  "contract_version": 1
}
```

This is a contract example, not a final DRF serializer.

Public fields may describe how to render the task, how to collect input, which step types are accepted, parser/display profile, difficulty, reveal/hint presentation rules, and `contract_version`.

`input_schema` and `step_schema` define only the public serialization and UX
contract. They may contain field names, public input types, required flags,
ordering rules, and non-secret shape constraints. They must not contain correct
values, correctness markers, hidden accepted variants, or rules from which the
correct result can be reconstructed.

Public fields must not reveal the correct answer, canonical solution, hidden accepted variants, or deterministic validation rules that trivially reconstruct the answer.

---

## 5. Server-only validation contract

Conceptual server representation:

```json
{
  "exercise_id": "exercise-id",
  "answer_key": {
    "type": "equation_solution",
    "value": 2
  },
  "validation_spec": {
    "validator": "linear_equation_v1"
  },
  "canonical_solution": {
    "steps": [
      "2x+6=10",
      "2x=4",
      "x=2"
    ]
  },
  "accepted_variants": [],
  "contract_version": 1
}
```

This object is never part of the ordinary public exercise GET payload.

---

## 6. Interaction mode matrix

| Mode | Student submits | Validation | Evidence semantics |
| --- | --- | --- | --- |
| `SELF_CHECK` | nothing required | no solution analysis; reveal action only | no positive mastery from view/reveal |
| `FINAL_ANSWER` | fields from `input_schema` | deterministic/domain answer validation | correct/weak wrong evidence; no specific misconception from wrong final result alone |
| `STEP_BY_STEP` | ordered `SolutionStep` objects | parser + transition validator + optional analyzer classification | confirmed problematic transition may support misconception evidence |
| `STRUCTURED_SOLUTION` | dynamic fields from `input_schema`, represented through typed steps defined by `step_schema` | schema/domain validators + optional LLM classification | evidence only from validated fields/steps |

---

## 7. `SELF_CHECK`

Typical public contract:

```json
{
  "interaction_mode": "SELF_CHECK",
  "input_schema": null,
  "step_schema": null,
  "reveal_policy": {
    "allowed": true
  }
}
```

Behavior:

- submission is not required;
- solution analysis is not required;
- reveal is explicit;
- for an attempt-backed intelligent exercise, the server records reveal before
  returning the answer/solution;
- positive mastery evidence is not created from reveal.

Existing legacy MathStart exercises may remain in this mode until deeper support is implemented.

---

## 8. `FINAL_ANSWER`

Public input example:

```json
{
  "interaction_mode": "FINAL_ANSWER",
  "input_schema": {
    "type": "object",
    "fields": [
      {
        "name": "answer",
        "input_type": "math_text",
        "required": true
      }
    ]
  }
}
```

Submission example:

```json
{
  "attempt_id": "attempt-final-001",
  "contract_version": 1,
  "payload": {
    "answer": "32"
  }
}
```

Behavior:

1. preserve submitted payload;
2. validate public payload shape;
3. run server-side deterministic/domain validator;
4. if correct, create the appropriate correct evidence later through Progress;
5. if wrong, create weak wrong evidence;
6. do not invent a specific misconception from the wrong value alone.

---

## 9. `STEP_BY_STEP`

`SolutionStep` example:

```json
{
  "step_no": 1,
  "step_type": "EQUATION_STATE",
  "payload": {
    "expression": "2x+3=10"
  },
  "raw_text": "2x+3=10",
  "normalized_repr": null,
  "parse_status": "NOT_REQUIRED"
}
```

`SolutionStepSubmission` is the client-to-server shape. The client supplies
`step_no`, `step_type`, `payload`, and `raw_text`. The server validates the
public shape and produces `normalized_repr` and `parse_status`; clients must not
claim authoritative parse results. The resulting stored/returned
`SolutionStep` contains all six logical fields shown above.

`step_no` is a positive, one-based position and is unique within an attempt.
The accepted ordering and retry/update behavior are implementation API details,
but historical order must remain unambiguous.

Required logical fields:

- `step_no: int`
- `step_type: string/enum`
- `payload: object`
- `raw_text: string | null`
- `normalized_repr: string | null`
- `parse_status: OK | UNSUPPORTED | INVALID | NOT_REQUIRED`

Baseline step types:

- `MATH_EXPRESSION`
- `EQUATION_STATE`
- `STRUCTURED_FIELDS`
- `FINAL_STATEMENT`

Behavior:

1. preserve raw step/payload;
2. validate step schema;
3. normalize/parse if required;
4. compare previous/new state when a validator supports the transition;
5. if valid, continue;
6. if suspicious, produce candidate error evidence;
7. optional Solution Analyzer classification may follow;
8. only validated evidence may affect Progress.

---

## 10. `STRUCTURED_SOLUTION`

`input_schema` is the dynamic UI/form contract and defines the user-facing
fields. The submitted payload passes public schema validation and server-side
domain validation.

`step_schema` separately defines how the solution is represented as typed,
ordered steps. It describes allowed step types, ordering, and serialization;
it does not replace `input_schema`.

Illustrative public contract:

```json
{
  "input_schema": {
    "type": "object",
    "fields": [
      {"name": "known_values", "input_type": "object", "required": true},
      {"name": "formula", "input_type": "math_text", "required": true},
      {"name": "substitution", "input_type": "math_text", "required": true},
      {"name": "answer", "input_type": "math_text", "required": true}
    ]
  },
  "step_schema": {
    "type": "ordered_steps",
    "allowed_step_types": ["STRUCTURED_FIELDS", "FINAL_STATEMENT"],
    "ordering": {
      "field": "step_no",
      "direction": "ascending"
    },
    "serialization": [
      {
        "step_type": "STRUCTURED_FIELDS",
        "payload_fields": ["known_values", "formula", "substitution"]
      },
      {
        "step_type": "FINAL_STATEMENT",
        "payload_fields": ["answer"]
      }
    ]
  }
}
```

This is an illustrative contract fixture.

It does not commit the project to one universal JSON-Schema implementation.

Domain extensions must preserve the generic attempt/step model and introduce validators/adapters deliberately.

---

## 11. Parser profile and parse status

`parser_profile` identifies the supported parsing/normalization behavior expected for an exercise.

It is public metadata only when needed by the client.

It must not expose correctness secrets.

Baseline parse states:

- `OK`
- `UNSUPPORTED`
- `INVALID`
- `NOT_REQUIRED`

Semantics:

- `OK`: supported input was parsed successfully;
- `UNSUPPORTED`: syntax/domain is not supported reliably;
- `INVALID`: malformed according to the expected public contract;
- `NOT_REQUIRED`: this step does not require parser normalization.

`UNSUPPORTED` is not a misconception.

---

## 12. Hint semantics

- hint use is observable;
- the attempt records the highest used hint level and/or event history;
- baseline hint levels are `0..3`;
- a correct answer after any hint in the attempt uses
  `CORRECT_AFTER_HINT`, not `CORRECT_FIRST_TRY`;
- exact numeric Progress effects are owned by `specs/progress/BASELINE-v1.md`.

R02 does not define tutor prompt wording.

---

## 13. Reveal semantics

Reveal flow:

1. student requests reveal;
2. server records reveal state/event;
3. `answer_revealed_at` (or equivalent fact) is persisted;
4. only then may the canonical answer/solution be returned;
5. subsequent work in the same attempt cannot qualify as `CORRECT_FIRST_TRY`;
6. copying the revealed solution is not knowledge evidence;
7. reveal itself maps to zero knowledge gain under the Progress baseline.

The ordinary exercise GET must not make reveal equivalent to reading a hidden field already delivered to the browser.

---

## 14. Contract versioning

Every exercise/interaction contract has a `contract_version`.

`contract_version` is the R02 logical name for the baseline `version` concept
from MathStart Technical Specification v3.1. It does not introduce a second
independent version counter.

The public exercise definition and the corresponding server-only validation
data are interpreted within the same contract version.

Breaking public contract changes require explicit review.

Every attempt is bound to the exercise `contract_version` active when the
attempt starts. Historical attempts must be interpreted against that version,
not against the current exercise definition.

The exact persistence strategy for immutable version records or snapshots is
deferred to the backend implementation spec.

The version stored server-side on the attempt is authoritative. A
`contract_version` in a client request is a compatibility/precondition value.
The server must compare it with the attempt version and reject a mismatch; the
client value cannot change the authoritative version of the attempt.

---

## 15. Mock contracts for parallel work

R02 provides these versioned specification fixtures:

- `fixtures/self-check.exercise-v1.json`;
- `fixtures/final-answer.exercise-v1.json`;
- `fixtures/step-by-step.exercise-v1.json`;
- `fixtures/structured-solution.exercise-v1.json`;
- `fixtures/reveal.exchange-v1.json`;
- `fixtures/final-answer-submission.exchange-v1.json`;
- `fixtures/step-submission.exchange-v1.json`.

Fixtures must contain no server validation secrets.

The exercise fixtures are ordinary public `ExerciseDTO` examples. Exchange
fixtures show public request/response shapes. The reveal response contains
revealed content only after the server has recorded the reveal; this is the
explicit reveal response, not an ordinary exercise GET payload. All fixtures
are specification artifacts, not runtime seed data or executable API output.

The current site renders authored legacy self-check answers in lesson HTML with
`<details>`. Those existing pages are compatibility input and may remain
`SELF_CHECK` until a later scoped conversion. They do not satisfy or redefine
the target server-reveal contract for new intelligent exercises.

---

## 16. Security / integrity checks

A later implementation regression test must assert that ordinary public ExerciseDTO does not contain:

```text
answer_key
validation_spec
canonical_solution
accepted_variants
```

Equivalent secret fields must be included in the same regression protection.

---

## 17. Acceptance criteria

- [x] four interaction modes are precisely defined;
- [x] public/server contracts are separate;
- [x] `STRUCTURED_SOLUTION` uses `input_schema` for dynamic fields and
  `step_schema` for typed-step ordering/serialization;
- [x] `SolutionStep` is typed and ordered;
- [x] baseline step types are defined;
- [x] parse statuses are defined;
- [x] hint/reveal semantics are explicit;
- [x] no wrong-final-answer diagnosis shortcut exists;
- [x] public examples contain no validation secrets;
- [x] contract versioning rule is defined;
- [x] mock contracts support backend/frontend parallel work;
- [x] ADR-0002 and this spec agree;
- [x] no product code or DB schema is changed in R02.

---

## 18. Verification

```bash
python scripts/verify_repo.py
git diff --check
```

Manual R02 contract review:

- verify no secret fields are present in public examples;
- verify all four modes are represented;
- verify no interaction mode is modeled as a skill;
- verify hint/reveal semantics agree with Progress baseline;
- verify no product implementation is introduced.

---

## 19. Follow-up implementation tasks

After R02 human acceptance:

- backend implements persistence/API contracts against the accepted specification;
- frontend implements renderers and interaction states against versioned mocks;
- R03 formalizes Knowledge/Progress algorithms and event semantics without silently changing R02 interaction contracts.
