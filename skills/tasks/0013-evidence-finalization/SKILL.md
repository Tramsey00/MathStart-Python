---
name: mathstart-0013-evidence-finalization
description: Выполнить MS-N013 — Atomic Analysis → Progress и аудит persisted loop. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N013 — Atomic Analysis → Progress и аудит persisted loop

## Проблема, цель и текущее состояние

Связать реальный submit, analysis, completion и progress в единую проверяемую операцию.

Исходные доказательства: Attempts/exposure N009, validators N011 и Progress N012 готовы отдельно.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N012. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Snapshot-bound operation/finalize, AnalysisRecord/CompletionFact/ProgressEvent/projection consistency и adversarial persisted evidence audit.

Затрагивается: Assessment services/HTTP, Progress ingest, UoW/locks/receipts; no direct Analyzer/Tutor state writes.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Computation вне long transaction; recheck snapshot/policy/exposure под locks; first positive per user/version, one defect/negative; uncertain commit reconciliation.
- Frontend: Typed polling/retry responses, pending/DEGRADED/unsupported и stable operation identity для N014.
- Интеграция и рекомендуемый порядок: Freeze/read facts → deterministic result → короткий atomic finalize → fault injection/parallel retry → independent domain review.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Crash до/после commit, reveal race, stale snapshot, double finalization, foreign user, duplicate source with changed payload, neutral completion.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Реальная PG история объясняет каждый state change; retry не дублирует evidence; leak/owner/transaction boundaries доказаны.

Необходимые проверки: Persisted end-to-end/PG concurrency/fault injection, replay equality, HTTP envelope/privacy и negative safety tests.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Finalization implementation, evidence-chain diagram и scoped audit findings/corrections.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Mismatch online/replay или unvalidated negative блокирует acceptance; не скрывать его synthetic response.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
