# Последовательная очередь MathStart

20.10.2026. Единственный порядок новой работы; подробное задание — одна
каноническая карточка `SKILL.md`. Это task skills coding-агента, не учебные Skill.
`registry.json` — машинное представление той же таблицы для проверки связей.
Ничего здесь не разрешает автоматическое выполнение следующего задания.
Первая доступная будущая задача после ревью/приёмки текущего MS-N000 — **MS-N001**.
В этом поручении она не начинается. Миграция PR54 и консолидация PR55 завершены.

Один исполнитель работает в одной ветке от проверенного актуального main
без `codex/`. Уже существующие ветка/PR задания продолжаются. Порядок backend/
frontend определяет задача, не персональная специализация. Назначенных моделей,
обязательных субагентов и новых сроков нет.

Статусы: PLANNED → IN_PROGRESS → READY_FOR_REVIEW → CHANGES_REQUESTED →
READY_FOR_REVIEW → HUMAN_ACCEPTANCE_PENDING → ACCEPTED. BLOCKED_DEPENDENCY и
BLOCKED_DECISION содержат причину/недостающий вход; REMOVED_FROM_PLAN означает
«снято с плана», не DONE. MERGED фиксируется отдельно от human acceptance.
В таблице PLANNED не означает, что upstream принят или работа разрешена.
Зависимости должны быть приняты перед зависимой реализацией; порядок строк
задаёт последовательное исполнение даже там, где data dependencies независимы.
После отдельного человеческого решения об отложенной геймификации N020 можно
снять и скорректировать зависимость N021 явным изменением реестра.

Общие источники/DoD — [AGENTS](../../AGENTS.md), [архитектура](../../ARCHITECTURE.md),
[ТЗ](../specifications/technical-spec-v7.2-draft.md),
[verification](../../skills/verification/SKILL.md).
Репозиторные skills открываются явно по ссылке, не обещают автообнаружение Codex.

