# MS7-MIG-I01 frontend foundation

Final verification checkpoint: functional foundation locally verified; task INCOMPLETE pending PR CI and independent review. PostgreSQL-specific checks and dedicated hover remain unverified.

Accepted integration input: 8d958aeeb17da46839722441425ccbb5889e2ab7.
MIG_BASE_SHA: 60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7 (provenance only).
Canonical Django source appearance: 8c11edadc8debc81432d1db1145feac504f09061.
Original implementation commit: c54a98b91195458b22a14aa4a6cbf14c7fe57e28. The final content manifest binds that original capture; checkpoint1/2/final remain immutable historical snapshots.
Current uncommitted B1/B2 corrections and fresh verification are recorded in the separate
[PR50 follow-up report](../docs/acceptance/MS7-MIG-I01/review-b1-b2-20261010/report.md).

## Toolchain / commands

Use Node24.21.0/npm11.19.0 on this host. Exact direct versions and lockfile;
TypeScript5.9.3, React19.2.8, React Router7.18.4, Vite7.3.7, Vitest4.1.11,
openapi-typescript7.13.0, Ajv8.20.0/ajv-formats3.0.1.
Ajv is generation tooling; emitted validators have no runtime schema compilation
or dependency on Ajv. Their Unicode length helper is ordinary generated ESM.

Run in frontend, using a process-local PATH (C:/Program Files/nodejs first)
and task-local npm cache. Never print or copy environment credentials.

~~~text
npm ci
npm run generate:api
npm run check:contracts
npm run typecheck
npm test
npm run build
npm run verify:foundation
npm run dev
npm run preview
~~~

verify:foundation records versions, typecheck, native validator import,
unit/component/security tests, unchanged historical dispatcher tests,
production build/guards, dependency tree and audit. It does not run Django,
connect to a DB, run full verify_repo or replace CI. Each run creates a NEW ignored
`.cache/verification-runs/run-<timestamp>-<unique>/command-results.json`.
For a new explicit output use `npm run verify:foundation -- --output .cache/NEW.json`
(relative to frontend). Existing files, Git metadata, external paths and historical
checkpoint1/checkpoint2/final captures are rejected; nothing is overwritten.
Reports contain actual Git HEAD/branch, before/after dirty status and source
fingerprints, versions, exact commands, start/end times and exit codes. Dirty or
uncommitted runs have `tested_implementation_sha: null`: HEAD is provenance only.
Source/history changes during a run fail verification. Capture new review evidence
separately; legacy record-evidence.mjs/record-final-evidence.mjs are historical
checkpoint recorders and must not be run to refresh published captures.

Dev/preview: http://127.0.0.1:5171/ with no API proxy or DB configuration.
Do not point mutations at working DB or the existing R01 runtime.

## Rendering and routes

React Router framework mode; appDirectory=src/app, generated route types,
ssr:false, explicit prerender:[]. Build emits only a generic anonymous index.
Root document stays identical during hydration. Pathless public/account/staff/debug
layouts expose extension boundaries without adding visual wrappers.
Account/staff have no loaders, private data, auth forms or prerender artifacts.
Route layout handles are organizational metadata, never authorization.

Only development registers /__ui__/foundation/. Fixture imports, gallery,
debug layout and reference middleware are absent from the production graph.
No fixture substitutes a real API. Original site.css is linked first;
gallery then links original tokens.css and foundation.css. No reset/UI library,
copied theme, new fonts, or authored lesson CSS/JS changes.

Local preview uses explicit foundation URLs and returns404 for unknown/debug/API/
missing assets. Its status tests establish local artifact behavior only.
V05 must verify production gateway status/method/CSRF/cache/redirect parity.
Never deploy with wildcard index rewrites or Vite SPA fallback.

I02 owns content/catalogue/SEO, the complete validated R02 published URL manifest
and selective public prerender. Never set prerender:true or include private URLs.
I03 owns LessonHost/widgets. I04 owns account/staff and receipt reconciliation.
F01–F04 remain assigned13baybars: fixes no later than I03, mandatory I05 verification.
F04 criteria remain readability at360×800 at ordinary scale without clipping/
overlap, preserving angles/coordinates/text readout/controls/math; regression768/1440.
No new font/pixel threshold is introduced.

## Approved UI and dispatcher

Debug gallery consumes the original synthetic UI pack, validated against its
schema plus unique state/mode/ID coverage and dispatcher checks.
Ports all four states, static cards, raw input preservation, error/help IDs,
live regions, non-submit buttons, retry focus and controlled unsupported.
No network, persistence, forms, mathematical verdict or progress update.

Dispatcher takes unknown, rejects coercion, non-string modes, missing schema,
extra/private properties, malformed metadata, getters, cycles and proxy failures.
Canonical schema validation plus immutable identity/difficulty cross-checks
select four metadata slots only. enum/object metadata never invents a renderer.
Historical JS regression source stays unchanged and runs independently.

## API boundary and I04 handoff

