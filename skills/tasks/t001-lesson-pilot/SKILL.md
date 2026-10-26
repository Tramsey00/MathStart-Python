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
algebra. Реализация и стандарт приняты пользователем 25.10.2026; статус ACCEPTED
в ограниченном bootstrap scope. Автопрогоны NOT_RUN_BY_USER_REQUEST; отдельное
статическое review оформлено в записи закрытия ниже. Это не production-приёмка.
Действующие требования приведены ниже и в общем стандарте.
Исторические receipts ниже относятся к указанным в них candidates и не
подтверждают новую ревизию. Текущий итог — раздел «Закрытие bootstrap 25.10.2026».

Второй пилот поручен отдельно 25.10.2026 и реализован в этапе B. Разрешение
на него и приёмка линейного фиксируются раздельно; одно не означает другое.
Приёмка пилотов и общего стандарта завершена по явному подтверждению пользователя;
проверки и готовность запуска из чистого clone остаются отдельными статусами.

| Поле | Второй пилот — этап B |
| --- | --- |
| Статус | ACCEPTED; статическое review завершено, автопрогоны NOT_RUN_BY_USER_REQUEST |
| Заголовок | Деление с остатком. Понятие обыкновенной дроби |
| Источник | `curriculum/5-klass/matematika/03-obyknovennye-drobi/01-5-klass-ponyatie-obyknovennoy-drobi` |
| Утверждённый canonical | `/materials/5-math-12`, номер по полному curriculum класса и предмета |
| Предмет | Content identity `matematika`, URL-код `math`, подпись в breadcrumbs «Математика» |
| Материалы источника | 4 учебных SVG + 1 UI-иконка содержания, 1 таблица, 12 самопроверок |

### Этап B — порученный второй пилот

При отдельном поручении перенести только указанную страницу через общий
LessonPage, существующие блоки и Content/FastAPI; использовать текущие HMR и
browser origin 8131. Сохранить все задания и решения самопроверки, таблицу,
формулы и authored SVG в сохраняемой части материала. Исключить исходную
секцию «Что нужно знать перед темой» и все учебные блоки после самопроверки,
включая «Мини-итог». Самопроверка — последняя секция, дальше только общая
навигация и footer. Зафиксировать исключённые блоки и anchors в карте переноса.

Общее сопоставление предметов и отсечение материала после самопроверки
подготовлены 25.10.2026. Последнее уточнение пользователя: английский код
остаётся в URL, в breadcrumbs нужна русская подпись. Применить общие компоненты
без частных обходов. Адрес и react-v1 документ этапа B уже подключены к локальному
snapshot; повторять перенос не нужно. Новые правки применяются через HMR.
Не переносить весь 5 класс и не переписывать два действующих пилота заново.
После результата второго пилота MS-T003 переиспользует его в составе 35 тем.

### Этап C — отдельно порученный пробный перенос

| Поле | Следующий пробный урок |
| --- | --- |
| Статус | ACCEPTED; migration_authorized=true; автопрогоны NOT_RUN_BY_USER_REQUEST |
| Заголовок | Теорема Пифагора и обратная теорема. Применение |
| Класс / предмет | 8 класс / Геометрия; Content identity `geometriya`, URL-код `geometry` |
| Источник | `curriculum/8-klass/geometriya/02-ploshhadi-i-teorema-pifagora/03-teorema-pifagora-i-obratnaya-teorema-primenenie` |
| Утверждённый canonical | `/materials/8-geometry-6`; номер закреплён пользователем, не пересчитывается |
| Цель | Проверить перенос другого предмета, корней/степеней, геометрических схем и доказательств через тот же шаблон |

Перенос отдельно поручен пользователем 25.10.2026 в рамках этапа C MS-T001.
Разрешение не означает приёмку предыдущих пилотов или всей MS-T001.
Применить принятую MathML-запись,
новые рамки примеров/схем и все действующие правила; математические доказательства
и рисунки сохранять. Не начинать полный 8 класс и не создавать отдельный runtime.

### Источник первого пилота — линейная функция

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
4. Обновить линейный урок по текущему стандарту: исключить «Что нужно знать перед темой», все учебные блоки после самопроверки независимо от названия и legacy UI навигацию; сохранить материал до самопроверки и всю самопроверку с её заданиями/решениями. Точное число оставшихся секций установить при сверке.
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

## Подготовка второго пилота 25.10.2026

