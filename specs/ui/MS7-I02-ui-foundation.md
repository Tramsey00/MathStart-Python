# SPEC MS7-I02: UI foundation and fixtures

- **Status:** PR OPEN / CHANGES_REQUESTED (pre-fix reviews); correction published / CI SUCCESS; Task Approvals PENDING
- **Owner:** Ilya (Илья)
- **Reviewer / Task Approver:** Ruslan and Vladimir
- **Canonical issue:** [#21 - MS7-I02: UI foundation and fixtures](https://github.com/Tramsey00/MathStart-Python/issues/21)
- **Branch:** `ms7-i02-ui-foundation`
- **Baseline SHA:** `428ece726918f635549fc7dd8fdd352f799c3308`
- **PR:** [#22](https://github.com/Tramsey00/MathStart-Python/pull/22), OPEN
- **Final correction SHA:** `e471efc0b1a6b4af9baf1401e49311a203f12450`
- **Correction CI:** [37060459060](https://github.com/Tramsey00/MathStart-Python/actions/runs/37060459060), SUCCESS
- **Published pre-fix HEAD:** `931f83af01ea44c880ab94c5f7c134a29613a332`
- **Related ADRs:** ADR-0001/0002/0003 and the accepted MS7-R02A addendum package
- **Exec plan:** [MS7-I02](../../docs/exec-plans/active/MS7-I02-ui-foundation.md)
- **Trace:** [MS7-I02](../../docs/agent-traces/MS7-I02.md)
- **Milestone Gate:** G3; I02 does not independently close G3
- **Acceptance deadline:** 2026-10-05, from the revised Section 20 calendar
- **Last updated:** 2026-10-02

## 1. Goal

Provide a reusable Django UI foundation for later student screens: shared
templates/components, design tokens, safe versioned fixtures, loading/error/empty
states, schema dispatch and baseline keyboard/mobile accessibility.

Preparation and three implementation/docs commits were published through PR #22;
`931f83af01ea44c880ab94c5f7c134a29613a332` is the historical pre-fix head.
The correction is committed and published as `e471efc0b1a6b4af9baf1401e49311a203f12450`.
GitHub API confirms [run 37060459060](https://github.com/Tramsey00/MathStart-Python/actions/runs/37060459060)
completed SUCCESS for this correction head / PR merge-ref against main
`fa0d87033113a30abc6e9de2acc174b01e98d9db`. Pre-fix run 37027103585 remains historical.
PR #22 is OPEN and MERGEABLE at the synchronization snapshot. Both existing reviews
are CHANGES_REQUESTED on the pre-fix SHA; Ruslan/Vladimir Task Approvals are PENDING.
The user authorized records/PR description synchronization and repeat review.
This documentation-only follow-up preserves all tested product/test/fixture/image
bytes; its subsequent head/CI must be distinguished from the correction run.
No human approval, merge or task/G3 closure is claimed.

## 2. Why this belongs in MathStart

The v7.1 MS7-I02 card (Section 24, page 68) covers NFR-13 (browser/mobile),
NFR-16 (keyboard/accessibility) and FR-04 (PublicExerciseDTO). It prepares shared
UI assets for MS7-I03, MS7-I04 and MS7-I08 without replacing the Django site.

### Normative source and accepted inputs

The sole normative source of new MS7-I02 requirements is the full
`.local-docs/MathStart_Technical_Specification_v7_1_SECTION20_PARALLEL_DEADLINES.pdf`.
Its filename does not limit its contents to Section 20. The path is local;
availability through GitHub is not claimed. Do not copy or publish the PDF as part
of this task. Specification v6 is not an implementation requirements source.

```text
Canonical PDF SHA-256
e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd

MS7-R02A OpenAPI SHA-256
133aae117333e66b40662ec4fdb47fc02ee08e7aeecbbd9cbb200d5468ca7362

MS7-R02A package manifest SHA-256
1b4a4b43df6052db5d91840cb2e748745cafb0529a766272d5a29b2b88e6dbac
```

Applicable v7.1 sections: 5-7, 11, 15-17, 20-21, 24-25; broader acceptance routes
in Section 27 apply only within this foundation's scope. Section 20.6 states that
the calendar layer was revised; older card NORMAL/EARLY dates do not override
the 2026-10-05 I02 deadline.

| Dependency | Accepted input and use |
| --- | --- |
| HARD: MS6-I01 | Accepted/frozen UX handoff: [UX spec](../../docs/ux/MS6-I01-ux-spec.md), [states matrix](../../docs/ux/MS6-I01-states-matrix.md), [screen map](../../docs/ux/MS6-I01-screen-map.md), [wireframes](../../docs/ux/MS6-I01-wireframes.md), [API needs](../../docs/ux/MS6-I01-api-needs.md). v7.1 Section 2 records PR #11 / merge `861433a6`. No reimplementation or status housekeeping. |
| CONTRACT: MS7-R02A | Accepted by Ruslan, explicitly confirmed by the user; [HTTP contract](../api/MS7-R02A-http-eligibility.md), [OpenAPI](../api/openapi-v1.json), [DTO schemas](../api/schemas/dto-v1.schema.json), [policy](../api/http-policy-v1.json), [package manifest](../api/candidate-manifest-v1.json) and offline fixtures. |
| HANDOFF | None. |
| INTEGRATION | None; no upstream runtime API is needed for I02 task-specific acceptance. |

Acceptance of upstream comes from v7.1/user confirmation, not stale document
labels or mere hash equality. All 17 R02A manifest pins match current bytes at
preparation. Its frozen package remains unchanged. R02 and ADR-0001/0002/0003
remain accepted compatibility inputs, not permission to expand this task.

## 3. Scope

### In scope

- A shared extensible Django shell preserving existing Content pages,
  SEO/canonical metadata, authored content, catalogue and lesson resources.
- Minimal reusable button, labelled field/error, card and state components.
- CSS design tokens and isolated foundation styles.
- Loading, recoverable error with a demonstration retry, successfully received
  empty data and ordinary content. Error is never interpreted as empty success.
- Foundation dispatch for the four accepted modes using public mode/schema;
  controlled unsupported-shape presentation, without a complete renderer.
- Versioned synthetic UI fixtures with provenance and R02A compatibility.
- A minimal GET-only fixture gallery in the existing `content` app, available
  only under `DEBUG=True`, with permanent fixture-only marking.
- Keyboard/accessibility baseline, mobile smoke at 360/768/1440 px,
  Python/Django tests and available manual browser evidence.

### Out of scope

- Complete four-mode rendering (MS7-I04), solution editors or student workflows.
- Browser mathematical assessment, parser/checker, verdicts, normalization or
  authoritative mastery/confidence/eligibility calculations.
- Backend APIs, models, migrations, seeds/bootstrap or historical-data changes.
- Real auth/onboarding, Attempt lifecycle, submission, hints/reveal, Tutor,
  progress, diagnostics or practice flows.
- Business behavior for pending/degraded/conflict/unauthorized and other future
  flows; extension points do not implement these behaviors.
- Node/Playwright/frontend toolchain, new CI, dependency changes, a separate
  preview server or full cross-browser/accessibility audit.
- Bulk lesson conversion, SPA/stack replacement, deployment, live providers,
  Harness changes or housekeeping of frozen upstream status records.

## 4. Actors / entry points

The local developer/reviewer uses `GET /__ui__/foundation/` through the
existing Django server. It is a demonstration surface, not a student endpoint.
It reads only allowlisted repository-authored synthetic fixtures. It neither
loads private user data nor accepts arbitrary fixture-file paths.

Gallery/fixture scripts are not attached to ordinary Content pages. The development
route is implemented; legacy rendering is covered by no-database Django tests.
Published home/catalogue/lesson browser comparison now passes after the user's
runtime migrate/bootstrap; the gallery remains isolated from these pages.

## 5. Domain rules and invariants

1. Preserve Django Templates and existing Content ownership and publication.
2. Only Progress can change long-term knowledge state; this task writes none.
3. Dispatch is based on declared public mode/schema, never statement guessing.
4. Schema validation checks shape, never mathematical truth.
5. Preserve raw demonstration input in memory across loading/error presentation;
   do not normalize it or label it as saved on the server.
6. Fixture-only marking remains visible, including empty/error presentations.
7. Public artifacts contain no checker or hidden answer/reveal content.
8. No new mode, step type, HTTP status, DTO field or eligibility policy is added.
9. Do not infer independence from a new Attempt or reset cross-attempt exposure.
10. Existing legacy authored SELF_CHECK answers remain the compatibility baseline
    explicitly preserved by v7.1 Section 11; new components do not inherit it.

## 6. Interaction / workflow

1. A local GET renders the gallery using reusable templates and safe fixtures.
2. Component examples show ordinary content, loading, error and confirmed empty.
3. Demonstration retry changes presentation only; it sends no student mutation.
4. A public exercise descriptor selects a foundation slot after shape checks.
5. Unsupported descriptors receive an explanation and no guessed form/verdict.
6. The reviewer exercises keyboard navigation and the three mobile widths.

No submitted result, server save, reveal or progress gain is simulated as real.

## 7. Data model changes

No schema change. No new/changed models, constraints, indexes, data migration or
backfill. Task-specific fresh/upgrade/locking migration tests are N/A.
The canonical migration consistency check remains part of baseline verification.

## 8. Public vs server-only data

Allowed data consists of reviewed public exercise metadata, non-secret field
shape descriptors, presentation state/copy and synthetic demonstration strings.
UI state projections are identified as projections, not fabricated wire DTOs.

Exclude `answer_key`, `validation_spec`, `canonical_solution`, checker/reference
solution, secret accepted variants, correctness-bearing metadata and equivalent
prose/data. Do not deliver the complete R02A `http-exchanges-v1.json`: it contains
explicit reveal responses and solutions from completed attempts. Do not include
reveal content, completed solution drafts or answer-equivalent hints in I02 assets.

## 9. API / input contract

No `/api/v1/` endpoint or serializer is implemented or changed. The
DEBUG-only gallery is GET-only; non-GET requests must not invoke a mutation.
It is absent from routing under `DEBUG=False`.

Wire DTO examples conform to accepted R02A schemas. UI state fixture version and
HTTP artifact version are separate from immutable exercise version. Do not add a
made-up `schema_version` wire field. Preserve `version`/`contract_version` aliases
and bound exercise identity. A new numeric exercise version alone is not a reason
to reject an otherwise supported shape.

## 10. Interaction mode contract

| Accepted mode | I02 foundation responsibility |
| --- | --- |
| SELF_CHECK | Select an unassessed foundation slot; no scored submit. |
| FINAL_ANSWER | Recognize the required public input schema and select its slot. |
| STEP_BY_STEP | Recognize public ordered-step metadata and select its slot. |
| STRUCTURED_SOLUTION | Recognize distinct input/step metadata and select its slot. |

Full forms, ordered-step editing/serialization, autosave, submission, hints and
reveal are downstream. Parser profile and reveal/help policy are public metadata
only; I02 does not execute them. Missing metadata needed by a future form is not
invented. Generic `enum`/`object` metadata does not authorize guessing choices or
nested fields. No new modes or step types.

## 11. Validation behavior

Use the existing Python/jsonschema stack for wire fixture shape/provenance checks
and Django tests for template/routing behavior. Dispatch performs only explicit
supported-shape checks. A controlled unsupported-shape view is distinct from an
Assessment `UNSUPPORTED` outcome and never indicates wrong mathematics.

The JS dispatcher rejects non-string modes before `slots` lookup. SELF_CHECK
requires both schema fields present and null; FINAL_ANSWER requires input_schema,
STEP_BY_STEP step_schema, STRUCTURED_SOLUTION both. These existing R02A requirements
are regression-tested without changing the accepted contract or adding renderers.

No mathematical validator, LLM, provider call or prompt change is required.

## 12. Progress / evidence semantics

This feature does not create or mutate knowledge evidence. There are no student
mutations, ProgressEvents, CompletionFacts, eligibility decisions or persisted
attempts. Gallery state transitions are presentation demonstrations only.

## 13. Security / ownership

- Gallery is development-only, GET-only and synthetic; no auth policy changes.
- No private owner data, credentials, cookies, real student records or production
  database contents are read for gallery fixtures or browser evidence.
- No browser storage for credentials/private results/answers; temporary raw
  demonstration input remains in memory only.
- Escape untrusted statement/feedback/raw strings; do not trust arbitrary HTML.
  Preserve the existing trusted authored Content HTML boundary separately.
- Use an explicit fixture allowlist; no path traversal/arbitrary file reads.
- Check delivered HTML/JSON/JS/data attributes/network for secret equivalents.
- Do not alter Session/CSRF, reveal or rate-limit contracts. No AI endpoint exists
  in this increment, so provider/rate-limiter implementation is N/A.

## 14. Observability

Record fixture/state/mode provenance and dispatch decisions without secret data.
Browser evidence contains the actual browser version, DOM assertions, network and
console observations, keyboard actions and screenshots at recorded widths.
Screenshots supplement assertions. Record scope limitations; do not claim full
cross-browser/a11y audit or runtime student integration.

## 15. Acceptance criteria

- [x] Gallery demonstrates reused templates/components and tokens.
- [x] Loading/error/empty are distinguishable; failed load is not empty success.
- [x] Four modes dispatch by declared metadata; unknown/unsupported shapes fail
  safely without a guessed renderer or mathematical verdict.
- [x] Fixtures are versioned/provenanced and wire examples conform to R02A.
- [x] Fixture-only marking is always visible; no checker/answers/reveal secrets
  appear in delivered artifacts or network responses.
- [x] Gallery rejects mutations, performs no database writes and is absent when
  DEBUG=False; ordinary Content pages do not load gallery fixtures.
- [x] Untrusted strings are escaped; raw demonstration input is not silently
  changed or falsely described as server-saved.
- [x] Keyboard baseline has reachable controls, visible focus and associated
  labels/errors; mobile smoke covers 360/768/1440 px.
- [x] Existing Content metadata/content/resources retained in Django rendering;
  published home/catalogue/lesson browser comparison passes after runtime setup.
- [x] Canonical and task checks have actual results with limitations and evidence
  ownership recorded; historical user confirmation and current agent reruns are separate.
- [ ] Ruslan and Vladimir independently approve the concrete final result;
  applicable final-SHA CI and authorized merge satisfy Section 17.

## 16. Tests

### Python contract / Django tests (implemented)

- Four-mode dispatch descriptors; unknown mode, missing required schema,
  unsupported shapes, inconsistent version aliases/identity.
- Fixture versions/provenance and R02A schemas; deliberate invalid inputs remain
  negative test inputs, not accepted public fixtures.
- Loading/error/empty markup, marking, labels/errors and script asset isolation.
- XSS escaping and secret-equivalent rejection in delivered artifacts.
- DEBUG routing, non-GET rejection and no database writes.
- Existing Content shell metadata, authored content and resource regressions.

### JS regression / browser smoke (implemented, using available tools)

- `tests/test_i02_schema_dispatch.js` executes the production JS using an already
  available runtime, no npm/dependency/CI changes: 5 tests, 138 dispatch calls.
- Unknown strings, non-string types, required schemas and SELF_CHECK null-schema
  invariants fail safely; valid fixtures keep their four slots.
- Post-fix browser matrix calls `window.MathStartUI.dispatchExercise` directly:
  40/40 cases, no exceptions/forms/generated inputs. Matrix and gallery are separate
  observations; no full malformed-DTO audit is claimed.

- Runtime dispatch and loading/error/empty/retry observations.
- Raw input preservation without normalization or false saved state.
- Keyboard walkthrough, focus/labels/errors/live-region baseline.
- 360/768/1440 layouts; DOM/network/console and screenshots without PII.

Full Chrome/Edge/Firefox matrix is not blocking I02 acceptance. No Playwright or
new frontend tooling is assumed. If existing tools cannot demonstrate a mandatory
requirement, document the gap and stop dependent work for separate confirmation.

## 17. Verification matrix

Follow [the verification skill](../../skills/verification/SKILL.md). After separate
implementation authorization, use configured Python 3.12+, the existing complete
`requirements.lock`, `python -m pip check` and actual version reporting. Do not
switch a failing PostgreSQL configuration to SQLite merely to obtain a pass.

```text
python scripts/verify_repo.py
python -m unittest discover -s tests -p test_r02a_contract.py -v
python -m unittest discover -s tests -p "test_i02_*.py" -v
git diff --check
```

The I02 command becomes meaningful only once its tests exist; also explicitly
run `python manage.py test content.test_ui_foundation` when added. Preserve the
existing eight canonical checks, including Django/content/migration/R03/Harness
verification. Runtime content checks require a migrated/bootstrapped environment
and generate reports; do not migrate/bootstrap user data during this preparation.

### Historical / pre-publication environment and Content evidence

The user's manual PowerShell checks confirm the host `.venv` works: both
`.\.venv\Scripts\python.exe --version` and `python --version` report Python
3.14.7 with exit 0; `python -m pip check` reports `No broken requirements found`,
and Django imports as version 5.2.16. The earlier version-command failure occurred
on the Codex execution surface and did not establish a broken host `.venv`.
The user's latest manual checks confirm Docker Desktop is installed, Compose is
available and the PostgreSQL 16 container is healthy. Dependencies were synchronized
from `requirements.lock`; psycopg 3.3.6 imports successfully and pip check passes.
`python scripts/check_database.py` passes with `PostgreSQL connection OK;
server_version_num=160015`; `python manage.py check` passes with
`System check identified no issues (0 silenced)`. The basic local Python -> Django
-> PostgreSQL connection through Docker is confirmed; PostgreSQL/Docker setup is
no longer a current blocker. These are user-reported host results, not Codex reruns.

Implementation checks are recorded in the trace: 7 I02 Python tests, 5 no-DB Django
tests, 30 R02A tests, system/database checks and available browser smoke pass.
The user initialized the local runtime database with `python manage.py migrate`
and `python manage.py bootstrap_site`, then confirmed database/system checks and
`python scripts/verify_repo.py` -> PASS (8 checks passed). The prior empty-database
failure is resolved; it was a runtime prerequisite, not an I02 defect. The agent
did not migrate/bootstrap or rerun the already passing canonical/task suites in
this follow-up; the user's shell exit code was not separately supplied.
The agent repeated only the previously blocked Content checks: published
home/catalogue/lesson browser smoke and read-only rendering comparison against
the `cd10705` template pass; `/favicon.ico` returns normal HTTP 404, not 500.
No product code changed in the follow-up. See trace Section 17 for actual results.
Exact browser engine version is unavailable through permitted browser controls;
full cross-browser/a11y and browser malformed-DTO matrix are not claimed.
Tooling/CI changes are outside
this plan and require a dedicated reviewed change before becoming project tooling.

### Current published correction evidence

Trace Section 20 and `smoke.json.current` record fresh agent verification of the
corrected working content, including production JS/browser matrix, gallery states,
keyboard and 360/768/1440 smoke. Canonical PASS 8/8 is an actual agent rerun (exit 0),
distinct from the historical user-confirmed run. Browser context reports Chromium/Google Chrome
`154.0.8037.93`; full userAgent, userAgentData and high entropy values are retained.
Earlier unavailable-version, missing-table and pre-publication evidence remains
historical. Existing Content comparison/favicon evidence is retained with its
original ownership; it is not relabelled as a new browser rerun.
Correction CI run 37060459060 is SUCCESS on `e471efc0b1a6b4af9baf1401e49311a203f12450`.
The browser rerun occurred before the correction commit on identical product bytes;
its digest binding is verified against that commit, not represented as a new
post-publication rerun. Document-only synchronization adds no new browser results.
Independent approvals remain PENDING; CI/local PASS is not Task Approval.

## 18. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Runtime initialization (resolved) | Empty DB previously prevented Content checks | User applied migrate/bootstrap and confirmed canonical PASS 8/8; repeated Content smoke passes; no agent DB repair. |
| Browser evidence limitations | Single browser and focused dispatcher matrix only | Exact version/UA recorded; full cross-browser/a11y audit remains NOT RUN; independent review remains required. |
| PDF is local, not a public GitHub asset | Another checkout needs the source | Pin exact filename/digest; source distribution is a human follow-up, not PDF publication in I02. |
| Full upstream exchanges contain solutions | Fixture bundle could leak answers | Curate safe examples/projections; review delivered data, not just forbidden keys. |
| Shell extraction affects legacy resources | Existing site regression | Narrow Content tests and browser smoke; scoped revert preserves authored sources. |
| DEBUG-dependent URL configuration is cached | Disabled-gallery test could be misleading | Verify routing under separately loaded DEBUG=True/False configurations. |
| Dispatch grows into a renderer | I04 scope would be implemented early | Keep foundation slots explicit; missing form metadata is not guessed. |
| Browser evidence is insufficient | Mandatory baseline could remain unproven | Record actual gap; seek separate tooling confirmation before dependent work. |

## 19. Definition of Done

Deliverables: reusable shell/components, tokens, dispatcher, safe versioned state
fixtures, DEBUG-only gallery, tests, browser smoke and handoff documentation.
Done requires Section 15, the verification skill and v7.1 Section 17: meaningful
positive/negative evidence, no leaks/unrelated changes, closed blockers, independent
Ruslan/Vladimir acceptance, applicable green final-SHA CI and authorized merge.
No task acceptance, final SHA or G3 closure is asserted at preparation.

## 20. Trace / implementation links and downstream handoff

- Issue: [#21](https://github.com/Tramsey00/MathStart-Python/issues/21).
- Plan/trace: linked in the header; PR #22 OPEN; correction SHA/green CI pinned
  above, documentation-only follow-up separate; Task Approvals remain PENDING.
- Browser evidence: [smoke record](../../docs/agent-traces/MS7-I02-evidence/smoke.json)
  and 360/768/1440 plus keyboard screenshots beside it. Existing app browser control
  was used; no Node/Playwright toolchain was added to the project.
- MS7-I03 receives accepted shell/tokens/labelled components/state conventions;
  real auth/profile/onboarding and V02 integration remain its responsibility.
- MS7-I04 receives accepted public descriptors/dispatcher/fixture provenance;
  full catalogue/renderer and V04 integration remain its responsibility.
- MS7-I08 receives gallery instructions, assets and browser evidence/limitations;
  its frontend profile, real Harness run and independent review are separate.

Handoff pins the eventual accepted artifact SHA/version and actual test evidence.
This draft does not constitute an accepted downstream implementation handoff.
