# EXEC PLAN MS7-I03: Auth/profile/onboarding UI

- **Status:** Active; implementation published and local acceptance/verification PASS; independent human acceptance pending
- **Owner:** Илья
- **Reviewer / Task Approver:** Руслан и Владимир
- **Created / last updated:** 2026-10-04 / 2026-10-05
- **Canonical Issue:** [#25](https://github.com/Tramsey00/MathStart-Python/issues/25)
- **Spec:** [MS7-I03](../../../specs/ui/MS7-I03-auth-profile-onboarding.md)
- **Trace:** [MS7-I03](../../agent-traces/MS7-I03.md)
- **Branch:** `ms7-i03-auth-profile-onboarding`
- **Pull request:** [#26](https://github.com/Tramsey00/MathStart-Python/pull/26), OPEN
- **Implementation commit:** `635e8ecaff65f2fdc7069656a7e5b47e863aa853` (55 files)
- **Baseline SHA:** `c945ef6f768564fbd876b8d95f61a83a6d8cbda2`
- **Stage 2 starting HEAD:** `c0bfecfa53795c6b4fb07bb5ffb8ed0ff04dac66`
- **Gate:** G3
- **Deadline:** 09.10.2026, revised canonical v7.1 §20.4
- **FR coverage:** FR-01, FR-02
- **Human gate required:** Yes; independent Руслан and Владимир Task Approvals
- **Latest correction:** Auth review feedback locally verified; same PR #26 (see §15)

```text
Implementation: COMPLETE; overall task INCOMPLETE pending human gates
BROWSER ACCEPTANCE: PASS (stage 3)
FINAL VERIFICATION: PASS (stage 4 and UX follow-up)
COMMIT/PUSH: PERFORMED
PR: OPEN #26
IMPLEMENTATION-SHA CI: SUCCESS; final publication-record head checked on PR
Task Approval: PENDING
G3: PENDING
```

## 1. Objective and authority

Deliver auth/profile/onboarding screens on the real V02 API using the accepted
I02 foundation, with three mode selections, saved server state, safe CSRF/error/
retry handling and keyboard forms. Downstream: MS7-I11 and MS7-I14.

Canonical source: MathStart Technical Specification v7.1, G0 ACCEPTED,
`.local-docs/MathStart_Technical_Specification_v7_1_SECTION20_PARALLEL_DEADLINES.pdf`.
PDF SHA-256:
`e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd`.
Task card §24 pages 68–69; applicable §11/16/17/20/21/25. Revised §20 calendar
overrides old card dates. Use no v6 requirements.

## 2. Current authorization and preconditions

The initial five stages and contextual-retry cleanup were published in PR #26.
The latest instruction authorizes **Ruslan auth UI feedback corrections**: limit
registration to 30 on the UI boundary, show one auth form with a switcher, update
tests/docs/evidence, repeat full verification and real browser acceptance, then
ordinary commit/non-force push to the same branch/PR and exact-head CI.
No new Issue/branch/PR, merge, manual Issue closure, self-approval or G3 closure.
Earlier phase restrictions/results are historical.

| Stage | Scope | Current status |
| --- | --- | --- |
| 1. Preparation | Canonical Issue, Spec, Exec Plan, Trace; document diff checks | COMPLETE; preparation committed/pushed as `c0bfecfa53795c6b4fb07bb5ffb8ed0ff04dac66`. |
| 2. Implementation core | Real-API auth/profile/onboarding UI and required targeted tests | CORE COMPLETE locally; targeted tests PASS. |
| 3. Tests + browser acceptance | Remaining automated coverage, real keyboard, DOM/network/console/screenshots | PASS on real PostgreSQL/Chromium; logout focus corrected; targeted reruns PASS; sanitized evidence recorded. |
| 4. Verification + cleanup | Full verifier, scoped diff, plan/trace updates | PASS; all eight mandatory checks and extra I03/I02 Node/R02A suites; evidence/scope audit complete. |
| 5. Commit/push/PR | Core publication only after checks; independent review/approval | Implementation committed/pushed; PR #26 OPEN; both reviewers requested; exact implementation-head CI SUCCESS. Docs-only follow-up requires its own exact-head CI. Independent approvals pending. |

Preparation inspected authority/repository inputs, runtime, tests and upstream
migrations. Initial branch, HEAD, local main, origin/main and live remote main
match the expected baseline; working tree was clean. No existing canonical I03
Issue/artifacts were found before Issue #25 creation.

Before core work, confirm the then-current branch/baseline and scoped state again.
Record any changed contract/dependency or environment failure before proceeding.
This plan does not instruct checkout, branch replacement or dependency repair.

## 3. Dependencies and current inputs

| Type | Dependency | Evidence / use |
| --- | --- | --- |
| HARD | MS7-I02 | Merged PR #22; Руслан/Владимир approvals; reusable shell/components/tokens/fixtures. |
| CONTRACT | — | Consume frozen accepted R02A as a named input; do not add an edge or reopen it. |
| HANDOFF | — | No canonical handoff prerequisite. |
| INTEGRATION | MS7-V02 | Merged PR #19; Руслан approval; real auth/profile/onboarding services. |
| Integration correction | V02 PR #24 | Merged into baseline, Issue #23 closed, grades runtime and I03 consumer acceptance available. |

Read inputs linked in the spec, including `AGENTS.md`, `PRODUCT.md`,
`ARCHITECTURE.md`, ADR-0001/0002/0003, accepted R02A/ADR-0004 addendum,
I02 and V02 spec/plan/trace, and `specs/api/MS7-V02-grades-runtime.md`.
Use actual accepted GitHub/main state when historical headers disagree.

The old missing-grade-source blocker is removed. Missing separate PR #24 backend/
migration approval evidence is a records question for reviewers, not permission
for I03 to perform a backend review or reimplement the endpoint.

## 4. Scope and architecture boundaries

Allowed future feature scope: registration, login/logout, own profile, real grades,
START_ZERO/SELF_REPORT/DIAGNOSTIC selection, saved state, CSRF, safe errors/retry,
keyboard and real-API acceptance. Reuse Django Templates + progressive JS and I02.
Canonical file areas: templates/static/UI fixtures/browser tests; actual UI file
and route choices will be recorded during the separately authorized core phase.
Any necessary thin Django page-routing glue must be justified as UI integration;
no backend domain/API redesign follows from that possibility.

```text
I03 UI -> existing Users identity/profile/onboarding API
I03 UI -> existing Content public grade catalogue API
Users/Content services -> their existing persistence
Only Progress -> validated knowledge evidence / long-term state
```

Exclude assessment, Attempt/renderer, diagnostic session runtime, numerical skill
initialization, Progress calculations, Tutor/practice/history, client verdicts,
server secrets, schema/migration/seed changes, unrelated refactor and frozen API
changes. New stack/toolchain requires necessity and human approval. Fixtures
remain synthetic and labelled; they cannot stand in for accepted real integration.

No schema change. No migration, seed/bootstrap or LLM/prompt change.

## 5. Implementation phases and actual progress

The original phase definitions remain below. Phases 1–10 are implemented as core;
phases 11–13 passed local automated, browser and final verification. Phase 14
is in independent review; required human approvals/merge remain pending. Detailed
commands and results are in the trace.

| # | Phase | Planned behavior | Evidence before advancing |
| --- | --- | --- | --- |
| 1 | auth shell/navigation | Reuse I02 shell/tokens/components; show session state from real GET me; preserve existing Content. | Scoped template/navigation and anonymous/authenticated state checks; no fixture success substitution. |
| 2 | registration | Closed username/password/optional-email JSON, CSRF bootstrap, stable action key and 201 handling. | Real registration, safe invalid request, lost-acknowledgement replay and no duplicate identity. |
| 3 | login/logout | Safe credentials form, POST logout, cookie auth and refreshed CSRF after login rotation. | Missing/wrong/inactive credential parity; rotation; repeated logout 401 and recovery read. |
| 4 | profile + grades | Fetch public catalogue pages, display title, use returned ID, PATCH only selected_grade_id. | `id != number`, pagination/empty/error states and owner-only profile save/read. |
| 5 | START_ZERO | POST returned grade ID and START_ZERO, reflect backend-confirmed choice. | Real mode save + GET me recovery; no frontend progress initialization. |
| 6 | SELF_REPORT | POST returned grade ID and SELF_REPORT only; preserve logical key/body on retry. | Saved mode and duplicate retry/lost acknowledgement without another mutation; no skill-list payload. |
| 7 | DIAGNOSTIC selection | Save DIAGNOSTIC choice through existing V02 only. | Persist/restore mode; no claim that a diagnostic session was performed. |
| 8 | saved state | Restore through GET me after reload/later login; reconcile historical receipt responses. | Existing state survives sessions; pending local input never displayed as saved. |
| 9 | CSRF/error/retry | Required mutation headers, refresh after rotation, safe envelopes, 429 Retry-After, conflict/recovery. | Missing/stale token, safe 400/401/403/409/429/503 and network-loss paths; stable action identity. |
| 10 | keyboard/accessibility | Labels/errors, native controls, visible focus, reachable status/retry, responsive forms. | Tab/Shift+Tab/Enter and native selection walkthrough at applicable I02 baseline widths. |
| 11 | automated tests | Meaningful UI integration tests for required paths with configured tools; preserve upstream regressions. | Three modes, saved state, retry, invalid credentials, keyboard-related DOM contract, CSRF and grade identity tests. |
| 12 | browser acceptance | Real API browser walkthrough and sanitized DOM/network/console/screenshots. | Actual request payloads/responses, all required flows, keyboard and 360/768/1440 evidence; actual versions. |
| 13 | verification | Complete applicable verifier/contract/frontend checks; scoped diff cleanup and factual trace/plan. | Passing actual results or surfaced blockers; unchanged frozen inputs; no unexplained files/secrets. |
| 14 | PR/review/approval | After authorized stage 5, commit/push/scoped PR linked to #25; exact-head CI and reviewers. | Руслан and Владимир independent Task Approvals, blocking comments resolved, authorized merge; G3 assessed separately. |

| Phases | Actual current status (stages 2–4) |
| --- | --- |
| 1–3 auth shell / registration / login/logout | CORE IMPLEMENTED; template/JS and real runtime flow tested. |
| 4 profile + grades | CORE IMPLEMENTED; real returned ID, pagination and PATCH flow tested. |
| 5–7 three mode selections | CORE IMPLEMENTED; real API, replay and no numerical/session implementation. |
| 8 saved state | CORE IMPLEMENTED; GET me after auth/reload/replay and controller state restore tested. |
| 9 CSRF/error/retry | CORE IMPLEMENTED; rotation, frozen action identity, lost acknowledgement/reconciliation tested. |
| 10 keyboard/accessibility | PASS: real native keyboard walkthrough; disabled-fieldset logout focus defect corrected and retested. |
| 11 automated tests | PASS after auth review corrections: 33 Node (28 I03 + 5 I02), 96 Django, 18 R03, 73 Harness and R02A 30/30, no skips. |
| 12 browser acceptance | PASS: real API/PostgreSQL, three modes, retry, restoration, errors, DOM/console and actual 360/768/1440px evidence. |
| 13 final verification | PASS locally; full mandatory sequence, scoped diff/whitespace and evidence audit complete. |
| 14 PR/review/approval | PR #26 OPEN; implementation exact-head CI SUCCESS; review requested from both verified approvers. Human approvals, merge and G3 pending. |

Final publication is now authorized. Stop after exact final-head CI and the
publication report; independent human approval and merge are separate gates.

### Actual core file boundary

`/account/` is a GET-only presentation page in `users/ui_urls.py` and
`users/ui_views.py`, registered in `config/urls.py`. It renders
`templates/users/account.html` and `grade_field.html`. The base navigation gains
one account link. I02 field/button components gain optional type/autocomplete/
name/maxlength parameters with unchanged defaults.

Task CSS: `static/mathstart/css/ui/account.css`. Task JS:
`static/mathstart/js/ui/identity-api.js` (existing API consumer), `account.js`
(presentation controller). API routes, business services, models, migrations,
frozen DTO/OpenAPI/policy and I02 fixtures remain unchanged.

Tests: `users/tests/test_i03_ui.py`, `tests/test_i03_identity_api.js`,
`tests/test_i03_account.js`, `tests/i03_runtime_flow.js`. The latter runs production
JS against an isolated Django/PostgreSQL live test server, not a browser.

## 6. API and state handling plan

Consume exactly the eight operations in the spec; add no endpoint/field:

```text
GET   /api/v1/auth/csrf/
POST  /api/v1/auth/register/
POST  /api/v1/auth/login/
POST  /api/v1/auth/logout/
GET   /api/v1/users/me/
PATCH /api/v1/users/me/
POST  /api/v1/onboarding/complete/
GET   /api/v1/grades/
```

Every mutation uses JSON and X-CSRFToken. Registration/onboarding additionally
use a stable Idempotency-Key for one unchanged logical action. Refresh CSRF after
registration/login. Keep bootstrap/session identity for retry; do not persist
credentials/secrets in browser storage. Read GET me for current state after a
lost acknowledgement or a historical receipt replay. Profile PATCH/login/logout
have no receipt replay. Logout repetition can be 401.

Grade selection uses `title` and returned `id`, never `number` as a PK. Complete
opaque-cursor pagination with unchanged page size; no DB internals or hardcoded
IDs. Onboarding contains only selected_grade_id and mode. Actual diagnostic
sessions and SELF_REPORT skill/progress initialization belong outside I03.

## 7. Test and browser acceptance plan

- Three real onboarding selections including catalogue `id != number`.
- Saved profile/mode state across reload and later authenticated session.
- Registration/onboarding retry and lost acknowledgement; SELF_REPORT deduplication.
- Invalid credential parity and foreign-account nondisclosure.
- Required CSRF for anonymous auth and private mutations; token/session rotation.
- Grade pages, successfully empty catalogue, safe failure and repeated selection.
- Accessible labels/errors/focus and keyboard form submission/retry/native selection.
- Existing Content compatibility and public/server secret boundary.

Use existing upstream tests as regressions, not as a claim that the future UI is
tested: `users.tests.test_identity`, `users.tests.test_postgres`,
`content.test_grades_api`, I02 tests and R02A contracts. Select any new task test
names only when implemented. Avoid tests that simply mirror implementation.

Browser acceptance checks DOM state, network method/path/payload/response, cookies/
CSRF behavior and console. Preserve sanitized screenshots without real PII or
credentials. Record actual browser/server/tool versions, viewport, results and
limitations. Use the existing environment and browser capabilities before
considering a new toolchain. A static gallery or mocked success is insufficient.

## 8. Verification plan

Current scoped Git checks (also used in preparation):

```text
git status --short
git diff --check
git diff --stat
git diff
```

New core files remain untracked. Ordinary `git diff` excludes them; inspect their
contents/whitespace with `git diff --no-index` against empty input without staging.
Record results in trace; staged files must remain empty in stage 2.

Executed core targeted checks:

```text
node --test tests/test_i03_identity_api.js tests/test_i03_account.js
.venv/Scripts/python.exe -B manage.py test users.tests.test_i03_ui users.tests.test_identity content.test_grades_api content.test_ui_foundation --noinput
.venv/Scripts/python.exe -B manage.py test users.tests.test_i03_ui --noinput
```

Actual environment: Python 3.14.7, Django 5.2.16, PostgreSQL 16.15, existing Node
24.19.0. Tests use a separate PostgreSQL test DB. Stage 2 performed no local
migration/bootstrap/browser setup; stage 3 then applied the existing migration,
ran unchanged bootstrap, collected static and completed the real walkthrough.
See trace for initial failure, correction and results. The configured interpreter
required execution outside the sandbox;
that access was approved for targeted tests.

Stage 4 executed the complete `skills/verification/SKILL.md` sequence with the
configured interpreter. `scripts/verify_repo.py` covered the entire Django suite,
including the listed upstream regressions; those suites were not duplicated:

```text
.venv/Scripts/python.exe -B -m pip install --no-deps -r requirements.lock
.venv/Scripts/python.exe -B -m pip check
.venv/Scripts/python.exe -B --version
.venv/Scripts/python.exe -B scripts/version_report.py
.venv/Scripts/python.exe -B scripts/verify_repo.py
node --test tests/test_i03_identity_api.js tests/test_i03_account.js tests/test_i02_schema_dispatch.js
.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_r02a_contract.py -v
git diff --check
```

All 17 locked dependencies were already satisfied; pip check passed. Full local
verification passed without skips; no new CI run is claimed. No task schema
change was authored, so the MS6-V01 disposable fresh-install/failed-connection
sequence was not added to I03. Existing grade/users migration and PostgreSQL
integration tests did run within the full Django suite. Future exact-head CI
retains its configured fresh-install requirements before merge.

After accepted G1, apply applicable §17 Harness engineering-run requirements;
do not claim a current production Harness run merely from plan creation.

## 9. Risks and human review

| Risk | Handling |
| --- | --- |
| Separate PR #24 backend/migration approval record was not found | Руслан/Владимир clarify evidence before final acceptance; I03 consumer approval and merged grade runtime remain available. |
| Local DB upgrade/server/browser prerequisites | Resolved in stage 3 using documented real PostgreSQL setup; no new migration authored. |
| CSRF rotation or logical retry key replaced | Exercise lost acknowledgements and stale-token recovery with unchanged action identity. |
| SELF_REPORT/DIAGNOSTIC claims exceed saved choice | Match exact V02 payload/state; no diagnostic or Progress implementation. |
| Shared shell/control extension regresses Content or keyboard | Scoped reuse, escaping/focus checks and existing Content regression. |
| Tooling/architecture scope grows | Surface a demonstrated requirement and seek the specified human decision before changing stack/contracts. |

Task Approvers are Руслан and Владимир; Owner Илья cannot self-approve the task.
Task acceptance, PR merge and G3 closure are distinct. Move this plan to completed
only after completion/human acceptance in a later authorized phase; never now.

## 10. Completion checkpoints

- [x] Stage 2 core implementation complete within the spec boundary; targeted tests PASS.
- [x] Required task-owned targeted tests and real browser acceptance complete; final verifier remains separate.
- [x] Local verification, scoped diff and final evidence complete (stage 4).
- [x] Authorized implementation commit/push/PR created; exact implementation-head CI SUCCESS.
- [ ] Руслан and Владимир Task Approvals recorded; required merge completed.
- [ ] I03 downstream handoff recorded; G3 status assessed independently.

Stage 1 history and stages 2–3 results are recorded separately in the trace.
PR #26 is OPEN; overall task completion, Task Approval, merge and G3 remain pending.
The publication-record follow-up's final-head CI proof is maintained in PR #26;
verify that new SHA/run before issuing the final publication report.

## 11. Stage 3 actual acceptance / stopping boundary

Evidence: [index](../../agent-traces/MS7-I03-evidence/README.md),
[acceptance JSON](../../agent-traces/MS7-I03-evidence/acceptance.json),
[network JSON](../../agent-traces/MS7-I03-evidence/network.json).
Chromium 154.0.8037.98; real `/account/` -> existing API -> PostgreSQL 16.15.

Runtime preparation followed README: connection check, existing migration,
idempotent bootstrap (zero new/changed catalogue/pages/lessons/media), collectstatic
and Django runserver. The temporary loopback observer/probe lived under ignored
`var/reports/ms7-i03-browser/`; no project browser stack or backend semantics changed.

All required user flows, keyboard and responsive states passed. Actual grade
identity mismatch was 5 класс / number 5 / PK 1. CSRF rotation/current headers,
receipt-header scope and frozen retry body/key were observed without storing
secrets. A read-only production-consumer probe loaded three cursor pages.
Read-only PostgreSQL counts proved one registration receipt and four onboarding
receipts for the normal synthetic account's four logical operations, despite
six onboarding POST attempts. Saved state came from GET me after reload/login.

Only I03 core fix: defer logout/auth focus until controls are re-enabled in the
controller's finally path. Strengthened the controller test adapter to reproduce
native disabled-fieldset focus rejection. Initial red run: 10/11. Corrected run:
19/19 Node; task Django rerun: 5/5, no skips. Browser logout focus then passed.

Single-browser evidence is not a full cross-browser/screen-reader audit. Expected
401/session/network-fault behavior is recorded; the legacy favicon 404 is a
non-blocking pre-existing shell detail. Generated runtime/static assets remain
ignored. Final verification, commit/push/PR and human gates are NOT STARTED/PENDING.

## 12. Stage 4 verification snapshot before UX follow-up

All eight verifier checks passed: system/migration consistency, three content
checks, 95 Django tests, 18 R03 contract tests and 73 Harness unit tests. Additional
Node tests passed 24/24 (19 I03 + 5 I02); R02A contracts passed 30/30. No skips.
Full Django discovery includes I03 UI/live production-consumer tests (5), I02
foundation (5), V02 identity (43), Users PostgreSQL (6), grades API (10), Content
PostgreSQL publication (2), bootstrap (1), grade migration (1), Users migration
(1) and other existing Content suites (21). Exact commands/results are in trace.

Stage 4 audited all 27 screenshots, source/served-asset bindings and sanitized
network records. Evidence remains at the accepted I02-style trace location;
temporary reports and generated static/runtime data stay ignored. All frozen
contracts, models, migrations, API business code and seeds remain unchanged.
Only a miscopied I03 manifest digest and current documentation status/results
required cleanup; no implementation code changed in this stage.

Branch/HEAD remain the preparation branch/commit; 51 task-owned paths are listed
in the trace (7 tracked modifications + 44 untracked files). Nothing staged.
`git diff --check` and equivalent UTF-8 untracked whitespace/content checks pass.
Branch is ready for a separately authorized commit/push phase. No implementation
commit/push/PR, Issue change, merge, Task Approval or G3 closure was performed.
Legacy favicon 404 and the recorded single-browser/screen-reader limits remain
non-blocking. Independent Руслан/Владимир approvals and final-head CI are pending.

## 13. Authorized contextual retry UX follow-up (2026-10-05)

COMPLETE locally. Hide state reload in normal initial/saved state; show
**Повторить загрузку** only for failed state restoration/session reconciliation.
Retry calls the same GET me; automatic opening/auth restoration, CSRF/receipt
behavior and backend semantics remain unchanged. Success hides retry and moves
focus to an enabled username input/profile heading (or pending mutation retry).
Repeated failure retains an accessible error/retry state with correct status.

Updated controller, account template, controller regressions and Django semantic
assertions. I03 targeted tests passed (22 Node + 5 Django); final Node run including
I02 passed 27/27. Full verifier re-ran after the final repeated-error status fix:
all eight checks PASS, 95 Django / 18 R03 / 73 Harness, no skips. This includes
the five I03 Django tests again. No transport/API/model/migration/contract edit.

Real browser re-check passed normal initial state, anonymous/authenticated
GET-only retry, repeated read failure, registration/login saved-state restoration,
reload and keyboard Tab/Shift+Tab/Space/Enter/focus. Three sanitized screenshots
and [current UX record](../../agent-traces/MS7-I03-evidence/ux-recheck.json) supplement
the preserved historical evidence. Temporary servers/probe were stopped; runtime
files remain ignored. Final UTF-8/whitespace/links/source bindings pass.

Current candidate set: the original 51 paths plus four UX evidence files listed
in trace §18, **55 files** total (7 tracked modifications + 48 untracked).
Nothing staged. Commit/push/PR/Issue changes/merge not performed; independent
Руслан/Владимир Task Approvals and G3 still pending. Stop after the UX cleanup report.

## 14. Final publication / review handoff (2026-10-05)

Implementation commit `635e8ecaff65f2fdc7069656a7e5b47e863aa853`, 55 task-owned
files, preserves preparation `c0bfecfa53795c6b4fb07bb5ffb8ed0ff04dac66`.
Scoped staged audit/whitespace checks passed; no frozen R02A, model/migration,
API-business, secret or generated/runtime file changes. Non-force push succeeded.

[PR #26](https://github.com/Tramsey00/MathStart-Python/pull/26) targets `main` from
the existing task branch; includes `Closes #25`. GitHub confirmed review requests
for Руслан `Tramsey00` and Владимир `VladimirFrolov777`, verified against accepted
PR #22 reviews. Both Task Approvals are pending; Owner did not self-approve.

[Implementation CI run 37241717597](https://github.com/Tramsey00/MathStart-Python/actions/runs/37241717597)
completed **SUCCESS**, exact head
`635e8ecaff65f2fdc7069656a7e5b47e863aa853`. Fresh PostgreSQL smoke, full verifier
and accepted R02A/R03A checks all passed. Trace §19 records exact publication
actions. This Spec/Plan/Trace follow-up changes records only. Its own final SHA
and new exact-head CI run/result are recorded in the PR body/live checks after
push; wait for that run before the final publication report. Earlier stage 3/4
and UX stopping blocks are historical snapshots, not current publication status.

No merge or manual Issue #25 closure; G3 remains pending. Keep this plan active.
After the report, stop for Руслан/Владимир independent review; do not treat review
requests or green CI as human approval. Legacy favicon 404 remains non-blocking.

## 15. Ruslan auth UI feedback / same-PR follow-up (2026-10-05)

Starting branch/head matched `ms7-i03-auth-profile-onboarding` /
`dfe7a9205b0431df1b9e783c918a6efb25a33719`; clean checkout; PR #26 OPEN with
the same head. Existing review event by `Tramsey00` was CHANGES_REQUESTED although
its prose says APPROVED; record this discrepancy and require explicit re-review.
Владимир's review request remains pending. No Task Approval claimed by Owner.

Completed corrections: registration-only `maxlength=30`, matching helper/safe
field error and pre-action submit guard; accepted V02/model maximum 150 untouched.
Named native-button auth group, `aria-pressed`/controls, one visible section,
inactive disabled fieldset, first-field focus, retained mode after errors,
default Login after logout and locked switching during uncertain/pending actions.
Transport/CSRF/receipt/session and current-server-state authority remain unchanged.

Verification PASS: Node 33, targeted Django 64 (including I03 6); full eight-check
verifier 96 Django / 18 R03 / 73 Harness; accepted R02A 30; pip/locked runtime
consistency. Real browser PASS: 30/31, errors, auth, keyboard both switch directions,
360/768/1440 without overflow, actual grade PK and three modes, lost SELF_REPORT
acknowledgement/retry, reload and login saved-state restoration. See trace §20.

Evidence [review-auth-ui.json](../../agent-traces/MS7-I03-evidence/review-auth-ui.json):
11 new sanitized screenshots, 56 real API events, 13 source bindings. Prior
evidence is preserved history. Temporary runtime/observer/logs stay ignored and
servers/tabs are stopped after acceptance. No unrelated API/schema/stack work.

Commit/push uses only this scoped follow-up set, same existing branch and PR #26.
After push, confirm PR head and successful CI on that exact SHA; final head/run
proof lives in PR body/checks and final report. No new PR or merge. Keep the plan
active; independent re-review/Task Approvals and G3 remain pending.

## 16. Vladimir P2 credential-cleanup follow-up (2026-10-05)

- Confirmed clean starting branch/head and PR #26 head
  `62fe7bc569528fe109fd8139c2272b330adb303c`; exact-head CI SUCCESS.
- Read Vladimir's CHANGES_REQUESTED review on that head. Confirmed P2: successful
  acknowledgement cleared credentials, terminal failures and form switches did not.
- Fixed only I03 credential lifecycle: serialize operation then clear DOM;
  terminal cleanup; clear outgoing password on switch; keep immutable pending
  body/key and all transport/backend semantics. Added/strengthened regressions.
- Node **34**, targeted Django **64**, full verifier **8 checks** (96/18/73),
  accepted R02A **30**, dependency consistency and frozen pins **PASS**, no skips.
- Real PostgreSQL/Django browser **PASS** for 401/400, both keyboard switches,
  direct success, lost registration response/identical retry and saved-state
  rotation/restoration. Eight sanitized screenshots and 47 real API events in
  [security record](../../agent-traces/MS7-I03-evidence/security-auth-credentials.json).
  Trace §21 records exact commands, limits and the 15-path follow-up set.
- Publish ordinary commit/non-force push to existing PR #26 and re-request
  Vladimir's independent review. New SHA/exact-head CI status will be recorded in
  PR body/live checks after push; no claim of approval from verification alone.

Keep plan active. Do not create another Issue/branch/PR, manually close #25,
self-approve or merge. Руслан/Владимир independent Task Approval and G3 pending.
