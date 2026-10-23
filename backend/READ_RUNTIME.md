# Текущий runtime публичных страниц и идентификации

Обычная ASGI factory объединяет публичные releases, `frontend.rendering.PublicRenderer`,
сервисы identity/session на PostgreSQL и React-формы аккаунта/staff. Явная
тестовая factory `create_public_app` сохраняет режим только для чтения по умолчанию, если не передан сервис identity.
Для обычных путей публикации/восстановления и свежей установки имеются ограниченные
фактические свидетельства для соответствующих SHA. Текущий candidate проходит QA в собственной CI;
приёмка человеком остаётся отдельным решением. Проверки Django запускаются только из
[pinned oracle](../docs/legacy-oracle.md). Текущая конфигурация/архитектура и соответствие исторических
документов описаны в [docs/target-runtime.md](../docs/target-runtime.md).
Приведённые ниже синтетические команды — QA fixtures; для обычной установки используется
[deploy/RELEASE.md](../deploy/RELEASE.md).

Установите `backend/infrastructure/http/requirements.lock` в target environment.
Для тестов также установите `backend/tests/v04/requirements.lock`. Ни один из файлов не требует
Django. Legacy golden oracle остаётся в отдельном окружении.

Запускайте из корня основного репозитория. Задайте следующие переменные окружения, не
выводя их значения:

- `MATHSTART_DATABASE_URL`: подключение PostgreSQL/psycopg к новой пустой
  синтетической DB с именем `test_ms7_mig_v01_<unique suffix>`.
- `MATHSTART_DISPOSABLE=1`.
- `MATHSTART_HTTP_SIGNING_KEY`: временный приватный signing key, сохраняемый на
  время синтетической сессии; необязательный JSON-массив `MATHSTART_HTTP_SIGNING_FALLBACK_KEYS`.
- `MATHSTART_PUBLIC_ORIGIN`: точный HTTP origin, например локальный port8121.

```text
python -m backend.content.synthetic_setup prepare --disposable --runtime-root var/i02-runtime --release-id i02-public-<unique suffix> --source-sha <reviewed commit>
```

Команда проверяет имя и пустоту DB до резервирования принятого маркера V01
применяет неизменённые свежие Alembic migrations, дважды выполняет bootstrap и сравнивает
сохранённую source edition, создаёт только синтетические fixtures staff/group/media/session
а затем собирает неизменяемые public inputs в `var/i02-runtime/releases/`.
Файл `prepare-result.json` содержит digests и пути release/input/receipt.
`private-staff-cookie.json` содержит синтетическую непрозрачную cookie: оставьте файл в ignored-каталоге,
не выводите содержимое и не прикладывайте его. Это тестовый fixture, а не endpoint входа.

Соберите React output из тех же свежих inputs с помощью `frontend.build_public`.
Используйте точное значение `MATHSTART_PUBLIC_ORIGIN`; сохраните digest доверенного output manifest.
Затем выполните:

```text
python -m backend.content.synthetic_setup activate-initial --disposable --runtime-root var/i02-runtime --release-id <release> --receipt-digest <trusted input receipt digest> --artifact-root <new frontend output> --artifact-digest <trusted output manifest digest>
```

Эта разовая синтетическая настройка проверяет полный перечень input/output и
DB edition перед установкой начального descriptor в одной SQL-транзакции.
Она отклоняет уже существующий authority публикации. Это не publish/retry/takeover,
не заменяет активную release и не является свидетельством production cutover.

Для read server задайте:

- `MATHSTART_RELEASE_ROOT` равным `var/i02-runtime/releases`.
- `MATHSTART_PUBLIC_ARTIFACT_ROOT` равным корню frontend output или родительскому каталогу
  per-release subdirectories.
- `MATHSTART_PUBLIC_ARTIFACT_DIGESTS` равным доверенной JSON-карте соответствия release ID
  и SHA256 output manifest.

```text
python -m uvicorn backend.content.public_runtime:application --factory --host 127.0.0.1 --port 8121 --no-access-log --no-proxy-headers
```

