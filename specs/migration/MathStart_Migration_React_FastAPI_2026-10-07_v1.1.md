# Техническое задание на перенос текущей версии MathStart на React и FastAPI

Версия 1.1 от 07.10.2026. Программа MS7-MIG. Срок 07.10.2026-13.10.2026 включительно, семь календарных дней. Все даты и часы - Europe/Moscow. Пользователь принял ТЗ с тремя правками: убрать префикс веток, явно включить §17 в карточки и добавить таблицу личных очередей. Эти правки внесены в v1.1. Выполнение задач и закрытие MIG-G0 не заявляются: проверки исходного снимка и отдельные решения участников ещё предстоят.

Изменения v1.1: названия всех веток без префикса codex; §11.1 - три параллельные очереди; в каждой карточке - обязательная адаптация выполненных задач из §17 с deliverable, проверкой и критерием приёмки. Остальные требования v1.0 сохранены.

Заказчик и команда: Руслан, Владимир, Илья. Код и проверки выполняются через Codex; участники задают границы задач, просматривают результат и принимают работу. Документ задаёт полный перенос существующего функционального контура, подготовку нового основного ТЗ и передачу работающей версии. Изменение дизайна и реализация ещё отсутствующих учебных доменов в этот срок не входят.

## 1 Цель и границы результата

К 13.10 должна быть принята текущая версия сайта на React + TypeScript и FastAPI + SQLAlchemy + Alembic с PostgreSQL, с сохранением контента, адресов, данных, безопасности, служебных операций и проверок. React становится frontend текущих страниц; FastAPI становится единственным обслуживающим backend. Django/DRF не требуются для обычного запуска, публикации, миграций, auth и целевой верификации. Исторические миграции и evidence сохраняются как история.

В перенос входят: главная, каталог и структурные страницы; 263 урока и их authored HTML/CSS/JS/SVG/формулы; account UI MS7-I03; identity MS7-V02; grades API; публикация, bootstrap, index и проверки; URL/redirect/sitemap/robots; static/media; staff/admin возможности исходного снимка; окружения, CI, migration upgrade/fresh, backup/restore и документация. Слово «полный» не допускает незаметного исключения admin, служебных команд или сложного виджета.

Не входят: редизайн, новая UI-библиотека с глобальным reset, MUI/shadcn/Tailwind/Motion, новые уроки и массовый JSX conversion, новый assessed exercise runtime, Knowledge/Assessment/Progress persistence, Tutor/Analyzer/adaptive practice, live Product AI, Redis/Celery/микросервисы, новая большая CMS. Существующие reference-контракты, fixtures и Harness сохраняются и проверяются, но не объявляются реализованным продуктом.

Результат - reproducible release candidate и принятый migration gate. Публичное production переключение существующего сервиса выполняется только по принятому runbook и явной записи deployment approval. Если внешняя площадка не определена, проверенная staging/disposable поставка обязательна, публичный deployment остаётся явно отдельным pending действием; это не скрывает отсутствие воспроизводимого запуска.

## 2 Фактические исходные данные

GitHub проверен через API 07.10.2026. Репозиторий: https://github.com/Tramsey00/MathStart-Python. Default branch main: 4df7403208312d73adaa34f00f10b025db686fe4, merge MS7-I03 06.10.2026. Открытых PR на момент проверки: 0. Main push CI 37470970648 завершён SUCCESS на этом SHA: https://github.com/Tramsey00/MathStart-Python/actions/runs/37470970648. Это подтверждение исходной Django-версии; целевая реализация должна получить собственный CI.

Локальный checkout отличается: fix/topics-catalog, HEAD a378ab2f01bd76b514833bf692cb4c7425e90ace, 235 modified tracked files и 8 untracked entries; diff 7206 additions / 10068 deletions. Основной массив - изменения уроков. Не выполнять reset/clean, не игнорировать новые page.css, не переносить только GitHub main, потеряв локальные исправления. Неотслеживаемые output/tmp/var материалы не становятся источниками уроков автоматически.

В локальном дереве 263 lesson.json, 16 page.json site_content, 11 Django HTML templates, 97 lesson-local page.css, 7 lesson-local page.js; существуют также shared scripts. В GitHub main дополнительно есть account template и identity controller, grades runtime и content.0002_grade_created_at. Число локальных шаблонов не описывает полный remote baseline.

PostgreSQL повторно проверен 07.10 в REPEATABLE READ READ ONLY. Версия 16.15. В локальной БД 281 ContentPage: 263 published topic, 2 published grade, 10 published subject, 1 home, 3 published static, 2 unpublished static; итого 279 опубликованных. Redirect 282. Применена только content.0001_initial среди content/users; users_* отсутствуют; Grade.created_at отсутствует. Подробные агрегаты предыдущей проверки: 6 Grade, 12 Subject, 63 Section, 263 LessonPublication, 29 MediaAsset. Эта БД отстаёт от GitHub main; её нельзя stamp как полностью актуальную.

База переноса MIG_BASE_SHA должна объединять проверенный remote main и одобренные локальные изменения контента. Точный SHA появляется в R01 после snapshot PR и проверок; здесь он намеренно не выдуман. Записываются отдельные source manifest, runtime data manifest, source/render digests и remote/local delta. Разница источников и БД не исправляется слепым bootstrap поверх runtime edits.

### 2.1 GitHub результаты и независимая приёмка

| Результат | GitHub факт | Что считать исходным evidence |
| --- | --- | --- |
| R01 | PR 2 merged; Issue 1 closed | Принятый исторический baseline; новую платформу не подтверждает |
| R02 | PR 5 merged; Issue 4 closed | Frozen exercise contracts; не переписывать семантику |
| R03 | PR 7 и closeout PR 8 merged; Issue 6 closed | Frozen graph/progress reference |
| MS6-R04 | PR 10 merged; Issue 9 closed | Существующий Harness runner; platform adapters требуют проверки |
| MS6-I01 | PR 11 merged; Issue 12 closed | UX/domain map; сценарии и состояния переиспользовать |
| MS6-V01 | PR 14 merged; Issue 13 closed; Руслан APPROVED | PostgreSQL/CI baseline, новые fresh/upgrade обязательны |
| MS7-R02A | PR 15 merged; Issue 16 closed; review submissions не найдены | Сверить acceptance ledger/comments/digest; не считать отсутствие review доказательством отсутствия всех approvals |
| MS7-R03A | PR 20 merged; Issue 18 closed; review submissions не найдены | То же; исторические Candidate/Pending строки требуют сверки |
| MS7-V02 | PR 19 merged; Issue 17 closed; Руслан APPROVED | PR head CI 37138386552 SUCCESS |
| MS7-I02 | PR 22 merged; Issue 21 closed; Руслан и Владимир APPROVED | PR head CI 37061664068 SUCCESS |
| Grades follow-up | PR 24 merged; Issue 23 closed; Илья consumer APPROVED | CI 37203374678 SUCCESS; отдельную required migration approval запись Руслана найти/уточнить |
| MS7-I03 | PR 26 merged; Issue 25 closed; Владимир и Руслан APPROVED | PR head CI 37456350007 SUCCESS; main CI указан выше |

Все номера ссылаются на https://github.com/Tramsey00/MathStart-Python/pull/NUMBER либо /issues/NUMBER. PR descriptions/specs содержат старые OPEN/PENDING строки даже после merge/approval. Источник текущего статуса - live API и записи acceptance, а не одна устаревшая строка. Closed Issue, merge, green CI, Task Approval и Global Gate - разные факты. Product G1-G5 этим аудитом не закрываются.

## 3 Нормативная база и решения до реализации

Основной источник - MathStart Technical Specification v7.1 SECTION20 PARALLEL DEADLINES от 01.10.2026, 114 страниц. SHA256 e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd. Применяются §§5-11 (стр. 8-18), 15-17 (22-30), 20-25 (37-85), 26-27 (86-102). Формат карточек взят из §21 и §§22-24; правила независимости из §17. Это самостоятельный migration addendum; он не выдаётся за уже принятую редакцию основного ТЗ.

В MIG-G0 принимаются ADR перехода (следующий свободный номер после актуальной проверки, ожидаемый ADR-0006), текущий source baseline, минимальный стек, auth/session cutover, content delivery contract, admin inventory, DDL/write ownership, правила integration PR и семидневный календарь. ADR-0001 superseded только в части platform/frontend/ORM/migrations; доменное владение и evidence invariants сохраняются. Applied migrations, frozen contracts и исторические traces не переписываются.

Новые canonical IDs MS7-MIG-R01..R06, V01..V06, I01..I06 не заменяют R01/MS6-V01/MS7-I03 и не занимают номера 52 существующих MS7 задач. Формат follow-up Relation указывается явно. Реализация начинается после accepted HARD/CONTRACT и зарегистрированной canonical Issue; подготовка fixtures и чтение разрешены раньше. Текущий документ создаёт карточки и предлагает workflow, но сам по себе не создаёт branches/issues/PR и не изменяет старое ТЗ.

## 4 Минимальный целевой стек и структура

Frontend: React + TypeScript, Vite через React Router framework mode, существующие CSS/tokens. Public routes pre-rendered в HTML по полному publish manifest; private account client-rendered с no-store. Node используется для build/publish rendering, постоянный Node SSR server не требуется. SSG обязан обеспечивать publish/unpublish freshness через автоматическую генерацию и activation, без ручной правки dist. Если эта модель не проходит проверку публикации, решение меняется явно в ADR, а не потерей SEO.

Backend: Python 3.12+, FastAPI, Pydantic, SQLAlchemy 2, psycopg, Alembic, Uvicorn. PostgreSQL 16+. Синхронные короткие SQLAlchemy transactions/services; Session не делится между threads/tasks. Async LLM и isolated CPU math - будущие области, не добавляются сейчас. Dependency versions совместимо фиксируются в lock при V01/I01; установка latest без lock не допускается. Дополнительные deps имеют task-specific обоснование.

Frontend tests: существующие semantic Node tests как inputs, component/lifecycle tests и Playwright browser checks. Backend tests: pytest/API client и PostgreSQL integration. openapi-typescript создаёт types из canonical contract; небольшой fetch adapter сохраняет cookies/CSRF/envelopes. Redux/TanStack Query не обязательны для нынешних экранов; достаточно явного scenario state и fetch. Генерация типов не заменяет runtime schema validation.

Предлагаемые каталоги: frontend/src/{app,features,shared,content}; backend/mathstart/{users,content,infrastructure}; backend/migrations; tests/{api,integration,migration,content}; tests/harness и pure contract suites остаются. curriculum/site_content/static source paths сохраняются. Копии legacy миграций и renderer fixtures архивируются с manifest; normal target commands не импортируют Django. Нельзя создать пустые будущие домены и заявить их готовность.

Runtime схема: browser -> один HTTPS origin/reverse proxy -> React public HTML/assets + FastAPI /api/v1 -> PostgreSQL/media. Business ownership сохраняется в одном Python-монолите. Content позже зависит от Knowledge для TopicSkill; Knowledge не зависит от Content; только Progress владеет long-term knowledge updates. Приватные ответы, credentials и LLM content не входят в SSG export.

## 5 Контракты и неизменность поведения

37 canonical OpenAPI operations сохраняются как планируемая поверхность; реализованные identity 7 operations + grades GET и существующие page/service routes переносим. Остальные planned endpoints не выдаём за работающие и не закрываем fake success. Auto-generated FastAPI OpenAPI не заменяет specs/api/openapi-v1.json. Framework-specific изменения версионируются addendum, а исходные manifest pins сохраняются; производные ссылки/digests записываются отдельно.

/api/v1, snake_case, trailing slash, UTF-8, request_id, success data/meta и безопасный error envelope сохраняются. Контролируются default 422, slash 307, HTML tracebacks и permissive coercion: malformed JSON, duplicate keys, nonfinite numbers, oversized/invalid UTF-8/unknown fields дают существующий 400. Private anon 401, CSRF/roles 403, foreign/missing 404, conflicts 409, limits 429 + Retry-After, safe unavailable 503. Unsupported/degraded business results не превращаются в wrong. DB exceptions не раскрывают SQL/DSN/поля владельца.