Исходный HEAD: `e3c4a0b731470bd68bcaa2583d294156ea681747`. По новому решению
пользователя утверждён `/materials/5-math-12`, добавлено общее сопоставление
публичных кодов предметов и английских breadcrumbs. Конвертер завершает материал
после всей секции самопроверки и отбрасывает любые следующие учебные блоки,
независимо от названия. Оба конфигурационных реестра включены в source files
подготовки/build; Content identity не переименовывается.

Изменены общие компоненты/правила и подготовлен scope этапа B. content.json
второго пилота не создавался, адрес ещё не опубликован; начало переноса ждёт
отдельного поручения. Тесты, typecheck, browser/smoke, source/docs gates и сборка
не запускались: NOT_RUN_BY_USER_REQUEST. Текущий review/human acceptance PENDING.

## Результат этапа B — второй пилот, 25.10.2026

Явное поручение пользователя 25.10.2026: реализовать этап B MS-T001, перенести только второй пилот, выполнить Content prepare/build и подключить локальный snapshot; без тестов, новой ветки/Issue и merge. Приёмка первого пилота и всей MS-T001 остаётся отдельной.

Исходный HEAD: `8a76f9a12a1139d3de611f21361d88a166ba8a05`, чистая `ui/ux`, после fetch
на 22 commit впереди `origin/main`, совпадала с `origin/ui/ux`.
Код реализации: `f8f404689e24ed3ae8c31d6efa1a19cd767d5e33`, tree `698c9af4e40f07a01e5473181b26087ecea17631`.
Это исходники сборки, а не проверенный QA candidate; проверенный SHA отсутствует.
Последующая запись результата меняет документацию, не runtime-код.

Реализация COMPLETE; Content prepare/build/initial disposable activation COMPLETE;
отдельное review PENDING; human/visual acceptance PENDING; merge NOT_PERFORMED.
Проверки: NOT_RUN_BY_USER_REQUEST. Приёмка первого пилота и всей MS-T001
не изменена. Другие темы 5 класса и следующие карточки не начаты.

Добавлены `curriculum/5-klass/matematika/03-obyknovennye-drobi/01-5-klass-ponyatie-obyknovennoy-drobi/content.json`, renderer_version react-v1,
registry `/materials/5-math-12` и assigned_path в inventory. Content identity
`matematika`, breadcrumbs `math` — через существующее общее сопоставление.
Общие LessonPage, header/footer, содержание, раскрытие решений и навигация
используются без новой оболочки. Добавлены общие стили дробной записи и подписей
схем. Главная, каталог, линейный и квадратичный уроки включены в новый snapshot;
их исходники и документы не переписывались, регрессионные прогоны не выполнялись.

Сохранены 7 секций (`theory`, `lesson-section-3`–`lesson-section-8`),
все 12 заданий с ответами/решениями, таблица, формулы и 4 учебных SVG.
Число 5 в подготовительной карточке включало SVG-иконку старого содержания.
Исключены prerequisite «Что нужно знать перед темой» (`lesson-section-1`),
весь материал после самопроверки — «Мини-итог» (`lesson-section-9`), старое
содержание, hero actions и legacy navigation. Новый header/heading/contents/
navigation заменяет прежний UI; исходный body.html сохранён без изменения.
Пофайловая карта и исключённые anchors — `specs/maintenance/t001-dispositions.json`.

Команды: `node frontend/scripts/convert-lesson.mjs <source>`;
`var/t001-qa/target-env/Scripts/python.exe var/t001/prepare-fraction-preview.py`
(явные Content prepare → React Router build → initial activation нового
собственного disposable PostgreSQL snapshot); `npm --prefix frontend run dev -- --stop`,
затем скрытый запуск `var/t001-qa/target-env/Scripts/python.exe scripts/dev_server.py`
(тот же общий dev runner, который вызывает npm run dev).
Первый prepare остановлен штатным source-commit guard из-за изменения HEAD
во время подготовки; повтор выполнен на зафиксированном коде. Логи в ignored
`var/t001/fraction-preview-build*.log`; immutable releases не переписывались.
Доменные integrity guards штатной сборки сохранены; отдельные QA-команды,
typecheck, Playwright, smoke, source/docs/preservation gates, CI и backend suite
не запускались — NOT_RUN_BY_USER_REQUEST.

Snapshot: `a13e3366-287c-4cda-a922-544fcff206e0`; manifest digest
`6c30407811f8967a074655d7d0e640f4e2b31b9358572acbc6199251fd3a7f20`.
Просмотр: http://127.0.0.1:8131/materials/5-math-12, общий dev origin с HMR.
Подготовленный экземпляр использует ignored private конфигурацию этого checkout;
воспроизводимый запуск из чистого clone остаётся MS-T002A. Production deploy
не выполнялся. Визуальная приёмка, отдельное review и назначенные пользователем
проверки остаются открытыми; сборка не объявляется технической приёмкой.

