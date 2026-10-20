# Аудит документации, процесса и собственного Engineering Harness

Дата:20.10.2026, Europe/Moscow. Одно поручение, один исполнитель; субагенты и
автоматическая оркестрация не использовались. Статус: подготовка к отдельному
ревью; человеческая приёмка и main merge не заявлены.

## Проверенная база и scope

Основной root `C:/Projects/MathStart-Python`, исходная ветка main, HEAD
`1a015f7513933901e8bb252e94c660e4383b6b0e`, tree `eaf04bd26e1352b999320662e922b5d09df6c4e1`.
До правок dirty tree пуст. Fetch origin/main успешно выполнен; main...origin/main
0/0. Ветка создана от этой базы, затем по уточнению пользователя переименована
в **docs-and-workflow-cleanup**, без codex/. Изменений/коммитов в main нет.
Отдельные worktree/старые очереди не поднимались; reset/force/merge не выполнялись.

Проверены реальные imports/build inputs, locks/manifests, Dockerfile/Compose,
CI/job IDs/registry, scripts и прямые потребители. Аудит не реализует новые
учебные функции, UI или игровые механики. Existing site/database/volumes и
защищённый acceptance stack не использовались для tests.

## Что есть в продукте и что остаётся проектом

| Область | Реальное состояние / основание |
| --- | --- |
| Платформа | FastAPI/Pydantic, SQLAlchemy/Alembic/PostgreSQL, React Router SSG; backend/, frontend/, deploy/, locks и ADR-0006 |
| Content | Reviewed sources → immutable inputs → React build → fenced publication journal/gate/descriptor + HTTP probes; backend/content, frontend/build_public.py, READ_RUNTIME |
| Identity/staff | Совместимый hash verifier, PostgreSQL opaque sessions/receipts/cutover, CSRF/owner/permission-bound API, React account/admin shells; backend/users, backend/staff |
| Учебный контент | 263 lesson sources и retained grade10; source HTML/math/JS/SVG/URL/media не менялись; текущий code source check и preservation отдельно |
| Onboarding/self-check | Выбор режима сохраняется; существующий reveal HTML не assessed evidence, чтение не mastery |
| Knowledge/Assessment/Progress | Контракты/pure graph/Decimal/replay fixtures; product models/ingest/read UI будущие, tests не доказывают persistence |
| Analyzer/Tutor/Adaptive/Product LLM | Специфицированы, не работающий runtime; provider/model/budget/policy требуют будущих решений |
| Редизайн/геймификация | Подготовлены требования/бриф/task skills; конкретный внешний вид/libraries/mechanics/storage не выбраны |
| Миграция | PR54 и PR55 завершены/приняты; прежние exact-SHA results в maintenance, не evidence новой ветки |

Существенный дефект исходной документации: root architecture после нового
вводного абзаца всё ещё содержала Django context/deploy/auth diagrams,
templates/DRF/ORM/transaction.atomic, старую package tree, PostgreSQL transition,
manage.py checks и список исключённых FastAPI/React. Весь документ теперь
согласован с реальным кодом, отдельно описывает implemented/future/open choices.
Таблица версий взята из manifests/locks/CI/images, без обновления dependencies
или latest. Numeric patch image tag не выдуман по digest.

## Вывод собственного Harness и зависимостей

Проверен не только FakeAdapter: весь harness CLI/runner/lifecycle/contracts/tools,
task manifest, schemas, tests, repository command routing, CI, source registry,
preservation и import graph. В backend/, product CLIs, frontend build и image
entry points нет импорта собственного harness. Ни API, ни publisher, ни
identity/staff операторские команды не вызывают его. Вне его каталогов были:

