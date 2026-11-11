# MS-T005 — перенос независимых материалов 7 класса

08.11.2026. Issue [#61](https://github.com/Tramsey00/MathStart-Python/issues/61), ветка `ms-t005-grade-7`.
Статус **BLOCKED_DEPENDENCY**: полный класс не готов.

## Candidate и границы

Checkout `C:/Users/User/PycharmProjects/MathStart-host-check`, remote `https://github.com/Tramsey00/MathStart-Python.git`.
Исходное состояние: detached `a44c5f72e4cc7d9958f03c84dbfb79dac697be6c`, clean tree, single-branch fetch ui/ux.
`git fetch origin refs/heads/main:refs/remotes/origin/main` получил `cf8690794644fe5f90c42d5aae2c1c5f7ca9b888`; исходный HEAD отставал на 7 commits.
Безопасный переход: `git checkout --no-overwrite-ignore -b ms-t005-grade-7 origin/main`.
Проверенный implementation SHA: 8488584758c5131ebba789fa13711639331be254, tree 467a32e8f2e3aa940c18e23876e587ebd9f3a2bc.
Последующий commit содержит только execution record/workflow status, не новый проверенный runtime candidate.

Реализованы 24 новых React-документа: 7 алгебра, 3 геометрия, 14 статистика; 1 пилот переиспользован, 4 документа подготовлены без активации, 46 тем остаются legacy. Всего 75.
Подключённые новые темы сохраняют 186 учебных секций, 30 SVG, 10 таблиц, 218 заданий самопроверки. Линейный пилот не переписывался.
Новые content.json получены существующим convertLesson; альтернативного конвертера нет.
Данные только в curriculum/7-klass, новые назначения только своих 24 тем в общем реестре маршрутов.
Общие converter/sources.py, renderer/components/CSS и материалы других классов не изменены.
БД, .venv, var/local не менялись; release build/публикация не запускались; dev origin не запускался и не останавливался.

## Сохранность и исключения

[Пофайловая карта](../tasks/ms-t005-migration-map.json) содержит source paths всех 75 тем, SHA256 body/CSS/JS, секции, SVG/таблицы/задания и первые ошибки.
Все существующие body.html/page.css/page.js и media сохранены byte-for-byte, удалений нет.
В новых документах исключены только prerequisites, блоки после самопроверки и legacy-навигация по действующему пользовательскому стандарту. Исключённые учебные section IDs перечислены по каждой теме; для заблокированных тем это только план исключений.
SVG-комментарии остаются в исходном body.html; converter их не переносит как учебные данные. Тест сравнивает SVG markup без HTML/React boundary comments; геометрия, атрибуты и подписи сравниваются полностью.
Четыре подготовленных content.json проходят schema validation, но lesson.json/URL не активированы из-за неэквивалентности renderer/CSS. Это не завершённый перенос.

## Проверки и ограничения

Пользователь в текущем поручении явно разрешил scoped tests/typecheck/Playwright/source/URL проверки. Глобальная testing policy не изменена.
Команды из root, если не оговорено frontend cwd.

| Проверка | Результат actual candidate |
| --- | --- |
| `node node_modules/vitest/vitest.mjs run tests/grade-7-preservation.test.tsx tests/material-routes.test.ts tests/lesson-navigation.test.tsx tests/linear-lesson.test.tsx tests/linear-math.test.ts tests/linear-interaction.test.tsx --reporter=json --outputFile=../var/ms-t005/vitest-final.json` (frontend cwd) | **38 passed**, 6 files, 0 failed/pending, не полный frontend suite |
| Новый grade-7-preservation test | Exact inventory 75, hashes frozen sources, уникальность canonical+alias; SSR text/answers/table cells/SVG/links/anchors всех 24 подключённых тем, общая navigation |
| `load_sources(Path.cwd())`, затем `load_material_routes(Path.cwd(), {b.snapshot['slug']:b for b in bundles})`, `apply_material_redirects` через .venv Python | **PASS**: 279 bundles, 28 assignments всего, 25 grade-7 canonical routes, 26 direct old-slug/alias redirects, без БД |
| `npm.cmd run typecheck` (frontend cwd) | **FAIL**: frozen API generation PASS, затем `Stale generated staff contracts`; wrapper до typegen/tsc не дошёл. staff-contracts.json byte-identical исходному main, generator/inputs этим PR не менялись |
| `node node_modules/@react-router/dev/bin.js typegen`, отдельно `node node_modules/typescript/bin/tsc --noEmit` (frontend cwd) | **PASS**, это не PASS всего wrapper |
| `.venv/Scripts/python.exe -m unittest backend.tests.v04.test_lesson_document -v` | **8 passed / 1 ERROR** из 9: test_registry_rejects_duplicate_routes_and_renderer_mismatch, Invalid material subject registry; existing mock подменяет также subject registry данными route registry до использования текущих assignments. Тест, loader и subject registry не менялись |
| `node var/ms-t005/browser.mjs` | **48/48 PASS**, Playwright/Edge 157.0.4341.42, 24 offline SSR articles × 360/1440 px, JS disabled/reduced motion: h1, SVG bounds, no object corruption, native contents anchors, доступность ответов, light/dark overflow |
| `http://127.0.0.1:8131/materials/7-algebra-8` через Playwright | **UNAVAILABLE**, net::ERR_CONNECTION_REFUSED; HTTP routes/reload/Back/hydration не подтверждены |
| `git diff --check`, staged scope inspection | **PASS**; нет изменений frozen authored files/shared implementation |

Browser HTML получен временным renderToString(LessonPage) с фактическим shared runtime CSS и локальными шрифтами. Это не React Router release build, HMR или проверка опубликованных URL.
Подготовка browser HTML: `node node_modules/vitest/vitest.mjs run --config ../var/ms-t005/vitest.config.mjs --reporter=dot` из frontend; затем browser.mjs из root.
Сырой JSON/logs и временные scripts находятся в ignored var/ms-t005, в Git не включены. Секреты/PII не выводились.
Content snapshot не обновлялся: новые URL появятся в runtime только после отдельно разрешённой подготовки/публикации.

При разработке preservation test выявил SVG title corruption двух тем: они переведены в prepared/inactive. Три первоначальных SVG mismatch относились только к comments; сравнение уточнено без исключения geometry/text.
Первоначальный browser script остановился на неоднозначном multi-section locator; после исправления allInnerTexts выполнены все 48 сценариев.
Новый test TS error (aliases отсутствует в MaterialRoute) исправлен чтением сырых assignments. Ранние технические ошибки cwd Vitest, списка вместо slug-map в route loader и import временного exporter исправлены; они не учитываются как PASS.

## Зависимости и URL

Владимир выполняет MS-T003 и ещё не передал общий commit. Пользователь подтвердил: продолжать независимые темы, converter/sources.py не менять; интеграция будет отдельно поручена.
Ниже фиксируется первая ошибка каждого converter-blocked источника; она может скрывать последующие неподдерживаемые элементы.
Дополнительно `/materials/7-algebra-1` конфликтует с закреплённым alias линейного пилота. Нужное решение о URL принимает пользователь; перенумерация/удаление alias не выполнялись.
У неподключённых тем сохраняются исходники и legacy маршруты. Runtime availability нового candidate без публикации не заявляется.

## Все 75 тем

У неподключённых тем адрес ниже — только proposed curriculum-based assignment, не опубликованный/закреплённый canonical. Пилот сохраняет /materials/7-algebra-8 и alias /materials/7-algebra-1.

| Адрес / предложение | Тема | Реализация | Точная блокировка |
| --- | --- | --- | --- |
| `/materials/7-algebra-1` | Числовые выражения. Алгебраические выражения | Не перенесена | Composite legacy term needs explicit authored MathML; URL already reserved as a permanent alias of the linear pilot; human route decision required |
| `/materials/7-algebra-2` | Математический язык | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-3` | Математические модели реальных ситуаций | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-4` | Линейное уравнение с одной переменной. Алгоритм решения | Не перенесена | Composite legacy term needs explicit authored MathML |
| `/materials/7-algebra-5` | Координатная прямая. Числовые промежутки | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-6` | Координатная плоскость. Координаты точки | Перенесена | — |
| `/materials/7-algebra-7` | Линейное уравнение ax + by + c = 0. График линейного уравнения | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-8` | Линейная функция y = kx + b. График линейной функции | Принятый пилот | — |
| `/materials/7-algebra-9` | Линейная функция y = kx, её свойства | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-10` | Взаимное расположение графиков линейных функций | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-11` | Понятие системы линейных уравнений с двумя переменными | Перенесена | — |
| `/materials/7-algebra-12` | Решение систем линейных уравнений. Метод подстановки | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-13` | Решение систем линейных уравнений. Метод сложения | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-14` | Система линейных уравнений как математическая модель | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-15` | Понятие степени с натуральным показателем | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-16` | Часто используемые степени | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-17` | Базовые свойства степеней с натуральным показателем | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-18` | Умножение и деление степеней с одинаковыми натуральными показателями | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-19` | Понятие степени с нулевым показателем | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-20` | Понятие одночлена. Приведение одночлена к стандартному виду | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-21` | Сложение и вычитание подобных одночленов | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-22` | Произведение одночленов и возведение одночлена в степень | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-23` | Деление одночленов | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-24` | Понятие многочлена. Приведение многочлена к стандартному виду | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-25` | Как складывать и вычитать многочлены | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-26` | Как умножать многочлен на одночлен | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-27` | Как умножать многочлен на многочлен | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-28` | Применение формул сокращённого умножения | Перенесена | — |
| `/materials/7-algebra-29` | Как делить многочлен на одночлен | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-30` | Понятие разложения многочленов на множители | Перенесена | — |
| `/materials/7-algebra-31` | Разложение на множители. Вынесение общего множителя за скобки | Не перенесена | Unsupported attribute: dy |
| `/materials/7-algebra-32` | Разложение на множители. Способ группировки | Перенесена | — |
| `/materials/7-algebra-33` | Разложение на множители. Использование формул сокращённого умножения | Перенесена | — |
| `/materials/7-algebra-34` | Разложение на множители. Сочетание различных приёмов | Перенесена | — |
| `/materials/7-algebra-35` | Применение разложения на множители для сокращения алгебраических дробей | Не перенесена | Composite legacy term needs explicit authored MathML |
| `/materials/7-algebra-36` | Понятие тождества | Не перенесена | Unsupported attribute: dy |
| `/materials/7-geometry-1` | Точки, прямые, отрезки и лучи. Измерение отрезков | Не перенесена | Unsupported attribute: font-style |
| `/materials/7-geometry-2` | Угол: виды, измерение и биссектриса | Перенесена | — |
| `/materials/7-geometry-3` | Смежные и вертикальные углы. Перпендикулярные прямые | Не перенесена | Unsupported attribute: font-style |
| `/materials/7-geometry-4` | Треугольник и его элементы. Медиана, биссектриса и высота | Не перенесена | Unsupported attribute: font-style |
| `/materials/7-geometry-5` | Три признака равенства треугольников | Не перенесена | Unsupported attribute: fill-opacity |
| `/materials/7-geometry-6` | Равнобедренный и равносторонний треугольники | Перенесена | — |
| `/materials/7-geometry-7` | Окружность и основные задачи на построение | Перенесена | — |
| `/materials/7-geometry-8` | Параллельные прямые и секущая. Признаки параллельности | Готов документ; renderer блокирует | Shared source-renderer.tsx renders SVG title children as [object Object]; academic/accessibility SVG title preservation fails. Shared renderer change requires coordination. |
| `/materials/7-geometry-9` | Аксиома параллельных прямых. Свойства углов | Готов документ; renderer блокирует | Shared source-renderer.tsx renders SVG title children as [object Object]; academic/accessibility SVG title preservation fails. Shared renderer change requires coordination. |
| `/materials/7-geometry-10` | Сумма углов треугольника. Внешний угол | Не перенесена | Unsupported attribute: font-style |
| `/materials/7-geometry-11` | Соотношения между сторонами и углами. Неравенство треугольника | Не перенесена | Unsupported source tag: img |
| `/materials/7-geometry-12` | Прямоугольные треугольники. Расстояния и построение треугольника | Не перенесена | Unsupported attribute: fill-opacity |
| `/materials/7-statistics-1` | Представление данных в таблицах | Перенесена | — |
| `/materials/7-statistics-2` | Практические вычисления по табличным данным | Перенесена | — |
| `/materials/7-statistics-3` | Извлечение и интерпретация табличных данных | Перенесена | — |
| `/materials/7-statistics-4` | Практическая работа «Таблицы» | Не перенесена | Unreviewed lesson root block: div |
| `/materials/7-statistics-5` | Графическое представление данных в виде круговых диаграмм | Готов документ; CSS блокирует | CSS-only pie chart and coloured legend depend on static/mathstart/css/lesson-diagrams.css; React delivery intentionally excludes legacy CSS, so the chart collapses. Shared UI/CSS agreement required. |
| `/materials/7-statistics-6` | Графическое представление данных в виде столбиковых (столбчатых) диаграмм | Перенесена | — |
| `/materials/7-statistics-7` | Чтение и построение диаграмм | Не перенесена | Unsupported authored layout style |
| `/materials/7-statistics-8` | Практическая работа «Диаграммы» | Не перенесена | Unreviewed lesson root block: div |
| `/materials/7-statistics-9` | Числовые наборы. Среднее арифметическое | Не перенесена | Composite legacy term needs explicit authored MathML |
| `/materials/7-statistics-10` | Медиана числового набора. Устойчивость медианы | Перенесена | — |
| `/materials/7-statistics-11` | Практическая работа «Средние значения» | Перенесена | — |
| `/materials/7-statistics-12` | Наибольшее и наименьшее значения числового набора. Размах | Перенесена | — |
| `/materials/7-statistics-13` | Свойства средних | Не перенесена | Composite legacy term needs explicit authored MathML |
| `/materials/7-statistics-14` | Решение задач | Перенесена | — |
| `/materials/7-statistics-15` | Примеры случайной изменчивости | Перенесена | — |
| `/materials/7-statistics-16` | Частота значений в массиве данных | Не перенесена | Composite legacy term needs explicit authored MathML |
| `/materials/7-statistics-17` | Группировка. Гистограммы | Перенесена | — |
| `/materials/7-statistics-18` | Практическая работа «Случайная изменчивость» | Не перенесена | Missing section heading or anchor |
| `/materials/7-statistics-19` | Введение в теорию графов | Не перенесена | Unsupported attribute: dy |
| `/materials/7-statistics-20` | Степень вершины | Перенесена | — |
| `/materials/7-statistics-21` | Цепи и цикл. Пути в графе | Перенесена | — |
| `/materials/7-statistics-22` | Понятие эйлерова графа. Ориентированные графы | Перенесена | — |
| `/materials/7-statistics-23` | Случайный опыт и случайное событие | Перенесена | — |
| `/materials/7-statistics-24` | Вероятность и частота события | Готов документ; CSS блокирует | Probability scale depends on page.css (.ms-scale-track and midpoint pseudo-element); React delivery excludes page.css. Shared UI/CSS agreement required. |
| `/materials/7-statistics-25` | Монета и игральная кость в теории вероятностей | Не перенесена | Unreviewed lesson root block: div |
| `/materials/7-statistics-26` | Практическая работа «Частота выпадения случайного события» | Не перенесена | Missing section heading or anchor |
| `/materials/7-statistics-27` | Обобщение, систематизация знаний | Не перенесена | Unsupported source tag: linearGradient |

## Review и приёмка

Scoped самопроверка завершена с ограничениями. Независимое review **PENDING**, ручная визуальная/педагогическая приёмка **PENDING**, HTTP/hydrated UI **NOT VERIFIED**, merge **NOT PERFORMED**.
Предметный interactive — принятый LinearGraph пилота; math/interaction unit tests прошли. Новых интерактивов не добавлено. Остальные схемы статичны; CSS-only диаграммы блокируются явно. Полная ручная проверка всех 75 тем и особых графиков не выполнена и не заявляется.