Публичные документы/API/assets закреплены за авторитетной DB release. Явные native
account/staff URLs предоставляют только проверенную анонимную shell с private/no-store;
их API-чтения и мутации проверяют opaque session, срок действия/отзыв/
auth-hash и текущие разрешения DB. Мутации проверяют CSRF и validators.
Скомпилированные UI-файлы проверяют закреплённый committed descriptor, доверенный output manifest
и hash запрошенного файла; публичный контент дополнительно проверяет полный source release.
Прямые команды ASGI отключают proxy headers. Конфигурация target Compose
использует два worker и доверяет только зарезервированному IP edge; edge
перезаписывает forwarded client/protocol headers и удаляет альтернативные заголовки.
Не доверяйте произвольным proxy peers и не открывайте этот API port напрямую.
Приватные staff-документы получают snapshot представления только с логическими значениями из
текущих разрешений DB. Он скрывает недоступные действия, сохраняет объединённые разрешения на создание User
и элементы управления Content только для чтения; каждый API всё равно проводит
собственную авторизацию. Snapshot не содержит user IDs, PII или credentials и никогда не
записывается в public artifact. Неизвестные
staff URLs по-прежнему возвращают404. Сгенерированные assets frontend должны находиться в доверенном output
manifest. Повреждённые/отсутствующие файлы приводят к отказу. Постоянного Node server нет.

Наблюдатель состояния публикации для staff сообщает о неизменяемой активной release,
зафиксированной DB edition и долговечной ожидающей операции, включая возможность takeover
и recovery. Authority проверяется до и после формирования представления;
конфликтующие данные или повреждённые артефакты приводят к отказу. Чтение не захватывает и не продлевает
lease publisher. Неопубликованные страницы сохраняют свои DB identity и возвращают
null для digest/path публичной страницы.

Для браузерных тестов укажите `MATHSTART_STAFF_COOKIE_FILE` как путь к приватному cookie
файлу в ignored-каталоге. Для целевых PG-тестов session используйте ту же среду DB/signing/cookie:

```text
python -m unittest backend.tests.v04.test_read_runtime -v
```

После проверок остановите принадлежащий вам процесс Uvicorn. Согласно журналу запуска сохраняйте или удаляйте только
новую зарезервированную синтетическую DB с указанным именем и соответствующее поддерево var.
Корневая portable verification/CI отвечает за общий lifecycle и итоговые запуски с точным SHA.

Для существующих команд проверки контента теперь есть target adapters:

```text
python -m backend.cli check-lesson-sources --source-root . --all
python -m backend.cli check-lesson-sources --source-root . --slug <existing lesson slug>
python -m backend.cli check-site-integrity --static-root static --media-root site_content/media --report-root var/inspection-reports
python -m backend.cli check-content-quality --origin http://127.0.0.1:8121 --report-root var/inspection-reports
```

Они используют явно настроенную target DB. Проверка урока сравнивает все
метаданные урока, HTML, CSS, JS и identity каталога с DB; одна команда `check-sources`
проверяет только исходные файлы. Integrity проверяет страницы текущей DB, redirects,
ссылки и зарегистрированные media относительно указанных storage roots. Quality
проверяет реальные HTTP-ответы и использует сохранённую проверку авторских материалов/SVG/anchors;
она отклоняет redirects и пустой опубликованный перечень. Требуется запущенный
target origin; fixture HTTP tests подтверждают связь команды, а не публичное
принятие отрисовки. Storage roots должны соответствовать реальному deployment; путь media
выше указан для синтетического seed.

Проверки PostgreSQL используют повторяемую транзакцию только для чтения. Quality/integrity
также создают или заменяют JSON-отчёт в явном report root, в том числе
когда найденные проблемы приводят к ненулевому коду выхода. Они не предлагают вводящий в заблуждение флаг dry-run.
Отсутствие tools или storage, несовпадение исходников, HTTP-ответ не 200 и ошибочный HTML приводят к сбою;
о незадействованных зарегистрированных media сообщается без критической ошибки, сохраняя
существующую политику команд. Файлы ограничены настроенными storage roots.
Эти адаптеры проверки не выполняют publication или cutover. Отдельная
`index-lessons` команда записывает только явно выбранный INDEX.md output.