| Потребитель | Решение |
| --- | --- |
| scripts/target_check.py | Использовал только `_safe_diagnostic`; bounded redaction перенесён без изменения правил в scripts/verification_diagnostics.py |
| tests/test_migration_r03_verification.py | Сняты только nested runner/VerificationOutcome assertions; registry/group/empty/timeout/missing/receipt/PG/privacy/CI provenance checks сохранены |
| tests/harness/test_canonical_verification.py | Общие list/skip/failure selection проверки сохранены в product R03 suite; runner recursion/CLI cases сняты вместе с runner |
| verify_repo/target_verification | Только Harness suite убран; было16 checks/6 pure, стало15/5. Product group IDs и commands сохранены, retired harness group не маскируется PASS |
| CI | Workflow `Harness verification`, job `verify` и все Migration job IDs сохранены; выполняют product contracts. Добавлены current queue/source checks, docs/skills triggers |
| Locks/images/Compose | Ненужной отдельной Harness dependency нет. jsonschema/psycopg нужны product checks; locks/images не повышались |
| Future tasks/gates | 8 Harness-only карточек REMOVED_FROM_PLAN; G1, D-026/027, OD-12/13/14, NFR-19, AT-13 сняты. Product LLM/parser safety/eval/rates остаются |
| Mixed report/eval tasks | R16 описывает фактические Codex/instructions/task skills/check/review/fixes; R14 сохраняет Analyzer/Tutor eval без Harness12/three-owner-run |

Удалены ровно40 отслеживаемых файлов из harness/, specs/harness/, tests/harness/.
Пофайловые original byte count/SHA256 и причины —
[карта изменений](../../specs/maintenance/docs-workflow-dispositions.json).
Оригиналы доступны по исходному HEAD; удалённые tasks не объявлены выполненными.
Codex runtime не изменяется. Продуктовые API/auth/PG/migrations/content/frontend/
security/install/recovery/combined checks сохранены. Исторические approval/receipts
и post-django-preservation.json не переписаны.

Preservation сохраняет прежние trusted hashes и дополняется отдельной картой
ровно изменённых current файлов/retired subsystem. Для каждого проверяется
original blob из фиксированного HEAD, before hash/size и actual after hash либо
точное отсутствие removed path. Нет wildcard освобождения retained content;
unknown change/deletion остаётся FAIL. Новые negative tests проверяют drift,
неизвестные/cyclic/retired dependencies, неверное соответствие source IDs.

## GitHub status checks

Read-only GitHub API20.10: main SHA совпал с local; branch response сообщает
protected:false, protection.enabled:false, required contexts/checks пусты;
repository rulesets вернул []. Административный endpoint required_status_checks
вернул403 Resource not accessible by integration: отдельная admin-проверка
недоступна. Поэтому не делается вывод о настройках, не видимых connector.
Название workflow/job оставлено, никакие branch protection settings не менялись.
Открытого PR этой ветки на момент начала не найдено. Old green CI не доказывает
готовность нового candidate; required combined runtime CI остаётся обязательным.

## Источники пользователя и метод просмотра

Весь отслеживаемый Markdown набор на исходном HEAD: **67 файлов**.
Выполнен full-text scan по текущей платформе/командам/owners/workflow/Harness,
просмотр структуры и ссылок; ключевые architecture/product/specification,
verification/runtime/release/recovery, domain/API/UX и Harness consumers разобраны
по существу. Это первичный аудит, не правило перечитывать всю историю при каждом
задании. Dependencies/node_modules/venvs/generated dirs/var logs исключены.
Tracked curriculum/INDEX включён как нужный source navigation artifact.

Desktop migration MD доступен, byte-identical Git копии:
`c5a554e3911bdb43db28d67fd02d26e38d50b2820e1154a272d89ecb44b1faae`.
Оба Desktop PDF доступны: migration60 pages,
SHA256 `a0c72fda223f86622d01665eaa7ec9d854c7b0b3014de38174f9ad4c582eb66e`;
v7.1 114 pages,
SHA256 `e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd`.
Прочитаны через pypdf text extraction в bundled runtime, относящиеся к scope
требования сверены с полной Git Markdown/source-card транскрипцией. Visual PDF
layout QA не проводился и для исходных документов не заявляется. Оригиналы на
Desktop не изменены. LMS/полные лекции/недоступные внешние источники заново не
проверялись; их прежние source/time records не выдаются за новый просмотр.

## Классификация оставшихся Django/Harness упоминаний

