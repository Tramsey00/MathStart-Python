# MathStart Harness R04: запуск и границы

R04 даёт bootstrap CLI runner, версионированные TaskManifest/RunResult, заменяемый ModelAdapter protocol и детерминированный FakeAdapter. Это локальный исполняемый каркас для проверки workflow; он пока не доказывает G1.

## Подготовка

Целевая версия Python — 3.12+. Из корня репозитория в PowerShell для новой установки:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python --version
```

Для `repo-baseline` требуется также подготовленная локальная база и контент по основному [README](../../README.md). Текущий локальный `.venv` может работать на 3.10.11; `doctor` тогда сообщает `READY_WITH_WARNINGS`, что не заменяет проверку на целевой 3.12+.

## Команды R04

```powershell
python -m harness doctor
python -m harness run MS6-R04 --mode dry-run
python -m harness run MS6-R04 --mode execute
python -m harness status <run-id>
```

`dry-run` проверяет конфигурацию без вызова model adapter и без изменения продуктовых файлов. `execute` по умолчанию использует FakeAdapter: тот выполняет фиксированный test tool loop, после чего runner запускает все `required_checks`. `FINISHED` сам по себе не означает успех.

| Exit code | Статус |
| ---: | --- |
| 0 | `READY_FOR_REVIEW` |
| 1 | `FAIL` |
| 2 | `BLOCKED_CONFIGURATION` |
| 3 | `NEEDS_HUMAN` |
| 4 | `INTERRUPTED` или `BUDGET_EXCEEDED` |

`READY_FOR_REVIEW` означает успешную автоматическую verification, а не merge или human acceptance.

## Файлы и evidence

- Task manifests: `harness/tasks/`.
- Schemas и Adapter Protocol v1: `specs/harness/`.
- Локальные результаты: `var/harness/runs/<run-id>/result.json`; там же initial/final Git evidence, events и ограниченные `checks/*.stdout.txt` / `*.stderr.txt`.
- `var/harness/` — локальное runtime state, не история runs для коммита.

Три R04 check ID (`repo-baseline`, `harness-unit`, `harness-cli-smoke`) сопоставлены фиксированным argv-командам; произвольный shell не исполняется. `repo-baseline` использует `scripts/verify_repo.py`. Подробности общей проверки находятся в [verification skill](../../skills/verification/SKILL.md).

## Граница этапа

R04 `read_file` и `write_fixture` — ограниченные basic tools для FakeAdapter, не production Tool Registry. R05 добавляет Context Layer и typed tools; R06 — policy, hooks, sandbox и trace enforcement. Непрозрачный внешний CLI subprocess без перехвата tool calls не является enforcement-capable. Текущий R04 не подтверждает G1.
