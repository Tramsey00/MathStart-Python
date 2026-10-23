# Источники HTTP-схем

`dto-v1.schema.json` — канонический пакет публичных HTTP DTO (JSON Schema
2020-12). `scenario-v1.schema.json` проверяет входные данные fixture последовательных
транзакций и ожидаемые наблюдения; это не HTTP response и не schema базы данных.

`openapi-3.1-2025-09-15.schema.json` — неизменённая официальная структурная schema
OpenAPI Initiative, загруженная с
https://spec.openapis.org/oas/3.1/schema/2025-09-15 2026-09-30.
Она явно проверяет OAS документ **без валидации Schema Object**.
Дополнительно suite задачи проверяет meta-schema definitions DTO,
разрешает локальные references offline, валидирует типизированные примеры и проверяет
семантику operations. Отдельный установленный пакет OpenAPI validator не заявляется.
Библиотеки JSON Schema или OpenAPI не добавляются; `jsonschema==4.26.0` уже закреплена в lock.

Manifest candidate в родительской директории закрепляет точные bytes OpenAPI,
внешних schemas, policy, fixtures и источников review. Его принятие остаётся PENDING;
нельзя подменять schema, отредактированную за digest уже принятого OpenAPI.
JSON/source artifacts контракта используют окончания строк LF.

Все публичные references разрешаются локально. Тесты не загружают ресурсы и не обращаются
к providers. Проверка schema не доказывает математическую истинность, PostgreSQL locking
или отсутствие prose, эквивалентной ответу; требования задачи и последующие human gates
по-прежнему действуют.
