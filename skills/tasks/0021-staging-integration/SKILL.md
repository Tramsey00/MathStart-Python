---
name: mathstart-0021-staging-integration
description: Выполнить MS-N021 — Полный учебный цикл на staging. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N021 — Полный учебный цикл на staging

## Проблема, цель и текущее состояние

Собрать coherent candidate с реальными domain/API/UI путями и доказанной эксплуатацией.

Исходные доказательства: Отдельные increments готовы; принятый перенос уже имеет install/recovery tooling, его не делать заново как миграцию.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N020. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Staging configuration и full login→topic→attempt→analysis→progress→practice→return→Tutor/history, readiness и degraded behavior.

Затрагивается: deploy, backend/frontend integration, scripts target/install/recovery, environment runbooks.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Реальные persisted services, schema/version compatibility, no startup writes; core работает при Product provider outage.
- Frontend: Все режимы и состояния на реальных endpoints; mock flags отсутствуют на основных путях, no-store/private guards сохранены.
- Интеграция и рекомендуемый порядок: Выбрать owned staging/env и rollout plan → install exact candidate → source/auth/domain probes → browser matrix → corrective review.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Fresh clone, incomplete publication503, CSRF/owner failures, provider outage, stale clients, no candidate, archived origin, version mismatch.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Один source SHA/image/public tuple, полный цикл без fixture substitutes и skipped, понятный список remaining human gates.

Необходимые проверки: Full verify_repo/managed target, install/fresh/upgrades, browser nine projects, image/recovery/combined CI по runbooks.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Staging runbook, release tuple/receipts, integration findings и corrected candidate evidence.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Host/secrets/operator choices требуют человека. Не использовать production или защищённый acceptance stack для rehearsal.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
