# Дополнение к adapter аутентификации/безопасности v1.0.2

PROPOSED. DTO/OAS/policy замороженного R02A остаются побайтно неизменными. Исходный baseline:
users/http.py, users/views.py, users/services.py, users/models.py и
config/api_http.py/settings.py; независимые тесты users/tests и content/test_grades_api.py.

## Граница wire-протокола

В [карте routes](implemented-routes-v1.json) указаны восемь реализованных операций и точные
имена схем request/response и statuses. Строгий UTF-8 JSON object;
application/json с отсутствующим encoding или UTF-8; raw body <=65536 bytes. Отклонять
некорректный UTF-8/JSON, повторяющиеся ключи на любой глубине, NaN/Infinity, ошибку recursion,
неизвестные поля, неверные типы/boolean-as-ID без coercion. Превышение размера — 400
LIMIT_EXCEEDED; прочие некорректные данные — 400 INVALID_REQUEST с безопасным фиксированным сообщением.
Пустое тело logout должно быть `{}`. Несовпадение HTTP method endpoint — 400 INVALID_REQUEST;
не использовать default FastAPI 422/405 или slash 307. Различия GET/HEAD описаны в карте routes.
Middleware auth/CSRF выполняется до валидации body: для private — anonymous 401, затем CSRF 403
для write, затем проверка формы. Anonymous register/login тоже требуют проверенный CSRF.
Поиск отсутствующего/чужого internal owner — 404 NOT_FOUND; выбранный grade с неверной схемой — 400,
неподдерживаемый сохранённый grade slug — 503, не выдуманный номер.

Успех `{data,meta:{request_id,version:'http-v1'}}`; списки дополняются pagination.
Ошибка `{error:{code,message,field_errors,retryable,request_id}}`; безопасный фиксированный
`field_errors {}`, retryable только для 429/503. В ошибках не должно быть SQL/DSN/password/body/digest/
чужой revision. Сериализация JSON UTF-8, `sort_keys=True`, `ensure_ascii=False` сохраняет байты replay,
даже если jsonb переставляет ключи. Все существующие API responses, включая публичные grades,
имеют Cache-Control: private, no-store. Новые request IDs — UUID; replay возвращает исходные
сохранённые request_id/status/body без изменений. 429 RATE_LIMITED содержит целое Retry-After
seconds >=1. Ошибки базы данных — 503 SERVICE_UNAVAILABLE. CSRF 403 CSRF_FAILED; роль 403 FORBIDDEN;
owner 404; digest 409 IDEMPOTENCY_CONFLICT; state 409 STATE_CONFLICT.

Лимиты policy: 40 steps, 512 expression chars, 128 tokens, nesting 16, 12 numeric digits,
`abs_power10`, 250ms на expression/2000ms на batch относятся к будущим assessed operations;
нельзя утверждать, что текущий identity parser обеспечивает эти domain limits.
UNSUPPORTED/INDETERMINATE assessed 200 и Tutor 200 DEGRADED остаются будущими бизнес-результатами.
Сохранять канонический контракт persisted SUBMITTED с кодом 202 и polling; не придумывать его
для регистрации или публикации.

Существующие API paths без slash возвращают 301 на путь с конечным slash при DEBUG=False,
включая POST (браузер может потерять body); baseline probe фиксирует это поведение, а не 404.
Target явно сохраняет 301 для этих известных paths, но не default FastAPI 307. Клиенты всегда
используют канонические paths со slash и никогда не повторяют mutation вслед за redirect.
Неизвестные API paths возвращают безопасный 404. Небезопасные slash errors в DEBUG — диагностика
разработки, а не семантика deployment. Если ревьюеры предпочтут безопасный 400/404 для небезопасных
запросов без slash, это отдельное одобренное изменение поведения, а не baseline equivalence.

GET grades игнорирует request body (включая некорректный JSON), как подтвердил disposable probe;
разбираются только query parameters. Это различие с разбором JSON mutations сохраняется.
GET CSRF/me также не разбирают JSON body.
Cursor: <=1024 символа; только singleton cursor/page_size, ASCII `size[0-9]{1,3}` и 1..100.
Payload строго `scope/page_size/created_at/id`; int, но не bool, `0<id<2**63`, timestamp с timezone
и нулевым offset, route scope `public:/api/v1/grades/`; salt
`content.grades.http-v1.cursor`. Сохранять Django signing JSONSerializer (compact separators/
ensure_ascii ASCII), необязательную метку zlib compression, URL-safe Base64 без padding,
base62 времени TimestampSigner и salted HMAC signature; baseline loads не применяет max_age.
V02 должен проверить независимые signer vectors old/new с сохранённым verifier key ring.
Новый signer другого формата должен читать неистёкшие legacy cursors до замены их выпуска.

