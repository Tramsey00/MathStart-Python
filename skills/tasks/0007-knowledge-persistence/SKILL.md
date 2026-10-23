---
name: mathstart-0007-knowledge-persistence
description: Выполнить MS-N007 — Knowledge и Content-owned TopicSkill. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N007 — Knowledge и Content-owned TopicSkill

## Проблема, цель и текущее состояние

Сохранить pilot graph и topic mappings в PostgreSQL с проверяемым импортом.

Исходные доказательства: Есть 10 skills/13 edges fixtures и pure R03 reference; product Knowledge tables/API отсутствуют.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-T011. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

SQLAlchemy models/services, Alembic fresh/upgrade, atomic/idempotent pilot import, DAG validation и Content TopicSkill.

Затрагивается: backend/knowledge, backend/content, backend/migrations; specs/knowledge fixtures и read DTO.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Stable code, unique edges, no cycles/self edges, prerequisite→dependent; basic_arithmetic внешняя предпосылка. TopicSkill в Content, не обратная зависимость Knowledge.
- Frontend: Предоставить безопасный read contract для будущих экранов; не рисовать несуществующий mastery.
- Интеграция и рекомендуемый порядок: Проверить принятые contracts и exact FK к retained ContentPage, согласовать schema plan, реализовать graph/import, затем DTO/integration.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Unknown/duplicate code, reversed/self/cyclic edge, архивный topic, отсутствующая связь, повтор import, corrupt package без partial writes.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Exact pilot inventory и deterministic depth2 ancestor query, сохранность user history, fresh+upgrade PostgreSQL и идемпотентный импорт.

Необходимые проверки: R03 pure graph + PostgreSQL constraints/import/concurrency по применимости; verify_repo и preservation; Alembic reviewed SQL.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Models/services/migration, import receipt, schema/ownership review и проверенный candidate.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Изменение codes/edges/FK semantics требует принятого addendum. Не делать startup seed и не трогать operating DB.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

Геймификация MS-N006 не является HARD dependency Knowledge.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
