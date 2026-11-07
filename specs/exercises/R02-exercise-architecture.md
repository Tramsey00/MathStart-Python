# SPEC R02: Архитектура упражнений

- **Статус:** Принято
- **Владелец:** Руслан
- **Связанная Issue:** https://github.com/Tramsey00/MathStart-Python/issues/4
- **Связанный ADR:** `docs/adr/ADR-0002-exercise-contract-architecture.md`
- **Связанный exec plan:** `docs/exec-plans/completed/R02-exercise-architecture.md`
- **Целевой этап:** M0 — основа, готовая к работе агентов
- **Плановое окно:** 2026-10-02 — 2026-10-08
- **Последнее обновление:** 2026-09-24
- **Human gate:** Принято Русланом 2026-09-24

---

## 1. Цель

Определить стабильный версионируемый контракт упражнения, который позволяет независимо
разрабатывать backend и frontend, не раскрывая ответы, хранящиеся на сервере, и не смешивая
слабые свидетельства с подтверждёнными заблуждениями.

R02 содержит только архитектуру/спецификацию.

Он не реализует Django models, migrations, APIs, validators или UI.

---

## 2. Базовый продукт

MathStart поддерживает четыре режима взаимодействия с упражнением:

1. `SELF_CHECK`
2. `FINAL_ANSWER`
3. `STEP_BY_STEP`
4. `STRUCTURED_SOLUTION`

Для каждого упражнения задаётся один режим взаимодействия.

Режим взаимодействия определяет UX, форму payload ученика, путь validation,
поведение reveal/hint и семантику evidence.

---

## 3. Обязательные инварианты

1. Публичный payload упражнения MUST NOT содержать `answer_key`.
2. Публичный payload упражнения MUST NOT содержать `validation_spec`.
3. Публичный payload упражнения MUST NOT содержать `canonical_solution`.
4. Секретные принятые варианты MUST оставаться на сервере.
5. Reveal MUST быть явным и записываться до возврата канонического ответа/решения.
6. Попытка с полным reveal MUST NOT создавать `CORRECT_FIRST_TRY`.
7. Один только неверный `FINAL_ANSWER` MUST NOT создавать конкретное заблуждение.
8. Raw input ученика MUST сохраняться отдельно от нормализованного представления.
9. Parse status `UNSUPPORTED` MUST NOT превращаться в выдуманное заблуждение.
10. AI/LLM output не является источником математической истины.
11. Режим взаимодействия не является skill.
12. Progress остаётся владельцем соответствующего домена.

---

## 4. Публичный контракт упражнения

Концептуальный DTO:

```json
{
  "id": "exercise-id",
  "code": "linear_parentheses_001",
  "topic": {
    "id": "topic-id",
    "slug": "linear-equations"
  },
  "statement": "Solve: 2(x+3)=10",
  "interaction_mode": "STEP_BY_STEP",
  "input_schema": null,
  "step_schema": {
    "allowed_step_types": ["EQUATION_STATE"]
  },
  "parser_profile": "algebra_linear_v1",
  "difficulty": "medium",
  "reveal_policy": {
    "allowed": true,
    "confirmation_required": true
  },
  "contract_version": 1
}
```

Это пример контракта, а не окончательный DRF serializer.

Публичные поля могут описывать отображение задания, сбор ввода, допустимые типы шагов,
профиль parser/display, сложность, правила показа reveal/hint и `contract_version`.

`input_schema` и `step_schema` определяют только публичный контракт сериализации и UX.
Они могут содержать имена полей, публичные типы ввода, обязательность, правила порядка
и несекретные ограничения формы. В них нельзя включать правильные значения, маркеры
корректности, скрытые принятые варианты или правила, из которых можно восстановить ответ.

Публичные поля не должны раскрывать правильный ответ, каноническое решение, скрытые
принятые варианты или детерминированные правила проверки, тривиально восстанавливающие ответ.

---

## 5. Контракт проверки только на сервере

Концептуальное серверное представление:

```json
{
  "exercise_id": "exercise-id",
  "answer_key": {
    "type": "equation_solution",
    "value": 2
  },
  "validation_spec": {
    "validator": "linear_equation_v1"
  },
  "canonical_solution": {
    "steps": [
      "2x+6=10",
      "2x=4",
      "x=2"
    ]
  },
  "accepted_variants": [],
  "contract_version": 1
}
```

Этот объект никогда не входит в обычный публичный payload GET упражнения.

---

## 6. Матрица режимов взаимодействия

| Режим | Что отправляет ученик | Validation | Семантика evidence |
| --- | --- | --- | --- |
| `SELF_CHECK` | ничего не требуется | нет анализа решения; только действие reveal | просмотр/reveal не повышают mastery |
| `FINAL_ANSWER` | поля из `input_schema` | детерминированная/domain validation ответа | свидетельство правильности/слабое свидетельство ошибки; один неверный финальный ответ сам по себе не создаёт конкретное заблуждение |
| `STEP_BY_STEP` | упорядоченные объекты `SolutionStep` | parser + validator перехода + необязательная классификация analyzer | подтверждённая проблемная операция может служить свидетельством заблуждения |
| `STRUCTURED_SOLUTION` | динамические поля из `input_schema`, представленные типизированными шагами из `step_schema` | schema/domain validators + необязательная классификация LLM | evidence создаётся только на основе проверенных полей/шагов |

---

## 7. `SELF_CHECK`

Типичный публичный контракт:

```json
{
  "interaction_mode": "SELF_CHECK",
  "input_schema": null,
  "step_schema": null,
  "reveal_policy": {
    "allowed": true
  }
}
```

Поведение:

- отправка ответа не требуется;
- анализ решения не требуется;
- reveal выполняется явно;
- для интеллектуального упражнения, связанного с attempt, сервер записывает reveal до
  возврата ответа/решения;
- reveal не создаёт положительное evidence mastery.

Существующие legacy упражнения MathStart могут оставаться в этом режиме, пока
не будет реализована более глубокая поддержка.

---

## 8. `FINAL_ANSWER`

Пример публичного input:

```json
{
  "interaction_mode": "FINAL_ANSWER",
  "input_schema": {
    "type": "object",
    "fields": [
      {
        "name": "answer",
        "input_type": "math_text",
        "required": true
      }
    ]
  }
}
```

Пример отправки:

```json
{
  "attempt_id": "attempt-final-001",
  "contract_version": 1,
  "payload": {
    "answer": "32"
  }
}
```

Поведение:

1. сохранять отправленный payload;
2. проверять форму публичного payload;
3. запускать детерминированный/domain validator на сервере;
4. если ответ правилен, позднее создать соответствующее evidence корректности через Progress;
5. если неверен, создать слабое evidence ошибки;
6. не выдумывать конкретное заблуждение только по неверному значению.

---

## 9. `STEP_BY_STEP`

Пример `SolutionStep`:

```json
{
  "step_no": 1,
  "step_type": "EQUATION_STATE",
  "payload": {
    "expression": "2x+3=10"
  },
  "raw_text": "2x+3=10",
  "normalized_repr": null,
  "parse_status": "NOT_REQUIRED"
}
```

`SolutionStepSubmission` задаёт форму данных от client к server. Client передаёт
`step_no`, `step_type`, `payload` и `raw_text`. Server проверяет публичную форму и
формирует `normalized_repr` и `parse_status`; client не должен заявлять авторитетные
результаты parsing. Сохранённый/возвращённый `SolutionStep` содержит все шесть логических
полей, показанных выше.

`step_no` — положительная нумерация с единицы, уникальная в пределах attempt.
Принятые правила порядка и retry/update относятся к деталям API реализации,
но исторический порядок должен оставаться однозначным.

Обязательные логические поля:

- `step_no: int`
- `step_type: string/enum`
- `payload: object`
- `raw_text: string | null`
- `normalized_repr: string | null`
- `parse_status: OK | UNSUPPORTED | INVALID | NOT_REQUIRED`

