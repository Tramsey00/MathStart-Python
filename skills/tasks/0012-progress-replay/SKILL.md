---
name: mathstart-0012-progress-replay
description: Выполнить MS-N012 — ProgressEvent, CompletionFact, проекция и replay. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N012 — ProgressEvent, CompletionFact, проекция и replay

## Проблема, цель и текущее состояние

Транзакционно хранить и воспроизводить долгосрочное знание по принятому reducer.

Исходные доказательства: R03 exact Decimal reference и R03A CompletionFact draft; production Progress отсутствует.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N011. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Закрыть pending addendum decisions, event/mirror/state persistence, ingest/replay/version policy, self-report и real PG concurrency.

Затрагивается: backend/progress, immutable Assessment DTO, Knowledge references, Alembic; frozen R03/R03A fixtures.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Only Progress writes; exact deltas/clamp/ROUND_HALF_UP, global dual completion identity, neutral recent-ten, late event reproject, permanent dedupe.
- Frontend: Read models для mastery/confidence/status/coverage и own history, отдельно self-report; UI в N015.
- Интеграция и рекомендуемый порядок: Human contract closeout → schema/ingest constraints → online reducer adapter → replay/late delivery → concurrent conflict proof.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Same timestamp, duplicate/conflicting global ID under foreign owner, neutral completion changes status only, revealed version, repeat/reset, out-of-order ingestion.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Online/replay равны по всем state fields, progress-v1 compatibility сохранена; mirror не зависит от Assessment ORM; no evidence overwrite.

Необходимые проверки: R03/R03A pure parity + PostgreSQL concurrency/atomicity/fresh/upgrade/replay, exact immutable fixtures; no float.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Reviewed migrations/services, parity/concurrency report и retained policy-version mapping.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Нельзя изменять численные правила/порог ради реализации. Proposed CompletionFact пункты требуют явного решения, прежний approval не переносится.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.

## Выполнение 19.11.2026 — READY_FOR_REVIEW

Issue: https://github.com/Tramsey00/MathStart-Python/issues/98. База после fetch:
`d8d76f1d08e4eecca0a6f7eb20369029e4649c73` (N011 включена), отдельная ветка
`ms-n012-progress-replay`, новый изолированный worktree. Existing checkout/worktree,
учебные материалы, чужие DB/Docker не менялись.

Пользователь явно передал подтверждение Руслана R03A/ADR-0005. Решения зафиксированы
в [closeout](../../../specs/progress/N012-runtime-closeout-v1.md); historical pending
artifacts не переписывались. Добавлены persistence/immutable guards, v01_0008/ACL,
version registry, точный reducer, permanent dual dedupe, immutable DTO/read boundary,
legacy import, self-report, own read API и typed client. N013/N015 не реализованы.

Проверено на новом собственном PostgreSQL 16.15 (loopback 55493, отдельный cluster,
уникальная DB на каждый тест, удалены после прогона; сервер остановлен):

- `python -m unittest backend.tests.test_progress backend.tests.test_unit.UnitTests.test_single_chain -v`: 14 PASS; fresh и upgrade v01_0007→v01_0008, ACL/immutable guards,
  online/replay, late delivery, neutral status-only, global ID races/atomic refusal,
  self-report/auth/CSRF/privacy/pagination/legacy IDs.
- `python -m unittest discover -s tests -p test_r03_contract.py -v`: 18 PASS.
- `python -m unittest discover -s tests -p test_r03a_contract.py -v`: 41 PASS.
- `node scripts/generate-progress.mjs --check`: PASS; scoped TypeScript check: PASS;
  `vitest run tests/progress-client.test.ts`: 3 PASS.

Native finalization reader намеренно fail-closed до N013: для положительных consumer
PG тестов использован явный trusted server DTO fixture с реальными version/mappings;
отдельно доказан отказ отсутствующим/нефинализированным source rows. Это не тест
будущего production end-to-end Assessment→Progress. Полные тяжёлые наборы, UI/browser,
Docker builds и живые providers не запускались. Исходные frozen R03/R03A fixtures
сохранены. Результирующий SHA/tree и PR фиксируются в PR; самопроверка не заменяет
независимое ревью и человеческую приёмку. Merge не выполнялся.
