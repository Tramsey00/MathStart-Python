# MathStart repository map

## Purpose

MathStart extends an existing Django mathematics site with an intelligent
learning layer. Work through `spec -> agent -> verification -> trace -> human
review`. Recover context from the repository, not previous chats.

## Read and discover

1. Read `AGENTS.md`, `PRODUCT.md`, then `ARCHITECTURE.md`.
2. Read relevant accepted decisions in `docs/adr/` (start with
   `ADR-0001-preserve-django.md`), contracts in `specs/`, and the active task in
   `docs/exec-plans/active/`.
3. Inspect relevant code, tests, and migrations before editing. Use `README.md`
   for setup and `docs/architecture.md` for the existing content pipeline.
4. Use `skills/verification/SKILL.md` for checks and failure reporting.

Documents define scope and ownership; tests and migrations provide executable
evidence. Surface conflicts or missing essential contracts instead of inventing
architecture. Templates live beside ADRs, specs, active plans, and traces.

## Current and target platform

Current runtime: Django, Django ORM/migrations, SQLite, Django Templates, and
shared HTML/CSS/JavaScript. `requirements.txt` and `config/settings.py` describe
what is installed; the `content/` app owns the existing site.

Accepted v3.1 target: Python 3.12+, Django 5.2+, PostgreSQL, Django Templates
with progressive JavaScript, DRF where APIs are needed, deterministic/SymPy
validation, Pydantic structured outputs, and isolated LLM providers. Future
domains and tooling are introduced in scoped tasks, not implied to exist now.

## Critical invariants

- Preserve the modular monolith and domain ownership in `ARCHITECTURE.md`.
  Content owns topic-to-skill mappings and depends on Knowledge for them.
- Only Progress changes long-term knowledge state, through validated
  `ProgressEvent` evidence. Reading a topic never increases mastery.
  Tutor, Analyzer, frontend, and LLM providers must not directly mutate it.
- Prefer deterministic mathematical validation. Preserve raw input separately
  from normalized data; unsupported parsing is not a misconception.
- Schema-validate LLM outputs that affect domain decisions. Malformed or
  low-confidence output must not produce strong negative misconception
  evidence. Keep provider SDKs in infrastructure and prompts versioned.
- Keep exercise answers and validation secrets server-side until explicit
  reveal. A wrong final answer alone does not identify a misconception; full
  reveal prevents `CORRECT_FIRST_TRY`. Record evidence-relevant hints/reveals.
  See the architecture's current-baseline section for legacy self-checks.
- Preserve the four exercise modes and typed ordered solution steps. New modes
  or changed semantics need a spec, validation/tests, and architectural review.
- Skill codes are stable; topics and skills differ. Prerequisites point from
  prerequisite to dependent and have no self-edges or cycles.
- Bootstrap must not overwrite historical user evidence. Never commit or log
  secrets; normal automated tests must not require a live LLM.

## Scope and migrations

Preserve existing `content/`, `curriculum/`, `site_content/`, publication tools,
templates, and tests. Prefer a complete pilot slice to broad rewrites; do not
convert all lessons or add technologies/features outside `PRODUCT.md` scope.
Do not replace Django or introduce a separate frontend without an accepted ADR.
Do not delete content or historical evidence without explicit authorization.

Every schema change requires a reviewed Django migration, consistency checks,
applicable migration/fresh-install verification, and tests. Do not edit applied
migrations to repair local state; prefer additive changes and archive evidence-
referenced objects. Details belong in `ARCHITECTURE.md` and the task plan.

## Task workflow and records

1. Inspect repository state, required sources, affected boundaries, and acceptance
   criteria. Use an execution plan for substantial work.
2. Make small scoped changes; preserve behavior unless the spec changes it.
   Update relevant tests/contracts and never weaken validation to pass checks.
3. Run required verification, investigate failures, and fix only in-scope issues.
   Record exact results and classify pre-existing/environment failures honestly.
4. Update the trace and prepare the result for the required human gate.

| Artifact / gate | When required | Location |
| --- | --- | --- |
| ADR | Significant platform, ownership/dependency, persistence, API, exercise, progress, graph, LLM-trust, or deployment decision changes | `docs/adr/ADR-TEMPLATE.md` |
| Spec | New/changed feature or domain contract, including exercise, evidence, or LLM behavior | `specs/SPEC-TEMPLATE.md` |
| Exec plan | Substantial work across domains, schema/migration sequences, new subsystems, public contracts, progress/LLM semantics, or multiple iterations | `docs/exec-plans/active/EXEC-PLAN-TEMPLATE.md` |
| Trace | Significant agent task; observable actions/results only, no private chain-of-thought | `docs/agent-traces/TRACE-TEMPLATE.md` |
| Human gate | Architectural/product decisions, breaking migrations, security/deployment/provider changes, or any gate required by the task/ADR/spec | Relevant task plan and PR template |

Move active plans to `docs/exec-plans/completed/` only after completion and
human acceptance. Keep detailed verification, observability, and record formats
in the linked architecture, skill, and templates rather than duplicating them here.

## Verification and Definition of Done

Run from the configured project environment:

```bash
python scripts/verify_repo.py
```

Use the verification skill for relevant additional checks. Report actual tooling
and interpreter versions; never claim checks passed when unconfigured or skipped.

Done requires the requested result, preserved scope/invariants, required
migrations and meaningful tests, passing relevant checks, updated contracts and
trace, no secrets or unrelated changes, and completed human gates. The result
must be understandable from repository artifacts. Do not declare completion
while required checks fail or acceptance remains outstanding.
