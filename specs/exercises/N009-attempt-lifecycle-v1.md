# MS-N009: lifecycle implementation closeout v1

Статус: **IMPLEMENTED_CANDIDATE / HUMAN_REVIEW_PENDING**, не принятие R02A или ADR-0004.
Issue: https://github.com/Tramsey00/MathStart-Python/issues/90.
Base: `fdc8dc59b255b646f2f680cc993e616917d7f5e4` (N008, PR #89).

## Полномочия и сохранённые источники

Реализация явно поручена пользователем 19.11.2026, включая профильные PG/race/crash/privacy проверки.
Task skill N009, действующая архитектура и learning-requirements §§6–7/11 задают scope.
R02 принят; R02A остаётся PENDING, ADR-0004 — Proposed. Этот closeout передаёт
конкретную реализацию D-022/023 на ревью, не подменяет человеческое решение.
Frozen документы, schemas, fixtures и их статусы не изменены.

| Источник | SHA-256 неизменённого входа |
| --- | --- |
| specs/api/MS7-R02A-http-eligibility.md | 13ab20c4c03fda1d6baad2378497efc28864f87437d2df94fe331926d8e06970 |
| docs/adr/ADR-0004-http-eligibility-addendum.md | 281bce1938c4396218fde2865ab2ea8cce472d6acd27b2dcee526bcb30033b06 |
| specs/api/openapi-v1.json | 133aae117333e66b40662ec4fdb47fc02ee08e7aeecbbd9cbb200d5468ca7362 |
| specs/api/http-policy-v1.json | 3ba1823a149dc67ea65d84954dbbeb33d515169e94031edc787b75020d67eea8 |

## Реализованное поведение

- Auth и CSRF проверяются до mutations; внутри транзакции повторно проверяется
  действующая session. Поиск по owner предшествует replay; чужой/отсутствующий
  owned UUID даёт одинаковый 404. Guest mutations не создают Attempt, Exposure,
  actions, events, AIRun или provider calls. GET не создаёт доменных строк.
- Create использует только PUBLISHED версию и тему активной Content release.
  Shared version lock сериализует создание с архивированием. Открытые попытки
  сохраняют старый version ID после archive; новые по архивной версии запрещены.
  `previous_attempt_id` указывает на собственную уже отправленную/терминальную
  попытку той же версии; FK сохраняет owner/version binding.
- Draft заменяется целиком, partial input разрешён до submit. Revision начинается
  с 1; draft/submit/abandon повышают её на 1. Шаги непрерывны с 1, максимум 40;
  server step IDs сохраняются по позиции при full replace. После reorder ID
  обозначает позицию нового draft. Raw strings не нормализуются, длина поля до 512.
- Поля payload берутся из N008 templates и frozen R02: `expression` для
  MATH_EXPRESSION/EQUATION_STATE, `answer` для FINAL_STATEMENT; structured fields —
  по serialization привязанной формы. На submit обязательны требуемые поля.
  `normalized_repr=null`, `parse_status=NOT_REQUIRED`: parsing не выполнялся,
  математическая корректность или UNSUPPORTED не утверждаются.
- Submit принимает только revision/version, замораживает сохранённый draft,
  server steps/IDs, version и итоговую revision в SHA-256 snapshot. Возвращает
  durable 202 SUBMITTED с operation_id, snapshot_digest, submitted_at. GET статуса
  работает; автоматической очереди/evaluator нет. Исправление — новая Attempt.
- Assessed STARTED→SUBMITTED либо STARTED→ABANDONED. SELF_CHECK не submit-ится;
  подтверждённый reveal переводит STARTED→REVIEWED без assessed result/credit.
  COMPLETED и finalization не реализованы до N013; новые DB guards потребуется
  расширить отдельной миграцией N013, а не редактировать v01_0007.
- Permanent identity: owner+operation+key UNIQUE; digest включает canonical route,
  body, expected_revision и owner. Auth/CSRF/schema/owner → точный replay → state/revision.
  Ровно тот же сохранённый HTTP status/body возвращается после lost ACK; иной
  digest конфликтует. У action нет expiry. Очистка краткосрочных IdentityReceipt
  не снимает uniqueness. PUT draft согласуется через GET, без action receipt.
- Порядок locks: session validation → advisory action identity → Exposure → Attempt.
  Сортировка нескольких Exposure не нужна: mutation затрагивает ровно одну версию.
  GET/list используют REPEATABLE READ для согласованной проекции draft/steps/exposure.
- Exposure UNIQUE(user,version), monotonic max help/reveal/credit guard. Hint/reveal
  и постоянный response сохраняются атомарно **до** выдачи текста. Reveal после
  submit не меняет snapshot. Новая Attempt не стирает помощь. Pending eligibility
  false/PENDING; STARTED отображает перспективную eligibility, ничего не начисляет.
- У N008 банк REVEAL-only. Он не переписан и не дополнен выдуманными подсказками.
  Hint endpoint обслуживает только явно разрешённые levels и отдельные reviewed
  version-bound строки с проверенным digest/формой. Нужна содержательно проверенная
  публикация hint-enabled версии; runtime не импортирует банк, не меняет published
  версии и не вызывает LLM. Нет строки банка — 503; запрещённое действие — 409.
- Ответы/solution читаются только явным reveal. Runtime получает column SELECT
  только version_id/answer_key/canonical_solution; validation_spec/accepted_variants
  недоступны. Обычные Attempt/list/ошибки не содержат серверных ключей/решений.
  Action responses с раскрытием — закрытая серверная история, не public fixture.
- Typed client использует канонические DTO validators, CSRF и same-origin/no-store;
  не повторяет mutation автоматически. Unknown outcome сохраняет canonical key/raw
  draft. Poll delays 1/2/4 s передаются N014, затем ручной retry с исходным ключом.
  State fixtures синтетические, находятся только в tests и не импортируются runtime.

## Persistence и применение

`v01_0007` добавляет assessment_exposure/attempt/solution_step/action/attempt_event/
reviewed_hint. FK/UNIQUE/CHECK и PostgreSQL triggers защищают binding, snapshot,
submitted steps, append-only actions/events и monotonic exposure; TRUNCATE запрещён.
Manifest снят с отдельного PostgreSQL 16.15 и проверяется штатным schema inventory.
Существующие миграции не менялись. Startup не делает DDL/seed/publication.

Штатный путь установки: reviewed `backend.release_migrate preview/apply/check`;
для N008 head v01_0006 используется `TARGET_0006`, для пустой БД `FRESH`.
Применение к рабочей БД здесь не выполнялось. Обновляются также штатные runtime
column privileges; возвращение прежнего приложения сохраняет аддитивную схему.

## Race/crash matrix и граница передачи

| Сценарий | Обязательный исход |
| --- | --- |
| Две сессии edit/submit одной revision | Один победитель; второй REVISION_CONFLICT/STATE_CONFLICT |
| Два create с одним operation key | Одна Attempt/action; один и тот же ответ |
| Hint или reveal одновременно submit | Оба durable; raw snapshot неизменен, Exposure виден до будущей finalization |
| Crash процесса до COMMIT submit/reveal | Нет частичного action/exposure/snapshot и disclosure |
| Crash после COMMIT до ACK | GET видит committed state; retry возвращает сохранённый response, без второго действия |
| Receipt expiry/другой route под ключом | Постоянный action сохраняется; другой digest конфликтует |
| Logout/чужой owner | Replay закрыт текущим auth/owner gate; после нового login того же owner возможен точный replay |
| GET между row-read и save другой вкладки | Один согласованный snapshot, без смеси двух revisions |

N010: parser/normalizer/AST/resource isolation. N011: validators/analyzer.
N013: evaluator/finalization, COMPLETED/result, atomic credit reservation under Exposure
lock и передача immutable evidence в Progress. N014: форма/отображение и согласование
raw drafts. Эти части не реализуются в N009; положительных ProgressEvent здесь нет.

## Вопросы человеческого ревью

1. Подтвердить этот конкретный closeout D-022/023 в scope N009; общий R02A/ADR-0004
   остаётся Proposed/PENDING до отдельного явного решения по точным artifacts.
2. Для включения hints в реальном банке нужны проверенные тексты и новая согласованная
   публикация версии с HINT policy. Текущий REVEAL-only банк продолжает работать.

Результаты и SHA итогового candidate — в execution record карточки N009/PR.
Самопроверка не является независимым ревью или человеческой приёмкой; merge/deploy не выполнены.