## Общие правки оформления трёх уроков — 25.10.2026

Исходный HEAD: `9be5886a293897382863a0663fca0a475f4199b7`. По новому поручению
пользователя обновлены общие LessonPage/LessonSource/WorkedExample/LessonDiagram
и scoped CSS для линейной, квадратичной функций и дробей этапа B. URL-коды
остались английскими; подписи предметов в breadcrumbs — русские. Renderer
объединяет заголовок, условие и решение настоящего примера одной рамкой,
название/подпись и SVG — другой, убирает пустые абзацы и избыточные br между
блочными элементами. Отступы стали компактнее с сохранением логических групп.
Самостоятельные схемы шире текста только на desktop; авторская геометрия,
anchors, MathML, содержимое дробей и учебный текст не переписывались.

Правила закреплены в стандарте, UI contract и общем skill вместе с прямой
ссылкой на принятую tweakcn Professional Theme / QraftHive. Единая запись
дробей и корней описана как PROPOSED / WAITING_USER_APPROVAL; новый math font
не подключён, формулы по этому предложению не менялись. Следующая пробная
страница в этом поручении не переносилась.

Тесты/typecheck/browser/smoke/source/docs/preservation gates и сборка не
запускались: NOT_RUN_BY_USER_REQUEST. HMR используется для пользовательского
просмотра. Отдельное review и визуальная/human acceptance новых правок PENDING.

## Принятая математическая запись и различающиеся рамки — 25.10.2026

Исходный HEAD: `5828ebbe769ff4c7e9e86edfc8bac5e6e6f888b4`. Пользователь принял
вид дробей и корней и поручил внедрение, затем добавил смешанные числа и дробные
степени. Подключён локальный STIX Two Math v2.13b171 с OFL. Общие helpers
MathML в math-notation.mjs применяются конвертером; добавлен безопасный mspace
для целой и дробной частей смешанного числа. Степень с дробным показателем
представляется msup с mfrac, без ручного смещения текста и без упрощения формулы.

В content.json этапа B старые CSS-дроби заменены MathML; в квадратичном уроке
три дробные записи через slash переведены в mfrac с сохранением всех чисел,
операторов, группировки и ответов. Уже существующий MathML подключён к общему
шрифту. В линейном документе записей для замены не обнаружено; общие стили
действуют на все три урока. Frozen HTML и authored SVG не переписывались.

Рамка примера слегка тонирована primary, радиус 12 px, заголовок отделён тонкой
линией; новая рамка схемы нейтральная, радиус 14 px, название отделено от рисунка.
Авторские готовые рамки сохраняются. Professional Theme и основные текстовые
шрифты QraftHive не заменены. Следующим пилотом выбран этап C о теореме Пифагора;
конвертация этой страницы, публикация URL и полный перенос класса не начинались.

Выполнена только миграция данных математической разметки и правка исходников.
Тесты/typecheck/browser/smoke/source/docs/preservation gates и сборка не запускались:
NOT_RUN_BY_USER_REQUEST. Отдельное review и приёмка реализации PENDING.

## Результат этапа C — теорема Пифагора, 25.10.2026

Отдельное разрешение пользователя на один урок, canonical `/materials/8-geometry-6`.
Исходный HEAD `ab2881bb4f6bdcb7744df588a4bc5e32428753bf`, чистая `ui/ux`;
после fetch совпадал с origin/ui/ux, на 26 commit впереди origin/main.
Код сборки `8b52b118618f5e280fbf98eefb3029d6cbcbe67c`, tree `9ded3ce90a95739dbc15aaedd76ab41db068eaee`.
Проверенного QA SHA нет: проверки NOT_RUN_BY_USER_REQUEST.

Реализация COMPLETE; Content prepare/build/local snapshot connection COMPLETE.
Отдельное review PENDING; visual/human acceptance PENDING; merge NOT_PERFORMED.
Приёмка предыдущих пилотов и всей MS-T001 не изменена. Полный класс и следующая
задача не начаты; production deploy не выполнялся.

Типизированный content.json передаётся общему LessonPage/Content/FastAPI.
Сохранены 8 секций, 2 доказательства по 4 шага, алгоритм из 3 шагов,
7 примеров, 5 учебных SVG, таблица и все 8 самопроверок с полными решениями.
Урок использует Content identity geometriya, публичный код geometry и подпись
«Геометрия» через общее сопоставление. В registry/inventory закреплён canonical;
общий Content adapter направляет старый slug и `/mathstart/` alias прямо на него.
Общая навигация: предыдущая тема в текущем разделе, следующий раздел геометрии
8 класса; ссылки формируются из полного каталога, без частного списка.

