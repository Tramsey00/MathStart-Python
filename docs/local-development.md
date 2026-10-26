# Командная разработка MathStart через Docker Compose

Нужны **Git, Docker Desktop с Linux engine/Compose и PowerShell**. Python,
Node/npm и PostgreSQL на хосте не нужны. До отдельного merge клонируйте `ui/ux`.
Windows entry point `dev.cmd` вызывает локальный dev.ps1 через системный
PowerShell; execution policy задаётся только этому процессу, глобальные настройки
Windows не меняются. Все четыре операции реализованы в одном PowerShell workflow.
Это основной локальный dev-путь; production Compose и его данные отдельны.
Статус проверки конкретного candidate — в [MS-T002A](../skills/tasks/t002a-team-local-start/SKILL.md).

## Первый запуск

Из родительской папки PowerShell, в собственный новый каталог:

```powershell
git -c http.version=HTTP/1.1 -c core.longpaths=true -c core.autocrlf=false clone --branch ui/ux --single-branch https://github.com/Tramsey00/MathStart-Python.git MathStart-team
Set-Location MathStart-team
git config core.longpaths true
git config core.autocrlf false
git config http.version HTTP/1.1
.\dev.cmd prepare
.\dev.cmd start
```

Откройте **http://127.0.0.1:8131**. На хосте публикуется только этот loopback-порт.
Своя PostgreSQL работает без host-порта. В app-контейнере существующий supervisor
запускает Vite и внутренний FastAPI на loopback 8132; API/private/legacy routes
и WebSocket используют тот же browser origin 8131 с исходными Host/Origin/cookies.
Подготовка использует отдельный одноразовый tools-контейнер того же dev image.

Docker Desktop должен быть уже в состоянии Engine running. Нужен доступ к
GitHub и package/image registries при первой загрузке. Не используйте shallow
clone: build читает некоторые точные historical Git pins. Используйте полный
clone этой ветки с HTTP/1.1: в текущей репетиции deferred blob fetch partial clone
зависал, тогда как полный GitHub transfer начался нормально. Локальные Git objects
автора для установки не используются.
Windows/PowerShell — целевой хост; другие ОС не объявляются проверенными.

## Четыре операции

| Команда | Действие |
| --- | --- |
| `.\dev.cmd prepare` | Первая подготовка; повторно сохраняет DB/credentials и пропускает неизменившиеся шаги |
| `.\dev.cmd start` | Запуск подготовленной БД и Vite/FastAPI; без install, DDL, seed, build/publication |
| `.\dev.cmd update` | Явная подготовка изменений после вашего pull; останавливает только свой app |
| `.\dev.cmd stop` | Остановка своего app/DB с сохранением volumes, credentials и Content |

Prepare/update оставляют app остановленным: после завершения выполните start.
Stop не выполняет down -v, не удаляет volumes, не перезапускает Docker/WSL и не
завершает неизвестных владельцев 8131. Если порт занят, остановите известный
собственный режим его штатной командой. Конфигурацию production/acceptance не трогать.

## Обязательный review планов

Prepare объединяет locked install, schema и Content prepare/build/publication,
но не утверждает планы за человека. Сначала создаётся подписанный FRESH schema
plan. Команда показывает конкретный путь, digest и сводку: профиль, target head,
DB/role identity, table count и expiry. Просмотрите файл, затем введите **полный
SHA256 этого плана**. Enter оставит его pending без применения.

После schema строится Content plan с origin, previous release, input/output
digests и перечнем изменений. Его также нужно просмотреть и подтвердить точным
SHA256. Первый запуск поэтому требует двух отдельных решений; длинные pip/npm/
CLI команды вводить вручную не нужно. Startup никогда не спрашивает review и
не применяет изменения вместо prepare/update.

Для отложенного review или автоматизации без автоматического согласия:

```powershell
.\dev.cmd prepare -NonInteractive
# Exit 42: конкретный plan и review.json находятся в ignored var/compose/.
# После отдельного review подставьте полученный digest:
.\dev.cmd prepare -NonInteractive -SchemaDigest SCHEMA_SHA256
# Затем просмотрите полученный Content plan и подтвердите его:
.\dev.cmd prepare -NonInteractive -ContentDigest CONTENT_SHA256
```

Эти параметры передают ваше уже принятое решение по конкретному плану. Они не
подавляют validators. Истёкший неприменённый schema preview сохраняется и
заменяется новым preview с новым обязательным digest. Изменение source/code/DB
после review отклоняется штатным schema/publication протоколом. После неизвестного
COMMIT или оставшегося pending journal не повторяйте apply вслепую: установка
сохраняет state/plans/logs и требует нормального [recovery](../deploy/RECOVERY.md).

