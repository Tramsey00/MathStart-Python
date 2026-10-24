---
name: mathstart-t001-lesson-pilot
description: Выполнить MS-T001 — Перенести новый HTML-урок по стандарту в основной React/SSG runtime; только по отдельному поручению из реестра MathStart.
---

# MS-T001 — Перенести новый HTML-урок по стандарту в основной React/SSG runtime

> Решение пользователя 25.10.2026: автоматические прогоны временно выключены.
> Списки тестов ниже — план отдельно назначенной технической приёмки и история,
> а не разрешение запускать QA при реализации. Для обычной UI-правки — HMR и
> результат NOT_RUN_BY_USER_REQUEST. См. docs/frontend/testing-policy.md.

Зависимости: MS-T000. Статус — в [реестре](../../../docs/tasks/INDEX.md).
Результаты реализации и ограничения проверок приведены в конце карточки; человеческая приёмка учитывается отдельно.

## Результат и входы

Основной пилот: **Линейная функция y = kx + b. График линейной функции**, 7 класс,
algebra. Корректировки текущего этапа выполнены; статус HUMAN_ACCEPTANCE_PENDING.
Действующие требования приведены ниже и в общем стандарте.
Старый receipt в конце карточки — только
историческая запись исходного candidate, не свидетельство выполнения коррекций.

Вторая пробная страница включена в scope подготовки, но её миграция ожидает
отдельной приёмки линейного пилота и явного разрешения пользователя. Не начинать
её конвертацию или UI-реализацию в этом этапе.

| Поле | Ожидающая страница |
| --- | --- |
| Статус | WAITING_USER_APPROVAL |
| Заголовок | Деление с остатком. Понятие обыкновенной дроби |
| Источник | `curriculum/5-klass/matematika/03-obyknovennye-drobi/01-5-klass-ponyatie-obyknovennoy-drobi` |
| Материалы источника | 5 SVG, 1 таблица, 12 самопроверок |

Точный источник — [папка урока](../../../curriculum/7-klass/algebra/02-linejnaya-funkciya-y-kx-b/03-linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii/),
slug — `linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii`. Запись уже есть в
[inventory](../../../docs/tasks/lesson-inventory.json); canonical path после коррекции — `/materials/7-algebra-8`; прежний `/materials/7-algebra-1` становится 301 alias.
Устойчивый URL назначен явно через Content и не выводится из текущего порядка тем.

Квадратичная функция y = ax² + bx + c служит визуальным эталоном и источником
общих компонентов. Её подключение к основному renderer/Content/FastAPI уже
выполнено раньше MS-T006 по поручению пользователя в MS-T002. Оба урока доступны
на общем origin 8131. MS-T006 переиспользует этот урок; повторять перенос не нужно.
Общее содержание обоих пилотов следует разделу «Содержание: принятый образец»
[стандарта](../../../docs/frontend/lesson-migration.md), включая полный заголовок,
просторные строки и адаптацию к числу секций без внутренней прокрутки.

Используй [общий skill переноса](../../lesson-migration/SKILL.md),
[архитектуру](../../../ARCHITECTURE.md), [стандарт переноса](../../../docs/frontend/lesson-migration.md),
[UI contract](../../../docs/ux/shared-ui-contract.md) и [проверки](../../../docs/frontend/testing-policy.md).
Не перечитывай прежние ТЗ/аудиты: они не являются входом этой задачи.

## Объём работы

1. Ввести validated content.json/renderer_version и один authoritative route mapping в Content.
2. Выделить из React-эталона общие layout и blocks; обобщить source adapters и registry интерактивов без привязки к квадратичной функции.
3. Подключить selective hydration через текущие prepare/build/publication, не обходя verified release.
4. Обновить линейный урок по текущему стандарту: исключить «Что нужно знать перед темой», заключительные recap/outcome секции после самопроверки и legacy UI навигацию; сохранить остальную теорию и задания. Точное число оставшихся секций установить при сверке.
   Линейный график реализовать отдельным React interactive с чистой математикой: коэффициенты k/b, направление, пересечения с осями, координаты и reset к k=1, b=0. Не подменять его квадратичным графиком и не копировать оболочку урока.
