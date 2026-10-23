---
name: mathstart-0006-gamification-spec
description: Выполнить MS-N006 — Педагогическая спецификация геймификации. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N006 — Педагогическая спецификация геймификации

## Проблема, цель и текущее состояние

Определить полезную игровую мотивацию и критерии приёмки до реализации наград.

Исходные доказательства: Игрового runtime/storage нет. XP/уровни/achievements/streaks/daily tasks/mascot — неподтверждённые кандидаты.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-T011. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Сравнить механики по педагогической цели и риску давления; выбрать действия, начисления, лимиты, retries/hints/reveals, антидубли, offline/timezone и UI. Определить owner/events/storage отдельным ADR.

Затрагивается: PRODUCT.md, полное ТЗ, docs/ux и новый gamification contract/ADR; без product code/schema/dependency changes.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Спроектировать trusted source identity, exactly-once awards, rollback/replay/privacy; XP не пишет UserSkillState и не создаёт fake ProgressEvent.
- Frontend: Объяснимая обратная связь, opt-out/reduced motion, отсутствие стыда/обязательной серии, связь с выбранной design system.
- Интеграция и рекомендуемый порядок: Цель/аудит аудитории → сравнение кандидатов → численные rules и сценарии → data ownership/acceptance → решение пользователя; N020 только после этого.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Повтор submit, exposed exercise, подсказка, reveal, timezone boundary, пропуск дня, позднее событие, удалённый аккаунт, no evidence.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Утверждённый набор механик либо явно отложенное решение; формальные positive/negative начисления, idempotency и отдельность знания; модель хранения не объявлена реализованной.

Необходимые проверки: Ревью decision tables и walkthrough сценариев с raw/expected outcome; проверка отсутствия mastery side effects в проекте контракта.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Product spec, event/ownership ADR, UI prototype и decision receipt.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Без решения пользователя не выбирать XP values/mascot/rewards и не создавать migrations. При отказе от направления N020 снимается, не считается выполненным.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
