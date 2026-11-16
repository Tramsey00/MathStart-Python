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

## Актуальная передача — 16.11.2026

Реализация: READY_FOR_REVIEW. Issue #78, ветка ms-t010-staff-ui; PR связан с Issue.
Исходный main: e5da1e73f08fe6d974ac712e5d46c8380d9949ff; итоговые SHA/tree — в PR.
MS-T009 явно принята Русланом, что подтверждено Issue #68 / PR #69.
Четыре исходные dirty-правки о приёмке T009 сохранены и в коммит T010 не включены.

**Карта runtime и покрытия.** routes.ts → staff layout → staff-foundation;
User/Group и password_change делегируются staff-write. root обходит прежний
SiteShell для staff, включая anonymous fallback. Новый StaffWorkspace использует
существующие Brand, LessonHeader/LessonFooter, useSiteTheme и общие theme/base.
Он не использует OrbitShell, auth CSS или учебный renderer. staff-records имеет
только двух runtime-потребителей: эти read/write страницы. Удалены их импорты
старых tokens/foundation и заменены inline table styles; сами foundation files
сохраняются для gallery. Прежний SiteShell остаётся у root для других legacy,
error и debug consumers; staff его больше не использует. Новых dependencies нет.

| Ресурс / URL после /admin/ | Операции и ограничения |
| --- | --- |
| content/grade/ — классы | list/search, фильтры и sort из OAS, detail/history; только чтение |
| content/subject/ — предметы | то же; только чтение |
| content/section/ — разделы | то же; только чтение |
| content/contentpage/ — страницы | то же + чтение состояния публикации; нет publication mutation |
| content/lessonpublication/ — публикации | list/search/sort/detail/history; только чтение |
| content/mediaasset/ — медиа | list/search/sort/detail/history; только чтение |
| content/redirect/ — перенаправления | list/search/filter/sort/detail/history; только чтение |
| auth/user/ — пользователи | list/search/filter/sort/detail/history; create при add_user И change_user; edit/password при change_user; preview/single/bulk delete при delete_user |
| auth/group/ — группы | list/search/default sort/detail/history; add/change/delete_group по действию, permission assignments; preview/single/bulk delete |

Точные доступные filters/orders задаёт generated staff-contracts из delivery-staff OAS,
не произвольные поля; cursor pagination всех списков/истории сохранена. Главная
показывает разрешённые resources. Собственный пароль: /admin/password_change/,
active staff без change_user; done показывает успех только после подтверждённого
ответа, переданного React Router state. Permission choices и user group choices
не дают отдельного CRUD Permission или права просмотра Group.

**Диагноз и исправление runtime.** Штатный Windows host-dev обслуживал этот
checkout с PR #79, но dev proxy отправлял /admin/* в backend immutable private
shell, обходя текущий React/HMR. Получены HTML старого entry без Vite и скриншот
старого Brand с галочкой. Причина установлена по процессам, route/imports и HTTP,
кеши не удалялись. Dev documents теперь проходят текущие React routes. Только
явный same-origin fetch с X-MathStart-Staff-Presentation читает существующий private
HTML adapter для свежих закрытых boolean hints; DOMParser инертен, HTML не вставляется.
Production private adapter, no-store и запреты public/SSG остаются.

**Граница доступа.** До подтверждения сессии и capabilities private children не
монтируются. Anonymous переходит на штатный /auth с safe return; nonstaff видит
«Нет доступа», ЛК и главную, без sidebar/filters/forms. Прямые API независимо
проверяют права. При visibility/pagehide private frame скрыт/inert; focus,
visibility return, persisted pageshow и 401/403 сверяют сессию до/после новых hints.
Подтверждённый тот же actor и права сохраняют ordinary input. Изменение actor,
доступа или denial размонтирует private subtree. Пароли очищаются перед отправкой;
обычные исправимые ошибки и 409 сохраняют черновик. Synchronous pending lock,
abort/generation guards и блокировка unknown outcome без автоматического повтора
сохранены. Password done без подтверждённого router state не заявляет успех.
В существующем AuthPage исправлена гонка: после обновления сессии login использует
тот же safeReturn, что AuthForm, вместо безусловного перехода в ЛК. Register сохраняет
переход в ЛК; внешний return отклоняется. Дизайн и остальные auth-потоки не менялись.

**Согласованная защита обычного PUT.** Руслан отдельно разрешил expected_revision
и 409 в этом чате. Ранее обнаруженный last-write-wins User/Group исправлен через
[addendum](../../../specs/api/staff-t010.md) и машиночитаемое расширение. GET detail
возвращает подписанную ревизию показанного снимка, связанную с actor/scope/resource/id;
PUT проверяет её под существующими authorization/row locks до изменений и audit.
Один из двух конкурентных PUT изменённого снимка получает 409. Create/password,
delete preview protocol и исходные frozen R02/R02A/delivery bytes не изменены.
Миграций и DDL нет. Frontend и backend расширение следует выпускать вместе;
старые формы без revision получают 400. Семантика ревизии по содержимому, no-op
не обещает новую монотонную версию. Независимое security/architecture review PENDING.

