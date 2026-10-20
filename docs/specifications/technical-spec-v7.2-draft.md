# MathStart — техническое задание v7.2 (полная рабочая редакция)

20.10.2026, Europe/Moscow. **DRAFT_HUMAN_PENDING**. Существующий сайт перенесён
и принят (PR54/55); future product requirements не реализованы автоматически.
Редакция обновляет весь действующий scope после dependency audit Harness.
Она не разрешает выполнение новой очереди или production changes.

## 1. Паспорт и правила применения

Полная рабочая редакция **v7.2 от 20.10.2026, Europe/Moscow**; статус
**DRAFT_HUMAN_PENDING**. Миграция существующего сайта и адаптация платформы
приняты в PR54, консолидация PR55 завершена. Эта редакция не объявляется принятой
пользователем; G0/approvals v7.1 относятся только к прежним документам/SHA.
Новые сроки и согласование преподавателя не выдумываются.

Канонические источники: PRODUCT.md (поведение), ARCHITECTURE.md (структура/стек),
AGENTS.md (процесс), это полное ТЗ (требования), [единая очередь](../tasks/INDEX.md)
и её task skills (подробные задания). Прежнее ТЗ v7.1 и полная предыдущая редакция
доступны в Git. [Provenance](technical-spec-v7.2-provenance.md) сохраняет hashes,
историю сверки и границы изменения scope.

Изменения: сохранены учебные/domain/API/security/ops требования; исправлены
текущая платформа, документация и процесс; добавлены редизайн/дизайн-система и
проектирование геймификации; сняты собственный Engineering Harness, его adapter/
sandbox/orchestration/subagent/eval/real-owner-run обязательства. Один Codex
последовательно выполняет одно поручение в отдельной ветке, затем самопроверка,
PR, отдельное ревью, исправления и человеческая приёмка. Следующее задание
автоматически не начинается. Персональные роли и даты старых карточек — история.

## 2. Проверенное состояние и принятая история

Аудит начат на main `1a015f7513933901e8bb252e94c660e4383b6b0e`, после fetch он совпал с origin/main;
рабочее дерево было чистым. Изменения выполняются в `docs-and-workflow-cleanup`.
Полный инвентарь документов, evidence, ограничения среды и карта вывода
подсистемы — в [аудите](../audits/docs-and-workflow-cleanup.md).

Реализованы FastAPI/Pydantic HTTP, SQLAlchemy/Alembic persistence и retained
PostgreSQL schema/history, Content publication authority/CLI, identity/profile/
onboarding, opaque sessions/receipts, staff permissions/mutations, React/SSG,
полные public HTML и owned install/recovery/combined проверки. Onboarding хранит
выбор, а не исполняет будущую диагностику. Legacy self-check не является assessed API.

Будущие Knowledge/Assessment/Progress persistence, Analyzer/Tutor/Adaptive и
Product LLM не реализованы. R02/R03/R02A/R03A schemas/reference/tests описывают
контракты; наличие теста не доказывает работающий intelligent runtime.

