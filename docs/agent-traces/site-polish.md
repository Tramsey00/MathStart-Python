# TRACE: Bounded public-site polish

- Date: 2026-10-04
- Branch/start HEAD: `fix/topics-catalog` / `9ef93f90767b6639a0ebf3c23aa7bc9d288456d3`
- Spec/plan: `specs/ui/site-polish.md`, `docs/exec-plans/active/site-polish.md`
- Human acceptance: Pending

## Baseline

Read repository/product/architecture/ADR/publication/UI documents, previous
catalogue task and verification skill. No tracked or staged initial edits;
foreign untracked files retained. Working DB is local PostgreSQL `mathstart`,
DEBUG=False, runtime at repository root. Actual port-8000 requests returned
200, including both obsolete pages. Catalogue/About/Contacts body differed
from source. Seven public-page rows, related publication/PDF and existing
redirects snapshotted in `var/site-polish/before-fixture.json`.

Fingerprint inventory initially hit a missing `users_studentprofile` table.
Adjusted the read-only evidence script to inventory existing tables; did not
apply out-of-scope account migrations. Actual Python 3.12.10, Django 5.2.16,
psycopg 3.3.6, PostgreSQL server 160015. Browser baseline records all six
representative pages at 360/768/1440 before edits.

## Implementation and local application

- Compact catalogue introduction, inline decorative square-root brand, one
  shared responsive footer. Changed only shell selectors and page/block roots;
  existing UI tokens load on the three revised informational/home pages.
- Rewrote About/Contacts body and SEO; preserved confirmed email and precise
  partial grade-10 coverage. Removed gallery markup and its only-consumer CSS;
  kept PDF rules in combined selectors and all physical/MediaAsset records.
- Replaced exactly two home information sections and removed the note. Hero,
  CTA, class/subject selector, accordions and inline behavior are preserved.
- Added `update_public_pages` management command/service using validated source
  loading, selected bootstrap synchronization, existing conflict-safe lesson
  publication, public-record snapshot and a DB transaction. Existing full
  bootstrap/retirement implementation remains unchanged.
- Ran working `--dry-run` (rolled back), isolated source-copy upgrade and fresh
  smoke, then the permitted local command. It selected 4 pages/4 redirects,
  retired 2 static rows, published 1 prepared PDF-link lesson, copied no file.
  Snapshot: `var/backups/before-public-pages-20261004T192025339076Z-4f57b259.json`.
- Collected static: 2 copied, 170 unmodified, 457 post-processed. Touched only
  LastWriteTime of already edited `lesson_theme.py` to trigger the existing
  runserver's autoreloader; did not stop processes or change configuration.

Full-row fingerprint comparison shows only ContentPage IDs 13–18/111,
LessonPublication 93, MediaAsset 22 and Redirect 113/145/283/284 changed.
Redirect 283/284 are the two new root rules. All other existing table rows,
including users, grades, subjects, sections, media and lessons, are unchanged.
Evidence: `var/site-polish/database-changes.json` and before fingerprints.

## Verification evidence so far

| Check | Observable result |
| --- | --- |
| `python -m pip check` | PASS, no broken requirements |
| Isolated working-content upgrade / dry-run / repeat | PASS, restored 934 Content records in a migrated disposable PostgreSQL DB; unrelated rows and user sentinel unchanged |
| `python scripts/fresh_install_smoke.py --disposable` | PASS, fresh PostgreSQL migrations, double bootstrap, content/media/identities/static checks |
| `python manage.py test content.test_public_pages --noinput` | PASS, 5 tests on PostgreSQL, including conflict refusal, late rollback and production manifest/CSS |
| Live port-8000 pages and CSS | PASS, six pages HTTP 200, all linked CSS HTTP 200 and updated content matches source |
| Four live old URLs | PASS, direct 301 to catalogue/powers lesson; no old HTML |
| Live sitemap | PASS, retired paths absent |
| PDF storage/link/ownership | PASS, 1,217,381 unchanged bytes, SHA256 `21a676be8d2be2b49aade668dfc7929e53a971d99fa0c1bee3990fd21e6f3868`, original URL and published link, correct related_page |
| PDF HTTP on working runserver | EXISTING ENVIRONMENT LIMITATION: 404 at DEBUG=False; unchanged config/urls.py only serves media with DEBUG=True |

First focused run (12 tests) had two test-isolation failures: a prior test's
backup directory remained on disk while later tests expected an absent shared
directory. Separated each test's backup root; the five new tests then passed.
No product validation or expected behavioral assertion was weakened.

Integrity reports zero critical issues and 3 unused assets: i2.png, i3.png,
i4.png, intentionally retained after gallery removal. Checks remain unchanged.
Working account-profile table remains absent; no account migration was applied.

## Browser evidence

Used installed Node/Edge DevTools headless with its own test profile, no added
frontend packages. Edge 154.0.4258.53. Before/after are both actual port 8000.
`var/site-polish/browser-{before,after}.json` and `browser.cjs` preserve evidence.

PASS at 360/768/1440 for home/catalogue/About/Contacts/ordinary lesson/grade:
no horizontal overflow, one h1, live CSS 200, visible keyboard focus and shell
links. Catalogue Cyrillic search with filters (13 results), empty results,
native details keyboard expansion, refresh and browser Back pass with page
JavaScript disabled. Home class-7 hash accordion behavior passes with JS enabled.
Ordinary lesson and grade bodies excluding shell are identical; component
width/height/font/padding match baseline at each width. Home hero/classes markup
and sizes match. Changes in vertical position follow the intended smaller blocks
and shared shell. Visually inspected desktop/mobile/tablet screenshots including
new sections and footer; no extra visual changes were necessary.

Artifacts: `after-{home,catalogue,about,contacts,lesson,grade}-{360,768,1440}.png`,
`ms-home-benefits-*.png`, `ms-home-lesson-*.png`, `footer-*.png` in
`var/site-polish/`. Browser evidence is desktop Edge viewport testing, not a
physical-device, screen-reader or multi-browser audit.

## Final verification and review

| Required/additional check | Final result |
| --- | --- |
| `python scripts/verify_repo.py` | PASS 8/8, exit 0; 90 Django tests, 18 R03 tests, 73 Harness tests |
| Explicit SQLite `content.test_public_pages` | PASS, 5 tests; separate compatibility test DB |
| `python scripts/check_database.py` | PASS, working PostgreSQL server 160015 |
| `git diff --check` | PASS; new task files checked for whitespace/conflict markers |

Logs: `var/site-polish/verify-repo.log`, `public-pages-fixed.log`,
`public-pages-sqlite.log`, `fresh-postgres.log`, `upgrade-postgres.log`.
Browser tool runtime: Node 24.19.0. Live proof: `live-result.json`.
No failed mandatory automated check remains. PDF HTTP remains the explicitly
reported pre-existing local media-serving limitation; unused gallery assets
remain reported. No deployment/remote update or account migration performed.

Reviewed full diff versus starting HEAD and all six new task files. Changes:
base template; site/site-pages CSS; theme asset selection; four selected HTML
sources and About/Contacts metadata; scoped service/command; five substantive
tests; spec/plan/trace. Ten modified tracked files and six new task files.
No curriculum source changed in this turn: the already committed PDF paragraph
was only published through its normal service. Foreign untracked work retained.
HEAD is still `9ef93f90767b6639a0ebf3c23aa7bc9d288456d3`, staged diff empty.
No commit, branch, PR, push, merge or deploy. Implementation remains for the
owner's review; human acceptance is pending and plan remains active.