| Класс | Где / почему оставлено |
| --- | --- |
| Устаревшее описание платформы | Исправлено в root architecture, product admin, lesson guides, template commands, submission draft, testing/setup. Старые несуществующие manage.py/collectstatic не являются active commands |
| Необходимая совместимость | backend/users/passwords/legacy_proof/notices, retained django_* tables/history, hash/signing/cursor/staff mapping contracts. Это самостоятельные target adapters, не runtime импорт Django |
| Исторический факт | ADR-0001/исторические части ADR-0006, migration input, parity/evidence ledgers, source_card_text, old approvals/receipts и course attribution. Удалять их ради нулевого слова нельзя |
| Изолированный oracle | docs/legacy-oracle, historical comparisons в CI/backend tests и pre-admission legacy return; отдельный pin/interpreter, никогда Django в target |
| Frozen domain/API/UI source | R02/R03/R02A/R03A и I01/I02/I03 сохраняют exact source semantics и статусы. Framework wording применяется через ADR-0006/current adapters; [карта](../../specs/current-contracts.md) явно отделяет историю от текущих инструкций |
| Собственный Harness | Только retirement/history, legacy source fields, old accepted CI label и preservation paths; импортов/исполнения нет |
| Слово harness в test fixture | tests/test_i03_identity_api.js называет так локальный JS test fixture, deploy/RECOVERY упоминает прежний CookieConflict test failure; это не собственная engineering программа |

## Документы и процесс после изменения

AGENTS → ARCHITECTURE → relevant PRODUCT/full ТЗ → docs/tasks/INDEX → task skill
→ related contracts/runbooks. README — пользовательский вход, не обязательный
посредник. Старые личные очереди не действуют. Стабильные52 IDs и115 source edges
сохранены буквально; current workflow fields отдельно. Новая очередь24 detailed
skills без персональных владельцев/моделей/субагентов, с зависимостями и human gates.
Восемь сняты, пять сохраняют выполненный baseline,39 будущих адаптированы/объединены.

ТЗ остаётся существующей полной Markdown редакцией32 глав; §§6–11 data/exercise/
Progress/math/Tutor/HTTP сохранены целиком и проверяются против исходного HEAD.
Product defaults/eval/security/backup/performance сохранены; история52 карточек
доступна полностью в source registry. New draft HUMAN_PENDING, old G0 approvals
на него не переносятся. Report/course требования не приписывают преподавателю
неподтверждённое согласование снятия или обязательность собственной программы.

Дизайн-бриф фиксирует code/source audit, а не новый visual/user research PASS.
Три направления и library decision → design system → pilot → rollout; future
exercise/progress prototypes маркируются. Gamification spec определит педагогику,
правила/лимиты/help/reveal/anti-duplicates/UI/data owner; XP/посещения/чтение
не становятся mastery. Ни один из этих новых механизмов сейчас не внедрён.

## Инвентарь Markdown исходного HEAD

Категория «до» отмечает противоречия, исправленные этим поручением; исторические
originals/approvals сохраняются. Нормативность frozen semantics не отменяет
proposed status и не делает старые platform/owner указания текущими.

