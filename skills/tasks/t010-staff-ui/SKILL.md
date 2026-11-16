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

## Актуальная передача — 16.11.2026, только User/Group

Новое явное решение Руслана заменяет требование девяти ресурсов в UI: остаются
только Пользователи и Группы со всеми существующими разрешёнными операциями.
/admin/ выбирает первый разрешённый ресурс (users, затем groups); при отсутствии
обоих сохраняется отказ без пустого рабочего frame и без расширения прав.
Content UI удалён из staff-foundation, меню и прямых маршрутов; неизвестные /admin/*
передаются существующему root 404 boundary. Для защиты от старого dev route manifest
StaffWorkspace также использует ту же существующую error presentation, вынесенную
без изменения разметки в RouteErrorPage. Дизайн/политика 404/403 не менялись.
Backend Content API, данные, публикации, redirects, схема БД и shared clients сохранены.
Самостоятельная own-password форма и её done UI удалены; оба старых адреса ведут
через Navigate replace в действующий /account/?section=security. Административный
пароль User, backend password/session API и отзыв сеансов сохранены.
Staff использует непосредственно OrbitHeader из orbit-shell.tsx, как главная;
staff overrides header удалены, header находится вне staff-workspace styles.
Главная и подвал не переоформлялись. Общий компонент уже существовал.

Вход: local e43e99d / published b4dd42d, tree97d94bf38603fc9aa2731e65e0af2c986f2b3be1.
Итоговые SHA/tree — в PR #79. Четыре исходных dirty-файла T009 сохранены вне коммита.
Саморевью diff/imports/routes и git diff --check. Новые прогоны, typecheck, build,
automated browser QA и QA scripts: NOT_RUN_BY_USER_REQUEST. Исторические 57/3
и замеры загрузки ниже не являются новым прогоном сокращённого UI.
Ручной просмотр: /admin/→users, users search с пустым результатом, Group add с
permissions, обе темы, mobile390px/desktop, сравнение общей шапки с главной,
старый Content URL без staff форм, password_change→безопасность ЛК. Записи,
права и пароли не менялись. Свежая ручная nonstaff-сессия в этом проходе не
проверена; сохранён gate и исторический receipt, новый PASS не заявляется.
Проверка публикации ограничена файлами/материалами T010: текущий diff и staged,
новые файлы и два итоговых снимка без пользователей. Секреты/реальные аккаунты
не добавлены в fixtures/документацию; локальные credentials и старые captures
остаются ignored и не включены. Полный GitHub/history audit не проводился.
Независимое review и human acceptance PENDING. Merge/deploy/Issue close/T011 нет.

## Историческая доработка — 16.11.2026, стиль и загрузка

Реализация: READY_FOR_REVIEW, Issue #78 / PR #79, та же ms-t010-staff-ui.
Входной local SHA: 3e1ac93c70dd1da29dcc0aecaa6fbe90b1b8dcca; published
5860c6e92ec671f203535acdaaa4ad806e4299a0; у обоих tree
d23bd7b36d537cdab19f89010b341cd634157ab3. Итоговые SHA/tree фиксируются в PR.
Четыре исходные dirty-правки приёмки T009 сохранены вне коммита этой задачи.

**Последнее решение Руслана:** вернуть прежнюю компоновку админки и менять её
стиль по главной и ЛК. Оно уточняет исходное поручение о перестройке композиции.
Сохранены плоское боковое меню, двухколоночный указатель разделов, breadcrumbs,
toolbar, все видимые фильтры и прежний порядок полей форм. Фон #e7f0f8 / #141a31,
поверхности, границы и action-цвета взяты из текущих OrbitShell/orbit.css ЛК;
Golos Text, Brand/Outfit, общие шапка и подвал — из принятого MathStart.
Кнопки, поля, таблицы, состояния и focus оформлены scoped staff.css. На узком
экране меню переносится, details складываются, широкая таблица прокручивается
в собственной keyboard-focusable области. Нового UI kit, motion и dependencies нет.
Root получил только начальный фон /admin/, чтобы не было белого кадра до staff CSS.

**Подтверждённое избыточное ожидание.** Несколько начальных/focus эффектов
одновременно читали сессию; staff перезапускал и отменял собственную проверку,
а внутренние anchors полностью перезагружали документ. SessionProvider теперь
объединяет только одновременно выполняющиеся автоматические чтения; явный refresh
после login/logout/мутации всегда начинает новый запрос. Результат старого запроса
не заменяет новую сессию. Все потребители проверены: root, SiteShell, account,
AuthForm и StaffWorkspace; публичные страницы staff capabilities/стили не загружают.
Staff использует только что законченный первоначальный общий session read как
первую проверку actor; затем новые capabilities и новый actor read. При navigation,
focus/return/retry выполняются свежие проверки до и после capabilities. Одновременные
события возврата объединяются лишь на время этой проверки. Кеша прав/TTL нет.
Внутренние Link/navigate сохраняют свежий gate и исключают перезагрузку JS/CSS.
Данные следующего pathname монтируются только после его проверки; старый child
не показывается на новом адресе. Контекст прав вынесен в стабильный модуль для HMR.
Ошибка соединения блокирует скрытую/inert форму того же actor, сохраняя ordinary
draft до успешного retry; подтверждённый denial/смена actor или scope очищает subtree.
CSRF, no-store, API permissions, revision, confirmation и unknown outcome сохранены.

**Измерения:** один работающий Windows host-dev, этот checkout, Vite PID14044
(parent20304) на8131 и FastAPI PID24832 (parent21424) на8132; origin127.0.0.1:8131.
По два открытия до/после при1280×900, без throttle, очистки кеша и рестарта процессов.
Уже прогретый dev-server; запуск и первый запрос после запуска не измерялись.
Performance navigation/resource timings и появление реального DOM формы/данных
сняты временным dev-only инструментом; он и его import удалены. Измерение DOM
не равно TTI/Core Web Vitals. Sanitized локальные timings — только ignored var/tmp.

| Страница / показатель, мс | До | После |
| --- | --- | --- |
| /admin/ — доступный index DOM | 756–791 | 624–680 |
| /admin/content/grade/ — доступная таблица при полном открытии | 891–1021 | 664–697 |
| /account/ — доступная форма выбора класса | 578–620 | 475–513 |
| / — загрузка HTML-документа | 210–267 | 226–308 |
| /materials — загрузка HTML-документа | 223–266 | 270–293 |

Первоначальный staff: 6 session fetch (включая отменённые) и1–2 capability fetch;
после: 2 session fetch всего (общий initial + свежий after) и1 capabilities.
ЛК: 2 одновременных session fetch →1, state/grades остаются параллельными.
Внутренний index→список:394мс, список→запись:380мс, без нового документа;
это отдельные SPA-наблюдения, не сравнение с полным reload. Финальные API reads
в этих наблюдениях: session67–96мс, capabilities54–61мс, таблица/запись73–139мс.
JS/CSS/шрифты наблюдались отдельно: например, staff index первый повтор до —
JS до329мс, CSS до336мс, шрифты до395мс; после —390/408/457мс. Улучшение загрузки
assets не заявляется. Public DOM мог появляться до hydration: он не использовался
как доказательство интерактивной готовности. В public нет staff fetch/assets.
Общее заметное замедление главной/Материалов **не воспроизведено**; ускорение этих
страниц не заявляется. Существующее чтение/JSON.parse public-view на сервере
обнаружено в исходнике, но его причинная связь с жалобой не доказана; не изменялось.
Текущего сохранённого server stdout нет; исторические логи не выданы за измерения.

**Профильная перепроверка этого изменения (разрешена отдельным поручением):**

- `node frontend/node_modules/vitest/vitest.mjs run tests/staff-access.test.tsx tests/staff-session.test.tsx tests/staff-form.test.tsx tests/staff-read.test.ts tests/staff-write.test.ts tests/staff-capabilities.test.ts tests/staff-return.test.tsx --root frontend`:
  **57/57 PASS, 7 файлов**. Новые случаи: initial shared readiness, совмещение
  событий возврата, gate нового pathname, transport failure/retry с сохранением
  draft, StrictMode readiness и свежий post-mutation read поверх старого запроса.
  Существующие assertions доступа, revision/409, unknown outcome, int64 и return сохранены.
- `.venv/Scripts/python.exe var/tmp/ms-t010/access_scope.py`: **3/3 PASS** —
  `test_admin_read_privacy_denies_anonymous_nonstaff_and_limits_staff_scope`,
  `test_expired_staff_session_cannot_read_or_write_private_data`,
  `test_private_ui_capabilities_preserve_combined_gate_and_content_readonly`.
  Отдельный disposable PostgreSQL16 наloopback55462, fresh fixture; runner,
  контейнер и временные env очищены. Target/protected DB для тестов не использовались.
- Самопроверка imports/consumers/diff и `git diff --check`. Full suites, typecheck,
  release build, lesson QA/smoke, mass captures, live mail и scans:
  **NOT_RUN_BY_USER_REQUEST**.

Финальный ручной просмотр: принятые главная, Материалы, ЛК как реальные источники;
staff index/list/detail/history, пустой поиск, User/Group add, собственный password
и отказ delete ограниченному staff; обе темы, desktop и390px. Обычный input
не отправлялся. Logout→закрытый /admin/→auth с safe return→login→/admin/ подтверждены
после изменения SessionProvider. Удаление и изменение прав/паролей действующих
аккаунтов не выполнялись. Delete preview недоступен этому staff и визуально заново
не проверен; его прежний protocol и профильные проверки остаются историческим receipt.
Локальный staff, созданный ранее по разрешению Руслана, не пересоздавался и права
не расширялись. Данные входа остаются вне Git. Диагностический код удалён,
финальный браузерный reload выполнен, viewport override сброшен.

Независимое review и human acceptance: **PENDING**. Замеры малой выборки не
подтверждают cold start/production performance; полный QA не разрешён. Merge,
deploy, закрытие Issue и T011 не выполнялись.

## Историческая передача — 16.11.2026, кандидат 5860c6e

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