| Порядок | ID / название | Статус | Зависимости | Канонический skill | Основание приёмки |
| --- | --- | --- | --- | --- | --- |
| 00 | MS-N000 — Аудит документации и вывод собственного Harness | READY_FOR_REVIEW | — | [Текущее поручение/аудит](../audits/docs-and-workflow-cleanup.md) | Отдельное ревью, проверки нового candidate и решение пользователя; docs/audits/docs-and-workflow-cleanup.md |
| 01 | MS-N001 — Три визуальных направления и выбор пользователя | PLANNED | MS-N000 | [SKILL.md](../../skills/tasks/0001-visual-directions/SKILL.md) | Три различимых варианта с одной матрицей экранов/состояний; сопоставлены учебное удобство, возрастная уместность, стоимость сопровождения и геймификация; явное решение пользователя либо BLOCKED_DECISION. |
| 02 | MS-N002 — Выбор UI-библиотек под принятый дизайн | PLANNED | MS-N001 | [SKILL.md](../../skills/tasks/0002-ui-library-decision/SKILL.md) | Decision matrix с точными проверенными версиями/источниками и рекомендацией; пользователь выбирает stack; обновление архитектуры отличает выбранное от установленного. |
| 03 | MS-N003 — Дизайн-система и доступные базовые компоненты | PLANNED | MS-N002 | [SKILL.md](../../skills/tasks/0003-design-system/SKILL.md) | Каждый компонент имеет согласованный variant/state contract и accessibility evidence; нет answer leakage или глобального CSS конфликта; stack отражает установленные версии. |
| 04 | MS-N004 — Пилот редизайна существующего учебного сценария | PLANNED | MS-N003 | [SKILL.md](../../skills/tasks/0004-redesign-pilot/SKILL.md) | Все pilot URLs и semantic assertions сохранены; пользователь принял actual visual result; visual baseline меняется только для утверждённых экранов. |
| 05 | MS-N005 — Поэтапное внедрение редизайна текущего сайта | PLANNED | MS-N004 | [SKILL.md](../../skills/tasks/0005-redesign-rollout/SKILL.md) | Полная карта существующих экранов и матрица состояний; согласованный дизайн и semantic preservation; assessed placeholders не имитируют runtime. |
| 06 | MS-N006 — Педагогическая спецификация геймификации | PLANNED | MS-N005 | [SKILL.md](../../skills/tasks/0006-gamification-spec/SKILL.md) | Утверждённый набор механик либо явно отложенное решение; формальные positive/negative начисления, idempotency и отдельность знания; модель хранения не объявлена реализованной. |
| 07 | MS-N007 — Knowledge и Content-owned TopicSkill | PLANNED | MS-N006 | [SKILL.md](../../skills/tasks/0007-knowledge-persistence/SKILL.md) | Exact pilot inventory и deterministic depth2 ancestor query, сохранность user history, fresh+upgrade PostgreSQL и идемпотентный импорт. |
| 08 | MS-N008 — Immutable exercise versions и pilot bank | PLANNED | MS-N007 | [SKILL.md](../../skills/tasks/0008-exercise-bank/SKILL.md) | Точные coverage quotas и две содержательно разные structured forms; offline deterministic verification и explicit review учебной математики; без конвертации всех263 уроков. |
| 09 | MS-N009 — Attempts, immutable revisions и recorded help/reveal | PLANNED | MS-N008 | [SKILL.md](../../skills/tasks/0009-attempt-help-lifecycle/SKILL.md) | Immutable submitted snapshot, duplicate no-op/conflict, reveal только после recorded exposure, permanent uniqueness и owner privacy. |
| 10 | MS-N010 — Ограниченный математический parser и normalizer | PLANNED | MS-N009 | [SKILL.md](../../skills/tasks/0010-math-parser/SKILL.md) | Supported pilot grammar reproducible; timeout/limit/unsupported не становятся wrong/misconception, resource limits проверены. |
| 11 | MS-N011 — Детерминированные validators и первый доказанный дефект | PLANNED | MS-N010 | [SKILL.md](../../skills/tasks/0011-deterministic-analysis/SKILL.md) | Validated AnalysisResult не меняет UserSkillState; known deterministic verdict не переопределяется LLM; false strong negative=0 safety subset. |
| 12 | MS-N012 — ProgressEvent, CompletionFact, проекция и replay | PLANNED | MS-N011 | [SKILL.md](../../skills/tasks/0012-progress-replay/SKILL.md) | Online/replay равны по всем state fields, progress-v1 compatibility сохранена; mirror не зависит от Assessment ORM; no evidence overwrite. |
| 13 | MS-N013 — Atomic Analysis → Progress и аудит persisted loop | PLANNED | MS-N012 | [SKILL.md](../../skills/tasks/0013-evidence-finalization/SKILL.md) | Реальная PG история объясняет каждый state change; retry не дублирует evidence; leak/owner/transaction boundaries доказаны. |
| 14 | MS-N014 — Четыре exercise UI, typed steps и help/reveal recovery | PLANNED | MS-N013, MS-N005 | [SKILL.md](../../skills/tasks/0014-exercise-ui/SKILL.md) | Все четыре режима работают с реальным backend, no secret in HTML/JSON/JS/network до reveal, новый attempt не сбрасывает exposure. |
| 15 | MS-N015 — Прогресс, история и завершение onboarding | PLANNED | MS-N014 | [SKILL.md](../../skills/tasks/0015-progress-history/SKILL.md) | UI точно отражает server state и explanation; reading/XP не дают mastery; diagnostic placeholder не имитирует готовую N016. |
| 16 | MS-N016 — Диагностика и adaptive practice с возвратом | PLANNED | MS-N015 | [SKILL.md](../../skills/tasks/0016-diagnostic-practice/SKILL.md) | Exact §10 selection/stop rules и нейтральность skip/unsupported, stable item under refresh, real evidence path и доступный возврат. |
| 17 | MS-N017 — Product LLM provider, AIRun и безопасный fallback | PLANNED | MS-N016 | [SKILL.md](../../skills/tasks/0017-product-provider/SKILL.md) | Обычные tests offline; bad output не создаёт strong negative; actual metadata без PII, provider outage не скрывает working core. |
| 18 | MS-N018 — Tutor policy, reviewed hint bank и conversations UI | PLANNED | MS-N017 | [SKILL.md](../../skills/tasks/0018-tutor/SKILL.md) | No pre-reveal arbitrary mathematical prose leakage; exact context budgets, user/version scope и correct exposure; frontend не bypass-ит сервер. |
| 19 | MS-N019 — Golden evaluation Analyzer/Tutor и safety gates | PLANNED | MS-N018 | [SKILL.md](../../skills/tasks/0019-product-evaluation/SKILL.md) | Сохранены количественные product thresholds/cohorts; failed/timeouts не исключены; модель/prompt/schema/version и бюджет указаны; результаты одного SHA не присвоены другому. |
| 20 | MS-N020 — Реализация только принятых игровых механик | PLANNED | MS-N006, MS-N019 | [SKILL.md](../../skills/tasks/0020-gamification-implementation/SKILL.md) | Каждое начисление объяснимо source/rule/version, двойное невозможно; XP/streak/reading не создают ProgressEvent/mastery, выбранный UX принят. |
| 21 | MS-N021 — Полный учебный цикл на staging | PLANNED | MS-N020 | [SKILL.md](../../skills/tasks/0021-staging-integration/SKILL.md) | Один source SHA/image/public tuple, полный цикл без fixture substitutes и skipped, понятный список remaining human gates. |
| 22 | MS-N022 — Security/privacy, производительность и доступность RC | PLANNED | MS-N021 | [SKILL.md](../../skills/tasks/0022-release-quality/SKILL.md) | Нет открытых blocking security/accessibility findings; >=200 ordinary/10 concurrent и >=30 AI/2 concurrent с согласованным budget; failures включены в metrics. |
| 23 | MS-N023 — Upgrade/restore, публичный RC и browser rehearsal | PLANNED | MS-N022 | [SKILL.md](../../skills/tasks/0023-release-recovery/SKILL.md) | Exact release tuple и unskipped CI, measured restore, successful external full-loop только после разрешения; локальный loopback не называется публичной готовностью. |
| 24 | MS-N024 — Отчёт о реальном AI-процессе, demo и freeze/handover | PLANNED | MS-N023 | [SKILL.md](../../skills/tasks/0024-report-handover/SKILL.md) | Полный reproducible artifact/evidence index, final SHA, реальные ограничения и actual contributions; C-08 описывает применённые AI tools, не обязательство собственного Harness. |

