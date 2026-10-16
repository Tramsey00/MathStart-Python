# I02/I03 implementation checkpoint

Scope was narrowed by the user to I02/I03 on2026-10-16. Account and staff write
forms are deferred. Their exact unverified WIP is preserved separately in commit
`bcdb121eccc7643de154b7e8b3f70544cb209766`, branch
`ms7-mig-frontend-i04-wip`, parent`24d06112bcd6abcd1abad9b052de14a0a7b49e8e`.
That checkpoint is not part of this candidate and has no acceptance claim.

The implementation consumes a publisher-owned immutable H-BUILD-INPUTS release,
checks the trusted receipt digest and exact file coverage/hash/size, validates
V02 DTO/body/assets/relations, then prepares internal decimal ID labels without
rewriting the frozen numeric wire artifacts. React Router framework mode
prerenders the complete reviewed route manifest. Public packaging removes only
the Router hydration runtime; authored HTML and ordered scripts remain. Ordinary
links use full-document navigation. Node is build-only.

The V02 render_page(page,context,canonical_url) adapter uses an externally trusted
output-manifest digest, matching release/index/page semantics, HTML hash and
canonical origin/path. Query catalogue HTML is produced from the same pinned
Python projection, preserving Unicode casefold/strip behavior and escaping query
and labels. The catalogue_full digest is bound to the artifact. Unknown paths
remain404 through the serving gateway; this is not an SPA rewrite policy.

Staff UI has only28 canonical GET interfaces: nine registered resource
list/detail/history reads plus publication_state. It uses server authorization,
private/no-store, frozen migration-r02-v1 envelopes, exact int64 numeric transport
and escaped fields. The account route remains the accepted I01 placeholder.
No write form or future assessed runtime is exported by this candidate.

## Observed checks before the first source commit

- Locked npm ci succeeded with Node24.19.0/npm11.17.0, existing accepted lock,
  one registry socket after connection resets. No dependency version changed.
- Typecheck passed four actual stages: frozen identity generation, frozen staff
  read generation, React Router route types and TypeScript noEmit.
- Existing+new Vitest suite119/119 passed before staff-read additions.
- Focused staff/int64/query regression suite27/27 passed after reviewer fractional
  token correction. `1.0000000000000001` and `9007199254740990.1` now fail before
  a rounded Number can satisfy an integer schema; exact exponent integers work.
- Python artifact boundary suite4/4 passed, including corrupt receipt/missing/
  added/changed file rejection and query/label escaping.
- Actual build04 from reviewed development inputs produced279 pages/280 HTML
  URLs+robots/sitemap,422 files including manifest. Input index:
  `7c65edcc6423edd6f5b6e4a7cd18f09fecd1ccaceb4b36112bdc84e7172779d3`;
  trusted input receipt:
  `9b81f963b2a84d25ae80f322f4d6f1d18453c44ff1dca870fc489dda90186136`;
  output manifest:
  `fc176a6d76e58a5e87b5a3bce31f403a4207e109f56f84a80c460fc0385e1763`.
  The measured R03 build receipt has703 assertions. This is a dirty development
  artifact, not final-SHA release acceptance; later source changes require rebuild.
- Initial Chrome360 artifact-preview public browser run11/11 passed in44.295s:
  complete body/head manifest, no-JS catalogue/GET search and nine script-family
  representatives with navigation/back/resize. Preview is not active-release/API
  evidence. Chrome360 actual controls/F01–F04 smoke8/9 passed; its one test failure
  assumed exact1024 rather than the preserved three-significant-digit display
  1.02e+3. The test now follows the existing display precision; rerun pending.

## Remaining required evidence

Complete build on committed source; all distinct style and script families;
Chrome/Edge/Firefox at360/768/1440; focused matched live legacy/target captures;
manual ordinary-scale F04 review; real V02 active-release/public/staff API browser
checks and negative/security/retention integration. Independent review and final
human acceptance remain pending. No I02/I03 completion is claimed here.

## Portable command contract

Install frontend lock with npm ci. Use a no-Django Python3.12+ environment with
the accepted backend locks. Obtain the backend writer's immutable release and
trusted receipt digest from its separately reviewed handoff; do not copy hidden
runtime directories or private data from another checkout. Build config keys
are shown in frontend/build-config.example.json. Relative input/output paths
resolve against the repository root. Set MATHSTART_BUILD_CONFIG to that JSON
file and MATHSTART_PYTHON to the configured interpreter, then run npm run build
from frontend. Output must not already exist. The command creates the build-only
view at frontend/.cache/public-view-<release_id>.json and a fresh output manifest.

npm run typecheck and npm test need no DB. npm run test:e2e requires an external
ASGI lifecycle owner (start/health/stop), MATHSTART_E2E_BASE_URL,
MATHSTART_PUBLIC_VIEW, MATHSTART_STAFF_COOKIE_FILE for a guarded disposable opaque
staff session and MATHSTART_LEGACY_BASE_URL for matched live baseline captures.
Playwright uses installed Chrome/Edge and its pinned Firefox runtime. Browser
installation is explicit: npm exec -- playwright install firefox. Set
PLAYWRIGHT_BROWSERS_PATH if not using frontend/.cache/browsers.

All four npm check wrappers honor MATHSTART_CHECK_ID/MATHSTART_CHECK_RESULT and
emit a fresh structured receipt only after actual success, nonempty case IDs and
zero skips. E2E additionally requires all nine browser/width projects. Partial
single-project commands are useful diagnostics and cannot satisfy that receipt.