Grades: real PK != class number; number выводится из canonical slug, sorting по (created_at,id), keyset cursor bound to route/page_size, default20 max100, tampering/repeated/unknown query rejected. Legacy Grade epoch 2026-10-04T00:00:00Z сохраняется как tracking baseline, не «восстановленная дата создания». Cursor protocol совместимость на переходе проверяется отдельно.

Текущий onboarding только сохраняет выбранный путь/профиль; START_ZERO/SELF_REPORT/DIAGNOSTIC не запускают новые домены и не увеличивают mastery при GET. Preserve UI registration maximum30, backend maximum150, login старых длинных username, quiet anonymous initial state, contextual GET-only recovery, password cleanup после serialization/terminal outcome/form switch, frozen in-memory pending retry и CSRF refresh.

## 6 PostgreSQL и передача схемы

V01 инвентаризирует фактические table/column types, PK/FK/UNIQUE/CHECK/index/sequence/default/timezone и все migrations. Существующие table/column names и IDs сохраняются; новые profile UUID уже из users не перенумеровываются. on_delete Django не эквивалент SQL FK action автоматически; защиту parent deletion обеспечивают services/constraints и тесты. auto_now/add/Python default/bulk updates получают явно проверенные эквиваленты. FileField переносится как storage key + storage service.

Upgrade path A: локальная БД content.0001 без users/Grade.created_at. Upgrade path B: актуальный Django main со всеми content/users migrations. Upgrade path C: populated identity data с профилями/receipts/roles и synthetic pending operations. Все пути проверяются на disposable копиях. Недостающие Django migration effects воспроизводятся reviewed target upgrade либо контролируемым legacy preparation step на копии; normal target fresh/install не требует Django. Пустая БД создаётся Alembic chain, bootstrap twice без overwrite user evidence.

Alembic baseline содержит проверяемое создание целевой схемы с нуля. Существующую схему stamp только после inventory/equivalence/rehearsal и human review. Alembic autogenerate/check - часть проверки, не доказательство успешного переноса. Django DDL и Alembic DDL никогда не управляют одними таблицами одновременно. Unused django_* history/log/session tables можно сохранить архивными; dropping не входит в обязательное завершение.

В переходный период Django - единственный writer Content/Users на старом runtime, FastAPI shadow читает или пишет только disposable data. После domain cutover все его routes/CLI/admin переходят FastAPI, старому writer отзываются права. Новые domain writes не дублируются. Production mirror/shadow запросы read-only; registration/login/publish нельзя исполнять дважды для сравнения.

## 7 Auth безопасность и staff операции

Серверные opaque sessions в PostgreSQL, secure HttpOnly SameSite cookies, login rotation/logout/expiry/revocation, CSRF bootstrap/header и Origin/Host checks на одном origin. JWT/localStorage tokens не вводятся. Password encoded hashes/iterations/algorithms сохраняются; inventory не выводит хеши. Проверка и validators проходят parity на synthetic fixtures и старых форматах. Final normal runtime не требует django.setup или Django hashers; выбирается совместимый проверенный adapter/library с лицензиями и test vectors. Неподдерживаемые существующие алгоритмы блокируют cutover, не приводят к массовому reset.

Переход sessions допускает согласованный один повторный вход, без сброса паролей. Учётные записи, roles/groups/permissions, inactive flags, profiles, receipts и constraints сохраняются. Receipt digest/serialization/scope минимум7дней и uniqueness должны пережить переключение; сохраняются pending acknowledgement/retry либо выполняется явно принятый secure scope bridge. Простая очистка sessions/receipts не закрывает compatibility. Не делать registration replays между anonymous scopes без доказанной привязки.

Login rate10/5min/IP совместный между workers, не local-memory only; IP proxy policy явно определена и не доверяет arbitrary forwarded header. Session/receipt storage private, отсутствие account enumeration, права проверяются на сервере. Пароли очищаются из DOM, не записываются в logs/storage/screenshots. Остальные будущие rates из основного ТЗ сохраняются как future requirements.

Admin baseline обязателен: read-only Content list/detail, существующие User/Group/Permission и staff операции инвентаризируются R01. V02/V03 обеспечивают staff API/authorization/audit; I02/I04 - минимальные эквивалентные страницы с текущей визуальной основой. Create/edit/deactivate/password change/roles разрешены только в объёме зарегистрированного baseline и прежних permissions. Не создавать новую CMS. Операцию можно исключить только отдельным явным решением MIG-G0, отражённым как изменение scope, а не скрыто назвать CLI равноценным всем Django admin функциям.

## 8 Контент публикация и отсутствие редизайна

Сохраняются authored HTML, math markup, SVG, local/shared CSS/JS, IDs якорей, чтение и навигация, page metadata, source paths, digest conflict, slug identity immutability и provenance. React LessonHost вставляет только publisher-reviewed HTML; user/LLM text escaped. Старые details answers сохраняются как legacy self-check без assessed evidence. Fixtures с reveal/private answers не включаются в bundles/manifest.

Для каждого script выбирается tested mount(root,config)->dispose или full-document navigation. Dispose удаляет listeners, disconnect observers, отменяет RAF/timers; DOM queries scoped к lesson root. Global math dependencies загружаются в верном порядке. React StrictMode remount/back-forward проверяются. Asset loading/content switch не оставляют CSS от предыдущего урока; нельзя называть один работающий график переносом семи local JS и shared scripts.

Существующие цвета, типографика, spacing, header/cards/form layout сохраняются по approved source screenshots. Не подключать глобальный CSS reset и не менять дизайн из-за default компонентов. Layout bug fix допустим только для parity и фиксируется. Две archived static pages остаются unpublished; upgrade их не удаляет, fresh install не обязан создавать retired pages. Поэтому baseline existing281/279published и fresh279 нужно сопоставлять по declared legacy extras, а не hardcode одинаковый total.

Все management commands перечисляются в inventory, включая publish_lessons, bootstrap_site, index_lessons, source/quality/integrity checks и реальную семантику dry-run. Django template component renderer заменяется deterministic adapter с golden HTML parity. Target dry-run должен явно описывать writes/rollback и побочные файлы; не обещать read-only без SQL доказательства. Runtime media/storage keys/seed hashes/backups сохраняются.

DB и filesystem/SSG не являются одной транзакцией. Использовать staging assets/render, operation journal/manifest, explicit activation и resume/recovery; failure не возвращает success. После publish/unpublish public HTML, catalogue, sitemap и redirects соответствуют активному release. Тестируется сбой до/после DB commit и до/после asset activation; cleanup ограничен workspace operation paths и не удаляет чужие материалы.

## 9 Проверки и evidence

Baseline и target сравниваются по семантическим assertions, а не равному числу тестов. Existing Harness, R03, R02A и R03A suites сохраняются. Значимые engineering increments используют принятый Harness; пока будущий Product G1 не принят, допускается явно обозначенный bootstrap Codex surface по §17, без обхода независимого review.

| Старая проверка | Целевая обязательная проверка |
| --- | --- |
| Django check | FastAPI config/startup/routes/security settings check |
| makemigrations check | metadata/Alembic drift + one head + reviewed SQL |
| lesson source validation | Все263 source validation через CLI |
| content quality | HTML/SVG/формулы/asset правила без ослабления |
| site integrity | URL/media/catalog/redirect/SSG completeness |
| Django tests | API/services/migration/content/staff PostgreSQL tests |
| R03/R02A/R03A | Существующие pure suites и новые adapters parity |
| Harness unit/CLI | Прежние check IDs и nonrecursive runner, новая registry |
| fresh smoke | Alembic from zero, bootstrap twice, assets/frontend build |
| UI tests | React semantic/lifecycle + реальные browser/API flows |

Предлагаемые реальные entry points, которые должны быть реализованы: python scripts/verify_repo.py; python scripts/fresh_install_smoke.py --disposable; python scripts/migration_smoke.py --disposable --source-profile <profile>; python scripts/check_database.py; python scripts/version_report.py. Frontend scripts: npm ci, npm run typecheck, npm run test, npm run build, npm run test:e2e. На Windows и CI запускаются из documented roots. Это требования к будущим deliverables, а не заявления о наличии commands сегодня.

CI запускается на task PR -> integration, integration push/PR и final main PR/push. Python/Node locks, dependency checks, PostgreSQL16 service, fresh/upgrade, content, pure/Harness, frontend/build/browser smoke обязательны. Normal CI offline без live LLM. Не считать старый head CI проверкой нового diff; final reviewed SHA и tested merge-ref записываются. Недоступный инструмент/skip/env failure не равны PASS.

E(ID): docs/agent-traces/<ID>.md, source/contract/release digests, run IDs, actual commands/exit codes/versions, CI and PR URLs, review findings/closure, separate Task Approval. Browser - sanitized screenshots/DOM/network/console и version; DB - schema/data manifests без PII; migration - input/output profile, backups, recovery time. QA output не содержит passwords/session keys/DSN. Evidence index связывает старые результаты и новые адаптации; архивы не удаляются ради красивого отчёта.

## 10 Git branches и интеграционный workflow

Ни одна ветка ниже не создаётся этим документом. До implementation R01 регистрирует 18 canonical Issues и их владельцев. GitHub login mapping: Руслан Tramsey00, Владимир VladimirFrolov777, Илья 13baybars. Код пишет Codex, автор задачи и approver остаются людьми.

Сначала snapshot branch ms7-mig-baseline из свежего remote main; в неё входят только согласованные локальные изменения и source manifest. Snapshot PR -> main, независимое approval и CI; resulting MIG_BASE_SHA фиксируется. До accepted snapshot ни один worker не стартует от устаревшей local ветки. Затем integration branch ms7-mig-react-fastapi из MIG_BASE_SHA. Один Owner Руслан интегрирует; feature branches из текущего принятого integration SHA, update без force-push и чужих resets. Новые commits main в этот период либо freeze, либо reviewed intake с повторными checks.

Отдельный worktree/checkout для каждого активного Owner/task; отдельные ports, runtime roots и test DB names. Secrets не копируются в Git. Один writable Alembic chain owner Владимир; frontend lock/routes owner Илья; root docs/verify/CI owner Руслан. Междоменные правки передаются согласованным patch/PR, агенты не редактируют общий рабочий каталог втроём.

| Ветка | Назначение и ответственный |
| --- | --- |
| ms7-mig-baseline | Исходный snapshot, Руслан |
| ms7-mig-react-fastapi | Интеграция, Руслан |
| ms7-mig-r01-baseline | Inventory и ADR, Руслан |
| ms7-mig-r02-contracts | Contracts/parity, Руслан |
| ms7-mig-r03-verification | CI/Harness/checks, Руслан |
| ms7-mig-r04-audit | Integration/security audit, Руслан |
| ms7-mig-r05-main-spec | Основное ТЗ и records, Руслан |
| ms7-mig-r06-release | Release assembly, Руслан |
| ms7-mig-v01-schema | Models/Alembic/upgrade, Владимир |
| ms7-mig-v02-content | Content/routes/staff read, Владимир |
| ms7-mig-v03-identity | Auth/profile/receipts/staff writes, Владимир |
| ms7-mig-v04-publishing | Publisher/bootstrap/CLI, Владимир |
| ms7-mig-v05-operations | Docker/runbooks/restore, Владимир |
| ms7-mig-v06-cutover | Final backend rehearsal, Владимир |
| ms7-mig-i01-foundation | React/toolchain/shell, Илья |
| ms7-mig-i02-pages | Public/catalogue/staff pages/SSG, Илья |
| ms7-mig-i03-lessons | LessonHost/assets/widgets, Илья |
| ms7-mig-i04-account | I03 account port, Илья |
| ms7-mig-i05-browser | Browser/parity/accessibility, Илья |
| ms7-mig-i06-freeze | Frontend release freeze, Илья |