Очистка identity записывает естественное истечение session как `DETACHED`, а истечение окна replay — как
`EXPIRED`, не удаляя identity receipt или response. Отзыв является
окончательным, в том числе при инвалидации независимых sessions по auth-hash. Повтор регистрации
принимается с уже привязанной session владельца или исходным доказательством bootstrap;
после явного входа того же владельца это исходное доказательство может повторно привязать отсоединённый
receipt без создания другой session. Одного ключа receipt или входа владельца
недостаточно, чтобы выбрать анонимную область. Конкурентные повторные привязки старой эпохи завершаются отказом.
Импорт приватных данных legacy при cutover реализован в `backend.users.cutover_cli`.
Команда проверяет фактический PostgreSQL NOLOGIN единственной настроенной legacy writer role,
отсутствие sessions и участников role; он никогда не меняет роли и не удаляет старые
sessions/receipts. Сначала оператор должен остановить старый runtime, отозвать
login и членство writer в ролях, а также сохраняет исходный signing keyring.
Это явная операция обслуживания; production cutover не выполнялся.

После настройки окружения target database/signing/origin задайте
`MATHSTART_LEGACY_WRITER_ROLE` как эту legacy role и используйте новый UUID:

```text
python -m backend.users.cutover_cli preview --checkpoint-id <uuid> --plan var/cutover-plan.json
python -m backend.users.cutover_cli apply --plan var/cutover-plan.json
```

Preview устанавливает эксклюзивный identity barrier и создаёт приватные HMAC digests
без изменений DB. Apply повторно проверяет происхождение role и весь снимок
identity, сохраняет bytes/scope/digests/results receipt, импортирует привязанные к владельцу
проверенные факты legacy session, отсоединяет подходящие bridges, отзывает target sessions
и атомарно сохраняет один checkpoint. При неоднозначных сопоставлениях или изменении исходных данных
импорт отклоняется. Храните plan приватно. Повторное применение уже завершённой операции выполняется только для чтения,
даже после повторной привязки target; другой checkpoint запрещает запись.

Настройте возвращённый checkpoint digest как `MATHSTART_IDENTITY_CUTOVER_DIGEST`
для каждого target runtime, сохранив `MATHSTART_LEGACY_WRITER_ROLE`. Identity,
записи staff и lifecycle используют общий import barrier и проверяют долговечное происхождение данных;
неизвестные checkpoints, повторно включённый writer или новые членства role возвращают503.
Для новых target без legacy sessions/осиротевших receipts checkpoint не нужен.

Старый `sessionid` никогда не аутентифицирует target. Один явный вход по паролю
его точного владельца может использовать импортированную приватную привязку F для создания новой
opaque target session. Затем повтор регистрации воспроизводит только исходный receipt
под текущим authority S. Одни только login/key не могут выбрать старую область
bootstrap. Terminal bridges остаются terminal; конкурирующие входы F из одной наблюдаемой
эпохи не могут создать две sessions. Восстановление по исходному доказательству B остаётся доступно
с действующими проверками password/owner/digest/retention. Импортированные отсоединённые
bridges без линии target также отзываются при смене пароля target.
При деактивации staff отзывается тот же полный набор owner bridge/session до того, как
может быть выполнена повторная активация; она не восстанавливает отозванные права.
Эти ограниченные проверки не являются полной репетицией migration/cutover.

Внутренняя `backend.content.publication.PublisherAuthority` теперь реализует
слот PostgreSQL P1 для pending, lease владельца/поколения, takeover, факт фиксации домена,
активацию descriptor, reconciliation и acknowledgement. Её участник должен
предоставлять проверенную подготовку content/artifact, краткие проверки/обновления DB edition и
public probes; fixture participant не является production content publisher.
Staging/probes выполняются вне row locks. Их receipts связывают operation, owner, fence,
plan и release identity и принимаются только при той же действующей lease.
Итоговые условные SQL-проверки используют время DB и откатывают сброшенные изменения домена
при истечении срока. Pending освобождается только в состоянии COMPLETE или после доказанного FAILED_PRECOMMIT. Нет
активного указателя в файловой системе и очистки путей, которыми операция не владеет.

