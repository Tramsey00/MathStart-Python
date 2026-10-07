# TRACE: Topics catalogue and retired support pages

- Date: 2026-10-04
- Surface: Codex desktop, Windows PowerShell; no subagents
- Branch: `fix/topics-catalog`
- Starting HEAD: `150e569b51a2ef84d2d17a25c675e364c808d2fc`
- Spec: [topics-catalogue](../../specs/ui/topics-catalogue.md)
- Plan: [topics-catalogue](../exec-plans/active/topics-catalogue.md)
- Human review: **Pending**, repository owner
- Commit/PR/deploy: none; implementation intentionally uncommitted

## Request and inputs

Remove standalone Materials/Handouts pages and make All topics a usable catalogue,
preserving Django, existing visual foundation, topic URLs/content and user data.
Inputs: AGENTS.md, PRODUCT.md, relevant ARCHITECTURE.md sections, ADR-0001,
docs/architecture.md, README.md, verification skill, I02 UI spec/active plan,
current Content views/templates/bootstrap/publication/models/tests and initial
migration. Other task documents are compatibility context only.

Initially no tracked changes. Pre-existing untracked files were three pairs of
MS7-AUDIT-specification, MS7-G0Candidate-correction and MS7-PREG0-correction
plans/traces, plus output/ and tmp/. They were not edited. No working-database
migration/bootstrap was performed.

## Implementation and file inventory

| File | Reason |
| --- | --- |
| `content/services/catalogue.py` (new) | Published-topic read model, dynamic grade/subject options, trimmed Unicode casefold search; one related query, no lesson bodies |
| `content/views.py` | Attach catalogue GET context |
| `content/services/lesson_theme.py` | Catalogue-only loading of existing UI tokens and new scoped stylesheet |
| `templates/includes/catalogue.html` | Labelled GET form, count/reset/empty state, hierarchy and directly visible search results |
| `templates/page_detail.html` | Single main container for catalogue heading/form/results; ordinary content unchanged |
| `templates/base.html` | Remove only the two retired navigation links |
| `static/mathstart/css/catalogue.css` (new) | Responsive layout, wrapping and focus, scoped to `.ms-catalogue` |
| `site_content/pages/karta-sajta/body.html` | Compact heading/introduction |
| `site_content/pages/karta-sajta/page.json` | All topics title and SEO metadata |
| `site_content/pages/kontakty/body.html` | Remove retired link/promise; link All topics |
| `site_content/pages/o-proekte/body.html` | Clarify rules/algorithms belong in lessons |
| `site_content/pages/materialy/body.html`, `page.json` (deleted) | Remove page source only |
| `site_content/pages/pamyatki/body.html`, `page.json` (deleted) | Remove page source only |
| `curriculum/7-klass/algebra/04-svojstva-stepenej-s-naturalnym-pokazatelem/03-bazovye-svojstva-stepenej-s-naturalnym-pokazatelem/body.html` | One PDF link paragraph |
| `site_content/media.json` | Associate existing PDF with that lesson; bytes/path/hash unchanged |
| `site_content/redirects.json` | Four direct permanent redirects; two existing legacy rules updated, two root rules added |
| `content/services/site_bootstrap.py` | Explicitly unpublish only the two retired static slugs; retain rows and references |
| `content/management/commands/bootstrap_site.py` | Report actual unpublished count |
| `content/test_catalogue.py` (new) | Five catalogue regression tests |
| `content/test_bootstrap.py` | New upgrade/rollback/idempotency/preservation test; strengthened composition checks; updated exact counts |
| `scripts/fresh_install_smoke.py` | Update exact fresh counts; retain identity/content/media/user/source verification |
| `specs/ui/topics-catalogue.md` (new) | Scoped UI/publication contract |
| `docs/exec-plans/active/topics-catalogue.md` (new) | Plan and application procedure |
| `docs/agent-traces/topics-catalogue.md` (new) | This evidence record |

