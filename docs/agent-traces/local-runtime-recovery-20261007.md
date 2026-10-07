# TRACE: Local Django runtime recovery after PR27 pull

- Date: 2026-10-07, Europe/Moscow.
- Owner: Руслан / Tramsey00; execution surface: Codex desktop.
- Starting checkout: `main`, `8c11eda` (PR27 merged).
- Request: diagnose and restore pages returning HTTP 500 after pulling main.
- Scope: apply existing accepted Django migrations and refresh local static
  files; no new migration, source-content publication, or platform migration.

## Diagnosis

Actual GET `/7-klass-algebra/` returned 500. Migration inventory showed pending
`content.0002_grade_created_at`, `users.0001_initial`, and
`users.0002_backfill_profiles`. The preceding PR27 verification had identified
missing `content_grade.created_at` in this local database. Git pull updates
repository files but does not apply database migrations or collect static.
Read the pending migrations before execution: additive Grade timestamp,
identity tables, and empty profiles for identities without profiles.

## Actions

Executed with `.venv312/Scripts/python.exe` (Python 3.12.10):

- `manage.py showmigrations --plan`: confirmed the three pending migrations.
- `manage.py migrate --noinput`: all three applied successfully, exit 0.
- `manage.py collectstatic --noinput`: exit 0; 9 files copied, 166 unmodified,
  466 post-processed.
- Requested normal dev-server autoreload by updating only the modification
  time of `config/urls.py`; file contents and Git diff remain unchanged.

After database/static update the existing server initially returned 500 for
`/account/`, while a fresh Django process returned 200. After autoreload the
running server also returned 200. This is consistent with stale server state
after the static manifest update; the server's traceback was not captured.
No bootstrap, publish, table deletion, history rewrite, Git commit/push,
or production deployment performed. This trace is the only new source-tree file.

## Verification

`scripts/verify_repo.py --group backend --group database --group content`
completed exit 0: all 5 checks PASS. Sources: 263 lessons; content quality:
279 published pages / 1137 SVG / 0 errors; site integrity: no blocking errors.
The integrity report separately lists 24 unused images, classified by the
existing checker as informational.

Actual final GET results from `http://127.0.0.1:8000`:

| Path | HTTP status |
| --- | --- |
| `/` | 200 |
| `/7-klass-algebra/` | 200 |
| `/karta-sajta/` | 200 |
| `/account/` | 200 |
| `/api/v1/grades/` | 200 |
| `/static/mathstart/css/site.css` | 200 |

The 107 Django / 18 R03 / 73 Harness tests passed during the immediately
preceding PR27 merge verification; they were not rerun for this local runtime
setup repair, which changed no application or migration code. No new canonical
full-run PASS claimed. Observed local HTTP failure resolved; no migration
program gate or independent Task Approval claimed.
