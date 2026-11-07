# SPEC MS7-R02A: Дополнение к HTTP и eligibility v1

- **Статус:** Кандидат на независимое человеческое ревью; приёмка PENDING
- **Владелец:** Руслан
- **Reviewer / Task Approver:** Владимир
- **Этап:** Завершение контракта G1
- **Связь:** FOLLOW-UP / ДОПОЛНЕНИЕ К ЗАМОРОЖЕННОМУ R02
- **Нормативный источник:** MathStart Technical Specification v7.1, принят G0
  2026-09-30, §§4–11,15–17,21–22,25–27,30,32.
- **Замороженные входы:** ADR-0002 и `../exercises/R02-exercise-architecture.md`;
  R03/ADR-0003 задаёт неизменённые имена событий и числовую семантику.
- **Предлагаемый ADR:** `../../docs/adr/ADR-0004-http-eligibility-addendum.md`
- **План:** `../../docs/exec-plans/active/MS7-R02A-http-eligibility.md`

## Deliverables и полномочия

`openapi-v1.json` — единственный канонический OpenAPI artifact. OAS 3.1 JSON использует
JSON Schema 2020-12; `schemas/dto-v1.schema.json` определяет повторно используемые wire DTO.
`http-policy-v1.json` задаёт машиночитаемые правила operations, revision, lifecycle,
idempotency, exposure и limits. `schemas/scenario-v1.schema.json` — контракт только для fixtures,
не компонент публичного API. Fixtures — синтетические примеры спецификации, а не seeds
или сохранённые runtime evidence.

Версия `1.0.0` / metadata `http-v1` идентифицирует этот HTTP artifact. Exercise
`contract_version` и дополнительный `version` — равные alias одного счётчика неизменяемых
версий упражнения, как требует R02. Это не независимые счётчики. Привязанные к серверу
ExerciseVersion id, exercise id и version являются авторитетными. Публичные difficulty bands
easy/medium/hard сопоставляются с difficulty_level 1–2/3/4.

Документ задаёт будущие endpoints; реализации endpoints, models, database migration,
Progress reducer, CompletionFact или provider здесь нет. Замороженный R02 остаётся принятым.
Новый artifact и D-022/023 требуют принятия Владимиром их точного digest до использования
как принятого upstream в V02/I02.

## Поверхность HTTP и общие правила

OpenAPI содержит все 37 операций method/route из §11: Identity, Content, Attempts,
Diagnostics, Progress, Practice, Tutor и Operations. Namespace `/api/v1/`, snake_case,
конечный slash, UTF-8 JSON. API v2 и альтернативный канонический route не вводятся.

Django Session Auth применяется к данным ученика и assessed exercises. Опубликованные
grades/topics/theory, CSRF bootstrap и минимальная health доступны анонимно для чтения.
Registration/login создают session; email необязателен, обещания канала восстановления
без верификации нет. Ошибка login не различает отсутствующий username и неверный password.
Cookie session ротируется при login. Каждая mutation, включая registration/login/logout,
требует `X-CSRFToken`, совпадающий с CSRF cookie, полученной через GET auth/csrf/.
CSRF bootstrap может установить cookie; GET не создаёт Attempt, выбранный элемент session
или доменное evidence.

Поиск с ограничением владельца применяется к attempts, sessions, conversations,
progress/history и переданным previous_attempt/context IDs. Сначала выполнить authentication,
затем ограничить поиск владельцем. Отсутствующий и чужой owned object дают общий 404 envelope.
В ошибках нельзя раскрывать чужую revision, identifier, action или eligibility. Неаутентифицированный
запрос ученика получает общий 401 независимо от существования объекта. 403 зарезервирован для
CSRF и ролей, не раскрывая resource с секретом владельца. IDs тем Content сохраняют идентичность/
slugs ContentPage; новые resource identifiers — UUID. Все timestamps — aware UTC с точностью
до шести дробных цифр; детерминированные примеры используют фиксированные UUID/timestamps.

Ответы GET с pagination содержат `meta.pagination`: `next_cursor` (null в конце), `page_size`,
`has_more`. По умолчанию 20, максимум 100; неверные размеры/cursors — 400.
Стабильная сортировка `(created_at,id)` по возрастанию и непрозрачные cursors,
связанные с owner/filter, предотвращают пересечения/сдвиги между страницами.
У ресурсов каталога, где нет публичного created_at, сервер всё равно сохраняет устойчивые
факты порядка; раскрывать timestamps только ради pagination не нужно. Private responses
не кэшируются в публичном shared cache.