## Соответствие прежней программе

Полные исходные 52 карточки, source hashes, 115 typed edges и approvals сохранены
в [source registry](../../specs/product/task-dispositions-v7.2.json).
Поля `current_*` этого источника — исторический снимок переноса, а
`workflow_disposition`/`workflow_tasks` — актуальная судьба карточки. Их нельзя
смешивать. Текущие зависимости определяются таблицей выше, не историческими
HARD/CONTRACT/HANDOFF/INTEGRATION edges. Исходные IDs не перенумерованы.

| Прежний ID | Судьба | Новые задания / причина |
| --- | --- | --- |
| MS7-R02A | COMPLETED_BASELINE | Сохранён выполненный scope/accepted platform PR54; не объявляет future assessed runtime или новое одобрение addenda. |
| MS7-R03A | COMPLETED_BASELINE | Сохранён выполненный scope/accepted platform PR54; не объявляет future assessed runtime или новое одобрение addenda. |
| MS7-R05 | REMOVED_FROM_PLAN | Снято с плана: собственный Harness выведен, продуктового потребителя нет. |
| MS7-R06A | REMOVED_FROM_PLAN | Снято с плана: собственный Harness выведен, продуктового потребителя нет. |
| MS7-R06B | REMOVED_FROM_PLAN | Снято с плана: собственный Harness выведен, продуктового потребителя нет. |
| MS7-R04A | REMOVED_FROM_PLAN | Снято с плана: собственный Harness выведен, продуктового потребителя нет. |
| MS7-R07 | REMOVED_FROM_PLAN | Снято с плана: собственный Harness выведен, продуктового потребителя нет. |
| MS7-R08 | REMOVED_FROM_PLAN | Снято с плана: собственный Harness выведен, продуктового потребителя нет. |
| MS7-R09 | ADAPTED | MS-N010; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-R10 | ADAPTED | MS-N011; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-R11 | MERGED | MS-N016; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-R12 | MERGED | MS-N018; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-R13 | MERGED | MS-N013; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-R14 | ADAPTED | MS-N019; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-R15 | MERGED | MS-N022; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-R16 | MERGED | MS-N024; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-R17 | MERGED | MS-N023; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-R18 | MERGED | MS-N024; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V02 | COMPLETED_BASELINE | Сохранён выполненный scope/accepted platform PR54; не объявляет future assessed runtime или новое одобрение addenda. |
| MS7-V03 | ADAPTED | MS-N007; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V04 | ADAPTED | MS-N008; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V05 | MERGED | MS-N009; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V06 | MERGED | MS-N009; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V07 | REMOVED_FROM_PLAN | Снято с плана: собственный Harness выведен, продуктового потребителя нет. |
| MS7-V08 | MERGED | MS-N012; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V09 | MERGED | MS-N012; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V10 | MERGED | MS-N013; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V11 | ADAPTED | MS-N017; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V12 | MERGED | MS-N016; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V13 | MERGED | MS-N018; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V14 | MERGED | MS-N021; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V15 | MERGED | MS-N022; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V16 | MERGED | MS-N023; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V17 | MERGED | MS-N023; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-V18 | MERGED | MS-N024; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I02 | COMPLETED_BASELINE | Сохранён выполненный scope/accepted platform PR54; не объявляет future assessed runtime или новое одобрение addenda. |
| MS7-I03 | COMPLETED_BASELINE | Сохранён выполненный scope/accepted platform PR54; не объявляет future assessed runtime или новое одобрение addenda. |
| MS7-I04 | ADAPTED | MS-N005; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I05 | MERGED | MS-N014; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I06 | MERGED | MS-N014; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I07 | MERGED | MS-N014; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I08 | REMOVED_FROM_PLAN | Снято с плана: собственный Harness выведен, продуктового потребителя нет. |
| MS7-I09 | MERGED | MS-N014; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I10 | MERGED | MS-N015; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I11 | MERGED | MS-N015; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I12 | MERGED | MS-N018; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I13 | MERGED | MS-N016; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I14 | MERGED | MS-N021; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I15 | MERGED | MS-N022; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I16 | MERGED | MS-N024; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I17 | MERGED | MS-N023; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |
| MS7-I18 | MERGED | MS-N024; продуктовый scope сохранён, персональные назначения/Harness obligations сняты. |

R01/R02/R03, MS6-R04/MS6-V01/MS6-I01 — выполненный historical baseline;
MS6-R04 сохраняется как история, его продолжение снято, не «выполнено заново».
MS7-HK01 объединена с текущим MS-N000 без выдуманного принятия старой карточки.
MS7-ORG01 адаптирована в MS-N024: actual LMS/registration receipts и данные
участников проверяются человеком; истёкшая дата не становится новым deadline.
Issue52 — отложенное cosmetic наблюдение для MS-N001, не разрешение кодировать UI.

Критерии готовности к переходу: отдельное ревью, исправленные blocking findings,
применимые проверки exact candidate и явная человеческая приёмка. Даже после
merge следующая задача начинается только по новому поручению пользователя.
