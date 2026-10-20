---
name: mathstart-0002-ui-library-decision
description: Выполнить MS-N002 — Выбор UI-библиотек под принятый дизайн. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N002 — Выбор UI-библиотек под принятый дизайн

## Проблема, цель и текущее состояние

Выбрать минимальный поддерживаемый frontend stack по требованиям и фактическому React/SSG.

Исходные доказательства: React 19.2.8, Router 7.18.4, TypeScript 5.9.3, Vite 7.3.7; принятой компонентной библиотеки нет.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N001. Путь skill каждой — в едином реестре.
Исторические IDs: новое направление, прежней карточки нет.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `docs/specifications/technical-spec-v7.2-draft.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Сравнить разумные кандидаты и вариант развития текущих компонентов: лицензии, accessibility/focus, темы/tokens, prerender/hydration, math/graphs, bundle и сопровождение. Не обновлять пакеты только ради новизны.

Затрагивается: frontend/package.json/package-lock.json, react-router.config.ts; ARCHITECTURE.md и новый decision/ADR.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Оценить отсутствие влияния на публичные DTO и server-only validation. Новых API нет.
- Frontend: Изолированные spikes на репрезентативных компонентах и длинном контенте; сравнить фактические artifacts/размер, не маркетинговые обещания.
- Интеграция и рекомендуемый порядок: Прочитать принятое направление, проверить текущие official docs/лицензии и совместимость, провести малый SSG spike, представить tradeoffs; installation в продукт после решения.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

No-JS theory, server build без browser globals, hydration mismatch, unknown math renderer, high-contrast/focus, отсутствие пакета в locked окружении.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Decision matrix с точными проверенными версиями/источниками и рекомендацией; пользователь выбирает stack; обновление архитектуры отличает выбранное от установленного.

Необходимые проверки: Locked install/build/typecheck/tests в отдельном spike; license review; фиксировать результаты и ограничения. Не считать spike полной runtime проверкой.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

ADR/decision, spike evidence, impact/rollback plan.
Одна ветка от проверенного main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Новая dependency и license/security выбор требуют решения пользователя. Без него не переносить spike в продукт.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.
