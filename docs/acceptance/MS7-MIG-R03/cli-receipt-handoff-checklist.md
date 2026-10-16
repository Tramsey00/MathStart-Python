# R03 CLI/receipt handoff checklist — 2026-10-12; dependency update2026-10-16

Статус checklist: **PREPARED_FOR_OWNER_REVIEW**. R03: **INCOMPLETE**.
Это review checklist в зоне R03; согласованность с deliverables проверена по
принятому ТЗ и parity matrix. Подтверждение checklist владельцами и независимые
Task Approvals R03 пока не получены.

Текущий принятый integration input:
`a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6`.
MIG_BASE_SHA: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
Предыдущие inputs `0c03197e23f69a233c0fcf8bdffa336feca20b92` и
`8d958aeeb17da46839722441425ccbb5889e2ab7` сохранены в provenance.
I01/V01/V02 — ACCEPTED_INTEGRATION. Для V02 проверены human review5538854677,
squash a359b0b / parent0c03197 / равенство дерева74c30145 с approved8256cbf:
[текущий receipt](v02-integration-a359b0b/README.md). Consumer source review
8256cbf/47baaa9 не принимает полный I02 pipeline. Принятые service/locks/tests
V02 доступны; root CLI/receipt adapters ещё требуют review. I02 и применимый
V04 CLI, полная композиция и независимые R03 approvals остаются pending.
Конкретный текущий внешний блокер I02 — **H-BUILD-INPUTS: verified release
build-input handoff от V04/Владимира**. I02 может напрямую читать проверенные
immutable index/pages/assets; ждать fully activated release для SSG build
не требуется. Build-input validation, HTML build и activation/publication
разделены ниже; остальные обязательные checks R03 сохранены.
Исторические совместные I01/V01 successful CI receipts сохранены
в [текущем handoff](accepted-integration-ci-20261012.md).

Историческая проверка refs и GitHub PRs 2026-10-12: принятых migration V02/I02/V04
deliverables нет. Issues35/41/37 OPEN; branches `ms7-mig-v02-content`,
`ms7-mig-i02-pages`, `ms7-mig-v04-publishing` не опубликованы. Имеющаяся
`codex/ms7-v02-grades-api` относится к прежней MS7-V02, а не migration V02.
До поступления принятых входов полный target запуск не выполняется повторно:
его известный prerequisite FAILURE не выдаётся за выполненную проверку.

## Источники и роли

- [Migration v1.1](../../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md):
  §§5–9, cards R03/V02/I02/V04 и §17.
- [R02 parity matrix](../../../specs/migration/r02-v1/parity-matrix-v1.json)
  и [R01 inventory](../MS7-MIG-R01/inventory.md): исходные assertions, семь
  content commands, URL/admin inventory и негативные случаи.
- [Машинный checklist](../../../specs/migration/r03-v1/cli-receipt-handoff-v1.json):
  все10 backend checks,4 frontend checks, владельцы, формы intake/review.
- [Операционный handoff](../../../specs/migration/r03-v1/runtime-commands.json)
  остаётся PENDING с пустым `commands`; checklist не активирует dispatch.
- `scripts/target_check.py`, `scripts/target_verification.py` и
  `.github/workflows/migration-ci.yml` определяют существующие R03 interfaces.

| Зона | Владелец deliverables | Review/потребитель |
| --- | --- | --- |
| V02 Content/grades/routes/staff read API, manifest и transport | Владимир / VladimirFrolov777 | Руслан; Илья подтверждает consumer/browser handoff, где применимо |
| I02 public/current staff read pages, SSG/SEO и asset manifest | Илья /13baybars | Руслан — UX/integration; Владимир — API/security |
| V04 publisher/bootstrap/index/check CLI, media, journal/recovery | Владимир / VladimirFrolov777 | Руслан; Илья — consumer/browser handoff, где применимо |
| V03 current identity/session/receipt/staff-write runtime assertions | Владимир / VladimirFrolov777 | Руслан runtime/security review; Илья consumer where applicable |
| I03 LessonHost/math/SVG/scripts/lifecycle handoff | Илья /13baybars | Руслан UX/integration; Владимир API/security; полная I03 приёмка по её карточке |
| Принятые V01 schema/fresh/upgrade assertions | Владимир / VladimirFrolov777 | R03 связывает существующую реализацию с reviewable CLI/receipt; реализация V01 не расширяется |
| Registry, root wrappers, CI, intake и §17 trace | Руслан / Tramsey00 | Владимир и Илья — независимые Task Approvers R03 |

## Обязательный пакет от владельца

- [ ] Task ID, source PR/полный40-character SHA, scope и source/contract digests.
  Для результата, заявленного как accepted task: human approval IDs, merge
  SHA/parents, integration SHA/tree. Для обязательного full I02 нужны обе зоны
  approval; полные V02/V04 принимаются Русланом с применимым consumer review.
- [ ] Для scoped CLI/renderer/LessonHost handoff отдельно: exact source SHA,
  paths/locks/inventory digests, область independent artifact review и consumer
  compatibility, реальные positive/negative evidence. Этот review не является
  Task Approval V04/I03 и не разрешает early merge; требования full receipts
  применяются только к формальным accepted-task gates, названным ниже.
- [ ] Версия контракта/manifest, SHA256 всех передаваемых scripts/locks/case
  inventories, пути raw evidence и список §17 original_result → follow_up → target_evidence.
- [ ] Для каждого backend check: существующий `backend/... .py` файл, точный
  `args` array, cwd=root, env names, права/side effects, service/port/DB/runtime
  ownership, deadline и teardown. Передаются реальные paths; пустое поле блокирует review.
- [ ] Для frontend: точные package scripts/lock/tool versions, build/SSG roots,
  API/release manifest pins, browser/service startup-health-stop commands и
  fixture/real API boundary. `test:e2e` должен существовать и завершаться сам.
- [ ] Positive и negative commands с exit codes, versions, collected/passed/
  failed/skipped counts, case IDs и raw stdout/stderr. Документированные counts
  и пример receipt не являются результатом запуска.
