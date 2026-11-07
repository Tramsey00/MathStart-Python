# Репетиция восстановления и поддерживаемые границы отката

Повторяемая проверка ниже использует только новые синтетические containers, databases
и volumes, созданные для этого запуска. Она не подключается к production и не разрешает его восстановление.
Храните реальные резервные копии в зашифрованном виде, с ограниченным доступом и вне Git; определите
срок хранения, внешнее хранилище, восстановление ключей и ответственного оператора до release.

Установленная release представляет собой набор: состояние schema/data/history/protocol PostgreSQL,
полный корень изменяемых исходных media, неизменяемые input releases, скомпилированный
frontend, их receipts/manifests/digests, ключи проверки signing и привязка writer при cutover
Одной копии скомпилированных публичных файлов недостаточно. В
предыдущей публичной release были только4 непосредственно подключённых media-файла.
Текущая проверенная поставка главной страницы сохраняет все29 URL и hashes public seed media,
включая файлы без ссылок. Всё равно сохраняйте резервную копию всего изменяемого media root,
включая сохранённые uploads за пределами проверенного seed; нельзя выводить полный
набор резервирования по текущему HTML или неизменяемому asset manifest.

Используется именно физический метод. Происхождение cutover связывает OIDs базы данных и role
и факт остановки writer. Логическое восстановление в другую DB/role
не сохраняет эту identity и не должно незаметно переводить систему в READY. Не
создавайте новый digest, не меняйте ключ verifier и не перепривязывайте checkpoint автоматически
для запуска импортированной DB. Такое восстановление требует отдельно проверенной
процедуры подтверждения происхождения. Текущая проверенная процедура сохраняет identity кластера.

Порядок создания проверенной резервной копии для обслуживания:

1. Ограничьте входящий трафик и остановите API workers, publishers и legacy writers. Отключите
   and drain the sole legacy role; keep role memberships and the actual role
   snapshot. Retain the current signing/verifier keys separately in the private
   operator secret store. Never log their values or put them into public volumes.
2. В принадлежащем запуску container PostgreSQL16 выполните `pg_basebackup` от пользователя ОС postgres
   user with the selected replication-capable database role, `-X stream`,
   `--checkpoint=fast` and `--manifest-checksums=SHA256`, into a new private backup
   directory/volume. The rehearsal uses its own cluster's local socket and does
   not relax network replication authentication.
3. Выполните `pg_verifybackup` для готовой резервной копии. Скопируйте весь неизменяемый
   input/frontend tuple and the entire source media root. Bind full file hashes,
   retained DB input HMAC, DB/role identity and cutover digest in the private
   tuple manifest. No raw private rows/password/session values enter that
   manifest. Flush it before considering the backup complete.
4. Остановите исходный cluster до включения writer восстановленной копии. Выполняйте restore только
   into newly created, explicitly owned empty data/public/media volumes, using
   the same pinned PostgreSQL image. Preserve ownership and private file modes.
   Keep the backup mount read-only during restoration; never boot PostgreSQL
   directly on the only retained backup copy.
5. После восстановления WAL подтвердите физические schema/head, HMAC каждой строки и sequence,
   DB/role OIDs, writer/checkpoint facts, every public file hash and every media
   hash. Only then start the API against the restored volume tuple and retained
   keys. Prove exact HTML/catalogue, revoked sessions staying revoked, password
   re-login, profile/opaque session, and read-only repeated checkpoint import.
   Readiness must use the ordinary authority gateway.

Автоматическая реализация находится в `scripts/image_recovery.py` и запускается только через
`scripts/verify_images.py --recovery`. До резервирования команда создаёт фактический успешный registration
receipt, pending receipt, членство в группе, permissions role и checkpoint cutover
перед резервированием. После восстановления проверяются все SQL rows/sequences;
затем проверка API испытывает границу сохранённой opaque session и повторного входа.
Все корни копирования и identity очистки принадлежат этой проверке. Операторская команда restore,
перезаписывающая произвольный существующий volume, не предоставляется.

