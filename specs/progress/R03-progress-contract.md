# SPEC R03: Контракт ProgressEvent и UserSkillState v1

- **Статус:** Принято
- **Владелец:** Руслан; резервный владелец — Владимир
- **Связанная Issue:** https://github.com/Tramsey00/MathStart-Python/issues/6
- **Числовой норматив:** `specs/progress/BASELINE-v1.md` (без изменений)
- **Связанный ADR:** `docs/adr/ADR-0003-knowledge-progress-semantics.md`
- **Связанный контракт exercises:** `specs/exercises/R02-exercise-architecture.md`
- **Fixture:** `fixtures/progress-v1-cases.json`
- **Reference/checks:** `scripts/r03_contract_reference.py`, `tests/test_r03_contract.py`

## Границы и термины

`ProgressEvent` — единственное текущее имя события progress evidence. Более ранняя
терминология `KnowledgeEvent` в исторических artifacts заменена и не обозначает
второй сохраняемый тип. Только Progress принимает проверенные свидетельства и меняет
долгосрочный `UserSkillState`. Assessment предоставляет факты attempt/hint/reveal и validation;
Analyzer предоставляет только controlled evidence misconception, прошедшее confidence gate.
По одному неверному итоговому ответу нельзя определить misconception. Неподдерживаемый parsing
не является assessed wrong attempt или misconception. Код Tutor, frontend и LLM provider
не может записывать проекцию.

Этот контракт и его reference code — чистые версионированные примеры домена. Они не создают
Django models, migrations, services, database rows, endpoints или runtime seed data.
Будущая persistence должна транзакционно обеспечивать те же инварианты и защищать
исторические события от bootstrap.

## Envelope события и validation

Принятый `ProgressEvent` имеет следующие неизменяемые поля:

| Поле | Значение |
| --- | --- |
| `event_id` | Глобально уникальная стабильная строковая identity; также часть детерминированного порядка |
| `user_id`, `skill_id` | Ученик и стабильная ссылка Skill; reference fixture использует код Skill как `skill_id` |
| `event_kind` | Один из восьми базовых видов ниже |
| `occurred_at` | Timestamp с timezone в UTC, сериализованный RFC 3339 с `Z` |
| `policy_version` | Записанная policy проекции; на этом этапе `progress-v1` |
| `attempt_id` | Обязателен для assessed/reveal событий, происходящих из attempt; отсутствует для self-report |
| `evidence_ref` | Стабильная identity проверенного исходного evidence; обязательна для событий из attempt |
| `difficulty` | Обязательна для assessed events; число 1–4 или строка R02 easy/medium/hard |
| `misconception_code`, `confirmed` | Controlled code и подтверждение true нужны только для `MISCONCEPTION_DETECTED` |
| `source_kind` | Класс подтверждающего источника; misconception требует validated step, domain или structured-field source, а не один неверный итоговый ответ |
| `independent_evidence_rule` | Если проецируются две разные единицы отрицательного evidence одной attempt, обе записи должны иметь правило Assessment `distinct_validated_steps` |
| `hint_used`, `reveal_used` | Проверенные сервером факты attempt; утверждение client не считается достоверным |
| `completed_at` | Необязательный неизменяемый факт завершения Assessment для этой attempt/skill; RFC 3339 с timezone, нормализованный в UTC; см. правило recent-window |

Восемь видов: `SELF_REPORTED_KNOWN`, `CORRECT_FIRST_TRY`, `CORRECT_AFTER_HINT`,
`WRONG_ATTEMPT`, `MISCONCEPTION_DETECTED`, `ANSWER_REVEALED`, `DIAGNOSTIC_CORRECT`
и `DIAGNOSTIC_WRONG`. В R03 новые виды событий не вводятся. Для каждого принятого события
требуется поддерживаемая записанная версия policy. Отсутствующее поле, недопустимый enum,
неверное время, неfinite число, неподдерживаемая policy или противоречивый факт hint/reveal/
first-try отклоняются до изменения immutable log или проекции.

Для события из attempt Progress проверяет исходные факты Assessment/validation;
reference fixture передаёт эти факты напрямую. События правильного ответа и результата диагностики
требуют факта завершённой attempt. Для `CORRECT_FIRST_TRY` не должно быть hint/reveal.
`CORRECT_AFTER_HINT` требует hint и отсутствие reveal. Полный reveal до более поздней якобы
самостоятельной правильной работы в той же attempt лишает эту работу eligibility. Положительное
evidence, скопированное после полного reveal, отклоняется. `MISCONCEPTION_DETECTED` требует
controlled подтверждённый code и отдельную ссылку на supporting evidence; отдельный неверный
`FINAL_ANSWER` не может служить таким evidence.

## Числовой baseline без изменений