PR54 merged `3a290a46d991e22269a17dde41e39f0637576071`, PR55 merged
`12450dfd39b51166aa5a40955ce78e40169a1cb4`: [maintenance](../maintenance.md)
сохраняет точные approvals/CI. R01/R02/R03/MS6-R04/MS6-V01/MS6-I01 остаются
завершённой историей, MS6-R04 после этого выведен из текущего runtime.
Ошибки и исправления R04 сохраняются как case study (§18), не как необходимость
строить новый sandbox. [Прежний baseline и численные результаты](https://github.com/Tramsey00/MathStart-Python/blob/1a015f7513933901e8bb252e94c660e4383b6b0e/docs/specifications/technical-spec-v7.2-draft.md#2-проверенное-состояние-и-frozen-baseline)
не являются readiness нового candidate.

## 3. Цель, пользователи и границы продукта
Ученик читает тему, решает задачу одним из четырёх способов, получает проверяемую обратную связь,
безопасную помощь и практику на нужный prerequisite. Система хранит причины изменения прогресса,
а не только итоговый процент. Успех MVP — воспроизводимый полный путь на публичном HTTPS URL, а
не наличие чата или рост mastery от открытия страницы.
CORE MVP: сохранить каталог и публикацию, auth/profile/onboarding, доступный browser UI, версия
контента, история, безопасность, deployment, backup/restore. INTELLIGENT PILOT: три темы
(отрицательные числа; распределительное свойство/скобки; линейные уравнения со скобками), 10
skills/13 edges, 40 assessed exercises и минимум 3 SELF_CHECK, Analyzer, Progress, diagnostics/adaptive
practice, Tutor. В 40 assessed exercises должно быть ≥4 PRIMARY упражнения на каждый skill,
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


Новые направления: полный редизайн, дизайн-система, отдельно проектируемая
геймификация и последовательная разработка одним исполнителем. Их реализация
не входит в текущее поручение. Конкретные дизайн/библиотеки/игровые механики
не утверждены; порядок получения решений — §§12–14 и единый реестр.

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
D-026/D-027 — REMOVED_FROM_PLAN: собственный Harness и live coding adapter
сняты по решению пользователя после dependency audit. Не являются продуктовыми gates.
D-028 — адаптировано: исторические typed edges сохранены как provenance;
новая последовательная очередь имеет собственные зависимости без Harness.
Номера D-001–020 не реконструируются по памяти: в переданном v6 нет полного нумерованного
реестра. Их содержательные базовые решения закреплены указанными ADR и настоящими разделами;
вымышленных соответствий ADR не вводится. Два AI-контура разделены. Product AI (Analyzer/Tutor)
видит минимальный учебный контекст, имеет отдельные credentials/budgets/AIRun и не выполняет tools
ОС. Engineering AI — реально используемый Codex, который видит разрешённый checkout,
следует AGENTS/task skill и сохраняет проверяемый execution/review record. Ключи двух контуров, prod DB и student logs не передаются друг другу. Доверенные: reviewed
contracts, publisher, deterministic validator, domain services. Недоверенные: ответы ученика, содержимое
исходников для coding agent, LLM response, external tool output, внешние сообщения. Schema validation
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

## 12. Полный редизайн и выбор направления

Редизайн согласован как направление. Старое migration-only ограничение внешнего
вида завершено; его исходный текст сохранён в историческом migration input.
Не выбраны палитра, шрифты, mascot или компонентная библиотека.
[Бриф](../ux/redesign-brief.md) покрывает существующие screens/scenarios,
пригодность I01, navigation/reading/exercise/feedback, mobile, long content,
formulas/graphs, keyboard/focus/contrast/reduced motion и все failure/empty/AI states.

MS-N001 сначала подтверждает source audit на реальном сайте и готовит **три
различимых направления**, каждое на одинаковых теме, решении упражнения и
прогрессе, с desktop/mobile и одними состояниями. Будущие exercise/progress
экраны помечаются prototype. Сравнить язык, аудиторию, учебное удобство,
реализацию/сопровождение и геймификацию. Выбор пользователя — отдельный receipt.
Никакой вариант не объявляется принятым без него.

## 13. Дизайн-система, библиотеки и внедрение

После выбора направления MS-N002 сравнивает libraries с фактическими React/
TypeScript/React Router SSG: prerender/hydration, accessibility, license,
math/graphs, themes/tokens, performance и support. Дополнительная библиотека
допустима при доказанной пользе; обновление ради новизны не цель.

MS-N003 внедряет принятую дизайн-систему, MS-N004 — pilot существующего
сценария, MS-N005 — rollout групп экранов. Сохранить authored content/formulas,
URLs/anchors/widgets, identity/permissions и public authority. Semantic tests
сохраняются, visual references меняются только под явно принятый дизайн.
Новые assessed screens появляются вместе с domain runtime в MS-N014–018.
После внедрения принятого stack обновляется ARCHITECTURE.md.

## 14. Геймификация как отдельное проектирование

XP, уровни, достижения, streaks, задания дня, персонаж и награды — кандидаты
для обсуждения, не утверждённый обязательный набор. MS-N006 определяет
педагогическую цель, действия/начисления/лимиты, retries/hints/reveals,
защиту от повторов, UI и accessibility; data owner/storage/events — отдельное
решение/ADR. До него нет реализованного reward domain или migration.

Игровой прогресс отделён от знаний. Чтение темы, посещения, XP и награды
не увеличивают mastery. Только валидированные ProgressEvent меняют knowledge
state. Спецификация обязана включать exactly-once source identity, timezone/
late events и privacy, positive/negative acceptance. MS-N020 реализует только
выбранные правила после готовности evidence runtime; без выбора BLOCKED_DECISION.

## 15. Verification, eval и наблюдаемость
Базовая команда — python scripts/verify_repo.py в configured environment. Продуктовые проверки сохраняются; 15 current registry checks и 5 pure suites
не заменяют отдельные install/recovery/combined jobs. Новые tests включаются в canonical verification/CI отдельными reviewed changes;
Ruff/mypy/pytest не объявляются настроенными без фактического добавления;
Playwright уже используется в текущем frontend. Для schemas
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
reveal explanation. Обычный CI offline: fake Product provider, deterministic/domain/API suites.
Live Analyzer/Tutor acceptance проводится отдельно после provider/budget решения
с redacted AIRun и fallback. Harness eval и три owner runs сняты с плана;
общие timeout/empty/failed/skipped/privacy checks продукта сохранены.

---

## 16. Security, privacy и эксплуатационные числа
Auth — независимый совместимый verifier encoded Django hashes, PostgreSQL opaque sessions, username/password; email optional до утверждения recovery. Plaintext passwords не
хранятся; login error одинаков для missing/wrong account. Без verified recovery channel самостоятельный
password reset не обещается. CSRF/session rotation, secure cookies, TLS, production-safe configuration, allowed hosts, least
privilege staff, owner-scoped queries. Другой owner получает 404. Rate limiting работает совместно между
workers через PostgreSQL counters/locks, не local-memory only. Default rates: login10/5min/IP;
submit30/min/user; reveal10/min/user; AI5/min/user и 50/day/user плюс global money cap. 429 Retry-After;
границы window/idempotent retries проверяются concurrency tests. Денежный лимит и provider approval
TBD до live, секреты только environment/secret store; логи маскируются до записи. Pilot использует
synthetic demo identities. AIRun и development execution records retention90days; attempts/messages до защиты+30days;
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
OD-12/13/14 — REMOVED_FROM_PLAN. Engineering Harness budgets/subagents сняты;
исходные числа сохранены в историческом source registry/Git, не действуют как
обязательные limits реально используемого Codex.
OD-15 / Analyzer eval §15
≥50:12correct/16errors/10ambiguous/6wrongfinal/6structured;≥20holdout;≥95%deterministic/
≥85%taxonomy;false strong=0 safety subset
Измерить качество на объявленных denominators
OD-16 / Tutor eval §15
≥20Tutor; live Product + fallback; обычный CI offline
Проверить продуктовую AI-интеграцию и воспроизводимость CI
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
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
ADR + versioned contract, parity/replay; G2
A HARD INVARIANT
OD-02
R02 + R02A schemas/services
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Contract addendum/ADR, regression; до клиентов/G2
A HARD INVARIANT
OD-03
Versioned pilot fixtures и bank import
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Изменение acceptance на human gate, graph contract при изменении codes/edges; G2/G3
B ACCEPTANCE REQUIREMENT
OD-04
Versioned parser profile и server schema limits в R09/R02A
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Approved config + worst-case tests; schema/security widening требует contract/ADR; G2
C CONFIGURABLE DEFAULT; effective caps enforced
OD-05
Isolated executor config
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Security review + timeout tests; G2
C CONFIGURABLE DEFAULT; finite process deadline обязателен
OD-06
Versioned Analyzer policy
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
ADR/contract + golden safety eval; G2/G4
B ACCEPTANCE REQUIREMENT; evidence validation A
OD-07
Versioned Context Builder config в V13
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Approved config + leak/fallback eval; G3
C CONFIGURABLE DEFAULT
OD-08
Provider policy/AIRun config в V11
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Approved config + safety/performance checks; G3/G4; bypass требует ADR
C CONFIGURABLE DEFAULT; превышать effective cap нельзя
OD-09
Versioned R11 policy и V12 fixtures
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Contract/ADR и replay/session fixtures; G3
A HARD INVARIANT для принятой policy version
OD-10
API config и frontend retry config
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Approved config + API/browser tests; изменение public schema требует R02A addendum
C CONFIGURABLE DEFAULT
OD-11
Receipt retention config/constraint
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Contract review для снижения минимума; G2
B ACCEPTANCE REQUIREMENT minimum; uniqueness A
OD-12/13/14: сняты с плана вместе с собственной engineering программой.
OD-15
Versioned golden set/eval acceptance
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Изменение acceptance — отдельное human решение с обоснованием; G4
B ACCEPTANCE REQUIREMENT
OD-16
Eval sets и gate evidence ledger
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
G3/G4; снижение product acceptance не config tweak
B ACCEPTANCE REQUIREMENT
ID
Where configured
Who may change
Gate/ADR required
Hard limit or default
OD-17
Shared PostgreSQL limiter/provider config
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Approved config + multiworker tests; G3/G4; 429/Retry-After contract сохраняется
C CONFIGURABLE DEFAULT
OD-18
Versioned retention/runbook config
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Privacy review, replay/backup safety; новые реальные minors требуют отдельного решения
C CONFIGURABLE DEFAULT; не разрешение удалить evidence
OD-19
Versioned load-test scenarios/acceptance
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
G4 human exception/acceptance change; samples не отбрасываются
B ACCEPTANCE REQUIREMENT
OD-20
Backup schedule/restore runbook в V16
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
RPO/RTO change через deployment review/G4, не молчаливый config change
B ACCEPTANCE REQUIREMENT дляRPO/RTO/daily
OD-21
CI/environment lock/browser matrix
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
Dependency/platform change по ADR/AGENTS; G3/G4
B ACCEPTANCE REQUIREMENT
OD-22
Accepted contracts + domain services
Исполнитель текущей задачи; отдельное ревью и решение пользователя по применимости
ADR/contract/security gate при изменении; G0–G4
A HARD INVARIANT

---

## 17. Последовательная разработка, ревью и gates

Порядок чтения и Git — AGENTS.md. Одно задание, одна ветка от проверенного
актуального main без `codex/`, один исполнитель. Существующие ветка/PR задания
продолжаются; main не редактируется. Force push/automatic merge запрещены.
Backend/frontend выполняются последовательно по зависимостям, без обязательных
субагентов и постоянных персональных назначений. Следующее задание — только по
новому поручению пользователя после передачи текущего результата.

Реализация → самопроверка → PR → отдельное ревью → исправления и необходимые
перепроверки → HUMAN_ACCEPTANCE_PENDING → явное решение пользователя.
PASS не равен приёмке. Record содержит actual SHA/tree, commands/exit/inputs,
findings/fixes и ограничения; секреты/PII/private reasoning исключаются.
Fresh/upgrade/concurrency для schema, реальные browser/runtime для integration;
empty/skipped/missing/timeout/flaky fail. Pure не устанавливает runtime readiness.

G0 v7.1 — историческое принятие прежней версии, не approval этой редакции.
G1 (собственный Harness) — REMOVED_FROM_PLAN, номер не переиспользуется.
G2 сохраняет persisted evidence/replay/eligibility: MS-N007–013.
G3 сохраняет staging full loop/four modes/Tutor/diagnostic/practice:
MS-N014–021, authorized live Product + fallback отдельно.
G4 сохраняет security/performance/accessibility/public HTTPS/install/restore:
MS-N019/022/023. G5 — report/freeze/handover MS-N024.
Каждый gate требует exact release evidence, закрытых blocking findings,
отдельного ревью и человеческого решения, без назначенных по старому плану лиц.
Миграция PR54/консолидация PR55 не повторяются и не входят в эти future gates.
Production/provider/security решения не выводятся из green CI.

## 18. Исторические ошибки разработки R04 и уроки

Исторический case study выведенной подсистемы; не текущая задача и не обязательство
сохранить её runtime/tests. Имена удалённых tests ниже восстанавливаются по Git
`1a015f7513933901e8bb252e94c660e4383b6b0e`. Общие продуктовые проверки сохранены отдельно.

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
success, approval23:08, merge23:09; историческая suite73tests. Урок: fault injection должен моделировать side
effect, произошедший несмотря на ошибочный return. Каждый кейс в отчёте сопровождается PR URL,
review date, исправляющим commit, именем regression и CI SHA. Эти кейсы не выдаются за испытания
будущего OS sandbox/live adapter. Источник: https://github.com/Tramsey00/MathStart-Python/pull/10 .

---

## 19. Требования курса и исторические сроки

Первичные course источники и точные source/time/scope записи C-01–17 сохранены
в §28 и предыдущем ТЗ в Git. Общее требование описать AI-инструменты/процесс
не означает обязанность создать собственный MathStart Harness. Отчёт отражает
реальные Codex, AGENTS, task skills, tests/CI, отдельное ревью и исправления.
Советы другой команде и внешние примеры не создают MathStart mandate.

Исторические 08.10 meeting/checkpoint и регистрация до 09.10 включительно не
становятся новыми deadlines. Дата защиты, LMS/registration receipt, официальные
ФИО/группы и согласование проекта подтверждаются человеком; недостающие факты
TBD. MS7-ORG01 адаптирована в MS-N024, не объявляется выполненной без evidence.
Ориентир отчёта 45–60 страниц сохранён; оформление кафедры требует уточнения.
Нового согласования преподавателя эта редакция не заявляет.

## 20. Единая последовательность и готовность

Единственный chronological registry — [docs/tasks/INDEX.md](../tasks/INDEX.md),
machine mirror — registry.json; подробности — отдельные skills/tasks/.../SKILL.md.
Очередь начинается после приёмки текущего MS-N000 с MS-N001 (три визуальных
направления и выбор). Ни одно будущее задание этим поручением не запускается.
Исторические task IDs сохранены; 52 исходные карточки и 115 typed edges остаются
provenance, не новым календарём и не active dependencies.

Снятые Harness tasks не DONE. Сохранённые/адаптированные/объединённые задачи
имеют явную карту §25 и source registry workflow fields. В новой очереди нет
рёбер к снятым tasks. PLANNED не доказывает upstream acceptance. Непринятый
дизайн/механика блокирует зависимую реализацию, а не заменяется догадкой.

## 21. Task skills и lifecycle

Task ID стабилен; прежние R/V/I IDs не переименованы и не назначают участников.
Новые MS-N IDs обозначают интегрированные последовательные increments.
Один skill-пакет имеет YAML name/description и единственную canonical карточку;
AGENTS и реестр указывают explicit read, автоматическое discovery не обещается.

Карточка определяет проблему/цель, actual baseline evidence, scope/exclusions,
dependencies/sources, modules/data/contracts, backend/frontend/integration,
порядок по зависимостям, ошибки/compatibility, acceptance/checks, artifacts/review,
stop conditions и требуемое решение. Модели/авторы/субагенты не назначаются.

Статусы PLANNED, IN_PROGRESS, READY_FOR_REVIEW, CHANGES_REQUESTED,
HUMAN_ACCEPTANCE_PENDING, ACCEPTED, BLOCKED_DEPENDENCY, BLOCKED_DECISION,
REMOVED_FROM_PLAN различаются; merge фиксируется отдельно. Tests не закрывают
human gate. Если Issue уже есть, продолжить её и соответствующий PR; новая
Issue не обязательный промежуточный барьер для поручения пользователя. PR
содержит task ID, scope/validation/findings и closing link только к реально
соответствующей Issue. Merge — после решения пользователя, без force push.

## 22. Соответствие прежних карточек R

Исторические буквенные группы сохранены для прослеживаемости, без персональных
владельцев и параллельного плана. Полный исходный текст — `source_card_text`
в [source registry](../../specs/product/task-dispositions-v7.2.json).

### MS7-R02A · HTTP и eligibility addendum

Судьба: **COMPLETED_BASELINE**. Сохранён выполненный scope/accepted platform PR54; не объявляет future assessed runtime или новое одобрение addenda.

### MS7-R03A · CompletionFact addendum

Судьба: **COMPLETED_BASELINE**. Сохранён выполненный scope/accepted platform PR54; не объявляет future assessed runtime или новое одобрение addenda.

### MS7-R05 · Context Layer и typed tools

Судьба: **REMOVED_FROM_PLAN**. Снято с плана: собственный Harness выведен, продуктового потребителя нет.

### MS7-R06A · Policy, hooks и machine trace

Судьба: **REMOVED_FROM_PLAN**. Снято с плана: собственный Harness выведен, продуктового потребителя нет.

### MS7-R06B · Физический sandbox

Судьба: **REMOVED_FROM_PLAN**. Снято с плана: собственный Harness выведен, продуктового потребителя нет.

### MS7-R04A · Live coding-model adapter

Судьба: **REMOVED_FROM_PLAN**. Снято с плана: собственный Harness выведен, продуктового потребителя нет.

### MS7-R07 · Skills и bounded subagents

Судьба: **REMOVED_FROM_PLAN**. Снято с плана: собственный Harness выведен, продуктового потребителя нет.

### MS7-R08 · Harness eval и G1

Судьба: **REMOVED_FROM_PLAN**. Снято с плана: собственный Harness выведен, продуктового потребителя нет.

### MS7-R09 · Parser и normalizer

Судьба: **ADAPTED**. MS-N010; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N010](../../skills/tasks/0010-math-parser/SKILL.md).

