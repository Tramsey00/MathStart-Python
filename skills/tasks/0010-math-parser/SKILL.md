---
name: mathstart-0010-math-parser
description: Выполнить MS-N010 — Ограниченный математический parser и normalizer. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N010 — Ограниченный математический parser и normalizer

## Передача на ревью

Реализация **READY_FOR_REVIEW**, независимое ревью и человеческая приёмка
ожидаются. [Issue #92](https://github.com/Tramsey00/MathStart-Python/issues/92).
SHA/tree, точные команды и результаты фиксируются в связанном PR.

- Серверные точки входа — `backend.math_validation.parser.parse_expression` и
  `parse_batch`. В них передаётся математическое поле payload и профиль версии
  упражнения. `ParseResult.raw` сохраняет это поле дословно. Отдельный
  `raw_text` шага остаётся у Assessment, в том числе когда в нём есть запись
  перехода с `->`, как в fixture R02. Профиль `None` означает
  `NOT_REQUIRED`.
- `arithmetic_v1`, `algebra_scalar_v1` и `probability_fraction_v1` дают
  точное скалярное значение. `algebra_linear_v1` также поддерживает
  коэффициенты при `x` и уравнения. Для уравнения доступны оба исходных
  нормализованных члена равенства и тип множества решений. Строка
  `normalized_repr` воспроизводит `Eq(2*x + 6, 10)` из R02.
- Умножение без знака поддержано для числа перед `x` или открывающей
  скобкой по примерам R02. Запись `1/2x` получает `UNSUPPORTED`.
  Если её нужно принимать, требуется решение пользователя о приоритете
  деления и неявного умножения. Однозначные записи `(1/2)*x` и `1/(2x)`
  различаются, вторая получает `VARIABLE_DENOMINATOR`. Степень задаётся
  целым литералом с допустимым знаком, в том числе в скобках.
- Один изолированный процесс обрабатывает пакет. Родитель прекращает его
  после 250 мс на выражение или 2 с на пакет и сохраняет уже полученные
  результаты. Дополнительный предел роста числителя и знаменателя
  вычисляется из лимитов токенов и цифр (6144 бита). Поля с отказом имеют
  `value=None` и `normalized_repr=None`. Пакет сверх 40 элементов или
  64 КиБ разбираемых полей возвращает `rejection` и пустой список результатов.
  Предел полного HTTP-запроса применяется на транспортном уровне.
- Модуль готов к вызову вне транзакции БД. Подключение к оцениванию и
  проверка переходов относятся к MS-N011. Parser API возвращает только
  результат разбора и причину отказа. Изменения схемы и новые зависимости
  для реализации не требуются.

## Проблема, цель и текущее состояние

Получать exact typed mathematical representation с предсказуемыми отказами.

Исходные доказательства: R02 parser profiles/fixtures задают границы; production parser пока нет, SymPy не включён.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N009. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
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
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Расширение grammar/limits и новая dependency требуют review; нельзя повышать limits для прохождения adversarial tests.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
