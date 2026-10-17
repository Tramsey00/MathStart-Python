# Покрытие единой задачи

Это справочная матрица требований, не очередь отдельных поручений/approvals.
Одна цель — закончить весь перенос. Подробности — канонические карточки
`specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md`.
Actual results — existing execution ledgers, не эта исходная таблица.

| IDs | Сохранить или закончить |
| --- | --- |
| R01, R02, V01, V02, I01 | Принятый baseline/contracts/schema/read API/React foundation; сохранить и проверять регрессии |
| R03 | Реальные10 backend/4 frontend commands, target/pure/Harness CI, failure/timeout handling, no empty PASS |
| V03 |7 identity operations, hashes/sessions/CSRF/Host-Origin/rates, receipt/bridge/replay/races, весь User/Group staff-write inventory |
| V04 | Все source/quality/integrity/publish/bootstrap/index CLI, deterministic renderer, immutable inputs, staged build/journal/fence/activation/recovery |
| I02 | Все public/staff-read pages, catalogue/search, SSG/SEO/no-JS/redirect/404, exact IDs и pinned release |
| I03 | Все lesson/math/SVG/CSS/local+shared JS families, lifecycle или full navigation, visual F01–F04 |
| I04 | Real account/onboarding/staff forms, quiet state,30/150 boundaries, password cleanup, frozen pending/retry/reconciliation |
| V05 | Reproducible environments/health/proxy/storage, backup+restore, ordinary API measurements, runbooks |
| I05 | Chrome/Edge/Firefox ×360/768/1440, keyboard/focus/visual/error/recovery и all-family coverage |
| R04 | Отдельный аудит объединённого кандидата: contracts/data/security/publication/parity и zero blocking findings |
| R05 | Full v7.2/source/changelog,52 product task dispositions,§17 old-to-new evidence, current docs/verification/runbooks |
| V06 | Final fresh/upgrade A/B/C/cutover/rollback rehearsal на disposable данных, legacy writer revocation, compatible recovery |
| I06 | Final locked frontend build/SSG/assets matching backend/release, no secrets, final smoke/rollback artifact |
| R06 | One final SHA/CI/draft PR, release/evidence/docs/rollback и HUMAN_PENDING closeout |

## Реальные зависимости

Accepted R02 contracts/V01 schema/V02 reads/I01 foundation уже доступны.
V04 immutable build inputs -> I02 HTML -> I03 integration -> полная V04 activation;
не ждать active release перед HTML build. V03 -> real I04; их parts могут идти
последовательно у одного исполнителя без передачи между людьми.
Ready runtime/CLI/browser inputs -> полный R03. V03/V04/I03/I04 -> V05;
I03/I04/V05 -> I05; R03 и объединённая готовая система -> R04;
V05/R04 -> V06; I05/V06 -> I06; R04/R05/V06/I06 -> R06.
R05 source/draft можно готовить заранее, final alignment — после реализации.
R04 до final freeze, затем review release delta: не создавать цикл R04 -> R06 -> R04.

Formal dependency kinds сохранены в frozen
`specs/migration/r02-v1/dependency-policy-v1.json`. Они определяют доступность
реального входа/проверки; персональные handoffs/поштучные stop gates отменены.

## Не потерять

- Полный admin inventory R01, в том числе guarded deletion/history/User/Group
  permissions; empty working DB не повод исключить операции. Content source-managed.
- Frozen HTTP/DTO/numeric/cursor/error contracts, all required negative cases,
  PG constraints/concurrency/retention и recorded reveal semantics.
- Весь inventory263 topics/97 local CSS/7 local JS + shared, сверенный с manifest,
  не только representative demo. Сохранить runtime extras/retired pages.
- Visual F01–F04, fixture overlap Issue52, I01 query P3 и V01 helper finding по
  исходному record. Closed V02 asset F01/F02 не путать с visual findings.
- Полнота40 parity IDs/AT-M01–12, source hashes, historical approvals и §17.
  Не превращать будущие product tasks в реализованный runtime.
