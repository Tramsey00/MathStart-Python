# MS-T005 — SVG title, CSS diagrams and four lesson activations

08.11.2026. Issue #61, Draft PR #62, branch ms-t005-grade-7.
Input HEAD: `0b08b5eda21345ca32ec734fb94498f036451109`, clean working tree.
Checked tree before adding this execution receipt: `8d537e70607e24f9cc08bd6b955dc67901586901`.
This receipt is the only subsequent addition to that checked tree; no runtime inputs changed after verification.

## Implementation

1. Renderer commit `391002c`: React requires plain text children for title, including SVG title. Render its authored text fragments as a string while keeping the original title node, ID, attributes, SVG namespace and labelled-by references. No HTML replacement, SVG geometry changes, or class-specific renderer variants.
2. CSS commit `d23f5ff`: only runtime.css changed. Transfer the required circle/legend and probability-scale rules. Preserve the five sector colours and boundaries 0/35/60/80/95/100%, corresponding legend colours, and midpoint at 50%. Use shared surface/text/divider/accent tokens; dark scale gradient adapts to the dark surface. Pie stacks below 720px, scale below 760px. No whole legacy CSS imports, no lesson.css edits.
3. Activation commit accompanying this record: set renderer_version=react-v1 and add stable assignments for exactly four prepared documents:
   - /materials/7-geometry-8 — Параллельные прямые и секущая. Признаки параллельности;
   - /materials/7-geometry-9 — Аксиома параллельных прямых. Свойства углов;
   - /materials/7-statistics-5 — Графическое представление данных в виде круговых диаграмм;
   - /materials/7-statistics-24 — Вероятность и частота события.

All four content.json bytes are unchanged: no converter rerun or content rewrite was needed. The map records resolved blockers and updates current counts to 28 new migrated documents + 1 reused pilot, 0 prepared/inactive, 46 legacy topics not reassessed. Existing route assignments and the pilot alias remain intact. Historical blocker messages for the 46 are explicitly labelled as preceding shared fixes, not current failures.

## Verification

Current instruction explicitly authorizes scoped SVG/diagram/responsive/compatibility checks; global testing policy is unchanged.

| Command / scope | Result |
| --- | --- |
| `node node_modules/vitest/vitest.mjs run tests/grade-7-preservation.test.tsx tests/svg-title.test.tsx tests/linear-lesson.test.tsx tests/material-routes.test.ts tests/lesson-navigation.test.tsx --reporter=json --outputFile=../var/ms-t005-renderer-css/activation-tests.json` from frontend | **43 passed**, 5 files, 0 failed/pending |
| SVG-specific tests included above | Literal fragmented title text and special characters, original SVG namespace/ID/aria-labelledby, full SVG markup of both geometry lessons, SSR/hydration without recoverable errors or replacement |
| Grade-7 preservation included above | All 75 inventory identities/source hashes; actual React SSR of all 28 migrated lessons, academic text/answers/tables/full SVG/links/retained IDs, deliberate excluded sections, explicit URLs/aliases/navigation |
| Existing linear and navigation/route tests | PASS within the 43-test result; existing pilot source and behaviour preserved |
| `node node_modules/typescript/bin/tsc --noEmit` from frontend | **PASS**; wrapper typecheck not repeated because of its previously recorded unrelated staff generation failure |
| Four prepared JSON documents through validate_lesson_document before activation | **4/4 PASS**, no database access |
| load_sources + load_material_routes + apply_material_redirects after activation | **PASS**: 279 source bundles, 32 assignments total, 29 grade-7 canonical routes, 30 direct grade-7 old-slug/alias redirects; no SQL/build/publication |
| Offline Playwright/Edge 157.0.4341.42, actual shared runtime CSS | **128/128 PASS**: four target lessons at 320/360/768/1440 px in light/dark (32 cases), 24 existing migrated lessons at 360/1440 px in light/dark (96 cases). JS disabled, reduced motion |
| Browser assertions | Non-collapsed square pie, original percentage gradient stops and matching legend colours; scale dimensions/gradient/2px by 26px midpoint at 50%; SVG sizes/title/reference integrity; available no-JS answers/native contents anchors; no viewport overflow in either theme |
| Visual self-inspection | Captured 16 target-region PNGs; inspected mobile dark pie, mobile light scale, mobile geometry SVG and desktop dark scale. This is agent self-check, not user acceptance |
| `git diff --check` and scoped diff/metadata checks | **PASS**; protected files unchanged, other grades and all authored source payloads unchanged; .venv/var/local metadata unchanged |

The browser HTML was temporary renderToString(LessonPage) output with actual shared runtime CSS and local fonts, not a release build or publication. Browser checks ran before metadata activation; the four content.json files and renderer/CSS inputs remained identical through activation. Separate source/route tests verified the activated metadata afterward. Temporary exporter command from frontend: `node node_modules/vitest/vitest.mjs run --config ../var/ms-t005-renderer-css/vitest.config.mjs --reporter=dot`; browser command from root: `node var/ms-t005-renderer-css/browser.mjs`. Raw logs, screenshots and scripts are ignored under var/ms-t005-renderer-css; no secrets/PII are included.

### Recorded limitation and corrected test harness

The additional existing `tests/quadratic-source.test.tsx` run found **3 passed / 1 failed**: it expects 8 sections while the current source adapter has 7 (line 43). Combined with SVG and linear tests that exploratory run was 10 passed / 1 failed. Reproduced **the same 3/1 failure on the unmodified renderer from input HEAD** with guaranteed restoration of the fix. The unrelated count assertion and 8th-grade sources were not changed; the full quadratic preservation suite is not reported as PASS.
The first offline browser run was interrupted after a harness error: checking open on the surrounding NAV caused the dark-theme pass to close its nested native DETAILS. Fixed the ignored harness to read details.open, set a 5-second action timeout, then completed all 128 cases. The interrupted run is not counted as PASS.

## Preservation and remaining work

- No changes to lesson.css, convert-lesson.mjs, backend/content/sources.py or math-notation.mjs relative to input 0b08b5e.
- No modifications to materials of grades 5/6/8/9/10, existing content.json, body.html, page.css or page.js. No deletions.
- .venv: 3928 file entries; var/local: 2656 entries; paths/sizes/mtime_ns match the pre-task snapshot. No DB, environment installation, server start/stop, release build or publication commands were run.
- 46 legacy topics were not re-converted or reassessed, as instructed. Their current readiness cannot be inferred from historical converter errors. The future first-topic URL /materials/7-algebra-1 still conflicts with the preserved linear-pilot alias and needs a human route decision.
- Activation here means source metadata/route registration. The installed immutable Content snapshot is unchanged; the four URLs are not claimed as published or tested through HTTP.
- Independent review **PENDING**; user visual/pedagogical acceptance **PENDING**; full MS-T005 **INCOMPLETE**. Draft PR remains draft; no merge and no Issue closure.
