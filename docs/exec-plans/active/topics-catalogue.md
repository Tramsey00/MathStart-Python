# EXEC PLAN: Topics catalogue

- Status: Active
- Created: 2026-10-04
- Human gate: repository owner, pending final review
- Spec: `specs/ui/topics-catalogue.md`
- Trace: `docs/agent-traces/topics-catalogue.md`

## Baseline and scope

Branch `fix/topics-catalog`, HEAD `150e569b51a2ef84d2d17a25c675e364c808d2fc`.
Tracked tree initially clean. Existing untracked MS7-AUDIT, MS7-G0Candidate and
MS7-PREG0 plans/traces, `output/` and `tmp/` belong to other work and are preserved.
Read AGENTS, PRODUCT, relevant ARCHITECTURE, ADR-0001, docs/architecture,
verification skill, I02 spec/plan, current templates/views/bootstrap/tests/migration.

Only Content catalogue, removal of two support pages, navigation, PDF link,
publication, relevant tests and task records are in scope. No schema, domain,
dependency, CI, deploy, account, exercise or lesson-design changes. No agents,
commits, branch creation, PRs or updates to other task records.

## Steps

1. Implement GET catalogue with database-derived options, Unicode search,
   scoped styles and single heading/content container.
2. Retire exactly two static pages through bootstrap, direct redirects and
   relocate PDF link/metadata; preserve records and publication safeguards.
3. Verify focused tests, fresh/repeated bootstrap and upgrade on isolated DBs;
   run mandatory verify_repo and available browser comparisons.
4. Inspect full diff, record actual environment/results, provide exact local
   update commands; leave this plan active for human acceptance.

## Verification and risks

Use `.venv312/Scripts/python.exe` (3.12.10). PostgreSQL connection read check
succeeds (160015); `.venv` is older Python 3.10.11, not the target environment.
Do not initialize working DB. Use a new disposable database/runtime for bootstrap.
Run focused tests on PostgreSQL and SQLite; do not present SQLite as PostgreSQL
evidence. Browser tool initially fails to start due to Windows sandbox ACL setup;
record actual visual coverage separately from template assertions.

## Completion checklist

- [x] Implementation and focused tests
- [x] Baseline verification and diff check
- [x] Visual results/limitations recorded
- [x] Final review/update commands available
- [ ] Human acceptance (required; not assumed)

## Apply to the existing local database after review

Run in a normal PowerShell with the project's intended `.env` configuration,
without the agent's disposable `DJANGO_DB_NAME` / `DJANGO_RUNTIME_ROOT` overrides:

```powershell
Set-Location C:\Projects\MathStart-Python
.\.venv312\Scripts\python.exe scripts/check_database.py
.\.venv312\Scripts\python.exe manage.py bootstrap_site --dry-run
.\.venv312\Scripts\python.exe manage.py bootstrap_site
.\.venv312\Scripts\python.exe manage.py collectstatic --noinput
.\.venv312\Scripts\python.exe scripts/verify_repo.py
```

Run each command only after the preceding command succeeds. There is no schema
change and no new migration to apply. `--dry-run` executes SQL in a rolled-back
transaction, not a read-only audit. Standard bootstrap synchronizes repository
sources and retains lesson conflict protection; investigate any conflict instead
of bypassing it. It now explicitly unpublishes only `materialy` and `pamyatki`.
No other absent source is inferred to be retired. Existing retired rows remain;
fresh bootstrap never creates them. Repeated application is verified.

Expected redirects (all direct HTTP 301): `/materialy/` and
`/mathstart/materialy/` → `/karta-sajta/`; `/pamyatki/` and `/mathstart/pamyatki/`
→ `/bazovye-svojstva-stepenej-s-naturalnym-pokazatelem/`. PDF URL is unchanged.
Restart an already running local Django process after application if it has
cached old Python/templates. Working database application remains user-controlled.

## Verification outcome

Final `verify_repo.py`: PASS 8/8 (85 Django tests, 18 R03 tests, 73 Harness tests).
Fresh PostgreSQL smoke and actual original-source upgrade/dry-run/repeat pass.
Focused PostgreSQL: 12 tests; SQLite compatibility: 7 tests. Edge browser flows
pass at 360/768/1440 including no-JS and browser Back. Final diff check passes.
See trace for initial environment failures and their corrections. Task remains
active solely for final human acceptance; no working-DB update or publication.