### MS7-R10 · Validators и deterministic Analyzer

Судьба: **ADAPTED**. MS-N011; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N011](../../skills/tasks/0011-deterministic-analysis/SKILL.md).

### MS7-R11 · Adaptive и diagnostic policy

Судьба: **MERGED**. MS-N016; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N016](../../skills/tasks/0016-diagnostic-practice/SKILL.md).

### MS7-R12 · Tutor policy и hint bank

Судьба: **MERGED**. MS-N018; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N018](../../skills/tasks/0018-tutor/SKILL.md).

### MS7-R13 · Аудит persisted evidence loop

Судьба: **MERGED**. MS-N013; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N013](../../skills/tasks/0013-evidence-finalization/SKILL.md).

### MS7-R14 · Golden eval и AI gates

Судьба: **ADAPTED**. MS-N019; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N019](../../skills/tasks/0019-product-evaluation/SKILL.md).

### MS7-R15 · Security/privacy release audit

Судьба: **MERGED**. MS-N022; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N022](../../skills/tasks/0022-release-quality/SKILL.md).

### MS7-R16 · Архитектура и глава Harness

Судьба: **MERGED**. MS-N024; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N024](../../skills/tasks/0024-report-handover/SKILL.md).

### MS7-R17 · Публичный RC и репетиция

