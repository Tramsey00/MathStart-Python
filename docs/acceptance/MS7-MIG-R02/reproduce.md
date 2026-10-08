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
integration workflow runs baseline+R02A+R03A; R02 standalone19 command is local
evidence and a future R03 CI handoff, not falsely reported as an added CI stage.
