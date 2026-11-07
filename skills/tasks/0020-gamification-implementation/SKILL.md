---
name: mathstart-0020-gamification-implementation
description: Выполнить MS-N020 — Реализация только принятых игровых механик. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N020 — Реализация только принятых игровых механик

## Проблема, цель и текущее состояние

Внедрить согласованную мотивацию без изменения долгосрочного знания.

Исходные доказательства: Реализация разрешена только при принятой MS-N006 specification/ownership decision; concrete mechanics сейчас не выбраны.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N006, MS-N019. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Ровно выбранные mechanics, source/idempotency/limits, schema/API и UI; исключённые в решении кандидаты не реализуются.

Затрагивается: Пакеты/data owner/events определяются ADR MS-N006; frontend accepted design system, Alembic при persistence.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Trusted source events и permanent duplicate guard, transactional awards, replay/timezone по спецификации; никакого direct mastery mutation.
- Frontend: Отдельные game/knowledge indicators, explainable awards и доступные reduced-motion/empty/error состояния.
- Интеграция и рекомендуемый порядок: Повторно проверить actual decision → migration/award service → events/API → UI → concurrency/replay/visual QA.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Duplicate/late event, help/reveal/retry, no evidence, day/timezone boundary, undo/archive/deletion; значения ожидаемых awards берутся только из принятого spec.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Каждое начисление объяснимо source/rule/version, двойное невозможно; XP/streak/reading не создают ProgressEvent/mastery, выбранный UX принят.

Необходимые проверки: Spec-driven unit/PG concurrency/fresh/upgrade/replay; доказательство unchanged knowledge при game-only actions; browser/a11y/visual.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Implementation/migrations, rule/source matrix, evidence и acceptance.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Без принятого набора/owner/rules статус BLOCKED_DECISION. Если направление отложено пользователем, снять задачу с причиной; не пометить DONE.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