Судьба: **MERGED**. MS-N023; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N023](../../skills/tasks/0023-release-recovery/SKILL.md).

### MS7-R18 · Freeze и handover

Судьба: **MERGED**. MS-N024; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N024](../../skills/tasks/0024-report-handover/SKILL.md).

## 23. Соответствие прежних карточек V

Исторические буквенные группы сохранены для прослеживаемости, без персональных
владельцев и параллельного плана. Полный исходный текст — `source_card_text`
в [source registry](../../specs/product/task-dispositions-v7.2.json).

### MS7-V02 · Аккаунты и права

Судьба: **COMPLETED_BASELINE**. Сохранён выполненный scope/accepted platform PR54; не объявляет future assessed runtime или новое одобрение addenda.

### MS7-V03 · Knowledge и TopicSkill persistence

Судьба: **ADAPTED**. MS-N007; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N007](../../skills/tasks/0007-knowledge-persistence/SKILL.md).

### MS7-V04 · Exercise versions и pilot bank

Судьба: **ADAPTED**. MS-N008; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N008](../../skills/tasks/0008-exercise-bank/SKILL.md).

### MS7-V05 · Attempts, revisions и steps

Судьба: **MERGED**. MS-N009; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N009](../../skills/tasks/0009-attempt-help-lifecycle/SKILL.md).

