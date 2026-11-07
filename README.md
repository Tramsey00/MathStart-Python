# MathStart

Образовательный сайт: FastAPI/Pydantic, SQLAlchemy/Alembic, PostgreSQL и
React/TypeScript с immutable Content/SSG. Главная, каталог и четыре React-урока
приняты в bootstrap scope; будущий интеллектуальный учебный цикл не реализован.

Основной командный dev на Windows — **host-dev**. Нужны Git, Python 3.12,
Node 24/npm 11, PowerShell, Docker Desktop и включённые длинные пути Windows.
Vite/FastAPI работают на Windows, PostgreSQL — в Docker. Используйте одну обычную
папку проекта. После merge PR #58 используйте опубликованный main:

```powershell
git -c http.version=HTTP/1.1 -c core.longpaths=true -c core.autocrlf=false clone --branch main --single-branch https://github.com/Tramsey00/MathStart-Python.git MathStart-Python
Set-Location MathStart-Python
git config core.longpaths true
git config core.autocrlf false
git config http.version HTTP/1.1
# Одна первая подготовка по инструкции ниже, затем ежедневный запуск:
npm.cmd --prefix frontend run dev:host
```

Первая подготовка включает `.venv`, locked dependencies, свою БД и явные schema/
Content планы с review полного SHA256. Пошаговые команды — в
[инструкции host-dev](docs/local-development-host.md). Уже подготовленный clone
можно использовать как основную рабочую папку; отдельный host-check не требуется.

Один адрес **http://127.0.0.1:8131**: главная /, каталог /materials и уроки
/materials/7-algebra-8, /materials/8-algebra-32, /materials/5-math-12,
/materials/8-geometry-6. PostgreSQL хранится в persistent volume, настройки —
в ignored var/. API и HMR/WebSocket same-origin.

Повторный запуск, получение изменений и остановка:

```powershell
npm.cmd --prefix frontend run dev:host
# После сохранения своих изменений и отдельного Git pull:
git pull --ff-only origin main
# Изменения зависимостей/схемы/Content подготавливаются явно по инструкции.
# Для повторного запуска остановленного окружения:
npm.cmd --prefix frontend run dev:host
# Остановить свой экземпляр, сохранив данные:
npm.cmd --prefix frontend run dev:host:stop
```

Исходники остаются в обычном checkout. React/CSS обновляются через HMR,
Python в backend/ перезапускает только FastAPI. Существующий content.json обновляет dev-only проекцию,
не опубликованную БД/API. Startup не выполняет DDL, install, seed или publication.
Локальные данные сохраняются после остановки.

[Полная инструкция, review/digests и ограничения](docs/local-development.md).
[Основной Windows host-dev](docs/local-development-host.md) и альтернативный
полный Compose описаны отдельно.

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

Статус конкретных candidate и целевого контроля —
[карточка MS-T002A](skills/tasks/t002a-team-local-start/SKILL.md), [PR #58](https://github.com/Tramsey00/MathStart-Python/pull/58).
Отдельные review/приёмка, решение о merge и запуск clone опубликованного main
ещё необходимы. Вся MS-T002A не ACCEPTED, MS-T003 и production deploy не начаты.

[AGENTS](AGENTS.md), [архитектура/версии](ARCHITECTURE.md), [продукт](PRODUCT.md),
[очередь](docs/tasks/INDEX.md), [история](docs/maintenance.md),
[release](deploy/RELEASE.md), [recovery](deploy/RECOVERY.md).
