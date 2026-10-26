# Окружения проверки V01 и legacy

Общая точка входа backend теперь использует target-окружение, установленное из
`backend/tests/v04/requirements.lock` (без Django), а также отдельное
окружение `MATHSTART_LEGACY_PYTHON`, установленное по историческому корневому lock-файлу.
Для legacy-окружения также нужны закреплённые зависимости oracle паролей, указанные
в `.github/workflows/migration-ci.yml`. Приведённые ниже исторические общие окружения
остаются свидетельствами, но не являются обычным target runtime.

Для принадлежащего локальному запуску временного сервиса PostgreSQL16 на127.0.0.1:55441 задайте
`MATHSTART_DATABASE_URL`, `MATHSTART_DISPOSABLE=1` и путь к отдельному legacy
интерпретатору, затем выполните команды из корня репозитория:

```text
python scripts/target_check.py backend-tests
python scripts/target_check.py fresh-install --disposable
python scripts/target_check.py upgrade-A --disposable
python scripts/target_check.py upgrade-B --disposable
python scripts/target_check.py upgrade-C --disposable
```

Точки входа создают и удаляют новые помеченные UUID databases и реальные React
артефакты. Наборы проверок никогда не подключаются к существующим данным приложения.
Fresh запускается дважды, сохраняет контент/пользователей при повторном bootstrap, проверяет полный
release из 279 страниц/263 уроков/29 медиафайлов и действительно собирает frontend. Команды
upgrade запускают target schema CLI на заполненных исторических fixtures и
проверяют данные, историю миграций, grade epoch, constraints/head и sequences.
Result receipts сохраняются в `var/target-checks/<check>-<uuid>/result.json`; ошибки,
пустые наборы проверок или пропущенные тесты не могут дать PASS. Для дочернего backend установлен предел1800s,
а родительский процесс репозитория резервирует1860s, включая очистку. Полный bootstrap
добавляет813 фактических public probes к имеющимся проверкам backend/legacy/build; измеренная
длительность только на Windows превысила прежний запас timeout backend.
Все assertions и требования об отсутствии пропусков сохраняются. Для дочернего процесса полного браузерного набора из девяти проектов установлен предел7200s,
для родителя/очистки —7500s; обычные команды сохраняют более короткие пределы. Эти команды не устанавливают окончательную приёмку миграции.

Управляемая точка входа владеет общей target database, одной фактической сборкой главного frontend
target ASGI и отдельным legacy comparator. Она выполняет все15 команд реестра
ровно один раз (перенося frontend-build перед его потребителями runtime), затем
fresh-install и все три upgrade. Наборы backend/install сохраняют собственные
дочерние databases. Нужны те же закреплённые зависимости target/legacy/Node и
установленные Playwright Chrome, Edge и Firefox; отсутствие браузеров означает сбой.

```text
python scripts/verify_target.py --runtime-root var/target-candidate-<unique> --legacy-python <separate legacy interpreter>
```

A new runtime-root under this checkout's ignored var/ is mandatory. The supplied
PostgreSQL parent служит только точкой подключения; команда создаёт и удаляет
новую помеченную database. Сервисы отказываются использовать занятый port и очищают принадлежащие им
деревья процессов. Ненулевой код/timeout/пустой или пропущенный результат дочерней команды означает сбой. Логи
и снимки исходников находятся в runtime-root; приватные fixture cookies и DSNs нельзя
загружать. `--group content` (или другая явно заданная группа) и `--allow-dirty`
дают ограниченные свидетельства разработки, но не полный target PASS. Переносимый
`verify_repo.py --profile target` также оставлен для уже управляемого
runtime; сам по себе он не запускает и не собирает общий runtime.

Набор backend также включает настоящий release schema CLI, отклонение подписанного maintenance
plan и drift, сохранение заполненных A/B/C и transactional DDL rollback.
Явная команда оператора — `python -m backend.release_migrate`; запуск API
её не вызывает. Границы ревью/maintenance описаны в `deploy/RELEASE.md`.

Набор backend включает побайтовое сравнение с legacy INDEX, чистые предварительные проверки bootstrap
сохранение выведенных из эксплуатации строк/приватных фактов, регистрацию source с предложенными ID,
настоящий fenced bootstrap/publication/HTTP и инвалидацию output-pin по версии строки.
Исторические CI receipts относятся только к зафиксированной в них копии; для нового текущего кода
нужны собственные затронутые проверки и итоговая общая проверка candidate.

Исторические combined/Django discovery инструкции находятся только в Git
`1a015f7513933901e8bb252e94c660e4383b6b0e:backend/TESTING.md`. В текущем checkout
нет manage.py, backend.load_tests или backend/requirements-test.lock. Не пытайтесь
восстановить их в target. Golden fixtures/password/timestamp comparisons используют
отдельный pinned oracle по docs/legacy-oracle.md.

Наборы target PostgreSQL также запускаются в обычном окружении без Django.
Задайте `MATHSTART_LEGACY_PYTHON` как путь к отдельно установленному legacy-интерпретатору;
перенос исторических fixtures и сравнение timestamp запускаются только в том дочернем
окружении. POSIX-пути вызова virtualenv сохраняются без разрешения
символических ссылок. При отсутствии инструментов oracle проверки завершаются ошибкой, а не пропускаются.

```text
python -m pip install --no-deps -r backend/requirements.lock
python -m pip check
python -m unittest backend.tests.test_postgres backend.tests.test_remediation -v
python -m backend.tests.runtime_verification
```

Проверочная репетиция runtime CLI по умолчанию использует текущий target-интерпретатор;
`MATHSTART_TARGET_PYTHON` позволяет явно выбрать другой установленный target-only
интерпретатор. Отсутствие Django проверяется до и после каждой команды.
Ранее заданное фиксированное расположение Windows venv больше не требуется. Для каждого запуска задавайте новый
`MATHSTART_V01_EVIDENCE_DIR` чтобы сохранить receipts и ошибки.

В явный набор target входят Fresh дважды, upgrades A/B/C, B01, точное сравнение CHECK, F1/F2/F3, constraints,
sequences и rollback. По умолчанию
новая диагностическая JSON-информация F1/F2 записывается в игнорируемый `var/ms7-mig-v01-evidence`.
Задайте `MATHSTART_V01_EVIDENCE_DIR` как новый каталог запуска, чтобы сохранить новые результаты
не перезаписывая зафиксированные исторические записи о приёмке.

Обычный target использует backend/tests/v04/requirements.lock; Django не входит
в него. Наличие tests/reference не равно runtime acceptance. Текущий реестр после
вывода development Harness —15 checks; portable pure —5 suites. Полный managed
run и prerequisites принадлежащих запуску ресурсов описаны в docs/target-runtime.md.
