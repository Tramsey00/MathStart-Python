# EXEC PLAN <ID>: <Task / milestone>

- **Status:** Active | Blocked | Completed | Superseded
- **Owner:** <name>
- **Created:** YYYY-MM-DD
- **Last updated:** YYYY-MM-DD
- **Related issue:** <link>
- **Related spec(s):** <paths>
- **Related ADR(s):** <paths or none>
- **Target milestone:** M0 | M1 | M2 | M3 | M4
- **Estimated effort:** <hours/days>
- **Human gate required:** Yes | No

---

## 1. Objective

State the concrete result this plan must produce.

A good objective describes a working repository state, not a list of files to create.

---

## 2. Preconditions

Before implementation starts, confirm:

- [ ] `AGENTS.md` read
- [ ] relevant `PRODUCT.md` sections read
- [ ] relevant `ARCHITECTURE.md` sections read
- [ ] related ADRs read
- [ ] related specs read
- [ ] existing implementation inspected
- [ ] relevant tests inspected
- [ ] relevant migrations inspected if DB is affected
- [ ] acceptance criteria known
- [ ] required verification known

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

The coding agent must not expand scope without updating this plan/spec and getting human review where required.

---

## 4. Current state

Describe the current repository state relevant to the task.

Include:

- current modules/apps;
- current behavior;
- current models/contracts;
- known limitations;
- existing tests;
- known technical debt that directly affects the task.

Do not include unrelated project history.

---

## 5. Target state

Describe what must be true when the plan is complete.

Examples:

- fresh PostgreSQL DB can migrate and bootstrap successfully;
- public exercise DTO and server validation records are separated;
- knowledge graph seed validates with no cycles;
- step-by-step attempt persists typed steps;
- analyzer returns validated taxonomy result;
- adaptive session returns student to origin topic.

---

## 6. Architecture boundaries

List affected domains:

- [ ] Users
- [ ] Content
- [ ] Knowledge
- [ ] Assessment
- [ ] Math Validation
- [ ] Progress
- [ ] Solution Analyzer
- [ ] AI Tutor
- [ ] Adaptive Practice
- [ ] LLM Infrastructure
- [ ] Deployment/CI
- [ ] Harness/docs

Describe allowed dependency direction for this task:

```text
<domain> -> <domain/service>
```

List forbidden shortcuts:

- ...
- ...
- ...

---

## 7. Planned changes

Break the task into minimal coherent implementation steps.

### Step 1 — <name>

**Goal:** ...

**Files/modules likely affected:**

- ...

**Expected behavior:**

- ...

**Verification before continuing:**

```bash
...
```

### Step 2 — <name>

**Goal:** ...

**Files/modules likely affected:**

- ...

**Expected behavior:**

- ...

**Verification before continuing:**

```bash
...
```

### Step 3 — <name>

**Goal:** ...

**Files/modules likely affected:**

- ...

**Expected behavior:**

- ...

**Verification before continuing:**

```bash
...
```

Add more steps only when necessary.

Each step should leave the repository in a coherent state where possible.

---

## 8. Database / migration plan

If no schema change:

`No schema change.`

If schema changes are required, define:

### Model changes

- ...

### Migration sequence

1. ...
2. ...
3. ...

### Data migration / backfill

- ...

### Fresh DB verification

```bash
python manage.py makemigrations --check --dry-run
python manage.py migrate
```

Also verify the full migration chain against a clean PostgreSQL database.

### Historical-data protection

Explain how attempts, knowledge events, detected mistakes, or other historical evidence are preserved.

---

## 9. Seed / bootstrap impact

If repository-managed data changes, define:

- source files;
- seed/bootstrap command;
- idempotency expectations;
- conflict behavior;
- tests.

Explicitly confirm that bootstrap will not overwrite runtime student evidence.

---

## 10. API / UI plan

### API changes

- endpoints:
- serializers/DTOs:
- request schemas:
- response schemas:
- error codes:

### Public/server boundary

- public fields:
- server-only fields:

### UI changes

- templates:
- JavaScript modules:
- interaction states:
- mobile/responsive concerns:

---

## 11. LLM / prompt plan

If no LLM change:

`No LLM/prompt change.`

If applicable, define:

- purpose;
- provider abstraction call;
- structured output schema;
- prompt version;
- fake provider behavior;
- timeout;
- retry policy;
- confidence gate;
- fallback behavior;
- eval subset.

Do not place a live LLM dependency in normal automated tests.

---

## 12. Tests to add/update

### Unit

- ...

### Integration

- ...

### API

- ...

### Golden/eval

- ...

### E2E

- ...

---

## 13. Verification plan

Run narrower checks after each coherent step, then broad verification.

Use `skills/verification/SKILL.md` and `python scripts/verify_repo.py` for the
current baseline. Future checks below apply only after their tooling exists.

### Backend

```bash
python manage.py check
python manage.py test
```

Ruff, mypy, and pytest are not configured in R01. Add them only through a
dedicated tooling change; do not report them as passing or replace the
existing Django test suite with them.

### DB

For schema changes:

```bash
python manage.py makemigrations --check --dry-run
```

Also:

- fresh PostgreSQL migration;
- migration smoke;
- bootstrap/seed smoke if affected.

### Existing content

If relevant:

```bash
python manage.py check_content_quality
python manage.py check_site_integrity
python manage.py check_lesson_sources --all
```

### Domain-specific

- graph validation;
- exercise contract validation;
- public DTO secret-leak test;
- structured-output validation;
- golden eval subset;
- frontend checks;
- Playwright flow when this is a release/major user flow.

---

## 14. Risks and fallback

| Risk | Detection | Mitigation / fallback |
| --- | --- | --- |
| ... | ... | ... |

For migrations, specify whether rollback is safe or forward-fix is preferred.

For external-provider work, specify behavior when the provider is unavailable.

---

## 15. Human gates

Human approval is required before merge if this plan changes:

- architecture boundaries;
- breaking DB migration;
- interaction mode semantics;
- public/server exercise boundary;
- reveal policy;
- progress formula/thresholds;
- taxonomy historical meaning;
- prompt policy affecting teaching behavior;
- security/auth/deployment;
- external dependency/provider.

**Gate owner:** <name>

**Gate status:** Pending | Approved | Changes requested

---

## 16. Completion checklist

- [ ] all planned steps completed
- [ ] acceptance criteria satisfied
- [ ] migrations verified
- [ ] tests pass
- [ ] relevant verification matrix passes
- [ ] spec updated if implementation discoveries changed behavior
- [ ] ADR updated/created if architecture changed
- [ ] trace summary created
- [ ] PR/diff ready for review
- [ ] human gate completed where required
- [ ] no known blocking failures remain

---

## 17. Completion summary

Fill when complete.

### Result

...

### Files/modules changed

- ...

### Verification

- ...

### Known follow-ups

- ...

### Links

- PR:
- Trace:
- Demo:
