# MathStart

Образовательный сайт: FastAPI/Pydantic, SQLAlchemy/Alembic, PostgreSQL и
React/TypeScript с immutable Content/SSG release. Главная, каталог и четыре
React-урока приняты в bootstrap scope. Остальные материалы сохраняют legacy
renderer. Будущий интеллектуальный учебный цикл не реализован.

До отдельного merge клонируйте **ui/ux**, чтобы получить новую версию:

```powershell
git -c core.longpaths=true -c core.autocrlf=false clone --branch ui/ux --single-branch https://github.com/Tramsey00/MathStart-Python.git MathStart-team
Set-Location MathStart-team
git config core.longpaths true
git config core.autocrlf false
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --no-deps -r requirements.lock
& .\.venv\Scripts\python.exe -m pip check
npm --prefix frontend ci --no-audit --no-fund
& .\.venv\Scripts\python.exe scripts/team_local.py init
& .\.venv\Scripts\python.exe scripts/team_local.py schema-preview
# Просмотреть plan; подставить напечатанный digest (в течение 30 минут):
& .\.venv\Scripts\python.exe scripts/team_local.py schema-apply --reviewed-plan-sha256 <SCHEMA_SHA256>
& .\.venv\Scripts\python.exe scripts/team_local.py content
# Просмотреть publication plan; подставить его напечатанный digest:
& .\.venv\Scripts\python.exe scripts/team_local.py publish --reviewed-plan-sha256 <PUBLICATION_SHA256>
npm --prefix frontend run dev
```

Нужны Windows/PowerShell, Git, Python 3.12, Node 24.x/npm 11.x, Docker Desktop
Linux engine и доступ к registries. Пакеты закреплены locks. Своя PostgreSQL
создаётся явно на loopback; private настройки генерируются в ignored var/.
Чужие БД/cookies/.env/runner/файлы автора не нужны. Пользователи автоматически
не создаются. Подробности prerequisites, plan review и ошибок —
[полная инструкция](docs/local-development.md).

Один адрес **http://127.0.0.1:8131**: /, /materials, /materials/7-algebra-8,
/materials/8-algebra-32, /materials/5-math-12, /materials/8-geometry-6.
Vite HMR и внутренний FastAPI используют same-origin proxy. CSS/React не требуют
release build. Существующий content.json обновляет dev-просмотр без публикации в БД.

Остановка Ctrl+C или из второго PowerShell в том же checkout:

```powershell
npm --prefix frontend run dev -- --stop
& .\.venv\Scripts\python.exe scripts/team_local.py db-stop
# Следующий запуск, без повторной подготовки:
& .\.venv\Scripts\python.exe scripts/team_local.py db-start
npm --prefix frontend run dev
```

Собранный FastAPI-просмотр: остановите dev, выполните
`& .\.venv\Scripts\python.exe scripts/lesson_server.py`; адрес тот же,
остановка Ctrl+C. Startup не делает DDL, seed, build или publication.

| Путь | Назначение |
| --- | --- |
| backend/ | Content/Users/Staff, API, persistence, schema/publication CLI |
| frontend/ | React/TypeScript, HMR и immutable build |
| curriculum/, site_content/, static/ | Учебный контент, структура, tracked assets |
| deploy/ | Канонические images/Compose, release/recovery |
| specs/ | Доменные контракты и manifests |
| docs/tasks/, skills/tasks/ | Единая очередь и карточки |
| var/ | Игнорируемые собственные config/build/log resources |

Автоматические прогоны выключены решением пользователя 25.10.2026. Npm test
сообщает NOT_RUN; test:full/typecheck и остальные gates — по отдельному поручению.
Dev/setup их не вызывают. Доменные валидаторы и publication guards сохранены.
[Политика проверок](docs/frontend/testing-policy.md).

MS-T002A передаёт clone-запуск ui/ux на review. Вся задача завершится после
человеческого решения о merge и контроля clone опубликованного main. Merge и
production deploy не выполняются автоматически; MS-T003 не начата. С MS-T003:
Issue, ветка от origin/main без codex/ и PR по [AGENTS](AGENTS.md).
Другие ОС этим Windows-контролем не подтверждены.

[Архитектура/версии](ARCHITECTURE.md), [продукт](PRODUCT.md),
[очередь](docs/tasks/INDEX.md), [MS-T002A](skills/tasks/t002a-team-local-start/SKILL.md),
[стандарт уроков](docs/frontend/lesson-migration.md), [история](docs/maintenance.md),
[release](deploy/RELEASE.md), [recovery](deploy/RECOVERY.md).
Legacy oracle — только отдельно по [инструкции](docs/legacy-oracle.md).
