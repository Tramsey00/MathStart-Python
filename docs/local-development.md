# Local target runtime

Основной checkout — корень репозитория. Разработка — в отдельной ветке
от проверенного main без `codex/`, по [AGENTS](../AGENTS.md). Docker uses the canonical
deploy/compose.yaml and images built from the accepted main commit. Local private
settings and the instance README live in ignored var/local/. There is no dependency
on migration-execution, tmp, a historical checkout, or Django.

From the root in PowerShell:

```powershell
./scripts/local.ps1 start
./scripts/local.ps1 status
./scripts/local.ps1 logs
./scripts/local.ps1 stop
```

Stop retains data. The script neither removes volumes nor restarts Docker/WSL.
The existing local instance uses http://127.0.0.1:8121/, /account/ and /admin/.
Its operator is acceptance_admin; obtain the password locally with
`notepad ./var/local/private/operator.env`. Do not paste private files or cookies.
The instance keeps the PostgreSQL/public volumes from manual acceptance; their
historical names do not select old source code. Use the instance README for exact
image revisions and storage identities.

A clean clone has no private settings or prepared data. Follow
[release installation](../deploy/RELEASE.md) with new explicitly owned volumes,
dedicated roles/keys, schema preview/apply/check, initial operator, immutable
prepare/build and ordinary publication plan/publish. Do not attach another writer
or reset an existing database to obtain an empty installation. Before replacing
images, retain a tested database backup and check compatibility; see
[recovery](../deploy/RECOVERY.md).

Optional host tools use Python3.12 and the existing root requirements.lock;
frontend tooling uses its existing package-lock. На аудите20.10.2026 указанный прежде var/local/venv/Scripts/python.exe не обнаружен; наличие
подготовленного host venv нужно проверять, а не считать обязательным фактом.
Новая target среда создаётся из locks без Django/DRF. Comparative QA prepares the separately
pinned [oracle](legacy-oracle.md) only when required. Full managed QA is described
in [target testing](target-runtime.md); ordinary local start does not run it.