- [ ] Список открытых замечаний с классификацией blocking/nonblocking и
  человеческим решением о допустимом scope; нет переноса approvals на новый HEAD.

R03 проверяет этот пакет и заполняет свой command map. Backend, frontend,
locks, Alembic chain и product behavior меняют соответствующие владельцы.

## Оставшаяся цепочка: задача, проверенный handoff и полная приёмка

Срез:2026-10-16 Europe/Moscow, inputa359b0b. Live integration ref совпадает; из migration PR
открыт только R03 PR49. Issues30/36/37/41/42 открыты и имеют владельцев,
соответствующих карточкам. OPEN/старое PLANNED в теле Issue не означает, что
accepted V02 не принят. Наличие у Ильи consumer47baaa9 подтверждено человеком;
отсутствие этого SHA среди branch refs не отменяет source review и не доказывает
полную готовность I02. Проверяется только доступный R03 intake.

В таблицах **handoff** означает конкретный проверяемый артефакт: команда/renderer
либо непосредственно читаемый immutable build input, с exact SHA, digest/inventory,
областью независимого review и реальными positive/negative results. Для команд и
services дополнительно нужны locks/env/start/health/stop/cleanup. Название команды, JSON schema,
synthetic fixture, отчёт с общим count и source compatibility review не заменяют
такой артефакт. Handoff не принимает всю задачу и не разрешает её ранний merge.

### Текущий конкретный блокер I02: H-BUILD-INPUTS от V04

Зафиксировано по прямому уточнению пользователя2026-10-16:
**verified release build-input handoff от V04 не получен/не проверен в R03**.
Владелец передачи — Владимир/V04; потребитель — Илья/I02.
Это запись о недостающем конкретном входе, без заявления, что остальные gates
I02 уже пройдены.

R02 допускает прямое потребление validated DTO сборщиком ([content-v1, строка6][DIRECTDTO])
и определяет файловый build artifact index.json + pages/<id>.json отдельно от
active endpoint ([public-build contract, строки4–8][BUILDINPUT]).
Поэтому **полный активированный release не является предварительным условием
SSG build I02**. Immutable input должен быть полным и проверенным; его не нужно
предварительно активировать. Последовательность R02 сначала staging HTML/assets,
затем DB_COMMITTED/ACTIVATING/ACTIVATED ([publication sequence][STAGING]).

| Фаза | Владелец / необходимый вход | Что проверяется и сохраняется | Текущий статус |
| --- | --- | --- | --- |
|1. Build inputs | Владимир/V04 → Илья/I02, review exact handoff | Immutable root/archive: index.json по PublicBuildIndex, все referenced pages/<id>.json по ContentDelivery и все referenced assets; producer/source SHA, release_id, inventory/digests, actual bytes/schema/completeness/trust/path/private-export checks. | **BLOCKED: H-BUILD-INPUTS не передан verified**. Active descriptor/active index/полная activation не нужны. |
|2. SSG HTML build | Илья/I02, проверенный вход фазы1 | Прямое чтение одного закреплённого immutable index/pages/assets; все public HTML/body/head/SEO/no-JS, catalogue/aliases/redirects/404/sitemap/robots/assets, private exclusion. Отдельные toolchain/argv/exit/input/output digests и build QA. | **PENDING: verified inputs и принятый build evidence**. Полная activation не является входом. |
|3. Activation/publication | Владимир/V04; I02/I03 renderer, V05 gateway где применимо; готовый output фазы2 | DB/journal/pending/fence/PG-CAS, active index/public URLs/catalogue/sitemap/cache, publish/unpublish freshness и failures/recovery/cleanup. Отдельный runtime receipt. | **Отдельный pending gate**; build PASS не даёт publication PASS. |

Checklist verified input handoff:

- [ ] Exact producer/source SHA и immutable root либо архив с inventory и
  воспроизводимым чтением/восстановлением; consumer source SHA фиксируется отдельно.
- [ ] Полные index/pages/assets и release identity; hashes/размеры переданных
  bytes независимо сверены с reviewed handoff pins, без автоматического принятия
  пересчитанных candidate pins. Companion inventory допустим; frozen DTO/schema
  не получают выдуманное обязательное поле.
- [ ] Index/ContentDelivery schemas, IDs/aliases/catalogue/redirect/system URL
  completeness, source/render/asset identity, trust/private export и bounded paths
  проверены. Runtime serving inputs и build source bytes не смешиваются.
- [ ] Missing referenced page/asset, invalid DTO/hash, изменение bytes,
  mixed release/root и path escape дают failure до сборки.
- [ ] Положительная проверка: при отсутствии active descriptor/index проверенный
  immutable input всё равно пригоден для SSG build. Изменение active pointer
  во время build не переключает закреплённые input bytes.
- [ ] HTML generation и staging QA имеют собственный receipt; invalid input/render
  failure не запускает publication. Последующий activation failure сохраняется
  своим failure/recovery evidence и не переименовывается в build failure.
- [ ] Проверки actual activated public serving выполняются в фазе3. До неё нет
  publication approval или фиктивного ACTIVE/COMPLETE.

Проверенный immutable build artifact может быть достаточным входом I02 без
установки executable V04 source renderer в процесс SSG. Отдельные обязательные
R03 source/quality/golden renderer/CLI/bootstrap/publication проверки сохраняются
у своих владельцев; они не переносятся в prerequisites этого build.
Полная V04/I03 приёмка и их поздние task-level зависимости также не меняются.

### Где требуется полная приёмка задачи

