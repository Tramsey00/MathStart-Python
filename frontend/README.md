> Для ежедневной разработки: `npm --prefix frontend run dev` из корня,
> один адрес http://127.0.0.1:8131 с HMR. CSS/React не требуют пересборки.
> Остановка: `npm --prefix frontend run dev -- --stop`.
> Собранный FastAPI preview запускается отдельно; режимы занимают один порт.
> Подготовленное окружение и границы clone-запуска — [инструкция](../docs/local-development.md).

> Текущий просмотр: один FastAPI server http://127.0.0.1:8131 — главная `/`,
> каталог `/materials`, уроки `/materials/8-algebra-32` и `/materials/7-algebra-8`.
> Vite preview ниже — историческая разработка, для просмотра он не требуется.
> Инструкция: [локальный запуск](../docs/local-development.md).

# React frontend

Текущий runtime: React/TypeScript, immutable public SSG и авторизованные формы
account/staff через FastAPI publication gateway. Основной checkout — корень
репозитория. Правила задач и исключение bootstrap — [AGENTS](../AGENTS.md).
Node работает при сборке и разработке; API/edge не запускают Node server.
Будущие учебные домены этим frontend пока не реализованы.

## Открыть учебную страницу

Основной runtime — FastAPI/SSG на одном origin: http://127.0.0.1:8131.
Линейная функция: http://127.0.0.1:8131/materials/7-algebra-8.
Все последующие переносимые уроки обслуживаются тем же сервером.

Для подготовленного локального экземпляра используй scripts/lesson_server.py
из [инструкции запуска](../docs/local-development.md). Новый урок не требует
Vite, отдельного порта или python http.server. Основной текст уже входит в SSG,
а React добавляет интерактивность. Автоматического seed при API startup нет.

Квадратичный Vite preview остаётся разработческим эталоном до MS-T006;
обычный просмотр новых страниц выполняется через FastAPI.
Чистый clone и единая установка команды — результат будущей MS-T002A.

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
