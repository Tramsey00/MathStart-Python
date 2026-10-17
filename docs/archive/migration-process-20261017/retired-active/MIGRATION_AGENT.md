# Единая задача миграции MathStart

## Цель и полномочия

Довести текущую ветку `ms7-mig-react-fastapi` до воспроизводимой версии существующего
MathStart на FastAPI/React и единого проверенного release-кандидата. Это одна задача,
продолжаемая между сеансами, без остановок на границах R/V/I и без персональных очередей.
Полный объём исходного ТЗ сохраняется, включая документацию и эксплуатацию.

Пользователь заменил прежние порядки «вся команда», «два/три задания» и «только I02».
Эти ограничения больше не действуют. Принятые R01/R02/V01/V02/I01 сохранены;
R03, I02/I03, части V04/V03/I04/R05 уже имеют код. Ничего из этого не начинать заново.
Ориентироваться на actual Git/dirty files и STATE, а не на старые TODO_FROM_ZERO.

Разрешены связанные backend/frontend/verifier/docs изменения, изолированные tests,
scoped commits, push migration refs и draft final PR. Финальная человеческая приёмка,
main merge, Issue closure, production writes/deployment — отдельные действия пользователя.
Исторические approvals не подделывать; новый процесс заменяет промежуточные
персональные task approvals для технического продолжения, но не финальный human gate.

## Источники: читать по потребности

На старте: AGENTS.md, этот файл и MIGRATION_STATE.md. Один раз установить объём
по каноническому `specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md`
(SHA256 c5a554e3911bdb43db28d67fd02d26e38d50b2820e1154a272d89ecb44b1faae),
ADR-0006 и [покрытию](MIGRATION_TASKS.md). Затем читать нужные части PRODUCT,
ARCHITECTURE, R01 inventory и `specs/migration/r02-v1/` рядом с меняемым кодом.
Технические contracts/frozen tests не заменяются этим кратким файлом.
Перед итоговой проверкой прочитать [полную матрицу](MIGRATION_VERIFICATION.md).
На возобновлении не перечитывать всё: STATE -> свежий diff -> нужный контракт.

## Сохранить и закончить текущую работу

1. Проверить root/branch/HEAD, dirty files и remote. Использовать существующий
   execution checkout; новый bootstrap не нужен. Не работать поверх другого writer.
2. Сохранить и закончить незакоммиченный Linux legacy-interpreter fix и его
   regression tests. Это уже существующая работа; сначала узкая проверка.
3. Обеспечить реальные public pages/SSG/LessonHost и identity/staff flows,
   публикацию/CLI/activation/recovery. Переиспользовать WIP из веток STATE после
   анализа diff/dependencies; не сливать вслепую и не объявлять WIP готовым.
4. Заполнить реальный R03 command map, собрать clean setup/fresh/upgrade/restore,
   браузеры и документацию. Внутренний порядок выбирать по фактическим зависимостям.
5. Получить final code candidate, полный применимый CI и отдельный final review.
   Исправить blockers, проверить delta и подготовить единую передачу.

Начинать от текущего кода. `a359b0b` — исторический принятый baseline, не команда
откатиться. Сохранить user changes, source manifests, tests и все raw evidence.
Не выполнять reset/clean/stash поверх чужой работы, не удалять ветки/worktrees.
Новые имена веток/коммитов/артефактов без брендовых префиксов, суффиксов и trailers.
Временные ветки допустимы для безопасности; не создавать ветку на каждую мелкую правку.

## Архитектура и границы

Один Python-монолит: FastAPI/Pydantic, SQLAlchemy2/psycopg/Alembic/Uvicorn,
Python3.12+, PostgreSQL16+. Короткие transactions/Session на unit of work.
React/TypeScript, принятые Vite/React Router и совместимые locks, existing CSS/tokens.
Один origin; Node для build/publish, без permanent Node SSR. Normal runtime/API/auth/
publisher/migration/target verification без Django/DRF; legacy comparison отдельно.
Сохранить opt-in SQLite для local non-concurrency, но PG ошибки не скрывать fallback.

