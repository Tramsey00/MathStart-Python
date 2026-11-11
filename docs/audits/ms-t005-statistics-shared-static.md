# MS-T005 — интеграция двух fixes статистики и статический разбор

Дата: 08.11.2026. Это новый scoped execution record; прежние audits, receipts,
логи, подтверждения и результаты не редактируются и не подтверждают этот candidate.

## Git и точный scope

Checkout: `C:/Users/User/PycharmProjects/MathStart-host-check`.
Ветка: `ms-t005-grade-7`; вход: `318b9d941a162bca6f8c9f428e53113cb25962a3`.
Начальное рабочее дерево чистое; существующая работа сохранена на месте,
ignored runtime-файлы не перемещались и не изменялись.
Backup: `backup/ms-t005-before-statistics-fixes-20261108-318b9d9` на входном HEAD.
Origin: `https://github.com/Tramsey00/MathStart-Python.git`.

Получены через `git fetch origin <полный SHA>` и перенесены по одному:

| Исходный commit | Результат cherry-pick -x | Единственный файл |
| --- | --- | --- |
| b57b692d3f31017bbfd2c66fa71231140a7a923a | 85b30aa2d78462b20345f9158b45ec95c900025f | frontend/scripts/convert-lesson.mjs |
| ee2c1d3cbed451c62addee20b0ab66d4688935c5 | 05e42b9f6cb8a0fbe61ac5e8c6edd41118923ccc | backend/content/sources.py |

Конфликтов не было. Не переносились диапазон, вся ветка или PR #63.
Implementation candidate: `05e42b9f6cb8a0fbe61ac5e8c6edd41118923ccc`.
Последующий отдельный commit меняет только текущую документацию и карту.

Ручное чтение `git show`, `git diff <backup> HEAD`, `git log`:
суммарно в двух общих файлах **19 добавлений, 3 удаления**. Дополнительных правок
реализации нет. Предыдущие SVG/HTML/img/URL/math правила сохранены: diff не меняет
их строки. Никаких учебных материалов других классов или 7 класса не изменено.
Canonical/redirects, Content registry, renderer, CSS и helper не менялись;
адреса `/materials/7-algebra-1` и `/materials/7-algebra-8` сохранены.

## Что меняют правила по исходникам

Converter добавляет пять terminal titles: «Практические задания», «Задания и
проверка», «Проверь исследование», «Задания по результатам опыта», «Итоговая
самопроверка». Существующий cleanSectionTitle удаляет числовой префикс.
Остальной порядок неизменен: direct root section требует direct h2 и id;
после конвертации terminal section следующие root blocks не читаются.
Все children terminal section, кроме заголовка, остаются входом конвертации.
Это не исправляет более ранний root figure, nested heading или unsupported SVG.

Validator сохраняет прежний margin-top допуск и добавляет только HTML div,
не SVG, с точным набором классов {ms-bar-fill} или {ms-equalizer-bar}.
В первом случае допустимы width 37.5/62.5/50/75/100/83.333/66.667/33.333%,
во втором height 72/96/120px. Другие размеры/составные styles/классы не получают
нового допуска. Это статическое чтение условий, не исполненная проверка.

## Восемь тем: статическое заключение

Точные source directories и элементы/строки по каждой теме приведены в
[текущем списке](../tasks/ms-t005-remaining.md). В карте старые наблюдавшиеся
ошибки сохранены, новый static_assessment явно отделён от них.

### 7-statistics-4 — Практическая работа «Таблицы»

`curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/04-prakticheskaya-rabota-tabliczy/body.html`.

body.html:42 «Практические задания» теперь распознаётся как terminal self-check; потенциально исключает поздний root div :112.

Конвертация/валидация не повторялись; сверить все задания/ответы внутри terminal section и границу исключения следующих разделов.

### 7-statistics-7 — Чтение и построение диаграмм

`curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html`.

body.html:47–52: div.ms-bar-fill, width 37.5/62.5/50/75/100/50% совпадают с новым узким допуском.

Оформление ms-bars/ms-bar-track/ms-bar-fill отсутствует в текущих lesson/runtime CSS. Нужны отдельно согласованное scoped оформление, фактическая конвертация/валидация и визуальная сверка данных.

### 7-statistics-8 — Практическая работа «Диаграммы»

`curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html`.

