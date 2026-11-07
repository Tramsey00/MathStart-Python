---
name: mathstart-0012-progress-replay
description: Выполнить MS-N012 — ProgressEvent, CompletionFact, проекция и replay. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N012 — ProgressEvent, CompletionFact, проекция и replay

## Проблема, цель и текущее состояние

Транзакционно хранить и воспроизводить долгосрочное знание по принятому reducer.

Исходные доказательства: R03 exact Decimal reference и R03A CompletionFact draft; production Progress отсутствует.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N011. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Закрыть pending addendum decisions, event/mirror/state persistence, ingest/replay/version policy, self-report и real PG concurrency.

Затрагивается: backend/progress, immutable Assessment DTO, Knowledge references, Alembic; frozen R03/R03A fixtures.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Only Progress writes; exact deltas/clamp/ROUND_HALF_UP, global dual completion identity, neutral recent-ten, late event reproject, permanent dedupe.
- Frontend: Read models для mastery/confidence/status/coverage и own history, отдельно self-report; UI в N015.
- Интеграция и рекомендуемый порядок: Human contract closeout → schema/ingest constraints → online reducer adapter → replay/late delivery → concurrent conflict proof.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Same timestamp, duplicate/conflicting global ID under foreign owner, neutral completion changes status only, revealed version, repeat/reset, out-of-order ingestion.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Online/replay равны по всем state fields, progress-v1 compatibility сохранена; mirror не зависит от Assessment ORM; no evidence overwrite.

Необходимые проверки: R03/R03A pure parity + PostgreSQL concurrency/atomicity/fresh/upgrade/replay, exact immutable fixtures; no float.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Reviewed migrations/services, parity/concurrency report и retained policy-version mapping.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Нельзя изменять численные правила/порог ради реализации. Proposed CompletionFact пункты требуют явного решения, прежний approval не переносится.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
