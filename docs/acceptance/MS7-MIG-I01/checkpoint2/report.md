# MS7-MIG-I01 checkpoint2

Status: functional foundation prepared; task INCOMPLETE / independent review pending.
Owner13baybars. No commit/push/PR/full verify_repo/CI authorized at this checkpoint.

## Provenance and isolation

Task branch ms7-mig-i01-foundation, HEAD/start8d958aeeb17da46839722441425ccbb5889e2ab7.
MIG_BASE60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7 is provenance only.
Canonical source appearance8c11edadc8debc81432d1db1145feac504f09061.
No implementation commit: [manifest](content-manifest.json) binds current uncommitted
bytes. Do not attribute Stage2 tests to an implementation commit or previous CI.

Primary checkout remains main at8c11edad, clean/behind1; no branch update.
Accepted tracked task files unchanged. No DB commands/connections, environment
creation/copy, migration/bootstrap/publication or existing baseline modification.
Working DB fingerprint was not re-read; this task performs no DB access.

## Implemented

- Strict canonical schema-backed dispatcher: four slots, unknown/non-string,
  missing/null/undefined schema, malformed metadata/private properties and coercion
  attacks fail controlled unsupported. Identity/difficulty aliases cross-checked.
- Full approved synthetic gallery: four states/cards, unchanged raw input,
  accessible labels/help/error/live regions, non-submit buttons, retry focus,
  unknown-mode example. No evaluation, guessed forms, network or storage.
- Generated canonical OpenAPI types and16 non-coercing runtime DTO validators;
  debug fixture schema validator; native portable Unicode helper.
- Typed eight-operation baseline transport: canonical same-origin URLs/cookies,
  fresh CSRF, request serialization/key snapshot, errors/status/content type/JSON/
  UTF8/schema validation, optional timeout/cancellation, no mutation retries,
  unknown-outcome reporting, RequestScope and latest-read guards.
- Pathless public/account/staff/debug boundaries; no downstream route functionality.
- Production module-graph/debug/private-export/canary guards; no wildcard preview.
- Own §17 [old-to-new evidence](old-to-new-evidence.json), current adapter references
  in frontend README and [trace](../../../agent-traces/MS7-MIG-I01.md).

## Actual verification

[Exact commands, stdout/stderr and exit codes](command-results.json).
Node24.21.0/npm11.19.0; exact frontend lock, no root dependency changes.

| Check | Result |
| --- | --- |
|17 historical pins +24 R02 pins/OAS/DTO/inventory/type generation | PASS, exit0 through typecheck |
|Typecheck / generated route types | PASS, exit0 |
|Native standalone ESM import + Unicode boundary + fixture pack | PASS, exit0 |
|Unit/component/security-negative suite |88 PASS /10 files, exit0 |
|Unmodified historical JS dispatcher suite |5 PASS, exit0 |
|Production build + graph/payload/export guards |PASS, exit0;47 client modules /12 output files |
|Dependency tree |PASS, exit0 |
|npm audit |0 vulnerabilities, exit0 |

Unit evidence uses actual frontend functions with jsdom or mocked fetch.
It does not verify a target FastAPI runtime, live HTTP/session/bridge, browser,
PostgreSQL concurrency, deployment, SSG catalogue or recovery.

Initial generation failed on Ajv nested OAS dynamic-anchor handling; fixed by
explicit equivalent in-memory #meta binding. A subsequent replacement-string
escaping error was corrected. UI schema registry alias then required resolution
to the canonical DTO bundle. None changed accepted sources.
First gallery import failed Vitest fs.allow (outside frontend root); corrected
test configuration to permit existing repository CSS, without replacing CSS.
First production hook had a syntax error; later its declaration exposed generic
Vite ObjectHook instead of the actual function. Both corrected; raw failed runs:
[initial](initial-verification-failure.json), [hook typing](hook-type-verification-failure.json).
A new deliberately invalid runtime test required an explicit second type bypass:
[negative-case typing](additional-negative-type-failure.json).
Direct Node import additionally found an extensionless CommonJS helper reference
that Vitest masked. Replaced it with generated ESM Unicode code-point counting,
then added the native import/Unicode check. One ad-hoc recheck used the wrong CWD;
the permanent URL-relative script fixes that reproducibility error.
Resumed API inspection found cancellation after headers/during response-body read
was mapped to INVALID_RESPONSE. Two new regression cases reproduced this for GET
and sent login: [pre-fix failing tests](body-cancellation-regression-failure.json).
The adapter now reports CANCELLED; sent mutation outcome stays unknown, with no
retry. [Earlier86-test run](pre-body-cancellation-results.json) is retained.
All nine final scoped checks were rerun after the correction;88 tests pass.
This transport module is not imported by the gallery/shell, so their screenshots
remain applicable; the actual production graph was regenerated.
React Router future-v8 notices remain advisory; no future flag enabled.

