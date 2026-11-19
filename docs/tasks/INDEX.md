# Задачи MathStart

## Текущее состояние — 18.11.2026

**MS-T011 принята Русланом 18.11.2026: «Я принимаю», ACCEPTED.** [Issue #84](https://github.com/Tramsey00/MathStart-Python/issues/84), [PR #85](https://github.com/Tramsey00/MathStart-Python/pull/85). Принято дерево `0edef4c8549359a1a2af73807a7ff000e68eed1f` (локальный source `c63edfa`, опубликованный commit `a8dc0b2`). Локально подключён выпуск `ms-t011-c63edfa-20261118`. Независимое полное ревью и merge остаются отдельными шагами; Issue открыт. Следующая основная карточка — **MS-N007**; реализация не начата и требует отдельного поручения после решения об интеграции T011. MS-T010/N006/N020 остаются в backlog.

Внутренние ссылки должны вести прямо на новые canonical URL. Старые публичные учебные адреса после вывода возвращают 404, без прежнего UI и без перенаправления. Это решение 16.11.2026 заменяет прежнее требование сохранять legacy lesson redirects. Технические HTTPS/auth redirects не отменяются. Подробная карта вывода lesson/category/prefix aliases, runtime/pinned-release границы и приёмка GET/HEAD/SPA закреплены в карточке T011 (уточнение 18.11.2026).

Руслан принял MS-T003 (35/35, source `8673cd39778f4b9df99f7612d972fd29fc5b1228`)
и MS-T005 (75/75, source `e2aa448da8dbcf675428a00e4ff8ee0d73732e50`).
PR #63 и PR #62 объединены Русланом в main (итоговый SHA
`5a5ef883f1017d646ad0ff8f849a0af97a6078fa`). Замечания T003-RV-004/005
приняты как исключения, исправлять их не требуется.
Автоматические проверки: NOT_RUN_BY_USER_REQUEST. Интеграция не означает
повторного браузерного просмотра или публикации объединённой версии.

**Не путать ID:** принятая MS-T011 завершает публичную интеграцию. MS-N011 — математические validators, только после N007 → N008 → N009 → N010. Эта актуализация не начинает реализацию ни одной из карточек.

