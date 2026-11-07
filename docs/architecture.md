# Текущая платформа Content

Основная архитектура: [target runtime](target-runtime.md),
[корневые инварианты](../ARCHITECTURE.md), [Content CLI](../backend/READ_RUNTIME.md),
[release](../deploy/RELEASE.md) и [recovery](../deploy/RECOVERY.md).
Авторские curriculum/site_content/static/media сохранены; schema и services
используют FastAPI/SQLAlchemy/Alembic. Исторические внутренние механизмы публикации
Django доступны в Git 1a87b044e8c5a7519b0ab57e22d2a35d57b4a986:docs/architecture.md
и запускаются только в [отдельном oracle](legacy-oracle.md).
