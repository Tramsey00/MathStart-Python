---
name: mathstart-0024-report-handover
description: Выполнить MS-N024 — Отчёт о реальном AI-процессе, demo и freeze/handover. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N024 — Отчёт о реальном AI-процессе, demo и freeze/handover

## Проблема, цель и текущее состояние

Передать проверенный продукт, доказательства и учебный отчёт без выдуманных approvals.

Исходные доказательства: Курс и исторические источники перечислены в ТЗ §§19/28; migration accepted PR54/55, собственный Harness снят.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N023. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Архитектура/данные/алгоритмы, настройка реально используемого Codex/AGENTS/task skills, checks→review→fixes, реальные failures, demo и reproducible clean-clone handover.

Затрагивается: docs/submission/report/demo, PRODUCT/ARCHITECTURE/runbooks и queue statuses; product freeze по actual release.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: Проверить documented schema/install/recovery и соответствие report работающему runtime; новых features нет.
- Frontend: Screenshots/demo четырёх режимов и return/history, versions/SHA captions без PII; source paths reproducible.
- Интеграция и рекомендуемый порядок: Сверить course requirements/actual LMS receipts → report/demo → независимое review → исправления → human acceptance и freeze.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Недоступные/неподтверждённые LMS данные, stale screenshots, synthetic/live confusion, missing private setup, source-only ZIP без Git history.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

Полный reproducible artifact/evidence index, final SHA, реальные ограничения и actual contributions; C-08 описывает применённые AI tools, не обязательство собственного Harness.

Необходимые проверки: Document/link/source/task checks, clean-clone commands и release verification по actual changes; human acceptance отдельно от PASS.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Отчёт/демо/runbooks, changelog/release tuple, acceptance/handover record и остановленная очередь.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Не придумывать ФИО/LMS receipt/согласование преподавателя/даты защиты. Не переписывать approvals и не начинать новое задание после handover.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
