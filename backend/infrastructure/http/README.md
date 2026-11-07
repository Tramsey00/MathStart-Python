# V02 адаптеры чтения

Это приложение теневого чтения: при запуске оно не изменяет доменные данные и не выполняет DDL.
Авторитетны замороженные исторические OpenAPI/DTO. Сгенерированная документация FastAPI отключена.
Factory `create_app(engine, signer, ...)` создаёт один V01 UoW для каждой операции.
Транзакции PG явно READ ONLY; чтение не выполняет autoflush/commit/row locks.

Установите в изолированное окружение venv на Python3.12+:

```text
python -m pip install --no-deps -r backend/infrastructure/http/requirements.lock
python -m pip check
```

`python -m backend.infrastructure.http.runtime` требует явных
MATHSTART_DATABASE_URL (postgresql+psycopg), MATHSTART_HTTP_SIGNING_KEY,
MATHSTART_PUBLIC_ORIGIN; optional MATHSTART_HTTP_SIGNING_FALLBACK_KEYS JSON list,
MATHSTART_RELEASE_ROOT. Не наследуйте рабочий .env и не используйте production-данные для
тестов. Привяжите сервис к localhost8202; журналирование запросов отключено. SQLite — только явный V01
вариант совместимости; при ошибках PostgreSQL переключения на него нет.
Для secrets нет значений по умолчанию. При cutover используйте сохранённый keyring legacy-проверки подписи.
Анонимные grades сохраняют Django JSONSerializer/TimestampSigner (в том числе сжатые
старые токены), salt, область route/size/position и отсутствие max_age. Не назначайте старому
cursor срок действия в рамках новой политики. Staff cursors повторно используют эту проверенную криптографическую
реализацию с отдельным domain salt и связывают revision разрешений actor, полученную из DB.

V03 `authenticate(request)` возвращает AuthenticatedIdentity только после проверки server session
; значение по умолчанию None означает отказ. V02 повторно считывает flags и прямые/групповые разрешения.
Заголовки client role, cookies и user IDs здесь никогда не преобразуются в identity.
`csrf_check` — доверенный порт подтверждения от V03/gateway; при отсутствии подтверждения небезопасные разрешённые
public views отклоняются. Обычный запуск не передаёт ни identity, ни подтверждение CSRF. Проверки Session/hash/
rotation/revocation/Origin/Host остаются в ведении V03/V05.

V04 записывает неизменяемые <release-root>/<release_id>/index.json, pages/<id>.json и
разрешённые assets, а также descriptor/journal PostgreSQL. V02 проверяет закрытые
схемы index/page, перекрёстные ссылки, точные hashes index/body/assets и границы root.
Проверенное неизменяемое хранилище publisher считается доверенным; V02 не превращает произвольные
файлы файловой системы в проверенные артефакты. Происхождение public source_digest сохраняется,
и не сравнивается ошибочно с другой редакцией checkout. Целостность всех метаданных страниц
и исходных source artifacts должна быть подтверждена полной инвентаризацией staged hashes в V04.
При отсутствии/несогласованности активного snapshot возвращается503; fallback к latest DB отсутствует. Сохраняемые
неизменяемые routes требуют зафиксированный журнал APPLIED; перечисление каталогов не используется.

I02/V05 `render_page(page, context, canonical_url)` предоставляет проверенный HTML;
при отсутствии реализации по умолчанию возвращается503. V02 не создаёт вывод React/SSG. Каталог использует
темы, уже упорядоченные PostgreSQL, последние значения query и Python strip/casefold.
Внутренний context содержит `pinned_release: {release_id, manifest_digest}` для
каждой public HTML-страницы. Только karta-sajta также получает `catalogue_full` — полный
PublicCatalogue `{grades, subjects, sections, topics}`, вместе со всеми семью существующими
отфильтрованные поля каталога. Выбор класса/предмета сохраняет прежнюю семантику;
полные справочные массивы не заменяют этот выбор, отфильтрованные темы или count.
`Release.renderer_context(page, params)` использует уже выбранный Release и
не обращается к database и не разрешает активный descriptor повторно. Полный
context копируется глубоко, включая вложенные отфильтрованные строки. Страница, передаваемая
renderer, также копируется глубоко вместе со вложенными dictionaries и lists, чтобы изменения renderer
или его сбои не могли изменить проверенные страницы Release или index. Обе копии
взяты из одной выбранной release. Это внутренняя передача Python, а не новый JSON DTO,
endpoint, поле public schema или реализация renderer. Canonical вычисляется
как trusted origin плюс page canonical_path, без query parameters.
IDs в page/context остаются точными значениями Python `int` согласно существующему положительному
контракту int64 R02; преобразования в string/float не выполняются. Для моста I02 к Node
или browser JavaScript до обработки IDs выше `2**53 - 1` нужно согласовать без потерь представление на границе потребителя либо
parser. Обычные JSON.parse/Number не могут
сохранить все такие целые числа. Эта передача не разрешает менять public R02
DTO или вводить преобразование JavaScript; согласование границы потребителя остаётся
за Ильёй/Русланом. Идентификатор release runtime отличается от исходного Git SHA.
Прямые public routes закреплены за одной активной release; redirect выполняется только после фактического404.
HEAD возвращает пустое тело, для произвольных public verbs сохраняется приоритет CSRF, а Grades поддерживает только GET.
Если существует HOME, его точный alias `/<actual-home-slug>/` с кодом200, совпадающим page_id и
canonical `/` является обязательным. При отсутствии или ошибке alias release недоступна и возвращается503;
redirect или fallback к предыдущей/latest edition не выполняется. Для release без HOME
этот alias не требуется. Дополнительные HOME aliases запрещены; сохранённые
записи redirect сохраняют отдельную семантику fallback.
Только существующий путь Grades без завершающего slash явно возвращает301. Другие неподдерживаемые API paths
возвращают404, ошибки метода —400, записи Content —403 после staff authorization.

V04 `observe_publication(uow, page_id)` предоставляет неизменяемые факты активной edition/DB.
V02 считывает authority DB до и после (не более3 попыток), проверяет schema, owner/fence/
область действия на основе lease и отношения состояний; если provider отсутствует, возвращается503. Это граница,
а не доказательство работоспособности активации V04 или конвейера edition.

Ответы API используют JSON UTF8 и private,no-store. meta.version для Staff/delivery —
migration-r02-v1, для historical grades — http-v1. Внутренние исключения преобразуются в
фиксированный безопасный503. History сохраняет IDs/actors/timestamps/actions в порядке action_time/id;
исходные исторические сообщения не возвращаются, что предотвращает утечку паролей/запросов.
GET не предоставляет разрешение на запись, удаление, публикацию или активацию.

Явные проверки:

```text
python -m pip install --no-deps -r backend/tests/v02/requirements.lock
python -m unittest backend.tests.v02.test_unit backend.tests.v02.test_http backend.tests.v02.test_postgres -v
```

MATHSTART_V02_TEST_ADMIN_URL должен указывать на выделенный localhost15441/postgres;
для защиты проверки fresh() fixture DB используют префикс/маркер репетиции V01.
Проверки создают новые UUID databases и никогда не подключаются к существующим данным. Linux test
containers могут запускать неизменённые проверки V01 на localhost55441 в network namespace PostgreSQL
если Windows исключает этот порт хоста. Корневые проверки/workflows не меняются;
Руслан отвечает за подключение этих явных target-команд к общей CI.
