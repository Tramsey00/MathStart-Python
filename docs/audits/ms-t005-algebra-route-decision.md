# MS-T005 — окончательное решение маршрутов алгебры 7 класса

08.11.2026. Issue #61, Draft PR #62, ветка ms-t005-grade-7.
Входной HEAD: `d3f183fca9208ed0ff542e3611ae443c2e752bd9`, рабочее дерево чистое.
Резервная ветка: `backup/ms-t005-before-algebra-route-20261108-d3f183f`.
Source-изменение: `70a58e5d884a54dd4c387dec3d5626c80923704e`; последующий commit фиксирует только действующие документы/статусы и этот отчёт.

## Решение Руслана и ожидаемый результат

Руслан отменил до публичного выпуска прежний permanent alias `/materials/7-algebra-1 → /materials/7-algebra-8`: исторический адрес пилота освобождён для первой темы.

| Назначение | Постоянный адрес |
| --- | --- |
| Числовые выражения. Алгебраические выражения | `/materials/7-algebra-1` |
| Ранее принятый линейный пилот | `/materials/7-algebra-8` |
| Дополнительный /materials/7-algebra-37 | Не создавать |

В material-routes.json удалён только отменённый alias у пилота, его canonical номер 8 сохранён. Первой теме добавлено явное назначение number=1/renderer_version=react-v1; её lesson.json переключён на react-v1. Подготовленный content.json, все авторские HTML/формулы/ответы/SVG и MathML ledger не редактировались. Inventory assigned_path и текущая карта согласованы с решением.
Ожидаемое состояние источников — **67/75**: 66 новых документов + 1 принятый пилот. Остались только 8 статистических тем. Это ожидаемое source-состояние по изменённым данным и ручному чтению, не результат автоматического прогона или приёмки.

## Ручная сверка по исходному коду

Ниже чтение исходников и diff, без импорта/запуска приложения или проверок.

| Цепочка | Просмотренные места и вывод |
| --- | --- |
| Canonical | material-routes.json → backend/content/build.py load_material_routes/write_build_inputs → ReviewedSource.canonical_path → backend/content/projection.py delivery_candidate/seo. Первое назначение ведёт на 1, pilot на 8; общий код не менялся |
| Каталог | build_index_candidate присваивает topic.url из delivery.seo.canonical_path. PublicCatalogueProvider передаёт опубликованный каталог. materials-page.tsx topicLink возвращает topic.url |
| Поиск | results в materials-page.tsx фильтруют те же catalogue.topics и используют тот же topicLink; отдельного hardcoded pilot alias нет |
| Навигация | backend/content/lesson_context.py формирует previous/next по темам класса/предмета/разделов и берёт topic.url; LessonPage передаёт его в LessonNavigation. Новое назначение не требует смены общего resolver |
| Breadcrumbs/section | lesson_context строит section href по grade/subject/section; LessonPage использует эти данные и материал предмета. URL урока не подставляется как synthetic breadcrumb alias |
| Framework routes | frontend/src/app/routes.ts берёт publicPaths из verified published view; public-input.server.ts выбирает view по exact path и pinned release. Для нового адреса нужен будущий штатный Content handoff, не добавление частного router route |
| Redirects | apply_material_redirects выводит старые slug URLs и только явно назначенные aliases. Новый источник больше не задаёт alias 1→8. site_content/redirects.json не содержит этой записи и не менялся. Все прочие assignments/redirect sources оставлены |
| Прямо затронутый browser-сценарий | frontend/e2e/linear-lesson.spec.ts больше не ожидает redirect первой темы к пилоту: ожидается 200/её title. Пилот выбирается по стабильному slug, а не как первый попавшийся react-v1. **Сценарий не запускался** |

Общие unit fixtures с synthetic route aliases не являются текущими назначениями реестра и не менялись. Ранее выданные receipts/подтверждения с alias 1→8 остаются историей; они не используются как действующая политика и не подтверждают этот candidate.