5. Сохранить legacy renderer для неперенесённых страниц. Не публиковать заново все классы.
6. Проверить текст/формулы/ответы, redirects, no-JS article, touch/keyboard/reset, light/dark и reflow.
7. Поправить стандарт по реальному пилоту; очистить заменённые assets только после проверки потребителей.

## Приёмка

Новый урок «Линейная функция y = kx + b. График линейной функции» скорректирован по текущему стандарту; canonical `/materials/7-algebra-8` обслуживается основным Content/FastAPI release, старый `/materials/7-algebra-1` ведёт прямым 301 redirect; состав, ссылки, навигация и визуальное поведение отвечают принятым решениям; проверка, отдельное review и человеческая приёмка зафиксированы раздельно.

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

## Результат 24.10.2026 — исходный candidate, историческая запись

> Запись ниже описывает исходный candidate до пользовательских корректировок.
> Её числа, URL и поведение не являются текущими требованиями и не подтверждают
> выполнение correction changes.

MS-T000 принят пользователем 24.10.2026. Исходный HEAD подготовки:
`b29a7ccdd07784cfcfd19278cbe59b30c83cd4ea`; согласованный пакет зафиксирован
в `406995b4005d9b78525f3e985e9345a5437a5e67` и перенесён fast-forward в ui/ux.
Main остался на `49b1240c495cb7c657cbb5ba9ea592bd9cb6c1d0`.

Реализация COMPLETE; отдельное review PASS; human/visual acceptance PENDING;
merge NOT_PERFORMED. Проверки PARTIAL_USER_DEFERRED: по прямому указанию
пользователя GitHub gate пока не ожидается, длительный backend suite остановлен.
Это не общий runtime/combined PASS и не техническая приёмка полного gate.

Проверенный код: `e6c16a69c03fcc9031793caf405c5fae06243eb6`, чистый tree
`a0c21d5b5f9c1cad05852c09fc71854bdae8f76c`. Последующая правка этой карточки,
реестра и стандарта содержит документацию и явную карту provenance; её docs
checks учитываются отдельно от проверок этого кода.

Реализованы content.json lesson-document-v1, общий LessonPage/header/footer,
содержание, самопроверки, навигация и стили. Полностью сверены 13 секций,
13 самопроверок, 4 таблицы, 3 авторских SVG и один linear interactive,
включая предварительные знания и экспресс-анализ. График сохраняет диапазоны,
пересечения, координаты, keyboard/touch/cancel/reset и reduced motion.
`/materials/7-algebra-1` назначен Content registry; прежний slug/aliases ведут
к canonical с query и сохранением fragment браузером. Остальные уроки остаются
legacy; квадратичный preview сохраняется без runtime-переноса.

Проверки и фактические результаты:

- `npm --prefix frontend test`: полный unit/component набор, 214 PASS/28 files;
  включает полноту текста/таблиц/SVG, линейную математику, жесты, reset и hydration
  с сохранённой тёмной темой. `npm --prefix frontend run typecheck`: PASS,
  включая API/staff generation, Router typegen и TypeScript.
- Targeted backend `test_lesson_document`: 9 PASS; repository_history: 5 PASS.
  Регрессии publication selection, строгого immutable document и compatibility
  snapshots добавлены; полный backend suite не имеет итогового результата.
- `python scripts/verify_target.py --runtime-root var/t001-qa/target-candidate-06
  --legacy-python var/t001-qa/legacy-env/Scripts/python.exe`: preparation,
  build, activation, system/routes/security, migrations — PASS; lesson sources
  263 PASS, content quality 279 PASS, site integrity 1917 PASS, skipped=0.
  Backend suite остановлен пользователем после 1572 секунд; исходный receipt
  остался FAIL с ненулевым exit, а не переписан в PASS. Последующие registry
  stages, полный browser matrix и fresh/upgrade A/B/C этого запуска NOT_RUN.
