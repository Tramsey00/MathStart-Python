---
name: mathstart-0010-math-parser
description: Выполнить MS-N010 — Ограниченный математический parser и normalizer. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N010 — Ограниченный математический parser и normalizer

## Проблема, цель и текущее состояние

Получать exact typed mathematical representation с предсказуемыми отказами.

Исходные доказательства: R02 parser profiles/fixtures задают границы; production parser пока нет, SymPy не включён.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N009. Путь skill каждой — в едином реестре.
Исторические IDs: MS7-R09.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `docs/specifications/technical-spec-v7.2-draft.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Whitelist grammar/lexer/AST, normalization numbers/signs/fractions/implicit multiplication и bounded isolated execution по ТЗ §9.

Затрагивается: backend/math_validation, versioned parser profiles и tests; dependency lock только при обоснованном выборе.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Raw отдельно; INVALID/UNSUPPORTED/OK/NOT_REQUIRED; exact rationals, никаких eval/exec/прямого sympify. Finite process deadline.
- Frontend: Read-only пример input/display normalization, UI не становится math truth.
- Интеграция и рекомендуемый порядок: Грамматика/limits → AST → exact normalization → isolated timeout/termination → public result contract.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Unicode minus, decimal comma, unary minus, nesting16, 512chars/128tokens, large literals/power, variable denominator, nonlinear/functions, adversarial input.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Supported pilot grammar reproducible; timeout/limit/unsupported не становятся wrong/misconception, resource limits проверены.

Необходимые проверки: Golden parser cases, invalid/worst-case/termination tests, no live LLM; verify_repo affected suites.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Parser/versioned profile, safety evidence, dependency review если нужен.
Одна ветка от проверенного main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Расширение grammar/limits и новая dependency требуют review; нельзя повышать limits для прохождения adversarial tests.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.
