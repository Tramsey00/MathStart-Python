# Content delivery/publication addendum v1.0.0

PROPOSED. Public content DTO is a delivery snapshot for V02/V04/I02/I03, distinct
from frozen TopicDTO and public exercise contract. V02 additive read adapter
GET /api/v1/content/pages/{slug}/ is described by the separate OAS; it is not
implemented. Publisher/build consumers use the same validated DTO directly.

## Trust, exact fields and SEO

ContentDelivery has delivery_version, existing integer id, slug, page_type,
title, nullable grade_id/subject_id/section_id, order, body_html, is_published
const true, seo{title,description,canonical_path}, created_at/updated_at,
source{path,source_digest,render_digest}, assets ordered by load order.
All fields required/closed; see [schema](delivery-v1.schema.json). Digests are
SHA256 lowercase64; source exact Git/files bytes, render exact published payload
bytes, assets exact bytes; publication snapshot digest remains the unchanged
content.services.publishing.digest algorithm, not conflated with these hashes.
Trust attaches to a reviewed publisher artifact/digest, never a DTO field alone.

Only authored/publisher-reviewed HTML/math/SVG goes into LessonHost. Keep IDs,
anchors, SVG geometry/text/ARIA, formulas, details legacy self-check answers,
template component markup and style/script ordering. Escape all user/LLM text;
no execution or trust escalation from input. Legacy details are intentionally
public authored self-check; assessed answer_key/validation_spec/canonical_solution
and private reveal/exchange fixtures never enter build/manifest/bundle. Closed
public export allowlist, not a SELECT* of ContentPage/user/session tables.
Staff private detail can contain unpublished authored content but has its own
DTO/auth/no-store and is never a public snapshot.

SEO reproduces ContentPage.meta_title/meta_description fallbacks from source;
custom metadata uses baseline strip behavior. Russian lang, UTF-8 viewport,
absolute trusted-origin canonical using get_absolute_url: home '/', other slug
'/<slug>/'. Home alias /glavnaya/ stays200 with canonical '/'. Head/footer/header,
catalogue search/filter/order from content.services.catalogue and current tokens
remain. Pre-render every published URL; unknown/unpublished404, no SPA wildcard200.
Sitemap uses published pages, updated_at, priority/frequency of baseline
content/sitemaps.py; robots allow public, disallow /admin/, absolute sitemap.
Redirect only after route404: active exact old_path, permanent301/temporary302;
no self-loop, working page wins, retain archived redirects. No mass slug rewrite.

Public GET/HEAD serve activated release; public page views baseline also accept
other methods without mutation. Preserve their read-only200 via the gateway's
activated-snapshot handler for other methods, including OPTIONS, while unsafe
methods still pass CSRF checks; no target default405 silently changes baseline.
Account GET only (HEAD baseline405), private no-store, no SSG. Debug fixture
gallery GET only/development gated; nondebug404. API limits remain separate.

## Assets and lifecycle

Each ordered asset specifies storage_key/public URL, kind style/script/media,
sha256, load order, and script lifecycle none/mount_dispose/full_document.
Keep all263 lesson sources/97 local CSS/7 local JS and shared assets/media.
Content source manifest independent of rendered snapshots/runtime text. Import
existing media keys and seed hashes; public path allowlist rejects traversal,
absolute filesystem paths and private paths. CSP/asset MIME/loader policy is
V02/I03 reviewed implementation, no arbitrary uploaded scripts. Load shared math
dependencies before local scripts. For every script family implement
mount(root,config)->dispose or explicitly tested full-document navigation.
Dispose cancels observers/timers/RAF/listeners; queries scoped to root; remove
previous lesson CSS; test StrictMode remount, back/forward and repeated resize.
One widget is not evidence for all script families. No redesign/reset/library.

## Publication operation contract

DB/files/assets/SSG cannot commit atomically. V04 owns durable journal and DB
transaction; I02/I03 build renderer; V05 owns reverse-proxy active pointer.
Operation UUID and idempotency key, expected active release and expected source/
published digests bind a frozen plan; journal has sanitized status/timestamps,
previous/next release, manifest digest, affected paths, stage, failure code and
resume cursor. Do not store credentials or private DTO. Journal schema in
delivery-v1.schema.json specifies valid stages, NOT a table migration.

Sequence: VALIDATED -> STAGED -> DB_COMMITTED -> ACTIVATED -> COMPLETE.
Preflight source validation/identity immutability/conflicts before writes.
Stage assets and complete public HTML/catalogue/sitemap/redirect manifest under
an operation-specific directory; verify all hashes and no private export.
Acquire publication gate and locks in platform order; recheck expected active
release/current snapshots; commit ContentPage+LessonPublication+DB revision and
journal DB_COMMITTED together. Activation compare-and-swaps the previous pointer
to matching release/manifest. Verify public probes, then record COMPLETE.
No success before complete activation. Repeated same key/plan returns same
operation; changed key body or unexpected release/digest fails409/conflict.

Committed DB edition and public active edition may briefly differ after failure;
public reads MUST use the active edition snapshot/manifest consistently, never
mix fresh DB title with old SSG body. Staff shows pending edition separately.
This requires a V04 release snapshot/activation representation, reviewed V01
additive schema. If chosen storage cannot serve active snapshot consistently,
keep public service unavailable503 during switch rather than mixed success;
approve alternate ADR delivery before claiming parity.

Unpublish immediately removes URL from the next active manifest/catalogue/
sitemap, retaining DB row/history; direct request404 unless an explicit retained
redirect applies. Invalidate/purge cache entries before final success and test
both warmed cache and previously opened navigation. Freshness is measured at
operation completion: all probes observe the same new release; no numeric SLA
is invented here. Concurrent publish/unpublish serialize at activation gate.

| Failure | Observable outcome and recovery |
| --- | --- |
| Before staging / validation conflict | No DB/public change; nonzero or safe conflict; fix source and new operation. |
| Partial assets/renderer failure | FAILED_PRECOMMIT; previous public edition intact; resume only matching staged hashes. |
| After staging, before DB commit | Rollback DB; previous active intact; resumable staged operation, no success. |
| After DB commit, before activation | RECOVERY_REQUIRED; journal+DB durable, old public snapshot intact; forward resume exact manifest under gate. |
| Pointer switched, acknowledgement/journal update lost | Inspect pointer+digest; mark ACTIVATED/COMPLETE idempotently after public probes, never reapply DB write. |
| Cache purge/health fails after activation | RECOVERY_REQUIRED/nonzero; retain both manifests; repair/purge forward, or reviewed safe pointer rollback only if DB snapshot consistency holds. |
| Concurrent stale expected release |409, do not overwrite winner or clear its journal. |

Cleanup resolves absolute targets within the operation directory; delete only
unreferenced owned staging after retention/recovery proof. Never remove working
media, source or another operation's paths. Dry-run validates/stages in isolated
operation root with explicit filesystem side effects but no DB publication or
active pointer writes; if a target command uses SQL rollback, it must label
that accurately. Baseline bootstrap dry-run SQL writes then rolls back, whereas
publish dry-run preflights without persistence; preserve that historical fact.

## Baseline exceptions

Ruslan working DB, Ilya working DB and Ilya disposable source reference stay
separate; CRLF/LF and five payload drift are not normalized away. Legacy
unpublished materialy/pamyatki stay retained on upgrade. [F01–F04 matrix](parity-matrix-v1.json)
copies Ilya's accepted positive criteria:13baybars fixes by I03, verifies I05;
360/768/1440 all mandatory, F04 ordinary scale (enlargement insufficient).
R02 performs no UI fix and no new browser claim.