### MS7-V06 · Единая помощь и reveal

Судьба: **MERGED**. MS-N009; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N009](../../skills/tasks/0009-attempt-help-lifecycle/SKILL.md).

### MS7-V07 · Backend skill и real run

Судьба: **REMOVED_FROM_PLAN**. Снято с плана: собственный Harness выведен, продуктового потребителя нет.

### MS7-V08 · ProgressEvent и проекция

Судьба: **MERGED**. MS-N012; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N012](../../skills/tasks/0012-progress-replay/SKILL.md).

### MS7-V09 · Replay и concurrency

Судьба: **MERGED**. MS-N012; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N012](../../skills/tasks/0012-progress-replay/SKILL.md).

### MS7-V10 · Finalize Analysis→Progress

Судьба: **MERGED**. MS-N013; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N013](../../skills/tasks/0013-evidence-finalization/SKILL.md).

### MS7-V11 · Product provider и AIRun

Судьба: **ADAPTED**. MS-N017; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N017](../../skills/tasks/0017-product-provider/SKILL.md).

### MS7-V12 · Диагностика и Practice API

Судьба: **MERGED**. MS-N016; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N016](../../skills/tasks/0016-diagnostic-practice/SKILL.md).

### MS7-V13 · Tutor context и conversations

Судьба: **MERGED**. MS-N018; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N018](../../skills/tasks/0018-tutor/SKILL.md).

### MS7-V14 · Staging сборка

Судьба: **MERGED**. MS-N021; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N021](../../skills/tasks/0021-staging-integration/SKILL.md).

### MS7-V15 · Backend security/performance

Судьба: **MERGED**. MS-N022; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N022](../../skills/tasks/0022-release-quality/SKILL.md).

### MS7-V16 · Restore/upgrade и backend chapter

Судьба: **MERGED**. MS-N023; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N023](../../skills/tasks/0023-release-recovery/SKILL.md).

### MS7-V17 · Публичный backend release

Судьба: **MERGED**. MS-N023; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N023](../../skills/tasks/0023-release-recovery/SKILL.md).

### MS7-V18 · Backend freeze

Судьба: **MERGED**. MS-N024; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N024](../../skills/tasks/0024-report-handover/SKILL.md).

## 24. Соответствие прежних карточек I

Исторические буквенные группы сохранены для прослеживаемости, без персональных
владельцев и параллельного плана. Полный исходный текст — `source_card_text`
в [source registry](../../specs/product/task-dispositions-v7.2.json).

### MS7-I02 · UI foundation и fixtures

Судьба: **COMPLETED_BASELINE**. Сохранён выполненный scope/accepted platform PR54; не объявляет future assessed runtime или новое одобрение addenda.

### MS7-I03 · Auth/profile/onboarding UI

Судьба: **COMPLETED_BASELINE**. Сохранён выполненный scope/accepted platform PR54; не объявляет future assessed runtime или новое одобрение addenda.

### MS7-I04 · Каталог и renderer

Судьба: **ADAPTED**. MS-N005; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N005](../../skills/tasks/0005-redesign-rollout/SKILL.md).

### MS7-I05 · SELF_CHECK и final answer UI

Судьба: **MERGED**. MS-N014; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N014](../../skills/tasks/0014-exercise-ui/SKILL.md).

### MS7-I06 · Пошаговый редактор

Судьба: **MERGED**. MS-N014; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N014](../../skills/tasks/0014-exercise-ui/SKILL.md).

### MS7-I07 · Structured solution UI

Судьба: **MERGED**. MS-N014; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N014](../../skills/tasks/0014-exercise-ui/SKILL.md).

### MS7-I08 · Frontend skill и visual run

Судьба: **REMOVED_FROM_PLAN**. Снято с плана: собственный Harness выведен, продуктового потребителя нет.

### MS7-I09 · Hints/reveal и recovery UI

Судьба: **MERGED**. MS-N014; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N014](../../skills/tasks/0014-exercise-ui/SKILL.md).

### MS7-I10 · Feedback/progress views

Судьба: **MERGED**. MS-N015; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N015](../../skills/tasks/0015-progress-history/SKILL.md).

### MS7-I11 · Onboarding completion/history

Судьба: **MERGED**. MS-N015; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N015](../../skills/tasks/0015-progress-history/SKILL.md).

### MS7-I12 · Tutor panel

Судьба: **MERGED**. MS-N018; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N018](../../skills/tasks/0018-tutor/SKILL.md).

### MS7-I13 · Practice и diagnostics UI

Судьба: **MERGED**. MS-N016; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N016](../../skills/tasks/0016-diagnostic-practice/SKILL.md).

