# R01 baseline inventory

Input commit: `8c11edadc8debc81432d1db1145feac504f09061`; live remote/local main
agree. [Source manifest](source-manifest.json) records all 1,026 tracked files,
sizes, exact Git-blob SHA256 and both checkout byte hashes. Runtime facts are
separate in [runtime-data-manifest.json](runtime-data-manifest.json), with
[rendered digests](rendered-runtime-digests.json). [File inventory](file-inventory.json)
enumerates templates/assets/tests and management command arguments. This is
the current Django contour; target React/FastAPI is proposed only.

## Routes and services

| Current surface | Actual implementation / behavior |
| --- | --- |
| `/`, `/<slug>/` | `content.views.home/page_detail`, published ContentPage only; Django template/theme context; unknown/unpublished 404; karta-sajta adds catalogue/search query context. These public view functions have no explicit method decorator; GET is HTTP-verified, method acceptance is inventoried from source. The published `/glavnaya/` slug alias responds 200 before redirect fallback. |
| `/account/` | GET-only Django account template; private no-store, client identity controller talks to real API; contains no new diagnostics/progress engine. |
| `GET /api/v1/auth/csrf/` | CSRF bootstrap; real identity API. |
| `POST /api/v1/auth/register/`, `login/`, `logout/` | Real strict raw-JSON identity/session services, validators, CSRF, safe envelopes, DB-shared login window and registration receipts. |
| `GET/PATCH /api/v1/users/me/` | Two real operations; authenticated profile read/update, selected Grade PK, no mastery mutation. |
| `POST /api/v1/onboarding/complete/` | Real idempotent profile mode selection for START_ZERO / DIAGNOSTIC / SELF_REPORT; no implemented learning diagnostics or Progress writes. |
| `GET /api/v1/grades/` | Public DRF GradeListView, real ID vs number, `(created_at,id)` keyset, signed cursor scope/default20/max100; invalid query/body/unsupported row safe outcomes. |
| `/sitemap.xml` | Published-only ContentPageSitemap, absolute page locations, updated_at/priority/frequency. |
| `/robots.txt` | Text/plain, allow public, disallow admin, absolute sitemap URL. |
| Redirect service | RedirectFallbackMiddleware runs only after 404; active exact old_path; 301/302; self-loop guarded; does not override working route. 282 runtime/source rules; retain all, including retired page redirects. |
| `/static/` | Shared static sources; WhiteNoise compressed manifest delivery; collectstatic-generated runtime is separate. |
| `/media/` | FileSystemStorage; local DEBUG URL serving only; deployment needs external/edge delivery. 29 versioned seed media and working MediaAsset rows. |
| `/__ui__/foundation/` | DEBUG-only GET synthetic fixture gallery, no-store; absent in non-debug runtime; fixtures do not implement exercises. |
| `/admin/` | Django login/logout/password/site/model administration; exact operation inventory below. |

Seven implemented identity operations plus one grades operation are distinct
from the 37 canonical OpenAPI operations in `specs/api/openapi-v1.json`.
Content pages are actual Django delivery, not additional implemented DTO APIs.
Health/topics/attempts/diagnostics/progress/practice/tutor operations in the
canonical specification remain planned; pure R03/R02A/R03A oracles are reference
contracts, not ORM persistence or live AI. No generated FastAPI OAS exists.

## Templates, authored lessons and assets

13 repository Django HTML templates include page_detail/base, lesson components,
UI/gallery and `templates/users/account.html`. Preserve template renderer
equivalence, inherited metadata and stylesheet/script ordering. The exact list
is in file-inventory; no asset family is omitted based on a sample lesson.

The source tree contains 263 lesson.json and body payloads, 97 lesson-local
page.css and seven page.js, plus 16 structural page.json. `component_html` and
`themed_html` use deterministic Django component/contents rendering; plain html
is authored as-is. Shared CSS covers site/account/lesson math/components/
diagrams/contents and widgets; shared JS covers identity actions/controller,
transport, foundation, lesson contents/diagrams and widgets. All paths and
source hashes are listed, including SVG/formula-bearing authored HTML and seed
media. The existing legacy `<details>` answers are self-check content, not
assessed server-reveal evidence. Future target exports may not bundle private
fixtures or validation secrets.

