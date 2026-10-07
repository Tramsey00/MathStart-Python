# MS7-I03 stage 3 browser evidence

## Screenshot storage after Owner cleanup (2026-10-06)

Current tree: **26 JPEGs**. The Owner requested removing obsolete
Login/Registration images: **24 JPEGs / 1,589,151 bytes** moved intact
to `var/archives/MS7-I03-auth/`, already ignored by `var/`. No I03 PNGs were present.
[Archive index](archived-auth-screenshots.json) records each hash/size and immutable
GitHub URL. Historical screenshot entries retain their original file/dimensions/
hashes and now include retrieval URLs/local archive paths. Older links below point
to that history rather than missing working-tree files. Counts such as 27/41/49/50
below describe their dated acceptance snapshots, not today's image set.

Retained: [current initial screen](quiet-initial.jpg), all eight security follow-up
captures, profile/onboarding/session-recovery images and their acceptance records.
No runtime/tests/contracts changed and no evidence results were re-written.
Removing images from this tree does not reclaim already committed Git-history
storage. No history rewrite or new browser acceptance is claimed.

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
| Anonymous/login | [Auth](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/auth-1440.jpg) | [Auth](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/auth-768.jpg) | [Auth](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/auth-360.jpg) |
| Registration | [Form](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/registration-1440.jpg) | [Form](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/registration-768.jpg) | [Form](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/registration-360.jpg) |
| Profile/saved state | [Saved](saved-1440.jpg) | [Saved](saved-768.jpg) | [Saved](saved-360.jpg) |
| Onboarding choice | [Choices](onboarding-1440.jpg) | [Choices](onboarding-768.jpg) | [Choices](onboarding-360.jpg) |
| Invalid credentials | [Error](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/invalid-credentials-1440.jpg) | [Error](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/invalid-credentials-768.jpg) | [Error](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/invalid-credentials-360.jpg) |
| Expired session/recovery | [Error](session-error-1440.jpg) | [Error](session-error-768.jpg) | [Error](session-error-360.jpg) |

Additional captures: [logout → login](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/login-1440.jpg),
[grade selection](grade-selection-1440.jpg),
[START_ZERO selection](onboarding-selection-1440.jpg),
[START_ZERO saved](start-zero-saved-1440.jpg),
[SELF_REPORT uncertain outcome/retry](self-report-retry-1440.jpg),
[DIAGNOSTIC saved](diagnostic-saved-1440.jpg), [reload restoration](restored-1440.jpg),
[150-character synthetic username](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/long-username-360.jpg).
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

Recorded 2026-10-05. [Initial state without reload](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/ux-initial.jpg),
[state-loading error / contextual retry](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/ux-state-error.jpg),
[saved state restored after login](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/ux-login-restored.jpg).
[UX record](ux-recheck.json) includes hashes, final source/collected-asset bindings,
38 sanitized real API events, repeated read-error recovery and targeted/full checks.
Only synthetic identities; no credential/cookie/token/key values. Browser checks
passed normal initial state, GET-only retry, automatic auth restoration and native
keyboard/focus. The last status-only correction was followed by a real browser
repeated-error/focus re-check and a complete verifier run. See the record for
snapshot provenance; no historical evidence was replaced or deleted.

## Ruslan auth UI review follow-up (2026-10-05)

[Current review record](review-auth-ui.json) binds the registration UI maximum 30
and single-form Login/Registration switcher. The older original/UX records and
150-character registration screenshot are historical; the current registration
UI accepts at most 30. Existing longer backend usernames remain valid for login.

| Current auth state | 1440px | 768px | 360px |
| --- | --- | --- | --- |
| Login | [Login](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/review-login-1440.jpg) | [Login](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/review-login-768.jpg) | [Login](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/review-login-360.jpg) |
| Registration | [Registration](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/review-register-1440.jpg) | [Registration](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/review-register-768.jpg) | [Registration](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/review-register-360.jpg) |

Additional actual captures: [31-character UI error](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/review-register-error.jpg),
[generic registration error](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/review-backend-register-error.jpg),
[safe login error](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/review-login-error.jpg), [saved state](review-saved-state.jpg),
[state restored after login](https://github.com/Tramsey00/MathStart-Python/blob/6706a25a8d7e94de214e1a2bbf6cb9420f595fc2/docs/agent-traces/MS7-I03-evidence/review-login-restored.jpg).

11 new native JPEG screenshots (41 total with preserved history), no credential/
cookie/token/receipt-key values or real personal identities. 56 sanitized real API
events include all eight surfaces, actual current-CSRF mutations/rotation and
same-body/key SELF_REPORT replay. Browser DOM input values are masked by tooling;
the 30-character success is established by the real returned server profile,
and the 31-character error by the visible associated alert and no registration
request until corrected. Thirteen source hashes bind this reviewed implementation.

Native Enter/Space switching, Tab/Shift+Tab, first-field focus, inactive-form
exclusion and visible 3px outline passed; responsive 360/768/1440 without overflow.
Real browser warn/error capture empty. Legacy favicon 404 remains non-blocking;
single-browser evidence does not claim cross-browser/auditory screen-reader QA.

## Vladimir P2 credential cleanup (2026-10-05)

[Security record](security-auth-credentials.json) binds the new source bytes:
13 source hashes, 47 sanitized real API events (208–254), 12 mutations with
current CSRF and unchanged receipt scope. Lost registration acknowledgement was
replayed with the same logical operation/body/key and returned the same account.
The local observer forwards the real backend; it truncates one actual response
after commit without replacing API data. Runtime observer/logs are ignored.

Eight new screenshots (49 total with preserved history):

- [Login 401, automatically blank password](security-login-401.jpg).
- [Registration 400, automatically blank password](security-register-400.jpg).
- [Returned Login after switch, native required validation](security-login-switch.jpg).
- [Returned Registration after switch](security-register-switch.jpg).
- [Pending registration / explicit retry](security-register-pending.jpg).
- [Registration restored after retry](security-register-success.jpg).
- [Direct registration success](security-register-direct.jpg).
- [Login restored saved grade/mode/completion](security-login-restored.jpg).

No manual password clearing before these captures. Native required validation
after Enter, blank-field screenshots and production-controller regressions
establish cleanup; masked DOM values are not used as empty-value evidence.
Only synthetic identities/public grade data; no password/cookie/token/key values
or EXIF metadata. Browser warn/error capture empty. No viewport override used.
Prior records remain historical; this fixes the subsequently discovered password
retention gap and does not retroactively claim it was covered by earlier audits.

## Quiet anonymous initial state (2026-10-06, local only)

[Initial page](quiet-initial.jpg) shows the introduction and auth switcher without
the duplicate prompt/status card. [Record](quiet-state.json) binds 13 current
source hashes, this sanitized native JPEG and 12 real API events (255–266).
Pre-action error / safe login 401 still reveal the alert card; contextual Enter
retry after a truncated real GET me response restores first-field focus.
Reload returns to the quiet anonymous state. No credential values or EXIF.
One new image, 50 total with all historical evidence preserved; no viewport change.
The record distinguishes completed checks from the interrupted default verifier
and its separately completed Harness group. No publication performed.