Используйте проверенный синтетический source runtime и сборку frontend с выбранным
loopback origin и локальные candidate images API/edge. Для HTTPS предоставьте приватный
тестовый certificate/key с фактическим loopback IP в SAN; его публичный сертификат
явно считается доверенным CA для этой проверки. И клиент хоста, и
отдельный TCP client проверяют CA и имя хоста. Отдельный container направляет
public origin к своему edge peer, не изменяя URL/Host/SNI. Он никогда не использует
`verify=False`. Обычный недоверенный client должен отклонить сертификат.

```text
python scripts/verify_images.py --disposable --recovery --rollback-image mathstart-api:<prior-compatible> --runtime-root var/recovery-<run> --source-runtime var/<managed-run>/runtime --artifact-root var/<https-build>/site --api-image mathstart-api:<candidate> --edge-image mathstart-edge:<candidate> --tls-cert <private-test-cert> --tls-key <private-test-key>
```

Опускайте TLS flags, только если фактический origin artifact использует HTTP. Команда
получает edge port из этого artifact, резервирует loopback PG55442 (или явно указанный
`--pg-port`), создаёт уникальные помеченные ресурсы и удаляет только их.
Signing keys/passwords находятся в приватных env-файлах ignored-каталога и
удаляются в `finally`. Отчёты содержат точные image IDs, привязки source, реальные
assertion IDs, public hashes/HMACs и измерения. Не завершайте процесс-владелец принудительно;
при прерывании перед следующим запуском сверяйте только его записанные IDs/labels.

Откат приложения выполняется отдельно от восстановления DB snapshot. Если задан отдельный
`--rollback-image`, репетиция сначала запускает этот предыдущий реальный бинарный API на
восстановленном target head до новых записей target. Затем она переключается на candidate,
выполняет вход и подтверждает запись данных target, переключается обратно на предыдущий API и
проверяет полный сохранённый account/profile DTO, session и неизменившийся DB
HMAC. Перед измерением нагрузки выполняется возврат на candidate. HTTP envelopes
должны сохранять точную структуру/version, а каждый запрос получать новый UUID;
тест не сравнивает изменчивые request IDs как сохранённые данные.

Это подтверждает совместимость только двух проверенных image IDs с общей
schema head. Будущая несовместимая комбинация image/schema не допускает безопасный
откат. До любых записей target можно рассматривать сохранённый до cutover snapshot всего кластера
только при блокировке обоих writer clusters и проверенном возврате
к старому приложению/ролям. Включение старого writer в target cluster с
последующее повторное использование старого checkpoint cutover не поддерживается. После записей target,
не заменяйте текущие данные старым snapshot. Сохраните текущие data/WAL и
используйте подтверждённое переключение совместимой версии приложения или восстановление вперёд. Применённые
migrations/history, receipts и sequences нельзя переписывать ради видимости безопасности.
Отдельная репетиция возврата legacy cluster ниже теперь охватывает границу до допуска
всего кластера; проверка images выше охватывает переключения совместимых target API.

Последние локальные свидетельства для ограниченной проверки сохранены в `image-recovery-result-20261018.json` в
`docs/acceptance/migration-execution/i02-verification`:449 фактических assertions,
828 public files и29 hashes исходных media, физическая проверка и очистка
PASS. Резервирование заняло8.797s; восстановление до authenticated readiness, включая
переключения приложений, заняло36.656s. В локальной конфигурации Windows/Docker Desktop
80 sequential HTTPS requests,20 cycles of `/`, `/_content/index.json`,
`/api/v1/grades/`, `/api/v1/users/me/`, one authenticated keep-alive client and
два API workers после восстановления показали p50=70.5ms, p95=110ms и max=1157ms.
Это измерения синтетического локального запуска, а не показатели capacity или SLO production.
Предыдущие сбои и частичное восстановление только immutable-public остаются в материалах.
Итоговая общая QA и операционная приёмка человеком ещё не завершены.

## Возврат legacy cluster до допуска target

```text
python scripts/verify_legacy_return.py --disposable --runtime-root var/legacy-return-<new-run> --legacy-python <separate installed Django interpreter>
```

