# MathStart — техническое задание v7.2 (полная рабочая редакция)

> DRAFT_REFERENCE_ONLY. Это черновик продуктового ТЗ, а не поручение на реализацию.
> Перенос существующего сайта принят и слит; [текущий итог](../maintenance.md). Работа начинается только по новому поручению пользователя.
> Исторические карточки, роли и даты ниже сохраняют требования и provenance;
> они не создают отдельные задания и не разрешают реализацию будущих функций продукта.

**DRAFT_REFERENCE_ONLY / PRODUCT HUMAN_PENDING.** Сверка источника18.10.2026, актуализация статуса19.10.2026, Europe/Moscow. Все32 главы и52 canonical product task cards исходного v7.1 сохранены. Миграция существующего сайта принята в PR54, main3a290a46d991e22269a17dde41e39f0637576071 прошёл обязательный CI. Это не утверждение будущих Product Gates и не production deployment. Исторический PDF доступен по закреплённому Git SHA/path; G0 v7.1 не переносится как approval этой продуктовой редакции.

Сверка полного114-страничного PDF и52 карточек выполнена;115 явных typed dependency edges совпадают с источником. Исправлено геометрическое расположение знаков ≤/≥/→, искажённое первоначальным извлечением PDF; численные значения не менялись. [Provenance/changelog](technical-spec-v7.2-provenance.md) фиксирует источники, границы сверки и ещё ожидающуюся общую приёмку.

Изменения этой редакции: принятая FastAPI/SQLAlchemy/Alembic и React/TypeScript платформа; Django-independent operational boundary; public manifest prerender; совместимые auth/session/receipt adapters; task/Issue migration workflow;52-row platform disposition и dependency/readiness вместо новых обещаний календаря. Доменная семантика, numerical defaults, organisational roles и course requirements сохраняются. Исходные карточки и зависимость каждого типа доступны в machine-readable source registry. Принятый SHA, CI, текущие runbooks и границы production описаны в кратком maintenance-итоге; исторические результаты сохраняют свои SHA.

## 1. Паспорт и правила применения

Редакция v7.2 — DRAFT, человеческая приёмка HUMAN_PENDING. Полный исходный v7.1 сохранён в Git3a290a46d991e22269a17dde41e39f0637576071:docs/specifications/sources/technical-spec-v7.1.pdf с SHA256 e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd. Исторический G0 v7.1 принят30.09.2026; это не approval редакции v7.2. Нормативная платформа переноса принята в ADR-0006 и R02 migration contracts. Принятая миграция PR54 и завершённая консолидация PR55, их точные SHA и evidence описаны в [maintenance](../maintenance.md). Пользователь принял адаптацию платформы v7.2; это не утверждение всей продуктовой редакции, будущих gates или production rollout. Новые сроки основной программы не назначены.

### Исторический паспорт и источники v7.1

Репозиторий: https://github.com/Tramsey00/MathStart-Python. Проверенный main:
fc4e907149da026e4710c3e453d8065c0106e4b9, merge 28.09.2026. Live GitHub проверен 29.09.2026 через
connector в режиме чтения. Локальный HEAD совпадает. ZIP содержит те же 870 отслеживаемых файлов:
545 побайтово совпадают, 325 отличаются только CRLF/LF, смысловых расхождений нет. Это снимок
состояния, а не гарантия неизменности main после даты проверки. Команда: Руслан — технический
руководитель, архитектура, алгоритмы, Harness, интеграция; Владимир — backend, PostgreSQL, данные и
эксплуатация; Илья — frontend, UX и browser verification. Полные официальные ФИО/группы,
подтверждение регистрации и согласования MathStart в LMS: TBD, закрываются организационной
задачей MS7-ORG01 до 09.10 включительно. Слова «должен», «обязательно» и числа приёмки задают
требования к будущему результату после G0. «Реализовано» относится только к проверенному main.
PLANNED не означает начатую работу. FROZEN/DONE означает исторически принятую работу в
установленном ниже объёме. Проектные решения не приписываются преподавателю. Весь intelligent
runtime, кроме явно перечисленного baseline, ещё предстоит реализовать. Приоритет источников
требований курса: новые прямые слова преподавателя, прежние слова, официальные материалы,
интерпретация v6. Приоритет состояния проекта: merged main, принятые ADR/specs, review и CI, затем
v6. Будущие решения соблюдают требования курса и принятые границы архитектуры. Противоречие
оформляется ADR/contract addendum; агент не меняет семантику молча. Доступные первоисточники: ТЗ
v6 от 25.09 (56 страниц); ZIP; полная лекция 1 (L1, 28:39); лекция 2 TXT/SRT (L2, 20:56, два представления
одной записи); последний созвон webcams.srt (L3, 34:11); вопросы и исторический фрагмент чата R03;
main, PR/reviews/CI; внешние учебные примеры Harness. Материалы LMS и официальный календарь
зачётной недели не предоставлены. Чат — исторический контекст, не источник разрешения менять
проект. Точные контрольные суммы включены в отдельный audit.

---

## 2. Проверенное состояние и frozen baseline

### 2.0. Снимок переноса

MIG_BASE_SHA60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7; принятый migration integration a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6. Пять результатов R01/R02/V01/V02/I01 программы MS7-MIG сохранены. Единая миграция завершена и принята в PR54; консолидация завершена в PR55. Точные результаты и границы приёмки — в [maintenance](../maintenance.md). Дальнейшая таблица описывает исторический baseline v7.1, а не современную полноту FastAPI/React.

### Исторические результаты v7.1
2.1. Что работает сейчас
Сайт — Django modular monolith. В INSTALLED_APPS из проектных приложений существует content;
используются Django auth/admin. content/models.py содержит Grade, Subject, Section, ContentPage.
Учебная тема — ContentPage типа TOPIC. Сохраняются curriculum/, site_content/, публикационные
инструменты, шаблоны и HTML/CSS/JS. В исходниках есть материалы 5–10 классов; продуктовый фокус 5–
9 не разрешает удалять существующий 10-й класс. Проверка обнаруживает 263 темы; существующие
материалы не требуется превращать целиком в intelligent exercises. PostgreSQL dev/test и CI настроены и
имеют успешное исполнение; SQLite допускается только явно как compatibility-режим, без
автоматического отката при ошибке PostgreSQL. Docker/Compose — dev/test foundation, не production
deployment. CI на main 36449820246 завершён успешно: dependency install, runtime report, bounded failed
connection, fresh PostgreSQL migration/bootstrap/static/content smoke, canonical verification. Workflow
использует Python 3.12 и PostgreSQL 16. Точная patch-версия CI здесь не заявляется без лога version-
report. Локальная повторная проверка 29.09: Python 3.10.11, Django 5.2.16, pip 26.1.2, SQLite; psycopg
локально не установлен. verify_repo.py: PASS 8/8; Django — 24 теста, 2 PostgreSQL-specific skipped; R03 —
18 pure tests; Harness — 73 tests. pip check прошёл, но это не доказывает установку полного lock.
Локальный результат не доказывает Python 3.12+/PostgreSQL/Compose execution. Они не подменяют друг
друга. На main отсутствуют runtime-модули Knowledge, Progress, Assessment, Analyzer, Tutor, Adaptive и
продуктовые LLM adapters. DRF, SymPy, Pydantic не являются уже установленным стеком. Их добавление
выполняется scoped tasks с lock и проверками. I01 — UX-контракты и wireframes, не работающий
frontend. R03 — чистый reference reducer, не persisted Progress.
2.2. Реестр принятой работы
Историческая задача
Подтверждение
Точный frozen объём
R01
PR #2, merge 24.09, 0a5398d6
Repository knowledge, workflow, verification; accepted owner record. Независимого GitHub APPROVED нет.
R02
PR #5, merge 24.09, 951ad487
Четыре modes, PublicExerciseDTO/server Validation, ordered typed steps, exercise contract. Полного HTTP API
ещё нет.
R03
PR #7 и #8, merge 24.09, 61042ddb / e410a4e2
10 skills/13 edges, progress-v1, exact reducer/fixtures, closeout; 18 pure tests.
MS6-R04
PR #10, final head f401dc6, merge 9f705b0e
Runner, Adapter Protocol, FakeAdapter, deadline boundaries, validated READY publication receipt, verification.
Владимир APPROVED 27.09.
MS6-I01
PR #11, final head fe60f035, merge 861433a6
SC-01–08, states matrix, 8 desktop/mobile SVGs; review Руслана и Владимира.
MS6-V01
PR #14, final head 0c3556ad, merge fc4e9071
PG/lock/CI/fresh-install/dev-test, publication locking fix, source preservation; Руслан APPROVED 28.09.
R01/R02/R03 сохраняют свои реальные короткие исторические идентификаторы; обозначение «MS6R01–
03» допускается только как alias строки старого календаря. Completed IDs не превращаются в MS7. PR
#2/#5/#7 не имеют formal independent approval в API; записанное owner acceptance и merge достаточно
для сохранения заданного frozen baseline, но не доказывают современный независимый gate. Новые
работы требуют независимого review. Проверены 13 issue/PR записей: issues #1/#4/#6/#9/#12/#13 и PR
#2/#5/#7/#8/#10/#11/#14 закрыты; открытых на момент проверки нет. Из 20 полученных runs есть
исторические failures; последующий success не стирает их из evidence. Главная ветка API сообщает
protected:false. Требование green CI существует в процессе, но техническая branch protection не доказана
и должна быть отдельно настроена после human gate.
2.3. Сохранение сильной реализации R04
READY_FOR_REVIEW — успешный результат проверок и публикации пакета, а не разрешение merge.
Одного JSON со словом READY недостаточно. Поддерживаемые readers проверяют digest-bound receipt,
идентичность run и deadline; runner и status используют одну каноническую интерпретацию. Commit
point — завершённая вовремя canonical replacement. Receipt может физически завершиться позже
deadline, если подтверждает своевременный commit. Crash между replacement и receipt не даёт READY;
ambiguous replacement, реально записавший корректный receipt, должен одинаково
интерпретироваться CLI и status. Deadline проверяется на границах model/tool/verification/publication.
R04 не обещает физическое прерывание произвольного зависшего внешнего вызова. Будущий sandbox
добавляет process termination, не ослабляя receipt protocol. MESSAGE продолжает model loop; protocol
version и manifest digest проверяются; runtime branch enforcement сохранён, smoke использует fixture и
не требует task branch. Stale human acceptance pending, активное положение закрытых планов и DRAFT в
adapter document — housekeeping MS7-HK01. Это не повод переоткрыть R04/V01/I01. Исправление
NOT_STARTED в I01 уже есть в main; повторно объявлять его дефектом нельзя. Простыми словами:
сейчас есть сайт, проверяемые правила будущей системы и надёжный каркас запуска агента. Умная
учебная система и настоящий coding-model adapter ещё не готовы.

---

## 3. Цель, пользователи и границы продукта
Ученик читает тему, решает задачу одним из четырёх способов, получает проверяемую обратную связь,
безопасную помощь и практику на нужный prerequisite. Система хранит причины изменения прогресса,
а не только итоговый процент. Успех MVP — воспроизводимый полный путь на публичном HTTPS URL, а
не наличие чата или рост mastery от открытия страницы.
CORE MVP: сохранить каталог и публикацию, auth/profile/onboarding, доступный browser UI, версия
контента, история, безопасность, deployment, backup/restore. INTELLIGENT PILOT: три темы
(отрицательные числа; распределительное свойство/скобки; линейные уравнения со скобками), 10
skills/13 edges, 40 assessed exercises и минимум 3 SELF_CHECK, Analyzer, Progress, diagnostics/adaptive
practice, Tutor. Engineering Harness — отдельный обязательный проектный результат, используемый
командой для разработки. В 40 assessed exercises должно быть ≥4 PRIMARY упражнения на каждый skill,
≥12 STEP_BY_STEP, ≥12 FINAL_ANSWER, ≥2 содержательно разных STRUCTURED_SOLUTION schemas. Один
exercise имеет один PRIMARY skill для подсчёта покрытия; secondary mappings не позволяют дважды
закрывать квоту. Для каждого skill ≥2 уровня сложности; для скобок/уравнений присутствуют уровни 2, 3, 4. Схемы structured: например, поля раскрытия скобок и переносов/упрощения уравнения; это
различные проверяемые формы, а не две копии UI. POST-MVP FR-25–29: вся школьная математика с
произвольными преобразованиями, геометрический canvas, OCR рукописных решений, полный RAG,
роли родителей/учителей. Не входят обучение собственной LLM, дополнительный frontend-стек помимо принятого React/TypeScript, microservices, Neo4j,
Redis/Celery без отдельного обоснования. Внешние context/memory tools могут оцениваться отдельно и
не являются зависимостью MVP без отдельного human decision/ADR. Роли: anonymous читает published
каталог; student управляет только своими попытками, сессиями, диалогами и прогрессом; staff публикует
и архивирует контент через доверенные инструменты; operators обслуживают среду с минимальными
правами. Продуктовая LLM не является пользователем с доступом к ORM. Административная редактура
content не должна менять historical evidence.

---

## 4. Решения и границы доверия
ADR-0006 заменяет платформенную часть ADR-0001: FastAPI/Pydantic, SQLAlchemy2/Alembic, React/TypeScript/Vite/React Router с полным public prerender. PostgreSQL16+ и модульный Python-монолит сохраняются. ADR-0002 фиксирует exercise boundaries; ADR-0003 фиксирует Knowledge/Progress. Frozen HTTP/CompletionFact contracts и их текущие acceptance receipts сохраняются; будущая persistence не объявляется реализованной. D-021–026 из v6 были предложениями, а не
автоматически принятыми ADR; v7 сохраняет их смысл и задаёт новые задачи для согласования.
Решение
Статус и реализация
D-021 CompletionFact/progress-v1.1
Предложено; MS7-R03A оформляет ADR/addendum и parity до V08/V09. Старые формулы v1 сохраняются.
D-022 immutable revision, cross-attempt exposure, один positive
Предложено как backend addendum MS7-R02A; отражённые в I01 UX-требования не равны реализации.
D-023 HTTP/idempotency/retry
MS7-R02A; OpenAPI + fixtures раньше auth/attempt clients.
D-024 limits/evals/retention/performance
Классификация A/B/C в Operational Defaults Registry §16; значения и release criteria сохранены; G0,
R14/R15/V15.
D-025 curated pre-reveal Tutor
Сохранено; R12/V13; LLM выбирает допустимое действие, не публикует произвольное решение.
D-026 controlled Harness
Сохранено; R05/R06A/R06B/R07/R04A/R08, V07/I08. R04 bootstrap не равен G1.
D-027 live adapter capability gate
Новое уточнение; explicit adapter task R04A и negative enforcement proof.
D-028 typed dependencies и baseline rebase
Новое управление планом; граф календарных зависимостей, без переоткрытия frozen work.
Номера D-001–020 не реконструируются по памяти: в переданном v6 нет полного нумерованного
реестра. Их содержательные базовые решения закреплены указанными ADR и настоящими разделами;
вымышленных соответствий ADR не вводится. Два AI-контура разделены. Product AI (Analyzer/Tutor)
видит минимальный учебный контекст, имеет отдельные credentials/budgets/AIRun и не выполняет tools
ОС. Engineering AI видит разрешённый checkout, работает через Harness Registry/Policy/Sandbox и пишет
run trace. Ключи двух контуров, prod DB и student logs не передаются друг другу. Доверенные: reviewed
contracts, publisher, deterministic validator, domain services. Недоверенные: ответы ученика, содержимое
исходников для coding agent, LLM response, external tool output, сообщения subagents. Schema validation
устанавливает форму, но не математическую истинность. Инструкция в lesson/README/trace не
повышает права агента.

---

## 5. Модули, зависимости и потоки
Домен
Владение
Разрешённые чтения и вызовы
users
Совместимая identity, Profile, onboarding; FastAPI services/SQLAlchemy repositories
Пользовательский контекст; без Progress ORM writes
content
Grade/Subject/Section/ContentPage, TopicSkill
Зависит от Knowledge для FK; не владеет Skill
knowledge
Skill, Prerequisite, версии graph
Не зависит от Content/Progress/AI
assessment
Exercise/Version/Validation, Attempt/Step/Event, CompletionFact, Analysis record, Diagnostics
Knowledge, Content references, math/analyzer service, Progress public ingest
progress
ProgressEvent, completion mirror, UserSkillState, reducer/replay
Knowledge и собственные DTO; не импортирует Assessment models
math_validation
parser, normalization, exact validators
Чистые typed inputs; не обращается к DB/LLM
analyzer
AnalysisResult/taxonomy/evidence validation
math_validation; llm interface для неопределённых случаев; нет state writes
adaptive
selector, PracticeSession/items
read Progress/Knowledge/Content; Assessment API для попыток
tutor
Conversation, Message, context policy
read models через services, Assessment help API, llm; нет writes в Progress
llm
provider interface, AIRun, prompts/versioning
SDK только здесь; не зависит от доменных ORM
harness
инженерные run/context/tools/policy/trace
Checkout и разрешённые checks; не импортируется production app
Стрелка A→B означает «A вызывает публичный контракт B». FK/string references не оправдывают
циклические runtime imports. Зависимость Assessment→Progress односторонняя: он передаёт
валидированный пакет evidence, Progress проверяет и изменяет только свою проекцию.
Идентификаторы source в Progress — значения/DTO; reverse ORM dependency на Assessment не нужен.
Анализатор возвращает результат, а Assessment решает, какой event допустим. Topic — термин API для
ContentPage(TOPIC), новый дублирующий Topic model не создаётся. TopicSkill принадлежит Content и
связывает ContentPage с Knowledge.Skill. Архивирование skill/version защищает историю; удаление
evidence-referenced объектов запрещено. Публикационный pipeline читает filemanaged sources и
обновляет content, не пытается «инициализировать заново» пользовательский прогресс. Основной
поток: browser→Assessment draft/submit→immutable snapshot→deterministic validation→возможный
bounded Analyzer→transactional finalization→Progress ingest/reducer→public result. Tutor help/reveal
проходят тот же Assessment service. Adaptive выбирает задачу из разрешённого pool, не начисляет
прогресс сам. Sequence submit: (1) auth/CSRF/owner/schema/idempotency; (2) короткая транзакция lock
attempt и exposure, freeze revision, operation_id, SUBMITTED; (3) вычисление/LLM вне DB transaction; (4)
транзакция lock owner/skill проекций в stable order, проверка snapshot digest/policy, запись
Analysis+CompletionFact+ProgressEvent и COMPLETED; (5) return persisted response. Повтор finalization не
создаёт вторую историю. Сбой до (4) оставляет повторяемую operation, а не фиктивный успех. Простыми
словами: модули договариваются через узкие входы. Только Progress меняет долговременные знания
ученика, и только после проверенного свидетельства о решении.

---

## 6. Данные, ключи, миграции
Ниже — целевая схема продукта, не перечень уже реализованных SQLAlchemy моделей. Applied Django migrations сохраняются как история; целевая DDL цепочка — additive reviewed Alembic. Новые PK — UUID; existing
ContentPage identifiers/slugs сохраняются. FK к history используют PROTECT/архивирование. Все
timestamps aware UTC с микросекундами. Массовые seed/import сначала валидируют пакет, затем
атомарно публикуют.
Сущность
Минимальные поля и ограничения
Profile
user OneToOne, выбранный класс, onboarding_mode/status, created_at; не хранит mastery
Skill
code UNIQUE immutable, title, description, active, graph_version
Prerequisite
from_skill/to_skill, UNIQUE pair, no self-edge; cycle validation в service и импорте
TopicSkill
content_page, skill, role PRIMARY/SECONDARY, importance>0, UNIQUE pair, published mapping version
Exercise
stable code UNIQUE, topic, archived; logical identity
ExerciseVersion
exercise+version UNIQUE, mode, difficulty 1–4, public statement/schema, status, digest, provenance; published
immutable
ExerciseValidation
OneToOne version, server-only checker type/version, answer/rules/reference steps, digest
ExerciseSkill
version+skill UNIQUE, PRIMARY/SECONDARY; один PRIMARY в pilot
Attempt
user, exercise_version, previous_attempt, revision, snapshot_digest, state, outcome, operation_id,
created/submitted/completed_at
SolutionStep
attempt+step_no UNIQUE, stable step_id, step_type, raw_text/payload, normalized_repr, parse_status;
immutable после submit
AttemptEvent
append-only id, attempt, type, occurred_at, help_level/reveal/submit source, request_id; unique action key
Exposure
user+exercise_version UNIQUE, max_help_level, revealed_at, credited_positive_event nullable; lock до help и
finalization
AnalysisRecord
attempt+snapshot_digest+analyzer_version UNIQUE, structured result, references, policy versions
CompletionFact
immutable completion_id, attempt, skill, outcome, independent flag, completed_at, policy_version; UNIQUE
attempt+skill; время получения хранится отдельно
ProgressEvent
event_id UNIQUE, user/skill/type, occurred_at, source_attempt/revision/evidence_ref, versions, validated
payload; UNIQUE(attempt_id,skill_id,event_kind,evidence_ref)
UserSkillState
UNIQUE user+skill, mastery/confidence Decimal(5,2), status, evidence_count, last_updated, reducer_version
IdempotencyReceipt
user+endpoint+key UNIQUE, request digest, operation/response/status, expires_at; минимум 7 суток
DiagnosticSession
user, state, ordered skill itinerary, selected item, policy_version, completion; максимум 10 items
PracticeSession/Item
user, target_skill, origin_topic, state, counter/streak, selected version; один active, UNIQUE session+position
Conversation/Message
owner, scope topic/exercise_version, bounded messages, safe content, help action reference
AIRun
correlation/operation, provider/model, prompt/schema versions, status, latency, tokens/cost if known, redacted
error, fallback
Индексы: ProgressEvent(user,skill,occurred_at,event_id); CompletionFact(user,skill,completed_at,attempt_id);
Attempt(user,created_at,id); Attempt(state,operation_id); ExerciseVersion(status,mode,difficulty);
TopicSkill(content_page,role); AIRun(correlation_id,created_at); receipts(expires_at). Unique constraints
обеспечивают idempotency на уровне DB, а не только Python-проверкой. Не хранить полный expected
answer в public JSON, cache key, analytics или source maps. Секретная Validation может находиться в private
source пакете на сервере, но не в статических файлах. Исторический digest версий воспроизводит
проверку и защищает от замены checker «на месте». Каждая schema change имеет additive migration,
fresh PostgreSQL и upgrade проверки, rollback plan и review. Applied migration не переписывается.
Необратимые преобразования и destructive operations требуют отдельного human gate. Bootstrap
дважды даёт те же content identities, не очищает Attempts/Progress. Synthetic demo reset — отдельная
explicit command только для disposable environment.

---

## 7. Exercise, Attempt, помощь и eligibility
Режимы неизменны: SELF_CHECK (ученик сверяет себя, нет автоматического positive), FINAL_ANSWER
(один ответ), STEP_BY_STEP (упорядоченные типизированные шаги), STRUCTURED_SOLUTION (schema-
driven поля и steps). PublicExerciseDTO сохраняет R02 имена
id/code/topic/statement/interaction_mode/input_schema/step_schema/parser_profile/difficulty/reveal_policy/
con tract_version; v7 добавляет version, difficulty_level1–4, skill codes и допустимые help actions. difficulty
остаётся публичной band easy/medium/hard, соответствующей 1–2/3/4; исключает answer_key, checker,
hidden rules, reference solution. Сервер повторно валидирует всё, независимо от frontend. SolutionStep
сохраняет принятые R02 поля: step_no (положительный номер с 1), step_type, payload, raw_text,
normalized_repr, parse_status. Baseline step_type: MATH_EXPRESSION, EQUATION_STATE,
STRUCTURED_FIELDS, FINAL_STATEMENT. Client отправляет только step_no/step_type/payload/raw_text;
normalized_repr и parse_status устанавливает сервер. R02A добавляет revision/identity, не
переименовывая эти поля. Новые types требуют contract review; произвольный текст не получает
математической оценки без поддерживаемого validator. Reorder разрешён только в draft; после submit
порядок входит в digest. State machine: STARTED→SUBMITTED→COMPLETED для assessed;
STARTED→REVIEWED для SELF_CHECK; STARTED→ABANDONED. SUBMITTED immutable. COMPLETED имеет
CORRECT/WRONG/UNSUPPORTED/INDETERMINATE, а не четыре новых state. Сетевой сбой не означает
WRONG. После submit исправление — новый Attempt с previous_attempt_id. GET никогда не увеличивает
mastery. PUT draft требует expected_revision и целый валидный draft; успешный update повышает
revision. Конфликт 409 возвращает текущую revision и безопасный способ reload. Submit принимает
expected_revision и idempotency key, фиксирует snapshot; edit/submit race имеет одного победителя.
Expired exercise version не подменяется новым checker: открытая попытка использует frozen published
version, архивирование запрещает лишь новые попытки по policy. Помощь — POST hints/reveal с owner
checks. Подсказка/reveal сначала записывается транзакционно, затем возвращается текст. Lock
Exposure(user,version) сериализует help/submit/finalization. Idempotent retry возвращает ту же action/level,
не повышает уровень повторно. Уровни 0–3; уровень 3 не должен фактически содержать целое решение
одношаговой задачи. Full solution выдаётся только явным reveal. D-022: новая попытка не стирает
помощь на той же версии. Revealed версия навсегда не даёт CORRECT_FIRST_TRY этому пользователю;
предыдущая независимо завершённая до reveal попытка не отзывается задним числом. Hint сохраняет
helped eligibility между попытками. На user+exercise_version допускается максимум один зачтённый
positive event; повторное решение сохраняет CompletionFact/history, но не выращивает mastery. Другая
published version рассматривается отдельно, если это содержательное изменение; version bump ради
обхода eligibility запрещён. Определение independent для mastery window: CORRECT, без ранее выданных
hints/reveal на версии, без repeated positive credit, с validated supported input. Неподсказанный
DIAGNOSTIC_CORRECT также считается independent, как в R03. Вывод LLM не способен повысить
независимость. Нейтральные completions сохраняются даже при reveal/repeat/unsupported. SELF_CHECK
остаётся отдельной семантикой: просмотр решения не становится assessed success. Простыми словами:
Attempt — конкретная попытка с неизменяемым отправленным ответом. Idempotency означает, что
повтор из-за плохой сети не засчитывает одно действие дважды. Evidence — проверяемое основание, по
которому система вправе обновить знание.

---

## 8. Knowledge Graph и точный Progress
Skill — стабильный математический навык, а Topic — страница обучения. Knowledge Graph задаёт
prerequisite→dependent, не обратное направление. 10 codes: integer_number_line, negative_numbers,
sign_rules_add_sub, sign_rules_mul_div, distributive_property, expand_parentheses, combine_like_terms,
equation_balance, linear_one_step, linear_parentheses. Названия сверяются с R03 fixture; окончательные
machine codes всегда из fixture, без алиасов в DB.
13 рёбер: integer_number_line→negative_numbers; negative_numbers→sign_rules_add_sub;
negative_numbers→sign_rules_mul_div; sign_rules_add_sub→distributive_property;
sign_rules_mul_div→distributive_property; distributive_property→expand_parentheses;
sign_rules_add_sub→combine_like_terms; expand_parentheses→combine_like_terms;
combine_like_terms→equation_balance; equation_balance→linear_one_step;
linear_one_step→linear_parentheses; expand_parentheses→linear_parentheses;
combine_like_terms→linear_parentheses. Все веса 1.0; graph_version pilot-v1. Self-edges, duplicates, cycles
отклоняются целиком. basic_arithmetic — внешняя предпосылка, не одиннадцатый skill. Mastery отражает
накопленную оценку владения, Confidence — достаточность подтверждений; оба 0..100. Confidence не
является вероятностью истинности ответа LLM. Начало с нуля: 0/0. Самоотметка: один
SELF_REPORTED_KNOWN на skill даёт 60/15, не доказывает MASTERED. Повторная и postassessment
самоотметка отклоняется; «до assessment» определяется replay order, поэтому валидный backfill до
первого assessed event допустим. Режим onboarding выбирается явно: START_ZERO, SELF_REPORT,
DIAGNOSTIC; чтение тем не является evidence. Progress event
Δ mastery
Δ confidence
SELF_REPORTED_KNOWN
установить 60
установить 15
CORRECT_FIRST_TRY
+6
+5
CORRECT_AFTER_HINT
+3
+4
WRONG_ATTEMPT
2−
+3
MISCONCEPTION_DETECTED
5 × repeat factor−
+5
ANSWER_REVEALED
0
0
DIAGNOSTIC_CORRECT
+8
+8
DIAGNOSTIC_WRONG
6−
+8
Точные event names и reference behavior проверяются against specs/progress/BASELINE-v1.md/fixtures.
Коэффициент difficulty для assessed deltas mastery: уровни 1/2 — 0.8; 3 — 1.0; 4 — 1.2. Confidence не
масштабируется. Decimal, clamp [0,100], ROUND_HALF_UP до 2 знаков после каждого event. Не
использовать float; decay отсутствует. Missing/invalid difficulty — validation error, не default. Повтор одной
misconception на skill: 1, 1.25, затем 1.5. Самостоятельный correct сбрасывает repeat counters всех codes
этого skill; helped correct и иной wrong не сбрасывают. На evidence unit (user,skill,attempt,evidence_ref)
нельзя одновременно начислять WRONG и MISCONCEPTION за один дефект; диагностическая ошибка
даёт один DIAGNOSTIC_WRONG. Wrong final сам по себе не доказывает misconception. Pilot подтверждает
первую доказанную ошибку на skill; дополнительные независимые шаги требуют отдельного
проверенного evidence. Status: evidence_count=0 → NOT_STARTED. Иначе mastery≥80, confidence≥60 и ≥3
independent correct в последних 10 завершениях → MASTERED. Иначе mastery<50 и confidence≥30 →
WEAK. Остальное → LEARNING. Самоотметка даёт LEARNING. Topic mastery — importance-weighted average
mapped skills; coverage — доля assessed PRIMARY skills по accepted UI contract. Topic coverage считается по
его PRIMARY mapped skills, не по всем десяти; supplementary skills показываются отдельно. Нулевой
denominator — «нет оценочных навыков», не 0% знаний. Replay упорядочивает events по
(occurred_at,event_id,policy_version), UTC precision не более 6 дробных знаков; точность не усекать. Exact
duplicate event/source с тем же payload — no-op; иной payload под тем же ключом — conflict. Поздний
event вызывает пересчёт истории затронутого user+skill, не прибавляется поверх нынешнего состояния.
Replay result должен совпадать с online reducer по всем полям. D-021 добавляет CompletionFact stream
для каждого завершённого assessed attempt/skill. Neutral completions занимают место в последних 10,
могут снять MASTERED, но не меняют mastery/confidence/evidence_count/last_updated. Не создавать fake
WRONG/ANSWER_REVEALED лишь ради окна. Completion mirror принадлежит Progress; Assessment
отправляет immutable DTO. Окно completions сортируется по (completed_at,attempt_id), как R03;
объединённый replay сохраняет порядок events (occurred_at,event_id,policy_version), explicit dedupe и
связь streams; R03A задаёт fixtures, включая одинаковые timestamps и поздние facts. progress-v1
сохраняется для исторических events; новый reducer_version progress-v1.1 вводится additive с parity вне
нейтрального окна.
Простыми словами: граф показывает, что надо знать раньше. Прогресс — воспроизводимый расчёт по
журналу доказательств. Replay позволяет пересчитать результат; CompletionFact не даёт системе забыть
неудачные или подсмотренные завершения только потому, что у них нет числового штрафа.

---

## 9. Безопасная математическая проверка и Analyzer
Парсер принимает ограниченную грамматику чисел, одной переменной x, +  * /, скобок, равенства и −
согласованного implicit multiplication. Десятичные записи переводятся в точные rational; raw input
сохраняется отдельно. Нельзя выполнять eval/exec или передавать произвольную строку прямо в
sympify. После whitelist lexer и собственного AST разрешена нормализация SymPy в изолированном
процессе. Два эквивалентных rational answers считаются равными без float tolerance. Поддерживаемый
pilot: целые/рациональные выражения, знаки, распределительное свойство, подобные члены, линейные
ax+b=cx+d, включая no solution/all solutions. x² может лексически распознаться, но нелинейный смысл —
UNSUPPORTED. Variable denominator, функции, системы, произвольные доказательства, геометрия и OCR
вне scope. Parse statuses: OK, INVALID, UNSUPPORTED, NOT_REQUIRED. INVALID syntax не является
misconception; неподдерживаемая область не считается WRONG. Лимиты D-024: request ≤64 KiB, ≤40
steps, ≤512 chars на expression, ≤128 tokens, nesting≤16, numeric literal≤12 digits, абсолютная
степень≤10; ≤250 ms на expression и ≤2 s на пакет в отдельном процессе. Превышение возвращает
controlled unsupported/limit result без strong negative. Родитель останавливает процесс по deadline;
timeout не держит worker и DB transaction. Диапазоны и repeated operators тестируются на worst-case
input. Step validator рассматривает непрерывный проверенный prefix. First proven error — первый
неверный переход, для которого достаточно предыдущего корректного состояния и правила. После
unknown/unsupported gap нельзя обвинять следующий шаг как будто prefix доказан. Cascading
consequences одной ошибки не дают множество штрафов. FINAL_ANSWER может доказать final verdict, но
не локализует ошибочное правило без evidence. Taxonomy: SIGN_ERROR с конкретным sign rule;
DISTRIBUTIVE_PROPERTY; LIKE_TERMS; EQUATION_BALANCE; ARITHMETIC_ERROR только с подтверждённым
действием и mapped skill; OTHER — пояснение/abstain без strong misconception. Код и skill должны быть
согласованы с версией taxonomy и упражнением. Неподдерживаемый basic_arithmetic не подменяется
ближайшим pilot skill ради штрафа. AnalysisResult содержит schema_version, verdict, classification,
first_error_step_id nullable, misconception_code nullable, skill_codes, evidence_refs, confidence 0..1, source,
parser/validator/taxonomy/prompt/model versions, safe_feedback. Model response проходит
Pydantic/schema plus domain validation. confidence≥0.8 необходимо, но недостаточно для strong negative:
нужны известное правило и независимо проверенный evidence. LLM не изменяет математический
verdict поверх доказанного deterministic result. Fallback: deterministic safe feedback или INDETERMINATE с
объяснением ограничения. Invalid JSON/schema, unknown code/skill, low confidence, provider timeout,
injection — abstain; ноль strong negative. Retry максимум в пределах общего deadline; обычные tests
используют fake provider. UI не сообщает «ты не знаешь тему» на основании одного uncertain
результата. Простыми словами: Analyzer объясняет только ту ошибку, которую можно подтвердить.
Отказ от диагноза — корректный результат, когда информации мало.

---

## 10. Tutor, диагностика и адаптивная практика
Tutor Context Builder берёт public exercise, текущую помощь, ≤4000 chars релевантной теории, ≤10 skills,
≤5 последних подтверждённых ошибок, ≤6 сообщений. Общий budget ≤6000 estimated tokens, с reserve
под schema/output. Checker/answer/private solution до reveal не попадают в prompt. Контекст имеет
версии/digests и обрезает сначала историю, сохраняя policy и текущее действие.
До reveal модель может выбрать только schema-valid intent/hint_id/level/followup_id из reviewed hint bank.
Сервер проверяет принадлежность bank к version, допустимый уровень, owner и exposure; пишет help
event; только затем отдаёт заранее проверенный текст. Произвольная сгенерированная математика не
выводится. Даже «общий совет» может раскрыть одношаговый ответ, поэтому bank проверяется
редактором. После reveal разрешён bounded explanation по раскрытому solution, escaped output, без raw
HTML/scripts и с fallback. Product LLM: общий deadline 12 s, ≤2 model calls на action; retries не сбрасывают
deadline. Budget exhausted → safe fallback, никакого скрытого третьего вызова. Provider/model/pricing и
общий денежный лимит TBD до live smoke; model identifier и actual token usage фиксируются, стоимость
не выдумывается. Product AI действительно вызывается в отдельном live acceptance, хотя core и CI
работают offline. Диагностика: ≤10 заданий, по одному PRIMARY skill в топологическом порядке. Skip
нейтрален; помощь снижает независимость, reveal запрещает diagnostic correct credit. Выбор
опубликованного supported упражнения фиксируется до отправки клиенту. Завершение или повтор next
не создаёт новый item. Onboarding не блокируется навечно при unsupported/no candidate: сохраняется
безопасный результат и доступен START_ZERO с явным выбором. Adaptive selector: сначала слабые
prerequisites target до глубины 2; сортировка mastery ascending, depth descending, code ascending. Если
слабых нет, но есть confidence<30 — diagnostic route с depth/code tiebreak; иначе target. Difficulty при
достаточной confidence: mastery<40→1–2, <70→2–3, иначе 3–4; выбрать ближе к нижней границе. При
confidence<30 диагностический выбор начинает с 2, при отсутствии допустимого уровня 2 — с 1; это
отдельный low-confidence fallback, а не правило всегда выбирать 1. Выбирается published supported
mode; фиксируются reason/policy version/candidate IDs. Среди подходящих candidates предпочесть
PRIMARY target и наибольшую mapped importance; для глубокой диагностики STEP_BY_STEP, для быстрой
FINAL_ANSWER; затем difficulty ближе к нижней границе, code, version. Не использовать случайный
неповторяемый порядок без seed. Исключаются последние 10 exercise IDs и текущие session items. При
исчерпании обычного pool допускается repeat с reason REPEAT_POOL_EXHAUSTED и без повторного
positive. Диагностика исключает revealed versions. Если допустимого кандидата нет — NO_CANDIDATE с
доступным возвратом, без бесконечного цикла и без подмены unsupported задачей. PracticeSession:
один active на user; target и origin_topic immutable. Успех: три последовательных independent correct на
различных versions, либо mastery≥70/confidence≥60 после хотя бы одного session item. Лимит семь
items, включая skip; wrong/help/reveal/unsupported/skip сбрасывают streak. Exit reasons SUCCESS,
LIMIT_REACHED, NO_CANDIDATE, ABANDONED. Next/finish idempotent; refresh восстанавливает текущий
item. При архивном origin возврат на опубликованного parent/catalogue, без 404-тупика. Простыми
словами: Tutor помогает безопасно, не выдавая ответ незаметно. Adaptive Practice выбирает короткую
тренировку на нужную предпосылку и возвращает ученика к исходной теме.

---

## 11. HTTP API и frontend
Цель MS7-R02A — versioned OpenAPI/JSON schemas/fixtures. Следующий контракт полностью задаёт
поведение v7, но ещё не объявляется реализованным. Namespace /api/v1/, snake_case, trailing slash, JSON
UTF-8. Session auth и CSRF на всех mutations. Anonymous/foreign requests не раскрывают существование
чужого объекта. UUID новых ресурсов; pagination cursor с stable (created_at,id), default20/max100. GET не
создаёт attempts, session items или evidence. Surface
Endpoints и обязанности
Identity
GET auth/csrf/; POST auth/register/, auth/login/, auth/logout/; GET/PATCH users/me/; POST
onboarding/complete/
Content
GET grades/, topics/, topics/{slug}/, topics/{slug}/exercises/, exercises/{id}/; assessed DTO только с
допустимым доступом
Attempt
POST/GET attempts/; GET attempts/{id}/; PUT attempts/{id}/draft/; POST submit/, hints/, reveal/, abandon/ под
attempt
Diagnostic
POST diagnostics/sessions/; GET session; POST next/, finish/; state/policy/item explicit
Surface
Endpoints и обязанности
Progress
GET progress/skills/, progress/topics/, progress/events/; POST progress/self-reports/ только onboarding policy
Practice
POST practice/sessions/; GET session; POST next/, finish/; reason/return route explicit
Tutor
POST ai/conversations/; GET/POST ai/conversations/{id}/messages/; context binding проверяет сервер
Operations
GET health/live/, health/ready/; не возвращать credentials, SQL, provider keys
Error envelope: {error:{code,message,field_errors,retryable,request_id}}; success содержит data и
meta(request_id,version/pagination). Idempotency-Key для create/submit/help/reveal/next/finish/self-report;
request_digest включает owner, route, body, expected revision. Повтор с тем же digest получает прежний
operation/result; иной digest под ключом —409. Receipts хранятся ≥7 дней, permanent source uniqueness в
evidence живёт по retention evidence и не исчезает с receipt. 400 invalid schema/limit; 401 no auth; 403
CSRF/forbidden role; 404 foreign/missing resource; 409 revision/idempotency/version/state conflict; 429 с
Retry-After; 503 только если действие не может безопасно завершиться. Supported business result
UNSUPPORTED —200, provider fallback —200 с DEGRADED. 202 содержит operation_id и повторяемый status
route через attempt/session; не обещает существующую background queue. Poll 1/2/4 s, затем manual retry,
без нового submit key. Long processing не держит SQL lock. UI наследует I01 SC-01–08 и state matrix:
empty/loading/error/ready/pending/degraded/conflict/unsupported/unauthorized. Frontend показывает
только server verdict/state/help. Ctrl/keyboard, focus restoration, live regions и labels — реализуемая
приёмка, не доказанная wireframe. Mobile widths360/768/1440; Chrome/Edge/Firefox versions фиксируются
в evidence. Graph обязательно имеет доступный list view, цвет не единственный носитель статуса.
Exercise renderer dispatch по mode/schema, не по угадыванию текста. Draft autosave debounce с revision;
stale response не затирает новый ввод. Submit lock UI снижает дубли, но безопасность обеспечивает
сервер. Help/reveal отображается после server acceptance; timeout→GET canonical state. Structured
unknown schema показывает controlled unsupported. XSS payload в raw response/feedback всегда escaped.
Public build не содержит hidden checker/solution, в том числе в HTML <details>, JSON, JS bundle, cache и
network. Legacy SELF_CHECK <details> в существующем content остаётся compatibility baseline, не
оценивает mastery. Новые assessed exercises не наследуют эту утечку. Перенос всего historical content на
новые режимы не входит в MVP. Простыми словами: браузер рисует интерфейс, сервер решает, что
действительно произошло. Повторные клики и обновление страницы не должны изменять историю
дважды.

---

## 12. Engineering Harness: результат и adapter
Harness — локальная инженерная программа вокруг coding model. Он собирает ограниченный контекст,
принимает запросы инструментов, проверяет права, исполняет действия в sandbox, запускает проверки
и сохраняет evidence. Он не входит в product runtime и не запускается из student endpoint. Этапы:
accepted R01/R02/R03 + MS6-R04/V01/I01 bootstrap; Context/Registry R05; Policy/hooks/trace R06A; OS
sandbox R06B; live coding adapter R04A; bounded skills/subagents R07; реальные owner runs V07/I08/R08;
regression/eval и G1. После G1 обычные significant increments трёх участников проходят собственный
Harness. До G1 разрешён текущий coding-agent bootstrap с честной trace, без заявления «MathStart
Harness уже всё контролировал». R04 ModelAdapter уже задаёт identity/capabilities, start,
continue_with_tool_result, continue_after_message, cancel и versioned events. FakeAdapter используется для
deterministic tests. MS7-R04A добавляет реальный provider, не меняя contract без review. Event
TOOL_REQUEST не является разрешением выполнить действие; executor существует только в Harness.
Вариант
Решение для v7
Direct model API с function/tool calls
Предпочтительный первый adapter: модель возвращает request, приложение решает и исполняет.
Проще доказать полный interception.
Codex App Server/SDK
Кандидат после capability spike: проверить все actions, approvals, terminal/file/browser/MCP,
cancel/deadline и отсутствие bypass. Название SDK не доказывает enforcement.
CLI wrapper с непрозрачными внутренними tools
Только bootstrap/advisory. Наблюдение stdout после действия не равно pre-authorize. G1 таким запуском
не закрывается.
Другой provider
Допустим при том же protocol/capability/eval; изменение model не даёт дополнительных прав.
Официальная документация function calling подтверждает, что tool execution выполняет приложение:
https://developers.openai.com/api/docs/guides/function-calling . Возможности App Server проверяются по
https://learn.chatgpt.com/docs/app-server на выбранной версии. Это технические источники adapter
выбора, не требования курса. Конкретный provider/model/цена TBD до human budget gate, без live
credentials в repo. Adapter capability matrix: can_request_tools, intercept_all_actions, supports_messages,
supports_cancel, usage_reporting, vision, structured_output. Для enforcement нужны intercept_all_actions и
sandbox proof. Нет обязательного vision/MCP, если они не нужны approved task. Cancel best effort в
adapter дополняется hard subprocess/network deadline исполнителя. Unknown event/protocol/schema →
safe failed run. Простыми словами: adapter переводит сообщения модели в язык Harness. Возможность
наблюдать агента ещё не означает возможность запретить ему действие заранее.

---

## 13. Context Layer и Typed Tool Registry
Context складывается из pinned policy/AGENTS/contracts, task/acceptance/manifest, выбранного versioned
skill, relevant source ranges, результатов tools и summary. Manifest содержит path, revision/SHA, digest,
range, role, bytes/tokens estimate, source trust. Обязательные contracts либо помещаются целиком/с
approved excerpt digest, либо run останавливается до model call. Случайное усечение rule запрещено.
Default run limits: context24k estimated tokens, 30 model turns, 30 minutes wall, суммарно 100k tokens
вместе с children, tool output32 KiB, child depth1/max2children. 80% budget→checkpoint/compaction,
90%→запрет новых child,100%→stop. Если provider tokenizer недоступен, conservatively estimate и
отмечать estimated, а не точные tokens. Output reserve вычитается до call. Compaction сохраняет
task/acceptance, policy, mandatory contract versions, unresolved failures/denials, pending tool pairs, decisions
и artifacts. Summary не является новым system instruction и не может повысить права. Нельзя разрывать
request/result пару. Full raw tool result может храниться redacted artifact с digest и range_read; summary
содержит ссылку и truncation marker. Каждый compact event фиксирует before/after
budget/digests/retained constraints. Overflow — controlled stop до опасного вызова. Registry spec каждого
tool: name/version/input schema/output schema, side_effects, allowed roots/hosts, timeout, max output,
authorization class, audit metadata, executor identity. Unknown tool/arg/property →deny. Минимум:
list(path,depth); read(path); range_read(path,start,end); search(pattern,roots,limit);
patch(expected_digest,changes); git_status; git_diff; run_check(check_id);
local_browser(approved_origin,action); optional read_image(artifact_id). Read outputs содержат source
digest/range/truncated и data, не скрытый success при частичном чтении. Patch требует expected digest и
atomic per-file write; конфликт возвращает stale input, не перезаписывает новые изменения. run_check
выбирает заранее reviewed command vector из registry, не shell string модели. Произвольный shell не
базовый tool. Git mutation/push/deploy не разрешены model по умолчанию. Browser restricted local test
origin, disposable synthetic session; внешние network hosts разрешаются отдельно. Изображения —
optional capability: применять для wireframe/screenshot comparison с artifact digest и DOM assertions.
Изображение не заменяет текстовый verdict/test. При отсутствии vision run честно сообщает capability
mismatch; frontend verification может выполняться DOM+human visual review.
Простыми словами: Context Layer выдаёт агенту нужные страницы, а Registry — список конкретных
разрешённых действий. Ни один из них не должен превращаться в неограниченный доступ ко всему
компьютеру.

---

## 14. Policy, hooks, sandbox, trace, skills и subagents
Policy fail-closed: deny по умолчанию; canonical paths после resolve, symlink/junction escape запрещён;
roots входят в TaskManifest. Protected paths .git, secrets, external home, production data закрыты. Network
allowlist минимален. Approval, если требуется, связан с run/action/args digest, expires_at и scope;
неизвестное/истёкшее approval не действует. Инструкция из untrusted tool result не меняет policy. Hooks:
run_start, context_built, before_model, before_tool, after_tool, before_verification, after_verification,
before_publication, run_end. Security before_tool обязателен; его ошибка запрещает действие.
Наблюдательный hook может degraded только если это заранее разрешено policy; trace failure для
evidence-relevant action останавливает run до дальнейших writes. Hooks не выполняют произвольный
текст из repo как privileged код. Sandbox physically ограничивает writes checkout artifact roots, network,
процессное время и child tree. Предпочтителен отдельный Linux container/VM с read-only source base,
writable scoped worktree, unprivileged UID и без host socket/credentials. Windows native mode должен
иметь доказанные ACL/process tree ограничения; до таких tests он advisory, не полноценный
enforcement. Timeout убивает процессное дерево; запрещены escape через junction, symlink, path case,
traversal, inherited handles и environment. G1 включает реальные denial attempts, а не только mocked
policy return. Trace: append-only JSONL sequence с
run_id,parent_run_id,task_id,time,event_type,tool/schema/model versions,input/output
digests,decision/reason,exit_code,latency,budget,artifact refs. Не писать hidden chain-ofthought, private
prompts с credentials, raw student PII, env dump. Human report описывает наблюдаемые actions, failures,
corrections, tests, review. Hash chain и manifest digest позволяют обнаруживать изменение evidence; это
не криптографическое доказательство честности оператора. Resume проверяет checkout/contracts/policy
digest, последний complete tool pair и remaining budgets; при drift требует new run/human review, не
повторяет неоднозначный side effect автоматически. Harness skills — versioned workflow instructions со
входами, check IDs и выходными artifacts. Они не дают прав. Backend skill знает migrations/PG/ownership;
frontend skill — fixture→runtime contract/browser/a11y; reviewer skill read-only. Skill validator проверяет
references и limits. Термин Harness skill не равен математическому Skill. Subagents: независимый
минимальный context, subset parent permissions, отдельный trace, общий budget ledger, depth1/max2;
один writer в конкретной области. Reviewer read-only; ребёнок не approve/merge и не запускает детей.
Handoff schema: findings(severity,file/ref,evidence), changes/artifacts,digests,checks,status,remaining risks.
Parent проверяет outputs и принимает ответственность; child «всё хорошо» не является evidence. Human
review остаётся независимым от агента. Простыми словами: Policy решает, можно ли действие; Hook
запускает проверку в нужный момент; Sandbox физически ограничивает действие; Trace записывает
результат. Subagent — помощник с меньшими правами, не второй администратор.

---

## 15. Verification, eval и наблюдаемость
Базовая команда — python scripts/verify_repo.py в configured environment. Existing 8 checks не
ослабляются. Новые tests включаются в canonical verification/CI отдельными reviewed changes;
Ruff/mypy/pytest/Playwright не называются настроенными до фактического добавления. Для schemas
обязательны fresh/upgrade PostgreSQL tests; SQLite skips не принимаются как locking proof. Content
bootstrap twice и source identity checks сохраняются. Каждый request получает correlation_id; связаны
Attempt/operation/Analysis/ProgressEvent/AIRun и policy versions. Metrics:
outcome/latency/fallback/error/abstention, DB query counts, dedupe conflicts, replay queue/operation age,
budget use. Наблюдаемость не хранит secret answer в общедоступных logs.
Health/live не зависит от модели; ready проверяет необходимую БД/config, provider outage не скрывается,
core fallback работает. Golden Analyzer set ≥50: 12 correct,16 доказанных ошибок (по 4 основных
taxonomy),10 ambiguous,6 wrong-final без локализации,6 structured; минимум 20 holdout, не использовать
их для prompt tuning. Deterministic accuracy≥95% на supported/applicable subset, LLM taxonomy≥85% на
applicable cases; abstention не засчитывается как верный ответ. Отдельно показывать coverage, false
positive, denominator и unknowns. False strong negative на invalid/unsupported/ambiguous safety subset =0.
Числа — release criterion пилота, не заявление педагогической эффективности. Tutor eval ≥20 cases:
prompt injection, answer request, hint levels, single-step leakage, timeout/malformed/lowconfidence, after-
reveal explanation. Harness eval ≥12 cases: unknown tool, path escape, network deny, protected writes,
malicious file instruction, child escalation, overflow/compaction, resume drift, deadline during tool/publication,
failing checks, forged READY, interrupted run. Реальные регрессии R04 остаются в suite, synthetic eval
отдельно помечается. No-live normal CI: fake Product provider и FakeAdapter; release smoke отдельно с
budget и версией настоящей модели. Для G1 нужны три real owner runs, для Product AI — live
Analyzer/Tutor acceptance с fallback и redacted AIRun. Запись успешного API ping не равна работе coding-
model loop.

---

## 16. Security, privacy и эксплуатационные числа
Auth — независимый совместимый verifier encoded Django hashes, PostgreSQL opaque sessions, username/password; email optional до утверждения recovery. Plaintext passwords не
хранятся; login error одинаков для missing/wrong account. Без verified recovery channel самостоятельный
password reset не обещается. CSRF/session rotation, secure cookies, TLS, DEBUG=False, allowed hosts, least
privilege staff, owner-scoped queries. Другой owner получает 404. Rate limiting работает совместно между
workers через PostgreSQL counters/locks, не local-memory only. Default rates: login10/5min/IP;
submit30/min/user; reveal10/min/user; AI5/min/user и 50/day/user плюс global money cap. 429 Retry-After;
границы window/idempotent retries проверяются concurrency tests. Денежный лимит и provider approval
TBD до live, секреты только environment/secret store; логи маскируются до записи. Pilot использует
synthetic demo identities. AIRun и engineering trace retention90days; attempts/messages до защиты+30days;
backups30days. Реальные несовершеннолетние пользователи требуют отдельного
privacy/consent/deletion review и изменения retention policy до сбора данных; юридическое соответствие
не заявляется этим документом. Delete workflow учитывает replay integrity: персональные ссылки
удаляются/анонимизируются по утверждённой политике, не произвольным SQL. Performance: p95
обычных API<500ms, AI<15s. Фиксировать CPU/RAM, app/DB versions, seed size, network region. После
warmup ≥200 ordinary requests при 10 concurrent users; ≥30 AI requests при 2 concurrent в согласованном
бюджете. Раздельные cohorts catalogue,submit,progress,AI; p50/p95/max/error rate. p95=ceil(0.95*n)-й
отсортированный sample. Failures/timeouts не исключаются; upstreamsuccess/fallback отдельными
рядами. Это demo profile, не интернет-SLA. Недостижение — finding с исключением human gate, не
удаление неудобных samples. Deployment: public HTTPS URL, Python3.12+/FastAPI/Pydantic/SQLAlchemy2/Alembic/PostgreSQL16, versioned locks, отдельный migration release step, static/media separation и ASGI Uvicorn. React/TypeScript/Vite/React Router генерирует весь public HTML по manifest; Node нужен для build/publish, постоянный Node SSR server не требуется. Production process manager/config утверждаются V14; dev server не является production evidence. Host/domain/region/secrets/backups
owner TBD до G3; перед G4 публичный доступ проверяется с внешнего браузера. Pydantic включён в target HTTP runtime; SymPy добавляется в будущей задаче математической проверки с compatible pins. Django/DRF остаются в отдельно изолированных исторических comparator окружениях и не требуются normal target startup/API/auth/publisher/migrations/verification. Backup: daily encrypted DB+needed
media/config references, RPO≤24h/RTO≤2h, retention30days. Restore drill в disposable environment
измеряет фактическую длительность, проверяет integrity/progress replay/content, не только exit0
pg_restore. Upgrade drill с текущего release; rollback app совместим с additive schema, breaking migration
имеет отдельный план. Never rewrite applied migrations. Public operation не зависит от Harness или каких-
либо внешних context/memory tools.
Operational Defaults Registry Все числа в технических разделах остаются действующими. Классификация
ниже уточняет способ изменения, не ослабляет acceptance. A HARD INVARIANT — правило versioned
contract/security model; без ADR/contract change менять нельзя. B ACCEPTANCE REQUIREMENT —
проверяемое условие приёмки; изменение требует явного human решения с новым evidence. C
CONFIGURABLE DEFAULT — начальное значение утверждаемой конфигурации; можно менять без новой
версии всего ТЗ после указанного review и тестов. При необходимости менять security/domain semantics
нужен ADR даже для C. Значение C после выбора становится принудительным лимитом конкретного
run/request; модель не может повысить его сама. Реестр представлен двумя связанными таблицами по
ID: все восемь полей сохранены, чтобы не сжимать текст в восемь узких колонок. Where configured для
будущих подсистем — целевое место хранения, а не заявление о существующем файле. Effective
config/version фиксируется в evidence; G0 не устанавливает credentials и не разрешает live расходы.
Исторические counts тестов/страниц, source timestamps и commit IDs — факты, а не operational defaults.
Версии schemas, cardinality, точные формулы и enums остаются частью contract; ссылки на главы и
номера задач не являются настраиваемыми параметрами. ID / Parameter
Default или требование
Why
OD-01 / Progress и Knowledge §§6/8
Все event deltas, Decimal(5,2), 0..100, ROUND_HALF_UP, difficulty/repeat factors, status thresholds, last10 и
replay precision/order без изменений
Воспроизводимость принятого R03
OD-02 / Exercise и eligibility §§6/7/11
Четыре modes, step_no с 1, difficulty1–4 и bands, hints0–3, один positive/user/version, immutable revisions,
API status semantics
Совместимость и честность evidence
OD-03 / Пилот §3/8
3 темы;10skills/13edges, weights1.0;40assessed+3self-check; ≥4PRIMARY/skill; ≥12step/≥12final/≥2schemas;
≥2difficulty/skill
Проверяемое покрытие продукта
OD-04 / Парсер размер §9
64KiB request;40steps;512chars/expression;128tokens; nesting16; literal12digits; abs power10
Ограничить сложность недоверенного ввода
OD-05 / Парсер deadline §9
250ms/expression;2s/batch
Освобождать worker при тяжёлом вводе
OD-06 / Strong negative §9
confidence≥0.8 и отдельно доказанное known evidence
Не путать уверенность модели с математической истиной
OD-07 / Tutor context §10
4000chars theory;10skills;5confirmed errors;6messages;6000estimated tokens
Минимизировать контекст и стоимость
OD-08 / Product calls §10
12s общий deadline;≤2calls/action, retries внутри него
Ограничить ожидание и обеспечить fallback
OD-09 / Diagnostic/Adaptive/Practice §10
Diagnostic≤10; depth2; confidence30; mastery bands40/70; последние 10 excluded; streak3 или
mastery70/confidence60 после 1item; max7; oneactive
Сохранить воспроизводимую учебную семантику
OD-10 / API pagination/poll §11
default20/max100; poll1/2/4s затем manual retry
Ограничить ответы и запросы без duplicate submit
OD-11 / Idempotency receipt §§6/11
Минимум 7 суток; evidence source uniqueness не истекает вместе с receipt
Безопасное восстановление операции
OD-12 / Harness run budgets §13
context24k;30turns;30min wall;100k tokens incl children;output32KiB
Предсказуемое ограничение run
OD-13 / Budget thresholds §13
80% checkpoint/compaction;90% запрет нового child;100% stop
Оставить место для завершения и не превысить лимит
OD-14 / Subagents §§13/14
depth1/max2children; один writer; reviewer read-only; subset rights
Сдержать расширение прав и конфликт записи
OD-15 / Analyzer eval §15
≥50:12correct/16errors/10ambiguous/6wrongfinal/6structured;≥20holdout;≥95%deterministic/
≥85%taxonomy;false strong=0 safety subset
Измерить качество на объявленных denominators
OD-16 / Tutor/Harness eval §15
≥20Tutor;≥12Harness;3real owner runs; live Product + fallback; обычный CI offline
Доказать обе AIинтеграции и сохранить воспроизводимость CI
ID / Parameter
Default или требование
Why
OD-17 / Rates §16
login10/5min/IP;submit30/min/user;reveal10/min/user;AI5/min и 50/day/user;global money cap TBD до live
Защитить сервис и расходы
OD-18 / Retention §16
AIRun/trace90days;attempts/messages до защиты+30days;backups30days
Ограничить хранение и сохранить evidence для приёмки
OD-19 / Performance §16
p95 API<500ms/AI<15s;≥200ordinary при 10concurrent;≥30AI при 2concurrent;ceil(0.95*n)
Воспроизводимая приёмка demo profile
OD-20 / Backup/restore §16
daily encrypted;RPO≤24h/RTO≤2h;retention30days поOD-18
Проверяемое восстановление данных
OD-21 / Browser/public runtime §§11/16
360/768/1440;Chrome/Edge/Firefox;Python3.12+/FastAPI/React/PostgreSQL16, exact locks
Совместимость и подтверждённая release среда
OD-22 / Security, schemas и versions §§4–16
Fail-closed;server-only secrets;Only Progress writes;typed ordered steps;versioned
DTO/registry;atomic/idempotent writes
Сохранить границы доверия
Порядок настройки и принятия изменений по тем же ID: ID
Where configured
Who may change
Gate/ADR required
Hard limit or default
OD-01
Versioned progress/knowledge contracts и fixtures
Руслан; независимый Владимир
ADR + versioned contract, parity/replay; G2
A HARD INVARIANT
OD-02
R02 + R02A schemas/services
Руслан + Владимир; review Ильи для UX
Contract addendum/ADR, regression; до клиентов/G2
A HARD INVARIANT
OD-03
Versioned pilot fixtures и bank import
Руслан + Владимир + Илья
Изменение acceptance на human gate, graph contract при изменении codes/edges; G2/G3
B ACCEPTANCE REQUIREMENT
OD-04
Versioned parser profile и server schema limits в R09/R02A
Руслан; Владимир approves
Approved config + worst-case tests; schema/security widening требует contract/ADR; G2
C CONFIGURABLE DEFAULT; effective caps enforced
OD-05
Isolated executor config
Руслан; Владимир approves
Security review + timeout tests; G2
C CONFIGURABLE DEFAULT; finite process deadline обязателен
OD-06
Versioned Analyzer policy
Руслан + Владимир
ADR/contract + golden safety eval; G2/G4
B ACCEPTANCE REQUIREMENT; evidence validation A
OD-07
Versioned Context Builder config в V13
Руслан; Владимир approves
Approved config + leak/fallback eval; G3
C CONFIGURABLE DEFAULT
OD-08
Provider policy/AIRun config в V11
Владимир; Руслан approves
Approved config + safety/performance checks; G3/G4; bypass требует ADR
C CONFIGURABLE DEFAULT; превышать effective cap нельзя
OD-09
Versioned R11 policy и V12 fixtures
Руслан + Владимир, UX review Ильи
Contract/ADR и replay/session fixtures; G3
A HARD INVARIANT для принятой policy version
OD-10
API config и frontend retry config
Владимир + Илья; Руслан approves
Approved config + API/browser tests; изменение public schema требует R02A addendum
C CONFIGURABLE DEFAULT
OD-11
Receipt retention config/constraint
Владимир; Руслан approves
Contract review для снижения минимума; G2
B ACCEPTANCE REQUIREMENT minimum; uniqueness A
OD-12
Versioned Harness run/registry config
Руслан; Владимир approves
Approved config + overflow/timeout/compaction tests; G1
C CONFIGURABLE DEFAULT
OD-13
Harness budget policy config
Руслан; Владимир approves
Approved config; stop на effective cap и fail-closed не смягчаются без ADR; G1
C для 80/90; A для запрета превышения cap
OD-14
Versioned Policy/Sandbox/skill schema
Руслан; Владимир и Илья review
Изменение hard bounds/permission model требует security ADR и escape tests; G1
A HARD INVARIANT
OD-15
Versioned golden set/eval acceptance
Руслан; Владимир и Илья approve
Изменение acceptance — отдельное human решение с обоснованием; G4
B ACCEPTANCE REQUIREMENT
OD-16
Eval sets и gate evidence ledger
Руслан + Владимир + Илья
G1/G3/G4; снижение acceptance не config tweak
B ACCEPTANCE REQUIREMENT
ID
Where configured
Who may change
Gate/ADR required
Hard limit or default
OD-17
Shared PostgreSQL limiter/provider config
Владимир; Руслан approves; budget owner до live
Approved config + multiworker tests; G3/G4; 429/Retry-After contract сохраняется
C CONFIGURABLE DEFAULT
OD-18
Versioned retention/runbook config
Владимир; Руслан approves privacy policy
Privacy review, replay/backup safety; новые реальные minors требуют отдельного решения
C CONFIGURABLE DEFAULT; не разрешение удалить evidence
OD-19
Versioned load-test scenarios/acceptance
Владимир; Руслан approves, Илья browser witness
G4 human exception/acceptance change; samples не отбрасываются
B ACCEPTANCE REQUIREMENT
OD-20
Backup schedule/restore runbook в V16
Владимир; Руслан approves
RPO/RTO change через deployment review/G4, не молчаливый config change
B ACCEPTANCE REQUIREMENT дляRPO/RTO/daily
OD-21
CI/environment lock/browser matrix
Владимир + Илья; Руслан approves
Dependency/platform change по ADR/AGENTS; G3/G4
B ACCEPTANCE REQUIREMENT
OD-22
Accepted contracts + domain services + Policy
Domain owner и независимый reviewer
ADR/contract/security gate при изменении; G0–G4
A HARD INVARIANT

---

## 17. Unified Task Execution Rules и Global Gates
Unified DoD Эти правила нормативны для всех будущих карточек; в карточке указываются только
дополнения. Owner выполняет работу, Reviewer проверяет её независимо, Task Approver принимает
конкретный результат. Reviewer и Task Approver могут быть одним человеком, но не Owner. Milestone
Gate — контрольная точка проекта, а не человек и не замена task acceptance. Для frontend/API-sensitive
задач Руслан принимает UX и общую интеграцию, Владимир подтверждает API/backend совместимость;
Илья выполняет browser acceptance, не одобряя собственную работу. До изменения кода Owner читает
spec → AGENTS/ARCHITECTURE → accepted ADR/contracts → task inputs, проверяет scoped checkout,
состояние файлов и digests. HARD и CONTRACT зависимости должны быть приняты до основной
реализации; отдельное знакомство с документами и предварительный fixture sketch не закрывают
задачу. HANDOFF и INTEGRATION могут поступать во время разработки, но обязательно приняты до task
acceptance. Неизвестные контрактные решения выносятся человеку; неподтверждённый upstream не
подменяется догадкой. В рамках задачи обязательны весь Detailed Scope, позитивный маршрут,
negative/failure acceptance и применимые проверки. Scope карточки не сокращается из-за компактного
оформления. Сбой имеет диагностируемый status, не объявляет success. Сохраняются raw input, versions,
validated evidence, server-only secrets и доменное владение. Запрещены новые режимы/формулы,
массовая конвертация каталога, unrelated refactor и неявный deployment вне отдельного принятого
изменения. Canonical verification: python scripts/verify_repo.py в настроенном окружении, плюс task-
specific проверки. Final SHA, к которому относятся acceptance и merge, должен иметь успешный
применимый CI. Tests не ослабляются и не добавляются ради числа. Для schema changes нужны additive
Alembic migrations, metadata consistency и PostgreSQL fresh/upgrade/concurrency evidence по применимости. SQLite
skips и environment failures фиксируются честно. Documentation-only N/A runtime checks обосновываются;
fixtureonly результат не закрывает runtime integration. Новые инструменты проверки сначала
добавляются в reviewed конфигурацию, а не объявляются установленными. Evidence E(ID): trace
docs/agent-traces/<ID>.md, run_id/surface, inputs/versions/digests, команды и exit results, final SHA, CI/PR
links, фактические browser/model/runtime versions, findings и решения Reviewer/Task Approver. Browser
tasks добавляют DOM/network/console evidence и screenshots без PII. Live задачи — redacted provider/run
evidence; обычный CI использует fake/offline. До G1 разрешён обозначенный bootstrap-agent surface;
после G1 significant engineering increments проходят принятый Harness. Ключи, скрытые ответы и private
chain-of-thought не входят в trace. Отсутствующие ссылки явно pending, не выдумываются. DoD: приняты
все deliverables, доказаны positive/negative cases, закрыты blocking findings, приняты
HANDOFF/INTEGRATION зависимости, записано независимое approval, проверен final SHA и выполнен
merge по действующему workflow. Gate не закрывается автоматически из-за task merge. Исторические
FROZEN результаты не проходят это повторно. Recovery: scoped revert сохраняет контент и evidence;
schema rollback учитывает additive compatibility, applied migrations не переписываются. Повтор
безопасной операции использует idempotency; drift требует нового manifest/run. Evidence не удаляется
для создания видимости успеха. Task-specific exception/rollback оформляется до действия в exec plan.
Breaking migrations, provider/security/deployment changes имеют отдельный human gate по AGENTS. Агент
не заменяет это одобрение.
Кто принимает Global Gates Gate Owner собирает пакет и фиксирует решение, но не подписывает
результат за других. В ledger docs/acceptance/<gate>-<date>.md указываются digest/SHA нормативного
документа и release, каждый approver, дата, ссылки на evidence и findings. При отказе хотя бы одного
обязательного approver Gate остаётся pending. Подписи команды подтверждают соответствие проекта, а
не автоматическое согласие преподавателя. Gate / Owner
Required Approvers
Required Evidence
Blocking findings
Что разрешается после
G0 / Руслан — ACCEPTED 30.09.2026 · G0-2026-09-30.md
Руслан, Владимир, Илья — три отдельные записи
PreG0 v7 digest, preserved baseline, task/dependency registry, два target roadmap, D-021–028 как принятые
направления с отдельными contract closeouts
Конфликт frozen ADR; неясный scope/owner; отсутствующее approval v7
v7 становится нормативным baseline дальнейшей разработки; R02A/R03A разрешены как отдельные
задачи. Их реализация/fixtures ещё не утверждены.
G1 / Руслан
Владимир и Илья принимают Harness; Руслан отдельно принимает их V07/I08 profiles/runs
R05/R06A/R06B/R04A/R07/R08, V07/I08; три real owner runs, физические deny tests, trace/receipt, child limits,
green CI
Fake-only loop; opaque tool bypass; unproven sandbox; missing run/approval
Регулярные significant increments команды через собственный Harness.
G2 / Владимир
Руслан и Владимир с cross-review, Илья как независимый browser witness
V03–V06/V08–V10, R09/R10/R13; PostgreSQL atomic finalize/eligibility/CompletionFact/re play, AT-02–08
Direct Progress writes, race/duplicate, online/replay mismatch, лишь SQLite/fixtures
Можно утверждать, что показанный UI progress основан на проверенном persisted evidence.
G3 / Илья
Руслан, Владимир, Илья; каждый подтверждает соседние границы
V02/V11–V14, R11/R12, I02–I14; четыре режима, auth, Tutor/diagnostics/practice, SC routes на staging, live
Product + fallback
Mocks на основных путях, leaks, непроверенный provider/host, нерабочий возврат
Полная staging acceptance завершена; release hardening и публичная приёмка.
G4 / Руслан
Руслан, Владимир, Илья — общий RC review
R14/R15/R17, V15–V17, I15–I17; public HTTPS, AT-01–16, eval/performance/security/restore, report draft, один
release SHA
Critical defects, unknown ownership/budget, failed restore, недоступный public URL, missing approval
RC принят; можно согласовать защиту и завершать freeze/handover.
G5 / Руслан
Руслан, Владимир, Илья — каждый проверяет передаваемые артефакты
R18/V18/I18, R16/I16/V16, final PDF report, runbooks/evidence index, release access, согласованная дата
защиты
Pending Gate, broken links/assets, непереданные доступы, несогласованная защита
Проект передан и готов к защите; Early Defense проходит те же проверки.
G0 не означает реализацию проекта, завершение future tasks или одобрение преподавателем каждого
D-решения. Три отдельные подписи принимают v7 и порядок реализации; новые API/CompletionFact
artifacts принимаются по R02A/R03A до зависимых клиентов. Это устраняет цикл «G0 требует
выполненную первую post-G0 задачу». R02A/R03A относятся к contract closeout до G1 и далее являются
blockers своих потребителей. Принятые R01/R02/R03 не переоткрываются. Provider/host/budget TBD
допустимы на G0 только с ответственными и сроками до соответствующего live/deployment gate.

