---
name: mathstart-0023-release-recovery
description: Выполнить MS-N023 — Upgrade/restore, публичный RC и browser rehearsal. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N023 — Upgrade/restore, публичный RC и browser rehearsal

## Проблема, цель и текущее состояние

Подготовить безопасный проверенный release и отдельно разрешённую публичную демонстрацию.

Исходные доказательства: Platform release/recovery инструменты сохранены; новый schema/domain release требует нового exact-candidate evidence.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N022. Путь skill каждой — в едином реестре.
Исторические IDs: MS7-V16, MS7-V17, MS7-R17, MS7-I17.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `docs/specifications/technical-spec-v7.2-draft.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Clean install, populated upgrade, physical tuple backup/restore и compatible app switch; reviewed public HTTPS exposure и full browser demo.

Затрагивается: deploy/runbooks, scripts verification, candidate images, schema/content/public tuple и private operator setup.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Сохранить DB/role OIDs/history/provenance/current writes; RPO<=24h/RTO<=2h и actual timings, restore не только pg_restore exit0.
- Frontend: Реальный внешний HTTPS/browser full loop, assets/no-JS/private pages, source URL/formula integrity.
- Интеграция и рекомендуемый порядок: Disposable install/upgrade/restore → reviewed release/fencing/backup plan → явное решение о deployment → внешние probes/rehearsal.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Lost commit/activation, wrong key/OID, incompatible schema rollback, target writes forbid stale snapshot, certificate trust/hostname, provider fallback.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Exact release tuple и unskipped CI, measured restore, successful external full-loop только после разрешения; локальный loopback не называется публичной готовностью.

Необходимые проверки: Full target/install/deployment/images/recovery/combined, retained no-JS/source/auth/browser; separate authorized Product live/fallback.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Release/recovery receipts, operator ownership/rollback plan, external browser evidence и RC review.
Одна ветка от проверенного main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Production/public changes выполняются только по решению пользователя. Не менять operating data, применённую history и signing identity ради readiness.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.
