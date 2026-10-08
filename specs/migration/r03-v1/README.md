# R03 verification adapter contract v1

Status: PROPOSED / INCOMPLETE; independent review and runtime handoff pending.
Owner Tramsey00; reviewers VladimirFrolov777 /13baybars. [Issue30](https://github.com/Tramsey00/MathStart-Python/issues/30).
Accepted input `8d958aeeb17da46839722441425ccbb5889e2ab7`,
MIG_BASE_SHA `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
Authority: [migration v1.1](../MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md)§§9/17,
[R02 matrix](../r02-v1/parity-matrix-v1.json) and accepted ADR0006.

## Profiles and commands

`python scripts/verify_repo.py --profile target` runs16 named checks across
backend/database/content/tests/harness/frontend. `--group`, repeated groups,
`--exclude-group`, `--skip-tests` and `--list` preserve their selection semantics.
An empty execution fails. A partial selection never establishes full target
acceptance. `--profile pure` runs only6 pure/Harness checks; no runtime claim.
The transitional default is explicitly legacy to keep frozen ci.yml reproducible.
At final cutover R03 must switch the default through reviewed intake; until then
this increment does not satisfy the final no-Django verification requirement.

Harness keeps `repo-baseline`, `harness-unit`, `harness-cli-smoke`; repo-baseline
now explicitly selects target and excludes harness. Its15 checks cannot recursively
run Harness; standalone unit/CLI retain original identity/lifecycle/deadlines.
Fake FINISHED with missing runtime dependencies fails verification, never READY.
Historical TaskManifest/RunResult schemas, manifests and domain suites stay intact.

Use Python3.12+, an isolated venv, `pip install --no-deps -r verification.lock`
from this directory (or its full root-relative path), then `pip check`.
Product locks remain the V01/I01 owners' deliverables. No latest dependency install.

## Required semantic equivalents and owner handoff

The [command handoff](runtime-commands.json) is intentionally PENDING with no
invented backend entry points: each absent required command fails. V/I owners
provide concrete commands to R03 for review/integration; this file is R03-owned.
Set REVIEWED only after command-contract review, not to claim task acceptance.
Backend entry: `{ "script": "backend/<existing-script>.py", "args": ["..."] }`.
Only Python scripts resolving inside backend are accepted; no arbitrary shell.
The wrappers are real executable dispatchers; the domain implementations are absent.

| Key / old assertion | Required target assertion / owner |
| --- | --- |
| system / Django check | FastAPI config/startup/registered routes/security, V02 |
| migrations / makemigrations | Metadata/Alembic drift, one head, reviewed SQL/PG equivalence, V01 |
| lesson-sources | All263 sources with publication/source digest parity, V04 |
| content-quality | Unweakened HTML/SVG/math/assets checks, V02/V04 |
| site-integrity | All URL/media/catalog/redirect/SSG completeness, V02/V04/I02 |
| backend-tests / Django tests | Nonempty unskipped real PG API/services/migration/content/staff tests, V01/V02/V03/V04 |
| fresh-install | Alembic from zero, bootstrap twice without evidence overwrite, assets/build, V01/V04/I02 |
| upgrade-A/B/C | Exact schema/data/ID/FK/default/timestamp/sequence preservation for the3 specified disposable profiles, V01 |
| frontend-typecheck/tests/build/e2e | Locked `npm run typecheck/test/build/test:e2e`, I01/I02 |

Backend command runs receive `MATHSTART_CHECK_RESULT` naming a unique output
under var/target-checks. Exit0 additionally requires a JSON receipt containing
`check_id` (exact key), `status:PASS`, `evidence_class:TARGET_RUNTIME`, integer
`assertions>0`, integer `skipped:0`. lesson-sources requires at least263 assertions.
Migration/backend-tests/fresh/upgrade receipts additionally require
`database_vendor:postgresql`, integer `postgresql_major>=16`.
Counts and receipts prevent empty/skip success; independent assertion review
and real implementation evidence are still required. They do not prove parity
by themselves and model/synthetic results cannot use this evidence class.
Frontend package, lock, each script and npm must exist; missing tool is fail.
Scripts must use deterministic test execution and fail on no tests, not watch mode.

`python scripts/fresh_install_smoke.py --profile target --disposable` and
`python scripts/migration_smoke.py --disposable --source-profile A|B|C` dispatch
the owner-reviewed rehearsals, requiring `MATHSTART_DISPOSABLE=1` as a second
explicit guard. The owner implementation must also enforce DB/runtime isolation,
empty fresh DB and populated profile identity; a flag is no production authorization.
The wrapper currently fails because implementations are absent; no schema is created.

`python scripts/check_database.py --profile target` uses psycopg directly with
MATHSTART_DB_HOST/PORT/NAME/USER/PASSWORD, a read-only SELECT1/version query,
5s connection/statement bounds and15s outer bound. No credential/DSN/driver error
is printed; no SQLite fallback. These env names are the R03 diagnostic interface,
not a replacement for future backend configuration. `version_report.py --profile
target` requires backend/requirements.lock, exact installed versions and real PG.

## CI and evidence boundaries

Separate migration-ci runs task pushes, integration/main PRs and pushes. Frozen
ci.yml and its whole-file pin remain unchanged. The pure job uses only the R03
tooling lock with an explicit no-Django/DRF import-availability assertion. The
historical baseline job runs unchanged standalone R02 suite63 at accepted input
in its own detached worktree; its all-input HEAD assertion remains meaningful.
Its Django observations are historical, not target portability. Current target
pure R02 protocol32 are included separately. Remaining standalone R02 runtime
assertions need V/I equivalents; no tests are removed or silently skipped.

The target job has PG16, owner locks, fresh and upgrades A/B/C, full target registry
and frontend browser smoke. It fails on missing owners' inputs today; no job-level
skip/continue-on-error hides that blocker. Provenance records actual checkout SHA,
tree, event, run/attempt, PR head/base and tested merge parents/ref. Evidence is
uploaded even on failure. Green pure/historical jobs do not override failed target.
`ci_provenance.py` detects stale checkout and wrong merge parents; local invocation
does not count as CI. No live Product LLM or production credentials are required.

Plan stays active and Issue30 open. Accepted V02/I02 plus fresh/upgrade/content/
frontend real evidence, final current-head/merge-ref CI and independent approvals
are required before task acceptance. [Handoff](../../../docs/acceptance/MS7-MIG-R03/handoff.md)
and [trace](../../../docs/agent-traces/MS7-MIG-R03.md) record exact current limits.
