# Техническое задание: завершить миграцию MathStart на FastAPI и React

## Единая задача

Продолжить уже начатый перенос и получить воспроизводимую работающую версию
существующего MathStart на FastAPI и React. Сохранить учебный контент, данные,
адреса страниц, внешний вид, административные возможности и служебные операции.
Закончить реализацию, проверить объединённую систему и передать пользователю
один release-кандидат с инструкциями запуска и восстановления.

Это одно большое задание, продолжаемое между сеансами. Исполнитель сам выбирает
порядок связанных изменений. Не требуются отдельные поручения на backend,
frontend, документы или каждый внутренний шаг. Прежние персональные очереди,
календарь и ограничения «только одна страница/одна задача/один блок» отменены.
Старые обозначения карточек используются только для проверки полноты исходных
требований в существующих records, а не как самостоятельные задания.

Документ является действующим заданием на оставшуюся работу. Он не означает,
что она уже выполнена, и не запускает её без пользовательского поручения.

## От какой версии продолжать

Существующий execution checkout на этом компьютере:
`C:/Projects/MathStart-Python/migration-execution/integration`.
В другом клоне использовать его Git root. Ветка результата:
`ms7-mig-react-fastapi`. Исходный родительский checkout `C:/Projects/MathStart-Python`
остаётся старым main; не переносить его код или окружение поверх новой реализации.

При подготовке ТЗ remote migration находился на
`b8a93821eccf37eebaebe744460a9f9c6b002cc2`, local migration — на
`a46daa9eda4e3fa84be4da380fe4b39c23f59430` с незакоммиченными изменениями.
Эти SHA — ориентиры наблюдения, не указание откатиться. Перед работой проверить
актуальные local/remote refs, dirty files и состояние процессов.

Уже приняты и существуют: исходный snapshot и архитектурное решение перехода,
контракты совместимости, SQLAlchemy/Alembic-схема и upgrade-профили,
FastAPI Content/grades/staff-read API, основа React и API-adapter.
После них уже написаны и частично проверены публичные страницы/SSG/LessonHost,
доставка immutable releases, read-serving, инструменты проверок и регрессии.
Значительная часть этого кода включена в migration-ветку. Переписывать его с нуля
или повторять первоначальный bootstrap не нужно.

Есть опубликованные незавершённые наработки:

| Ветка | Что в ней сохранено |
| --- | --- |
| `ms7-mig-backend-execution` / `fdac6e6` | identity/session/staff-write implementation |
| `ms7-mig-frontend-i04-wip` / `bcdb121` | account/staff forms |
| `ms7-mig-documentation-checkpoint` / `07dad69` | новая редакция документации |
| `ms7-mig-frontend-execution` / `66c6639` | frontend и comparator correction |

Свежие SHA и уже включённые deltas проверить. Использовать полезный код после
анализа зависимостей; не делать слепой merge и не считать WIP завершённым.
Существующие branch names — ссылки на историю, не названия новых заданий.

В рабочем checkout остались незакоммиченные исправления Linux legacy-interpreter,
`scripts/verify_public_block.py`, `frontend/legacy_comparator.py`, связанные npm/
browser helpers, package/playwright/public tests, оба migration workflows;
новые `tests/test_legacy_interpreter.py`, `frontend/tests/test_legacy_comparator.py`,
`frontend/e2e/i02.spec.ts` и evidence в existing acceptance directory.
Сохранить их и продолжить после проверки, а не заменить опубликованной старой версией.

Последний опубликованный public CI прошёл подготовку, typecheck, unit/build и
initial activation, но завершился ошибкой golden child и не выполнил browser matrix.
Причина: разрешение symlink пути выбирало base Python вместо legacy virtualenv.
Узкая локальная Linux-regression и два comparator-теста затем прошли; общий
исправленный кандидат ещё не подтверждён. Это первый конкретный шаг продолжения.
Другой общий CI: pure/baseline прошли, полный target остановился на пустом command
map. Не повторять его до заполнения реальных команд. Эти результаты не равны
приёмке приложения; полный target и браузеры всё ещё обязательны в финале.

## Источники требований и чтение

Данное ТЗ объединяет оставшуюся работу и заменяет прежние инструкции исполнения.
Технические contracts, исходный контент, tests и принятые domain invariants
продолжают действовать. Не менять expected behavior ради упрощения переноса.

