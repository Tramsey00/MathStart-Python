---
name: mathstart-t010-staff-ui
description: Выполнить MS-T010 — Применить общую систему к staff без изменения прав; только по отдельному поручению из реестра MathStart.
---

# MS-T010 — Применить общую систему к staff без изменения прав

Зависимости: MS-T009. Статус — в [реестре](../../../docs/tasks/INDEX.md).
Карточка описывает будущий результат, не выдаёт наличие прототипа за готовность.

## Результат и входы

Привести действующие staff/admin страницы к общим компонентам. Учебные задачи не должны оставлять второй устаревший глобальный SiteShell.

Прочитай [архитектуру](../../../ARCHITECTURE.md), [стандарт переноса](../../../docs/frontend/lesson-migration.md),
[UI contract](../../../docs/ux/shared-ui-contract.md) и [проверки](../../../docs/frontend/testing-policy.md).
Не перечитывай прежние ТЗ/аудиты: они не являются входом этой задачи.

## Объём работы

1. Инвентаризировать staff routes/resources до правок.
2. Подключить shell/components и scoped styles, сохранить private no-store boundary.
3. Не менять Content source-managed view-only и запреты мутаций.
4. Проверить permission denial, stale revision, validation, sensitive input и session expiry.
5. Удалить заменённые UI стили только после полного анализа потребителей.

## Приёмка

Все действующие staff resources сохраняют server permissions, read/write ограничения, revision conflicts и подтверждения; новый UI использует общий chrome без утечки данных в public artifact.

Отметь реализацию, проверки, отдельное review и human acceptance раздельно.
Выбирай проверки по области изменения; не ослабляй семантические/API/security
assertions ради нового внешнего вида. Список неисполненных пунктов и ограничения
передай явно. Результат/команды фиксируй кратко в задаче или PR; временные outputs
в var/ либо frontend/.cache/, без новых tracked audit folders и массовых captures.

## Границы

Сохрани чужой dirty tree, учебную математику и пользовательские данные. Не меняй
платформу публикации вне необходимых документированных adapters. Не трогай
protected acceptance DB. Не запускай следующую карточку автоматически. Merge,
production и provider/security решения требуют отдельного поручения человека.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
