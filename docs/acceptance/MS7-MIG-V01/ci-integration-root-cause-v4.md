# PR51 CI integration finding — independent root cause

Input/local HEAD `d5dc9a4e130d3901c26894aa01e30a935dac84b6`, branch
`ms7-mig-v01-schema`. The user supplies the failing
[GitHub Actions job](https://github.com/Tramsey00/MathStart-Python/actions/runs/37967496112/job/113945407346?pr=51).
The web tool could not retrieve that job's logs; its live log contents are not
claimed independently read. The exact four import failures were reproduced
locally in a fresh venv installed solely from the unchanged root lock.

## Dependency availability

`.github/workflows/ci.yml:43` and `migration-ci.yml:43` install
`requirements.lock` with `--no-deps`; that lock contains Django5.2.16 and
psycopg3.3.6 but no SQLAlchemy/Alembic. `scripts/verify_repo.py` invokes
`python manage.py test` without labels. SQLAlchemy2.0.46 and Alembic1.18.4 are
owned by V01's separate locks. Until cutover, Django remains the live runtime;
fixture tests use `backend/requirements-test.lock`, target runtime uses
`backend/requirements.lock`. No root-lock dependency drift was found.

## Python/Django discovery and import chain

Inspected installed Django5.2.16 `django/test/runner.py`: `build_suite` defaults
to labels `["."]`, then calls `self.test_loader.discover`. Inspected the actual
Python3.12.10 `Lib/unittest/loader.py`: `_find_test_path` imports every directory
with `__init__.py`, independently of the test filename pattern. This is the
documented [unittest load_tests protocol](https://docs.python.org/3.12/library/unittest.html#load-tests-protocol).

Before the fix, root discovery traversed `backend` with no package boundary:

1. `backend/models/__init__.py:2` eagerly reexports baseline metadata and registry;
   `backend/models/baseline.py:12` imports SQLAlchemy. This package is imported
   despite its name not matching `test*.py`.
2. `backend/tests/test_postgres.py:17`, `test_remediation.py:16` and
   `test_unit.py:10` import SQLAlchemy at module scope. `test_unit` also requires
   Alembic. PG skip decorators execute only after those imports; an admin URL
   or class skip cannot prevent these import-time errors.
3. unittest wraps each error as a `_FailedTest`; Django runs these as errors,
   producing a nonzero exit and therefore a failing Verify repository check.

The initial local no-target-dependency run produced all4 exact ImportErrors.
Its SQLite diagnostic also had8 existing PG skips and1 unrelated I03 browser
NETWORK_ERROR in the restricted loopback sandbox; that failure is preserved,
not used as PostgreSQL acceptance. The discovery regression introduced before
the production fix independently failed with the same4 loader errors.

## Minimal code fix and failure visibility

`backend/__init__.py` now implements standard `load_tests`. Root discovery loads
only the two dependency-independent compatibility regressions from this package
and leaves every legacy Content/Users test in place. A package with this hook
owns its recursion; unittest stops descending before importing `backend.models`.
No catch of ImportError, SkipTest, fake tests or dependency-based global skip
was added. Removing the hook makes the positive regression fail.

The separate explicit target command loads test modules directly and bypasses
the package discovery hook. Missing SQLAlchemy still causes nonzero errors for
all three named modules and direct `backend.models` import. Regression tests
prove this using a fresh subprocess/import finder, both with and without target
dependencies installed. Tests also compare root IDs with independently collected
legacy Content/Users IDs and require zero attempted target dependency imports.

No lazy proxy/reexport or model/Alembic import redesign was necessary. Public
`backend.models.metadata` and `mapper_registry` object identities, and the
owning Alembic chain `v01_0001 -> v01_0002`, were checked in the locked target
environment. All persistence/domain/lock/B01/CHECK implementations are unchanged.

The F1/F2/runtime diagnostic writers now use a fresh run output directory
instead of overwriting committed v3 results. The new legacy verification helper
requires target dependencies to be physically absent, validates root-lock
versions, and creates/removes only its own marked reserved disposable PG DB.
Root workflows remain byte-identical; proposed owner handoff v4 isolates target
CI dependencies in another venv. Detailed results are recorded separately.
