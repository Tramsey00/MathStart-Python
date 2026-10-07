# MathStart v7 PreG0 correction pass

Дата: 29.09.2026. Status: artifact preparation and verification complete; G0 approval pending.

Работа выполняется по прямому запросу пользователя из приложенного текста. Это редактура существующего v7, основанного на v6.0 от25.09.2026; новое ТЗ/v8 не создаётся. Product code, DB, GitHub, accepted ADR и frozen implementations не изменяются.

## Изменения и критерии

Удалить все оценки трудозатрат из ТЗ; заменить календарём NORMAL/EARLY по typed dependencies. Проверить отсутствие одновременно активной основной реализации у одного Owner и явно отделить review/integration-only windows. Для52future cards сохранить Detailed Scope и Negative acceptance, добавить31поле с осмысленными outcomes; вынести общий DoD. Разделить Reviewer/Task Approver/Milestone Gate; определить Gate Owner и approvers G0–G5. Устранить G0/post-G0 contract-closeout cycle, сохранив R02A/R03A как новые задачи. Классифицировать технические числа A/B/C без изменения значений. Сохранить architecture, course registry, real R04 failure history, v6→v7 mapping, requirements и frozen baseline. Graphify остаётся отдельно.

## Verification

Сопоставить protected sections с предыдущим v7; сравнить все52scope/negative/dependency records; проверить DAG и оба календаря машинно, поля карточек и forbidden planning phrases. Проверить DOCX integrity/TOC и все PDF pages: сначала структурно, затем visual. Runtime tests не повторяются для document-only correction, предыдущие результаты сохраняются как historical evidence. Штатный renderer не нашёл LibreOffice; использовать отдельный скрытый Word instance только с generated DOCX, экспорт PDF, затем Poppler. Итоговые4артефакта в output/tz-v7-preg0-2026-09-29/. До human acceptance план остаётся active.

## Результат

Четыре артефакта созданы; PDF/DOCX61страница. Все проверки A–P завершены PASS, подробности в Corrections и trace. План остаётся active только до отдельного human G0 acceptance.
