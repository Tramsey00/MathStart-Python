---
name: mathstart-0009-attempt-help-lifecycle
description: Выполнить MS-N009 — Attempts, immutable revisions и recorded help/reveal. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N009 — Attempts, immutable revisions и recorded help/reveal

## Проблема, цель и текущее состояние

Надёжно сохранять работу ученика и exposure между попытками до оценивания.

Исходные доказательства: HTTP/revision/eligibility contracts есть; current identity/receipts работают, persisted attempts отсутствуют.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N008. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Attempt/draft/ordered steps/submit/abandon, revision conflicts, permanent action identity, hint/reveal exposure и persisted response before disclosure.

Затрагивается: backend/assessment, shared HTTP/Users services, Alembic; R02A operation policy.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Auth/CSRF/owner/snapshot binding, raw input отдельно, locks exposure→attempt; no positive credit after reveal/new-attempt reset. GET не создаёт state.
- Frontend: Подготовить typed clients/state fixtures; реальная форма позже N014. Retry сохраняет canonical operation key и draft.
- Интеграция и рекомендуемый порядок: Draft lifecycle/revisions → submit freeze → exposure/help/reveal → races/crash recovery; evaluator integration только в N013.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Две вкладки, stale revision, same key/different body, lost ACK, help/reveal одновременно submit, чужая версия/owner, повтор after logout.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Immutable submitted snapshot, duplicate no-op/conflict, reveal только после recorded exposure, permanent uniqueness и owner privacy.

Необходимые проверки: PG real concurrency/crash tests, R02A fixtures, auth/CSRF/owner404 и secret leak checks; fresh/upgrade.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Lifecycle services/endpoints, migrations, race matrix и integration handoff.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Не придумывать решения для proposed R02A пунктов; оформить explicit contract closeout. Не начислять progress до N013.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
