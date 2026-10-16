# Состояние единого выполнения миграции

## 1. Текущее состояние пакета

- Package: PREPARED_NOT_STARTED.
- Execution: NOT_STARTED; подготовлены только инструкции, миграция не запускалась.
- Process authority: пользователь поручил подготовить единое выполнение всех
  оставшихся задач, без персональных очередей/сроков, с нуля для V04/I02.
- Final acceptance: HUMAN_PENDING.
- Execution checkout / current candidate / package import commit: не назначены.
- Source snapshot observed: 2026-10-16, Europe/Moscow. Это дата наблюдения,
  не дедлайн; при старте повторно проверить GitHub и не доверять stale snapshot.

## 2. Проверенные исходные refs

Repository: <https://github.com/Tramsey00/MathStart-Python>.

| Назначение | Ref / полный SHA |
| --- | --- |
| Immutable MIG_BASE_SHA; remote main при подготовке | `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7` |
| Принятый integration `ms7-mig-react-fastapi` | `a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6` |
| Integration tree по существующему receipt | `74c3014516ec3a2110d2cfec13c8e7afb8ae5024` |
| R03 draft `ms7-mig-r03-verification` | `fb39647beb983a4f488ad82d4984d3f96e87b9a8` |
| Historical I01 candidate | `150279e6ca7f1c82a6f23d8899e50992cf358f55` |
| Historical V01 candidate | `393d98890649c6c7c47908424ba0d076b5b5e56e` |
| Historical V02 candidate | `8256cbf4b38e97fc1169fea85f2d558950543be8` |

История integration: R01 records `c133f920…` -> R02 `8d958aee…` ->
V01 `4a1b8b05…` -> I01 `0c03197e…` -> V02 `a359b0bf…`.
MIG_BASE_SHA не заменять новым integration/candidate SHA.

