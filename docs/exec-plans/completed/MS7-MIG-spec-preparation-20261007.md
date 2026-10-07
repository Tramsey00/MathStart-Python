# EXEC PLAN MS7-MIG-SPEC: Prepare migration specification

- **Status:** Completed specification preparation; user accepted with three corrections, applied in v1.1. Migration implementation gates remain separate.
- **Owner:** User / Руслан; authoring surface Codex.
- **Created / Last updated:** 2026-10-07.
- **Related issue / PR:** None created; this is specification preparation.
- **Related spec:** `output/specifications/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md` and PDF; v1.0 retained as history.
- **Related ADR:** ADR-0001 and current ADR-0002..0005 as inputs. A replacement platform ADR is a proposed MS7-MIG-R01 deliverable, not accepted by this plan.
- **Target milestone:** Preparation for MIG-G0; migration window 07–13 October 2026.
- **Human gate required:** Yes, before adopting the platform change; drafting the specification is authorized.

## 1. Objective

Produce a reviewable Russian specification for migration of the existing project to React and FastAPI without redesign. Match existing task-card structure, assign work to three existing owners, describe branches, dates, verification and adaptations of completed tasks.

## 2. Preconditions and inputs

AGENTS, PRODUCT, ARCHITECTURE, relevant ADRs/contracts/plans/traces, code/tests/migrations, verification skill and the current 114-page v7.1 PDF were read. The pasted request and follow-up discussion define scope: migrate the current version and update the main specification, rather than implement future product domains.

## 3. Scope and boundaries

Read-only repository, GitHub and PostgreSQL audit; author PDF/Markdown and preparation records. No application code/schema/data changes, implementation branches, GitHub mutations, deployment or edits to historical acceptance. Users/Content/Deployment/Harness are analyzed; no domain ownership is changed by drafting.

## 4. Current and target state

Local branch `fix/topics-catalog`, HEAD `a378ab2f01bd76b514833bf692cb4c7425e90ace`, substantial existing dirty content changes. GitHub main `4df7403208312d73adaa34f00f10b025db686fe4` includes merged I03/grades changes and green main CI. Local PostgreSQL is behind that schema. The target for this preparation is a checked artifact, not an installed target runtime.

## 5. Steps and observable results

1. Read current spec and repository contracts; map scope and ownership. **Executed.**
2. Fetch live GitHub main, Issues, PR/review metadata and workflow results; distinguish stale document statuses. **Executed.**
3. Recheck PostgreSQL using a read-only transaction; record aggregate schema/data state without credentials or PII. **Executed.**
4. Write seven-day program, 18 task cards, branch/dependency/review matrix, historical-task mapping and acceptance cases. **Executed.**
5. Generate PDF/Markdown, check task dependency graph/deadline order and render/inspect pages. **Executed; final QA recorded in trace.**
6. Deliver concrete artifact for human review. **User accepted with corrections; all three applied and verified in v1.1. No participant signatures or MIG-G0 execution evidence invented.**

## 6. Database, bootstrap, API and LLM changes

No schema, migration, seed, bootstrap, API or product LLM change in this preparation. DB inspection used explicit read-only isolation and rollback. Proposed target actions are future tasks in the specification. Existing application behavior is preserved.

## 7. Verification plan

Validate all 18 IDs/unique branches, dependency existence, no cycles and deadline ordering. Generate embedded Cyrillic text, TOC/bookmarks; check text margins and render all pages with Poppler for visual QA. Record actual Python/library versions. Runtime verification, fresh migration and E2E execution do not prove a document and are not claimed as run; live source CI is recorded separately from local execution.

## 8. Risks, acceptance and completion

Seven days is a constrained forecast, contingent on source reconciliation, schema/auth/publication compatibility, daily review and usable environments. Codex limits are not a duration guarantee. Historical acceptance is retained; missing approvals are reconciled from evidence, never invented. The artifact requires review before MIG-G0; this active plan is not moved to completed without acceptance.

- [x] Requested scope and detailed task format drafted.
- [x] Live GitHub and read-only DB facts recorded.
- [x] Dependencies/branches/role calendar checked.
- [x] PDF/Markdown generated and QA performed.
- [x] Preparation trace added.
- [x] User acceptance of specification with applied corrections. MIG-G0 implementation prerequisites remain future migration work.

Trace: `docs/agent-traces/MS7-MIG-spec-preparation-20261007.md`.
