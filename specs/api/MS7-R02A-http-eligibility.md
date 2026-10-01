# SPEC MS7-R02A: HTTP and eligibility addendum v1

- **Status:** Candidate for independent human review; acceptance PENDING
- **Owner:** Руслан
- **Reviewer / Task Approver:** Владимир
- **Milestone:** G1 contract closeout
- **Relation:** FOLLOW-UP / ADDENDUM TO FROZEN R02
- **Normative source:** MathStart Technical Specification v7.1, G0 ACCEPTED
  2026-09-30, §§4–11,15–17,21–22,25–27,30,32.
- **Frozen inputs:** ADR-0002 and `../exercises/R02-exercise-architecture.md`;
  R03/ADR-0003 supplies unchanged event names and numerical semantics.
- **Proposed ADR:** `../../docs/adr/ADR-0004-http-eligibility-addendum.md`
- **Plan:** `../../docs/exec-plans/active/MS7-R02A-http-eligibility.md`

## Deliverables and authority

`openapi-v1.json` is the sole canonical OpenAPI artifact. OAS 3.1 JSON uses
JSON Schema 2020-12; `schemas/dto-v1.schema.json` owns reusable wire DTOs.
`http-policy-v1.json` owns machine-readable operation, revision, lifecycle,
idempotency, exposure and limit rules. `schemas/scenario-v1.schema.json` is a
fixture-only contract, not a public API component. Fixtures are synthetic
specification examples, not seeds or persisted runtime evidence.

Version `1.0.0` / metadata `http-v1` identifies this HTTP artifact. Exercise
`contract_version` and additive `version` are equal aliases of one immutable
exercise version counter, as required by R02. They are not independent counters.
The server-bound ExerciseVersion id, exercise id and version are authoritative.
Public difficulty bands easy/medium/hard map to difficulty_level 1–2/3/4.

This document specifies future endpoints; no endpoint, model, database migration,
Progress reducer, CompletionFact implementation or provider is supplied here.
Frozen R02 stays accepted. The new artifact and D-022/023 require Vladimir's
acceptance of their precise digest before V02/I02 use them as accepted upstream.

## HTTP surface and common rules

The OpenAPI contains all 37 method/route operations from §11: Identity,
Content, Attempts, Diagnostics, Progress, Practice, Tutor and Operations.
Namespace `/api/v1/`, snake_case, trailing slash, UTF-8 JSON. No API v2 or
alternative canonical route is introduced.

Django Session Auth applies to student data and assessed exercises. Published
grades/topics/theory, CSRF bootstrap and minimal health are anonymous-readable.
Registration/login bootstrap a session; email is optional and no unverified
recovery channel is promised. Login failure is indistinguishable for missing
username and bad password. Session cookies rotate at login. Every mutation,
including registration/login/logout, requires `X-CSRFToken` matched to the CSRF
cookie obtained through GET auth/csrf/. The CSRF bootstrap may set a cookie;
GET creates no Attempt, selected session item or domain evidence.

Owner-scoped lookups include attempts, sessions, conversations, progress/history,
and referenced previous_attempt/context IDs. First authenticate, then restrict
lookup to the owner. Missing and foreign owned objects share a generic 404
envelope. Never expose foreign revision, identifier, action or eligibility in
errors. Unauthenticated student requests produce generic 401 independent of
object existence. 403 is reserved for CSRF and roles without disclosing an
owner-secret resource. Content topic IDs preserve ContentPage identities/slugs;
new resource identifiers are UUIDs. All timestamps are aware UTC, precision up
to six fractional digits; deterministic examples use fixed UUIDs and timestamps.

Paginated GET responses carry meta.pagination: next_cursor (null at end),
page_size, has_more. Default 20, maximum 100; invalid sizes/cursors are 400.
Stable ascending `(created_at,id)` order and opaque owner/filter-bound cursors
prevent overlap/drift when fetching the next page. Catalogue resources without
public created_at still have server-side stable ordering facts; timestamps need
not be disclosed solely for pagination. Private responses are not cached in a
public shared cache.

Success is `{data,meta}` with mandatory meta.request_id, optional artifact
version, mandatory pagination only for list operations. Error is
`{error:{code,message,field_errors,retryable,request_id}}`. The revision conflict
subtype adds current_revision and canonical owner-safe reload_url; other conflicts
do not disclose digests, private response bodies or foreign resource facts.

| HTTP | Meaning |
| --- | --- |
| 400 | malformed/schema-invalid request, size/shape limit exceeded |
| 401 | session authentication required |
| 403 | CSRF failure / forbidden role without owner-secret disclosure |
| 404 | missing or foreign owned resource |
| 409 | revision / idempotency / exercise version / state conflict |
| 429 | rate limited, mandatory Retry-After seconds |
| 503 | safe completion unavailable; retry/reconcile explicitly |

UNSUPPORTED is a 200 assessed business result, never automatically HTTP error
or WRONG. Safe provider fallback is 200 with service_state DEGRADED. Tutor
message creation may return 201 when a message was created; a fallback response
uses 200 DEGRADED explicitly. Health readiness returns a typed safe health
envelope with 503 when necessary DB/config are unavailable; provider outage with
working core fallback returns 200 READY and provider DEGRADED/UNAVAILABLE.
Health never returns credentials, SQL, exception text, model keys or prompt data.

