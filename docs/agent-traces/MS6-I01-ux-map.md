# TRACE MS6-I01: UX-карта и предметная область

- **Date:** 2026-09-26
- **Task ID:** MS6-I01
- **Owner:** Илья
- **Coding agent / surface:** Codex desktop
- **Related issue:** #12
- **Related spec:** `specs/exercises/R02-exercise-architecture.md`; `specs/progress/R03-progress-contract.md`
- **Related exec plan:** `docs/exec-plans/completed/MS6-I01-ux-map-and-domain.md`
- **Related ADR:** ADR-0001, ADR-0002, ADR-0003
- **PR / commit:** #11 / published baseline `b06f836` before review fixes
- **Human review status:** Руслан: initial CHANGES_REQUESTED, repeat UX/product review pending; Владимир: API/backend APPROVED on 2026-09-27 for published `b06f836`, not the current local diff; final human acceptance pending

## 1. Task

Initial task: produce the MS6-I01 documentation set: UX-spec, states matrix, screen map, low-fidelity desktop/mobile wireframes, source notes, and an I02/R02 API-needs handoff. That initial request prohibited commit/push. The 2026-09-27 review-fix request initially authorized a scoped commit/push, but the user's subsequent STOP instruction supersedes it: prepare and verify local fixes only; no commit, push, PR-body update, or other GitHub mutation. Vladimir's baseline review is now complete; leave the combined local fixes uncommitted pending separate publication authorization and Ruslan's repeat review. Runtime code, API, migrations, PRODUCT, ARCHITECTURE, and ADRs remain out of scope.

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

- `docs/exec-plans/completed/MS6-I01-ux-map-and-domain.md`
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

## 10. Historical verification results (initial unpublished pass)

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
| Product/API reviews | Final acceptance pending | Vladimir approved baseline `b06f836`; his P3 is fixed locally after approval. Ruslan's repeat UX/product review is pending. |

## 12. Remaining risks / follow-ups

- Руслан completed the product walkthrough and requested changes; approval after these fixes remains pending.
- Владимир completed API/backend review on 2026-09-27: `APPROVED`, no blocking findings, for published baseline `b06f836`. His non-blocking P3 on `NOT_STARTED` / no assessed evidence was fixed locally after approval and remains unpublished; this does not establish approval of the current local diff.
- The final route and error-envelope names remain implementation decisions of later scoped tasks.
- The initial bundled-interpreter failure remains historical evidence; later published-baseline CI passed. Current review-fix verification is recorded separately below.

## 13. Harness improvement

**No.** No harness weakness was observed; external-source limitations were recorded directly.

## 14. Human review

**Reviewer:** Руслан (product/UX); Владимир (API needs)

**Status:** Руслан completed initial UX/product review with `CHANGES_REQUESTED`; repeat UX/product review remains pending. Владимир completed API/backend review on 2026-09-27 with `APPROVED` and no blocking findings for `b06f836`. His non-blocking P3 was corrected locally after approval, not yet published. Current local diff is not claimed approved. Final human acceptance remains pending.

## 15. Final status

`INCOMPLETE`

Documentation artifacts are produced; Vladimir's baseline API/backend approval is recorded, while Ruslan's repeat UX/product review and final human acceptance remain pending. Technical/documentation PASS entries are not final acceptance or approval of the local diff.

## 16. PR #11 review-fix pass (2026-09-27)

- Issue #12; PR #11; clean starting tree at published baseline `b06f836c5f8373834f26076172780d6c21ee99a4` on `ms6-i01-ux-map`.
- Branch was renamed by team agreement before publication, instead of the `codex/...` convention. This is a known workflow deviation, not an I01 content defect. No branch switch, rename, merge, or issue/PR closure is part of this pass.
- GitHub CLI confirmed successful baseline Harness verification CI, run `36243075680`, completed 2026-09-26. The PR body records seven passing checks, 15 Django tests and 18 R03 tests. These later results do not replace the initial local environment failure above.
- Руслан's initial UX/product review is `CHANGES_REQUESTED`; repeat review remains pending. Владимир's API/backend review of `b06f836` was `APPROVED` on 2026-09-27 with no blocking findings. His non-blocking P3 was fixed locally after approval and is unpublished; current local diff approval is not claimed. Final human acceptance remains pending.
- Clarified separately retained hint/reveal exposure for user + exercise version and server-determined eligibility of later attempts. Substantial hint assistance cannot be bypassed by starting a new attempt. API-needs remains a handoff, not a new backend contract.
- Corrected both progress sheets to illustrate coverage of the displayed topic's mapped skills, not the full pilot.
- Replaced the static onboarding keyboard-verification claim and clarified mobile focus intent; runtime accessibility must be verified during implementation.
- Initial CLI/Python access inside the sandbox failed; approved execution outside the sandbox restored access to GitHub CLI and the configured project environment. A discovery `rg` call with Windows wildcard paths failed and was rerun with directory-based searches; neither failure is a product defect.

