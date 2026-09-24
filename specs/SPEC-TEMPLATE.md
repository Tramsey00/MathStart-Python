# SPEC <ID>: <Feature name>

- **Status:** Draft | Ready | In progress | Implemented | Superseded
- **Owner:** <name>
- **Related issue:** <issue/link>
- **Related ADRs:** <paths or none>
- **Related exec plan:** <path or none>
- **Target milestone:** M0 | M1 | M2 | M3 | M4
- **Last updated:** YYYY-MM-DD

---

## 1. Goal

Describe the user-visible or domain-level result this feature must deliver.

The goal should be testable and narrow enough to implement as a coherent change.

---

## 2. Why this belongs in MathStart

Connect the feature to the v3.1 product baseline.

Reference the relevant product behavior, such as:

- student onboarding;
- exercise interaction modes;
- knowledge graph;
- deterministic validation;
- Solution Analyzer;
- Progress Engine;
- AI Tutor;
- Adaptive Practice;
- public deployment;
- coding-agent harness.

Avoid implementation detail in this section.

---

## 3. Scope

### In scope

- ...
- ...
- ...

### Out of scope

- ...
- ...
- ...

Do not silently expand scope during implementation.

---

## 4. Actors / entry points

Describe who or what starts the flow.

Examples:

- authenticated student;
- content administrator;
- Django management command;
- internal service;
- scheduled/internal verification.

List relevant entry points:

- page;
- endpoint;
- command;
- service call;
- seed/bootstrap step.

---

## 5. Domain rules and invariants

List all rules that must remain true.

Examples:

- only Progress may mutate long-term mastery/confidence;
- page view must not increase mastery;
- wrong `FINAL_ANSWER` alone must not create a specific misconception;
- public exercise DTO must not expose `answer_key`;
- full reveal prevents `CORRECT_FIRST_TRY`;
- graph must remain acyclic;
- raw input must be preserved;
- unsupported parse state must remain explicit;
- LLM structured output must pass schema validation;
- low-confidence output must not create strong negative evidence.

Add feature-specific rules below:

1. ...
2. ...
3. ...

---

## 6. Interaction / workflow

Describe the end-to-end flow step by step.

Example:

1. ...
2. ...
3. ...

For complex flows, include state transitions.

---

## 7. Data model changes

### New models

| Model | Purpose | Owner domain |
| --- | --- | --- |
| `<Model>` | ... | ... |

### Changed models

| Model | Change | Reason |
| --- | --- | --- |
| `<Model>` | ... | ... |

### Constraints / indexes

- ...
- ...
- ...

### Migration expectations

- Django migration required: Yes | No
- Data migration required: Yes | No
- Fresh DB migration smoke required: Yes | No

If schema changes are involved, implementation is not Done until migration verification passes.

---

## 8. Public vs server-only data

This section is mandatory for exercise, assessment, tutor, or API work.

### Public/client-visible fields

- ...
- ...
- ...

### Server-only fields

- ...
- ...
- ...

For exercise flows, server-only fields normally include:

- `answer_key`;
- `validation_spec`;
- `canonical_solution`;
- secret accepted variants.

Do not expose server-only fields through HTML, JSON, JavaScript fixtures, or template data before reveal.

---

## 9. API / input contract

### Endpoint(s)

```text
METHOD /api/v1/...
```

### Request

```json
{
  "example": "value"
}
```

### Response

```json
{
  "example": "value"
}
```

### Validation errors

| Code | Meaning | HTTP status |
| --- | --- | --- |
| `<CODE>` | ... | ... |

If no HTTP API is involved, describe the relevant service/command contract instead.

---

## 10. Interaction mode contract

If this feature touches exercises, specify the applicable mode:

- `SELF_CHECK`
- `FINAL_ANSWER`
- `STEP_BY_STEP`
- `STRUCTURED_SOLUTION`

Define:

- input schema;
- step schema;
- parser profile;
- reveal policy;
- hint behavior;
- validation path;
- progress/evidence behavior.

A new interaction mode or step type requires explicit spec + validator/test contract.

---

## 11. Validation behavior

Describe deterministic/domain validation first.

### Deterministic validation

