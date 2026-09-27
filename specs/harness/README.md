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

Три R04 check ID (`repo-baseline`, `harness-unit`, `harness-cli-smoke`) сопоставлены фиксированным argv-командам; произвольный shell не исполняется. Обычный `python scripts/verify_repo.py` и CI запускают 8 checks в 5 группах,
включая `harness`. Внутренний `repo-baseline` использует
`python scripts/verify_repo.py --exclude-group harness` (7 checks в 4 группах),
а `harness-unit` отдельно запускает Harness suite. Это исключает рекурсию.
CLI dry-run smoke использует fixture и работает независимо от branch checkout;
реальная команда MS6-R04 требует ветку из manifest. Подробности общей проверки находятся в [verification skill](../../skills/verification/SKILL.md).

## Граница этапа

R04 `read_file` и `write_fixture` — ограниченные basic tools для FakeAdapter, не production Tool Registry. R05 добавляет Context Layer и typed tools; R06 — policy, hooks, sandbox и trace enforcement. Непрозрачный внешний CLI subprocess без перехвата tool calls не является enforcement-capable. Текущий R04 не подтверждает G1.

## Deadline и MESSAGE

Runner блокирует несовместимый adapter protocol до start. MESSAGE сохраняется
как промежуточный output и продолжает сессию через `continue_after_message`;
он не означает PASS. Все adapter calls учитывают turn budget.

Wall-time проверяется до и после adapter calls, до и после tool handler,
перед verification и перед публикацией READY_FOR_REVIEW. Checks используют
remaining timeout. После expiry новый model/tool/check action не начинается;
RunResult сохраняется как BUDGET_EXCEEDED, exit 4. Blocking adapter/tool calls,
которые уже начались, не прерываются на уровне ОС в R04.

PR #10 после REQUEST_CHANGES требует повторного human review. Human gate PENDING;
актуальные test counts и fixture run ID находятся в [trace](../../docs/agent-traces/MS6-R04.md).


## Committed publication для READY

Поддерживаемые readers — `harness status` и общий загрузчик RunResult — считают
READY_FOR_REVIEW опубликованным только при валидном sidecar
`var/harness/runs/<run-id>/result.ready-commit.json`. Сам файл result.json со
статусом READY без такого receipt является **uncommitted**. Ручное чтение raw
файла вне Harness API не входит в этот reader contract.

Writer выполняет следующий протокол:

1. Формирует и schema-валидирует RunResult, записывает READY в result.staged.json.
2. Проверяет deadline после staging write. При expiry записывает только
   BUDGET_EXCEEDED / exit 4, обновляет обе wall-time metrics и не создаёт receipt.
3. Выполняет atomic replace staging -> result.json. Сразу после возврата replace
   снимает `post_replace_now = time.monotonic()`.
4. Если post_replace_now >= deadline, READY остаётся uncommitted. Runner
   понижает его до BUDGET_EXCEEDED / exit 4, обновляет wall-time metrics,
   verification FAIL и next_gate null, оставляет один WALL_TIME_EXCEEDED,
   повторно валидирует и записывает failure. READY receipt не создаётся.
5. Если post_replace_now < deadline, создаёт receipt через временный файл и
   atomic replace. Только успешное завершение этого шага разрешает execute
   вернуть READY_FOR_REVIEW / exit 0.

Внутренний receipt v1 валидируется общим helper
`harness/contracts/publication.py`; JSON schema RunResult v1 не меняется.
Receipt содержит:

| Поле | Значение / правило |
| --- | --- |
| schema_version | `harness-ready-commit-v1` |
| run_id | Равен run_id canonical RunResult; status также сверяет запрошенный run ID |
| result_sha256 | SHA-256 точных bytes canonical result.json, 64 lowercase hex characters |
| published_monotonic | Конечное числовое значение часов, снятое сразу ПОСЛЕ canonical replace |
| deadline_monotonic | Конечное числовое значение deadline того же запуска |
| status | `READY_FOR_REVIEW` |

Обязательно published_monotonic < deadline_monotonic. Запись receipt может
закончиться после deadline: она подтверждает уже состоявшийся своевременный
canonical replace. Reader проверяет сохранённые значения, а не текущие часы.
Canonical JSON разбирается и проверяется по одному снимку bytes; его SHA-256
сверяется с receipt. Временный файл receipt не считается commit.

Если receipt отсутствует, повреждён, имеет неподдерживаемую версию, неверный
run_id/status/digest или не подтверждает своевременный replace, status возвращает
BLOCKED_CONFIGURATION / exit 2 с диагностикой UNCOMMITTED_RESULT и не показывает
READY_FOR_REVIEW. Это относится и к историческим READY без receipt; receipt
не достраивается задним числом. Для non-READY чтение и exit codes не меняются.

При ошибке создания receipt execute возвращает BLOCKED_CONFIGURATION / exit 2,
verification FAIL, next_gate null и blocker READY_COMMIT_FAILED. Runner пытается
сохранить этот диагностический result. Если и эта запись недоступна, возвращает
non-success с RESULT_PERSISTENCE_FAILED; оставшийся raw READY без receipt всё
равно блокируется reader. Crash после canonical replace до receipt также
оставляет uncommitted result и не может дать успешный status.

Run workspace принадлежит одному writer и имеет уникальный run ID. Receipt —
внутреннее свидетельство публикации, отдельное от artifacts RunResult; это
исключает циклическую зависимость digest. Протокол относится к процессному crash
и reader visibility; OS-level preemption файловых вызовов не добавляется.
Human acceptance этого R04 contract остаётся PENDING.
