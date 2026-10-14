# MS7-MIG-V02: Content, Grades, routing and staff reads

- Status: Active; implementation and independent review pending.
- Owner: Vladimir; Reviewer / Task Approver: Ruslan. Consumer: Ilya.
- Created: 2026-10-12 Europe/Moscow. Issue: https://github.com/Tramsey00/MathStart-Python/issues/35.
- V02_BASE_SHA / initial HEAD / merge-base: `0c03197e23f69a233c0fcf8bdffa336feca20b92`.
- MIG_BASE_SHA: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7` (historical provenance).
- Initial branch `ms7-mig-v02-content`, clean; R02 PR48, V01 PR51 and I01 PR50 integrated.
- Surface: bootstrap Codex; no live Product LLM, no acceptance/commit/push/PR authorization.

## Sources and interpretation

Actual supplied v7.1 SECTION20 PARALLEL DEADLINES PDF: 114/114 readable pages,
SHA256 `e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd`.
Supplied migration PDF: 60/60 readable pages, SHA256
`a0c72fda223f86622d01665eaa7ec9d854c7b0b3014de38174f9ad4c582eb66e`.
Normative sections: v7.1 §§5–11,15–17,20–27, migration v1.1 §§3–11,15 V02,17,20.
The supplied SECTION20 bytes are authoritative; no replacement by the earlier G0 edition.
Platform supersession follows ADR0006 only; domain/evidence invariants remain.
Read R01 route/admin inventory, R02 delivery/staff/auth/platform/build/list policy,
historical R02A OAS/DTO/policy, Django grades/catalogue/views/admin/sitemap/redirect
code/tests, V01 model/UoW/repository/schema chain and I01 consumer README (read-only).
Historical PROPOSED/PENDING labels remain immutable; user supplies accepted R02/V01
intake and their merged integration commits. No historical approval is rewritten.

## Plan and route mapping

| Legacy source / route | Accepted contract | Target / tests |
| --- | --- | --- |
| content.api_views, GET /api/v1/grades/ | R02A GradeListResponse + R02 auth cursor | V01 UoW, bounded SQL keyset; signer parity, IDs/number, edits/deletion/inserts, no writes |
| home/page_detail; / and /<slug>/ | R01 routes, R02 content/build | Active descriptor + validated immutable release; renderer port to I02/V05; visibility, aliases, metadata |
| Content delivery | R02 GET /api/v1/content/pages/{slug}/ | Closed ContentDelivery; source/render/asset digests, negative export/manifest cases |
| karta-sajta catalogue | R02 B02, legacy catalogue_context | Already PG-ordered release catalogue; LAST query values, Unicode casefold, grade-local IDs, filters/count |
| sitemap/robots/redirect/static/media | R02 method/CSRF families and public build | Same active release, read methods, trusted origin, fallback precedence, URI serialization, safe asset allowlist |
| Seven Content admin models + User/Group reads | R02 staff OAS/list policy | List/detail/history, DB flags and direct/group permissions, actor/revision-bound keyset, exact DTO |
| Existing User form selectors | R02 narrow group/permission choice gates | Guards before lookup, no Group administration grant |
| Publication observable state | R02 B06/P1 | Read-only consistent sampling; unavailable/coherent pending facts; V04 activation remains external |

Code changes restricted to new backend/content, backend/staff,
backend/infrastructure/http, backend/tests/v02; task plan, trace and
docs/acceptance/MS7-MIG-V02. No new ORM models, DDL, migrations or schema edits.
Preserve backend V01 locks; separate V02 runtime/test locks include them.
Do not implement planned assessed topic/exercise operations with absent domains.
GET grades ignores bodies including malformed JSON, per baseline; raw JSON
parser is for subsequent contract consumers, not an invented mutation endpoint.
Anonymous grades cursors have no user scope/expiry in accepted baseline.

## Ownership / handoffs

V03 supplies verified server identity and CSRF ports; default denies private/unsafe
access. V02 recomputes active/staff/superuser flags and current DB permission scope.
V04 writes journal/gate/descriptor and immutable release; V02 reads only. Missing
or invalid active release fails503, never falls back to newer DB page fields.
I02/Ilya owns full React HTML renderer and build; V05 owns production gateway.
HTTP tests may use a clearly synthetic renderer, never claim browser/SSG parity.
Root verification/CI owner Ruslan; no shared registry/workflow edits.
Full identity/session/CSRF/activation and production acceptance remain later tasks.

## Verification and evidence

Explicit V02 unit/contract/HTTP negative suite; disposable PG16 with fresh Alembic,
bounded SELECTs and READ ONLY transactions; historical Django comparator fixtures;
V01 unit/23-PG regression and unchanged R02/R02A/R03A suites.
Baseline verification uses a separate synthetic runtime, no working .env/DB.
Record commands, interpreter/packages/PG/container versions, exit codes, individual
test names/categories and safe failures. Frozen Git blob and checkout comparison
plus ownership diff, no pin refresh. §17 index links original results, follow-up,
target evidence with platform_disposition/current_status and distinct SHA fields.
Uncommitted implementation: tested_implementation_sha null, PENDING_PUBLICATION;
after owner-authorized commit, separately verify Git blobs and current candidate CI.
Plan remains active until independent human acceptance.