body.html:46 «Задания и проверка» теперь terminal; :80 width 100/83.333/66.667/50/33.333% совпадают с допуском. Потенциально обходится поздний root div :128.

Нет полного scoped оформления столбцов и authored ms-pie-practice. page.css:2–10 задаёт доли 30/25/20/15/10%, которые нельзя подменять generic pie. Сверить задания/ответы и исключаемые «Заполненная таблица» :107 / «Результат работы» :124; конвертация/валидация не выполнялись.

### 7-statistics-9 — Числовые наборы. Среднее арифметическое

`curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe/body.html`.

body.html:55–59: div.ms-equalizer-bar height 72/96/120/96/96px совпадают с новым допуском.

В source :41 словесная ms-frac («сумма всех чисел» / «количество чисел») требует поформульного MathML, без изменения helper; прежние overrides не доказывают новый candidate. Scoped equalizer CSS отсутствует. Нужны конвертация/валидация и визуальная сверка.

### 7-statistics-18 — Практическая работа «Случайная изменчивость»

`curriculum/7-klass/veroyatnost-i-statistika/03-sluchajnaya-izmenchivost/04-prakticheskaya-rabota-sluchajnaya-izmenchivost/body.html`.

body.html:121–122 section#lesson-section-6 «Проверь исследование» теперь terminal; потенциально обходятся section без id :133 и root div :143.

Сверить все 8 заданий/ответов и согласованную границу terminal section. Реальные конвертация/валидация не выполнялись.

### 7-statistics-25 — Монета и игральная кость в теории вероятностей

`curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/03-moneta-i-igralnaya-kost-v-teorii-veroyatnostej/body.html`.

Новые правила не устраняют прежнюю раннюю структурную причину; «5. Задания для самопроверки» :114 распознавалось ранее.

body.html:68 meaningful root div.ms-figure с SVG монеты/кости находится до self-check. Нужен согласованный структурный адаптер с сохранением SVG, подписи и порядка; не удалять figure.

### 7-statistics-26 — Практическая работа «Частота выпадения случайного события»

`curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13/body.html`.

body.html:164 «6. Задания по результатам опыта» распознаётся после удаления номера; потенциально исключает поздний nav :232, если достигнут.

body.html:21 section#theory имеет h2 :24 внутри ms-lab-header, а converter требует direct h2. Root div.ms-figure :76 с SVG тоже остаётся неподдержанным. Нужен согласованный адаптер структуры; terminal fix не устраняет эти ранние препятствия.

### 7-statistics-27 — Обобщение, систематизация знаний

`curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html`.

body.html:465 «7. Итоговая самопроверка» распознаётся после удаления номера; потенциально исключает поздний section без id :606.

body.html:250–252 linearGradient/stop и offset/stop-color по-прежнему не поддержаны. Дополнительно по исходникам :492/:494/:582/:584 ms-frac-num/ms-frac-den не совпадают с ожидаемыми helper ms-num/ms-den (math-notation.mjs:61–63): прогноз последующей ошибки Incomplete legacy fraction, не результат запуска. Нужны согласованная поддержка градиента и поформульный MathML/адаптация без потери математики.

## Результаты и ограничения

- Ручное чтение Git diff/history и HTML/CSS/converter/helper/validator исходников выполнено; конфликтов не обнаружено.
- Tests, typecheck, Playwright, smoke, validators, gates и любые QA-скрипты: **NOT_RUN_BY_USER_REQUEST**.
- Повторная конвертация и фактическая валидация восьми тем: **NOT_RUN_BY_USER_REQUEST**. Ни одна не объявлена разблокированной по статическому анализу.
- Активация, release build, publication, обновление installed Content snapshot: **NOT_PERFORMED**.
- БД, .venv, var/local и штатные validation guards не менялись/не отключались.
- 67/75 source activations сохранены (66 MIGRATED + 1 REUSED_PILOT), восемь BLOCKED_DEPENDENCY. Runtime readiness и сохранность нового candidate выполнением проверок не доказаны.
- Independent review и human visual/pedagogical acceptance **PENDING**. Issue #61 не закрыта, merge не выполнялся.

Следующие действия требуют отдельного поручения: фактическая конвертация/валидация,
согласованные adapters для figures/nested heading/градиентов, MathML и scoped
CSS диаграмм, затем сохранность/визуальная проверка перед любой активацией.
Нельзя удалять задания, ответы, SVG или данные ради успешной обработки.