Task PR -> integration содержит Refs #canonical_issue, task ID, exact input SHA и scope. Closing keywords на PR не-default branch не обеспечивают ожидаемое закрытие Issues: это явное исключение migration workflow. До final merge статус ACCEPTED_INTEGRATION, Issue остаётся open. Final PR integration -> main перечисляет Closes # для всех принятых 18 Issues и snapshot references; GitHub closure проверяется после merge. Номера новых Issues заранее не выдумываются. Не закрывать старые Issues заново и не переписывать старые PR.

Review независим от Owner; свой Codex может провести self-check, но не заменить человеческое Task Approval. Руслан не утверждает собственные R задачи: их принимают Владимир/Илья в назначенной зоне. Reviewer проверяет входные SHA, positive/negative cases и реальный CI. Merge не заменяет approval. Final release PR принимает Владимир и Илья, Руслан собирает evidence. Main должен оставаться работоспособным до final cutover.

## 11 Семидневный календарь и Gates

Семь календарных дней включают субботу 10.10 и воскресенье 11.10. Предположение плана: каждый доступен ежедневно для постановки/review 2-4 часа, Codex выполняет implementation/checks между контрольными точками; окружения готовы в D1. Это напряжённый срок, без гарантии по лимитам аккаунтов. Старт позже 07.10 не маскируется прежними датами. Никаких автоматических TASK DONE по наступлению дедлайна.

| День | Руслан | Владимир | Илья | Контроль |
| --- | --- | --- | --- | --- |
| 07.10 D1 | R01 snapshot/ADR; R02 подготовка | Schema inventory и V01 подготовка | Baseline screenshots и I01 подготовка | MIG-G0 решения и source freeze до18:00 |
| 08.10 D2 | R02 accepted contracts; R03 начало | V01 models/migrations | I01 React shell | Первый real lesson и config parity |
| 09.10 D3 | R03 checks/CI; R05 mapping | V02 content/grades/staff reads | I02 pages/SEO/SSG | MIG-G1 foundation до21:00 |
| 10.10 D4 | R03 acceptance; R04 audit начало | V03 identity | I03 lessons/widgets | Реальная auth API + lesson lifecycle |
| 11.10 D5 | R04 integration; R05 draft | V04 publication/CLI | I04 account integration | MIG-G2 current behavior до21:00 |
| 12.10 D6 | R04 findings close; R05 spec | V05 staging/restore | I05 cross-browser/parity | MIG-G3 compatibility до22:00 |
| 13.10 D7 | R06 release/independent gates | V06 migration/cutover rehearsal | I06 frontend freeze | MIG-G4 final до23:59 |

На D7 V06/I06 ready до12:00; integration checks и release candidate до15:00; независимое review до18:00; final PR/main CI и acceptance ledger до23:59. Если CI/review не готовы, gate pending и фиксируется новый прогноз; scope, security и data tests не сокращаются.

MIG-G0: три записи Руслана/Владимира/Ильи о baseline и ADR; запускает implementation. MIG-G1: schema + frontend foundation + content real delivery, approvers Руслан для V/I и Владимир/Илья для R contracts. MIG-G2: полный текущий behavior/publisher/account/staff, владельцы передают evidence, независимые task approvals. MIG-G3: upgrade/fresh/restore, visual/no-redesign, security, все blockers закрыты. MIG-G4: один final SHA, required CI, 18 task approvals, main merge/closure, новое основное ТЗ и runbooks, отдельные approvals Владимира/Ильи; Руслан фиксирует ledger без подписи за других. MIG Gates не заменяют Product G1-G5.

Если D2 сложный урок/schema/contract не работают либо D4 identity parity не проходит, Руслан оформляет blocker и перерасчёт в тот же день. Превышение доступности/лимитов, data drift, unsupported hash, admin scope gap или publication inconsistency - реальные blockers, не разрешение упростить результат. Функциональность после миграции не объявляется finished MVP.

### 11.1 Три параллельные очереди задач

Работа начинается 07.10.2026; финальная передача - 13.10.2026. Все даты ниже - 2026 год, время Europe/Moscow. Номер строки задаёт место в личной очереди, а не общий этап команды. Участник переходит к следующей задаче после выполнения её зависимостей; завершение строки не требует ждать совпадающую строку остальных. Подготовка может идти параллельно по правилам карточек. Дедлайн включает проверки, независимое review и интеграцию результата.

| № | Руслан | Владимир | Илья |
| --- | --- | --- | --- |
| 1 | **MS7-MIG-R01** - до 07.10 | **MS7-MIG-V01** - до 08.10 | **MS7-MIG-I01** - до 08.10 |
| 2 | **MS7-MIG-R02** - до 08.10 | **MS7-MIG-V02** - до 09.10 | **MS7-MIG-I02** - до 09.10 |
| 3 | **MS7-MIG-R03** - до 10.10 | **MS7-MIG-V03** - до 10.10 | **MS7-MIG-I03** - до 10.10 |
| 4 | **MS7-MIG-R04** - до 12.10 | **MS7-MIG-V04** - до 11.10 | **MS7-MIG-I04** - до 11.10 |
| 5 | **MS7-MIG-R05** - до 12.10 | **MS7-MIG-V05** - до 12.10 | **MS7-MIG-I05** - до 12.10 |
| 6 | **MS7-MIG-R06** - до 13.10 | **MS7-MIG-V06** - до 13.10 | **MS7-MIG-I06** - до 13.10 |

Таблица не заменяет ежедневные контрольные точки выше и зависимости в карточках. Пункт 17 является обязательной частью задач этой очереди, а не отдельной незапланированной работой после 13.10.

## 12 Требования миграции

| ID | Проверяемое требование |
| --- | --- |
| MIG-FR01 | Approved baseline сохраняет remote main и agreed local delta |
| MIG-FR02 | React без редизайна, public HTML и private account |
| MIG-FR03 | Полный Content delivery/URL/SEO/media/redirect behavior |
| MIG-FR04 | HTML/формулы/SVG/styles/widgets и lifecycle parity |
| MIG-FR05 | FastAPI identity + grades wire/security parity |
| MIG-FR06 | Password/session/CSRF/rate/receipt compatibility |
| MIG-FR07 | PostgreSQL IDs/constraints/timestamps/relationships сохранены |
| MIG-FR08 | Reviewed Alembic baseline, upgrade profiles и fresh |
| MIG-FR09 | Publish/bootstrap/index/check CLI и recovery |
| MIG-FR10 | Staff/admin inventory и эквивалентные разрешённые операции |
| MIG-FR11 | Canonical contracts/pure reference/Harness сохраняются |
| MIG-FR12 | Target checks/CI с offline/failure coverage |
| MIG-FR13 | Reproducible build/staging/static/media/restore |
| MIG-FR14 | Roles/branches/Issues/independent approval/evidence |
| MIG-FR15 | Основное ТЗ обновлено без отмены исторической приёмки |
| MIG-FR16 | Final runtime/CLI/verification не требуют Django/DRF |
| MIG-NFR01 | Нет потери исходников/данных/секретов; scope bounded |
| MIG-NFR02 | 360/768/1440, keyboard/focus, browser versions |
| MIG-NFR03 | Ordinary API p95<500ms, 200 samples/10 concurrency, failures included |
| MIG-NFR04 | Backup DB+media/release; restore<=2h; RPO<=24h deployment policy |

## 13 Карточки задач

Все карточки имеют Status PLANNED до реального execution. На каждую распространяются §§3,9-11: canonical Issue, accepted upstream, trace, independent review, final-SHA CI. Live Product LLM не требуется. Branch/outputs ниже - предписания, не созданные артефакты. HARD/CONTRACT/HANDOFF/INTEGRATION входят в cycle check; порядок личных очередей сохраняется. Полный Detailed Scope и negative acceptance обязательны.

В календаре, acceptance matrix и колонках нового подтверждения R01/V01/I01 и аналогичные краткие ссылки означают MS7-MIG-R01/V01/I01. В колонке «Старый результат» и поле Relation используются исторические IDs. Task PR, Issue, trace и dependency manifest всегда содержат полный migration ID.

## 14 Рабочие карточки Руслан

### MS7-MIG-R01 Исходный снимок архитектурное решение и владение

**Status:** PLANNED

**Owner:** Руслан

**Reviewer:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Task Approver:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Milestone Gate:** MIG-G0

**Relation to previous task:** Follow-up к R01/ADR-0001 и current baseline

**Что получим простыми словами:** Approved baseline manifest, ADR, exec plan, Issue/branch map и owner matrix. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Все три участника приняли scope; remote I03/grades и local content сохранены; нет неопределённого владельца write/DDL. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR01/10/14; MIG-NFR01

**HARD:** -

**CONTRACT:** Принятые исходные ADR/contracts; точные approvals сверяются

**HANDOFF:** -

**INTEGRATION:** -

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** Verified remote main SHA, текущий local HEAD и dirty-tree manifest, основное ТЗ v7.1, repository contracts и read-only DB inventory. MIG_BASE_SHA создаётся этой задачей; это output, а не заранее существующая dependency.

**Branch:** ms7-mig-r01-baseline

**Target start/window:** 07.10-07.10.2026

**Target deadline:** 07.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** R01; текущий baseline; статусы R02A/R03A/grades: Зафиксировать исторические SHA/PR/approval, согласованный current source manifest и platform disposition. Сверить недостающие записи приёмки без переоткрытия закрытых задач.

**Detailed Scope:**

1. Сверить live main/branches/PR/reviews/CI и состав локальной работы; зарегистрировать SHA/digests без checkout/reset и потери файлов.
2. Составить inventory routes, admin actions, commands, media, schema и tests; отличить исходники от runtime и будущих DTO.
3. Подготовить snapshot branch/PR с одобренными локальными правками, source manifest и MIG_BASE_SHA после проверки.
4. Создать platform ADR и exec plan, принять staff scope, SSG/publish модель, auth cutover, SQLite compatibility и ownership.
5. Зарегистрировать 18 canonical Issues; определить worktrees/DB/ports, общий календарь и приёмку MIG-G0.
6. Обязательная адаптация §17 (R01; текущий baseline; статусы R02A/R03A/grades): Зафиксировать исторические SHA/PR/approval, согласованный current source manifest и platform disposition. Сверить недостающие записи приёмки без переоткрытия закрытых задач.

**Область файлов:** docs/adr, docs/exec-plans, docs/acceptance, source manifest; код только согласованного snapshot.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** Approved baseline manifest, ADR, exec plan, Issue/branch map и owner matrix. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Все три участника приняли scope; remote I03/grades и local content сохранены; нет неопределённого владельца write/DDL. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Divergent local/runtime правка не затирается; отсутствующее approval явно pending; неизвестная staff операция не исключается молча.

**Task-specific tests:** Inventory completeness, source/diff hashes, doc links, baseline existing checks на disposable snapshot; DB read-only facts. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Не копировать .env/credentials/PII; source freeze не разрешает publish/deploy.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-R01), trace docs/agent-traces/MS7-MIG-R01.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. Approved baseline manifest, ADR, exec plan, Issue/branch map и owner matrix. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R02, MS7-MIG-R05, MS7-MIG-V01, MS7-MIG-I01

**Task-specific risks:** Неполный baseline и неверное принятие stale PR body.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Отменить только migration docs/snapshot PR; исходное дерево и данные сохраняются.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-R02 Контракты переноса и проверка эквивалентности

**Status:** PLANNED

**Owner:** Руслан

**Reviewer:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Task Approver:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Milestone Gate:** MIG-G1

**Relation to previous task:** Addendum к R02A/R03A и grades runtime

**Что получим простыми словами:** Accepted platform/auth/content addenda, implemented-route map, parity and migration acceptance matrix. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Контракт достаточен V01-V04/I01-I04; fixture outputs согласованы; никакая default422/307/coercion не меняет API. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR03/05/06/07/08/11; MIG-NFR01

**HARD:** MS7-MIG-R01

**CONTRACT:** Исходные R02/R03/R02A/R03A; MIG ADR

**HANDOFF:** -

**INTEGRATION:** -

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-r02-contracts

**Target start/window:** 07.10-08.10.2026

