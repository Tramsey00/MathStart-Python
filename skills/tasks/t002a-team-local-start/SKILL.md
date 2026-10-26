---
name: mathstart-t002a-team-local-start
description: Выполнить MS-T002A — единое контейнерное dev-окружение, воспроизводимый запуск из clone и обновление после pull перед переносом классов.
---

# MS-T002A — Подготовить воспроизводимый запуск после clone и передать baseline команде

> Решение пользователя 25.10.2026: автоматические прогоны временно выключены.
> Списки тестов ниже — план отдельно назначенной технической приёмки и история,
> а не разрешение запускать QA при реализации. Для обычной UI-правки — HMR и
> результат NOT_RUN_BY_USER_REQUEST. См. docs/frontend/testing-policy.md.

Зависимости: MS-T002. Это третья задача bootstrap после MS-T001 и MS-T002,
а не публичный deploy. Реализация выполняется только по отдельному поручению.

## Текущее решение 26.10.2026 — IN_PROGRESS после уточнения CHANGES_REQUESTED

Пользователь уточнил ожидаемый командный workflow: clone → подготовка → запуск;
далее commit/push → PR/merge → pull → обновление окружения → запуск новой версии.
Основной командный dev должен работать через Docker Compose. На компьютере
участника обязательны Git и Docker Desktop с Linux engine/Compose; отдельная
установка Python, Node/npm и PostgreSQL для этого пути не требуется.

