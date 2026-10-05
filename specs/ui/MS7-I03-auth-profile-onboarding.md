# SPEC MS7-I03: Auth/profile/onboarding UI

- **Status:** Implementation published; browser acceptance and final local verification PASS; independent human acceptance pending
- **Owner:** Илья
- **Reviewer / Task Approver:** Руслан и Владимир
- **Canonical Issue:** [#25](https://github.com/Tramsey00/MathStart-Python/issues/25)
- **Branch:** `ms7-i03-auth-profile-onboarding`
- **Pull request:** [#26](https://github.com/Tramsey00/MathStart-Python/pull/26), OPEN; independent reviews requested
- **Implementation commit:** `635e8ecaff65f2fdc7069656a7e5b47e863aa853`
- **Baseline SHA:** `c945ef6f768564fbd876b8d95f61a83a6d8cbda2`
- **Milestone Gate:** G3
- **Acceptance deadline:** 09.10.2026, revised v7.1 §20.4
- **Direct FR coverage:** FR-01, FR-02
- **Exec plan:** [MS7-I03](../../docs/exec-plans/active/MS7-I03-auth-profile-onboarding.md)
- **Trace:** [MS7-I03](../../docs/agent-traces/MS7-I03.md)
- **Last updated:** 2026-10-05
- **Latest review feedback:** Registration UI limit 30; single-form auth switcher; local/browser verification PASS (see §18)

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

## 1. Goal and authority

Deliver **Auth/profile/onboarding screens on real API**. Students can register,
sign in/out, select a grade, choose an onboarding mode, and restore saved server
state through accessible forms. Preparation defines the consumer boundary; no
UI or runtime is executed by these documents. The core snapshot and targeted
results are recorded in §13 and the trace; overall acceptance remains pending.

The canonical requirements source is MathStart Technical Specification **v7.1,
G0 ACCEPTED**:
`.local-docs/MathStart_Technical_Specification_v7_1_SECTION20_PARALLEL_DEADLINES.pdf`.
The local PDF is not published by this task. v6 is not a requirements source.

```text
PDF SHA-256
e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd

Accepted R02A OpenAPI SHA-256
133aae117333e66b40662ec4fdb47fc02ee08e7aeecbbd9cbb200d5468ca7362

Accepted R02A manifest SHA-256
35da935f191f34103023e53ac4855313232ef95e6e4eb312bdfc9f9b55065b03
```

Task card: §24, pages 68–69. Applicable requirements: §11, §16, §17, revised
§20, §21 and §25. Revised §20 takes precedence over the old NORMAL/EARLY dates
inside the card; the acceptance deadline is **09.10.2026**. Downstream consumers
are **MS7-I11 and MS7-I14**. I03 acceptance does not independently close G3.

## 2. Accepted inputs and dependencies

Read `AGENTS.md`, `PRODUCT.md`, `ARCHITECTURE.md` and the existing verification
skill. Preserve ADR-0001 (Django), ADR-0002 (exercise/public boundary), ADR-0003
(Progress ownership) and the accepted R02A HTTP/eligibility addendum associated
with ADR-0004. This task does not reopen their frozen decisions.

| Type | Canonical edge | Available baseline input |
| --- | --- | --- |
| HARD | MS7-I02 | PR #22 merged as `46c1b3ddbb9611482d288262249152be839ddae6`; required Руслан/Владимир approvals recorded. |
| CONTRACT | — | Accepted R02A remains a named API input, not a new dependency edge. |
| HANDOFF | — | No additional canonical edge. |
| INTEGRATION | MS7-V02 | PR #19 merged as `150e569b51a2ef84d2d17a25c675e364c808d2fc`; required Руслан approval recorded. |
| V02 runtime correction | PR #24 / Issue #23 | Merged as baseline `c945ef6f768564fbd876b8d95f61a83a6d8cbda2`; Issue #23 CLOSED; grades route available. |

The former grade-source blocker is removed. I03 consumer acceptance is recorded
in [review 5406384114](https://github.com/Tramsey00/MathStart-Python/pull/24#pullrequestreview-5406384114).
That review covers consumer handoff only. It does not constitute Руслан's
backend/migration Task Approval; see the evidence note in §11.

Specific inputs:

- `specs/ui/MS7-I02-ui-foundation.md`, `docs/agent-traces/MS7-I02.md` and its plan.
- `templates/base.html`, `templates/ui/components/{button,card,field,state}.html`.
- `static/mathstart/css/ui/{tokens,foundation}.css` and I02 foundation/schema JS.
- `specs/ui/ui-state-fixtures-v1.schema.json` and `specs/ui/fixtures/ui-states-v1.json`.
- `specs/api/MS7-R02A-http-eligibility.md`, `openapi-v1.json`,
  `schemas/dto-v1.schema.json`, `http-policy-v1.json`, `candidate-manifest-v1.json`.
- `docs/exec-plans/active/MS7-V02-accounts-rights.md`, `docs/agent-traces/MS7-V02.md`.
- `specs/api/MS7-V02-grades-runtime.md`, V02 grades plan/trace and current runtime.

Historical upstream OPEN/PENDING headers do not override merged GitHub/main
state. They are preserved; I03 does not edit accepted upstream records.

## 3. Scope and exclusions

In scope: registration; login/logout; profile; onboarding with **START_ZERO,
SELF_REPORT, DIAGNOSTIC**; CSRF; safe errors; keyboard-accessible forms;
saved/restored server state; real V02 integration and the public grade catalogue.
Use existing Django Templates, HTML/CSS and progressive JavaScript with I02
components/tokens. Canonical file areas: `templates/`, `static/`, UI fixtures and
browser tests. Concrete screen URLs and file names are implementation choices
to record in the later implementation phase, not additional API requirements.

Out of scope:

- Mathematical assessment, Attempt/exercise renderer, checker or validator secrets.
- Actual diagnostic session implementation; DIAGNOSTIC only selects the mode.
- Numerical skill initialization/progress for SELF_REPORT.
- Progress calculations, client-authoritative verdict/progress, Tutor, adaptive practice/history.
- Backend API/model/migration changes without a separate demonstrated requirement.
- Seed/bootstrap changes, unrelated refactoring and frozen R02A modifications.
- A new frontend stack/toolchain without necessity and human approval.

## 4. Actors and workflow

Anonymous students access registration/login and the public catalogue.
Authenticated students access their own profile, onboarding and logout.

1. Obtain CSRF through the real bootstrap API; read `users/me` to establish the
   current session/profile state. Its anonymous 401 is an authentication state.
2. Register or log in with real credentials; refresh CSRF after success/rotation.
3. Fetch all catalogue pages needed for grade selection. Display `title`, retain
   returned `id`, and send that same identity to profile/onboarding mutations.
4. Choose one of the three modes. POST the closed onboarding payload and reflect
   confirmed backend state. Do not report a diagnostic session or mastery change.
5. Restore saved state using GET `users/me` after reload/login and reconciliation.
6. Logout using the private mutation; reconcile a lost acknowledgement through
   session state rather than assuming repeat logout returns success.

## 5. Invariants and persistence

The backend is authoritative for identity, selected grade and onboarding state.
Only Progress changes long-term knowledge state through validated evidence.
This feature does not create or mutate knowledge evidence.

I03 introduces no models, migrations, seed or bootstrap changes. Existing V02
persists User, StudentProfile, session and identity receipts. Frontend pending
input is not proof of a save. Saved state is restored through the API, not an
authoritative local profile cache.

`onboarding_complete=true` confirms the V02 onboarding choice is saved; for
DIAGNOSTIC it does not prove diagnostic exercises were performed. SELF_REPORT
here saves the mode only: no topic/skill list or numerical initialization exists
in the accepted `OnboardingRequest`.

## 6. Exact baseline API contract

Source of truth: accepted OpenAPI/DTO/policy plus `users/urls.py`, `views.py`,
`http.py`, `services.py`, `config/api_http.py` and Content grades runtime at the
baseline. All paths have trailing slashes. Transport uses UTF-8 JSON and
same-origin Django session cookies. No JWT/Basic authentication is introduced.

All request objects below are closed (`additionalProperties=false`). Mutations
send `Content-Type: application/json` and `X-CSRFToken`, including anonymous
registration/login. A hidden form token alone does not satisfy these JSON APIs.
Private anonymous requests return 401 before CSRF/schema processing.

### Shared response shapes

`UserResponse` returned by register/login/me/PATCH/onboarding:

```text
{
  "data": {
    "id": integer|string,
    "username": nonempty string,
    "selected_grade_id": integer|string|null,
    "onboarding_mode": "START_ZERO"|"DIAGNOSTIC"|"SELF_REPORT"|null,
    "onboarding_complete": boolean
  },
  "meta": {"request_id": UUID string, "version": "http-v1"}
}
```

These are type descriptions, not literal JSON payloads. Current runtime emits
integer User/Grade PKs. `meta.version` is optional in the accepted schema and
present in runtime. No email, profile UUID, role, password or progress is returned.

Common safe `ErrorEnvelope`:

```text
{
  "error": {
    "code": accepted error code,
    "message": nonempty safe string,
    "field_errors": {field: [nonempty string, ...]},
    "retryable": boolean,
    "request_id": UUID string
  }
}
```

Current identity/catalogue errors use empty `field_errors={}`; the UI must support
form-level errors without inventing field-specific server messages. Responses
use `Cache-Control: private, no-store`. Unknown fields are rejected.

### Endpoint matrix

| Method / path | Auth | CSRF | Idempotency-Key | Exact request | Success |
| --- | --- | --- | --- | --- | --- |
| GET `/api/v1/auth/csrf/` | Anonymous allowed | No | No | No body | 200 `{data:{csrf_token:nonempty string},meta}`; sets CSRF cookie. |
| POST `/api/v1/auth/register/` | Anonymous bootstrap; an existing authenticated session is not a new registration | Required | Required | `{username:string,password:string,email?:string}` | 201 `UserResponse`; establishes session. |
| POST `/api/v1/auth/login/` | Anonymous allowed | Required | No | `{username:string,password:string}` | 200 `UserResponse`; establishes/rotates session. |
| POST `/api/v1/auth/logout/` | Session required | Required | No | `{}` (`EmptyRequest`) | 200 `{data:{completed:true},meta}`. |
| GET `/api/v1/users/me/` | Session required | No | No | No body | 200 `UserResponse`. |
| PATCH `/api/v1/users/me/` | Session required | Required | No | `{selected_grade_id:integer\|string}` only | 200 `UserResponse`. |
| POST `/api/v1/onboarding/complete/` | Session required | Required | Required | `{selected_grade_id:integer\|string,mode:"START_ZERO"\|"DIAGNOSTIC"\|"SELF_REPORT"}` | 200 `UserResponse`. |
| GET `/api/v1/grades/` | Public; anonymous allowed | No | No | No body; optional `cursor`, `page_size` only | 200 `GradeListResponse`. |

Register requires username length 1..150 and nonempty password in the wire
schema; Django username/email/password validators additionally apply. Optional
email must be a valid email string; omit an absent email. Login requires nonempty
username/password. Do not invent password length rules or new profile fields.

The user-authorized review correction narrows **I03 registration UI** to 30
characters (`maxlength=30` plus an explicit submit guard before action/key or API
creation). Help text and safe associated error use the same limit. The frozen
RegisterRequest/backend remain 1..150; no model, migration, V02/DTO change.
Login and restored existing usernames retain their backend-compatible behavior.
PATCH has `minProperties=1` and only the grade field, making that field necessary.
Profile/onboarding grade IDs must resolve to existing positive Grade PKs below
`2**63`; runtime also accepts ASCII decimal strings of at most 19 characters.
Null is allowed in a response, not as a grade mutation input.

### State, errors and retry per operation

| Operation | Backend state / read behavior | Important errors and retry semantics |
| --- | --- | --- |
| CSRF GET | Creates no auth session, profile, receipt or domain state; obtains CSRF cookie/token. | Safe to repeat. Refresh after successful register/login because CSRF rotates. |
| Register | Creates hashed-password nonstaff User, initial null-grade/null-mode/incomplete profile, session and receipt. | 400 invalid/duplicate registration details; 403 CSRF; 409 `IDEMPOTENCY_CONFLICT` or `STATE_CONFLICT`; 503 DB failure. Same key + unchanged canonical body + original bootstrap/session identity replays original 201/body without another User/Profile/receipt. |
| Login | Establishes session, creates a missing profile if needed; each successful login rotates session and CSRF. | Missing/wrong/inactive credentials share 401 `AUTHENTICATION_REQUIRED`, `Invalid username or password.` Budget 10 attempts/300s/IP, including success; 429 has `Retry-After`. No receipt replay; a repeated success rotates again. |
| Logout | Invalidates auth session; profile/onboarding state remains. | 401 anonymous, 403 CSRF, 503 DB failure. Repetition after logout returns 401; reconcile uncertain outcome with GET me. |
| GET me | Reads current owner's saved profile; does not create a missing profile. | 401 anonymous, 503 DB failure. Authoritative recovery read, including after historical receipt replay. |
| PATCH me | Sets only current owner's selected grade; creates profile if missing. | 400 invalid/nonexistent grade or forbidden extra fields; 401/403/503. Same value does not create another profile. No receipt; reconcile via GET me before deciding to repeat. |
| Onboarding | Saves selected grade, mode and completion flag with an owner-scoped receipt. No Assessment/Progress/diagnostic-session mutation. | 400 invalid grade/mode/extra fields or missing key; 401/403/503. Same key/body replays original 200/body without duplicate SELF_REPORT mutation. Changed body with same key is 409 `IDEMPOTENCY_CONFLICT`. New explicit choice uses a new key. |
| Grades | Read-only public catalogue; no session, profile, onboarding, receipt, evidence or attempt writes. | 400 invalid query/cursor/size; 503 DB or unmappable row. Safe repeat with unchanged query; see pagination below. |

Registration/onboarding receipts are retained for at least seven days; current
runtime retains them beyond that minimum. Preserve one key for retries of one
unchanged logical action. Receipt identity is scoped to the verified bootstrap
identity for registration and authenticated owner for onboarding. Losing those
cookies/session is not a cross-browser registration recovery contract. Never
rotate the key simply to retry an uncertain save. A receipt replays historical
bytes, even if the profile later changed: use GET me to recover current state.

General errors: 400 `INVALID_REQUEST` / `LIMIT_EXCEEDED`, 401
`AUTHENTICATION_REQUIRED`, 403 `CSRF_FAILED` / `FORBIDDEN`, 404 `NOT_FOUND`
for unavailable/foreign resources, 409 conflict codes, 429 `RATE_LIMITED`,
503 `SERVICE_UNAVAILABLE`. Runtime sets `retryable=true` only for 429/503.
On CSRF failure obtain a fresh token; this is not permission to change an
idempotent action's key/body. On 429 respect `Retry-After`; on network/503 retain
the unresolved action and safe user input, without claiming a save. Do not
blindly retry login/logout as receipt-backed operations.

### Grade catalogue and identity

```text
{
  "data": [{"id": integer|string, "number": integer 1..12, "title": nonempty string}],
  "meta": {
    "request_id": UUID string,
    "version": "http-v1",
    "pagination": {
      "next_cursor": nonempty string|null,
      "page_size": integer 1..100,
      "has_more": boolean
    }
  }
}
```

Each closed item contains exactly `id`, `number`, `title`. Runtime `id=Grade.pk`,
`title=Grade.title`; `number` is derived by Content from its canonical grade slug.
Slug, timestamp, description and display order are not public fields. The UI
does not parse slugs or inspect database internals.

Display **title** and use returned **id** as option value and `selected_grade_id`.
For example a returned `{id:70,number:5,title:"5 класс"}` requires sending 70,
not 5. The example is synthetic; no identity is hardcoded.

Pagination is ascending `(created_at,id)`, default page size 20, maximum 100.
Treat cursors as opaque and URL-encode them; continue `next_cursor` with the same
page size until `has_more=false`. No offset or numeric-school-year ordering is
promised. Later new rows may appear; pagination is not a catalogue snapshot.
Empty `data=[]` is successful empty state; 400/503 is not empty success. Repeated
or unknown query parameters, changed page size, and invalid/tampered/cross-route
cursors receive safe 400. Unmappable rows receive safe 503, not fabricated data.

## 7. Security and public/server boundary

Use the existing owner-scoped `/users/me/`; send no owner, user ID, role or private
profile UUID to select an account. No arbitrary account lookup is added. Missing,
wrong and inactive login credentials must remain indistinguishable to the UI.
Do not transform safe backend errors into account-existence hints.

Escape usernames/catalogue titles and error text; associate errors with controls.
Do not expose secrets, passwords, CSRF/session tokens or real personal results
in logs, trace screenshots, fixtures or local/session storage. Credentials remain
transient form input. Existing HttpOnly session authentication stays server-owned.
No validator secrets, answer keys, canonical solutions or public checker enter
the frontend. I02 fixture gallery remains a marked demonstration, not a real save.

## 8. UI behavior and accessibility

Reuse I02 shell, components, design tokens, loading/error/empty states. Distinguish
pending submission, confirmed saved state, unauthenticated state and recoverable
failure. Preserve entered safe form data after a recoverable error; do not retain
passwords as persistent saved state. Show only the profile fields the API supports.

Provide associated labels, native keyboard-operable controls, visible focus,
reachable submission/retry actions and error/status announcements. Verify Tab,
Shift+Tab, Enter and applicable native selection keys. Mobile checks reuse the
I02 360/768/1440 widths and preserve existing Content/navigation behavior.
Browser evidence includes DOM/network/console assertions and sanitized screenshots;
record actual browser versions. Fixture-only tests cannot establish API integration.

## 9. Acceptance and negative acceptance

Local implementation checks and browser/final verification are recorded in
§14–15 and the trace. The task-level acceptance checklist below remains subject
to independent human review; local PASS does not record Task Approval:

- [ ] Registration and login/logout work through the real API with CSRF rotation.
- [ ] Profile selection uses all required grade pages and returned IDs, including `id != number`.
- [ ] START_ZERO, SELF_REPORT and DIAGNOSTIC choices are saved and restored via real V02.
- [ ] Saved profile/onboarding state survives reload and later login via GET me.
- [ ] Retry/lost acknowledgement preserves logical-action identity and does not duplicate SELF_REPORT mutation or registration.
- [ ] Invalid credentials and foreign-account cases remain safe and nondisclosing.
- [ ] Backend-required CSRF is enforced for every mutation, including anonymous auth.
- [ ] Keyboard forms, errors, focus, loading/empty/failure and mobile behavior are demonstrated.
- [ ] No false saved state, fabricated progress/verdict, diagnostic completion or skill initialization is presented.
- [ ] Existing Content behavior and frozen R02A bytes remain intact.
- [ ] Task-specific automated tests, browser acceptance and applicable canonical verification pass.
- [ ] Final-head CI, scoped diff/trace and Руслан/Владимир independent Task Approvals are recorded before task completion.

## 10. Required tests and future verification

Required task tests: **three onboarding paths, saved state, retry, invalid
credentials, keyboard**. Cover registration/login/logout, CSRF/session rotation,
grade identity/pagination, profile persistence and safe errors as part of these
flows. Test the UI's actual request/response handling; do not merely re-test DTO
constants or substitute synthetic success fixtures for real API acceptance.

Existing upstream evidence to preserve:

- `content/test_grades_api.py`: `test_catalogue_id_is_accepted_by_all_three_onboarding_modes`
  gets grade ID 70 for number 5 and submits returned ID through real-CSRF V02 for all modes.
- `content/test_grade_migrations.py`, `content/test_bootstrap.py`: upstream ID/relation/timestamp preservation.
- `users/tests/test_identity.py`: retry, saved state, all modes, invalid credentials, CSRF, rotation, nondisclosure.
- `users/tests/test_postgres.py`: upstream concurrent identity/receipt/rate-limit behavior.
- I02 template/JS/escaping/keyboard foundation tests and browser evidence.

After implementation is separately authorized, select meaningful UI tests using
the configured Django/Python/JS tools; run relevant Users/Content regressions and
R02A contract tests. Complete real browser acceptance with DOM, network, console,
sanitized screenshots and keyboard walkthrough. Then run
`python scripts/verify_repo.py` and applicable contract/frontend checks according
to `skills/verification/SKILL.md`. Record actual commands, versions, exit codes,
skips and environment limitations. Do not invent a Ruff/mypy/pytest/Playwright
pass or add a toolchain merely to obtain evidence. After G1, apply the engineering
run requirement in §17 when that accepted Harness is available; do not claim it
was performed in preparation.

Initial preparation verification was limited to document status/diff review.
Stage 2 subsequently ran task-owned and targeted regression tests. Stage 3 real
PostgreSQL/browser acceptance and the post-correction targeted rerun passed.
Stage 4 then passed the complete canonical verifier and relevant extra suites;
exact commands and coverage are recorded in §15 and the trace.

## 11. Risks, human gates and completion

| Risk / evidence limit | Handling |
| --- | --- |
| Historical upstream OPEN/PENDING labels | Use accepted GitHub/main/user state; preserve frozen documents. |
| PR #24 separate backend/migration approval not located in prior pre-flight evidence | Record the missing approval evidence for Руслан/Владимир clarification before final acceptance. Consumer approval and merge are verified; the grade-source blocker is removed. I03 does not perform backend-owner approval. |
| Local runtime DB upgrade/browser setup not executed in preparation | Resolved in authorized stage 3: existing migration applied, unchanged bootstrap, collected static and real PostgreSQL/browser walkthrough. |
| Replayed receipt differs from subsequently changed profile | Recover current state with GET me. |
| Catalogue pages/order/identity assumed from small seed | Follow accepted pagination and use returned IDs; no number-to-PK mapping. |
| Product-wide SELF_REPORT/DIAGNOSTIC semantics exceed current consumer DTO | Persist mode only; defer actual progress/session behavior to owning tasks. |
| Existing generic I02 field component lacks specific password/select behavior | Core adds optional native input semantics with preserved defaults; browser label/password/select/focus checks passed. |

Preparation completion means one canonical Issue and three reviewed documents
exist. Overall I03 remains incomplete until runtime acceptance, required tests,
verification, final-head CI, independent Руслан/Владимир Task Approvals and the
authorized PR/merge workflow are complete. No approval or G3 closure is inferred.

## 12. Links

- [Canonical Issue #25](https://github.com/Tramsey00/MathStart-Python/issues/25)
- [Exec plan](../../docs/exec-plans/active/MS7-I03-auth-profile-onboarding.md)
- [Trace](../../docs/agent-traces/MS7-I03.md)
- [Accepted grades handoff](../api/MS7-V02-grades-runtime.md)
- [I02 spec](MS7-I02-ui-foundation.md)
- [V02 trace](../../docs/agent-traces/MS7-V02.md)
- PR/demo/browser artifacts: not created in preparation.

## 13. Stage 2 core snapshot (2026-10-04)

Starting HEAD: `c0bfecfa53795c6b4fb07bb5ffb8ed0ff04dac66`, clean branch
`ms7-i03-auth-profile-onboarding`. Core changes are uncommitted.

Entry point: GET `/account/`, a task-owned presentation route with no business
mutation. Forms are powered by existing API operations only. Thin routing/view
glue is separate from `users/urls.py`, `views.py` and `services.py`.

The controller restores current server state through GET me, displays safe
catalogue titles and sends original returned IDs. One pending action freezes
serialized payload/key in page memory; conflicting submissions are blocked until
an uncertain result is resolved. An explicit new action creates a new key.
Passwords and pending action data are not stored in browser storage. Reload
restores confirmed server state; it does not persist credential-bearing drafts.

Each mutation obtains fresh CSRF. Successful registration/login refreshes CSRF
and reads GET me. A known auth acknowledgement followed by a failed recovery read
blocks forms and offers restoration instead of another registration. Non-receipt
login/logout/profile retries first reconcile current server state. Private retries
check the session owner before another mutation. Login failures remain generic.

Native POST forms, labels, password/autocomplete semantics, legends/radio groups,
required select controls, error associations, live status/alerts and focus handling
are implemented using I02 components/tokens. No diagnostic session or numerical
skill/progress behavior is added.

Targeted tests PASS (details in trace). Actual keyboard/mobile/browser DOM/network/
console/screenshots and final repository verification remain **NOT STARTED**.
This paragraph records the stage 2 stopping state; stage 3 results follow below.
No stage 2 commit, push, PR, Issue change or merge was performed.

## 14. Stage 3 browser acceptance (2026-10-04)

User-authorized scope: real `/account/` browser acceptance, documented local
runtime preparation, I03-owned fixes and sanitized evidence. HEAD remains
`c0bfecfa53795c6b4fb07bb5ffb8ed0ff04dac66`; core remains uncommitted.

PASS on Chromium **154.0.8037.98**, Django **5.2.16**, Python **3.14.7** and
PostgreSQL **16.15**. Applied the existing `content.0002_grade_created_at`, ran
unchanged `bootstrap_site`, collected static and used documented `runserver`.
No model/migration/API/contract/business-semantic change was authored.

Real flows passed: registration, logout/login, catalogue/profile save, all three
mode selections, reload/later-login restoration, safe invalid credentials and
other-tab logout recovery. Catalogue `5 класс` returns PK **1**, number **5**;
PATCH/onboarding send returned **1**. All mutations used current CSRF; receipt
headers appeared only on registration/onboarding. Actual auth rotation was
observed without storing token values. Production consumer pagination was also
exercised with three real pages at `page_size=2` in a read-only probe; normal
account UI used the actual six-row catalogue at its default `page_size=20`.

A loopback transparent observer forwarded the UI's requests to the unchanged
Django/PostgreSQL API. Two controlled lost acknowledgements after real
SELF_REPORT writes demonstrated transport replay and explicit keyboard retry;
unchanged keys/bodies resulted in four onboarding receipts for four logical
operations despite six POST attempts. No mocked API success or profile state.
DIAGNOSTIC remains mode selection, SELF_REPORT remains mode persistence only.

Keyboard Tab/Shift+Tab/Enter/Space/native grade arrows/radio arrows passed, with
associated labels/errors, visible focus, disabled/loading/pending states and no
trap. Found and fixed logout focus attempted before its fieldset was enabled.
The regression adapter now models disabled-fieldset focus rejection. Red test
reproduced the defect; post-fix **19/19 Node** and **5/5 Django** tests passed.
Actual browser logout now focuses the enabled login username field.

Registration/login, profile/onboarding, saved and safe error layouts passed at
actual **360/768/1440px** widths, including a real 150-character synthetic
username on mobile. DOM had no duplicate IDs; browser warn/error capture was
empty and no JS stack trace was observed. Legacy `/favicon.ico` server 404 is a
pre-existing shell request, not an I03 failure. One-browser walkthrough does not
claim a cross-browser or auditory screen-reader audit.

Evidence: [index](../../docs/agent-traces/MS7-I03-evidence/README.md),
[acceptance record](../../docs/agent-traces/MS7-I03-evidence/acceptance.json),
[sanitized network](../../docs/agent-traces/MS7-I03-evidence/network.json).
No passwords/cookies/CSRF/key values are retained. Tested source hashes and
served/source equality are recorded. Final verifier, CI, commit/push/PR, human
Task Approvals and G3 closure remain pending; Issue #25 is unchanged.

## 15. Stage 4 final local verification (2026-10-04)

The full verification-skill entry point passed all eight checks, including the
complete PostgreSQL Django suite (95 tests), R03 contracts (18) and Harness unit
suite (73), without skips. Additional Node checks passed 24 tests (19 I03 and
5 I02); accepted R02A contracts passed 30 tests. Exact commands, upstream coverage
and tooling versions are recorded in the trace and active plan.

All 27 screenshots were re-inspected; JPEG dimensions/digests, 12 tested-source
bindings, three served-asset hashes and local evidence links matched. Sanitized
network evidence retains 99 events with 21 current-CSRF mutations and no secret
values. The stage 3 evidence remains a historical snapshot. Keyboard/responsive
acceptance still applies to the unchanged implementation bytes.

Scope audit found no API/business-semantic, model/migration, frozen R02A, seed,
Progress or diagnostic-runtime changes. All 17 frozen manifest pins and the
manifest itself match HEAD. Corrected the I03 documents' previously miscopied
manifest digest above; no frozen artifact was edited. No implementation fix was
needed in stage 4. Legacy favicon 404 remains non-blocking.

Local verification is complete; commit/push/PR, exact-head CI, independent
Руслан/Владимир Task Approvals, merge and G3 acceptance remain pending.

## 16. Contextual state-loading retry UX (2026-10-05)

User-authorized UX cleanup: normal anonymous/authenticated states have no manual
state-reload button. Automatic GET me on opening the page and after successful
registration/login remains unchanged. Failed restoration or session reconciliation
offers **Повторить загрузку**; it reads the existing GET users/me only and does
not replay a mutation. A successful read hides the button. Failed/repeated reads
show an error status rather than an obsolete loading message.

Recovery moves keyboard focus after controls are enabled: anonymous state to
login username, authenticated state to profile title, or to the pending mutation
retry when applicable. CSRF/receipt transport, backend auth/API semantics and
authoritative server state are unchanged. No extra normal-state action is needed.

Regression tests, real API/browser keyboard re-check and full verifier passed;
see [UX evidence](../../docs/agent-traces/MS7-I03-evidence/ux-recheck.json) and trace.
Stage 3/4 snapshots remain historical; the new record binds the final UX source
bytes. The above sections describe their local-stage snapshots; current
publication facts follow. Human Task Approvals and G3 remain pending.

## 17. Publication / independent review (2026-10-05)

Published implementation commit `635e8ecaff65f2fdc7069656a7e5b47e863aa853`
(55 task-owned files) in [PR #26](https://github.com/Tramsey00/MathStart-Python/pull/26),
base `main`, head `ms7-i03-auth-profile-onboarding`. Preparation commit is
preserved. Review requests confirmed for Руслан (`Tramsey00`) and Владимир
(`VladimirFrolov777`), whose accounts were verified in accepted I02 reviews.

[CI run 37241717597](https://github.com/Tramsey00/MathStart-Python/actions/runs/37241717597)
completed **SUCCESS** on that exact implementation SHA, including fresh PostgreSQL
smoke, full verifier and R02A/R03A checks. A normal documentation-only follow-up
records publication; its SHA/new exact-head CI evidence is kept in PR #26's body
and live checks after push. No source or acceptance-evidence changes in the
publication record; see trace §19 for exact actions and provenance.

Independent Task Approvals **PENDING**; request is not approval. Issue #25 remains
OPEN; no manual closure, self-approval or merge. G3 **PENDING**. Single-browser
limits and legacy favicon 404 remain non-blocking. Keep the Exec Plan active
until the required independent human acceptance.

## 18. Ruslan auth UI review corrections (2026-10-05)

The Owner explicitly authorized two scoped corrections in existing PR #26:
registration username UI maximum 30 and a Login/Registration switcher in place
of two simultaneously visible forms. This instruction changes the consumer UX,
not the accepted backend registration contract described in §6.

Default anonymous mode is **Вход**. Two native `type=button` controls in a named
group use `aria-pressed` and `aria-controls`; the active button is filled and the
inactive button outlined using existing I02 tokens. The inactive section is
`hidden` and its fieldset disabled, excluding it from the normal tab order.
Enter/Space activation focuses the enabled first username field. Errors keep
the submitted auth mode; switching clears obsolete errors. Busy or pending
mutation/retry locks the switcher so immutable operation body/key cannot change.
Successful auth retains CSRF refresh/current GET me; logout returns to Login.

Registration username 30 is accepted. A 31-character prefilled/programmatic
value is rejected before action/key/CSRF/API creation with a static safe error,
`aria-invalid`, associated field error and focused alert. Native maxlength also
constrains ordinary typing. Existing long backend usernames can still log in and
restore; no truncation or backend-limit workaround is introduced.

Automated results: **33 Node** (28 I03 + 5 I02), **64 targeted Django** (I03 6,
V02 43, grades 10, I02 5), full eight-check verifier (**96 Django / 18 R03 /
73 Harness**), **30 R02A** and dependency consistency PASS, no skips.
Real Django/PostgreSQL browser checks passed both switch directions/focus,
30/31 boundary, errors, auth/rotation, saved state, three modes and SELF_REPORT
same-operation retry. Login/Registration layouts have no horizontal overflow at
360/768/1440. Console warn/error capture empty; legacy favicon 404 non-blocking.

Current evidence: [review record](../../docs/agent-traces/MS7-I03-evidence/review-auth-ui.json)
and its 11 new sanitized screenshots, 56 real network events and 13 source hashes.
Older captures remain historical snapshots. No backend/API/model/migration,
transport, frozen contract, Progress or diagnostic-engine changes. Publication
uses the same branch and PR #26; new exact-head CI is verified there after push.
Both independent approvals remain required. Руслан's existing GitHub event is
CHANGES_REQUESTED despite APPROVED prose; request alone/text alone does not
resolve that GitHub gate. No self-approval, manual Issue closure, merge or G3 closure.