| Документ | Категория до | Применение после | Строк / исходный SHA256 (prefix) | Вывод |
| --- | --- | --- | --- | --- |
| [.github/ISSUE_TEMPLATE/task.md](../../.github/ISSUE_TEMPLATE/task.md) | Устаревший/противоречивый | Действующий справочный | 113 / `6067a242eb22` | Исправлено в этой ветке: текущие runtime/workflow/команды вместо прежних описаний. Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [.github/PULL_REQUEST_TEMPLATE.md](../../.github/PULL_REQUEST_TEMPLATE.md) | Действующий справочный | Действующий справочный | 142 / `adf3094b9d75` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [AGENTS.md](../../AGENTS.md) | Действующий нормативный | Действующий нормативный | 63 / `74cb95005536` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [ARCHITECTURE.md](../../ARCHITECTURE.md) | Устаревший/противоречивый | Действующий нормативный | 1676 / `50de46439afa` | Исправлено в этой ветке: текущие runtime/workflow/команды вместо прежних описаний. Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [PRODUCT.md](../../PRODUCT.md) | Устаревший/противоречивый | Действующий нормативный | 703 / `a2d9b4a5c70a` | Исправлено в этой ветке: текущие runtime/workflow/команды вместо прежних описаний. Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [README.md](../../README.md) | Действующий справочный | Действующий справочный | 82 / `26aef9fd9428` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [backend/READ_RUNTIME.md](../../backend/READ_RUNTIME.md) | Действующий справочный | Действующий справочный | 342 / `604150df2049` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [backend/TESTING.md](../../backend/TESTING.md) | Устаревший/противоречивый | Действующий справочный | 147 / `4d8a421b5c64` | Исправлено в этой ветке: текущие runtime/workflow/команды вместо прежних описаний. Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [backend/infrastructure/http/README.md](../../backend/infrastructure/http/README.md) | Действующий справочный | Действующий справочный | 100 / `4409797ba8f1` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [backend/users/THIRD-PARTY-NOTICES.md](../../backend/users/THIRD-PARTY-NOTICES.md) | Действующий справочный | Действующий справочный | 14 / `8adf1d29ba4a` | Обязательная атрибуция password data/license; Django не runtime dependency. |
| [curriculum/INDEX.md](../../curriculum/INDEX.md) | Действующий справочный | Действующий справочный | 494 / `13ebd02b2bf9` | Отслеживаемый навигационный индекс учебных источников; не менять при документационной очистке. |
| [curriculum/README.md](../../curriculum/README.md) | Устаревший/противоречивый | Действующий справочный | 163 / `7abf77f2b126` | Исправлено в этой ветке: текущие runtime/workflow/команды вместо прежних описаний. Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [deploy/README.md](../../deploy/README.md) | Действующий справочный | Действующий справочный | 87 / `bf59943463f9` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [deploy/RECOVERY.md](../../deploy/RECOVERY.md) | Действующий справочный | Действующий справочный | 180 / `05238740c599` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [deploy/RELEASE.md](../../deploy/RELEASE.md) | Действующий справочный | Действующий справочный | 181 / `a2a0b1ec1aa6` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [docs/adr/ADR-0001-preserve-django.md](../../docs/adr/ADR-0001-preserve-django.md) | Исторический | Исторический | 506 / `42bdb4c23e27` | Прежний scope/стадия; не новые назначения. Текущая платформа/очередь имеют приоритет. |
| [docs/adr/ADR-0002-exercise-contract-architecture.md](../../docs/adr/ADR-0002-exercise-contract-architecture.md) | Действующий нормативный | Действующий нормативный | 363 / `0c49ead74a4a` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [docs/adr/ADR-0003-knowledge-progress-semantics.md](../../docs/adr/ADR-0003-knowledge-progress-semantics.md) | Действующий нормативный | Действующий нормативный | 55 / `bb38e13b3c70` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [docs/adr/ADR-0004-http-eligibility-addendum.md](../../docs/adr/ADR-0004-http-eligibility-addendum.md) | Действующий нормативный | Действующий нормативный | 96 / `9663b6365181` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [docs/adr/ADR-0005-completion-fact.md](../../docs/adr/ADR-0005-completion-fact.md) | Действующий нормативный | Действующий нормативный | 323 / `111b9f9f59b8` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [docs/adr/ADR-0006-react-fastapi-migration.md](../../docs/adr/ADR-0006-react-fastapi-migration.md) | Действующий нормативный | Действующий нормативный | 210 / `37e3f1c2e1a9` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [docs/adr/ADR-TEMPLATE.md](../../docs/adr/ADR-TEMPLATE.md) | Действующий справочный | Действующий справочный | 277 / `ceff99cdc580` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [docs/architecture.md](../../docs/architecture.md) | Действующий справочный | Действующий справочный | 9 / `0853c32e5451` | Справочный Content pointer; основная архитектура только корневая ARCHITECTURE.md. |
| [docs/editing-lessons.md](../../docs/editing-lessons.md) | Устаревший/противоречивый | Действующий справочный | 256 / `d4cf53089b23` | Исправлено в этой ветке: текущие runtime/workflow/команды вместо прежних описаний. Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [docs/legacy-oracle.md](../../docs/legacy-oracle.md) | Действующий справочный | Действующий справочный | 63 / `1ef5e41eb092` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [docs/lesson-theme.md](../../docs/lesson-theme.md) | Устаревший/противоречивый | Действующий справочный | 274 / `7815b55157bf` | Исправлено в этой ветке: текущие runtime/workflow/команды вместо прежних описаний. Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [docs/local-development.md](../../docs/local-development.md) | Действующий справочный | Действующий справочный | 37 / `4850e00ac701` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [docs/maintenance.md](../../docs/maintenance.md) | Действующий справочный | Действующий справочный | 59 / `bca6c9d45721` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [docs/runbooks/postgres-dev-test.md](../../docs/runbooks/postgres-dev-test.md) | Действующий справочный | Действующий справочный | 10 / `1c7e7931b845` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [docs/specifications/technical-spec-v7.2-draft.md](../../docs/specifications/technical-spec-v7.2-draft.md) | Устаревший/противоречивый | Действующий нормативный | 3908 / `1160bcdd0d69` | Исправлено в этой ветке: текущие runtime/workflow/команды вместо прежних описаний. Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [docs/specifications/technical-spec-v7.2-provenance.md](../../docs/specifications/technical-spec-v7.2-provenance.md) | Действующий справочный | Действующий справочный | 45 / `f4500dc96a37` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [docs/submission/C-16-draft.md](../../docs/submission/C-16-draft.md) | Устаревший/противоречивый | Действующий справочный | 33 / `938b77ee749f` | Исправлено в этой ветке: текущие runtime/workflow/команды вместо прежних описаний. Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [docs/target-runtime.md](../../docs/target-runtime.md) | Действующий справочный | Действующий справочный | 208 / `d7a66e98e7a7` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [docs/ux/MS6-I01-api-needs.md](../../docs/ux/MS6-I01-api-needs.md) | Исторический | Исторический | 29 / `2233c1c5d4aa` | Прежний scope/стадия; не новые назначения. Текущая платформа/очередь имеют приоритет. |
| [docs/ux/MS6-I01-screen-map.md](../../docs/ux/MS6-I01-screen-map.md) | Исторический | Исторический | 101 / `bf8b4da38527` | Прежний scope/стадия; не новые назначения. Текущая платформа/очередь имеют приоритет. |
| [docs/ux/MS6-I01-source-notes.md](../../docs/ux/MS6-I01-source-notes.md) | Исторический | Исторический | 55 / `6a3dbdd52c8a` | Прежний scope/стадия; не новые назначения. Текущая платформа/очередь имеют приоритет. |
| [docs/ux/MS6-I01-states-matrix.md](../../docs/ux/MS6-I01-states-matrix.md) | Исторический | Исторический | 49 / `672f01889eb3` | Прежний scope/стадия; не новые назначения. Текущая платформа/очередь имеют приоритет. |
| [docs/ux/MS6-I01-ux-spec.md](../../docs/ux/MS6-I01-ux-spec.md) | Исторический | Исторический | 69 / `ee9e9b12b200` | Прежний scope/стадия; не новые назначения. Текущая платформа/очередь имеют приоритет. |
| [docs/ux/MS6-I01-wireframes.md](../../docs/ux/MS6-I01-wireframes.md) | Исторический | Исторический | 16 / `f58e779f7de9` | Прежний scope/стадия; не новые назначения. Текущая платформа/очередь имеют приоритет. |
| [frontend/README.md](../../frontend/README.md) | Действующий справочный | Действующий справочный | 46 / `af926136192d` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [skills/verification/SKILL.md](../../skills/verification/SKILL.md) | Действующий справочный | Действующий справочный | 10 / `2f42033beeda` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/SPEC-TEMPLATE.md](../../specs/SPEC-TEMPLATE.md) | Устаревший/противоречивый | Действующий справочный | 470 / `363ffceb3408` | Исправлено в этой ветке: текущие runtime/workflow/команды вместо прежних описаний. Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/api/MS7-R02A-http-eligibility.md](../../specs/api/MS7-R02A-http-eligibility.md) | Действующий нормативный | Действующий нормативный | 264 / `1f3cd44b32e5` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [specs/api/MS7-V02-grades-runtime.md](../../specs/api/MS7-V02-grades-runtime.md) | Действующий нормативный | Действующий нормативный | 95 / `cd9e2e4f2622` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [specs/api/schemas/README.md](../../specs/api/schemas/README.md) | Действующий нормативный | Действующий нормативный | 24 / `484e07054322` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [specs/exercises/R02-exercise-architecture.md](../../specs/exercises/R02-exercise-architecture.md) | Действующий нормативный | Действующий нормативный | 485 / `9823fd311173` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [specs/harness/README.md](https://github.com/Tramsey00/MathStart-Python/blob/1a015f7513933901e8bb252e94c660e4383b6b0e/specs/harness/README.md) | Исторический | Исторический, выведен | 150 / `748e69097d4a` | Удалён текущий файл; оригинал40-file retirement сохранён в Git. |
| [specs/harness/adapter-protocol-v1.md](https://github.com/Tramsey00/MathStart-Python/blob/1a015f7513933901e8bb252e94c660e4383b6b0e/specs/harness/adapter-protocol-v1.md) | Исторический | Исторический, выведен | 423 / `0bd9b33af425` | Удалён текущий файл; оригинал40-file retirement сохранён в Git. |
| [specs/knowledge/R03-knowledge-graph.md](../../specs/knowledge/R03-knowledge-graph.md) | Действующий нормативный | Действующий нормативный | 78 / `e6114118d666` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md](../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md) | Исторический | Исторический | 1778 / `c5a554e3911b` | Прежний scope/стадия; не новые назначения. Текущая платформа/очередь имеют приоритет. |
| [specs/migration/README.md](../../specs/migration/README.md) | Действующий справочный | Действующий справочный | 29 / `71219157f83c` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/migration/r02-v1/README.md](../../specs/migration/r02-v1/README.md) | Действующий справочный | Действующий справочный | 64 / `30e3bd19e54a` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/migration/r02-v1/adapters-v1.md](../../specs/migration/r02-v1/adapters-v1.md) | Действующий справочный | Действующий справочный | 45 / `7ce74ae8ebeb` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/migration/r02-v1/auth-v1.md](../../specs/migration/r02-v1/auth-v1.md) | Действующий справочный | Действующий справочный | 269 / `0f18279d86ae` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/migration/r02-v1/content-v1.md](../../specs/migration/r02-v1/content-v1.md) | Действующий справочный | Действующий справочный | 272 / `d8e75b2957ae` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/migration/r02-v1/parity-v1.md](../../specs/migration/r02-v1/parity-v1.md) | Действующий справочный | Действующий справочный | 37 / `805506036178` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/migration/r02-v1/platform-v1.md](../../specs/migration/r02-v1/platform-v1.md) | Действующий справочный | Действующий справочный | 213 / `ed300b3594f9` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/migration/r02-v1/staff-v1.md](../../specs/migration/r02-v1/staff-v1.md) | Действующий справочный | Действующий справочный | 142 / `903a4477ef2c` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/migration/r03-v1/README.md](../../specs/migration/r03-v1/README.md) | Действующий справочный | Действующий справочный | 218 / `23970d37aa4f` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/migration/r03-v1/v02-publication/README.md](../../specs/migration/r03-v1/v02-publication/README.md) | Исторический | Исторический | 70 / `327c84c1adfd` | Прежний scope/стадия; не новые назначения. Текущая платформа/очередь имеют приоритет. |
| [specs/progress/BASELINE-v1.md](../../specs/progress/BASELINE-v1.md) | Действующий нормативный | Действующий нормативный | 82 / `78b16f4f1fa0` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [specs/progress/R03-progress-contract.md](../../specs/progress/R03-progress-contract.md) | Действующий нормативный | Действующий нормативный | 101 / `2ec8098921b8` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [specs/progress/R03A-completion-fact.md](../../specs/progress/R03A-completion-fact.md) | Действующий нормативный | Действующий нормативный | 239 / `5589ed4824c4` | Доменные ограничения/принятые решения; source/proposed status и platform adapters различаются. |
| [specs/ui/MS7-I02-ui-foundation.md](../../specs/ui/MS7-I02-ui-foundation.md) | Действующий справочный | Действующий справочный | 400 / `d5052869c8d9` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/ui/MS7-I03-auth-profile-onboarding.md](../../specs/ui/MS7-I03-auth-profile-onboarding.md) | Действующий справочный | Действующий справочный | 622 / `7d79397ac80c` | Источник команд/справки; historical evidence имеет собственный SHA/scope. |
| [specs/ui/site-polish.md](../../specs/ui/site-polish.md) | Исторический | Исторический | 53 / `40e7cc5a9c80` | Прежний scope/стадия; не новые назначения. Текущая платформа/очередь имеют приоритет. |
| [specs/ui/topics-catalogue.md](../../specs/ui/topics-catalogue.md) | Исторический | Исторический | 47 / `0329ccb4827e` | Прежний scope/стадия; не новые назначения. Текущая платформа/очередь имеют приоритет. |