## Credentials и validators

Backend регистрации: username 1..150 символов, UnicodeUsernameValidator
`^[\w.@+-]+\Z`; необязательный корректный email; username уникален, email — нет.
Frontend ограничивает username 30 символами, есть тесты на 30/31; legacy login username
длиной до 150 должен работать. Совпадают Django UserAttributeSimilarityValidator default 0.7
по username/first_name/last_name/email, MinimumLengthValidator 8,
CommonPasswordValidator по списку baseline соответствующей версии и numeric-only validator.
Пароли нельзя обрезать/нормализовать. Некорректная/повторная регистрация — общий ответ 400;
отсутствующий username/неверный password/неактивный login дают одинаковый 401, включая
эквивалентный dummy дорогой hash для отсутствующих пользователей.

Сохранённый password и algorithm/iterations при migration переносятся без изменений;
default hasher baseline — pbkdf2_sha256 (настроенные Django defaults также включают
pbkdf2_sha1, argon2, bcrypt_sha256, scrypt). Hashes независимо проверяются синтетическими
детерминированными salts/vectors и старыми iteration counts, Unicode и неверными паролями.
Инвентаризировать только algorithm/count, никогда реальные hashes/PII. Нулевое число users
в R01 не доказывает совместимость алгоритмов production. V03 выбирает проверенный лицензией
Django-independent verifier; неподдерживаемый algorithm блокирует cutover. Opportunistic rehash
после успешного login допустим по проверенной baseline policy, но массовый reset запрещён.
Маркер unusable-password остаётся непригодным. Создание staff с usable/unusable паролем и их смена
должны сохранять baseline поведение validators.

## Session/CSRF/rate

Один HTTPS origin, непрозрачные sessions в PostgreSQL, session cookie с HttpOnly,
Secure при deployment, SameSite=Lax (CSRF cookie доступна bootstrap flow).
При каждом успешном login выполнять rotation, включая вход того же user; register создаёт
session только для неаутентифицированного пользователя; точный authenticated register replay
session не ротирует. Logout выполняет flush/revoke; expiry/revocation и изменения password
auth-hash аннулируют остальные sessions. При смене staff собственного пароля сохранять
Django update_session_auth_hash: после успеха обновить текущую аутентифицированную session с rotation,
остальные sessions становятся недействительными. При cutover допускается один явный повторный login;
сброс пароля не нужен. Базовые TTL по умолчанию: 1209600 секунд для session и 31449600 для CSRF cookie,
если настройки deployment отличаются и это явно записывает V03. Host allowlist/проверки Origin+Referer,
без permissive CORS или browser JWT/storage. CSRF bootstrap возвращает masked token и может поставить
cookie, не создавая profile/domain write. Проверять tokens до parse; при retry обновлять CSRF.
Очищать все private client caches при logout/loss session. Staff и account не экспортируются через SSG.

Бюджет login: 10 попыток за 300 секунд на HMAC серверного REMOTE_ADDR, общий DB counter lock
между workers. Счётчик увеличивается до аутентификации, в том числе при неверных credentials;
сбрасывается после 300 секунд, вычисленных ПОСЛЕ захвата lock; попытка 11 получает 429 и ceil
оставшегося окна в Retry-After. Произвольный X-Forwarded-For игнорируется. V05 может задать
доверенный список proxy, который удаляет forwarded headers на одном origin; иначе авторитетен
REMOTE_ADDR. Rate limiter только в памяти процесса запрещён.

## Receipt и мост анонимного scope

Сохраняются IdentityReceipt UUID/scope/operation/key_digest/request_digest/user/response/status/
created_at/expires_at и unique(scope,operation,key_digest), согласованные CHECK response/status/user.
key_digest — SHA256 UTF-8 header. request_digest — SHA256 UTF-8 sorted compact JSON,
ensure_ascii=False/allow_nan=False для `{owner,operation,canonical_route,body,expected_revision:body.get(...)}`.
Порядок массива/raw string точен, Unicode/math не нормализуются. Owner регистрации — bootstrap scope;
digest onboarding owner — str(user.pk), scope — `user:<pk>`. Identity replay хранится как минимум
604800 секунд, а уникальность source постоянно; текущий service не удаляет просроченные receipts.
Один key с изменённым digest — 409. Raw password/body в receipt не сохраняются; только request digest
и безопасный результат в private storage.

