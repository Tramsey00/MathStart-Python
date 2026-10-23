# PostgreSQL: разработка и проверки

Используй текущие [README](../../README.md), [release runbook](../../deploy/RELEASE.md)
и [target verification](../target-runtime.md). Runtime — FastAPI/SQLAlchemy,
канонический Compose — deploy/compose.yaml. Для QA выбирай новые собственные
ресурсы, а не существующие acceptance/legacy БД или volumes.

Прежний Django runbook MS6-V01 является историческим:
1a87b044e8c5a7519b0ab57e22d2a35d57b4a986:docs/runbooks/postgres-dev-test.md.
Его команды выполняются только через [pinned oracle](../legacy-oracle.md).
