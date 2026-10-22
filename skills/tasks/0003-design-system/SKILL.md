---
name: mathstart-0003-design-system
description: Выполнить MS-N003 — Дизайн-система и доступные базовые компоненты. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N003 — Дизайн-система и доступные базовые компоненты

## Проблема, цель и текущее состояние

Превратить принятый дизайн в проверяемые tokens и компоненты без изменения учебной семантики.

Исходные доказательства: Общие authored styles живут в static/mathstart, React shells — frontend/src/app; библиотечный выбор должен быть принят MS-N002.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N002. Путь skill каждой — в едином реестре.
Исторические IDs: новое направление, прежней карточки нет.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `docs/specifications/technical-spec-v7.2-draft.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Tokens typography/spacing/color/themes/focus, navigation/forms/dialogs/feedback, math/content containers, loading/error/empty/degraded и reduced motion. Описать постепенное взаимодействие с legacy lesson CSS.

Затрагивается: frontend/src/, static/mathstart/ только общие границы; docs/ux/design-system, ARCHITECTURE.md stack после внедрения.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: DTO/auth/evidence semantics неизменны; проверить, что component examples не содержат private checker или credentials.
- Frontend: Реальные reusable components и development gallery, keyboard/focus/contrast/labels; scoped styles без массового reformat учебных HTML/SVG.
- Интеграция и рекомендуемый порядок: Сначала tokens и content boundaries, затем controls/states и gallery, затем component/browser checks; product rollout отдельно.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Long labels, multiline equations, narrow viewport, modal focus return, disabled/pending, dark/high-contrast если выбран, reduced motion.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Каждый компонент имеет согласованный variant/state contract и accessibility evidence; нет answer leakage или глобального CSS конфликта; stack отражает установленные версии.

Необходимые проверки: Frontend typecheck/unit tests и browser accessibility walkthrough; representative lesson visual inspection; semantic preservation.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Tokens/components/gallery, usage guidance и review evidence.
Одна ветка от проверенного main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Новые визуальные решения сверх MS-N001/002, включая mascot, возвращаются пользователю. Не начинать rollout до приёмки системы.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.