`backend.content.editions` предоставляет точные fingerprints семи таблиц контента и защищённые подготовленные обновления до/после, сохраняя IDs и timestamps.
Он отклоняет таблицы auth, изменения primary key, повторные patches и устаревшие строки;
принимает явно заданные предложенные IDs для нового контента и никогда не удаляет контент.
Подготовка не расходует sequences; зафиксированные inserts монотонно продвигают sequences.
Прерванные транзакции PostgreSQL могут оставлять обычные пропуски sequence. Эти внутренние уровни покрыты
реальными PostgreSQL-тестами crash/race/rollback. Конкретный participant подготовки content/SSG
и операторский CLI теперь интегрированы. Начальная синтетическая активация
остаётся отдельным fixture. Регистрация source, новые предложенные IDs и bootstrap всего сайта
используют того же fenced participant. Production cutover и итоговая
приёмка публикации ещё не выполнялись.

Подготовьте и опубликуйте исходные данные из проверенного Git commit:

```text
python -m backend.content.publish prepare-sources --source-root . --source-sha <full reviewed SHA> --release-id <unique release> --all --input-root var/publication-inputs --changes var/prepared-edition.json
python -m frontend.build_public --input-root var/publication-inputs --release-id <unique release> --manifest-digest <input manifest digest> --receipt-digest <input receipt digest> --output var/publication-output/<unique release> --origin http://127.0.0.1:8121
python -m backend.content.publish plan --changes var/prepared-edition.json --plan var/publication-plan.json --input-root var/publication-inputs --output-root var/publication-output/<unique release> --output-digest <trusted output manifest SHA256> --release-root var/serving/releases --artifact-root var/serving/frontend --origin http://127.0.0.1:8121
python -m backend.content.publish publish --plan var/publication-plan.json --key <stable unique operation key> --owner <stable owner UUID> --input-root var/publication-inputs --output-root var/publication-output/<unique release> --release-root var/serving/releases --artifact-root var/serving/frontend
python -m backend.content.publish status
```

Target DB уже должна содержать проверенную schema. `prepare-sources` требует
существующих родительских объектов каталога; команда может зарегистрировать соответствующую существующую тему или предложить
новую тему и строку публикации. Инициализация каталога/media/redirect всего сайта
выполняется через `prepare-bootstrap` ниже.
Подготовка source читает единый повторяемый snapshot и сохраняет PK/FK/created_at.
Зафиксированный updated_at получают только изменённые строки; принадлежность source и digests не позволяют
изменять runtime-данные. Все публикуемые sources/assets должны соответствовать candidate.
PostgreSQL упорядочивает VALUES-проекцию сохранённого каталога, сохраняя
фактическую collation, без записи строк или выделения sequences. Команда создаёт
неизменяемые input-файлы и эксклюзивный файл подготовленной edition; она не захватывает
и не активирует публикацию. `--dry-run` проверяет source/selection/conflict,
не создавая файлы, не захватывая gate, не вставляя строки и не продвигая
sequences. Предложенные IDs становятся фактическими только в защищённой транзакции домена.
Коллизии identity source/path, отсутствующие родительские записи каталога и изменения runtime приводят к закрытому отказу.
Существующие PKs, FKs и значения created_at сохраняются.

Output сборки независимо проверяется до того, как `plan` запишет эксклюзивный файл plan.
Связанный файл edition отклоняет расхождения между подготовкой и планированием.
`publish` захватывает durable gate, выполняет staging в каталогах operation/owner/generation,
устанавливает только отсутствующие или побайтно совпадающие файлы, один раз фиксирует обновления домена и
переключает descriptor только после полной проверки установленных байтов. Worker lease
использует собственные sessions при staging/probing. Фактический HTTP проверяет текущую
release identity, каждый публичный документ/alias и проверенный asset, asset ETags,
sitemap/robots, redirects и удалённые URL. Неудачные probes сохраняют pending recovery
и возвращают ненулевой код. Активного указателя в файловой системе или serving process Node нет.