- На реальном published FastAPI gateway: `npx playwright test
  e2e/linear-lesson.spec.ts --project=chrome-360 --project=chrome-1440
  --reporter=line` — 8 PASS. Проверены canonical/301/query/anchors, direct/reload/
  Back, no-JS статья и решения, keyboard, touch/cancel, reset, light/dark.
  Дополнительно reflow при 200% CSS zoom в обеих темах — без overflow и pageerror.
- `python scripts/check_workflow_docs.py`, `python scripts/check_product_source.py`,
  `python scripts/check_migration_preservation.py` — завершающие docs/provenance
  проверки; исторические pins/approvals не переписывались.

Полный CI [40041756161](https://github.com/Tramsey00/MathStart-Python/actions/runs/40041756161)
привязан к e6c16a6. На последнем наблюдении прошли pure, target-readiness, verify,
deployment-images и release-operations (включая ordinary independent installation).
Backend-install, target и итоговый combined gate не подтверждены: дальнейшее
ожидание/проверка GitHub отложены пользователем. Результат не присваивается
следующему документационному commit.

Отдельное read-only review проведено GPT-6 Luna medium после самопроверки и
исправлений. Закрыты findings: публикация неизбранного content.json, обход
проверки selfCheck.attrs, отсутствие строгой проверки immutable release и
метаданных. Исправлены также extensionless Router input, compatibility assets,
redirects частичной публикации, pinned quality authority adapter и favicon 404.
Финальный re-review e6c16a6 не нашёл оставшихся scoped code findings.
Ранние неуспешные прогоны сохранены в var/t001-qa; один подготовительный запуск
также прервался Windows PermissionError при stage rename. Они не названы PASS.

Все QA выполнялись на собственном PostgreSQL 16 127.0.0.1:55441, с отдельными
locked target/legacy окружениями и pinned oracle; рабочий/protected stack не
использовался. Managed combined DB и две БД остановленного backend suite удалены;
собственный preview snapshot оставлен для визуальной приёмки. Host Node 24.19/
npm 11.17 удовлетворяют engines, но отличаются от pinned CI 24.21/11.19.

Просмотр в этом checkout: http://127.0.0.1:8131/materials/7-algebra-1.
После остановки preview из корня можно запустить:

```powershell
docker start mathstart-ms-t001-qa-pg
& var/t001-qa/target-env/Scripts/python.exe var/t001/serve-preview.py
```

Это сохранённый disposable QA экземпляр с приватными ignored настройками,
не инструкция запуска из чистого clone (MS-T002A). Остановка foreground preview:
Ctrl+C. Удалять frozen body.html/page.css/page.js до human acceptance нельзя;
они сохранены для сравнения и compatibility snapshots, React их не исполняет.
MS-T002 не начата; main merge и production deploy не выполнялись.

## Результат корректировок 24.10.2026 — текущий candidate

Исходный HEAD: `b595548405dad082cc89bc06ab3bbe675435c4d0`.
Проверенный код: `cc95d1fc43352cf30ade37cb4eb566a2edb9a658`, tree
`f478dea0c82d6f25b50bc3d0a1ef65fa84f878aa`. Последующее изменение этой карточки,
реестра и критерия компактного содержания — документация, без изменения runtime.
Реализация корректировок COMPLETE; scoped review выполнен двумя GPT-6 Luna
medium без оставшихся замечаний после уточнения критерия высоты содержания.
Human acceptance PENDING; merge NOT_PERFORMED.

Canonical — `/materials/7-algebra-8`, ordinal назначен по полному порядку
алгебры 7 класса, а не очереди миграции. `/materials/7-algebra-1` и старый slug
перенаправляются прямым 301 с query. Общие breadcrumbs показывают класс,
предмет и раздел; содержание помещается без внутреннего scroll и обрезки;
заголовки секций без чисел. Самопроверка использует общий компактный disclosure
справа, отступы и разделители. Увеличение схем удалено вместе с функцией,
иллюстрации заданий получили рамку. Footer показывает шесть классов через общий
компонент. Навигация учитывает границы разделов и крайние уроки предмета.

В новой редакции 11 секций, 13 самопроверок, 4 таблицы, 3 authored SVG и один
linear interactive. Явно исключены prerequisite `lesson-section-1`, финальный
recap `lesson-section-13` и legacy navigation; пофайловая карта —
`specs/maintenance/t001-dispositions.json`. Остальной учебный текст/ответы/таблицы/
SVG сверены с frozen HTML. Сам HTML, page.css/page.js и вторая пробная страница
не изменены. x изменяется только ползунком, указатель на самом графике не влияет
на точку; крайние SVG подписи внутри сетки, reset остаётся анимированным.

Фактические проверки текущего кода:

- `python scripts/verify_lesson.py` в locked target venv — PASS: 201 frontend
  tests/27 files, полный typecheck, 12 pure lesson/navigation/renderer tests,
  7 schema/UI contract tests, source gate 629, workflow docs 619 и preservation.
  Frontend tests заняли 9 секунд; это scoped результат, не full managed gate.
- `python -m unittest tests.test_repository_history -v` — 6 PASS; исходные
  исторические pins сохранены при валидации новых explicit изменений.
- Verified prepare/build/activation нового собственного disposable PostgreSQL
  snapshot — PASS. `scripts/lesson_server.py` обслуживает его на одном origin
  `http://127.0.0.1:8131`; рабочий/protected stack не использован.
- `playwright test e2e/linear-lesson.spec.ts --project=chrome-360
  --project=chrome-1440 --reporter=line --max-failures=1` — 8/8 PASS, 23,5 секунды.
  Проверены redirects/query/anchors/reload/Back, no-JS, ответы, темы, keyboard,
  reset, touch и фактические SVG границы. Геометрия содержания дополнительно
  проверена на 320×568, 360×640, 720×500, 1366×768. Снимки только в ignored cache.

Ранние неуспешные проверки не названы PASS: sandbox запрещал test temp/typegen;
первый snapshot выявил недостающий lesson_section в строгом renderer context;
замер графика выявил выход крайних подписей. Контракт и отступы исправлены,
финальный browser прогон выполнен после подтверждённого перезапуска preview.

Автоматический CI теперь использует короткий профиль. Полные backend/legacy,
browser matrix, clean install/recovery и combined gate сохранены в ручных
workflows; в этом этапе НЕ запускались. Два дорогих tooling test-файла сохранены
в полном npm test и исключены только из test:lesson. Будущая назначенная
интеграция/MS-T009 обязана выполнить соответствующий полный gate.

Второй пилот «Деление с остатком. Понятие обыкновенной дроби» остаётся
WAITING_USER_APPROVAL, migration_authorized=false. Его перенос, MS-T002,
MS-T002A и последующие классы не начаты. Обычный запуск после чистого clone
остаётся задачей MS-T002A; этот preview использует приватную ignored конфигурацию.

## Уточнение содержания и правил 25.10.2026

Исходный HEAD этого уточнения: `ee7ea1d6b6af920d537c473fcc4023f3edd66096`.
Общий CSS LessonContents обновлён для обоих уроков по повторно приложенному
пользователем образцу: просторные строки, desktop заголовок 22 px / пункты
17 px, полный заголовок и адаптация списка к оставшемуся месту. Убран общий
breakpoint 740 px, который чрезмерно уплотнял даже короткий квадратичный список.
Правила закреплены в стандарте, UI contract и общем skill. В текущих указаниях
исправлены устаревшие ссылки на отложенное подключение квадратичного урока,
порядок назначения URL и автоматические прогоны. Записи результатов 24.10 выше
остаются историей того candidate.

Тесты, typecheck, browser/smoke, source/docs gates и сборка не запускались:
NOT_RUN_BY_USER_REQUEST. Визуальная приёмка этого уточнения PENDING; прежний
review не подтверждает новый CSS. Следующая пробная страница по-прежнему
WAITING_USER_APPROVAL, её перенос не начат.
