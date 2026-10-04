# MS7-I03 stage 3 browser evidence

2026-10-04; Issue #25; branch `ms7-i03-auth-profile-onboarding`; HEAD remains
`c0bfecfa53795c6b4fb07bb5ffb8ed0ff04dac66`. Core is a local uncommitted diff.
**Historical stage 3 snapshot: browser PASS; final verification then NOT STARTED.**
Current local verification and authorized UX follow-up PASS; human gates PENDING.
See [UX re-check record](ux-recheck.json) and trace §18 for the current source
bindings and contextual retry behavior. Older images/manifests below intentionally
retain the previously tested state, including the old always-visible reload action.

Real Chromium 154.0.8037.98 / Django 5.2.16 / PostgreSQL 16.15. No mock API.
Documented runserver at 127.0.0.1:8000; a temporary transparent loopback observer
at :8001 recorded sanitized headers/status/payload metadata. Temporary probe
uses unmodified production consumer JS for read-only catalogue pagination.

Only synthetic identities appear. Password fields are empty in auth/error images;
no session/cookie/CSRF/idempotency-key values are stored. JPEG files are actual
viewport screenshots; browser scrollbar may make image width smaller than the
requested viewport. Actual dimensions/digests are in the manifest.

| Record | Contents |
| --- | --- |
| [Acceptance](acceptance.json) | Flows, keyboard, DOM, actual responsive widths, correction, targeted tests, limitations and source hashes. |
| [Network](network.json) | 99 real API events, safe header checks, rotation booleans and same-action body/key comparisons; opaque public cursors omitted. |
| [Pagination/browser probe](browser-pagination-probe.json) | Exact browser version; production consumer loads six real grades via three pages at page_size=2. |
| [Served assets](served-assets.json) | Actual served JS/CSS digests equal current source bytes. |
| [Screenshot manifest](screenshots.json) | JPEG dimensions and SHA-256 bindings. |

| Useful state | 1440px | 768px | 360px |
| --- | --- | --- | --- |
| Anonymous/login | [Auth](auth-1440.jpg) | [Auth](auth-768.jpg) | [Auth](auth-360.jpg) |
| Registration | [Form](registration-1440.jpg) | [Form](registration-768.jpg) | [Form](registration-360.jpg) |
| Profile/saved state | [Saved](saved-1440.jpg) | [Saved](saved-768.jpg) | [Saved](saved-360.jpg) |
| Onboarding choice | [Choices](onboarding-1440.jpg) | [Choices](onboarding-768.jpg) | [Choices](onboarding-360.jpg) |
| Invalid credentials | [Error](invalid-credentials-1440.jpg) | [Error](invalid-credentials-768.jpg) | [Error](invalid-credentials-360.jpg) |
| Expired session/recovery | [Error](session-error-1440.jpg) | [Error](session-error-768.jpg) | [Error](session-error-360.jpg) |

Additional captures: [logout → login](login-1440.jpg),
[grade selection](grade-selection-1440.jpg),
[START_ZERO selection](onboarding-selection-1440.jpg),
[START_ZERO saved](start-zero-saved-1440.jpg),
[SELF_REPORT uncertain outcome/retry](self-report-retry-1440.jpg),
[DIAGNOSTIC saved](diagnostic-saved-1440.jpg), [reload restoration](restored-1440.jpg),
[150-character synthetic username](long-username-360.jpg).
[Initial profile](profile-1440.jpg) is historical visual evidence before the logout
focus correction. Final saved-state images and responsive matrices are post-fix.

Found defect: logout focus attempted while its fieldset was disabled. Corrected
focus timing and reproduced the browser behavior in the test adapter. Browser
rerun passed; Node 19/19 and task Django 5/5 passed, no skips.

No duplicate IDs/JS stack traces; captured console warn/error list was empty.
Legacy favicon request returned server 404; recorded as pre-existing shell detail.
Single Chromium walkthrough does not claim a cross-browser/auditory screen-reader
audit. Default `/account/` catalogue was one real page; the separate production
consumer probe demonstrated multi-page behavior without changing product settings.

## Contextual retry UX follow-up

Recorded 2026-10-05. [Initial state without reload](ux-initial.jpg),
[state-loading error / contextual retry](ux-state-error.jpg),
[saved state restored after login](ux-login-restored.jpg).
[UX record](ux-recheck.json) includes hashes, final source/collected-asset bindings,
38 sanitized real API events, repeated read-error recovery and targeted/full checks.
Only synthetic identities; no credential/cookie/token/key values. Browser checks
passed normal initial state, GET-only retry, automatic auth restoration and native
keyboard/focus. The last status-only correction was followed by a real browser
repeated-error/focus re-check and a complete verifier run. See the record for
snapshot provenance; no historical evidence was replaced or deleted.