### MS7-I14 · Полная интеграция

Судьба: **MERGED**. MS-N021; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N021](../../skills/tasks/0021-staging-integration/SKILL.md).

### MS7-I15 · A11y/mobile/security UX

Судьба: **MERGED**. MS-N022; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N022](../../skills/tasks/0022-release-quality/SKILL.md).

### MS7-I16 · Demo и главы отчёта

Судьба: **MERGED**. MS-N024; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N024](../../skills/tasks/0024-report-handover/SKILL.md).

### MS7-I17 · Public browser rehearsal

Судьба: **MERGED**. MS-N023; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N023](../../skills/tasks/0023-release-recovery/SKILL.md).

### MS7-I18 · Frontend freeze

Судьба: **MERGED**. MS-N024; продуктовый scope сохранён, персональные назначения/Harness obligations сняты.

Каноническое подробное задание: [MS-N024](../../skills/tasks/0024-report-handover/SKILL.md).

## 25. Зависимости и карта изменения scope

Все52 source IDs и115 source typed edges сохранены дословно в machine source
registry с original results/acceptance. Текущие `workflow_disposition`,
`workflow_tasks`, `workflow_reason` отделены от исторических current_status/
platform_disposition. Machine queue и Markdown таблица проверяются на unique IDs,
существующие skills/dependencies, отсутствие cycles и ссылок к снятым карточкам.

Сняты MS7-R05/R06A/R06B/R04A/R07/R08/V07/I08: только собственный Harness.
MS7-R16 адаптирован в отчёт о фактическом AI-процессе, R14 сохранил Product eval,
NFR-08 offline CI сохранён, NFR-12 cold-start адаптирован, NFR-20 privacy артефактов
сохранён. Из mixed задач убраны Harness12 eval/three-owner-run обязательства.
Product validators/AI limits/eval/PG/install/recovery/security не сняты.

Пять historical result карточек сохраняют выполненный baseline и отдельные
approval/proposal limits; оставшиеся39 future карточек адаптированы или объединены
в новую очередь. Исторические события не становятся новыми pending migration tasks.

