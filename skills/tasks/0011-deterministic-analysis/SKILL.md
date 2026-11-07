---
name: mathstart-0011-deterministic-analysis
description: Выполнить MS-N011 — Детерминированные validators и первый доказанный дефект. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N011 — Детерминированные validators и первый доказанный дефект

## Проблема, цель и текущее состояние

Определять final verdict и проверенный first-error без ложных причин.

Исходные доказательства: Parser N010 и R02 contracts; persisted finalization позже N013.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N010. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Exact final/transition/structured validators, controlled taxonomy/skill/evidence mapping, typed AnalysisResult с safe confidence/abstain.

Затрагивается: backend/math_validation, backend/solution_analyzer, Assessment interfaces и versioned golden fixtures.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Проверенный prefix; unsupported gap останавливает локализацию; wrong final не доказывает misconception; одна причинная ошибка не множит штраф.
- Frontend: Определить safe feedback и first-error/unsupported public states, без секретного checker текста.
- Интеграция и рекомендуемый порядок: Final rational checks → equivalence/transition rules → structured schemas → taxonomy/evidence gates → negative safety corpus.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

No/all solutions, equivalent fractions, cascade, unknown step, basic_arithmetic outside pilot, malformed result/ref, multiple independent errors.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Validated AnalysisResult не меняет UserSkillState; known deterministic verdict не переопределяется LLM; false strong negative=0 safety subset.

Необходимые проверки: Golden supported/invalid/unsupported/prefix/taxonomy tests; deterministic offline lane; timing/resource limits.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Validators/analysis schemas/fixtures, expected-vs-actual matrix и review.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Новая misconception taxonomy или rule semantics требует contract review; нельзя угадывать unsupported переход.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
