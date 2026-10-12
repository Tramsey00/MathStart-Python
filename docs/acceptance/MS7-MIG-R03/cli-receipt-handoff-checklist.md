# R03 CLI/receipt handoff checklist — 2026-10-12

Статус checklist: **PREPARED_FOR_OWNER_REVIEW**. R03: **INCOMPLETE**.
Это review checklist в зоне R03; согласованность с deliverables проверена по
принятому ТЗ и parity matrix. Подтверждение checklist владельцами и независимые
Task Approvals R03 пока не получены.

Текущий принятый integration input:
`0c03197e23f69a233c0fcf8bdffa336feca20b92`.
MIG_BASE_SHA: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
Предыдущий input `8d958aeeb17da46839722441425ccbb5889e2ab7` сохранён в provenance.
I01/V01 — ACCEPTED_INTEGRATION; их совместные successful CI receipts сохранены
в [текущем handoff](accepted-integration-ci-20261012.md).

При проверке refs и GitHub PRs 2026-10-12 принятых migration V02/I02/V04
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
| Принятые V01 schema/fresh/upgrade assertions | Владимир / VladimirFrolov777 | R03 связывает существующую реализацию с reviewable CLI/receipt; реализация V01 не расширяется |
| Registry, root wrappers, CI, intake и §17 trace | Руслан / Tramsey00 | Владимир и Илья — независимые Task Approvers R03 |

## Обязательный пакет от владельца

- [ ] Task ID, PR URL, полный40-character approved head SHA, human approval IDs,
  merge SHA/parents, accepted integration SHA и tree. Для I02 нужны обе зоны
  approval; для V02/V04 — Task Approval Руслана и применимое consumer подтверждение.
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

## Конкретные interface gaps на текущем input

1. V01 runtime lock содержит schema tooling; FastAPI startup/routes deliverable
   V02 отсутствует. Владимир передаёт reviewed runtime/test dependencies и entry
   points вместе с V02; R03 не объявляет FastAPI установленным по наличию backend/.
2. Принятый `backend/requirements-test.lock` V01 включает Django/DRF для baseline
   fixtures. Он остаётся неизменным в отдельном schema/legacy rehearsal env.
   Установка этого lock в общий target env нарушит существующий no-Django/DRF
   guard. Owner handoff должен разделить target tests и legacy preparation,
   дать точные locks/interpreters и сохранить полный PG coverage без skips.
3. Принятый V01 runner `docs/acceptance/MS7-MIG-V01/run-target-ci-v5.py` находится
   вне backend, использует `MATHSTART_V01_*` и stdout summary, а не общий
   `MATHSTART_CHECK_RESULT`. Его нельзя вставить как backend script в существующий
   dispatcher. R03 и Владимир должны review конкретный composition/receipt
   adapter к уже принятой реализации; нельзя копировать/переписывать v5 gate,
   выдумывать entry point или ослаблять path/receipt checks.
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

1. Получить human-accepted V02/I02 exact-SHA deliverables и необходимые
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
   8d958/0c03197 и прежние runs. Текущий guard намеренно закреплён на0c03197;
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