## 26. Требования и прослеживаемость
Номера FR/NFR/AT сохранены; FR-25–29 явно POST-MVP. Ни одно обязательное требование не
закрывается только ссылкой на старое ТЗ. В реестрах ниже source P означает PROJECT DECISION из
настоящего ТЗ и frozen contracts; Cxx — course registry. Evidence E(task) — обязательный task bundle из
§21, с test report и final SHA; gate ledger ссылается на него. Для всех planned требований evidence ещё
предстоит получить. ID / требование
Source
Historical task references (актуальная карта §25)
Test / evidence
Gate
FR-01 Auth/profile
P; C-02/03/11 по scope
MS7-V02, MS7-I03
AT-01; E(MS7-V02)
G3
FR-02 Три onboarding modes; чтение не прогресс
P; C-02/03/11 по scope
MS7-V08, MS7-V12, MS7-I03
AT-02; E(MS7-V08)
G3
FR-03 Каталог и TopicSkill
P; C-02/03/11 по scope
MS7-V03, MS7-I04
AT-12; E(MS7-V03)
G3
FR-04 PublicExerciseDTO
P; C-02/03/11 по scope
MS7-R02A, MS7-V04
AT-03; E(MS7-R02A)
G3
FR-05 SELF_CHECK
P; C-02/03/11 по scope
MS7-V05, MS7-I05
AT-03; E(MS7-V05)
G3
FR-06 FINAL_ANSWER
P; C-02/03/11 по scope
MS7-R10, MS7-V10, MS7-I05
AT-04; E(MS7-R10)
G3
FR-07 STEP_BY_STEP
P; C-02/03/11 по scope
MS7-R10, MS7-V05, MS7-I06
AT-04; E(MS7-R10)
G3
FR-08 Две STRUCTURED schemas
P; C-02/03/11 по scope
MS7-V04, MS7-R10, MS7-I07
AT-05; E(MS7-V04)
G3
FR-09 Server-only secrets
P; C-02/03/11 по scope
MS7-V04, MS7-V06, MS7-I09
AT-03; E(MS7-V04)
G3
FR-10 Безопасная математика
P; C-02/03/11 по scope
MS7-R09, MS7-R10
AT-04; E(MS7-R09)
G3
FR-11 First proven error
P; C-02/03/11 по scope
MS7-R10, MS7-V10
AT-04; E(MS7-R10)
G3
FR-12 Taxonomy/confidence/abstain
P; C-02/03/11 по scope
MS7-R10, MS7-V11
AT-10; E(MS7-R10)
G3
FR-13 Skill evidence mapping
P; C-02/03/11 по scope
MS7-R10, MS7-V08
AT-06; E(MS7-R10)
G3
FR-14 Evidence→Progress
P; C-02/03/11 по scope
MS7-V08, MS7-V10
AT-06; E(MS7-V08)
G3
FR-15 Replay/idempotency
P; C-02/03/11 по scope
MS7-V09
AT-07; E(MS7-V09)
G3
FR-16 DAG depth2
P; C-02/03/11 по scope
MS7-V03, MS7-R11
AT-12; E(MS7-V03)
G3
FR-17 Tutor context
P; C-02/03/11 по scope
MS7-R12, MS7-V13
AT-10; E(MS7-R12)
G3
FR-18 Hints/reveal/fallback
P; C-02/03/11 по scope
MS7-V06, MS7-V13, MS7-I09
AT-03; E(MS7-V06)
G3
FR-19 Adaptive selection
P; C-02/03/11 по scope
MS7-R11, MS7-V12
AT-11; E(MS7-R11)
G3
ID / требование
Source
Historical task references (актуальная карта §25)
Test / evidence
Gate
FR-20 Practice и возврат
P; C-02/03/11 по scope
MS7-V12, MS7-I13
AT-11; E(MS7-V12)
G3
FR-21 History
P; C-02/03/11 по scope
MS7-V05, MS7-I11
AT-06; E(MS7-V05)
G3
FR-22 Progress map/list
P; C-02/03/11 по scope
MS7-V08, MS7-I10
AT-12; E(MS7-V08)
G3
FR-23 AIRun
P; C-02/03/11 по scope
MS7-V11
AT-10; E(MS7-V11)
G3
FR-24 Public HTTPS
P; C-02/03/11 по scope
MS7-V17, MS7-I17
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
MS7-R13
Scope/failure tests карточки; E(MS7-R13)
G2
NFR-02 LLM не создаёт неподтверждённый штраф
P, §§5–16
MS7-R14
Scope/failure tests карточки; E(MS7-R14)
G4
NFR-03 Replay воспроизводим
P, §§5–16
MS7-V09
Scope/failure tests карточки; E(MS7-V09)
G2
NFR-04 Нет утечки answers
P, §§5–16
MS7-R15
Scope/failure tests карточки; E(MS7-R15)
G4
NFR-05 Auth/CSRF/ownership/rates
P, §§5–16
MS7-V15
Scope/failure tests карточки; E(MS7-V15)
G4
NFR-06 Synthetic/privacy/redaction
P, §§5–16
MS7-R15
Scope/failure tests карточки; E(MS7-R15)
G4
NFR-07 p95 500ms/15s
P, §§5–16
MS7-V15
Scope/failure tests карточки; E(MS7-V15)
G4
NFR-08 Offline CI
P, §§5–16
MS-N019/MS-N022; offline CI и actual candidate evidence
G4
NFR-09 Correlation/observability
P, §§5–16
MS7-V11
Scope/failure tests карточки; E(MS7-V11)
G3
NFR-10 Migrations fresh/upgrade
P, §§5–16
MS7-V16
Scope/failure tests карточки; E(MS7-V16)
G4
NFR-11 Воспроизводимая среда
P, §§5–16
MS7-V14
Scope/failure tests карточки; E(MS7-V14)
G3
NFR-12 Repo cold start
P, §§5–16
MS-N024; чистый clone/task-skill walkthrough
G5
NFR-13 Browser/mobile
P, §§5–16
MS7-I15
Scope/failure tests карточки; E(MS7-I15)
G4
NFR-14 Registry schemas
P, §§5–16
MS7-R10
Scope/failure tests карточки; E(MS7-R10)
G2
NFR-15 Raw отдельно
P, §§5–16
MS7-R09
Scope/failure tests карточки; E(MS7-R09)
G2
NFR-16 Keyboard/a11y
P, §§5–16
MS7-I15
Scope/failure tests карточки; E(MS7-I15)
G4
NFR-17 Atomic/recovery
P, §§5–16
MS7-V10
Scope/failure tests карточки; E(MS7-V10)
G2
NFR-18 Version/provenance
P, §§5–16
MS7-V04
Scope/failure tests карточки; E(MS7-V04)
G2
NFR-19 — REMOVED_FROM_PLAN: enforcement/budgets собственного Harness сняты.
Исходный ID/текст сохранён в предыдущей редакции; product security не изменена.
NFR-20 Visual artifacts без PII
P, §§5–16
MS-N022/MS-N024; visual/report privacy
G4/G5
NFR-12 authoritative cold-start route:
1. fresh git clone публичного MathStart-Python;
2. checkout pinned release/task SHA;
3. установка документированной версии Python и dependency lock в
чистой среде;
4. только документированные non-secret environment values;
credentials остаются вне repo;
5. doctor/runtime report;
6. canonical repository verification;
7. открыть AGENTS → architecture → requirements → queue → task skill без прежней переписки;
8. сохранить actual implementation/check/review/fix evidence;
9. проверка contract/digest/version consistency.
Source-only ZIP допустим только как audit snapshot и не является достаточным evidence для
Git-aware task/source reproducibility, поскольку не содержит полного Git metadata.

---


Новые FR-30 (три направления/редизайн), FR-31 (дизайн-система), FR-32
(проектирование геймификации) и NFR-21 (один исполнитель, отдельное ревью,
человеческая приёмка) относятся к новому draft scope. Их evidence — MS-N001–006,
MS-N020 и AGENTS/реестр. Существующие FR-01–29 и product NFR/числа сохранены;
полная приёмка новых направлений пользователем ещё ожидается.

## 27. Сквозные acceptance routes
AT-01. Другой пользователь/CSRF/login:401/403/404, ноль чужих данных. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-02. Zero0/0/selfreport60/15 один раз; чтение не пишет. Evidence:
expected/actual
assertions, SHA, commands/browser versions и gate ledger; провал блокирует соответствующий G2/G3/G4.
AT-03. Leaks HTML/JSON/JS/network; hint/reveal+submit race и cross-attempt eligibility. Evidence: expected/actual assertions, SHA, commands/browser versions и gate ledger; провал
блокирует соответствующий G2/G3/G4.
AT-04. Equivalent rational, first proven error, cascade/unsupported gap. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-05. Две structured schemas: valid/invalid/unknown/reorder. Evidence:
expected/actual
assertions, SHA, commands/browser versions и gate ledger; провал блокирует соответствующий G2/G3/G4.
AT-06. Retry/crash/repeated positive: exactly-once persisted evidence. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-07. Late events/facts, same timestamps, online/replay equality. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-08. Neutral completions вытесняют independent из 10, числа не меняются. Evidence: expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-09. Diagnostic10/skip/help/reveal, no fake independent. Evidence:
expected/actual
assertions, SHA, commands/browser versions и gate ledger; провал блокирует соответствующий G2/G3/G4.
AT-10. Malformed/low confidence/injection/provider outage: abstain/fallback. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-11. Adaptive depth2/max7/no-candidate/repeat/return. Evidence: expected/actual
assertions, SHA, commands/browser versions и gate ledger; провал блокирует соответствующий G2/G3/G4.
AT-12. Topic PRIMARY denominator, external basic_arithmetic, accessible graph. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-13 — REMOVED_FROM_PLAN: испытания собственного Harness сняты; ID не переиспользуется.
AT-14. IDOR/CSRF/XSS/rates/redaction/secrets. Evidence: expected/actual
assertions,
SHA, commands/browser versions и gate ledger; провал блокирует соответствующий G2/G3/G4.
AT-15. Clean install/upgrade/backup restore, source preservation. Evidence:
expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.
AT-16. Public full loop, four modes, Product live+fallback . Evidence: expected/actual assertions, SHA, commands/browser versions и gate ledger; провал блокирует
соответствующий G2/G3/G4.

