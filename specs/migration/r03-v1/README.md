# R03 verification adapter contract v1

Status: PROPOSED / INCOMPLETE; independent review and runtime handoff pending.
Owner Tramsey00; reviewers VladimirFrolov777 /13baybars. [Issue30](https://github.com/Tramsey00/MathStart-Python/issues/30).
Current accepted input `a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6`;
previous input `0c03197e23f69a233c0fcf8bdffa336feca20b92` and its receipts retained;
historical input `8d958aeeb17da46839722441425ccbb5889e2ab7` is preserved,
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

The [command handoff](runtime-commands.json) now has real target
entry points for all ten backend checks: system/routes/security, exact schema/head,
all263 lesson sources, full279-page filesystem integrity, live HTTP quality,
the complete backend suites in isolated databases, fresh twice with real React
artifacts and repeated bootstrap, and populated upgrade A/B/C via actual schema
CLI with retained data/history/sequence assertions. `IMPLEMENTED_PARTIAL` allows
these entries to execute while any absent entry still fails. The remaining gap
is managed combined runtime/build/browser orchestration and final verification.
Set REVIEWED only after command-contract review, not to claim task acceptance.
Backend entry: `{ "script": "backend/<existing-script>.py", "args": ["..."] }`.
Only Python scripts resolving inside backend are accepted; no arbitrary shell.
Each entry emits nonempty unskipped target receipts. Public scoped CI executes
the five read-only checks; the backend-install CI job executes backend/fresh/
upgrades against its own PostgreSQL16 service on55441. Neither job claims full
target acceptance. Actual local entry-point checks are recorded under
`docs/acceptance/migration-execution/i02-verification/`; historical failures stay
retained beside successful continuation receipts.

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

All fourteen command interfaces receive `MATHSTART_CHECK_RESULT` naming a unique output
under var/target-checks. Exit0 additionally requires a JSON receipt containing
`check_id` (exact key), `status:PASS`, `evidence_class:TARGET_RUNTIME`, integer
`assertions>0`, integer `skipped:0`. lesson-sources requires at least263 assertions.
Migration/backend-tests/fresh/upgrade receipts additionally require
`database_vendor:postgresql`, integer `postgresql_major>=16`.
Counts and receipts prevent empty/skip success; independent assertion review
and real implementation evidence are still required. They do not prove parity
by themselves and model/synthetic results cannot use this evidence class.
Each command also receives `MATHSTART_CHECK_ID` with its exact interface key.
Frontend commands must write the same nonempty structured result from actual
tool/test/build observations; exit0 with no receipt is failure. Typecheck/build
assertions describe checked source/build invariants, not browser acceptance.
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

## Accepted I01/V01 joint-input CI — 2026-10-12

Historical joint-input runs below remain pinned to0c03197. Current V02 squash
acceptance and guards now use [accepted-integration-20261015.json](accepted-integration-20261015.json)
at a359b0b, with approval8256cbf/review5538854677 retained separately:
[merge receipt and next steps](../../../docs/acceptance/MS7-MIG-R03/v02-integration-a359b0b/README.md).
Post-merge baseline38796031561 is separate from candidate V02 suites; consumer
review8256cbf/47baaa9 is source-only. R03 INCOMPLETE, full I02 not accepted.

Human receipts and merges now establish both tasks as ACCEPTED_INTEGRATION.
Separate frontend and V01 PostgreSQL jobs test the pinned combined input0c03197,
using approved source heads only as provenance references. Strict receipt/tree/
source/merge-chain/live-ref validation complements unchanged event-SHA and PR
merge-parent checks. Historical runs, captures, workflow pins and previous8d958
input remain separate. Current acceptance, retained follow-ups and actual joint
runs: [handoff](../../../docs/acceptance/MS7-MIG-R03/accepted-integration-ci-20261012.md).

## CLI/receipt handoff preparation — 2026-10-12

[Concrete owner/review checklist](../../../docs/acceptance/MS7-MIG-R03/cli-receipt-handoff-checklist.md) maps all10 backend checks,4 frontend
checks and7 baseline content commands to V02/I02/V04 deliverables and R02 parity
assertions. Accepted V01 schema/foundation evidence remains separate. The new
machine checklist is PREPARED_FOR_OWNER_REVIEW. That historical intake predated
the five concrete target entries now recorded above; remaining gaps are explicit.
Full target execution awaits accepted exact-SHA inputs and reviewed command
contracts; R03 stays INCOMPLETE until full checks and independent approvals.

## V02 published-candidate technical checks — 2026-10-15

PR53 exact implementation76d8eac / parent0c03197 / tree dbad1e8 is pinned in
v02-published-candidate.json. Published run38637910883 executes unchanged
confirmed controls1b75c6e on fresh Linux commit checkout; final task
run38642117604 verifies unchanged owner86/all40 PG cases plus separate V01
34/all23 PG,0 skips, historical contracts, full Content projection279/263 and
real isolated runtime without Django/DRF. Complete downloaded raw artifacts,
separate workflow/control/implementation/checkout revisions and digests are in
[technical packet](../../../docs/acceptance/MS7-MIG-R03/v02-review-20261015/review-packet.md).
Human V02 Task Approval is pending; no accepted input is fabricated. First task
run's incomplete hidden-cache upload is retained separately from the complete
rerun. Global R03 target still requires its reviewed command map, accepted
V02/I02 inputs and applicable V04 CLI/full combined pipeline/independent reviews;
this global prerequisite is not a new V02 card condition. R03 INCOMPLETE.

## Authorized V02 narrow successor — 2026-10-15

New v02-successor-intake.json remains NOT_READY/null for unpublished new SHA/tree.
Separate v02_successor_gate verifies direct parent76d8eac and unchanged original
BASE lineage, owner-reviewed exact diff/blobs/metadata/attributes plus preserved
controls40/73. Original publication-v3/control/input is unchanged; no blanket
descendant acceptance or automatic tree/pin replacement. Human approval5525315946
is received at predecessor76d8eac only. [Current handoff](../../../docs/acceptance/MS7-MIG-R03/v02-successor-20261015/handoff.md)
records required exact renderer contract/owner diff/current case inventory and
new-SHA suite sequence. Guard preparation CI is not successor task evidence.

## Published V02 successor8256cbf — 2026-10-15

New reviewed scope v02-successor-reviewed-8256cbf.json is independently pinned
SHA25604a47175 (5 modified +63 new files, exact metadata/patch/case IDs), separate
from unchanged original candidate/anchor/control inputs. Root workflow/control
0effadc run38784183591 SUCCESS: original v3 replay at76d8eac, successor chain/
delta at8256cbf/tree74c3014, V02118/all50 PG with original86 retained and0 skips,
separate V0134/all23 PG, contracts/Content/runtime without Django. Full clean
checkout includes helper verifier/evidence dependencies. [Current review](../../../docs/acceptance/MS7-MIG-R03/v02-successor-review-8256cbf/review-packet.md)
retains raw hashes/reconciliation and baseline/stale/global-target classifications.
Current intake is technical PASS, renewed human review pending; no approval
transfer, merge or Issue closure. Global R03 remains INCOMPLETE.