**Target deadline:** 08.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** R02, R03, MS7-R02A, MS7-R03A: Перенести только framework-facing ссылки и adapter contracts в отдельный addendum; сохранить frozen схемы, semantics, digests и исходные approvals.

**Detailed Scope:**

1. Описать content delivery DTO/HTML trust/SEO/assets/digests и все current route methods; private export forbidden.
2. Зафиксировать exact HTTP/status/JSON limits, grades cursor, auth validators/hash/session/CSRF и receipt bridge.
3. Определить full schema/IDs/default/on_delete/timestamp mapping и shared transaction/lock order.
4. Составить old-to-new assertion matrix, raw-input/stale-response/UI parity и staff API authorization.
5. Версионировать addenda отдельно от frozen pins; определить pub operation journal/SSG activation/recovery; сверить approvals R02A/R03A/grades.
6. Обязательная адаптация §17 (R02, R03, MS7-R02A, MS7-R03A): Перенести только framework-facing ссылки и adapter contracts в отдельный addendum; сохранить frozen схемы, semantics, digests и исходные approvals.

**Область файлов:** specs/migration, specs/api addenda, test matrices; canonical frozen файлы только derived references.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** Accepted platform/auth/content addenda, implemented-route map, parity and migration acceptance matrix. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Контракт достаточен V01-V04/I01-I04; fixture outputs согласованы; никакая default422/307/coercion не меняет API. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Malformed/foreign/unsupported и conflict cases имеют безопасный outcome; нельзя объявить 37 routes реализованными.

**Task-specific tests:** JSON Schema/OAS validation, frozen digests, dependency cycle check, synthetic old/new exchange comparison. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Staff/private DTO separate; replay bound to owner/bootstrap; secrets не включаются в fixtures frontend.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-R02), trace docs/agent-traces/MS7-MIG-R02.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. Accepted platform/auth/content addenda, implemented-route map, parity and migration acceptance matrix. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R03, MS7-MIG-R04, MS7-MIG-R05, MS7-MIG-V01, MS7-MIG-V02, MS7-MIG-V03, MS7-MIG-V04, MS7-MIG-V05, MS7-MIG-V06, MS7-MIG-I01, MS7-MIG-I02, MS7-MIG-I03, MS7-MIG-I04, MS7-MIG-I05, MS7-MIG-I06

**Task-specific risks:** Недостаточно описанный anonymous replay на границе sessions.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Addendum остаётся proposed и implementation зависимых задач не начинается.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-R03 Целевая верификация CI и адаптация Harness

**Status:** PLANNED

**Owner:** Руслан

**Reviewer:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Task Approver:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Milestone Gate:** MIG-G2

**Relation to previous task:** Адаптация R01 и MS6-R04/MS6-V01

**Что получим простыми словами:** Reviewed verify registry, CI workflows, check wrappers и Harness adapter update. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Применимые старые проверки имеют named equivalents; target pipeline запускается и failures дают nonzero; pure/Harness зелёные. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR11/12/14/16

**HARD:** MS7-MIG-R02

**CONTRACT:** Parity matrix R02

**HANDOFF:** -

**INTEGRATION:** MS7-MIG-V02, MS7-MIG-I02

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-r03-verification

**Target start/window:** 08.10-10.10.2026

**Target deadline:** 10.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** R01, R03, MS6-R04, MS6-V01, R02A/R03A suites: Заменить verification command adapters и setup/check registry; сохранить прежние check IDs, pure/Harness suites и доказать их работу на target без Django.

**Detailed Scope:**

1. Перенести registry verify_repo и group semantics на target checks, без recursion repo-baseline/harness-unit.
2. Сохранить pure R03/R02A/R03A, Harness unit/CLI и frozen tests; заменить Django-dependent assertions эквивалентами.
3. Настроить CI для task/integration/main, locks, versions, PG16 fresh/upgrade, content and frontend build/E2E smoke.
4. Добавить failed DB connection, skipped-tool/failing-check/timeout negative coverage; final SHA/merge-ref linkage.
5. Задать real CLI entry points и documented commands; отсутствие обязательного check является fail, не empty PASS.
6. Обязательная адаптация §17 (R01, R03, MS6-R04, MS6-V01, R02A/R03A suites): Заменить verification command adapters и setup/check registry; сохранить прежние check IDs, pure/Harness suites и доказать их работу на target без Django.

**Область файлов:** scripts/verify_repo.py, scripts check wrappers, .github/workflows, harness registry/tests.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** Reviewed verify registry, CI workflows, check wrappers и Harness adapter update. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Применимые старые проверки имеют named equivalents; target pipeline запускается и failures дают nonzero; pure/Harness зелёные. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Failed test/timeout не переводит run в READY; missing dependency и SQLite skip не выдаются за PG evidence.

**Task-specific tests:** Harness regression, fake dry-run/execute/status, CI on current head, unit checks of command routing and nonrecursive registry. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** CI synthetic secrets only; logs sanitized; no live Product LLM or production DB.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-R03), trace docs/agent-traces/MS7-MIG-R03.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. Reviewed verify registry, CI workflows, check wrappers и Harness adapter update. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R04

**Task-specific risks:** CI target branch не triggers либо заменены проверки формальными заглушками.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Scoped revert registry/workflow; legacy verification остаётся историческим reproducible baseline.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-R04 Независимый аудит интеграции безопасности и сохранности

**Status:** PLANNED

**Owner:** Руслан

**Reviewer:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Task Approver:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Milestone Gate:** MIG-G3

**Relation to previous task:** Новая проверка migrated implementations без отмены старой приёмки

**Что получим простыми словами:** Independent audit report, findings ledger, accepted compatibility matrix. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Все обязательные parity cases доказаны; zero open blocking findings; R audit принят Владимиром/Ильёй независимо. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR01..16; MIG-NFR01..04

**HARD:** MS7-MIG-R03

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** MS7-MIG-V03, MS7-MIG-V04, MS7-MIG-V05, MS7-MIG-I03, MS7-MIG-I04, MS7-MIG-I05

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-r04-audit

**Target start/window:** 10.10-12.10.2026

**Target deadline:** 12.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** Все строки §17: Проверить old-to-new evidence index, сохранность исторических результатов и реальную эквивалентность новых adapters; проверить результаты V/I, не считать новую компиляцию старой приёмкой.

**Detailed Scope:**

1. Сравнить baseline и target route/data/source/publication/admin assertions на одном agreed manifest.
2. Провести independent review auth/staff/receipt/cursor, publication concurrency/recovery и source-to-SSG consistency.
3. Проверить upgrade profiles A/B/C, fresh twice, archived pages, ID/sequence stability и no Django normal runtime.
4. Проверить bundle/export secrets, keyboard/stale input и отсутствие редизайна; перенести findings владельцам без чужого refactor.
5. Собрать закрытие каждого blocker с regression/evidence; не переписать historical failure или approval.
6. Обязательная адаптация §17 (Все строки §17): Проверить old-to-new evidence index, сохранность исторических результатов и реальную эквивалентность новых adapters; проверить результаты V/I, не считать новую компиляцию старой приёмкой.

**Область файлов:** docs/agent-traces/MS7-MIG-R04.md, audit/evidence index, regression tests в согласованной зоне.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** Independent audit report, findings ledger, accepted compatibility matrix. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Все обязательные parity cases доказаны; zero open blocking findings; R audit принят Владимиром/Ильёй независимо. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Пропущенная admin action, unsupported password или incomplete restore остаётся blocker, несмотря на green unit tests.

**Task-specific tests:** AT-M01..AT-M12, full target checks, PG races, security negative flows, content manifest and browser evidence. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Не запускать mutations на production ради shadow compare; никаких secrets/PII в audit.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-R04), trace docs/agent-traces/MS7-MIG-R04.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. Independent audit report, findings ledger, accepted compatibility matrix. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R05, MS7-MIG-R06, MS7-MIG-V06

**Task-specific risks:** Само-review или сравнение с неверным baseline.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Остановить release; вернуть отдельный scoped change, не откатывать данные разрушительно.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-R05 Обновление основного ТЗ и готовых задач

**Status:** PLANNED

**Owner:** Руслан

**Reviewer:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Task Approver:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Milestone Gate:** MIG-G3

**Relation to previous task:** Follow-up к R01/MS6-I01 и всем migrated completed tasks

**Что получим простыми словами:** Основное ТЗ v7.2, 52-row task impact/calendar matrix, updated current docs, old-to-new evidence index. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Нет нормативного конфликта про required Django; все old IDs и domain semantics сохранены; дедлайны и gates согласованы отдельно. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR11/14/15; MIG-NFR01

**HARD:** MS7-MIG-R01, MS7-MIG-R02

**CONTRACT:** Frozen product contracts и accepted migration decisions

**HANDOFF:** -

**INTEGRATION:** MS7-MIG-R04

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-r05-main-spec

**Target start/window:** 09.10-12.10.2026

**Target deadline:** 12.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** Все строки §17; все 52 canonical IDs основного ТЗ: Выполнить полный §17.1-17.2: disposition для каждой выполненной карточки, актуальные документы, main spec v7.2 и согласованный календарь. Связать original_result, platform_disposition, migration_follow_up, target_evidence, current_status с точными источниками.

**Detailed Scope:**

1. Подготовить основное ТЗ v7.2 и machine-readable/source version; обновить platform, ORM/migrations/auth/frontend/deployment/verification.
2. Для каждой выполненной карточки создать disposition: historical accepted / platform-adapted / new evidence required; не менять её прошлые даты/PR/tests.
3. Обновить AGENTS/PRODUCT/ARCHITECTURE/README/docs architecture/verification/runbooks/Issue-PR templates текущим baseline.
4. Проверить все 52 canonical task IDs, owners и dependency edges; planned Django-specific deliverables заменить SQLAlchemy/React эквивалентами.
5. Пересчитать §20 после migration, сохранить ORG сроки и явно согласовать влияние на 03.12; provisional forecast не делать approved deadline.
6. Синхронизировать merged/current statuses с live GitHub evidence; сохранить superseded docs и link/digest provenance.
7. Обязательная адаптация §17 (Все строки §17; все 52 canonical IDs основного ТЗ): Выполнить полный §17.1-17.2: disposition для каждой выполненной карточки, актуальные документы, main spec v7.2 и согласованный календарь. Связать original_result, platform_disposition, migration_follow_up, target_evidence, current_status с точными источниками.

**Область файлов:** docs current files, migration spec, main ТЗ source/PDF; frozen historical sections через appendix/addendum.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** Основное ТЗ v7.2, 52-row task impact/calendar matrix, updated current docs, old-to-new evidence index. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Нет нормативного конфликта про required Django; все old IDs и domain semantics сохранены; дедлайны и gates согласованы отдельно. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Нет фиктивного нового acceptance старого task; versioned contract не меняется массовой заменой слова Django.

**Task-specific tests:** Document link/ID/FR-NFR/dependency/manifest checks, acceptance ledger consistency, final rendered PDF review. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Не раскрывать credentials; ADR author не ставит approval за остальных.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-R05), trace docs/agent-traces/MS7-MIG-R05.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. Основное ТЗ v7.2, 52-row task impact/calendar matrix, updated current docs, old-to-new evidence index. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R06

**Task-specific risks:** Новый календарь необоснованно подтверждает 03.12 или стирает старую приёмку.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Сохранить draft v7.2 и исходный v7.1; blocker означает pending document gate.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-R06 Единый release и передача новой базовой версии

**Status:** PLANNED

**Owner:** Руслан

**Reviewer:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Task Approver:** Владимир и Илья по архитектуре, контрактам и UI; собственную работу Руслан не принимает.

**Milestone Gate:** MIG-G4

**Relation to previous task:** Новый migration release gate

**Что получим простыми словами:** One release SHA, final PR/main CI, approved ledger, handover package и backlog resume map. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Final SHA checked/approved; все обязательные deliverables доступны; main работающий; no Django normal runtime; v7.2 accepted. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR12..16; MIG-NFR01..04

**HARD:** MS7-MIG-R04, MS7-MIG-R05, MS7-MIG-V06, MS7-MIG-I06