Сохранить public URLs/redirect/404/SEO, authored HTML/math/SVG/CSS/JS и все script
families. Reviewed HTML доверен только через publisher; user/LLM input escaped.
Private account/staff no-store, без PII/secrets в SSG/bundle. Никакого массового JSX
conversion, редизайна, global reset, новой CMS/UI stack/Redis/Celery/microservices.

Сохранить strict HTTP contracts, exact JSON integer IDs, CSRF/Host/Origin,
opaque sessions/password compatibility/rotation/revocation, shared rates,
owner-bound receipt replay/retention и весь baseline staff/admin inventory.
JWT/browser credentials storage не вводить. Успешный build не доказывает auth.
DB и HTML/files не одна transaction: immutable inputs -> staged HTML -> DB/journal/
pending/fencing -> activation/recovery. Не ждать active release перед SSG build.

Будущие Knowledge/Assessment/Progress/Tutor/Analyzer/adaptive practice/диагностика
не реализуются; Product G1–G5 не закрываются. R05 адаптирует platform docs и полное
ТЗ v7.2 с 52 product IDs, не реализуя эти функции. Полный source v7.1 уже в repository.
Исторические contracts/approval/failure records не переписывать.

## Экономный рабочий цикл

- Один основной исполнитель. Не держать постоянных backend/frontend/reviewer.
  Не создавать новые пользовательские чаты. Если нужен субагент, дать только
  конкретный вопрос, нужные paths/contract, exact diff и требуемый краткий ответ.
  Не наследовать всю переписку, если доступен свежий ограниченный context.
- Самостоятельно реализовать связанный законченный кусок и проверить изменённое.
  Отдельное ревью каждого среза, отчёта или маленького исправления не требуется.
- Final reviewer один раз проверяет готовый кандидат по профилю
  [reviewer](docs/migration-agents/reviewer.md). Раннее отдельное review допустимо
  только для конкретного существенного риска schema/auth/publication/recovery.
  После fixes проверяются findings и затронутая delta; полный review повторяется
  лишь при существенном новом изменении. No independent review -> REVIEW_PENDING.
- Сначала быстрый reproducer/unit/preflight, затем integration, затем full run.
  Для уже известных неизменных prerequisites не повторять заведомый FAIL.
  Полный final target обязателен; pending/skip не даёт готовности.
- Длительные команды запускать с raw logs и summary; ждать завершения, не читать
  один и тот же полный log и не опрашивать часто. В контекст — exit/failing test/
  короткий traceback. Сканы всего inventory выполнять скриптами, не чтением
  сотен файлов моделью. Установленные совместимые среды переиспользовать.
- Полный прогон не повторять после docs-only change при прежнем code/config/input;
  старый результат сохраняет свой SHA. Для final combined code нужен actual run.
  После нового существенного изменения повторить применимые проверки.
- Не создавать дополнительные слои command wrappers/evidence frameworks без
  потребности действующего registry/контракта. Уже написанное переиспользовать.

## Продолжение и результат

При блокере сначала исправлять доступное в рамках всей миграции, а не ждать
нового task approval. Если нет внешнего входа/permission/лимита — записать
конкретную причину и перейти к независимой работе. После двух одинаковых неудач
не повторять механически: сменить проверяемую гипотезу либо сохранить checkpoint.
Не останавливать всю цель только потому, что закончен один исходный task ID.

Текущие факты хранить только в STATE и существующих machine ledgers. Один общий
execution plan/trace, без отдельного отчёта на каждый микро-шаг. Старые записи
живут в Git/архиве и читаются только для конкретного доказательства.
Перед остановкой: current SHA/dirty paths, checks/finding и точный next action.
Продолжение после закрытия сеанса требует нового запуска; не обещать фоновую работу.

Финиш: все исходные requirements технически покрыты, clean build/startup и
target/PG/browser/restore/evidence/docs проверены, final review без blockers,
release/rollback/draft PR готовы. Статус READY_FOR_HUMAN_ACCEPTANCE.
MIG-G4/main merge/Issue closure/deployment остаются HUMAN_PENDING до фактического
решения и исполнения. Не сокращать scope и не менять тесты ради экономии.
