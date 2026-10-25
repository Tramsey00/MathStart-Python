# React frontend

React/TypeScript, React Router framework, immutable public SSG и формы
account/staff через FastAPI. Node работает при сборке и dev; собранный runtime
использует FastAPI и PostgreSQL.

Первый запуск clone требует своей БД, schema и Content publication:
[Windows-инструкция](../docs/local-development.md). До merge клонируйте ui/ux.
Один Vite без Content не является установленным основным приложением.

После установки из корня:

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py db-start
npm --prefix frontend run dev
# Из другого терминала того же checkout:
npm --prefix frontend run dev -- --stop
& .\.venv\Scripts\python.exe scripts/team_local.py db-stop
```

Browser origin **http://127.0.0.1:8131**: /, /materials,
/materials/7-algebra-8, /materials/8-algebra-32, /materials/5-math-12,
/materials/8-geometry-6. API и HMR WebSocket остаются на 8131; FastAPI 8132 —
внутренний loopback. CSS/React обновляются через HMR. Существующий content.json
вызывает dev reload с валидацией, без изменения Content API/БД. Новые identity/URL
требуют отдельной публикации.

Собранная версия: остановите dev, выполните
`& .\.venv\Scripts\python.exe scripts/lesson_server.py`, остановка Ctrl+C.
Тот же адрес 8131, Node runtime не нужен. Startup не делает DDL/seed/publication.

Manifest допускает Node >=24 <25/npm >=11 <12. PackageManager и Docker/CI
закреплены на npm 11.19.0/Node 24.21.0. Пакеты exact в package-lock.json.
Установка: npm --prefix frontend ci --no-audit --no-fund. Фактически проверенные
локальные версии записаны в карточке MS-T002A. Lock не пересоздавать.

Python -m frontend.build_public потребляет verified immutable inputs/receipt
digests; team_local.py content вызывает именно этот build. Обычная Vite build
не устанавливает release. Dev/build не запускают suites. Account/staff APIs
сохраняют session/CSRF/permission guards; public artifacts не содержат PII.

Tests/typecheck/Playwright/check:dev выключены по
[политике](../docs/frontend/testing-policy.md). Отдельное поручение разрешает
конкретный scope. Npm test сообщает NOT_RUN с кодом 2; полный suite сохранён
как npm run test:full. Clone-контроль не является полным QA/production acceptance.

Dev:design — исторический prototype preview, не команда запуска сайта.
Квадратичная функция уже подключена к runtime; MS-T006 переиспользует её.
[AGENTS](../AGENTS.md), [архитектура и версии](../ARCHITECTURE.md).