- ...
- ...
- ...

### Unsupported / ambiguous behavior

Define what happens when the parser/validator cannot decide.

Do not invent a misconception.

### LLM involvement

- Required: Yes | No
- Purpose: ...
- Structured schema: ...
- Prompt version: ...
- Confidence threshold/gate: ...
- Fallback behavior: ...

LLM output must never be the only source of mathematical truth for supported MVP mathematics.

---

## 12. Progress / evidence semantics

If the feature can affect progress, define the exact knowledge-event behavior.

| Condition | Event | Mastery effect | Confidence effect | Notes |
| --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... |

State explicitly:

- which service emits evidence;
- what source identity is used;
- how duplicate evidence is prevented;
- whether hints/reveal modify evidence;
- whether misconception evidence is strong or weak.

If no progress impact exists, write:

`This feature does not create or mutate knowledge evidence.`

---

## 13. Security / ownership

Describe:

- auth requirement;
- object ownership;
- CSRF/session behavior;
- secret exposure constraints;
- rate limits if AI endpoint;
- payload/step/message size limits if relevant.

---

## 14. Observability

Specify what must be observable.

Examples:

- request/attempt ID;
- exercise/version/mode;
- validation outcome;
- candidate problematic step;
- final taxonomy code/confidence;
- provider/model/prompt version;
- latency/tokens/status;
- hint/reveal flags.

Do not log secrets.

---

## 15. Acceptance criteria

- [ ] ...
- [ ] ...
- [ ] ...
- [ ] ...

Acceptance criteria must describe externally verifiable behavior, not implementation activity.

Bad:

- [ ] Create serializer.

Good:

- [ ] Ordinary exercise GET does not return `answer_key`, `validation_spec`, or `canonical_solution`.

---

## 16. Tests

### Unit

- [ ] ...
- [ ] ...

### Integration

- [ ] ...
- [ ] ...

### API

- [ ] ...
- [ ] ...

### Golden / analyzer eval

- [ ] ...
- [ ] ...

### E2E

- [ ] ...
- [ ] ...

Use only the categories relevant to this feature.

---

## 17. Verification matrix

Run all applicable checks. The current baseline is documented in
`skills/verification/SKILL.md` and executed by `python scripts/verify_repo.py`.
Future checks below apply only after their tooling exists.

### Backend

```bash
python manage.py check
python manage.py test
```

Ruff, mypy, and pytest are not configured in R01. Introduce them through a
dedicated tooling change before making them required or reporting results.

### Database

For schema changes:

```bash
python manage.py makemigrations --check --dry-run
```

Also verify migrations on a fresh PostgreSQL database and run migration smoke.

### Existing content

When content/runtime is affected:

```bash
python manage.py check_content_quality
python manage.py check_site_integrity
python manage.py check_lesson_sources --all
```

### Knowledge graph

- no cycles;
- no self-edge;
- no missing skill codes.

### Exercise contracts

- schema fixtures valid;
- public DTO secret-leak regression passes.

### Frontend

- relevant JS/template/unit checks;
- responsive behavior where applicable.

### LLM / Analyzer

- structured-output validation;
- relevant golden eval subset;
- fake provider paths;
- timeout/error behavior.

---

## 18. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| ... | ... | ... |

Include relevant project risks when applicable:

- LLM misclassification;
- answer leakage;
- over-general exercise model;
- accidental diagnosis from weak evidence;
- scope expansion;
- coupling between Django apps;
- migration/data-loss risk.

---

## 19. Definition of Done

This spec is Done only when:

- [ ] acceptance criteria pass;
- [ ] implementation matches architecture boundaries;
- [ ] migrations exist and pass when required;
- [ ] tests pass;
- [ ] verification matrix passes for affected areas;
- [ ] docs/ADR are updated if behavior/architecture changed;
- [ ] trace summary exists for a significant agent task;
- [ ] no server validation secrets leak;
- [ ] no unrelated files were changed without reason;
- [ ] human gate is completed where required.

---

## 20. Trace / implementation links

- Issue: <link>
- PR: <link>
- Exec plan: <path>
- Trace: <path>
- Demo/screenshot: <link/path>