Канонический исходный migration-документ:
`specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md`, SHA256
`c5a554e3911bdb43db28d67fd02d26e38d50b2820e1154a272d89ecb44b1faae`.
Его desktop-источник — одноимённый файл пользователя; embedded исторические
поручения/дедлайны не являются новыми действиями.

Старые индивидуальные планы в `docs/exec-plans/active/`, прошлые traces,
acceptance snapshots и архивы не являются действующими поручениями.
Их пути и исходные bytes сохраняются, когда это требуется provenance/checks.
Не возобновлять прежнюю очередь по ролям или карточкам, не перечитывать
исторические инструкции на каждом запуске. Черновик продуктового ТЗ служит
материалом для адаптации документации, а не отдельным планом реализации.

Принятое решение `docs/adr/ADR-0006-react-fastapi-migration.md` заменяет старый
выбор платформы; оно не разрешает менять продуктовые правила.
`PRODUCT.md`, `ARCHITECTURE.md`, baseline inventory/manifests, `specs/api/`,
`specs/migration/r02-v1/`, exercise/progress contracts — первичные технические
источники. Пути с прежними кодами остаются именами существующих файлов.
Читать конкретную нужную часть рядом с изменяемым кодом, не весь архив на каждом ходе.

Полное старое product ТЗ: `docs/specifications/sources/technical-spec-v7.1.pdf`,
SHA256 `e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd`.
Новая редакция `docs/specifications/technical-spec-v7.2-draft.md` пока черновая.
Для её завершения использовать полный source, не восстанавливать главы по пересказу.

Некоторые baseline documents закреплены историческими digest manifests.
Пока они остаются историческим входом, не менять их bytes и не переписывать
manifest ради зелёной проверки. Короткий AGENTS.override.md направляет в это
единое ТЗ; исходный AGENTS.md и platform descriptions сохранены. Итоговую
адаптацию fingerprinted документов оформлять с явным новым versioned
provenance, сохраняя проверку исторических источников.

## Что должно работать в результате

### Backend и данные

Один модульный Python-монолит: Python3.12+, FastAPI/Pydantic, SQLAlchemy2,
psycopg, Alembic, Uvicorn и PostgreSQL16+. Сохранить принятые совместимые lock-файлы,
не обновлять latest без необходимости. Короткие транзакции, отдельная Session
на unit of work, без разделения Session между threads/tasks.

Обычные startup/API/auth/publisher/migrations/target verification не требуют
Django/DRF. Исторические fixtures/golden comparators могут использовать отдельное
legacy окружение. Не устанавливать Django в target ради прохождения comparator.
Сохранить opt-in SQLite для local non-concurrency development, если это требуется
принятым решением; PostgreSQL failures не скрывать fallback.

Сохранить реальные table/column identities, PK/FK/UUID, CHECK/UNIQUE/indexes,
sequences/defaults/timezones/timestamps и все существующие данные. Проверить
различия ORM on_delete и SQL actions. Не редактировать applied migrations,
не stamp непроверенную схему; изменения делать additive с проверенным SQL.
Исторические migrations и evidence сохраняются как история.

### Пользователи, безопасность и административные операции

Закончить существующие регистрацию, вход, выход, профиль, выбор класса и пути
onboarding с точными текущими HTTP contracts. Путь onboarding сохраняет выбор,
но не реализует будущую диагностику или изменение mastery.

Сохранить password hash algorithms/iterations и validators без массового reset;
opaque PG-backed sessions, login rotation, logout/expiry/revocation,
HttpOnly/Secure/SameSite cookies, CSRF bootstrap/header и Origin/Host checks.
Один origin для UI/API. JWT и credentials в browser storage не вводить.

Сохранить owner-bound receipts, digest/serialization/uniqueness, retention не
менее семи дней, anonymous bridge lifecycle и повтор запросов после lost ack.
Проверить logout/account switch/expiry/revoked proof, replay/conflict и concurrent
registration/profile writes. Rate limiting должен работать между workers;
trusted proxy policy не доверяет произвольному forwarded header.

Закончить весь baseline admin/staff inventory: Content list/detail/search/filter,
User/Group создание, изменение, роли/permissions, смену пароля, историю и
guarded deletion, включая delete-selected где оно было. Сохранить combined
permissions и PROTECT. Empty DB не повод убрать операции. Не добавлять новую CMS
или standalone Permission CRUD, если этого не было в inventory.
Проверки прав обязательны на сервере; видимость кнопки не авторизация.

