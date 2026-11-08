# Задачи MathStart

## Текущее состояние — 08.11.2026

MS-T000, MS-T001, MS-T002 и **MS-T002A — ACCEPTED**.
Пользователь явно принял MS-T002A 08.11.2026. Review/fixes, merge PR #58 в main
`45e6e6532572f64780e21610d9f319c7e7fc4c42` и контроль независимого clone завершены.
Повторный host-dev старт — 25,000 с; данные/config сохранены после stop/restart.
Точные результаты и ограничения — в [карточке MS-T002A](../../skills/tasks/t002a-team-local-start/SKILL.md).
Пользователь 08.11.2026 явно разрешил публикацию этой редакции в main через PR #59.
MS-T003–MS-T008 доступны для параллельного назначения; сами переносы ещё не начаты.

Основной Windows dev — host-dev в своей обычной папке, полный Compose — альтернатива.
[Инструкция](../local-development-host.md) описывает первую подготовку и обновление.
Автопрогоны — только по отдельному поручению; [политика](../frontend/testing-policy.md)
приоритетнее старых checklist. Отложенные проверки — NOT_RUN_BY_USER_REQUEST.

## Как пользоваться очередью

Карточки и [registry.json](registry.json) — одна очередь; прежние source cards
и персональные планы не назначают работу. Все upstream должны быть приняты
перед реализацией. Статусы: PLANNED → IN_PROGRESS → READY_FOR_REVIEW →
HUMAN_ACCEPTANCE_PENDING → ACCEPTED; CHANGES_REQUESTED и BLOCKED_DEPENDENCY/
BLOCKED_DECISION сопровождаются причиной. Merge фиксируется отдельно.

[Inventory](lesson-inventory.json) содержит 263 темы. Null URL не разрешает
вычислять адрес по порядку переноса. Принятые пилоты переиспользуются в своих
классах; их адреса и общий UI определены [стандартом](../frontend/lesson-migration.md).
Дизайн не выбирается заново. Общие правила — [AGENTS](../../AGENTS.md),
[архитектура](../../ARCHITECTURE.md), [UI-контракт](../ux/shared-ui-contract.md).