## Изменённые файлы

Source/связи:
- `site_content/material-routes.json` — снять только отменённый alias, добавить первую тему;
- `curriculum/7-klass/algebra/01-matematicheskie-modeli/01-chislovye-vyrazheniya-algebraicheskie-vyrazheniya/lesson.json` — renderer metadata;
- `docs/tasks/lesson-inventory.json`, `docs/tasks/ms-t005-migration-map.json` — assigned path/актуальное source-состояние;
- `frontend/e2e/linear-lesson.spec.ts` — только непосредственно устаревшее route expectation/выбор пилота; без запуска.

Действующие решения/статус:
- `docs/frontend/lesson-migration.md`, `docs/ux/shared-ui-contract.md`;
- `skills/tasks/t001-lesson-pilot/SKILL.md`, `skills/tasks/t005-grade-7/SKILL.md`;
- `docs/tasks/INDEX.md`, `docs/tasks/registry.json`, `docs/tasks/ms-t005-remaining.md`;
- этот новый execution record.

Исторические audit files, HISTORY.md, receipts, logs и прежние human approvals не редактировались. Старый MathML ledger сохранён целиком: его прежний document_status относится к моменту подготовки; актуальное состояние темы задаёт migration map.

## Проверки и границы

**NOT_RUN_BY_USER_REQUEST**: tests, typecheck, Playwright, smoke, автоматические validators/gates/source-preservation checks и новые QA-скрипты не запускались. Старые PASS не присваиваются этому изменению. Результат ручного чтения исходников не называется runtime PASS.

Build, publication, Content prepare/update установленного snapshot и server lifecycle не запускались. БД, .venv, var/local и материалы других классов не изменялись. Общие converter/validator/renderer/CSS/math helper не менялись; штатные guards не отключались.

Installed snapshot может продолжать прежнюю адресацию до отдельно разрешённого штатного обновления. В данном поручении не читалась/не исправлялась runtime DB alias row, не изменялась publication authority. При будущей передаче проверяется как итоговый canonical, так и отсутствие активного redirect 1→8 в candidate; это не разрешение запускать подготовку сейчас.
Independent review **PENDING**, human visual/pedagogical acceptance **PENDING**, MS-T005 целиком **INCOMPLETE**, merge **NOT PERFORMED**. Issue #61 остаётся открытой, PR — Draft.

## Страницы для последующей ручной проверки

Выполнять после отдельно разрешённого обновления Content snapshot; сейчас эти действия не выполнялись:

1. `/materials/7-algebra-1` — первая тема и её MathML, без redirect на пилот; reload, `#theory`, `#lesson-section-4`, `#lesson-section-10`, ответы самопроверки и no-JS чтение.
2. `/materials/7-algebra-8` — тот же линейный пилот, его график и якоря; прямой вход/reload, query и Back.
3. `/materials?grade=7-klass&subject=algebra` и раздел `section=matematicheskie-modeli` — первая тема открывает 1, линейная — 8; поиск по обоим названиям ведёт в соответствующую тему.
4. `/materials/7-algebra-2` — «Предыдущая тема» ведёт на 1; первая тема — «Следующая» на 2.
5. `/materials/7-algebra-7` и `/materials/7-algebra-9` — соседство с пилотом ведёт на 8. Breadcrumbs/«Все темы раздела» сохраняют раздел и предмет.
6. `/chislovye-vyrazheniya-algebraicheskie-vyrazheniya/?from=manual#theory` — прямой canonical 1; `/linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii/?from=manual#theory` — прямой canonical 8, с сохранением query/fragment без цепочки через старый alias.
7. `/materials/7-algebra-37` — адрес не назначен; не должен появляться в каталоге/поиске/навигации или становиться заменой первой темы.

Ручная проверка UI и педагогическая приёмка этими пунктами не объявляются выполненными. После передачи текущего результата работа останавливается.