Registration scope — session `identity_registration_scope`, если он задан, иначе
`'bootstrap:' + legacy salted_hmac('users.register.bootstrap', csrf_secret, algorithm='sha256')`
с Django-совместимым baseline key derivation/signing key. Перед ротацией cookies при login этот scope
переносится. Его нельзя вычислять заново из нового CSRF. Target bridge — private server record,
связывающий старый проверенный fingerprint/ scope CSRF bootstrap с новой непрозрачной session;
необязательный подписанный HttpOnly Secure SameSite=Lax bootstrap ticket содержит непрозрачную случайную
ссылку, никогда user/receipt/digest. Ticket проверяется по подписи, expiry и исходному bootstrap proof
на сервере; факты bridge хранятся >=7 дней; validity/revocation и истечение ticket следуют lifecycle P2 ниже.
Key ring сохраняет необходимые legacy HMAC verifier keys на срок replay window; secrets остаются вне Git.
Исходный scope/digest receipt после появления bridge не меняется.

Все случаи потерянного ответа должны работать на disposable data: (a) DB commit произошёл, body не дошло,
но login cookies получены — тот же owner/key/body воспроизводит результат; (b) потеряны и body, и Set-Cookie —
у клиента осталась исходная CSRF cookie и неизменяемые key/body; проверить исходный bootstrap proof,
восстановить первоначальный scope, проверить пароль из receipt.user, если запрос анонимный, и установить
rotated session; (c) перезагрузка страницы потеряла credentials в памяти — только GET restore, затем явный
повторный login пользователя; никогда не создавать второй аккаунт автоматически; (d) proof/session scope
отсутствует или истёк — безопасный отказ/re-login, никогда lookup receipt только по key; (e) аутентифицированный
другой user, неактивный владелец receipt или несоответствующий password дают общий 409 STATE_CONFLICT.
Same-owner authenticated replay может вернуть безопасный сохранённый результат без хранения password.
Смена scope не должна воспроизводить receipt другого bootstrap, даже если key/body равны.
V03 проверяет импортированный заполненный profile C и гонки; этот дизайн предложен и не объявляется
доступным текущим bridge. Если keys/proof нельзя сохранить, до activation требуется конкретное решение человека
о cutover.

## Контракт frontend

Сохранять исходные login/switcher, тихий initial anonymous 401, contextual GET-only restore/retry,
register 30/backend 150 и реальный grades PK. Pending action хранит неизменяемые сериализованные body/key
только в памяти; при retry обновлять CSRF, не меняя body. Очищать DOM passwords после serialization
и terminal outcome; очищать pending memory при terminal 400/401/form switch/disposal; credentials нельзя
писать в logs/storage/screenshots. Отбрасывать устаревшие ответы по generation/request identity,
чтобы более новое состояние ввода/session имело приоритет; сохранять точный raw student input и порядок
steps в будущих fixtures, не обрезать для маскировки stale conflict. GET не увеличивает mastery и не запускает
diagnostics. Только три onboarding modes сохраняют выбор profile.

## Разъяснение приоритета B07 по ревью

Method 400 для identity endpoints действует только после предыдущих middleware outcomes.
Private identity routes возвращают anonymous 401 до CSRF или проверки method;
authenticated unsafe requests требуют CSRF до endpoint 400/body parsing. Для public identity
resolved routes сначала проверяется unsafe CSRF (отсутствующий/неверный Origin — 403), затем method 400.
GradeListView имеет DRF csrf_exempt и не требует authentication: GET 200, остальные methods 400
независимо от token/Origin. Для account require_GET выполняется после CSRF: безопасные HEAD/OPTIONS/TRACE
дают 405, unsafe без CSRF — 403, unsafe с корректным CSRF — 405. Public pages/sitemap/robots и
unresolved 404 fallback различаются, как указано в content-v1.md; нельзя применять один глобальный
middleware precedence ко всем семействам.

## P2 Lifecycle receipt bridge (предложен, не реализован)

Retention не является разрешением. Private PostgreSQL bridge facts содержат opaque bridge ID,
неизменяемые исходные scope/bootstrap fingerprint, nullable receipt owner (привязывается один раз при commit
регистрации), durable session_lineage_id, текущее session binding и epoch revocation, состояние
ACTIVE/DETACHED/REVOKED/EXPIRED, replay_until >= исходный commit + 604800 секунд, а также версию/expiry/revocation
ticket. Scope/digests/result/uniqueness receipt остаются в IdentityReceipt навсегда согласно текущей policy;
переходы не удаляют и не переписывают их. Менять полномочия bridge может только identity/session service;
cutover import выполняется исключительным target writer после остановки/отзыва старых writers.
Cleanup принадлежит service, не frontend event и не задаче удаления receipts.
[Storage mapping](protocol-storage-mapping-v1.json) описывает логические факты и будущее проверенное
additive DDL, а не migration или дополнительный browser DTO.