Сохранить строгую обработку UTF-8/JSON, неизвестных/повторных полей, nonfinite
numbers, size limits, query/cursors, HTTP statuses/error envelopes/request IDs
и trailing slashes. Default FastAPI coercion/422/307 не должны незаметно менять
принятый wire behavior. Будущие endpoints не реализовывать fake success.
Identifiers передаются точно во всём разрешённом диапазоне, без JS rounding
и самовольной замены JSON integers строками. Grade PK отличается от номера класса.

### React, страницы и уроки

Закончить существующий React/TypeScript frontend на принятом Vite/React Router,
с existing CSS/tokens и визуальным поведением. Главная, каталог, структурные
страницы, поиск/навигация, страницы уроков и staff UI должны работать через
реальные target API/артефакты. Не добавлять global reset, новую UI library,
Tailwind/MUI/shadcn/Motion, редизайн или permanent Node SSR server.

Публичные страницы имеют полный предварительно сформированный HTML body/head
без выполнения JS, согласованные metadata/canonical/OG/lang, sitemap/robots,
redirect/404 и поиск GET без JS по принятому контракту. Не отдавать wildcard SPA200.
Node используется для build/publish. Private account/staff no-store, без PII
в public SSG, bundles, fixtures и cache.

Сохранить reviewed authored HTML, formulas, SVG, anchors, source paths,
local/shared CSS и scripts. Массовое JSX conversion уроков не требуется.
Проверить весь source/URL/asset inventory; исторические ориентиры263 темы,
97 local CSS и7 local JS не заменяют список и actual manifest.

LessonHost должен корректно обслуживать каждое семейство интерактивов:
tested mount/dispose или full-document navigation, верный порядок dependencies,
cleanup events/observers/RAF/timers и styles при переходе. Проверить remount,
back-forward, resize, scrolling, математические readouts, keyboard и controls.
Сохранить утверждённые visual fixes, исправить оставшиеся clipping/overlap/
нечитаемые SVG labels при обычном масштабе. Legacy details/self-check не становятся
assessed evidence. Вставлять только publisher-reviewed HTML; user/LLM строки escaped.

Account и staff forms подключить к real backend. Сохранить quiet anonymous state,
registration UI max30/backend150 и вход старых длинных username, реальные Grade IDs/
paging и три onboarding choices. Сохранить immutable pending request/key,
CSRF refresh, GET-first reconciliation, abort/stale response guards и очистку
password/pending credentials. Unknown mutation outcome не считать success
и не повторять unsafe POST автоматически.

### Контент, сборка и публикация

Закончить Django-independent source validation и deterministic component renderer
с golden HTML/math/SVG parity, identity/digest/conflict semantics и storage keys.
Перенести все команды исходного inventory: publication, bootstrap, index, source,
quality/integrity checks и сопутствующие операции. Проверить реальные side effects
dry-run, не обещать read-only без доказательства.

Сборка принимает проверенный immutable index/pages/assets с release identity,
полным inventory/digests/schema/trust/path/private-export validation. Активировать
release до HTML build не нужно. Сохранить принятый rendering contract:
`render_page(page, context, canonical_url)`, HOME alias/canonical,
`pinned_release`, filtered catalogue fields и `catalogue_full` для sitemap.
Page/context должны принадлежать одному выбранному release; не reread latest
в середине rendering. Защитить validated release от мутации renderer.

DB commit и file/SSG activation — разные ресурсы. Закончить staged output,
operation journal, durable pending owner, fencing/lease/takeover/recovery,
atomic descriptor switch и acknowledgement/reconciliation по контракту.
Publish/unpublish должны согласованно обновлять public HTML, catalogue,
sitemap, redirects и cache. Проверить сбои до/после SQL commit, build и activation,
stale owners и competing recovery. Failure не возвращает success.

Bootstrap twice не перезаписывает runtime edits или исторические evidence.
Сохранить retired pages и различие existing/fresh inventories, Grade epoch,
media/seed hashes. Cleanup ограничен owned operation paths; чужие материалы
и БД не удалять. Django/FastAPI live writes и Django/Alembic DDL на одних
owned таблицах одновременно запрещены.

### Запуск, обновление и восстановление

