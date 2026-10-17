# План подготовки пакета агентов миграции

- Status: PREPARED_FOR_REVIEW; baseline verification BLOCKED_ENVIRONMENT.
- Scope: только документация и стартовое поручение; implementation NOT_STARTED.
- Observation date: 2026-10-16, Europe/Moscow; календарь исполнения не задаётся.
- Human review: пользователь рассматривает подготовленный пакет и запускает
  его отдельным поручением; планы не перемещать в completed автоматически.

## Цель

Подготовить переносимый пакет, по которому одна команда агентов выполнит все
13 оставшихся migration-задач на основе пяти принятых, с отдельным ревью,
сохранением архитектуры, полным verification и возобновлением по записанному
состоянию. Основной `AGENTS.md`, код, БД, Git refs и история не изменяются
при подготовке.

## Входы и границы

Пользователь явно разрешил создать пакет в проекте, исключил реализацию сейчас,
указал существующую migration-ветку, V04/I02 с нуля, R03 continuation,
отсутствие персональных очередей/сроков и брендовых приписок в новых именах.

Прочитаны применимые repository инструкции, PRODUCT/ARCHITECTURE/ADR-0001,
verification skill/templates, migration ТЗ/ADR-0006 и принятые R02 contracts,
R03 CLI/checklist, GitHub branches/PR/reviews/CI из текущего анализа.
Полное product ТЗ v7.1 на этом этапе не анализировалось: наличие/hash проверены,
его полное чтение явно включено в будущую R05.

Нет schema, seed, API/UI, dependency или Product LLM изменений.
Не создавать SKILL/config automation и не запускать субагентов реализации:
профили ролей подключаются будущим координатором явно.

## Изменения

1. [Главная инструкция](../../../MIGRATION_AGENT.md): authority/process overlay,
   bootstrap, архитектура, Git/ownership, review, autonomy и final human boundary.
2. [Очередь](../../../MIGRATION_TASKS.md):18 task dispositions,13 remaining cards,
   formal dependency kinds, staged V04/I02 handoff и обязательные follow-ups.
3. [Проверки](../../../MIGRATION_VERIFICATION.md):14 command interfaces,
   40 parity IDs, AT-M01–12, negative coverage и evidence/review protocol.
4. [Состояние](../../../MIGRATION_STATE.md): проверенные refs, initial ledger,
   source hashes, environment limitation, resume instructions.
5. [Стартовый промпт](../../../MIGRATION_START.md) и три role profiles в
   `docs/migration-agents/`.
6. [Trace](../../agent-traces/migration-agent-preparation.md) с фактическими
   проверками и ограничениями.

## Проверки подготовки

- UTF-8, local Markdown links, trailing whitespace, balanced code fences.
- Ровно18 task ledger rows, пять accepted и13 remaining; formal H/I сравнить
  с accepted dependency-policy; полный набор40 parity IDs сравнить с source.
- Явное разделение preparation/execution, technical/formal acceptance,
  historical/input/final SHA, existing code/future implementation.
- Нет брендовой приписки в новых именах/содержимом и нет изменений `AGENTS.md`.
- `git diff --check`, scope/status inspection и hash сохранности.
- Required `python scripts/verify_repo.py` попытаться в project environment;
  unavailable interpreter классифицировать честно без установки/DB repair.

## Риски и решения

| Риск | Решение |
| --- | --- |
| Старый локальный main | Selective package transfer в isolated integration checkout |
| Конфликт старых персональных gates | Explicit user process overlay; genuine final human gate |
| Потеря R03 или повторный I02 intake | R03 controlled continuation; V04/I02 from-zero instruction |
| Цикл renderer/publication | Immutable input -> HTML output -> activation |
| Отчёт о сборке вместо приёмки | Full runtime/PG/browser matrix и отдельное review |
| Неработающее локальное Python окружение | BLOCKED_ENVIRONMENT; package-only static checks |

## Состояние сдачи

Документы подготовлены для пользовательского review. Миграция не запускалась;
техническая готовность приложения и MIG-G4 этим изменением не заявляются.
Подробные фактические результаты — в trace.
