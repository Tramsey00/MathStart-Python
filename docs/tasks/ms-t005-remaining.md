# MS-T005 — оставшиеся 8 тем статистики

## Текущий этап: общие fixes и только статический разбор

67/75 source activations сохраняются (66 новых + принятый пилот). Восемь тем ниже
остаются `BLOCKED_DEPENDENCY`: ни одна не объявлена разблокированной или активированной.
Фактическая конвертация и валидация после двух новых fixes ещё не подтверждены.
Автоматические проверки, повторная конвертация и валидация — **NOT_RUN_BY_USER_REQUEST**.

Интегрированы b57b692 → 85b30aa и ee2c1d3 → 05e42b9 строго через cherry-pick -x.
[Execution record](../audits/ms-t005-statistics-shared-static.md) содержит scope/diff и ограничения.
Прежние наблюдавшиеся ошибки сохранены в полях blockers/инвентаризации
[карты](ms-t005-migration-map.json); они исторические, не результаты нового запуска.
Новые `static_assessment` отделены от них. Исторические audits/receipts не переписаны.

## /materials/7-statistics-4 — Практическая работа «Таблицы»

Source: `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/04-prakticheskaya-rabota-tabliczy`.

Потенциальный эффект: body.html:42 «Практические задания» теперь распознаётся как terminal self-check; потенциально исключает поздний root div :112.

Остаётся / требуется: Конвертация/валидация не повторялись; сверить все задания/ответы внутри terminal section и границу исключения следующих разделов.

## /materials/7-statistics-7 — Чтение и построение диаграмм

Source: `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm`.

Потенциальный эффект: body.html:47–52: div.ms-bar-fill, width 37.5/62.5/50/75/100/50% совпадают с новым узким допуском.

Остаётся / требуется: Оформление ms-bars/ms-bar-track/ms-bar-fill отсутствует в текущих lesson/runtime CSS. Нужны отдельно согласованное scoped оформление, фактическая конвертация/валидация и визуальная сверка данных.

## /materials/7-statistics-8 — Практическая работа «Диаграммы»

Source: `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy`.

Потенциальный эффект: body.html:46 «Задания и проверка» теперь terminal; :80 width 100/83.333/66.667/50/33.333% совпадают с допуском. Потенциально обходится поздний root div :128.

Остаётся / требуется: Нет полного scoped оформления столбцов и authored ms-pie-practice. page.css:2–10 задаёт доли 30/25/20/15/10%, которые нельзя подменять generic pie. Сверить задания/ответы и исключаемые «Заполненная таблица» :107 / «Результат работы» :124; конвертация/валидация не выполнялись.

## /materials/7-statistics-9 — Числовые наборы. Среднее арифметическое

Source: `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe`.

Потенциальный эффект: body.html:55–59: div.ms-equalizer-bar height 72/96/120/96/96px совпадают с новым допуском.

Остаётся / требуется: В source :41 словесная ms-frac («сумма всех чисел» / «количество чисел») требует поформульного MathML, без изменения helper; прежние overrides не доказывают новый candidate. Scoped equalizer CSS отсутствует. Нужны конвертация/валидация и визуальная сверка.

## /materials/7-statistics-18 — Практическая работа «Случайная изменчивость»

Source: `curriculum/7-klass/veroyatnost-i-statistika/03-sluchajnaya-izmenchivost/04-prakticheskaya-rabota-sluchajnaya-izmenchivost`.

Потенциальный эффект: body.html:121–122 section#lesson-section-6 «Проверь исследование» теперь terminal; потенциально обходятся section без id :133 и root div :143.

Остаётся / требуется: Сверить все 8 заданий/ответов и согласованную границу terminal section. Реальные конвертация/валидация не выполнялись.

## /materials/7-statistics-25 — Монета и игральная кость в теории вероятностей

Source: `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/03-moneta-i-igralnaya-kost-v-teorii-veroyatnostej`.

Потенциальный эффект: Новые правила не устраняют прежнюю раннюю структурную причину; «5. Задания для самопроверки» :114 распознавалось ранее.

Остаётся / требуется: body.html:68 meaningful root div.ms-figure с SVG монеты/кости находится до self-check. Нужен согласованный структурный адаптер с сохранением SVG, подписи и порядка; не удалять figure.

## /materials/7-statistics-26 — Практическая работа «Частота выпадения случайного события»

Source: `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13`.

Потенциальный эффект: body.html:164 «6. Задания по результатам опыта» распознаётся после удаления номера; потенциально исключает поздний nav :232, если достигнут.

Остаётся / требуется: body.html:21 section#theory имеет h2 :24 внутри ms-lab-header, а converter требует direct h2. Root div.ms-figure :76 с SVG тоже остаётся неподдержанным. Нужен согласованный адаптер структуры; terminal fix не устраняет эти ранние препятствия.

## /materials/7-statistics-27 — Обобщение, систематизация знаний

Source: `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij`.

Потенциальный эффект: body.html:465 «7. Итоговая самопроверка» распознаётся после удаления номера; потенциально исключает поздний section без id :606.

Остаётся / требуется: body.html:250–252 linearGradient/stop и offset/stop-color по-прежнему не поддержаны. Дополнительно по исходникам :492/:494/:582/:584 ms-frac-num/ms-frac-den не совпадают с ожидаемыми helper ms-num/ms-den (math-notation.mjs:61–63): прогноз последующей ошибки Incomplete legacy fraction, не результат запуска. Нужны согласованная поддержка градиента и поформульный MathML/адаптация без потери математики.

## Следующие действия — отдельное поручение

1. Разрешённая фактическая конвертация и штатная валидация всех восьми тем с сохранением результатов; static review не заменяет их.
2. Для Владимира: согласовать поддержку meaningful root figures (25/26), nested heading (26), SVG gradient/stop (27), сохраняя данные, порядок и SVG. Не переносить всю ветку/PR #63.
3. Для 7/8/9 отдельно согласовать scoped CSS диаграмм, затем визуальную/мобильную/светлую/тёмную проверку; не удалять размеры, подписи или данные. Для 9/27 нужна согласованная поформульная MathML-адаптация без изменения общего helper.
4. Перед активацией подтвердить сохранность каждого задания, ответа, формулы, SVG, таблицы, URL и якоря, включая согласованную terminal boundary 4/8/18/26/27. Не объявлять успех по одному анализу исходников.

Утверждённые адреса алгебры неизменны: 1 — первая тема, 8 — линейный пилот,
37 не создавать. Installed snapshot не обновлялся. Independent review и human
acceptance PENDING; публикация и merge не выполнялись, Issue #61 остаётся открыта.