### Переходный workflow MS7-MIG

Программа миграции существующего сайта завершена: QA, техническое review, человеческая приёмка и merge PR54 состоялись; последующая консолидация PR55 завершена. [Maintenance](../maintenance.md) сохраняет точные SHA и evidence. Прежняя ветка и персональные очереди не являются действующими заданиями. Новую работу определяет только отдельное поручение пользователя. Product G1–G5, утверждение всей продуктовой редакции, public deployment и production writer switch остаются отдельными решениями; принятие миграции и адаптации платформы v7.2 их не закрывает.


---

## 18. Реальные ошибки разработки и исправления R04
Источник всех четырёх кейсов — PR #10 reviews и main tests; это наблюдаемая история разработки с
coding-agent workflow. Публичное review не позволяет надёжно приписать каждую строку конкретной
модели: hidden reasoning и «мысли агента» не реконструируются.
1. Review Владимира 26.09 выявил manifest digest, protocol version,
deadline, branch-sensitive smoke,
отсутствие Harness suite в canonical CI и неправильное продолжение MESSAGE. Commit13945bd исправил
основную часть. Regression: adapter/message/protocol/manifest и runner boundary suites. Урок:
заявленного adapter protocol недостаточно без executable negative cases.
2. После первого исправления deadline мог истечь во время result
write. 27.09 16:04 reviewer сохранил
blocker. Commit85dd0ff добавил staged write и post-write checks; 61 tests и CI success не доказывали
отсутствие всех publication races. Следующее review21:20 нашло истечение внутри final replace.
Regression test_expiry_during_result_persistence_cannot_publish_ready и
test_expiry_during_final_result_replace_cannot_return_ready. Урок: проверка до операции не доказывает её
завершения до deadline.
3. Commits5863bd/eabea37 усилили commit/receipt protocol. Regression
в
tests/harness/test_ready_publication.py: crash after canonical replace, corrupt/missing receipt, digest
mismatch, late final replace. В истории есть failed runs eabea37/66b071; их нельзя называть green. Урок:
supported status reader обязан проверять commit evidence, а не один state field.
4. Review27.09 22:25 выявил ambiguous receipt replacement: запись
могла фактически пройти, но вернуть
OSError; cleanup и diagnostic overwrite тоже могли упасть. Runner выдавал exit2, status —exit0. Final
f401dc6 согласовал чтение canonical publication. Regression
test_ambiguous_receipt_commit_recovers_ready_when_cleanup_and_rewrite_fail; final PR CI 36357233039
success, approval23:08, merge23:09; текущая suite73tests. Урок: fault injection должен моделировать side
effect, произошедший несмотря на ошибочный return. Каждый кейс в отчёте сопровождается PR URL,
review date, исправляющим commit, именем regression и CI SHA. Эти кейсы не выдаются за испытания
будущего OS sandbox/live adapter. Источник: https://github.com/Tramsey00/MathStart-Python/pull/10 .

---

## 19. Организация курса и сроки
L3 прочитан целиком до 34:11. Общие слова преподавателя о регулярном значимом продвижении,
voice/screen и регистрации относятся ко всем проектам. Конкретные советы по инструментам и Harness-
механизмам, данные другой команде в 14:03–18:14, для MathStart являются только contextual material:
MathStart может независимо принять полезный механизм как PROJECT DECISION, но не приписывает его
преподавателю как MathStart mandate. Разрешение LearnForge около 24:21 не является согласованием
MathStart. Совет другой команде в L2 также не создаёт обязательного требования к конкретному
внешнему context/memory tool для MathStart. 9 октября включительно — регистрация/согласование
проекта; L2 исправляет 5→9 в 02:16–02:29, L3 подтверждает в 31:58–32:12. Защита — зачётная неделя,
точная дата TBD (L3 32:41–32:58). Ранняя сдача разрешена: вопрос 33:00.133–33:03.853, ответ 33:04.818–
33:14.358. Принадлежность вопроса нашей команде известна из задания пользователя; SRT не содержит
speaker identity. Следующая встреча — «восьмого в девять вечера», L3 33:42.737–34:11.458; рабочий
checkpoint08.10.2026 21:00, timezone/LMS приглашение подтверждает Руслан. MS7-ORG01: Руслан до 07.10
собирает название/описание/ФИО/группы/public GitHub/подтверждение согласования, остальные
проверяют свои данные. До 09.10 сохраняется LMS receipt/screenshot без лишних персональных данных.
Это отдельный организационный gate, не защита и не G0/G1. 08.10 показать actual baseline+новый
выполненный increment+review/evidence, а не обещать весь MVP. Примерный объём пояснительной
записки 45–60 страниц относится к отчёту, не ограничивает объём ТЗ. Преподаватель допускает
иллюстрацию trace; обязательность repo trace в MathStart — внутреннее принятое правило. 3NF —
рекомендация по нормализации, а не запрет любых обоснованных JSON snapshots. Внешние учебные
примеры Harness использовались только как ненормативный источник инженерных идей. Их названия,
структуры, версии языка и лицензии не определяют архитектуру MathStart; её задают это ТЗ, accepted
ADR/specs и merged repository state.

---

## 20. Зависимости и готовность основной программы

Исторический календарь v7.1 сохранён в исходном PDF, страницы37–42. Он не является новым обещанием сроков после миграции. Новый календарь, deadline защиты и capacity обязательства этим техническим переносом не утверждаются. Организационные даты §19 сохраняются как исторические источники; фактическая регистрация требует собственного receipt.

Основная программа содержит те же52 canonical task IDs и те же HARD/CONTRACT/HANDOFF/INTEGRATION рёбра (§25). До основной реализации должны быть приняты HARD/CONTRACT; HANDOFF/INTEGRATION обязательны к финальной приёмке. При ожидании входа фиксируется конкретный blocker и выполняется доступная независимая подготовка. Будущие Knowledge/Assessment/Progress/Analyzer/Tutor/adaptive задачи остаются planned.

Миграционный release принят; готовность каждой будущей задачи зависит от контракта и фактических upstream deliverables каждой карточки. Полная машинная52-row таблица с исходными карточками/типами зависимостей, historical result, platform disposition и target evidence: [текущий registry](../../specs/product/task-dispositions-v7.2.json). Исторические результаты карточек сохранены; принятие платформы не означает реализации будущих задач.


---

## 21. Dependency model и организация карточек
TASK ID NAMING CONVENTION FOLLOW-UP SUFFIX: суффикс A в MS7-R02A, MS7-R03A и MS7-R04A означает
первую самостоятельную post-baseline follow-up/addendum задачу после соответствующей frozen-задачи.
R02 остаётся FROZEN в объёме Exercise/API architecture contract; R03 — Progress v1 reference contract;
MS6R04 — Runner, Adapter Protocol и FakeAdapter. Новая downstream-задача имеет собственные scope,
evidence и acceptance и не меняет статус принятого результата. R02A НЕ означает «исправить
неправильно сделанную R02». R03A НЕ означает «переделать R03». R04A НЕ означает «переоткрыть R04».
Это отдельные planned downstream-задачи; их PLANNED относится к новому объёму, а не к
историческому baseline. SPLIT SUFFIX: MS7-R06A и MS7-R06B получены разделением будущей MS6-R06
ещё до её реализации. R06A отвечает за Policy, Hooks и Machine Trace, R06B — за Physical Sandbox.
Завершённой frozen R06 здесь нет: это SPLIT PLANNED TASK, а не follow-up к выполненной работе. В
таблице используются полные canonical IDs. Короткие R02A/R03A/R04A/R06A/R06B в дорожной карте
обозначают те же задачи; историческая R04 здесь всегда означает MS6-R04. IDs сохраняются ради
traceability. ID
Relation
Meaning
MS7-R02A
FOLLOW-UP TO FROZEN R02
HTTP/eligibility addendum
MS7-R03A
FOLLOW-UP TO FROZEN R03
CompletionFact/progress-v1.1 addendum
MS7-R04A
FOLLOW-UP TO FROZEN MS6-R04
Live coding-model adapter
MS7-R06A
PART A OF SPLIT PLANNED MS6-R06
Policy/Hooks/Machine Trace
MS7-R06B
PART B OF SPLIT PLANNED MS6-R06
Physical Sandbox
Follow-up не переоткрывает frozen-задачу; split делит ещё не выполненную planned-задачу. Семантика
суффикса задаётся этим правилом и полем Relation, а не одной буквой A. HARD — результат нужен до
начала реализации потребителя. CONTRACT — нужен accepted schema/fixture, хотя runtime реализации
потребителя может ещё не быть. HANDOFF — работа начинается параллельно, но именованный artifact
должен быть принят до task acceptance. INTEGRATION — настоящий upstream runtime нужен для
завершения, хотя fixtures допустимы раньше. SOFT — рекомендация без блокировки. Типы рёбер из
предыдущего v7 сохранены; все четыре blocking типа входят в cycle check, SOFT не ограничивает
топологический порядок. У карточки 31 базовое содержательное поле; только у пяти неоднозначных IDs
добавлено Relation to previous task. Базовые поля сгруппированы для чтения: identity/ответственность;
результат/цель/requirements; четыре типа dependencies; parallel work; inputs/scope/out-of-scope;
deliverables/acceptance/failure; tests/security/live/evidence; handoff/downstream/risks; календарь/DoD
additions. Canonical ID и название стоят в заголовке. Unified DoD §17 применяется по ссылке, не
дублируется. Requirements covered перечисляет прямые связи из §26/28; общие NFR применяются по
своему scope, а не искусственно приписываются каждой карточке. Inputs включают только принятые
версии артефактов названных dependencies и соответствующие §§5–
16. Контракты §7–11, Registry/Policy §12–14, eval/security §15–16
остаются нормативными в полном
объёме. Пустой список direct FR не означает, что задача необязательна: Harness/contract closeout может
закрывать D-решение, C/NFR либо быть upstream для требуемого runtime. Scope каждого исходного task
сохранён дословно.
Parallel work в карточках разрешено другим Owner и на названной стадии. Generic SOFT guidance:
предыдущие traces сходных задач; это не новая задача и не требование повторять historical work.
Отдельных SOFT task edges в baseline нет. Evidence E(ID), migrations/recovery, независимость approvals и
boundaries определены §17. Task-specific risks — опасный отказ в Negative acceptance и явно указанный
integration risk; известный failure нельзя спрятать общим «tests passed».
Canonical GitHub Issue lifecycle для исполняемых Task Cards
Нормативное правило: каждая исполняемая задача имеет ровно одну canonical GitHub Issue с тем же
canonical Task ID, что и task card (MS7-Rxx, MS7-Vxx, MS7-Ixx, MS7-ORGxx, MS7-HKxx и иные canonical IDs
настоящего ТЗ). Issue создаётся до начала основной implementation; основная implementation не начинается,
пока canonical Issue не зарегистрирована. Issue содержит либо однозначно ссылается на canonical Task ID,
task card, Owner, Reviewer, Task Approver, Milestone Gate, dependencies, scope, acceptance criteria и, когда
применимо, accepted exec plan/evidence. Одна исполняемая task card = одна canonical Issue; дополнительные
Issues для той же карточки допускаются только с отдельным обоснованием. Branch обязана ссылаться на
canonical Task ID/Issue. PR обязан ссылаться на соответствующую Issue и использовать GitHub closing keyword
(например, Closes #<issue-number> или эквивалент), чтобы после успешного merge canonical Issue
закрывалась автоматически. Нормальный lifecycle: Task Card -> GitHub Issue -> Branch -> Implementation -> PR
-> Independent Review -> Task Approval -> CI / Verification -> Merge -> GitHub Issue Closed -> Evidence / trace.
Создание PR не закрывает Issue; закрытие происходит после фактического успешного merge либо вручную
только по специально предусмотренному workflow. Автоматическое закрытие Issue после merge не равно
Task Acceptance и не равно Milestone Gate; merge не заменяет approval, Gate не закрывается автоматически
из-за task merge, а evidence E(ID) остаётся обязательным. Owner != Reviewer/Task Approver; Reviewer и Task
Approver могут совпадать. Hotfix/bootstrap/экстренное исключение фиксируется в evidence/exec plan и не
превращается в обычный путь выполнения задач.

---

## 22. Рабочие карточки: Руслан

### MS7-R02A · HTTP и eligibility addendum

Status: HISTORICAL_RESULT_PRESERVED; новый платформенный evidence указан ниже. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G1
(contract closeout; не повтор G0). Relation to previous task: FOLLOW-UP / ADDENDUM TO FROZEN R02.
Что получим простыми словами: Сервер и интерфейс получат единые правила отправки решений,
повторных запросов и показа подсказок; два разработчика смогут независимо делать совместимые
части.
Зачем нужна задача: Устранить пробел между принятым Exercise contract и будущим HTTP API.
Requirements covered: FR-04.
HARD: —.
CONTRACT: R02.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: у остальных участников — review/подготовка по §20.
Inputs/contracts: R02 accepted artifact §2; нормативные разделы по §21.
Detailed Scope: OpenAPI всех endpoints §11; immutable revision, exposure и idempotency fixtures; human
review D-022/023 до клиентов.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; полная реализация зависимых runtime-потребителей.
Deliverables: OpenAPI, DTO и набор fixtures для revision/exposure/idempotency.
Acceptance criteria: OpenAPI всех endpoints §11; соответствие named contract и ожидаемые результаты
task-specific tests.
Negative/failure acceptance: help-submit race и повторный positive не проходят.
Task-specific tests: Повтор submit, stale revision, help-submit race, second-positive eligibility.
Task-specific security checks: Исключение answer/checker из public DTO; данные чужого owner
недоступны.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R02A).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R09, MS7-R10, MS7-R11, MS7-R12, MS7-V02, MS7-V03, MS7-V04, MS7-V05, MS7V06,
MS7-I02.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: Accepted OpenAPI digest перед V02/I02; R02 имена полей сохранены.

**Platform disposition:** CONTRACT_PRESERVED. Новая migration-приёмка: MS7-MIG-R02, MS7-MIG-R03. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R03A · CompletionFact addendum

Status: HISTORICAL_RESULT_PRESERVED; новый платформенный evidence указан ниже. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G1
(contract closeout; не повтор G0). Relation to previous task: FOLLOW-UP / ADDENDUM TO FROZEN R03.
Что получим простыми словами: Будет точно определено, как завершение попытки без оценки
влияет на историю и последние десять попыток, не меняя числовые знания ученика.
Зачем нужна задача: Согласовать CompletionFact отдельно от уже принятого progress-v1.
Requirements covered: D-021; FR14/15; NFR-03.
HARD: —.
CONTRACT: R03.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-V02, MS7-I02.
Inputs/contracts: R03 accepted artifact §2; нормативные разделы по §21.


Detailed Scope: ADR D-021, progress-v1.1 и parity fixtures; порядок completed_at/attempt_id, neutral window,
late facts; старые deltas
неизменны.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; полная реализация зависимых runtime-потребителей.
Deliverables: ADR D-021, addendum progress-v1.1, neutral/late/parity fixtures.
Acceptance criteria: ADR D021, progress-v1.1 и parity fixtures; соответствие named contract и ожидаемые
результаты task-specific tests.
Negative/failure acceptance: нейтральное завершение не создаёт fake penalty.
Task-specific tests: Одинаковые timestamps, поздний факт, дубликат, вытеснение independent из окна.
Task-specific security checks: Нейтральный факт не превращается в штраф и не получает полномочия
менять mastery.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R03A).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R11, MS7-V08.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: Parity fixtures с progress-v1 и versioned CompletionFact принят отдельно.

**Platform disposition:** CONTRACT_PRESERVED. Новая migration-приёмка: MS7-MIG-R02, MS7-MIG-R03. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R05 · Context Layer и typed tools

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G1.
Что получим простыми словами: Агент сможет получать нужные части репозитория и вызывать
заранее описанные инструменты с понятными входами и результатами.
Зачем нужна задача: Ограничить контекст и подготовить проверяемые вызовы для Policy.
Requirements covered: NFR-12.
HARD: MS6-R04.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-V02, MS7-V03, MS7-I02, MS7-I03.
Inputs/contracts: MS6-R04 accepted artifact §2; нормативные разделы по §21.
Detailed Scope: Manifest digests/range reads; context budgets/compaction; registry schemas всех tools §13;
tests обязательного контекста.
Область файлов: harness/, specs/, tests/harness/.
Out of Scope: Общие исключения §17; повторная реализация frozen Runner/publication.
Deliverables: Context manifest, compaction format, schemas typed tools.
Acceptance criteria: Manifest digests/range reads; соответствие named contract и ожидаемые результаты
task-specific tests.
Negative/failure acceptance: overflow до model call; stale patch запрещён.
Task-specific tests: Digest drift, missing mandatory contract, oversized context, truncated range и output.
Taskspecific security checks: Patch только с expected digest; run_check из registry, без произвольной
shellстроки.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R05).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R06A, MS7-R04A.
Task-specific risks: См. Negative/failure acceptance этой карточки.



Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R06A · Policy, hooks и machine trace

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G1.
Relation to previous task: SPLIT PART A OF PLANNED R06.
Что получим простыми словами: Harness будет проверять действие до исполнения, разрешать или
запрещать его и сохранять причину решения.
Зачем нужна задача: Превратить наблюдение за агентом в предварительный контроль действий.
Requirements covered: D-026; NFR-19.
HARD: MS7-R05.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-V03, MS7-V04, MS7-I03.
Inputs/contracts: MS7-R05 Context Layer и typed tools; нормативные разделы по §21.
Detailed Scope: before-tool fail-closed, approval binding, hooks lifecycle, redacted append-only trace/resume;
unknown schema
deny.
Область файлов: harness/, specs/, tests/harness/.
Out of Scope: Общие исключения §17; повторная реализация frozen Runner/publication.
Deliverables: Policy rules, before/after hooks, approval binding, redacted trace/resume.
Acceptance criteria: before-tool fail-closed, approval binding, hooks lifecycle, redacted append-only
trace/resume; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: ошибка security hook останавливает действие.
Task-specific tests: Unknown tool/arg, hook failure, expired approval, resume drift и forged permit.
Taskspecific security checks: Fail-closed при ошибке hook; разрешение связано с точным действием и
состоянием.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R06A).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R06B.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R06B · Физический sandbox

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G1.
Relation to previous task: SPLIT PART B OF PLANNED R06.
Что получим простыми словами: Даже при ошибке агента исполнитель не сможет выйти за
разрешённые файлы, сеть и дочерние процессы.
Зачем нужна задача: Обеспечить физическое выполнение ограничений Policy.
Requirements covered: D-026; NFR-19.
HARD: MS7-R06A.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-V04, MS7-V05, MS7-I04.
Inputs/contracts: MS7-R06A Policy, hooks и machine trace; нормативные разделы по §21.
Detailed Scope: Изолированный executor с roots/network/process tree limits; real escape и timeout tests на
объявленной ОС.



Область файлов: harness/, specs/, tests/harness/.
Out of Scope: Общие исключения §17; повторная реализация frozen Runner/publication.
Deliverables: Изолированный executor и матрица реально доказанных ограничений ОС.
Acceptance criteria: Изолированный executor с roots/network/process tree limits; соответствие named
contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: junction/symlink/path traversal и child escape блокируются физически.
Task-specific tests: Real symlink/junction/traversal escape, inherited handles, subprocess tree timeout.
Taskspecific security checks: Нет host socket/credentials; ограничения проверяются вне mocked Policy.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R06B).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R04A, MS7-R07.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: Доказанная ОС и реальные denial tests; advisory mode не закрывает задачу.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R04A · Live coding-model adapter

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G1.
Relation to previous task: FOLLOW-UP IMPLEMENTATION TO FROZEN MS6-R04.
Что получим простыми словами: Настоящая coding-модель сможет изменить разрешённый участок
кода через Harness, пройти проверки и подготовить результат человеку.
Зачем нужна задача: Подтвердить полный live loop, которого FakeAdapter не доказывает.
Requirements covered: D-027; NFR-19.
HARD: —.
CONTRACT: MS7-R05.
HANDOFF: —.
INTEGRATION: MS7-R06B.
Что можно делать параллельно: MS7-V05, MS7-V06, MS7-I04, MS7-I05.
Inputs/contracts: MS7-R05 Context Layer и typed tools; MS7-R06B Физический sandbox; нормативные
разделы по §21.
Detailed Scope: Capability spike direct API/App Server; start/message/tool loop; usage/cancel; реальная
scoped правка через Registry и checks.
Область файлов: harness/, specs/, tests/harness/.
Out of Scope: Общие исключения §17; повторная реализация frozen Runner/publication.
Deliverables: Capability matrix, live adapter, redacted end-to-end run bundle.
Acceptance criteria: Capability spike direct API/App Server; соответствие named contract и ожидаемые
результаты task-specific tests.
Negative/failure acceptance: opaque tools не получают enforcement label; no hidden bypass.
Task-specific tests: Start/message/tool/cancel/usage, неизвестный event, deadline, denied tool.
Task-specific security checks: Все действия проходят Registry и sandbox; непрозрачные внутренние tools
не получают enforcement label.
Live model/API requirement: Обязателен live evidence этой задачи; normal CI offline.
Evidence: E(MS7-R04A).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R08, MS7-V07, MS7-I08.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: Verified capability matrix: intercept_all_actions и sandbox proof.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R07 · Skills и bounded subagents

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G1.
Что получим простыми словами: Агент сможет подключать инструкции для задачи и помощника с
меньшими правами, не теряя контроля над изменениями.
Зачем нужна задача: Разделять специализированную работу без расширения доверия.
Requirements covered: D-026; NFR-19.
HARD: MS7-R06B.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-V06, MS7-I05, MS7-I06.
Inputs/contracts: MS7-R06B Физический sandbox; нормативные разделы по §21.
Detailed Scope: Versioned skill schema, subset rights, depth1/max2, one-writer ledger, reviewer read-only и
structured handoff.
Область файлов: harness/, specs/, tests/harness/.
Out of Scope: Общие исключения §17; повторная реализация frozen Runner/publication.
Deliverables: Versioned skills, subagent protocol, rights/budget ledger и handoff schema.
Acceptance criteria: Versioned skill schema, subset rights, depth1/max2, one-writer ledger, reviewer read-only
и structured handoff; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: child не расширяет permissions/budget.
Task-specific tests: Invalid skill reference, excessive depth/count, concurrent writer, malformed handoff.
Taskspecific security checks: Reviewer child read-only, subset permissions, запрет самоодобрения и запуска
внуков.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R07).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R08, MS7-V07, MS7-I08.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R08 · Harness eval и G1

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G1.
Что получим простыми словами: Команда получит доказательство, что собственный Harness работает
на реальных задачах всех трёх участников и выдерживает опасные сценарии.
Зачем нужна задача: Закрыть G1 по наблюдаемым результатам, а не по наличию CLI.
Requirements covered: NFR-08, NFR-19, C-01 (+ действующие внутренние D-requirements).
HARD: MS7-R04A, MS7-R07.
CONTRACT: —.
HANDOFF: MS7-V07, MS7-I08.
INTEGRATION: —.
Что можно делать параллельно: MS7-V10, MS7-I09.
Inputs/contracts: MS7-R04A Live coding-model adapter; MS7-R07 Skills и bounded subagents; MS7-V07
Backend skill и real run; MS7-I08 Frontend skill и visual run; нормативные разделы по §21.
Detailed Scope: 12 eval cases, три real owner runs, final CI и независимая приёмка; собрать R04 regressions
без ослабления.
Область файлов: harness/, specs/, tests/harness/.
Out of Scope: Общие исключения §17; повторная реализация frozen Runner/publication.
Deliverables: Harness eval report и сводный пакет трёх owner runs для G1.
Acceptance criteria: 12 eval cases, три real owner runs, final CI и независимая приёмка; соответствие