Получить воспроизводимые dev/staging и production-oriented configs/images:
Node build, ASGI, edge static/media, PG, health и отдельный release migration step.
Проверить proxy/cookie/storage permissions/no-debug/no-fallback. Clean clone
должен запускаться по документации без старых абсолютных путей/venv/worktrees.
Secrets остаются вне Git; использовать безопасные placeholders и local env.

Повторить fresh installation и все принятые populated upgrade profiles, включая
users/roles/profiles/receipts/pending, IDs/sequences/constraints/content/media.
Проверить реальный DB+media+frontend backup/restore в disposable среде, manifests,
auth/content, время восстановления и обычный API performance на описанном workload.
Новых AI performance claims не делать.

Отрепетировать maintenance/drain/snapshot/writer switch/один согласованный
re-login/retry/health и отзыв legacy writers только на synthetic/disposable данных.
Проверить app rollback до/после synthetic target writes, schema compatibility
и receipt reconciliation. Нельзя обещать разрушительное восстановление snapshot
как всегда безопасный rollback; при несовместимости описать forward recovery.

### Документация и полнота

Закончить полную новую редакцию основного product ТЗ с source/changelog/hashes,
сохранив старую. Сверить52 исходных product cards и dependency kinds без потерь:
принятые результаты остаются историей, future deliverables получают платформенные
эквиваленты и остаются future. Не придумывать новые сроки/персональные назначения.
Сохранить original-result -> platform-disposition -> target-evidence связи.

Согласовать текущие AGENTS/PRODUCT/ARCHITECTURE/README/content architecture,
verification skill, runbooks и Issue/PR guidance с фактическим target runtime.
Frozen schemas, mathematical references, historical tests/approvals/failures
не переписывать массовой заменой слов. Existing execution ledgers достаточно;
не создавать новую систему evidence или отчёт на каждую мелкую правку.

## Что не входит

Не реализовывать будущие Knowledge/Assessment/Progress persistence, диагностику,
Solution Analyzer, AI Tutor, adaptive practice, live Product AI и новые assessed
exercise scenarios. Не закрывать основные product milestones. Не добавлять
Redis/Celery/microservices, новую CMS/frontend framework или новые уроки.

Сохранить модульное владение: Content владеет topic-to-skill mappings и зависит
от Knowledge, не наоборот. Только Progress меняет long-term state по validated
evidence; GET не повышает mastery. Сохранить четыре modes, typed ordered steps,
raw/normalized input, deterministic validation, graph DAG, hint/reveal и secrecy.
Wrong final answer не доказывает misconception; unsupported parsing — отдельный
исход. LLM decisions schema/confidence validated, provider SDKs изолированы.
Это обязательные существующие contracts, а не разрешение реализовать новые домены.

## Как выполнять без лишнего расхода

Один основной исполнитель ведёт весь результат. Не запускать постоянную команду
backend/frontend/reviewer. Связанные файлы менять самостоятельно; не создавать
отдельный worktree, handoff или approval для каждой внутренней правки.
Не менять модель/усилие автоматически. Новый существенный выбор вне принятых
контрактов вынести пользователю как конкретное решение, продолжая независимую работу.

Один отдельный reviewer подключается к готовому общему кандидату. Раннее отдельное
review допустимо только для конкретного существенного риска schema/auth/publication/
recovery. Передать ему exact diff/base/head, нужный contract, summary проверок
и open findings; не всю историю чата. После fixes — проверка delta/findings,
полное повторное review лишь при существенном новом изменении. Не заявлять
independent review, если его фактически не было.

Читать минимально нужный контекст: данное ТЗ, короткую текущую запись в конце,
changed code/tests и соответствующий contract. Не перечитывать весь архив,
сотни source files или полное старое PDF на каждом продолжении. Inventory
и hashes проверять скриптами; raw logs хранить в artifacts, в контекст выводить
exit/failing assertion и короткий traceback. Длительные команды не опрашивать часто.

Проверки по возрастающей стоимости: reproducer/preflight -> affected unit/
integration -> полный final run. До дорогого browser run проверить interpreter,
imports, URLs и health. Совместимые среды переиспользовать. Не повторять неизменный
prerequisite FAIL; реализовать недостающий вход. Docs-only change с прежним
code/config/input не требует повторения полного прогона; старый run сохраняет SHA.
Новый final code candidate требует actual проверок. Не дублировать весь QA
исполнителя у reviewer без конкретной причины.

