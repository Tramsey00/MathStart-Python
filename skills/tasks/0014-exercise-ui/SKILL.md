---
name: mathstart-0014-exercise-ui
description: Выполнить MS-N014 — Четыре exercise UI, typed steps и help/reveal recovery. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N014 — Четыре exercise UI, typed steps и help/reveal recovery

## Проблема, цель и текущее состояние

Дать ученику реальные interaction modes с сохранением работы и доверия к серверу.

Исходные доказательства: Принятая design system, public exercise bank и persisted submit/help endpoints; legacy self-checks остаются отдельно.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N013, MS-N005. Путь skill каждой — в едином реестре.
Исторические IDs: MS7-I05, MS7-I06, MS7-I07, MS7-I09.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `docs/specifications/technical-spec-v7.2-draft.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

SELF_CHECK/final answer, ordered step editor, две structured schemas, hint/reveal confirmation, draft/revision/idempotency recovery.

Затрагивается: frontend exercise routes/components/clients, R02/R02A schemas, Assessment HTTP integration.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Устранить выявленные integration defects в рамках accepted contract; correctness/eligibility только серверные.
- Frontend: Raw work сохраняется, unknown schema controlled unsupported, pending/conflict не стирают новый ввод, reveal не скрытая DOM data; accessibility/keyboard.
- Интеграция и рекомендуемый порядок: Public dispatcher → simple final → ordered steps/structured → help/reveal/retry → real browser/server scenarios.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Double click, refresh/two tabs, out-of-order response, lost ACK, hint/reveal+submit race, screen reader, XSS payload, unknown schema/version.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Все четыре режима работают с реальным backend, no secret in HTML/JSON/JS/network до reveal, новый attempt не сбрасывает exposure.

Необходимые проверки: Type/unit/schema tests, no-JS theory, real browser matrix/owner/CSRF/secrecy/retry; visual screenshots просмотрены.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

UI/clients, state matrix evidence, corrected integration findings и user acceptance.
Одна ветка от проверенного main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Не менять modes/eligibility ради UI. Будущий free-form mathematical editor вне принятого parser не внедрять.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.
