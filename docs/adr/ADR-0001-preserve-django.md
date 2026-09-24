# ADR-0001: Preserve Django as the Backend Platform

- **Status:** Accepted
- **Date:** 2026-09-24
- **Decision owners:** MathStart team
- **Primary owner:** Ruslan, technical lead
- **Related baseline:** MathStart Technical Specification v3.1
- **Supersedes:** the earlier pre-v3.1 backend direction based on FastAPI + SQLAlchemy + Alembic
- **Scope:** backend platform, ORM/migrations, MVP frontend integration, migration strategy

---

## 1. Context

MathStart is not a greenfield project.

Before the intelligent-learning MVP begins, the repository already contains a working Django-based educational website with:

- curriculum content for grades 5-9;
- Django models and migrations;
- site/content publishing infrastructure;
- repository-managed curriculum and site content;
- management commands;
- content quality and integrity checks;
- automated tests;
- Django templates and static assets;
- an established local development workflow.

The course project adds a substantial intelligent-learning layer:

- student accounts and onboarding;
- PostgreSQL;
- a unified exercise/attempt model;
- four interaction modes;
- a knowledge graph;
- deterministic mathematical validation;
- Solution Analyzer;
- Progress Engine;
- AI Tutor;
- Adaptive Practice;
- LLM infrastructure and observability;
- public deployment;
- coding-agent harness.

The course requirements demand a sufficiently complex project, use of coding agents / a coding-agent harness, an LLM/agent component with software orchestration, a public GitHub repository, demonstrable architectural/data-flow decisions, deployment, and a working final system.

The backend framework itself is an engineering decision of the team rather than a mandatory course technology.

An earlier architectural direction proposed:

- FastAPI;
- SQLAlchemy;
- Alembic;
- Next.js/React as the primary frontend.

After reviewing the actual repository state, a full backend rewrite would duplicate working infrastructure before the team could begin the new intelligent-learning functionality that defines the course project.

---

## 2. Decision

MathStart v3.1 will **preserve Django as the primary backend platform and application runtime**.

The MVP architecture is:

- **Backend:** Python 3.12+ / Django 5.2+
- **Architecture style:** modular monolith
- **ORM:** Django ORM
- **Schema migrations:** Django migrations
- **Primary target database:** PostgreSQL 16+
- **Current transitional local database:** SQLite until PostgreSQL migration is completed
- **API layer:** Django REST Framework where JSON API endpoints are required
- **Frontend for MVP:** Django Templates + HTML/CSS + progressive JavaScript
- **Mathematical validation:** SymPy + project-owned deterministic/domain validators
- **LLM structured output:** Pydantic
- **LLM integration:** provider abstraction
- **Deployment direction:** Docker-based reproducible path + PostgreSQL + HTTPS
- **CI:** GitHub Actions

A full backend rewrite to FastAPI/SQLAlchemy/Alembic is explicitly **not part of the MVP**.

A separate SPA/Next.js frontend is also **not required for the MVP** and may be introduced only later through a separate ADR if actual frontend complexity justifies it.

---

## 3. Why this decision was made

### 3.1. Preserve existing working value

The current Django codebase already solves important infrastructure problems:

- routing;
- ORM integration;
- migrations;
- admin/tooling;
- templates;
- content publication;
- bootstrap;
- testing;
- project configuration.

Replacing these components would consume implementation time without directly advancing the intelligent learning loop.

### 3.2. Focus semester effort on new course-project complexity

The new complexity should be concentrated in:

- exercise contracts;
- typed solution steps;
- knowledge graph;
- mathematical validation;
- progress/evidence model;
- misconception analysis;
- LLM orchestration;
- AI Tutor;
- adaptive practice;
- observability;
- agent harness.

These are the parts that demonstrate the project's technical depth.

### 3.3. Django supports the required architecture

Django does not prevent MathStart from implementing:

- a modular monolith;
- strict domain boundaries;
- PostgreSQL;
- API endpoints;
- typed service contracts;
- deterministic mathematical validation;
- provider-isolated LLM integration;
- event-based progress;
- background-compatible service design if later required;
- public HTTPS deployment.

Therefore, switching frameworks is not required to satisfy the target architecture.

### 3.4. Lower migration risk

An incremental evolution allows the existing website to remain runnable while new intelligent-learning domains are added.

This reduces the risk of spending a large part of the semester rebuilding existing behavior before the new MVP can be demonstrated.

### 3.5. Better reuse of Django capabilities

The project can reuse:

- Django authentication;
- password hashing;
- sessions;
- CSRF protection;
- Django Admin;
- Django ORM;
- transactions;
- migrations;
- management commands;
- testing infrastructure.

