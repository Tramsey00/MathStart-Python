# V01 → Ruslan / R03 target CI handoff v5 — PENDING

Reviewed implementation: `1f97d762c4089efb2e4ef6d8c7ebe0bdcbe161f4`.
PR: [#51](https://github.com/Tramsey00/MathStart-Python/pull/51), branch `ms7-mig-v01-schema`.
Accepted input: `8d958aeeb17da46839722441425ccbb5889e2ab7`.
This supersedes the unapplied [v4 proposal](r03-ci-handoff-v4.md) without changing it.
No root workflow was edited or applied. R03 owns workflow integration, triggers,
service lifecycle, artifact retention and the actual GitHub run.

The [current green legacy run](https://github.com/Tramsey00/MathStart-Python/actions/runs/38054413732)
belongs to this implementation HEAD and installs root `requirements.lock` only.
It verifies Django migrations/bootstrap and legacy tests, not target SQLAlchemy/
Alembic fresh or upgrade profiles. Keep that interpreter, job and coverage intact.

Create a separate target job with Python 3.12 and its own disposable
`postgres:16-bookworm` service; publish port `55441:5432`, wait for service health.
Use synthetic CI-only user/password and a clean `postgres` admin database.
No production/shared database, existing local service, credential secret, dump or
persisted volume may be connected. The job/service must be owned by this run and
destroyed afterwards; tests create and remove only their marked databases.
The reserved endpoint check alone is not proof of ownership: R03 must configure
the dedicated service, confirm server major version 16 and ensure cleanup even
on failure. No container/DB is started by this evidence task.

Run the job on the **actual exact PR candidate HEAD**. Before publication this is
the implementation SHA above. A future evidence commit has no SHA yet. Once
published, separately record its actual PR HEAD and rerun legacy and target CI
there. For pull_request checkout, explicitly checkout the PR head SHA, or record
the merge-checkout SHA separately and also obtain an exact-head target run.
Do not substitute an accepted input SHA for a checked implementation.

Linux job commands after R03 creates its owned service (synthetic password shown):

```bash
set -euo pipefail
python -m venv var/v01-target-ci
TARGET_PY=var/v01-target-ci/bin/python
"$TARGET_PY" -m pip install --no-deps -r backend/requirements-test.lock
"$TARGET_PY" -m pip check
export MATHSTART_V01_EXPECTED_HEAD="$(git rev-parse HEAD)"
export MATHSTART_V01_DISPOSABLE_ACK=OWNED_DISPOSABLE_POSTGRES_16
export MATHSTART_V01_TEST_ADMIN_URL='postgresql+psycopg://mathstart_v01_ci:disposable-v01-ci-only@127.0.0.1:55441/postgres'
export MATHSTART_V01_EVIDENCE_DIR="$PWD/var/v01-target-evidence-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
"$TARGET_PY" -c 'import os; import sqlalchemy as sa; e=sa.create_engine(os.environ["MATHSTART_V01_TEST_ADMIN_URL"]); c=e.connect(); assert int(c.exec_driver_sql("SHOW server_version_num").scalar_one())//10000 == 16; c.close(); e.dispose()'
"$TARGET_PY" docs/acceptance/MS7-MIG-V01/run-target-ci-v5.py
```

R03 must compare `MATHSTART_V01_EXPECTED_HEAD` to the PR API head SHA before the
commands; `git rev-parse HEAD` alone does not prove correspondence to the PR.
`set -euo pipefail` makes installation, pip check, version check and suite failure
fail the step; if logs are piped through `tee`, preserve pipefail. Keep exit codes
in evidence. Do not use `continue-on-error`, `|| true`, or skip-based success.
On PowerShell use `var/v01-target-ci/Scripts/python.exe` and explicitly check
`$LASTEXITCODE` after every external command, throwing on any nonzero result.

The [proposed runner](run-target-ci-v5.py) explicitly loads the same modules as:

```text
python -m unittest backend.tests.test_unit backend.tests.test_postgres backend.tests.test_remediation -v
```

It requires **34 unique collected and executed tests: 11 unit + 23 PostgreSQL**,
zero errors/failures/skips/expected failures, and returns nonzero otherwise.
It refuses absent URLs, other endpoints, missing disposable acknowledgement,
wrong candidate HEAD, or backend changes after the reviewed implementation.
The plain unittest command alone is insufficient for CI acceptance because the
existing fixtures skip PostgreSQL tests when the admin URL is absent.

Required cases are enumerated in [target-ci-cases-v5.json](target-ci-cases-v5.json).
Coverage includes fresh twice in different databases; upgrade A/B/C with data,
defaults, Grade epoch and sequence preservation; constraints/deferred FK/JSON
NULL/PROTECT; rollback injection and sequence disconnect retry; schema drift,
unknown/malformed tracking and forbidden stamp; B01 three BIGINT PK with INTEGER
neighboring FK; exact CHECK canonicalization/truth table and visible drift;
F1 real-Django timestamp parity; F2 real two-session ordered-lock/delete races;
F3 tracking and revision-graph controls. Do not weaken those assertions.

Save exact HEAD/tree, Python/dependency/PostgreSQL versions, locked installation
and pip check logs, all 34 test IDs/results and exit codes, diagnostics and final
cleanup record as CI artifacts; append the real run URL to a new versioned V01
record. Preserve previous FAIL and local/self-check records. All 23 PostgreSQL
cases must execute; a PASS with skips does not close this handoff.

v5 runner guards were checked without DB access; the complete runner has **not**
been executed in Linux/GitHub or against PostgreSQL during this evidence task.
R03 integration and target CI are **PENDING**. Independent Ruslan Task Approval
is **PENDING**; V01 remains **INCOMPLETE** and cannot be merged/accepted yet.
