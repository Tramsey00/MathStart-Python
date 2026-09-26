# TRACE MS6-I01: UX-карта и предметная область

- **Date:** 2026-09-26
- **Task ID:** MS6-I01
- **Owner:** Илья
- **Coding agent / surface:** Codex desktop
- **Related issue:** Not supplied
- **Related spec:** `specs/exercises/R02-exercise-architecture.md`; `specs/progress/R03-progress-contract.md`
- **Related exec plan:** `docs/exec-plans/active/MS6-I01-ux-map-and-domain.md`
- **Related ADR:** ADR-0001, ADR-0002, ADR-0003
- **PR / commit:** None — commit and push were not requested
- **Human review status:** Pending

## 1. Task

Produce the MS6-I01 documentation set: UX-spec, states matrix, screen map, low-fidelity desktop/mobile wireframes, source notes, and an I02/R02 API-needs handoff. Do not change runtime code, API, migrations, PRODUCT, ARCHITECTURE, ADRs, commit, or push.

## 2. Inputs used

- `AGENTS.md`, `PRODUCT.md`, `ARCHITECTURE.md`
- `.local-docs/MathStart_TZ_v6.0_2026-09-25.pdf`, especially SC-01--SC-08 and I01
- ADR-0001 through ADR-0003
- R02 exercise and R03 progress contracts and fixtures inventory
- `docs/architecture.md`, `docs/lesson-theme.md`, existing templates/static-path inventory
- Official first-party sources listed in `docs/ux/MS6-I01-source-notes.md`

## 3. Initial repository state

```text
Branch: codex/ms6-i01-ux-map
Start commit: e410a4e29de2eb800b3325667df94b200bdae22b
Working tree: clean
Existing UX-document directory: absent
```

## 4. Files changed

### Added

- `docs/exec-plans/active/MS6-I01-ux-map-and-domain.md`
- `docs/ux/MS6-I01-ux-spec.md`
- `docs/ux/MS6-I01-states-matrix.md`
- `docs/ux/MS6-I01-screen-map.md`
- `docs/ux/MS6-I01-wireframes.md`
- `docs/ux/MS6-I01-source-notes.md`
- `docs/ux/MS6-I01-api-needs.md`
- eight low-fidelity SVG wireframes in `docs/ux/wireframes/`
- this trace

### Modified / deleted

None.

## 5. Commands / tools executed

```powershell
rg --files docs templates static content curriculum site_content
git status --short --branch
git rev-parse HEAD
git diff --check
python scripts/verify_repo.py
```

Official-source inspection used the Khan Academy, IXL, Яндекс Образование, and GeoGebra primary URLs recorded in source notes.

## 6. Implementation summary

- Added documentation-only UX artifacts covering every required scenario and explicit safe feedback/help/reveal/outage distinctions.
- Added eight SVG low-fidelity sheets for the four required surfaces at desktop and mobile breakpoints.
- Kept R02/R03 as authoritative contracts; the API-needs artifact makes review questions rather than changing an API.
- Applied one review-requested consistency pass: transport retry is separated from a new attempt after completed evaluation; reveal/exposure eligibility is user + exercise-version scoped across attempts; `INDETERMINATE` is distinct from wrong/unsupported; help levels are bounded at 1--3 with 0 meaning no help; practice stop conditions match the v6 requirement; and guest theory is separated from authenticated personal attempt work.
- Reworked learner-visible wireframe copy into Russian while keeping canonical technical labels only in explicit `DEV` annotations. Added the 360/768/1440 implementation baseline without creating a third wireframe set.

## 7. Observable failures / incidents

| Failure / limitation | Detection | Impact |
| --- | --- | --- |
| Khan Academy Math page had no readable extracted content in the inspection tool | Official URL inspection | Source notes use only the readable official About page plus state this limitation. |
| IXL diagnostic URL redirected to a regional catalogue | Official URL inspection | No diagnostic-flow behavior is claimed. |
| Учи.ру redirected to an old-browser page | Official URL inspection | Excluded from the final four observable-source set. |

## 8. Root cause summary

The source limitations are external page rendering/redirect behavior, not repository defects.

## 9. Corrections made

- Replaced the inaccessible Учи.ру candidate with GeoGebra, whose official public page was readable.
- Recorded non-observation explicitly instead of inferring authenticated or redirected flows.
- Added a separately observed official IXL UK public Diagnostic landing page while preserving the original redirect fact and explicitly excluding authenticated session/result UI claims.
- Added the directly observed official public Яндекс Учебник page while keeping authenticated cabinet, concrete task, result, and progress screens outside the evidence.

## 10. Verification results

| Check | Result | Detail |
| --- | --- | --- |
| SVG XML parsing | PASS | All eight `docs/ux/wireframes/*.svg` files parse successfully. |
| Local Markdown links | PASS | UX-document relative links resolve. |
| SC-01--SC-08 coverage | PASS | Each scenario has an explicit row in the states matrix and a route in the screen map. |
| Required state/scope audit | PASS | Documents explicitly distinguish help/reveal/confirmed/uncertain/unsupported/outage and exclude teacher/parent scope. |
| `git diff --check` | LIMITED: tracked diff only | The command produced no findings in the tracked diff. These artifacts are untracked, so this command did not check their contents and does not establish a whitespace PASS for them. After authorized staging, `git diff --cached --check` must be run before commit; staging and commit were not performed in this task. |
| `python scripts/verify_repo.py` | ENVIRONMENT FAILURE | Bundled Python lacks Django, so system check, migration, content checks, and Django suite could not start. The independent R03 contract suite passed: 18 tests. |

The revision-pass consistency audit also confirmed: `wrong final` does not name a misconception; `confirmed`, `uncertain`, `unsupported`, and `indeterminate` remain distinct; hint is not reveal; exposure persists across attempts for user + exercise version; retry does not create evidence; Tutor outage is not deterministic-validation outage; `NOT_STARTED` is presented as «Ещё не проверено» rather than lack of knowledge; progress/status remain server-provided; and the guest route ends before personal attempt work.

No runtime behavior was changed; browser E2E is N/A for this documentation-only increment.

## 11. Acceptance criteria result

| Acceptance criterion | Result | Evidence |
| --- | --- | --- |
| All SC-01--SC-08 have a route | PASS | states matrix and screen map |
| Help/reveal/uncertainty distinct | PASS | UX spec, states matrix, exercise wireframes |
| No teacher/parent scope | PASS | UX spec and plan scope |
| Desktop/mobile sketches present | PASS | eight SVGs parsed as XML |
| Product/API reviews prepared | Pending | API-needs handoff |

## 12. Remaining risks / follow-ups

- Руслан must conduct the product walkthrough.
- Владимир must review the API-needs handoff before I02/R02 reliance.
- The final route and error-envelope names remain implementation decisions of later scoped tasks.
- The configured repository verification needs an interpreter/environment with Django before its six blocked groups can be rerun.

## 13. Harness improvement

**No.** No harness weakness was observed; external-source limitations were recorded directly.

## 14. Human review

**Reviewer:** Руслан (product/UX); Владимир (API needs)

**Status:** Pending

## 15. Final status

`INCOMPLETE`

Documentation artifacts are produced, but the required human walkthrough and API-needs review remain pending.