Working content quality has 279 published pages and 1,137 inline SVG. Digests of
authored blobs are not digests of renderer output or DB text. All 263 topic
runtime snapshots and publication digests match the rendered candidate sources.
Thirteen structural body payloads differ only by LF/CRLF and match after LF
normalization; their exact hashes remain recorded. Eleven match original local
source bytes; home/catalogue also contain LF/CRLF differences relative to that
checkout. No field outside body_html differs. Keep the working runtime unchanged
and obtain the explicit baseline byte-policy decision. The two unpublished
`materialy` / `pamyatki` rows are runtime legacy extras, not lost source pages.

## Commands and publication

| Existing custom command | Effects / boundary |
| --- | --- |
| `publish_lessons --slug ... / --all [--root] [--dry-run]` | Validates source/render/catalogue, builds conflict-aware plan, locked transaction/recheck; preserves identity and accepted publication digest. Normal run writes DB and SQLite-only backup; dry-run is publication preflight, no persistence. It is not a general read-only database audit. |
| `bootstrap_site [--root] [--dry-run]` | Synchronizes source catalogue/structural pages/redirects, publishes lessons, copies verified missing media and syncs MediaAsset. Normal execution has multiple DB/files stages; dry-run performs SQL structure writes inside rollback, no media copying. Never use it to claim read-only. |
| `update_public_pages [--dry-run]` | Scoped home/catalogue/about/contact + power lesson/PDF + retirement redirects; conflict preflight, public-record fixture backup, media copying, transaction. Dry-run rolls SQL back and avoids backup/media files; preserves retired rows as unpublished. |
| `index_lessons [--root]` | Reads published catalogue/source and writes curriculum/INDEX.md. Filesystem mutation; not an admin equivalent or DB read-only guarantee. |
| `check_lesson_sources --slug ... / --all [--root]` | Compares runtime lesson snapshots/identity/publication to renderer sources; no DB mutation. |
| `check_content_quality` | Reads published HTML/SVG, reports source issues to isolated var/reports; no DB mutation. |
| `check_site_integrity` | Reads routes/catalogue/redirect/media/assets, blocking vs informational findings, writes reports under runtime root. |

`scripts/verify_repo.py` has eight checks across backend/database/content/tests/
Harness. Additional current scripts are check_database (bounded safe failure),
version_report, fresh_install_smoke (strict disposable PostgreSQL guard, migrate
from zero, bootstrap twice, user/source preservation, collectstatic/content),
lock_dependencies and pure r03/r02a/r03a reference modules. The Harness owns
TaskManifest/RunResult, check identities, lifecycle and provider adapters; its
deterministic tests require no live LLM. `repo-baseline` excludes Harness to
prevent recursion. No Harness/verify entry rewrite is part of R01.

The framework-command registry is exported by the inventory tool, including
admin auth operations (`createsuperuser`, `changepassword`), migrate/showmigrations/
makemigrations/sqlmigrate/migrate checks, runserver, collectstatic/findstatic,
test, check, shell/dbshell, dumpdata/loaddata/flush and other installed Django
commands. These remain baseline capabilities to classify for replacement or
retained historical tooling; destructive/import/export operations are not run
against working data. CLI is not accepted as a blanket replacement for admin.

## Models, migrations and working schema

Content owns Grade, Subject, Section, ContentPage, LessonPublication, MediaAsset
and Redirect. Users owns StudentProfile (UUID, protected user/grade),
IdentityReceipt (private durable replay, uniqueness/checks) and LoginWindow
(shared IP-HMAC counter, count limit). Auth User/Group/Permission, associations,
sessions/contenttypes/admin history are framework tables. No Knowledge,
Assessment or Progress persistence exists. Schema manifest records actual
columns/types/nullability/defaults, PK/FK/UNIQUE/CHECK/index/sequence metadata
and all 22 applied migrations. Django on_delete behavior differs from SQL FK
actions and needs explicit future mapping.

