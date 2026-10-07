# TRACE PR27: Resolve bootstrap test merge conflict

- Date: 2026-10-07 (Europe/Moscow).
- Owner: Руслан / Tramsey00; coding surface: Codex desktop.
- PR: https://github.com/Tramsey00/MathStart-Python/pull/27
- Scope: resolve the existing PR conflict with main; no migration implementation.
- Human review and main merge: pending.

## Inputs and initial state

Read repository instructions, architecture, verification skill, bootstrap tests,
main's Grade timestamp migration/test change, and existing visual-fix records.
Starting branch `fix/topics-catalog`, HEAD
`30d48b71a23e8b446fad34d1c480e55ce4150609`; only `output/` and `tmp/`
were untracked. Fetched main at
`4df7403208312d73adaa34f00f10b025db686fe4`.

## Change and preservation checks

Merged `origin/main` into the PR branch. Git reported one conflict, at the end
of `content/test_bootstrap.py`. Preserved the branch's source/count assertions
and retirement/data-preservation test, plus main's Grade `created_at`
idempotency assertion. Removed conflict markers without dropping either test.
Main's grades/account code and the account navigation link were also retained
by the merge. No user source files, runtime data, or temporary output deleted.
No working-database migration/bootstrap/publish and no deployment performed.

## Verification

Actual environment: Python 3.12.10 (`.venv312`), Django 5.2.16,
psycopg 3.3.6, PostgreSQL server 160015, Git 2.47.0.windows.1.
The older `.venv` reports Python 3.10.11; it was not used for tests.

| Check | Observed result |
| --- | --- |
| `.venv312/Scripts/python.exe -m pip check` | PASS |
| PostgreSQL connection diagnostic | PASS with sandbox escalation; restricted attempt failed |
| `manage.py test content.test_bootstrap --noinput --verbosity 1` | PASS, 2 tests, 142.546 s, exit 0 |
| `git diff --cached --check` / unresolved index entries | PASS / none |
| `scripts/verify_repo.py` | FAIL, exit 1: 5/8 checks pass; 3 runtime content checks fail against stale local schema |
| Canonical Django / R03 / Harness suites | PASS: 107 / 18 / 73 tests respectively |

Bootstrap tests used a separate disposable PostgreSQL test database named
`test_mathstart_pr27_conflict`, destroyed by Django on completion.
The canonical runner uses a different test database,
`test_mathstart_pr27_verify`; its diagnostic log is local at
`var/pr27-conflict-verify.log` (ignored).

## Failures and acceptance

Local runtime lacks `content_grade.created_at`, introduced by the already
accepted main migration. Django system/migration consistency checks pass;
lesson source validation, content quality, and site integrity fail against
that old runtime schema. Classified as an existing local environment/schema
failure, not a conflict-resolution failure. Working DB was left unchanged.
Do not claim a passing canonical run. New PR-head CI and independent review
remain required before main merge; no Task Approval or migration gate claimed.

## Publication

Merge resolution pushed to the existing PR in commit
`239fefcad7dacafb78e642e08df6d2371b8f8427`. GitHub API subsequently reports
`mergeable: true`; CI/review status is separate (`mergeable_state: unstable`
at that observation). This trace follow-up records completed local verification;
main merge was not performed. Only existing untracked `output/` and `tmp/`
remain outside the committed changes.
