# React frontend

Основной dev — [Compose workflow](../docs/local-development.md), из корня
Windows checkout с Git/Docker Desktop/PowerShell. Host Node/Python не нужны:

```powershell
.\dev.cmd prepare
.\dev.cmd start
# После обычного Git pull:
.\dev.cmd update
.\dev.cmd start
.\dev.cmd stop
```

Prepare/update объединяют locked dependencies и Content release preparation,
с обязательным человеческим review конкретных schema/publication планов.
Start читает подготовленный release; DDL/seed/build/publication не запускаются.
Stop сохраняет данные и credentials. Update не выполняет Git mutations.

Browser origin http://127.0.0.1:8131: /, /materials, /materials/7-algebra-8,
/materials/8-algebra-32, /materials/5-math-12, /materials/8-geometry-6.
Существующий supervisor запускает Vite/HMR и внутренний FastAPI в app-контейнере;
API и WebSocket остаются на 8131, PostgreSQL использует отдельный persistent volume.
Исходники bind-mounted из checkout, dependencies/.cache/.react-router/build —
в named volumes. Windows polling поддерживает CSS/React/content.json refresh.
Dev content projection не публикует данные в БД; новая identity/URL требует update.

Node/npm/Python берутся из pinned development target deploy/Dockerfile.
Frontend packages exact в package-lock.json; root/runtime Python locks сохранены.
Python -m frontend.build_public потребляет verified immutable input/receipt
handoff; простой Vite build не устанавливает Content release.
Production API/edge targets и deploy/compose.yaml остаются отдельными.

[Host-dev](../docs/local-development-host.md) — альтернатива с host Python/Node,
не prerequisite Compose. Собранный FastAPI режим через lesson_server.py сохранён.
Dev:design — исторический prototype, не основной сайт. Квадратичная функция
уже подключена к runtime; MS-T006 переиспользует её.

Tests/typecheck/Playwright/check:dev/gates не запускаются этими операциями.
Npm test сообщает NOT_RUN; полный test:full только по поручению, по
[политике](../docs/frontend/testing-policy.md). Точный container evidence и
ограничения — в [MS-T002A](../skills/tasks/t002a-team-local-start/SKILL.md).
[AGENTS](../AGENTS.md), [архитектура](../ARCHITECTURE.md).