**Проверки по отдельному разрешению Руслана:**

- `node frontend/node_modules/vitest/vitest.mjs run tests/staff-access.test.tsx tests/staff-capabilities.test.ts tests/staff-form.test.tsx tests/staff-read.test.ts tests/staff-write.test.ts tests/staff-return.test.tsx --root frontend`:
  6 файлов, 51/51 PASS. Включены gate до mount, view-only direct URL, сохранение
  ordinary draft при focus, смена actor/отзыв доступа, инертные hints, exact int64,
  required revision, 409 без повтора и потери черновика, unknown outcome, auth return
  после обновления сессии и отказ внешнему адресу возврата.
- `.venv/Scripts/python.exe var/tmp/ms-t010/run_staff_scope.py`: 16/16
  StaffWriteTests PASS в одноразовом PostgreSQL 16 на отдельном loopback55461,
  fresh setup и finally cleanup контейнера. Проверены anonymous401/nonstaff403,
  ограниченные permissions, expiry401, CSRF, combined gates, relations, password
  revocation, stale/forged/missing/wrong-resource revision, concurrent PUT,
  отсутствие частичных writes/audit, delete preview stale/PROTECT.
  Временный runner удалён после проверки; tracked tests остаются в backend/tests/v03.
- Самопроверка diff/imports/consumers и `git diff --check` выполнены.
- Full suites, typecheck, release build, lesson QA/smoke, массовые captures,
  live mail, dependency scanning: NOT_RUN_BY_USER_REQUEST.

**Ручной браузерный просмотр.** Принятые главная, Материалы и ЛК осмотрены в обеих
темах до изменения staff. Затем открыты реальные /admin/, Content list/detail,
User list/add, Group list/add, read-only Content и запрет delete для ограниченного
staff; desktop и узкий390px, обе темы. Таблица имеет caption/scope и клавиатурную
прокрутку, узкие details складываются вертикально. Проверены обычный nonstaff без
staff оболочки, anonymous redirect и logout → Back к staff → auth с safe return;
успешный повторный login возвращает на исходную staff страницу. Формы просматривались
без изменения существующих пользователей, прав, паролей или удаления записей.
Реальные expiry/revocation и конкурентные mutations проверены на изолированных
данных тестами; в браузере не имитировались изменением действующих аккаунтов.

**Использованные skills и источники.** Явно применены task skill, frontend-design,
Impeccable Operate (без переустройства PRODUCT.md), ui-ux-pro-max, verification и
computer-use. Визуально осмотрены [Khan Academy Integrated math 1](https://www.khanacademy.org/math/math1)
(разделение навигации и основного содержания) и live-пример
[Carbon v10 Data table](https://v10.carbondesignsystem.com/components/data-table/usage/)
(компактный toolbar, шапка/строки и локальная прокрутка). Палитра и шрифты взяты
из принятого MathStart. [WAI Tables](https://www.w3.org/WAI/tutorials/tables/)
использован для caption/headers, [MDN pageshow](https://developer.mozilla.org/en-US/docs/Web/API/Window/pageshow_event)
для persisted return, [OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
для независимого server-side gate. Статьи не выдаются за визуальный осмотр.

**Локальный результат.** Штатный host-dev работает на общем origin
http://127.0.0.1:8131/admin/ (API8132), с HMR; prototype/release build не запускались.
По отдельному подтверждённому разрешению создан новый local staff: 9 view и
add/change User/Group, без delete и superuser. Existing users не менялись.
Credentials только в ignored var/tmp/ms-t010/local-staff-access.json, вне Git/PR.
Основная local target DB использовалась только для этого разрешённого аккаунта
и чтения; tests используют disposable DB, protected acceptance DB не затронута.

Первый опубликованный кандидат fda5ace236a86d8f23c0cba4b9f39d21da24a1d1 не принят
Русланом визуально; текущая доработка его заменяет. Локальная пауза сохранена
checkpoint 1e13dfc6e3eee2243dd3ebaa4f93a30fcd02e5c0, затем отменена Русланом.
Итоговые проверенные SHA/tree и способ публикации фиксируются в существующем PR #79.
Независимое review: PENDING. Ручной просмотр исполнителем: выполнен в указанном
объёме. Human acceptance: PENDING. Merge/deploy/закрытие Issue/переход к T011
не выполнялись.
