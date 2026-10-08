# R02 verification reproduction

Use this task worktree and a new baseline venv with requirements.lock installed
using --no-deps, followed by pip check. The committed pure contract suite uses
synthetic settings and never opens a DB connection:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_migration_r02_contract.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_r02a_contract.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_r03a_contract.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_i02_*.py' -v
```

For the recorded baseline DB checks, use only the disposable container
ms7-mig-r02-pg-20261008, host127.0.0.1/port55439,
DJANGO_DB_NAME=ms6_v01_smoke_ms7_mig_r02_20261008,
DJANGO_DB_TEST_NAME=test_ms7_mig_r02_20261008, DJANGO_DB_BACKEND=postgresql,
DJANGO_DB_USER=mathstart_r02; inject disposable password/secret via environment,
DJANGO_DEBUG=False, DJANGO_RUNTIME_ROOT=<worktree>/var/r02-runtime.
Never inherit working .env or point these commands at the working DB.

```powershell
# Only on an empty disposable DB: smoke refuses nonempty storage.
.\.venv\Scripts\python.exe scripts/fresh_install_smoke.py --disposable
.\.venv\Scripts\python.exe scripts/verify_repo.py
.\.venv\Scripts\python.exe scripts/version_report.py
# Metadata/probes are readonly; scripts assert the specific disposable port/name.
.\.venv\Scripts\python.exe docs/acceptance/MS7-MIG-R02/tools/schema_mapping.py .
.\.venv\Scripts\python.exe docs/acceptance/MS7-MIG-R02/tools/route_probes.py .
```

The last two commands regenerate snapshot artifacts: run in a scratch checkout
when auditing an approved digest. Schema query starts REPEATABLE READ READ ONLY,
endsROLLBACK; HTTP probes assert no domain INSERT/UPDATE/DELETE. No target
implementation is exercised. Frozen history uses exact Git blob digests;
new contract-digests uses the explicitly LF-written new files. Existing
integration workflow runs baseline+R02A+R03A; R02 standalone20 command is local
evidence and a future R03 CI handoff, not falsely reported as an added CI stage.


## Review amendment B01–B07/N01

Use the same isolated environment above (PG55439, reserved DB/runtime), never
the working database. Real observations command enforces the disposable port
and DB name and runs SET TRANSACTION READ ONLY:

```powershell
.venv/Scripts/python.exe docs/acceptance/MS7-MIG-R02/tools/review_baseline.py .
.venv/Scripts/python.exe -m unittest discover -s tests -p "test_migration_r02_*.py" -v
.venv/Scripts/python.exe scripts/verify_repo.py
.venv/Scripts/python.exe -m unittest discover -s tests -p test_r02a_contract.py -v
.venv/Scripts/python.exe -m unittest discover -s tests -p test_r03a_contract.py -v
.venv/Scripts/python.exe -m unittest discover -s tests -p "test_i02_*.py" -v
.venv/Scripts/python.exe scripts/version_report.py
.venv/Scripts/python.exe -m pip check
```

Observed local combined suite31 PASS; full8/8, R02A30/R03A41/I027 PASS.
Baseline snapshot outputs are observations, not target runtime fixtures. Running
the collector again changes generated observation files (real timestamps/HEAD
response lengths may vary); do not overwrite published review evidence without
recording a new observation round. Final containing HEAD/CI/check-out SHA are
external in PR48; unchanged baseline CI does not run the new standalone suite.

## Protocol round09.10.2026

Use the same isolated PG55439 environment and commands above; standalone glob
now runs63 tests, including32 new abstract protocol cases. It neither connects
to target services nor proves runtime concurrency/crypto. The full verify run
used the default test DB test_ms6_v01_smoke_ms7_mig_r02_20261008 (observed), not
the ignored DJANGO_TEST_DB_NAME setting. To explicitly name a test DB use the
repository-supported DJANGO_DB_TEST_NAME. Never target the working database.
Use protocol-*.log under ignored var/r02-qa; hashes/results in verification.json.
Historical readonly HTTP/catalogue snapshots are reused; do not overwrite them.
