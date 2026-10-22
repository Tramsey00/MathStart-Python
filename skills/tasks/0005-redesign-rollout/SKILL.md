---
name: mathstart-0005-redesign-rollout
description: Выполнить MS-N005 — Поэтапное внедрение редизайна текущего сайта. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N005 — Поэтапное внедрение редизайна текущего сайта

## Проблема, цель и текущее состояние

Привести существующие public/account/staff поверхности к принятой системе и сохранить текущие contracts.

Исходные доказательства: MS-N004 доказывает pilot; I04 catalogue/renderer требования частично перекрыты принятым переносом, будущий exercise renderer ещё нужен MS-N014.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N004. Путь skill каждой — в едином реестре.
Исторические IDs: MS7-I04.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `docs/specifications/technical-spec-v7.2-draft.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

По группам public pages, catalogue/topic, account/profile и staff внедрить design system; зафиксировать фактически уже выполненный I04 scope, не выдать будущие exercises за готовые.

Затрагивается: frontend layouts/routes, static shared styles, rendering/build; auth/content/staff contracts.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Сохранить permission/CSRF/opaque session/publication authority; API изменения только отдельным согласованным addendum.
- Frontend: Единая navigation и feedback, responsive/accessibility states; сохранение GET search, URL/anchors/math/lesson lifecycle.
- Интеграция и рекомендуемый порядок: Определить cohorts и rollback, внедрять одну группу за раз с semantic+visual QA; account/staff после public layout, затем общий проверенный candidate.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Private no-store, logout/session expiry, permission denial, revision conflict, long catalogue, media error, unknown URL, browser Back.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Полная карта существующих экранов и матрица состояний; согласованный дизайн и semantic preservation; assessed placeholders не имитируют runtime.

Необходимые проверки: Полный affected frontend и target content/auth/staff checks, public build/browser matrix; install/recovery при изменении артефактов доставки.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Rollout record по cohorts, обновлённые visual references, review/acceptance evidence.
Одна ветка от проверенного main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Новый functionality/дизайн за пределами выбора не добавлять. При regression вернуть scoped cohort, сохранив данные.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.