| Потребитель / gate | Требование полной приёмки | Основание и граница |
| --- | --- | --- |
| R03 | R02 HARD/CONTRACT; V02 и I02 INTEGRATION. R02/V02 выполнены, полный I02 остаётся pending. | [Карточка R03, строки420–426][R03]. Подтверждение renderer interface позволяет готовить wiring; для завершения R03 требуется accepted I02 с human approvals и фактическим integration receipt. |
| Проверки R03, использующие CLI/renderer/LessonHost | Отдельного task-level требования «полностью принять V04/I03 прежде R03» в карточке нет. Нужен проверенный реальный handoff и PASS соответствующих assertions. | Вывод из [карточки R03][R03] вместе с обязательными semantic equivalents [§9][S9], content contract [§8][S8] и [R02 parity guide][R02PARITY]. Это интерпретация уровня check, а не явно заданная ТЗ новая форма partial Task Approval. Отсутствующий renderer/bootstrap/activation/lifecycle всё равно блокирует свою проверку. |
| V04 | HARD V02; INTEGRATION **I03**. Для полного V04 результата scoped renderer contract не заменяет приёмку I03. | [Карточка V04][V04]: строки992–998, scope1014–1020 и acceptance1028. Проверенный CLI от V04 для R03 и полная приёмка V04 — разные gates. |
| R04 | HARD R03; INTEGRATION **V03/V04/V05/I03/I04/I05**. | [Карточка R04][R04]. Именно здесь полные V04 и I03 становятся названными task-level входами независимого audit. |
| V05 | HARD V01; INTEGRATION **V03/V04/I03/I04**. | [Карточка V05][V05]. CLI/renderer smoke не заменяет staging/restore/performance/операционную приёмку V05. |
| I05 | HARD **I03/I04**, INTEGRATION V05. | [Карточка I05][I05]. Здесь обязательны полная browser/visual matrix и проверка lesson follow-ups; R03 E2E smoke не принимает I05. |

«Достаточно handoff» не означает «можно исключить тесты до появления владельца».
Если для обязательного check нужен весь publisher или все script families,
именно этот работающий функциональный объём должен быть передан и проверен.
Если владелец не передаёт independently reviewed артефакт до полного завершения
своей задачи, фактическая дата R03 будет ждать её deliverable. Это ограничение
готовности/очереди; оно не добавляет новый HARD в карточку R03.
Изменение task scope/формальных dependencies требует отдельного решения, здесь
они сохранены без изменения.

### Каталог конкретных недостающих передач

IDs ниже совпадают с external_handoffs машинного checklist.

| ID | Задача и владелец | Необходимый deliverable и критерий review |
| --- | --- | --- |
| H-I02 | I02 #41, Илья; approvals Руслан UX/integration + Владимир API/security | Полный current public/staff-read page/SSG результат, published manifest и real browser/API evidence; exact approved head, оба reviews, merge SHA/parent/tree. Source review8256cbf/47baaa9 этого не закрывает. [I02][I02], [R03][R03]. |
| H-CLI | V04 #37, Владимир; root review Руслан | Все7 target CLI из таблицы ниже: точные Python paths/options/env/exit semantics, права/side effects и bounded cleanup;263 sources; проверенные dry-run/rollback/negative cases. Нужен исполняемый CLI handoff, не whole V04 approval. [§8][S8], [§9][S9], [V04][V04]. |
| H-RENDER | V04, Владимир; consumer Илья | Deterministic Django-independent source/component renderer,263 inventory и source/render/runtime hashes, golden HTML/math/SVG,97 CSS/7 local JS references, closed trusted export и corruption/missing-input failures. Source preservation и legacy comparison уже есть, target renderer из них не следует. [V04 scope1][V04], [CONTENT-01/03][R02MATRIX]. |
| H-BUILD-INPUTS | V04, Владимир → I02, Илья | Текущий конкретный блокер: verified immutable index/pages/assets root/archive, exact source/release/inventory/digests, schema/completeness/trust/path/bytes review и consumer intake. Activation и active endpoint не prerequisites. [Build artifact][BUILDINPUT], [direct DTO][DIRECTDTO]. |
| H-I02-RENDER | I02, Илья; backend context Владимир | SSG HTML builder напрямую читает H-BUILD-INPUTS из одного immutable root, фиксирует input/output identity/digests и полный raw body/head/SEO/no-JS/private exclusion. Отдельно serving/browser lifecycle и последующая activation; полная I02 приёмка остаётся обязательной. [I02][I02], [build artifact][BUILDINPUT], [staging][STAGING]. |
| H-I03 | I03 #42, Илья; review Руслан/Владимир по зонам | LessonHost interface, весь263/97/7+shared inventory, для каждой script family mount/dispose либо tested full-document navigation; remount/back-forward/resize/CSS/listener cleanup, trusted math/SVG и applicable golden fixtures360/768/1440. Проверенный handoff закрывает свою часть checks; full I03 receipt нужен для V04/R04/V05/I05. [§8][S8], [I03][I03]. |
| H-PUBLISH | V04, Владимир; renderer consumers I02/I03 | Реальный bootstrap twice и publish/unpublish stage/journal/activation/recovery: frozen plan, pending/fence/PG-CAS, conflicts/multi-connection, pre/postcommit/render/activation/ack/cache failure, active/db/pending probes и scoped cleanup. V02 read-only observer и R02 model не являются writer/runtime evidence. [§8][S8], [V04][V04], [PUB-01/PROTOCOL-P1][R02MATRIX]. |
| H-V03 | V03 #36, Владимир; root/runtime review Руслан | Для соответствующих current system/backend assertions:7 identity operations, sessions/CSRF/Host-Origin/hash/rate/receipt/replay/staff-write target PG tests, exact locks/cases и безопасный test-session setup. Full V03 не добавляется как R03 task gate; runtime-заявления нельзя закрыть только V02 read tests или pure R02A. Реальная login-сессия нужна и browser flow, если он заявлен. [§7][S7], [§9][S9], [§17][S17], [V03][V03]. |
| H-ORIGIN | I02/V02 — Илья/Владимир; V05 provider при необходимости; composition Руслан | Один owned origin с реальными API/public HTML/immutable release paths; точные startup/readiness/health/stop/ports/roots, cache/fail-closed probes и cleanup. Совместный I02/V02 CI runtime может закрыть smoke без whole V05; claims о конкретном gateway/cache/active pointer требуют его настоящего verified artifact. [§4][S4], [§8][S8], [§9][S9], [V05][V05]. |
| H-ENV | R03 Руслан; backend env contracts Владимир; frontend Илья | Exact Python3.12+/Node/npm/browser/locks и per-check target/test/legacy renderer env composition. Повторно использовать уже проверенные отдельные env; normal target без Django/DRF, legacy comparators отдельно, PG16 без skips, startup/teardown receipts. Нового «отсутствующего owner lock» автоматически не требовать: сначала review известных locks и состава команд. [§6][S6], [§9][S9], [R03][R03]. |
| H-R03-APPROVAL | R03 #30; независимо Владимир и Илья | После final exact-SHA full applicable target/pure/Harness/PG/browser evidence: оба Independent Task Approvals, закрытые blockers и input/command review. Upstream handoff/Task Approval V02 не переносится на R03. [R03][R03]. |