Источники: [integration](https://github.com/Tramsey00/MathStart-Python/tree/ms7-mig-react-fastapi),
[PR49](https://github.com/Tramsey00/MathStart-Python/pull/49),
[PR53](https://github.com/Tramsey00/MathStart-Python/pull/53).

## 3. Локальная подготовка и bootstrap

Пакет подготовлен в `C:/Projects/MathStart-Python`, локальный `main` на
`8c11edadc8debc81432d1db1145feac504f09061`. Это не execution base.
До подготовки уже существовали:

```text
 M AGENTS.md
?? docs/agent-traces/local-runtime-recovery-20261007.md
?? output/
?? tmp/
```

Пользовательский `AGENTS.md` перед подготовкой:
SHA256 `b960506c0ea0e64ae6544875d5045d4de443293310246d163ccf0628a36e00e6`.
Не переносить этот dirty файл в migration checkout автоматически.

Существующие worktrees R03 и старых verification candidates обнаружены;
не использовать их как свободные рабочие каталоги. Для нового execution
подготовить отдельный checkout и выполнить selective package transfer по AGENT.
Никакие ветки/commits/PR при подготовке пакета не создавались и не изменялись.

Локальные `.venv` и `.venv312` при подготовке не запускаются: отсутствуют
интерпретаторы, на которые указывают их launchers. `py -0p` сообщает, что
установленных Python не найдено. Это environment observation, не свойство
GitHub target. При execution заново проверить инструменты и создать scoped
совместимое окружение; старые venv не считать пригодными по наличию каталога.

## 4. Task ledger — исходная таблица

Execution status и formal status — разные поля. Старые acceptance сохраняются;
новые task rows переходят TODO -> IN_PROGRESS -> IMPLEMENTED -> REVIEW_PENDING
-> TECHNICALLY_VERIFIED. BLOCKED содержит конкретную внешнюю причину, а не
отсутствие человека из прежней очереди. Candidate integration SHA записывается
отдельно; formal acceptance новых задач до решения пользователя HUMAN_PENDING.

| Task | Issue | Execution status | Formal status / source |
| --- | --- | --- | --- |
| MS7-MIG-R01 | #28 | BASELINE_ACCEPTED | Historical accepted, PR46/47 |
| MS7-MIG-R02 | #29 | BASELINE_ACCEPTED | Historical accepted, PR48 |
| MS7-MIG-R03 | #30 | PARTIAL_INTAKE_REQUIRED | Draft PR49, incomplete |
| MS7-MIG-R04 | #31 | TODO | HUMAN_PENDING |
| MS7-MIG-R05 | #32 | TODO | HUMAN_PENDING |
| MS7-MIG-R06 | #33 | TODO | HUMAN_PENDING |
| MS7-MIG-V01 | #34 | BASELINE_ACCEPTED | Historical accepted, PR51 |
| MS7-MIG-V02 | #35 | BASELINE_ACCEPTED | Historical accepted, PR53 |
| MS7-MIG-V03 | #36 | TODO | HUMAN_PENDING |
| MS7-MIG-V04 | #37 | TODO_FROM_ZERO | HUMAN_PENDING |
| MS7-MIG-V05 | #38 | TODO | HUMAN_PENDING |
| MS7-MIG-V06 | #39 | TODO | HUMAN_PENDING |
| MS7-MIG-I01 | #40 | BASELINE_ACCEPTED | Historical accepted, PR50 |
| MS7-MIG-I02 | #41 | TODO_FROM_ZERO | HUMAN_PENDING |
| MS7-MIG-I03 | #42 | TODO | HUMAN_PENDING |
| MS7-MIG-I04 | #43 | TODO | HUMAN_PENDING |
| MS7-MIG-I05 | #44 | TODO | HUMAN_PENDING |
| MS7-MIG-I06 | #45 | TODO | HUMAN_PENDING |

Прежний локальный I02 не является dependency нового исполнения по решению
пользователя. Исходные reviewed V02 interfaces обязательны независимо от этого.

## 5. Известные проверки и gaps исходного состояния

- [R03 общий run38811690819](https://github.com/Tramsey00/MathStart-Python/actions/runs/38811690819):
  verify/pure SUCCESS, target FAILURE на prerequisite executable handoff;
  последующие target steps SKIPPED. Это исторический CI read, не новый local run.
- [V01 run38811690821](https://github.com/Tramsey00/MathStart-Python/actions/runs/38811690821)
  и [frontend run38811690796](https://github.com/Tramsey00/MathStart-Python/actions/runs/38811690796)
  SUCCESS; отдельные suites не принимают полный target.
- В R03 `specs/migration/r03-v1/runtime-commands.json` исходно `commands={}`,
  status pending. Нужно создать реальные interfaces и проверить их.
- На accepted integration в `frontend/package.json` отсутствует `test:e2e`.
- H-BUILD-INPUTS ещё не реализован в новом execution: требуется V04 -> I02.
- Open follow-ups: R01 visual F01–F04; I01 fixture overlap Issue52;
  I01 query-validation P3; V01 helper follow-up по исходному record.

## 6. Источники R05

Полное исходное product ТЗ v7.1 доступно при подготовке:
`C:/Users/Tramsey/Desktop/MathStart_Technical_Specification_v7.1_SECTION20_PARALLEL_DEADLINES_2026-10-01.pdf`.
SHA256 проверен:
`e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd`.

Canonical migration ТЗ находится в migration-ветке по пути из AGENT.
Его source hash: `c5a554e3911bdb43db28d67fd02d26e38d50b2820e1154a272d89ecb44b1faae`.
Если доступ к исходному PDF пропадёт, сначала искать repository source с тем же
подтверждённым содержимым; иначе запросить конкретный источник, продолжая
независимые задачи. Не восстанавливать полное ТЗ по пересказу.

## 7. Журнал выполнения — пока пуст

При запуске координатор ведёт эту секцию и detailed evidence отдельно.

| Slice / роль | Input SHA | Checkout / paths / DB / port | Candidate SHA | Checks / review | Status / next step |
| --- | --- | --- | --- | --- | --- |
| — | — | — | — | Ничего не выполнялось | NOT_STARTED |

Для каждого blocking finding: ID, task, description, reproduction/contract,
fix SHA, regression run, reviewer disposition. Для CI указать workflow/event/
actual checkout отдельно. Для долгого внешнего запуска сохранить run/session ID.
Не сохранять credentials, private reasoning или бессодержательные периодические
записи. Finished run не перезаписывается новым.

## 8. Следующий шаг

После явного исполнения [стартового поручения](MIGRATION_START.md):
прочитать пакет -> проверить live refs/worktrees -> подготовить isolated
integration checkout и перенести только пакет -> R03 intake -> runnable tooling
и baseline -> доступные V03/V04/I02/R03 slices по TASKS.

При возобновлении сначала проверить факты из журнала, затем продолжить первый
доступный незавершённый срез. Не возвращаться к этой первоначальной TODO-таблице,
если новые commits/receipts уже доказывают выполненную работу.