**CONTRACT:** Accepted migration ADR/addenda

**HANDOFF:** -

**INTEGRATION:** -

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-r06-release

**Target start/window:** 13.10-13.10.2026

**Target deadline:** 13.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** Все адаптации §17: Включить принятый old-to-new evidence index и основное ТЗ v7.2 в финальную передачу; проверить закрытие новых migration Issues и сохранность старых закрытых Issues/PR.

**Detailed Scope:**

1. Собрать final integration SHA, matching frontend/backend/schema/assets/docs и evidence index.
2. Проверить 18 task approvals и final PR Closes mappings; получить Владимира/Ильи release review.
3. Выполнить final CI/merge-ref checks; оформить release PR integration->main без force-push/history rewrite.
4. После принятого merge сверить main SHA/CI/Issue closure; сохранить rollback package и operational approval boundary.
5. Записать MIG-G4 ledger и resume entry points для нового основного ТЗ; не закрывать Product G1-G5.
6. Обязательная адаптация §17 (Все адаптации §17): Включить принятый old-to-new evidence index и основное ТЗ v7.2 в финальную передачу; проверить закрытие новых migration Issues и сохранность старых закрытых Issues/PR.

**Область файлов:** release/evidence docs и integration metadata; runtime изменения только через принятые task PR.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** One release SHA, final PR/main CI, approved ledger, handover package и backlog resume map. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Final SHA checked/approved; все обязательные deliverables доступны; main работающий; no Django normal runtime; v7.2 accepted. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Новый commit после review требует применимой повторной проверки; stale CI и Issue closure не заменяют approval.

**Task-specific tests:** Canonical full target checks, fresh/upgrade smoke, browser smoke, link/package integrity, post-merge CI. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Deployment отдельно approved; secrets передаются вне repository/artifacts.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-R06), trace docs/agent-traces/MS7-MIG-R06.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. One release SHA, final PR/main CI, approved ledger, handover package и backlog resume map. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MIG-G4 / дальнейший backlog основного ТЗ

**Task-specific risks:** Финальное объединение ломает ранее принятые независимые ветки.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** До merge оставить main legacy; после cutover использовать проверенный runbook и совместимость из V06.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.


## 15 Рабочие карточки Владимир

### MS7-MIG-V01 SQLAlchemy модели Alembic и upgrade profiles

**Status:** PLANNED

**Owner:** Владимир

**Reviewer:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Task Approver:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Milestone Gate:** MIG-G1

**Relation to previous task:** Platform adaptation MS6-V01/V02/grades migration

**Что получим простыми словами:** SQLAlchemy metadata, Alembic chain, schema mapping и upgrade/fresh fixtures. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Empty target DB создаётся без Django; A/B/C сохраняют ID/FK/data; no unexpected schema drift. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR07/08/16; MIG-NFR01

**HARD:** MS7-MIG-R01

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** -

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-v01-schema

**Target start/window:** 07.10-08.10.2026

**Target deadline:** 08.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** MS6-V01, MS7-V02, grades PR24: Перенести schema/ORM/migration layer с сохранением ID, constraints, Grade epoch, credentials/roles и applied migration history; доказать fresh и upgrade A/B/C.

**Detailed Scope:**

1. Инвентаризировать PG schema и все baseline migrations; сохранить legacy auth/content IDs, table names и references.
2. Создать target models/repos/UoW, locks/default/timestamp/FK/check/index/sequence equivalents; explicit SQLite compat configuration без fallback.
3. Добавить Alembic from-zero baseline и reviewed upgrade A/B/C, Grade epoch/users backfill без overwrite credentials/roles.
4. Разделить DDL allowlist и ownership; existing stamp только после schema proof; сохранить migration history.
5. Зафиксировать dependencies lock/config/env placeholders/test DB isolation и schema drift checks.
6. Обязательная адаптация §17 (MS6-V01, MS7-V02, grades PR24): Перенести schema/ORM/migration layer с сохранением ID, constraints, Grade epoch, credentials/roles и applied migration history; доказать fresh и upgrade A/B/C.

**Область файлов:** backend models/infrastructure, backend/migrations, requirements lock/config, migration tests.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** SQLAlchemy metadata, Alembic chain, schema mapping и upgrade/fresh fixtures. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Empty target DB создаётся без Django; A/B/C сохраняют ID/FK/data; no unexpected schema drift. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Unknown schema/migration head блокирует stamp; duplicate/invalid FK/CHECK отклоняются; failure PostgreSQL не выбирает SQLite.

**Task-specific tests:** Fresh+upgrade disposable PG, constraints/defaults/timestamps/sequence, rollback failure injection и backfill twice. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Не выводить hashes/DSN; production migration не выполняется без gate.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-V01), trace docs/agent-traces/MS7-MIG-V01.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. SQLAlchemy metadata, Alembic chain, schema mapping и upgrade/fresh fixtures. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-V02, MS7-MIG-V03, MS7-MIG-V05

**Task-specific risks:** SQL equivalent ошибочно принят за equivalent ORM behavior.

**DB migration impact:** Schema/data effects только reviewed ownership/migrations; no production write в этой карточке без gate.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Additive forward repair; не редактировать applied Django migrations и не делать DROP ради совпадения.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-V02 FastAPI Content grades маршруты и staff чтение

**Status:** PLANNED

**Owner:** Владимир

**Reviewer:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Task Approver:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Milestone Gate:** MIG-G1

**Relation to previous task:** Перенос Content и merged PR24

**Что получим простыми словами:** FastAPI Content APIs/routes, public manifest, staff read adapters, transport contract. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Все current GET cases соответствуют baseline; grades mutation integration IDs корректны; private exports отсутствуют. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR03/05/10/16

**HARD:** MS7-MIG-V01

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** -

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-v02-content

**Target start/window:** 08.10-09.10.2026

**Target deadline:** 09.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** Существующий Content; grades PR24; HTTP contract MS7-R02A: Перенести реальные Content/Grades HTTP adapters, cursor и permissions на FastAPI без изменения wire contract; сохранить оригинальную additive migration history.

**Detailed Scope:**

1. Перенести published-only content reads/catalogue/delivery manifest и SEO/asset metadata из baseline.
2. Перенести grades GET с real PK/number, created_at/id keyset, signed cursor scope и safe errors.
3. Реализовать current redirects precedence/status, unpublished404, sitemap/robots/static/media routing; неизвестный slug не SPA200.
4. Создать strict transport/error/request_id boundary, raw JSON validation и implemented-route registry.
5. Перенести staff read APIs/current admin permissions и filters согласно R01 inventory; no public leakage.
6. Обязательная адаптация §17 (Существующий Content; grades PR24; HTTP contract MS7-R02A): Перенести реальные Content/Grades HTTP adapters, cursor и permissions на FastAPI без изменения wire contract; сохранить оригинальную additive migration history.

**Область файлов:** backend/content, infrastructure/http, api/schema adapters/tests; frontend code не изменять.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** FastAPI Content APIs/routes, public manifest, staff read adapters, transport contract. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Все current GET cases соответствуют baseline; grades mutation integration IDs корректны; private exports отсутствуют. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Foreign/invalid cursor, unpublished, invalid slug/path traversal/unsupported catalogue rows отвечают безопасно; GET не создаёт профиль/evidence.

**Task-specific tests:** API DTO/status/method/content-type, pagination races/query limits, catalogue/redirect/SEO/media and staff permission tests. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Owner auth precedes private lookup; staff reads guarded; no SQL/path/DSN in errors.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-V02), trace docs/agent-traces/MS7-MIG-V02.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. FastAPI Content APIs/routes, public manifest, staff read adapters, transport contract. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R03, MS7-MIG-V03, MS7-MIG-V04, MS7-MIG-I02, MS7-MIG-I03, MS7-MIG-I04

**Task-specific risks:** Canonical DTO расширен без addendum либо grade number подменён PK.

**DB migration impact:** Schema/data effects только reviewed ownership/migrations; no production write в этой карточке без gate.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Вернуть route owner на legacy только до target writes; manifest version pinned.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-V03 Identity sessions CSRF receipts и staff запись

**Status:** PLANNED

**Owner:** Владимир

**Reviewer:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Task Approver:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Milestone Gate:** MIG-G2

**Relation to previous task:** Перенос MS7-V02 с сохранением accepted semantics

**Что получим простыми словами:** FastAPI Users services/API/security, session model/migration, hash/receipt cutover adapter. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Credentials/roles/profiles сохранены; auth/security/receipt parity и staff operations проходят; no Django import in target normal auth. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR05/06/10/16; MIG-NFR01

**HARD:** MS7-MIG-V01

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** MS7-MIG-V02

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-v03-identity

**Target start/window:** 09.10-10.10.2026

**Target deadline:** 10.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** MS7-V02; identity contract MS7-R02A: Перенести Users services/models/session/receipts на target, сохранить profiles/roles/hash/HTTP behavior и доказать retries/races/cutover.

**Detailed Scope:**

1. Перенести все7 identity operations, strict body/validators/limits и deterministic replay bytes.
2. Сохранить existing encoded hashes и password policy через independent compatibility adapter; synthetic parity, no forced reset.
3. Реализовать PG opaque sessions/rotation/logout/expiry, anonymous CSRF bootstrap, mutation CSRF+Origin и shared login rate.
4. Перенести receipt scope/digest/retention/uniqueness и profile locks; доказать concurrent register/onboarding и cross-cutover retry.
5. Перенести разрешённые current user/group/role/staff write operations с permission/audit, PROTECT/archive behavior.
6. Onboarding сохраняет только baseline selection; никаких fake diagnostic/progress writes.
7. Обязательная адаптация §17 (MS7-V02; identity contract MS7-R02A): Перенести Users services/models/session/receipts на target, сохранить profiles/roles/hash/HTTP behavior и доказать retries/races/cutover.

**Область файлов:** backend/users/session/password/security, migration append, identity/staff tests.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** FastAPI Users services/API/security, session model/migration, hash/receipt cutover adapter. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Credentials/roles/profiles сохранены; auth/security/receipt parity и staff operations проходят; no Django import in target normal auth. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** 401 indistinguishable, foreign404, CSRF403, repeated conflicting key409, limit429, unavailable503; failed mutation не оставляет partial user.

**Task-specific tests:** Port identity tests, real multi-connection PG races, synthetic old hash vectors, two worker rate, session fix/replay boundary and admin privilege escalation. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** HttpOnly/Secure/SameSite, no localStorage credentials, safe proxy IP, password never logs/response.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-V03), trace docs/agent-traces/MS7-MIG-V03.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. FastAPI Users services/API/security, session model/migration, hash/receipt cutover adapter. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R04, MS7-MIG-V05, MS7-MIG-I04

**Task-specific risks:** Anonymous receipt scope теряется при reauthentication; unsupported legacy hash.

**DB migration impact:** Schema/data effects только reviewed ownership/migrations; no production write в этой карточке без gate.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Drain writes; retain compat receipts/hashes; revert только по proven old-reader compatibility, иначе forward fix.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-V04 Публикация bootstrap медиа и служебные команды

**Status:** PLANNED

**Owner:** Владимир

**Reviewer:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Task Approver:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Milestone Gate:** MIG-G2

**Relation to previous task:** Перенос existing content pipeline

**Что получим простыми словами:** Target publisher/bootstrap/index/check CLI, media services, SSG activation/recovery runbook. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** 263 sources публикуются; digest conflicts не overwrite; all CLI preserved; repeated bootstrap stable; publication immediately reflected in active release. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR04/09/13/16

**HARD:** MS7-MIG-V02

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** MS7-MIG-I03

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-v04-publishing

**Target start/window:** 10.10-11.10.2026

**Target deadline:** 11.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** Существующие content publication/bootstrap/index tools: Перенести Django commands/template renderer в target CLI/deterministic adapter; сохранить source identity, digests, conflict behavior, authored content и исторические evidence.

**Detailed Scope:**

