# MathStart migration

Итог технически завершённой миграции и ожидающая человеческая приёмка —
[MIGRATION.md](MIGRATION.md). Не начинать перенос заново и не выполнять старые
персональные очереди или карточки. Новая работа — только по поручению пользователя;
contracts/code читать по затронутой области. Сохранить данные/контент/history и
незакоммиченные fixes. Не ослаблять tests, не логировать secrets и не выполнять
production mutations. Наличие документов не запускает реализацию или приёмку.

Текущие runtime/product/architecture/setup guidance, вместо frozen platform описаний:
[docs/target-runtime.md](docs/target-runtime.md). Исторические исходники сохраняются.
