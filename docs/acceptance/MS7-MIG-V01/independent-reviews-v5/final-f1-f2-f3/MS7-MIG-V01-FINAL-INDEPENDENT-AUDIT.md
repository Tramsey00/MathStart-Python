# MS7-MIG-V01 FINAL INDEPENDENT AUDIT

Дата: 2026-10-09. Независимый READ-ONLY re-review после F1/F2/F3. Рекомендация: **READY для подготовки commit/push/PR**. F1, F2, F3 — **FIXED**. Новых P1/P2/P3 findings не обнаружено. Это результат проверки реализации и локальных доказательств; human Task Approval и фактический Linux/GitHub CI остаются отдельными delivery gates.

## 1. Reviewed branch / HEAD / actual file scope

Worktree: `C:\Projects\MathStart-Python-V01`; branch `ms7-mig-v01-schema`; HEAD и accepted integration input `8d958aeeb17da46839722441425ccbb5889e2ab7`. Immutable MIG_BASE_SHA `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.

Tracked diff и staged diff пусты. Проверены все **71 untracked файл, 599578 bytes**: 34 backend-файла, 35 acceptance/evidence-файлов, один active plan и один trace. Полный список — приложение A. AST/JSON разобраны, manifest-v3 hashes сверены. Прочитаны scope/ownership/ADR/spec/plan/trace, реальные Django models/migrations, новая metadata, Alembic и проверки. Frozen R02 digests совпадают; исходный baseline snapshot идентичен принятому R02 mapping. Код HTTP/API/фронтенда/доменов за пределами V01 не изменён.

Проверки исполнены из внешней копии: `C:\Users\vladimir\AppData\Local\Temp\ms7-v01-final-audit-3khxnwy5`. Использована общая Git object database для чтения frozen input; source checkout не менялся. Повторная SHA-256 проверка всех 1451 исходных файлов показала 0 изменений. Итоговая машинная запись: [final-state-proof.json](final-state-proof.json).

## 2. F1 — FIXED

[baseline.py](C:/Projects/MathStart-Python-V01/backend/models/baseline.py:161) теперь применяет mapper before_insert/before_update semantics. При обычном INSERT явно переданные старые значения auto_now_add/auto_now заменяются текущим UTC временем, как Django pre_save. Полный save обновляет auto_now даже для неизменённого существующего объекта; auto_now_add существующей записи сохраняется.

[repositories.py](C:/Projects/MathStart-Python-V01/backend/infrastructure/repositories.py:27) различает полный save и restricted save(fields). Исключённый auto_now сохраняется, включённый обновляется. no_autoflush предотвращает промежуточный общий flush при restricted save. Core update/bulk_update не вызывают pre_save, что соответствует Django QuerySet.update/bulk поведению. [import_historical](C:/Projects/MathStart-Python-V01/backend/infrastructure/repositories.py:56) — явный отдельный Core insertion с обязательными PK и всеми историческими auto timestamps; пропуск timestamps отклоняется до вставки. У обычного add/save нет общего флага обхода; импорт не подмешан в обычный путь. Произвольный вызывающий Python/SQL код, сознательно выбирающий import_historical, остаётся доверенным кодом. Production HTTP adapter в V01 не реализован.

Независимо повторён реальный Django/SQLAlchemy differential на disposable PostgreSQL по всем семи полям: Grade.created_at; ContentPage.created_at/updated_at; LessonPublication.published_at; MediaAsset.created_at; StudentProfile.created_at; IdentityReceipt.created_at. Проверены create с явно старым временем, full/restricted save, Core/bulk, historical import, отрицательный missing-timestamps и autoflush=True. Timezone-aware значения и точность PostgreSQL timestamps проверены; все семь historical timestamps сохранены точно. Исходные Grade/Content времена при migration не перезаписываются. Результаты повторного запуска во внешней копии: [f1-timestamp-parity-v3.json](docs/acceptance/MS7-MIG-V01/f1-timestamp-parity-v3.json). Original developer evidence в source не переписано.

## 3. F2 — FIXED

[collector.py](C:/Projects/MathStart-Python-V01/backend/infrastructure/collector.py:67) строит общий plan: CASCADE deletion, PROTECT, SET_NULL mutation targets, затем замыкание FK parent references для всех блокируемых строк. Это покрывает прежнюю inversion, включая deferred FK: нельзя сначала удержать Page, а затем запросить более ранний Grade/Subject/Section.

Все строки блокируются через общий TABLE_ORDER и стабильные ключи. [locks.py](C:/Projects/MathStart-Python-V01/backend/infrastructure/locks.py:41) возвращает действительно захваченные IDs из FOR UPDATE; отсутствующие строки не объявляются заблокированными. Нет skip_locked. После захвата [collector.py](C:/Projects/MathStart-Python-V01/backend/infrastructure/collector.py:115) повторно вычисляет plan и проверяет deletion/SET_NULL sets и включение всех необходимых current locks в реально acquired locks. Новый parent/dependency требует DeletionPlanChanged и outer rollback/restart. Новое PROTECT запрещает deletion. Мутации выполняются после proof, по PK, в общей транзакции.

Retry policy остаётся на внешнем уровне; скрытых retries/deadlock suppression нет. Воспроизведения изменившегося SET_NULL, нового PROTECT, нового parent, исчезнувшего/reused parent PK и failure после SET_NULL прошли; частичные изменения откатываются. Универсальная свобода от deadlock при произвольном будущем raw SQL не утверждается.

## 4. F3 — FIXED

[schema.py](C:/Projects/MathStart-Python-V01/backend/migrations/schema.py:15) проверяет точный линейный graph `v01_0001 -> v01_0002`, единственный head и запрещает неизвестную/ambiguous graph. [assert_tracking](C:/Projects/MathStart-Python-V01/backend/migrations/schema.py:28) требует единственную column version_num VARCHAR(32) NOT NULL без default; корректные PK/index alembic_version_pkc; отсутствие extra columns/constraints/index/identity. Для target обязателен ровно один row `v01_0002`. Для unmanaged legacy допустимы отсутствие tracking table либо её каноническая пустая форма, а не повреждённая форма.

CLI check и upgrade используют общий schema proof, включая drift при известном head. Upgrade проверяет до stamp и повторно после table locks. Fresh требует пустую isolated DB и проверяет итог. Прямой стандартный Alembic entry point закрыт [env.py](C:/Projects/MathStart-Python-V01/backend/migrations/env.py:7); независимо исполненный `python -m alembic -c backend/alembic.ini stamp v01_0002` завершился exit 1 до DB connection с ожидаемым guard rejection. Offline обход запрещён. Internal configuration атрибут является guard доверенного adapter, не границей безопасности против произвольного Python/SQL. Capture utility отказывает при существующем reviewed snapshot до доступа к DB. Никакого automatic repair tracking table нет.

## 5. B01/CHECK regression

B01 остаётся исправленным: BIGINT только у трёх согласованных M2M surrogate PK; соседние FK остаются INTEGER. Проверены реальные generated INSERT RETURNING IDs выше int32, включая пределы sequence, во fresh и A/B/C, а не только декларации metadata. B01 owner approval сохранён.

CHECK normalization остаётся ограниченной согласованными PostgreSQL отображениями. Truth-table cases (42), точное canonical comparison и negative drift проходят. Подмена настоящего CHECK на CHECK(true) отклоняется; canonicalization не превращена в произвольное игнорирование CHECK.

## 6. Schema and Alembic completeness

Физическая PostgreSQL schema сравнена с frozen reference: 20 baseline + 7 additive protocol tables, плюс строго проверенная alembic_version. SQLAlchemy metadata/Alembic chain согласованы. Columns/types/nullability/defaults, PK/FK/UNIQUE/CHECK, indexes, identity/sequences проверяются catalog proof. Protocol model, две revisions, compatibility-v1.json и оба dependency locks не переписаны относительно предыдущего аудита.

Protocol DDL остаётся PROPOSED_V01_DDL_REVIEW_PENDING; успешные тесты не заменяют human DDL acceptance. Django runnable application и frozen contracts сохранены.

## 7. Fresh twice / upgrade A/B/C

Независимо выполнены target runtime CLI fresh дважды в разных новых DB и upgrades A/B/C с последующим check: **10/10, все exit 0**. Django отсутствует в target runtime environment и не импортируется target command. Fresh выполняется только на пустой disposable DB. A/B/C используют собственные schema-valid fixture profiles и reviewed gate; отрицательные unknown schema/head/no-review пути проверены. [runtime-verification-v3.json](docs/acceptance/MS7-MIG-V01/runtime-verification-v3.json) во внешней копии содержит результаты этого повторного запуска.

## 8. IDs/FKs/data/hashes/Grade epoch

Подтверждено сохранение baseline IDs, FK relationships, data digest, password hashes, is_staff/is_superuser/roles и timestamps при upgrade. Backfill Grade epoch детерминирован, идемпотентен и не перезаписывает исторические данные. Sequences продвигаются относительно существующих IDs; empty и uncalled semantics проверены.

Failure injections до завершения migration сохраняют schema/data/history; disconnect после setval до COMMIT откатывает данные и позволяет безопасный retry. Неподтверждённый ACK после уже состоявшегося COMMIT остаётся отдельной неисполненной веткой. PostgreSQL connection failure не переключает adapter на SQLite. R02 migration regression — 63/63 PASS.

## 9. Lock/concurrency evidence

Помимо suite независимо написан и исполнен [final_independent_probes.py](final_independent_probes.py), результаты [independent-f2-two-orders.json](independent-f2-two-orders.json). В двух отдельных DB воспроизведены schema-valid crossed Grade/Subject/Section/Page SET_NULL relationships. Barrier синхронизирует конкурентов перед первым общим FOR UPDATE; принудительно выбраны оба порядка: сначала Grade 1 и сначала Grade 2.

| Порядок | Outcomes | SQLSTATE | Проверка данных |
| --- | --- | --- | --- |
| Grade 1 первым | COMMIT / COMMIT | отсутствуют, в частности нет 40P01 | SET_NULL верен, Grade/Subject/Section удалены, 2 publications сохранены |
| Grade 2 первым | COMMIT / COMMIT | отсутствуют, в частности нет 40P01 | те же assertions |

В обоих прогонах дополнительное соединение изменяет Page title; update сохранён. Все recorded lock tokens монотонны. Это проверяет успешную атомарность и отсутствие lost update в данном interleaving. Полнота общего порядка оценена по коду, включая FK reference closure, реальный acquired set и revalidation. После revalidation новые FK references сериализуются locks/constraints на parents; изменённый необходимый lock set до mutations приводит к conflict. Contention при больших closure и все возможные timings не измерены; проверка не заявляет исчерпывающего доказательства любых конкурентных операций.

## 10. Alembic corruption negatives

Все 14 PostgreSQL негативных случаев независимо повторены в target suite. Для каждого actual CLI check возвращает exit 1, upgrade отказывает; tracking rows/schema/data остаются неизменными. В fixtures специально допускаются разные corruption patterns, чтобы proof проверял catalog и revision content отдельно.

| Группа | Случаи | Результат |
| --- | --- | --- |
| Malformed empty legacy tracking (7) | missing_PK, nullable, extra_column, wrong_type, wrong_length, missing_column, default | отказ до stamp, без repair |
| Target tracking/schema (7) | unknown, multiple, empty, base_only, schema_with_valid_head, missing_table, extra_index | fail closed, ненулевой CLI exit |

Дополнительно graph ambiguity отрицательный control и canonical-empty legacy, normal fresh/upgrade положительные controls проходят. Конкретные tests: [test_remediation.py](C:/Projects/MathStart-Python-V01/backend/tests/test_remediation.py:334), :355 и :377.

## 11. Test suite results and 23 skips coverage

Использованы существующие configured interpreters: Python 3.12.10; Django 5.2.16 (test environment); SQLAlchemy 2.0.46; Alembic 1.18.4; psycopg 3.3.6. Actual PostgreSQL 16.15, Docker client/server 29.8.0, Compose 5.5.1. Обе среды `pip check` exit 0. Fresh installation dependency locks не повторялась.

Команды исполнялись во внешней копии, с PYTHONDONTWRITEBYTECODE=1 и явно заданным isolated PostgreSQL URL. Admin credential синтетический и использовался только внутри нового container. В отчёт URL с паролем не включён.

| Команда / группа | Фактический результат | Exit |
| --- | --- | --- |
| python -m unittest backend.tests.test_unit backend.tests.test_postgres backend.tests.test_remediation -v | 34 PASS, 0 SKIP, 0 FAIL/ERROR; 68.710s | 0 |
| python -m backend.tests.runtime_verification | 10/10 CLI checks | 0 |
| python -m backend.tests.baseline_verification | 6/6 setup/check subprocesses | 0 |
| nested python scripts/verify_repo.py | 8/8 checks | 0 |
| nested Django suite | 141 collected; 118 PASS, 23 SKIP; 177.839s | 0 |
| nested R03 contract | 18 PASS | 0 |
| nested Harness | 73 PASS | 0 |
| nested R02 migrations | 63 PASS | 0 |
| python -m unittest tests.test_r02a_contract tests.test_r03a_contract -v | 71 PASS = 30 R02A + 41 R03A | 0 |
| git diff --check; CI patch apply --check --ignore-space-change | PASS; patch не применён | 0 |
| Independent two-order F2 probe | 2/2 scenarios, assertions PASS | 0 |
| Direct Alembic stamp negative control | ожидаемый refusal до подключения | 1 (ожидаемый) |

Baseline запускается без target-admin URL и потому пропускает 23 backend PostgreSQL tests. Независимо извлечён DiscoverRunner suite и каждому skip сопоставлен тот же exact test ID, реально исполненный в отдельном 34-test target run с reserved admin URL. Таким образом, это не арифметическое сопоставление 23 с 23. Полный mapping — [baseline-skips-coverage.json](baseline-skips-coverage.json) и приложение B. 11 других target tests — unit, без skip. Test functions проверены на meaningful assertions, rollback/catalog/state/real CLI behavior; одних зелёных counters для вердикта не использовано.

Raw baseline logs: [verification log directory](var/ms7-mig-v01-baseline-354dca1ccf9e4eb68a5cb4ff27579739). Runtime/baseline/F1/F2 JSON в этой внешней копии получены повторным исполнением, а source evidence сохранены.

## 12. Evidence/ownership/security

Original F1/F2/F3 report, probes и failed results сохранены в independent-audit-v3; три файла byte-identical внешним original audit artifacts и SHA-256 совпадают. Исправления связаны с original evidence, включая исходный 40P01; исторические failed attempts не переименованы в успехи. Русланово B01 approval, frozen R02 и принятый source SHA сохранены. Manifests/deltas/plan/trace описывают текущую remediation, ownership Владимира и R03 handoff.

Архивы исходных байтов находятся в ignored `var/ms7-mig-v01-remediation-input` и `var/ms7-mig-v01-resume-input`; git check-ignore подтверждён. Все 53 prior-input file hashes сохранены. Эти каталоги не входят в 71 commit candidate. В candidate нет .env/real credentials, dumps, backup archives, runtime venv, временных test DB или иных incidental generated outputs. JSON snapshots/evidence, CI patch и намеренно сохранённые три original-audit artifacts имеют task purpose. Secret-signature и file-type/size review не выявили утечки; это проверка содержимого, а не внешняя attestation отсутствия любых возможных секретов.

Все DB writes выполнялись только в новом контейнере `ms7-v01-final-independent-20261009`, ID `952c8236fec2421faa2899ccb8bfa19cc331c1d504dbf42693fd61020e27a84b`, label mathstart.audit=final-v01, loopback port 55441, tmpfs data. Использовались UUID test DB с disposable marker. Production/shared DB не использовались. После suite собственные DB удалены; перед cleanup осталось 0 test DB. Затем удалён только этот контейнер. Четыре ранее существовавших остановленных контейнера не затронуты. Source file bytes, Git index и HEAD сохранены. Commit/push/merge/reset/clean/review не выполнялись.

## 13. CI handoff readiness

R03 v3 handoff patch использует текущую 34-test команду со всеми тремя test modules; устанавливает backend lock вместе с root dependencies; PostgreSQL service/ports и scoped disposable URL согласованы с Windows verification. Patch applicability независимо PASS, применения к owned CI файлам не было. CI/root-owned files остались неизменны. Handoff **готов к review владельцем R03**; Linux/GitHub execution не выполнялся и не объявлен PASS.

## 14. NOT VERIFIED

Не выполнены Linux/GitHub CI, чистая переустановка lock environments, production cutover/действительная deployed source inventory, внешняя live проверка исторических GitHub approvals, MS6-V02 environment и будущие V02–V04 lifecycle flows. Не воспроизведены потерянный ACK после COMMIT и исчерпывающие concurrency timings/масштабирование lock closure. Эти границы не скрываются за локальными PASS. Human Task Approval для proposed additive DDL и PR delivery остаются pending; отсутствие PR/approval не является дефектом реализации в данном pre-commit аудите.

## 15. New findings P1/P2/P3

**Нет новых actionable findings.** F1/F2/F3 закрыты воспроизводимыми проверками и независимым code review. Никакие failed/missing execution gates не объявлены пройденными. Для локально проверенной V01 scope blocking implementation defects не обнаружены.

## 16. Recommendation READY / NOT READY for commit/push/PR

**READY** для подготовки commit/push/PR текущих 71 файлов на reviewed HEAD. Это разрешение к следующему delivery review, а не заявление о принятии pending DDL или production migration. Перед merge остаются требуемые human approval и CI владельца. READ-ONLY аудит завершён без изменения исходников, evidence или Git state.

## Приложение A — все 71 commit candidate файла

- `backend/__init__.py` — 84 bytes
- `backend/alembic.ini` — 237 bytes
- `backend/infrastructure/__init__.py` — 51 bytes
- `backend/infrastructure/collector.py` — 6318 bytes
- `backend/infrastructure/database.py` — 2285 bytes
- `backend/infrastructure/locks.py` — 3786 bytes
- `backend/infrastructure/repositories.py` — 4201 bytes
- `backend/infrastructure/uow.py` — 1443 bytes
- `backend/migrate.py` — 1980 bytes
- `backend/migrations/__init__.py` — 80 bytes
- `backend/migrations/env.py` — 1046 bytes
- `backend/migrations/protocol-schema-v1.json` — 31161 bytes
- `backend/migrations/schema.py` — 10107 bytes
- `backend/migrations/upgrade.py` — 5931 bytes
- `backend/migrations/versions/v01_0001_baseline.py` — 744 bytes
- `backend/migrations/versions/v01_0002_protocol.py` — 494 bytes
- `backend/models/__init__.py` — 108 bytes
- `backend/models/baseline-v1.json` — 208162 bytes
- `backend/models/baseline.py` — 8896 bytes
- `backend/models/compatibility-v1.json` — 859 bytes
- `backend/models/protocol.py` — 8806 bytes
- `backend/requirements-test.lock` — 553 bytes
- `backend/requirements.lock` — 245 bytes
- `backend/requirements.txt` — 125 bytes
- `backend/tests/__init__.py` — 65 bytes
- `backend/tests/baseline_verification.py` — 3111 bytes
- `backend/tests/capture_protocol_schema.py` — 2295 bytes
- `backend/tests/check_canonicalization.py` — 3759 bytes
- `backend/tests/django_timestamp_probe.py` — 3579 bytes
- `backend/tests/legacy_fixture.py` — 1071 bytes
- `backend/tests/runtime_verification.py` — 2498 bytes
- `backend/tests/test_postgres.py` — 22865 bytes
- `backend/tests/test_remediation.py` — 30895 bytes
- `backend/tests/test_unit.py` — 10323 bytes
- `docs/acceptance/MS7-MIG-V01/b01-owner-approval-v1.json` — 1396 bytes
- `docs/acceptance/MS7-MIG-V01/baseline-verification-v2.json` — 1523 bytes
- `docs/acceptance/MS7-MIG-V01/baseline-verification-v3.json` — 1523 bytes
- `docs/acceptance/MS7-MIG-V01/check-canonicalization-v1.json` — 1475 bytes
- `docs/acceptance/MS7-MIG-V01/check-canonicalization-v1.md` — 1918 bytes
- `docs/acceptance/MS7-MIG-V01/compatibility-addendum-v1.0.0.md` — 2163 bytes
- `docs/acceptance/MS7-MIG-V01/container-tooling-v3.json` — 58 bytes
- `docs/acceptance/MS7-MIG-V01/continuation-delta-v2.json` — 11649 bytes
- `docs/acceptance/MS7-MIG-V01/continuation-delta-v3.json` — 23206 bytes
- `docs/acceptance/MS7-MIG-V01/disposable-cleanup-v2.json` — 342 bytes
- `docs/acceptance/MS7-MIG-V01/disposable-cleanup-v3.json` — 342 bytes
- `docs/acceptance/MS7-MIG-V01/f1-timestamp-parity-v3.json` — 2015 bytes
- `docs/acceptance/MS7-MIG-V01/f2-concurrency-v3.json` — 1588 bytes
- `docs/acceptance/MS7-MIG-V01/file-manifest-v2.json` — 10070 bytes
- `docs/acceptance/MS7-MIG-V01/file-manifest-v3.json` — 13789 bytes
- `docs/acceptance/MS7-MIG-V01/file-manifest.json` — 5675 bytes
- `docs/acceptance/MS7-MIG-V01/finding-B01.md` — 3621 bytes
- `docs/acceptance/MS7-MIG-V01/implementation-report-v2.md` — 7457 bytes
- `docs/acceptance/MS7-MIG-V01/implementation-report-v3.md` — 10066 bytes
- `docs/acceptance/MS7-MIG-V01/implementation-report.md` — 7456 bytes
- `docs/acceptance/MS7-MIG-V01/independent-audit-v3/MS7-MIG-V01-INDEPENDENT-AUDIT-REPORT.md` — 25624 bytes
- `docs/acceptance/MS7-MIG-V01/independent-audit-v3/audit-probes-results.json` — 1549 bytes
- `docs/acceptance/MS7-MIG-V01/independent-audit-v3/audit_probes.py` — 8362 bytes
- `docs/acceptance/MS7-MIG-V01/old-to-new-evidence-v2.json` — 3404 bytes
- `docs/acceptance/MS7-MIG-V01/old-to-new-evidence-v3.json` — 3416 bytes
- `docs/acceptance/MS7-MIG-V01/old-to-new-evidence.json` — 2875 bytes
- `docs/acceptance/MS7-MIG-V01/r03-ci-handoff-v2.md` — 2418 bytes
- `docs/acceptance/MS7-MIG-V01/r03-ci-handoff-v2.patch` — 1642 bytes
- `docs/acceptance/MS7-MIG-V01/r03-ci-handoff-v3.md` — 1898 bytes
- `docs/acceptance/MS7-MIG-V01/r03-ci-handoff-v3.patch` — 1655 bytes
- `docs/acceptance/MS7-MIG-V01/runtime-verification-v2.json` — 2990 bytes
- `docs/acceptance/MS7-MIG-V01/runtime-verification-v3.json` — 2990 bytes
- `docs/acceptance/MS7-MIG-V01/verification-v2.json` — 9071 bytes
- `docs/acceptance/MS7-MIG-V01/verification-v3.json` — 16340 bytes
- `docs/acceptance/MS7-MIG-V01/verification.json` — 3817 bytes
- `docs/agent-traces/MS7-MIG-V01.md` — 15959 bytes
- `docs/exec-plans/active/MS7-MIG-V01.md` — 10073 bytes

## Приложение B — exact mapping 23 baseline skips

Для каждой строки baseline ID и separately executed target ID идентичны; target outcome PASS, baseline reason: NOT RUN: set reserved disposable PostgreSQL administration URL.

1. `backend.tests.test_postgres.PostgreSQLTests.test_additive_protocol_schema_drift_is_visible` → тот же target ID, PASS.
2. `backend.tests.test_postgres.PostgreSQLTests.test_check_canonicalization_exact_and_truth_table` → тот же target ID, PASS.
3. `backend.tests.test_postgres.PostgreSQLTests.test_constraints_jsonnull_deferred_fk_and_protect` → тот же target ID, PASS.
4. `backend.tests.test_postgres.PostgreSQLTests.test_existing_unknown_alembic_and_no_review_refused` → тот же target ID, PASS.
5. `backend.tests.test_postgres.PostgreSQLTests.test_fresh_twice_separate_databases_no_django` → тот же target ID, PASS.
6. `backend.tests.test_postgres.PostgreSQLTests.test_ordered_row_lock_is_real_and_receipts_use_stable_order` → тот же target ID, PASS.
7. `backend.tests.test_postgres.PostgreSQLTests.test_postgres_defaults_timestamps_and_collector_cascade` → тот же target ID, PASS.
8. `backend.tests.test_postgres.PostgreSQLTests.test_rollback_injection_no_ddl_data_or_history_mutation` → тот же target ID, PASS.
9. `backend.tests.test_postgres.PostgreSQLTests.test_sequence_empty_and_uncalled_semantics` → тот же target ID, PASS.
10. `backend.tests.test_postgres.PostgreSQLTests.test_unknown_head_and_schema_forbid_stamp` → тот же target ID, PASS.
11. `backend.tests.test_postgres.PostgreSQLTests.test_upgrade_profiles_preserve_data_defaults_epoch_sequences` → тот же target ID, PASS.
12. `backend.tests.test_remediation.RemediationTests.test_b01_actual_generated_join_ids_and_superuser_preservation` → тот же target ID, PASS.
13. `backend.tests.test_remediation.RemediationTests.test_f1_all_auto_timestamps_match_real_django_and_historical_import` → тот же target ID, PASS.
14. `backend.tests.test_remediation.RemediationTests.test_f2_changed_setnull_plan_conflicts_before_mutations` → тот же target ID, PASS.
15. `backend.tests.test_remediation.RemediationTests.test_f2_crossed_setnull_two_sessions_canonical_locks_no_deadlock` → тот же target ID, PASS.
16. `backend.tests.test_remediation.RemediationTests.test_f2_new_protect_dependency_rechecked_under_locks` → тот же target ID, PASS.
17. `backend.tests.test_remediation.RemediationTests.test_f2_new_referenced_parent_requires_outer_restart` → тот же target ID, PASS.
18. `backend.tests.test_remediation.RemediationTests.test_f2_reused_reference_pk_is_not_a_falsely_acquired_lock` → тот же target ID, PASS.
19. `backend.tests.test_remediation.RemediationTests.test_f2_setnull_failure_rolls_back_cascade_and_data` → тот же target ID, PASS.
20. `backend.tests.test_remediation.RemediationTests.test_f3_malformed_empty_tracking_refused_before_stamp` → тот же target ID, PASS.
21. `backend.tests.test_remediation.RemediationTests.test_f3_revision_graph_and_clean_empty_tracking_positive_controls` → тот же target ID, PASS.
22. `backend.tests.test_remediation.RemediationTests.test_f3_unknown_ambiguous_empty_and_inapplicable_target_heads_fail_closed` → тот же target ID, PASS.
23. `backend.tests.test_remediation.RemediationTests.test_sequence_disconnect_before_commit_preserves_data_and_retry` → тот же target ID, PASS.

**Blocking findings for MS7-MIG-V01: none.**
