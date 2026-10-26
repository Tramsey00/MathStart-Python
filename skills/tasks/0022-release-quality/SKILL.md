---
name: mathstart-0022-release-quality
description: Выполнить MS-N022 — Security/privacy, производительность и доступность RC. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N022 — Security/privacy, производительность и доступность RC

## Проблема, цель и текущее состояние

Закрыть риски границ данных, нагрузку и browser accessibility перед public release.

Исходные доказательства: Coherent staging N021; старые platform measurements не доказывают новый intelligent/game runtime.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N021. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Auth/IDOR/CSRF/XSS/secrecy/rate/redaction/privacy review, API/AI cohorts, keyboard/focus/contrast/mobile/reduced motion.

Затрагивается: Все затронутые services/HTTP/UI, rate/observability/privacy policies, load/browser tests.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Shared multiworker PostgreSQL rates, private/retention/deletion and replay integrity, budget/provider limits, p95<500ms/API и <15s/AI.
- Frontend: Own records only, no answer in caches/bundles, accessible feedback/list alternative, full 360/768/1440.
- Интеграция и рекомендуемый порядок: Threat/privacy scope → targeted tests/review → declared load cohorts → browser/a11y inspection → fixes and affected recheck.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Multiworker limit races, foreign IDs, expired/revoked session, injection, slow/failed AI, timeout denominator, narrow/keyboard-only UI.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Нет открытых blocking security/accessibility findings; >=200 ordinary/10 concurrent и >=30 AI/2 concurrent с согласованным budget; failures включены в metrics.

Необходимые проверки: Security/PG concurrency/secret scans, public DTO probes, browser/visual inspection, real measured load с versions/hardware/nearest-rank p95.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Threat/privacy review, measured metrics/raw samples, a11y findings/fixes, human decisions по исключениям.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Новые реальные данные несовершеннолетних/provider/privacy решения не утверждать агентом. Не отбрасывать плохие samples ради PASS.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
