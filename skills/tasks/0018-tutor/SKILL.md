---
name: mathstart-0018-tutor
description: Выполнить MS-N018 — Tutor policy, reviewed hint bank и conversations UI. Использовать только для отдельно порученного задания из реестра MathStart.
---

# MS-N018 — Tutor policy, reviewed hint bank и conversations UI

## Проблема, цель и текущее состояние

Давать безопасную контекстную помощь, сохраняя честную evidence eligibility.

Исходные доказательства: Recorded help/reveal N009, bank N008, Product provider N017; Tutor runtime отсутствует.
После начала задания сверить это с actual HEAD, imports/build и принятыми upstream
результатами; описание не является доказательством будущей готовности.

## Зависимости и обязательные источники

Зависимости: MS-N017. Путь skill каждой — в едином реестре.
Открой от Git root: `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `specs/product/learning-requirements.md`, `docs/tasks/INDEX.md`, `skills/verification/SKILL.md`, `docs/target-runtime.md`.
Связанные domain/API/UI contracts выбирай по перечисленным ниже модулям;
статус proposed не превращай в accepted по наличию tests.

## Границы, модули, данные и контракты

Reviewed hint bank, bounded context builder, conversations/messages, model intent validation и frontend panel/fallback.

Затрагивается: backend/ai_tutor, llm interface, Assessment help service, frontend panel, versioned hint bank.
Вне scope: новые несогласованные механики/режимы, массовая конвертация авторского
контента, automatic deployment и реализация следующего задания.

## Backend, frontend и интеграция

- Backend: До reveal только разрешённый hint_id/level из bank, запись help до текста; answer/private solution вне prompt, no mastery writes.
- Frontend: Hint-first flow, distinct explicit reveal, approved fallback при outage, accessible messages/rate/pending/error states.
- Интеграция и рекомендуемый порядок: Editorial hint review включая single-step leaks → context/schema policy → persistence/help integration → UI → separate live acceptance.

Один исполнитель выполняет части последовательно по зависимостям. Никаких
постоянных персональных владельцев, выбора модели или автоматической делегации.

## Ошибки, граничные случаи и совместимость

Request full answer, injection in lesson/input, foreign conversation/version, malformed intent, repeated hint, budget limit, post-reveal explanation.
Сохранить исторические IDs/данные, raw input и public/server boundary. Не считать
неподдерживаемую математику отрицательным knowledge evidence.

## Приёмка и проверки

No pre-reveal arbitrary mathematical prose leakage; exact context budgets, user/version scope и correct exposure; frontend не bypass-ит сервер.

Необходимые проверки: >=20 Tutor eval cases из §15, leak/owner/CSRF/timeout/fallback tests, PG persistence и browser states; authorized live lane отдельно.
Записать actual SHA/tree, commands/exit/results, skipped/missing отдельно.
Portable pure не доказывает runtime. Для schema/runtime — только новые owned
disposable ресурсы по runbook; operating DB/acceptance stack не трогать.

## Артефакты, ревью и остановка

Policy/hint bank/conversation API/UI, redacted eval и editorial review.
Отдельные Issue и ветка от проверенного origin/main без `codex/`; существующие ветка/PR задания
продолжаются. Самопроверка → PR → отдельное ревью → fixes/affected rerun →
человеческая приёмка → решение пользователя о merge. PASS не означает ACCEPTED.

Leak-equivalent hint блокирует publication. Provider output не принимается как разрешение раскрыть answer.
При недостающем решении записать BLOCKED_DECISION с конкретным вопросом и
сохранить независимые подготовленные артефакты. После передачи остановиться.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.