Классы proof в таблице переходов:
S = текущая authenticated active owner session с совпадающим bridge session binding и epoch.
B = проверенный ИСХОДНЫЙ bootstrap CSRF proof, точно разрешающий старый scope; свежий request CSRF
обязателен отдельно и не заменяет B.
T = подписанная непросроченная и неотозванная ссылка ticket reference ПЛЮС B; одного ticket недостаточно.
F = свежий login того же владельца ПЛЮС server-authenticated transfer binding от исходной проверенной
Django session/bridge. Одна лишь аутентификация owner не выбирает anonymous receipt scope по key.
Для anonymous replay через B/T также проверяется password для активного receipt.user; для authenticated
replay B/T/F требуется именно этот owner, а не пароль другого user. Ни один proof не разрешает несовпадающие
body/digest/key/operation или неактивного владельца.

Создание bridge сохраняет проверенный исходный scope до ротации cookie и связывает receipt owner
при commit регистрации; затем может устанавливаться session/ticket. DB receipt commit с потерей body
и обеих cookies восстанавливается через B+password, даже если ticket не доставлен. После создания session
точный replay того же authenticated owner не выполняет rotation. Успешное anonymous recovery ротирует
session один раз, аннулирует предыдущее binding/ticket, затем выдаёт новую версию ticket, если они применяются.
Ticket не потребляется разрушительно при первом использовании: пока proof/key/body актуальны, тот же запрос
безопасно воспроизводится; версии и epoch отзывают заменённые tickets. В bridge facts не хранятся raw
password/CSRF/session token.

| Переход | Эффект для bridge / ticket / owner-session | Proof, retry/replay, отказ и неопределённый результат |
| --- | --- | --- |
| Явный logout (authenticated + CSRF, пустое body) | Отозвать текущую session, все bridges и tickets, привязанные к ЕЁ session lineage; увеличить их epoch, очистить binding. Сохранить факты REVOKED и receipts. Другие независимые sessions не меняются. | Возвращать принятый 200 `completed:true` только после durable revoke. Повтор со старой session — 401; replay logout receipt отсутствует. Потеря ответа: очистить private client state, только GET me; anonymous 401 согласует потерю session, результат с активной session требует явного действия пользователя, слепой POST retry запрещён. B/T/F не могут восстановить revoked bridge, даже с тем же owner/password. |
| Переключение account A -> B успешным login | Сначала аутентифицировать B; атомарно отозвать session lineage/bridges/tickets A, очистить прежнее private binding, создать rotated session B. Bridge A нельзя перепривязать к B. Неудачный login оставляет полномочия A. | B не может использовать S/B/T/F или receipt пользователя A; при authenticated mismatch общий 409 STATE_CONFLICT. Повторный login того же user ротирует session, но безопасно переносит его собственный ACTIVE bridge на новое binding/epoch и отзывает старый ticket (нового receipt нет). Неизвестный результат login: GET me; автоматически не повторять login и не использовать pending body A под B. |
| Очистка session / естественное истечение | Истёкшая session непригодна; ACTIVE -> DETACHED, очистить session binding и сделать старый S/epoch недействительными. Исходные bootstrap и актуальный ticket сохраняются до replay_until. Ticket может истечь раньше; это не отзывает identity receipt. | До replay_until восстановление возможно через B+password, authenticated same-owner B/T или F; истёкший/revoked ticket не проходит, но независимый B всё ещё доказывает scope. Одна session/key не проходит проверку: безопасный 409 для регистрации (private auth routes дают 401); чужой authenticated owner — 409. Повторный cleanup идемпотентен и не оживляет REVOKED; неизвестный результат commit cleanup/rebind требует перечитать authoritative facts, успех нельзя угадывать. |
| Cutover Django -> FastAPI | Остановить/отозвать legacy writers и sessions; сохранить receipts/digests/uniqueness и проверенные transfer facts bridge. Неотозванный bridge становится DETACHED; legacy session не аутентифицирует target. Verifier/reference tickets T и proof B сохраняются на replay window. Импортированный F mapping приватен и привязан к owner; bridge нельзя создать только по receipt key. | Допускается ОДИН явный re-login, сброс password не нужен. После входа того же owner перепривязка возможна через F или актуальные B/T. Pending onboarding replay основан независимо на authenticated identity `user:<pk>`. Чужой owner/proof/key/body — 409; отсутствие proof ведёт к fail-closed/re-login, не к новой регистрации. Неизвестная точка cutover: остановить target writes до согласования exclusive writer/import provenance; dual writer и автоматический обратный cutover запрещены. |
| Наступил replay_until / истёк ticket | Истечение ticket отзывает только T; по replay_until bridge становится EXPIRED (факты сохраняются >=7 дней), binding/tickets очищаются. REVOKED остаётся revoked. | Истёкший bridge не выбирает registration scope; GET restore и явный login, без автоматического создания аккаунта/lookup только по key. Существующий onboarding receipt остаётся связанным с owner и replay возможен даже после минимального окна. Повторные переходы/cleanup возвращают то же durable terminal authority state. |

