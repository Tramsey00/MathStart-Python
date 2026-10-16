# Проверка и ревью миграции

Применяется к [задачам](MIGRATION_TASKS.md) после запуска
[главной инструкции](MIGRATION_AGENT.md). Этот файл задаёт требования,
а не утверждает, что будущие команды уже реализованы или проверки пройдены.

## 1. Окружения и честные результаты

- Использовать configured project interpreters и совместимые locks. Записывать
  фактические Python/Node/npm/PG/Docker/browser versions, cwd и env profile names.
  Версия из `pyvenv.cfg` не доказывает работающий интерпретатор.
- Target runtime и его обычные CLI/verification не устанавливают Django/DRF.
  Legacy fixture preparation/comparators допустимы в отдельном явно отмеченном
  окружении и не должны стать зависимостью обычной эксплуатации.
- Проверки writes/fresh/upgrade/restore/concurrency выполняются только с
  disposable DB/runtime/media/ports. Проверить ownership до подключения,
  запретить fallback к SQLite при ошибке PG и bounded cleanup чужих ресурсов.
- Проверять реальные negative outcomes: failed connection/test, timeout,
  missing tool/command, empty suite/receipt, skipped PG cases, unsafe path.
  Все они не дают зелёный target result.
- `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED_ENVIRONMENT`, `REVIEW_PENDING`,
  `HUMAN_PENDING` различать. Отчёт об источниках и успешная компиляция не
  заменяют runtime/browser/data evidence.
- Не устанавливать случайную новую версию для обхода lock. Ошибку среды
  исправлять в scoped disposable окружении; если это недоступно, записать
  точную причину и продолжать независимую работу без заявления final readiness.

## 2. Команды и обязательные интерфейсы R03

В существующей R03 есть отдельные профили. До применения проверить актуальный
parser/README и окружение; запуск без `--profile target` пока проверяет legacy.
Не принять default baseline PASS за target acceptance.

| Команда из root execution checkout | Назначение |
| --- | --- |
| `python scripts/verify_repo.py --profile pure` | Pure contracts/protocols/Harness без Django |
| `python scripts/verify_repo.py --profile target --list` | Проверка реального состава registry, не исполнение |
| `python scripts/verify_repo.py --profile target` | Полный target registry после готовности команд |
| `python scripts/fresh_install_smoke.py --profile target --disposable` | Alembic zero + bootstrap twice + media/build/activation |
| `python scripts/migration_smoke.py --disposable --source-profile A` | Upgrade A |
| `python scripts/migration_smoke.py --disposable --source-profile B` | Upgrade B |
| `python scripts/migration_smoke.py --disposable --source-profile C` | Upgrade C |
| `python scripts/check_database.py` | Проверенный target PG diagnostic после адаптации |
| `python scripts/version_report.py` | Реальный состав среды после адаптации |

В `frontend/`: `npm ci`, `npm run typecheck`, `npm run test`, `npm run build`,
`npm run test:e2e`. На исходном integration `test:e2e` ещё не определён;
его требуется реализовать с terminating startup/health/browser/stop lifecycle.
Наличие зависимости Playwright не считается существованием этого сценария.

В финальном R03/R05 согласовать default `python scripts/verify_repo.py` с target
платформой либо явно изменить все текущие entry points так, чтобы обязательная
проверка миграции всегда выбирала target. Сохранить воспроизводимый исторический
legacy profile отдельно, не менять его доказательства задним числом.

| Backend check ID | Обязательный исполняемый результат |
| --- | --- |
| system | Startup/routes/security, real current identity/grades/content/staff |
| migrations | Metadata drift, one Alembic head, reviewed SQL, PG equivalence |
| lesson-sources | Весь source inventory, hashes/identity/conflict/tamper cases |
| content-quality | Deterministic renderer, HTML/math/SVG/assets, golden parity |
| site-integrity | URLs/media/catalogue/redirect/SEO/private exclusion и active coherence |
| backend-tests | V01/V02 regressions + V03/V04 auth/staff/publish/concurrency |
| fresh-install | Empty PG -> schema + bootstrap twice + реальный release |
| upgrade-A | Frozen profile A -> проверенные schema/data outcomes |
| upgrade-B | Frozen profile B -> проверенные schema/data outcomes |
| upgrade-C | Frozen profile C -> UUID/roles/receipts/pending preservation |

Frontend check IDs: `frontend-typecheck`, `frontend-tests`, `frontend-build`,
`frontend-e2e`. Для каждой из 14 строк нужны существующие executable paths/args,
cwd, locks, env names, allowed writes, service lifecycle, timeout, teardown,
nonempty structured receipt и реальные positive/negative результаты.
Не сочинять команды, paths или case counts, не создавать success-only wrapper.