Submit may return 202 only for a persisted SUBMITTED Attempt with nonnull
operation_id, snapshot_digest and submitted_at. GET `/api/v1/attempts/{id}/`
is its repeatable status route. Poll at 1/2/4 seconds, then manual retry using
the original submit key. A transient failure leaves a recoverable operation;
network failure does not mean WRONG. No background queue is asserted to exist.
Other actions are synchronous in this contract; no unpollable 202 is offered.

## Revision, ordered input and version binding (D-022)

Assessed lifecycle: STARTED -> SUBMITTED -> COMPLETED, or STARTED -> ABANDONED.
COMPLETED has outcome CORRECT/WRONG/UNSUPPORTED/INDETERMINATE; outcomes are not
states. SELF_CHECK uses STARTED -> REVIEWED via explicit confirmed reveal,
or STARTED -> ABANDONED. It cannot submit for mathematical assessment.

Initial revision is 1. PUT draft sends a complete valid `{payload,steps}` draft,
contract_version and expected_revision. Server validates mode/input/step schemas
and limits before replacing; expected_revision must equal current revision.
Successful draft, submit and abandon advance revision by one. Help updates
exposure, not draft revision. Stale saves return 409 REVISION_CONFLICT with
current_revision and GET reload_url; clients retain raw input for reconciliation.
State is checked after exact idempotent replay and before editing a frozen draft.

Submit sends expected_revision and contract_version, requires Idempotency-Key,
and freezes exactly the existing draft, version, resulting revision and ordered
steps into snapshot_digest. Submit does not accept a second ambiguous answer
payload. Clients first PUT their complete draft, then submit its acknowledged
revision. Edits and submit serialize; for the same expected_revision exactly one
wins. Late draft after submit is STATE_CONFLICT. Draft-winning submit at old
revision is REVISION_CONFLICT. SUBMITTED and terminal drafts never change.

Client steps retain step_no, step_type, payload, raw_text. step_no is one-based,
contiguous, unique and ordered ascending in the submitted array. Reordering is
allowed by replacing/renumbering the full STARTED draft. Clients do not set
step_id, normalized_repr or parse_status. Server returns stable step_id and all
six R02 fields; types and parse enums are unchanged. Subject payload fields are
untrusted dynamic data, validated against the frozen exercise public schema.
No arbitrary payload is permission to run code or accept mathematical truth.
Raw strings and array order are preserved before normalization and digesting.

ExerciseVersion is immutable after publication. A started attempt continues to
use its bound frozen version even if archived or superseded. Archival prohibits
new attempts; it never swaps the checker/version of an open or historical
attempt. Client version mismatch deterministically returns VERSION_CONFLICT.
Post-submit correction creates a new owner-scoped Attempt referencing
previous_attempt_id; the original snapshot is untouched. A substantive new
published version is a distinct exposure key; a version bump to evade eligibility
is prohibited and requires publication review.

## Help, disclosure and positive credit (D-022)

Exposure is keyed by `(user,exercise_version)`, carrying maximum help level,
reveal time and prior positive credit. A new Attempt does not clear any of it.
Hint/reveal is persisted transactionally before disclosing reviewed content.
Level 0 means no help; requested levels 1–3 remain bounded hints. Level 3 must
not secretly reveal a complete one-step solution. A full solution is returned
only by the explicit confirmed reveal response, never exercise GET, ordinary
Attempt/result, prompt/context, public metadata, cached bundle or source map.

Before reveal, Tutor chooses a schema-valid reviewed hint-bank action belonging
to the bound version. Assessment checks owner/exposure/level and records the
help before returning prepared text; arbitrary generated math is not shown.
After reveal bounded explanations are escaped, with safe fallback. Tutor cannot
write Progress or override eligibility. Context binds topic/version/attempt
server-side. Bounded output/input limits and rates are inherited from §§9–10/16,
not an authorization to use a live model.

Help, submit and finalization serialize on Exposure. Submit freezes raw solution;
finalization freezes the eligibility decision under the Exposure lock and
reserves any positive credit atomically. A hint/reveal committed before submit
or while SUBMITTED before finalization is considered by finalization. Pending
submit does not grant independence. Once COMPLETED, its recorded decision is
immutable; subsequent help/reveal cannot revoke an earlier independent result.
Exposure shown on later GET can change while the recorded completed eligibility
and award remain frozen. `eligibility.independent` and `positive_credit_eligible`
describe the frozen decision for COMPLETED, prospective server eligibility for
STARTED, and false/PENDING before evaluation of SUBMITTED.

