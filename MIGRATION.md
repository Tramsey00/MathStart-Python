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

- Общее задание продолжается в existing integration/ms7-mig-react-fastapi. Исходные a46daa9+dirty instructions/fixes/archive сохранены в360e75b, прежний checkpoint a2467ad не откатывался. Draft PR https://github.com/Tramsey00/MathStart-Python/pull/54 остаётся IN_PROGRESS; описание обновлено. Main, Issues и production не изменены.
- После a2467ad сохранены и завершены начатые bridge/security/service/admin/tests изменения: c1dd872 — durable DETACHED/EXPIRED, epoch-CAS rebind, private boolean-only permission-driven UI, combined User gate, Content readonly, native password_change/done, общая staff authorization lock и реальная гонка Group revoke/User write. c1dd872 exact Linux CI39034614979 PASS:167 frontend,33 source/read/golden,18 Chrome360,29 PG identity/staff; artifact12101274742 SHA256 b6e3b3e0276d4e0c1f77feb0a2ca4e0841ff36df33ac8d53a6dc3d37cec48aa3 проверен.
- 62197b3d25251b7f157af203cccb2aa65135b173 — Django-independent CLI check-lesson-sources/check-content-quality/check-site-integrity с сохранением старых helpers/policy; PG read-only snapshot, explicit report writes/nonzero failures/no misleading dry-run, confined storage. Baseline HTML quality checker переиспользован без Django; bs4/soupsieve взяты в точных версиях из сохранённого lock. Local7 tests+1 extended CLI subprocess PASS; DB digest unchanged,263 lessons/279 pages, negatives/HTTP404/redirect/report effects проверены. Команды и границы в backend/READ_RUNTIME.md.
- Exact62197b3 Linux CI39035330261 PASS:167 frontend tests/19 files,40 source/read/golden/content-command tests,18 Chrome360 scenarios/0 skips,29 PG identity/staff, preparation/build/initial activation/startup/cleanup/source guard PASS. Artifact12101498432 SHA256 028bdf09a1adc54181f042be6844fed611280ced701651ad4f42347c92ae1f00 проверен. Actual receipts ci-c1dd872-* и ci-62197b3-* в existing docs/acceptance/migration-execution/i02-verification/. Старые45a4a31 результаты остаются evidence только своего SHA.
- Текущий runtime commit ebe27f0003f50618ac12589e9405f7485acf5c2d опубликован: explicit same-owner login+original B proof rebind без дополнительной сессии, отказ key/login-only и foreign owner, durable auth-hash revocation всех owner sessions (включая независимые без bridge), запрет оживления старого cookie после hash restore, быстрый отказ revoked cookie. Local affected32 PG tests PASS(var/identity-admin-20261017-161324.log); финальный revoked-cookie/session delta2 PASS(var/auth-revocation-20261017-161452.log). Integrated push CI39035893192/PR39035897143 на момент записи RUNNING; сначала сверить фактический итог, не приписывать старый PASS новому SHA.
- General CI62197b3 pure/legacy PASS, полный target всё ещё SKIPPED/PENDING из-за пустого concrete command map (НЕ PASS). Full mandatory target/fresh/upgradeA/B/C, nine-project browser/visual/interactivity matrix и эксплуатационная приёмка не пройдены. Ближайшая общая engineering work: verified legacy cutover/checkpoint/import/F-proof recovery; полный admin role/permission/password/bulk inventory; publisher journal/staging/fencing/lease/takeover/recovery/ack и write CLI/index/bootstrap inventory; затем target command map, images/edge/dev/staging, disposable backup/restore/performance/cutover/rollback, полная source product-spec adaptation52 cards/versioned docs. Publisher сейчас поддерживает только отдельно маркированную synthetic initial activation — не считать recovery готовым.
- Все новые PostgreSQL runs создавали новый owned tmpfs mathstart-migration-verify на55441 и удаляли exact ID после name/label/tmpfs checks. HTTP fixtures остановлены с shutdown/join. Docker/Windows final check: owned container/listeners8131/8132/55441 отсутствуют; original mathstart-python-db-1/5432 работает и не тронут. Target/legacy env, raw ZIP/job logs и уникальные local logs сохранены в ignored var/. Keys/cookies/DSN не публиковались. Для следующих mutations нужна новая owned disposable БД.
- Общий кандидат НЕ готов; final independent reviewer НЕ запускался (по поручению после готовности всей работы). Status IN_PROGRESS/HUMAN_PENDING, не READY/COMPLETE. Не повторять unchanged full QA или пустой target prerequisite; использовать affected checks, затем обязательный полный run на общем готовом candidate. Продолжать ту же миграцию; старые traces/планы не являются заданиями.