В каталоге serving frontend используйте отдельные подкаталоги для каждой release. Сохраняйте там же начальный
artifact под его release ID; не помещайте старый manifest для единственного output в родительский каталог будущих releases. Новые output pins читаются
из соответствующего зафиксированного/применённого journal plan вместе с его digest;
отрисовка ранее выбранной release никогда не выбирает latest повторно. Env pin
map сохраняется для явно доверенных старых начальных artifacts и может иметь значение `{}`
если все releases используют подготовленный publisher.

Чтобы снять с публикации существующую страницу, замените `--all` на `--slug <slug>` и добавьте
`--kind unpublish` в команды `prepare-sources` и `plan`; вместо `publish` выполните `unpublish`.
Следующая сборка исключит её HTML/запись каталога/sitemap и сохранит
строку DB и исторические releases. Явные redirects сохраняют обычный
приоритет. Успешная очистка cache не предполагается; публичные документы повторно проверяются в
Python gateway, публичные assets используют content ETags.

Команды восстановления/управления используют operation UUID и наблюдаемое/текущее поколение
из `status`; все ошибки очищаются, возвращается ненулевой код:

```text
python -m backend.content.publish resume --operation-id <operation> --owner <current owner> --generation <current generation> --input-root var/publication-inputs --output-root var/publication-output/<release> --release-root var/serving/releases --artifact-root var/serving/frontend
python -m backend.content.publish recover --operation-id <operation> --owner <new recovery owner> --generation <observed expired generation> --input-root var/serving/releases --output-root var/serving/frontend/<release> --release-root var/serving/releases --artifact-root var/serving/frontend
python -m backend.content.publish renew --operation-id <operation> --owner <current owner> --generation <generation>
python -m backend.content.publish surrender --operation-id <operation> --owner <current owner> --generation <generation>
python -m backend.content.publish abort --operation-id <operation> --owner <current owner> --generation <generation> --release-root var/serving/releases
```

Для takeover нужны истёкшая/добровольно освобождённая lease и точное наблюдавшееся поколение.
После commit восстановление всегда продвигается вперёд и согласует фактический descriptor;
исправление домена повторно не применяется. До commit команда abort подтверждает неизменность DB
и предыдущей release, даже если файлы candidate потеряны. Для управления lease и
терминального resume файлы candidate не нужны. Для восстановления до успешного
staging передайте исходные проверенные input/output handoffs вместо показанных выше
установленных корней. Сохраняйте staging paths, принадлежащие operation, для диагностики;
автоматическая сборка мусора не реализована, никакие другие пути не удаляются.

Bootstrap всего сайта и индекс уроков:

```text
python -m backend.content.publish prepare-bootstrap --source-root . --source-sha <full reviewed SHA> --release-id <unique release> --input-root var/publication-inputs --changes var/bootstrap-edition.json --dry-run
python -m backend.content.publish prepare-bootstrap --source-root . --source-sha <full reviewed SHA> --release-id <unique release> --input-root var/publication-inputs --changes var/bootstrap-edition.json
python -m backend.cli index-lessons --source-root . --output-root var/lesson-index --dry-run
python -m backend.cli index-lessons --source-root . --output-root var/lesson-index
```

Продолжите bootstrap теми же командами build, plan и publish, передав
`bootstrap-edition.json`. Они подготавливают все public/lesson sources, каталог, метаданные seed
media и redirects в одной edition. Байты media должны совпадать с проверенным
manifest. Совпадающие существующие записи сохраняют IDs и timestamps; изменения runtime и
неоднозначные identity приводят к отказу подготовки. С публикации снимаются только две явно выведенные из эксплуатации исходные
static pages `materialy` и `pamyatki`; их строки, контент, даты
и ссылки сохраняются. Auth, членство в permission-группах, профили, receipts, login
windows и sessions не входят в патч контента. Повторный bootstrap предлагает ровно
ноль изменений, если sources и runtime совпадают. Помощник `backend.cli bootstrap
--disposable` предназначен только для создания синтетических fixtures.

