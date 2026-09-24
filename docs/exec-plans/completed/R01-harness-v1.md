# EXEC PLAN R01: Baseline Repo Knowledge + Harness v1

- **Status:** Completed
- **Owner:** Руслан
- **Created:** 2026-09-24
- **Last updated:** 2026-09-24
- **Related issue:** [R01 — Baseline repo knowledge + Harness v1](https://github.com/Tramsey00/MathStart-Python/issues/1)
- **Related spec(s):** `PRODUCT.md`, `ARCHITECTURE.md`
- **Related ADR(s):** `docs/adr/ADR-0001-preserve-django.md`
- **Target milestone:** M0 — Agent-ready foundation
- **Planned window:** 2026-09-25 — 2026-10-01
- **Estimated effort:** 20 hours
- **Priority:** P0
- **Human gate required:** Yes

---

## 1. Objective

Turn the existing MathStart Django repository into an **agent-ready repository** that can be used as the operational source of truth by coding agents without relying on previous chat history.

R01 is complete when the repository contains and actually uses:

- `AGENTS.md`;
- `PRODUCT.md`;
- `ARCHITECTURE.md`;
- the initial accepted ADR for preserving Django;
- ADR/spec/exec-plan/trace templates;
- GitHub issue and PR workflow templates;
- a minimal verification skeleton;
- the first observable agent trace;
- a reviewed acceptance baseline.

R01 must not rewrite application functionality or introduce unrelated product features.

---

## 2. Baseline requirements from MathStart v3.1

This plan implements the first Ruslan backlog task from the v3.1 baseline:

**R01 — Baseline repo knowledge + Harness v1**

Expected result:

- agent-ready repo;
- first trace;
- acceptance baseline.

The project uses the agent-first workflow:

`spec -> coding agent -> verification -> trace -> human gate`

The Git repository is the operational source of truth.

Critical architectural decisions must be stored in repository documents rather than existing only in chat.

---

## 3. Preconditions

Before implementation continues:

- [x] stable pre-Harness tag created: `v3.1-pre-harness-baseline`
- [x] baseline tag pushed to GitHub
- [x] dedicated working branch created
- [x] `AGENTS.md` prepared
- [x] `PRODUCT.md` prepared
- [x] `ARCHITECTURE.md` prepared
- [x] ADR-0001 prepared
- [x] ADR template prepared
- [x] feature spec template prepared
- [x] execution-plan template prepared
- [x] trace template prepared
- [x] branch name aligned with GitHub convention: `R01-harness-v1`
- [x] GitHub Issue R01 created: [#1](https://github.com/Tramsey00/MathStart-Python/issues/1)
- [x] issue/PR templates added
- [x] verification skeleton added
- [x] repository documentation consistency checked
- [x] first agent task executed through Harness
- [x] first trace created
- [x] human review completed — Accepted by Ruslan on 2026-09-24

Audit evidence is recorded in `docs/agent-traces/R01-harness-v1.md`.
The local baseline tag exists; the earlier claim that it was pushed was not
independently verified by this local audit. GitHub Issue R01 is
[#1](https://github.com/Tramsey00/MathStart-Python/issues/1). The requested
documentation corrections and subsequent verification are recorded in the
trace. R01 is Completed after Ruslan accepted the final human gate on
2026-09-24.

---

## 4. Scope

### In scope

- repository knowledge hierarchy;
- coding-agent operating rules;
- product and architecture source-of-truth documents;
- ADR workflow;
- feature-spec workflow;
- execution-plan workflow;
- trace workflow;
- GitHub issue/PR workflow;
- minimal verification entry point/skeleton;
- first Harness exercise and trace;
- acceptance baseline for later R02 work.

### Out of scope

- PostgreSQL migration;
- authentication implementation;
- new Django apps for intelligent domains;
- exercise database models;
- four-mode exercise implementation;
- Solution Analyzer implementation;
- Progress Engine implementation;
- AI Tutor implementation;
- Adaptive Practice implementation;
- frontend redesign;
- content migration;
- deployment changes.

These belong to later R/V/I tasks.

---

## 5. Current repository state

The repository is an existing working Django MathStart project.

Relevant established assets include:

- Django runtime;
- `content/` application;
- `curriculum/`;
- `site_content/`;
- Django migrations;
- content bootstrap/publication logic;
- management commands;
- current tests;
- content quality and integrity checks;
- existing templates/static assets.

The current stable pre-Harness baseline is tagged:

`v3.1-pre-harness-baseline`

The architecture decision for v3.1 is to evolve this Django codebase incrementally rather than rewrite it.

---

## 6. Target repository state

At R01 completion, the repository should contain at minimum:

```text
MathStart-Python/
├── AGENTS.md
├── PRODUCT.md
├── ARCHITECTURE.md
│
├── docs/
│   ├── adr/
│   │   ├── ADR-0001-preserve-django.md
│   │   └── ADR-TEMPLATE.md
│   ├── exec-plans/
│   │   ├── active/
│   │   └── completed/
│   └── agent-traces/
│       └── TRACE-TEMPLATE.md
│
├── specs/
│   └── SPEC-TEMPLATE.md
│
├── skills/
│
├── scripts/
│   └── <verification skeleton>
│
└── .github/
    ├── ISSUE_TEMPLATE/
    │   └── <task template>
    └── PULL_REQUEST_TEMPLATE.md
```

The repository must remain runnable as the existing Django application.

---

## 7. Architecture boundaries

R01 primarily affects:

- Harness/docs;
- repository governance;
- GitHub workflow.

It must **not** alter business-domain ownership.

The following architecture rules are already active during R01:

- Django remains the backend;
- no backend rewrite;
- schema changes require Django migrations;
- LLM must not mutate progress directly;
- public exercise payloads must not expose validation secrets;
- content bootstrap must not become a user-data reset;
- unrelated files must not be edited "while we are here".

---

## 8. Planned changes

### Step 1 — Align branch and task identity

**Goal:** Make the working branch match the v3.1 GitHub convention.

Rename the current local branch:

```powershell
git branch -m R01-harness-v1
git branch --show-current
git status
```

Expected branch:

```text
R01-harness-v1
```

Create GitHub Issue:

```text
R01 — Baseline repo knowledge + Harness v1
```

Issue labels should include, where available:

```text
harness
priority:P0
```

---

### Step 2 — Install repository knowledge baseline

**Goal:** Place the already prepared root source-of-truth documents in the repository.

Required files:

```text
AGENTS.md
PRODUCT.md
ARCHITECTURE.md
```

Verification:

- files exist at repository root;
- internal paths are correct;
- Django is consistently described as the v3.1 backend;
- PostgreSQL is consistently described as the target primary DB;
- no stale FastAPI/SQLAlchemy/Alembic baseline remains in these root documents.

---

### Step 3 — Install ADR baseline

**Goal:** Make the framework decision explicit and reviewable.

Required files:

```text
docs/adr/ADR-0001-preserve-django.md
docs/adr/ADR-TEMPLATE.md
```

ADR-0001 must record:

- existing Django codebase;
- decision to preserve Django;
- PostgreSQL target;
- Django ORM/migrations;
- DRF for JSON APIs where required;
- templates + progressive JS for MVP;
- rejected backend rewrite alternatives;
- consequences and follow-up actions.

---

### Step 4 — Install spec / exec-plan / trace workflow

**Goal:** Establish the spec-driven agent workflow required by the v3.1 Harness.

Required files:

```text
specs/SPEC-TEMPLATE.md
docs/exec-plans/active/EXEC-PLAN-TEMPLATE.md
docs/agent-traces/TRACE-TEMPLATE.md
```

At completion, the final plan record is stored as:

```text
docs/exec-plans/completed/R01-harness-v1.md
```

Trace documents must record only observable actions and engineering summaries, never hidden chain-of-thought.

---

### Step 5 — Add GitHub workflow templates

**Goal:** Make issue/PR workflow match the v3.1 change-control rules.

Create:

```text
.github/ISSUE_TEMPLATE/task.md
.github/PULL_REQUEST_TEMPLATE.md
```

Issue template should capture:

- task ID;
- owner;
- goal;
- scope;
- acceptance criteria;
- related spec/ADR;
- expected tests/verification;
- priority/module labels.

PR template should capture:

- Goal;
- Scope;
- Acceptance;
- Tests;
- DB migration;
- API/schema impact;
- Screenshots;
- Agent trace;
- Risks.

---

### Step 6 — Add verification skeleton

**Goal:** Provide one discoverable Harness verification entry point without prematurely rebuilding the project's tooling.

The verification skeleton must:

- document/run the currently valid Django checks;
- fail clearly when a blocking check fails;
- remain extensible for future architecture/knowledge/exercise checks;
- avoid claiming tools are configured when they are not.

Baseline existing-project checks should cover, where currently available:

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py check_lesson_sources --all
python manage.py check_content_quality
python manage.py check_site_integrity
```

Do not add fake `ruff`, `mypy`, or `pytest` success if those tools are not yet configured in the repository.

If v3.1 requires them later, introduce/configure them explicitly in a dedicated change.

---

### Step 7 — Run baseline verification

**Goal:** Prove that adding Harness documentation/governance did not break the existing MathStart runtime.

Run the repository's relevant existing checks.

Record exact outcomes for the first trace.

If a check fails because of a pre-existing baseline issue, do not hide it.
Classify it explicitly as:

- introduced by R01;
- pre-existing;
- environment-specific;
- tooling not yet configured.

R01 cannot be marked complete if it introduces a blocking regression.

---

### Step 8 — First coding-agent Harness exercise

**Goal:** Prove that the Harness is actually usable rather than only documented.

Give the coding agent a bounded repository task such as:

```text
Audit the newly added MathStart Harness v1 against AGENTS.md,
PRODUCT.md, ARCHITECTURE.md, ADR-0001 and the active R01 exec plan.

Do not change application/domain behavior.

Check:
- repository knowledge links and paths;
- contradictions in framework/database/frontend decisions;
- missing Harness artifacts required by R01;
- verification commands against the current repository;
- unrelated/stale instructions.

Make only minimal documentation/Harness corrections that are
supported by the repository and R01 scope.

Run applicable verification and report observable results.
```

The agent must begin by reading `AGENTS.md`.

---

### Step 9 — Create first trace

**Goal:** Capture the first observable Harness run.

Create:

```text
docs/agent-traces/R01-harness-v1.md
```

Trace must include:

- task;
- source documents;
- starting branch/commit;
- changed files;
- important commands;
- failures;
- corrections;
- verification results;
- final diff summary;
- human review status.

Do not include chain-of-thought.

---

### Step 10 — Human architecture gate

**Goal:** Руслан confirms the Harness baseline before merge.

Review:

- root docs;
- ADR-0001;
- templates;
- GitHub workflow;
- verification skeleton;
- first trace;
- actual diff;
- all relevant check results.

Gate result:

The first review produced `Changes requested`; all requested corrections were
completed. Ruslan accepted the final human gate on 2026-09-24. Exact Progress
Algorithm v1 is transcribed in `specs/progress/BASELINE-v1.md`, and the
transcription finding is resolved.

---

## 9. Database / migration plan

R01 introduces **no database schema change**.

Expected command:

```bash
python manage.py makemigrations --check --dry-run
```

must show no unintended model changes.

No migration file should be created as part of R01 unless an unexpected existing issue is explicitly investigated and separately approved.

---

## 10. Seed / bootstrap impact

R01 must not change:

- `curriculum/` data;
- `site_content/` data;
- content bootstrap semantics;
- existing seed/publication behavior.

No runtime user data exists as a Harness responsibility.

---

## 11. API / UI plan

No product API or UI behavior change.

R01 may add only repository/development workflow files.

Existing Django pages must continue working unchanged.

---

## 12. LLM / prompt plan

No product LLM integration is introduced by R01.

The only agent use is the **development coding agent** operating through the Harness.

Product prompts for Solution Analyzer and AI Tutor belong to later tasks.

---

## 13. Tests / checks

The entry point is `python scripts/verify_repo.py`; prerequisites and tooling
limits are documented in `skills/verification/SKILL.md`. The audit passed on
the existing Python 3.10.11 environment, not the accepted Python 3.12+ target.
Target-version verification is a pre-existing environment follow-up, not a
blocker introduced by R01. This documentation task does not change the environment.

### Repository/runtime baseline

- [x] `python manage.py check`
- [x] existing Django tests
- [x] `python manage.py makemigrations --check --dry-run`
- [x] lesson source validation
- [x] content quality validation
- [x] site integrity validation

### Harness checks

- [x] required files exist
- [x] internal document paths resolve
- [x] no contradiction between Django/PostgreSQL/frontend baseline docs
- [x] active exec plan exists
- [x] first trace exists
- [x] GitHub Issue R01 exists: [#1](https://github.com/Tramsey00/MathStart-Python/issues/1)
- [x] PR template exists
- [x] issue template exists

---

## 14. Verification plan

Run narrow structural checks first.

Then run the current application verification.

Recommended order:

```text
1. git status
2. inspect Harness tree
3. python manage.py check
4. python manage.py makemigrations --check --dry-run
5. targeted/existing tests
6. content source checks
7. content quality
8. site integrity
```

If the full test suite is expensive, record targeted checks first, then run the broad suite before declaring R01 complete.

---

## 15. Risks and fallback

| Risk | Detection | Mitigation / fallback |
| --- | --- | --- |
| Harness docs contradict actual repository | agent audit / human review | correct docs before merge |
| Stale FastAPI-era decision remains | repository text search | update only authoritative Harness docs / record exceptions |
| Verification skeleton references unavailable tooling | command failure | detect/configure explicitly; do not fake success |
| R01 expands into product refactor | large/unrelated diff | reject unrelated changes and restore scope |
| Agent edits application code during Harness audit | `git diff` | revert unrelated application changes |
| Context still depends on chat | new-session audit cannot recover task | strengthen repo docs/links |

Rollback for R01 is simple because it should not contain schema/product changes:

- revert Harness commit/PR if necessary;
- stable baseline remains available at `v3.1-pre-harness-baseline`.

---

## 16. Human gates

Required because R01 establishes project architecture/governance rules.

**Gate owner:** Руслан

Review must confirm:

- v3.1 baseline is represented correctly;
- Django preservation ADR is accepted;
- repository knowledge hierarchy is coherent;
- verification results are truthful;
- first trace is usable;
- no product code was changed without reason.

**Gate status:** Approved / Accepted — Ruslan, 2026-09-24

---

## 17. Acceptance criteria

- [x] Branch follows the R01 naming convention.
- [x] GitHub Issue R01 exists: [#1](https://github.com/Tramsey00/MathStart-Python/issues/1)
- [x] `AGENTS.md`, `PRODUCT.md`, `ARCHITECTURE.md` are present and consistent.
- [x] ADR-0001 is present and accepted.
- [x] ADR/spec/exec-plan/trace templates are installed.
- [x] GitHub issue and PR templates are installed.
- [x] Verification skeleton exists and reflects real repository tooling.
- [x] Existing Django application remains healthy.
- [x] No unintended migrations are generated.
- [x] First coding-agent Harness run is completed.
- [x] First trace is saved in the repository.
- [x] Human architecture gate is completed.
- [x] R01 change is reviewable as a coherent PR/diff.
- [x] No known P0 Harness blocker remains.

---

## 18. Definition of Done

R01 is Done only when:

- [x] all acceptance criteria pass;
- [x] repository remains runnable;
- [x] applicable existing checks pass;
- [x] verification results are recorded honestly;
- [x] first trace exists;
- [x] Руслан completes the human gate;
- [x] the final R01 diff contains no unrelated product changes.

---

## 19. Completion summary

Fill after human review.

### Result

Completed. R01 Harness v1 was accepted by Ruslan on 2026-09-24.

### Files/modules changed

- Repository map and source-of-truth documents: `AGENTS.md`, `PRODUCT.md`, and `ARCHITECTURE.md`.
- ADR, spec, execution-plan, trace, and GitHub workflow templates.
- `scripts/verify_repo.py` and `skills/verification/SKILL.md`.
- `specs/progress/BASELINE-v1.md` and `docs/agent-traces/R01-harness-v1.md`.

### Verification

`python scripts/verify_repo.py` passed all six configured groups in the existing
environment. No unintended migrations, content changes, product-code changes,
or database-data changes were introduced by R01.

### Known follow-ups

Expected next Ruslan task after R01:

`R02 — Exercise architecture`

This will formalize:

- four interaction modes;
- public/server exercise contracts;
- `SolutionStep`;
- reveal/hint policy;
- schemas and invariants;
- mock contracts for Vladimir and Ilya.

Python 3.12+ verification remains a separate pre-existing environment follow-up.
It did not block R01 acceptance.

### Links

- Issue: [R01 — Baseline repo knowledge + Harness v1](https://github.com/Tramsey00/MathStart-Python/issues/1)
- PR: pending
- Trace: `docs/agent-traces/R01-harness-v1.md`
