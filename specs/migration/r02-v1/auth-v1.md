# Authentication/security adapter addendum v1.0.2

PROPOSED. Frozen R02A DTO/OAS/policy remain byte-identical. Baseline source:
users/http.py, users/views.py, users/services.py, users/models.py and
config/api_http.py/settings.py; independent tests users/tests and content/test_grades_api.py.

## Wire boundary

Eight implemented operations and exact request/response schema names/statuses
are in [route map](implemented-routes-v1.json). Strict UTF-8 JSON object;
application/json with encoding absent or UTF-8; raw body <=65536 bytes. Reject
malformed UTF-8/JSON, duplicate keys at any depth, NaN/Infinity, recursion failure,
unknown fields, wrong types/boolean-as-ID without coercion. Oversize400
LIMIT_EXCEEDED; other malformed400 INVALID_REQUEST, safe fixed message. Empty
logout body must be {}. Endpoint method mismatch400 INVALID_REQUEST, no default
FastAPI422/405 or slash307. GET/HEAD distinctions are in the route map.
Middleware auth/CSRF precedes body validation: private anonymous401, then CSRF403
on writes, then shape. Anonymous register/login still require verified CSRF.
Foreign/missing internal owner lookup404 NOT_FOUND; schema-invalid selected
grade400, unsupported stored grade slug503, not a fabricated number.

Success {data,meta:{request_id,version:'http-v1'}}; lists add pagination.
Error {error:{code,message,field_errors,retryable,request_id}}; fixed safe
field_errors {}, retryable only429/503. No SQL/DSN/password/body/digest/foreign
revision in errors. JSON UTF-8, sort_keys=True, ensure_ascii=False serialization
preserves replay bytes even jsonb reorders keys. All existing API responses,
including public grades, have Cache-Control: private, no-store. New request IDs
are UUIDs; replay returns persisted original request_id/status/body unchanged.
429 RATE_LIMITED has integer Retry-After seconds >=1. Database errors503
SERVICE_UNAVAILABLE. CSRF403 CSRF_FAILED; role403 FORBIDDEN; owner404;
digest409 IDEMPOTENCY_CONFLICT; state409 STATE_CONFLICT.

Policy limits40 steps,512 expression chars,128 tokens,16 nesting,12 numeric
digits,abs_power10,250ms expression/2000ms batch belong to future assessed
operations; do not claim current identity parser enforces these domain limits.
UNSUPPORTED/INDETERMINATE assessed200 and Tutor200 DEGRADED remain future
business outcomes. Preserve canonical202 persisted SUBMITTED/polling contract,
never invent it for registration or publication.

Slashless existing API paths return301 to the trailing slash in DEBUG=False,
including POST (the browser may discard its body); the baseline probe records
this rather than calling it404. Target explicitly preserves301 for these known
slashless paths, never FastAPI's default307. Clients always use canonical slash
paths and never follow a mutation redirect as a retry. Unknown API paths return
safe404. DEBUG unsafe slash errors are development diagnostics, not deployment
semantics. If reviewers prefer safer400/404 for unsafe slashless requests, that
is a separately approved behavior change, not baseline equivalence.

Grades GET ignores request body (including malformed JSON), as verified by the
disposable probe; only query parameters are parsed. Preserve this distinction
from mutation JSON parsing. GET CSRF/me likewise do not parse JSON bodies.
Cursor: <=1024 characters; only singleton cursor/page_size, ASCII size[0-9]{1,3}
and1..100. Payload exactly scope/page_size/created_at/id; strict int not bool,
0<id<2**63, aware zero-offset timestamp, route scope public:/api/v1/grades/;
salt content.grades.http-v1.cursor. Preserve Django signing JSONSerializer
(compact separators/ensure_ascii ASCII), optional zlib compression marker,
URL-safe Base64 without padding, TimestampSigner base62 time and salted HMAC
signature; no max_age is applied by baseline loads. V02 must verify independent
old/new signer vectors with retained verifier key ring. A different new signer
must read outstanding legacy cursors before it can replace emission.

## Credentials and validators

Registration backend username1..150 chars, UnicodeUsernameValidator
^[\w.@+-]+\Z; optional valid email; unique username, no email uniqueness.
Frontend registration max30 with30/31 tests; legacy login username up to150
must work. Match Django UserAttributeSimilarityValidator default0.7 against
username/first_name/last_name/email, MinimumLengthValidator8,
CommonPasswordValidator matching the versioned baseline list, and numeric-only
validator. Do not trim/normalize passwords. Invalid/duplicate registration400
generic message; missing username/wrong password/inactive login identical401,
including equivalent dummy expensive hash for absent users.

