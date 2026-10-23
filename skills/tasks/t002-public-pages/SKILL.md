---
name: mathstart-t002-public-pages
description: Выполнить MS-T002 — Подключить утверждённые главную и каталог к основному приложению; только по отдельному поручению из реестра MathStart.
---

# MS-T002 — Подключить утверждённые главную и каталог к основному приложению

Зависимости: MS-T001. Статус — в [реестре](../../../docs/tasks/INDEX.md).
Карточка описывает будущий результат, не выдаёт наличие прототипа за готовность.

## Результат и входы

Перенести homepage и материалы из prototypes/home в основные public routes, используя подтверждённую систему MS-T001.

Прочитай [архитектуру](../../../ARCHITECTURE.md), [стандарт переноса](../../../docs/frontend/lesson-migration.md),
[UI contract](../../../docs/ux/shared-ui-contract.md) и [проверки](../../../docs/frontend/testing-policy.md).
Не перечитывай прежние ТЗ/аудиты: они не являются входом этой задачи.

## Объём работы

1. Разместить routes/layout/features по стандарту.
2. Взять согласованный inline expanding search, grade picker, subject accordion и topics dialog без повторного redesign.
3. Привязать темы к общему resolver, учитывая временный legacy/React mix.
4. Сохранить keyboard/focus, no-JS доступность каталога и readable public pages.
5. Homepage auth preview не выдавать за работающий вход: заменить/подключить только в MS-T009.
6. Перенести нужные prototype сценарии в основной набор и удалить дублирующие проверки только для заменённого scope.

## Приёмка

Главная и /materials используют общий header/footer, реальные catalogue данные, поиск и grade navigation; нет localhost8121/5173 links или prototype-only virtual modules в runtime; старые catalogue URLs имеют явную совместимость.

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

Работать в ui/ux без отдельного Issue и без новой ветки на каждую задачу. Исключение действует только для MS-T001, MS-T002, MS-T002A. Готовность локального запуска проходит review в MS-T002A, затем пользователь решает merge ui/ux в main. Проверка clone опубликованного main завершает MS-T002A и открывает MS-T003.