1. Выделить source validation/digest/theme/component core из Django settings/templates и создать deterministic renderer adapter.
2. Перенести transaction/locks/rebuild-plan/conflict checks и source owner constraints, preserving runtime edits.
3. Перенести bootstrap/catalog/media/redirect/index/all inventory CLI commands и права записи.
4. Подключить SSG render/build и staged release journal/activation; publish/unpublish visibility согласована с DB.
5. Реализовать failure/recovery по стадиям DB/media/frontend, scoped cleanup и правильный nonzero.
6. Проверить bootstrap twice, preserved retired pages/evidence/Grade timestamps, storage keys и dry-run side effects.
7. Обязательная адаптация §17 (Существующие content publication/bootstrap/index tools): Перенести Django commands/template renderer в target CLI/deterministic adapter; сохранить source identity, digests, conflict behavior, authored content и исторические evidence.

**Область файлов:** backend/content/services, CLI/check scripts, legacy template equivalents, source golden tests.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** Target publisher/bootstrap/index/check CLI, media services, SSG activation/recovery runbook. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** 263 sources публикуются; digest conflicts не overwrite; all CLI preserved; repeated bootstrap stable; publication immediately reflected in active release. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Lock/source collision, missing media/hash mismatch/render failure/partial activation дают safe fail/recovery, не success.

**Task-specific tests:** Port publication/bootstrap/content tests, multi-connection lock contention, golden renderer, interrupted stage resume and source/runtime manifest checks. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Trusted reviewed HTML only; no validation fixtures in export; file paths bounded.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-V04), trace docs/agent-traces/MS7-MIG-V04.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. Target publisher/bootstrap/index/check CLI, media services, SSG activation/recovery runbook. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R04, MS7-MIG-V05

**Task-specific risks:** DB commit и public artifacts расходятся; скрыт double bootstrap write.

**DB migration impact:** Schema/data effects только reviewed ownership/migrations; no production write в этой карточке без gate.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Journal resume либо approved prior release/data snapshot; user evidence не восстанавливать из content seed.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-V05 Окружения сборка backup restore и эксплуатация

**Status:** PLANNED

**Owner:** Владимир

**Reviewer:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Task Approver:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Milestone Gate:** MIG-G3

**Relation to previous task:** Адаптация MS6-V01 окружения и текущей эксплуатации

**Что получим простыми словами:** Reproducible environments, images/locks, runbooks, restore/performance evidence. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Fresh clone запускает target; restore<=2h с integrity; ordinary profile200/10 и failures included; no normal Django dependency. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR13/16; MIG-NFR03/04

**HARD:** MS7-MIG-V01

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** MS7-MIG-V03, MS7-MIG-V04, MS7-MIG-I03, MS7-MIG-I04

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-v05-operations

**Target start/window:** 11.10-12.10.2026

**Target deadline:** 12.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** MS6-V01: Заменить devserver/migrate/collectstatic/smoke и окружения целевыми эквивалентами; обновить runbooks/locks/images, подтвердить restore и версии.

**Detailed Scope:**

1. Подготовить dev/staging/production-oriented containers: build Node, ASGI runtime, edge static/media, PG16 и health.
2. Обновить configs/env/docs, no fallback/no debug/proxy/secure cookie; migration отдельный release step.
3. Создать DB+media+frontend release backup package, restore на disposable окружении и verify manifests/auth/content.
4. Измерить restore duration, ordinary API p95/error profile и ресурсные versions; AI perf остаётся future.
5. Подготовить operational CLI staff/start/stop/check/rollback, credential handover references и storage permissions.
6. Обязательная адаптация §17 (MS6-V01): Заменить devserver/migrate/collectstatic/smoke и окружения целевыми эквивалентами; обновить runbooks/locks/images, подтвердить restore и версии.

**Область файлов:** Docker/Compose/deployment config, scripts/check_database/version_report, runbooks and env examples.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** Reproducible environments, images/locks, runbooks, restore/performance evidence. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Fresh clone запускает target; restore<=2h с integrity; ordinary profile200/10 и failures included; no normal Django dependency. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Unavailable PG/asset release/secret configuration не дают false healthy; backup без media не принят.

**Task-specific tests:** Container clean build/start/health, missing config/DB timeout, restore drill, load test baseline/target and runtime dependency scan. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Production HTTPS/allowed hosts/least privilege/injected secrets; no public DB exposure.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-V05), trace docs/agent-traces/MS7-MIG-V05.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. Reproducible environments, images/locks, runbooks, restore/performance evidence. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R04, MS7-MIG-V06, MS7-MIG-I05

**Task-specific risks:** Dev server объявлен production; migration запускает каждый worker.

**DB migration impact:** Schema/data effects только reviewed ownership/migrations; no production write в этой карточке без gate.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Previous image/assets и compatible schema; destructive restore только approved с RPO/reconciliation.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-V06 Итоговая репетиция upgrade и передача backend

**Status:** PLANNED

**Owner:** Владимир

**Reviewer:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Task Approver:** Руслан; Илья подтверждает consumer/browser handoff, если применимо.

**Milestone Gate:** MIG-G4

**Relation to previous task:** Final handoff existing runtime to target

**Что получим простыми словами:** Final backend SHA, approved cutover/rollback rehearsal и upgrade/fresh evidence. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** All profiles pass, one writer, repeat safe, no data/source loss; review Руслана принят; известные ограничения явно закрыты или blocker. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR06..09/13/16; MIG-NFR01/04

**HARD:** MS7-MIG-V05, MS7-MIG-R04

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** -

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-v06-cutover

**Target start/window:** 13.10-13.10.2026

**Target deadline:** 13.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** MS6-V01, MS7-V02, grades PR24; publication pipeline: Подтвердить финальные fresh/upgrade/restore и auth/publisher compatibility на release SHA; передать platform-adapted evidence без изменения прошлой приёмки.

**Detailed Scope:**

1. Повторить fresh и upgrade A/B/C на final backend/release SHA, проверить sequences/profiles/receipts/media/page manifest.
2. Отрепетировать maintenance/drain/snapshot/switch writer/reauth/retry/health/canary порядок и отзыв legacy writes.
3. Проверить app rollback до/после synthetic target writes; incompatible case фиксирует forward recovery, без silent loss.
4. Зафиксировать legacy table retention и отсутствие Django в CLI/runtime/dependency lock.
5. Передать Руслану backend freeze, runbooks и DB manifest до12:00; production switch отдельно approved.
6. Обязательная адаптация §17 (MS6-V01, MS7-V02, grades PR24; publication pipeline): Подтвердить финальные fresh/upgrade/restore и auth/publisher compatibility на release SHA; передать platform-adapted evidence без изменения прошлой приёмки.

**Область файлов:** Cutover/upgrade scripts, runbook, backend release evidence; других Owner files только по handoff.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** Final backend SHA, approved cutover/rollback rehearsal и upgrade/fresh evidence. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** All profiles pass, one writer, repeat safe, no data/source loss; review Руслана принят; известные ограничения явно закрыты или blocker. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Lost ack/restart/partial switch не создают double registration или mixed publisher; rollback не теряет новые records молча.

**Task-specific tests:** Final migration smoke, real auth/publication races, restore/route-switch simulations, dependency/runtime scan. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Maintenance controls/private backup, no real student credentials in evidence.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-V06), trace docs/agent-traces/MS7-MIG-V06.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. Final backend SHA, approved cutover/rollback rehearsal и upgrade/fresh evidence. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R06, MS7-MIG-I06

**Task-specific risks:** Final Alembic revision diverges from tested image.

**DB migration impact:** Schema/data effects только reviewed ownership/migrations; no production write в этой карточке без gate.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** По проверенной таблице совместимости; retain DB/media and forward repair where old app cannot read new writes.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.


## 16 Рабочие карточки Илья

### MS7-MIG-I01 React foundation без изменения дизайна

**Status:** PLANNED

**Owner:** Илья

**Reviewer:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Task Approver:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Milestone Gate:** MIG-G1

**Relation to previous task:** Адаптация MS7-I02 и MS6-I01

**Что получим простыми словами:** React shell, routes/component foundation, toolchain и visual baseline. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Shell matches baseline, mobile/keyboard intact, build works; invalid descriptor controlled unsupported. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR02/11; MIG-NFR02

**HARD:** MS7-MIG-R01

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** -

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-i01-foundation

**Target start/window:** 07.10-08.10.2026

**Target deadline:** 08.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** MS6-I01, MS7-I02, R02 dispatcher contracts: Перенести UX map/template examples, tokens/shapes/states/gallery и approved dispatcher fix в React foundation; сохранить дизайн и frozen exercise semantics.

**Detailed Scope:**

1. Создать React/TS/Router/Vite и package lock, build/typecheck/test entry points.
2. Перенести shell/header/navigation/tokens/base components из approved current sources без UI library reset.
3. Задать маршруты public/account/staff/debug foundation и client API/CSRF/error adapter.
4. Переиспользовать I02 fixtures/schema dispatcher строго typed; debug only и no private answers.
5. Снять matched baseline screenshots widths360/768/1440; actual browser versions и root CSS isolation.
6. Обязательная адаптация §17 (MS6-I01, MS7-I02, R02 dispatcher contracts): Перенести UX map/template examples, tokens/shapes/states/gallery и approved dispatcher fix в React foundation; сохранить дизайн и frozen exercise semantics.

**Область файлов:** frontend app/shared/ui/api, package lock/config/tests; global CSS меняет только Илья.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** React shell, routes/component foundation, toolchain и visual baseline. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Shell matches baseline, mobile/keyboard intact, build works; invalid descriptor controlled unsupported. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Non-string mode/missing schema не приводит к supported slot; fixture data не substitute API.

**Task-specific tests:** Port dispatcher JS regressions, component keyboard/focus, typecheck/build, screenshot parity. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Escape untrusted text, no answers/checkers/credentials in bundles.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-I01), trace docs/agent-traces/MS7-MIG-I01.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. React shell, routes/component foundation, toolchain и visual baseline. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-I02, MS7-MIG-I04

**Task-specific risks:** Default reset/fonts/layout случайно становятся редизайном.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Revert foundation commit, preserve existing styles/source baseline.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-I02 Страницы каталог SSG SEO и staff оболочка

**Status:** PLANNED

**Owner:** Илья

**Reviewer:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Task Approver:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Milestone Gate:** MIG-G1

**Relation to previous task:** Перенос текущих Templates/page routes

**Что получим простыми словами:** React public/current staff read pages и SSG pipeline/manifest. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** All published URLs covered, unpublished not200, metadata/body present raw HTML, styles same, staff guarded server-side. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR02/03/10/13; MIG-NFR02

**HARD:** MS7-MIG-I01

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** MS7-MIG-V02

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-i02-pages

**Target start/window:** 08.10-09.10.2026

**Target deadline:** 09.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** Существующие pages/catalogue; MS6-I01 UX states: Перенести template-oriented page integration в React/public HTML и staff оболочку; сохранить навигацию, состояния, URL/SEO и текущий внешний вид.

**Detailed Scope:**

1. Перенести главную/каталог/структурные страницы/navigation/search current scope через real delivery API.
2. Настроить pre-render полного public URL manifest, title/meta/canonical/OG/lang и текст без JS.
3. Сохранить special sitemap page, anchor/history/scroll и redirect/404 precedence; no wildcardSPA200.
4. Подготовить current staff list/detail/navigation/permission states согласно inventory, no new CMS design.
5. Связать generated assets и release digest; private account/staff не pre-render персональными данными.
6. Обязательная адаптация §17 (Существующие pages/catalogue; MS6-I01 UX states): Перенести template-oriented page integration в React/public HTML и staff оболочку; сохранить навигацию, состояния, URL/SEO и текущий внешний вид.

**Область файлов:** frontend routes/pages/SSG scripts, staff read views; backend через named handoff.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** React public/current staff read pages и SSG pipeline/manifest. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** All published URLs covered, unpublished not200, metadata/body present raw HTML, styles same, staff guarded server-side. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Unknown/unpublished/missing asset не показывают fake ready; external redirect/location handling safe.

