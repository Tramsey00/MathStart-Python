# MS-T008 — регрессия аудита runtime ACL

- Исходный HEAD: `41a864ec4fb45e0d7a9bd4e57ae613e6b9174173`. Проверенный код и тесты — в коммите с этим отчётом.
- Во всех трёх запросах аудита PostgreSQL зарезервированный алиас заменён на `privilege_name`; политика GRANT сохранена.
- `python -B -m unittest -v backend.tests.v04.test_runtime_privileges backend.tests.v04.test_runtime_privileges_postgres`: 5/5, включая 2/2 на отдельной PostgreSQL 16 с проверкой имени и маркера disposable БД.
- Проверены блокировки справочников, CRUD групп, запреты изменения защищённых PK, истории миграций, DDL и доступа к последовательностям и publication history.
- Синтетический отказ после COMMIT оставил APPLIED receipt и pending marker, а транзакция GRANT откатилась. Повторный DDL и неверный digest отклонены. ACL завершена после физической проверки схемы без повторного DDL.
- UPDATE двух полей справочников (`auth_permission.name` и `django_content_type.model`) реально разрешён. Это остаточный риск колоночных прав, необходимых для сохранения силы блокировки.
- Существующий профиль MS-T008 и его БД не использовались. Schema preview, Content и запуск приложения вне проверки.
