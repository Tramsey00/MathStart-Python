# [reviewer]: working-runtime drift evidence for R01

Source baseline: `8c11edadc8debc81432d1db1145feac504f09061` (after PR27).
Scope: five published ContentPage records and their served payloads; not a claim
about the whole working database or all data at an earlier commit.
Captured from the read-only analysis of 2026-10-07. No working DB synchronization,
publication, migration or screenshots were performed for that analysis.

## Method and limits

- Existing Django environment; PostgreSQL connection in a verified READ ONLY
  transaction with rollback; process default_transaction_read_only=on.
- Compare source through the normal load_bundle renderer for lessons, authored
  site_content payload for public pages, and actual ContentPage fields.
- Compare exact bytes and again after CRLF/CR -> LF normalization. For the power
  lesson also compare parsed HTML tokens and normalized text nodes.
- GET the five routes: HTTP 200, published DB payload present in HTTP response.
  Fourteen referenced shared CSS/JS resources match Git after LF normalization.
- Verify source hashes against the existing R01 source-manifest at saved ref
  origin/ms7-mig-baseline = 2af105c515c4e296613834118c15609efcdb6710.
- For the specifically checked payload fields, current working values match
  HEAD^ (4df7403208312d73adaa34f00f10b025db686fe4) after LF normalization.
  This does NOT establish that the entire DB corresponds to that commit.
- Visual impact below is inferred from DOM/CSS/JS differences; no new image or
  pixel comparison was made. Working DB is not the source-baseline authority.

## Differences

1. `/` (slug glavnaya), HTML: runtime has old card sections "Для чего нужен
   сайт" / "Что находится внутри разделов" and trailing note. Source has
   ms-benefits-list and ms-lesson-sequence / "Как устроен урок", new text,
   and no trailing note. Hero/classes/inline behavior retained. Substantive,
   visibly changes blocks and vertical spacing. Local CSS/JS empty in both;
   compared metadata agrees.
   Files: site_content/pages/glavnaya/{body.html,page.json}.
2. `/karta-sajta/`, HTML and metadata/SEO: old hero/badge and "Карта сайта"
   versus compact header "Все темы" and new introduction. Runtime title is
   "Карта сайта", seo_title/seo_description empty; source sets "Все темы",
   "Все темы — MathStart" and the search/grade/subject description. Substantive,
   visible heading/spacing/tab title changes. Current catalogue template/search
   is already served; no local CSS/JS difference.
   Files: site_content/pages/karta-sajta/{body.html,page.json};
   templates/includes/catalogue.html.
3. `/linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii/`, HTML/CSS/JS:
   old ms-linear-lab versus shared ms-graph-layout, reset next to formula,
   compact legend/properties/readout; balanced four-card group; single rather
   than double br in solutions. Old local CSS replaced with four shared-theme
   additions. New JS rendering and pointer hover/readout/guides/point marker
   absent from runtime. The old body does not trigger function-graphs.css.
   All substantive, visibly and functionally significant. Metadata agrees.
   Files: curriculum/7-klass/algebra/02-linejnaya-funkciya-y-kx-b/
   03-linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii/
   {lesson.json,body.html,page.css,page.js}.
4. `/10-klass-stepennye-funkcii-i-grafiki-2-0/`, HTML including inline CSS:
   source adds display:flex;flex-wrap:wrap to graph layout, flex:1 1 280px to
   graph area, flex:0 1 245px;min-width:0 to controls, and ms-balanced-four to
   three card groups. Five DOM-token change groups; all text nodes agree.
   Formatting differences also exist; layout differences are substantive and
   affect responsive wrapping/card grids. Shared math.js/power-functions.js
   agree with Git; local CSS/JS empty. Metadata agrees.
   Files: curriculum/10-klass/algebra/02-stepeni-korni-stepennye-funkcii/
   07-10-klass-stepennye-funkcii-i-grafiki-2-0/{lesson.json,body.html}.
5. `/10-klass-chislovaya-okruzhnost-2-0/`, CSS only: runtime lacks source's
   @media(max-width:620px) .ms-lesson-page .v2-lab-grid {
   grid-template-columns:minmax(0,1fr) }. Substantive mobile layout correction,
   relevant at 360px; this rule is inactive at 768/1440px. LF/CRLF differences
   coexist and do not explain the missing rule. HTML/JS/metadata agree.
   Files: curriculum/10-klass/algebra/04-sinus-kosinus-tangens-kotangens/
   01-10-klass-chislovaya-okruzhnost-2-0/{lesson.json,body.html,page.css,page.js}.

Shared rendering sources: templates/{base.html,page_detail.html},
content/{views.py,services/lesson_theme.py,services/lesson_sources.py},
static/mathstart/css and static/mathstart/js. They are the current baseline;
the drift described here is in specific working published records.

## SHA256: exact Git source / exact current DB payload

Hashes are field/file payloads, not whole HTTP responses. Source hashes already
exist in R01 source-manifest; current DB hashes were calculated in memory.
All changed fields remain unequal after LF normalization.

| Route / field | Git source SHA256 | Current working DB SHA256 |
| --- | --- | --- |
| / body_html | fbb6da7e15260ebac785a991887043621bfcf956518bc953ecaf2388038f18ae | 5134bbb63363499182f331c234eb21c96b3f02d3a344e95ed3b0c58f669ed60d |
| /karta-sajta/ body_html | 3251e567532c70e9c5df14e927133f6a6a999fb2ef52d3d84adcdb91ce2c61c1 | 75fce758f5c00fc7deeda2f16d1cc5f990d8ad5317141d81b905747cdd70658d |
| linear body_html | ab50d467686dd1667b167042c4bec137f8b8527740fe0953b77a1cc88c4397e6 | a6a6f38c7f58abc9efe4a7328a94b58c5c5d8543f9b4b47cf55506f656f29304 |
| linear page_css | 879c690b8cfe5dbf78ac6a28500539124a955502635036988b4bcb181b39d77f | 393a88175e5fcbccd01b2826e5e09d65d76615b881093caf61761da8c603133f |
| linear page_js | 0faac1e2466e7464bf402e4a21f46c6538a84909d164388d764f482080c77bc7 | 23a4f3a7020a50388d0dea364762f4607f9a04417739ec6ff1398f982f7371d2 |
| power body_html | 912de6a98700ea78bc6fdd719200d1c09ed6dd16fdca75f2b658d368661e97c7 | abc5d282893ee217a84bb196a6b4b0391c5c5d3b8308a707242b6f83eab270bb |
| circle page_css | 61c38c2d920cd051ec515ca0023e5d2a8e16ef3fdff1a0d1a60f32c8ab2b2486 | 71179196256131e673fb664c97ca64ce4afa9de69af0ef80550590ac745abe1b |

## Existing R01 evidence is a separate runtime observation

In R01 rendered-runtime-digests.json at the saved ref above, all three lessons'
runtime/rendered/publication snapshots agree. Those payload hashes equal the
Git hashes above. Its home/catalogue runtime differs only by LF/CRLF and has
body_html hashes 35377874b1ab0929a6a72b6159711c4d08b11f3b2ad591769226f4e4a76fe437
and 37c2bc215441492de46f7ed2ef2498fb0e63442db6488b10733d04641e35fb62.
These are NOT the current working DB hashes in this report.

## Review implication

Source 8c11edad reflects PR27's intended final implementation for these routes.
Independent visual/content acceptance is not inferred from merge. D02/D03 are
human decisions; this report grants no approval and changes no shared R01 record.
Use a separate fresh PostgreSQL/source instance for source-baseline screenshots.