Preserve encoded password and algorithm/iterations verbatim on migration;
baseline default hasher pbkdf2_sha256 (configured Django defaults also include
pbkdf2_sha1, argon2, bcrypt_sha256, scrypt). Verify hashes independently using
synthetic deterministic salts/vectors and old iteration counts, Unicode and
wrong-password cases. Inventory only algorithm/count, never actual hashes/PII.
R01 zero users is not proof of compatible deployed algorithms. V03 chooses a
license-reviewed Django-independent verifier; unsupported algorithm blocks
cutover. Opportunistic successful-login rehash may follow reviewed baseline
policy, never bulk reset. Unusable-password marker stays unusable. Staff usable/
unusable creation and password change must preserve baseline validator behavior.

## Session/CSRF/rate

One HTTPS origin, opaque PostgreSQL-backed sessions, HttpOnly session cookie,
Secure in deployment, SameSite=Lax (CSRF cookie readable by bootstrap flow).
Rotate on every successful login, including same-user login; register establishes
session only if unauthenticated; exact authenticated register replay does not
rotate. Logout flushes/revokes; expiry/revocation and password auth-hash changes
invalidate other sessions. For staff changing their own password, preserve
Django update_session_auth_hash: rotate and update the current authenticated
session after success, while other sessions become invalid. One explicit
re-login at cutover is accepted; no password
reset. Session TTL baseline defaults1209600 seconds and CSRF cookie31449600
unless deployment settings differ and are explicitly recorded by V03.
Host allowlist/Origin+Referer checks, no permissive CORS or browser JWT/storage.
CSRF bootstrap returns masked token and may set cookie, creates no profile or
domain write. Validate tokens before parse; refresh CSRF on retry. Clear all
private client caches on logout/session loss. Staff and account never SSG export.

Login budget10 attempts/300 seconds per HMAC of server REMOTE_ADDR, shared DB
counter lock between workers. Count before authentication, including failed
credentials; reset after300s evaluated AFTER lock acquisition; attempt11 gets429
and remaining-window ceil Retry-After. Ignore arbitrary X-Forwarded-For. V05
may establish a trusted proxy list that strips forwarded headers at one origin;
otherwise REMOTE_ADDR remains the authority. No local-memory-only rate limiter.

## Receipt and anonymous scope bridge

Preserve IdentityReceipt UUID/scope/operation/key_digest/request_digest/user/
response/status/created_at/expires_at and unique(scope,operation,key_digest),
consistent response/status/user CHECK. key_digest SHA256 UTF-8 header.
request_digest SHA256 UTF-8 sorted compact JSON, ensure_ascii=False/allow_nan=False
of {owner,operation,canonical_route,body,expected_revision:body.get(...)}.
Array/raw string order is exact, no Unicode/math normalization. Registration
owner is bootstrap scope; onboarding digest owner is str(user.pk), scope user:<pk>.
Identity replay retained at least604800s and source uniqueness permanently;
current service does not delete expired receipts. Same key/changed digest409.
No raw password/body in receipt; request digest and safe result only, private.

Registration scope = session identity_registration_scope if present, otherwise
'bootstrap:' + legacy salted_hmac('users.register.bootstrap', csrf_secret,
algorithm='sha256') using baseline Django-compatible key derivation/signing
key. Transfer that scope before login rotates cookies. Do not recompute it from
the new CSRF value. Target bridge is a private server record binding old verified
CSRF bootstrap fingerprint/scope to the new opaque session; optional signed
HttpOnly Secure SameSite=Lax bootstrap ticket carries an opaque random reference,
never user/receipt/digest. Validate ticket signature, expiry and matching original
bootstrap proof server-side; retain bridge facts >=7days; validity/revocation and ticket expiry follow the P2 lifecycle below. Key ring retains required
legacy HMAC verifier keys for the replay window, secrets stored out of Git.
The receipt original scope/digest never changes when the bridge is introduced.

Lost-response cases must all work on disposable data: (a) DB commit then no body,
but login cookies received -> same owner/key/body replays; (b) body+Set-Cookie
both lost -> client still has pre-login CSRF cookie and immutable key/body;
verify original bootstrap proof, recover original scope, verify submitted
password against receipt.user if anonymous, and establish rotated session;
(c) page reload loses in-memory credentials -> GET restore only, then explicit
user re-login; never auto-create another account; (d) scope/session proof absent
or expired -> fail closed/re-login, never lookup receipt by key alone; (e) an
authenticated different user, inactive receipt owner or mismatched password
gets generic409 STATE_CONFLICT. A same-owner authenticated replay may return
the safe persisted result without retaining password. Changing scope must never
replay a different bootstrap's receipt even if key/body are equal.
V03 validates imported populated profile C and races; this design is proposed
and not claimed as a currently available bridge. If keys/proof cannot be
retained, a concrete human cutover decision is required before activation.

## Frontend contract

