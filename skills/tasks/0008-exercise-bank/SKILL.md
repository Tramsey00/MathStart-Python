---
name: mathstart-0008-exercise-bank
description: Выполнить MS-N008 — Immutable exercise versions и pilot bank. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N008 — Immutable exercise versions и pilot bank

## Проблема, цель и текущее состояние

Публиковать проверенный pilot bank, выдавая браузеру только public contract.

Исходные доказательства: R02/R02A schemas и fixtures существуют, Assessment persistence нет.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N007. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Exercise/Version/Validation/Skill, reviewed import/publish/archive, public DTO и curated pilot: 40 assessed + минимум3 SELF_CHECK, 4 PRIMARY/skill, 12 step/12 final, 2 distinct structured schemas, difficulty coverage.

Затрагивается: backend/assessment, content/knowledge references, Alembic, specs/exercises и curated server-only bank.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Published version immutable, one PRIMARY, retained historical refs; answer/checker/accepted variants отделены от public output и SSG.
- Frontend: Сверить renderer-facing schemas и unsupported fallback; новый UI renderer в N014.
- Интеграция и рекомендуемый порядок: Contract closeout/versioning → persistence/import → coverage validator → public reads/secrecy probes; человеческое mathematical review банка.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Duplicate version, missing skill/topic, undercovered bank, mutation published version, secret in nested payload, unknown schema, archive referenced by history.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Точные coverage quotas и две содержательно разные structured forms; offline deterministic verification и explicit review учебной математики; без конвертации всех263 уроков.

Необходимые проверки: R02/R02A contracts, schema/coverage/domain tests, PG fresh/upgrade/import rollback, HTML/JSON/JS/network secret-leak checks.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Versioned bank, coverage report, service/API/migration, editorial review.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Недостаточный bank не компенсируется снижением quotas. Не раскрывать validation data в generated frontend fixtures.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
