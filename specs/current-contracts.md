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


## Текущая программа 24.10.2026

Полное старое ТЗ, старый source registry, I01 wireframes и дизайн-аудиты удалены
из checkout и доступны по Git b29a7ccdd07784cfcfd19278cbe59b30c83cd4ea/path.
[Новые задачи](../docs/tasks/INDEX.md) — единственный порядок;
[стандарт](../docs/frontend/lesson-migration.md) — инструкция переноса.
Текущие API/domain fixtures в specs сохранены, поскольку их читают код/тесты.
Старые UI MD не задают внешний вид: применяй [принятый UI](../docs/ux/shared-ui-contract.md).
Будущая семантика/численные требования сохранены в [learning requirements](product/learning-requirements.md).

## Identity MS-T009 — 13.11.2026

[Identity addendum](api/identity-t009.md) расширяет действующую Identity: вход,
ЛК, recovery, лимиты и v01_0003. Frozen R02 bytes остаются неизменными;
новые решения ожидают отдельного ревью и приёмки по карточке MS-T009.


## Приоритеты и публичный доступ — решение 16.11.2026

T010 (включая staff concurrency addendum из закрытого PR #79) отложена; этот addendum не объявляется внедрённым в main. Обязательный путь и отложенные задачи — docs/tasks/INDEX.md и DEFERRED.md. В T011 новый canonical URL используется напрямую; выведенный старый публичный учебный URL возвращает 404 без legacy redirect. Это заменяет прежнее правило сохранения legacy lesson URL/redirects, не технические HTTPS/auth redirects. Нужные transport-изменения оформляются addendum при реализации, frozen fixtures не переписываются.

Публичная самопроверка без LLM не требует входа и не создаёт assessed Attempt/ProgressEvent/mastery. Assessed API остаётся авторизованным. Guest helper блокируется UI и сервером до submit/Analyzer/Tutor/provider; подробности в N009/N014/N017.
