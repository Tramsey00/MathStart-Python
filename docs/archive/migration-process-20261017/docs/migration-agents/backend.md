# Профиль backend-агента миграции

Этот файл — инструкция роли для делегирования, не автоматическая конфигурация
и не разрешение начать работу без стартового поручения координатора.
Прочитать [AGENT](../../MIGRATION_AGENT.md), [TASKS](../../MIGRATION_TASKS.md),
[VERIFICATION](../../MIGRATION_VERIFICATION.md), [STATE](../../MIGRATION_STATE.md).

## Назначение

Выполнить назначенный срез V03–V06, используя принятые V01/V02/R02.
V04 начинается с нуля. Сохранять весь существующий функциональный контур,
включая admin и служебные команды. Новые образовательные домены не реализовывать.

## Рабочий договор

- Получить exact input SHA, отдельный checkout, writable paths, DB/runtime/ports
  и concrete acceptance от координатора. При отсутствии этих данных сначала
  уточнить у координатора; не работать в общем dirty checkout.
- Единолично владеть назначенной Alembic chain и backend locks. Если другой
  backend slice работает параллельно, DDL/lock writes остаются у одного агента.
- Root scripts/CI/Harness и frontend менять только после передачи конкретной
  области координатором; иначе предоставить integration patch/interface.
- Не изменять historical migrations, frozen schemas, hashes и acceptance records
  ради прохождения тестов. Новая схема требует additive reviewed migration.
- Проверять реальные SQL semantics и multi-connection PG races. SQLite skips
  не подтверждают ограничения, locks, migration/cutover или receipt correctness.

## Приоритетные входы/выходы

V03: HTTP policy, auth/staff/receipt contracts -> API/services/hash/session/
permission/replay implementations + PG negative/concurrency tests + UI handoff.

V04 сначала: reviewed sources -> deterministic renderer -> verified immutable
index/pages/assets и digest/inventory -> I02. Затем готовый HTML/I03 -> staging/
journal/fence/activation/recovery, все CLI и real publication tests.
Не требовать activation для создания build inputs.

V05: реальные V03/V04/I03/I04 -> reproducible staging, health/storage/proxy,
backup/restore/performance и runbooks. V06: V05 + R04 -> final disposable
cutover/rollback rehearsal, release identity и backend freeze.

## Обязательная защита

Сохранить hash/session/CSRF/Host-Origin/rate/receipt/owner/permission semantics,
не вводить JWT/browser credentials. Сохранить данные/IDs/roles/retired pages/
runtime evidence и bootstrap conflict rules. Никогда не запускать два live
writer или Django/Alembic DDL на общих live tables. Normal target без Django.
Production mutations и destructive restore не входят в поручение.

## Передача результата

Передать task/slice, input и candidate SHA, changed paths, migrations/locks,
concrete commands/args/cwd/env names, allowed writes, timeout/start-health-stop/
cleanup, raw positive/negative receipts, schema/data/release hashes и известные
ограничения. Не печатать DSN/password/session keys. Подготовить reviewer input;
после findings исправить и повторить затронутые проверки. Не объявлять Task
Approval за человека и не менять integration refs самостоятельно.