Новые active документы: этот аудит, docs/tasks/INDEX.md + registry.json,
24 skills/tasks/*/SKILL.md, docs/ux/redesign-brief.md, specs/current-contracts.md,
explicit maintenance disposition map. Они дополняют canonical sources, не создают
вторую архитектуру или конкурирующее действующее ТЗ. Source provenance связывает
актуальные полные SHA256; Markdown local links проверяются скриптом.

## Проверки, findings и границы передачи

Начальная среда: Python3.12.10 без target packages, Node24.19.0/npm11.17.0,
Docker Linux engine pipe отсутствует. var/local/venv/Scripts/python.exe,
который старый guide называл подготовленным, не найден; guide исправлен.
Создан отдельный ignored var/docs-cleanup/venv и установлен существующий locked
backend/test runtime без Django/DRF. Сначала ensurepip отказал из-за sandbox TEMP,
затем TEMP перенесён в owned var/docs-cleanup/tmp; pip network install потребовал
разрешённого escalation. Зависимости проекта/lock versions не менялись.

Первичная самопроверка: pip check PASS,7 targeted queue/preservation/redaction
tests PASS. Остальные фактические команды/результаты будут дописаны после
проверки coherent candidate. Это не отдельное ревью. Статус MS-N000
READY_FOR_REVIEW означает готовность к передаче после перечисленных проверок,
не green runtime/CI и не HUMAN_ACCEPTED.

Полный managed PostgreSQL/browser/install/recovery run локально не установлен:
Docker engine остановлен, owned QA resources/legacy interpreter/browser inputs
не подготовлены. Работающий acceptance stack/БД не трогался, daemon не запускался.
Эти ограничения не обходятся fixture success. Mandatory CI нового SHA/PR и
отдельное ревью/приёмка остаются обязательны перед решением о main merge.

Первое будущее доступное задание после приёмки текущего: **MS-N001**.
Его реализация не начиналась. Force push/auto-merge/production changes отсутствуют.

### Результат самопроверки рабочей версии перед коммитом

- Portable pure: PASS5/5 suites,169 tests (18+30+41+32+48),0 skipped.
- Current queue/document/import/CI checks: PASS639.
- Source/current-product reconciliation: PASS931;32 главы/52 disposition IDs,
  все прежние52 source rows/115 edges и полные §§6–11 сохранены.
- Preservation: PASS;802 unchanged baseline files +568 explicit baseline
  dispositions =1370;1627 прежних dispositions и70 task-specific entries
  (40 removed/30 updated), historical hashes не обновлены.
- Stock skill-creator validator:25/25 PASS (24 task skills + verification).
  На Windows потребовался PYTHONUTF8=1; первая попытка с cp1251 не PASS.
- CI YAML parsed: все3 workflows, прежние name/job IDs сохранены.
- `backend.cli check-sources`:279 pages/263 topics; `git diff --check` PASS.

Самопроверка нашла и исправила: stale count16 в platform regression;
проверку moved registry, которая должна проверять и неизменный before, и новый
after; неверное описание пути index output (фактически output-root/INDEX.md).
Попытка обновить frozen R02 README/platform выявлена exact manifest check;
изменения этих двух файлов отменены, их baseline bytes оставлены. Их historical
framework wording объяснён в specs/current-contracts.md. Первоначальные failures
в owned logs сохранены; последующий PASS их не стирает.

Новые implementation/review findings не объявлены независимым review. После
коммита повторная verification должна записать конкретный candidate SHA и
actual default verify_repo outcome. Отдельное ревью и human acceptance PENDING.
