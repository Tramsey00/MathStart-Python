# MS7-MIG-V01 — CI Integration Remediation Report

**CI discovery finding FIXED locally. Ready for repeated PR review; GitHub CI
and human approval pending.** The previous independent audit and all v1-v3
records remain byte-identical; this is a new continuation record.

## Actual state

Worktree `C:/Projects/MathStart-Python-V01`; branch `ms7-mig-v01-schema`;
published/input/final HEAD `d5dc9a4e130d3901c26894aa01e30a935dac84b6`.
Distinct immutable MIG_BASE_SHA `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
Input worktree clean. Changes are unstaged; no commit/push/merge/reset/clean/PR
mutation. All102 inspected input files preserved in ignored
`var/ms7-mig-v01-ci-input-v4`; existing commits/evidence retained.

## Root cause and minimal fix

The root CI lock deliberately has Django/psycopg and no SQLAlchemy/Alembic.
`scripts/verify_repo.py` invokes unlabelled `manage.py test`; Django DiscoverRunner
defaults to `.`. Python3.12 unittest imports every regular package while walking,
including packages not matching `test*.py`. `backend/models/__init__.py:2` eagerly
imports baseline SQLAlchemy mapping (`baseline.py:12`); `test_postgres.py:17`,
`test_remediation.py:16` and `test_unit.py:10` import it at module scope. Those four
imports become failing unittest test cases before PG decorators can run.
See [independent analysis](ci-integration-root-cause-v4.md) and the retained
pre-fix raw logs referenced by [verification](verification-v4.json).

`backend/__init__.py` now defines standard `load_tests`, making this package own
its root-discovery recursion. It loads only two dependency-independent
compatibility regressions; every107 existing Content/Users test remains collected.
The explicit target modules still load normally, require their locked dependencies
and return nonzero when dependencies are missing. No import exception swallowing,
global SKIP, fictitious PASS, lazy metadata proxy or settings/runner rewrite.
Public `backend.models.metadata`/`mapper_registry` identities and Alembic owning
chain `v01_0001 -> v01_0002` were verified unchanged. Root dependencies unchanged.

The regression uses the real default Django DiscoverRunner in a fresh subprocess
with SQLAlchemy/Alembic imports blocked, proves zero attempted target imports and
preserves independently collected legacy IDs. A second regression explicitly
loads all3 target modules/direct metadata package and requires their actual
ModuleNotFoundError/nonzero exit. The positive test fails before the hook fix.

## Changed files

- `backend/__init__.py`: discovery boundary, the only production-code change.
- `backend/tests/test_discovery.py`: two dependency-independent regressions.
- `backend/tests/legacy_ci_verification.py`: reproducible root-lock absence proof
  and fresh disposable PG baseline verification, with no SQLAlchemy imports.
- `backend/tests/test_remediation.py`, `runtime_verification.py`: diagnostic JSON
  uses a new run output directory rather than overwriting historical v3 evidence;
  test assertions/fixtures/production semantics unchanged.
- `backend/TESTING.md`: exact separate environment/test commands.
- V01 active plan/trace and new v4 report, evidence, manifest/delta and CI handoff.

Frozen R02, historical Django/Alembic migrations, B01/domain/lock/schema contracts,
root locks, `verify_repo`, `.github/workflows/ci.yml` and `migration-ci.yml` unchanged.
Exact paths/hashes are in [delta](continuation-delta-v4.json) and
[manifest](file-manifest-v4.json).

## Actual verification

Windows, Python3.12.10, Django5.2.16, PostgreSQL16.15, psycopg3.3.6;
target SQLAlchemy2.0.46 / Alembic1.18.4. Three independently locked environments:
root-only legacy, target-test, and target-runtime without Django.

| Check | Dependencies / exact result |
| --- | --- |
| Pre-fix root-lock SQLite diagnostic | No SQLAlchemy/Alembic; 111 tests:98 PASS/1 FAIL/4 ERROR/8 SKIP,150.558s |
| Discovery regression before fix | 1 PASS/1 FAIL/0 ERROR/0 SKIP,2.058s; same4 import errors |
| First new helper DDL setup | FAIL before tests; COMMENT quoting fixed, own DB removed, log retained |
| Discovery regressions after fix, root-only | 2 PASS/0 FAIL/0 ERROR/0 SKIP,2.145s |
| Discovery regressions after fix, target env | 2 PASS/0 FAIL/0 ERROR/0 SKIP,2.368s |
| Legacy `manage.py test --noinput -v 2` on disposable PG | No SQLAlchemy/Alembic; **109 PASS/0 FAIL/0 ERROR/0 SKIP**,174.181s |
| Exact unlabelled `manage.py test` inside unchanged verify_repo | No SQLAlchemy/Alembic; **109 PASS/0 FAIL/0 ERROR/0 SKIP**,170.744s |
| Unchanged `verify_repo` | No SQLAlchemy/Alembic; **8 PASS/0 FAIL** |
| R03 / Harness | No SQLAlchemy/Alembic; **18/18 /73/73 PASS**,0 skips |
| R02 migration / R02A / R03A | No SQLAlchemy/Alembic; **63/63 /30/30 /41/41 PASS**,0 skips |
| Explicit V01 target suite | backend test lock with SQLAlchemy/Alembic; **34 PASS/0 FAIL/0 ERROR/0 SKIP**,68.507s |
| Target-only fresh twice/A/B/C/check CLI | backend runtime lock with SQLAlchemy/Alembic, no Django installed/imported; **10/10 exit0** |
| Exact locks/pip checks, public exports/Alembic graph | PASS |
| Frozen/history/CI/old evidence preservation; scope/AST/JSON/hash/diff | PASS |
| Proposed R03 patch applicability | PASS; not applied |

Legacy109 =107 existing tests +2 discovery regressions. Target34 =11 explicit
SQLite unit compatibility checks +23 PostgreSQL methods; all PG tests ran.
Pre-fix diagnostic's additional I03 NETWORK_ERROR was a restricted loopback
environment failure, and8 skips were existing PostgreSQL tests under SQLite.
Both full PG baseline runs exercised those tests/browser flow without skips or
modifications. No failed run was relabelled as passing.

Fresh twice and upgrades A/B/C preserve IDs/FKs, hashes/roles/superuser flags,
data, Grade epoch/microseconds and Django migration history. B01 actual generated
join int8 IDs and adjacent integer FKs pass. Exact CHECK canonicalization/42-case
comparison and drift refusal pass. F1 all7 fields match real Django and explicit
historical import preserves dates; F2 forced crossed references yield
COMMIT+COMMIT/no40P01 under unchanged lock order; F3 strict proof refuses damaged
tracking/head states. Constraints/defaults/timestamps/sequences/no-rewind,
backfill twice, rollback and pre-COMMIT connection-loss regressions pass.

Migrate/bootstrap twice/collectstatic and all10 legacy helper commands exit0.
Only new marked databases in the validated reserved local tmpfs container were
used. Cleanup read found zero test DBs; own container stopped, other services
untouched. Exact raw-log hashes/commands are in verification-v4.json.

## CI owner handoff, limits and readiness

Repairing historical Verify repository needs no CI modification. Separate
explicit target coverage needs Руслан/R03's integration of
[handoff v4](r03-ci-handoff-v4.md), superseding unapplied v3: keep root installation,
add reserved service mapping and a separate target-test venv/step for main PR and
integration workflows. Proposal prepared and applicability checked, **not applied**.
No owner message sent. Actual GitHub Actions after this fix is not run/claimed.

NOT VERIFIED: Linux/GitHub CI rerun, proposed target steps on CI, independent
PR re-review/Task Approval, live original job logs (web retrieval unavailable),
production/cutover/deployed data, AFTER-COMMIT lost acknowledgement, exhaustive
lifecycle/lock scaling. Local exact import failures were independently reproduced.

No new code blocker in tested scope. Ready for repeated PR review; owner target
CI integration, actual green CI and human approval remain open gates. No domain,
schema, accepted lock protocol or ownership contradiction was introduced.
