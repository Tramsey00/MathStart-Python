# Локальный запуск MathStart

Основной checkout — корень репозитория. Порядок веток и исключение ui/ux для
первых трёх задач — в [AGENTS](../AGENTS.md). После bootstrap каждый участник
работает в отдельной ветке своей задачи от origin/main, без codex/.

## Разработка: один адрес и автоматическое обновление

Для ежедневных правок используйте http://127.0.0.1:8131. Главная `/`, каталог
`/materials`, уроки `/materials/8-algebra-32` и `/materials/7-algebra-8` работают
на одном browser origin. В dev-режиме Vite обслуживает React/HMR на 8131,
а внутренний FastAPI — на loopback 8132. Этот внутренний адрес открывать не нужно.
API, private и legacy страницы проксируются с исходными Host/Origin и cookies.

В уже подготовленном checkout из корня:

```powershell
npm --prefix frontend run dev
```

Команда сама запускает оба процесса. Нужны Node 24, `frontend/node_modules` из
package-lock, target Python venv и приватная конфигурация опубликованного
локального экземпляра. Python выбирается из MATHSTART_PYTHON, корневой .venv,
активного VIRTUAL_ENV либо сохранённого локального runner. Чистый clone ещё
требует подготовки окружения и своей БД в MS-T002A; чужой var/ копировать нельзя.

Явный запуск через подготовленный venv этого checkout:

```powershell
& var/t001-qa/target-env/Scripts/python.exe scripts/dev_server.py
```

Для другого собственного экземпляра: `scripts/dev_server.py --env-file <path>`.
Приватный env-file по умолчанию — `var/local/lesson-preview/private-env.json`.
Обычный startup ничего не создаёт в БД и не запускает build/seed/тесты.
Сохранённые настройки runner — удобство этого checkout, не prerequisite команды.

После сохранения `.tsx`/`.css` страница обновляется автоматически. Существующие
React `content.json` также обновляют dev-просмотр; схема и identity проверяются
при чтении. Эти правки не публикуются в Content и не изменяют ответ API/БД.
Новый урок, URL, состав каталога или renderer_version требуют явной подготовки
Content release и перезапуска dev. Private/legacy UI пока остаются собранными;
их перенос/HMR входит в MS-T009/MS-T010 и задачи классов соответственно.

Остановка обоих собственных процессов — Ctrl+C в терминале запуска или:

```powershell
npm --prefix frontend run dev -- --stop
```

Занятые порты не освобождаются убийством неизвестных процессов. Сначала остановите
известный собственный режим. Для dev пишутся только ignored `var/local/dev/`
и frontend cache; Node не получает секретные значения из private env-file.
HMR доступен только на loopback, не предназначен для публичного deploy.

## Собранная версия: просмотр перед приёмкой

Тот же адрес 8131 обслуживает FastAPI без Vite/Node runtime:

```powershell
& var/t001-qa/target-env/Scripts/python.exe scripts/lesson_server.py
```

Dev и собранный режим не запускаются одновременно на одном порту. Готовые файлы
обновляются обычным prepare/build/publication; для каждой CSS-правки это не нужно.
`scripts/lesson_server.py --port` используется dev-supervisor только для
внутреннего bind; логический public origin остаётся прежним.

## Ручная проверка dev-режима — только по поручению

Не запускать автоматически или после UI-правок. Только по отдельному поручению
`npm --prefix frontend run check:dev` проверяет четыре текущие страницы, API proxy,
WebSocket на 8131, реальное обновление CSS/React/content.json и изоляцию опубликованного
Content API. Временные маркеры удаляются с восстановлением исходных bytes;
при конкурентной правке script отказывается её перезаписывать. Это явный smoke
при изменении dev tooling/MS-T002A, не действие после каждой кнопки и не полный QA.

## Исторический preview утверждённого дизайна

Для просмотра новой главной, каталога и React-эталона урока достаточно tracked
исходников и Node 24.21.0/npm 11.19.0. Из корня репозитория:

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev:design
```

Главная: http://127.0.0.1:5173/; материалы: http://127.0.0.1:5173/materials.html;
эталон квадратичной функции: http://127.0.0.1:5173/materials/8-algebra-32.
Для этого preview Docker, Python, БД и var/local владельца не нужны.
Команда должна выполняться из ветки/commit, где опубликованы новые исходники.
Незакоммиченные локальные изменения автора не появляются в чужом clone.

Это временный самостоятельный preview. Команда npm run dev пока использует
основную оболочку на 5171 и требует подготовленные public inputs. MS-T001 и
MS-T002 интегрируют шаблон на новом линейном уроке и public pages. Квадратичный
React preview сохраняется; его runtime-интеграция — MS-T006. MS-T002A подтверждает единый запуск итогового main
из чистого clone у другого участника. Публичный production deploy не требуется.

## Подготовленный локальный runtime FastAPI

Docker использует canonical deploy/compose.yaml и images из согласованного
commit. Приватные настройки и README конкретного экземпляра находятся в
игнорируемом var/local/. Они не должны быть скрытым prerequisite чужого clone.
Зависимости от migration-execution, tmp, исторического checkout или Django нет.

Из корня в PowerShell:

```powershell
./scripts/local.ps1 start
./scripts/local.ps1 status
./scripts/local.ps1 logs
./scripts/local.ps1 stop
```

Stop сохраняет данные. Скрипт не удаляет volumes и не перезапускает Docker/WSL.
Существующий экземпляр доступен по http://127.0.0.1:8121/, /account/ и /admin/.
Его operator — acceptance_admin; пароль владельца хранится локально в
var/local/private/operator.env. Не копировать приватные файлы/cookies в Git
или другим участникам. Точные image revisions и storage identities описаны
в локальном README экземпляра; historical имена volumes не выбирают старый код.

## Новая независимая установка

Чистый clone не содержит private settings и подготовленной БД. Используй
[release installation](../deploy/RELEASE.md): новые собственные volumes,
отдельные roles/keys, schema preview/apply/check, initial operator, immutable
prepare/build и обычные publication plan/publish. Не подключай второго writer
и не сбрасывай существующую БД ради новой установки. До замены images сохрани
проверенный backup БД и проверь совместимость по [recovery](../deploy/RECOVERY.md).

Host tools используют Python 3.12 и root requirements.lock; frontend — свой
package-lock. Подготовленный venv не считать уже существующим: при необходимости
создать его явно по locks, без Django/DRF. Отдельный pinned [oracle](legacy-oracle.md)
готовится только для необходимого historical сравнения. Полный managed QA —
[target testing](target-runtime.md); обычный локальный запуск его не выполняет.

Техническая основа proxy/HMR соответствует [документации закреплённого Vite 7.3.7](https://github.com/vitejs/vite/blob/v7.3.7/docs/config/server-options.md).