This is especially valuable for internal management of:

- skills;
- prerequisite relationships;
- exercises;
- mistake taxonomy;
- validation metadata;
- pilot seed data.

---

## 4. Consequences

### 4.1. Positive consequences

The team can begin intelligent-learning development immediately instead of first rebuilding the existing site.

The current curriculum and content infrastructure remains usable.

Migration to PostgreSQL can be performed independently from domain-feature development.

Django Admin can serve as an internal content/domain administration interface for the MVP.

The project retains one backend/runtime, reducing operational complexity.

The team can introduce API endpoints only where interactive features require them.

The existing Django template UI can evolve progressively without forcing a frontend rewrite.

---

### 4.2. Negative consequences

The project will not use FastAPI's API-first ergonomics as the primary runtime.

Async LLM/network operations require care because Django's application model is not being selected solely around async workloads.

Domain boundaries must be enforced intentionally because Django makes direct cross-app ORM access easy.

The team must avoid turning the modular monolith into a tightly coupled collection of Django apps.

If frontend complexity grows substantially, server-rendered templates plus progressive JavaScript may eventually become insufficient.

These drawbacks are accepted for the MVP.

---

## 5. Required architectural rules resulting from this ADR

### 5.1. No backend rewrite without a new ADR

Do not introduce FastAPI, SQLAlchemy, Alembic, or another backend stack as a replacement for Django without a new accepted ADR.

A library may not be introduced merely because a coding agent prefers it.

---

### 5.2. PostgreSQL remains the target database

Preserving Django does not mean preserving SQLite as the target database.

The target production database remains PostgreSQL.

The migration path must ensure that:

- existing Django migrations apply successfully;
- repository bootstrap works;
- current content tests/checks work;
- new intelligent-domain models work;
- a clean environment can be created reproducibly.

---

### 5.3. Use Django ORM and Django migrations

New persistent domain models use Django ORM unless a later ADR changes this decision.

Every schema change must have a Django migration.

Already-applied migrations must not be edited merely to repair local state.

---

### 5.4. Preserve the existing content subsystem

Existing `content/`, `curriculum/`, `site_content/`, templates, static assets, publication/bootstrap logic, integrity checks, and quality checks must not be removed as collateral damage from intelligent-domain development.

The new system extends the current MathStart content platform.

---

### 5.5. Separate repository-managed content from runtime user evidence

Repository-managed/bootstrap data may include stable catalogue/domain definitions.

Runtime student evidence includes, for example:

- solution attempts;
- solution steps;
- detected mistakes;
- knowledge events;
- user skill state;
- practice sessions;
- AI conversations.

Content bootstrap must never wipe or overwrite runtime user evidence.

---

### 5.6. Maintain modular-monolith boundaries

Target logical domains include:

- Users
- Content
- Knowledge
- Assessment
- Math Validation
- Progress
- Solution Analyzer
- AI Tutor
- Adaptive Practice
- LLM Infrastructure

Django app boundaries should align with domain ownership where appropriate.

Do not place unrelated models/services into an existing app only because it is convenient.

---

### 5.7. DRF is the baseline API layer

Use Django REST Framework for JSON API endpoints required by interactive functionality.

The project remains primarily server-rendered for MVP.

API serializers must explicitly separate public exercise data from server-only validation data.

---

### 5.8. Frontend remains incremental for MVP

Use:

- Django Templates;
- shared CSS;
- progressive JavaScript;
- `fetch()`/JSON endpoints where needed.

Do not introduce Next.js/React as a mandatory application shell during MVP development without a separate ADR.

A future frontend split is allowed if there is demonstrated need.

---

## 6. Architecture invariants preserved by this decision

This ADR changes the framework choice, not the core product invariants.

The following remain mandatory:

1. AI Tutor must not directly update `UserSkillState`.
2. LLM provider code must not own or mutate progress state.
3. Frontend code must not calculate authoritative mastery/confidence.
4. Opening a topic must not increase mastery.
5. Every automatic progress change must be represented by a `knowledge_event`.
6. LLM structured output that affects domain logic must pass schema validation.
7. Low-confidence/invalid LLM output must not create strong negative misconception evidence.
8. A wrong `FINAL_ANSWER` by itself must not create a specific misconception.
9. `answer_key`, `validation_spec`, and `canonical_solution` must not appear in an ordinary public exercise payload.
10. A full reveal prevents the same attempt from generating `CORRECT_FIRST_TRY`.
11. Knowledge graph self-edges and cycles are invalid.
12. Provider-specific LLM SDK usage must remain in infrastructure/provider code.
13. Raw student input must be preserved separately from normalized representation.
14. Unsupported parsing must remain an explicit state rather than being converted into an invented mathematical error.
15. All schema changes require migrations and verification.