### Все14 ещё не закрытых строк общего dispatcher

В specialized CI уже есть PASS, но это не означает, что общий
MATHSTART_CHECK_RESULT/command map заполнен. Для строк с готовой реализацией
не требуется заново ставить owner задачу; остаётся R03 composition/review.

| Check | Кто передаёт / кто связывает | Что конкретно ещё нужно | Handoff / требование |
| --- | --- | --- | --- |
| system | Владимир V02/V03; Руслан adapter | Generic startup/routes/security CLI+receipt. V02 runtime принят; полные8 current routes и identity assertions требуют реального V03 provider, planned29 не объявляются working. | H-V03/H-ENV; [§9][S9], [HTTP-01/02/03][R02MATRIX]. |
| migrations | Принятый V01 Владимир; Руслан adapter | Metadata drift + one head + reviewed SQL/PG equivalence invocation и общий receipt; не новая schema implementation. | H-ENV; [§6][S6], [V01][V01]. |
| lesson-sources | V04 Владимир; Руслан wrapper | Target check_lesson_sources,263 source/render/runtime inventory и tamper/missing/conflict/nonwrite proof. | H-CLI/H-RENDER; [§9][S9], [CONTENT-01/03/CLI-01][R02MATRIX]. |
| content-quality | V04 Владимир; I03 Илья; Руслан composition | Target quality CLI + golden component renderer; проверяемые HTML/math/SVG/asset и applicable lesson/lifecycle rules, явные visual follow-ups. | H-CLI/H-RENDER/H-I03; [§8][S8], [CONTENT-01/03/UI-02][R02MATRIX]. |
| site-integrity | V02/V04 Владимир; I02 Илья | Полный active build/URL/media/catalogue/redirect/SEO/private exclusion и real publication coherence; scoped lifecycle of gateway where used. | H-CLI/H-I02-RENDER/H-PUBLISH/H-ORIGIN; [CONTENT-01/02/PUB-01][R02MATRIX]. |
| backend-tests | Владимир V01/V02/V03/V04; Руслан observer |118/50 PG V02 и34/23 PG V01 уже доказаны. Нужны общий receipt/env mapping и реальные current identity/staff-write/publication cases для остальных Django-equivalent assertions. | H-V03/H-PUBLISH/H-ENV; [§9][S9], [STAFF-01/TX-01/PROTOCOL-P1/P2][R02MATRIX]. |
| fresh-install | V01/V04 Владимир; I02 Илья; Руслан | Alembic zero уже есть; target bootstrap×2/no evidence overwrite + actual source/media/render/public build/activation smoke и scoped failure cleanup ещё нет. Schema-only fresh×2 не заменяет его. | H-CLI/H-RENDER/H-PUBLISH/H-I02-RENDER/H-ENV; [§6][S6], [§9][S9]. |
| upgrade-A | Принятый V01 Владимир; Руслан | Profile A PASS существует; подключить контролируемый legacy preparation/accepted runner к root migration_smoke и receipt, сохранить backfill/data/defaults/IDs. | H-ENV; [§6][S6], [SCHEMA-01/02][R02MATRIX]. |
| upgrade-B | Принятый V01 Владимир; Руслан | Profile B PASS существует; exact main source/equivalence/cleanup к root wrapper и receipt. | H-ENV; [§6][S6], [SCHEMA-01/02][R02MATRIX]. |
| upgrade-C | Принятый V01 Владимир; Руслан | Profile C PASS существует; UUID/roles/receipts/pending preservation и root receipt. Это не доказательство реального V03/V06 session/receipt cutover. | H-ENV; [§6][S6], [§17][S17]. |
| frontend-typecheck | I02 Илья; Руслан CI | I01 generation/pins/typecheck PASS; прогон на accepted I02 routes/renderer/types и новом combined SHA. | H-I02/H-ENV; [I02][I02], [§9][S9]. |
| frontend-tests | I02/I03 Илья; Руслан observer | Вместо только112 foundation/5 dispatcher: terminating page/SSG/staff-read и applicable script-family/lifecycle cases, no mock-only real API claim. | H-I02/H-I02-RENDER/H-I03/H-ENV; [I02][I02], [I03][I03]. |
| frontend-build | I02 Илья; V04 build inputs Владимир | Production foundation PASS; получить verified immutable inputs, затем полный HTML/SEO/no-JS build с input/output/asset/release digests и private guards. Active release и установка executable V04 source renderer не prerequisites этой сборки; R03 renderer-quality obligations отдельно сохранены. | H-BUILD-INPUTS/H-I02/H-I02-RENDER/H-ENV; [BUILDINPUT][BUILDINPUT], [DIRECTDTO][DIRECTDTO], [I02][I02]. |
| frontend-e2e | I02/I03 Илья; runtime Владимир; composition Руслан | test:e2e отсутствует наa359b0b. Нужны locked terminating browser/API/public/staff-read smoke, реальный startup/health/stop; applicable LessonHost regressions и реальные session provider если тест требует login. | H-I02/H-I02-RENDER/H-I03/H-ORIGIN/H-ENV; [§9][S9], [I02][I02]. |

Компиляция/статический source audit не требуют выполнения всей LessonHost
browser matrix. Но проверку script execution/lifecycle нельзя назвать PASS
по одному widget, описанию будущего adapter или только compile/build.
Full I04 account/forms и I05 browser matrix не добавлены к R03 card; их отдельные
gates ниже остаются обязательными для финальной миграции.

### Общие проверки вне14 строк

