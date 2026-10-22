# Применение сохранённых контрактов

20.10.2026. Основная архитектура — [ARCHITECTURE](../ARCHITECTURE.md).
R02/ADR-0002 и R03/ADR-0003 сохраняют domain invariants и exact fixtures.
R02A/ADR-0004, R03A/ADR-0005 и I02/I03 сохраняют source/proposed/accepted scope
своей версии; наличие tests или принятого переноса не создаёт нового approval.

Слова Django/DRF/models/serializers/management commands в frozen domain/UX
контрактах относятся к исходной платформе, которая заменена ADR-0006 и
[platform/auth/content/staff adapters](migration/r02-v1/README.md).
Действующее применение: SQLAlchemy/Alembic, FastAPI DTO/transport, opaque
PostgreSQL sessions/CSRF, React/SSG и explicit CLI. Frozen source не используется
как инструкция установить Django. Его bytes/digests не обновлены массово.
Это включает frozen r02-v1 README/platform с прежним «runtime does not exist»,
proposed statuses и персональными назначениями: они описывают исходный этап,
текущий код/приёмка PR54/55 имеют отдельные источники в maintenance/architecture.

`specs/ui/site-polish.md` и `topics-catalogue.md` — исторические source contracts
принятого поведения. Их запреты ветки/commit и port8000/Django/collectstatic
относятся к прежнему поручению, не к текущей разработке. Принятые source/URL/
search/permissions требования сохраняются, а новый редизайн определяется брифом
и решением пользователя. Historical no-redesign migration condition завершено.

Для нового задания: [единая очередь](../docs/tasks/INDEX.md), указанный task skill,
затем необходимые contracts и текущие runtime commands. Старые owners/deadlines,
pending migration snapshots и Harness dependencies не создают новую очередь.