Preserve default login/switcher, quiet anonymous initial401, contextual GET-only
restore/retry, register30/backend150 and real grades PK. Pending action holds
immutable serialized body/key in memory only; fresh CSRF on retry without body
mutation. Clear DOM passwords after serialization and terminal outcome, clear
pending memory on terminal400/401/form switch/disposal; no logs/storage/screenshots
of credentials. Ignore stale responses using generation/request identity so
newer input/session state wins; preserve exact raw student input and step order
in future fixtures, never trim to hide stale conflict. GET does not increment
mastery or start diagnostics. Three onboarding modes only store profile choice.


## Review B07 precedence clarification

Method400 for identity endpoints applies only after earlier middleware outcomes.
Private identity routes return anonymous401 before CSRF or method handling;
authenticated unsafe requests require CSRF before endpoint400/body parsing.
Public identity resolved routes require unsafe CSRF first (missing/bad Origin403),
then method400. GradeListView is DRF csrf_exempt with no authentication: GET200,
other methods400 independent of token/Origin. Account require_GET follows CSRF:
safe HEAD/OPTIONS/TRACE405, unsafe missing CSRF403, unsafe valid CSRF405.
Public pages/sitemap/robots and unresolved404 fallback differ as documented in
content-v1.md; never impose one global middleware precedence on every family.

## P2 receipt bridge lifecycle (proposed, not implemented)

Retention is not authorization. Private PostgreSQL bridge facts contain opaque
bridge ID, immutable original scope/bootstrap fingerprint, nullable receipt
owner (bound once at registration commit), durable session_lineage_id, current session binding and revocation epoch,
ACTIVE/DETACHED/REVOKED/EXPIRED state, replay_until >= original commit+604800s,
and ticket version/expiry/revocation. Receipt scope/digests/result/uniqueness stay
in IdentityReceipt forever under the existing policy; no transition deletes or
rewrites them. Only the identity/session service may mutate bridge authority;
cutover import uses the exclusive target writer after old writers drain/revoke.
Cleanup is service-owned, not a frontend event or a receipt deletion job.
[Storage mapping](protocol-storage-mapping-v1.json) describes logical facts and
future reviewed additive DDL, not a migration or additional browser DTO.

Proof classes used in the transition table:
S = current authenticated active owner session, matching bridge session binding
and epoch. B = verified ORIGINAL bootstrap CSRF proof resolving exactly the old
scope; fresh request CSRF is separately mandatory and never substitutes for B.
T = signed unexpired nonrevoked HttpOnly ticket reference PLUS B; ticket alone
is insufficient. F = fresh same-owner login PLUS a server-authenticated transfer
binding from the original verified Django session/bridge. Owner authentication
alone does not select an anonymous receipt scope by key. For anonymous B/T replay,
also verify submitted password against active receipt.user; for authenticated
B/T/F replay require that exact owner, not a password for some other user.
No proof authorizes a mismatched body/digest/key/operation or inactive owner.

Bridge creation stores verified original scope before cookie rotation, binds
receipt owner with registration commit, then session/ticket establishment may
follow. DB receipt commit with both body/cookies lost can recover with B+password
even if no ticket was delivered. Once session is established, authenticated
same-owner exact replay does not rotate. Anonymous successful recovery rotates
session once, invalidates any previous binding/ticket, then issues a fresh ticket
version if tickets are used. Ticket use is not destructive single-use consumption:
same valid proof/key/body replays safely while current; versions and epoch revoke
superseded tickets. No raw password/CSRF/session token is stored in bridge facts.

