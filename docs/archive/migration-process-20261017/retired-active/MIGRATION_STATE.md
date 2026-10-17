# Актуальное состояние общей миграции

Режим: UNIFIED_GOAL / IN_PROGRESS. Один основной исполнитель, финальный reviewer.
Не действуют прежние ограничения «только I02», «по одной/две/три задачи» и
инструкции начинать I02/V04 с нуля. Следующий старт продолжает всю миграцию.
Подготовка этого режима сама по себе implementation не запускает.

## Checkout и сохранённая работа

- Рабочий root: `C:/Projects/MathStart-Python/migration-execution/integration`.
  В новом клоне использовать его собственный Git root, а не создавать такой путь.
- Branch: `ms7-mig-react-fastapi`; local HEAD при обновлении `a46daa9eda4e3fa84be4da380fe4b39c23f59430`.
- Remote при проверке: `b8a93821eccf37eebaebe744460a9f9c6b002cc2`. Перед push сверить заново.
- Immutable MIG_BASE_SHA: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`;
  accepted five-task snapshot: `a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6`.
- R03 уже включён controlled merge `f5c0558`; код продолжать, task не завершён.
- Published I02/I03 candidate и read runtime уже интегрированы. Переписывать не нужно.
- WIP branches: V03 `ms7-mig-backend-execution` / `fdac6e6`;
  I04 `ms7-mig-frontend-i04-wip` / `bcdb121`;
  R05 `ms7-mig-documentation-checkpoint` / `07dad69`.
  Дополнительный frontend fix: `ms7-mig-frontend-execution` / `66c6639`.
  Проверить свежие SHA и уже включённые deltas до reuse.

## Что не завершено

Техническая приёмка оставшихся13 IDs не заявлена. Existing source of detailed
facts: `docs/acceptance/migration-execution/task-ledger.json` и `parity-ledger.json`.
R01/R02/V01/V02/I01 historical accepted; остальные partial/TODO по ledger.
Наличие merge/кода или пустого findings array не означает technical completion.

На момент остановки есть НЕЗАКОММИЧЕННЫЕ исправления:
`frontend/legacy_comparator.py`, `scripts/verify_public_block.py`, helper/npm
commands, package/playwright/public e2e и оба migration workflows;
новые `tests/test_legacy_interpreter.py`, `frontend/tests/test_legacy_comparator.py`,
`frontend/e2e/i02.spec.ts`, evidence в `docs/acceptance/migration-execution/i02-verification/`.
Сохранить/проверить их, не перекрыть старой версией и не принять за опубликованные.
Точный dirty inventory/bytes до обновления инструкций — в архивном manifest.

## Проверки и следующий шаг

- Published CI38951840140 FAIL:27/28 source/read PASS, golden child ERROR,
  browser matrix NOT_RUN. CI-LEGACY-01: resolve() выбирал base Python вместо venv.
- Локальная новая Linux-regression:1 PASS; comparator tests:2 PASS по сохранённым
  логам. Fix ещё требует actual combined verification на новом коммите.
- Published CI38951840175: pure/legacy verify PASS, target prerequisite FAIL
  из-за `specs/migration/r03-v1/runtime-commands.json` с `commands={}`.
  Не повторять неизменный full target сейчас, но обязательно реализовать к финишу.
- Local combined02: частичный результат, был остановлен; не финальная matrix PASS.
- Конфигурация CI с PENDING/skip target находится в dirty diff. Проверить, что
  final acceptance всё равно FAIL при отсутствующем обязательном target.

Сначала проверить existing interpreter fix narrow tests, затем public/read runtime;
продолжить недостающее identity/staff, publisher/recovery/CLI и общий R03 registry
по фактическим dependencies. Не ограничиваться завершением I02.
Доступные среды: `var/public-target-env` и `var/public-legacy-env` (в Windows
`Scripts/python.exe`, Linux `bin/python`). Python3.12.14 был фактически доступен;
при запуске проверить версии/locks заново. Ports8111/8112 использовались для
owned disposable runtime; состояние ports/containers проверить, не удалять чужие.

## Источники и финальная передача

Migration ТЗ: `specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md`.
Product source: `docs/specifications/sources/technical-spec-v7.1.pdf`, SHA256
`e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd`.
`docs/specifications/technical-spec-v7.2-draft.md` — черновик, не принятая v7.2.
Полный source читать для завершения документации, не на каждом продолжении.
Архив прежних инструкций: `docs/archive/migration-process-20261017/`.
Исторические reviews/evidence сохраняются по исходным путям; не читать весь архив.

Финальная человеческая приёмка: HUMAN_PENDING. Main merge/Issue closure/production
не выполнены. При остановке заменить актуальные строки выше, не добавлять
весь предыдущий STATE ниже. Измеренные новые runs сохранять отдельно.
