# MS7-MIG-V02 — Implementation Report

Current status: **READY FOR INDEPENDENT RE-AUDIT; positive independent audit and human approval PENDING**.

The initial snapshot received **CHANGES REQUIRED** for F01/F02. Its report,
47-file snapshot and original results are retained without alteration in
`remediation-f01-f02/history/initial/` and `remediation-f01-f02/original-audit/`.
The current owner remediation and actual reruns are authoritative in
[F01/F02 Remediation Report](remediation-f01-f02/report.md): V0286 (original41
+new45), V0134, R0263/R02A30/R03A41, PostgreSQL smoke and verify_repo8/8 PASS.
The remainder below describes the initial implementation and original run;
the archived original is byte-identical to the audited snapshot.
This is uncommitted task work, **PENDING_PUBLICATION**, not ACCEPTED/merged/deployed.
Owner Vladimir; Reviewer/Task Approver Ruslan; consumer handoff Ilya.
Issue: https://github.com/Tramsey00/MathStart-Python/issues/35. Gate MIG-G1 pending.

## 1. Input

V02_BASE_SHA, initial/current HEAD and merge-base with origin/ms7-mig-react-fastapi:
`0c03197e23f69a233c0fcf8bdffa336feca20b92`; branch `ms7-mig-v02-content`;
initial tree clean. MIG_BASE_SHA `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`
is historical provenance. R02 PR48 (`8d958ae`), V01 PR51 (`4a1b8b0`) and I01
PR50 (`0c03197`) are in this fixed input. No fetch/base update/reset/checkouts.
Canonical Issue registration is in R01 records; current user explicitly names35.
No independent new GitHub acceptance/CI receipt is invented.

## 2. Normative sources

Supplied v7.1 SECTION20 PARALLEL DEADLINES PDF:114 pages, all readable;
actual bytes SHA256 `e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd` matches expected.
Supplied migration v1.1 PDF:60 readable pages;
SHA256 `a0c72fda223f86622d01665eaa7ec9d854c7b0b3014de38174f9ad4c582eb66e`.
Use v7.1 §§5–11,15–17,20–27 and migration §§3–11, V02 card,17,20.
Earlier G0 document does not replace the supplied114-page source.
Repository authority: AGENTS/PRODUCT/ARCHITECTURE, ADR0001/0006, R01 inventory/admin
and acceptance indices, R02 r02-v1 content/auth/platform/staff/OAS/build/list policy,
R02A frozen OAS/DTO/policy and original tests, V01 code/schema/repository/UoW/tests,
Django Content/catalogue/Grade/admin/SEO/redirect/source code, I01 README (read-only).
Historical pending/proposed labels remain unchanged; accepted dependency intake
comes from the user's assignment and fixed integrated commits, not retroactive edits.

## 3. Implemented endpoints / mapping

See [routes.json](routes.json) for32 scoped GET operations and public adapters.