| Gate | Владелец | Что остаётся |
| --- | --- | --- |
|10 backend/4 frontend reviewed map | Руслан; review Владимир/Илья | Конкретные script/args/receipts, output/side effects и timeouts; operational map пока PENDING/empty. |
| Versions/locks/no-Django/DB diagnostics | Руслан + owner env handoff | H-ENV/H-ORIGIN; exact target interpreters, owned PG16, bad-port bounded nonzero, отсутствие SQLite fallback, cleanup. Проверенные специализированные env не равны общей композиции. |
| Pure/Harness и registry | Руслан |6 groups уже PASS; сохранить IDs/nonrecursive routing/fail/timeout/CLI и rerun на final changed composition. Новая внешняя runtime/domain задача для pure R03/R03A не нужна. |
| Provenance/§17 | Руслан | Exact approved input, workflow/event/head/checkout/tree и raw digests; frozen/history/old results сохраняются, target overlay отдельно. |
| CI + final R03 review | Руслан; approvals Владимир/Илья | Full applicable combined target/fresh/A/B/C/content/frontend/browser/pure/Harness evidence, task/integration/main linkage, blockers closed и оба approvals. Текущий global target FAILURE/NOT_RUN не скрывать. [§9][S9], [R03][R03]. |

### Вся очередь внешних поступлений и поздние gates

| Ветка цепочки | Тип и смысл | Что можно планировать отдельно |
| --- | --- | --- |
| accepted V02 + accepted I01 → I02 → R03 | I02 — формальный INTEGRATION R03; V02/I01 уже приняты. | Дата renderer/SSG interface review отдельно от полного I02 approval+integration. |
| V04 verified immutable build inputs → I02 HTML build → поздняя activation/publication | Артефактный порядок, не ожидание full V04/activated release до I02. | Раздельные readiness dates/receipts: input validation, build output, actual publication. [R02][BUILDINPUT], [staging][STAGING]. |
| I02 → I03 → V04 | I03 HARD I02; V04 HARD V02 и INTEGRATION I03. | Scoped LessonHost/renderer handoff для R03 может иметь собственный проверенный SHA; full I03 receipt всё равно нужен, чтобы принять V04. |
| V03 → V04 в очереди Владимира | Порядок личной очереди, **не новый HARD V03→V04**. V03 также provider current identity checks. | Подготовка по контрактам может идти параллельно. Раннюю implementation/передачу вне порядка нельзя молча предположить; согласовать это в следующем capacity плане. |
| I03 → I04 в очереди Ильи; V03+V02 → I04 по карточке | Личная очередь и INTEGRATION; I04 HARD I01, **не новый HARD I03**. | I04 account/staff forms и browser runtime остаются поздним продуктовым scope, не условием существующего V02 approval. |
| V03+V04+I03+I04 → V05 → I05 | V05 INTEGRATION все4; I05 HARD I03/I04 + INTEGRATION V05. | Полные staging/restore/performance, затем browser/accessibility/visual/F01–F04 proofs. CI runtime smoke не закрывает эти задачи. |
| R03 → R04, а V03/V04/V05/I03/I04/I05 → R04 acceptance | HARD R03; перечисленные полные INTEGRATION результаты. | Начало audit после R03 и дата его полной приёмки — разные milestones. |
| R04+V05 → V06; I05+V06 → I06 | [V06 HARD V05/R04][V06]; [I06 HARD I05 + INTEGRATION V06][I06]. | Финальная upgrade/cutover репетиция и frontend freeze не сводятся к ранним V01/renderer checks. |
| R04 → R05 integration; R04+R05+V06+I06 → R06 | [R05 HARD R01/R02][R05] уже выполнены; [R06 требует все4 accepted HARD][R06]. | Полнота нового основного ТЗ, final SHA/CI/main/Issue closure — отдельные поздние решения. |

Все формальные рёбра взяты без изменения из
[accepted dependency-policy][DAG] и карточек; их копия, типы и личные очереди
есть в машинном checklist. Нового цикла «R03 ждёт R04, а R04 ждёт R03» не вводится:
V03/I03/V04 не имеют HARD R03. Функциональные handoffs могут фактически задержать
R03 до готовности частей I03/V04, даже если full Task Approval этих задач ему
формально не нужен.

### Coverage, которую нельзя незаметно потерять

- Current identity/session/receipt/staff-write runtime: V03, при UI — I04,
  operational rates/gateway — V05, final cutover — V06. Нужные старому backend
  check assertions требуют actual target evidence;7 endpoints не становятся
  реализованными от наличия37 planned OAS operations. [§7][S7], [§17][S17].
- Source/render/publication: CONTENT-01/02/03, PUB-01, CLI-01,
  PROTOCOL-P1 и REVIEW-B02/B06. Разделены static source validation, deterministic
  renderer, active/public manifest и real journal/activation/recovery.
- **R01 visual F01–F04**: исправления owner Илья/I03, обязательная browser
  verification Илья/I05, independent task review по карточкам. Это **другие**
  findings, чем принятые V02 audit asset F01/F02. Сохранённая source exception
  не является waiver финальной React версии; optional independent Владимир F04
  review не выдумывается. [R02 parity guide][R02PARITY].
- Full account UI UI-01/REVIEW-N01, I04 grades/UI, I05 cross-browser matrix
  и V06 actual bridge/cutover остаются своими поздними gates. Ни foundation
  gallery, ни early R03 smoke не являются их приёмкой.
- ADAPT-02/04 и pure R03/R03A требуют неизменных oracle/trace/адаптерных ссылок,
  а не новых Knowledge/Assessment/Progress runtime domains. [§17][S17].
- В coverage_boundary_ledger машинного checklist перечислены **все40 R02 rows**;
  это распределение источников proof, а не автоматическое PASS этих строк.

### Что нужно для следующего пересчёта сроков трёх очередей

Даты07–13.10 остаются историческим календарём; этот increment сроки не меняет.
[§11][S11] требует новый прогноз при неготовности CI/review; [§11.1][S11Q]
сохраняет личные очереди и включает человеческое review/integration в deadline.

