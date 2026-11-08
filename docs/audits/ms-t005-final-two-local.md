# MS-T005 — последние две темы, локальный candidate 75/75

Этап по явному поручению пользователя; push запрещён. Source activation и
человеческая визуальная приёмка разделены. Исторические audits/receipts не переписаны.

## Исходное состояние и сохранение работы

Checkout: C:/Users/User/PycharmProjects/MathStart-host-check.
Ветка ms-t005-grade-7, входной HEAD **39545fd8d68057a9a76fe2f2635e544fc62a9f51**.
Origin https://github.com/Tramsey00/MathStart-Python.git.
Backup branch: backup/ms-t005-before-shared-final-two-20261108-39545fd.
Исходно были ровно два untracked-файла, прочего dirty tree не было:

- docs/tasks/ms-t005-structural-overrides.json;
- frontend/scripts/ms-t005-final-statistics.mjs.

Выполнен только адресный stash:

```
git stash push -u -m "MS-T005 abandoned local adapters preserved before shared fixes" -- docs/tasks/ms-t005-structural-overrides.json frontend/scripts/ms-t005-final-statistics.mjs
```

Stash commit **65fc4aa87ea42683831b713f8b6e0fdda209339b** (на момент создания stash@{0}).
`git hash-object` до stash и `git ls-tree -r <stash>^3` после дали те же blob ids:

| Файл | Git blob |
| --- | --- |
| structural-overrides.json | 85eaedc150e3d8914df765e4cb41bbed75510c34 |
| ms-t005-final-statistics.mjs | adbac4118a4b57e2feaafca23ee6a4662f6f9c8b |

Сохранность проверена сопоставлением этих значений. Stash не применялся и не удалялся;
старые adapters не коммитились и не использовались для новой обработки.
frontend/.cache/ms-t005-final-statistics/ оставлен без изменений; новые outputs
пишутся в отдельный frontend/.cache/ms-t005-final-shared/.
Не восстанавливать старые adapters поверх новых файлов без отдельного решения.

## Точные общие исправления

Выполнен `git fetch origin ms-t003-grade5-migration`.
В текущем HEAD до переноса не было cherry-pick записей обоих исходных SHA;
исходники converter ещё не содержали этих двух функций. Полные исходные diff
прочитаны вручную: оба меняют только frontend/scripts/convert-lesson.mjs.

| Исходный commit | Локальный cherry-pick -x |
| --- | --- |
| d919429fba6087b1cfa637ae93bd1e54dfbe01b9 | 00e1be561b56b000318a12f4666e5d789ba1f95f |
| 7ab82ee44d0bb0edc3111ea9f773aa0d107db97b | ca8041dcc2b68b7784e5bce020423e3897586e96 |

Перенесены строго по одному, в указанном порядке, без конфликтов.
Весь PR #63, ветка и другие commits не переносились.
Итоговый общий diff **+63/−2**, один файл. Дополнительных собственных правок
конвертера нет. Прежние terminal/gradient/dimensions/HTML/SVG/math правила сохранены
по чтению diff; это не проверка исполнения других уроков.

Root figure принимается только в проверенной структуре между retained sections,
конвертируется существующим convert и добавляется nodes.push в предыдущий раздел.
Nested heading извлекается только для точной лабораторной структуры theory;
из копии header удаляется один heading, остальные children сохраняются.

## Новая штатная обработка оригиналов

Converter candidate: ca8041dcc2b68b7784e5bce020423e3897586e96.
Вызов из checkout через `node --input-type=module -`: импорт существующего
convertLesson и `convertLesson(topic.source)` непосредственно для двух исходных
directories из migration map. Никаких временных адаптированных body.html,
structural/MathML overrides, старого adapter или ручного изменения content.json.

Результаты и свежие candidates сохранены в frontend/.cache/ms-t005-final-shared/.
Затем `python -B -`: импорт backend.content.sources.validate_lesson_document,
чтение каждого candidate и `validate_lesson_document(document, slug)`.
Guards не отключались/не обходились, failures не игнорировались.
После ручной source-сверки в curriculum скопированы те же валидированные bytes.
Повторная генерация теперь использует обычный converter/CLI и тот же встроенный
validator, локальный structural adapter для этих тем больше не требуется.

| Тема | Конвертация оригинала | Встроенная валидация | Секции | Задания/полные решения | SVG | Таблицы |
| --- | --- | --- | --- | --- | --- | --- |
| 7-statistics-25 | OK | OK | 5 | 10/10 | 1 | 1 |
| 7-statistics-26 | OK | OK | 6 | 8/8 | 1 | 1 |

В обеих темах source-блокировок не обнаружено. Штатная обработка разрешена явно;
это не suite/gate/QA. Другие 73 темы не конвертировались и не менялись.

## Ручная сверка сохранности

Исходники:

- curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/03-moneta-i-igralnaya-kost-v-teorii-veroyatnostej/body.html;
- curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13/body.html.

Чтением исходных HTML и подготовленных JSON (включая компактные представления
текста/attrs для чтения, без автоматических preservation assertions/gates)
сопоставлены текст, порядок, таблицы, SVG, атрибуты и все 18 заданий с решениями.

### Statistics-25

Порядок section ids: theory, lesson-section-2, lesson-section-3,
lesson-section-4, lesson-section-5. Синтетических секций нет.
Figure «Две простые вероятностные модели» присутствует один раз: **последний
элемент nodes раздела lesson-section-3**, после текста/кости/таблицы и перед
section-4. Caption, wrapper и SVG сохранены. ViewBox 0 0 920 520, xmlns,
role img и aria-label исходной математической монеты/кости не менялись.