| Route / surface | Contract / legacy mapping |
| --- | --- |
| GET /api/v1/grades/ | Frozen R02A GradeListResponse; content.api_views / grade_catalogue |
| GET /api/v1/content/pages/{slug}/ | R02 separate delivery OAS and ContentDeliveryResponse |
| GET /api/v1/staff/{resource}/ | Nine resources: grades,subjects,sections,pages,publications,media_assets,redirects,users,groups; exact R02 DTO/list policy |
| GET /api/v1/staff/{resource}/{id}/ | Same nine registered models; authorized closed detail |
| GET /api/v1/staff/{resource}/{id}/history/ | Same nine models; action_time/id keyset; preserved log IDs/actor/time/action |
| GET /api/v1/staff/users/{id}/group_choices/ | Narrow active staff + change_user gate, existing user form |
| GET /api/v1/staff/permission_choices/ | Applicable User/Group form permissions only; no Permission CRUD |
| GET /api/v1/staff/pages/{id}/publication_state/ | Protected coherent sampling boundary; missing V04 edition provider503 |
| /,/<slug>/, home alias,karta-sajta | Active release page selection; I02/V05 renderer port, no SPA wildcard200 |
| sitemap.xml,robots.txt,redirect fallback | Same pinned active release, trusted origin; exact fallback301/302 |
| /static/*,/media/* | Verified public asset union only, GET/HEAD/ETag304, missing404 |
| /_content/index.json; immutable release index/page paths | Accepted R02 build handoff; active descriptor or retained committed APPLIED journal authority |

No assessed Topic/Exercise/Attempt/Progress/identity mutation or staff write is fabricated.
New staff/delivery slashless endpoints are unsupported; only existing Grades has301.

## 4. Content / catalogue / manifest

V01 read projections produce closed ContentDelivery/PublicCatalogue/PublicBuildIndex
candidates without writes/activation. Preserve real IDs, source paths, SEO fallbacks,
canonical home/, ordered topic joins/NULL behavior and all published page enumeration.
The full disposable Django source profile comparison proves279-page SEO/source identity
and263-topic ordering against actual Django properties/catalogue_context; READ ONLY SQL.
Source digest in that comparison hashes actual source file bytes. It does not pretend
an empty fixture asset list proves all CSS/JS/lifecycle families.

Public serving uses one validated immutable release, never latest DB page fields.
Closed schema checks exclude drafts/private fields; index/page/relations/aliases are
consistent; exact index digest, body render digest and ordered asset hashes are checked.
Storage containment rejects traversal/symlink escape; asset MIME/kind allowlist covers
current CSS/JS/PNG/PDF plus reviewed image formats. Missing/corrupt release503.
V04 must bind original sources and all page metadata to its reviewed staged hash
inventory; V02 does not manufacture that trust or a publication journal.

## 5. Grades

Real PK is distinct from number parsed only from canonical1..12-klass. Unsupported
rows fail503 instead of being skipped. Ascending created_at/id, limit page_size+1,
default20/max100, no offset/locks/commit. Signed cursor payload exact scope/size/time/id;
strict types, aware UTC, int64 bounds. Old/new exact signing bytes, zlib compression,
keyring and no-expiration behavior independently compared with actual Django signing.
Old cursors are not given invented max_age/user scope. Bodies remain ignored on GET.
Tests cover removal of delivered rows, mutable titles/order and new later rows.

## 6. Routing / SEO / media

Working page beats fallback; exact Unicode old_path, safe301/302 Location serialization,
self-loop/unsafe target rejection. Unknown/unpublished404 in a valid active release.
Resolved unsafe requests require CSRF proof before page lookup/404; unresolved legacy
paths preserve all-method fallback. Arbitrary verbs tested; HEAD empty. Sitemap is
published-only, ID-ordered, canonical URLs/frequency/priority; robots uses trusted origin.
Production HTML/React/SSG, full asset family and gateway/browser parity remain I02/I03/V05.

## 7. HTTP transport

Frozen envelopes and versions: grades http-v1; separate delivery/staff migration-r02-v1.
JSON UTF8, private,no-store, per-request UUID shared by response/error. Explicit method
and routing boundary prevents accidental307/422. Raw parser tests UTF8/MIME/schema,
nested duplicates/nonfinite/oversize; it is not attached to read endpoints that ignore
bodies. Internal exception text never enters responses. Generated OpenAPI disabled.

## 8. Staff authentication / authorization

Default identity port denies. V03 alone provides a verified server identity; no header,
role/user-ID/body trust. V02 rereads active/staff/superuser and effective DB direct/group
permissions before object lookup. View OR change gates; narrow selectors do not grant
Group administration. Scope revision hashes effective codes/flags; redundant assignment
does not change it, actual permission revocation invalidates cursors. Nine list sorts,
every permitted direction, mixed sorts, quoted search, nullable relations, page-size1
pagination are compared to native Django Admin over nonempty synthetic PG data.
History exposes closed safe action summaries, not raw arbitrary historical messages.
No read grants content mutations, User/Group writes, publishing or deletion.

## 9. V01 integration

Existing models/metadata/repository/UoW only. PG reads set TRANSACTION READ ONLY;
autoflush disabled, normal exit rollback, no read row locks. No DDL at HTTP startup.
V01 Alembic/schema/locks/snapshot and backend locks untouched. Target runtime installs
from its own lock without Django; imports/factory registry verified with Django absent.

## 10. Tests

| Command / environment | Actual result |
| --- | --- |
| python -m unittest backend.tests.v02.test_unit backend.tests.v02.test_http backend.tests.v02.test_postgres -v | PASS41,0skips:9 unit/contract,15 SQLite HTTP,17 PostgreSQL HTTP/parity |
| python -m backend.tests.v02.public_baseline_projection | PASS279pages/263topics; actual source hashes/SEO/order and read-only SQL; no activation |
| python -m unittest backend.tests.test_unit backend.tests.test_postgres backend.tests.test_remediation -v (isolated Linux container) | PASS34,0skips including23 PostgreSQL methods |
| python -m unittest discover -s tests -p test_migration_r02_*.py -v | PASS63 |
| python -m backend.tests.v02.baseline -> scripts/fresh_install_smoke.py --disposable | PASS on new PG16 database; bootstrap twice/source preservation |
| same driver -> python scripts/verify_repo.py | PASS8/8; Django109, R0318, Harness73, no reported skips |
| same driver -> R02A / R03A frozen suites | PASS30 / PASS41 |
| pip check, both isolated test/runtime environments | PASS |
| compileall scoped code; git diff --check | PASS |
| Ruff/mypy/formatter | NOT CONFIGURED by this repository; no invented PASS |

Each named test/category and exact command/log provenance is in [verification.json](verification.json)
and [test-matrix.json](test-matrix.json). Historical and final checks are distinct.
Initial fixture/adapter failures were retained; no failing assertion is reportedPASS.

## 11. PostgreSQL verification

Actual PostgreSQL16.15, Docker29.8.0, Compose5.5.1; Windows Python3.12.10,
isolated V01 Linux Python3.12.15; actual installed packages in verification record.
Dedicated new container ms7-mig-v02-pg-alt-20261012, localhost15441; no existing DB.
Windows excludes55351–55450, explaining failed55441 bind. PG internally55441; separate
read-only-checkout Python container shares that network for original V01 guards.
V02 UUID DBs retain V01 rehearsal prefix/marker required by existing fresh(); no guard
was weakened. Successful test DBs removed by their own fixtures only. Early failed
setup DBs and baseline runtime remain in the disposable container for inspection;
no broad cleanup or existing container deletion. No production migrations/writes.

## 12. Security findings / corrections

No known unresolved P1/P2 V02 adapter defect after the executed suite and code review;
this is the implementer's statement, not independent security acceptance.
Initial bool keyset comparisons caused safe503; corrected cast-based comparisons with
full Django oracle regression. Initial MediaAsset multi-sort differed from native;
corrected queryset/default ordering distinction. Search now preserves native embedded
quotes/escapes. Active descriptor must agree with committed APPLIED journal and gate.
No SQL/DSN/path/password in error tests; no private DTO/export or unauthorized lookup.
Full real V03 session/CSRF, V04 pending/recovery and V05 deployment security NOT VERIFIED.

## 13. Frozen / ownership verification

[frozen-ownership.json](frozen-ownership.json) compares frozen Git blobs at fixed input
and HEAD, pins, current checkout bytes, tracked diff and allowed new paths. Existing
frontend/workflows/root scripts/historical reports/contracts/migrations/V01 are untouched.
New task-specific scripts never update shared verification registry or historical evidence.

## 14. §17 old-to-new evidence

[old-to-new-evidence.json](old-to-new-evidence.json) links existing Content baseline,
Grades PR24 and R02A results -> V02 follow-up -> named target evidence. Retain original
PR/head/merge/approvals and current acceptance reconciliation from R01/R02; distinguish
platform_disposition/current_status, original SHA, input SHA and uncommitted result.

## 15. Manifest / provenance

[workspace-manifest.json](workspace-manifest.json) contains exact current file-byte
SHA256, not fictitious commit blobs. tested_implementation_sha is null;
HEAD is input provenance only. All target publication SHA/CI/approval fields pending.
After explicit publication authorization, compute a NEW Git-blob manifest and bind
actual commit/merge-ref/CI; preserve this pre-publication record and historical records.

## 16. NOT VERIFIED / limitations

Real session/CSRF runtime, actual I02/V05 HTML renderer/gateway, full263-topic asset
lifecycle/browser visual parity, V04 edition producer/activation/recovery and final
candidate CI/independent approval. Default ports fail closed; no fake production success.
Public source/page-metadata trust comes from reviewed immutable publisher artifacts;
schema validation and body/asset hashes alone do not constitute publisher approval.
No performance/public deployment/live Product LLM claim.

## 17. Required handoffs

Ruslan: review exact uncommitted adapters/locks/tests/evidence; wire explicit target
commands into his CI task, then independently approve a future published candidate.
Ilya/I02/I03: consume closed delivery/index/catalogue; connect full HTML renderer,
ordered asset lifecycle and gateway contracts; verify complete browser/SSG parity.
V03: connect synchronous verified identity/CSRF ports; prove real sessions, revocation,
same-origin security and staff writes separately. V04: supply reviewed complete release
files/staged hash inventory and edition reader; prove actual pending/recovery/activation.
Handoffs are documented, not sent as unauthorized external messages.

## 18. Recommendation / file list

**READY FOR INDEPENDENT REVIEW of this V02 backend scope.** Task approval, publication,
current target CI and downstream integration are still pending; no COMPLETE/ACCEPTED claim.
[workspace-manifest.json](workspace-manifest.json) and [files.md](files.md) enumerate
every created file with purpose. No tracked existing file was modified/deleted.
