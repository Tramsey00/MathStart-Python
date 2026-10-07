# R01: итог fresh PostgreSQL smoke и parity

Source SHA: `8c11edadc8debc81432d1db1145feac504f09061`.
DB: `ms6_v01_smoke_ilya_r01_20261007_8c11edad`, role `ms7_r01_ilya`,
host endpoint `127.0.0.1:55447`. Отдельные container/volume/runtime.
Запуск разрешён пользователем после preflight. Working DB `mathstart:5432`
не использовалась для migrations/bootstrap/publication.

## Выполненная команда

`SOURCE_AT_8c11edad/.venv/Scripts/python.exe -B scripts/fresh_install_smoke.py --disposable`

cwd: `./source`.
Запущена через ожидающий controller с уже проверенным изолированным окружением.
Общий exit code **0**. Полный stdout/stderr: `command-07.log`; запись argv/cwd/
времени/exit code: `commands.json`. Все штатные subcommands smoke завершились
успешно (subprocess check=True); модификаций исходников не было.

Python 3.14.7, Django 5.2.16, PostgreSQL 16.15.

| Этап | Фактический результат |
| --- | --- |
| check_database | PostgreSQL OK, server_version_num=160015 |
| migrate --noinput | 22 migrations применены, все OK |
| migrate --check | PASS, неприменённых migrations нет |
| makemigrations --check --dry-run | PASS, No changes detected |
| bootstrap_site, первый запуск | 6 grades, 12 subjects, 63 sections, 16 site pages + 263 lessons = 279 ContentPage; 263 publications; 29 media; 282 redirects |
| bootstrap_site, второй запуск | 0 новых/изменённых записей и 0 copied media; identities/content/media snapshot unchanged |
| Sentinel preservation | Штатный smoke проверил сохранность своего disposable user; пользователь working DB не создавался |
| collectstatic --noinput | 175 files copied, 507 post-processed, staticfiles manifest создан в isolated runtime |
| check_lesson_sources --all | Все 263 урока полностью совпали с БД |
| check_content_quality | 279 pages, 1137 SVG, 0 проблем |
| check_site_integrity | 1638 links/resources, 0 critical/broken links/missing media; 25 unused media сохранены |
| Штатная проверка source-material hashes в finally | PASS |

25 unused media — информационный результат unchanged check, не critical failure.
Ничего не удалялось для устранения этого сообщения.

## Независимый read-only source -> published comparison

`parity_audit.py`, exit **0**, полный лог `command-08.log`, JSON
`source-published-parity.json`. PostgreSQL REPEATABLE READ READ ONLY + rollback.
Целевые DB/role/port/source/runtime проверены до открытия подключения и в SQL.
Использованы штатные load_bundles/load_site_source/page_snapshot/digest.

- Все 279 mapped pages: 263 lessons и 16 structural/public pages.
- Exact mismatches HTML/CSS/JS/metadata/identity: **0**.
- Missing/unexpected pages: **0**.
- Все 263 LessonPublication digests совпадают со штатно rendered source.
- Все 1026 файлов source archive повторно сверены с исходным manifest:
  **unchanged**, без добавленных файлов.
- Для всех шести обязательных routes view rendering HTTP 200 и опубликованный
  body присутствует в результирующем HTML.
- LF/CRLF-исключения не понадобились: equality точная.

Обязательные routes:

1. `/`
2. `/karta-sajta/`
3. `/linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii/`
4. `/10-klass-stepennye-funkcii-i-grafiki-2-0/`
5. `/10-klass-chislovaya-okruzhnost-2-0/`
6. `/polozhitelnye-i-otriczatelnye-chisla-opredelenie-koordinatnoj-pryamoj/`

## Сервер и фактические HTTP-ответы

`python -B manage.py runserver 127.0.0.1:8002 --noreload`, cwd=isolated source,
PYTHONDONTWRITEBYTECODE=1, PGOPTIONS=-c default_transaction_read_only=on,
disposable environment. PID 29624; процесс работает, exit code ещё отсутствует.
Django system check: 0 issues. URL: http://127.0.0.1:8002/.

`http_audit.py`, exit **0**: 6/6 required routes HTTP 200; полные HTTP response
SHA256 совпадают с independently rendered views; 15/15 referenced CSS/JS HTTP
200 и совпадают с archived Git source после LF normalization. Детали и hashes:
`disposable-http-check.json`. Это GET-only проверка, не UI/keyboard/widget review.

Главная открыта через Codex in-app browser: title и h1 подтверждены по DOM,
новые ms-benefits-list / ms-lesson-sequence присутствуют. Screenshots не снимались.
Точная browser build/version для screenshot evidence ещё не зафиксирована;
её требуется установить перед следующим этапом, UA не предполагается из имени
браузера. Текущий browser tab сохранён для продолжения review.

## Working DB preservation

После smoke `working_fingerprint.py after` завершился с exit **0**:
WORKING_DB_FINGERPRINT_UNCHANGED=True. Снимок сохранён отдельно как
`working-db-after-smoke.json`. Counts/hashes всех 20 таблиц, column/index schema
и sequence states совпадают с `working-db-before.json`.
Оба probe read-only с rollback; содержимое строк/PII/secrets не сохранено.

## Следующий этап и статус human decisions

UI/content review подготовлен в `ui-review-plan.json`: 6 обязательных routes ×
360/768/1440 = 18 исходных состояний, дополнительные keyboard/widgets states.
Этот этап ещё не выполнен; screenshot-файлы не созданы, visual findings не
выдумываются. D02 остаётся human visual/content decision после review.
D03: fresh source/published parity подтверждён; отдельный substantive drift
working DB сохранён в drift-report.md и не устранён. Решение о принятии D03
принадлежит людям. Общие R01 records [координатор R01] не изменялись.
I01/React/FastAPI не начинались; commit/push и финальный review PR46 не выполнялись.