| Порядок | ID / название | Статус | Зависимости | Карточка | Приёмка |
| --- | --- | --- | --- | --- | --- |
| 00 | MS-T000 — Подготовить очередь, стандарт переноса и очистить документацию | ACCEPTED | — | [SKILL.md](../../skills/tasks/t000-workflow-preparation/SKILL.md) | Очередь/карточки согласованы друг с другом, inventory содержит все 263 темы; нет конфликтующих текущих ТЗ и битых действующих ссылок; удалённое восстанавливается из точного Git SHA; scope проверок и ограничения честно отражены. |
| 01 | MS-T001 — Перенести новый HTML-урок по стандарту в основной React/SSG runtime | ACCEPTED | MS-T000 | [SKILL.md](../../skills/tasks/t001-lesson-pilot/SKILL.md) | Четыре React-урока и общий стандарт приняты 25.10.2026; COMPLETE_STATIC_SOURCE_REVIEW, human acceptance ACCEPTED; автопрогоны NOT_RUN_BY_USER_REQUEST. Clone/production остаются за пределами этой приёмки. |
| 02 | MS-T002 — Подключить утверждённые главную и каталог к основному приложению | ACCEPTED | MS-T001 | [SKILL.md](../../skills/tasks/t002-public-pages/SKILL.md) | Главная и каталог подключены и приняты 25.10.2026; статическое review завершено, автопрогоны отложены. Самостоятельный запуск из clone — MS-T002A. |
| 03 | MS-T002A — Подготовить воспроизводимый запуск после clone и передать baseline команде | ACCEPTED | MS-T002 | [SKILL.md](../../skills/tasks/t002a-team-local-start/SKILL.md) | Windows host-dev в обычной рабочей папке: Vite/FastAPI на хосте, PostgreSQL в Docker; HMR/авторелоад, сохранение данных, подготовка и обновление по инструкции; review, merge #58 и clone main завершены; приёмка пользователя 08.11.2026. |
| 04 | MS-T003 — Полностью перенести 5 класс | PLANNED | MS-T002A | [SKILL.md](../../skills/tasks/t003-grade-5/SKILL.md) | Все 35 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, пользователь принял cohort. |
| 05 | MS-T004 — Полностью перенести 6 класс | PLANNED | MS-T002A | [SKILL.md](../../skills/tasks/t004-grade-6/SKILL.md) | Все 28 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, пользователь принял cohort. |
| 06 | MS-T005 — Полностью перенести 7 класс | BLOCKED_DEPENDENCY | MS-T002A | [SKILL.md](../../skills/tasks/t005-grade-7/SKILL.md) | Все 75 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, пользователь принял cohort. |
| 07 | MS-T006 — Полностью перенести 8 класс | PLANNED | MS-T002A | [SKILL.md](../../skills/tasks/t006-grade-8/SKILL.md) | Все 66 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, пользователь принял cohort. |
| 08 | MS-T007 — Полностью перенести 9 класс | PLANNED | MS-T002A | [SKILL.md](../../skills/tasks/t007-grade-9/SKILL.md) | Все 46 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, пользователь принял cohort. |
| 09 | MS-T008 — Полностью перенести 10 класс | PLANNED | MS-T002A | [SKILL.md](../../skills/tasks/t008-grade-10/SKILL.md) | Все 13 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, пользователь принял cohort. |
| 10 | MS-T009 — Заменить старый интерфейс авторизации и профиля | PLANNED | MS-T003–MS-T008 (все) | [SKILL.md](../../skills/tasks/t009-identity-ui/SKILL.md) | Человек выбрал email/username и маршруты до API изменений; новый UI работает с реальной Identity; заменённые old forms/controllers/styles/tests удалены без потери auth/CSRF/session/owner/privacy поведения; нет двух независимых реализаций входа. |
| 11 | MS-T010 — Применить общую систему к staff без изменения прав | PLANNED | MS-T009 | [SKILL.md](../../skills/tasks/t010-staff-ui/SKILL.md) | Все действующие staff resources сохраняют server permissions, read/write ограничения, revision conflicts и подтверждения; новый UI использует общий chrome без утечки данных в public artifact. |
| 12 | MS-T011 — Завершить перенос и сократить переходные проверки | PLANNED | MS-T010 | [SKILL.md](../../skills/tasks/t011-rollout-finalization/SKILL.md) | Все 263 темы и public links/redirects разрешаются; нет prototype runtime/старого UI; тесты распределены по policy, meaningful assertions сохранены, обязательный combined candidate не подменён быстрым профилем. |
| 13 | MS-N006 — Педагогическая спецификация геймификации | PLANNED | MS-T011 | [SKILL.md](../../skills/tasks/0006-gamification-spec/SKILL.md) | Утверждённый набор механик либо явно отложенное решение; формальные positive/negative начисления, idempotency и отдельность знания; модель хранения не объявлена реализованной. |
| 14 | MS-N007 — Knowledge и Content-owned TopicSkill | PLANNED | MS-T011 | [SKILL.md](../../skills/tasks/0007-knowledge-persistence/SKILL.md) | Exact pilot inventory и deterministic depth2 ancestor query, сохранность user history, fresh+upgrade PostgreSQL и идемпотентный импорт. |
| 15 | MS-N008 — Immutable exercise versions и pilot bank | PLANNED | MS-N007 | [SKILL.md](../../skills/tasks/0008-exercise-bank/SKILL.md) | Точные coverage quotas и две содержательно разные structured forms; offline deterministic verification и explicit review учебной математики; без конвертации всех263 уроков. |
| 16 | MS-N009 — Attempts, immutable revisions и recorded help/reveal | PLANNED | MS-N008 | [SKILL.md](../../skills/tasks/0009-attempt-help-lifecycle/SKILL.md) | Immutable submitted snapshot, duplicate no-op/conflict, reveal только после recorded exposure, permanent uniqueness и owner privacy. |
| 17 | MS-N010 — Ограниченный математический parser и normalizer | PLANNED | MS-N009 | [SKILL.md](../../skills/tasks/0010-math-parser/SKILL.md) | Supported pilot grammar reproducible; timeout/limit/unsupported не становятся wrong/misconception, resource limits проверены. |
| 18 | MS-N011 — Детерминированные validators и первый доказанный дефект | PLANNED | MS-N010 | [SKILL.md](../../skills/tasks/0011-deterministic-analysis/SKILL.md) | Validated AnalysisResult не меняет UserSkillState; known deterministic verdict не переопределяется LLM; false strong negative=0 safety subset. |
| 19 | MS-N012 — ProgressEvent, CompletionFact, проекция и replay | PLANNED | MS-N011 | [SKILL.md](../../skills/tasks/0012-progress-replay/SKILL.md) | Online/replay равны по всем state fields, progress-v1 compatibility сохранена; mirror не зависит от Assessment ORM; no evidence overwrite. |
| 20 | MS-N013 — Atomic Analysis → Progress и аудит persisted loop | PLANNED | MS-N012 | [SKILL.md](../../skills/tasks/0013-evidence-finalization/SKILL.md) | Реальная PG история объясняет каждый state change; retry не дублирует evidence; leak/owner/transaction boundaries доказаны. |
| 21 | MS-N014 — Четыре exercise UI, typed steps и help/reveal recovery | PLANNED | MS-N013, MS-T009 | [SKILL.md](../../skills/tasks/0014-exercise-ui/SKILL.md) | Все четыре режима работают с реальным backend, no secret in HTML/JSON/JS/network до reveal, новый attempt не сбрасывает exposure. |
| 22 | MS-N015 — Прогресс, история и завершение onboarding | PLANNED | MS-N014 | [SKILL.md](../../skills/tasks/0015-progress-history/SKILL.md) | UI точно отражает server state и explanation; reading/XP не дают mastery; diagnostic placeholder не имитирует готовую N016. |
| 23 | MS-N016 — Диагностика и adaptive practice с возвратом | PLANNED | MS-N015 | [SKILL.md](../../skills/tasks/0016-diagnostic-practice/SKILL.md) | Exact §10 selection/stop rules и нейтральность skip/unsupported, stable item under refresh, real evidence path и доступный возврат. |
| 24 | MS-N017 — Product LLM provider, AIRun и безопасный fallback | PLANNED | MS-N016 | [SKILL.md](../../skills/tasks/0017-product-provider/SKILL.md) | Обычные tests offline; bad output не создаёт strong negative; actual metadata без PII, provider outage не скрывает working core. |
| 25 | MS-N018 — Tutor policy, reviewed hint bank и conversations UI | PLANNED | MS-N017 | [SKILL.md](../../skills/tasks/0018-tutor/SKILL.md) | No pre-reveal arbitrary mathematical prose leakage; exact context budgets, user/version scope и correct exposure; frontend не bypass-ит сервер. |
| 26 | MS-N019 — Golden evaluation Analyzer/Tutor и safety gates | PLANNED | MS-N018 | [SKILL.md](../../skills/tasks/0019-product-evaluation/SKILL.md) | Сохранены количественные product thresholds/cohorts; failed/timeouts не исключены; модель/prompt/schema/version и бюджет указаны; результаты одного SHA не присвоены другому. |
| 27 | MS-N020 — Реализация только принятых игровых механик | PLANNED | MS-N006, MS-N019 | [SKILL.md](../../skills/tasks/0020-gamification-implementation/SKILL.md) | Каждое начисление объяснимо source/rule/version, двойное невозможно; XP/streak/reading не создают ProgressEvent/mastery, выбранный UX принят. |
| 28 | MS-N021 — Полный учебный цикл на staging | PLANNED | MS-N020 | [SKILL.md](../../skills/tasks/0021-staging-integration/SKILL.md) | Один source SHA/image/public tuple, полный цикл без fixture substitutes и skipped, понятный список remaining human gates. |
| 29 | MS-N022 — Security/privacy, производительность и доступность RC | PLANNED | MS-N021 | [SKILL.md](../../skills/tasks/0022-release-quality/SKILL.md) | Нет открытых blocking security/accessibility findings; >=200 ordinary/10 concurrent и >=30 AI/2 concurrent с согласованным budget; failures включены в metrics. |
| 30 | MS-N023 — Upgrade/restore, публичный RC и browser rehearsal | PLANNED | MS-N022 | [SKILL.md](../../skills/tasks/0023-release-recovery/SKILL.md) | Exact release tuple и unskipped CI, measured restore, successful external full-loop только после разрешения; локальный loopback не называется публичной готовностью. |
| 31 | MS-N024 — Отчёт о реальном AI-процессе, demo и freeze/handover | PLANNED | MS-N023 | [SKILL.md](../../skills/tasks/0024-report-handover/SKILL.md) | Полный reproducible artifact/evidence index, final SHA, реальные ограничения и actual contributions; C-08 описывает применённые AI tools, не обязательство собственного Harness. |

