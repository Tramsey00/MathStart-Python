---
name: mathstart-t011-rollout-finalization
description: Выполнить MS-T011 — Завершить перенос и сократить переходные проверки; только по отдельному поручению из реестра MathStart.
---

# MS-T011 — Завершить перенос и сократить переходные проверки

Зависимости: MS-T010. Статус — в [реестре](../../../docs/tasks/INDEX.md).
Карточка описывает будущий результат, не выдаёт наличие прототипа за готовность.

## Результат и входы

Свести 263 урока, главную, каталог, auth/staff в одну систему; удалить оставшиеся prototype и legacy UI adapters с доказанным отсутствием потребителей.

Прочитай [архитектуру](../../../ARCHITECTURE.md), [стандарт переноса](../../../docs/frontend/lesson-migration.md),
[UI contract](../../../docs/ux/shared-ui-contract.md) и [проверки](../../../docs/frontend/testing-policy.md).
Не перечитывай прежние ТЗ/аудиты: они не являются входом этой задачи.

## Объём работы

1. Сверить inventory всех классов, canonical/sitemap/redirects и asset lifecycle.
2. Удалить prototypes/home только после миграции всех действующих consumers.
3. Выполнить карту testing-policy: obsolete exact-Django visual assertions убрать, protocol/security/content проверки сохранить, дубли объединить.
4. Ввести scoped local команды без молчаливого сужения mandatory CI и без фиксированных прежних case counts.
5. Отделить generic tooling regressions от UI набора. Каждый удалённый тест связать с выведенным consumer или сохраняющим invariant новым тестом.
6. Выполнить требуемый full integration/release checks для actual candidate; зафиксировать отдельно human acceptance.

## Приёмка

Все 263 темы и public links/redirects разрешаются; нет prototype runtime/старого UI; тесты распределены по policy, meaningful assertions сохранены, обязательный combined candidate не подменён быстрым профилем.

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