| Transition | Bridge / ticket / owner-session effect | Proof, retry/replay, refusal and uncertain result |
| --- | --- | --- |
| Explicit logout (authenticated + CSRF, empty body) | Revoke current session, all bridges bound to THAT session lineage, and their tickets; increment their epoch, clear binding. Retain REVOKED facts and receipts. Other independent sessions are unchanged. | Return accepted200 completed:true only after durable revoke. Repeat with old session401; no logout receipt replay. Lost response: clear private client state, GET me only; anonymous401 reconciles session loss, still-authenticated result requires explicit user action, no blind POST retry. B/T/F cannot resurrect revoked bridge, even with same owner/password. |
| Account switch A -> B by successful login | Authenticate B first; atomically revoke A session lineage/bridges/tickets, clear old private binding, establish rotated B session. Never rebind A bridge to B. Failed login leaves A authority intact. | B cannot use A S/B/T/F or receipt; generic409 STATE_CONFLICT when authenticated mismatch. Repeated same-user login rotates but securely transfers its own ACTIVE bridge to new binding/epoch and revokes old ticket (no new receipt). Unknown login outcome: GET me; never repeat login automatically or reuse A pending body under B. |
| Session cleanup / natural expiry | Expired session is unusable; ACTIVE -> DETACHED, clear session binding and invalidate old S/epoch. Preserve original bootstrap and valid ticket facts through replay_until. Tickets can expire earlier; expiry never revokes receipt identity. | Before replay_until, B+password, authenticated same-owner B/T, or F may recover/rebind; expired/revoked ticket fails but independent B can still prove scope. Session/key alone fails closed409 on registration (private auth routes401); authenticated foreign owner409. Cleanup repeats are idempotent, never revive REVOKED; unknown cleanup/rebind commit must reread authoritative facts, no guessed success. |
| Django -> FastAPI cutover | Drain/revoke legacy writers and sessions; preserve receipts/digests/uniqueness and verified bridge transfer facts. Nonrevoked bridge -> DETACHED; no legacy session is authenticated by target. Retain valid T verifier keys/reference and B proof through replay window. Imported F mapping is private and owner-bound; no bridge can be minted from receipt key alone. | Accepted ONE explicit re-login, no password reset. After same-owner login, F or valid B/T rebinds. Pending onboarding replays by authenticated user:<pk> identity independently of bridge. Different owner/proof/key/body409; missing proof fails closed/re-login, never new registration. Unknown cutover checkpoint: stop target writes until exclusive writer/import provenance reconciles; no dual writer or automatic reverse cutover. |
| replay_until reached / ticket expiry | Ticket expiry revokes only T; bridge replay_until sets EXPIRED (facts retained >=7days), clears bindings/tickets. REVOKED stays revoked. | Expired bridge cannot select registration scope; GET restore and explicit login, no auto-create/key-only lookup. Existing onboarding receipt replay still owner-bound and retained, even beyond minimum window. Cleanup/repeated transitions return same durable terminal authority state. |

Internal lifecycle transitions are atomic under namespace -> sorted User ->
receipt then bridge/session locks in stable ID order at platform rank4. Revocation/rebind CAS rechecks
epoch, state, owner and session after locks; revocation wins against later use,
an earlier completed replay remains historical receipt truth. A second concurrent
rebind from an old epoch fails; it cannot mint another session or ticket. Revoked
bridges have no reverse transition. Natural expiry/cutover detach only, and cannot
undo earlier logout/account-switch revocation. Auth-hash invalidation/security
revocation follows logout revocation, not recoverable natural expiry.

Response precedence stays B07: private anonymous401 before CSRF, unsafe CSRF403
before body/proof; then safe409 STATE_CONFLICT for invalid/absent/revoked foreign
bridge proof,409 IDEMPOTENCY_CONFLICT for proven scope with changed body. No
foreign receipt existence, revision or proof detail leaks. Storage/unknown commit
is503 SERVICE_UNAVAILABLE, not success. Automatic retry is GET-only. Explicit
registration retry is allowed solely while the immutable pending key/body and
valid proof survive, using fresh request CSRF; terminal failure, logout, account
switch, disposal or form switch clears pending credentials. Unknown logout/login
uses GET me; unknown registration/rebind uses GET restore first and only an
explicit proof-valid replay of the SAME operation. A lost response after bridge
revocation never permits resurrection. No generic lifecycle HTTP endpoint or
blind receipt-based logout retry is introduced. V03 must prove real transaction,
ticket/signature/keyring, cutover and session races; the R02 model is synthetic.

The epoch in the model is an internal CAS observation, not a browser capability.
An original B proof is resolved to current facts server-side; a competing rebind
using an obsolete observed epoch fails without effects. A later explicit replay
may reread facts and prove B+password again after cookies were lost, producing
a rotated session but the same receipt/result and no additional account.

Cutover checkpoint identity and verified import provenance are durable private
identity-service facts. Repeating the same completed checkpoint is read-only,
including after a bridge was rebound to a target session; it must not detach
that target session again. A different/unknown checkpoint or unproven exclusive
writer halts writes and requires reconciliation. Authentication before account
switch occurs outside locks; then acquire namespace/session-lineage locks in
stable order and both old/new User rows in ascending PK. All bridge/session
binding changes share the lineage namespace and recheck current epoch after
the rank4 locks; cleanup cannot attach authority. Failed new-user authentication
does not revoke the old session or its bridge. ACTIVE committed bridges require
non-null owner and session binding; DETACHED never authenticates an old session.
Fresh deliberate registration uses its own newly verified bootstrap scope/key;
a pending replay with lost proof cannot be silently reinterpreted as that new
registration. Explicit onboarding replay after logout/re-login remains available
by authenticated same-owner user scope, independent of revoked anonymous bridge.

The durable session_lineage_id remains for revocation lookup when a session
binding is detached/expired. Same-user rotation keeps lineage; explicit rebind
associates the bridge to the newly authenticated/recovered owner session lineage
under epoch CAS. Logout/switch revoke bridges of the departing lineage only,
including detached records, without revoking another independent owner session.
