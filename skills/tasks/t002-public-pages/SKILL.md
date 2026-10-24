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

## Дополнительное поручение 24.10.2026

Пользователь явно поручил сейчас подключить утверждённые главную, каталог и
квадратичную функцию к тому же FastAPI, что и линейная, без запуска проверок.
Это расширяет текущий scope: runtime-интеграция квадратичной функции выполнена
раньше MS-T006. Новые отдельные порты не создавать. Адреса: `/`, `/materials`,
`/materials/8-algebra-32`, `/materials/7-algebra-8`. Старые catalogue URLs
перенаправляются на `/materials`. Исходный HTML уроков остаётся frozen.
Тесты, typecheck, browser QA и отдельное review — DEFERRED_BY_USER. Выполняются
только преобразование контента, сборка и обязательная публикация собственного
локального snapshot; успешная сборка не считается приёмкой или PASS проверок.
Основные public React компоненты находятся в `frontend/src/features/public-pages/`,
данные каталога приходят из pinned Content release; prototype virtual modules и
порт 8121 в runtime не используются. Авторизация не перерабатывается: настоящие
ссылки ведут на `/account/`, email-форма остаётся явно обозначенным preview.

## Подключение общего runtime — 24.10.2026

Код подключения: `7aa5e81` в общей ui/ux. Главная и каталог вынесены в
`frontend/src/features/public-pages/`; их approved JSX/CSS использованы без
повторного redesign. Shared LessonHeader/LessonFooter и theme hook общие с
уроками. Данные каталога строятся из pinned Content catalogue; ссылки тем берутся
из опубликованного url. Квадратичная функция переведена в lesson-document-v1
с существующим React-графиком и восемью секциями принятого эталона. Старый HTML
не изменялся. Линейная остаётся на `/materials/7-algebra-8`.

Каталог имеет canonical `/materials`; старые `/karta-sajta/`, `/materials.html`
и `/materials/` получают 301. Главное меню, footer, breadcrumbs, поиск и ссылки
разделов используют относительные адреса текущего FastAPI origin. Node нужен
только при сборке. Email-форма главной остаётся preview и не отправляет данные;
без hydration её поля/submit disabled. Вход в настоящий runtime — `/account/`.

При сборке исправлены Windows rename-lock и файловое пересечение каталога
`/materials` с namespace уроков; артефакт каталога хранится в materials/index.html.
Это изменения build adapters, не отдельная проверка установки/CI.

Тесты, typecheck, browser QA и отдельное review НЕ запускались по прямому
указанию пользователя. Не присваивать этой работе результаты MS-T001.
Реализация подключения не означает полную техническую приёмку MS-T002 или
готовность clone-запуска: последнее остаётся MS-T002A. Merge не выполнен.