Базовые типы шагов:

- `MATH_EXPRESSION`
- `EQUATION_STATE`
- `STRUCTURED_FIELDS`
- `FINAL_STATEMENT`

Поведение:

1. сохранять raw step/payload;
2. проверять step schema;
3. при необходимости нормализовать/разбирать;
4. сравнивать предыдущее и новое состояние, если validator поддерживает такой переход;
5. если корректно — продолжать;
6. если вызывает подозрение — сформировать candidate error evidence;
7. при необходимости после этого выполняется классификация Solution Analyzer;
8. на Progress может повлиять только проверенное evidence.

---

## 10. `STRUCTURED_SOLUTION`

`input_schema` — динамический UI/form contract, определяющий поля для пользователя.
Отправленный payload проходит публичную schema validation и серверную domain validation.

Отдельная `step_schema` определяет, как решение представляется типизированными,
упорядоченными шагами. Она описывает допустимые типы шагов, порядок и сериализацию;
`input_schema` она не заменяет.

Иллюстративный публичный контракт:

```json
{
  "input_schema": {
    "type": "object",
    "fields": [
      {"name": "known_values", "input_type": "object", "required": true},
      {"name": "formula", "input_type": "math_text", "required": true},
      {"name": "substitution", "input_type": "math_text", "required": true},
      {"name": "answer", "input_type": "math_text", "required": true}
    ]
  },
  "step_schema": {
    "type": "ordered_steps",
    "allowed_step_types": ["STRUCTURED_FIELDS", "FINAL_STATEMENT"],
    "ordering": {
      "field": "step_no",
      "direction": "ascending"
    },
    "serialization": [
      {
        "step_type": "STRUCTURED_FIELDS",
        "payload_fields": ["known_values", "formula", "substitution"]
      },
      {
        "step_type": "FINAL_STATEMENT",
        "payload_fields": ["answer"]
      }
    ]
  }
}
```

Это пример fixture контракта.

Он не обязывает проект использовать одну универсальную реализацию JSON Schema.

Расширения domain должны сохранять общую модель attempt/step и вводить validators/adapters
осознанно.

---

## 11. Профиль parser и parse status

`parser_profile` задаёт поддерживаемое поведение parsing/normalization, ожидаемое для упражнения.

Это публичная metadata только в случае необходимости для client.

Он не должен раскрывать секреты корректности.

Базовые состояния parsing:

- `OK`
- `UNSUPPORTED`
- `INVALID`
- `NOT_REQUIRED`

Семантика:

- `OK`: поддерживаемый input успешно разобран;
- `UNSUPPORTED`: syntax/domain нельзя надёжно обработать;
- `INVALID`: форма нарушает ожидаемый публичный контракт;
- `NOT_REQUIRED`: этому шагу не нужна нормализация parser.

`UNSUPPORTED` не является заблуждением.

---

## 12. Семантика hint

- использование hint наблюдаемо;
- attempt записывает самый высокий использованный уровень hint и/или историю событий;
- базовые уровни hint: `0..3`;
- правильный ответ после любого hint в рамках attempt использует
  `CORRECT_AFTER_HINT`, а не `CORRECT_FIRST_TRY`;
- точные числовые эффекты Progress задаются в `specs/progress/BASELINE-v1.md`.

R02 не задаёт формулировки prompt для tutor.

---

## 13. Семантика reveal

Порядок reveal:

1. ученик запрашивает reveal;
2. сервер записывает состояние/event reveal;
3. сохраняется `answer_revealed_at` (или эквивалентный факт);
4. только после этого можно вернуть канонический ответ/решение;
5. последующая работа в рамках этой attempt не может считаться `CORRECT_FIRST_TRY`;
6. копирование раскрытого решения не является evidence знания;
7. сам reveal соответствует нулевому приросту знания согласно baseline Progress.

Обычный GET упражнения не должен делать reveal эквивалентным чтению скрытого поля,
которое уже передано браузеру.

---

## 14. Версионирование контракта

Для каждого exercise/interaction contract задаётся `contract_version`.