**Task-specific tests:** All URL manifest HTTP checks, SEO HTML parsing/no-JS, catalogue search/current links, auth staff negative and pages snapshots. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** No private pre-render/shared cache; API ownership не выводится из client route.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-I02), trace docs/agent-traces/MS7-MIG-I02.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. React public/current staff read pages и SSG pipeline/manifest. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R03, MS7-MIG-I03

**Task-specific risks:** Dynamic slug omitted by prerender:true и SEO потерян.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Previous public artifact release, invalidate failed build manifest.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-I03 LessonHost формулы стили и интерактивы

**Status:** PLANNED

**Owner:** Илья

**Reviewer:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Task Approver:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Milestone Gate:** MIG-G2

**Relation to previous task:** Перенос current lessons/shared scripts

**Что получим простыми словами:** All lesson delivery, widget adapters/lifecycle inventory и visual regression cases. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** 263 lessons manifest complete; all JS families tested; no leaked CSS/listeners and no visual redesign. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR04/09; MIG-NFR01/02

**HARD:** MS7-MIG-I02

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** MS7-MIG-V02

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-i03-lessons

**Target start/window:** 09.10-10.10.2026

**Target deadline:** 10.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** Topics/site/visual fixes; существующие уроки: Перенести только technical integration/path/lifecycle, сохранив одобренные local appearance, HTML/CSS/JS/math/SVG и authored content.

**Detailed Scope:**

1. Создать LessonHost для reviewed HTML, math/SVG/local styles и asset registry без JSX conversion263.
2. Инвентаризировать7 local page.js и shared dependencies; каждому назначить mount/dispose либо full document navigation.
3. Scoped event/observer/RAF lifecycle и script order; StrictMode remount/back-forward/resize/scroll.
4. Сохранить diagram axes/arrows, contents/anchors, tables/formula overflow и approved visual fixes.
5. Подключить publisher render handoff и representative golden browser fixtures; legacy details остаются unassessed.
6. Обязательная адаптация §17 (Topics/site/visual fixes; существующие уроки): Перенести только technical integration/path/lifecycle, сохранив одобренные local appearance, HTML/CSS/JS/math/SVG и authored content.

**Область файлов:** frontend/content/lesson-host/widgets/assets, frontend tests; shared lesson CSS only scoped parity fixes.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** All lesson delivery, widget adapters/lifecycle inventory и visual regression cases. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** 263 lessons manifest complete; all JS families tested; no leaked CSS/listeners and no visual redesign. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Missing script/unsupported adapter error is visible and recorded; LLM/user HTML не исполняется.

**Task-specific tests:** Mount/unmount/remount, navigation/back/forward, repeated resize, representative full SVG/graph math samples at3 widths; all assets static audit. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Trusted HTML boundary only; no evaluate arbitrary user scripts; no assessed secrets in bundle.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-I03), trace docs/agent-traces/MS7-MIG-I03.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. All lesson delivery, widget adapters/lifecycle inventory и visual regression cases. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R04, MS7-MIG-V04, MS7-MIG-V05, MS7-MIG-I05

**Task-specific risks:** Виджет работает только при первом mount; old CSS persists.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Use tested full-document navigation per named lesson; no silent removal of interaction.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-I04 Account onboarding и разрешённые staff формы

**Status:** PLANNED

**Owner:** Илья

**Reviewer:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Task Approver:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Milestone Gate:** MIG-G2

**Relation to previous task:** Перенос MS7-I03 включая merged security fixes

**Что получим простыми словами:** React account and current staff mutation UI connected to real FastAPI. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Register/login/logout/profile/3 modes/restore/lost ack pass; current appearance/keyboard unchanged; no credential retention. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR05/06/10; MIG-NFR02

**HARD:** MS7-MIG-I01

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** MS7-MIG-V03, MS7-MIG-V02

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-i04-account

**Target start/window:** 10.10-11.10.2026

**Target deadline:** 11.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** MS7-I03; MS7-V02 consumer behavior: Перенести account/controller/forms на React и реальный FastAPI, сохранив password cleanup, retry/recovery, 30/150 limits, quiet state и permissions.

**Detailed Scope:**

1. Перенести merged I03 account/controller поведение на React с существующим дизайном и real API.
2. Login default/switcher, registration max30/backend150, old long username login, quiet anonymous state, GET-only restore retry.
3. Сохранить immutable pending body/key, fresh CSRF retry, password clearing/pending memory disposal и session reconciliation.
4. Grades paging uses real ID, profile patch and3 onboarding modes сохраняются; no fake diagnostic.
5. Перенести staff forms baseline с server authorization/CSRF/audit и безопасным подтверждением критичных операций.
6. Обязательная адаптация §17 (MS7-I03; MS7-V02 consumer behavior): Перенести account/controller/forms на React и реальный FastAPI, сохранив password cleanup, retry/recovery, 30/150 limits, quiet state и permissions.

**Область файлов:** frontend/features/account/staff, API adapter, component/E2E tests.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** React account and current staff mutation UI connected to real FastAPI. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Register/login/logout/profile/3 modes/restore/lost ack pass; current appearance/keyboard unchanged; no credential retention. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Terminal401/400/form switch empty passwords; stale response не overwrites newer input; retry does not mutate twice.

**Task-specific tests:** Port I03 transport/action/controller assertions to React, real PG browser flow, 30/31 input boundary, CSRF rotation/lost response, staff privilege tests. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** No localStorage/sessionStorage credentials; retry memory only while pending; private no-store/cache clear logout.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-I04), trace docs/agent-traces/MS7-MIG-I04.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. React account and current staff mutation UI connected to real FastAPI. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R04, MS7-MIG-V05, MS7-MIG-I05

**Task-specific risks:** React rerender loses frozen retry or retains password; role buttons treated as authorization.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Revert UI release before cutover; after target switch retain API compatible previous React build.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-I05 Браузерная совместимость доступность и parity

**Status:** PLANNED

**Owner:** Илья

**Reviewer:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Task Approver:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Milestone Gate:** MIG-G3

**Relation to previous task:** Новая browser acceptance перенесённого I01/I02/I03

**Что получим простыми словами:** Cross-browser report, parity evidence and resolved UI findings. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Required matrix passed; no blocking UI/security/visual drift; Илья не ставит собственный approval. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR02..06/10/12; MIG-NFR02

**HARD:** MS7-MIG-I03, MS7-MIG-I04

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** MS7-MIG-V05

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-i05-browser

**Target start/window:** 11.10-12.10.2026

**Target deadline:** 12.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** MS6-I01, MS7-I02, MS7-I03; topics/site/visual fixes: Подтвердить UX/schema/lifecycle/keyboard/security/visual parity новых React adapters по old-to-new fixtures и approved screenshots.

**Detailed Scope:**

1. Проверить Chrome/Edge/Firefox с actual versions; widths360/768/1440, no overflow and keyboard/focus.
2. Сравнить matched approved baseline/target screenshots: main/catalog/account/staff and all widget/style families.
3. Проверить no-JS public HTML, sitemap/404/redirects, console/network/hydration and page lifecycle.
4. Прогнать real anonymous/authenticated/offline503/CSRF/sessionexpiry/retry flows, raw input and state recovery.
5. Собрать sanitize screenshots/DOM/network evidence и передать findings; критичные проблемы исправляются до gate.
6. Обязательная адаптация §17 (MS6-I01, MS7-I02, MS7-I03; topics/site/visual fixes): Подтвердить UX/schema/lifecycle/keyboard/security/visual parity новых React adapters по old-to-new fixtures и approved screenshots.

**Область файлов:** frontend browser tests, docs/agent-traces evidence and scoped parity fixes.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** Cross-browser report, parity evidence and resolved UI findings. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Required matrix passed; no blocking UI/security/visual drift; Илья не ставит собственный approval. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Single Chromium walkthrough не называется cross-browser; unavailable browser recorded pending/blocker.

**Task-specific tests:** Playwright full E2E, lifecycle tests, source/asset all manifest checks, keyboard/focus and visual regression manual review. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Synthetic accounts only, screenshots redact PII/password, no sensitive DOM dumps.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-I05), trace docs/agent-traces/MS7-MIG-I05.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. Cross-browser report, parity evidence and resolved UI findings. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R04, MS7-MIG-I06

**Task-specific risks:** Большой набор screenshot скрывает непроверенный negative flow.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Keep previous frontend artifact; reopen specific task finding before final freeze.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

### MS7-MIG-I06 Frontend freeze и передача проверенной сборки

**Status:** PLANNED

**Owner:** Илья

**Reviewer:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Task Approver:** Руслан по UX/integration и Владимир по API/security; Илья не утверждает собственный результат.

**Milestone Gate:** MIG-G4

**Relation to previous task:** Final React handoff current version

**Что получим простыми словами:** Immutable frontend artifact, hashes, final evidence/run instructions and browser smoke. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Зачем нужна задача:** Reproducible build matches final backend; all scope tests pass; independent Руслан/Владимир approvals recorded. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Requirements covered:** MIG-FR02..06/12..16; MIG-NFR01/02

**HARD:** MS7-MIG-I05

**CONTRACT:** MS7-MIG-R02

**HANDOFF:** -

**INTEGRATION:** MS7-MIG-V06

**Что можно делать параллельно:** Другие Owner по принятому контракту; общие файлы имеют одного владельца.

**Inputs/contracts:** MIG_BASE_SHA и принятые exact versions названных dependencies; §§3-9; related sources из§20.

**Branch:** ms7-mig-i06-freeze

**Target start/window:** 13.10-13.10.2026

**Target deadline:** 13.10.2026, включая review/integration; календарь§11.

**Обязательная адаптация выполненных задач (§17):** Все frontend адаптации §17: Передать финальную React сборку, screenshots/test evidence и ссылки old-to-new для I01/I02/I03 и контента; не объявлять future exercise runtime реализованным.

**Detailed Scope:**

1. Создать final frontend build/SSG/assets manifest на integration inputs, проверить matching API/schema release.
2. Проверить clean npm ci/typecheck/tests/build/E2E, no private fixtures/credentials/checkers in bundle.
3. Зафиксировать all263 lesson sources/full URL coverage, retained design/legacy widgets and account/staff state.
4. Передать Руслану до12:00 hashes/build instructions/browser evidence/rollback release; final merge-ref smoke повторить.
5. Обновить current frontend docs and resume backlog, no assertion finished future exercise renderer.
6. Обязательная адаптация §17 (Все frontend адаптации §17): Передать финальную React сборку, screenshots/test evidence и ссылки old-to-new для I01/I02/I03 и контента; не объявлять future exercise runtime реализованным.

**Область файлов:** frontend release manifest/build docs/evidence, scoped final fixes.

**Out of Scope:** Редизайн и новая продуктовая функциональность; общие исключения§1; не менять frozen domain semantics.

**Deliverables:** Immutable frontend artifact, hashes, final evidence/run instructions and browser smoke. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Acceptance criteria:** Reproducible build matches final backend; all scope tests pass; independent Руслан/Владимир approvals recorded. Адаптация §17 по своей области выполнена; historical IDs/PR/approval сохранены; target evidence привязано к точному SHA и независимо проверено.

**Negative/failure acceptance:** Late asset/code change invalidates stale screenshots/build acceptance; no untested optimistic ready.

**Task-specific tests:** Final clean build, full type/unit/E2E, bundle scan, public HTML metadata/URL checks and final API smoke. Проверка ссылок original_result -> migration_follow_up -> target_evidence и неизменности frozen contracts/history в своей области.

**Task-specific security checks:** Private responses not bundled/cached; logout/recovery no secret retention.

**Live model/API requirement:** Live Product LLM не требуется; Codex engineering surface и реальные PostgreSQL/browser проверки по применимости.

**Evidence:** E(MS7-MIG-I06), trace docs/agent-traces/MS7-MIG-I06.md и final SHA/CI; правила§9.

**Handoff:** Accepted exact-SHA deliverables, contracts/commands/test evidence и outstanding blockers. Immutable frontend artifact, hashes, final evidence/run instructions and browser smoke. Записи old-to-new evidence index по указанным выполненным задачам и обновлённые current adapter/docs references.

