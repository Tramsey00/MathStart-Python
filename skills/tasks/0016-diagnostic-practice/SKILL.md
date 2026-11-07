---
name: mathstart-0016-diagnostic-practice
description: Выполнить MS-N016 — Диагностика и adaptive practice с возвратом. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N016 — Диагностика и adaptive practice с возвратом

## Проблема, цель и текущее состояние

Замкнуть короткую целевую практику по prerequisite и возврат в исходную тему.

Исходные доказательства: Knowledge, bank, attempts, progress готовы; selector/session runtime ещё отсутствует.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N015. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Versioned deterministic policy, DiagnosticSession <=10, PracticeSession/Item, next/finish/abandon, real UI и origin fallback.

Затрагивается: backend/adaptive_practice, Assessment diagnostics/services, frontend practice/diagnostic, migrations.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Depth2/mastery/confidence ordering, supported published candidates, max7/streak3, repeat/no-candidate semantics и одна active session.
- Frontend: Target/reason/count, unsupported/skip/degraded/no candidate, refresh resumes item; return topic/parent/catalogue без тупика.
- Интеграция и рекомендуемый порядок: Policy fixtures → persistence/idempotency → selection/finalization integration → real UI/return flow.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Pool exhausted, revealed versions, unknown skill, confidence<30 difficulty fallback, concurrent next, archive origin, abandon/offline.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Exact §10 selection/stop rules и нейтральность skip/unsupported, stable item under refresh, real evidence path и доступный возврат.

Необходимые проверки: Policy golden tests, real PG concurrency/session/atomicity/fresh/upgrade, browser full loop и replay.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Policy/session API/UI, candidate/return evidence и review.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Изменение selection/stop semantics требует human contract decision; случайный порядок без seed не вводить.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
