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
и git diff --check. Tests/typecheck/Playwright/smoke/gates: NOT_RUN_BY_USER_REQUEST.
Новый startup не запускался, ускорение не измерено; нужен отдельно разрешённый
контроль cache hit/miss, изменения входов и восстановления повреждённого кеша.
Принятые уроки и БД не перепубликовывались. Независимое ревью PENDING.

## Карта перемещений и сохранённых файлов

- scripts/dev_server.py::prepare_view → scripts/dev/projection.py; прежний import
  в supervisor сохраняет доступ к функции, CLI и пути конфигурации не меняются.
- Промежуточные этапы docs/tasks/INDEX.md перенесены внутри файла в историю;
  исторические receipts не переписаны.
- curriculum/INDEX.md меняет только ссылки и подписи; файлы уроков не перемещаются.
- frontend/prototypes/home сохранён: lesson-source.mjs потребляет существующий
  frontend/tests/quadratic-source.test.tsx; theme registry остаётся дизайн-эталоном.
- body.html/page.css/page.js, static, migration receipts, tests сохранены из-за
  действующих потребителей. Массовые удаления и переименования не выполнялись.

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