Общий command map должен проверять версионированный execution-процесс,
описанный в AGENT. Старые frozen contracts/approval records сохранить.
Автоматизированное review разрешает candidate dispatch по новому процессу,
но не подделывает прежние human approval fields.

## 3. Полная матрица R02

Источником assertions и negative cases остаётся
`specs/migration/r02-v1/parity-matrix-v1.json`. Создать новый execution ledger
в `docs/acceptance/migration-execution/`, не менять frozen `target_evidence`.
На исходном snapshot ровно следующие 40 ID; сравнить наборы, не только число:

```text
HTTP-01 HTTP-02 HTTP-03
GRADE-01 GRADE-02 GRADE-03
AUTH-01 AUTH-02 AUTH-03 AUTH-04
PROFILE-01 SCHEMA-01 SCHEMA-02 TX-01
CONTENT-01 CONTENT-02 CONTENT-03 PUB-01 CLI-01
UI-01 UI-02 STAFF-01
ADAPT-01 ADAPT-02 ADAPT-03 ADAPT-04
F01 F02 F03 F04
REVIEW-B01 REVIEW-B02 REVIEW-B03 REVIEW-B04
REVIEW-B05 REVIEW-B06 REVIEW-B07 REVIEW-N01
PROTOCOL-P1 PROTOCOL-P2
```

Каждая строка ledger содержит original assertion/source, implementation paths,
task/slice, test IDs, exact input/code SHA, raw result/exit, negative coverage,
review/finding links и current status. Не создавать тест, который только
повторяет implementation; expected behavior брать из принятого контракта.

Дополнительно сохранить точные наборы pure R02/R03/R02A/R03A/Harness assertions,
V01/V02 accepted case IDs и проверять изменения guards/locks отдельно.
Математические reference fixtures не превращаются в новый persisted runtime.

## 4. Финальная acceptance matrix

| ID | Техническая проверка |
| --- | --- |
| AT-M01 | Source baseline + approved delta/manifests, отсутствуют потерянные edits |
| AT-M02 | Все current public URLs/content/assets/SEO/404/redirects |
| AT-M03 | Полный lesson HTML без JS, formulas/SVG/widgets lifecycle, дизайн |
| AT-M04 | Register/login/logout/profile, три onboarding choices, Grade IDs/restore |
| AT-M05 | CSRF/rotation/expiry/owner/staff/privacy/password cleanup |
| AT-M06 | Concurrent register/replay/conflict/rates/lost ack/cutover |
| AT-M07 | Fresh и upgrades A/B/C, IDs/hashes/roles/constraints/timestamps |
| AT-M08 | Publish/bootstrap/index/check CLI, locks/conflicts/activation recovery |
| AT-M09 | Pure/Harness contracts, полный target CI, deliberate failure cases |
| AT-M10 | Chrome/Edge/Firefox, widths360/768/1440, keyboard/focus/error/retry |
| AT-M11 | Clean build/staging/restore/performance, обычный target без Django |
| AT-M12 | v7.2, все18 task dispositions, единый release/CI/rollback и final workflow |

AT-M12 разделить на `technical_release_ready` и `human_merge_closeout`.
Первая часть подтверждается source/build/docs/evidence; вторая остаётся
HUMAN_PENDING до фактических решения пользователя, merge/main CI/Issue closure.
MIG-G4 нельзя объявить COMPLETE, пока эта часть не завершена.
Это предусмотренная финальная граница, а не повод остановить implementation
раньше подготовки полного проверяемого кандидата.

## 5. Особо важные regression cases

### API, identity, staff

- Strict UTF-8/JSON: nested duplicate keys, nonfinite numbers, nonobject,
  unknown fields, size boundary, malformed query и status/envelope precedence.
- Existing eight current product API operations и delivery/staff additions
  различать от 37 canonical planned operations; не выводить готовность из counts.
- Пароли synthetic, старые hash formats/iterations, login rotation/expiry/logout,
  CSRF/Host/Origin, rates между workers, proxy spoofing, enumeration/privacy.
- Receipt bridge: lost cookies/ack, account switch, revoked/expired proof,
  cross-owner access, replay/conflict, duplicate concurrent writes и retention.
- Staff User/Group create/change/password/roles/history/guarded deletion и
  delete-selected, AND permissions where required; семь Content models view-only.
  Permission не добавлять как новый самостоятельный CRUD; исходный inventory
  всех операций сверить с real API и UI.
- Frontend password cleanup, unknown logout outcome, frozen pending request,
  GET-first restore, abort/stale response, no automatic unsafe retries.

### БД и публикация

