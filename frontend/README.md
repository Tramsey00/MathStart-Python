# React frontend

Основной dev — [Windows host-dev](../docs/local-development-host.md), из корня
обычного рабочего checkout с Git/Python 3.12/Node 24/npm 11/Docker Desktop.
После первой подготовки достаточно команд:

```powershell
npm.cmd --prefix frontend run dev:host
# Из второго терминала той же папки:
npm.cmd --prefix frontend run dev:host:stop
```

Первая подготовка устанавливает locked dependencies и создаёт свою БД и Content
release с review конкретных schema/publication планов. Start читает готовый
release, stop сохраняет данные. Действия после pull перечислены в инструкции.

Browser origin http://127.0.0.1:8131: /, /materials, /materials/7-algebra-8,
/materials/8-algebra-32, /materials/5-math-12, /materials/8-geometry-6.
Существующий supervisor запускает Vite/HMR и внутренний FastAPI на Windows;
API и WebSocket остаются на 8131, PostgreSQL использует отдельный persistent volume.
Исходники, node_modules и caches находятся в обычной папке проекта.
React/CSS используют HMR; изменения backend Python перезапускают FastAPI.
Dev content projection не публикует данные в БД; новая identity/URL требует подготовки Content.

Версии Node/npm/Python для Windows указаны в инструкции, pins контейнеров — в deploy/Dockerfile.
Frontend packages exact в package-lock.json; root/runtime Python locks сохранены.
Python -m frontend.build_public потребляет verified immutable input/receipt
handoff; простой Vite build не устанавливает Content release.
Production API/edge targets и deploy/compose.yaml остаются отдельными.

[Полный Compose](../docs/local-development.md#альтернативный-полный-docker-compose) —
альтернативный dev. Собранный FastAPI режим через lesson_server.py сохранён.
Dev:design — исторический prototype, не основной сайт. Квадратичная функция
уже подключена к runtime; MS-T006 переиспользует её.

Tests/typecheck/Playwright/check:dev/gates не запускаются этими операциями.
Npm test сообщает NOT_RUN; полный test:full только по поручению, по
[политике](../docs/frontend/testing-policy.md). Точный container evidence и
ограничения — в [MS-T002A](../skills/tasks/t002a-team-local-start/SKILL.md).
[AGENTS](../AGENTS.md), [архитектура](../ARCHITECTURE.md).