Если повторяется одна ошибка, проверять новую гипотезу, а не механически запускать
дорогой pipeline. При внешнем блокере сохранить причину/next action и продолжить
независимую работу. Не останавливаться на границе старой карточки. При лимите
сохранить checkpoint; продолжение после закрытия сеанса требует нового запуска.

## Проверка результата

Использовать существующие registry/helpers и закончить их реальные interfaces,
а не строить параллельный verifier. Полный target сейчас не готов; его нужно
сделать исполняемым. Все обязательные commands дают meaningful nonempty results,
failures/timeouts/missing tools/empty suites/required skips не становятся PASS.
Если промежуточный CI пропускает target с PENDING, финальная readiness проверка
обязана отклонить такой результат. Не получать зелёный final за счёт skip.

Из рабочего checkout с правильным interpreter доступны profiles:

```text
python scripts/verify_repo.py --profile pure
python scripts/verify_repo.py --profile target --list
python scripts/verify_repo.py --profile target
python scripts/fresh_install_smoke.py --profile target --disposable
python scripts/migration_smoke.py --disposable --source-profile A
python scripts/migration_smoke.py --disposable --source-profile B
python scripts/migration_smoke.py --disposable --source-profile C
```

`--list` не исполняет tests; default verify пока legacy, не target acceptance.
Frontend: compatible locked install, typecheck/unit/build и real browser tests.
Scope-specific browser run допустим в разработке; финал включает Chrome/Edge/
Firefox на360/768/1440, keyboard/focus, private/error/retry/expiry flows,
no-JS/SEO, lifecycle и matched visual evidence всех необходимых families.
Полный existing source/asset inventory проверяется отдельно от representative captures.

Сохранить все40 existing parity assertions и их negative cases из frozen matrix,
все12 итоговых acceptance scenarios, pure mathematical/HTTP/exercise/Harness
oracles и принятые DB/API regressions. Counts не заменяют точные ID sets и
содержание assertions. Технически должны быть доказаны:

- Source/data preservation, полный URL/content/assets/SEO inventory.
- Public HTML без JS, математическое поведение и корректные интерактивы.
- Identity/profile/onboarding/grades/admin и denied-access сценарии.
- CSRF/session/owner/privacy/password cleanup, replay/concurrency/rates/cutover.
- Fresh/upgrade schema/data compatibility и recoverable publication.
- Исполняемые CLI, pure/Harness/target CI, deliberate failure/timeout cases.
- Реальные браузеры/responsive/accessibility и отсутствие редизайна.
- Clean build/startup, backup/restore/performance и no-Django normal runtime.
- Полные актуальные документы, единый frontend/backend/schema/assets release,
  rollback и подготовленная финальная передача.

Все изменяющие проверки — только owned disposable data/runtime/ports.
Actual versions/locks, code/input SHA, dirty state, argv/cwd, exits/counts,
raw outputs/digests, CI actual checkout и cleanup фиксируются существующими
ledgers/trace. Не логировать DSN/password/session keys/PII. Старые runs не
переименовывать как выполненные на новом SHA и не перезаписывать failures.

## Git, сохранность и финиш

Не делать reset/clean/stash поверх чужой работы, force-push или массовое удаление
веток/worktrees. Прежние instruction copies и role profiles убраны из активного
набора в `docs/archive/migration-process-20261017/`; это historical-only архив,
не startup reading. Existing code/tests/evidence сохранены. Новые имена веток,
коммитов и артефактов — без брендовых приписок и рекламных trailers.

В рамках явно запущенной реализации разрешены scoped commits, push migration
refs, disposable tests и draft final PR. Перед push проверить advancement remote;
сохранить связанные незавершённые изменения честными WIP checkpoint, не смешивая
их с утверждением готовности. Не выполнять main merge, Issue closure, production
writes/deployment или сообщения людям/чатам без отдельного решения пользователя.

Цель достигнута технически, когда вся существующая функциональность перенесена,
обязательные проверки реально пройдены на согласованном combined code candidate,
отдельное final review не имеет unresolved blockers, clean запуск/обновление/
восстановление воспроизводимы, документация/rollback/release artifacts готовы.
Передать пользователю candidate SHA, draft PR, запуск/демонстрацию, summary
проверок и список ожидающих решения действий. Статус READY_FOR_HUMAN_ACCEPTANCE.
Фактическая human acceptance/main merge/main CI/Issue closure и public deployment
не подделываются; пока они не выполнены, финальный migration gate не COMPLETE.

