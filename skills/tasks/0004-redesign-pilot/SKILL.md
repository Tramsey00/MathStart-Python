---
name: mathstart-0004-redesign-pilot
description: Выполнить MS-N004 — Пилот редизайна существующего учебного сценария. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N004 — Пилот редизайна существующего учебного сценария

## Проблема, цель и текущее состояние

Доказать новый дизайн на каталоге → теме → возврате без потери обучения и интерактивов.

Исходные доказательства: Существующие catalogue/topic URLs и LessonHost работают на immutable public build; будущие assessed endpoints отсутствуют.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N003. Путь skill каждой — в едином реестре.
Исторические IDs: новое направление, прежней карточки нет.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `docs/specifications/technical-spec-v7.2-draft.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Внедрить один согласованный existing flow с новым shell/navigation/content styling. Exercise/progress prototypes остаются отдельно до domain runtime.

Затрагивается: frontend public routes/layouts/LessonHost, shared static styles, public build tests; curriculum bytes сохраняются.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Сохранить authority/publication/no-JS/404/query semantics. SQL schema/API не изменять.
- Frontend: Принятые components/tokens; формулы, anchors, SVG/widgets, Back/scroll/focus, search state и responsive layout.
- Интеграция и рекомендуемый порядок: Выбрать pilot URLs и semantic baseline, затем shell/components, реальный immutable build, browser/visual QA и решение о rollout.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Прямой deep link/anchor, JS off, widget повторный mount, long content/mobile, unpublished URL, back из темы к фильтру.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Все pilot URLs и semantic assertions сохранены; пользователь принял actual visual result; visual baseline меняется только для утверждённых экранов.

Необходимые проверки: Frontend type/unit/build; owned runtime content checks и Chrome/Edge/Firefox ×360/768/1440 по затронутым сценариям; no-JS и просмотр screenshots.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Pilot implementation, URL/semantic mapping, visual evidence и rollout findings.
Одна ветка от проверенного main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Семантическая потеря/сломанный widget блокирует pilot. Protected local instance не становится disposable fixture.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.
