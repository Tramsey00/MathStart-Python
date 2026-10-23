# React frontend

Текущий runtime: React/TypeScript, immutable public SSG и авторизованные формы
account/staff через FastAPI publication gateway. Основной checkout — корень
репозитория. Правила задач и исключение bootstrap — [AGENTS](../AGENTS.md).
Node работает при сборке и разработке; API/edge не запускают Node server.
Будущие учебные домены этим frontend пока не реализованы.

## Посмотреть утверждённый новый дизайн

Из корня clone с установленными Node 24.21.0 и npm 11.19.0:

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev:design
```

Открой http://127.0.0.1:5173/ — главная,
http://127.0.0.1:5173/materials.html — каталог,
http://127.0.0.1:5173/materials/8-algebra-32 — принятый React-эталон квадратичной функции.
Этот preview читает tracked curriculum и не требует БД или чужого var/.
Порт 5173 должен быть свободен; второй сервер на занятом порту не запускать.
После остановки команды сервер прекращает работу.

`npm run dev` пока запускает основную React Router оболочку на 5171, а не
этот preview. Для реальных public страниц ей нужны verified public build inputs.
MS-T001 проверит перенос на новом линейном уроке, MS-T002 подключит public pages;
runtime-интеграция квадратичной функции включена в MS-T006. MS-T002A должна подтвердить
единый документированный запуск результата из чистого clone опубликованного main.
Preview сам по себе не доказывает работу FastAPI, входа или публикации.

## Зафиксированные инструменты

Используй существующие Node 24.21.0/npm 11.19.0 и package-lock.json.
Не пересоздавай lock для документационной правки.

```powershell
npm --prefix frontend run typecheck
npm --prefix frontend test
npm --prefix frontend run build
```

Генерация API сохраняет canonical OpenAPI/DTO и исходные manifest digests.
Только явно выведенные historical pins читаются из точных Git commits;
сохранённые контракты и проверенные текущие adapters используют фактические
HEAD/working bytes. Для проверки истории нужен полный Git history.

Обычный опубликованный сайт собирается командой `python -m frontend.build_public`
с точными immutable input/receipt digests, release ID, output directory и
public origin из [release runbook](../deploy/RELEASE.md). Обычная Vite build
или dev server не являются установленным public release.

Для существующего локального runtime см. [локальный запуск](../docs/local-development.md).
Account/staff APIs проверяют session, CSRF, permissions и mutation contracts;
видимость React не заменяет authorization. Public artifacts содержат только
анонимные оболочки, а не приватные данные пользователя.

## Проверки

Type/unit проверки дают evidence только своего scope. Полный managed target
запускает настоящий Chrome/Edge/Firefox на 360/768/1440 и проверяет функции,
математику, доступность, authorization и security. Missing/skipped/flaky либо
неполные project receipts не засчитываются. См. [target verification](../docs/target-runtime.md)
и [политику выбора проверок](../docs/frontend/testing-policy.md).
Точечная поддержка не вводит новые pixel-perfect/spacing критерии.

`verify:foundation` создаёт новый игнорируемый verification-run receipt,
сохраняет source/checkout provenance и отказывается перезаписывать существующие
или historical evidence paths. Старые checkpoint recorders требуют исходный
pinned task checkout/branch и не являются текущими entry points. Их исходники
и approvals доступны в Git 3a290a46d991e22269a17dde41e39f0637576071.