Сохранены два круга О/Р (cx 165/295, cy 225, r 72) и две подписи P=1/2;
шесть граней 1–6, rect width/height 74, rx 17, позиции x=550/653/756,
y=135/245; подпись «каждая грань: P = 1/6». Фон/рамки, заключительная
подпись про равновозможность, все fill/stroke/text attrs и порядок SVG сохранены.
Таблица событий и матрица двух бросков ОО/ОР/РО/РР сохранены.

Сохранены все десять вопросов/полных решений: исходы монеты; решка 1/2;
четыре ordered outcomes; ровно один орёл; число 5 на кости; не меньше 4;
простые 2/3/5; повреждённая монета; (2;5) против (5;2); достоверное событие.
Последний учебный раздел — Самопроверка, исходный id lesson-section-5.
Поздний root div.ms-note «В задачах с монетой и костью не угадывают ответ…»
и legacy nav исключены по действующему self-check-last стандарту, записаны
в map disposition. Note не имел id; задания/ответы не вырезались.

### Statistics-26

Section ids: theory, lesson-section-2, lesson-section-3, lesson-section-4,
lesson-section-5, lesson-section-6. Синтетических секций нет.
Section theory.title = «Цель и оборудование»; вложенный h2 исключён один раз,
дублированного h2 среди nodes нет. Сохранён весь ms-lab-header:
цель сравнить наблюдаемую частоту с 1/2, четыре chips «монета», «таблица
наблюдений», «калькулятор», «50 бросков»; badge strong 50 и текст
«испытаний в пяти сериях по десять бросков», оба wrapper div/class сохранены.

Figure «Как менялась накопленная частота орла» один раз, **последний элемент
nodes lesson-section-3**, после таблицы/пояснения, перед разделом 4.
Таблица всех пяти последовательностей по десять О/Р сохранена, числа орлов
6/4/5/7/3, накоплено 6/10/15/22/25, частоты 0.60/0.50/0.50/0.55/0.50.
ViewBox 0 0 920 560, xmlns, role img и полная aria-label SVG сохранены.

Сохранены polyline points «230,190 365,260 500,260 635,225 770,260» и пять circles
в тех же координатах, r=9; обе оси, пять grid lines, метки 10/20/30/40/50 и
0.3–0.7; оранжевая линия y=260 x=150..820, stroke-dasharray 10 8, надписи
«Теоретическая вероятность», «P(орёл) = 0,5», названия обеих осей и все attrs.

Все восемь полных решений сохранены: 50 бросков, 25 орлов, 0.5 общая частота,
0.7 четвёртая серия, первое совпадение после 20, отклонения 0.2, осторожный
вывод по короткой серии, объединённая частота 53/100=0.53. Последний раздел
Самопроверка сохраняет lesson-section-6; последующий legacy nav исключён.

### Anchors, ссылки и оболочка

Все исходные section ids двух тем сохранены; в частности theory и section-3/4/5,
а у 26 также section-6. SVG не имели дополнительных локальных id/URL references.
Retained document nodes не содержат href на исключённые секции (href в них нет).
Старые hero/toc/nav заменены общим LessonPage shell по стандарту, без новых
anchors или искусственного раздела для рисунка. Source body.html не редактировались.
Визуальная проверка реального renderer/DOM, размеров/тем и HTTP не выполнялась.

## Source activation, локальные документы и статус

Commit source activation: **41a4bbc18d6961065b11c92a1a648f9af6465501**.
Два content.json, два lesson.json renderer_version=react-v1, два собственных
Content assignments statistics 25/26 и inventory assigned_path; чужие canonical,
redirects и маршруты алгебры 1/8 не менялись. Migration map обновлена только для
двух тем и итогов: **75/75 локально (74 MIGRATED + 1 REUSED_PILOT)**,
source blockers 0; предыдущие причины сохранены как исторические данные.

Следующий документационный commit обновляет INDEX, registry, remaining и task
skill; статус READY_FOR_REVIEW относится к локальному candidate. Independent
review и human visual/pedagogical acceptance остаются PENDING, не ACCEPTED.
Tests/typecheck/Playwright/smoke/QA/gates: **NOT_RUN_BY_USER_REQUEST**, не PASS.
Build, Content publication, snapshot update, merge/Issue closure: NOT_PERFORMED.
БД, .venv, var/local, FastAPI/host-dev config и процессы не менялись.

**Push не выполнен по прямому запрету пользователя.** Draft PR #62 не обновлялся;
удалённый candidate остаётся 39545fd, 73/75. Перед передачей прочитан итоговый Git
scope/status; stash сохраняется отдельно, не входит в branch diff.

## Будущая ручная визуальная приёмка

После отдельного разрешения на доставку candidate и штатное обновление snapshot:

1. /materials/7-statistics-25: два исхода монеты, шесть граней и вероятности,
   caption/aria-label, одно размещение рисунка после таблицы, все десять раскрытий.
2. /materials/7-statistics-26: один «Цель и оборудование», цель/четыре chips/badge;
   таблица пяти серий; один график, пять точек, оси/метки/линия 0.5, восемь раскрытий.
3. Обе страницы: theory, section-2..5 (для 26 также section-6), содержимое/anchors,
   reload/Back/slug redirects, каталог/поиск/breadcrumbs/соседние темы, terminal
   self-check без поздних блоков, no-JS/keyboard доступность ответов, 320/360/768/1440px,
   zoom, светлая/тёмная тема, читаемость и отсутствие overflow.
4. Приёмка всех 75 тем остаётся отдельным действием; предыдущие source/QA receipts
   не подтверждают визуальный результат этого candidate.

После локальных коммитов остановиться для согласования; push без нового разрешения
не выполнять. Старый stash не восстанавливать автоматически.
