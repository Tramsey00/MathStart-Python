---
name: mathstart-0017-product-provider
description: Выполнить MS-N017 — Product LLM provider, AIRun и безопасный fallback. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N017 — Product LLM provider, AIRun и безопасный fallback

## Проблема, цель и текущее состояние

Изолировать готовую LLM за bounded versioned product interface без прав на доменные данные.

Исходные доказательства: Product provider/AIRun отсутствуют; Pydantic установлен для HTTP, provider/model/budget не выбраны.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N016. Путь skill каждой — в едином реестре.
Исторические IDs: MS7-V11.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `docs/specifications/technical-spec-v7.2-draft.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Provider/model/budget/privacy decision, infrastructure adapter, schemas/prompt versions, redaction/usage, timeout/retry и deterministic fallback.

Затрагивается: backend/llm или infrastructure provider, AIRun persistence/Alembic, versioned prompts, fake test provider.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Общий12s/<=2 calls per action, no reset on retry, minimal context, unknown code/ref abstain, никакого direct Progress ORM.
- Frontend: Публичные available/degraded/unavailable состояния без provider secrets; safe existing action остаётся доступным.
- Интеграция и рекомендуемый порядок: Согласовать provider/budget/privacy → interface/fake → schema/domain gate → adapter → отдельно разрешённый live smoke.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Malformed JSON/schema, low confidence, timeout/rate/budget exhaustion, injection, SDK error, unavailable network, unknown usage/cost.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Обычные tests offline; bad output не создаёт strong negative; actual metadata без PII, provider outage не скрывает working core.

Необходимые проверки: Fake-provider schema/security/deadline/fallback tests; separate live evidence только после явного budget/provider approval.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Decision, adapter/AIRun/prompts/migrations, redacted smoke и limitations.
Одна ветка от проверенного main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

До provider/security/budget решения не делать live calls и не выдумывать цену. Новая SDK dependency через review.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.