Предыдущий host-dev результат READY_FOR_REVIEW на `9f4fce49b275a41bf27936e0f2e4d3b3360ad1ec`
сохранён ниже как история. Он не подтверждает готовность контейнерного dev.
Карточка снова требует реализации; существующий [PR #58](https://github.com/Tramsey00/MathStart-Python/pull/58)
продолжается в ui/ux, новый PR/Issue/ветка не нужны. Коммит 88f9d2c менял только
описание задачи. Затем получено отдельное явное поручение реализации и целевого
контроля; его исполнение отражено ниже, прежний host-dev result остаётся историей.

### Исполнение поручения 26.10.2026 — IN_PROGRESS

Отдельное поручение на реализацию и ограниченный контроль получено. Исходный
HEAD `88f9d2cd5c0193d8bca5a238d3a623dcde16864f`, ветка ui/ux, clean tree;
origin/ui/ux после fetch совпадал, origin/main — на 36 коммитов позади без
собственных новых коммитов. Чужих dirty edits на старте не было.

Добавлены dev.cmd → dev.ps1 prepare/start/update/stop, development target и
deploy/compose.dev.yaml. Vite/FastAPI переиспользуют существующий supervisor в
app-контейнере; DB отдельная, без host-порта. Dependencies/cache/build/runtime
хранятся в named volumes; private settings/review copies/logs — ignored var/compose.
Schema и Content используют прежние CLI/guards; обязательное утверждение
конкретного digest остаётся человеческим. NonInteractive оставляет review pending.
При неизменных inputs шаги пропускаются; update не меняет Git и не удаляет данные.
README/frontend README/AGENTS/architecture/local-development согласованы; host-dev
сохранён отдельно как альтернатива. Дизайн и authored lessons не менялись.

Контейнерный runtime пока НЕ проверен: Docker Desktop запущен, но pipe Linux engine
отсутствует, его status завершился по timeout; запрос пользователю на ручное
завершение запуска отправлен. Не перезапускались WSL/Docker, не удалялись чужие
containers/volumes. На старте 8131/8132 не слушались, исходный dev не останавливался.
Исторические результаты ниже не переносятся на эту реализацию. Статус не
READY_FOR_REVIEW до фактического разрешённого clone/pull/update/HMR контроля.

Независимый полный GitHub clone получен в C:/Projects/ms-t002a-compose-full-20261026:
HEAD `965df7c37285df46a7505acd7cd99c06fa65e255`, tree
`bc99dbff042fa596a184340354b139e2610c1fca`, tracked tree чистый. Partial clone
зависал на deferred blob fetch; остановлены только собственные Git clone процессы,
полный transfer с HTTP/1.1 завершился. Основная инструкция использует полный clone.
Первый реальный dev.cmd prepare -NonInteractive выполнен с PATH без python.exe
и node.exe. Windows launcher дошёл до Docker и остановился с exit=1 из-за
отсутствующего Linux engine pipe; создана только новая собственная private
конфигурация checkout, без containers/volumes/schema/Content. Лог — ignored
var/compose-control/prepare-attempt.log независимого clone. Это НЕ PASS контейнерного
workflow. Default Docker context также не имеет engine pipe. Пользователь
подтвердил готовность отдельно рассматривать конкретные планы; сами планы ещё
не созданы и не утверждены из-за недоступного engine.

Самопроверка кода добавила контроль неизменности applied migration files и отказ
start при pending review; это защитные исправления orchestration, не изменения
продукта ради проверки. Они будут получены тем же clone через обычный pull.

## Результат

Участник клонирует GitHub-репозиторий и запускает frontend, FastAPI и собственную
PostgreSQL в согласованном контейнерном dev-окружении. Один browser origin —
`http://127.0.0.1:8131`, React/CSS обновляются через HMR. Исходники редактируются
в обычном checkout и подключаются к контейнерам; изменения остаются видны Git.
Через GitHub передаются исходники, контент, locks и описание окружения. БД,
credentials, зависимости и собранные контейнеры не коммитятся. Локальные данные
каждого участника независимы и сохраняются при обновлении/остановке окружения.
После приёмки baseline находится в main; MS-T003 может выполняться командой.

## Входы

- Принятые MS-T001 и MS-T002, [архитектура](../../../ARCHITECTURE.md).
- Их bootstrap scope принят 25.10.2026 со статическим review и отложенными
  автопрогонами. Это открывает продолжение MS-T002A, но не заменяет проверку clone.
- [Локальный запуск](../../../docs/local-development.md), frontend/README.md.
- Существующие scripts/team_local.py, scripts/dev_server.py, deploy/Dockerfile,
  deploy/compose.yaml и корневой compose.yaml: проверить реальные зависимости
  и переиспользовать подходящую реализацию, не создавать второй Content protocol.
- deploy/RELEASE.md и deploy/RECOVERY.md — если для локального FastAPI/Content
  действительно нужен установленный release; production-разрешением они не служат.

## Объём работы

1. Подготовить контейнерный dev frontend/FastAPI/PostgreSQL с закреплёнными
   зависимостями. Сохранить существующую production-конфигурацию и отдельный
   просмотр собранного сайта. Добавлять dev targets/Compose по необходимости;
   не подменять основной runtime статическим prototype server.
2. Дать один документированный entry point с четырьмя операциями: первоначальная
   подготовка, запуск, обновление после pull, остановка. Конкретные имена выбрать
   при реализации. Entry point не требует host Python/Node/npm; не заставлять
   участника вручную повторять длинный набор pip/npm/schema/build команд.
3. Подготовка создаёт свои конфигурацию, БД и Content через существующие явные
   schema/publication протоколы. Обновление определяет необходимость установки
   locked dependencies, пересборки образов, миграций и новой подготовки Content
   после изменения уроков/каталога/URL. При отсутствии изменений шаги пропускаются.
   Обязательные preview/review/digest и publication guards сохраняются: команда
   может объединить шаги и запросить необходимое подтверждение конкретного плана,
   но не должна молча утверждать его. Обычный запуск не делает DDL, seed или publish.
4. Источники подключить из checkout для HMR и обычных commit/push. Решить права
   файлов и Windows mounts без необходимости править только внутренний слой
   контейнера. Существующий content.json сохраняет dev-only projection/refresh
   без публикации в БД; новые темы/URL готовятся явным обновлением окружения.
   API/private/legacy routes и WebSocket идут через один origin 8131 с корректными
   Host/Origin/cookies; внутренние сервисы не требуют открытия отдельных адресов.
5. Хранить БД в persistent volume, generated dependencies/builds отдельно от
   tracked source. Остановка/повторная подготовка/обновление не удаляют БД и
   пользователей, не ротируют существующие credentials без необходимости.
   Не копировать var/, БД или secrets автора. Ресурсы имеют понятного владельца;
   не затрагивать чужие контейнеры, volumes и защищённый acceptance stack.
6. Описать Git workflow: task branch → commit/push → PR → review/merge → pull
   нужной ветки → обновление окружения → запуск. Команда обновления не выполняет
   самостоятельно Git pull/reset/переключение ветки и не перезаписывает dirty tree.
   В ui/ux действует bootstrap-исключение; после передачи main — правила MS-T003.
7. По отдельному поручению выполнить только целевой контроль контейнерного пути
   из независимого GitHub clone без зависимости от host Python/Node и var/ автора:
   подготовка, запуск шести страниц с содержимым, assets/API/WebSocket, HMR
   React/CSS и content isolation, остановка/повторный запуск. Отдельно подтвердить
   цикл обновления из более раннего опубликованного candidate через pull и явную
   команду обновления: получить изменённые исходники/контент/зависимости/схему в
   пределах фактических изменений, сохранить локальные данные, повторное
   обновление без новых изменений ничего не публикует. Не придумывать продуктовые
   изменения ради проверки; непокрытые случаи честно перечислить. Общие suites,
   typecheck, Playwright, check:dev и gates не входят в этот контроль.
8. Обновить README, frontend/README.md, docs/local-development.md и актуальные
   инструкции агента: контейнерный путь становится основным только после
   реализации; host-dev при сохранении явно помечен альтернативой. Документировать
   prerequisites, первый/повторный запуск, pull/update, stop и сохранность данных.
   Windows — основной целевой хост; прочие ОС не объявлять проверенными без запуска.
9. Передать контейнерный запуск и обновление ветки ui/ux на review и приёмку
   готовности к merge. После отдельного решения пользователя слить bootstrap
   результаты ui/ux → main и опубликовать на GitHub. Повторить запуск из clone
   опубликованного main; передать точный commit и команды. Эта проверка завершает
   приёмку всей MS-T002A. До неё MS-T003 не начинается.

## Приёмка

Другой участник с Git и Docker запускает новую версию из чистого clone через
четыре простые операции, без host Python/Node/PostgreSQL и чужих локальных файлов.
Он редактирует checkout, видит HMR, может commit/push; другой участник получает
изменения через pull и обновляет окружение с сохранением собственной БД. Не нужно
переустанавливать проект с нуля или вручную согласовывать зависимости/Content.
Все нужные исходники и example-конфигурации находятся в Git, секретов в Git нет.
Отдельное review и человеческая приёмка контейнерного пути обязательны; прежний
host-dev PASS не считается его проверкой. Опубликованный main содержит принятый
baseline и отдельно проверен из clone. Это не production deploy.

## GitHub и ветка

Продолжать ui/ux и существующий PR #58, без нового Issue/PR/ветки. Исключение
действует только для MS-T001, MS-T002, MS-T002A. Merge main — после решения
пользователя. С MS-T003 каждая задача получает отдельные Issue, ветку от
origin/main без codex/ и PR. Не создавать все Issue заранее.

## История: частичное поручение 24.10.2026 — удобный dev-режим

Текущее состояние 25.10.2026: MS-T001/MS-T002 приняты в bootstrap scope.
HMR-часть уже реализована. Следующее поручение должно продолжить подготовку
независимого чистого clone, не повторять перенос уроков или разработку HMR.
До отдельного решения пользователя о merge результат передачи локального
запуска имеет статус READY_FOR_REVIEW, а вся MS-T002A остаётся незавершённой:
clone опубликованного main ещё впереди. Старые результаты ниже не являются
проверкой нынешнего candidate. Автоматические suites не возобновляются.

Пользователь поручил настроить live development сейчас, с учётом этой карточки.
Это разрешение на данную часть MS-T002A до полной приёмки MS-T002, а не разрешение
на merge, запуск следующего класса или приёмку всей MS-T002A.

Реализация: `scripts/dev_server.py`, frontend `npm run dev`. Browser origin
остаётся `http://127.0.0.1:8131`: Vite обслуживает React/HMR, внутренний FastAPI
слушает loopback 8132 и сохраняет public origin 8131. Private/legacy UI пока
проходят через FastAPI; их HMR рассматривается при реализации MS-T009/MS-T010.
Изменение public React/CSS не требует build/restart. Существующие React
content.json имеют dev-only read projection и browser auto-reload; это не
публикация Content и не изменение БД. Новые URL/темы/relations требуют явной
подготовки Content и перезапуска dev, а готовая версия — обычного release build.

Пока используется уже подготовленный собственный локальный экземпляр. Создание
окружения/БД/env из чистого clone, отдельное review, человеческая приёмка,
решение о merge и повтор clone опубликованного main остаются НЕ завершены.

## Результат dev-части 24.10.2026

Исходный HEAD `eb9d6e3216c9ef5c1acc773ab45815359ddae97d`; шесть уже имевшихся
незакоммиченных файлов предыдущих UI-правок сохранены. Проверенный код —
`282a1e6b98b7d12754f57755fed74837fc06da2c`, tree
`f58bb199fd117cd1918e907d3ed3eb680bd9423e`. Последующая запись результата — docs.

- `npm --prefix frontend run check:dev` — scoped PASS: четыре текущие страницы
  200, API через 8131, private shell no-store, legacy без Vite hydration,
  canonical alias с query; CSS/React обновляются без ручного reload, content.json
  вызывает auto-reload, опубликованный Content API остаётся без временных правок.
  WebSocket подключён к 8131; probe edits восстановлены byte-for-byte.
- `node node_modules/typescript/bin/tsc --noEmit` из frontend — PASS. Исправлен
  ранее существовавший undefined optional prop у LandingHeader явным default.
- `npm --prefix frontend run dev -- --stop` завершил оба собственных процесса
  и освободил 8131/8132; повторный запуск через npm run dev выполнен. Текущий
  dev оставлен запущенным. БД, active release и готовая сборка не изменены.

Первый smoke запросил будущий Topics API; финальный использует реализованный
ContentDelivery API. Неуспешный подготовительный запрос не называется PASS.
Полные npm/backend/managed suites, release build и cross-browser QA NOT_RUN.
Чистый clone, отдельное review, human acceptance, merge и clone main — PENDING.
Коммиты этого этапа используют [skip ci]; self-check не заменяет полную приёмку.

## Продолжение 25.10.2026 — независимая установка ui/ux

Исходный HEAD `868a6cdec0929935d2a218bbbc858e12e270cfb6`, clean tree,
ветка ui/ux; после fetch origin/ui/ux совпадал с HEAD, origin/main
`49b1240c495cb7c657cbb5ba9ea592bd9cb6c1d0`, отставание/опережение main: 0/29.
Чужих незакоммиченных изменений на старте не было.

Поручение разрешает только целевой контроль clone/install, шести текущих страниц,
assets/API/WebSocket, CSS/React/content refresh, остановки и повторного запуска.
Остальные suites/typecheck/check:dev/gates — NOT_RUN_BY_USER_REQUEST.

Добавлен scripts/team_local.py: собственные labelled PostgreSQL container/volume,
раздельные nonsuperuser schema/runtime roles, приватная генерация конфигурации,
явные schema preview/apply/check, обычные Content prepare-bootstrap/build/plan/
publish. Review digests обязательны; domain/publication guards не ослаблены.
Обычный startup не выполняет DDL/seed/publication и не создаёт пользователей.
README/frontend README/local-development согласованы. Дизайн/уроки не изменены.

### Findings первых репетиций

- Обычный GitHub clone завис на pack download. Собственный зависший процесс
  остановлен; HTTP/1.1 + --filter=blob:none завершились. История не shallow,
  недостающие historical blobs загружались с GitHub; локальный .git не копировался.
- `ec26d36181a2833a09a240ea366c61b0ded32acc`: install/schema/build завершились,
  publish отказал EDITION_CONFLICT, STAGED, db_committed=false, active=null.
  Alias `/materials/7-algebra-1` отсутствовал в DB edition; порядок derived
  redirects зависел от порядка registry/deliveries. В d805e15 alias добавлен
  в bootstrap plan, derived order стабилизирован. Guard точного равенства
  DB и immutable release не менялся.
- `6fcc3df50e45bd3fdd762bd3dafdee23fb3cc5b0`: новая установка/schema/build,
  затем PUBLIC_VERIFICATION_FAILED, db_committed=true, activation APPLIED,
  RECOVERY_REQUIRED. Реальный `/materials` возвращал 404: ordinary preparation
  в отличие от существующего build path сохраняла `/karta-sajta/` как canonical.
  В b379885 ordinary preparation получила уже принятый canonical `/materials`.
  Journal не сбрасывался, committed update не переигрывался. Две собственные БД
  неуспешных попыток остановлены, state/logs сохранены в ignored var/ их clone.
- Pip первой попытки: TLS EOF retries, затем locked install и pip check успешны
  без отключения TLS. Npm ci предупреждает об allow-scripts esbuild; первая
  реальная сборка прошла без approve-scripts и без изменения lock/глобальных settings.

- `b379885ae4af68976b59a3c878be7ab04a9e0620`: canonical исправлен, но cold
  HTTP guard снова отказал после активации. Наблюдаемое fenced recovery локализовало
  ReadTimeout на первом `/_content/index.json` (participant.py:254), без повторного
  domain commit. На том же прогретом gateway index отвечал 200 за 0,359 с,
  `/materials` — 200 за 0,735 с. Это измерение причины, не PASS установки b379885.
  В 9f4fce4 явная установка получила ограниченный exact-index warmup и обычный
  fenced resume только после проверки собственного durable committed/activated
  state. HTTP guards остаются 5 секунд. Третья репетиция также остановлена с
  сохранением состояния. Автоматического повторного domain update нет.

Дизайн, authored контент, media, принятые URL и доменные validators не изменены.

### Передача части до merge — READY_FOR_REVIEW, 25.10.2026

Проверенный GitHub clone: `9f4fce49b275a41bf27936e0f2e4d3b3360ad1ec`, tree
`fa98a52d327d8c4993d246dc617d985cb009f2fd`. Новый независимый каталог
`C:/Projects/ms-t002a-handoff-20261025` — только provenance этой репетиции,
не prerequisite запуска. GitHub origin, clean tracked tree до установки и после
восстановления probes. Нет local clone/hardlinks, копии var/, БД, private env,
cookies, venv, build или runner автора. Все локальные ресурсы созданы заново.
Последующая запись handoff меняет только docs/реестр/example, runtime code тот же.

Среда: Windows/PowerShell, Python 3.12.10, Node 24.19.0, npm 11.17.0,
Docker engine 29.8.1, PostgreSQL 16.15 (фактический server_version).
Node/npm входят в manifest engines; Docker/CI pins 24.21.0/11.19.0 отдельно
этим host-контролем не проверены. Locks не менялись. Использованы обычные
package/image caches; полностью холодная загрузка registries отдельно не проверялась.

Выполнены команды из docs/local-development.md:

- GitHub clone с HTTP/1.1, longpaths, LF, --filter=blob:none, ветка ui/ux;
  собственный .venv, pip install --no-deps -r requirements.lock, pip check
  (No broken requirements found), npm ci --no-audit --no-fund.
- team_local.py init → schema-preview → просмотр FRESH/0 tables/своей роли/DB
  → schema-apply по точному digest → physical schema check. Отдельные schema/
  runtime roles без superuser. Initial operator не создавался: для публичных
  страниц он не нужен; auth scope не проверялся.
- team_local.py content → prepare-bootstrap/immutable build/plan:
  279 страниц, 282 public URLs, 451 файл; просмотрены origin/previous=null/
  canonical и alias. team_local.py publish завершился **COMPLETE** с generation=1,
  после exact-index cold warmup 0,687 с и обычного resume. Domain commit один,
  все стандартные publication probes/guards включены. Первый cold отказ и
  успешный resume сохранены раздельно; warmup не засчитан как acknowledgement.
- npm --prefix frontend run dev: оба процесса этого clone, origin 8131,
  внутренний FastAPI 8132, .venv найден без сохранённого runner автора.

Целевой runtime-контроль — COMPLETE_SCOPED_LOCAL_START, не общий QA:

| Страница | Фактический результат |
| --- | --- |
| / | 200, заголовок «Математика для 5–10 классов», основной текст и общий chrome |
| /materials | 200, наполненный каталог 7 класса/алгебры, разделы и навигация |
| /materials/7-algebra-8 | 200, линейная функция: текст, таблица, график; 11 h2 в browser DOM |
| /materials/8-algebra-32 | 200, квадратичная функция: текст, график, формулы; 8 h2 |
| /materials/5-math-12 | 200, дроби: текст, схемы, MathML; 7 h2 |
| /materials/8-geometry-6 | 200, теорема Пифагора: текст, доказательства, SVG/MathML; 8 h2 |

Все шесть открыты в реальном in-app browser через dev 8131; проверены DOM,
заголовки и содержание, а не только пустая HTML shell. Наблюдались CSS/JS,
локальные Outfit/STIX, Vite connected, нет browser error logs. Явные запросы
к API grades и ContentDelivery, CSS module, Vite client и обоим fonts — 200.
WebSocket handshake ws://127.0.0.1:8131 — 101 Switching Protocols.

CSS custom property и React attribute изменились в открытой вкладке без ручного
reload. Существующий content.json subtitle вызвал auto-refresh; одновременно
опубликованный ContentDelivery.data остался равен исходному, marker в API
отсутствовал. Все три файла восстановлены byte-for-byte; marker исчез из DOM.

Штатный dev --stop освободил 8131/8132; своя БД остановлена/запущена, dev повторно
запущен без schema/build/publication. Шесть документов снова 200 с содержимым,
Vite подключился. Content fingerprint до/после одинаковый, users=0, tables=28,
publication journals=1. Проверочный dev/БД в конце остановлены, volumes сохранены.
Исходный dev основного C:/Projects/MathStart-Python восстановлен на 8131/8132
с прежней private config; acceptance stack не затронут.

Логи и JSON результата находятся только в ignored var/ соответствующих clone:
var/local/team/logs и var/t002a-control/targeted-results.json. Новых tracked
audit folders нет. Первый вывод ad-hoc summary столкнулся с cp1251; файл был
записан в UTF-8, вывод исправлен через Python -X utf8 без повторного runtime прогона.

Ограничения: in-app screenshot capture недоступен; DOM/resources/JS/HMR проверены,
но pixel/cross-browser/mobile/accessibility и функциональная приёмка всех
интерактивов не выполнялись. Сохранённый FastAPI режим использовался реальным
gateway в publication/probes; отдельного повторного полного browser прогона
собранного режима нет. Linux/macOS/WSL не проверены. Полные npm/test:full,
typecheck, Playwright suites, check:dev, verify_repo, source/docs/preservation
gates и backend suite — **NOT_RUN_BY_USER_REQUEST**. Production не проверен.

Самопроверка кода и целевой контроль завершены; отдельное review — PENDING,
human acceptance готовности локального запуска — PENDING, merge — NOT_PERFORMED.
Остаются отдельное review/fixes, человеческая приёмка части до merge, решение
пользователя о merge ui/ux → main, затем clone опубликованного main и его запуск.
Только после этого возможна приёмка всей MS-T002A и MS-T003. Сейчас вся MS-T002A
**не ACCEPTED**, MS-T003 не начата; production deploy не входит в поручение.