Target interpreter должен оставаться без Django; нужны Docker и свободные loopback ports
55444/18135/18136 55444/18135/18136. Создаются только новые помеченные volumes/containers.
Запускаются фактические сохранённые Django migrations, bootstrap и collectstatic; реальный
HTTP registration/onboarding создаёт native session/profile/success receipts.
Также сохраняются приватные fixtures group/permission/admin-history/pending.
Скрипт останавливает legacy process, отключает единственную legacy LOGIN role, подтверждает, что sessions
отозваны, и записывает полный schema/row/sequence HMAC и DB/role OIDs. Физическая
pg_basebackup с потоковой передачей WAL и pg_verifybackup сохраняют кластер до cutover;
все29 media и неизменяемая legacy static build хранятся отдельно.

Затем выполняются обычная проверенная target schema и cutover CLI. Пользовательский
трафик target ещё не допущен: выполнены только контролируемые изменения миграции/импорта.
Target cluster останавливается и проверяется на изоляцию до копирования физического
snapshot до миграции в новый принадлежащий запуску volume. До повторного включения любой legacy LOGIN role
полные private HMAC/schema/history/sequences/OIDs восстановленной копии должны совпадать с
записанными фактами snapshot. Старый target cluster остаётся остановленным. Возвращённый
процесс Django должен отдавать тот же public HTML и полный profile/session, а также
успешно выполнять реальный вход по паролю. Это единственная ограниченная точка, где возврат всего кластера
до cutover можно рассматривать; это не откат после рабочих записей.

При возобновлении миграции после возврата к legacy снова остановите/освободите legacy и
создайте новые проверенные планы schema и cutover по текущему состоянию. Старый
checkpoint повторно использовать нельзя. Эта репетиция выполняет новое принятие данных,
требует одного F-login с сохранённым паролем/native proof, сохраняет
полный profile, а затем выполняет настоящую запись profile в target. Процедура, принадлежащая запуску,
отклоняет старый физический snapshot после допуска target и подтверждает, что текущие
приватные факты не менялись. Эта защита отслеживает собственный контролируемый lifecycle;
это не production oracle записей внешних операторов. В
эксплуатируемом stack независимая блокировка ingress/writer и аудит истории допуска
остаются ответственностью оператора. После записей target используйте переключение совместимого API
или forward recovery, сохраняя текущие data/WAL.

Результат ограниченной проверки18 October2026:34 измеренных assertion events, резервирование1.313s,
физический возврат до authenticated Django login7.860s; исходные данные не менялись, очистка
PASS. Receipts `i02-verification/legacy-return-02-20261018.json`; the prior
ошибка CookieConflict harness/cleanup PASS сохранена в legacy-return-01.
Cookie jars теперь сохраняют domain/path, не объединяя дублирующиеся записи
имён с разными областями действия. Это подтверждает синтетическую процедуру, а не конфигурацию production,
одобрение оператора, приёмку публичного домена или итоговую общую QA.

### Обычная конкурентная нагрузка API, 2026-10-18

Последующая репетиция `var/image-performance-01` сохранила полную физическую
проверку восстановления и отдельные проверки отката на совместимый image; пройдены455 assertions.
Дополнительно измерено400 фактических HTTPS-запросов от10 одновременных клиентов к
существующим `/api/v1/grades/` и аутентифицированному `/api/v1/users/me/` (по200 к каждому) после
20 отдельных прогревочных запросов. Все400 успешно завершились с корректными DTO/no-store;400 корреляций
запросов были уникальны, наблюдаемый пик concurrency составил10. Общий nearest-rank
p95 составил203ms; Grade —32ms, profile —219ms; каждый результат ниже существующего критерия500ms.
Сбои учитываются в знаменателе и распределении задержек; автоматических повторов нет.
Нагрузка не изменила database целиком, sequences и HMAC приватных фактов.

Область применимости: Windows/WSL2 Docker Desktop,12 логических CPUs,7,978,807,296 bytes memory,
PostgreSQL16.15, Python3.12.15 и два API workers через принадлежащий запуску HTTPS edge.
Разрешение часов Windows квантует отдельные измерения; это локальные временные
результаты, а не прогноз production capacity или будущих возможностей AI. Точные runtime
images собраны из3116fda с новым host recovery controller; исходные тайминги,
размеры групп, версии пакетов и hashes исходников сохранены в
`i02-verification/ordinary-api-workload-20261018.json` and the455-check result.
Workflow для полного candidate теперь запускает эту обычную нагрузку вместе с физическим восстановлением
как обязательную седьмую техническую job; одна проверка синтаксиса не подтверждает выполнение этой job.
