## Проблема и результат

Конкретный trigger и новое наблюдаемое поведение. Для документации — какие
противоречия устранены и где теперь canonical sources.

## Задание и scope

- Task ID / canonical skill / Issue (обязательно с MS-T003; bootstrap — исключение):
- Исходный SHA, ветка и проверенный candidate:
- Изменения и границы:
- Связанные contracts/ADR и scoped execution record:

## Проверки и ограничения

Actual команды/результаты/CI links на candidate SHA. Указать portable/runtime
scope и не выполненные проверки. Empty/skipped/missing/timeout не PASS.
Основная команда `python scripts/verify_repo.py`; prerequisites —
docs/target-runtime.md, staged checks — skills/verification/SKILL.md.
При schema changes: reviewed Alembic, fresh/upgrade/concurrency; при content/UI:
semantic source/URL/math/assets и actual browser/visual checks.

## Данные, API, безопасность

Schema/API/contracts impact или N/A. Сохранность user history/Content/Progress
ownership, answer/hint/reveal boundary, auth/CSRF/owner и секретов. Не включать
DSN/passwords/cookies/PII в evidence. Для снятых файлов — explicit disposition map.

## Отдельное ревью и приёмка

- Self-check findings и исправления:
- Отдельное ревью: PENDING / ссылка на actual review:
- Blocking findings / необходимые исправления:
- Человеческая приёмка: PENDING / ссылка на решение:
- Production/provider/security решения по применимости:

PASS и создание PR не означают human acceptance. Merge только по решению
пользователя после review/checks; force push и auto-merge запрещены.
После передачи текущего поручения следующая карточка не выполняется автоматически.