`contract_version` — логическое имя R02 для концепции baseline `version` из MathStart
Technical Specification v3.1. Оно не создаёт второй независимый счётчик версий.

Публичное определение упражнения и соответствующие серверные данные validation
интерпретируются в рамках одной версии контракта.

Изменения публичного контракта, нарушающие совместимость, требуют явного review.

Каждая attempt привязывается к `contract_version` упражнения, активной при её начале.
Исторические attempts интерпретируются согласно этой версии, а не текущему определению упражнения.

Точная стратегия persistence неизменяемых записей версий или snapshots отложена до
backend implementation spec.

Версия, сохранённая на сервере в attempt, авторитетна. `contract_version` в запросе client
служит значением совместимости/предусловием. Сервер сравнивает её с версией attempt и
отклоняет несовпадение; client не может изменить авторитетную версию attempt.

---

## 15. Mock-контракты для параллельной работы

R02 предоставляет следующие версионированные fixtures спецификации:

- `fixtures/self-check.exercise-v1.json`;
- `fixtures/final-answer.exercise-v1.json`;
- `fixtures/step-by-step.exercise-v1.json`;
- `fixtures/structured-solution.exercise-v1.json`;
- `fixtures/reveal.exchange-v1.json`;
- `fixtures/final-answer-submission.exchange-v1.json`;
- `fixtures/step-submission.exchange-v1.json`.

Fixtures не должны содержать secrets серверной validation.

Fixtures упражнений — обычные примеры публичного `ExerciseDTO`. Exchange fixtures
показывают публичные формы запросов/ответов. Response reveal содержит раскрытый content
только после записи reveal сервером; это явный reveal response, а не обычный payload GET
упражнения. Все fixtures — artifacts спецификации, а не runtime seed data или исполняемый
вывод API.

Текущий сайт отображает авторские ответы legacy self-check в HTML уроков через `<details>`.
Эти существующие страницы являются входом совместимости и могут оставаться в режиме
`SELF_CHECK` до последующей ограниченной конвертации. Они не выполняют и не переопределяют
целевой server-reveal contract для новых интеллектуальных упражнений.

---

## 16. Проверки безопасности / целостности

Последующий regression test реализации должен проверять, что обычный публичный ExerciseDTO
не содержит:

```text
answer_key
validation_spec
canonical_solution
accepted_variants
```

Эквивалентные секретные поля необходимо включить в те же regression checks.

---

## 17. Критерии приёмки

- [x] точно определены четыре режима взаимодействия;
- [x] публичный и серверный контракты разделены;
- [x] `STRUCTURED_SOLUTION` использует `input_schema` для динамических полей и
  `step_schema` для порядка/сериализации типизированных шагов;
- [x] `SolutionStep` типизирован и упорядочен;
- [x] определены базовые типы шагов;
- [x] определены parse statuses;
- [x] явно описана семантика hint/reveal;
- [x] отсутствует shortcut диагностики по одному неверному финальному ответу;
- [x] публичные примеры не содержат secrets validation;
- [x] задано правило версионирования контракта;
- [x] mock-контракты поддерживают параллельную backend/frontend работу;
- [x] ADR-0002 согласуется с этой спецификацией;
- [x] в R02 не меняется код продукта или schema базы данных.

---

## 18. Проверка

```bash
python scripts/verify_repo.py
git diff --check
```

Ручное ревью контракта R02:

- убедиться, что в публичных примерах нет секретных полей;
- проверить наличие всех четырёх режимов;
- проверить, что режим взаимодействия не моделируется как skill;
- проверить согласованность семантики hint/reveal с baseline Progress;
- убедиться, что реализация продукта не добавлена.

---

## 19. Последующие задачи реализации

После человеческой приёмки R02:

- backend реализует persistence/API contracts согласно принятой спецификации;
- frontend реализует renderers и состояния взаимодействия по версионированным mock;
- R03 формализует алгоритмы Knowledge/Progress и семантику событий, не меняя молча
  контракты взаимодействия R02.