No changes to site.css, site-pages.css, lesson styles, schema/migrations,
dependencies, CI, deployment, accounts, API/learning domains or other task status.
No generic missing-source deletion was introduced. Existing publication conflict
checks remain in effect. Native details and GET forms require no catalogue JS.

## Environment and database evidence

Actual project environment: `.venv312/Scripts/python.exe`, Python 3.12.10,
Django 5.2.16, psycopg/psycopg-binary 3.3.6, pip 26.2.1. `pip check` passed.
PostgreSQL connection check passed, server_version_num=160015. Docker client/server
29.8.1, Compose 5.5.1. Older `.venv` reports Python 3.10.11 and invalid configured
database input on that execution surface; it was not used for acceptance.

Agent-owned local runtime/evidence lives in ignored `var/topics-catalogue/`.
The working database was read only for connectivity/version reporting and to
create two separately named disposable databases through the configured account.

- `ms6_v01_smoke_topics_20261004`: migrated and bootstrapped from original source
  before the source removals; then dry-run, actual upgrade and repeat.
- `ms6_v01_smoke_topics_fresh_20261004`: fresh migrate and double bootstrap from
  the final source, via the existing disposable smoke command.
- Focused/full Django suites used separately named test databases; SQLite used
  an explicit isolated compatibility configuration, not a PostgreSQL fallback.

Upgrade snapshots confirm: no pre-existing row removed, 279 published pages
(263 topics + 16 support/structural pages), two retired ContentPage rows retained,
29 media assets, 282 redirects. Meaningful ContentPage changes are exactly the
catalogue, Contacts, About, PDF lesson and two retired pages. Grade/Subject/Section
values are unchanged. One lesson publication digest and one PDF relation change;
two legacy redirects change and two root redirects are added. Runtime PDF/media
bytes and sentinel user are unchanged. Repeat preserves identities and content;
preflight SQL changes roll back. Standard bootstrap auto-updated timestamps are
excluded from semantic snapshots. Existing test also preserves unrelated local
published and unpublished ContentPages with full-row equality.

## Verification

Commands below use `.venv312/Scripts/python.exe`; DB/runtime overrides always
target the isolated environments above.

| Check | Actual result |
| --- | --- |
| `python -m pip check` | PASS, no broken requirements |
| `python scripts/check_database.py` | PASS, PostgreSQL 16.15 |
| `python manage.py test content.test_catalogue content.test_bootstrap content.test_ui_foundation --noinput` | PASS, 12 tests on PostgreSQL |
| `python manage.py test content.test_catalogue content.test_bootstrap --noinput` with explicit SQLite | PASS, 7 tests, including Cyrillic and upgrade |
| Original-source upgrade/dry-run/repeat snapshots | PASS, `var/topics-catalogue/upgrade.json` |
| `python scripts/fresh_install_smoke.py --disposable` | PASS, fresh PostgreSQL migrations, double bootstrap, identity/content/media/user/source preservation and static/content checks |
| `python scripts/verify_repo.py` | PASS 8/8 on final rerun; 85 Django, 18 R03 and 73 Harness tests, all passing |
| `git diff --check` | PASS at final review; new files also checked for whitespace/conflict markers |

Initial full verification failed Content quality because this newly isolated
runtime had no collected static manifest (`Missing staticfiles manifest entry
for mathstart/css/site.css`). This is test-environment preparation, not an
application defect. `collectstatic --noinput` produced 172 files / 498 processed;
the canonical full verification was rerun. The initial Django, R03 and Harness
suites passed. No validation or check was weakened.

## Browser evidence

Built-in CUA and node_repl failed at process launch (`apply deny-read ACLs`).
Existing Node 24.19.0 and installed headless Edge 154.0.4258.53 were used through
DevTools for local browser testing. No frontend package/toolchain was installed;
browser had its own test profile and only accessed isolated localhost servers.
Test scripts and JSON evidence are in `var/topics-catalogue/browser-*.cjs/json`.
An initial automation Enter event omitted its character payload; correcting the
test event made native keyboard expansion pass; no product fix was needed.

