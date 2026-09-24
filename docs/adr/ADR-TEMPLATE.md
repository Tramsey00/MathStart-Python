# ADR-XXXX: <Decision title>

- **Status:** Proposed | Accepted | Superseded | Rejected
- **Date:** YYYY-MM-DD
- **Decision owners:** <names / team>
- **Primary owner:** <owner>
- **Related baseline:** MathStart Technical Specification v3.1
- **Related issue/spec/plan:** <links or paths>
- **Supersedes:** <ADR ID or none>
- **Scope:** <affected architecture/product areas>

---

## 1. Context

Describe the concrete situation that requires an architectural decision.

Include only context necessary to understand the decision.

Cover, where relevant:

- current implementation;
- constraints from `PRODUCT.md`;
- constraints from `ARCHITECTURE.md`;
- relevant requirements from the MathStart v3.1 baseline;
- existing technical debt;
- operational constraints;
- migration/data concerns;
- agent/harness implications.

Do not turn this section into a general design document.

---

## 2. Decision

State the accepted/proposed decision precisely.

The decision must be specific enough that a coding agent can distinguish compliant and non-compliant implementations.

Example structure:

- **We will:** ...
- **We will not:** ...
- **Applies to:** ...
- **Effective from:** ...

---

## 3. Rationale

Explain why this option is preferred.

Use concrete engineering reasons such as:

- architectural consistency;
- data ownership;
- migration risk;
- testability;
- explainability;
- security;
- operational complexity;
- delivery scope;
- compatibility with the current Django codebase;
- compatibility with the vertical-slice MVP.

Do not justify a decision only with "simpler", "modern", or "best practice".

---

## 4. Consequences

### 4.1. Positive consequences

- ...
- ...
- ...

### 4.2. Negative consequences / trade-offs

- ...
- ...
- ...

### 4.3. New obligations

List concrete follow-up constraints introduced by the decision.

Examples:

- new migration rule;
- new verification check;
- new API boundary;
- new test;
- new documentation;
- new trace requirement.

---

## 5. Architecture invariants affected

List invariants from `ARCHITECTURE.md` that are:

- preserved;
- strengthened;
- changed;
- newly introduced.

If the ADR changes an existing invariant, explicitly name the old and new behavior.

---

## 6. Data / migration impact

If the decision affects persistence, describe:

- affected models/tables;
- migration sequence;
- compatibility requirements;
- data backfill;
- rollback/forward-fix strategy;
- historical-evidence preservation;
- fresh-install impact.

If there is no data impact, write:

`No schema or persisted-data impact.`

---

## 7. API / contract impact

Describe any changes to:

- public DTOs;
- server-only fields;
- endpoint behavior;
- interaction modes;
- input schemas;
- step schemas;
- reveal policy;
- error codes;
- prompt structured output.

If none, write:

`No public or internal contract change.`

---

## 8. Security / privacy impact

Consider:

- auth/ownership;
- answer-key leakage;
- secret handling;
- LLM data exposure;
- logging;
- rate limiting;
- permissions.

If none, write:

`No material security/privacy impact.`

---

## 9. Alternatives considered

### Alternative A — <name>

**Decision:** Rejected | Deferred

Advantages:

- ...
- ...

Reasons not selected:

- ...
- ...

### Alternative B — <name>

**Decision:** Rejected | Deferred

Advantages:

- ...
- ...

Reasons not selected:

- ...
- ...

---

## 10. Verification

Describe how the repository proves that the ADR is implemented correctly.

Include relevant checks from `skills/verification/SKILL.md`, the current
MathStart verification matrix. Future checks below require configured tooling;
do not report them as passing before implementation.

Examples:

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
```

Where applicable also include:

```bash
python manage.py check_content_quality
python manage.py check_site_integrity
```

And domain-specific checks such as:

- knowledge graph cycle validation;
- exercise secret-leak regression tests;
- prompt/analyzer golden evals;
- API contract tests;
- architecture dependency checks;
- fresh PostgreSQL migration/bootstrap smoke.

---

## 11. Human gate

This ADR requires explicit human review if it changes any of the following:

- architecture boundary;
- breaking DB migration;
- interaction mode semantics;
- public/server exercise boundary;
- reveal policy;
- mastery/confidence formula or thresholds;
- taxonomy with historical meaning;
- prompt policy affecting learning strategy;
- security/auth/deployment;
- external provider/dependency.

**Reviewer:** <name>

**Decision:** Accepted | Changes requested | Rejected | Pending

**Review date:** YYYY-MM-DD

**Notes:** <optional>

---

## 12. Follow-up actions

- [ ] Update `ARCHITECTURE.md` if required.
- [ ] Update `PRODUCT.md` if product behavior changed.
- [ ] Update affected specs.
- [ ] Create/update execution plan if implementation is substantial.
- [ ] Add required migrations.
- [ ] Add/update verification checks.
- [ ] Add/update trace summary.
- [ ] Link issue/PR.
- [ ] Update baseline TЗ only if the change is significant enough to require a new baseline version.

---

## 13. Status history

- **YYYY-MM-DD — Proposed.** <summary>
- **YYYY-MM-DD — Accepted.** <summary>
