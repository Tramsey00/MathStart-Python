# V01 and legacy verification environments

The combined backend entry point now uses a target environment installed from
`backend/tests/v04/requirements.lock` (no Django), plus an explicitly separate
`MATHSTART_LEGACY_PYTHON` environment installed from the historical root lock.
The legacy environment also needs the pinned password-oracle dependencies shown
in `.github/workflows/migration-ci.yml`. Historical combined environments below
remain evidence, rather than the normal target runtime.

For a locally owned disposable PostgreSQL16 service on127.0.0.1:55441, set
`MATHSTART_DATABASE_URL`, `MATHSTART_DISPOSABLE=1`, and the separate legacy
interpreter path, then execute from the repository root:

```text
python scripts/target_check.py backend-tests
python scripts/target_check.py fresh-install --disposable
python scripts/target_check.py upgrade-A --disposable
python scripts/target_check.py upgrade-B --disposable
python scripts/target_check.py upgrade-C --disposable
```

The entry points create and remove new marked UUID databases and real React
artifacts. They never attach the test suites to the existing application data.
Fresh runs twice, preserves repeat-bootstrap content/users, validates the full
279-page/263-lesson/29-media release and actually builds the frontend. Upgrade
commands execute the target schema CLI on populated historical fixtures and
check data, migration history, grade epoch, constraints/head and sequences.
Result receipts are under `var/target-checks/<check>-<uuid>/result.json`; failures,
empty suites or skipped tests cannot produce PASS. The backend child has a1800s
bound and its repository parent reserves1860s including cleanup. The full bootstrap
adds813 actual public probes to the existing backend/legacy/build suites; its
measured Windows duration alone exceeded the old backend timeout's spare time.
All assertions and zero-skip requirements remain enforced. The full nine-project
browser child has a7200s bound, with7500s for its parent/cleanup; ordinary
commands retain their shorter bounds. These commands do not establish final migration acceptance.

The managed entry point owns the common target database, one actual main frontend
build, target ASGI and the separate legacy comparator. It executes all16 registry
commands exactly once (moving frontend-build before its runtime consumers), then
fresh-install and all three upgrades. Backend/install suites retain their own
child databases. It requires the same locked target/legacy/Node dependencies plus
installed Playwright Chrome, Edge and Firefox; absent browsers fail.

```text
python scripts/verify_target.py --runtime-root var/target-candidate-<unique> --legacy-python <separate legacy interpreter>
```

A new runtime-root under this checkout's ignored var/ is mandatory. The supplied
PostgreSQL parent is only a connection endpoint; the command creates and removes
a new marked database. Services refuse an occupied port and clean up their owned
process trees. Nonzero/timeout/empty/skipped child outcomes remain failures. Logs
and source snapshots are under runtime-root; private fixture cookies and DSNs must
not be uploaded. `--group content` (or another explicit group) and `--allow-dirty`
produce scoped development evidence, never full target PASS. The portable
`verify_repo.py --profile target` registry is also retained for an already managed
runtime; by itself it does not start/build the common runtime.

The backend suite includes byte-for-byte legacy INDEX comparison, pure bootstrap
previews, retained retired rows/private facts, proposed-ID source registration,
real fenced bootstrap/publication/HTTP and row-version output-pin invalidation.
Historical CI receipts apply only to their recorded checkout; current new code
requires its own affected checks and final combined candidate verification.

Until cutover, Django and its historical CI install only `requirements.lock`.
V01 runtime dependencies are in `backend/requirements.lock`; migration tests
also need Django fixtures and use the complete `backend/requirements-test.lock`.
Do not add target dependencies to the root lock to make discovery work.

Python unittest discovery imports packages even when their names do not match
`test*.py`. `backend.load_tests` is the package discovery boundary: root Django
discovery loads only `backend.tests.test_discovery` and leaves all legacy tests
in place. The two compatibility regressions verify the actual Django default
discovery with target dependencies blocked, and nonzero errors for explicitly
requested target modules without those dependencies. No import errors are
caught by the hook and no SkipTest or skip decorator was added.

The public `backend.models.metadata` / `mapper_registry` exports remain eager
and require SQLAlchemy. Alembic still imports the same metadata/revision chain.

Legacy environment:

```text
python -m pip install --no-deps -r requirements.lock
python -m pip check
python manage.py test
python scripts/verify_repo.py
```

The normal commands require the configured disposable runtime prepared with
migrations/bootstrap/static files. The local repeatable absence proof creates
and removes its own marked database on the reserved localhost:55441 container:

```text
python -m backend.tests.legacy_ci_verification --disposable
```

The target PostgreSQL suites also run in the ordinary Django-free environment.
Set `MATHSTART_LEGACY_PYTHON` to the separately installed legacy interpreter;
historical fixture migration and timestamp comparisons run only in that child
environment. POSIX virtualenv invocation paths are preserved without resolving
their symlinks. Missing oracle tools fail rather than skip required cases.

```text
python -m pip install --no-deps -r backend/requirements.lock
python -m pip check
python -m unittest backend.tests.test_postgres backend.tests.test_remediation -v
python -m backend.tests.runtime_verification
```

The runtime CLI rehearsal uses the current target interpreter by default;
`MATHSTART_TARGET_PYTHON` can explicitly select another installed target-only
interpreter. It checks absence of Django both before and after every command.
The earlier fixed Windows venv location is no longer required. Set a new
`MATHSTART_V01_EVIDENCE_DIR` per run to retain receipts and failures.

The historical combined target-test environment remains supported:

```text
python -m pip install --no-deps -r backend/requirements-test.lock
python -m pip check
python -m unittest backend.tests.test_unit backend.tests.test_postgres backend.tests.test_remediation -v
```

Set `MATHSTART_V01_TEST_ADMIN_URL` to the reserved synthetic local PostgreSQL
administration endpoint `postgresql+psycopg://postgres@127.0.0.1:55441/postgres`.
The fixtures reject other endpoints and create/remove new marked databases.
CI uses its service's synthetic credentials at the same reserved host/port.
All 23 PostgreSQL methods must execute without skips for acceptance; an unset
admin URL does not establish target acceptance. The target command loads named
modules directly and does not consult the root discovery hook. Explicit
`unittest discover -s backend/tests -t .` also requires target test dependencies.

Fresh twice, upgrades A/B/C, B01, exact CHECK comparison, F1/F2/F3, constraints,
sequences and rollback are included in the explicit target suite. By default
new F1/F2 diagnostic JSON is written under ignored `var/ms7-mig-v01-evidence`.
Set `MATHSTART_V01_EVIDENCE_DIR` to a fresh run directory to retain new results
without overwriting committed historical acceptance records.

Target runtime smoke without Django uses `backend/requirements.lock` in another
venv. Historical fixture construction stays in the target-test venv. Root CI
workflows are R03-owned; the v4 acceptance handoff proposes separate target
steps/venvs while leaving the root installation unchanged.
