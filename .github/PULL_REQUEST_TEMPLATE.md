## Проблема и результат

Конкретный trigger и новое наблюдаемое поведение. Для документации — какие
противоречия устранены и где теперь canonical sources.

## Задание и scope

- Task ID / canonical skill / Issue (обязательно с MS-T003; bootstrap — исключение):
- Исходный SHA, ветка и проверенный candidate:
- Изменения и границы:
- Связанные contracts/ADR и scoped execution record:

## Проверки и ограничения

Следовать docs/frontend/testing-policy.md. Для текущего переноса автоматические
прогоны не запускать: NOT_RUN_BY_USER_REQUEST, не PASS. Указать source SHA,
самопроверку diff, фактический охват ручного ревью и непроверенные места.
Штатные валидаторы публикации сохраняются. Для отдельно порученных проверок
указать только разрешённый scope и фактические результаты.

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
Для оставшихся классов переход по согласованной очереди разрешён после взаимного ревью; итоговая приёмка Русланом одна.
