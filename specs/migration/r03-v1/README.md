# Контракт verification adapter R03 v1

Статус: контракт команд REVIEWED после фактического независимого технического ревью.
Обычный обязательный CI с проверенной картой прошёл для указанных ниже candidates.
Затем пользователь принял миграцию и разрешил merge PR54 с SHA
3a290a46d991e22269a17dde41e39f0637576071; CI main также прошёл.
[Ревью и ограничения](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/migration-execution/review/final-review-20261018.md).
Историческая атрибуция владельцев: Tramsey00 / VladimirFrolov777 /13baybars.
[Issue30](https://github.com/Tramsey00/MathStart-Python/issues/30) фиксирует исходный scope;
результат завершённой миграции и текущие точки входа сопровождения указаны в
[maintenance](../../../docs/maintenance.md). Этот документ не запускает новую задачу.
Текущий принятый вход `a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6`;
предыдущий вход `0c03197e23f69a233c0fcf8bdffa336feca20b92` и его receipts сохранены в Git;
исторический вход `8d958aeeb17da46839722441425ccbb5889e2ab7` сохранён,
MIG_BASE_SHA `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
Основания: [migration v1.1](../MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md) §§9/17,
[матрица R02](../r02-v1/parity-matrix-v1.json) и принятый ADR0006.

## Профили и команды

Текущий registry после 20.10.2026: `python scripts/verify_repo.py` запускает 15
product checks, `--profile pure` — 5 переносимых наборов. Selection flags сохранены;
группа harness удалена вместе с подсистемой. Empty/failed/skipped/missing/timeout означают
fail. Product checks не зависят от development runner; ограниченная redaction перенесена
в scripts/verification_diagnostics.py. Общие регрессии registry/failure/privacy сохранены
в tests/test_migration_r03*.py. Legacy profile — только закреплённый oracle.
Исторические counts/registry IDs и receipts ниже описывают прежние SHA, а не действующие
обязательства. Полная пофайловая карта: docs/audits/docs-and-workflow-cleanup.md.

Использовать Python 3.12+, отдельный venv, `pip install --no-deps -r verification.lock`
из этой директории (либо полный путь относительно root), затем `pip check`.
Зависимости product устанавливаются из зафиксированных backend/frontend locks;
verification.lock — lock инструментов. Установка latest зависимостей запрещена.

## Обязательные семантические эквиваленты и передача владельцам

[Передача команд](runtime-commands.json) теперь указывает реальные target entry points
для всех десяти backend checks: system/routes/security, точная schema/head, все 263 lesson sources,
целостность файлов для всех 279 pages, live HTTP quality, полный набор backend suites
в изолированных базах, fresh дважды с реальными React artifacts и повторным bootstrap,
а также upgrade заполненных профилей A/B/C через реальный schema CLI с проверками сохранения
данных/history/sequence. Управляемая combined orchestration прошла на
42f6249:320 backend, 181 frontend unit, 1269 browser cases по всем 9 projects, без skip,
с fresh/upgrade profiles, recovery455 и combined gate. Независимый reviewer изучил все
10 backend и 4 frontend handoffs и одобрил их технический статус REVIEWED. Обычный обязательный
CI теперь проверяет это состояние. `IMPLEMENTED_PARTIAL` остаётся доступным промежуточным
состоянием с fail-closed для отсутствующих записей; ни один статус сам по себе не означает
человеческую приёмку задачи. Backend entry: `{ "script": "backend/<existing-script>.py", "args": ["..."] }`.
Допускаются только Python scripts, разрешающиеся внутри backend; произвольный shell запрещён.
Каждый entry создаёт непустые target receipts без skip. Public scoped CI исполняет пять read-only
checks; backend-install CI job исполняет backend/fresh/upgrades против собственной службы PostgreSQL16
на 55441. Ни одна задача не заявляет полную приёмку target. Фактические локальные проверки
entry points зафиксированы под `docs/acceptance/migration-execution/i02-verification/`
на указанном выше принятом main SHA; исторические сбои и успешные receipts восстанавливаются из Git.

| Ключ / прежнее утверждение | Обязательная target-проверка / владелец |
| --- | --- |
| system / Django check | FastAPI config/startup/зарегистрированные routes/security, V02 |
| migrations / makemigrations | Metadata/Alembic drift, одна head, проверенный SQL/эквивалентность PG, V01 |
| lesson-sources | Все 263 sources с parity publication/source digest, V04 |
| content-quality | Неослабленные проверки HTML/SVG/math/assets, V02/V04 |
| site-integrity | Полнота всех URL/media/catalog/redirect/SSG, V02/V04/I02 |
| backend-tests / Django tests | Непустые, не пропущенные реальные PG API/services/migration/content/staff tests, V01/V02/V03/V04 |
| fresh-install | Alembic с нуля, bootstrap дважды без перезаписи evidence, assets/build, V01/V04/I02 |
| upgrade-A/B/C | Точное сохранение schema/data/ID/FK/default/timestamp/sequence для трёх заданных disposable profiles, V01 |
| frontend-typecheck/tests/build/e2e | Зафиксированные `npm run typecheck/test/build/test:e2e`, I01/I02 |

Все 14 command interfaces получают `MATHSTART_CHECK_RESULT` с уникальным output
в `var/target-checks`. Для кода выхода 0 дополнительно требуется JSON receipt с
`check_id` (точный ключ), `status:PASS`, `evidence_class:TARGET_RUNTIME`, целым
`assertions>0` и `skipped:0`. Для lesson-sources требуется не менее 263 assertions.
Receipts migration/backend-tests/fresh/upgrade дополнительно требуют
`database_vendor:postgresql` и целый `postgresql_major>=16`.
Counts и receipts предотвращают успех без проверок/при skip, но всё равно нужны
независимое ревью assertions и свидетельства реальной реализации. Сами по себе они
не доказывают parity; model/synthetic результаты не могут иметь этот evidence class.
Каждая команда также получает `MATHSTART_CHECK_ID` с точным ключом интерфейса.
Frontend commands должны записывать такой же непустой структурированный результат
по фактическим наблюдениям tool/test/build; код 0 без receipt — ошибка. Assertions typecheck/build
описывают проверяемые инварианты исходника/build, но не browser acceptance. Должны существовать
frontend package, lock, каждый script и npm; отсутствующий tool — fail. Scripts должны
выполнять тесты детерминированно и завершаться ошибкой при отсутствии тестов, без watch mode.

`python scripts/fresh_install_smoke.py --profile target --disposable` и
`python scripts/migration_smoke.py --disposable --source-profile A|B|C` запускают
репетиции, проверенные владельцами, и требуют вторую явную защиту
`MATHSTART_DISPOSABLE=1`. Реализация владельца также обязана изолировать DB/runtime,
проверять пустую fresh DB и identity заполненного profile; flag не даёт права на production.
Эти wrappers запускают реализованные команды из карты со статусом REVIEWED. Репетиции fresh
и заполненных A/B/C прошли на записанных candidates с фактическими проверками schema/data.
Сам API startup по-прежнему не устанавливает schema.

`python scripts/check_database.py --profile target` использует psycopg напрямую через
MATHSTART_DB_HOST/PORT/NAME/USER/PASSWORD, read-only SELECT1/version query, ограничения
соединения/statement по 5 секунд и общий предел 15 секунд. Ошибки credentials/DSN/driver
не печатаются; fallback на SQLite отсутствует. Эти env names относятся к интерфейсу диагностики
R03, это не замена будущим backend configuration. `version_report.py --profile target`
требует backend/requirements.lock, точных версий установленного ПО и реального PG.

## Границы CI и evidence

Отдельный migration-ci запускает task pushes, integration/main PRs и pushes.
Замороженный ci.yml и его pin полного файла остаются неизменными. Pure job использует только
lock инструментов R03 с явной проверкой доступности imports без Django/DRF. Historical baseline
job запускает неизменённый standalone R02 suite63 на принятом input в собственном detached worktree;
его проверка HEAD всех входов сохраняет смысл. Наблюдения Django исторические и не доказывают
переносимость target. Текущие pure R02 protocol32 запускаются отдельно. Эквиваленты runtime
проверяются полным target registry; standalone historical suite нельзя переименовать в свидетельство
текущего runtime. Обязательные текущие tests не удаляются и не пропускаются.

Target job включает PG16, owner locks, fresh и upgrades A/B/C, полный target registry и реальные
Chrome/Edge/Firefox projects при размерах 360/768/1440. Реализации и входы доступны; map имеет
статус REVIEWED. Отсутствующие inputs всё равно fail-closed, без job-level skip/continue-on-error.
Provenance фиксирует фактические checkout SHA/tree, event, run/attempt, PR head/base и проверенные
merge parents/ref. Evidence загружается даже при ошибке. Успешные pure/historical jobs не перекрывают
провал target. `ci_provenance.py` обнаруживает stale checkout и неверных merge parents;
локальный запуск не считается CI. Live Product LLM и production credentials не требуются.

Миграция принята и слита в PR54; консолидация PR55 и закрытие migration Issues28–45
с проверкой scope завершены (см. maintenance выше). Полные target/recovery/combined checks
прошли на runtime 42f6249, затем на candidate `1d9e4d39aa103ccc049dd9569c2354893af30a75`
в [CI39164124957](https://github.com/Tramsey00/MathStart-Python/actions/runs/39164124957),
а также на cleanup `467866e7038071dce35883e1d20fa5be2d7d5fd3` в
[CI39181017096](https://github.com/Tramsey00/MathStart-Python/actions/runs/39181017096):
все 9 jobs SUCCESS, включая реальные target/image-recovery/combined; пропущенных jobs нет.
Каждый результат относится только к своему SHA. Для нового HEAD обязательны новые проверки.
[Руководство runtime](../../../docs/target-runtime.md) содержит текущие инструкции эксплуатации.
Исторические [handoff](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R03/handoff.md)
и [trace](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/agent-traces/MS7-MIG-R03.md)
сохраняют исходные ограничения.

## Исторические этапы (2026-10-12 — 2026-10-15)

Датированные далее разделы — исторические снимки, а не текущие инструкции выполнения.
Их INCOMPLETE/NOT_READY/pending описывают прежние этапы и не отменяют приведённый выше
завершённый результат. Одобрения, результаты, digests и identities проверенных inputs
не переназначаются. Старые workflows/controllers для фиксированных candidates удалены.
Сырые artifacts и удалённые tools можно восстановить по SHA исходника каждой записи в
существующем [restoration index](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/migration-execution/cleanup-20261019/restoration-index.json).

## Принятый совместный CI inputs I01/V01 — 2026-10-12

Исторические совместные прогоны ниже остаются закреплены за `0c03197`. Текущие squash acceptance
V02 и guards используют [accepted-integration-20261015.json](accepted-integration-20261015.json)
на `a359b0b`; approval `8256cbf`/review `5538854677` сохранены отдельно:
[квитанция merge и последующие шаги](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R03/v02-integration-a359b0b/README.md).
Post-merge baseline `38796031561` отдельна от suites candidate V02; consumer review `8256cbf/47baaa9`
проверял только source. R03 INCOMPLETE, полный I02 не принят.

Человеческие receipts и merges теперь подтверждают ACCEPTED_INTEGRATION для обеих задач.
Раздельные frontend и V01 PostgreSQL jobs тестируют закреплённый совместный input `0c03197`,
используя одобренные source heads только как ссылки provenance. Строгая проверка receipt/tree/
source/merge-chain/live-ref дополняет неизменённые проверки event-SHA и PR merge-parent.
Исторические runs, captures, workflow pins и предыдущий input `8d958` остаются отдельными.
Текущее принятие, сохранённые follow-ups и реальные совместные runs описаны в
[handoff](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R03/accepted-integration-ci-20261012.md).

## Подготовка передачи CLI/receipt — 2026-10-12

[Конкретный checklist владельца/review](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R03/cli-receipt-handoff-checklist.md)
сопоставляет все 10 backend checks, 4 frontend checks и 7 baseline content commands с deliverables V02/I02/V04
и assertions parity R02. Принятые свидетельства schema/foundation V01 остаются отдельными.
Новый machine checklist имеет статус PREPARED_FOR_OWNER_REVIEW. Этот исторический intake предшествовал
пяти конкретным target entries, теперь записанным выше; оставшиеся пробелы указаны явно.
Полное выполнение target ожидает принятые inputs точного SHA и проверенные command contracts;
статус R03 остаётся INCOMPLETE до полных checks и независимых approvals.

## Технические проверки опубликованного candidate V02 — 2026-10-15

Точный PR53 implementation `76d8eac` / parent `0c03197` / tree `dbad1e8` закреплён
в v02-published-candidate.json. Published run `38637910883` исполняет неизменённые подтверждённые
controls `1b75c6e` на свежем Linux commit checkout; финальный task run `38642117604` проверяет
неизменённые owner86/all40 PG cases плюс отдельно V01 34/all23 PG, 0 skips, исторические contracts,
полный Content projection 279/263 и настоящий изолированный runtime без Django/DRF.
Полные загруженные raw artifacts, отдельные workflow/control/implementation/checkout revisions
и digests находятся в [technical packet](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R03/v02-review-20261015/review-packet.md).
Человеческий Task Approval V02 ожидается; принятый input не выдуман. Неполная загрузка скрытого cache
первого task run сохранена отдельно от полного повторного запуска. Глобальный target R03 всё ещё требует
проверенной карты команд, принятых inputs V02/I02 и соответствующих V04 CLI/full combined pipeline/
independent reviews; эта общая предпосылка не является новым условием карточки V02. R03 INCOMPLETE.

## Узкий successor V02, имеющий разрешение — 2026-10-15

Новый v02-successor-intake.json остаётся NOT_READY/null для неопубликованных нового SHA/tree.
Отдельный v02_successor_gate проверяет прямого родителя `76d8eac` и неизменённую исходную
BASE lineage, проверенный владельцем точный diff/blobs/metadata/attributes и сохранённые controls40/73.
Исходные publication-v3/control/input не меняются; blanket acceptance потомков и автоматическая
замена tree/pin запрещены. Human approval `5525315946` получено только для predecessor `76d8eac`.
[Текущий handoff](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R03/v02-successor-20261015/handoff.md)
фиксирует точный renderer contract, diff владельца, актуальный case inventory и последовательность suite
на новом SHA. Guard preparation CI не является свидетельством задачи successor.

## Опубликованный successor V02 `8256cbf` — 2026-10-15

Новый проверенный scope `v02-successor-reviewed-8256cbf.json` закреплён отдельно:
SHA256 `04a47175` (5 изменённых + 63 новых files, точные metadata/patch/case IDs),
отдельно от неизменённых original candidate/anchor/control inputs. Root workflow/control
`0effadc`, run `38784183591` завершился SUCCESS: replay original v3 на `76d8eac`, цепочка/delta
successor на `8256cbf`/tree `74c3014`, V02 118/all50 PG с сохранёнными original86 и 0 skips,
отдельно V01 34/all23 PG, contracts/Content/runtime без Django. Полный чистый checkout включает
вспомогательные verifier/evidence dependencies. [Текущее ревью](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R03/v02-successor-review-8256cbf/review-packet.md)
содержит raw hashes/reconciliation и классификацию baseline/stale/global-target.
Текущий intake имеет технический PASS, ожидается новое человеческое ревью; перенос approvals,
merge и закрытие Issue не произошли. Общий R03 остаётся INCOMPLETE.
