# MathStart

Образовательный сайт по математике: FastAPI/Pydantic, SQLAlchemy/Alembic,
PostgreSQL 16+ и React/TypeScript с immutable SSG. Сохранены исходные уроки,
математика, URL, медиа, учётные записи и административные операции.
Будущие Knowledge/Assessment/Progress/Analyzer/Tutor/AI функции не реализованы.

| Путь | Назначение |
| --- | --- |
| backend/ | API, доменные сервисы, SQLAlchemy и Alembic, публикация и CLI |
| frontend/ | React, TypeScript, build, rendering и browser tests |
| curriculum/ | Исходные учебные HTML/JSON/CSS/JS/SVG, 263 темы |
| site_content/ | Структура сайта, редиректы, страницы и reviewed media |
| static/ | Общие authored CSS/JS/assets |
| deploy/ | Единственные канонические Dockerfile/Compose и runbooks |
| specs/ | Сохранённые доменные контракты и manifests |
| var/ | Игнорируемые локальные окружения, private настройки и отчёты |

Подготовленное локальное окружение: [запуск и остановка](docs/local-development.md).
Рабочая копия — основной Git root; разработка каждого задания идёт в отдельной ветке
от проверенного актуального main (без `codex/`) по [AGENTS.md](AGENTS.md). История переноса —
[краткая maintenance-запись](docs/maintenance.md).

## Чистый клон и запуск

Нужны Python 3.12+, Git, PostgreSQL 16+, Node 24 и npm 11.19.0; для контейнерного
пути Docker/Compose. Версии пакетов закреплены существующими lock-файлами.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --no-deps -r requirements.lock
python -m pip check
npm --prefix frontend ci
Copy-Item .env.example .env
```

Замените placeholders, храните ключи/DSN вне Git. Host CLI получает значения
через process environment (не печатайте `.env`). Контейнерный путь использует
отдельные private env files и явно выбранные volumes/subnet/loopback port.
Следуйте [deploy/RELEASE.md](deploy/RELEASE.md): schema `preview/apply/check`,
явный initial operator, `prepare-bootstrap`, locked frontend build,
publication `plan/publish`. До публикации readiness остаётся 503.
В [backend/READ_RUNTIME.md](backend/READ_RUNTIME.md) описаны env и content CLI.

```powershell
docker build -f deploy/Dockerfile --target api -t mathstart-api:local .
docker build -f deploy/Dockerfile --target edge -t mathstart-edge:local .
docker build -f deploy/Dockerfile --target frontend-builder -t mathstart-builder:local .
docker compose --env-file <private-compose-env> -f deploy/compose.yaml up -d db
# После schema/operator/build и перед HTTP publication probes:
docker compose --env-file <private-compose-env> -f deploy/compose.yaml up -d api edge
```

Корневой compose.yaml включает этот же deploy/compose.yaml; отдельного старого
Dockerfile/сервера нет. API запускается без Django, oracle и автоматического DDL.
Recovery/rollback после target writes описан в [deploy/RECOVERY.md](deploy/RECOVERY.md).
Не подключайте исходную Django-БД и чужие volumes к disposable-проверкам.

## Разработка и проверки

```powershell
python scripts/verify_repo.py --list
python scripts/verify_repo.py --profile pure
python scripts/check_migration_preservation.py
# Полный registry; нужны подготовленные DB/SSG/HTTP/browser inputs по runbook:
python scripts/verify_repo.py
```

Полный managed lifecycle, все 15 registry checks, fresh/upgrades и настоящие
Chrome/Edge/Firefox × 360/768/1440: [docs/target-runtime.md](docs/target-runtime.md).
Ordinary clean-clone installation отдельно проверяет `scripts/verify_installation.py`;
это disposable QA, он не оставляет сайт для использования. Skipped не равен PASS.
Локальные frontend команды: `npm --prefix frontend run dev`,
`npm --prefix frontend run typecheck`, `npm --prefix frontend test` и
`npm --prefix frontend run build`; build/preview требуют подготовленный публичный release.

Legacy comparisons запускаются явно из [отдельного pinned oracle](docs/legacy-oracle.md).
Обычный запуск сайта не требует этого checkout или его зависимостей.
Старые инструкции/исходники доступны по Git SHA; они не описывают текущий runtime.
Миграция принята и слита в PR54, консолидация завершена в PR55:
[принятый результат и evidence](docs/maintenance.md). Будущие продуктовые gates
и production rollout требуют отдельных решений.

Архитектура/версии: [ARCHITECTURE](ARCHITECTURE.md). Полное [ТЗ](docs/specifications/technical-spec-v7.2-draft.md),
[очередь](docs/tasks/INDEX.md), [дизайн-бриф](docs/ux/redesign-brief.md),
[аудит и вывод Harness](docs/audits/docs-and-workflow-cleanup.md). Новые дизайн/игровые решения ожидают выбора.
