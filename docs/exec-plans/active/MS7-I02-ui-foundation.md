# EXEC PLAN MS7-I02: UI foundation and fixtures

- **Status:** Active - documentation preparation; primary implementation awaiting user authorization
- **Owner:** Ilya (Илья)
- **Reviewer / Task Approver:** Ruslan and Vladimir
- **Created / last updated:** 2026-10-02
- **Canonical issue:** [#21 - MS7-I02: UI foundation and fixtures](https://github.com/Tramsey00/MathStart-Python/issues/21)
- **Spec:** [MS7-I02](../../../specs/ui/MS7-I02-ui-foundation.md)
- **Trace:** [MS7-I02](../../agent-traces/MS7-I02.md)
- **Related ADRs:** ADR-0001/0002/0003; accepted MS7-R02A addendum package
- **Milestone Gate / acceptance deadline:** G3 / 2026-10-05 (revised Section 20)
- **Estimated effort:** Not measured; no implementation duration is claimed
- **Human gate required:** Yes - independent Ruslan and Vladimir task acceptance
- **Branch:** `ms7-i02-ui-foundation`
- **Baseline SHA:** `428ece726918f635549fc7dd8fdd352f799c3308`

## 1. Objective

Prepare the repository records for a minimal reusable Django UI foundation.
The eventual result is shared templates/components and tokens, safe versioned
state fixtures, loading/error/empty, schema dispatch and baseline keyboard/mobile
evidence. The current permission allows only this plan, its spec and trace.

Canonical input: the complete
`.local-docs/MathStart_Technical_Specification_v7_1_SECTION20_PARALLEL_DEADLINES.pdf`,
Section 24 page 68 and applicable Sections 5-7, 11, 15-17, 20-21 and 25.
Specification v6 is excluded as an implementation requirements source.

```text
PDF SHA-256
e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd
R02A OpenAPI SHA-256
133aae117333e66b40662ec4fdb47fc02ee08e7aeecbbd9cbb200d5468ca7362
R02A manifest SHA-256
1b4a4b43df6052db5d91840cb2e748745cafb0529a766272d5a29b2b88e6dbac
```

The PDF is a local source, not a publicly published GitHub file. This plan does
not authorize copying/publishing it. Deadline follows revised Section 20 rather
than older NORMAL/EARLY card dates.

## 2. Preconditions

- [x] AGENTS, PRODUCT and ARCHITECTURE read during task discovery.
- [x] Relevant accepted ADR/contracts, existing templates/static/tests and Content
  pipeline inspected; templates and verification skill re-read for preparation.
- [x] Canonical Issue #21 registered and explicitly confirmed by the user.
- [x] HARD MS6-I01 accepted/frozen; UX artifacts named by v7.1 are upstream only.
- [x] CONTRACT MS7-R02A accepted by Ruslan, explicitly confirmed by the user.
- [x] All 17 R02A manifest pins and canonical PDF digest rechecked.
- [x] Branch/baseline and clean initial working tree confirmed.
- [x] Corrected scope approved: no new tooling, full renderer or future flow logic.
- [ ] User authorizes primary implementation after reviewing these three documents.
- [x] Host `.venv` works; user PowerShell confirms Python 3.14.7, pip check and Django 5.2.16 import.
- [x] Basic local Python -> Django -> PostgreSQL through Docker confirmed by user checks; PostgreSQL 16 container healthy, database connection and manage.py check PASS.

HANDOFF and INTEGRATION dependencies are empty. A live backend API is not required
for I02 task-specific acceptance. Stale upstream pending/draft records are not
blockers and remain unchanged. No schema/migration work is planned.

## 3. Scope

### In scope

The exact behavior/criteria are in spec Sections 3, 15 and 16: reusable Django
shell/components, isolated tokens/styles, loading/error/empty, foundation schema
dispatch, safe versioned fixtures, DEBUG-only gallery, Python/Django tests and
available browser keyboard/mobile smoke at 360/768/1440 px.

### Out of scope

Full four-mode renderer (I04), browser mathematical assessment/checker/secrets,
backend APIs/models/migrations/seed/evidence changes, real student flows, future
pending/degraded/conflict/unauthorized business behavior, Node/Playwright/frontend
tooling/new CI/dependencies, separate preview server, complete cross-browser/a11y
audit, unrelated refactors, bulk lesson conversion, deployment/live providers,
Harness changes and frozen upstream housekeeping. No commits/push in this phase.

## 4. Current state

The site uses `content`, a single `templates/page_detail.html`, lesson components
and shared static assets. There is no shared base template, I02 gallery/fixtures
or configured browser test toolchain. R02A is a contract package, not a runtime API.
Legacy authored SELF_CHECK answers are an explicitly preserved compatibility case.

The user's manual PowerShell checks confirm the host `.venv` works:
`.\.venv\Scripts\python.exe --version` and `python --version` both report Python
3.14.7 with exit 0; `python -m pip check` reports `No broken requirements found`;
Django imports as version 5.2.16. The earlier failure was on the Codex execution
surface and did not prove host `.venv` breakage.
The user's latest manual checks confirm Docker Desktop is installed, Compose is
available and the PostgreSQL 16 container is healthy. Dependencies were synchronized
from `requirements.lock`; psycopg 3.3.6 imports successfully and pip check passes.
`python scripts/check_database.py` passes with `PostgreSQL connection OK;
server_version_num=160015`; `python manage.py check` passes with
`System check identified no issues (0 silenced)`. The basic local Python -> Django
-> PostgreSQL connection through Docker is confirmed; PostgreSQL/Docker setup is
no longer a current blocker. Canonical verification remains NOT RUN, not PASS.
These are user-reported host results, not Codex runtime reruns. Bundled Python
3.12.14 remains the source/document audit interpreter.
No environment configuration or installation is authorized by this correction.

## 5. Target state

Reusable foundation assets are demonstrated on a clearly marked fixture-only
gallery in the existing Django server. Dispatch recognizes four public modes
without providing full renderers. Unsupported shapes fail safely. Loading/error/
empty are explicit. Keyboard/mobile baseline and security are evidenced. Existing
Content behavior is preserved. Deliverables pass spec acceptance and independent
review; final task/CI/merge evidence is recorded before downstream handoff.

## 6. Architecture boundaries

- Current phase: Harness/docs records only; no runtime dependency changes.
- Future phase: Content presentation, shared templates/static and local synthetic
  fixtures; accepted public R02A DTOs are read-only compatibility inputs.
- No Assessment/Progress/Knowledge/Tutor/LLM model writes or imports are added.
- No new app/server/toolchain/production API. Only Progress owns knowledge state.
- Existing trusted authored HTML remains separate from escaped untrusted strings.

## 7. Planned changes

### Step 1 - Documentation preparation (currently authorized)

Create only the spec, this active plan and trace. Pin sources, scope, gates,
verification and downstream boundaries. Audit local links, headings, whitespace,
digests and Git scope without staging. Stop for user confirmation.

### Step 2 - Safe fixture contract (not yet authorized)

Add a versioned UI fixture schema and curated examples. Preserve provenance and
R02A wire compatibility; UI projections are explicitly separate. Never deliver
whole upstream exchanges, reveal responses or completed solutions. Add meaningful
Python contract tests. Check valid/invalid shapes, pins and secret equivalents.

### Step 3 - Shell, tokens and minimal components (not yet authorized)

Extract a reusable shell while preserving SEO/canonical, authored body/CSS/JS,
catalogue and theme resources. Add tokens and button/field/card/state components
with narrow styles. Verify Django rendering, escaping and Content regression.

### Step 4 - States, dispatch and Django gallery (not yet authorized)

Add loading/error/empty presentation and a metadata-based foundation dispatcher.
Do not construct complete forms or implement lifecycle actions. Add a GET-only
`/__ui__/foundation/` view/route under DEBUG, with permanent fixture-only marking,
an allowlist and no DB writes. Verify separately loaded DEBUG on/off routing,
non-GET rejection, script isolation and absence of delivered secrets.

### Step 5 - Verification and review handoff (not yet authorized)

Run Python/Django checks and manual browser smoke with recorded versions and
DOM/network/console/screenshots. Resolve scoped failures. Record final evidence
and request independent Ruslan/Vladimir review. Do not claim task/G3 completion
from gallery screenshots or fixture behavior. Publication/merge requires its
separate authorization and applicable final-SHA CI.

### Planned file inventory

Only the first row is writable in this phase; other paths are future candidates.

| Phase | Paths relative to repository root |
| --- | --- |
| Preparation | `specs/ui/MS7-I02-ui-foundation.md`; `docs/exec-plans/active/MS7-I02-ui-foundation.md`; `docs/agent-traces/MS7-I02.md` |
| Fixture contract | `specs/ui/ui-state-fixtures-v1.schema.json`; `specs/ui/fixtures/ui-states-v1.json`; `tests/test_i02_ui_contract.py` |
| Shell/gallery | `templates/base.html`; `templates/page_detail.html`; `templates/ui/fixture_gallery.html` |
| Components | `templates/ui/components/button.html`; `field.html`; `card.html`; `state.html` in that directory |
| Assets | `static/mathstart/css/ui/tokens.css`; `foundation.css` in that directory; `static/mathstart/js/ui/schema-dispatch.js`; `foundation.js` in that directory |
| Django gallery/tests | `content/views.py`; `content/urls.py`; `content/test_ui_foundation.py` |
| Instructions | `README.md` only after implementation authorization |

No `package.json`, package lock, Playwright config, new CI workflow, preview server,
upstream manifest or `.gitignore` change is included.

## 8. Database / migration plan

No schema change. No models, migrations, backfill, local database bootstrap or
historical-data modifications. Canonical migration consistency remains required
later; task-specific fresh/upgrade/locking evidence is N/A. Tests use the existing
Django test isolation; do not mutate a user's runtime database to prepare evidence.

## 9. Seed / bootstrap impact

None. UI fixtures are synthetic presentation examples, not runtime seeds or
persisted evidence. Existing curriculum/site content/bootstrap remains untouched.

## 10. API / UI plan

No `/api/v1/` changes. Gallery is a DEBUG-only GET HTML route inside Django, not a
student API. No arbitrary path input, student writes or private resource loading.
UI state scope is loading/error/empty and ordinary content; unsupported descriptor
presentation is not an assessed outcome. Four-mode dispatch selects slots only.
Wire versions retain R02A semantics; no invented schema-version wire field.

Public/server separation and legacy compatibility are defined in spec Sections
8-13. Answers/checker/reveal secrets are excluded from delivered fixtures/assets.
No real identities, browser private-data storage or client Progress calculations.

## 11. LLM / prompt plan

No LLM/prompt change. No live Product model/API requirement for I02 functional
acceptance. Record the actual engineering surface: bootstrap-agent before G1;
after accepted G1, significant engineering increments use the accepted Harness.
Do not infer G1 acceptance from the calendar or R02A acceptance.

## 12. Tests to add/update

- Python: fixture schema/version/provenance/secrecy, public descriptor compatibility,
  unknown/missing/unsupported descriptors and version/identity inconsistencies.
- Django: component states/marking/escaping, DEBUG route isolation, no DB writes,
  non-GET rejection, Content shell metadata/content/assets regression.
- Browser smoke: actual JS dispatch/states/retry, raw input preservation,
  keyboard/focus/labels/errors/live regions and 360/768/1440 layouts.
- Inspect DOM, delivered network data and console; capture screenshots without PII.

No complete Chrome/Edge/Firefox matrix or full accessibility audit is blocking
I02. Python/static tests alone do not prove JS behavior; browser evidence remains
necessary. New browser tooling needs separate justification/review/confirmation.

## 13. Verification plan

Preparation: read-only PDF/upstream digest checks, local document link/heading/
whitespace audits, scoped Git status/diff checks. No runtime suite is claimed.

Implementation: use [the verification skill](../../../skills/verification/SKILL.md)
in a configured Python 3.12+ environment with the existing complete Python lock,
`python -m pip check` and actual interpreter/runtime version evidence.

```text
python scripts/verify_repo.py
python -m unittest discover -s tests -p test_r02a_contract.py -v
python -m unittest discover -s tests -p "test_i02_*.py" -v
python manage.py test content.test_ui_foundation
git diff --check
```

I02 commands apply only after the named tests exist. Preserve all eight baseline
checks and the accepted R02A test suite. Runtime content checks produce reports
and require configured DB/media. Classify environment/pre-existing failures;
never silently fall back from PostgreSQL or call skipped checks PASS. No CI or
dependency modifications are part of this task. Applicable final-SHA CI must be
green under the existing workflow; additional project tooling needs its own
reviewed change. No task-specific migration or live model test is required.

## 14. Risks and fallback

| Risk/question | Detection / response |
| --- | --- |
| Local PDF not on GitHub | Digest/link audit; another checkout needs access to the exact source. Distribution is outside this three-document phase. |
| Upstream secret-bearing examples | Review fixtures/HTML/JS/network including answer-equivalent prose, not just forbidden keys. |
| Legacy shell regression | Narrow tests/smoke; scoped forward fix/revert without republishing/removing content. |
| DEBUG route test caching | Reload/isolate URL configuration to prove the disabled route is really absent. |
| Under-specified future enum/object controls | No guessed choices/nested fields; foundation slot only; contract extension stays downstream. |
| Browser evidence unavailable/inadequate | Record the unmet criterion; justify any new tooling and stop dependent work for confirmation. |
| Scope or source drift | Recheck branch/HEAD/digests before editing; surface changes, do not rewrite accepted upstream. |

No essential contract or basic PostgreSQL environment blocker is currently
identified. Full canonical/task verification and future browser evidence remain
pending; successful basic host checks do not replace them or expand scope.

## 15. Human gates

The user approved scope and Issue text and authorized only documentation creation.
Primary implementation permission is still pending. Scope approval is not approval
of an unimplemented result.

Reviewer / Task Approver: Ruslan and Vladimir.
Their independent final-result decisions are pending.
Ilya is Owner, not self-approver. G3 is a separate gate with its full evidence.
The eventual PR references canonical Issue #21 with `Closes #21`. No staging,
commit/push, PR creation, merge, Issue update/closure or deployment is authorized
by this preparation request. Keep the plan active until recorded human acceptance.

## 16. Completion checklist

- [x] Canonical Issue/dependencies and agreed scope established.
- [ ] Preparation documents reviewed by the user; primary implementation authorized.
- [ ] All implementation deliverables and positive/negative criteria pass.
- [ ] Meaningful tests and required browser smoke evidence recorded.
- [ ] Canonical/task verification passes; environment failures resolved honestly.
- [ ] Security/Content preservation confirmed; no unrelated changes.
- [ ] Ruslan and Vladimir independently approve the final result.
- [ ] Authorized publication/merge and applicable green final-SHA CI recorded.
- [ ] Accepted downstream handoff pinned; plan moved only after acceptance.

## 17. Completion summary and handoff

Current result: preparation documents only; MS7-I02 remains INCOMPLETE.
Implementation SHA/PR/CI/browser evidence are pending. No fixture/component/runtime
deliverable exists yet. Preparation audits/results belong in the linked trace.

After acceptance, MS7-I03 receives shell/tokens/components/state conventions;
MS7-I04 receives dispatcher/public descriptors/fixture provenance; MS7-I08 receives
gallery instructions/assets/browser evidence and known limits. Each handoff pins
the accepted version/SHA, tests and review. Real auth/renderer/Harness-profile work
and downstream runtime integration remain separate task responsibilities.
