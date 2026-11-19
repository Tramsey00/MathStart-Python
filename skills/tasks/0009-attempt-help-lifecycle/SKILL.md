---
name: mathstart-0009-attempt-help-lifecycle
description: Выполнить MS-N009 — Attempts, immutable revisions и recorded help/reveal. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N009 — Attempts, immutable revisions и recorded help/reveal

## Implementation handoff — 19.11.2026

Статус реализации: **READY_FOR_REVIEW**. Issue [#90](https://github.com/Tramsey00/MathStart-Python/issues/90),
ветка `ms-n009-attempt-help-lifecycle`, отдельный worktree. Base SHA:
`fdc8dc59b255b646f2f680cc993e616917d7f5e4`; точный проверенный implementation SHA/tree фиксируется в PR.
[Contract closeout и race matrix](../../../specs/exercises/N009-attempt-lifecycle-v1.md).

Реализованы persistence/migration v01_0007, draft/steps/revisions, immutable submit,
abandon/corrections, permanent action replay/conflict, recorded Exposure/help/reveal,
HTTP/auth/CSRF/privacy, typed client и синтетические test-only fixtures.
N010/evaluator/Progress/UI N014 не реализованы, существующий учебный банк не изменён.

Профильные проверки явно разрешены текущим поручением пользователя:

- `python -m unittest backend.tests.test_attempt_lifecycle backend.tests.test_assessment_bank.PublicContractTests backend.tests.test_unit.UnitTests.test_single_chain -v`
  — **19/19 PASS, exit 0**, PostgreSQL 16.15 в собственном loopback-кластере N009.
  Включены две сессии/races, process crash до/после COMMIT для submit/reveal,
  fresh/reviewed upgrade, auth/CSRF/owner privacy и secret boundaries.
- Отдельные affected reruns `...PostgreSQLAttemptTests.test_runtime_privileges_do_not_grant_checker_or_ddl`
  и `...PostgreSQLAttemptTests.test_fresh_schema_upgrade_retains_history_and_guards`
  — **1/1 PASS каждый, exit 0** после уточнения минимальных row-lock privileges и
  добавления точной сверки сохранённых N008 exercise/version/validation/skill rows.
  Реальные create/draft/submit/reveal выполнены под `SET ROLE local_runtime`;
  checker/validation_spec и изменение опубликованной версии недоступны.
- `node scripts/generate-attempts.cjs --check` — **PASS, exit 0**.
- `tsc --noEmit --strict --noUncheckedIndexedAccess --exactOptionalPropertyTypes --skipLibCheck --target ES2022 --module ESNext --moduleResolution Bundler --lib ES2022,DOM,DOM.Iterable src/shared/api/attempt-client.ts`
  — **PASS, exit 0**, только затронутый клиент и его imports.
- `vitest run tests/attempt-client.test.ts` — **6/6 PASS, exit 0**.
- `python -m unittest discover -s tests -p test_r02a_contract.py -v`
  — **29 PASS / 1 ERROR, exit 1**: исторический pin-check падает с
  `Unreviewed task change: AGENTS.md`. AGENTS побайтно совпадает с base origin/main;
  base SHA-256 `6bc2ab18f6dc4baf1bfeac70810cac709d2c0fcb3961961b56cf3148d83a55a7`,
  старый manifest ожидает `a44e6578edad0c2230d6b5fdb97b2ad49c4dcbe0800ca5798c4aa41f49c211aa`.
  Это унаследованное расхождение, historical receipts/guards не переписаны и не ослаблены.

Самопроверка кода завершена; найденные проблемы согласованного GET snapshot,
Content release binding и SELECT FOR SHARE privileges исправлены и проверены.
Независимое ревью **PENDING**, человеческая приёмка **PENDING**, merge/deploy **NOT_DONE**.
R02A/ADR-0004 остаются PENDING/Proposed; конкретный closeout передан на ревью.
N008 остаётся REVEAL-only: включение реальных подсказок требует отдельно проверенных
текстов и согласованной hint-enabled версии. Автоматического импорта/публикации нет.
Чужие worktree/БД/Docker не использовались; собственный PostgreSQL остановлен.
Полные suites, browser/build и live LLM не запускались.

## Решение о доступе — 16.11.2026

Authentication/CSRF/owner проверяются сервером до создания assessed attempt, записи решения или запуска анализа. Guest mutations отклоняются без attempt/AIRun/LLM и расходов провайдера. Публичная самопроверка без LLM остаётся отдельным путём без persisted attempts/ProgressEvent; UI-граница и безопасный login return определены в MS-N014.

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
