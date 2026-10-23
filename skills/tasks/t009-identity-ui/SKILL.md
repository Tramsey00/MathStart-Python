---
name: mathstart-t009-identity-ui
description: Выполнить MS-T009 — Заменить старый интерфейс авторизации и профиля; только по отдельному поручению из реестра MathStart.
---

# MS-T009 — Заменить старый интерфейс авторизации и профиля

Зависимости: MS-T008. Статус — в [реестре](../../../docs/tasks/INDEX.md).
Карточка описывает будущий результат, не выдаёт наличие прототипа за готовность.

## Результат и входы

Новый UI входа, регистрации и account в утверждённой системе. I02/I03 fixtures и старые static controllers исключаются из образцов. Backend Identity остаётся действующей системой.

Прочитай [архитектуру](../../../ARCHITECTURE.md), [стандарт переноса](../../../docs/frontend/lesson-migration.md),
[UI contract](../../../docs/ux/shared-ui-contract.md) и [проверки](../../../docs/frontend/testing-policy.md).
Не перечитывай прежние ТЗ/аудиты: они не являются входом этой задачи.

## Объём работы

1. Получить недостающие решения: email против username, login/register routes и поведение homepage формы. При отсутствии решения отметить BLOCKED_DECISION, не выдумывать identity migration.
2. Разместить auth feature отдельно от generic layout; private данные не включать в SSG.
3. Сохранить restore/logout/expiry/conflict/retry semantics и доступность, не логировать credentials.
4. Заменить old account UI, homepage preview и его entry links. Backend users/passwords/sessions не удалять.
5. Перенести поведенческие/security assertions; удалить только тесты выведенного controller и старых fixture экранов после проверки imports.
6. Собрать affected identity/browser verification на disposable ресурсах.

## Приёмка

Человек выбрал email/username и маршруты до API изменений; новый UI работает с реальной Identity; заменённые old forms/controllers/styles/tests удалены без потери auth/CSRF/session/owner/privacy поведения; нет двух независимых реализаций входа.

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