| Событие | Mastery | Confidence |
| --- | ---: | ---: |
| `SELF_REPORTED_KNOWN` | инициализация на 60 | инициализация на 15 |
| `CORRECT_FIRST_TRY` | +6 | +5 |
| `CORRECT_AFTER_HINT` | +3 | +4 |
| `WRONG_ATTEMPT` | -2 | +3 |
| `MISCONCEPTION_DETECTED` | -5 | +5 |
| `ANSWER_REVEALED` | 0 | 0 |
| `DIAGNOSTIC_CORRECT` | +8 | +8 |
| `DIAGNOSTIC_WRONG` | -6 | +8 |

Для assessed events:

```text
new_mastery = clamp(old_mastery + base_delta * difficulty_coeff * repeat_coeff, 0, 100)
new_confidence = clamp(old_confidence + confidence_delta, 0, 100)
```

Числа 1 или 2 нормализуются как `EASY`/0.8; 3 — `MEDIUM`/1.0; 4 — `HARD`/1.2.
Строки R02 `easy`, `medium`, `hard` нормализуются к тем же уровням. Для assessed difficulty
нет значения по умолчанию при пропуске/ошибке. Confidence не использует множители difficulty
или repeat. `repeat_coeff` равен 1.0 для всех событий, кроме подтверждённого misconception.
В baseline временного decay нет. Mastery темы остаётся средним с весами importance связей
topic-skill под владением Content и находится за пределами этой ссылки на проекцию отдельного skill.

Используется точная арифметика Decimal. **После каждого принятого проецируемого события**
рассчитать оба значения, ограничить каждое диапазоном `[0, 100]`, затем округлить каждое
до двух десятичных знаков через `ROUND_HALF_UP` перед обновлением `UserSkillState`.
Binary float не является нормативным. Self-report инициализирует 60.00/15.00; reveal
не меняет состояние. Округление после каждого события — часть replay, а не только финальное
форматирование отображения.

## Evidence count, status и время

`UserSkillState` уникален по `(user, skill)`. Канонические поля: `mastery`, `confidence`,
`evidence_count`, `status`, `last_updated`, `reducer_version`. Исходные значения соответственно
`0.00`, `0.00`, `0`, `NOT_STARTED`, `null`, `progress-v1`. Старый ярлык `last_evaluated_at`
из переноса baseline не является вторым полем R03; каноническое имя в Technical Specification —
`last_updated`. `reducer_version` определяет reducer проекции и в R03 равен `progress-v1`.
Учитывается по одному каждому принятому проецируемому `SELF_REPORTED_KNOWN`, `CORRECT_FIRST_TRY`,
`CORRECT_AFTER_HINT`, `WRONG_ATTEMPT`, `MISCONCEPTION_DETECTED`, `DIAGNOSTIC_CORRECT` и
`DIAGNOSTIC_WRONG`. `ANSWER_REVEALED` принимается как факт attempt с нулевым эффектом,
но не увеличивает счётчик и не меняет время. Повторное или отклонённое событие счётчик не увеличивает.
`last_updated` равно `occurred_at` последнего проецируемого события в нормативном порядке replay;
такой же immutable log точно воспроизводит все шесть канонических полей.

Pure reference возвращает шестипольное `state` и отдельную диагностическую `recent_window`
(`attempt_ids`, `independent_correct_count`), чтобы tests могли проверить входные данные статуса.
Диагностика вычисляется replay и не является дополнительным полем `UserSkillState`.

Статус вычисляется строго в следующем порядке приоритета:

1. `evidence_count == 0` -> `NOT_STARTED`;
2. mastery >= 80.00, confidence >= 60.00 и минимум три недавние независимые правильные attempts -> `MASTERED`;
3. mastery < 50.00 и confidence >= 30.00 -> `WEAK`;
4. иначе -> `LEARNING`.

Только self-report учитывается один раз и оставляет статус `LEARNING`, он не доказывает знание.
Повторный self-report или self-report после assessed evidence отклоняется без нового проецируемого
события. «До assessed» определяется нормативным порядком replay, а не порядком поступления по сети;
валидный self-report, добавленный задним числом до первого assessed event, может привести к повторной
проекции состояния. У одного user/skill никогда не бывает двух принятых self-reports.

## Последние десять завершённых attempts

Окно — **последние десять разных завершённых attempts для user/skill** в порядке
`(completed_at, attempt_id)` по UTC. `completed_at` события — авторитетный неизменяемый факт
завершения Assessment; если его нет, attempt пока не учитывается в этом окне. Несколько событий
одной attempt/skill должны совпадать по времени completion после нормализации UTC.
`completed_at` может быть раньше или позже `occurred_at`: evidence создаётся, нормализуется,
анализируется или добавляется задним числом в другое время. Порядок между этими фактами
не ограничен. Этот completion fact обязателен во входе replay для любой завершённой пилотной attempt,
участвующей в статусе Progress; путь завершения Assessment без completion fact Progress является
пробелом интеграции, который нужно устранить до persistence, а не поводом выдумывать неверное событие.