Первый local publication может столкнуться с cold-read timeout. Существующий
установщик допускает одно ограниченное продолжение: собственные committed/
activated owner/fence/release проверяются, exact index прогревается read-only,
затем выполняется обычный fenced resume. Domain commit не повторяется; HTTP
publication guards остаются 5 секунд. Успех — только COMPLETE после всех probes.

## Работа с исходниками и GitHub

Исходники bind-mounted из обычной папки checkout. Редактируйте их своим editor,
смотрите HMR React/CSS без release build, коммитьте и отправляйте через Git.
Polling включён для Windows mounts. Существующий React content.json вызывает
validated dev-only refresh; опубликованная БД/API при этом не изменяются.
Новые URL/темы/relations и готовый SSG release требуют явного update.

Для получения изменений от команды:

```powershell
# Сначала сохраните собственные правки обычным commit; не сбрасывайте dirty tree.
git pull --ff-only origin ui/ux
.\dev.cmd update
.\dev.cmd start
```

Сейчас действует bootstrap-исключение ui/ux и PR #58. После отдельной приёмки и
merge baseline в main команда получает main; с MS-T003 — Issue → task branch
от origin/main → commit/push → PR → review → человеческое решение о merge.
Update не делает Git pull/reset/checkout и не переключает ветки самостоятельно.
Непринятые source/build-input правки перед publication нужно закоммитить;
при отказе они сохраняются. Обычный start/HMR не требует коммитить CSS-правку.

## Что обновляется и что сохраняется

- Изменение Dockerfile, Python locks и image COPY inputs вызывает build нового
  dev image. Docker layer cache сохраняет неизменившиеся dependency layers.
- Изменение frontend package/lock вызывает npm ci в named dependency volume.
  При том же digest повторная установка пропускается.
- Schema code fingerprint проверяется отдельно. Новая пустая DB получает только
  reviewed FRESH plan. Для существующей DB canonical physical schema check
  определяет совместимость code changes, без повторного fresh/stamp/seed.
  Неизвестная revision graph или несовместимая schema останавливают update:
  сначала нужен поддерживающий её reviewed release migration protocol. Текущая
  canonical chain содержит v01_0001/v01_0002; произвольный будущий upgrade не
  угадывается и applied history не переписывается.
  Изменение/удаление уже применённого migration-файла также останавливает update.
- Изменения lesson/source/assets, frontend build inputs, каталога и route registry
  вызывают обычную полную Content preparation/build и новый review plan.
  Existing runtime/source conflicts сохраняют отказ Content protocol. Добавление
  тем/relations/URL идёт через существующий bootstrap/source planner; конфликтующее
  переименование старой catalog identity требует отдельного scoped решения.
- Повтор без новых inputs пропускает image/dependencies/schema/build/publication
  и проверяет совпадение сохранённого active release. Новая публикация не создаётся.
- DB живёт в собственном persistent volume. Credentials генерируются один раз
  в ignored var/compose. Подготовка/обновление/остановка их не ротируют.
  Отдельные schema/runtime roles не superuser; startup не создаёт пользователей.
- Dependencies, frontend caches/build и immutable release находятся в named
  volumes. Private plans и временные logs — только в ignored var/compose.
  Secrets и .git/var не доступны через Vite filesystem serving.

Не копируйте var/ или volumes автора. Checkout identity и уникальное имя Compose
project предотвращают неявное присоединение к другому локальному экземпляру.
Удаление volumes не входит ни в одну из четырёх операций.

## Альтернативный host-dev и собранный режим

[Host-dev инструкция](local-development-host.md) сохранена как альтернатива:
она требует собственные host Python/Node и отдельную private конфигурацию.
Его прежние результаты — история, не доказательство container-ready.
`scripts/lesson_server.py` сохраняет отдельный FastAPI/SSG просмотр без Vite.
В контейнерном prepare этот же настоящий gateway используется для обязательных
publication probes; production targets/Compose не заменены dev-конфигурацией.

## Границы контроля

Обычные npm/backend suites, typecheck, Playwright suites, check:dev, verify_repo,
source/docs/preservation gates не являются частью этих операций и не запускаются.
[Политика](frontend/testing-policy.md). Разрешённый конкретный clone/pull/update/
startup/HMR контроль и его точные SHA фиксируются отдельно в карточке MS-T002A.
До отдельного review/приёмки, решения о merge и запуска clone опубликованного
main вся MS-T002A не ACCEPTED; MS-T003 и production deploy не начинаются.
