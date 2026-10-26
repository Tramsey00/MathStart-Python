# Альтернативный host-dev

Исторический путь от 25.10.2026, требующий host Python/Node и своей PostgreSQL.
Основной командный путь — [Docker Compose](local-development.md). Результаты
host-dev не подтверждают контейнерный candidate. Приватные конфигурации двух
путей независимы; var/ между checkout не копировать.
# Локальный запуск MathStart после clone

До отдельного merge bootstrap клонируйте опубликованную **ui/ux**. Main пока
не содержит новые страницы. Основной сайт — React + Content + FastAPI + PostgreSQL,
один browser origin **http://127.0.0.1:8131**. Это локальная установка, не production.

## Требования

- Windows, PowerShell, Git с long paths; короткий путь checkout.
- Python **3.12** с venv/pip (`python --version`). Если работает launcher,
  первую команду venv можно заменить на `py -3.12 -m venv .venv`.
- Node **24.x**, npm **11.x** по engines frontend/package.json. Docker/CI
  закреплены на Node 24.21.0/npm 11.19.0; фактически проверенные локальные
  версии записаны в карточке MS-T002A.
- Docker Desktop с работающим Linux engine; Compose этому host-dev пути не нужен.
  PostgreSQL image закреплён digest из deploy/compose.yaml.
- Доступ к GitHub, PyPI, npm и Docker registry при первой установке.
- Свободные loopback 8131/8132 и 55449 для своей БД. Последний можно изменить
  через `init --pg-port 55450`. Не завершайте неизвестных владельцев портов.

Runtime packages закреплены requirements.lock и вложенными locks; frontend —
package-lock.json. Django/DRF и oracle не нужны. Assets/шрифты/curriculum берутся
из Git. Не копируйте чужие var/, БД, .env, cookies, runner или готовые builds.

## 1. Clone и locked установка

В PowerShell из родительского каталога (выберите своё новое имя папки):

```powershell
git -c http.version=HTTP/1.1 -c core.longpaths=true -c core.autocrlf=false clone --filter=blob:none --branch ui/ux --single-branch https://github.com/Tramsey00/MathStart-Python.git MathStart-team
Set-Location MathStart-team
git config core.longpaths true
git config core.autocrlf false
git config http.version HTTP/1.1
git rev-parse HEAD
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --no-deps -r requirements.lock
& .\.venv\Scripts\python.exe -m pip check
npm --prefix frontend ci --no-audit --no-fund
```

Активация venv не требуется, execution policy PowerShell не мешает запуску.
Не пересоздавайте locks. npm ci не запускает tests. HTTP/1.1 и lazy blobs использованы после зависания обычного clone.
Filter=blob:none сохраняет историю; historical blobs догружаются с GitHub.
Не используйте shallow clone:
некоторые build inputs имеют точные historical Git pins.

## 2. Своя БД и явная schema

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py init
& .\.venv\Scripts\python.exe scripts/team_local.py schema-preview
```

Init создаёт уникальный labelled Docker container и persistent volume,
PostgreSQL только на 127.0.0.1:55449, отдельные nonsuperuser schema/runtime roles,
случайные пароли и ключи в ignored var/. Пароли не передаются в argv и не
печатаются. Application tables и пользователи пока не создаются.
Runtime не владеет DDL; отдельная schema-role используется явными CLI подготовки.

Просмотрите локально var/local/team/schema.json: profile=FRESH, table_count=0,
ожидаемые target_head и database/role binding. Private plans/config не публикуйте.
Preview печатает REVIEW_REQUIRED: plan SHA256 … . Подставьте digest за 30 минут:

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py schema-apply --reviewed-plan-sha256 <SCHEMA_SHA256>
```

Это обычные backend.release_migrate preview/apply/check с signature, maintenance,
code/DB identity и expiry guards. Явный шаг устанавливает schema и permission
metadata. Пользователь/operator для публичных страниц не требуется и автоматически
не создаётся. Если позже нужен staff, initial operator создаётся отдельно по
[release runbook](../deploy/RELEASE.md), до появления других пользователей.

## 3. Content prepare → build → plan → publication

Остановите свой dev перед первой публикацией: временный FastAPI gateway
использует 8131 для обязательных HTTP publication probes.

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py content
```

Команда вызывает обычный prepare-bootstrap из tracked source точного HEAD,
frontend.build_public с verified immutable input/receipt digests и publication
plan. Собирается весь текущий Content, включая legacy-страницы и шесть новых
React-страниц. Suites/typecheck/source gates не запускаются; штатные доменные
валидаторы и integrity/publication guards сохранены. Build занимает несколько
минут, вывод в var/local/team/logs/.

Просмотрите var/local/team/publication.json: initial install, previous=null,
origin http://127.0.0.1:8131, ожидаемые release/changes. Content печатает digest:

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py publish --reviewed-plan-sha256 <PUBLICATION_SHA256>
```