Внутренние lifecycle transitions атомарны в порядке namespace -> отсортированные User ->
receipt, затем bridge/session locks по стабильному ID на rank4 платформы. Revocation/rebind CAS
повторно проверяет epoch, state, owner и session после locks; revocation имеет приоритет над последующим
использованием, ранее завершённый replay остаётся исторической истиной receipt. Одновременный второй rebind
со старым epoch завершается отказом и не создаёт другую session/ticket. Revoked bridges нельзя восстановить.
Естественное истечение/cutover только отсоединяет bridge и не отменяет более ранние logout/account-switch
revocation. Инвалидация auth-hash/security revocation следует logout revocation, а не восстанавливаемому
естественному истечению.

Приоритет ответов остаётся B07: private anonymous 401 до CSRF, unsafe CSRF 403 до body/proof;
затем безопасный 409 STATE_CONFLICT для отсутствующего/недопустимого/revoked/чужого proof bridge,
409 IDEMPOTENCY_CONFLICT для изменённого body при доказанном scope. Нельзя раскрывать наличие чужого
receipt, revision или деталей proof. Storage/неизвестный commit — 503 SERVICE_UNAVAILABLE, не успех.
Автоматический retry только GET. Явный retry регистрации разрешён только пока неизменяемые pending key/body
и действительный proof доступны, с новым request CSRF; terminal failure, logout, account switch, disposal
или form switch очищает pending credentials. При неизвестном результате logout/login выполнить GET me;
при неизвестном результате registration/rebind сначала GET restore и только затем явный replay ТОЙ ЖЕ операции
при валидном proof. Потерянный ответ после отзыва bridge никогда не разрешает его оживление. Generic lifecycle
HTTP endpoint и слепой receipt-based повтор logout не вводятся. V03 должен доказать реальные транзакции,
ticket/signature/keyring, cutover и session races; модель R02 синтетическая.

Epoch в модели — внутренняя CAS observation, а не возможность браузера. Исходный proof B разрешается
сервером в текущие facts; конкурирующий rebind с устаревшим epoch не создаёт эффектов. Позже явный replay
может перечитать facts и повторно доказать B+password, даже после потери cookies, создав rotated session,
но сохранив тот же receipt/result и не создавая новый account.

Identity точки cutover и проверенная provenance import — долговечные private facts identity-service.
Повтор того же завершённого checkpoint — read-only, в том числе после перепривязки bridge к target session;
он не должен снова отсоединить target session. Другой/неизвестный checkpoint или недоказанный exclusive
writer останавливает записи и требует согласования. Аутентификация перед переключением account выполняется
вне locks; затем захватываются namespace/session-lineage locks в стабильном порядке и обе User rows
(старой и новой) по возрастанию PK. Все изменения bridge/session binding используют lineage namespace
и заново проверяют текущий epoch после rank4 locks; cleanup не может присоединить полномочия.
Неудачная аутентификация нового пользователя не отзывает старую session или bridge. ACTIVE committed bridges
обязаны иметь owner и session binding; DETACHED никогда не аутентифицирует старую session.
Новая осознанная регистрация использует собственный заново подтверждённый bootstrap scope/key;
pending replay с потерянным proof нельзя незаметно истолковать как новую регистрацию. Явный onboarding replay
после logout/re-login остаётся доступен через authenticated same-owner user scope независимо от отозванного
анонимного bridge.

Durable `session_lineage_id` сохраняется для поиска отзывов после отсоединения/истечения session binding.
Rotation того же пользователя сохраняет lineage; явный rebind связывает bridge с новой authenticated/recovered
session lineage по epoch CAS. Logout/switch отзывает bridges только уходящего lineage, включая отсоединённые
records, и не отзывает другую независимую session того же владельца.
