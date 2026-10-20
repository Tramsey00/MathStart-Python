---
name: mathstart-0001-visual-directions
description: Выполнить MS-N001 — Три визуальных направления и выбор пользователя. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N001 — Три визуальных направления и выбор пользователя

## Проблема, цель и текущее состояние

Получить осознанный выбор нового визуального направления на сравнимых учебных сценариях.

Исходные доказательства: Бриф docs/ux/redesign-brief.md основан на routes/source audit; I01 содержит low-fidelity SVG и state matrix. Новый actual screen audit ещё нужен.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N000. Путь skill каждой — в едином реестре.
Исторические IDs: новое направление, прежней карточки нет.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `docs/specifications/technical-spec-v7.2-draft.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Подтвердить бриф на существующем сайте, составить findings с экраном/действием/следствием; подготовить три различимых направления на одинаковых теме, упражнении и прогрессе, desktop/mobile и состояниях. У будущих экранов помечать synthetic данные.

Затрагивается: docs/ux/, frontend/src/app/ как read-only источник, I01 wireframes/states; backend и БД не меняются.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Сверить реальные DTO/owner/secrecy/retry состояния; новых endpoints не вводить.
- Frontend: Макеты и interactive prototype вне продуктовых routes. Проверить длинный урок, формулы/SVG, ввод/feedback, list alternative прогресса, keyboard/focus/contrast/reduced motion.
- Интеграция и рекомендуемый порядок: Сначала actual screen audit и одинаковый контент, затем три направления и сравнительная таблица; показать пользователю точные версии макетов и записать выбор до library/design-system работ.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

360/768/1440, длинная формула/заголовок, пустой progress, unsupported, network error, AI unavailable; отсутствие working assessed runtime не маскируется.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Три различимых варианта с одной матрицей экранов/состояний; сопоставлены учебное удобство, возрастная уместность, стоимость сопровождения и геймификация; явное решение пользователя либо BLOCKED_DECISION.

Необходимые проверки: Просмотр каждого макета; contrast/keyboard/focus walkthrough для interactive prototype; проверка ссылок и перечня экранов. Product runtime checks N/A с объяснением, если код продукта не изменён.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Версионированные макеты, comparison, findings, decision receipt и review record в docs/ux/.
Одна ветка от проверенного main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Палитра/шрифты/персонаж/библиотека не утверждаются агентом. Без выбора пользователя остановить зависимые задания.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.