Для каждого H-BUILD-INPUTS/H-I02/H-CLI/H-RENDER/H-I03/H-PUBLISH/H-V03 нужны отдельно:
дата exact-SHA executable handoff, время независимого review/исправлений,
дата полного Task Approval и дата integration. Дополнительно нужны доступность
Руслана/Владимира/Ильи, длительности CI/retry и slot для обоих R03 approvers.
Ранний scoped artifact и complete task нельзя ставить одной датой по умолчанию.
Текущий build path: verified V04 inputs → I02 HTML generation/QA; activation
планируется после готового HTML, не до передачи inputs или начала SSG build.

Кандидаты на фактическую цепочку R03: accepted I02 + готовность CLI/renderer/
bootstrap/publication/lesson artifacts + review общей10/4 композиции →
full exact-input target pipeline → independent R03 approvals. После этого
R04/V05/I05/V06/I06/R05/R06 имеют свои перечисленные выше gates.
Без длительностей и owner capacity это карта зависимостей, а не рассчитанный
критический путь или принятый новый срок. Другие задачи здесь не запускаются.

## Конкретные interface gaps на текущем input

1. V02 startup/routes/runtime locks/tests приняты наa359b0b;118/50 PG и отдельный
   runtime без Django/DRF проверены. Не хватает review общего system/backend-tests
   CLI/receipt adapter, а не повторной приёмки или новой реализации V02.
2. Принятый `backend/requirements-test.lock` V01 включает Django/DRF для baseline
   fixtures. Он остаётся неизменным в отдельном schema/legacy rehearsal env.
   Специализированные изолированные env уже проверены. Остался review общей
   target/test/legacy composition; нельзя установить legacy-containing test lock
   в normal target env и назвать его no-Django runtime.
3. Принятый V01 runner `docs/acceptance/MS7-MIG-V01/run-target-ci-v5.py` находится
   вне backend, использует `MATHSTART_V01_*` и stdout summary, а не общий
   `MATHSTART_CHECK_RESULT`. Его нельзя вставить как backend script в существующий
   dispatcher. R03 accepted-input observer уже проверен34/23 PG наa359b0b;
   исторический helper сохранён. Остался review generic composition/receipt
   bridge с теми же source/env/inventory guards, а не повторный перенос V01.
4. I01 уже имеет typecheck/test/build, но нет `test:e2e`. Илья передаёт его
   реализацию с I02 и real V02 API startup/health/cleanup mapping; root не заменяет
   browser/API flow fixture-галереей.
5. Семь target V04 CLI entry points, publication/SSG journal/recovery mapping и
   owner env translation ещё не переданы. Root command map остаётся пустым.

Эти gaps требуют named deliverables/review, а не расширения реализации V01.

## Backend checks: команды R03 и критерии review

Все перечисленные root entry points уже существуют. Внутренние backend
`script`/`args` ещё **NOT_PROVIDED**; их нельзя угадать или заменить Django.
Для первых6 строк вызов: `python scripts/target_check.py <check_id>` из root.

| check_id / исходный check | Владелец handoff | Обязательные assertions и negatives |
| --- | --- | --- |
| `system` / Django check | V02, Владимир | Реальный FastAPI startup/config, зарегистрированные routes, transport/status/method policy и security settings; invalid config/Host/Origin и planned route не дают fake200. Регистрируются только реализованные операции, не все37 planned OAS operations. |
| `migrations` / makemigrations check | Владимир, принятый V01 schema mapping | Metadata/Alembic drift, ровно один head, reviewed SQL и реальный PG16 schema/default/FK/index/sequence/timestamp equivalence; malformed baseline/multiple heads/drift дают nonzero. Autogenerate без equivalence не закрывает строку. |
| `lesson-sources` / check_lesson_sources | V04 CLI, Владимир; V02 delivery consumer | Все263 sources и runtime/source identity/publication/render digests; authored bytes отдельно от rendered bytes. Изменённый digest, missing source/asset и collision дают nonzero; assertions≥263. |
| `content-quality` / check_content_quality | V04, Владимир; I02/I03 renderer consumers | Сохранённые HTML/SVG/math/asset rules, полный опубликованный scope; golden renderer/metadata parity. Broken HTML/SVG/math/media выявляются; baseline F01–F04 остаются отдельными owner obligations по R02, не blanket waiver. |
| `site-integrity` / check_site_integrity | V02+V04, Владимир; I02, Илья | Полный published URL/public build index, catalogue/media/redirect/SSG coverage; SEO body/head в raw HTML. Unknown/unpublished404, redirect после404 без override working route; missing asset/digest/mixed release fail; private/account/staff не попадают в публичный pre-render/cache. |
| `backend-tests` / Django tests | V02 API/read/staff suite + принятый V01; V04 content suite; применимые другие semantic owners | Непустые реальные PG API/service/schema/content/staff tests с полным case inventory и0 skips. DTO/status/content-type, query limits/cursor races/legacy signing, Grade PK≠number, permission/auth-before-lookup и safe errors. V02 отвечает за staff reads; auth/staff writes остаются V03/I04 scope. Schema-only34/23 не заменяют API/content suite. |
| `fresh-install` / fresh smoke | V01 schema + V04 bootstrap + I02 assets/build; R03 composition | `python scripts/fresh_install_smoke.py --profile target --disposable`: пустая owned PG16 DB, Alembic с нуля, bootstrap×2, стабильные identities/digests/timestamps и сохранённое synthetic user evidence, media/assets и frontend build. Второй bootstrap не overwrite evidence. Неверный vendor/nonempty/unowned DB, missing asset/render/activation failure дают nonzero и scoped cleanup. Принятый V01 schema-only fresh×2 остаётся самостоятельным evidence. |
| `upgrade-A` / profile A | Принятый V01, Владимир; R03 mapping | `python scripts/migration_smoke.py --disposable --source-profile A`: disposable copy content.0001 без users/Grade.created_at, reviewed backfill и schema/data/PK/FK/default/sequence preservation; wrong profile/stamp mismatch/partial failure fail. |
| `upgrade-B` / profile B | Принятый V01, Владимир; R03 mapping | Тот же wrapper с `--source-profile B`: актуальный Django main migration state на копии, exact inventory/equivalence и сохранение данных; drift/unknown head/non-owned target fail. |
| `upgrade-C` / profile C | Принятый V01, Владимир; R03 mapping | Тот же wrapper с `--source-profile C`: populated identity profiles/receipts/roles/synthetic pending operations сохраняются; overwrite/UUID renumber/receipt loss/default/timestamp/sequence drift fail. |

