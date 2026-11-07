# SPEC MS7-I02: Основа UI и fixtures

> Историческая спецификация прежнего UI. Статусы, сроки и решения ниже относятся
> к указанным Git revisions и не задают текущую работу. Утверждённый дизайн —
> [общий UI contract](../../docs/ux/shared-ui-contract.md), новая очередь —
> [tasks/INDEX](../../docs/tasks/INDEX.md). Не использовать I02 как шаблон переноса.

- **Статус:** PR OPEN / CHANGES_REQUESTED (ревью до исправлений); исправление опубликовано / CI SUCCESS; ожидаются Task Approvals
- **Владелец:** Илья
- **Reviewer / Task Approver:** Руслан и Владимир
- **Каноническая Issue:** [#21 - MS7-I02: UI foundation and fixtures](https://github.com/Tramsey00/MathStart-Python/issues/21)
- **Ветка:** `ms7-i02-ui-foundation`
- **Baseline SHA:** `428ece726918f635549fc7dd8fdd352f799c3308`
- **PR:** [#22](https://github.com/Tramsey00/MathStart-Python/pull/22), OPEN
- **Итоговый SHA исправления:** `e471efc0b1a6b4af9baf1401e49311a203f12450`
- **CI исправления:** [37060459060](https://github.com/Tramsey00/MathStart-Python/actions/runs/37060459060), SUCCESS
- **Опубликованный HEAD до исправления:** `931f83af01ea44c880ab94c5f7c134a29613a332`
- **Связанные ADR:** ADR-0001/0002/0003 и принятый пакет дополнения MS7-R02A
- **Exec plan:** [MS7-I02](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/exec-plans/active/MS7-I02-ui-foundation.md)
- **Trace:** [MS7-I02](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/agent-traces/MS7-I02.md)
- **Milestone Gate:** G3; задача I02 самостоятельно Gate G3 не закрывает
- **Срок приёмки:** 2026-10-05, по пересмотренному календарю Section 20
- **Последнее обновление:** 2026-10-02

## 1. Цель

Создать переиспользуемую основу Django UI для будущих экранов ученика: общие templates/components,
design tokens, безопасные версионированные fixtures, состояния loading/error/empty,
dispatch по schema и базовую доступность keyboard/mobile.

Подготовка и три commits реализации/документации опубликованы через PR #22;
`931f83af01ea44c880ab94c5f7c134a29613a332` — исторический HEAD до исправления.
Исправление закоммичено и опубликовано как `e471efc0b1a6b4af9baf1401e49311a203f12450`.
GitHub API подтверждает, что [run 37060459060](https://github.com/Tramsey00/MathStart-Python/actions/runs/37060459060)
завершился SUCCESS для HEAD исправления / PR merge-ref относительно main
`fa0d87033113a30abc6e9de2acc174b01e98d9db`. Запуск до исправления 37027103585 остаётся историческим.
PR #22 имеет статус OPEN и MERGEABLE на момент синхронизации. Оба существующих review имеют
CHANGES_REQUESTED на SHA до исправления; Task Approvals Руслана/Владимира — PENDING.
Пользователь разрешил синхронизировать записи/описание PR и повторить ревью.
Это дополнение только к документации, сохраняет побайтно все проверенные product/test/fixture/image;
последующие HEAD/CI нужно отличать от прогона исправления. Человеческое одобрение, merge
или закрытие задачи/G3 не заявляется.

## 2. Почему это относится к MathStart

Карточка v7.1 MS7-I02 (Section 24, стр. 68) охватывает NFR-13 (browser/mobile),
NFR-16 (keyboard/accessibility) и FR-04 (PublicExerciseDTO). Она подготавливает общие
UI assets для MS7-I03, MS7-I04 и MS7-I08, не заменяя сайт Django.

### Нормативный источник и принятые входы

Единственный нормативный источник новых требований MS7-I02 — полный документ
`.local-docs/MathStart_Technical_Specification_v7_1_SECTION20_PARALLEL_DEADLINES.pdf`.
Имя файла не ограничивает содержимое Section 20. Путь локальный; доступность через GitHub
не заявляется. Не копировать и не публиковать PDF в рамках этой задачи. Specification v6
не является источником требований к реализации.

```text
Canonical PDF SHA-256
e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd

MS7-R02A OpenAPI SHA-256
133aae117333e66b40662ec4fdb47fc02ee08e7aeecbbd9cbb200d5468ca7362

MS7-R02A package manifest SHA-256
1b4a4b43df6052db5d91840cb2e748745cafb0529a766272d5a29b2b88e6dbac
```

Применимые разделы v7.1: 5-7, 11, 15-17, 20-21, 24-25; более широкие маршруты приёмки
из Section 27 применяются только в scope этой основы. Section 20.6 указывает, что календарный
слой пересматривался; прежние даты NORMAL/EARLY карточки не заменяют срок I02 2026-10-05.

| Зависимость | Принятый вход и использование |
| --- | --- |
| HARD: MS6-I01 | Принятая/замороженная UX-передача: [UX spec](../../docs/ux/MS6-I01-ux-spec.md), [матрица состояний](../../docs/ux/MS6-I01-states-matrix.md), [карта экранов](../../docs/ux/MS6-I01-screen-map.md), [wireframes](../../docs/ux/MS6-I01-wireframes.md), [требования API](../../docs/ux/MS6-I01-api-needs.md). В §2 v7.1 записан PR #11 / merge `861433a6`. Повторная реализация и обновление статусов не выполняются. |
| CONTRACT: MS7-R02A | Принято Русланом и явно подтверждено пользователем; [HTTP contract](../api/MS7-R02A-http-eligibility.md), [OpenAPI](../api/openapi-v1.json), [DTO schemas](../api/schemas/dto-v1.schema.json), [policy](../api/http-policy-v1.json), [package manifest](../api/candidate-manifest-v1.json) и offline fixtures. |
| HANDOFF | Нет. |
| INTEGRATION | Нет; для специальных критериев приёмки I02 upstream runtime API не нужен. |

Принятие upstream определяется v7.1/подтверждением пользователя, а не устаревшими ярлыками
документа или одним совпадением hash. При подготовке все 17 pins manifest R02A совпали
с текущими bytes. Замороженный пакет R02A не меняется. R02 и ADR-0001/0002/0003 остаются
принятыми входами совместимости, а не разрешением расширять задачу.

## 3. Scope

### Входит в scope

- Общая расширяемая Django shell с сохранением существующих Content pages,
  SEO/canonical metadata, авторского content, каталога и ресурсов уроков.
- Минимальные переиспользуемые button, labelled field/error, card и state components.
- CSS design tokens и изолированные стили foundation.
- Loading, восстанавливаемая ошибка с демонстрационным retry, успешно полученные пустые
  данные и обычный content. Ошибка не трактуется как пустой успешный ответ.
- Foundation dispatch для четырёх принятых режимов по public mode/schema;
  контролируемое отображение неподдерживаемой формы, без полного renderer.
- Версионированные synthetic UI fixtures с provenance и совместимостью R02A.
- Минимальная GET-only галерея fixtures в существующем приложении `content`, доступная
  только при `DEBUG=True` и с постоянной пометкой, что это только fixtures.
- Базовая доступность keyboard, mobile smoke при 360/768/1440 px,
  Python/Django tests и доступные ручные browser evidence.

### Не входит в scope

- Полная отрисовка четырёх режимов (MS7-I04), редакторы решений или workflow ученика.
- Математическая browser-оценка, parser/checker, verdicts, normalization или авторитетные
  расчёты mastery/confidence/eligibility.
- Backend APIs, models, migrations, seeds/bootstrap или изменения исторических данных.
- Реальные auth/onboarding, lifecycle Attempt, submission, hints/reveal, Tutor,
  progress, diagnostics или practice flows.
- Бизнес-поведение pending/degraded/conflict/unauthorized и других будущих flows;
  точки расширения это поведение не реализуют.
- Node/Playwright/frontend toolchain, новые CI, изменение dependencies, отдельный
  preview server или полный cross-browser/accessibility audit.
- Массовая конверсия уроков, замена SPA/stack, deployment, live providers,
  изменение Harness или housekeeping замороженных upstream status records.

## 4. Роли и точки входа

Локальный разработчик/reviewer открывает галерею через существующий Django server:
`GET /__ui__/foundation/`. Это демонстрационный экран, не endpoint ученика.
Он читает только разрешённые авторские synthetic fixtures из repository.
Private user data и произвольные пути к fixture files не загружаются.

Gallery/fixture scripts не подключаются к обычным Content pages. Development route реализован;
рендеринг legacy проверяется Django tests без базы данных. Сравнение browser для опубликованных
главной/каталога/урока после пользовательского runtime migrate/bootstrap прошло;
галерея изолирована от этих страниц.

## 5. Правила домена и инварианты

1. Сохранять Django Templates и существующее владение/публикацию Content.
2. Долгосрочное состояние знания меняет только Progress; эта задача ничего не записывает.
3. Dispatch определяется объявленным публичным mode/schema, не догадкой по тексту задания.
4. Schema validation проверяет форму, не математическую истинность.
5. Сохранять raw demonstration input в памяти во время loading/error; не нормализовать его
   и не называть сохранённым на сервере.
6. Fixture-only маркировка остаётся видимой, в том числе в empty/error состояниях.
7. Публичные artifacts не содержат checker или скрытого ответа/reveal content.
8. Не добавлять mode, step type, HTTP status, DTO field или policy eligibility.
9. Не выводить independence из новой Attempt и не сбрасывать межпопыточный exposure.
10. Существующие авторские legacy ответы SELF_CHECK остаются baseline совместимости,
    явно сохранённым в v7.1 Section 11; новые components их не наследуют.

## 6. Взаимодействие / workflow

1. Локальный GET выводит галерею с переиспользуемыми templates и безопасными fixtures.
2. Примеры компонентов показывают обычный content, loading, error и подтверждённый empty.
3. Демонстрационный retry меняет только представление; student mutation не отправляется.
4. Public exercise descriptor выбирает foundation slot после проверки формы.
5. Неподдерживаемый descriptor получает пояснение, но не выдуманную форму/verdict.
6. Reviewer проверяет keyboard navigation и три mobile ширины.

Не имитируются как реальные отправленный результат, server save, reveal или прирост progress.

## 7. Изменения модели данных

Schema не меняется. Новых/изменённых models, constraints, indexes, data migrations или
backfill нет. Специальные migration tests для fresh/upgrade/locking — N/A.
Каноническая проверка согласованности migrations остаётся частью baseline verification.

## 8. Публичные и только серверные данные

Допустимы проверенные public exercise metadata, несекретные описания формы полей,
состояние/текст представления и synthetic demonstration strings.
Проекции UI state обозначаются как проекции, а не как выдуманные wire DTO.

Исключить `answer_key`, `validation_spec`, `canonical_solution`, checker/reference solution,
секретные принятые варианты, metadata с данными о правильности и эквивалентные prose/data.
Не доставлять полный R02A `http-exchanges-v1.json`: он содержит явные reveal responses и решения
завершённых attempts. I02 assets не должны включать reveal content, завершённые черновики решений
или подсказки, эквивалентные ответу.

## 9. Контракт API / ввода

Endpoint `/api/v1/` или serializer не реализуется и не меняется. Галерея доступна только при
DEBUG и только через GET; не-GET requests не должны вызывать mutation. При `DEBUG=False`
маршрут отсутствует.

Примеры wire DTO соответствуют принятым schemas R02A. Версия fixture UI state и версия
HTTP artifact отличаются от неизменяемой версии упражнения. Не добавлять выдуманное wire field
`schema_version`. Сохранять alias `version`/`contract_version` и связанную identity exercise.
Один только новый номер версии exercise не является причиной отклонять иначе поддерживаемую форму.

## 10. Контракт режимов взаимодействия

| Принятый режим | Обязанность foundation I02 |
| --- | --- |
| SELF_CHECK | Выбрать foundation slot без оценки; scored submit отсутствует. |
| FINAL_ANSWER | Распознать обязательную public input schema и выбрать slot. |
| STEP_BY_STEP | Распознать metadata public ordered-step и выбрать slot. |
| STRUCTURED_SOLUTION | Распознать отдельные input/step metadata и выбрать slot. |

Полные формы, редактирование/сериализация ordered steps, autosave, submission,
hints и reveal относятся к downstream. Parser profile и reveal/help policy — только public metadata;
I02 их не исполняет. Metadata, отсутствующая для будущей формы, не выдумывается.
Общие metadata `enum`/`object` не разрешают угадывать choices или вложенные поля.
Новые modes/step types запрещены.

## 11. Поведение validation

Для проверки формы/provenance wire fixtures используется существующий Python/jsonschema stack,
для templates/routing — Django tests. Dispatch проверяет только явно поддержанные формы.
Контролируемый экран неподдерживаемой формы отличается от результата Assessment `UNSUPPORTED`
и никогда не означает, что математика неверна.

JS dispatcher отклоняет mode, не являющийся строкой, до поиска в `slots`.
SELF_CHECK требует наличия обоих schema fields со значением null; FINAL_ANSWER требует
input_schema, STEP_BY_STEP — step_schema, STRUCTURED_SOLUTION — оба. Эти требования R02A
защищены regression tests без изменения принятого контракта или добавления renderers.

Математический validator, LLM, вызов provider или изменение prompt не нужны.

## 12. Семантика Progress / evidence

Функция не создаёт и не меняет evidence знаний. Student mutations, ProgressEvents,
CompletionFacts, решения eligibility или сохранённые attempts отсутствуют.
Переходы состояния галереи — только демонстрация представления.

## 13. Безопасность / владение

- Галерея доступна только в development, только GET и содержит synthetic data; policy auth не меняется.
- Для fixture или browser evidence галереи не читаются private owner data, credentials, cookies,
  реальные записи учеников или содержимое production database.
- В browser storage нет credentials/private results/answers; временный raw demonstration input
  существует только в памяти.
- Экранировать недоверенные statement/feedback/raw strings; не доверять произвольному HTML.
  Доверенную границу авторского Content HTML сохранять отдельно.
- Использовать явный allowlist fixtures; traversal/произвольное чтение файлов запрещены.
- Проверять переданные HTML/JSON/JS/data attributes/network на эквиваленты secrets.
- Не менять Session/CSRF, контракты reveal или rate limit. В этом изменении нет AI endpoint,
  поэтому реализация provider/rate limiter — N/A.

## 14. Наблюдаемость

Записывать provenance fixtures/state/mode и решения dispatch без secret data.
Browser evidence содержит фактическую версию browser, DOM assertions, observations network/console,
действия keyboard и screenshots с зафиксированными размерами. Screenshots дополняют assertions.
Фиксировать ограничения scope; не заявлять полный cross-browser/a11y audit или интеграцию
runtime ученика.

## 15. Критерии приёмки

- [x] Gallery демонстрирует переиспользуемые templates/components и tokens.
- [x] Loading/error/empty различимы; неудачная загрузка не считается пустым успешным ответом.
- [x] Четыре режима выбираются по объявленным metadata; неизвестные/неподдерживаемые формы
  безопасно отклоняются без угадываемого renderer или математического verdict.
- [x] Fixtures версионированы, имеют provenance, wire examples соответствуют R02A.
- [x] Fixture-only маркировка всегда видна; checker/ответы/reveal secrets отсутствуют
  в переданных artifacts и network responses.
- [x] Gallery отклоняет mutations, не записывает в базу и отсутствует при DEBUG=False;
  обычные Content pages не загружают fixtures галереи.
- [x] Недоверенные strings экранируются; raw demonstration input молча не меняется
  и ложно не называется сохранённым на сервере.
- [x] В keyboard baseline доступны достижимые controls, видимый focus и связанные labels/errors;
  mobile smoke охватывает 360/768/1440 px.
- [x] В Django rendering сохраняются существующие Content metadata/content/resources;
  browser comparison главной/каталога/урока после runtime setup прошёл.
- [x] Канонические/task checks имеют фактические результаты с ограничениями и записанным
  владельцем evidence; историческое подтверждение пользователя отделено от новых прогонов агента.
- [ ] Руслан и Владимир независимо одобряют конкретный итог; применимый CI на финальном SHA
  и разрешённый merge выполняются согласно Section 17.

## 16. Tests

### Python contract / Django tests (реализованы)

- Descriptor dispatch для четырёх режимов; неизвестный mode, обязательная schema отсутствует,
  неподдерживаемые формы, несовпадение alias version/identity.
- Версии/provenance fixtures и schemas R02A; намеренно неверные inputs остаются отрицательными
  тестовыми данными, а не принятыми публичными fixtures.
- Разметка loading/error/empty, маркировка, labels/errors и изоляция script assets.
- XSS escaping и отклонение эквивалентов secrets в доставляемых artifacts.
- DEBUG routing, отклонение не-GET и отсутствие записей в базу данных.
- Regression существующих Content shell metadata, авторского content и ресурсов.

### JS regression / browser smoke (реализованы с доступными средствами)

- `tests/test_i02_schema_dispatch.js` запускает production JS через уже доступный runtime,
  без изменений npm/dependencies/CI: 5 tests, 138 вызовов dispatch.
- Неизвестные strings, нестроковые types, обязательные schemas и инварианты SELF_CHECK
  с null-schema безопасно отклоняются; корректные fixtures сохраняют свои четыре slots.
- Browser matrix после исправления вызывает напрямую `window.MathStartUI.dispatchExercise`:
  40/40 cases, без exceptions/forms/generated inputs. Matrix и gallery — отдельные наблюдения;
  полного аудита malformed DTO не заявляется.

- Наблюдения runtime dispatch и loading/error/empty/retry.
- Сохранение raw input без normalization или ложного статуса сохранения.
- Keyboard walkthrough, базовые focus/labels/errors/live-region.
- Layouts 360/768/1440; DOM/network/console и screenshots без PII.

Полная матрица Chrome/Edge/Firefox не блокирует приёмку I02. Playwright или новый frontend
tooling не предполагаются. Если доступные средства не позволяют показать обязательное требование,
зафиксировать пробел и приостановить зависимую работу до отдельного подтверждения.

## 17. Матрица проверки

Следовать [verification skill](../../skills/verification/SKILL.md). После отдельного разрешения
реализации использовать настроенный Python 3.12+, существующий полный `requirements.lock`,
`python -m pip check` и фактический отчёт версий. Не переключать неисправную PostgreSQL
configuration на SQLite только ради успешного результата.

```text
python scripts/verify_repo.py
python -m unittest discover -s tests -p test_r02a_contract.py -v
python -m unittest discover -s tests -p "test_i02_*.py" -v
git diff --check
```

Команда I02 имеет смысл только после появления её tests; дополнительно явно запускать
`python manage.py test content.test_ui_foundation` после добавления. Сохранять восемь
существующих канонических checks, включая Django/content/migration/R03/Harness verification.
Runtime проверки Content требуют мигрированного/bootstrap окружения и создают отчёты;
на этом подготовительном этапе не выполнять migrate/bootstrap над пользовательскими данными.

### Историческая среда до публикации / свидетельства Content

Ручные проверки пользователя подтвердили работу host `.venv`: команды
`.\.venv\Scripts\python.exe --version` и `python --version` возвращают Python 3.14.7
с exit 0; `python -m pip check` сообщает `No broken requirements found`, Django импортируется
как версия 5.2.16. Ранняя ошибка команды version возникла в execution surface Codex
и не доказывала неисправность host `.venv`. Последние ручные проверки пользователя подтверждают,
что Docker Desktop установлен, Compose доступен, а контейнер PostgreSQL 16 healthy.
Dependencies синхронизированы из `requirements.lock`; psycopg 3.3.6 импортируется успешно,
pip check проходит. `python scripts/check_database.py` проходит с ответом
`PostgreSQL connection OK; server_version_num=160015`; `python manage.py check` проходит с
`System check identified no issues (0 silenced)`. Локальное соединение Python -> Django -> PostgreSQL
через Docker подтверждено; настройка PostgreSQL/Docker больше не является текущим blocker.
Это результаты host, сообщённые пользователем, а не повторные прогоны Codex.

Проверки реализации записаны в trace: 7 I02 Python tests, 5 Django tests без DB,
30 tests R02A, system/database checks и доступный browser smoke прошли.
Пользователь инициализировал локальную runtime DB командами `python manage.py migrate` и
`python manage.py bootstrap_site`, затем подтвердил database/system checks и
`python scripts/verify_repo.py` -> PASS (пройдено 8 checks). Предыдущая ошибка из-за пустой
базы устранена; это было runtime prerequisite, а не дефект I02. В этом follow-up агент
не запускал migrate/bootstrap и не повторял уже успешные canonical/task suites;
exit code shell пользователя отдельно не предоставлен.
Агент повторил только ранее заблокированные проверки Content: browser smoke опубликованных
главной/каталога/урока и read-only сравнение rendering с template `cd10705` прошли;
`/favicon.ico` возвращает обычный HTTP 404, не 500. В follow-up product code не менялся.
Фактические результаты см. в trace Section 17. Версия browser engine недоступна через
разрешённые browser controls; полный cross-browser/a11y и browser matrix malformed DTO
не заявляются. Изменения tooling/CI находятся вне этого плана и требуют отдельного
проверенного изменения до включения в проектный tooling.

### Текущие свидетельства опубликованного исправления

Trace Section 20 и `smoke.json.current` фиксируют свежую проверку агентом исправленного
рабочего Content, включая production JS/browser matrix, состояния gallery, keyboard и smoke
для 360/768/1440. Canonical PASS 8/8 — фактический повтор агента (exit 0), отделённый от
исторического прогона, подтверждённого пользователем. Browser context указывает Chromium/Google
Chrome `154.0.8037.93`; полный userAgent, userAgentData и high entropy values сохранены.
Ранние наблюдения о недоступной версии, отсутствующих таблицах и состоянии до публикации
остаются историческими. Сравнение существующего Content/favicon evidence сохраняет исходную
атрибуцию и не переименовано в новый browser rerun.
CI исправления run 37060459060 завершился SUCCESS на
`e471efc0b1a6b4af9baf1401e49311a203f12450`. Browser rerun произошёл до commit исправления
на тех же product bytes; его digest привязан к этому commit и не выдаётся за новый post-publication
rerun. Синхронизация только документации не добавляет результатов browser checks.
Независимые approvals остаются PENDING; CI/local PASS не является Task Approval.

## 18. Риски

| Риск | Влияние | Снижение риска |
| --- | --- | --- |
| Инициализация runtime (устранено) | Раньше пустая DB блокировала проверки Content | Пользователь выполнил migrate/bootstrap и подтвердил canonical PASS 8/8; повторный Content smoke проходит; агент не исправлял DB. |
| Ограничения browser evidence | Только один browser и сфокусированная dispatcher matrix | Записаны точная версия/UA; полный cross-browser/a11y audit остаётся NOT RUN; требуется независимое ревью. |
| PDF локальный, не public GitHub asset | Другому checkout нужен исходник | Закрепить точное имя/digest; распространение источника — follow-up пользователя, не публикация PDF в I02. |
| В полных upstream exchanges есть решения | Пакет fixtures может раскрыть ответы | Отбирать безопасные примеры/проекции; проверять доставленные данные, а не только отсутствие запрещённых keys. |
| Извлечение shell затрагивает legacy resources | Регрессия существующего сайта | Узкие Content tests и browser smoke; scoped revert сохраняет авторские sources. |
| URL configuration с DEBUG кэшируется | Проверка выключенной gallery может быть обманчивой | Отдельно проверять routing при загруженных конфигурациях DEBUG=True/False. |
| Dispatch разрастается до renderer | Реализация I04 начнётся раньше срока | Сохранять явные foundation slots; не угадывать недостающую metadata формы. |
| Browser evidence недостаточно | Обязательный baseline может остаться неподтверждённым | Зафиксировать пробел; до зависимой работы отдельно подтвердить доступность tooling. |

## 19. Definition of Done

Deliverables: общие shell/components, tokens, dispatcher, безопасные версионированные state
fixtures, DEBUG-only gallery, tests, browser smoke и документация handoff.
Готовность требует Section 15, verification skill и Section 17 v7.1: содержательных положительных/
отрицательных свидетельств, отсутствия утечек/несвязанных изменений, закрытых blockers,
независимого принятия Русланом/Владимиром, применимого успешного CI на финальном SHA и
разрешённого merge. На этапе подготовки приёмка задачи, финальный SHA или закрытие G3 не заявляются.

## 20. Ссылки на trace/реализацию и downstream handoff

- Issue: [#21](https://github.com/Tramsey00/MathStart-Python/issues/21).
- Plan/trace указаны в заголовке; PR #22 OPEN; SHA исправления/успешный CI закреплены выше,
  дополнение только к документации учитывается отдельно; Task Approvals остаются PENDING.
- Browser evidence: [smoke record](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/agent-traces/MS7-I02-evidence/smoke.json)
  и screenshots размеров 360/768/1440 и keyboard рядом. Использовался browser control приложения;
  Node/Playwright toolchain в проект не добавлялся.
- MS7-I03 получает принятые shell/tokens/labelled components/state conventions;
  настоящие auth/profile/onboarding и интеграция V02 остаются его задачей.
- MS7-I04 получает принятые public descriptors/dispatcher/provenance fixtures;
  полный catalogue/renderer и интеграция V04 остаются его задачей.
- MS7-I08 получает инструкции gallery, assets и browser evidence/ограничения;
  его frontend profile, настоящий Harness run и независимое ревью выполняются отдельно.

Handoff закрепляет будущий принятый artifact SHA/version и фактические test evidence.
Этот draft не считается принятым downstream handoff реализации.