Успех — `{data,meta}` с обязательным `meta.request_id`, необязательной версией artifact
и обязательной pagination только у list operations. Ошибка —
`{error:{code,message,field_errors,retryable,request_id}}`. В subtype конфликта revision
добавляются `current_revision` и канонический безопасный для владельца `reload_url`;
прочие конфликты не раскрывают digests, private response bodies или факты о чужом resource.

| HTTP | Значение |
| --- | --- |
| 400 | Некорректный запрос/схема, превышено ограничение размера/формы |
| 401 | Требуется аутентификация session |
| 403 | Ошибка CSRF / запрещённая роль без раскрытия секрета владельца |
| 404 | Ресурс отсутствует или принадлежит другому владельцу |
| 409 | Конфликт revision / idempotency / версии exercise / state |
| 429 | Ограничение частоты; обязателен Retry-After seconds |
| 503 | Безопасно завершить операцию нельзя; retry/reconcile выполняются явно |

UNSUPPORTED — результат assessed-бизнес-логики с HTTP 200, а не автоматическая HTTP-ошибка
или WRONG. Безопасный fallback provider — 200 с `service_state DEGRADED`. Создание Tutor message
может вернуть 201, если message создан; fallback response явно возвращает 200 DEGRADED.
Health readiness возвращает типизированный безопасный health envelope с 503, если нужные
DB/config недоступны; сбой provider при работающем основном fallback даёт 200 READY и
provider DEGRADED/UNAVAILABLE. Health никогда не возвращает credentials, SQL, текст исключения,
model keys или данные prompts.

Submit может вернуть 202 только для сохранённого SUBMITTED Attempt с ненулевыми
`operation_id`, `snapshot_digest` и `submitted_at`. GET `/api/v1/attempts/{id}/` — повторно
доступный route статуса. Poll через 1/2/4 секунды, затем ручной retry с исходным submit key.
Временный сбой оставляет операцию восстановимой; network failure не означает WRONG.
Наличие background queue не заявляется. Остальные actions по этому контракту синхронны;
неполучаемый через polling 202 не выдаётся.

## Revision, упорядоченный ввод и привязка версии (D-022)

Lifecycle assessed: STARTED -> SUBMITTED -> COMPLETED либо STARTED -> ABANDONED.
COMPLETED имеет outcome CORRECT/WRONG/UNSUPPORTED/INDETERMINATE; outcomes не являются
states. SELF_CHECK использует STARTED -> REVIEWED через явное подтверждённое reveal либо
STARTED -> ABANDONED. Его нельзя отправить на математическую оценку.

Начальная revision равна 1. PUT draft передаёт полный корректный draft `{payload,steps}`,
`contract_version` и `expected_revision`. Сервер проверяет mode/input/step schemas и limits
до замены; expected_revision должен совпадать с текущей revision. Успешные draft, submit и
abandon увеличивают revision на единицу. Help меняет exposure, а не revision draft.
Устаревшие saves возвращают 409 REVISION_CONFLICT с `current_revision` и GET `reload_url`;
clients сохраняют raw input для согласования. State проверяется после точного idempotent replay,
но до редактирования замороженного draft.

Submit передаёт `expected_revision` и `contract_version`, требует Idempotency-Key и замораживает
в `snapshot_digest` точный существующий draft, версию, итоговую revision и упорядоченные steps.
Submit не принимает второй неоднозначный payload ответа. Сначала client отправляет полный draft через PUT,
затем submit с подтверждённой revision. Edits и submit сериализуются; для одного expected_revision
побеждает ровно один. Поздний draft после submit даёт STATE_CONFLICT. Если draft выиграл,
submit со старой revision получает REVISION_CONFLICT. SUBMITTED и терминальные drafts не меняются.

Client steps сохраняют `step_no`, `step_type`, `payload`, `raw_text`. Нумерация `step_no` начинается
с единицы, непрерывна, уникальна, в массиве submit идёт по возрастанию. Перестановка разрешена заменой/
перенумерацией всего STARTED draft. Client не задаёт `step_id`, `normalized_repr` или `parse_status`.
Server возвращает стабильный `step_id` и все шесть полей R02; типы и parse enums неизменны.
Поля subject payload — недоверенные динамические данные, проверяемые по публичной schema
замороженного exercise. Произвольный payload не даёт права запускать код или принимать
математическую истинность. Raw strings и порядок array сохраняются до normalization/digest.

