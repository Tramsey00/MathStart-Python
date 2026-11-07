# Команды для образов target

Собирайте из корня Git. deploy/Dockerfile — единственный канонический файл сборки; корневой compose.yaml включает
deploy/compose.yaml. Исторический запуск Django доступен только в
закреплённой oracle-копии (docs/legacy-oracle.md). Эти targets содержат текущий
runtime и неизменённые зависимости из lock-файлов:

```text
docker build -f deploy/Dockerfile --target api -t mathstart-api:<candidate> .
docker build -f deploy/Dockerfile --target frontend-builder -t mathstart-frontend-builder:<candidate> .
docker build -f deploy/Dockerfile --target edge -t mathstart-edge:<candidate> .
```

Базовые digests соответствуют фактическим Python- и Node-образам, разрешённым при локальных
проверках сборки. Версия Python —3.12.15, Node —24.21.0, npm —11.19.0. API image запускается
с UID10001, импортирует target HTTP/publisher без Django/DRF и не содержит Node.
Отдельный builder выполняет обычную установку npm по lock-файлу и сборку React.
Оба образа исключают из build context локальные runtime credentials, browser caches, результаты проверок и
каталоги node_modules/build хоста.

Используйте проверенные public build inputs и пустой каталог output, явно принадлежащий этому запуску:

```text
docker run --rm --network none --mount type=bind,source=<absolute inputs>,target=/inputs,readonly --mount type=bind,source=<absolute owned output parent>,target=/output mathstart-frontend-builder:<candidate> --input-root /inputs --release-id <release> --manifest-digest <input digest> --receipt-digest <receipt digest> --output /output/site --origin <public origin>
```

Путь output `site` не должен существовать заранее. UID10001 должен иметь право чтения
inputs и записи в родительский каталог output. Builder проверяет неизменяемые
inputs, включает public HTML/head, assets и анонимную private shell и
создаёт output manifest, закреплённый внешним образом. В API не запускается Node server.

Для API нужны установленная target schema, durable publication authority и
соответствующие друг другу установленные деревья input/frontend. Храните приватные environment-файлы вне
Git. Обязательная конфигурация описана в `backend/READ_RUNTIME.md`; в
container задайте `MATHSTART_RELEASE_ROOT=/runtime/releases` и
`MATHSTART_PUBLIC_ARTIFACT_ROOT=/runtime/frontend`. Supply an explicit PostgreSQL
URL, доступный в выбранной принадлежащей запуску container network, signing keys, public
origin и начальную output-pin map (`{}` для подготовленных публикаций). Для существующих
legacy databases также нужны проверенный cutover digest и остановленная writer
role. Оба дерева должны указывать на одну и ту же зафиксированную release.

```text
docker run --rm --network <owned network> --read-only --tmpfs /tmp:rw,nosuid,noexec,size=32m --env-file <private runtime env> --mount type=bind,source=<absolute releases>,target=/runtime/releases,readonly --mount type=bind,source=<absolute frontend>,target=/runtime/frontend,readonly -p 127.0.0.1:18080:8000 mathstart-api:<candidate>
```

Образ запускает ASGI без migrations и access logs. Proxy headers
отключены. Команда readiness читает обычный локальный public gateway с
настроенным доверенным Host. Отсутствующая/повреждённая публикация, redirect,503 или
неполный документ дают UNREADY. Образ не добавляет public health API route и
не пишет в DB или файловую систему. Оставьте serving mounts доступными только для чтения; права записи в них принадлежат
отдельно запускаемому publisher.

Edge image запускает Nginx с UID101 на8080. Запускайте его только для чтения, со всеми capabilities
dropped and a writable `/tmp` tmpfs owned by101:101. All Nginx temporary paths
на `/tmp`. Access logs отключены. Edge направляет все запросы public HTML/static/
media и private API через authority gateway, сохраняя контракты cache
и ошибок. Он перезаписывает forwarded client/scheme headers, удаляет
недоверенные варианты и отключает повторные upstream-запросы, включая небезопасные POST.
Используйте выделенную internal network с API alias `api`, публикуйте только edge
и включайте Uvicorn proxy headers только для точного зарезервированного IP edge. Произвольный
client не должен иметь возможности подключиться к доверенной сети.

Для воспроизводимой disposable-проверки образов нужны уже собранные локальные API
и edge images, закреплённый образ PostgreSQL16 и сохранённые синтетические inputs
из `scripts/verify_target.py`. Скрипт определяет loopback HTTP port по
проверенному frontend output. Он отклоняет уже существующие output-каталоги и занятые
ports, создаёт уникальные помеченные DB/volume/networks, проверяет фактический HTTP/auth и
независимые TCP client budgets и удаляет только принадлежащие ему ресурсы:

```text
python scripts/verify_images.py --disposable --runtime-root var/image-check-<run> --source-runtime var/<managed-run>/runtime --artifact-root var/<managed-run>/artifact --api-image mathstart-api:<candidate> --edge-image mathstart-edge:<candidate>
```

Запускайте в target environment без Django. `--docker <executable>` позволяет указать
CLI вне PATH; `--pg-port` выбирает свободный loopback port (по умолчанию55442).
Receipt связывает фактические image IDs со снимками исходников до и после. Ошибка
assertion, изменение исходников или сбой очистки дают FAIL. Временные приватные env-файлы
удаляются в `finally`; не прерывайте владеющий ими процесс принудительным завершением.

По умолчанию edge использует HTTP для изолированной локальной проверки. Отдельные проверенные
release schema CLI, конфигурация Compose/TLS и команды оператора описаны в
`deploy/RELEASE.md`. Фактическая проверка пустого Compose/schema прошла, но без публикации система остаётся
UNREADY. Для HTTPS/cookie, восстановления физических DB/media/frontend
и совместимых переключений приложения имеются ограниченные фактические свидетельства, описанные в
`deploy/RECOVERY.md`. Установка из clean clone, физический возврат legacy и полная combined gate
успешно пройдены на принятом main3a290a46d991e22269a17dde41e39f0637576071; см. docs/maintenance.md. Ограниченные проверки image
не подтверждают окончательную приёмку и не дают разрешения на production deployment.
