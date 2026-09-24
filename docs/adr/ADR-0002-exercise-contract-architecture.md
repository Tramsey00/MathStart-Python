# ADR-0002: Exercise Contract Architecture

- **Status:** Accepted
- **Date:** 2026-09-24
- **Decision owners:** MathStart team
- **Primary owner:** Ruslan
- **Related baseline:** MathStart Technical Specification v3.1
- **Related issue:** https://github.com/Tramsey00/MathStart-Python/issues/4
- **Related spec:** `specs/exercises/R02-exercise-architecture.md`
- **Related exec plan:** `docs/exec-plans/completed/R02-exercise-architecture.md`
- **Related mock contracts:** `specs/exercises/fixtures/`
- **Supersedes:** none
- **Scope:** exercise interaction contracts, public/server boundary, solution-step representation, hint/reveal semantics

---

## 1. Context

MathStart already contains educational pages and legacy self-check exercises, but the intelligent-learning MVP requires a stable exercise contract shared by backend and frontend before implementation begins.

The system must support different pedagogical interactions without forcing every task through the same validation path.

The MathStart v3.1 baseline requires:

- four explicit interaction modes;
- a strict separation between client-visible interaction metadata and server-only validation data;
- typed ordered solution steps;
- deterministic validation where supported;
- explicit hint/reveal semantics;
- evidence-safe behavior that prevents answer reveal or weak evidence from being misinterpreted as demonstrated knowledge.

Backend and frontend work must be able to proceed contract-first using versioned mocks.

---

## 2. Decision

MathStart adopts one versioned exercise architecture with four explicit interaction modes:

- `SELF_CHECK`
- `FINAL_ANSWER`
- `STEP_BY_STEP`
- `STRUCTURED_SOLUTION`

Every exercise declares exactly one interaction mode.

The public exercise contract describes how the client renders and submits the exercise.

Server-only validation data is stored and exposed separately from the public exercise contract.

`SolutionStep` is a typed ordered domain object rather than a plain text row.

Hint and reveal actions are part of attempt evidence semantics and must be observable.

No implementation-specific Django model shape is finalized by this ADR; persistence is implemented later against these contracts.

---

## 3. Interaction modes

### `SELF_CHECK`

Use when no submission is required or reliable automatic validation is not yet supported.

Behavior:

- client receives task/public interaction metadata;
- answer/solution may be revealed through an explicit server action;
- for an attempt-backed intelligent exercise, the server records reveal before
  returning the answer/solution;
- no positive mastery evidence is created merely by viewing/revealing the solution;
- full Solution Analyzer flow is not required.

### `FINAL_ANSWER`

Use when the final result is sufficient.

Behavior:

- student submits one or more fields defined by `input_schema`;
- server performs deterministic/domain answer validation;
- correct work may create appropriate positive evidence;
- wrong result produces weak negative evidence;
- wrong result alone must not create a specific persistent misconception.

### `STEP_BY_STEP`

Use when intermediate transitions matter pedagogically.

Behavior:

- student submits ordered typed steps;
- each mathematical step represents a state/transformation;
- raw input is preserved;
- supported input is normalized/parsed;
- transition validation occurs when supported;
- Solution Analyzer may classify a confirmed problematic transition;
- a specific misconception is created only from sufficient validated evidence.

### `STRUCTURED_SOLUTION`

Use when the natural solution contains heterogeneous fields/actions.

Examples:

- claim + reason;
- known values -> formula -> substitution -> answer;
- total/favorable outcomes -> probability;
- sorted dataset -> median.

Behavior:

- dynamic user-facing fields and their submitted payload are defined by
  `input_schema`;
- the submitted payload passes public schema validation and server-side domain
  validation;
- `step_schema` defines the typed-step representation, including allowed step
  types, ordering, and serialization structure; it does not replace
  `input_schema` as the UI/form contract;
- LLM classification is optional and subordinate to validated evidence.

---

## 4. Public/server boundary

### Public exercise contract

Client-visible data may include:

- exercise identifier/code;
- topic reference;
- statement;
- `interaction_mode`;
- `input_schema`;
- `step_schema`;
- `parser_profile`;
- difficulty;
- `reveal_policy`;
- contract/exercise version;
- public presentation metadata.

### Server-only validation data

The ordinary exercise payload must not contain:

- `answer_key`;
- `validation_spec`;
- `canonical_solution`;
- accepted variants that reveal the answer;
- equivalent validation secrets.

Reveal must be a server action performed after the attempt/reveal state is recorded.

---

## 5. `SolutionStep` contract

Baseline logical representation:

```text
SolutionStep {
    step_no: int
    step_type: enum/string
    payload: JSON object
    raw_text: string | null
    normalized_repr: string | null
    parse_status: OK | UNSUPPORTED | INVALID | NOT_REQUIRED
}
```

Baseline step types:

