# Content delivery/publication addendum v1.0.1

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


## B02 complete public build and catalogue handoff

[public-build-contract](public-build-contract-v1.json) defines the proposed
frontend/build format. V04 emits release-root/index.json (PublicBuildIndex) and
release-root/pages/<id>.json (ContentDelivery) for EVERY published page. I02 can
enumerate all routes before rendering; it never needs to invent slug discovery.
The activated /_content/index.json resolves one complete release atomically with
no-store; page files are fetched relative to its immutable
/_content/releases/<release_id>/ root and verified before use. Build reads the
same artifacts directly. These static delivery paths are proposed, not additional
implemented APIs or a target runtime claim. Asset URLs/digests come from the
per-page ordered Asset arrays; their full union is checked with the index.

Index contains all published page IDs/slugs/types/canonical paths, ordered
catalogue grade/subject/section ID/title/slug/order relations and ordered topic
ID/title/slug/order/relations/URL, home aliases, retained active fallback
redirects, sitemap metadata and system URLs. Each page has a validated Delivery
reference. HOME has canonical / and /<home-slug>/ alias200; only canonical page
URLs enter sitemap, in ID order. Account/admin/private APIs and unpublished
pages never enter public files. URLs, delivery paths, IDs and relations must be
unique/complete, and every topic corresponds to a published topic page. A build
with missing/repeated/foreign IDs, invalid relations, path traversal or private
fields fails before activation. Publication removes unpublished entries from all
new page/index/catalogue/sitemap assets together, leaving history in private DB.

Catalogue adapter reproduces catalogue_context and templates/includes/catalogue:
sort topic rows by grade order/ID, subject order/ID, section order/ID, topic order,
title and ID using the baseline PG ordering/NULL/collation. It exports this
already ordered topic list so frontend need not reproduce database collation.
Parameters are QueryDict strings: repeated q/grade/subject uses LAST value;
unknown parameters are ignored. grade not represented among topic grades resets
to empty. Available topics are then grade-filtered; available subjects dedupe by
slug keeping the first ordered entity (subject IDs are grade-local). Invalid
subject resets to empty in that available set. q uses Python str.strip and
Unicode casefold substring on topic TITLE only, preserving raw source titles;
no transliteration/normalization/body search. Empty q displays stable grouping
by actual grade/subject/section entities, selected filters open details; nonempty
q displays flat results and context labels. Preserve fallback labels, count,
zero-results/reset state. Filters do not change grade choices or re-sort matches.
Fixtures include unknown/cross-grade filters and Unicode negatives; future JS
casefold must pass these and supplementary Unicode vectors, not just lower().

The full real disposable baseline index is separately recorded in
review-baseline-public-index.json (279 published pages,263 topics,1 home alias);
it is evidence of the accepted source profile, not a deployed target release.
Counts in another source profile may differ: enumerate actual published rows,
never hardcode counts or silently export the two unpublished retained pages.

## B06 read-only publication observability

GET /api/v1/staff/pages/{id}/publication_state/ returns the closed private
PublicationObservableStateResponse under active staff and ContentPage view OR
change permission. Missing page404; unauthorized401/403; private,no-store. The
result reads the activation generation before and after a consistent journal/DB
revision sample. Return200 only if pointer generation/digest agree across both
reads and refer to validated immutable snapshots; retry at most3 samples, then
return503 rather than mixed success. A missing/unverifiable active snapshot can
be reported as UNAVAILABLE to authorized staff while public requests return503.
Reading neither mutates a journal/pointer/DB nor resumes a publish operation.

Data includes page_id, observed_at, state, active release page state, DB edition
page state, and nullable pending operation with next release/digest/stage/time
and safe enumerated failure code. No filesystem paths, raw plan, idempotency key,
actor identity, credential, publisher body or resume cursor is returned. Current
baseline serves ContentPage directly and has no pending activation layer; its
equivalent observation is IN_SYNC/current DB. New states describe the proposed
split DB/assets/SSG publication protocol and require real V04/V05 evidence.

IN_SYNC: active and DB edition match release/digest/published state, pending null.
Completed and FAILED_PRECOMMIT operations are terminal, not pending; retain their
private journal history and CLI failure outcome. This GET describes current
editions and a nonterminal operation, not a new journal/history administration.
PENDING: validated/staged operation leaves active and DB old; after DB_COMMITTED,
DB edition is next release while active stays previous. Activation switches
active to next; journal ACK may remain pending until public probes complete.
RECOVERY_REQUIRED: pending.stage=RECOVERY_REQUIRED with a safe failure code;
DB edition and active are reported separately (old active after failed activation,
or next active after ACK/cache failure). UNAVAILABLE: active pointer is missing
or its snapshot cannot be verified; active null and public requests503. A false
page_published requires null page digest/path in that edition. Relational
invariants (IN_SYNC equality, committed DB == pending next, observed generation
consistency) are service validations in addition to JSON Schema. Staff UI renders
these read-only facts without fabricating completion or offering a new CMS.

## B07 HTTP methods and CSRF precedence

Sitemap/robots are undecorated read views, like home/page_detail: safe
GET/HEAD/OPTIONS/TRACE read200; any unsafe method with valid CSRF reads200,
missing token/bad Origin403 BEFORE rendering or a page404. HEAD has no body.
No method405 replacement is accepted for these paths. RedirectFallback runs only
after actual404 for ALL methods. A resolved nonexistent /<slug>/ first receives
CSRF for unsafe requests:403 never redirects; valid token permits404 then lookup.
An unresolved legacy URL (e.g. nested .html path) has no view CSRF hook; its404
may become301/302 even for unsafe requests without CSRF. Active exact match,
working-view precedence and self-loop protection remain. Legacy redirect paths
include Cyrillic Unicode; preserve decoded request.path exact matching and UTF-8
URI serialization without normalization or double encoding. Static/media/account/
identity/grades have their distinct method behavior; see route family mapping.
Gateway/SSG must preserve these responses, not only GET navigation.
