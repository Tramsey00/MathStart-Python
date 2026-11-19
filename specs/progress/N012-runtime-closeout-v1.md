# MS-N012: Progress runtime / contract closeout v1

## Решение и полномочия

19.11.2026 пользователь передал подтверждение Руслана R03A / ADR-0005 и явно
поручил реализацию MS-N012. Подтверждены нижеуказанные runtime решения, включая
проверки на отдельной PostgreSQL. Issue #98; base main:
`d8d76f1d08e4eecca0a6f7eb20369029e4649c73` (N011, PR #95).

Это текущий closeout для реализации N012. Historical Proposed/PENDING в frozen
R03A/ADR-0005 описывают прежний этап; их bytes, fixtures и receipts не переписаны.
Принятие контрактных решений не является приёмкой реализации, независимым ревью,
решением о merge или разрешением production deploy.

## Подтверждённые решения

1. ProgressEvent сохраняет `policy_version=progress-v1`. Новые CompletionFact и
   UserSkillState используют `progress-v1.1`. Числовой R03, deltas, difficulty,
   repeat/reset, clamp/ROUND_HALF_UP, negative-evidence guards и старый replay
   неизменны. Binary float не принимается в delivery и не участвует в вычислении.
2. Authoritative CompletionFact принадлежит Assessment. Progress хранит immutable
   mirror и не импортирует Assessment ORM. Междоменный вход — detached immutable
   Delivery и серверный CompletedAttempt read projection с owner, version, mode,
   terminal instant, mapped skills, frozen outcome/eligibility и полным evidence.
   Входные events/facts сверяются со всеми этими authoritative данными.
3. Production adapter требует существующую COMPLETED owned attempt и соответствие
   версии и mapped skill. SELF_CHECK, STARTED/SUBMITTED, отсутствие source, другой
   owner/version/skill, неподтверждённый verdict или независимость не принимаются.
   Native reader сейчас fail-closed: N009 не хранит COMPLETED/outcome/authoritative
   CompletionFact. Их транзакционная запись и завершение reader принадлежат N013.
   Positive Progress intake проверен на явно доверенном серверном projection fixture,
   с реальными PostgreSQL Users/Knowledge/ExerciseVersion mappings. Это проверка
   consumer N012, не фиктивная реализация finalization N013.
4. `completion_id` уникален глобально; `(attempt_id,skill_id)` также уникален навсегда.
   Один attempt сохраняет одинаковые owner/terminal instant/version по всем skills.
   Exact canonical retry — no-op. Любое расхождение identity/source/payload — conflict,
   без перезаписи или частичного commit. Event ID и source tuple также постоянны.
5. Recent-ten включает все завершённые оцениваемые попытки конкретного skill,
   в том числе нейтральные. Порядок — UTC completed_at, затем attempt_id. Нейтральный
   fact может снять MASTERED, но не меняет mastery/confidence/evidence_count/
   last_updated и numerical cache. Fake WRONG/reveal events для окна не создаются.
6. Поздний event вызывает полный числовой replay user/skill по
   `(occurred_at,event_id,policy_version)`. Поздний fact переигрывает status-only
   mirror поверх сохранённого проверенного numerical result. Полный replay v1.1
   даёт тот же полный result/diagnostics. Неизвестные policies отклоняются.
7. Self-report — отдельное аутентифицированное явное действие Progress: один раз
   на skill, до уже известных assessed events/completions. Повтор не добавляет event;
   после assessment — отказ. Reviewed legacy backfill проверяется в полном replay
   order по R03; implicit inference завершений или новых IDs запрещён.
8. Neutral CompletionFact не является numeric evidence и не увеличивает coverage.
   TopicMastery/Confidence — Decimal importance-weighted means Content mappings;
   coverage counts — distinct PRIMARY skills с validated assessed ProgressEvents,
   без self-report/reveal. `total_skill_count=0` означает отсутствие assessed skills,
   не 0% знаний; UI-интерпретация остаётся N015.

## Persistence, транзакции и версии

Миграция v01_0008 добавляет progress_attempt_binding, progress_event,
progress_completion, progress_user_skill_state и permanent self-report receipts.
User/skill FK сохраняют исторические ссылки. Source identifiers — Text, включая
старые непустые строковые IDs; completion UUID не переназначается. Исходный
verified authority/provenance сохраняется вместе с mirror; source identity не
зависит от receipt expiry. UPDATE/DELETE immutable rows и TRUNCATE запрещены PG
triggers, в том числе schema owner; runtime имеет минимальные INSERT/read grants
и UPDATE только rebuildable state. Прежние migrations не редактируются.

Все global identity/attempt locks берутся до scope locks, в одном сортированном
порядке. Все affected scopes проецируются в той же transaction. Public ingest
и self-report имеют SAVEPOINT: даже пойманный caller-ом отказ не оставляет часть
evidence в внешней транзакции. Domain service не делает commit — N013 сможет
использовать его в своей finalization transaction без второй записи истории.

R03 runtime copy побайтно совпадает с pinned reference; R03A имеет только замену
импорта на тот же runtime R03. Дубликата числовых формул в сервисе нет.
`policy-versions-v1.json` хранит source SHA и hashes (LF); runtime проверяет свои
пины, в том числе в API image без scripts/. Старые reference files не менялись.

Для schema installation остаются reviewed preview/apply/check; N009/N011 schema
v01_0007 обновляется профилем TARGET_0007. FRESH и target upgrade проверяются
штатным inventory manifest. Compose schema-update и host-dev поддерживают этот
профиль, startup не выполняет DDL, seed, import или publication.

CLI `python -m backend.progress.cli replay --user-id ... --skill-code ...` по
умолчанию rollback-only. `--apply` разрешён для v1.1; `--policy progress-v1`
воспроизводит прежнюю числовую историю без её переинтерпретации/перезаписи.
`import-legacy --file ... --reviewed-sha256 ...` требует явно проверенный source
с полным legacy authority context. IDs/outcomes не выводятся из событий.

## HTTP и typed clients

Canonical read/self-report routes R02A реализуются без изменения frozen artifact:
GET /api/v1/progress/skills/, topics/, events/ и POST self-reports/.
Дополнительный owner-only GET /api/v1/progress/completions/ показывает нейтральную
историю без подмены её событиями. Это read model N012, не Assessment finalization.
Операции/DTO описаны в http-n012-v1.json и schemas/read-v1.schema.json.

Read schema аддитивно сохраняет legacy string event/attempt IDs вместо их
замены фиктивными UUID. Native IDs остаются UUID. Версии в DTO закрыты на v1/v1.1;
frozen schema/OpenAPI/fixtures сохранены. Нет public write API для events, facts,
mastery, outcome или eligibility. Нет UI N015.

Auth/session revalidation, CSRF, private/no-store, owner-scoped signed pagination
и закрытые response schemas действуют на каждом маршруте. GET не создаёт state.
Events/completions используют stable ingestion order для pagination; logical replay
и recent-ten имеют отдельный frozen порядок. Topic/skill pagination основана на
immutable slug/code. Owner/kind/page_size входят в подписанный cursor scope.
Числа выдаются как JSON decimal tokens без промежуточного float; frontend только
показывает server projections, не пересчитывает authoritative knowledge.

## Приёмка и граница

Обязательные доказательства: pure R03/R03A golden parity, online/full replay equality,
late delivery, neutral MASTERED→LEARNING с неизменными numbers/time, global foreign-owner
identity races, duplicate no-op, atomic refusal, migration fresh/upgrade/ACL,
retained legacy IDs и own HTTP privacy. Actual SHA/tree/results — в карточке/PR.

N013: authoritative Assessment finalization, AnalysisRecord/CompletionFact/source
reader, Exposure credit reservation и persisted end-to-end loop. N015: интерфейс.
Ни эти части, ни изменения учебного банка/материалов, LLM/provider, production
deploy или merge в N012 не входят.