---

## 7. Migration strategy

The architecture evolves incrementally.

### Phase 1 — Harness baseline

Create and adopt:

- `AGENTS.md`;
- `PRODUCT.md`;
- `ARCHITECTURE.md`;
- ADR workflow;
- specs workflow;
- execution-plan workflow;
- agent trace workflow.

### Phase 2 — PostgreSQL readiness

- make DB configuration environment-driven;
- add PostgreSQL dependency/configuration;
- verify current migrations from zero;
- verify current bootstrap on PostgreSQL;
- verify current tests/content checks;
- add PostgreSQL CI coverage.

### Phase 3 — Intelligent-domain vertical slice

Add only the domains needed by the pilot:

- Knowledge;
- Assessment;
- Math Validation;
- Progress;
- Solution Analyzer;
- AI Tutor;
- Adaptive Practice;
- LLM Infrastructure.

Do not attempt to migrate all grade 5-9 content into the intelligent exercise model before the pilot loop is complete.

---

## 8. Alternatives considered

### Alternative A — Rewrite backend to FastAPI + SQLAlchemy + Alembic

**Rejected for MVP.**

Advantages:

- strong API-first model;
- convenient Pydantic integration;
- attractive async API ergonomics;
- explicit service architecture.

Reasons for rejection:

- duplicates existing working backend infrastructure;
- increases migration scope;
- increases risk;
- delays intelligent-learning functionality;
- offers insufficient course-project benefit relative to the rewrite cost.

This alternative may be reconsidered post-MVP only if a concrete need appears.

---

### Alternative B — Keep Django only as a temporary legacy runtime while building a parallel FastAPI backend

**Rejected for MVP.**

This would create two backend stacks, two sets of domain boundaries, duplicated deployment concerns, and a synchronization/migration problem.

The course project does not require this operational complexity.

---

### Alternative C — Django backend + mandatory Next.js SPA immediately

**Rejected for MVP.**

A separate frontend application may become useful later, but introducing it immediately would force:

- API-first conversion of existing pages;
- duplicated routing/navigation concerns;
- authentication/session integration work;
- frontend deployment complexity;
- additional test/build infrastructure.

For the pilot vertical slice, progressive enhancement of the existing frontend is sufficient.

---

### Alternative D — Preserve Django + incremental modular-monolith evolution

**Accepted.**

This provides the best balance of:

- implementation speed;
- architectural clarity;
- reuse of existing work;
- manageable risk;
- alignment with the course requirements;
- focus on the intelligent-learning features.

---

## 9. Verification of this decision

This ADR is considered correctly implemented when:

- the repository continues to run as a Django project;
- new backend domain code uses Django rather than a parallel replacement framework;
- new schema changes use Django migrations;
- PostgreSQL becomes the target DB path;
- existing content/bootstrap behavior remains functional;
- DRF is used for required JSON APIs;
- existing pages can coexist with new interactive MVP features;
- no unrelated full-site rewrite is required for the intelligent vertical slice.

---

## 10. Relationship to MathStart v3.1 baseline

This ADR formalizes the v3.1 engineering direction:

- Django 5.2+ is the retained backend platform;
- PostgreSQL 16+ is the target primary database;
- Django ORM and Django migrations are retained;
- Django templates + HTML/CSS + progressive JavaScript are the MVP frontend;
- a separate SPA/Next.js architecture is POST-MVP and requires an ADR.

The ADR does **not** weaken or change the core intelligent-system requirements:

- four interaction modes;
- deterministic validation;
- server-only validation secrets;
- knowledge graph;
- event-based progress;
- Solution Analyzer;
- AI Tutor;
- Adaptive Practice;
- LLM structured-output validation;
- public deployment;
- coding-agent harness.

---

## 11. Follow-up actions

After accepting this ADR:

1. keep this file in `docs/adr/`;
2. add an ADR template for future decisions;
3. add `specs/SPEC-TEMPLATE.md`;
4. add execution-plan template;
5. add agent-trace template;
6. ensure `PRODUCT.md` and `ARCHITECTURE.md` remain aligned with this decision;
7. create the first active execution plan for the next implementation milestone;
8. do not begin the PostgreSQL/domain implementation until the Harness v1 baseline is committed and reviewed.

---

## 12. Status history

- **2026-09-24 — Accepted.**
  The team chose to preserve Django and evolve the existing MathStart codebase incrementally for v3.1 instead of performing a backend rewrite before the intelligent-learning MVP.