**Downstream tasks:** MS7-MIG-R06

**Task-specific risks:** Frontend build version diverges from final backend/publication snapshot.

**DB migration impact:** Нет самостоятельного изменения schema; соответствующие изменения выполняет Владимир.

**API/schema impact:** Сохранять accepted wire contract; изменения только addendum R02 и owner-approved mapping.

**Switching and rollback:** Previous accepted frontend release only with compatible API/schema; data untouched.

**Task-specific DoD additions:** Unified DoD§9-11; accepted dependencies, positive/negative evidence, closed blockers и независимое approval. До main merge - ACCEPTED_INTEGRATION, не исторический DONE.

## 17 Как адаптировать уже выполненные задачи основного ТЗ

«Изменить выполненную задачу» означает обновить текущие platform-facing документы и создать новый accepted migration result. Исторический Task ID, initial scope, дата, PR/commit, проверки и решение approver не изменяются. Closed Issues остаются closed; original PR не переписывается. В current task index добавляются поля original_result, platform_disposition, migration_follow_up, target_evidence и current_status. У stale pending после реального approval добавляется новая current-status запись с источником; старый pending snapshot остаётся historical.

| Старый результат | Сохранить | Изменить или перенести | Новое подтверждение |
| --- | --- | --- | --- |
| R01 | Harness workflow/templates/domain invariants/history | AGENTS/PRODUCT/ARCHITECTURE/README, verify skill/entry, ADR platform sections, Issue/PR checklists | R01/R02/R03/R05 migration, ADR and final target CI |
| R02 | Four modes, typed steps, public/private split, versions/raw/hint/reveal | Только framework references в current addendum; frozen schemas не переписывать | R02 migration digest checks, I01 dispatcher parity |
| R03 | Exact Decimal policy, graph10/13, events/recent window reference | ORM examples и future persistence wording отдельно | Pure suites unchanged; migrated references/CI |
| MS6-R04 | Runner/contracts/FakeAdapter/check IDs/lifecycle/history | Verification command adapters и current setup guide | R03 migration Harness tests/CLI run |
| MS6-V01 | PostgreSQL16/config principle/explicit SQLite/no fallback/history | Django devserver/migrate/collectstatic/smoke -> target equivalents, images/locks/runbooks | V01/V05/V06 fresh/upgrade/restore/version/CI |
| MS6-I01 | UX screen map/states/mobile/keyboard/domain concept | Template-oriented examples -> React state/component architecture; wireframes без redesign | I01/I05 and R05 doc links/state parity |
| MS7-R02A | canonical routes/statuses/DTO/revision/idempotency/exposure and pins | Django-specific auth wording через security addendum; new content/staff delivery separate | R02/V02/V03/I04 contracts and races |
| MS7-R03A | CompletionFact/dual uniqueness/mirror neutrality | Future ORM adapters wording; no fabricated runtime | Pure R03A unchanged and R05 status reconciliation |
| MS7-V02 | credentials/profiles/roles/receipts/onboarding behavior | Django services/models/session -> target implementations | V01/V03/V06 PG parity incl cutover |
| Grades PR24 | ID vs number, pagination, Grade epoch, additive migration history | SQLAlchemy mapping/cursor signer/HTTP adapter | V01/V02 tests, original approval clarification |
| MS7-I02 | tokens, shapes, states, fixtures, approved dispatcher fix | React components/gallery/toolchain; debug isolation | I01/I05 schema/lifecycle/visual tests |
| MS7-I03 | account UX,30/150 limits, quiet state, password cleanup, retry | React controller/forms + real target API | I04/I05/I06 browser/security evidence |
| Topics/site/visual fixes | Accepted authored content and approved local appearance | Только technical integration/path references | R01 source manifest, I03/I05 visual parity |

Для R02A/R03A/grades missing explicit review record сначала уточняется; merge не отменяется автоматически и новый approval задним числом не создаётся. Для V02/I02/I03 API reviews подтверждены 07.10 и current records приводятся в соответствие. Frozen R01/R02/R03/MS6-R04/V01/I01 не переоткрываются.

### 17.1 Изменения основного ТЗ v7.2

R05 обязан выпустить полноценную новую редакцию основного ТЗ с changelog и source hash, сохранив v7.1. §§1-2: новый verified snapshot и отдельные historical facts. §§3-6: React/FastAPI/SQLAlchemy/Alembic, module ownership, existing IDs/fresh/upgrade. §§7-10: product semantics без изменений, только platform adapter terminology. §11: same canonical HTTP + accepted auth/content addenda + React UX. §§12-14: Harness вне product, обновлённая check registry без framework rewrite. §§15-16: target verification/ASGI/build/static/media/session/restore. §§17,21: migration task/Issue/branch integration exception и separate gates. §20: новый согласованный календарь. §§22-25: все карточки current/future framework deliverables, exact dependency matrix. §§26-29: FR/NFR/AT coverage и demo/report target references. §§30-32: новые migration risks, backward compatibility и baseline status.

Выполненные карточки сохраняют historical implementation и получают migration disposition, а не новые старые дедлайны. Невыполненные карточки сохраняют IDs, owners, scope и HARD/CONTRACT/HANDOFF/INTEGRATION; future Django models/views/templates меняются на repositories/API/React при сохранении contracts и DoD. Не заменять «Django» массовым search/replace в frozen proofs.

Все 52 canonical IDs основной очереди сверяются отдельно; новые18 migration IDs добавляются как отдельная программа. Knowledge/Assessment/Progress ещё не реализованы и после MIG-G4 остаются planned. I04 exercise renderer не считается завершённым тем, что все уроки отображаются в React.

### 17.2 Календарь основной программы после миграции

07-13.10 основной implementation backlog временно уступает migration; организационные ORG01/показ08.10/регистрация09.10 остаются в исходных датах. Работа после MIG-G4 планируется с14.10. R05 создаёт 52-row таблицу старой даты/actual acceptance/new forecast/reason/dependency/owner capacity. Простой перенос всех дат на неделю не является доказанной осуществимостью.

Для первичного обсуждения: G1 02.11 -> 09.11, G2 21.11 -> 28.11, G3 22.11 -> 29.11, G4 02.12 -> 09.12, G5 03.12 -> 10.12. Это только сценарий +7 дней для согласования и проверки critical path, не новые принятые даты. Сохранение03.12 требует отдельного подтверждённого capacity/dependency плана после migration; человеческие gates/полнота MVP не сокращаются. Новый календарь основного ТЗ утверждают трое; внешнюю дату защиты подтверждают отдельно.

## 18 Итоговая acceptance matrix

| ID | Сценарий и ожидаемый результат | Владельцы evidence |
| --- | --- | --- |
| AT-M01 | Remote+local approved snapshot, all source hashes, no lost edits | R01/R04 |
| AT-M02 | All current public URLs/content/assets/SEO/404/redirects match | V02/I02/I03/I05 |
| AT-M03 | Public lesson HTML без JS, formulas/SVG/widgets lifecycle, no redesign | I02/I03/I05 |
| AT-M04 | Register/login/logout/profile/3 modes/grades IDs and saved-state restore | V03/I04 |
| AT-M05 | CSRF/rotation/expiry/owner/staff/account privacy/password cleanup | V03/I04/R04 |
| AT-M06 | Concurrent registration/replay/conflict/shared rates; lost ack and cutover | V03/V06 |
| AT-M07 | Upgrade A/B/C and fresh retain IDs/hash/roles/constraints/timestamps | V01/V06 |
| AT-M08 | Publish/bootstrap/index/checks, locks/conflicts, interrupted activation recovery | V04/I03 |
| AT-M09 | Pure contracts/Harness checks retained, target CI including failures | R03/R04 |
| AT-M10 | 360/768/1440 and Chrome/Edge/Firefox keyboard/focus/error/retry | I05/I06 |
| AT-M11 | Clean build/staging/restore/performance and target no Django dependency | V05/V06/R04 |
| AT-M12 | Main spec v7.2,18 tasks accepted, final SHA/CI/PR/Issue closure/rollback | R05/R06 |

AT-M01..12 обязательны для MIG-G4. Каждый case содержит positive и named negative cases из карточек. Любой blocking gap оставляет Gate pending. Historical count тестов/страниц не hardcoded substitute acceptance. Обычный public HTML содержит только published reviewed sources; JS/HTML exports не содержат assessed secrets. Current visual baseline и private-state behavior сохраняются даже при успешной компиляции.

## 19 Риски и решения при отклонении

Главные риски: local/remote baseline divergence; устаревшая БД; существующие hash/session/receipt форматы; staff scope; публикация SQL+files+SSG; 97 local CSS и script lifecycle; CI triggers/integration merge; независимое review у трёх занятых Owner; лимиты Codex и работа в выходные. Каждый имеет owner в карточке и контрольный gate. Stop on data loss/leak/unknown schema. В день обнаружения записать blocker/owner/recovery/new forecast; не повышать model budget или scope без согласованного решения.

Временный legacy coexistence разрешён до MIG-G4 с owner matrix и отключёнными duplicate writes. После MIG-G4 normal startup/API/publisher/migration/verification не требуют Django. Если остаётся imported Django compatibility code, migrations via manage.py, старый /admin/ backend или публикация только legacy command, задача полного переноса не завершена. Legacy source history может сохраняться неисполняемой.

Rollback plan хранит prior application+frontend artifacts, data/schema compatibility matrix, DB+media snapshots, route/credential writer switch, pending receipts/session reconciliation и restore limits. Revert code безопаснее удаления таблиц; restore после новых writes может потерять данные и требует reconciliation/human decision. Нельзя обещать «всегда откатим БД» без измеренного drill.

## 20 Источники и границы проведённого анализа

Основное PDF ТЗ: C:/Users/Tramsey/Desktop/MathStart_Technical_Specification_v7.1_SECTION20_PARALLEL_DEADLINES_2026-10-01.pdf. Repository sources: AGENTS.md, PRODUCT.md, ARCHITECTURE.md, README.md, docs/architecture.md, docs/adr/ADR-0001..0005, specs/api/openapi-v1.json и DTO/policy, specs/exercises/R02, specs/progress/R03/R03A, docs/ux/MS6-I01, active plans/traces, verification skill, content/users models/services/tests/migrations и GitHub main additions.

GitHub API endpoints/immutable references: repository/main branch; PR2/5/7/8/10/11/14/15/19/20/22/24/26 metadata; Issue1/4/6/9/12/13/16/17/18/21/23/25; review submissions14/15/19/20/22/24/26; Actions main push37470970648 и PR head runs указанной таблицы. Account aliases только публичные GitHub owners/reviewers; passwords/PII не собирались. Public web page cache показывал старый3-commit snapshot и не принят за актуальное состояние; live API used.

Официальные технические источники, проверенные07.10: React Router pre-rendering https://reactrouter.com/how-to/pre-rendering; SQLAlchemy transactions https://docs.sqlalchemy.org/en/20/orm/session_transaction.html; Alembic autogenerate https://alembic.sqlalchemy.org/en/latest/autogenerate.html; FastAPI concurrency https://fastapi.tiangolo.com/async/. Pre-render требует явного dynamic URL списка; async не решает CPU; autogenerate миграции требует review. Новые version pins определяются compatible lock, не копируются из latest заголовка документации.

При подготовке этого ТЗ выполнены только repository/GitHub reads и PostgreSQL READ ONLY; полная repo verification/миграции/bootstrap/install/deploy не запускались. Созданы только данный документ и служебные файлы его генерации/QA. Новые GitHub Issues/branches/PR, implementation, изменение основного ТЗ и approval ledger пока не выполнены. Это deliverables семидневной программы после MIG-G0.

До старта нужны три конкретных решения: agreed local delta/source snapshot; acceptance reconciliation для R02A/R03A/grades; production host/approval либо явно staging-only delivery boundary. Остальные технические defaults описаны выше. Если они меняются, фиксируется versioned decision и применимая проверка, а не незаметное изменение задачи агентом.