At 360, 768 and 1440 px:

- PASS one heading/container, 263-topic count and no horizontal overflow.
- PASS without site JavaScript: Cyrillic search, combined filters, dependent
  subject choices, reset, empty result and invalid parameter recovery.
- PASS native summary keyboard expansion and visible search-input focus.
- PASS direct URL, refresh and browser Back retain query/filters after a lesson.
- PASS real PDF response: HTTP 200, application/pdf, 1,217,381 bytes.
- PASS comparison of home, GCD/LCM and natural-exponent lesson at all three
  widths: identical body excluding the intended header edit, identical CSS
  lists and heading/section dimensions, no horizontal overflow.

Before screenshots used the baseline base.html from starting HEAD and the
original bootstrapped DB; no source checkout/reversion was performed. The compact
mobile header intentionally moves content upward. Visually inspected catalogue
screenshots at all three widths, mobile search, and representative before/after
pairs for all three ordinary pages. This is Edge desktop viewport evidence,
not a physical-device, screen-reader or full cross-browser audit.

Screenshots (local, ignored artifacts):

- `var/topics-catalogue/catalogue-360.png`, `catalogue-768.png`, `catalogue-1440.png`
- `var/topics-catalogue/search-360.png`, `search-768.png`, `search-1440.png`
- `var/topics-catalogue/empty-360.png`, `empty-768.png`, `empty-1440.png`
- `var/topics-catalogue/before-{home,gcd,powers}-{360,768,1440}.png`
- `var/topics-catalogue/after-{home,gcd,powers}-{360,768,1440}.png`

## Final review and limits

Implementation prepared for review; human acceptance is pending. Keep the plan
active. No claim of human acceptance, CI on a pushed commit, commit, PR, merge,
deployment or application to the working database. Search intentionally scans
the lightweight published title catalogue in Python for Unicode parity; at a
materially larger catalogue its cost should be re-evaluated in a separate task.
Subject options update on submitting the GET form, as the on-page helper explains.

Final full verification exited 0; log: `var/topics-catalogue/verify-repo-final.log`.
Fresh smoke exited 0; log: `var/topics-catalogue/fresh-postgres.log`. Content quality
checked 279 published pages / 840 SVGs with zero issues. Integrity reports no
broken internal, media or static links. All 263 lesson sources match the database.
Full tracked diff and six new files reviewed (26 task files including deletions).
Branch and HEAD remain unchanged. No unresolved automated failure remains.
Two agent-created local test servers were stopped; disposable databases and
ignored evidence/runtime files remain for reproducibility. No other browser or
server process was stopped.

Final status: **implementation verified; human acceptance pending**. Repository
Definition of Done is not declared complete until the owner accepts the result.

## Local 500 correction (2026-10-04)

The owner reported HTTP 500 at `http://127.0.0.1:8000/karta-sajta/`.
Read-only reproduction with the configured `.venv312` environment showed
`DEBUG=False` and an existing local staticfiles manifest missing both
`mathstart/css/ui/tokens.css` and `mathstart/css/catalogue.css`. Django raised
`ValueError: Missing staticfiles manifest entry` while rendering the catalogue.

Ran `python manage.py collectstatic --noinput` against the configured local
runtime: 32 files copied, 140 unmodified, 471 processed. A fresh Django process
then rendered HTTP 200; the running server still cached the old manifest.
Updated only the modification time of the already changed `lesson_theme.py`
to trigger normal runserver autoreload, without changing its bytes. The live
`127.0.0.1:8000/karta-sajta/` response and both hashed stylesheet URLs then
returned HTTP 200. No database update, migration/bootstrap or product-code
change was performed for this correction. Human acceptance remains pending.