Publish запускает временный обычный FastAPI gateway, выполняет fenced
backend.content.publish publish с обязательными HTTP probes, ждёт COMPLETE и
останавливает только свой временный процесс. Нет synthetic activation,
отключения guards, hosts override или чужой БД. До публикации runtime UNREADY.
Только этот явный шаг публикует Content в БД.

На Windows холодная полная валидация release может превысить HTTP timeout первого
publication probe. Setup допускает одно ограниченное продолжение: читает durable
status, требует свой operation/owner/generation, db_committed=true, activation=APPLIED,
RECOVERY_REQUIRED/PUBLIC_VERIFICATION_FAILED и ожидаемый active release. Затем
продлевает свою lease, прогревает read cache запросом с timeout 60 секунд и точным
сравнением immutable index, снова продлевает lease и выполняет обычный CLI resume.
Все HTTP guards publisher остаются с timeout 5 секунд; domain commit не повторяется.
Warmup сам по себе не является acknowledgement. Успех — только phase COMPLETE
после всех обычных probes. Первый отказ и resume сохраняются отдельными logs.
Другое/неизвестное состояние, mismatch или повторный отказ останавливают установку.

Init/schema/content — первая установка: существующие файлы не перезаписываются.
Не повторяйте apply/publish вслепую после ошибки/неопределённого COMMIT: состояние
и private logs сохранены; status/recovery — по [RELEASE](../deploy/RELEASE.md)
и [RECOVERY](../deploy/RECOVERY.md). Повтор bootstrap поверх данных не нужен.
При изменении schema/состава/URL контента нужна отдельная подготовка release.

## 4. Ежедневный dev с HMR

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py db-start
npm --prefix frontend run dev
```

Откройте:

- http://127.0.0.1:8131/
- http://127.0.0.1:8131/materials
- http://127.0.0.1:8131/materials/7-algebra-8
- http://127.0.0.1:8131/materials/8-algebra-32
- http://127.0.0.1:8131/materials/5-math-12
- http://127.0.0.1:8131/materials/8-geometry-6

Vite обслуживает React/HMR WebSocket на 8131, внутренний FastAPI — loopback 8132.
API/assets/private/legacy идут через same-origin proxy с исходными Host/Origin/
cookies. Внутренний адрес открывать не нужно. Npm run dev находит свой .venv;
активация и сохранённый runner не нужны. Явный Python: MATHSTART_PYTHON;
private JSON: аргумент --env-file. Не копируйте private config другого checkout.

Обычный startup читает release, готовит read-only dev view и запускает процессы.
Он не делает DDL, seed, создание пользователей, build, publication или tests.
Vite не получает private значения из JSON.

React/CSS обновляются через HMR без build. Существующий React content.json
вызывает reload и dev-only projection с валидацией identity/schema: БД,
опубликованный API и установленный release не изменяются. Новые URL/темы/relations/
renderer_version требуют явной подготовки Content. Private/legacy UI пока
используют собранную версию; их HMR не входит в этот этап.

## Остановка и повторный запуск

Ctrl+C в терминале dev останавливает оба процесса. Из второго PowerShell того
же checkout:

```powershell
npm --prefix frontend run dev -- --stop
& .\.venv\Scripts\python.exe scripts/team_local.py db-stop
```

Db-stop сохраняет volume/schema/Content. Для продолжения повторите db-start и
npm run dev из шага 4, без новой установки/публикации. Команды проверяют владельца
ресурсов, не останавливают Docker/WSL, не удаляют volumes и не завершают неизвестные
процессы. Scripts/local.ps1 обслуживает отдельный прежний экземпляр и здесь не
используется. Защищённый acceptance stack не трогать.

## Собранная FastAPI-версия без Vite

После остановки dev, при работающей своей БД:

```powershell
& .\.venv\Scripts\python.exe scripts/lesson_server.py
```

Адрес тот же 8131, установленный immutable Content/SSG release; Node runtime
не нужен. Остановка Ctrl+C. Возврат к HMR — npm --prefix frontend run dev.
Режимы не работают одновременно.

## Границы контроля

MS-T002A проверяет установку GitHub clone, шесть фактических страниц, CSS/JS/fonts,
API/WebSocket, CSS/React/content refresh, остановку/перезапуск. Точные SHA/версии/
ограничения — в [карточке](../skills/tasks/t002a-team-local-start/SKILL.md).
Остальные suites — NOT_RUN_BY_USER_REQUEST по [политике](frontend/testing-policy.md).
Check:dev не является шагом установки. Clone опубликованного main проверяется
после отдельного merge; до него вся MS-T002A не ACCEPTED и MS-T003 не начинается.

Windows — платформа этого поручения. Tooling имеет POSIX paths, но macOS/Linux/
WSL этим контролем не подтверждены: замените .venv/Scripts/python.exe на
.venv/bin/python, обеспечьте Docker и права. Production TLS/ingress/backups и
provider/security решения — отдельный scope.