Independent correct requires CORRECT, supported validated input, no earlier
hint/reveal exposure for the version and no prior positive credit. Any earlier
hint makes later same-version correct work helped (CORRECT_AFTER_HINT where
applicable). Reveal prevents new positive credit, including diagnostic correct;
neutral completion/history remain. An unassisted supported DIAGNOSTIC_CORRECT
qualifies as independent, as inherited from R03. At most one credited positive
event per user/version: repeated correct completion remains CORRECT and is
recorded without another mastery gain or fake WRONG. SELF_CHECK/view/reveal,
UNSUPPORTED and INDETERMINATE do not become assessed positive success.
Only validated domain evidence can enter Progress; numeric deltas, reducers and
CompletionFact schema remain in R03/R03A scope.

## Request identity, crash recovery and retry (D-023)

The operation policy explicitly identifies idempotent mutations: creates,
submit, hints, reveal, next, finish, self-report; abandon and onboarding complete
also preserve stable action identity. Draft PUT instead uses full replacement
with expected_revision; a lost acknowledgement reconciles through GET. Login,
logout and profile patch use their stated session/update semantics, not receipts.
GET never requires Idempotency-Key.

Receipt scope is owner+operation+key; concrete resource route is part of digest,
so reusing a key for a different object in the same operation conflicts. Register
before identity exists scopes the bootstrap key to its CSRF/session identity;
after creation the receipt binds to the created user. No credentials are logged.
The request_digest includes owner, operation identity, concrete canonical route,
request body and expected_revision (null when absent). Canonical UTF-8 JSON
sorts object keys with compact separators; array order/raw text are retained,
NaN/Infinity rejected. It does not mathematically or Unicode-normalize input.
Passwords in identity requests are processed privately; receipts/digests are
never public DTOs or logging fields.

Same key and digest returns the persisted previous HTTP status/body/operation,
without another domain action, hint escalation or evidence. Replay is checked
after auth/owner/CSRF/schema gates but before current revision/state checks.
Different digest under that key returns 409 IDEMPOTENCY_CONFLICT. Processing
receipts refer to the same operation; clients poll canonical state. Finalization
is itself permanently unique by immutable source identity and snapshot/version.

Receipts survive >=604800 seconds (seven days). Expiry can remove short-lived
HTTP replay data, never permanent action/evidence source uniqueness or the
user/version positive-credit guard. A retry of a completed attempt after expiry
cannot resubmit its snapshot. A new correct Attempt after expiry cannot credit
the same version again. Future persistence must enforce these guards with DB
constraints and short atomic transactions, keeping computation/LLM outside locks.
Reference fixtures prove allowed serial outcomes, not PostgreSQL locking.

## Minimal downstream DTO decisions

DTOs describe wire information needed by §11 and accepted I01, without inventing
future ORM fields. Session schemas expose state/policy/current item/counters and
terminal reason. POST next accepts current_item_id and ADVANCE/SKIP: a retry or
refresh preserves the selected item, does not reserve another. GET restores it.
Different-key next for a consumed/stale current_item_id conflicts rather than
skipping two items. Finish is permanently terminal; retry cannot select a new
item. Diagnostics cap 10; helped/revealed/skip results remain neutral as §10
requires. NO_CANDIDATE permits START_ZERO by explicit onboarding choice.

Practice exposes immutable target/origin, selection reason, server streak and
safe return route. One active session per user; create when one is active returns
STATE_CONFLICT (exact receipt retry returns the original session). Max seven
items including skip. Success is three independent correct on distinct versions,
or mastery>=70/confidence>=60 after >=1 item. Wrong/help/reveal/unsupported/skip
reset streak. Server chooses parent/catalogue when origin is archived. Client
does not select an arbitrary checker, candidate, streak or success verdict.
Finish reason is an intention checked against server policy, not a client truth.

Progress DTOs return server projections/history; no client-authored mastery,
confidence or events. Self-reports are once per skill, only before assessed
evidence under onboarding policy; repeats return already_reported_skill_codes
without another event. They do not prove mastery. Topic aggregate is weighted by
Content-owned mappings. Dynamic raw payload is the only intentionally open data
object; metadata and response DTOs are closed against extra fields. Further
subject/UI fields need an additive reviewed contract; this schema defines no
hidden correctness rules or broad opaque response objects.

## Verification and handoff

`python -m unittest discover -s tests -p test_r02a_contract.py -v` validates the
official vendored OAS 3.1 structural schema (source noted beside schemas), DTO
meta-schemas, offline resolvable refs, all §11 routes, wire fixtures and negative
shapes, frozen R02 names/examples, auth/CSRF/header/revision requirements,
secret leakage and health allowlists. Serial scenarios cover both edit/submit
orders, help/reveal before/after pending/completed submit, cross-attempt exposure,
same/different-digest retry, safe owner 404, version archival, SELF_CHECK,
neutral outcomes, diagnostic independence, repeated finalization and receipt
expiry. Schema validation alone cannot prove absence of answer-equivalent prose;
publication/hint-bank human review and downstream leakage tests remain required.

The existing eight canonical checks remain unchanged. A separate reviewed CI
step runs this suite; PostgreSQL fresh-install and locking/runtime integration
belong to downstream implementation, not this reference. The candidate digest,
actual commands/results/limitations and human gate are in
`../../docs/agent-traces/MS7-R02A.md`. Accepted digest is recorded only after
Vladimir reviews the final artifact, with applicable green CI at final SHA.
