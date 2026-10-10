# V01 and legacy verification environments

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

Target test environment, separately installed:

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