Negative/failure acceptance: fake run не закрывает live criterion.
Task-specific tests: Все 12 eval cases §15, R04 publication regressions, denied actions и failed checks.
Taskspecific security checks: Проверка физических запретов, forged READY и отсутствия скрытого обхода.
Live model/API requirement: Обязателен live evidence этой задачи; normal CI offline.
Evidence: E(MS7-R08).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R16.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: Три real owner runs приняты до решения G1.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R09 · Parser и normalizer

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G2.
Что получим простыми словами: Система сможет безопасно прочитать поддерживаемую
математическую запись, сохранив исходный текст ученика.
Зачем нужна задача: Отделить понимание записи от оценки правильности решения.
Requirements covered: FR-10, NFR-15.
HARD: —.
CONTRACT: MS7-R02A.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-V08, MS7-I06, MS7-I08.
Inputs/contracts: MS7-R02A HTTP и eligibility addendum; нормативные разделы по §21.
Detailed Scope: Whitelist AST, rational semantics и isolated limits §9; raw/normalized roundtrip; grammar
fixtures.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; OCR, геометрия и unsupported grammar вне whitelist §9.
Deliverables: Whitelist parser/normalizer и versioned grammar fixtures.
Acceptance criteria: Whitelist AST, rational semantics и isolated limits §9; соответствие named contract и
ожидаемые результаты task-specific tests.
Negative/failure acceptance: malicious/large/deep/nonlinear input даёт safe status.
Task-specific tests: Rational equivalence, raw roundtrip, глубина/размер/степень, unsupported nonlinear
input.
Task-specific security checks: Запрещён eval; процессные лимиты, злонамеренные и worst-case
выражения.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R09).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R10.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R10 · Validators и deterministic Analyzer

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G2.
Что получим простыми словами: MathStart сможет проверить ответ и шаги решения и указать первую
доказанную ошибку, не обвиняя ученика при непонятном вводе.
Зачем нужна задача: Создать детерминированную основу Analyzer и проверяемую связь с taxonomy.
Requirements covered: FR-06, FR07, FR-08, FR-10, FR-11, FR-12, FR-13, NFR-14.




HARD: MS7-R09.
CONTRACT: MS7-R02A.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-V07, MS7-V09, MS7-I08, MS7-I07.
Inputs/contracts: MS7-R09 Parser и normalizer; MS7-R02A HTTP и eligibility addendum; нормативные
разделы по §21.
Detailed Scope: Final/steps/две structured schemas, first proven error, taxonomy mapping;
AnalysisResult domain validation.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; изменение accepted Progress/Exercise семантики без addendum.
Deliverables: Validators оцениваемых режимов, два structured validators, AnalysisResult validation.
Acceptance criteria: Final/steps/две structured schemas, first proven error, taxonomy mapping; соответствие
named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: wrong final и broken prefix не создают misconception.
Task-specific tests: Equivalent answers, first error, cascade, invalid prefix, wrong-final-only, unknown
taxonomy.
Task-specific security checks: Недоверенный payload не выбирает validator произвольно; unsupported не
создаёт misconception.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R10).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R13, MS7-R14, MS7-V10, MS7-V11.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R11 · Adaptive и diagnostic policy

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G3.
Что получим простыми словами: Система получит понятные правила, какое упражнение предложить
дальше и когда остановить тренировку.
Зачем нужна задача: Сделать диагностику и адаптацию воспроизводимыми.
Requirements covered: FR-16, FR-19.
HARD: —.
CONTRACT: MS7-R03A, MS7-R02A.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-V10.
Inputs/contracts: MS7-R03A CompletionFact addendum; MS7-R02A HTTP и eligibility addendum;
нормативные разделы по §21.
Detailed Scope: Pure selector depth2, stable tie-break, difficulty bands, exclude/repeat/no-candidate и session
stop fixtures.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; полная реализация зависимых runtimeпотребителей.
Deliverables: Pure selector и versioned diagnostic/practice policy fixtures.
Acceptance criteria: Pure selector depth2, stable tie-break, difficulty bands, exclude/repeat/no-candidate и
session stop fixtures; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: revealed diagnostics и бесконечная практика запрещены.
Task-specific tests: Tie-break, prerequisite depth, difficulty fallback, repeats, empty pool, session limits.
Taskspecific security checks: Revealed diagnostics не считаются независимым успехом; нет бесконечной
практики.


Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R11).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-V12, MS7-I13.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R12 · Tutor policy и hint bank

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G3.
Что получим простыми словами: До раскрытия ответа ученик будет получать только заранее
проверенные подсказки; правила общения не позволят модели выдать всё решение.
Зачем нужна задача: Согласовать границу полезной помощи и раскрытия ответа.
Requirements covered: FR-17.
HARD: —.
CONTRACT: MS7-R02A.
HANDOFF: MS7-V04.
INTEGRATION: —.
Что можно делать параллельно: MS7-V11, MS7-I10.
Inputs/contracts: MS7-R02A HTTP и eligibility addendum; MS7-V04 Exercise versions и pilot bank;
нормативные разделы по §21.
Detailed Scope: Review pre-reveal curated bank, context minimization и allowed intent schema; prompt
versions и fallback.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; полная реализация зависимых runtimeпотребителей.
Deliverables: Reviewed hint bank, intent schema, prompt versions, fallback policy.
Acceptance criteria: Review pre-reveal curated bank, context minimization и allowed intent schema;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: одношаговая подсказка не раскрывает весь ответ.
Task-specific tests: Single-step leakage, unsupported intent, exhausted hints, before/after reveal.
Task-specific security checks: В контекст до reveal не попадает checker/answer; curated bank проходит
независимый review.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R12).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-V13, MS7-I12.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R13 · Аудит persisted evidence loop

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G2.
Что получим простыми словами: Команда проверит, что результат решения один раз и целиком
попадает в прогресс и восстанавливается из истории.
Зачем нужна задача: Подтвердить границы Assessment/Progress на работающей базе.
Requirements covered: NFR-01.
HARD: MS7-R10.
CONTRACT: —.
HANDOFF: —.




INTEGRATION: MS7-V10, MS7-V09.
Что можно делать параллельно: MS7-V12, MS7-I11.
Inputs/contracts: MS7-V10 Finalize Analysis→Progress; MS7-V09 Replay и concurrency; MS7-R10 Validators и
deterministic Analyzer; нормативные разделы по §21.
Detailed Scope: Cross-domain import audit, atomic finalize/Progress replay/eligibility; G2 evidence и
негативные race scenarios.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; изменение accepted Progress/Exercise семантики без addendum.
Deliverables: Cross-domain audit и G2 evidence pack.
Acceptance criteria: Cross-domain import audit, atomic finalize/Progress replay/eligibility; соответствие
named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: дубли и прямые writes Analyzer/Tutor в Progress запрещены.
Task-specific tests: Atomic finalize, crash/retry, concurrent reveal/submit, duplicate ingest, replay parity.
Taskspecific security checks: Поиск прямых Progress writes из Analyzer/Tutor/frontend; неверная eligibility
блокирует событие.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R13).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R16.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: AT-02–08 на PostgreSQL и crossdomain audit приняты до G2.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R14 · Golden eval и AI gates

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G4.
Что получим простыми словами: Появится измеримый отчёт о правильных ответах, ошибках и
отказах Analyzer, Tutor и Harness на заранее зафиксированных примерах.
Зачем нужна задача: Не выпускать AIповедение по впечатлению от нескольких удачных запросов.
Requirements covered: NFR-02.
HARD: MS7-R10.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V11, MS7-V13.
Что можно делать параллельно: MS7-V14, MS7-I13.
Inputs/contracts: MS7-V11 Product provider и AIRun; MS7-V13 Tutor context и conversations; MS7-R10
Validators и deterministic Analyzer; нормативные разделы по §21.
Detailed Scope: 50 Analyzer/20 Tutor/12 Harness cases, holdout≥20, denominators и live smoke; report
metrics §15.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; изменение accepted Progress/Exercise семантики без addendum.
Deliverables: Versioned golden/holdout sets, denominators и eval report.
Acceptance criteria: 50 Analyzer/20 Tutor/12 Harness cases, holdout≥20, denominators и live smoke;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: abstention не записывается как correct; false strong=0 на safety set.
Task-specific tests: Analyzer 50+, Tutor 20+, Harness 12+, holdout 20+; separate deterministic/live lanes.
Task-specific security checks: Safety subset без ложного strong negative; injection/unknown/malformed
входят в отчёт.
Live model/API requirement: Обязателен live evidence этой задачи; normal CI offline.
Evidence: E(MS7-R14).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R17.


Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: Denominators/holdout зафиксированы, safety false strong=0.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R15 · Security/privacy release audit

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G4.
Что получим простыми словами: До выпуска команда получит проверенный список рисков утечки
данных, чужого доступа и опасных настроек.
Зачем нужна задача: Закрыть security/privacy blockers на интегрированной системе.
Requirements covered: NFR-04, NFR-06.
HARD: —.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V14, MS7-I14.
Что можно делать параллельно: у остальных участников — review/подготовка по §20.
Inputs/contracts: MS7-V14 Staging сборка; MS7-I14 Полная интеграция; нормативные разделы по §21.
Detailed Scope: Threat review, CSRF/IDOR/leaks/rate/retention и deployment checks; findings с
owner/severity.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; изменение accepted Progress/Exercise семантики без addendum.
Deliverables: Threat review, severity/owner register и исправления блокирующих findings.
Acceptance criteria: Threat review, CSRF/IDOR/leaks/rate/retention и deployment checks; соответствие
named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: critical finding блокирует RC, не снимается сменой severity без review.
Task-specific tests: CSRF, IDOR, XSS, secret leak, rate bypass, retention и deployment checks.
Task-specific security checks: Понижение severity требует review; неизвестный доступ к данным
блокирует release.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R15).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R17, MS7-V15, MS7-I15.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R16 · Архитектура и глава Harness

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G5.
Что получим простыми словами: В отчёте появится объяснение архитектуры и собственного Harness с
реальными ошибками, исправлениями и вкладом участников.
Зачем нужна задача: Сделать инженерные решения проверяемыми на защите.
Requirements covered: C-06, C-08, C-09, C-10.
HARD: MS7-R08.
CONTRACT: —.
HANDOFF: MS7-R13.
INTEGRATION: —.
Что можно делать параллельно: MS7-V15, MS7-I15.
Inputs/contracts: MS7-R08 Harness eval и G1; MS7-R13 Аудит persisted evidence loop; нормативные
разделы по §21.
Detailed Scope: Chapters2/3, схемы из contracts, real failure cases с review/commit/test/CI; три вклада.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.




Out of Scope: Общие исключения §17; изменение accepted Progress/Exercise семантики без addendum.
Deliverables: Главы 2/3, схемы из contracts, ссылки на PR/CI/regressions.
Acceptance criteria: Chapters2/3, схемы из contracts, real failure cases с review/commit/test/CI;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: не выдумывать model reasoning и неизвестные approvals.
Task-specific tests: Сверка каждого кейса с review, commit, test name и CI; trace excerpt redaction.
Taskspecific security checks: Нет secrets, student PII или выдуманной private chain-of-thought.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R16).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R18.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R17 · Публичный RC и репетиция

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G4.
Что получим простыми словами: Команда пройдёт общий показ публичной версии и убедится, что
приложение, отчёт и доказательства относятся к одному выпуску.
Зачем нужна задача: Снять расхождения между отдельными приёмками до G4.
Requirements covered: C-02, C-05.
HARD: MS7-R14, MS7-R15.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V17, MS7-I17.
Что можно делать параллельно: MS7-V18, MS7-I17, MS7-I18; до MS7-I17 — только contract fixtures,
integration после handoff.
Inputs/contracts: MS7-R14 Golden eval и AI gates; MS7-R15 Security/privacy release audit; MS7-V17
Публичный backend release; MS7-I17 Public browser rehearsal; нормативные разделы по §21.
Detailed Scope: AT-01–16 на одном release SHA; сверить URL/CI/evidence/report draft, провести общий
demo.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; изменение accepted Progress/Exercise семантики без addendum.
Deliverables: RC ledger, AT-01–16 report, rehearsal record.
Acceptance criteria: AT-01–16 на одном release SHA; соответствие named contract и ожидаемые
результаты task-specific tests.
Negative/failure acceptance: видео/localhost не заменяют public system.
Task-specific tests: Полный внешний browser маршрут и fallback на release SHA.
Task-specific security checks: Критические findings, неизвестный owner и недоступный HTTPS блокируют
RC.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R17).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R18.
Task-specific risks: Непринятый runtime handoff: MS7-I17.
Task-specific DoD additions: AT-01–16 и public URL на одном RC SHA.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-R18 · Freeze и handover

Status: PLANNED. Owner: Руслан. Reviewer: Владимир. Task Approver: Владимир. Milestone Gate: G5.
Что получим простыми словами: Проект будет передан с окончательным отчётом, доступами,
инструкциями и перечнем известных ограничений.
Зачем нужна задача: Закрыть G5 и готовность к согласованной защите.
Requirements covered: C-12, C-13, C-15, C-17.
HARD: MS7-R17, MS7-V18, MS7-I18, MS7-R16.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: у остальных участников — review/подготовка по §20.
Inputs/contracts: MS7-R17 Публичный RC и репетиция; MS7-V18 Backend freeze; MS7-I18 Frontend freeze;
MS7-R16 Архитектура и глава Harness; нормативные разделы по §21.
Detailed Scope: Final report PDF, release ledger, accepted gates, links/runbooks/known limits; согласовать
защиту.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; изменение accepted Progress/Exercise семантики без addendum.
Deliverables: Final report PDF, freeze ledger, runbooks и evidence index.
Acceptance criteria: Final report PDF, release ledger, accepted gates, links/runbooks/known limits;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: pending gate не закрывать автоматически.
Task-specific tests: Проверка всех gate approvals, ссылок, доступа и совпадения release SHA. Taskspecific
security checks: Секреты передаются вне repo/report; pending acceptance не превращается в DONE.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-R18).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: gate ledger / handover.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: Все G0–G5 имеют отдельные approvals; дата защиты подтверждена.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.


---

## 23. Рабочие карточки: Владимир

### MS7-V02 · Аккаунты и права

Status: HISTORICAL_RESULT_PRESERVED; новый платформенный evidence указан ниже. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G3.
Что получим простыми словами: Ученик сможет зарегистрироваться, войти и выбрать профиль, а
сервер не позволит читать чужие данные.
Зачем нужна задача: Создать настоящую идентичность для попыток и прогресса.
Requirements covered: FR-01.
HARD: MS6-V01.
CONTRACT: MS7-R02A.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R03A, MS7-R05, MS7-I02.
Inputs/contracts: MS7-R02A HTTP и eligibility addendum; MS6-V01 accepted artifact §2; нормативные
разделы по §21.
Detailed Scope: FastAPI profile/auth/onboarding APIs с совместимыми hashes/sessions/receipts; owner queries, CSRF/session, registration/login negative
cases.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: FastAPI auth/profile/onboarding services и API, SQLAlchemy persistence и Alembic migrations.
Acceptance criteria: FastAPI profile/auth/onboarding APIs с совместимыми hashes/sessions/receipts; соответствие named contract и ожидаемые
результаты task-specific tests.
Negative/failure acceptance: чужой UUID404; GET не меняет знания.
Task-specific tests: Registration/login/logout, three onboarding modes, invalid credentials и ownership.
Taskspecific security checks: CSRF, session rotation, одинаковые login errors, чужой UUID 404.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V02).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-V05, MS7-I03.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** NEW_PLATFORM_EVIDENCE_REQUIRED. Новая migration-приёмка: MS7-MIG-V03, MS7-MIG-V06. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V03 · Knowledge и TopicSkill persistence

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G2.
Что получим простыми словами: В базе появятся навыки, связи между ними и соответствия темам;
повторная загрузка не испортит историю.
Зачем нужна задача: Дать общей модели знаний устойчивое хранилище.
Requirements covered: FR-03, FR-16, C-07.
HARD: MS6-V01.
CONTRACT: R03, MS7-R02A.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R05, MS7-R06A, MS7-I03.
Inputs/contracts: R03 accepted artifact §2; MS7-R02A HTTP и eligibility addendum; MS6-V01 accepted artifact
§2; нормативные разделы по §21.
Detailed Scope: Models/migrations/seed10skills13edges; ContentPage mappings; archive history и seed twice.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне


Deliverables: Models, additive migrations, pilot seed и TopicSkill mappings.
Acceptance criteria: Models/migrations/seed10skills13edges; соответствие named contract и ожидаемые
результаты taskspecific tests.
Negative/failure acceptance: cycle/unknown/duplicate отклоняются атомарно.
Task-specific tests: 10 skills/13 edges, seed twice, unknown/cycle/duplicate, fresh/upgrade.
Task-specific security checks: Archive вместо удаления evidence-referenced объектов; Content не владеет
Skill.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V03).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-V04, MS7-V08.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V04 · Exercise versions и pilot bank

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G2.
Что получим простыми словами: Преподавательский контент получит версии упражнений, а пилот —
проверенный банк заданий без ответов в браузере.
Зачем нужна задача: Подготовить реальные задания для всех четырёх режимов.
Requirements covered: FR-04, FR-08, FR-09, NFR-18.
HARD: MS7-V03.
CONTRACT: MS7-R02A.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R06A, MS7-R06B.
Inputs/contracts: MS7-V03 Knowledge и TopicSkill persistence; MS7-R02A HTTP и eligibility addendum;
нормативные разделы по §21.
Detailed Scope: Immutable versions/private validators; import40assessed+3selfcheck; PRIMARY coverage и
provenance; minimum12steps12final2schemas.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Immutable ExerciseVersion storage, importer, 40 assessed + 3 self-check.
Acceptance criteria: Immutable versions/private validators; соответствие named contract и ожидаемые
результаты task-specific tests.
Negative/failure acceptance: digest conflict не затирает published version; public DTO не течёт.
Task-specific tests: Coverage PRIMARY, two structured schemas, provenance, publication digest conflicts.
Task-specific security checks: Private validators/answers не попадают в public JSON/HTML/JS.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V04).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R12, MS7-V05, MS7-I04.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V05 · Attempts, revisions и steps

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G2.
Что получим простыми словами: Решение ученика будет сохраняться как черновик, а отправленная
версия станет неизменяемой и защищённой от дублей.
Зачем нужна задача: Сделать попытку надёжным источником дальнейшей проверки.
Requirements covered: FR-05, FR-07, FR-21.
HARD: MS7-V02, MS7-V04.
CONTRACT: MS7-R02A.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R06B, MS7-R04A, MS7-I04.
Inputs/contracts: MS7-V02 Аккаунты и права; MS7-V04 Exercise versions и pilot bank; MS7-R02A HTTP и
eligibility addendum; нормативные разделы по §21.
Detailed Scope: Draft CAS, submit snapshot, ordered typed steps, receipts/operation retry; schema migrations.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Attempt/revision/typed step persistence и draft/submit endpoints.
Acceptance criteria: Draft CAS, submit snapshot, ordered typed steps, receipts/operation retry; соответствие
named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: stale revision409; submitted edit forbidden.
Task-specific tests: CAS conflict 409, row reorder, immutable submit, retry receipt.
Task-specific security checks: Owner scoping, лимиты входа, запрет редактирования submitted snapshot.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V05).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-V06, MS7-V10, MS7-I05, MS7-I06, MS7-I07.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V06 · Единая помощь и reveal

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G2.
Что получим простыми словами: Нажатая подсказка или раскрытый ответ будут надёжно записаны до
показа, даже при одновременной отправке решения.
Зачем нужна задача: Не выдавать помощь за независимый успех.
Requirements covered: FR-09, FR-18.
HARD: MS7-V05.
CONTRACT: MS7-R02A.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R04A, MS7-R07, MS7-I05, MS7-I06.
Inputs/contracts: MS7-V05 Attempts, revisions и steps; MS7-R02A HTTP и eligibility addendum; нормативные
разделы по §21.
Detailed Scope: Exposure lock, hints/reveal durable before return, cross-attempt policy, shared Tutor endpoint.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Exposure service, hint/reveal endpoints и durable help records.
Acceptance criteria: Exposure lock, hints/reveal durable before return, cross-attempt policy, shared Tutor


Negative/failure acceptance: concurrent submit/help не теряет факт помощи.
Task-specific tests: Submit/help race, retries, new attempt, interrupted response.
Task-specific security checks: Cross-attempt eligibility и secret reveal только после server authorization.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V06).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-V10, MS7-V13, MS7-I09.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V07 · Backend skill и real run

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G1.
Что получим простыми словами: Владимир выполнит настоящий backend increment через Harness и
покажет проверки базы и независимое ревью.
Зачем нужна задача: Подтвердить, что Harness пригоден для backend работы команды.
Requirements covered: C-01/08; NFR-19.
HARD: —.
CONTRACT: MS7-R07.
HANDOFF: —.
INTEGRATION: MS7-R04A.
Что можно делать параллельно: MS7-R10, MS7-I08, MS7-I07.
Inputs/contracts: MS7-R07 Skills и bounded subagents; MS7-R04A Live coding-model adapter; нормативные
разделы по §21.
Detailed Scope: Backend profile migrations/PG/ownership; реальный increment с reviewer child и evidence;
human independent review.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Backend skill profile и live owner run bundle.
Acceptance criteria: Backend profile migrations/PG/ownership; соответствие named contract и ожидаемые
результаты task-specific tests.
Negative/failure acceptance: child read-only и отсутствующий PG не маскируются.
Task-specific tests: Migrations/PG/ownership checks, reviewer child, final verification.
Task-specific security checks: Child read-only; SQLite skips не маскируются как PostgreSQL proof.
Live model/API requirement: Обязателен live evidence этой задачи; normal CI offline.
Evidence: E(MS7-V07).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R08.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V08 · ProgressEvent и проекция

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G2.
Что получим простыми словами: Подтверждённые события начнут менять знания ученика по
принятой формуле; нейтральные завершения сохранятся отдельно.
Зачем нужна задача: Реализовать единственного владельца долгосрочного прогресса.
Requirements covered: FR-02, FR-13, FR-14, FR-22.




