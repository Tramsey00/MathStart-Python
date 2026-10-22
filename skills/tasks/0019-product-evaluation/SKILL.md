---
name: mathstart-0019-product-evaluation
description: Выполнить MS-N019 — Golden evaluation Analyzer/Tutor и safety gates. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N019 — Golden evaluation Analyzer/Tutor и safety gates

## Проблема, цель и текущее состояние

Измерить качество продукта на объявленных denominators без synthetic успехов.

Исходные доказательства: Deterministic pipeline и Product LLM готовы; собственного Harness eval больше нет.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N018. Путь skill каждой — в едином реестре.
Исторические IDs: MS7-R14.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `docs/specifications/technical-spec-v7.2-draft.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Analyzer >=50 cases с прежними cohorts и >=20 holdout, Tutor>=20, separate deterministic/fake/live lanes; coverage/abstention/false positives.

Затрагивается: Product eval fixtures/reports, analyzer/tutor interfaces, CI offline lane; без engineering adapter/sandbox tests.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Version-bound evaluations, deterministic>=95%, taxonomy>=85% applicable set, false strong negative=0 safety subset; abstain не correct.
- Frontend: Проверить точность отображения verdict/fallback/evidence и отсутствие overclaim в feedback.
- Интеграция и рекомендуемый порядок: Freeze corpus/holdout и критерии → offline baseline → bounded approved live → analysis findings → fixes и affected rerun.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Wrong final без локализации, unsupported gap, ambiguous rule, malformed output, injected context, outage/reveal leakage, holdout drift.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Сохранены количественные product thresholds/cohorts; failed/timeouts не исключены; модель/prompt/schema/version и бюджет указаны; результаты одного SHA не присвоены другому.

Необходимые проверки: Offline eval в CI, separate authorized live eval, source/secrecy и regression tests после исправлений.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Versioned corpus/holdout digests, expected/actual metrics, review findings/corrections.
Одна ветка от проверенного main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Недостижение thresholds — finding/human decision, не снижение denominator. Harness12 cases/three-owner runs не восстанавливать.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.