Индекс использует порядок PostgreSQL и создаёт байты, совпадающие с сохранённым
Django index oracle. Он читает DB и проверенное дерево source, атомарно записывает только
`<output-root>/INDEX.md` и не меняет mtime неизменённого файла.
Dry-run не создаёт каталог output. Публикация и SQL-записи не выполняются.

Writer barrier cutover применяется как к публикации, так и к identity/staff.
При наличии истории миграций Django необходим долговечный проверенный checkpoint cutover, даже если не осталось ни одной legacy session или bootstrap receipt. В снимок источника HMAC
входят login windows, permissions, profiles, receipts, sessions,
история admin, content types и история миграций. Неподдерживаемые или ошибочные
сохранённые кодировки паролей блокируют preview/apply; сброс и перезапись hash не выполняются.


## Ограниченное обновление установленных публичных страниц

Операция legacy `update_public_pages` соответствует действию обычного publisher
`prepare-public-update`. Она требует существующего урока о свойствах степеней;
новая программа не устанавливается, несвязанные строки каталога/media не переписываются.
Используя то же окружение target DB и проверенную копию исходников, выполните:

```text
python -m backend.content.publish prepare-public-update --source-root . --source-sha <full reviewed SHA> --release-id <unique release> --dry-run
python -m backend.content.publish prepare-public-update --source-root . --source-sha <full reviewed SHA> --release-id <unique release> --input-root var/public-update-inputs --changes var/public-update-edition.json --backup var/public-update-before.json
```

Выборка состоит из четырёх информационных страниц (`glavnaya`, `karta-sajta`, `o-proekte`,
`kontakty`), установленного урока `bazovye-svojstva-stepenej-s-naturalnym-pokazatelem`,
метаданных публикации, двух сохранённых флагов вывода из эксплуатации, четырёх проверенных retired
redirects и метаданных `uploads/2026/07/pamyatka-stepeni.pdf`. Существующие PK и
временные метки создания сохраняются; у снятых с публикации страниц остаются их тела и обе временные метки.
Несвязанные строки контента, users, roles, profiles, receipts и sessions не обновляются.

Dry-run проверяет предлагаемые изменения и hash PDF без записи файлов, строк
или sequences. Обычная подготовка проверяет конфликты уроков и полную
опубликованную source edition перед созданием эксклюзивной резервной копии выбранных публичных записей
(`public-records-before-update-v1`, без приватных таблиц), затем неизменяемых inputs сборки
и передачи edition. Если backup уже занят, операция отклоняется; если `--backup` не задан,
по умолчанию рядом с файлом edition создаётся `<changes stem>-before.json`. Родительские каталоги назначения
уже должны существовать. Последующая ошибка подготовки/сборки может оставить эту публичную копию
для проверки; публикация не захватывается и SQL не применяется.

Соберите эти inputs и выполните те же обычные шаги `plan` и `publish`, что описаны выше.
Только fenced participant публикации фиксирует выбранные SQL patches и
активирует полную соответствующую edition HTML/assets/catalogue/sitemap. PDF
берётся из проверенных неизменяемых исходных assets. Поставка главной страницы также закрепляет все29
public uploads в проверенном media manifest, включая25 файлов, на которые больше нет прямых
ссылок в текущем авторском HTML/CSS. Их исходные URL и точные hashes остаются
доступны, в том числе у media без привязки. Экспортируются только эти публичные seed-файлы;
сохранённые изменяемые uploads не заменяются
без явного указания. Если опубликованная страница, не входящая в проверенные sources, была отредактирована,
полная передача сборки завершается с `SOURCE_CONFLICT`; перед публикацией согласуйте этот source.
Повторный dry-run при совпадающих данных предлагает ноль изменений.