В исходнике отсутствуют «Что нужно знать перед темой», page.css, page.js
и внешние lesson resources. Схемы встроены в HTML; собственной интерактивности нет.
Исключены весь блок после самопроверки «Итог: сравните квадраты сторон»
с anchor `lesson-section-9`, старые hero actions/TOC (включая одну UI SVG-иконку)
и ms-nav. Сохраняемые anchors: `theory`, `lesson-section-2`–`lesson-section-8`.
Frozen body.html не редактировался. Карта: specs/maintenance/t001-dispositions.json.

Корни и степени явно размечены через mathExpression/mathToken/rootNode/powerNode
из math-notation.mjs, класс lesson-math и локальный STIX Two Math. Все исходные
числа, переменные, знаки и порядок вычислений сохранены, без пересчёта.
Длинные равенства разделены на MathML-фрагменты по знакам равенства для переноса.
Дробей, смешанных чисел и дробных степеней в этом источнике нет; формулы в SVG
сохранены как авторская геометрия. Примеры с внутренним заголовком получили
одну общую рамку WorkedExample; схемы — существующий LessonDiagram. Общий CSS
оформляет шаги доказательств/алгоритма с точками. Правила дополнены в стандарте
и общем skill; палитра, основные шрифты и UI kit не менялись.

Команды: `node frontend/scripts/convert-lesson.mjs <source>` и одноразовая явная
разметка формул `node var/t001/author-pythagorean-math.mjs`;
`var/t001-qa/target-env/Scripts/python.exe var/t001/prepare-pythagorean-preview.py`
(prepare → React Router build → initial activation в новом собственном disposable
PostgreSQL snapshot). Лог: ignored var/t001/pythagorean-preview-build.log.
Штатные integrity guards сборки сохранены; тесты, typecheck, Playwright,
check:dev, smoke, source/docs/preservation gates, CI и backend suite не запускались.
Результат проверок NOT_RUN_BY_USER_REQUEST, не PASS.

Snapshot `87656bdd-6238-455f-ba48-1c572362c1af`; manifest
`6cdb7164254bc31ec592ffbe6e443bc3fc52f18e480b302929ead1cb9d028faa`.
Прежние releases/БД сохранены. Новый snapshot включает главную, каталог и три
действующих урока; их документы не переписывались, регрессионные проверки не
проводились. Общий dev runner перезапущен (`npm --prefix frontend run dev -- --stop`,
затем скрытый запуск `var/t001-qa/target-env/Scripts/python.exe scripts/dev_server.py`);
штатная остановка не получила подтверждения от отсутствующего supervisor.
После сверки полных команд и parent PID адресно завершены только его оставшиеся
Vite/FastAPI процессы этого checkout; устаревшая локальная manifest/request удалена.
дальнейшие React/CSS правки используют HMR, без повторных release-сборок.
Просмотр: http://127.0.0.1:8131/materials/8-geometry-6.
Локальный runtime зависит от ignored private настроек этого checkout;
воспроизводимость из чистого clone остаётся MS-T002A. Визуальная приёмка,
независимое review и технические проверки остаются отдельными открытыми этапами.

## Закрытие bootstrap 25.10.2026 — текущая запись

Candidate статического review: `fd83af31318247291db732ef27ec715eec5c67a5`, tree `00cff571191be20cc4574fcd9f063fc0a6ded01e`.
Пользователь подтвердил визуальный результат и стандарт, затем явно поручил
закрыть оформление и review bootstrap. Реализация COMPLETE; review
COMPLETE_STATIC_SOURCE_REVIEW; human acceptance ACCEPTED; проверки
NOT_RUN_BY_USER_REQUEST; merge NOT_PERFORMED. Статус карточки ACCEPTED.

Проведён отдельный статический проход по общей React-композиции, MathML,
главной/каталогу, маршрутам, Content release boundary и dev projection.
Независимый второй исполнитель и runtime-проверки не заявляются. Блокирующих
замечаний в этой области не выявлено. Исправлены устаревший комментарий о
hydration и инструкции с четырьмя страницами/старым портом; runtime-код
не менялся. Исторические receipts и PASS других SHA сохранены как история.

Чистый clone, самостоятельная подготовка окружения, review локального запуска,
отдельное решение о merge и clone опубликованного main остаются MS-T002A.
Эта приёмка открывает её продолжение; production и MS-T003 не начинаются.