ExerciseVersion неизменяема после publication. Started attempt продолжает использовать
привязанную замороженную версию, даже если её архивировали или заменили. Archival запрещает
новые attempts; checker/version открытой или исторической attempt никогда не заменяется.
Несовпадение версии client предсказуемо даёт VERSION_CONFLICT. Исправление после submit создаёт
новую Attempt в scope владельца со ссылкой `previous_attempt_id`; исходный snapshot не меняется.
Новая содержательная опубликованная версия имеет отдельный exposure key; повышать version,
чтобы обойти eligibility, запрещено и требует review публикации.

## Help, раскрытие и положительный credit (D-022)

Exposure привязан к `(user,exercise_version)` и хранит максимальный help level,
время reveal и предшествующий positive credit. Новая Attempt не очищает эти значения.
Hint/reveal записывается транзакционно до раскрытия проверенного content.
Уровень 0 означает отсутствие помощи; запрошенные уровни 1–3 остаются ограниченными подсказками.
Уровень 3 не должен скрытно раскрывать полное решение одношаговой задачи. Полное решение
возвращается только в явном подтверждённом reveal response и никогда через exercise GET,
обычные Attempt/result, prompt/context, public metadata, cached bundle или source map.

До reveal Tutor выбирает действие hint-bank, принадлежащее привязанной версии и прошедшее
проверку schema. Assessment проверяет owner/exposure/level и записывает help до возврата
подготовленного текста; произвольная сгенерированная математика не показывается.
После reveal ограниченные объяснения экранируются и имеют безопасный fallback.
Tutor не может записывать в Progress или переопределять eligibility. Context привязывается
на сервере к topic/version/attempt. Ограничения ввода/вывода и частоты наследуются из §§9–10/16;
это не разрешение использовать live model.

Help, submit и finalization сериализуются по Exposure. Submit замораживает raw solution;
finalization под lock Exposure фиксирует eligibility decision и атомарно резервирует любой
positive credit. Hint/reveal, сохранённые до submit либо пока Attempt SUBMITTED до finalization,
учитываются при finalization. Pending submit не даёт независимость. После COMPLETED
сохранённое решение неизменяемо; последующий help/reveal не отменяет ранее полученный
independent result. Exposure, показанный последующим GET, может измениться, но записанная
eligibility и награда завершённой attempt остаются замороженными. `eligibility.independent` и
`positive_credit_eligible` описывают замороженное решение для COMPLETED, перспективную server
eligibility для STARTED и false/PENDING до оценки SUBMITTED.

Для independent correct необходимы CORRECT, поддерживаемый проверенный input, отсутствие
более раннего hint/reveal exposure данной версии и предыдущего positive credit. Любой более ранний
hint делает последующую верную работу по той же версии assisted (если применимо —
CORRECT_AFTER_HINT). Reveal блокирует новый positive credit, включая diagnostic correct;
нейтральные completion/history сохраняются. Поддерживаемый DIAGNOSTIC_CORRECT без помощи
считается independent согласно R03. Максимум одно зачтённое positive event на user/version:
повторное завершение с верным ответом остаётся CORRECT и записывается без нового прироста
mastery и без фиктивного WRONG. SELF_CHECK/view/reveal, UNSUPPORTED и INDETERMINATE
не становятся положительным assessed успехом. В Progress поступают только проверенные доменные
свидетельства; числовые deltas, reducers и schema CompletionFact остаются в scope R03/R03A.

## Request identity, восстановление после сбоя и retry (D-023)

Policy операций явно перечисляет idempotent mutations: creates, submit, hints, reveal, next,
finish, self-report; abandon и onboarding complete также сохраняют стабильную identity действия.
PUT draft вместо этого полностью заменяет данные с `expected_revision`; потерянное подтверждение
согласуется через GET. Login, logout и profile patch используют заданную для них семантику
session/update, а не receipts. GET никогда не требует Idempotency-Key.

Receipt scope — owner+operation+key; конкретный resource route включён в digest, поэтому повторный
key для другого объекта той же operation даёт conflict. Если при регистрации identity ещё нет,
bootstrap key связывается с CSRF/session identity; после создания receipt привязывается к новому user.
Credentials не записываются в logs. `request_digest` включает owner, identity operation,
конкретный canonical route, request body и expected_revision (null, если отсутствует).
Канонический UTF-8 JSON сортирует object keys и использует compact separators; порядок array/raw text
сохраняется, NaN/Infinity отклоняются. Математической/Unicode-normalization input не происходит.
Пароли identity requests обрабатываются приватно; receipts/digests никогда не входят в public DTO
или поля логов.

