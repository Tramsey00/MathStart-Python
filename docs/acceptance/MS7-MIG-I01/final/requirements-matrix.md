# Issue #40 — final acceptance matrix

Input `8d958aeeb17da46839722441425ccbb5889e2ab7`; implementation `c54a98b91195458b22a14aa4a6cbf14c7fe57e28`. Full I01 acceptance remains pending PR CI/tested merge-ref and independent Task Approvals. [Machine-readable detail](requirements-matrix.json), [Issue snapshot](issue-40.json).

|ID|Requirement|Result|Evidence / assessment|
|---|---|---|---|
|I01-01|React/TS/Vite/React Router framework mode, compatible exact versions + lock|PASS_LOCAL|npm ci, route typegen, tsc, build; appDirectory=src/app, ssr:false, prerender:[]|
|I01-02|Shell/header/footer/navigation; original cascade, fonts/SVG/classes; no redesign/reset/UI library|PASS_LOCAL_SCOPED|Existing site.css then gallery tokens.css/foundation.css; live gallery+shell match and source-derived empty-shell references. Not all public pages.|
|I01-03|Public/account/staff/debug route foundation and layout boundaries|PASS_LOCAL|Explicit /, /karta-sajta/, /o-proekte/, /kontakty/, /account/, /admin/; debug dev-only. Empty route containers, no account/staff implementation.|
|I01-04|No private prerender or wildcard production200; I02 selective public SSG boundary|PASS_LOCAL_WITH_DEPLOYMENT_GATE|Anonymous index only; local preview status checks pass. Real gateway HTTP/method/CSRF/cache proof remains V05; no deployment claim.|
|I01-05|Approved UI examples/gallery/four UX states and accessibility|PASS_LOCAL|Original synthetic pack; live regions, skip, raw data, retry/field-error focus, disabled state semantics; no persisted verdict/progress.|
|I01-06|Four dispatcher modes + historical regressions; malformed controlled unsupported|PASS_LOCAL|5 unchanged historical JS cases plus strict new TS/schema negative cases; no coercion, non-string/missing schema/malformed/extra/private/accessor/cycle failures supported.|
|I01-07|Canonical generated OpenAPI types + runtime boundary validation; frozen pins|PASS_LOCAL|17 historical +24 accepted R02 pins;37-operation type inventory;16 standalone DTO validators; eight identity/grade transport operations only.|
|I01-08|Same-origin cookies/CSRF/error foundation, safe messages, status/content-type/malformed JSON|PASS_LOCAL_MODEL|Fresh CSRF bootstrap for explicit mutation; credentials same-origin, no-store, redirects error; strict JSON/UTF8/envelopes; no raw private error exposure. Mocked transport, no target API verification.|
|I01-09|AbortController/cancellation/stale-response/no unsafe auto retry; R02 P1/P2 boundary|PASS_LOCAL_MODEL|Snapshot request, latest-read guard; sent mutation cancellation stays unknown. Full account/receipt/publication lifecycle I04/backend, NOT implemented.|
|I01-10|No debug fixture/private answer/checker/credentials in production; no production API fixture substitution|PASS_LOCAL_SCOPED|Actual graph47 modules/artifacts12; forbidden module/canary scan; anonymous index only/no maps. Foundation transport currently tree-shaken from empty production pages.|
|I01-11|Matched screenshots360×800/768×1024/1440×1000; browser/version and CSS isolation|PASS_LOCAL_SCOPED|10 new screenshots;3 live fresh Django SQLite gallery pairs byte-identical;22 elements geometry/CSS/leaf text equal. Earlier source-derived empty-shell evidence preserved. Not R01 PostgreSQL/full-site parity.|
|I01-12|Keyboard/focus/pointer; no horizontal overflow|PASS_LOCAL_WITH_HOVER_LIMIT|3 widths: skip/Enter/Tab, retry focus, field error Space/pointer, raw retention,4 modes/unsupported; no overflow; console[]; dedicated hover transition NOT_RUN, manual review required.|
|I01-13|§17 old-to-new index: original→follow-up→target, disposition/status, preserved history|PASS_LOCAL_PENDING_CI_REVIEW|Five records; explicit platform_disposition/current_status added to current final index. Historical checkpoint1/2/frozen records untouched. Implementation SHA bound; CI and independent acceptance pending.|
|I01-14|Migration v1.1/ADR0006/R02/F01–F04/scope/rollback|PASS_LOCAL|No accepted tracked change; no I02–I06/V01–V04 functionality. Rollback future foundation commit; original source remains. F01–F04 unchanged I03/I05.|
|I01-15|Clean install/typecheck/frontend tests/build/security/audit/whitespace|PASS_LOCAL|88 frontend +5 historical JS PASS/0FAIL; audit0; no dependency manifest update. git diff --check + untracked no-index checks.|
|I01-16|Required verify_repo / historical and migration contract suites safely isolated|PASS_SQLITE_ONLY_PG_PENDING|verify_repo8/8 checks; Django99 PASS/8SKIP (107run),R0318,Harness73; R02A30/R03A41/UI7/migrationR0263 PASS. PostgreSQL locking/concurrency NOT_RUN; Docker unavailable.|
|I01-17|Current trace/manifests/commands/exits/inventory/evidence privacy|PASS_LOCAL|Each candidate file size/SHA256, local links; ignored runtime/DB/env/profiles not included. No real secret detected in scoped review; not universal scanner.|
|I01-18|Exact implementation SHA/current PR CI/tested merge-ref + independent Task Approval|PENDING_HUMAN_GATE|Publication authorized; implementation `c54a98b91195458b22a14aa4a6cbf14c7fe57e28`. Accepted input8d958ae remains provenance. Ruslan UX/integration and Vladimir API/security must independently approve exact PR HEAD; no self-approval.|
|I01-19|Final integration/publication/Issue closure/global gate|NOT_REQUESTED_PENDING|Refs #40 target ms7-mig-react-fastapi. Task not historical DONE/ACCEPTED_INTEGRATION until applicable human gates/merge. Frontend CI wiring belongs R03/root-CI owner.|

See [final report](report.md) for scope and outstanding conditions. No acceptance is recorded on behalf of a reviewer.

Publication binding: [current machine-readable matrix](requirements-matrix.json) carries the exact implementation SHA. PR HEAD also includes a docs-only metadata commit; the PR records that final candidate SHA.