## Границы текущей редакции

Первые пять прежних дизайн-карточек выведены; mapping сохранён в registry.json.
Старые 52 source cards, deadlines и персональные назначения доступны только
в Git, не задают текущий порядок. Будущие N006–N024 сохранены с уточнёнными
зависимостями; существование карточек не означает готовую persistence/API.
Авторизация I02/I03 не является утверждённым интерфейсом: MS-T009 заменяет UI,
сохраняя Identity, и сначала получает решение email/username. Staff — MS-T010.

## Bootstrap и работа команды

MS-T001 → MS-T002 → MS-T002A выполнялись в ui/ux без отдельных Issue и веток.
PR #58 уже слит; контроль опубликованного main завершён.
MS-T002A принята пользователем 08.11.2026; повторять установку и контроль не нужно.

Начиная с MS-T003: GitHub Issue → отдельная ветка от актуального origin/main
после fetch → реализация и отдельно порученные проверки → PR со ссылкой на Issue →
review/fixes → human acceptance → решение о merge. Пример ветки: ms-t003-grade-5,
без codex/. Продолжать существующие Issue/ветки/PR без дублей.

### Параллельный перенос MS-T003–MS-T008

Решение 08.11.2026: все шесть задач зависят от принятой MS-T002A, друг от друга
не зависят. Нумерация задаёт классы, а не последовательность выполнения.
Каждому исполнителю отдельно поручается один класс со своим Issue/веткой/PR;
без поручения задача остаётся PLANNED. Карточек с суффиксом A для этих классов нет.
MS-T009 начинается после приёмки всех шести классов.

