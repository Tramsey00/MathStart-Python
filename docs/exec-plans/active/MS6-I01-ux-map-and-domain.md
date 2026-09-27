# EXEC PLAN MS6-I01: UX-карта и предметная область

- **Status:** Active — awaiting human review
- **Owner:** Илья
- **Created:** 2026-09-26
- **Last updated:** 2026-09-27
- **Related issue:** #12
- **Related PR:** #11; published baseline before review fixes: `b06f836`
- **Related spec(s):** `specs/exercises/R02-exercise-architecture.md`; `specs/progress/R03-progress-contract.md`
- **Related ADR(s):** `docs/adr/ADR-0001-preserve-django.md`; `docs/adr/ADR-0002-exercise-contract-architecture.md`; `docs/adr/ADR-0003-knowledge-progress-semantics.md`
- **Target milestone:** M0
- **Estimated effort:** 12 hours (W01, 2026-09-25--2026-09-28)
- **Human gate required:** Yes — product walkthrough with Руслан; API-needs review with Владимир

## 1. Objective

Create a reviewable, low-fidelity UX baseline for the student MVP. It must give every SC-01--SC-08 a traceable route, distinguish help/reveal/uncertainty/outage, and hand off only documented public-UI needs to I02/R02.

## 2. Preconditions

- [x] `AGENTS.md`, `PRODUCT.md`, and `ARCHITECTURE.md` read.
- [x] Relevant ADRs and R02/R03 contracts read.
- [x] Existing Content templates, static-resource guidance, catalogue and URL paths inspected.
- [x] I01 acceptance criteria and the v6.0 PDF card read.
- [x] Official primary sources checked with observation limits recorded.

## 3. Scope

### In scope

- UX specification, states matrix, screen map, low-fidelity desktop/mobile wireframes, source notes, and an API-needs handoff.
- Student, guest, and internal-admin boundary documentation only.

### Out of scope

- Runtime code, UI implementation, APIs, DTO changes, migrations, product/architecture/ADR changes, and teacher/parent dashboards.
- Claims about inaccessible third-party screens or product efficacy.

## 4. Current and target state

The current repository is a Django Content site with stable lesson URLs, file-managed curriculum, shared templates and static assets. R02 and R03 specify future contracts but explicitly do not implement runtime APIs or UI. The target is documentation that makes later I02/I04--I14 work traceable without altering those contracts.

## 5. Architecture boundaries

- [x] Harness/docs
- [ ] Users
- [ ] Content
- [ ] Assessment
- [ ] Progress

Allowed direction: `UX docs -> accepted product, architecture, exercise, and progress contracts`.

Forbidden shortcuts: client-side authoritative progress, public validation secrets, a new SPA/framework, teacher/parent flows, or a claim that fixtures are production APIs.

## 6. Planned changes

1. Record the student MVP boundary, terminology, input/display rules, and user-message policy.
2. Map routes and states for all eight scenarios, including guest/auth boundaries, errors, retries, and persistence semantics.
3. Produce low-fidelity desktop/mobile wireframes for onboarding, exercise, progress, and practice.
4. Record observable primary-source notes and explicit non-transfer decisions.
5. Hand off UI-facing contract needs to I02/R02; run documentation checks and request review.

## 7. Database, seed, API, and LLM plan

No schema, seed, API, runtime UI, or LLM/prompt change.

## 8. Verification plan

```powershell
git diff --check
python scripts/verify_repo.py
```

Additionally inspect document links, SC coverage, source-note metadata, SVG well-formedness, and the final diff/stat/status.

## 9. Risks and fallback

| Risk | Mitigation |
| --- | --- |
| Third-party route requires login or is unavailable | Record the exact limitation; infer nothing from it. |
| Later API differs from a documented need | Treat the handoff as a request, not an API contract; reconcile in R02/I02 review. |
| Wireframe is mistaken for final design | Mark every sheet LOW-FIDELITY and omit visual tokens/assets. |

## 10. Human gates and completion

**Gate owners:** Руслан (product/UX) and Владимир (API needs).

Completion requires their walkthrough/review, resolution of blocking comments, and a subsequent status update. This plan remains active until then.

## 11. Published baseline and review fixes (2026-09-27)

- Published branch: `ms6-i01-ux-map`. The team agreed to rename it before PR publication, instead of using the `codex/...` convention. This is a known workflow deviation, not an I01 content defect; do not rename it again.
- PR #11 / issue #12 baseline `b06f836` has successful Harness verification CI (run `36243075680`, verified via GitHub CLI). This later successful verification does not erase the initial local environment failure recorded in the trace.
- Руслан completed UX/product review and requested changes (`CHANGES_REQUESTED`). This pass addresses cross-attempt hint eligibility, topic-specific coverage, publication/review records, acceptance status, and static accessibility claims only.
- Владимир completed API/backend review on 2026-09-27: `APPROVED` for published baseline `b06f836`, no blocking API/backend findings. His non-blocking P3 about `NOT_STARTED` versus absence of assessed evidence was corrected locally after that approval and is not yet published. The approval is not approval of the current local diff. No backend/API contract is changed.
- Technical/documentation checks are recorded separately from approval. Human gate and final acceptance remain pending; the plan stays active until both reviews are accepted.
- Руслан completed the initial UX/product review with `CHANGES_REQUESTED`; repeat UX/product review and final human acceptance remain pending.
- Final-fixes scope: already-credited repeat semantics/message, assessed-reveal return path, current review records, cross-surface states, and the practice-desktop reason label only. Leave fixes local and uncommitted; await separate authorization to publish. No commit, push, PR-body update, or other GitHub mutation.
