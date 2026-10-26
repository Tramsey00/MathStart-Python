# MathStart

Образовательный сайт: FastAPI/Pydantic, SQLAlchemy/Alembic, PostgreSQL и
React/TypeScript с immutable Content/SSG. Главная, каталог и четыре React-урока
приняты в bootstrap scope; будущий интеллектуальный учебный цикл не реализован.

Основной командный dev — **Docker Compose**. На Windows нужны Git, Docker Desktop
с Linux engine/Compose и PowerShell. Host Python/Node/npm/PostgreSQL не требуются.
До отдельного merge используйте опубликованную ui/ux:

```powershell
git -c http.version=HTTP/1.1 -c core.longpaths=true -c core.autocrlf=false clone --filter=blob:none --branch ui/ux --single-branch https://github.com/Tramsey00/MathStart-Python.git MathStart-team
Set-Location MathStart-team
git config core.longpaths true
git config core.autocrlf false
git config http.version HTTP/1.1
.\dev.cmd prepare
.\dev.cmd start
```

Prepare показывает конкретные schema и Content планы: просмотрите каждый файл и
подтвердите его полным SHA256. Автоматического утверждения нет. Повторная
подготовка сохраняет DB/credentials; неизменившиеся шаги пропускаются.

Один адрес **http://127.0.0.1:8131**: главная /, каталог /materials и уроки
/materials/7-algebra-8, /materials/8-algebra-32, /materials/5-math-12,
/materials/8-geometry-6. Vite/FastAPI работают в app-контейнере, PostgreSQL —
в отдельном контейнере с persistent volume. API и HMR/WebSocket same-origin.

Повторный запуск, получение изменений и остановка:

```powershell
.\dev.cmd start
# После сохранения своих изменений и отдельного Git pull:
git pull --ff-only origin ui/ux
.\dev.cmd update
.\dev.cmd start
# Остановить свой экземпляр, сохранив данные:
.\dev.cmd stop
```

Исходники остаются в обычном checkout и bind-mounted в контейнеры. React/CSS
обновляются через HMR. Существующий content.json обновляет dev-only проекцию,
не опубликованную БД/API. Startup не выполняет DDL, install, seed или publication.
Update не делает Git pull/reset/checkout и не удаляет локальную БД.

[Полная инструкция, review/digests и ограничения](docs/local-development.md).
[Альтернативный host-dev](docs/local-development-host.md) сохранён отдельно;
его исторические результаты не подтверждают контейнерную приёмку.

| Путь | Назначение |
| --- | --- |
| backend/ | Content/Users/Staff, API, persistence, schema/publication CLI |
| frontend/ | React/TypeScript, HMR и immutable build |
| curriculum/, site_content/, static/ | Учебный контент, структура, tracked assets |
| deploy/ | Production images/Compose/runbooks и отдельный Compose dev |
| dev.ps1, scripts/container_dev.py | Четыре операции командного local workflow |
| specs/ | Доменные контракты и manifests |
| docs/tasks/, skills/tasks/ | Единая очередь и карточки |
| var/ | Игнорируемые private config/plans/logs; БД/dependencies/builds в volumes |

Автоматические suites выключены решением пользователя 25.10.2026. Npm test
сообщает NOT_RUN; полные suites/typecheck/gates — только по отдельному поручению.
Dev/setup их не вызывают; доменные validators и publication guards сохранены.
[Политика проверок](docs/frontend/testing-policy.md).

Статус конкретного контейнерного candidate и целевого контроля —
[карточка MS-T002A](skills/tasks/t002a-team-local-start/SKILL.md), [PR #58](https://github.com/Tramsey00/MathStart-Python/pull/58).
Отдельные review/приёмка, решение о merge и запуск clone опубликованного main
ещё необходимы. Вся MS-T002A не ACCEPTED, MS-T003 и production deploy не начаты.

[AGENTS](AGENTS.md), [архитектура/версии](ARCHITECTURE.md), [продукт](PRODUCT.md),
[очередь](docs/tasks/INDEX.md), [история](docs/maintenance.md),
[release](deploy/RELEASE.md), [recovery](deploy/RECOVERY.md).