Материалы меняются в пределах своего класса. В `site_content/material-routes.json`
добавляются только назначения своих тем, без перенумерации и перезаписи чужих записей.
Изменения общего renderer, конвертера, lesson-компонентов и общих стилей сначала
согласуются между исполнителями: общую необходимую правку интегрировать отдельно,
затем получить её в ветки классов. Не создавать шесть вариантов общего компонента.
У каждого своя локальная БД/config; публикации в чужое окружение исключены.
PR объединяются последовательно после review, ручной приёмки и решения пользователя;
перед интеграцией очередного PR учесть уже объединённые изменения и конфликты.

Проверка переноса — ручной просмотр материала и интерактивов пользователем.
Автоматические tests/typecheck/Playwright/smoke и source/docs/preservation gates
не запускать и не создавать вместо них новые скрипты QA. В отчёте —
NOT_RUN_BY_USER_REQUEST; это не PASS. Перенос сохраняет весь согласованный
материал и поведение интерактивов; штатные валидаторы/guards не отключаются.

N006 имеет отдельное педагогическое решение, но не блокирует Knowledge.

## История решений

[Исходная очередь с хронологией](HISTORY.md) сохранена без изменения текста.
Старые PENDING, планы merge и промежуточные candidates описывают прошлые этапы.
Подробные receipts находятся в историях соответствующих карточек; они не являются
поручением повторить работу или доказательством нового SHA.

08.11.2026, MS-T005 / Issue #61: перенесены 24 новые темы 7 класса, линейный пилот переиспользован; 4 документа подготовлены, но не активированы из-за общего renderer/CSS, 46 тем блокируются конвертером/validator. Класс целиком не готов. [Карта всех 75 тем](ms-t005-migration-map.json), [результаты и ограничения](../audits/ms-t005-grade-7.md). Независимое review и ручная приёмка ожидаются; merge не выполнялся. Текущее поручение пользователя отдельно разрешило scoped tests/typecheck/Playwright/source/URL checks; глобальная политика прогонов не меняется.

08.11.2026, MS-T005 — исправление renderer/CSS: активированы ещё 4 подготовленных урока (7-geometry-8/9, 7-statistics-5/24). Всего 28 новых React-документов + 1 принятый пилот, 46 legacy-тем не пересматривались после shared fixes. [Актуальный execution record](../audits/ms-t005-renderer-css.md). БД/publication не обновлялись; ручная приёмка и независимое review ожидаются.

08.11.2026, MS-T005 — повторная обработка 46 прежних blockers: ещё 30 тем перенесены. Всего 58 новых React-документов + 1 пилот; 1 валидный документ ждёт URL, 15 тем имеют текущие converter/validator blockers. [Отчёт](../audits/ms-t005-retry-46.md), [список для Владимира/пользователя](ms-t005-converter-followups.md). 74 профильных теста, 186 offline browser scenarios, прямой TypeScript и Content routes PASS; публикация и human acceptance не выполнялись.

08.11.2026, MS-T005 — активированы семь геометрических тем: всего 66/75 source routes (65 новых + пилот), geometry 12/12. Остались 8 тем статистики и URL первой алгебраической темы. [Отчёт](../audits/ms-t005-geometry-activation.md), [оставшиеся 9](ms-t005-remaining.md). 81 тест, 56 offline browser scenarios, TypeScript, Content routes и media checks PASS; установленный snapshot не публиковался, ручная приёмка PENDING. Узкое responsive image rule в runtime.css отдельно согласовано пользователем.