Требования к карточке T011 уточнены в [Issue #82](https://github.com/Tramsey00/MathStart-Python/issues/82): закреплены порядок замены legacy-зависимостей до удаления файлов, сохранность Content identity/данных, общая 404 и раздельная приёмка source/активного release. База — слитый PR #81, main `e25f302210a91e01364cc637a794704870fbcf31`. Этот Issue относится к подготовке требований. Реализация ведётся в Issue #84.

По дополнению Руслана 18.11.2026 в T011 обязательна адресная уборка остатков переноса: подтверждённо ненужных временных файлов, дублей, мёртвого кода и устаревших рабочих инструкций с обновлением потребителей/ссылок. Учебные материалы, пользовательские данные, необходимые ресурсы, история приёмки и сохранённые рабочие результаты защищены; подробные границы и критерий завершения — в карточке.

## Текущее сопровождение

[Issue #66](https://github.com/Tramsey00/MathStart-Python/issues/66) закрыт. [Карточка организации](../../skills/tasks/project-organization/HISTORY.md) хранит отчёт исходного этапа. Дополнительная адресная очистка выполняется в MS-T011, в PR #85.

## Как пользоваться очередью

Карточки и [registry.json](registry.json) — одна очередь; прежние source cards
и персональные планы не назначают работу. Зависимости продуктовых задач должны быть приняты перед реализацией. Для T011 входом служат объединённые source-complete классы с peer review; приёмка общего runtime выполняется в самой T011.
Порядок взаимного ревью классов закреплён решением от 12.11.2026 ниже. Статусы: PLANNED → IN_PROGRESS → READY_FOR_REVIEW →
HUMAN_ACCEPTANCE_PENDING → ACCEPTED; DEFERRED_BY_USER для явно отложенного объёма; CHANGES_REQUESTED и BLOCKED_DEPENDENCY/
BLOCKED_DECISION сопровождаются причиной. Merge фиксируется отдельно.

[Inventory](lesson-inventory.json) содержит 263 темы. Null URL не разрешает
вычислять адрес по порядку переноса. Принятые пилоты переиспользуются в своих
классах; их адреса и общий UI определены [стандартом](../frontend/lesson-migration.md).
Дизайн не выбирается заново. Общие правила — [AGENTS](../../AGENTS.md),
[архитектура](../../ARCHITECTURE.md), [UI-контракт](../ux/shared-ui-contract.md).

| Порядок | ID / название | Статус | Зависимости | Карточка | Приёмка |
| --- | --- | --- | --- | --- | --- |
| 00 | MS-T000 — Подготовить очередь, стандарт переноса и очистить документацию | ACCEPTED | — | [SKILL.md](../../skills/tasks/t000-workflow-preparation/SKILL.md) | Очередь/карточки согласованы друг с другом, inventory содержит все 263 темы; нет конфликтующих текущих ТЗ и битых действующих ссылок; удалённое восстанавливается из точного Git SHA; scope проверок и ограничения честно отражены. |
| 01 | MS-T001 — Перенести новый HTML-урок по стандарту в основной React/SSG runtime | ACCEPTED | MS-T000 | [SKILL.md](../../skills/tasks/t001-lesson-pilot/SKILL.md) | Линейный пилот сохраняет canonical /materials/7-algebra-8; окончательное решение Руслана 08.11.2026 отдаёт /materials/7-algebra-1 первой теме, прежний alias отменён до публичного выпуска. /materials/7-algebra-37 не создаётся; прежняя приёмка пилота и исторические receipts не переписываются. |
| 02 | MS-T002 — Подключить утверждённые главную и каталог к основному приложению | ACCEPTED | MS-T001 | [SKILL.md](../../skills/tasks/t002-public-pages/SKILL.md) | Главная и /materials используют общий header/footer, реальные catalogue данные, поиск и grade navigation; нет localhost8121/5173 links или prototype-only virtual modules в runtime; старые catalogue URLs имеют явную совместимость. |
| 03 | MS-T002A — Подготовить воспроизводимый запуск после clone и передать baseline команде | ACCEPTED | MS-T002 | [SKILL.md](../../skills/tasks/t002a-team-local-start/SKILL.md) | Windows host-dev в обычной рабочей папке: Vite/FastAPI на хосте, PostgreSQL в Docker; HMR/авторелоад, сохранение данных, подготовка и обновление по инструкции. Отдельные review/приёмка, решение о merge и clone опубликованного main до MS-T003. |
| 04 | MS-T003 — Полностью перенести 5 класс | ACCEPTED | MS-T002A | [SKILL.md](../../skills/tasks/t003-grade-5/SKILL.md) | Все 35 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, пользователь принял cohort. |
| 05 | MS-T004 — Полностью перенести 6 класс | HUMAN_ACCEPTANCE_PENDING | MS-T002A | [SKILL.md](../../skills/tasks/t004-grade-6/SKILL.md) | Все 28 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, коллега завершил независимое ревью; итоговая приёмка Русланом после всех классов. |
| 06 | MS-T005 — Полностью перенести 7 класс | ACCEPTED | MS-T002A | [SKILL.md](../../skills/tasks/t005-grade-7/SKILL.md) | Все 75 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, пользователь принял cohort. |
| 07 | MS-T006 — Полностью перенести 8 класс | HUMAN_ACCEPTANCE_PENDING | MS-T002A | [SKILL.md](../../skills/tasks/t006-grade-8/SKILL.md) | Все 66 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, коллега завершил независимое ревью; итоговая приёмка Русланом после всех классов. |
| 08 | MS-T007 — Полностью перенести 9 класс | HUMAN_ACCEPTANCE_PENDING | MS-T002A | [SKILL.md](../../skills/tasks/t007-grade-9/SKILL.md) | Все 46 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, коллега завершил независимое ревью; итоговая приёмка Русланом после всех классов. |
| 09 | MS-T008 — Полностью перенести 10 класс | HUMAN_ACCEPTANCE_PENDING | MS-T002A | [SKILL.md](../../skills/tasks/t008-grade-10/SKILL.md) | Все 13 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, коллега завершил независимое ревью; итоговая приёмка Русланом после всех классов. |
| 10 | MS-T009 — Вход по логину, личный кабинет и защита аккаунта | ACCEPTED | MS-T002A | [SKILL.md](../../skills/tasks/t009-identity-ui/SKILL.md) | Вход по логину, единая страница auth, новый ЛК и подтверждённая необязательная почта восстановления; главная расширена в стиле MathStart, auth без шапки/footer, ЛК перекомпонован, сессия обрабатывается без технических экранов; серверная защита и профильные проверки, сохранены пользователи; настоящая доставка почты и локальная готовность учтены отдельно. |
| 11 | MS-T011 — Завершить интеграцию сайта и вывести старые публичные страницы | ACCEPTED | MS-T009 | [SKILL.md](../../skills/tasks/t011-rollout-finalization/SKILL.md) | Объединённые 263 React-темы доступны по прямым новым canonical URL; внутренние ссылки не используют старые адреса; выведенные публичные учебные URL возвращают 404 без старой страницы и без legacy redirect. Staff redesign и реорганизация QA не блокируют интеграцию; профиль проверок согласуется отдельно. |
| 12 | MS-N007 — Knowledge и Content-owned TopicSkill | PLANNED | MS-T011 | [SKILL.md](../../skills/tasks/0007-knowledge-persistence/SKILL.md) | Exact pilot inventory и deterministic depth2 ancestor query, сохранность user history, fresh+upgrade PostgreSQL и идемпотентный импорт. |
| 13 | MS-N008 — Immutable exercise versions и pilot bank | PLANNED | MS-N007 | [SKILL.md](../../skills/tasks/0008-exercise-bank/SKILL.md) | Точные coverage quotas и две содержательно разные structured forms; offline deterministic verification и explicit review учебной математики; без конвертации всех263 уроков. |
| 14 | MS-N009 — Attempts, immutable revisions и recorded help/reveal | READY_FOR_REVIEW | MS-N008 | [SKILL.md](../../skills/tasks/0009-attempt-help-lifecycle/SKILL.md) | Immutable submitted snapshot, duplicate no-op/conflict, reveal только после recorded exposure, permanent uniqueness и owner privacy. Неавторизованные запросы не создают попытки, записи решений или LLM-запуски. |
| 15 | MS-N010 — Ограниченный математический parser и normalizer | READY_FOR_REVIEW | MS-N009 | [SKILL.md](../../skills/tasks/0010-math-parser/SKILL.md) | Supported pilot grammar reproducible; timeout/limit/unsupported не становятся wrong/misconception, resource limits проверены. |
| 16 | MS-N011 — Детерминированные validators и первый доказанный дефект | READY_FOR_REVIEW | MS-N010 | [SKILL.md](../../skills/tasks/0011-deterministic-analysis/SKILL.md) | Validated AnalysisResult не меняет UserSkillState; known deterministic verdict не переопределяется LLM; false strong negative=0 safety subset. |
| 17 | MS-N012 — ProgressEvent, CompletionFact, проекция и replay | PLANNED | MS-N011 | [SKILL.md](../../skills/tasks/0012-progress-replay/SKILL.md) | Online/replay равны по всем state fields, progress-v1 compatibility сохранена; mirror не зависит от Assessment ORM; no evidence overwrite. |
| 18 | MS-N013 — Atomic Analysis → Progress и аудит persisted loop | PLANNED | MS-N012 | [SKILL.md](../../skills/tasks/0013-evidence-finalization/SKILL.md) | Реальная PG история объясняет каждый state change; retry не дублирует evidence; leak/owner/transaction boundaries доказаны. |
| 19 | MS-N014 — Четыре exercise UI, typed steps и help/reveal recovery | PLANNED | MS-N013, MS-T009 | [SKILL.md](../../skills/tasks/0014-exercise-ui/SKILL.md) | Все четыре режима работают с реальным backend, no secret in HTML/JSON/JS/network до reveal, новый attempt не сбрасывает exposure. Публичная самопроверка без LLM доступна без входа и не создаёт attempts/mastery. Задания с помощником для гостя размыты и неинтерактивны; сервер запрещает guest submit/LLM calls. |
| 20 | MS-N015 — Прогресс, история и завершение onboarding | PLANNED | MS-N014 | [SKILL.md](../../skills/tasks/0015-progress-history/SKILL.md) | UI точно отражает server state и explanation; reading/XP не дают mastery; diagnostic placeholder не имитирует готовую N016. |
| 21 | MS-N016 — Диагностика и adaptive practice с возвратом | PLANNED | MS-N015 | [SKILL.md](../../skills/tasks/0016-diagnostic-practice/SKILL.md) | Exact §10 selection/stop rules и нейтральность skip/unsupported, stable item under refresh, real evidence path и доступный возврат. |
| 22 | MS-N017 — Product LLM provider, AIRun и безопасный fallback | PLANNED | MS-N016 | [SKILL.md](../../skills/tasks/0017-product-provider/SKILL.md) | Обычные tests offline; bad output не создаёт strong negative; actual metadata без PII, provider outage не скрывает working core. |
| 23 | MS-N018 — Tutor policy, reviewed hint bank и conversations UI | PLANNED | MS-N017 | [SKILL.md](../../skills/tasks/0018-tutor/SKILL.md) | No pre-reveal arbitrary mathematical prose leakage; exact context budgets, user/version scope и correct exposure; frontend не bypass-ит сервер. |
| 24 | MS-N019 — Golden evaluation Analyzer/Tutor и safety gates | PLANNED | MS-N018 | [SKILL.md](../../skills/tasks/0019-product-evaluation/SKILL.md) | Сохранены количественные product thresholds/cohorts; failed/timeouts не исключены; модель/prompt/schema/version и бюджет указаны; результаты одного SHA не присвоены другому. |
| 25 | MS-N021 — Полный учебный цикл на staging | PLANNED | MS-N019 | [SKILL.md](../../skills/tasks/0021-staging-integration/SKILL.md) | Один source SHA/image/public tuple, полный цикл без fixture substitutes и skipped, понятный список remaining human gates. |
| 26 | MS-N022 — Security/privacy, производительность и доступность RC | PLANNED | MS-N021 | [SKILL.md](../../skills/tasks/0022-release-quality/SKILL.md) | Нет открытых blocking security/accessibility findings; >=200 ordinary/10 concurrent и >=30 AI/2 concurrent с согласованным budget; failures включены в metrics. |
| 27 | MS-N023 — Upgrade/restore, публичный RC и browser rehearsal | PLANNED | MS-N022 | [SKILL.md](../../skills/tasks/0023-release-recovery/SKILL.md) | Exact release tuple и unskipped CI, measured restore, successful external full-loop только после разрешения; локальный loopback не называется публичной готовностью. |
| 28 | MS-N024 — Отчёт о реальном AI-процессе, demo и freeze/handover | PLANNED | MS-N023 | [SKILL.md](../../skills/tasks/0024-report-handover/SKILL.md) | Полный reproducible artifact/evidence index, final SHA, реальные ограничения и actual contributions; C-08 описывает применённые AI tools, не обязательство собственного Harness. |

Три необязательные задачи вынесены в [backlog](../backlog/README.md). Статусы и зависимости хранятся в едином registry.

ID карточек остаются постоянными для ссылок и истории; поле order и колонка
«Порядок» определяют последовательность. Основной оставшийся путь:
**T011 → N007 → N008 → N009 → N010 → N011 → N012 → N013 → N014 → N015 →
N016 → N017 → N018 → N019 → N021 → N022 → N023 → N024**.
Переход к следующей задаче выполняется только по отдельному поручению.

## Границы текущей редакции

Первые пять прежних дизайн-карточек выведены; mapping сохранён в registry.json.
Старые 52 source cards, deadlines и персональные назначения доступны только
в Git, не задают текущий порядок. Будущие N006–N024 сохранены с уточнёнными
зависимостями; существование карточек не означает готовую persistence/API.
Авторизация I02/I03 не является утверждённым интерфейсом. Решение 13.11.2026:
MS-T009 — вход по логину/паролю, необязательная подтверждённая почта только для
восстановления, новый ЛК без будущего прогресса. Backend можно расширять с
сохранением пользователей и данных. Полные требования — в карточке. Staff — MS-T010.

## Bootstrap и работа команды

MS-T001 → MS-T002 → MS-T002A выполнялись в ui/ux без отдельных Issue и веток.
PR #58 уже слит; контроль опубликованного main завершён.
MS-T002A принята пользователем 08.11.2026; повторять установку и контроль не нужно.

Начиная с MS-T003: GitHub Issue → отдельная ветка от актуального origin/main
после fetch → реализация и отдельно порученные проверки → PR со ссылкой на Issue →
review/fixes → готовность класса → итоговая приёмка общей версии → решение о merge. Пример ветки: ms-t003-grade-5,
без codex/. Продолжать существующие Issue/ветки/PR без дублей.

## Завершение переноса — решение Руслана 12.11.2026

Владимир и Илья работают параллельно по уже согласованным между ними очередям.
Не переназначай классы и не придумывай персональное распределение. У каждого
один активный класс, отдельные Issue, ветка и PR. После исправлений и независимого
ревью коллеги разрешён переход к следующему классу своей согласованной очереди
без промежуточной приёмки Русланом. Неизвестный состав очереди уточни у исполнителя.

Коллега вручную просматривает все URL класса: адрес и заголовок, прокрутка,
характерные интерактивы; подробнее — известные риски. Один итоговый комментарий
в PR содержит source SHA, release, охват, недоступные страницы и замечания
«URL — дефект — воспроизведение». Исправленные места перепроверяет тот же коллега.
Готовность исходников, независимое ревью, интеграция и приёмка учитываются отдельно.

Руслан выполняет одну итоговую проверку общей версии после завершения оставшихся
классов. До неё статус готового класса — HUMAN_ACCEPTANCE_PENDING, не ACCEPTED.
Принятые 5-й и 7-й классы остаются ACCEPTED. Решение о merge в main остаётся
за Русланом; разрешение продолжать свою очередь не разрешает merge.
Уточнение 13.11.2026: MS-T009 разрешена параллельно классам после MS-T002A,
без вмешательства в учебный перенос; общая auth-навигация согласуется отдельно.
Общие исправления согласуются между
исполнителями и переиспользуются, материалы чужого класса не перезаписываются.

Автопрогоны: NOT_RUN_BY_USER_REQUEST. Штатные валидаторы Content и review точного
плана публикации сохраняются; локальный план подтверждает человек, работающий
со своей БД. Новое правило приёмки не требует участия Руслана в каждой локальной публикации.

N006 имеет отдельное педагогическое решение, но не блокирует Knowledge.

[История решений и промежуточных передач](HISTORY.md).
