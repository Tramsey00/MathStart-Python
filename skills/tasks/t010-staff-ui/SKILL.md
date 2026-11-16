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

**Безопасность и статическое саморевью.** Прочитаны реальные imports, route/build inputs,
clients, DTO, backend staff authorization/presentation/writes и private shell adapter.
Сервер, схема, API clients и generated contracts не менялись. Active/staff/superuser,
model permissions, CSRF, exact int64 IDs, no-store/redirect/schema checks, Content
source-managed запреты и actor/revision/expiry-bound delete token/PROTECT сохранены.
Ответ 401/403 закрывает и размонтирует private view. При уходе фокуса/скрытии вкладки
private state размонтируется, запросы abort; возврат сверяет сессию, смена actor
перезагружает документ с новыми capabilities. Generation/request guards сохраняются.
Такая очистка намеренно сбрасывает несохранённый ввод при уходе со страницы.
Пароли очищаются перед отправкой, обычный ввод остаётся при исправимой ошибке.
Synchronous pending ref блокирует повторную мутацию; unknown outcome блокирует запись,
не повторяет её и не подменяет ошибку успешной загрузкой. Выборы permissions/groups
должны загрузиться до отправки формы. Confirmation token не отображается.

**Конкретное существующее ограничение, требующее отдельного решения.**
StaffUserUpdateRequest / StaffGroupWriteRequest не содержат expected revision;
StaffWrites.mutate блокирует строки, но не сравнивает версию со снимком открытой формы.
Поэтому обычный PUT может перезаписать более новое редактирование. Revision bound
delete preview защищён, но полной защиты устаревшей формы User/Group здесь нет.
Не расширяли DTO/backend под видом оформления. Для исправления требуется согласовать
optimistic-concurrency контракт, серверное сравнение и профильные проверки отдельно.
До решения нельзя заявлять выполнение этого критерия приёмки целиком.

**Проверки:** NOT_RUN_BY_USER_REQUEST — tests, typecheck, build, Playwright,
browser QA, smoke, gates и detector не запускались; QA scripts не создавались.
Саморевью чтением diff не является PASS или независимым review. Не проверены runtime
permission denial, stale revision, validation, sensitive input, session expiry,
unknown-write/repeat submit, desktop/mobile, keyboard и обе темы.

**Локальный запуск.** На 8131/8132 слушателей не было. Штатный
`npm.cmd --prefix frontend run dev:host` остановился на inspect-db: Docker Desktop
Linux Engine недоступен. БД/config не менялись, чужие процессы не останавливались.
После запуска Docker Desktop повторить штатную команду. Параллельных серверов нет.

**Ручной маршрут:** http://127.0.0.1:8131/admin/ → разрешённый ресурс → поиск/filters/sort
→ следующая страница → запись /<id>/change/ → /<id>/history/; у User/Group также
add/, password/ (User), delete/ с preview без финального удаления. Реальные id брать
из списка. Проверить /admin/password_change/, светлую/тёмную тему, узкий экран и Tab.
Изменения данных и разрушительные demo не выполнялись.

Независимое review: PENDING. Ручной просмотр: PENDING. Human acceptance: PENDING.
Merge/deploy/закрытие Issue/переход к T011 не выполнялись.