---

## 28. Course compliance registry
ID / формулировка
Классификация
Source/time/scop e
Историческая source attribution/task (текущая карта §25)
C-01 Agentic development
MANDATORY COURSE REQUIREMENT
L1 00:17–02:06; L3 00:43.513– 04:11.904; общее
MS-N024; Codex/AGENTS/task skills/check/review/fix evidence; G5
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
C-08 Описание настройки фактически используемых AI-инструментов/процесса
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
Собственный controlled Harness был PROJECT DECISION, не обязательством курса;
он снят по решению пользователя. C-01/08/09/10 теперь закрываются описанием
реальных Codex/инструкций/task skills/проверок/отдельного ревью/исправлений в N024.
Product LLM (C-03) остаётся отдельным результатом N017–019. Source/time/scope
записи и другие course требования сохранены; нового согласования преподавателя нет.

---


Персональные имена и 09.10 в source attribution выше — исторические записи источника,
не назначения/сроки новой очереди. Actual course receipts проверяет MS-N024.

## 29. Пояснительная записка и демонстрация

Записка описывает реально реализованный продукт, не выдаёт ТЗ/прототип за код.
Глава1: предметная область, аналоги с observation limits, сценарии/границы.
Глава2: фактический stack, modular monolith, ownership, ER/API/state machines,
submit/finalize/help/reveal/replay/return. Глава3: настройка реально используемого
Codex, AGENTS/task skills, execution/checks/отдельное review/fixes, реальные failures
и ограничения. История собственного Harness — короткий case study, не три новых
owner runs и не выдуманный sandbox enforcement. Глава4: реализация, screenshots,
tests/evals/load/recovery/deployment и ограничения. Ориентир45–60 страниц и
формат кафедры уточняются по course source, не назначаются агентом.

Demo: login→тема→step→first proven error→hint→practice prerequisite→возврат→
history/progress; independent success и explicit reveal отдельным маршрутом.
Product live/fallback различаются, redacted AIRun связывает actual calls.
Report appendix содержит короткие наблюдаемые traces/commands/findings, не
секреты/private reasoning. Каждый screenshot имеет SHA/date/browser evidence.
Длительность5–7min — прежний проектный ориентир, требует актуального согласования.

## 30. Риски и открытые решения

Не выбраны конкретный дизайн, UI stack, игровые механики/owner/storage/events,
Product provider/model/budget, public host/region/operator/security/privacy и
официальные course/LMS данные/защита. Получение решений подробно описано в task skills.
Нет обещанного календаря; порядок определяется dependencies и human decisions.

Основные риски: ложный strong negative, leakage через help/SSG/prompt, duplicate
evidence/award, loss of raw work, late event/replay drift, source/widget regression,
непроверенный backup/restore, смешение synthetic/live и PASS/acceptance.
Каждое unresolved решение имеет BLOCKED_DECISION, каждый failed check — finding;
неподтверждённая среда не называется готовой. Нет нового migration assignment.

## 31. История редакций и переходов

Ниже только историческая карта v6→v7.1. Старые owners/deadlines/Harness требования
не действуют в новой очереди; их current disposition — §§20–25. Полный исходник
и approvals сохранены в Git, не объявляются принятием редакции20.10.2026.

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


### 31.3. Редакция20.10.2026

Сохранено: продуктовый pilot/domain/HTTP/evidence/math/AI/security/ops scope и
исходная история52 карточек/115 edges. Изменено: полная текущая architecture,
documentation/branch/review workflow, active dependency graph. Добавлено:
redesign/design system/game design tasks. Снято: собственный Engineering Harness
и исключительно его обязательства. PR54/55 — завершённые факты, не будущая работа.

## 32. Источники, provenance и статус утверждения

[Provenance/changelog](technical-spec-v7.2-provenance.md) фиксирует hashes
актуального Markdown и registry и неизменные исходные hashes.
Исторический v7.1 PDF — Git `3a290a46d991e22269a17dde41e39f0637576071`:
`docs/specifications/sources/technical-spec-v7.1.pdf`, SHA256
`e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd`.
Предыдущий полный v7.2 — [точная версия](https://github.com/Tramsey00/MathStart-Python/blob/1a015f7513933901e8bb252e94c660e4383b6b0e/docs/specifications/technical-spec-v7.2-draft.md); её карточки и approvals
остаются в Git/source registry. Historical G0 APPROVED30.09.2026 Руслана,
Владимира и Ильи не подписывают нынешний draft. Эта запись не меняет оригиналы.

Desktop migration MD и два PDF прочитаны как прежние требования; Markdown
migration copy имеет exact SHA256 c5a554e3911bdb43db28d67fd02d26e38d50b2820e1154a272d89ecb44b1faae.
Исторические PDFs на Desktop не редактировались. Доступность/способ чтения и
проверки источников перечислены в аудите. Текущие инструкции — AGENTS,
архитектура — ARCHITECTURE; спецификация остаётся PRODUCT HUMAN_PENDING.
