---
name: mathstart-0015-progress-history
description: Выполнить MS-N015 — Прогресс, история и завершение onboarding. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N015 — Прогресс, история и завершение onboarding

## Проблема, цель и текущее состояние

Показать объяснимое знание и собственную историю без client-side начислений.

Исходные доказательства: Progress read projections N012 и real attempt UI N014; current onboarding хранит выбор без assessed initialization.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N014. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Skill/topic aggregate/list-map, recent attempts/errors/help, self-report marker, onboarding progress integration и resume.

Затрагивается: frontend account/progress/history, Progress/Users read APIs и accepted CompletionFact projections.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Owner pagination, topic PRIMARY denominator, no-evidence vs no mapping, self-report one-time policy и чтение без writes.
- Frontend: Mastery/confidence/status/coverage различимы, accessible list alternative графу, loading/error не подменяют нулями, raw feedback объясним.
- Интеграция и рекомендуемый порядок: Read DTO/aggregation tests → history pagination → progress list/map → onboarding integration → browser review.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Empty history/zero denominator, late event updates, neutral completion снимает MASTERED, foreign record, stale/offline data, archived topic.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

UI точно отражает server state и explanation; reading/XP не дают mastery; diagnostic placeholder не имитирует готовую N016.

Необходимые проверки: Aggregation/owner/API tests, frontend units и real browser accessibility/mobile/history scenarios.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Views/read contracts, state/denominator evidence и review.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Непринятые onboarding initialization решения вынести человеку; не использовать новый алгоритм в frontend.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
