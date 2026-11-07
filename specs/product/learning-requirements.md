# Требования к будущему учебному циклу

Доменный reference, не описание уже реализованных endpoints. Данные, математические
правила, thresholds и security requirements сохранены из редакции 20.10.2026.
Исходник восстановим из Git b29a7ccdd07784cfcfd19278cbe59b30c83cd4ea,
путь docs/specifications/technical-spec-v7.2-draft.md, разделы 6–11 и 14–16.
Это сохранение требований, не новое одобрение прежнего draft.

Текущие структура и runtime — [ARCHITECTURE](../../ARCHITECTURE.md), scope и порядок
реализации — [задачи](../../docs/tasks/INDEX.md). Старые номера задач, gates и
платформенные формулировки внутри reference не задают новый порядок исполнения.
При конфликте процессной формулировки используй AGENTS и текущую карточку;
изменять математическую/API/security семантику без отдельного решения нельзя.
Для переноса публичных уроков этот документ читается только по зависимости:
legacy самопроверка урока не является новым assessed exercise API.

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
ID: все восемь полей сохранены, чтобы не сжимать текст в восемь узких колонок. Где настраивается для
будущих подсистем — целевое место хранения, а не заявление о существующем файле. Effective
config/version фиксируется в evidence; G0 не устанавливает credentials и не разрешает live расходы.
Исторические counts тестов/страниц, source timestamps и commit IDs — факты, а не operational defaults.
Версии schemas, cardinality, точные формулы и enums остаются частью contract; ссылки на главы и
номера задач не являются настраиваемыми параметрами. ID / Параметр
Default или требование
Обоснование
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
OD-04 / Размер parser §9
64KiB request;40steps;512chars/expression;128tokens; nesting16; literal12digits; abs power10
Ограничить сложность недоверенного ввода
OD-05 / Срок выполнения parser §9
250ms/expression;2s/batch
Освобождать worker при тяжёлом вводе
OD-06 / Сильный отрицательный сигнал §9
confidence≥0.8 и отдельно доказанное known evidence
Не путать уверенность модели с математической истиной
OD-07 / Контекст Tutor §10
4000chars theory;10skills;5confirmed errors;6messages;6000estimated tokens
Минимизировать контекст и стоимость
OD-08 / Вызовы Product §10
12s общий deadline;≤2calls/action, retries внутри него
Ограничить ожидание и обеспечить fallback
OD-09 / Diagnostic/Adaptive/Practice §10
Diagnostic≤10; depth2; confidence30; mastery bands40/70; последние 10 excluded; streak3 или
mastery70/confidence60 после 1item; max7; oneactive
Сохранить воспроизводимую учебную семантику
OD-10 / Pagination/poll API §11
default20/max100; poll1/2/4s затем manual retry
Ограничить ответы и запросы без duplicate submit
OD-11 / Receipt идемпотентности §§6/11
Минимум 7 суток; evidence source uniqueness не истекает вместе с receipt
Безопасное восстановление операции
OD-12/13/14 — REMOVED_FROM_PLAN. лимиты и subagents Engineering Harness сняты;
исходные числа сохранены в историческом source registry/Git, не действуют как
обязательные ограничения для реально используемого Codex.
OD-15 / Оценка Analyzer §15
≥50:12correct/16errors/10ambiguous/6wrongfinal/6structured;≥20holdout;≥95%deterministic/
≥85%taxonomy;false strong=0 safety subset
Измерить качество на объявленных denominators
OD-16 / Оценка Tutor §15
≥20Tutor; live Product + fallback; обычный CI offline
Проверить продуктовую AI-интеграцию и воспроизводимость CI
ID / Параметр
Default или требование
Обоснование
OD-17 / Ограничения частоты §16
login10/5min/IP;submit30/min/user;reveal10/min/user;AI5/min и 50/day/user;global money cap TBD до live
Защитить сервис и расходы
OD-18 / Сроки хранения §16
AIRun/trace90days;attempts/messages до защиты+30days;backups30days
Ограничить хранение и сохранить evidence для приёмки
OD-19 / Производительность §16
p95 API<500ms/AI<15s;≥200ordinary при 10concurrent;≥30AI при 2concurrent;ceil(0.95*n)
Воспроизводимая приёмка demo profile
OD-20 / Backup/восстановление §16
daily encrypted;RPO≤24h/RTO≤2h;retention30days поOD-18
Проверяемое восстановление данных
OD-21 / Browser/public runtime §§11/16
360/768/1440;Chrome/Edge/Firefox;Python3.12+/FastAPI/React/PostgreSQL16, exact locks
Совместимость и подтверждённая release среда
OD-22 / Безопасность, schemas и версии §§4–16
Fail-closed;server-only secrets;Only Progress writes;typed ordered steps;versioned
DTO/registry;atomic/idempotent writes
Сохранить границы доверия
Порядок настройки и принятия изменений по тем же ID: ID
Где настраивается
Кто может менять
Требуемый Gate/ADR
Жёсткий предел или значение по умолчанию
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
Где настраивается
Кто может менять
Требуемый Gate/ADR
Жёсткий предел или значение по умолчанию
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

