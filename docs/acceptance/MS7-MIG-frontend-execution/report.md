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

## Committed-source verification checkpoint

Source `5308ae1e355edbf0296c6c6aa09db0d9dd21e832` was verified with
139/139 Vitest cases (71.14 seconds, `var/frontend-tests-05.json`) and full
build05: 703 assertions, 279 pages, 280 HTML URLs, robots/sitemap and 422 files.
Input release `ms7exec-i02-public-20261016` has manifest digest
`3d9a389bba5adcb6c097526fa440ad72b1efdd167536a661155b08e4e6dd435f`
and trusted receipt digest
`db059ce5e13fe0bd12904254348122ee15c6f7acd199c0e04f05969ec7db6eab`.
Output `var/frontend-public-05/output-manifest.json` digest is
`b44ab4d4cafec31410e09cdb4a99ffe3a4008f17bc13c56c6fe34f118014581e`.
These are build/unit results, with browser and independent review pending.

The first real-server smoke, `var/real-smoke-05.json`, failed all 12 cases
because port8121 refused connections. It is preserved as environment failure.
After the backend owner restarted the API, the full nine-project matrix began
with 1044 tests; `var/real-matrix-06.log` records that attempt. A start is not a
passing result, and no successful E2E receipt exists until the wrapper finishes.
Matrix06 was stopped after three page-load timeouts. Backend investigation found
that synchronous complete release validation during each auxiliary resource
request blocked serving. This is a failed attempt, not partial browser acceptance;
the backend owner is preparing and independently reviewing the serving fix before
another full run. No E2E success receipt was emitted.

The actual build view independently enumerates 280 routes and 263 topic pages,
97 distinct local CSS files and seven distinct local JS files. Including shared
dependencies, it references 108 distinct stylesheet URLs and 11 script URLs.
The browser suite derives representatives from those full inventories rather
than hard-coding a smaller list.

## Private hydration correction and live diagnostic

After the independently reviewed backend serving correction (`ef7a2b2`),
Chrome360 smoke07 passed 11 cases and failed its combined nine-resource staff
case after exhausting the cumulative 60-second budget. A focused real browser
diagnostic confirmed that detail GETs worked, while also revealing React418 on
every private full navigation: the framework SPA fallback contained the home
loader's public view, so the root HTML differed from the private client layout.

Source `48fadcc` prevents public loading only for the framework's explicit
`X-React-Router-SPA-Mode: yes` fallback build request. Ordinary public prerender
retains the verified loader. The complete initial route manifest avoids a
separate runtime route discovery service. Build now refuses a missing private
shell or one containing public view/canonical/lesson-host markers.
Two focused regressions passed; full Vitest141/141 passed in48.22s and fresh
typecheck passed all four stages. Build08 passed703 assertions with279 pages
and422 files; output manifest digest:
`a7a24e34f3364ecaa9a9c42e72b6a6af1b6967f4a45e7eac88858b5d58344d81`.
It uses the same pinned release/index/receipt as build05.

Each of the nine staff resources now has its own browser case with the unchanged
60-second limit, mandatory positive fixture rows, successful list/detail/history
GETs, private/no-store and zero page errors. No positive read is conditionally
omitted (`05dd362`). Only the complete public inventory case gets a volume-based
budget of30000ms plus5000ms per manifest URL; individual inventory requests
remain bounded at5000ms and the case attaches measured elapsed time. All body,
SEO, alias and private-exclusion assertions remain.

The independent reviewer reports PRIVATE-01 closed on48fadcc: its own newly
built artifact, actual Chrome155/360 and real backend passed anonymous/private
shell plus all nine positive list/detail/history flows with no page errors.
It also manually inspected all18 matched Chrome360 smoke07 captures and found
F01–F04 readable without clipping/overlap at ordinary scale. This is360-only
evidence on the recorded build05 visual source, not a complete matrix claim.
Author staff recheck09 on build08 passed10/10 Chrome360 cases (2.1 minutes):
anonymous denial plus all nine positive list/detail/history flows, at least
three real200/no-store API responses per resource and zero page errors. Raw
results are `var/staff-smoke-09.json` and `var/staff-smoke-09.log`, with sanitized
network attachments in `var/playwright-staff-09/`. This verifies the committed
05dd362 test source against the48fadcc build08 serving bytes and backendef7a2b2.
The authoritative clean combined matrix (1116 cases across nine projects) remains
pending. The coordinator owns that run to avoid duplicating the lengthy full
matrix. No full E2E receipt or I02/I03 completion is claimed by these diagnostics.

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

Matched legacy captures use a separate original Django environment installed
from the accepted historical requirements.lock. The portable comparator is
`python -m frontend.legacy_comparator --build-config CONFIG --legacy-python PYTHON
--runtime-root var/OWNED-DIRECTORY --port 8132`, run from the repository root
using a configured backend interpreter. It requires MATHSTART_DISPOSABLE=1 and
an explicitly configured reserved synthetic PostgreSQL database with the V01
disposable marker. It verifies the immutable release before copying only its
hash-checked media into its own runtime. Both a SQL preflight and the actual
Django connection must report transaction_read_only=on. The process uses
PGOPTIONS default_transaction_read_only=on and performs no migrations/bootstrap.
The caller owns health checks, process termination and its own runtime cleanup;
this comparator is excluded from normal target runtime requirements.

All four npm check wrappers honor MATHSTART_CHECK_ID/MATHSTART_CHECK_RESULT and
emit a fresh structured receipt only after actual success, nonempty case IDs and
zero skips. E2E additionally requires all nine browser/width projects. Partial
single-project commands are useful diagnostics and cannot satisfy that receipt.
