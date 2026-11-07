# Host-dev на Windows

Основной командный режим с 07.11.2026. Vite и FastAPI работают на Windows,
PostgreSQL — в Docker Desktop. [Полный Docker Compose](local-development.md#альтернативный-полный-docker-compose)
доступен как альтернативный режим.
Режимы используют отдельные данные и настройки. Перед переключением остановите
активный режим, чтобы освободить общий порт 8131.

После первой подготовки (шаги 1–3) на каждый день достаточно двух команд.

Используйте одну обычную папку проекта, например `C:\Projects\MathStart-Python`.
Название папки произвольное. `MathStart-host-check` использовалась для контроля;
создавать дополнительную копию для работы не нужно. Если коллега уже подготовил
проект в своей папке, он может продолжать там. Не перемещайте настроенный checkout
и не копируйте `var/`, venv или volumes между папками. Для другой папки выполните
первую подготовку заново с собственной БД. Старая установка останется сохранена.

```powershell
npm.cmd --prefix frontend run dev:host
# Из второго терминала того же checkout:
npm.cmd --prefix frontend run dev:host:stop
```

Команды ниже рассчитаны на опубликованный **main после merge PR #58**.
До этого merge candidate доступен в `ui/ux`; не используйте старый main для подготовки. Основной сайт — React + Content + FastAPI + PostgreSQL,
один browser origin **http://127.0.0.1:8131**. Это локальная установка, не production.

## Требования

- Windows, PowerShell, Git с long paths; короткий путь checkout.
- Windows `LongPathsEnabled=1`. Python копирует файлы в длинные staging-пути.
  `git config core.longpaths true` действует только на Git. До подготовки проверьте
  `Get-ItemPropertyValue -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled`.
  Если значение отличается от `1`, в PowerShell администратора выполните
  `New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled -Value 1 -PropertyType DWord -Force`
  и перезагрузите Windows. Host-dev проверяет настройку до запуска БД;
  init/content/publish — до соответствующих изменений. Скрипты не меняют реестр.
- Python **3.12** с venv/pip (`python --version`). Если работает launcher,
  первую команду venv можно заменить на `py -3.12 -m venv .venv`.
- Node **24.x**, npm **11.x** по engines frontend/package.json. Docker/CI
  закреплены на Node 24.21.0/npm 11.19.0; фактически проверенные локальные
  версии записаны в карточке MS-T002A.
- Docker Desktop с работающим Linux engine; Compose этому host-dev пути не нужен.
  PostgreSQL image закреплён digest из deploy/compose.yaml.
- Доступ к GitHub, PyPI, npm и Docker registry при первой установке.
- Свободные loopback 8131/8132 и 55449 для своей БД. Последний можно изменить
  через `init --pg-port 55450`. Не завершайте неизвестных владельцев портов.

Runtime packages закреплены requirements.lock и вложенными locks; frontend —
package-lock.json. Django/DRF и oracle не нужны. Assets/шрифты/curriculum берутся
из Git. Не копируйте чужие var/, БД, .env, cookies, runner или готовые builds.

## 1. Clone и locked установка

В PowerShell из родительского каталога (выберите своё новое имя папки):

```powershell
git -c http.version=HTTP/1.1 -c core.longpaths=true -c core.autocrlf=false clone --branch main --single-branch https://github.com/Tramsey00/MathStart-Python.git MathStart-Python
Set-Location MathStart-Python
git config core.longpaths true
git config core.autocrlf false
git config http.version HTTP/1.1
git rev-parse HEAD
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --no-deps -r requirements.lock
& .\.venv\Scripts\python.exe -m pip check
npm.cmd --prefix frontend ci --no-audit --no-fund
```

Активация venv не требуется, execution policy PowerShell не мешает запуску.
Используйте полный clone с HTTP/1.1: некоторые build inputs читают точные
historical Git pins.

Если у вас уже есть рабочий clone, начните с перехода в него и проверки ветки/SHA.
Clone и повторная установка готовых зависимостей не нужны. Создайте `.venv`, если
его ещё нет. Новому host-dev в существующей папке нужны шаги 2–3.
Остановите прежний dev перед первой публикацией и запуском, освободив 8131/8132.
Новая установка хранит runtime settings в `var/local/team/private-env.json`,
сохраняя старые настройки preview в `var/local/lesson-preview/private-env.json`.
Установки коллег, созданные до этого изменения, продолжают читать прежний файл
по своей installation.json; вручную переносить настройки не нужно.

## 2. Своя БД и явная schema

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py init
& .\.venv\Scripts\python.exe scripts/team_local.py schema-preview
```

Init создаёт уникальный labelled Docker container и persistent volume,
PostgreSQL только на 127.0.0.1:55449, отдельные nonsuperuser schema/runtime roles,
случайные пароли и ключи в ignored var/. Пароли не передаются в argv и не
печатаются. Application tables и пользователи пока не создаются.
Runtime не владеет DDL; отдельная schema-role используется явными CLI подготовки.

Просмотрите локально var/local/team/schema.json: profile=FRESH, table_count=0,
ожидаемые target_head и database/role binding. Private plans/config не публикуйте.
Preview печатает REVIEW_REQUIRED: plan SHA256 … . Подставьте digest за 30 минут:

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py schema-apply --reviewed-plan-sha256 <SCHEMA_SHA256>
```

Это обычные backend.release_migrate preview/apply/check с signature, maintenance,
code/DB identity и expiry guards. Явный шаг устанавливает schema и permission
metadata. Пользователь/operator для публичных страниц не требуется и автоматически
не создаётся. Если позже нужен staff, initial operator создаётся отдельно по
[release runbook](../deploy/RELEASE.md), до появления других пользователей.

Повторный `schema-preview` не перезаписывает существующий `schema.json` и может
отказать с `FileExistsError`. Для применения используйте исходный просмотренный
план, пока он действителен. Если план истёк, сохраните его и согласуйте новый.
После успешного `APPLIED` и `CHECKED` переходите к контенту. Не повторяйте FRESH
установку поверх уже установленной схемы. Фраза `does not reconcile an uncertain
prior apply` — постоянная часть вывода check; сама по себе она не означает сбой.

## 3. Content prepare → build → plan → publication

Остановите свой dev перед первой публикацией: временный FastAPI gateway
использует 8131 для обязательных HTTP publication probes.

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py content
```

Команда вызывает обычный prepare-bootstrap из tracked source точного HEAD,
frontend.build_public с verified immutable input/receipt digests и publication
plan. Собирается весь текущий Content, включая legacy-страницы и шесть новых
React-страниц. Suites/typecheck/source gates не запускаются; штатные доменные
валидаторы и integrity/publication guards сохранены. Build занимает несколько
минут, вывод в var/local/team/logs/.

Просмотрите var/local/team/publication.json: initial install, previous=null,
origin http://127.0.0.1:8131, ожидаемые release/changes. Content печатает digest:

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py publish --reviewed-plan-sha256 <PUBLICATION_SHA256>
```

Publish запускает временный обычный FastAPI gateway, выполняет fenced
backend.content.publish publish с обязательными HTTP probes, ждёт COMPLETE и
останавливает только свой временный процесс. Нет synthetic activation,
отключения guards, hosts override или чужой БД. До публикации runtime UNREADY.
Только этот явный шаг публикует Content в БД.

На Windows холодная полная валидация release может превысить HTTP timeout первого
publication probe. Setup допускает одно ограниченное продолжение: читает durable
status, требует свой operation/owner/generation, db_committed=true, activation=APPLIED,
RECOVERY_REQUIRED/PUBLIC_VERIFICATION_FAILED и ожидаемый active release. Затем
продлевает свою lease, прогревает read cache запросом с timeout 60 секунд и точным
сравнением immutable index, снова продлевает lease и выполняет обычный CLI resume.
Все HTTP guards publisher остаются с timeout 5 секунд; domain commit не повторяется.
Warmup сам по себе не является acknowledgement. Успех — только phase COMPLETE
после всех обычных probes. Первый отказ и resume сохраняются отдельными logs.
Другое/неизвестное состояние, mismatch или повторный отказ останавливают установку.

Init/schema/content — первая установка: существующие файлы не перезаписываются.
Не повторяйте apply/publish вслепую после ошибки/неопределённого COMMIT: состояние
и private logs сохранены; status/recovery — по [RELEASE](../deploy/RELEASE.md)
и [RECOVERY](../deploy/RECOVERY.md). Повтор bootstrap поверх данных не нужен.
При изменении schema/состава/URL контента нужна отдельная подготовка release.

## 4. Ежедневный старт и остановка

```powershell
npm.cmd --prefix frontend run dev:host
```

Дождитесь сообщения «Host-dev готов». Команда запускает свою PostgreSQL,
Vite и FastAPI, затем ждёт HTTP 200 от главной и API классов через 8131.
Терминал остаётся занят и показывает логи. Откройте:

- http://127.0.0.1:8131/
- http://127.0.0.1:8131/api/v1/grades/
- http://127.0.0.1:8131/materials/7-algebra-8

Vite обслуживает React/HMR WebSocket на 8131, внутренний FastAPI — loopback 8132.
API/assets/private/legacy идут через same-origin proxy с исходными Host/Origin/
cookies. FastAPI автоматически перезапускает рабочий процесс при изменении
`backend/**/*.py`. Vite и адрес 8131 остаются доступны. Запрос к API в момент
перезапуска может потребовать повторения.

Обычный startup читает release, готовит read-only dev view и запускает процессы.
Он не делает DDL, seed, создание пользователей, build, publication или tests.
Vite не получает private значения из JSON.

React/CSS обновляются через HMR без build. Существующий React content.json
вызывает reload и dev-only projection с валидацией identity/schema: БД,
опубликованный API и установленный release не изменяются. Новые URL/темы/relations/
renderer_version требуют явной подготовки Content. Private/legacy UI пока
используют собранную версию; их HMR не входит в этот этап.

Остановите режим через Ctrl+C или из второго PowerShell того же checkout:

```powershell
npm.cmd --prefix frontend run dev:host:stop
```

Supervisor завершает Vite и FastAPI и останавливает свою PostgreSQL. Volume,
схема, Content и настройки сохраняются для следующего запуска. При ошибке
до готовности supervisor останавливает только БД, которую запустил сам.
Если терминал был принудительно закрыт и своя БД осталась работать, используйте
`& .\.venv\Scripts\python.exe scripts/team_local.py db-stop`.
Логи операций Docker — в `var/local/team/logs/`. Если 8131 или 8132 занят,
остановите известный вам режим его штатной командой.

## После git pull

Сохраните свои правки и выполните `git pull --ff-only origin main`.

- Обычные изменения React/CSS и Python в `backend/` подхватываются в работающем
  режиме. Если окружение остановлено, выполните `dev:host`. Для изменений
  launcher, Vite config или настроек запуска перезапустите режим.
- Если изменились Python locks или frontend package/lock, остановите режим и
  повторите соответствующую locked установку из шага 1.
- Если изменилась схема или опубликованный состав Content (каталог, URL,
  связи, renderer или release inputs), нужна явная подготовка совместимой схемы
  или Content по [регламенту](../deploy/RELEASE.md) с review точного SHA256.
  Шаги 2–3 описывают первую установку. Для существующих данных используйте
  предусмотренный upgrade/publication workflow и новый план. На время
  подготовки остановите dev и поднимите только свою БД командой
  `& .\.venv\Scripts\python.exe scripts/team_local.py db-start`. После подготовки
  обычный start прочитает обновлённую установку.

## Собранная FastAPI-версия без Vite

После остановки dev, при работающей своей БД:

```powershell
& .\.venv\Scripts\python.exe scripts/lesson_server.py
```

Адрес тот же 8131, установленный immutable Content/SSG release; Node runtime
не нужен. Остановка Ctrl+C. Возврат к HMR — `npm.cmd --prefix frontend run dev:host`.
Режимы не работают одновременно.

## Статус командного режима

Ежедневный цикл проверен на подготовленном checkout Windows. Пользователь сообщил
об успешном запуске у Владимира (точный SHA a44c5f7, с включением длинных путей и
штатным восстановлением публикации) и Ильи (SHA не сообщён). Эти сообщения
подтверждают запуск, но не дополнительные HMR/авторелоад или полные suites.
Отдельное review завершено, PR #58 объединён с main 07.11.2026. Независимый
GitHub clone опубликованного main прошёл первую подготовку по утверждённым планам,
просмотр трёх адресов/урока с графиком и stop/restart с сохранением данных/config.
Повторный старт занял 25,000 с при работающем Docker Desktop. Человеческая приёмка
новых результатов MS-T002A остаётся отдельной.
Замеры и точный проверенный код указаны в [карточке MS-T002A](../skills/tasks/t002a-team-local-start/SKILL.md).

