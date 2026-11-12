---
name: mathstart-project-organization
description: Упорядочивание проекта после объединения 5-го и 7-го классов; Issue 66.
---

# Организация проекта — Issue #66

[Issue](https://github.com/Tramsey00/MathStart-Python/issues/66).
Исходный main: 5a5ef883f1017d646ad0ff8f849a0af97a6078fa.
Ветка project-organization. Статус READY_FOR_REVIEW, приёмка и merge PENDING.

## Результат

Указатель curriculum/INDEX.md открывает актуальный формат и показывает URL.
Карта docs/repository-map.md определяет владельцев файлов; документы и шаблоны
не требуют запрещённых прогонов. Очереди команды сохраняют их распределение,
параллельный перенос, взаимное ревью и одну итоговую приёмку Русланом.
Исторические сведения очереди сохранены в разделе истории, а текущие статусы
5-го и 7-го классов отражают приёмку и merge. Учебные данные не изменялись.

Подготовка dev-проекции вынесена из supervisor в scripts/dev/projection.py.
При совпадении байтов immutable inputs, конфигурации, Python-кода, схем и кеша
проекция переиспользуется. При изменении входов выполняется прежняя подготовка.
Публичная валидация и публикация не меняются; startup не выполняет QA или DDL.

## Самопроверка и ограничения

Просмотрены imports, consumers прототипа, код Content preparation, diff документов
и git diff --check. По отдельному поручению 12.11.2026 выполнены только проверки
изменённого кеша и запуска; остальные suites/typecheck/Playwright/gates остаются
NOT_RUN_BY_USER_REQUEST. БД использовалась только на чтение, Content publication
не выполнялась. Независимое ревью PENDING.

## Карта перемещений и сохранённых файлов

- scripts/dev_server.py::prepare_view → scripts/dev/projection.py; прежний import
  в supervisor сохраняет доступ к функции, CLI и пути конфигурации не меняются.
- Промежуточные этапы docs/tasks/INDEX.md перенесены внутри файла в историю;
  исторические receipts не переписаны.
- curriculum/INDEX.md меняет только ссылки и подписи; файлы уроков не перемещаются.
- frontend/prototypes/home выведен: тестовый адаптер перенесён в frontend/tests/helpers,
  theme registry — docs/ux/theme.registry.json. Отдельный preview и его tests/config
  удалены; основной runtime в frontend/src остаётся без изменений. Пофайловая карта:
  specs/maintenance/project-organization-dispositions.json, исходный SHA 090d005.
- body.html/page.css/page.js, static, migration receipts, tests сохранены из-за
  действующих потребителей. Действующие контракты, миграции и исходные материалы сохранены.

## Локальная уборка — инвентаризация, без удаления

Основная папка C:/Projects/MathStart-Python и работающий контейнер
mathstart-dev-21ea40c0f94f сохраняются.
Чистые старые копии без stash: MathStart-host-check, MS-main-20261107,
ms-t002a-clean-20261025, ms-t002a-final-20261025, ms-t002a-handoff-20261025,
ms-t002a-ready-20261025. Перед удалением сохранить уникальные commits/local data.
Соответствующие остановленные PostgreSQL: 0bb1c69607c5, 00c73ba97398,
5476eede263b, b436277e631b, 07f3326c125a, 48e024ec2221 (префикс mathstart-dev-).

ms-t002a-compose-full-20261026 содержит три изменённых файла: dev.ps1,
scripts/container_dev.py, scripts/dev_server.py. Compose-окружение msdev-44a2b52de6f0
связано с этой папкой. ms-t002a-compose-20261026 и compose-check имеют по 1301
изменению (в просмотренном выводе удаления); clone-20261025 имеет сломанную ветку.
MathStart-retired-20261019-181400 не Git-репозиторий; уникальность данных неизвестна.

msdev-ad051667164b — остановленный альтернативный Compose основной папки.
mathstart-ms-t001-qa-pg помечен disposable. mathstart-local-* использует прежние
acceptance volumes — сохраняется. test-mysql не подтверждён как часть MathStart;
heuristic_gould — демонстрационный контейнер. Другие проекты не затрагиваются.
Контейнеры и volumes удаляются адресно отдельно; общий prune --volumes не применять.


## Итог разбора категорий репозитория

Проверены точки входа и ссылки между основным frontend, прототипом, CLI,
документами и ручными workflows. Удалён самостоятельный preview, заменённый
frontend/src/features/public-pages и shared/lesson; сохранён его внешний тестовый
consumer через перенос адаптера. Общие CSS/JS в static ещё обслуживают legacy,
HTML curriculum участвует в Content preparation. Backend, миграции и specs
задают действующие схемы и протоколы. Scripts проверки/восстановления имеют
CLI/workflow-потребителей и не удаляются из-за временного запрета автопрогонов.
Исторические audits/receipts нужны для точных прежних SHA и не считаются текущими
инструкциями. Локальные node_modules/.venv/var не являются tracked архитектурой.
Удаление контейнеров и других C:/Projects в эту доработку не входит.


## Разрешённая проверка 12.11.2026

Проверялись рабочие изменения поверх 090d005 (runtime diff: backend JSON добавлен
в fingerprint; далее Python-код не менялся). БД — собственная host-dev установка,
чтение активного release; schema/Content publication не выполнялись.

- Обычный prepare_view: кеш повторно использован, 0,687 с после первого обращения.
- Намеренно повреждённый временный public-view.json: восстановлен, 66,657 с.
- Изменён PUBLIC_ORIGIN: штатная подготовка 72,422 с, все 280 route views содержат
  новый origin. Настройки рабочей установки не менялись.
- Изменение Python-файла и backend JSON на временных входах меняет ключ; возврат
  исходных байтов возвращает исходный ключ. Изменение входов во время подготовки
  было отвергнуто; кеш смешанного состояния не сохранён.
- Два запуска scripts/dev_server.py --host-dev и штатные --stop: готовность
  102,16 с / 22,09 с; оба stop exit 0. Dev projection 71,750 с / 1,969 с.
  Это Python entry штатной npm-команды; npm-обёртка не менялась.
- Перенесённый lesson-source.mjs импортирован Node успешно; сам suite не запускался.
- Ссылки на файлы в изменённых Markdown существуют; git diff --check без ошибок.

Первый заход застал выключенную БД; после запуска своей БД проверка повторена.
Одноразовый проверочный скрипт исправлен на чтение UTF-8 после ошибки cp1251;
это не изменение приложения. Скрипты и временная проекция удалены, логи двух
запусков сохранены локально в var/tmp/issue66/host-1.log и host-2.log.
Общий backend/frontend suite, typecheck, Playwright и release gates не запускались.
Окружение после проверки остановлено, данные сохранены. Независимое ревью PENDING.


## Уборка var/static/tests и проверка Git — 12.11.2026

По дополнительному поручению удалены локальные восстановимые каталоги:
var/docs-cleanup/venv, var/t001-qa/legacy-env, var/t001-qa/target-env,
var/local/venv (рабочий runner использует основную .venv), var/target-checks
(одноразовые результаты target_check.py), tests/__pycache__. Удалены три пустых
каталога; рабочие var/local и var/compose исключены из удаления пустых каталогов.
Перед каждым рекурсивным удалением абсолютный путь проверен на принадлежность
корню проекта. Чужие C:/Projects, контейнеры, volumes, активные releases,
планы и приватные конфигурации сохранены.

static сохранён по потребителям backend/content/build.py, frontend account/staff/
debug routes и тестам совместимости. Все 19 корневых тестовых файлов сохранены:
есть явные вызовы в ручных workflows/target_verification или unittest discovery;
они проверяют действующие контракты и инструменты, не самостоятельный старый UI.
Проверки не запускались: NOT_RUN_BY_USER_REQUEST. Анализ исходников и Git — выполнен.

Проверены git ls-files, отслеживаемые ignored-файлы, характерные имена приватных
конфигураций, расширения ключей/дампов и шаблоны токенов/DSN в текстах текущего
дерева. Отслеживаемых var/venv/node_modules/logs/private configs нет; найденные
DSN — примеры и синтетические тестовые значения. Реальных ключей/токенов
не обнаружено. Полная история Git и содержимое крупных двоичных файлов не
сканировались. .gitignore дополнен локальными данными агентов, private-env,
secrets, ключами, дампами и отчётами; git check-ignore подтвердил исключения.
