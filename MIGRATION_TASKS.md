# Очередь миграции и критерии результата

Исполнять вместе с [инструкцией координатора](MIGRATION_AGENT.md).
Все сокращения R/V/I здесь имеют префикс `MS7-MIG-`.
Карточки канонического ТЗ остаются полным техническим требованием; этот файл
задаёт рабочую очередь и обязательные выходы без персональных очередей и сроков.

## 1. Источники и принятый baseline

- [Каноническое ТЗ на принятом коммите](https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md).
- `specs/migration/r02-v1/dependency-policy-v1.json`: formal dependency kinds.
- `specs/migration/r02-v1/parity-matrix-v1.json`: все 40 assertions с negative cases.
- `docs/acceptance/MS7-MIG-R01/inventory.md`: routes/admin/commands/source inventory.
- [R03 interface checklist](https://github.com/Tramsey00/MathStart-Python/blob/fb39647beb983a4f488ad82d4984d3f96e87b9a8/docs/acceptance/MS7-MIG-R03/cli-receipt-handoff-checklist.md).

| Принято | Issue | PR | Что использовать |
| --- | --- | --- | --- |
| R01 | #28 | #46, #47 | Baseline, ADR-0006, inventory, manifests, preservation |
| R02 | #29 | #48 | Frozen migration contracts, schema/auth/publication/parity |
| V01 | #34 | #51 | SQLAlchemy/Alembic, fresh и upgrade A/B/C, constraints |
| V02 | #35 | #53 | Content/grades/transport/staff reads, immutable release reader |
| I01 | #40 | #50 | React foundation, API adapter, types, locks, gallery |

Повторная проверка регрессий обязательна; повторная реализация этих пяти задач
не нужна. Historical test counts не являются обязательной фиксированной суммой:
сохранить case IDs/assertions и покрыть новые изменения. Принятые Issues могут
оставаться OPEN до финального main workflow.

## 2. Формальные зависимости оставшихся задач

`H` — HARD, `C` — CONTRACT, `I` — INTEGRATION. CONTRACT для каждой задачи — R02;
для R05 также frozen product contracts, для R06 accepted ADR/addenda.
HARD определяет возможность полноценной реализации; INTEGRATION обязателен
для технического закрытия, но не запрещает раннюю подготовку частей.
В новом процессе проверенный кандидат может служить входом следующего этапа
по правилам AGENT; это не перенос исторического approval.

| Задача / Issue | H | I | Техническая роль |
| --- | --- | --- | --- |
| R03 / #30 | R02 | V02, I02 | координатор |
| R04 / #31 | R03 | V03, V04, V05, I03, I04, I05 | рецензент + координатор |
| R05 / #32 | R01, R02 | R04 | координатор |
| R06 / #33 | R04, R05, V06, I06 | — | координатор |
| V03 / #36 | V01 | V02 | backend |
| V04 / #37 | V02 | I03 | backend |
| V05 / #38 | V01 | V03, V04, I03, I04 | backend |
| V06 / #39 | V05, R04 | — | backend |
| I02 / #41 | I01 | V02 | frontend |
| I03 / #42 | I02 | V02 | frontend |
| I04 / #43 | I01 | V03, V02 | frontend |
| I05 / #44 | I03, I04 | V05 | frontend + рецензент |
| I06 / #45 | I05 | V06 | frontend |

Функциональные зависимости полных R03 checks могут требовать частей V03,
V04 и I03. Это конкретные исполняемые входы; не добавлять фиктивный HARD R04
для R03. V03 не является HARD V04, I03 не является HARD I04.

## 3. Рекомендуемые волны работы

1. BOOTSTRAP: свежие refs, isolated checkout, пакет, R03 intake, tooling inventory,
   воспроизводимые baseline checks и real evidence ledger.
2. FOUNDATION-CONTINUATION: V03 identity; V04 source renderer + immutable build
   inputs; I02 страницы/SSG с нуля; R03 reusable adapters и pure/Harness;
   R05 чтение источника и подготовка mapping. Разделить backend slices при
   параллельной работе, оставив одного владельца Alembic.
3. CURRENT-BEHAVIOR: I03 уроки после I02; I04 формы после V03; V04 publication
   с готовым renderer; полный R03 после необходимых runtime/CLI/browser inputs.
4. SYSTEM-VALIDATION: V05 эксплуатация/restore, I05 browser/visual, R04 общий audit
   после R03 и всех его integration inputs. Findings возвращаются исполнителям.
5. RELEASE: завершение R05 после audit, V06 rehearsal после V05/R04, затем I06
   freeze с V06, затем R06 единый пакет. Повторить итоговые проверки на одном SHA.

Волна не является барьером для независимого среза. Не ждать полной готовности
всех задач одной строки, если конкретный следующий вход уже проверен.

## 4. Обязательные результаты по задачам

### R03 — продолжить существующий implementation

- Проверить и принять в работу PR49 без объявления его принятой задачей.
- Сохранить registry IDs/group semantics, nonrecursive Harness, pure R03/R02A/
  R03A/R02 и negative runner/timeout/failure coverage.
- Заполнить реальные 10 backend/4 frontend command interfaces и receipts.
  Пустой runtime command map сейчас является незавершённостью, а не PASS.
- Отдельно учитывать baseline/legacy comparator environment и target без Django.
- CI: migration task/integration и final main PR, exact checkout/workflow/event/
  merge-ref linkage, locks/versions/PG/fresh/upgrade/content/frontend/browser.
- Закрытие: весь применимый pipeline выполнен, реальные CLI side effects и
  cleanup проверены, ошибки дают nonzero, отдельный review root integration.

### V03 — identity, session, receipts, staff writes

- Все семь существующих identity operations и профиль/onboarding; exact HTTP
  policy, validators и retry semantics. Onboarding не создаёт mastery.
- Совместимые encoded hashes/password validators без обязательного reset;
  PG opaque sessions, rotation/logout/expiry/revocation, CSRF/Origin/Host,
  shared worker-safe rates и explicit trusted-proxy policy.
- Owner-bound receipts, digest/serialization/uniqueness, retention не менее
  семи дней, anonymous bridge lifecycle, lost acknowledgement, replay/conflict,
  concurrent registration/profile updates и cross-cutover retry.
- Полный baseline User/Group staff-write inventory, server permissions/audit,
  создание/изменение/пароли/роли/history/guarded deletion/delete-selected.
  Сохранить PROTECT и combined permissions; отсутствие записей в БД не отменяет
  тестирование операций. Не вводить новую CMS.
- Закрытие: real PostgreSQL positive/negative/race suites и consumer contract
  review; новый lock/runtime не использует Django hashers/setup.

### V04 — сделать с нуля

- Django-independent source validator/component renderer с golden HTML parity,
  исходными paths/digests/identity/conflict semantics, math/SVG/CSS/JS inventory.
- Сначала передать I02 **H-BUILD-INPUTS**: immutable `index.json`, все referenced
  `pages/<id>.json` и assets, полные hashes/sizes, release identity, source SHA,
  schema/trust/path/private-export/coverage validation. Active descriptor
  и полная activation не являются условием этого входа.
- Перенести **все** management/CLI операции из R01 inventory, включая publication,
  bootstrap, index, source/quality/integrity checks. Зафиксировать реальные
  side effects dry-run; не обещать read-only без доказательства.
- Staged build + operation journal + durable pending ownership/fence/takeover;
  SQL commit, file/SSG activation и acknowledgement проверяются отдельно.
- Failure/recovery до/после commit/activation, competing/stale owners,
  publish/unpublish freshness, catalogue/sitemap/cache coherence, bounded cleanup.
- Bootstrap twice, сохранность runtime edits/evidence, retired pages/Grade epoch,
  storage keys и seeds. Никаких writes в пользовательскую рабочую БД.
- Закрытие: реальный публикационный цикл с I02/I03, PostgreSQL concurrency,
  target CLI/renderer/restore interfaces и negative tests.

### I02 — сделать с нуля

- Использовать I01 foundation и принятый V02 adapter contract. Перенести главную,
  каталог/структурные страницы/navigation/search и current staff-read оболочку.
- SSG по полному manifest из verified immutable V04 input, HTML body/head без JS,
  title/meta/canonical/OG/lang, sitemap/robots/redirect/404. GET-поиск должен
  сохранять согласованное поведение без JS. Не отдавать wildcard SPA 200.
- Сохранить V02 `render_page(page, context, canonical_url)`, HOME alias/canonical,
  `pinned_release`, семь filtered catalogue fields и `catalogue_full` только
  для `/karta-sajta/`; page/context должны относиться к одному release.
- Lossless JSON integer/ID/FK boundary Python/TypeScript: не округлять int64
  через JS Number, не менять frozen numeric schemas на строки или произвольные
  ограничения. Отдельные runtime validators, generation types не заменяет их.
- Private data/fixtures не экспортировать. Реальные serving/API/browser checks
  отличать от unit fixtures и SSG build. Asset/release retention проверять с V04.
- Закрытие: полный URL/body/SEO/private-exclusion manifest и браузерный smoke
  на реальном FastAPI; вход, output HTML и activation имеют отдельные receipts.

### I03 — все уроки и интерактивы

- LessonHost для reviewed HTML, math/SVG/assets и локальных CSS без массового JSX.
- По исходному inventory проверить 263 темы, 97 local CSS, семь local JS и shared
  dependencies; числа сверить с manifest, не использовать вместо полного списка.
- Каждому script family назначить mount/dispose либо tested full-document
  navigation; проверить StrictMode/remount/back-forward/resize/scroll, cleanup
  listeners/observers/RAF/timers и отсутствие CSS от предыдущего урока.
- Сохранить anchors, axes/arrows/readouts/controls, mathematical behavior,
  table/formula overflow; legacy details/self-check остаются unassessed.
- Закрыть исходные visual F01–F04 с доказательством; сохранить publisher handoff.
- Закрытие: все семьи интерактивов и ресурсов покрыты, golden/browser evidence
  на 360/768/1440, реальная интеграция I02/V02/V04.

### I04 — account и staff forms

- Реальные login/register/logout/profile/grade/onboarding flows с V03/V02,
  прежний дизайн и quiet anonymous initial state.
- Registration UI max30/backend150, вход старых длинных username, три onboarding
  choices, real Grade PK и pagination. Сохранить baseline UX/recovery.
- Immutable pending body/key и in-memory retry, свежий CSRF, GET-first
  reconciliation; неизвестный outcome не считать success и не повторять POST
  автоматически. Очистка пароля и pending credentials при нужных переходах.
- Все baseline staff forms с server authorization/CSRF/audit и безопасным
  подтверждением критичных действий. Credentials не хранить в browser storage.
- Закрытие: реальные PostgreSQL/API/browser flows, expiry/logout/account-switch,
  lost response, stale responses, denied permissions, cleanup и no-store.

### V05 — эксплуатация

- Воспроизводимые dev/staging и production-oriented images/configs: Node build,
  ASGI, edge static/media, PG, health, отдельный release migration step.
- Без debug/fallback; trusted proxy, cookies, storage permissions, env/docs.
- DB+media+frontend backup и восстановление в изолированной среде с manifests,
  проверкой content/auth и измеренным временем. Измерить обычный API p95/errors
  на описанном workload; AI performance остаётся вне объёма.
- Закрытие: clean startup/build/restore и operations runbooks на реальном
  составе V03/V04/I03/I04; публичный deployment не заявлен выполненным.

### I05 — browser, accessibility и parity

- Chrome, Edge, Firefox с actual versions, widths360/768/1440; keyboard/focus,
  no overflow, matched baseline/target screenshots и все widget/style families.
- No-JS HTML, URLs/SEO, network/console/hydration, lifecycle; anonymous/auth/staff,
  offline503/CSRF/expiry/retry flows на реальном backend.
- F01–F04, fixture-only overlap (#52), I01 query validation P3 закрыть до freeze.
- Закрытие: полная matrix с raw sanitized evidence и отдельным review.
  Один Chromium или наличие Playwright dependency не равны этой проверке.

### R04 — отдельный аудит объединённой системы

- Reviewer, не автор проверяемых изменений, проверяет все 40 parity rows и
  AT-M01–AT-M12, security/permissions/receipts/cursors/concurrency/recovery,
  данные/источники/URLs/admin, bundle/export secrets, no-redesign и no-Django.
- Проверить фактические fresh/upgrade/restore/browser outputs и §17 linkage.
- Findings имеют severity, source lines, reproduction, regression и disposition.
  Blocking findings исправляются исполнителем и проверяются повторно.
- Закрытие: zero unresolved blocking findings на объединённом candidate SHA;
  явно перечислены финальные человеческие действия R06/AT-M12.

R04 проверяет фактически готовую интеграцию до финального freeze. V06 затем
повторяет уже доказанные migration/cutover сценарии на окончательной сборке,
I06 фиксирует frontend, а reviewer делает release delta review для R06.
Не требовать завершённый R06 или main merge как вход для R04. При этом нельзя
отложить отсутствующую реализацию/первичную проверку security, recovery или
данных на V06 и назвать R04 пройденной: поздний этап повторяет проверки,
а не впервые доказывает обязательное поведение. AT-M12 на этом этапе отражает
готовность процесса/пакета и ещё не выполненные финальные действия по отдельности.

R04 проверяет фактически готовую интеграцию до финального freeze. V06 затем
повторяет уже доказанные migration/cutover сценарии на окончательной сборке,
I06 фиксирует frontend, а reviewer делает release delta review для R06.
Не требовать завершённый R06 или main merge как вход для R04. При этом нельзя
отложить отсутствующую реализацию/первичную проверку security, recovery или
данных на V06 и назвать R04 пройденной: поздний этап повторяет проверки,
а не впервые доказывает обязательное поведение. AT-M12 на этом этапе отражает
готовность процесса/пакета и ещё не выполненные финальные действия по отдельности.

### R05 — документация переноса, не новые функции

- Прочитать полный v7.1 по source path/hash из STATE, выпустить полную v7.2
  в редактируемом source format с changelog/hash; сохранить исходную редакцию.
  Если требуется PDF-поставка, собрать и визуально проверить её соответствующим
  инструментом. Краткое addendum не заменяет полный новый документ.
- Все 52 canonical product task IDs и dependency kinds сверить без потерь;
  completed -> historical result/platform disposition/target evidence,
  planned -> platform-equivalent deliverables, сохраняя будущими.
- Полный §17 old-to-new evidence index; current AGENTS/PRODUCT/ARCHITECTURE/
  README/docs architecture/verification/runbooks/Issue-PR templates.
- По пользовательскому изменению процесса новый migration calendar и персональные
  назначения не выпускать; вместо прогноза — dependency/readiness table.
  Исторические даты/принятия хранить как provenance. Новых обещаний по основной
  программе/защите не делать; организационные изменения вне миграции не выдумывать.
- Закрытие: нет текущих противоречий платформы, все 52 строки и §17 покрыты,
  будущие домены остаются planned, итоговые документы соответствуют runtime.

### V06 — финальная репетиция backend

- Fresh и upgrade A/B/C повторить на итоговом release candidate, включая
  sequences/profiles/roles/passwords/receipts/media/content manifests.
- На disposable данных проверить maintenance/drain/snapshot/writer switch,
  один согласованный re-login, retries, legacy writes revocation и health.
- App rollback до/после synthetic target writes, совместимость схемы и receipt
  reconciliation; при несовместимости документировать forward recovery.
- Закрытие: actual rehearsal/restore evidence, hashes/runbooks и backend freeze;
  production DB не переключена.

### I06 — финальная frontend-сборка

- Clean locked install, types/unit/build/E2E и complete SSG/assets manifest,
  matching backend/schema/content release, no private exports/checkers/credentials.
- Full source/URL coverage, retained design, all widget/account/staff states,
  final smoke на сборке для V06, previous compatible artifact для rollback.
- Закрытие: immutable artifact + hashes + инструкции, повторные проверки
  после любого позднего изменения relevant code/assets.

### R06 — единая передача

- Собрать один candidate SHA и matching backend/frontend/schema/assets/docs,
  все technical task/review receipts, final CI и проверенный rollback package.
- Подготовить draft final PR migration -> main, mapping всех 18 Issues,
  release summary, запуск/демонстрацию и resume map основной программы.
- До решения пользователя: `READY_FOR_HUMAN_ACCEPTANCE`, main merge/Issue
  closure/MIG-G4 и публичное переключение явно pending. Не отмечать AT-M12
  полностью PASS только по подготовленному PR.
- После отдельного решения на merge: проверить действительный main SHA/CI,
  closure каждого Issue и ledger. Production deployment требует своего решения.

## 5. Обязательные follow-ups

| Источник | Требование | Исполнение / проверка |
| --- | --- | --- |
| R01/R02 visual F01–F04 | Сохранить все исходные критерии, включая F04 при обычном масштабе | I03 / I05 |
| I01 Issue #52 | Постоянная fixture-only маркировка без перекрытия UI | frontend / I05 |
| I01 API review P3 | null/arrays/scalars query -> INVALID_REQUEST до fetch, negative tests | frontend / I04/I05 |
| V01 nonblocking helper follow-up | Прочитать исходный finding, решить в его фактическом scope | backend / R04 |
| V02 preservation/whitespace policy | Исторические FAIL/scoped PASS не переписывать; новые delta проверять | координатор / R04 |

Visual F01–F04 не путать с уже закрытыми V02 asset F01/F02. Новые обнаруженные
дефекты регистрировать отдельно; принятое source exception не означает waiver
корректности итоговой React-версии.
