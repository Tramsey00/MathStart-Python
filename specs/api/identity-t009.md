# MS-T009 — Identity addendum, 13.11.2026

Implementation proposal for Issue #68; independent security/architecture review
and human acceptance remain pending. Extends existing Identity, not the frozen
R02 baseline. Existing IDs, usernames (case sensitive), hashes, profile modes,
learning data, receipts and applied migrations are preserved.

Registration: username 1–30 Unicode word characters or `@ . + -`, exact case;
login continues to accept existing names up to 150. New passwords: 15–128 code
points, at most 512 UTF-8 bytes, retained common/numeric/similarity rejection;
no trim, composition requirement or scheduled expiry. Legacy login verification
retains its old rules with a 4096-byte pre-hash ceiling. UI uses autocomplete,
paste and password visibility. No email login or required registration email.

The current onboarding stage is grade selection: selected_grade_id in existing
UserResponse. A selected grade makes materials directly available. It does not
complete SELF_REPORT/DIAGNOSTIC, change their historical data or write mastery.
Future onboarding scenarios and the existing complete endpoint remain intact.

## Additional API

All paths below end in `/`; closed JSON DTOs, http-v1 envelope, private no-store.
GET is accepted only for state. Mutations accept only POST and require existing
Host/Origin/CSRF proof. No request-supplied owner ID is accepted. JSON body <=8KiB;
edge caps account at 8KiB and auth at 64KiB. Current passwords <=4096 UTF-8 bytes.

| /api/v1/account/ | Request | Result |
| --- | --- | --- |
| state/ GET | none, authenticated | email nullable, email_verified boolean, mail_available boolean |
| email/ POST | current_password, email (blank removes) | completed; authenticated owner, reauthentication |
| password/ POST | current_password, new_password | completed; revoke every session including current and all action tokens |
| sessions/ POST | current_password | completed; revoke every session including current |
| recover/ POST | username | same completed response whether known, unknown or without confirmed email |
| verify/ POST | token | completed; authenticated owner only |
| reset/ POST | token, new_password | completed; no session required; all sessions/tokens revoked |

Existing error envelope/statuses apply: invalid/expired/consumed token 400;
unverified owner 403; duplicate confirmed address 409; rate 429 + Retry-After;
mail unconfigured 503 for every recovery request. Unknown mutations are never
automatically replayed. UI reads authoritative state then requires a new visit
before another mutation. Existing registration/onboarding receipts retain their
owner/conflict/expiry behavior; no technical replay controls in product UI.

## Address/token policy

New recovery addresses are ASCII, trimmed and lowercased in full. A single
confirmed canonical address can belong to only one account, enforced by a PG
unique constraint. Pending addresses do not reserve ownership. No merge or
automatic verification of historical auth_user.email. This separate recovery
address does not overwrite that historical field. Address replacement/removal
requires current password, removes previous verification immediately and
revokes all action tokens. It becomes eligible only after explicit confirmation.

256-bit random tokens, separate verify/reset purposes, SHA-256 digests only in
DB, bound to owner/address. Verify TTL 60 minutes; reset TTL 30 minutes. A new
issuance replaces that purpose's tokens. User-row then token-row locks serialize
consumption against issue/change/revoke; only one concurrent consumer commits.
Links use trusted configured origin and a fragment; raw token never goes in a
GET, Referer or access log. Page clears the fragment, keeps token only in memory;
refresh requires reopening the original email link. GET does not consume a token.
Auth/account headers restrict referrers/framing/caching; production CSP is scoped
to private pages and does not change lesson policy. No third-party reset assets.

## Budgets and audit

PostgreSQL counters with atomic row locks across workers, DB clock, fixed windows,
admitted requests including success count. HMAC subjects, no plaintext IP/login.

| Action | Scope | Limit/window |
| --- | --- | --- |
| Login | IP; IP+exact login; exact login across IPs | 300/5m; 10/5m; 100/5m |
| Registration | IP | 30/hour |
| Recovery | IP; exact login | 60/hour; 5/15m |
| Sensitive account changes | IP; owner | 60/15m; 10/15m |
| Token consumption | IP | 60/15m |

Large school IP budget permits distinct pupils; narrow pair budget contains
ordinary guessing; global account budget bounds distributed guessing without
a permanent lock. Targeted temporary denial remains a known tradeoff; maximum
login wait is 5 minutes, recovery is separate. CAPTCHA/MFA/Redis not introduced.
Counters survive worker restarts. On budget calls, delete windows older than two
days, expired action tokens, and security events older than 30 days. Events store
UUID, action/rate-limit kind, HMAC subject and DB time only, no bodies/secrets.
No separate monitoring platform. Startup runs no tests/DDL/cleanup.

Peer address is authoritative by default. Production can explicitly set
MATHSTART_TRUSTED_PROXIES as JSON exact known edge IPs/CIDRs; only those peers
can supply one valid X-Forwarded-For. Edge overwrites that header. Never configure
0.0.0.0/0 or trust arbitrary client headers. Production topology/proxy values
require operator review; host-dev trusts no forwarded headers. HTTPS sets Secure
cookies/HSTS; existing HttpOnly session, SameSite=Lax, rotation remain intact.

## Mail and schema rollout

MailDelivery is an injected delivery port. Runtime defaults to UnconfiguredMail,
never FakeMail. Tests alone inject FakeMail; messages never enter reports. The
provider must support transactional delivery without click/open tracking and
must not log secret links. Unconfigured delivery is a uniform 503. Confirmation
delivery failure is 503; issuance may already have committed, so no blind replay.
Recovery delivery runs after the generic response, and provider failures are
audited without changing the known/unknown account response. A response acknowledges
the request, not actual inbox delivery. This small local adapter has no durable
mail queue/retry; process loss can require a new request after the rate window.
Actual delivery, bounce behavior,
timing/enumeration resistance with that provider and domain setup need separate
integration review and controlled live checks after Ruslan's decision.

Proposed connection: Unisender Go transactional HTTPS API, dedicated sender on
the MathStart domain, SPF/DKIM/DMARC, tracking disabled, runtime-only API secret,
bounded delivery timeout. No account, payment or live delivery is created here.
Final sender/domain/provider are human decisions.

v01_0003 adds four Identity tables, no edits of v01_0001/0002. Reviewed schema CLI
adds TARGET_0002 profile for an existing exact target schema, preserving normal
signed plan, expiry, DB/role/code/source binding and maintenance/drain checks.
Fresh installs include the new revision. No schema work occurs during startup.

Research applied: [OWASP Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html),
[OWASP recovery](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html),
[W3C accessible authentication](https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html),
[MDN passwords](https://developer.mozilla.org/en-US/docs/Web/Security/Authentication/Passwords),
[Khan Academy learner settings](https://support.khanacademy.org/hc/en-us/articles/204707040-How-can-I-edit-my-account-settings),
[Unisender Go DNS](https://godocs.unisender.ru/dns-setup),
[transactional API](https://godocs.unisender.ru/web-api-ref).
