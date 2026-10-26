# Пакет контрактов MS7-MIG-R02 v1.0.2

**Снимок исторического этапа.** Приведённые ниже формулировки об ожидающем ревью
и отсутствующем runtime описывают этот пакет на зафиксированном SHA входа, а не текущую платформу.
Миграция принята в PR54, консолидация завершена в PR55; см. [сопровождение](../../../docs/maintenance.md), [текущие проверки](../../../docs/target-runtime.md)
и [локальный запуск](../../../docs/local-development.md). Исторические одобрения,
контракты и digest ниже сохраняют исходную область применения.

Статус: PROPOSED / ожидается независимое ревью. Владелец — Руслан / Tramsey00;
ревьюеры и Task Approvers — Владимир / VladimirFrolov777 и Илья / 13baybars.
[Issue #29](https://github.com/Tramsey00/MathStart-Python/issues/29).

Принятый вход integration: `c133f920fc14ab18a463e039f8e480e064ced81c`;
MIG_BASE_SHA `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`;
каноническое приложение `8c11edadc8debc81432d1db1145feac504f09061`.
Это три различных факта. R01 получил ACCEPTED_INTEGRATION после PR46/47; его
исторические снимки pending остаются без изменений. Задача ограничена документацией/контрактами и
верификацией; target runtime FastAPI/React/SQLAlchemy/Alembic отсутствует.

Нормативные входы: [точная версия миграции v1.1](../MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md)
§§2–11, карточка R02 и §17; [ADR0006](../../../docs/adr/ADR-0006-react-fastapi-migration.md)
с сохранёнными ADR0002/0003 и замороженными R02/R03/R02A/R03A. Пользователь подтвердил
64-символьный SHA256 `c5a554e3911bdb43db28d67fd02d26e38d50b2820e1154a272d89ecb44b1faae`;
в варианте из prompt на 63 символа пропущена `f`. Байты источника не исправлялись.

Читайте [platform](platform-v1.md), [аутентификацию](auth-v1.md),
[content/publication](content-v1.md), [авторизацию staff](staff-v1.md),
[контракты adapters](adapters-v1.md), [карту routes](implemented-routes-v1.json),
[полное отображение схемы](schema-mapping-v1.json),
[матрицу приёмки](parity-matrix-v1.json) и [руководство к матрице](parity-v1.md).
[JSON Schema delivery](delivery-v1.schema.json) и
[отдельный OAS delivery/staff](delivery-staff-v1.openapi.json) описывают предлагаемые
дополнительные adapters; они не заменяют и не увеличивают реализованное число операций — 37
в замороженном OAS. [Примеры синтетических ответов кандидата](synthetic-exchanges-v1.json)
сверены с независимыми историческими ожиданиями.

[Новый индекс свидетельств](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R02/old-to-new-evidence.json)
буквально сохраняет original_result и добавляет ссылки на текущий framework.
[Verification/handoff](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R02/handoff.md),
[план](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/exec-plans/active/MS7-MIG-R02.md) и
[trace](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/agent-traces/MS7-MIG-R02.md) фиксируют наблюдаемые результаты.

Одобрение привязано к точному commit и manifest digest контракта. Пока оба ревьюера
не одобрят изменения, а владелец integration не примет merge, эти дополнения остаются
предложенными. Подготовка и работа только на чтение разрешены; зависимая реализация ждёт
принятого CONTRACT. Разрешение на production не подразумевается.


Ревизия ревью 1.0.1 отвечает на предложенные B01–B07/N01 из
[ревью Ильи 5461343942](https://github.com/Tramsey00/MathStart-Python/pull/48#pullrequestreview-5461343942).
Читайте [handoff сборки public](public-build-contract-v1.json) и
[wire policy списка staff](staff-list-policy-v1.json); см. [матрицу изменений по ревью](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R02/review-response.md).
Решение CHANGES_REQUESTED остаётся историческим/текущим до независимого
повторного ревью; это дополнение не создаёт одобрения и не меняет принятые входы.

Версия протокола 1.0.2 отвечает на [ревью Владимира 5462501369](https://github.com/Tramsey00/MathStart-Python/pull/48#pullrequestreview-5462501369)
на commit `6c1603b3ac55f3f0e8ef3b2bfb09298a42de5974`. Читайте P1 в platform/content и P2 в auth,
[переходы публикации](publication-protocol-v1.json),
[lifecycle bridge](receipt-bridge-lifecycle-v1.json) и
[отображение durable storage](protocol-storage-mapping-v1.json).
Это предложенные решения контракта для независимого повторного ревью, а не принятый
runtime и не свидетельства проверок гонок. Исправления B01–B07/N01 и исторические ревью сохранены.