- Все constraints/sequences/defaults/timezones/Grade epoch, FK/on_delete
  различия Django и SQL; не считать autogenerate проверенным migration SQL.
- Upgrade profiles из frozen mapping, включая populated users/groups/receipts,
  а не только пустую рабочую БД. Alembic stamp после доказанной equivalence.
- Повторный bootstrap не меняет runtime evidence/edits; working extra retired
  pages и fresh source counts сравнивать по manifest, не одной общей сумме.
- Failure до/после DB commit, HTML build, activation и response; durable pending
  gate, lease/fence/takeover, stale owner/competing recovery, SQL+file coherence.
- Immutable input -> output HTML -> activation: отдельные release identities,
  digests, corruption/missing/path-escape/private-data tests. V02 read-only
  observer не является реализацией publisher writer.
- Restore и rollback после synthetic target writes: compatibility и
  reconciliation доказаны; destructive snapshot restore не обещается как
  универсальный безопасный rollback.

### Контент, браузер и assets

- Полный published manifest, HOME alias/canonical, sitemap catalogue_full,
  pinned_release и отсутствие reread другого active release внутри render.
- Полные raw body/head/SEO/no-JS и реальная навигация. Private responses не
  попадают в SSG/cache/assets. Lossless numeric IDs проверяются по всему
  допустимому schema диапазону без изменения публичного представления.
- Каждая local/shared script family, order dependencies, StrictMode double mount,
  back-forward, resize, timers/RAF/observers/listeners/CSS cleanup.
- Сопоставимые baseline/target captures, обычный масштаб, widths360/768/1440;
  математическое поведение, SVG labels, axes/arrows, focus и keyboard.
- Closed historical asset findings не открывать заново без новой регрессии.
  Открытые visual F01–F04 и I01 follow-ups закрыть доказательствами.

## 6. Протокол отдельного ревью

1. Исполнитель передаёт task/slice, base/head/tree, diff, contracts, tests,
   raw evidence, limitations и known findings. Отчёт без доступного diff
   или без exact version не является достаточным review input.
2. Reviewer читает первичные файлы/negative cases, проверяет ownership и
   independently воспроизводит ключевые сценарии в своей disposable среде.
   Отдельно отмечает проверки, которые видел только в CI.
3. Finding: ID, priority, path/line, наблюдаемая проблема, reproduction,
   нарушенный контракт, ожидаемый regression test, status и проверенный fix SHA.
4. Исполнитель исправляет; reviewer проверяет новый diff. Старые результаты
   остаются историей. Если фикс затрагивает соседнюю область, повторить её проверки.
5. Перед release reviewer проверяет объединённый candidate и completeness ledger,
   включая собственные прежние замечания; self-check автора не заменяет этот шаг.

Ревью не должно превращаться в бесконечную перепись отчётов по уже принятому
участку. Повторять проверки при изменениях, новых failures или конкретном
неразрешённом сомнении. При ready input выполнять runtime работу, а не только
редактировать список будущих проверок.

## 7. Evidence и критерии готовности

Сохранять raw output и machine-readable summary под уникальным run ID;
не перезаписывать предыдущие failures/captures. Receipt включает:

```text
task_id / slice_id / requirement_ids / run_id
source_input_sha / implementation_sha / tree_sha / dirty_paths
workflow_ref / event_sha / actual_checkout_sha / tested_merge_ref (если CI)
command_argv / cwd / environment_profile / actual_versions
exit_code / collected / passed / failed / skipped / case_ids
input_manifest_digest / release_id / output_artifact_digests
start_end_time / stdout_stderr_paths / cleanup_result
review_context / reviewed_sha / findings / limitations
```

Секреты/DSN/cookies/passwords/PII в logs, screenshots, dumps и Git не сохранять.
Фиксировать env names, а не secret values. Snapshot verification не равно
production execution; equal tree не превращает candidate run в run на squash SHA.

Техническая готовность требует одновременно:

- Все13 новых execution task rows TECHNICALLY_VERIFIED; пять baseline rows сохранены.
- Все40 parity rows и AT-M01–AT-M11 PASS с применимыми negatives; AT-M12 technical PASS.
- Полный combined target/fresh/upgrade/content/browser/pure/Harness CI выполнен
  на final candidate; skips обязательного сценария, отсутствующие tools и
  environment failures не скрыты.
- Отдельный final agent review и zero unresolved blocking findings.
- v7.2, source/change/disposition matrix52, current docs, runbooks и rollback
  соответствуют сборке; основной продукт не расширен.
- Чётко перечислены HUMAN_PENDING действия. Нельзя одновременно писать
  «полностью принято» и оставлять required tests/final gate незавершёнными.