generate:api checks17 historical Git-blob pins and24 accepted R02 pins, normalized
Windows text equality, official OAS structure, DTO schemas and37-operation inventory.
It generates type-only canonical OpenAPI declarations, non-coercing standalone
validators and a runtime map of only eight baseline identity/grade operations.
Frozen sources and historical pending labels are preserved. Types are not evidence
that all37 operations or any target backend are implemented.

The official OAS #meta anchor is statically bound in the generator's in-memory
copy because there is no outer dialect extension; canonical files are untouched.
The historical UI DTO URN resolves to the same canonical DTO definitions.
Generation follows [openapi-typescript](https://openapi-ts.dev/node) and
[Ajv standalone](https://ajv.js.org/standalone.html).

createApiClient.call uses canonical relative URLs, same-origin cookies, no-store,
redirect:error, JSON-only request bodies and fresh CSRF bootstrap/header on each
explicit mutation. Request bytes/key are snapshotted before awaits.
No automatic retry/replay, password normalization, storage, logging, cookie access,
session inference or client-owned receipt registry exists.

Response boundary checks declared status, JSON content type/UTF8, JSON syntax/
duplicate keys, canonical envelope/schema, http-v1, empty R02 identity field_errors,
status/retryable agreement and integer Retry-After. Query bounds follow R02.
UI errors use fixed local messages; raw server messages/bodies/field details are
discarded. requestId/retryAfter are the only safe error metadata exposed.

AbortController propagates caller abort and optional timeout. If a mutation was
sent, cancellation/network/malformed response or409/503 means outcome unknown.
Logout additionally requires HTTP200 and strictly `data.completed === true`;
`completed:false` is INVALID_RESPONSE with unknown outcome, without POST replay or
session acknowledgement. Full lost-response reconciliation remains I04.
Successful validated response is the only transport success. CSRF bootstrap
failure is not-sent. The adapter never follows a redirect or repeats a mutation.

RequestScope + createLatestReader supersede reads and reject late responses.
The latest-reader cannot take mutations. I04 must invalidate scopes/private caches
on logout (including unknown logout), account switch, session expiry, disposal
and cutover. I04 owns quiet initial GET me401, pending credential cleanup,
explicit immutable registration/onboarding retry, GET me/restore reconciliation,
one cutover re-login, server-authorized bridge proofs/epochs/revocation and
owner/session binding. No bridge can be restored by a client helper.
These primitives do not implement or verify the complete P2 lifecycle.
P1 staff publication and private publication_state remain downstream.

## Evidence / limits

[Final report](../docs/acceptance/MS7-MIG-I01/final/report.md),
[Issue40 acceptance matrix](../docs/acceptance/MS7-MIG-I01/final/requirements-matrix.md),
[current §17 mapping](../docs/acceptance/MS7-MIG-I01/final/old-to-new-evidence.json),
[final file hashes](../docs/acceptance/MS7-MIG-I01/final/content-manifest.json).

Clean npm ci, generation/pins, typecheck, native validators,88 frontend tests,
5 unchanged historical JS tests, production build/guards and audit all exit0.
Full verify_repo exit0:8/8 checks in new task-local SQLite environment only;
Django99 PASS/8 SKIP, R0318/Harness73 PASS. Separate contract/model suites pass.
No existing DB or R01 runtime was used; PostgreSQL locking/concurrency NOT_RUN
because Docker Linux daemon is unavailable. Python local3.14.7, baseline CI3.12.

[Final browser index](../docs/acceptance/MS7-MIG-I01/final/screenshot-index.md)
contains10 new screenshots. Three live fresh Django SQLite gallery/React pairs
byte-identical at360×800/768×1024/1440×1000; geometry/CSS/leaf text, keyboard/focus,
pointer activation, no overflow and root CSS isolation pass.
This is gallery+shell parity, not R01 PostgreSQL, whole-site/public-page or target
runtime parity. Dedicated hover transition remains unverified; manual reviewer check.

[Checkpoint1](../docs/acceptance/MS7-MIG-I01/checkpoint1/report.md) and
[checkpoint2](../docs/acceptance/MS7-MIG-I01/checkpoint2/report.md) remain unchanged
historical records. Their source-derived empty-shell screenshots are not relabelled
as live Django evidence. Do not refresh their recorder/indexes for final results.

No target API/session/bridge/concurrency/recovery or production gateway404 claim.
Current root CI is baseline-only; frontend CI wiring belongs to R03/root-CI owner.
Implementation SHA is bound below; PR CI/tested merge-ref and independent Task Approvals pending.

Publication: owner accepted the final verification checkpoint and authorized commit/push/PR. Independent task acceptance is pending. Final recorder is for the pre-commit checkpoint only; do not refresh historical captures after publication. Exact implementation binding is recorded separately in current §17 references and the PR.

Implementation commit: `c54a98b91195458b22a14aa4a6cbf14c7fe57e28` (exact accepted input parent). Current §17/matrix bind this code SHA. PR candidate additionally contains a docs-only binding commit. Captured verification/screenshot metadata retain their original pre-commit provenance; PR exact HEAD/CI and independent approval are separate facts.