### Verification before the final-fixes pass

Interpreter: `.venv/Scripts/python.exe`, Python 3.14.7; Django 5.2.16. The historical untracked-file whitespace limitation no longer applies to these tracked review-fix files. This pass checks the working diff only; staged verification and commit/push are deferred until separately authorized.

| Command / check | Result | Evidence |
| --- | --- | --- |
| `.venv/Scripts/python.exe scripts/verify_repo.py` | PASS | All seven checks passed; details below. |
| `python manage.py check` | PASS | No issues. |
| `python manage.py makemigrations --check --dry-run` | PASS | No changes detected. |
| `python manage.py check_lesson_sources --all` | PASS | 263 lessons match the database. |
| `python manage.py check_content_quality` | PASS | 281 pages, 840 SVG resources, zero problems. |
| `python manage.py check_site_integrity` | PASS | 281 materials, 1685 links/resources, zero critical problems. |
| `python manage.py test` | PASS | 15 tests. |
| `python -m unittest discover -s tests -p test_r03_contract.py` | PASS | 18 tests. |
| PowerShell XML parsing of `docs/ux/wireframes/*.svg` | PASS | All eight files parse and have an SVG root. |
| PowerShell local Markdown-link audit | PASS | 13 relative link targets resolve across the I01 UX documents, plan, and trace. No repository Markdown-link checker is configured. |
| Accessibility wording audit | PASS | All eight SVGs and related I01 documents checked; keyboard/focus verification is an implementation requirement, not a completed runtime check. |
| `git diff --check` | PASS | Tracked working-tree diff; repeated after trace update. No staging performed. |
| Scope / diff audit | PASS | Only 11 I01 documentation/SVG files modified; no backend/API contracts, runtime files, or migrations changed. |

No commit, push, or GitHub mutation was performed. PR-body acceptance remains unchanged; after authorized publication of the fixes, replace `- [x] acceptance criteria from the issue/spec are satisfied` with `- [ ] acceptance criteria from the issue/spec are satisfied` while Ruslan's final approval is pending, leaving the pending human-gate checkboxes unchanged. Await explicit authorization for the combined publication pass; final acceptance is still pending.

## 17. Minimal final-fixes pass

- Scope: six files only in this pass: UX spec, states matrix, screen map, active plan, this trace, and `practice-desktop.svg`. Earlier local review fixes are preserved.
- Added server-authoritative already-credited repeat semantics and learner message: no repeated positive evidence/mastery/confidence gain merely from another success, even without hint/reveal; safe next actions remain available.
- Added assessed-source reveal return to topic without restoring eligibility of the exposed version.
- Updated publication/review records for issue #12, PR #11, baseline `b06f836`, Vladimir's baseline approval and subsequent unpublished P3 fix, and Ruslan's pending repeat review. Historical environment failure above is preserved.
- Added explicit loading, empty, retry, offline/degraded, content and unsupported applicability for the UI surfaces, including progress and history; no endpoint/DTO changes.
- Shortened only the desktop practice reason label to «Причина: нужен для текущей темы».
- Final verification: `.venv/Scripts/python.exe scripts/verify_repo.py` PASS, all seven checks (Python 3.14.7 / Django 5.2.16): system check clean; no migration changes; 263 lesson sources match; content quality 281 pages / 840 SVG / zero problems; integrity 1685 links/resources / zero critical problems; 15 Django tests and 18 R03 tests passed.
- Documentation checks: all eight SVGs parse as XML; 13 local Markdown links resolve. Mermaid 11.12.0 parse and render PASS in headless Chrome 154.0.8037.58. Browser geometry confirms the practice reason ends at x=329.953125 inside the card's right boundary x=410. These are static-document checks, not runtime accessibility/E2E verification.
- Consistency audit: all five requested findings addressed; already-credited repeats and exposed versions remain distinct, safe continuation does not reset eligibility, empty assessed coverage does not derive skill status, and cross-surface retries/offline states do not invent server acceptance. Only the six scoped files changed during this pass; cumulative uncommitted fixes affect 12 I01 files. `git diff --check` PASS, repeated after this trace update; staging remains empty.
- Technical verdict: READY FOR COMMIT/PUSH AND RE-REVIEW once separately authorized; this is not final human acceptance. No staging, commit, push, merge, GitHub mutation, runtime/backend/API contract change, or I02 work.
