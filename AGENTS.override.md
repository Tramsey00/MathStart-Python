# MathStart migration

Действующее единое задание и актуальная запись продолжения — [MIGRATION.md](MIGRATION.md).
Прочитать его перед реализацией; остальные contracts/code читать по изменяемой области.
Старые персональные очереди, ограничения по карточкам и постоянная команда отменены.
Сохранить данные/контент/history и незакоммиченные fixes. Не ослаблять tests,
не логировать secrets, не запускать production mutations. Один основной исполнитель,
отдельный final reviewer, затем человеческая приёмка. Само наличие файла не запускает работу.

Текущие runtime/product/architecture/setup guidance, вместо frozen platform описаний:
[docs/target-runtime.md](docs/target-runtime.md). Исторические исходники сохраняются.
