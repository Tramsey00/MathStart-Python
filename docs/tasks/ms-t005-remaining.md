# MS-T005 — оставшиеся 2 темы статистики

73/75 source activations: 72 новых документов и принятый пилот.
Шесть тем statistics-4/7/8/9/18/27 фактически конвертированы неизменённым
convertLesson, прошли штатный validate_lesson_document, вручную сопоставлены
с исходниками и активированы через react-v1/Content registry.
[Текущий execution record](../audits/ms-t005-six-statistics-activation.md).
Браузерная визуальная/педагогическая приёмка **PENDING_NOT_PERFORMED**.
Tests/typecheck/Playwright/smoke/отдельные QA/gates: **NOT_RUN_BY_USER_REQUEST**.
Это не относится к явно порученной штатной конвертации/встроенной валидации,
которые выполнены для всех шести. Snapshot не обновлялся, HTTP/runtime не проверен.

Ниже два прежних blockers. Темы 25/26, их исходники и записи карты на этом этапе
не менялись и не обрабатывались заново. Причины — результаты предыдущих этапов,
а не нового запуска. Исторические audits/receipts/logs не переписаны.

## /materials/7-statistics-25 — Монета и игральная кость в теории вероятностей

Source: `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/03-moneta-i-igralnaya-kost-v-teorii-veroyatnostej`.

Потенциальный эффект: Новые правила не устраняют прежнюю раннюю структурную причину; «5. Задания для самопроверки» :114 распознавалось ранее.

Остаётся / требуется: body.html:68 meaningful root div.ms-figure с SVG монеты/кости находится до self-check. Нужен согласованный структурный адаптер с сохранением SVG, подписи и порядка; не удалять figure.

## /materials/7-statistics-26 — Практическая работа «Частота выпадения случайного события»

Source: `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13`.

Потенциальный эффект: body.html:164 «6. Задания по результатам опыта» распознаётся после удаления номера; потенциально исключает поздний nav :232, если достигнут.

Остаётся / требуется: body.html:21 section#theory имеет h2 :24 внутри ms-lab-header, а converter требует direct h2. Root div.ms-figure :76 с SVG тоже остаётся неподдержанным. Нужен согласованный адаптер структуры; terminal fix не устраняет эти ранние препятствия.

## Следующие действия — отдельное поручение

Для Владимира: согласованные структурные исправления meaningful root figures
25/26 и nested heading 26 с сохранением SVG, подписи, порядка, заданий и ответов.
После интеграции — отдельно порученные фактическая конвертация и штатная валидация.

Для ручного браузерного просмотра новых шести тем — список в execution record:
диаграммы, MathML, SVG, 50 раскрываемых ответов, terminal boundaries, якоря,
мобильная ширина, светлая/тёмная тема и навигация. Визуальная приёмка ещё не проведена.
Установленный snapshot не менять без отдельного поручения.

Адреса алгебры 1/8 сохранены, 37 не создавать. Independent review/human acceptance
PENDING; release build, публикация, merge и закрытие Issue #61 не выполнялись.