- `MATH_EXPRESSION`
- `EQUATION_STATE`
- `STRUCTURED_FIELDS`
- `FINAL_STATEMENT`

New domain step types require a spec/ADR when semantics change, a validator/adapter contract, tests, and compatibility with the generic attempt/step model.

---

## 6. Schema responsibilities

### `input_schema`

Describes the public user-input/form contract for `FINAL_ANSWER` and
`STRUCTURED_SOLUTION`.

It defines:

- fields;
- client input types;
- required/optional fields;
- public validation constraints needed for UX;
- serialization shape.

It must not encode the correct answer or allow trivial reconstruction of it.

### `step_schema`

Describes the public step/payload contract for step-based modes.

It defines:

- allowed step types;
- field structure;
- required/optional data;
- public serialization rules.

It must not contain server-only correctness rules.

### `validation_spec`

Server-only.

Defines validation behavior/parameters that must not be present in ordinary client payloads.

---

## 7. Hint and reveal policy

Baseline rules:

- attempt records hint usage, either as `hint_level_used = 0..3` and/or an event history;
- reveal is explicit;
- server records reveal state before returning canonical answer/solution;
- after full reveal, the same attempt cannot produce `CORRECT_FIRST_TRY`;
- correct work after any hint in the attempt uses `CORRECT_AFTER_HINT`, not
  `CORRECT_FIRST_TRY`;
- `ANSWER_REVEALED` itself does not prove knowledge;
- attempt history must explain why a particular knowledge event was chosen.

Exact Progress Algorithm values remain owned by `specs/progress/BASELINE-v1.md`.

---

## 8. Parser behavior

Raw user input must be preserved.

Supported syntax may be normalized into a canonical representation.

Baseline parse states:

- `OK`
- `UNSUPPORTED`
- `INVALID`
- `NOT_REQUIRED`

Unsupported input is a valid system outcome and must not be converted into an invented misconception.

---

## 9. Versioning

Exercise/public interaction contracts are versioned.

`contract_version` is the logical name used by R02 for the baseline `version`
concept in MathStart Technical Specification v3.1. It is one version counter,
not a second independent counter layered on top of `version`.

The public exercise definition and its corresponding server-only validation
data must be interpreted within the same contract version.

Breaking changes to interaction-mode semantics, public schema structure, `SolutionStep` semantics, reveal policy, or server/public boundary require explicit review and, when architectural, an ADR.

Existing historical attempts must remain interpretable against the exercise/contract version under which they were created.

Each attempt is bound to the `contract_version` used when the attempt starts.
Later edits must not cause an historical submission to be interpreted against a
different contract. The implementation may use an immutable version reference
or a snapshot, but the persistence choice is deferred to the backend spec.

The version stored server-side for the attempt is authoritative. A
`contract_version` sent by the client in a request is a compatibility/precondition
value: the server must compare it with the attempt version and reject a
mismatch, but the client value cannot change the authoritative attempt version.

The versioned R02 mock contracts are specification artifacts under
`specs/exercises/fixtures/`; they are not runtime seed data or final serializer
implementations.

---

## 10. Consequences

### Positive

- backend and frontend can work in parallel against stable contracts;
- answer secrecy is explicit;
- step-by-step analysis has a typed foundation;
- legacy content can remain `SELF_CHECK` until deeper support exists;
- interaction mode remains separate from subject-domain skill.

### Trade-offs

- schemas require version discipline;
- generic step modeling needs domain adapters/validators;
- frontend cannot derive correctness from public payloads;
- reveal/hint semantics must be persisted consistently.

---

## 11. Alternatives considered

### One universal free-text mode

**Rejected.**

It cannot reliably represent final answers, structured solutions, reveal-only legacy tasks, and typed transitions without ambiguity.

### Separate unrelated model per subject/domain

**Rejected for MVP.**

It would fragment attempt/history/progress integration and make frontend/backend contracts harder to reuse.

### Embed answer/validator data in the public exercise payload

**Rejected.**

It violates the security/integrity boundary and allows trivial answer disclosure.

---

## 12. Verification

```bash
python scripts/verify_repo.py
git diff --check
```

Manual architecture checks:

- no public example includes server validation secrets;
- mode semantics do not contradict `PRODUCT.md` or `ARCHITECTURE.md`;
- progress ownership remains in Progress;
- interaction modes are not modeled as skills;
- no implementation code or migrations are introduced by R02.

---

## 13. Human gate

Required.

Human review must explicitly approve the four-mode contract, public/server boundary, `SolutionStep`, step types, hint/reveal semantics, contract versioning, and mock payloads.

**Reviewer:** Ruslan

**Decision:** Accepted

**Date:** 2026-09-24

---

## 14. Follow-up

After acceptance:

- Vladimir may implement backend persistence/API contracts against this spec.
- Ilya may implement frontend mode renderers against the mock contracts.
- R03 may define Knowledge/Progress semantics in greater detail without silently changing the exercise contract.