Для fresh/upgrade нужны одновременно `--disposable` и `MATHSTART_DISPOSABLE=1`.
Backend owner дополнительно проверяет ownership и точный target до SQL. Флаг
не разрешает рабочую/production БД. Сохраняются обе диагностические формы:
R03 `MATHSTART_DB_*` и документированная owner env mapping; DSN/credentials
не попадают в receipts/logs. V01 CI использует свой отдельный port55441/ack;
эти значения нельзя автоматически перенести в общий target job на5432.

## Receipt contract и review evidence

R03 wrapper создаёт новый `var/target-checks/<check_id>-<uuid>/result.json` и
передаёт абсолютный путь через `MATHSTART_CHECK_RESULT`. Backend обязан записать
receipt только после реальных assertions; exit0 без receipt не принимается.

Обязательные поля, уже проверяемые `scripts/target_check.py`:

| Поле | Условие |
| --- | --- |
| `check_id` | Точный ключ вызванной проверки |
| `status` | `PASS`; failure остаётся nonzero, не превращается в PASS receipt |
| `evidence_class` | `TARGET_RUNTIME`; MODEL_SYNTHETIC не подходит |
| `assertions` | integer>0, bool не допускается; для lesson-sources≥263 |
| `skipped` | integer0; bool не допускается |
| `database_vendor`, `postgresql_major` | `postgresql`, integer≥16 для migrations/backend-tests/fresh-install/upgrade-A/B/C |

В review bundle отдельно обязательны actual checkout SHA/tree, определение
case inventory и source/contract/lock digests, argv/cwd/env names, start/end/
exit/deadline, реальные versions, case IDs/results и hashed raw evidence.
Для SSG дополнительно DB/content/public-manifest/asset/release digests.
Для DB — before/after sanitized manifests и cleanup receipts. Связь минимального
receipt с этими данными должна быть однозначной. Companion receipt допустим;
immutable owner reports и historical captures не редактируются.

R03 receipt review:

- [ ] Отсутствие/битый JSON, wrong check_id/class, нулевые assertions, skips,
  bool counters, SQLite/wrong PG major и stale checkout отклоняются.
- [ ] Case inventory сопоставлен с R02 assertions/negative cases, а не только
  с суммарным количеством tests. Каждый count проверяется по raw observations.
- [ ] Exit1/timeout/missing tool/empty suite не становятся READY; timeout540s
  wrapper/600s outer остаётся bounded. Startup/teardown укладываются в deadline.
- [ ] Команда — Python файл внутри backend с точным args array; нет arbitrary
  shell, path escape или подстановки mutable branch вместо reviewed SHA.
- [ ] Normal target fresh/runtime не импортирует Django/DRF. Допустимый legacy
  preparation upgrade выполняется отдельно на disposable copy и явно маркируется.
- [ ] PG/service/ports/runtime roots изолированы; каждый fixture очищен;
  source/historical hashes до/после совпадают вне accepted owner changes.
- [ ] Нет реальных secrets/PII/private validation fixtures в logs/exports,
  нет live Product LLM; public manifests не включают private data.

## I02 frontend/SSG/browser handoff

| Root check | Конкретная owner команда в frontend | Review criterion / текущее состояние |
| --- | --- | --- |
| `frontend-typecheck` | `npm run typecheck` | Скрипт уже принят в I01; generation/pins и TS/router checks должны пройти на новом combined SHA. Владелец Илья. |
| `frontend-tests` | `npm run test` | Уже `vitest run`; nonempty deterministic suite,0 fail/skip, реальные I02 page/SSG/staff-read tests добавлены владельцем. Fixture112 PASS остаётся foundation evidence. |
| `frontend-build` | `npm run build` | Уже router build + security guard. I02 передаёт полный published manifest, raw HTML body/title/meta/canonical/OG/lang, sitemap/robots/redirect mapping, asset/release digest и private-data exclusion. |
| `frontend-e2e` | `npm run test:e2e` | **MISSING_SCRIPT** на текущем input. I02 передаёт настоящий terminating browser/API flow suite, locked browser version, start/health/stop, loopback base URLs/ports, case inventory и sanitized DOM/network/console/screenshots. |

До тестов — `npm ci`, exact Node24.21.0/npm11.19.0; browser install из locked
Playwright package, без latest fallback. Backend/frontend service startup и
cleanup передаются владельцами; R03 не угадывает будущий API launch command.
Проверяются все URL manifest HTTP/no-JS/SEO assertions, catalogue/search/current
links, redirect precedence, unknown/unpublished routes и staff denied/allowed
server authorization. Fixture gallery и synthetic API mocks не закрывают этот
real delivery gate. Private staff/account content не pre-render персональными данными.

I01 fixture-mark overlap принят как ограничение. Оба follow-ups из approval
сохранены; checklist не объявляет исправление плашки/P3 query validation.
Pure/Harness/model suites остаются отдельными evidence classes.

## V04 content CLI handoff: семь baseline commands

Владимир передаёт точные target entry points, options/exit semantics и scoped
side effects для каждой строки. Илья подтверждает SSG/browser consumption;
Руслан проверяет root composition. CLI не заменяет весь staff/admin UI.

| Исходная команда | Что обязательно сохранить и проверить |
| --- | --- |
| `publish_lessons --slug/--all [--root] [--dry-run]` | Source identity/immutable catalogue, digest conflict preflight + lock/recheck; dry-run semantics и no success при collision/renderer failure; публикация/снятие немедленно согласованы с активной SSG edition. |
| `bootstrap_site [--root] [--dry-run]` | Catalogue/structural/redirect/media/source completeness, twice stable и no user evidence overwrite. Legacy dry-run делает SQL в rollback; это не read-only audit. |
| `update_public_pages [--dry-run]` | Scoped public changes/retirement redirects, backup/media/conflict semantics и сохранение retired rows; rollback/recovery без user-data replacement. |
| `index_lessons [--root]` | Полный index; запись только в явно owned disposable output, не accepted curriculum tree во время CI verification. |
| `check_lesson_sources --slug/--all [--root]` | Все263 и source/render/runtime digest policy, без DB mutation; соответствует root lesson-sources receipt. |
| `check_content_quality` | Неослабленные HTML/SVG/math/assets assertions, isolated reports, no DB mutation; соответствует content-quality receipt. |
| `check_site_integrity` | Routes/catalogue/redirect/media/asset/SSG consistency и blocking findings, isolated reports; соответствует site-integrity receipt. |

