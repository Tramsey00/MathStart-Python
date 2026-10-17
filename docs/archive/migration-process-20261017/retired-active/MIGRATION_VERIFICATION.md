# Проверки общей миграции

Проверки выполнять по стоимости и риску. Не дублировать полную матрицу после
каждой маленькой правки. Полный final target остаётся обязательным.

## Разработка

1. Один reproducer/регрессионный test изменённой границы; для проблемы запуска
   сначала interpreter/import/health. Затем ближайшие unit/integration tests.
2. При готовности связанных частей — их real PG/API/browser checks.
3. Финальный combined candidate — полный target, fresh/upgrade/restore,
   content/browser matrix и отдельный review. Поздний существенный fix требует
   recheck delta и затронутых проверок, не автоматического повторения всего.

Не повторять известный prerequisite FAIL, пока вход не изменился. Pending/skip
экономит промежуточный run, но final readiness при нём запрещена. CI guards
нельзя ослабить так, чтобы skipped target выглядел завершённым переносом.
Существующий R03 registry/14 interfaces закончить, не создавать параллельный verifier.

## Окружения и команды

Проверить actual versions и compatible locks. Target без Django/DRF; legacy
golden/comparator в отдельной среде. Все writes/fresh/upgrade/restore на owned
disposable PG/runtime, с проверкой path/DB ownership и bounded cleanup.
SQLite не доказывает PG locks/races. Credentials/PII в raw logs не писать.

Из execution root, используя его interpreter:

```text
python scripts/verify_repo.py --profile pure
python scripts/verify_repo.py --profile target --list
python scripts/verify_repo.py --profile target
python scripts/fresh_install_smoke.py --profile target --disposable
python scripts/migration_smoke.py --disposable --source-profile A
python scripts/migration_smoke.py --disposable --source-profile B
python scripts/migration_smoke.py --disposable --source-profile C
```

`--list` не запускает проверки. Default verify пока legacy; не считать его PASS
target acceptance. Финальные defaults/docs согласовать с реальной новой платформой.
Frontend: locked install при изменении lock/отсутствии среды; typecheck/unit/build
по затронутому коду. Scope `test:i02` после проверки его actual package script;
`test:e2e`/combined full matrix в финале. Preflight/start/health/stop должны быть
проверены до длительного browser run. Full cross-browser — I05/final gate;
сценарии I02/I03 проверяются раньше по своей изменённой границе.

## Полнота требований

Frozen `specs/migration/r02-v1/parity-matrix-v1.json` — источник всех40 assertions
и negatives; результат записывать в existing execution parity-ledger, не менять
frozen target_evidence. Сравнивать ID sets, а не только counts:

```text
HTTP-01 HTTP-02 HTTP-03 GRADE-01 GRADE-02 GRADE-03
AUTH-01 AUTH-02 AUTH-03 AUTH-04 PROFILE-01 SCHEMA-01 SCHEMA-02 TX-01
CONTENT-01 CONTENT-02 CONTENT-03 PUB-01 CLI-01 UI-01 UI-02 STAFF-01
ADAPT-01 ADAPT-02 ADAPT-03 ADAPT-04 F01 F02 F03 F04
REVIEW-B01 REVIEW-B02 REVIEW-B03 REVIEW-B04 REVIEW-B05 REVIEW-B06 REVIEW-B07
REVIEW-N01 PROTOCOL-P1 PROTOCOL-P2
```

Сохранить pure R02/R03/R02A/R03A/Harness oracle assertions и V01/V02 case IDs.
10 backend checks: system, migrations, lesson-sources, content-quality,
site-integrity, backend-tests, fresh-install, upgrade-A/B/C.
4 frontend checks: frontend-typecheck/tests/build/e2e. Real commands/args/env/
timeout/side effects/cleanup и nonempty receipts обязательны.

| Gate | Финальное доказательство |
| --- | --- |
| AT-M01 | source baseline/manifests/сохранённые edits |
| AT-M02 | full URLs/content/assets/SEO/redirects/404 |
| AT-M03 | no-JS HTML, math/SVG/widgets/design/lifecycle |
| AT-M04 | real identity/profile/grades/3 onboarding choices/restore |
| AT-M05 | sessions/CSRF/owner/staff/privacy/password cleanup |
| AT-M06 | concurrency/replay/rates/lost ack/receipt cutover |
| AT-M07 | fresh/upgrade A/B/C, IDs/hashes/roles/constraints/timestamps |
| AT-M08 | CLI/publish/bootstrap/locks/conflicts/activation recovery |
| AT-M09 | pure/Harness/full target CI и deliberate failures |
| AT-M10 | Chrome/Edge/Firefox ×360/768/1440,keyboard/focus/errors |
| AT-M11 | clean build/staging/restore/performance,no-Django normal runtime |
| AT-M12 | full v7.2,18 dispositions,final SHA/CI/release/rollback и human closeout |

AT-M12 technical release readiness отделить от actual main merge/Issue closure/
human decision. Последние остаются HUMAN_PENDING; MIG-G4 COMPLETE до них запрещён.
Не откладывать первичное доказательство auth/data/recovery до final rehearsal:
V06 подтверждает уже работающую систему на окончательном release.

## Ревью и записи

Основной исполнитель делает self-check. Отдельный reviewer один раз на готовом
кандидате; earlier reviewer только для конкретного существенного риска.
Ему нужны exact diff/base/head, нужный contract, existing results/open findings;
полная история переписки не нужна. Reviewer проверяет риски/пробелы и при
необходимости воспроизводит ключевой сценарий, не дублирует всю QA автоматически.
После fix — delta review. Значимый новый дизайн может потребовать нового полного review.

Raw logs и большие screenshots остаются artifacts. В summary достаточно:
requirement/test IDs, exact code SHA/tree/dirty state, command/cwd/env profile,
exit/counts/versions/input-output digests, CI actual checkout, cleanup, findings.
Не переименовывать старый run как run нового SHA. Не перезаписывать failures.
Один task/parity ledger, один execution trace и STATE; отчёт на каждый microfix
не создавать. Environment failure/missing tool/skip/empty suite не равны PASS.
