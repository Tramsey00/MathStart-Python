# MS7-MIG-I01 — checkpoint1, 2026-10-09

Status: first implementation checkpoint; I01 INCOMPLETE, human review pending.
Owner13baybars. No commit/push/PR, target deployment or task acceptance.

## Reproduction and authority
Branch ms7-mig-i01-foundation, HEAD/accepted integration input
8d958aeeb17da46839722441425ccbb5889e2ab7 plus uncommitted files in content-manifest.json.
MIG_BASE60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7.
Canonical source appearance8c11edadc8debc81432d1db1145feac504f09061.
R01/R02 dependencies accepted by humans; PR48 merge matches starting input.
No accepted R02 semantics, historical approvals, app sources or pins modified.

## Created structure
frontend/package.json + package-lock.json; strict TypeScript and Vite/Router
configs; src/app/root.tsx and routes; shared/ui shell/components; public,
account, admin route extension points; development-only component preview;
tests for shell DOM, fields/escaping, routes and local artifact HTTP behavior;
scripts for build exclusion, local artifact preview and source-shell reference.
Own exec plan and trace, this report, screenshot/browser/command evidence.

React Router7.18.4 framework mode with appDirectory=src/app, generated types,
ssr:false, prerender:[]; build-time shell has no private/session/API state.
I02 supplies complete validated public manifest, content/SEO and public SSG.
I03 handles lessons/widgets; I04 handles account/staff functionality.
No production wildcard fallback or private HTML export is configured.
The preview script is localhost verification tooling, not the V05 gateway.

## Exact direct dependencies
Node24.21.0 / npm11.19.0 observed.
React/react-dom19.2.8, React Router/dev/node7.18.4, TypeScript5.9.3,
Vite7.3.7, Vitest4.1.11, isbot5.1.44; all direct versions exact in package.json.
Other exact pins: types/node24.12.0, types/react19.2.14, types/react-dom19.2.3,
Testing Library React16.3.0/DOM10.4.1, jsdom27.4.0,
Playwright1.58.2, openapi-typescript7.13.0. Lockfile v3.
Playwright/OpenAPI tooling presence is not evidence that their future suites ran.

## Executed verification
[Command results](command-results.json) preserves timestamps, output, exit codes.
- npm install --package-lock-only --ignore-scripts:0.
- npm ci / later npm ci --include=dev after explicit isbot pin:0.
- npm run typecheck:0; route type generation + tsc.
- npm test:0; 9 PASS across4 files.
- npm run build:0; debug exclusion/private HTML export guard PASS, no server artifact retained.
- npm ls --depth=0:0; resolved direct dependencies/peers valid.
- npm audit --json:0; reported vulnerabilities0.
- npm run dev:running on http://127.0.0.1:5171/.
- Browser interactive checks below: actual session, not synthetic model evidence.
Full verify_repo/DB fresh smoke/CI not run at this checkpoint. No DB is configured
for this frontend; no request is proxied to working or R01 API.

## First visual comparison
[Measurements](shell-browser-measurements.json), [screenshots](screenshot-index.md).
CSS viewport360x800,768x1024,1440x1000; DPR/raster assumptions limited to recorded
JPEG dimensions. Same-session React and controlled base.html reference compared.
Header/footer boxes, gaps, padding, fonts, colors and SVG geometry match at all
three sizes; no horizontal overflow. Screenshot byte hashes are in manifest.
Header/footer classes, links, labels and SVG also tested against source DOM.
Existing site.css is imported directly; gallery imports tokens.css then
foundation.css. No CSS copy/reset/UI library/global style change.

Current IAB session reports Google Chrome/Chromium155.0.8059.27 via User-Agent
Client Hints fullVersionList on the local diagnostic reference. Reduced UA says
Chrome155.0.0.0. Separate Codex browser/app version is not inferred.
Historical R01 screenshots retain their original WebView2/version qualifiers.

IMPORTANT: existing R01 localhost8002 was not listening. It was not started,
modified or synchronized. The reference is a controlled transformation of the
accepted Django source base.html with an empty content outlet, NOT a running
Django instance. Archived R01 screenshots were inspected as historical visual
evidence; complete-page runtime/browser parity is NOT claimed.
Public route containers intentionally have no I02 content, so the footer's
absolute page position differs from full home/catalogue/lesson screenshots.

## Keyboard and CSS isolation
[Keyboard evidence](keyboard-browser-evidence.json).
Seven shell links reachable in visible order with visible3px focus outline.
Gallery skip link is first, appears once after hydration, Enter focuses
foundation-main. No overflow at360. Actual stylesheet order: site -> tokens ->
foundation. Final captured console error/warn entries: see evidence JSON.
Full gallery fixtures/dispatcher/state transitions and root-CSS navigation
regression remain next checkpoint, not asserted PASS here.

## Failures discovered and corrected
1. Initial typegen exit1: default Router build-time entry auto-added floating
isbot and its nested production-mode install removed dev packages. Explicit
isbot5.1.44 + lock regeneration + ci --include=dev repaired it; final lock stable.
2. Initial tests exit1: Vite transformed source-reference new URL; explicit
NodeURL fixes the Node filesystem reference. No tests weakened.
3. One npm test command invoked from task root, exit1 ENOENT; corrected to
frontend. It wrote npm's ordinary diagnostic cache log outside project source;
no primary checkout or DB changes.
4. Browser found duplicate skip link after hydration. Moved route-dependent
shell from document Layout into App/fallback/error components; real browser
retest confirms single skip link. Root Layout is stable across hydration.
Non-blocking Router7 warnings advertise future8 flags; none enabled blindly.
npm warns esbuild install script is not allow-listed; native package works and
the actual typecheck/build pass. No global script policy changed.

## Remaining scope
Approved full gallery + fixture-only strict dispatcher; generated API types,
runtime-validated fetch/CSRF/error adapter, stale-response/security negatives;
broader component/lifecycle/browser/E2E coverage; old-to-new evidence index;
full isolated verification/CI and independent approvals.
No I02–I06/backend implementation. F01–F04 unchanged: fix no later thanI03,
verify inI05; F04 ordinary-scale readability criteria preserved.