HARD: MS7-V03.
CONTRACT: MS7-R03A.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R09, MS7-I06, MS7-I08.
Inputs/contracts: MS7-V03 Knowledge и TopicSkill persistence; MS7-R03A CompletionFact addendum;
нормативные разделы по §21.
Detailed Scope: Only Progress writes, exact Decimal reducer, event/source uniqueness, Completion mirror,
atomic ingest.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: ProgressEvent, completion mirror, UserSkillState и ingest service.
Acceptance criteria: Only Progress writes, exact Decimal reducer, event/source uniqueness, Completion
mirror, atomic ingest; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: conflicting duplicate409; malformed evidence не меняет state.
Task-specific tests: Decimal deltas/clamps, event/source uniqueness, duplicate conflict, atomic rollback.
Taskspecific security checks: Только validated evidence через Progress API; malformed input не меняет state.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V08).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-V09, MS7-I11.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V09 · Replay и concurrency

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G2.
Что получим простыми словами: Прогресс будет одинаковым при обычной работе и повторном
воспроизведении истории, включая поздние события.
Зачем нужна задача: Защитить данные от гонок, сбоев и разного порядка доставки.
Requirements covered: FR-15, NFR-03.
HARD: MS7-V08.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R10, MS7-I07.
Inputs/contracts: MS7-V08 ProgressEvent и проекция; нормативные разделы по §21.
Detailed Scope: Late event/fact replay, last10neutral window, stable locks, online/replay parity PostgreSQL.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Replay service, locking protocol и PostgreSQL regression suite.
Acceptance criteria: Late event/fact replay, last10neutral window, stable locks, online/replay parity
PostgreSQL; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: crash/retry и одинаковое время не дают расхождения.
Task-specific tests: Same timestamp, late facts, retry/crash, last-ten neutral window, online/replay parity.
Taskspecific security checks: Stable lock order; повтор не создаёт второе положительное evidence.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V09).


Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R13, MS7-V10, MS7-I10.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: PostgreSQL online/replay equality под concurrent writes.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V10 · Finalize Analysis→Progress

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G2.
Что получим простыми словами: Проверенное решение, завершение попытки и изменение прогресса
будут сохраняться вместе либо не сохраняться вовсе.
Зачем нужна задача: Соединить Analyzer и Progress без частично завершённых операций.
Requirements covered: FR-06, FR-11, FR-14, NFR-17.
HARD: MS7-V05, MS7-V06, MS7-V09.
CONTRACT: MS7-R10.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R08, MS7-R11, MS7-I09.
Inputs/contracts: MS7-V05 Attempts, revisions и steps; MS7-V06 Единая помощь и reveal; MS7-V09 Replay и
concurrency; MS7-R10 Validators и deterministic Analyzer; нормативные разделы по §21.
Detailed Scope: Validate outside transaction, atomic result/completion/event, operation recovery;
reveal/eligibility lock.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Finalize service, operation receipts/recovery и persisted result API.
Acceptance criteria: Validate outside transaction, atomic result/completion/event, operation recovery;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: provider failure не оставляет halfcompleted state.
Task-specific tests: Validate outside transaction, atomic commit, retry after crash, reveal lock.
Task-specific security checks: Provider failure не оставляет half-completed state; client verdict не
доверяется.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V10).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R13, MS7-V11, MS7-V12, MS7-I10.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V11 · Product provider и AIRun

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G3.
Что получим простыми словами: Приложение сможет безопасно обращаться к настоящей модели и
записывать версию, результат и причину отказа.
Зачем нужна задача: Изолировать внешнего провайдера от доменных решений.
Requirements covered: FR-12, FR-23, NFR-09, C-03.
HARD: MS7-V10.
CONTRACT: MS7-R10.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R12, MS7-I10.




Inputs/contracts: MS7-R10 Validators и deterministic Analyzer; MS7-V10 Finalize Analysis→Progress;
нормативные разделы по §21.
Detailed Scope: Infrastructure adapter, Pydantic/schema/domain gates, prompt version, redaction/deadlines;
live bounded Analyzer smoke.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Provider adapter, AIRun persistence, structured output validation и live smoke.
Acceptance criteria: Infrastructure adapter, Pydantic/schema/domain gates, prompt version,
redaction/deadlines; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: timeout/invalid/unknown code→abstain без strong negative.
Task-specific tests: Malformed/unknown/low-confidence response, timeout, unavailable provider.
Task-specific security checks: Credentials только infrastructure; domain validation и redaction до
сохранения.
Live model/API requirement: Обязателен live evidence этой задачи; normal CI offline.
Evidence: E(MS7-V11).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R14, MS7-V13.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V12 · Диагностика и Practice API

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G3.
Что получим простыми словами: Диагностика и тренировка будут помнить выбранное задание и не
менять его при обновлении страницы.
Зачем нужна задача: Перенести адаптивную политику в устойчивые пользовательские сессии.
Requirements covered: FR-02, FR-19, FR-20.
HARD: MS7-V10.
CONTRACT: MS7-R11.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R13, MS7-I11.
Inputs/contracts: MS7-R11 Adaptive и diagnostic policy; MS7-V10 Finalize Analysis→Progress; нормативные
разделы по §21.
Detailed Scope: Persist selected item, one-active, next/finish idempotency, max10/7, target/originreturn,
selfreport integration.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Diagnostic/Practice sessions и next/finish/skip APIs.
Acceptance criteria: Persist selected item, one-active, next/finish idempotency, max10/7, target/originreturn,
selfreport integration; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: refresh не выбирает новый item; empty pool завершает безопасно.
Task-specific tests: One-active, max10/7, deterministic refresh, empty pool, origin return.
Task-specific security checks: Чужая сессия недоступна; revealed evidence не получает independent credit.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V12).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-V14, MS7-I11, MS7-I13.
Task-specific risks: См. Negative/failure acceptance этой карточки.


Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V13 · Tutor context и conversations

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G3.
Что получим простыми словами: Ученик сможет вести связанный с текущим заданием диалог и
получать разрешённые подсказки даже при сбое модели.
Зачем нужна задача: Подключить Tutor к реальным попыткам и правилам помощи.
Requirements covered: FR-17, FR-18.
HARD: MS7-V11, MS7-V06.
CONTRACT: MS7-R12.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-I12.
Inputs/contracts: MS7-R12 Tutor policy и hint bank; MS7-V11 Product provider и AIRun; MS7-V06 Единая
помощь и reveal; нормативные разделы по §21.
Detailed Scope: Owner conversations, bounded context, bank intent selection, durable help, after-reveal safe
explanation.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Owner conversations, context builder, intent selection и fallback.
Acceptance criteria: Owner conversations, bounded context, bank intent selection, durable help, after-reveal
safe explanation; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: cross-owner/checker leak/injection не выдаёт ответ.
Task-specific tests: Before/after reveal, repeated hints, timeout, malicious message, bounded history.
Taskspecific security checks: No cross-owner context, checker leak, arbitrary pre-reveal math или unsafe HTML.
Live model/API requirement: Обязателен live evidence этой задачи; normal CI offline.
Evidence: E(MS7-V13).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R14, MS7-V14, MS7-I12.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V14 · Staging сборка

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G3.
Что получим простыми словами: Появится общая среда, где интерфейс и backend работают вместе на
PostgreSQL с настройками, близкими к выпуску.
Зачем нужна задача: Дать команде место для полной приёмки перед публичным размещением.
Requirements covered: NFR-11.
HARD: MS7-V12, MS7-V13.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R14, MS7-I13.
Inputs/contracts: MS7-V12 Диагностика и Practice API; MS7-V13 Tutor context и conversations;
нормативные разделы по §21.
Detailed Scope: Production-like PostgreSQL service, static/media, health/config, initial deploy runbook; clean
build and full runtime.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.




Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Staging deployment, config/health checks и initial runbook.
Acceptance criteria: Production-like PostgreSQL service, static/media, health/config, initial deploy runbook;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: не использовать runserver/SQLite как release proof.
Task-specific tests: Clean build, static/media, full runtime routes, failed readiness.
Task-specific security checks: Никакого runserver/SQLite в качестве production proof; secrets отделены от
кода.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V14).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R15, MS7-V15, MS7-I14.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V15 · Backend security/performance

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G4.
Что получим простыми словами: Будут измерены скорость и ошибки backend, а ограничения
запросов начнут работать между несколькими процессами.
Зачем нужна задача: Проверить выпуск под объявленной нагрузкой и закрыть backend findings.
Requirements covered: NFR-05, NFR-07.
HARD: MS7-V14.
CONTRACT: —.
HANDOFF: MS7-R15.
INTEGRATION: —.
Что можно делать параллельно: MS7-R16, MS7-I15.
Inputs/contracts: MS7-V14 Staging сборка; MS7-R15 Security/privacy release audit; нормативные разделы по
§21.
Detailed Scope: Shared rate limits, ownership/CSRF checks, measured cohorts §16, queries and errors/fallback
report.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Shared limits, cohort metrics и security/performance report.
Acceptance criteria: Shared rate limits, ownership/CSRF checks, measured cohorts §16, queries and
errors/fallback report; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: concurrent workers не обходят limits; samples не фильтруются.
Task-specific tests: Concurrent workers, rate window edges, retries, catalogue/submit/progress/AI cohorts.
Task-specific security checks: Не исключать failures из выборки; ownership/CSRF/leak regressions
обязательны.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V15).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-V16.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V16 · Restore/upgrade и backend chapter

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G4.
Что получим простыми словами: Команда сможет восстановить данные из резервной копии и
обновить выпуск без потери истории.
Зачем нужна задача: Подтвердить восстановимость, а не только создание backup файла.
Requirements covered: NFR-10.
HARD: MS7-V15.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-I16.
Inputs/contracts: MS7-V15 Backend security/performance; нормативные разделы по §21.
Detailed Scope: Measured backup restore RPO24h/RTO2h, additive upgrade drill, data consistency и report
chapter.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Restore/upgrade runbooks, measured drill и backend chapter.
Acceptance criteria: Measured backup restore RPO24h/RTO2h, additive upgrade drill, data consistency и
report chapter; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: повреждённый backup detected; исторические evidence не теряются.
Task-specific tests: Corrupt backup, fresh restore, additive upgrade, replay/content integrity.
Task-specific security checks: Encrypted backup, RPO/RTO evidence; applied migrations не переписываются.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V16).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-V17.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: Измерены RPO/RTO и restore/upgrade consistency.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V17 · Публичный backend release

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G4.
Что получим простыми словами: Backend станет доступен по публичному HTTPS адресу и передаст
интерфейсу точную версию выпуска.
Зачем нужна задача: Открыть реальный сервис для внешней проверки и защиты.
Requirements covered: FR-24, C-11.
HARD: MS7-V16.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: у остальных участников — review/подготовка по §20.
Inputs/contracts: MS7-V16 Restore/upgrade и backend chapter; нормативные разделы по §21.
Detailed Scope: HTTPS URL, approved config/secrets, production migrations и health; build SHA handoff Илье.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Production release, migration/health evidence и SHA handoff.
Acceptance criteria: HTTPS URL, approved config/secrets, production migrations и health; соответствие
named contract и ожидаемые результаты task-specific tests.


Negative/failure acceptance: failed readiness/restore rollback блокирует выпуск.
Task-specific tests: External HTTPS, startup/readiness, static/media, rollback check.
Task-specific security checks: Approved config/secrets; failed readiness или restore blocker останавливает
выпуск.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V17).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R17, MS7-V18, MS7-I17.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-V18 · Backend freeze

Status: PLANNED. Owner: Владимир. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G5.
Что получим простыми словами: Другой участник получит понятные инструкции по запуску и
обслуживанию backend и его ограничениям.
Зачем нужна задача: Завершить передачу серверной части до общего freeze.
Requirements covered: FR-24; NFR-11.
HARD: MS7-V17.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R17, MS7-I17.
Inputs/contracts: MS7-V17 Публичный backend release; нормативные разделы по §21.
Detailed Scope: Runbooks, backup ownership, schema/lock versions, secure credential handover и known
limits.
Область файлов: домены §5, specs/ и tests; точные files определяет exec plan.
Out of Scope: Общие исключения §17; доверие клиентскому verdict и прямые записи Progress вне
владельца.
Deliverables: Backend handover, dependency/schema versions и backup ownership.
Acceptance criteria: Runbooks, backup ownership, schema/lock versions, secure credential handover и known
limits; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: секреты не попадают в repo/report.
Task-specific tests: Проверка runbooks и доступа принимающим участником.
Task-specific security checks: Никаких ключей в отчёте; credential transfer по отдельному защищённому
каналу.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-V18).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R18.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.


---

## 24. Рабочие карточки: Илья

### MS7-I02 · UI foundation и fixtures

Status: HISTORICAL_RESULT_PRESERVED; новый платформенный evidence указан ниже. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: Появится общий каркас интерфейса: компоненты, мобильная основа
и состояния загрузки, ошибок и пустых данных.
Зачем нужна задача: Дать последующим экранам общую основу и согласованные fixtures.
Requirements covered: NFR-13/16; FR-04.
HARD: MS6-I01.
CONTRACT: MS7-R02A.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R03A, MS7-R05, MS7-V02.
Inputs/contracts: MS7-R02A HTTP и eligibility addendum; MS6-I01 accepted artifact §2; нормативные
разделы по §21.
Detailed Scope: Reusable React components, tokens/state fixtures, schema dispatch, loading/error/empty;
baseline accessibility.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: React components, design tokens и versioned state fixtures.
Acceptance criteria: Reusable React components, tokens/state fixtures, schema dispatch,
loading/error/empty; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: fixture-only явно маркирован; checker не включается.
Task-specific tests: Schema dispatch, loading/error/empty states, keyboard foundation.
Task-specific security checks: Fixture-only маркируется; checker и answer не входят в bundle.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I02).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I03, MS7-I04, MS7-I08.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLATFORM_ADAPTED_BASELINE. Новая migration-приёмка: MS7-MIG-I01, MS7-MIG-I05. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I03 · Auth/profile/onboarding UI

Status: HISTORICAL_RESULT_PRESERVED; новый платформенный evidence указан ниже. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: Ученик сможет пройти регистрацию, вход и начальную настройку
через понятные формы.
Зачем нужна задача: Сделать серверные аккаунты доступными пользователю.
Requirements covered: FR-01, FR-02.
HARD: MS7-I02.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V02.
Что можно делать параллельно: MS7-R05, MS7-R06A, MS7-V03.
Inputs/contracts: MS7-I02 UI foundation и fixtures; MS7-V02 Аккаунты и права; нормативные разделы по
§21.
Detailed Scope: Регистрация/вход/3onboarding modes, CSRF, safe errors, keyboard forms и saved state.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.


Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Auth/profile/onboarding screens на настоящем API.
Acceptance criteria: Регистрация/вход/3onboarding modes, CSRF, safe errors, keyboard forms и saved state;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: retry не дублирует selfreport; чужой account не раскрывается.
Task-specific tests: Три onboarding пути, saved state, retry, invalid credentials, keyboard.
Task-specific security checks: CSRF; не раскрывать чужой account или повторно начислять self-report.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I03).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I11, MS7-I14.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** NEW_PLATFORM_EVIDENCE_REQUIRED. Новая migration-приёмка: MS7-MIG-I04, MS7-MIG-I05. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I04 · Каталог и renderer

Status: PLANNED. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: Каталог сохранит прежние темы и научится показывать новые
задания нужного типа на телефоне и компьютере.
Зачем нужна задача: Связать существующий контент с пилотной учебной моделью.
Requirements covered: FR-03.
HARD: MS7-I02.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V04.
Что можно делать параллельно: MS7-R06B, MS7-R04A, MS7-V05.
Inputs/contracts: MS7-I02 UI foundation и fixtures; MS7-V04 Exercise versions и pilot bank; нормативные
разделы по §21.
Detailed Scope: ContentPage routes, PRIMARY coverage, four mode dispatch, schema versions, mobile theory.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Catalogue/topic templates и versioned four-mode renderer.
Acceptance criteria: ContentPage routes, PRIMARY coverage, four mode dispatch, schema versions, mobile
theory; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: unknown schema controlled; old content preserved.
Task-specific tests: ContentPage routes, PRIMARY denominator, unknown schema, old content.
Task-specific security checks: Публичный renderer не содержит validation secrets и не доверяет HTML
модели.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I04).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I05, MS7-I07.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I05 · SELF_CHECK и final answer UI

Status: PLANNED. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: Ученик сможет проверить себя или отправить итоговый ответ, не
создавая новую попытку случайным повторным нажатием.
Зачем нужна задача: Провести первый рабочий маршрут от задания к результату.
Requirements covered: FR-05, FR-06.
HARD: MS7-I04.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V05.
Что можно делать параллельно: MS7-R04A, MS7-R07, MS7-V06.
Inputs/contracts: MS7-I04 Каталог и renderer; MS7-V05 Attempts, revisions и steps; нормативные разделы
по §21.
Detailed Scope: Server attempt creation/draft/submit, selfcheck label, immutable result и retry key.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: SELF_CHECK и FINAL_ANSWER forms, draft/submit/retry state.
Acceptance criteria: Server attempt creation/draft/submit, selfcheck label, immutable result и retry key;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: refresh/двойной submit не удваивает completion.
Task-specific tests: Double click, refresh, interrupted submit, immutable result.
Task-specific security checks: Самопроверка явно отделена от оцениваемого решения; server receipt
авторитетен.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I05).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I06, MS7-I09.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I06 · Пошаговый редактор

Status: PLANNED. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: Ученик сможет записывать и переставлять шаги решения, а
интерфейс сохранит ввод и покажет конфликт старого черновика.
Зачем нужна задача: Собрать точное пошаговое решение для deterministic validation.
Requirements covered: FR-07.
HARD: MS7-I05.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V05.
Что можно делать параллельно: MS7-R07, MS7-R09, MS7-V06, MS7-V08.
Inputs/contracts: MS7-I05 SELF_CHECK и final answer UI; MS7-V05 Attempts, revisions и steps; нормативные
разделы по §21.
Detailed Scope: Typed ordered rows/reorder, raw text, CAS draft, focus restore и submitted freeze.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Typed ordered step editor, CAS draft и focus recovery.


Acceptance criteria: Typed ordered rows/reorder, raw text, CAS draft, focus restore и submitted freeze;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: stale response не затирает ввод; invalid step labelled.
Task-specific tests: Add/reorder/delete, raw text, stale response, submitted freeze.
Task-specific security checks: Клиент не утверждает parse status/verdict; limits и schema соблюдены.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I06).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I09.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I07 · Structured solution UI

Status: PLANNED. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: Для двух типов заданий появятся отдельные структурированные
формы с понятными ошибками полей.
Зачем нужна задача: Поддержать STRUCTURED режим без подмены его текстовым полем.
Requirements covered: FR-08.
HARD: MS7-I04.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V05.
Что можно делать параллельно: MS7-R10, MS7-V07, MS7-V09.
Inputs/contracts: MS7-I04 Каталог и renderer; MS7-V05 Attempts, revisions и steps; нормативные разделы
по §21.
Detailed Scope: Два разных schemas через registry, field errors, keyboard и payload contract.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Schema registry dispatch и два structured editors.
Acceptance criteria: Два разных schemas через registry, field errors, keyboard и payload contract;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: неизвестные поля не отправляются как trusted result.
Task-specific tests: Valid/invalid/unknown field, keyboard order, request payload parity.
Task-specific security checks: Неизвестные поля не отправляются как доверенный результат проверки.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I07).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I09.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I08 · Frontend skill и visual run

Status: PLANNED. Owner: Илья. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G1.
Что получим простыми словами: Илья выполнит реальное изменение интерфейса через Harness и
подтвердит его работой браузера.
Зачем нужна задача: Проверить пригодность frontend skill и browser tools.




Requirements covered: NFR-20.
HARD: MS7-I02.
CONTRACT: MS7-R07.
HANDOFF: —.
INTEGRATION: MS7-R04A.
Что можно делать параллельно: MS7-R09, MS7-R10, MS7-V08, MS7-V07.
Inputs/contracts: MS7-R07 Skills и bounded subagents; MS7-R04A Live coding-model adapter; MS7-I02 UI
foundation и fixtures; нормативные разделы по §21.
Detailed Scope: Frontend profile/browser tools, real increment, DOM/network/console+screenshots и read-
only reviewer.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Frontend profile, live run, DOM/network/console evidence и screenshots.
Acceptance criteria: Frontend profile/browser tools, real increment, DOM/network/console+screenshots и
read-only reviewer; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: visual screenshot не заменяет DOM/assertions; no external browsing bypass.
Task-specific tests: Real route assertions, failed UI state, reviewer child и allowed origin.
Task-specific security checks: Нет внешнего browsing bypass; screenshot не подменяет DOM assertions.
Live model/API requirement: Обязателен live evidence этой задачи; normal CI offline.
Evidence: E(MS7-I08).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R08.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I09 · Hints/reveal и recovery UI

Status: PLANNED. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: Подсказки и раскрытие ответа останутся видны после обновления
страницы или сбоя сети.
Зачем нужна задача: Согласовать видимое состояние помощи с серверной историей.
Requirements covered: FR-09, FR-18.
HARD: MS7-I05, MS7-I06, MS7-I07.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V06.
Что можно делать параллельно: MS7-R08, MS7-V10.
Inputs/contracts: MS7-I05 SELF_CHECK и final answer UI; MS7-I06 Пошаговый редактор; MS7-I07 Structured
solution UI; MS7-V06 Единая помощь и reveal; нормативные разделы по §21.
Detailed Scope: Server-accepted help levels, explicit reveal, refresh/network timeout canonical state.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Hint/reveal controls и canonical recovery views.
Acceptance criteria: Server-accepted help levels, explicit reveal, refresh/network timeout canonical state;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: help не исчезает при новом attempt/back.
Task-specific tests: New attempt/back/refresh, timeout after accepted help, explicit reveal.
Task-specific security checks: Нельзя локально стереть факт помощи или показать answer до
разрешения сервера.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.


Evidence: E(MS7-I09).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I10, MS7-I12.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I10 · Feedback/progress views

Status: PLANNED. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: Ученик увидит подтверждённую ошибку, неопределённый результат
и свои знания без ложного обвинения или выдуманного прогресса.
Зачем нужна задача: Показать настоящие результаты Analyzer и Progress.
Requirements covered: FR-22.
HARD: MS7-I09.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V10, MS7-V09.
Что можно делать параллельно: MS7-R12, MS7-V11.
Inputs/contracts: MS7-I09 Hints/reveal и recovery UI; MS7-V10 Finalize Analysis→Progress; MS7-V09 Replay и
concurrency; нормативные разделы по §21.
Detailed Scope: Confirmed/uncertain/unsupported, first error, skill list/map, topic denominator и history.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Feedback states, skill map/list, topic mastery/coverage и history views.
Acceptance criteria: Confirmed/uncertain/unsupported, first error, skill list/map, topic denominator и history;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: NOT_STARTED не равен любой низкой confidence; uncertain не обвиняет.
Task-specific tests: First error, unsupported/uncertain, NOT_STARTED, PRIMARY denominator.
Task-specific security checks: Unknown confidence не превращается в misconception; owner-only data.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I10).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I13.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I11 · Onboarding completion/history

Status: PLANNED. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: История и стартовая диагностика будут показывать реальные
сохранённые попытки и выбранный путь обучения.
Зачем нужна задача: Завершить onboarding и навигацию по доказательствам прогресса.
Requirements covered: FR-21.
HARD: MS7-I03.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V08, MS7-V12.
Что можно делать параллельно: MS7-R13, MS7-V12; до MS7-V12 — только contract fixtures, integration