## Production security evidence

[Actual build graph](production-client-modules.json), [artifact digests](build-manifest.json).
No debug route/layout, fixture pack/schema, fixture exchange or reference module
occurs in the production graph. Artifact scan rejects debug strings and synthetic
credential canaries; only anonymous index.html is emitted, no private HTML/maps.
No authored lesson JS, mathematical checker, real answer, credential, DB payload
or private session/user data is imported. Canonical type declarations are erased.
The API adapter is currently unreferenced by empty route containers, so it is
tested as a foundation module, not claimed to execute in the current production UI.
Negative tests prove forbidden-module rejection. This is a scoped source/graph/
artifact review, not a claim of a universal secret scanner.

## Responsive / keyboard evidence

[Current responsive evidence/index](responsive-evidence.md) and [raw browser observations](browser-evidence.json).
15 new screenshots; Chromium155.0.8059.27 from current UA Client Hints.
React/source-derived shell pairs at360×800,768×1024,1440×1000 are byte-identical.
Exact geometry, computed CSS and leaf text match; only aggregate template indentation
whitespace differs. Gallery has no horizontal overflow at all widths.
Real Tab order, skip Enter, focus-visible, state/status/alert, raw input retention,
retry focus before hiding, field-error Space/pointer activation and four/unsupported
slots passed. Console errors/warnings: none recorded. No in-scope visual defect found.
This remains source-derived shell evidence, not live Django/full-page parity.
Dedicated hover transition not verified; documented API exposes no hover action.

Initial IAB attempts reported ERR_BLOCKED_BY_CLIENT; resumed host inspection found
no old dev process. A hidden task-only dev process restored localhost5171, then
browser checks passed without security changes or alternate origins. Historical
limitation retained as RESOLVED. First comparison wait assumed the empty source
reference had a main element; corrected observation to its footer (no app change).
Initial raw metric equality also included aggregate indentation textContent;
comparator now checks exact geometry/CSS/leaf text and ignores only container
indentation whitespace. Final comparison and screenshot hashes pass.

## Evidence validation

[Complete candidate file list](changed-files.txt), [delta from checkpoint1](stage2-delta.json),
[isolation/source checks](isolation.json), [index/checksum validation](evidence-validation.json).
Recorder command: node frontend/scripts/record-evidence.mjs, final exit0.
Its first run found a Windows CRLF path-splitting error in the recorder itself
(exit1), corrected to Git NUL-separated paths. No unknown task file actually existed.
All included hashes, local links, mapping paths and preserved checkpoint1 evidence
are checked on the final run. These checks do not rerun application tests or
change their earlier execution timestamps. The final scoped suite was rerun after the response-body cancellation fix.
Current screenshots cover unchanged shell/gallery, not live API cancellation.
Full repository verification remains pending.

## Issue40 / next gate

Functional scope is implemented; no architectural conflict requiring contract
changes was identified. F01–F04 and criteria remain untouched and assigned13baybars:
fix no later than I03, verify in I05; no new F04 pixel/font threshold.

Remaining before I01 acceptance:
1. Independent visual review of the new screenshots; dedicated hover check on
   a browser surface that exposes pointer hover. No live Django/full-page parity claim.
2. Reproducible clean lock install and full verify_repo in a separately authorized
   verification environment, never working DB/R01 baseline.
3. Independent Ruslan UX/integration and Vladimir API/security review.
4. On separate authorization, create implementation commit, bind evidence to
   exact candidate SHA, push/task PR→integration (Refs#40), current CI/tested
   merge-ref and independent Task Approvals. No self-approval or Issue closure.

Production reverse-proxy404 parity belongs to deployment/gateway evidence;
local preview tests are not a substitute. I02–I06/V01–V04 remain out of scope.