Завершённая attempt считается независимо правильной, если в ней есть `CORRECT_FIRST_TRY`
или `DIAGNOSTIC_CORRECT` до любого hint/reveal этой attempt. Учитывается уникальный attempt ID.
Правильная диагностика без помощи подходит; помогавшая диагностика, `CORRECT_AFTER_HINT` и
раскрытая работа — нет. Последующий reveal не отменяет задним числом правильный результат,
полученный до него. Для базового требования минимум трёх независимых правильных ответов
проверяются только десять самых новых завершённых attempts. Проекция строит окно из неизменяемых
completion facts событий; временной decay не применяется.

## Повтор misconception и единственный штраф

Для `(user, skill, misconception_code)` последовательные подтверждённые
`MISCONCEPTION_DETECTED` используют коэффициенты 1.0, 1.25, затем 1.5 для третьего и последующих.
Прочие wrong events ни увеличивают, ни сбрасывают счётчик данного кода. Независимая правильная
завершённая attempt по skill сбрасывает **все** счётчики misconception codes этого user/skill.
Правильный ответ с hint их не сбрасывает. Множитель repeat влияет только на отрицательную delta
mastery события misconception, не на confidence.

Единица evidence — `(user_id, skill_id, attempt_id, evidence_ref)`. Для одной единицы создаётся
**одно нормализованное отрицательное `ProgressEvent`**: `MISCONCEPTION_DETECTED`, если конкретное
заблуждение подтверждено, иначе `WRONG_ATTEMPT`. Пара этих типов на одной единице — недопустимая
комбинация event log и отклоняется; исходный неверный факт Assessment/Analyzer может храниться вне
Progress, но вторым `ProgressEvent` не становится. Разные завершённые attempts — отдельные свидетельства
по identity attempt. В одной attempt допускаются две проецируемые отрицательные единицы только если
их `evidence_ref` различаются и **обе** записи содержат явное правило Assessment
`independent_evidence_rule = distinct_validated_steps`; reference отклоняет пару без этой отметки.
Один неверный `FINAL_ANSWER` остаётся `WRONG_ATTEMPT` и никогда не превращается в выдуманное misconception.

## Idempotency, порядок и replay

`event_id` глобально уникален. Для событий из attempt также уникальна пара
`(attempt_id, skill_id, event_kind, evidence_ref)`. Retry с точно той же identity и payload
возвращает существующий результат без добавления или повторной проекции. Повтор identity
с конфликтующим payload — конфликт, а не новое событие. Для self-report действует отдельная
защита «один раз на user/skill». Будущая Django implementation обязана при concurrency
обеспечивать эти identities и атомарную запись события/проекции; этот reference проверяет
логическое поведение, а не DB locking.

**Нормативный ключ полного порядка — `(occurred_at, event_id, policy_version)`**.
Требуется нормализация UTC; принятая точность timestamp не превышает шесть десятичных знаков,
поэтому reference никогда молча не отбрасывает различия в порядке. Сортировка не должна зависеть
от формата timezone входа. `event_id` уникален, но `policy_version` остаётся явным третьим ключом,
как требует Technical Specification. Каждое immutable event применяется с собственной записанной
`policy_version`. Текущий reference регистрирует `progress-v1`; незарегистрированная policy
выдаёт ясный отказ, а не молча использует новейшую. Валидное событие, добавленное поздно/задним
числом, вызывает повторную проекцию затронутого user/skill по полному упорядоченному immutable log.
Повтор того же log при любом порядке доставки даёт тот же `UserSkillState`, включая mastery,
confidence, evidence count, status, `last_updated` и `reducer_version`.

## Критерии приёмки контракта

`tests/test_r03_contract.py` должен проверять все восемь видов, точные deltas, difficulty,
confidence, Decimal rounding/clamp, границы статусов, self-report, последние десять attempts,
повторы/reset, reveal, source idempotency, отклонение пары отрицательных событий с одним evidence,
оба допустимых временных порядка completion и occurrence, а также детерминированный replay
события, добавленного поздно, для каждого канонического поля состояния. Для pilot codes, edges
и event kinds ожидаемые значения в tests задаются независимыми literal constants.
`scripts/verify_repo.py` запускает эту pure suite вместе с существующими checks.
Спецификация не заявляет проверку PostgreSQL, Django persistence, API или runtime Knowledge/Progress.
Итоговый human contract gate: ACCEPTED. R03 остаётся активным, пока её PR не слит в main.