Inputs/contracts: MS7-I03 Auth/profile/onboarding UI; MS7-V08 ProgressEvent и проекция; MS7-V12
Диагностика и Practice API; нормативные разделы по §21.
Detailed Scope: Real selfreport/zero/diagnostic entry, paginated attempts/events и filter labels.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Onboarding completion, diagnostic entry, paginated history/filter screens.
Acceptance criteria: Real selfreport/zero/diagnostic entry, paginated attempts/events и filter labels;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: не изображать diagnostic fixtures как runtime.
Task-specific tests: Zero/selfreport/diagnostic, pagination, filter labels, persisted refresh.
Task-specific security checks: Fixtures не выдаются за runtime; чужие attempts/events не отображаются.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I11).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I14.
Task-specific risks: Непринятый runtime handoff: MS7-V12.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I12 · Tutor panel

Status: PLANNED. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: Ученик сможет пользоваться Tutor в задании и понимать, когда
ответ ожидается, ограничен или заменён безопасной подсказкой.
Зачем нужна задача: Представить реальные состояния диалога и помощи.
Requirements covered: FR-17/18 (UI потребитель R12/V13).
HARD: MS7-I09.
CONTRACT: MS7-R12.
HANDOFF: —.
INTEGRATION: MS7-V13.
Что можно делать параллельно: MS7-V13; до MS7-V13 — только contract fixtures, integration после
handoff.
Inputs/contracts: MS7-I09 Hints/reveal и recovery UI; MS7-R12 Tutor policy и hint bank; MS7-V13 Tutor
context и conversations; нормативные разделы по §21.
Detailed Scope: Scoped conversation, bounded messages, approved hints, degraded/rate/pending, reveal
confirmation.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Tutor panel, scoped messages, degraded/rate/pending states.
Acceptance criteria: Scoped conversation, bounded messages, approved hints, degraded/rate/pending, reveal
confirmation; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: LLM HTML escaped; no free math before reveal.
Task-specific tests: Bounded messages, retry, hint selection, reveal confirmation.
Task-specific security checks: LLM HTML экранируется; произвольное решение до reveal не
отображается.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I12).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I14.


Task-specific risks: Непринятый runtime handoff: MS7-V13.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I13 · Practice и diagnostics UI

Status: PLANNED. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: Ученик сможет пройти диагностику или короткую тренировку и
вернуться к исходной теме без потери места.
Зачем нужна задача: Сделать адаптивный маршрут завершённым и понятным.
Requirements covered: FR-20.
HARD: MS7-I10.
CONTRACT: MS7-R11.
HANDOFF: —.
INTEGRATION: MS7-V12.
Что можно делать параллельно: MS7-R14, MS7-V14.
Inputs/contracts: MS7-I10 Feedback/progress views; MS7-R11 Adaptive и diagnostic policy; MS7-V12
Диагностика и Practice API; нормативные разделы по §21.
Detailed Scope: Target/reason/streak/count/max7, next/finish/skip, deterministic refresh и origin return.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Practice/diagnostic screens с причиной выбора, счётчиком и возвратом.
Acceptance criteria: Target/reason/streak/count/max7, next/finish/skip, deterministic refresh и origin return;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: no-candidate и archived topic не создают тупик.
Task-specific tests: Next/skip/finish, max7, streak, refresh, empty pool, archived origin.
Task-specific security checks: Server-selected item авторитетен; клиент не рисует успешное evidence сам.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I13).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I14.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I14 · Полная интеграция

Status: PLANNED. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G3.
Что получим простыми словами: Все основные действия ученика заработают вместе на общей среде
без подставных ответов.
Зачем нужна задача: Проверить продукт целиком до release hardening.
Requirements covered: FR-01–24 (интеграционная приёмка); NFR-11/13/17.
HARD: MS7-I03, MS7-I11, MS7-I12, MS7-I13.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V14.
Что можно делать параллельно: у остальных участников — review/подготовка по §20.
Inputs/contracts: MS7-I03 Auth/profile/onboarding UI; MS7-I11 Onboarding completion/history; MS7-I12
Tutor panel; MS7-I13 Practice и diagnostics UI; MS7-V14 Staging сборка; нормативные разделы по §21.
Detailed Scope: Все SC routes на PostgreSQL staging без mocks; four modes,




Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: SC route matrix, PostgreSQL staging browser suite и integration report.
Acceptance criteria: Все SC routes на PostgreSQL staging без mocks; соответствие named contract и
ожидаемые результаты taskspecific tests.
Negative/failure acceptance: network loss/relogin не портят evidence.
Task-specific tests: Четыре режима, auth/help/practice/return/history, network loss/relogin.
Task-specific security checks: Ни один основной путь не заменён mocks; interruption не портит evidence.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I14).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R15, MS7-I15.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: SC routes без mocks на PostgreSQL staging.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I15 · A11y/mobile/security UX

Status: PLANNED. Owner: Илья. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G4.
Что получим простыми словами: Интерфейс станет пригоден для клавиатуры, маленьких экранов и
нескольких браузеров, включая длинные формулы и ошибки.
Зачем нужна задача: Закрыть доступность и клиентские security findings.
Requirements covered: NFR-13, NFR-16.
HARD: MS7-I14.
CONTRACT: —.
HANDOFF: MS7-R15.
INTEGRATION: —.
Что можно делать параллельно: MS7-R16, MS7-V15.
Inputs/contracts: MS7-I14 Полная интеграция; MS7-R15 Security/privacy release audit; нормативные
разделы по §21.
Detailed Scope: 360/768/1440, Chrome/Edge/Firefox, keyboard, labels/focus/live regions/contrast, XSS safe
rendering.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: A11y/mobile/browser matrix и исправления UX.
Acceptance criteria: 360/768/1440, Chrome/Edge/Firefox, keyboard, labels/focus/live regions/contrast, XSS
safe rendering; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: цвет/мышь не единственный путь; длинные формулы не ломают layout.
Task-specific tests: 360/768/1440, Chrome/Edge/Firefox, labels/focus/live regions/contrast.
Task-specific security checks: XSS safe rendering; мышь и цвет не являются единственным способом
действия.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I15).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I16, MS7-I17.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I16 · Demo и главы отчёта

Status: PLANNED. Owner: Илья. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G5.
Что получим простыми словами: Будут готовы два воспроизводимых демонстрационных маршрута и
иллюстрации отчёта на искусственных данных.
Зачем нужна задача: Показать реальный продукт и вклад каждого участника.
Requirements covered: C-06/11/12 (demo и report).
HARD: MS7-I15.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7V16.
Inputs/contracts: MS7-I15 A11y/mobile/security UX; нормативные разделы по §21.
Detailed Scope: Synthetic stories, screenshots release SHA, главы 1/4, два demo маршрута и вклад каждого.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Demo stories, release-linked screenshots и главы 1/4.
Acceptance criteria: Synthetic stories, screenshots release SHA, главы 1/4, два demo маршрута и вклад
каждого; соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: не показывать реальные student данные и fake metrics.
Task-specific tests: Повтор сценариев на указанном SHA, сверка цифр и результатов.
Task-specific security checks: Не показывать реальных учеников и выдуманные метрики.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I16).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-I18.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I17 · Public browser rehearsal

Status: PLANNED. Owner: Илья. Reviewer: Руслан и Владимир. Task Approver: Руслан и Владимир. Milestone
Gate: G4.
Что получим простыми словами: Публичный сайт будет проверен из чистого внешнего браузера,
включая медленную сеть и повторный вход.
Зачем нужна задача: Подтвердить, что выпуск работает за пределами компьютера разработчика.
Requirements covered: FR-24.
HARD: MS7-I15.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: MS7-V17.
Что можно делать параллельно: MS7-R17, MS7-V18.
Inputs/contracts: MS7-I15 A11y/mobile/security UX; MS7-V17 Публичный backend release; нормативные
разделы по §21.
Detailed Scope: Clean external browser на public URL; slow network, relogin, refresh, reveal/history; evidence
versions.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: External browser acceptance bundle и release rehearsal findings.
Acceptance criteria: Clean external browser на public URL; соответствие named contract и ожидаемые
результаты task-specific tests.


Negative/failure acceptance: localhost/video не закрывают acceptance.
Task-specific tests: Public URL, relogin, refresh, reveal/history, slow network.
Task-specific security checks: Localhost и видео не принимаются как доказательство публичной работы.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I17).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R17, MS7-I18.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: Внешний чистый browser и production release SHA.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.

### MS7-I18 · Frontend freeze

Status: PLANNED. Owner: Илья. Reviewer: Руслан. Task Approver: Руслан. Milestone Gate: G5.
Что получим простыми словами: Принимающий участник получит окончательные ресурсы
интерфейса, версии и инструкции по проверке.
Зачем нужна задача: Закрыть передачу frontend до общего G5.
Requirements covered: FR-24; NFR-13.
HARD: MS7-I17, MS7-I16.
CONTRACT: —.
HANDOFF: —.
INTEGRATION: —.
Что можно делать параллельно: MS7-R17.
Inputs/contracts: MS7-I17 Public browser rehearsal; MS7-I16 Demo и главы отчёта; нормативные разделы
по §21.
Detailed Scope: Static build/contracts/browser versions, release links, known limits, handover.
Область файлов: frontend/, reviewed static/ assets, UI fixtures и browser tests.
Out of Scope: Общие исключения §17; математическое оценивание в браузере и секреты validator.
Deliverables: Frontend freeze ledger, asset/contract/browser versions и handover.
Acceptance criteria: Static build/contracts/browser versions, release links, known limits, handover;
соответствие named contract и ожидаемые результаты task-specific tests.
Negative/failure acceptance: сломанные production assets блокируют freeze.
Task-specific tests: Static build, production assets, links и known limits.
Task-specific security checks: Повреждённые assets или утечка секретов блокируют freeze.
Live model/API requirement: Не требуется для task-specific функциональной приёмки; правило
engineering run после G1 — §17.
Evidence: E(MS7-I18).
Handoff: принятая версия Deliverables; конкретный состав передачи — §25.
Downstream tasks: MS7-R18.
Task-specific risks: См. Negative/failure acceptance этой карточки.
Task-specific DoD additions: —.

**Platform disposition:** PLANNED_EQUIVALENT. Новая migration-приёмка: будущая scoped implementation по неизменённым dependency kinds. Текущие доказательства — execution ledger; future product runtime не реализуется этой миграцией.


---

## 25. Dependency matrix и handoff

| Consumer | HARD | CONTRACT | HANDOFF | INTEGRATION |
| --- | --- | --- | --- | --- |
| MS7-R02A | — | R02 | — | — |
| MS7-R03A | — | R03 | — | — |
| MS7-R05 | MS6-R04 | — | — | — |
| MS7-R06A | MS7-R05 | — | — | — |
| MS7-R06B | MS7-R06A | — | — | — |
| MS7-R04A | — | MS7-R05 | — | MS7-R06B |
| MS7-R07 | MS7-R06B | — | — | — |
| MS7-R08 | MS7-R04A, MS7-R07 | — | MS7-V07, MS7-I08 | — |
| MS7-R09 | — | MS7-R02A | — | — |
| MS7-R10 | MS7-R09 | MS7-R02A | — | — |
| MS7-R11 | — | MS7-R03A, MS7-R02A | — | — |
| MS7-R12 | — | MS7-R02A | MS7-V04 | — |
| MS7-R13 | MS7-R10 | — | — | MS7-V10, MS7-V09 |
| MS7-R14 | MS7-R10 | — | — | MS7-V11, MS7-V13 |
| MS7-R15 | — | — | — | MS7-V14, MS7-I14 |
| MS7-R16 | MS7-R08 | — | MS7-R13 | — |
| MS7-R17 | MS7-R14, MS7-R15 | — | — | MS7-V17, MS7-I17 |
| MS7-R18 | MS7-R17, MS7-V18, MS7-I18, MS7-R16 | — | — | — |
| MS7-V02 | MS6-V01 | MS7-R02A | — | — |
| MS7-V03 | MS6-V01 | R03, MS7-R02A | — | — |
| MS7-V04 | MS7-V03 | MS7-R02A | — | — |
| MS7-V05 | MS7-V02, MS7-V04 | MS7-R02A | — | — |
| MS7-V06 | MS7-V05 | MS7-R02A | — | — |
| MS7-V07 | — | MS7-R07 | — | MS7-R04A |
| MS7-V08 | MS7-V03 | MS7-R03A | — | — |
| MS7-V09 | MS7-V08 | — | — | — |
| MS7-V10 | MS7-V05, MS7-V06, MS7-V09 | MS7-R10 | — | — |
| MS7-V11 | MS7-V10 | MS7-R10 | — | — |
| MS7-V12 | MS7-V10 | MS7-R11 | — | — |
| MS7-V13 | MS7-V11, MS7-V06 | MS7-R12 | — | — |
| MS7-V14 | MS7-V12, MS7-V13 | — | — | — |
| MS7-V15 | MS7-V14 | — | MS7-R15 | — |
| MS7-V16 | MS7-V15 | — | — | — |
| MS7-V17 | MS7-V16 | — | — | — |
| MS7-V18 | MS7-V17 | — | — | — |
| MS7-I02 | MS6-I01 | MS7-R02A | — | — |
| MS7-I03 | MS7-I02 | — | — | MS7-V02 |
| MS7-I04 | MS7-I02 | — | — | MS7-V04 |
| MS7-I05 | MS7-I04 | — | — | MS7-V05 |
| MS7-I06 | MS7-I05 | — | — | MS7-V05 |
| MS7-I07 | MS7-I04 | — | — | MS7-V05 |
| MS7-I08 | MS7-I02 | MS7-R07 | — | MS7-R04A |
| MS7-I09 | MS7-I05, MS7-I06, MS7-I07 | — | — | MS7-V06 |
| MS7-I10 | MS7-I09 | — | — | MS7-V10, MS7-V09 |
| MS7-I11 | MS7-I03 | — | — | MS7-V08, MS7-V12 |
| MS7-I12 | MS7-I09 | MS7-R12 | — | MS7-V13 |
| MS7-I13 | MS7-I10 | MS7-R11 | — | MS7-V12 |
| MS7-I14 | MS7-I03, MS7-I11, MS7-I12, MS7-I13 | — | — | MS7-V14 |
| MS7-I15 | MS7-I14 | — | MS7-R15 | — |
| MS7-I16 | MS7-I15 | — | — | — |
| MS7-I17 | MS7-I15 | — | — | MS7-V17 |
| MS7-I18 | MS7-I17, MS7-I16 | — | — | — |

Типы рёбер и полный набор52 строк независимо сверены с исходной таблицей v7.1 страниц79–85. Все SOFT guidance остаются рекомендацией; четыре blocking вида участвуют в DAG. Runtime handoff, frozen contracts и проверки §21 остаются обязательными.

---

## 26. Требования и прослеживаемость
Номера FR/NFR/AT сохранены; FR-25–29 явно POST-MVP. Ни одно обязательное требование не
закрывается только ссылкой на старое ТЗ. В реестрах ниже source P означает PROJECT DECISION из
настоящего ТЗ и frozen contracts; Cxx — course registry. Evidence E(task) — обязательный task bundle из
§21, с test report и final SHA; gate ledger ссылается на него. Для всех planned требований evidence ещё
предстоит получить. ID / требование
Source
Owner / tasks
Test / evidence
Gate
FR-01 Auth/profile
P; C-02/03/11 по scope
Владимир; MS7-V02, MS7-I03
AT-01; E(MS7-V02)
G3
FR-02 Три onboarding modes; чтение не прогресс
P; C-02/03/11 по scope
Владимир; MS7-V08, MS7-V12, MS7-I03
AT-02; E(MS7-V08)
G3
FR-03 Каталог и TopicSkill
P; C-02/03/11 по scope
Владимир; MS7-V03, MS7-I04
AT-12; E(MS7-V03)
G3
FR-04 PublicExerciseDTO
P; C-02/03/11 по scope
Руслан; MS7-R02A, MS7-V04
AT-03; E(MS7-R02A)
G3
FR-05 SELF_CHECK
P; C-02/03/11 по scope
Владимир; MS7-V05, MS7-I05
AT-03; E(MS7-V05)
G3
FR-06 FINAL_ANSWER
P; C-02/03/11 по scope
Руслан; MS7-R10, MS7-V10, MS7-I05
AT-04; E(MS7-R10)
G3
FR-07 STEP_BY_STEP
P; C-02/03/11 по scope
Руслан; MS7-R10, MS7-V05, MS7-I06
AT-04; E(MS7-R10)
G3
FR-08 Две STRUCTURED schemas
P; C-02/03/11 по scope
Владимир; MS7-V04, MS7-R10, MS7-I07
AT-05; E(MS7-V04)
G3
FR-09 Server-only secrets
P; C-02/03/11 по scope
Владимир; MS7-V04, MS7-V06, MS7-I09
AT-03; E(MS7-V04)
G3
FR-10 Безопасная математика
P; C-02/03/11 по scope
Руслан; MS7-R09, MS7-R10
AT-04; E(MS7-R09)
G3
FR-11 First proven error
P; C-02/03/11 по scope
Руслан; MS7-R10, MS7-V10
AT-04; E(MS7-R10)
G3
FR-12 Taxonomy/confidence/abstain
P; C-02/03/11 по scope
Руслан; MS7-R10, MS7-V11
AT-10; E(MS7-R10)
G3
FR-13 Skill evidence mapping
P; C-02/03/11 по scope
Руслан; MS7-R10, MS7-V08
AT-06; E(MS7-R10)
G3
FR-14 Evidence→Progress
P; C-02/03/11 по scope
Владимир; MS7-V08, MS7-V10
AT-06; E(MS7-V08)
G3
FR-15 Replay/idempotency
P; C-02/03/11 по scope
Владимир; MS7-V09
AT-07; E(MS7-V09)
G3
FR-16 DAG depth2
P; C-02/03/11 по scope
Владимир; MS7-V03, MS7-R11
AT-12; E(MS7-V03)
G3
FR-17 Tutor context
P; C-02/03/11 по scope
Руслан; MS7-R12, MS7-V13
AT-10; E(MS7-R12)
G3
FR-18 Hints/reveal/fallback
P; C-02/03/11 по scope
Владимир; MS7-V06, MS7-V13, MS7-I09
AT-03; E(MS7-V06)
G3
FR-19 Adaptive selection
P; C-02/03/11 по scope
Руслан; MS7-R11, MS7-V12
AT-11; E(MS7-R11)
G3
ID / требование
Source
Owner / tasks
Test / evidence
Gate
FR-20 Practice и возврат
P; C-02/03/11 по scope
Владимир; MS7-V12, MS7-I13
AT-11; E(MS7-V12)
G3
FR-21 History
P; C-02/03/11 по scope
Владимир; MS7-V05, MS7-I11
AT-06; E(MS7-V05)
G3
FR-22 Progress map/list
P; C-02/03/11 по scope
Владимир; MS7-V08, MS7-I10
AT-12; E(MS7-V08)
G3
FR-23 AIRun
P; C-02/03/11 по scope
Владимир; MS7-V11
AT-10; E(MS7-V11)
G3
FR-24 Public HTTPS
P; C-02/03/11 по scope
Владимир; MS7-V17, MS7-I17
AT-16; E(MS7-V17)
G4
FR-25 Вся математика
P, POST-MVP
TBD после отдельного ADR
N/A для MVP; не orphan mandatory
после MVP
FR-26 Geometry canvas
P, POST-MVP
TBD после отдельного ADR
N/A для MVP; не orphan mandatory
после MVP
FR-27 OCR
P, POST-MVP
TBD после отдельного ADR
N/A для MVP; не orphan mandatory
после MVP
FR-28 Полный RAG
P, POST-MVP
TBD после отдельного ADR
N/A для MVP; не orphan mandatory
после MVP
FR-29 Teacher/parent roles
P, POST-MVP
TBD после отдельного ADR
N/A для MVP; не orphan mandatory
после MVP
NFR-01 Модульный монолит
P, §§5–16
Руслан; MS7-R13
Scope/failure tests карточки; E(MS7-R13)
G2
NFR-02 LLM не создаёт неподтверждённый штраф
P, §§5–16
Руслан; MS7-R14
Scope/failure tests карточки; E(MS7-R14)
G4
NFR-03 Replay воспроизводим
P, §§5–16
Владимир; MS7-V09
Scope/failure tests карточки; E(MS7-V09)
G2
NFR-04 Нет утечки answers
P, §§5–16
Руслан; MS7-R15
Scope/failure tests карточки; E(MS7-R15)
G4
NFR-05 Auth/CSRF/ownership/rates
P, §§5–16
Владимир; MS7-V15
Scope/failure tests карточки; E(MS7-V15)
G4
NFR-06 Synthetic/privacy/redaction
P, §§5–16
Руслан; MS7-R15
Scope/failure tests карточки; E(MS7-R15)
G4
NFR-07 p95 500ms/15s
P, §§5–16
Владимир; MS7-V15
Scope/failure tests карточки; E(MS7-V15)
G4
NFR-08 Offline CI
P, §§5–16
Руслан; MS7-R08
Scope/failure tests карточки; E(MS7-R08)
G1
NFR-09 Correlation/observability
P, §§5–16
Владимир; MS7-V11
Scope/failure tests карточки; E(MS7-V11)
G3
NFR-10 Migrations fresh/upgrade
P, §§5–16
Владимир; MS7-V16
Scope/failure tests карточки; E(MS7-V16)
G4
NFR-11 Воспроизводимая среда
P, §§5–16
Владимир; MS7-V14
Scope/failure tests карточки; E(MS7-V14)
G3
NFR-12 Repo cold start
P, §§5–16
Руслан; MS7-R05
Scope/failure tests карточки; E(MS7-R05)
G1
NFR-13 Browser/mobile
P, §§5–16
Илья; MS7-I15
Scope/failure tests карточки; E(MS7-I15)
G4
NFR-14 Registry schemas
P, §§5–16
Руслан; MS7-R10
Scope/failure tests карточки; E(MS7-R10)
G2
NFR-15 Raw отдельно
P, §§5–16
Руслан; MS7-R09
Scope/failure tests карточки; E(MS7-R09)
G2
NFR-16 Keyboard/a11y
P, §§5–16
Илья; MS7-I15
Scope/failure tests карточки; E(MS7-I15)
G4
NFR-17 Atomic/recovery
P, §§5–16
Владимир; MS7-V10
Scope/failure tests карточки; E(MS7-V10)
G2
NFR-18 Version/provenance
P, §§5–16
Владимир; MS7-V04
Scope/failure tests карточки; E(MS7-V04)
G2
NFR-19 Harness enforcement/budgets
P, §§5–16
Руслан; MS7-R08
Scope/failure tests карточки; E(MS7-R08)
G1
NFR-20 Visual artifacts без PII
P, §§5–16
Илья; MS7-I08
Scope/failure tests карточки; E(MS7-I08)
G1
NFR-12 authoritative cold-start route:
1. fresh git clone публичного MathStart-Python;
2. checkout pinned release/task SHA;
3. установка документированной версии Python и dependency lock в
чистой среде;
4. только документированные non-secret environment values;
credentials остаются вне repo;
5. doctor/runtime report;
6. canonical repository verification;
7. cold-start Harness run по repo instructions без прежней переписки;
8. сохранение run/context/tool/verification evidence;
9. проверка contract/digest/version consistency.
Source-only ZIP допустим только как audit snapshot и не является достаточным evidence для Git-aware
Harness reproducibility, поскольку не содержит полного Git metadata.

---