Тот же key и digest возвращает сохранённые HTTP status/body/operation без повторного доменного
действия, повышения подсказки или evidence. Replay проверяется после auth/owner/CSRF/schema gates,
но до текущих проверок revision/state. Другой digest под тем же key возвращает 409
IDEMPOTENCY_CONFLICT. Processing receipts относятся к той же operation; clients опрашивают
каноническое состояние. Finalization также навсегда уникален по неизменяемой identity source и
snapshot/version.

Receipts сохраняются >=604800 секунд (семь дней). Expiry может удалить краткосрочные данные
HTTP replay, но никогда постоянную уникальность source действия/evidence или guard positive credit
на user/version. Retry завершённой attempt после expiry не может повторно отправить её snapshot.
Новая верная Attempt после expiry не может снова начислить credit за ту же версию.
Будущая persistence обязана обеспечивать эти guards через DB constraints и короткие атомарные
transactions, оставляя computation/LLM вне locks. Reference fixtures доказывают допустимые
последовательные исходы, но не PostgreSQL locking.

## Минимальные решения по downstream DTO

DTO описывают wire-данные для §11 и принятого I01, не выдумывая будущие поля ORM.
Session schemas раскрывают state/policy/current item/counters и terminal reason.
POST next принимает `current_item_id` и ADVANCE/SKIP: retry/refresh сохраняет выбранный элемент
и не резервирует следующий. GET восстанавливает его. Next с другим key для уже использованного/
устаревшего `current_item_id` конфликтует вместо пропуска двух элементов. Finish окончателен;
retry не может выбрать новый item. Diagnostics ограничены 10; результаты с help/reveal/skip остаются
нейтральными, как требует §10. NO_CANDIDATE разрешает START_ZERO по явному выбору onboarding.

Practice раскрывает неизменяемые target/origin, причину выбора, server streak и безопасный return route.
У пользователя одна активная session; create при уже активной возвращает STATE_CONFLICT
(точный receipt retry возвращает исходную session). Не более семи items, включая skip.
Успех — три независимых правильных ответа на разных версиях либо mastery>=70/confidence>=60
после >=1 item. Wrong/help/reveal/unsupported/skip сбрасывают streak. Если origin архивирован,
родителя/catalogue выбирает server. Client не выбирает произвольный checker, candidate, streak или
вердикт успеха. Finish reason — намерение, проверяемое server policy, а не истина, заданная client.

Progress DTO возвращают server projections/history; client не задаёт mastery, confidence или events.
Self-reports допускаются один раз на skill только до assessed evidence согласно onboarding policy;
повторы возвращают `already_reported_skill_codes` без дополнительного event. Они не доказывают mastery.
Агрегат Topic взвешивается по mappings во владении Content. Dynamic raw payload — единственный
преднамеренно открытый объект данных; metadata и response DTO закрыты от дополнительных полей.
Дополнительные subject/UI fields требуют additive contract review; эта schema не определяет
скрытые правила корректности или широкие непрозрачные response objects.

## Проверка и передача

`python -m unittest discover -s tests -p test_r02a_contract.py -v` проверяет официальную
структурную schema OAS 3.1 (источник указан рядом со schemas), meta-schemas DTO,
разрешение refs offline, все routes §11, wire fixtures и негативные формы, замороженные имена/
примеры R02, требования auth/CSRF/header/revision, утечки secrets и health allowlists.
Последовательные сценарии охватывают оба порядка edit/submit, help/reveal до/после pending/
completed submit, exposure между attempts, retry с совпадающим/разным digest, безопасный owner 404,
архивацию version, SELF_CHECK, нейтральные исходы, независимость диагностики, повторную
finalization и expiry receipt. Одна проверка schema не доказывает отсутствие prose,
эквивалентной ответу; по-прежнему нужны человеческое ревью публикации/hint-bank и последующие
leakage tests.

Восемь существующих канонических checks не меняются. Отдельный проверенный шаг CI запускает
эту suite; PostgreSQL fresh-install и интеграция locking/runtime относятся к последующей реализации,
а не этому reference. Digest candidate, фактические команды/результаты/ограничения и human gate
указаны в `../../docs/agent-traces/MS7-R02A.md`. Принятый digest записывается только после
ревью финального artifact Владимиром и соответствующего успешного CI на итоговом SHA.