## Короткая запись для следующего запуска

- Продолжениеa2c52f4/abda9b7 в том же checkout/ветке; текущую вершину брать из `git rev-parse HEAD`. Draft PR54 остаётся IN_PROGRESS/HUMAN_PENDING. Предыдущие короткие записи архивированы в `docs/acceptance/migration-execution/continuation-history-7f51b84.md`; их next actions устарели. Main/production/Issues не менялись.
- Exact push CIa2c52f4 проверен без rerun: general39056852707 и public39056852688 SUCCESS; backend-install117466471940 —279 tests/0 skips, fresh1654, upgrades421/423/424. Artifacts12110251663 SHA256b1a5f7a7a50b32ea75094d557d2600c9c6bfec6ba50cf2ed3e9a2843f1d4baa0 и12109534740 SHA256e956ae4ebd26e071a912a72b95013d55940001b9671f6d7130a78f68b6ab33af скачаны/проверены. Safe receipts `i02-verification/ci-a2c52f4-*`. Full target117466519554 SKIPPED, не PASS. CI7f51b84/2d707db сохранены как evidence своих состояний.
- Добавлены новые content IDs/source registration и full bootstrap edition через P1, сохранение retired pages/private rows/media/IDs/timestamps, чистые previews; INDEX CLI с полной byte parity фактическому Django oracle. Усилен cutover snapshot/password inventory и publication writer barrier для retained Django history. Адресные PASS: INDEX3, cutover13, protocol18, password/cutover17, editions10, source/registration8, participant7, final source-snapshot3. Это последовательные scoped runs до последующих deltas, не общий QA; точные IDs/log hashes/scopes в `i02-verification/content-cutover-delta.json`.
- Полный bootstrap пока FAIL: build279 страниц и SQL activation получены, но public verification не завершилась. Сохранены timeout600s, диагностическая попытка с clock discontinuity, native0xC0000005 и последняя PUBLIC_VERIFICATION_FAILED/484.170s. Последняя проверила первые2 bootstrap/CLI tests PASS, включая prepare-bootstrap dry-run; затем full publication FAIL. Добавлен safe trace последних public paths/status/timing, но он ещё не запущен. Следующее конкретное действие: запустить только failing full-bootstrap test с новым trace; найти и исправить причину, без объявления activation/первых2 тестов успехом всей публикации. Первые успешные tests не повторять отдельно без изменения.
- Убрана ненужная загрузка site-sized journal plan из descriptor/immutable metadata reads; bounded output-pin reuse перепроверяет PostgreSQL xmin/ctid/authority каждый запрос.4 PG cache/tampering tests и25 HTTP regressions PASS;30 R03 adapters PASS. `scripts/verify_target.py` добавлен: owned DB, настоящий build, ASGI/comparator, все16 registry entries и4 install rehearsals; group/dirty runs только development. Реальный managed запуск ещё NOT_RUN. Его scoped build/backend/database/content шаг подключён в backend-install CI; map PARTIAL, full nine-browser target и final contract QA не выполнены.
- Начаты отдельные `deploy/Dockerfile` API/frontend-builder targets; оба images собраны, API read-only/non-root/network-none imports PASS с Python3.12.15/FastAPI0.115.12/SA2.0.46/Uvicorn0.34.2, Django/Node отсутствуют.3 actual HTTP readiness tests PASS. Base digests закреплены по фактически собранным inputs. Actual builder prerender, API с DB/артефактами, edge/proxy/dev/staging/release migration step ещё не проверены/не завершены; команды и scope — `deploy/README.md`.
- После bootstrap fix: real managed orchestration delta, остальные infrastructure/clean clone/backup+restore/performance/cutover+rollback, full admin inventory и40 parity/12 acceptance IDs, полная v7.2 редакция/52-card disposition/versioned docs, nine-project browser/visual/widget matrix. Затем combined final QA, один independent reviewer, исправления и affected rechecks. Это одна продолжающаяся работа; checkpoints не её завершение. Все mutating checks только owned disposable data; исходный mathstart-python-db-1:5432 не трогать. Перед новым helper проверить ownership/порты; завершённые helper tmpfs containers удалены. Коммиты/push/draft PR разрешены.