## 27. Сквозные acceptance routes
AT-01. Другой пользователь/CSRF/login:401/403/404, ноль чужих данных. Владелец: Илья. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-02. Zero0/0/selfreport60/15 один раз; чтение не пишет. Владелец: Владимир. Evidence:
expected/actual
assertions, SHA, commands/browser versions и gate ledger; провал блокирует соответствующий G2/G3/G4.
AT-03. Leaks HTML/JSON/JS/network; hint/reveal+submit race и cross-attempt eligibility. Владелец:
Владимир. Evidence: expected/actual assertions, SHA, commands/browser versions и gate ledger; провал
блокирует соответствующий G2/G3/G4.
AT-04. Equivalent rational, first proven error, cascade/unsupported gap. Владелец: Руслан. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-05. Две structured schemas: valid/invalid/unknown/reorder. Владелец: Илья. Evidence:
expected/actual
assertions, SHA, commands/browser versions и gate ledger; провал блокирует соответствующий G2/G3/G4.
AT-06. Retry/crash/repeated positive: exactly-once persisted evidence. Владелец: Владимир. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-07. Late events/facts, same timestamps, online/replay equality. Владелец: Владимир. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-08. Neutral completions вытесняют independent из 10, числа не меняются. Владелец: Руслан.
Evidence: expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-09. Diagnostic10/skip/help/reveal, no fake independent. Владелец: Владимир. Evidence:
expected/actual
assertions, SHA, commands/browser versions и gate ledger; провал блокирует соответствующий G2/G3/G4.
AT-10. Malformed/low confidence/injection/provider outage: abstain/fallback. Владелец: Руслан.
Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-11. Adaptive depth2/max7/no-candidate/repeat/return. Владелец: Илья. Evidence: expected/actual
assertions, SHA, commands/browser versions и gate ledger; провал блокирует соответствующий G2/G3/G4.
AT-12. Topic PRIMARY denominator, external basic_arithmetic, accessible graph. Владелец: Илья.
Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-13. Harness real tool deny/overflow/resume/child/deadline/receipt. Владелец: Руслан. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-14. IDOR/CSRF/XSS/rates/redaction/secrets. Владелец: Владимир. Evidence: expected/actual
assertions,
SHA, commands/browser versions и gate ledger; провал блокирует соответствующий G2/G3/G4.
AT-15. Clean install/upgrade/backup restore, source preservation. Владелец: Владимир. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-16. Public full loop, four modes, Product live+fallback и three-owner Harness evidence. Владелец:
Илья.
Evidence: expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.

---

## 28. Course compliance registry
ID / формулировка
Классификация
Source/time/scop e
Ответственный/task/evidence/g ate
C-01 Agentic development
MANDATORY COURSE REQUIREMENT
L1 00:17–02:06; L3 00:43.513– 04:11.904; общее
Руслан, MS7-R08; E(MS7-R08) и report/demo; G1
C-02 Сложная задача и значимый прогресс
MANDATORY COURSE REQUIREMENT
L1 00:17–02:06; L3 00:43.513– 04:11.904; общее
Руслан, MS7-R17; E(MS7-R17) и report/demo; G4
C-03 Готовая LLM внутри программной обвязки
MANDATORY COURSE REQUIREMENT
L1 20:23–21:10; общее
Владимир, MS7-V11; E(MS7-V11) и report/demo; G3
C-04 Публичный GitHub в регистрации
MANDATORY COURSE REQUIREMENT
L1 04:46–05:38; L2 00:15–00:52; общее
Руслан, MS7-ORG01; LMS receipt/meeting record; 09.10
C-05 Показывать продвижение с голосом/экраном
MANDATORY COURSE REQUIREMENT
L1 02:14–02:56; L3 00:43.513– 04:11.904; общее; SRT сегмент широкий
Руслан, MS7-R17; E(MS7-R17) и report/demo; G4
C-06 Описание задачи/стека/архитектуры в отчёте
MANDATORY COURSE REQUIREMENT
L1 09:42–11:34; общее
Руслан, MS7-R16; E(MS7-R16) и report/demo; G5
C-07 DB желательно 3NF
TEACHER RECOMMENDATIO N
L1 09:42–11:34; общее, рекомендация
Владимир, MS7-V03; E(MS7-V03) и report/demo; G2
C-08 Глава о настройке Harness
MANDATORY COURSE REQUIREMENT
L1 11:55–13:01; L2 03:39–04:12; общее
Руслан, MS7-R16; E(MS7-R16) и report/demo; G5
C-09 Trace excerpt в отчёте
TEACHER RECOMMENDATIO N
L1 12:05–12:14; разрешённый способ иллюстрации
Руслан, MS7-R16; E(MS7-R16) и report/demo; G5
C-10 Анализ неудач агента
TEACHER RECOMMENDATIO N
L2 17:59–18:45; совет другой команде; принят проектом
Руслан, MS7-R16; E(MS7-R16) и report/demo; G5
C-11 Внешняя работающая browser система
MANDATORY COURSE REQUIREMENT
L1 15:39–16:37; общее
Владимир, MS7-V17; E(MS7-V17) и report/demo; G4
C-12 Записка ориентировочно 45–60 стр
MANDATORY COURSE REQUIREMENT
L1 13:18–13:52; отчёт, не ТЗ; точное оформление TBD
Руслан, MS7-R18; E(MS7-R18) и report/demo; G5
C-13 Высокая траектория по обсуждениям курса
MANDATORY COURSE REQUIREMENT
L1 19:28– 19:51;25:27– 25:38; для выбранной высокой траектории
Руслан, MS7-R18; E(MS7-R18) и report/demo; G5
C-14 Командный состав обычно до 3
MANDATORY COURSE REQUIREMENT
L1 19:15–19:25;L2 02:53–03:06; межгрупповая команда допустима
Руслан, MS7-ORG01; LMS receipt/meeting record; 09.10
C-15 Финальная защита в зачётную неделю
MANDATORY COURSE REQUIREMENT
L3 32:41–32:58; дата TBD
Руслан, MS7-R18; E(MS7-R18) и report/demo; G5
C-16 Регистрация до 9 октября включительно
MANDATORY COURSE REQUIREMENT
L2 02:16–02:29;L3 31:58–32:12; не deadline защиты
Руслан, MS7-ORG01; LMS receipt/meeting record; 09.10
C-17 Ранняя сдача разрешена
OPTIONAL ENHANCEMENT
L3 33:00.133– 33:14.358; вопрос нашей команды по user context
Руслан, MS7-R18; E(MS7-R18) и report/demo; G5
Не являются course requirements: время встречи 08.10 — оперативный checkpoint MS7-ORG01; советы,
данные другой команде, — contextual material; выбор конкретных сторонних инструментов не является
mandate MathStart.
Внедрение собственного controlled Harness, numeric eval/limits и repo trace — PROJECT DECISION; их
требования перечислены в D-024/026/027 и NFR. Course→FR/NFR: C-01/08/09/10→NFR-12/19/20;
C-02/03→FR-01–23; C-04/05/06/12/13/14/15/16/17→workflow/report/ORG01; C-07→NFR-01/10;
C-11→FR-24/NFR-11/13. Рекомендации остаются рекомендациями даже когда команда принимает их
реализацию.

---

## 29. Пояснительная записка и демонстрация
Записка создаётся по итогам реализации, а не выдаёт это ТЗ за готовый отчёт. Глава 1: предметная
область, аналоги, сценарии, цели и границы (Илья/R16 review). Глава 2: стек, архитектура, ER, ownership,
state machines, algorithms/API (Руслан/Владимир). Глава 3: собственный Harness,
context/tools/policy/sandbox/skills/subagents, три real runs, реальные review failures и corrections (Руслан,
вклад всех). Глава 4: реализация, screenshots, tests/evals/performance/deployment, результаты и
ограничения (Владимир/Илья). Введение/заключение/библиография/приложения; формат кафедры TBD,
ориентир 45–60 страниц. Обязательные схемы отчёта: system context; domain dependency graph; ER
PK/FK; submit/finalize transaction; help/reveal race; progress replay/neutral completion; adaptive return;
Harness tool decision flow. Они выводятся из accepted contracts. Приложения — короткая redacted trace,
commands/eval summary, не полный листинг repo. Screenshot содержит release SHA/date/browser version
в evidence caption, без student PII. Основной demo5–7min — план команды, длительность согласуется:
login→тема→пошаговое решение→first proven error→hint→practice prerequisite→возврат→history/progress.
Второй маршрут показывает independent success и затем reveal без переписывания прошлого. Короткий
Harness run демонстрирует allowed patch/check, denied action и verified review bundle. Каждый участник
объясняет свой scope, модель не отвечает за него на защите. При provider outage показывается
настоящий fallback. Видео — резервная иллюстрация, не замена public browser service.

---

## 30. Риски, TBD и freeze
Риск/TBD
Владелец и срок решения
Правило до решения
LMS status, группы, согласование MathStart
Руслан, до 07–09.10
Не утверждать, что проект зарегистрирован/одобрен
Дата зачётной недели и early slot
Руслан, на 08.10 и перед G5
Forecast не объявлять deadline преподавателя
Provider/model/ключи/денежный cap
Руслан+Владимир, до R04A/V11 live
Только fake/offline; gate live остаётся pending
Host/domain/region/production runtime
Владимир, до V14
Dev Compose не считается deployment
Полная HTTP/eligibility спецификация
R02A, до V02/V05 client code
Работать только по accepted fixtures
CompletionFact change
R03A, до V08/V09
Не изменять старый reducer незаметно
Windows sandbox ограничения
R06B, до G1
Advisory label, не enforcement claim
Нагрузка одного Руслана и review bottleneck
Все, каждую неделю
Перераспределение загрузки и расход резерва относительно внутреннего target 18.12; no skipped gates
Неполный lock в локальной venv
Владимир, до runtime acceptance
Использовать verified CI/clean environment, не считать local SQLite PG proof
Риск/TBD
Владелец и срок решения
Правило до решения
Ветка main без protection
HK01/R15, отдельное human разрешение
Green CI/review вручную обязательны
Limited pilot coverage / pedagogical claims
R14/I16, G4
Публиковать denominators и ограничения, не обещать эффективность обучения
Freeze G5: immutable release SHA/tag, final report PDF, spec/ADR versions, dependency lock,
migrations/backup restore runbook, public URL, credential transfer вне repo, evidence index, known limits,
responsible contacts. Никаких новых feature merges после freeze без defect triage и повторения
затронутой acceptance. Active plans перемещаются в completed только после recorded human acceptance.
Разработчик следующего этапа получает repo+v7.1+gate evidence, не обязан искать прежние чаты.

---

## 31. Историческая миграция v6→v7.1 и переход v7.2

### 31.1. История v7.1 (не текущее требование Django)
PRESERVED: modular Django, PostgreSQL target/explicit SQLite compatibility, file-managed content, four
modes, deterministic-first, graph/progress baseline, controlled Product AI, bounded pilot, public deployment,
three-person ownership, evidence workflow, D-021–026 как proposals. CORRECTED: R02 не полный HTTP
implementation; R03 не CompletionFact persistence; R04 READY receipt сильнее исходной карточки; I01 не
frontend runtime; V01 verified PG CI отдельно от local SQLite; 09.10 регистрация; late lecture advice
контекстный; actual skill graph из fixture; Topic=ContentPage; old status cleanup не reopening. SUPERSEDED:
календарь 18 одинаковых окон v6; implicit same-index synchronization; generic «нет pending acceptance
значит всё закрыто»; будущее перечисление already merged задач. NEW: R02A/R03A/R04A, splitR06A/B,
HK01/ORG01, typed dependency matrix, G1 live capability proof, календарные target windows, full early
readiness, explicit unknowns и failure history. REMOVED: ложное требование заново выполнить frozen work;
смешение mocked tool loop с live coding agent; интерпретация советов другой команде как
универсального требования преподавателя; неявная нормативная зависимость от конкретных внешних
context/memory tools. Корректные product requirements и safety checks не удаляются. Старое planned
обозначение
Новое
Статус / причина
R01 / MS6 alias
R01
FROZEN; не переоткрывается
R02 / MS6 alias
R02 + отдельная MS7-R02A
R02 остаётся FROZEN; MS7-R02A — PLANNED follow-up (HTTP/eligibility), не reopening
R03 / MS6 alias
R03 + отдельная MS7-R03A
R03 остаётся FROZEN; MS7-R03A — PLANNED follow-up (CompletionFact), не reopening
R04 / MS6 alias
MS6-R04 + отдельная MS7-R04A
MS6-R04 остаётся FROZEN; MS7-R04A — PLANNED follow-up (live adapter), не reopening
MS6-R05
MS7-R05
PLANNED; rebase dependencies и acceptance
MS6-R06
MS7-R06A + MS7-R06B
SPLIT PLANNED TASK до реализации: Policy/Hooks/Machine Trace и Physical Sandbox; не follow-up к frozen
R06
MS6-R07
MS7-R07
PLANNED; rebase dependencies и acceptance
MS6-R08
MS7-R08
PLANNED; rebase dependencies и acceptance
MS6-R09
MS7-R09
PLANNED; rebase dependencies и acceptance
MS6-R10
MS7-R10
PLANNED; rebase dependencies и acceptance
MS6-R11
MS7-R11
PLANNED; rebase dependencies и acceptance
MS6-R12
MS7-R12
PLANNED; rebase dependencies и acceptance
Старое planned обозначение
Новое
Статус / причина
MS6-R13
MS7-R13
PLANNED; rebase dependencies и acceptance
MS6-R14
MS7-R14
PLANNED; rebase dependencies и acceptance
MS6-R15
MS7-R15
PLANNED; rebase dependencies и acceptance
MS6-R16
MS7-R16
PLANNED; rebase dependencies и acceptance
MS6-R17
MS7-R17
PLANNED; rebase dependencies и acceptance
MS6-R18
MS7-R18
PLANNED; rebase dependencies и acceptance
V01 / MS6 alias
MS6-V01
FROZEN; не переоткрывается
MS6-V02
MS7-V02
PLANNED; rebase dependencies и acceptance
MS6-V03
MS7-V03
PLANNED; rebase dependencies и acceptance
MS6-V04
MS7-V04
PLANNED; rebase dependencies и acceptance
MS6-V05
MS7-V05
PLANNED; rebase dependencies и acceptance
MS6-V06
MS7-V06
PLANNED; rebase dependencies и acceptance
MS6-V07
MS7-V07
PLANNED; rebase dependencies и acceptance
MS6-V08
MS7-V08
PLANNED; rebase dependencies и acceptance
MS6-V09
MS7-V09
PLANNED; rebase dependencies и acceptance
MS6-V10
MS7-V10
PLANNED; rebase dependencies и acceptance
MS6-V11
MS7-V11
PLANNED; rebase dependencies и acceptance
MS6-V12
MS7-V12
PLANNED; rebase dependencies и acceptance
MS6-V13
MS7-V13
PLANNED; rebase dependencies и acceptance
MS6-V14
MS7-V14
PLANNED; rebase dependencies и acceptance
MS6-V15
MS7-V15
PLANNED; rebase dependencies и acceptance
MS6-V16
MS7-V16
PLANNED; rebase dependencies и acceptance
MS6-V17
MS7-V17
PLANNED; rebase dependencies и acceptance
MS6-V18
MS7-V18
PLANNED; rebase dependencies и acceptance
I01 / MS6 alias
MS6-I01
FROZEN; не переоткрывается
MS6-I02
MS7-I02
PLANNED; rebase dependencies и acceptance
MS6-I03
MS7-I03
PLANNED; rebase dependencies и acceptance
MS6-I04
MS7-I04
PLANNED; rebase dependencies и acceptance
MS6-I05
MS7-I05
PLANNED; rebase dependencies и acceptance
MS6-I06
MS7-I06
PLANNED; rebase dependencies и acceptance
MS6-I07
MS7-I07
PLANNED; rebase dependencies и acceptance
Старое planned обозначение
Новое
Статус / причина
MS6-I08
MS7-I08
PLANNED; rebase dependencies и acceptance
MS6-I09
MS7-I09
PLANNED; rebase dependencies и acceptance
MS6-I10
MS7-I10
PLANNED; rebase dependencies и acceptance
MS6-I11
MS7-I11
PLANNED; rebase dependencies и acceptance
MS6-I12
MS7-I12
PLANNED; rebase dependencies и acceptance
MS6-I13
MS7-I13
PLANNED; rebase dependencies и acceptance
MS6-I14
MS7-I14
PLANNED; rebase dependencies и acceptance
MS6-I15
MS7-I15
PLANNED; rebase dependencies и acceptance
MS6-I16
MS7-I16
PLANNED; rebase dependencies и acceptance
MS6-I17
MS7-I17
PLANNED; rebase dependencies и acceptance
MS6-I18
MS7-I18
PLANNED; rebase dependencies и acceptance
MS7-R02A/R03A — новые addenda, MS7-R04A — отдельный live adapter; MS7-HK01 — stale records/branch
protection proposal (Руслан, Reviewer/Task Approver Владимир, target до 09.10); MS7-ORG01 — LMS/meeting
scheduling (Руслан, проверяют все, course deadline09.10). Они не переименовывают historical work.
Внешние context/memory tools могут оцениваться отдельными техническими исследованиями и не
входят в mandatory scope без отдельного human decision/ADR.

### 31.2. Платформа v7.2

Принятый ADR-0006 и R02 migration package заменяют только framework/frontend/ORM/migrations/auth/deployment adapters. Все domain/evidence/security invariants, four modes, source IDs, graph10/13, exact Decimal/replay и будущие Product AI требования сохраняются. Source hashes,13 historical adaptation rows и52 product dispositions связывают старый результат с новым evidence; новая компиляция не становится старым approval.


---

## 32. Источники и статус утверждения

Полный source v7.1: Git3a290a46d991e22269a17dde41e39f0637576071:docs/specifications/sources/technical-spec-v7.1.pdf, SHA256 e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd. Canonical migration ТЗ: ../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md, SHA256 c5a554e3911bdb43db28d67fd02d26e38d50b2820e1154a272d89ecb44b1faae. Accepted ADR-0006/R02 определяют платформу. Итоги принятых PR54/PR55 и адаптации платформы v7.2 приведены в [maintenance](../maintenance.md); завершённые execution overlays не задают новую работу. v7.2 approval: HUMAN_PENDING; Product G1–G5 не закрыты.

### Исторические источники и G0 v7.1

Весь остаток этой главы — исторический снимок v7.1. Его календарь, очереди по людям, READY/BLOCKED и G0 approvals не являются действующими поручениями, текущими статусами migration или новыми назначениями. Новую работу определяет текущее поручение пользователя; future product cards сохранены как требования, не как реализованные функции.

Основные pinned sources: main fc4e907149da026e4710c3e453d8065c0106e4b9: AGENTS.md, PRODUCT.md,
ARCHITECTURE.md, ADR-0001/0002/0003, specs/exercises/R02-exercise-architecture.md,
specs/knowledge/R03-knowledge-graph.md, specs/progress/R03-progress-contract.md, BASELINE-v1.md,
adapter-protocol-v1.md, docs/ux/MS6-I01-states-matrix.md, harness/contracts/publication.py,
harness/runner/engine.py, tests/harness/test_ready_publication.py, .github/workflows/ci.yml. Исходники
доступны по https://github.com/Tramsey00/MathStart-Python/blob/<SHA>/<path>. GitHub history:
https://github.com/Tramsey00/MathStart-Python/pull/2 ; /pull/5 ; /pull/7 ; /pull/8 ; /pull/10 ; /pull/11 ; /pull/14.
Main CI: https://github.com/Tramsey00/MathStart-Python/actions/runs/36449820246 . R04 final CI:
https://github.com/Tramsey00/MathStart-Python/actions/runs/36357233039. В ходе исследования изучались
внешние учебные примеры Harness; они ненормативны. Архитектура MathStart определяется этим ТЗ,
accepted ADR/specs и merged repository state. Course sources L1/L2/L3 с точными интервалами
перечислены в §28; TXT/SRT L2 — один источник, не два подтверждения. Audit history сохраняется
отдельно от canonical specification. Внешние context/memory tools оцениваются отдельными
техническими исследованиями и не входят в mandatory scope без отдельного human decision/ADR. G0
approval: Руслан — APPROVED 30.09.2026; Владимир — APPROVED 30.09.2026; Илья — APPROVED
30.09.2026. ACTUAL G0 DATE: 30.09.2026. Audited main snapshot:
fc4e907149da026e4710c3e453d8065c0106e4b9. Actual main SHA на момент approval —
fc4e907149da026e4710c3e453d8065c0106e4b9. Acceptance record: G0-2026-09-30.md. G0 ACCEPTED v7.1 —
canonical normative baseline; это не означает completion future tasks, G1+ или approval преподавателем
каждого внутреннего project decision.
G0 CONSOLIDATION CHECKLIST
 B1–B4 physically applied in the canonical text.
 M1–M4 physically applied in the canonical text.
 Actual main SHA rechecked at approval: fc4e907149da026e4710c3e453d8065c0106e4b9.
 Руслан — APPROVED 30.09.2026.
 Владимир — APPROVED 30.09.2026.
 Илья — APPROVED 30.09.2026.
 ACTUAL G0 DATE: 30.09.2026.
 Candidate PDF SHA-256 is recorded in G0-2026-09-30.md.
 MS7-ORG01 registration evidence due 09.10.2026 is handled separately.
 Current lifecycle statuses are managed through GitHub Issues/PR and accepted exec plans.
G0 EXECUTION SNAPSHOT — 30.09.2026
Current / Next Task
Owner
Reviewer / Approver
Blocking dependency
Target window
Milestone
Status
Architecture / Harness
MS7-R02A
Исторический снимок ближайшей очереди на 30.09.2026; G0 ACCEPTED 30.09.2026. Этот раздел не является вечным
source of truth. После изменения task lifecycle authoritative status определяется GitHub Issues/PR и accepted exec plans.
Таблица не заменяет canonical task cards §§22–24 и организационную запись §20/31. N = NORMAL, E = EARLY; все даты
— 2026. Future Target window в таблице пересчитан от 01.10.2026 по тем же durations, но остаётся планом, а не
evidence фактического старта; lifecycle/status в snapshot остаётся историческим на 30.09.2026.
Руслан
Владимир
G0 accepted 30.09.2026; frozen R02 принят
N/E 01–02.10
pre-G1 contract
READY
Backend
MS7-V02
Владимир
Руслан
G0 и accepted R02A; MS6-V01 frozen
G3 track
BLOCKED
Frontend
MS7-I02
Илья
Руслан; Владимир — schema compatibility
G0 и accepted R02A; MS6-I01 frozen
G3 track
BLOCKED
Organization
MS7-ORG01
Руслан
Проверяют все трое
Начало сбора сведений не блокировано; для DONE нужен LMS receipt
Course checkpoint
READY
Допустимые статусы: FROZEN, READY, BLOCKED, ACTIVE, IN REVIEW, DONE. ACTIVE ставится только по
evidence фактического старта; наступление target date его не создаёт. READY у ORG01 означает
готовность начать организационную подготовку, не подтверждение начала или регистрации. После G0 и
снятия blockers ответственный обновляет board по фактам; завершённый frozen baseline остаётся в §2.
Следующая очередь Руслана после R02A: R03A, затем R05 (§20); новые task IDs не создаются.
v7.1 CONSOLIDATION STATUS
Task ID Naming Convention, различие frozen-task follow-up и planned-task split, Relation в неоднозначных
карточках, typed dependencies, Gates и task-card semantics сохранены без смыслового изменения.
Нормативные G0 corrections физически применены в основном тексте; отменённые формулировки не
являются частью этой спецификации. G0 ACCEPTED 30.09.2026; approvals зафиксированы в G0-2026-09-
30.md. Audit/changelog history хранится отдельно и не требуется для правильной интерпретации v7.1.
N 01–04.10; E 01–03.10
N 01–04.10; E 01–03.10
Start 01.10; сбор до 07.10; checkpoint 08.10; receipt до 09.10
