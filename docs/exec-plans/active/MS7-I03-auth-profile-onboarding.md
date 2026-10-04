# EXEC PLAN MS7-I03: Auth/profile/onboarding UI

- **Status:** Active; preparation only
- **Owner:** Илья
- **Reviewer / Task Approver:** Руслан и Владимир
- **Created / last updated:** 2026-10-04
- **Canonical Issue:** [#25](https://github.com/Tramsey00/MathStart-Python/issues/25)
- **Spec:** [MS7-I03](../../../specs/ui/MS7-I03-auth-profile-onboarding.md)
- **Trace:** [MS7-I03](../../agent-traces/MS7-I03.md)
- **Branch:** `ms7-i03-auth-profile-onboarding`
- **Baseline SHA:** `c945ef6f768564fbd876b8d95f61a83a6d8cbda2`
- **Gate:** G3
- **Deadline:** 09.10.2026, revised canonical v7.1 §20.4
- **FR coverage:** FR-01, FR-02
- **Human gate required:** Yes; independent Руслан and Владимир Task Approvals

```text
Implementation: NOT STARTED
PR: NOT CREATED
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

The user split work into five stages. **Only stage 1 is authorized now.** This
plan records later work, but does not execute or authorize it.

| Stage | Scope | Current status |
| --- | --- | --- |
| 1. Preparation | Canonical Issue, Spec, Exec Plan, Trace; document diff checks | COMPLETE; Issue #25 and three documents created; actual checks recorded in trace. |
| 2. Implementation core | Real-API auth/profile/onboarding UI | NOT STARTED; await later user instruction. |
| 3. Tests + browser acceptance | Automated tests, keyboard, DOM/network/console/screenshots | NOT STARTED. |
| 4. Verification + cleanup | Full verifier, scoped diff, plan/trace updates | NOT STARTED. |
| 5. Commit/push/PR | Only after checks; independent review/approval | NOT STARTED; no commit/push/PR authorization in preparation. |

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

## 5. Future implementation phases

Every phase below is **NOT STARTED**. Checks are planned, not executed results.

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

Do not carry out phase 1 merely because preparation is complete. Issue creation,
this plan and its checklist do not begin core work.

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

Current preparation checks:

```text
git status --short
git diff --check
git diff --stat
git diff
```

New documents remain untracked. Ordinary `git diff` does not include untracked
files: inspect each document with `git diff --no-index` against the empty input,
including whitespace and stat checks, without staging. Record actual results in
the trace. Ensure only these three files are new and tracked runtime is unchanged.

Future authorized verification uses `skills/verification/SKILL.md` and:

```text
python scripts/verify_repo.py
python -m unittest discover -s tests -p test_r02a_contract.py -v
python manage.py test users.tests.test_identity users.tests.test_postgres content.test_grades_api
git diff --check
```

Add the actually implemented I03 tests and relevant existing I02/frontend checks.
Run from the configured project environment; report skips/environment failures
honestly. Run fresh DB/migration verification only if an independently justified
schema change enters scope. Current preparation executes no backend tests, DB
setup, bootstrap, browser acceptance or verifier. Upstream CI is inherited evidence.

After accepted G1, apply applicable §17 Harness engineering-run requirements;
do not claim a current production Harness run merely from plan creation.

## 9. Risks and human review

| Risk | Handling |
| --- | --- |
| Separate PR #24 backend/migration approval record was not found | Руслан/Владимир clarify evidence before final acceptance; I03 consumer approval and merged grade runtime remain available. |
| Local DB upgrade/server/browser prerequisites unexecuted | Verify in the later authorized environment/test phase; report actual setup limitations. |
| CSRF rotation or logical retry key replaced | Exercise lost acknowledgements and stale-token recovery with unchanged action identity. |
| SELF_REPORT/DIAGNOSTIC claims exceed saved choice | Match exact V02 payload/state; no diagnostic or Progress implementation. |
| Shared shell/control extension regresses Content or keyboard | Scoped reuse, escaping/focus checks and existing Content regression. |
| Tooling/architecture scope grows | Surface a demonstrated requirement and seek the specified human decision before changing stack/contracts. |

Task Approvers are Руслан and Владимир; Owner Илья cannot self-approve the task.
Task acceptance, PR merge and G3 closure are distinct. Move this plan to completed
only after completion/human acceptance in a later authorized phase; never now.

## 10. Completion checkpoints

- [ ] Stage 2 core implementation complete within the spec boundary.
- [ ] Required automated tests and real browser acceptance complete.
- [ ] Verification, scoped diff and final evidence complete.
- [ ] Authorized commit/push/PR created and exact final-head CI passes.
- [ ] Руслан and Владимир Task Approvals recorded; required merge completed.
- [ ] I03 downstream handoff recorded; G3 status assessed independently.

Stage 1 outcome and exact checks are recorded separately in the trace. No task
completion, PR, Task Approval or G3 acceptance is claimed by this plan.