Отдельные V04 negatives: concurrent source/lock conflicts, stale preflight,
missing media/hash mismatch, precommit render failure, postcommit activation/
ack/cache failure, interrupted stage resume и конкурирующие recovery claims.
Передаются durable pending slot/fencing/active-CAS observations, stage journal
и cleanup boundaries по PROTOCOL-P1/PUB-01. I02 доказывает consumer manifest
и public edition coherence; LessonHost-specific behavior остаётся I03 scope.

## Порядок review, intake и полного target запуска

1. V02 уже ACCEPTED_INTEGRATION. Получить human-accepted I02 exact-SHA и необходимые
   executable V04 CLI contracts/evidence. V04 не является новым HARD R03:
   это предусмотренный semantic owner content checks; отсутствие CLI блокирует
   соответствующие проверки. Другие R02 semantic owners сохраняют свои зоны.
2. Проверить PR/review/merge receipts и case/source/lock pins. Зафиксировать
   source approved heads, каждый merge SHA и совместный integration SHA/tree
   отдельно. Если inputs конфликтуют, вернуть named blocker владельцу; не менять
   его domain implementation в R03 и не принимать его результат самостоятельно.
3. Выполнить root command review по всем10 backend и4 frontend строкам;
   подтвердить coverage/negative evidence, side effects/deadlines/cleanup.
   Заполнить реальные script/args в runtime-commands.json. `REVIEWED` означает
   проверенный command contract; это не Independent Task Approval R03.
4. Создать новую versioned intake запись для новых accepted inputs. Сохранить
   8d958/0c03197 и прежние runs. Текущий guard намеренно закреплён наa359b0b;
   его обновление допускает только exact reviewed owner diffs, без blanket
   whitelist backend/frontend и без ослабления frozen/history/event guards.
5. На чистом combined checkout записать HEAD/tree, workflow event SHA, PR head/
   base/merge parents, versions/locks, service ownership и исходные hashes.
   Locked Python/Node env без Django/DRF, owned disposable PG16, no live LLM.
6. Выполнить sequence ниже и сохранить raw evidence на success/failure. Нельзя
   скрыть failure через skip/continue-on-error или partial group selection.
7. После successful полного target/применимого CI подготовить final-head
   review для Владимира/Ильи. До обоих Independent Task Approvals R03 остаётся
   INCOMPLETE. Final legacy-to-target default cutover выполняется в зоне R03
   после reviewed inputs; frozen historical baseline не переписывается.

Полная последовательность существующих R03 entry points, из repository root:

```text
python scripts/ci_provenance.py --output var/ci/provenance.json
python scripts/version_report.py --profile target
python scripts/check_database.py --profile target
# При MATHSTART_DB_PORT=1 ожидается nonzero bounded failure, без SQLite fallback.
python scripts/fresh_install_smoke.py --profile target --disposable
python scripts/migration_smoke.py --disposable --source-profile A
python scripts/migration_smoke.py --disposable --source-profile B
python scripts/migration_smoke.py --disposable --source-profile C
python scripts/verify_repo.py --profile target
python scripts/verify_repo.py --profile pure
```

Preflight: reviewed10-command map, backend/test/tooling/frontend locks,
Playwright/browser/services available и documented owned env mapping. Полный
target registry содержит16 проверок; fresh/upgrade sequence идёт отдельно.
Прежние Harness IDs `repo-baseline`, `harness-unit`, `harness-cli-smoke` и
nonrecursive lifecycle сохраняются; fake READY, timeout и missing inputs fail.
R03 §17 index охватывает R01/R03/MS6-R04/MS6-V01/R02A/R03A с исходными IDs и links.
Issues34/40 остаются OPEN до final main integration; merge/Issue closure в этом
handoff не выполняются.

Историческая документационная сверка на46ac5f1: [source snapshot](dependency-chain-20261016.json)
и [validation report](dependency-chain-validation-20261016.json). Проверены14
checks,10 handoffs,40 parity rows,18 canonical nodes и отдельные resource edges,
source line links и неизменность95 ранее сохранённых artifact files.
Runtime suites/CI вручную не запускались; operational map остаётся PENDING.
Карта требует owner review, не выдаёт approval и не меняет дедлайны.
Текущее уточнение build inputs: [verification](build-input-validation-20261016.json)
проверяет11 handoffs и раздельные input/build/activation phases; прежний report
с10 handoffs сохранён как evidence версии46ac5f1.

[S3]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L56
[S6]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L80
[S7]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L90
[S8]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L100
[S9]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L112
[S11]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L170
[S11Q]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L190
[R03]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L420
[R04]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L501
[V01]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L768
[V03]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L910
[V04]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L992
[V05]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L1074
[I02]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L1320
[I03]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L1401
[I04]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L1482
[I05]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L1563
[S17]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L1705
[S18]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L1741
[R02PARITY]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/r02-v1/parity-v1.md
[R02MATRIX]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/r02-v1/parity-matrix-v1.json
[DAG]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/r02-v1/dependency-policy-v1.json
[BUILD]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/r02-v1/public-build-contract-v1.json
[BUILDINPUT]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/r02-v1/public-build-contract-v1.json#L4
[DIRECTDTO]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/r02-v1/content-v1.md#L6
[STAGING]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/r02-v1/content-v1.md#L73
[S4]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L58
[R05]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L582
[R06]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L664
[V06]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L1155
[I06]: https://github.com/Tramsey00/MathStart-Python/blob/a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6/specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md#L1644
