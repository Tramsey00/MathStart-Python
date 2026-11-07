# Явные команды release и обслуживания

Эти команды являются операторскими инструментами для target runtime. Они не дают
разрешения на production. Сначала проведите репетицию на принадлежащих запуску временных данных. API при запуске никогда не
выполняет DDL, не создаёт начальные записи users/content и не принимает legacy history.

Используйте candidate images API/edge, собранные из той же копии кода и вывода builder по lock-файлу
output. Исторические Docker/Compose-файлы Django существуют только в закреплённом oracle.
Для текущего stack используйте `deploy/compose.yaml` (корневой Compose включает его). Необходимо явно задать уникальное
имя проекта, существующие именованные volumes PostgreSQL/public, отдельную свободную IPv4
subnet и точный IP edge, а также пути к приватным env/plan. PostgreSQL никогда не публикуется
на host, как и API. Только edge привязывается к заданному loopback port. Не подключайте
legacy и target writers к одним таблицам.

Bootstrap env PostgreSQL содержит `POSTGRES_USER`, `POSTGRES_PASSWORD` и
`POSTGRES_DB`. Runtime env содержит конфигурацию из
`backend/READ_RUNTIME.md`, используя host `db` в URL базы данных. Настройте
отдельную runtime role target; в рабочем
stack не используйте application superuser. Schema env задаёт отдельный `MATHSTART_SCHEMA_SIGNING_KEY` длиной не менее
32 случайных символа, а также `MATHSTART_DATABASE_URL` роли миграции,
переопределяющей runtime URL только в release service. Keys/DSNs остаются вне
Git, аргументов командной строки и логов. Сохраняйте оба существующих ключа verifier и привязку cutover
при восстановлении состояния identity.

Задайте эти переменные подстановки Compose в локальной shell или приватном
Compose env-файле; это пути и идентификаторы image/volume/network, а не пароли:

```text
MATHSTART_STACK
MATHSTART_API_IMAGE
MATHSTART_EDGE_IMAGE
MATHSTART_POSTGRES_ENV_FILE
MATHSTART_RUNTIME_ENV_FILE
MATHSTART_SCHEMA_ENV_FILE
MATHSTART_PLAN_DIRECTORY
MATHSTART_DATABASE_VOLUME
MATHSTART_PUBLIC_VOLUME
MATHSTART_INTERNAL_SUBNET
MATHSTART_EDGE_IP
MATHSTART_HTTP_PORT
```

Каталог plan должен быть доступен для записи UID10001. Serving volume paths:
`releases/<release>` and `frontend/<release>`, доступны для чтения UID10001; API
подключает их только для чтения. Publisher выполняет запись через отдельное явное подключение,
никогда не при запуске API. Сохраняйте input receipt, input/output manifests,
digest map и DB authority как единый набор release. Edge перенаправляет все public
static/media и private-запросы через этот authority; статические aliases, обходящие
ограничения publication, не допускаются.

До установки schema запустите только PostgreSQL. Остановите API, edge, всех publishers
и всех остальных клиентов базы на время обслуживания. Для принятия legacy отключите
and draв sole legacy writer role and remove incoming role memberships;
`NOLOGIN` alone does not drain existing sessions. Retaв pre-cutover schema,
снимок данных и role. CLI проверяет состояние role, все физические объекты baseline,
историю миграций и входные HMAC данных/sequences. Роли не изменяются.

```text
docker compose -f deploy/compose.yaml up -d db
docker compose -f deploy/compose.yaml run --rm --no-deps release preview --profile FRESH --plan-file /plans/schema.json
```

Для существующей поддерживаемой legacy schema используйте `--profile A`, `B` or `C` и
`--legacy-role <drained sole legacy writer>`. Preview выполняет повторяемое чтение
snapshot. Команда создаёт приватный подписанный plan и отказывается перезаписывать существующий
файл, выводит его SHA256. Проверьте код candidate, baseline/profile,
identity database/role, backup/drain и plan до применения по точному digest:

```text
docker compose -f deploy/compose.yaml run --rm --no-deps release apply --plan-file /plans/schema.json --maintenance --reviewed-plan-sha256 <reviewed digest>
docker compose -f deploy/compose.yaml run --rm --no-deps release check
```

Срок действия Plans —30 минут; они связаны с байтами кода/revision, DB/role OIDs,
остановленным legacy writer и полными входными schema/data/sequence. Неверный ключ, изменённые
данные, неизвестная история, другая DB/role, истёкший plan или подключённый другой
клиент database приводят к отказу до DDL. Fresh создаёт проверенную цепочку target и
метаданные разрешений auth. Adoption A/B/C сохраняет исходную историю Django,
IDs, существующие данные и Grade epoch; добавляет цепочку протокола target и заполняет
отсутствующие профили. Существующие публичные disposable schema wrappers сохраняют свои проверки.

Неопределённый COMMIT имеет статус `SCHEMA_REFUSED_OR_UNCERTAIN`, а не успех. Не повторяйте
операцию вслепую, не проставляйте отметки, не выполняйте downgrade, не откатывайте sequences и не восстанавливайте старую DB поверх записей
writes. Оставьте систему в режиме обслуживания и сверяйте schema/head, сохранённые строки, sequences,
role/cutover provenance и исходный snapshot. Команда `check` в режиме чтения подтверждает
только совместимость физической schema; она не подтверждает результат потерянного
предыдущего COMMIT. Пропуски sequence после неудачной транзакции допустимы.

Для новой неиспользованной target identity database явно создайте первого оператора
до запуска API/publishers. Это возможность работы staff/superuser,
а не автоматически созданная начальная учётная запись. Введите credentials в prompts без отображения введённого текста:

```text
python -m backend.users.operator --maintenance
```

Для автоматизации задайте приватные `MATHSTART_OPERATOR_USERNAME`,
`MATHSTART_OPERATOR_PASSWORD` и необязательный `MATHSTART_OPERATOR_EMAIL` в
окружении процесса и добавьте `--from-environment`. Их нельзя передавать как argv
и они никогда не выводятся. Команда использует сохранённые validators паролей
и hasher, создаёт профиль и отказывается работать при наличии user или legacy history,
session, pending receipt, состояния cutover или другого подключённого клиента. Она не может
сбрасывать пароль или принимать импортированного user. После неопределённого COMMIT выполните приватную сверку;
существующая identity блокирует повторное выполнение вместо перезаписи.

После установки/adoption завершите импорт identity и fenced публикацию контента
с помощью задокументированных `backend.users.cutover_cli` / `backend.content.publish`
команд и проверенных неизменяемых inputs. Для изолированной процедуры возврата legacy cluster до допуска имеются ограниченные
фактические свидетельства в deploy/RECOVERY.md; для возврата в рабочем окружении по-прежнему нужна отдельная
проверка блокировок/допуска. Не считайте совместимую пустую
schema установленным сайтом. Readiness должна оставаться UNREADY, пока не установлена соответствующая публикация content/frontend
и не выполнена reconciliation.

```text
docker compose -f deploy/compose.yaml up -d api edge
```

Edge запускается после старта API и может отдавать503, пока не установлена соответствующая release
is installed. It must be reachable for initial publication's actual HTTP probes;
ожидание API readiness до запуска edge создало бы цикл зависимости первой
публикации. Обычный authority gateway и readiness
продолжают отклонять неполную публикацию.

Для изолированной HTTPS-репетиции в Compose2.24.4+ можно применить
`-f deploy/compose.tls.yaml`. Задайте `MATHSTART_HTTPS_PORT` и приватный
`MATHSTART_TLS_DIRECTORY` с файлами `tls.crt` и `tls.key`, доступными для чтения UID101.
Задайте фактический public origin HTTPS до сборки release и настройки
API. Override заменяет HTTP port на loopback TLS8443 listener,
поддерживает TLS1.2/1.3, отключает session tickets и монтирует сертификаты только для чтения.
Внешние forwarded headers не считаются доверенными. Продление сертификата,
внешние ingress/firewall и доступность production требуют ревью оператора.
Реальная изолированная HTTPS/cookie-репетиция прошла с явно доверенным
тестовым loopback-сертификатом, отказом обычного клиента и полной проверкой CA/hostname.
Это не подтверждает deployment на публичном домене или владение сертификатом.
Реальная физическая репетиция backup/restore/application-switch и оставшаяся граница
возврата legacy cluster описаны в `deploy/RECOVERY.md`.

Воспроизводимая проверка пустого stack создаёт уникальный проект и помеченные
volumes, выполняет preview/apply/check в реальном контейнере, подтверждает отсутствие записи данных при запуске
и статус UNREADY без публикации, проверяет конфигурацию Nginx и удаляет
собственные ресурсы. Она не использует legacy DB, существующие volumes или port PostgreSQL хоста:

```text
python scripts/verify_deployment.py --disposable --runtime-root var/deployment-<run> --api-image mathstart-api:<candidate> --edge-image mathstart-edge:<candidate>
```

`scripts/verify_images.py` отдельно проверяет полностью установленную синтетическую release
и реальную аутентификацию через edge. Оба receipts являются ограниченными свидетельствами, а не итоговой
QA или приёмкой человеком.

## Независимая репетиция из чистого clone

Из target environment на Python3.12+ выполните эту временную проверку; Docker должен
быть доступен, как и свободные loopback ports55443/18125 (либо явно заданные `--pg-port`/`--port`):

```text
python scripts/verify_installation.py --disposable --runtime-root var/install-<new-run>
```

Verifier клонирует зафиксированный HEAD без hardlinks, создаёт новое окружение Python по lock-файлу
и собирает API/edge/Node-builder images из этой чистой
копии. Он использует обычные проверенные schema CLI, CLI начального оператора,
`prepare-bootstrap`, фактическую сборку Node по lock-файлу, plan/publish публикации, readiness,
сетевой вход/private admin shell и проверки source уроков. Требуются исходный ответ503,
публикация COMPLETE со всеми public HTTP assertions, повторный bootstrap без изменений,
чистый clone source и очистка. Синтетические fixtures никогда не подменяют
обычный путь установки. Используются только новые принадлежащие запуску помеченные Docker resources.

API и publisher используют общий именованный public volume; API монтирует его только для чтения, publisher —
для чтения и записи. Builder записывает отдельный неизменяемый output. Только для этой временной
loopback origin процесс publisher направляет socket точного public-origin
в фактический edge container; URL/Host, байты ответа, проверки cache и timeout5s
HTTP остаются без изменений. В рабочих deployment используется доступный public DNS.

Репетиция c205ef1 от18 October2026 прошла:279 страниц/282 public URLs/424 файлов,
813 фактических HTTP probes (максимум1.165s), обычный вход начального оператора,263 source
уроков, повторный preview без изменений, source guard и очистка PASS. Receipts:
`docs/acceptance/migration-execution/i02-verification/clean-install-03-20261018.json`
и соседний журнал public-probes. Это ограниченные свидетельства установки c205ef1,
не итоговая общая QA миграции. Предыдущий сбой install-02 сохранён;
исходное объяснение через bind-mount остаётся гипотезой, а не подтверждённой причиной.