Working rows: Grade6, Subject12, Section63, ContentPage281, LessonPublication263,
MediaAsset29, Redirect282. Published279; Users/auth/session/receipt/counter rows
are zero; permission catalogue64. Applied `content.0001_initial`,
`content.0002_grade_created_at`, `users.0001_initial`,
`users.0002_backfill_profiles` are present. Historical local profile-A absence
is obsolete for this working DB; retain it as a future synthetic upgrade profile.
Grade legacy timestamp epoch is tracking baseline, not recovered creation dates.
No migrate/bootstrap/publish/stamp is executed against the working DB.

## Staff / admin operations and permissions

[Machine admin inventory](admin-inventory.json) records nine registrations,
list/search/filter/read-only fields, add/change fieldsets, actions, model URLs
and permission codenames from installed Django using an unsaved synthetic user.
It exports metadata only and does not grant or exercise a real staff identity.

Seven Content registrations allow list/detail/history/search/filter where
configured, but deny add/change/delete even to superuser. Their action lists
are empty. SourceManagedAdminMixin is a real restriction to preserve. A
view-capable active staff identity needs `content.view_<model>` (or Django's
accepted change permission for view); add/change/delete flags remain false.
Page detail includes source_location, body/CSS/JS/SEO, hierarchy and timestamps;
Publication includes source path/digest; MediaAsset includes file/alt/page;
Redirect has active/permanent filters. Exact list fields are in JSON.

UserAdmin supports list/detail, username/email/name search, active/staff/
superuser/group filters, add with password/usable-password fields, change
username/contact/password, active/staff/superuser flags, groups/direct
permissions and date fields; dedicated password path; history, protected
delete confirmation and delete_selected. GroupAdmin supports name search,
add/edit/delete/history and permission selection, including delete_selected.
Model permissions `auth.view/add/change/delete_user/group` and active staff
site access govern these operations. Superusers have permission bypass;
deletions still meet related PROTECT constraints. No model-specific custom
Content mutation action exists.

Permission itself is **not registered** for standalone list/create/edit/delete;
permission assignment is available through User/Group selectors. Profile,
Receipt and LoginWindow also are **not registered**. Do not invent their staff
CRUD or drop a User/Group operation because there are no current users. Preserve
admin login/logout/site password change, auth authorization, search/filter/
pagination/list/detail/history and operation-specific protections. Any proposed
scope exclusion must name the operation and be accepted at MIG-G0. Target
staff/API/UI work remains V02/V03/I02/I04.

## Tests, CI and historical evidence

Existing Django tests cover content/public pages/catalogue/publishing/media,
grade migration/DTO/cursor, infrastructure/fresh guards, UI fixtures/account,
identity/profile/retry/security and real PostgreSQL multi-connection races.
Pure suites cover R03 graph/Decimal projection, R02A HTTP/exposure/idempotency,
R03A completion/replay, and I02 schema/dispatcher. Harness tests retain fake
adapters, manifest/digest checks and runner lifecycle. Semantic UI tests invoke
Node when configured; passing reference suites does not prove target UI.

Existing CI `.github/workflows/ci.yml` triggers PR→main and main push, installs
the existing Python lock, PG16 disposable service, versions/bounded connection
failure, fresh smoke, full baseline and separate R02A/R03A suites. It currently
does not target integration branches; changing that is R03. Input main CI
37595359404 is success on 8c11eda; it cannot establish new snapshot-head CI.
Live main is unprotected with no required contexts/rulesets discovered, but
the specification still requires green CI and independent review before merge.
See [GitHub audit](github-audit.json) and [old-to-new index](old-to-new-evidence.json).

Historical output links were checked on disk in
[historical-output-links.json](historical-output-links.json). Missing/pattern
references remain explicitly marked; files are not presumed present from a
trace. In particular the earlier v1.1 PDF/Markdown delivery paths must not be
used as reproducible inputs without their existence/hash evidence. The Desktop
Markdown exact copy is the canonical R01 input. The original working tree,
recovery trace and 18,568 pre-existing output/tmp files are preserved; a private
path/hash inventory lives in R01 QA, with only its aggregate digest committed.
