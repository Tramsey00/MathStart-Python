# Алгоритм Progress v1 — baseline MathStart v3.1

- **Статус:** Baseline перенесена в документ
- **Источник:** MathStart Technical Specification v3.1, раздел 12 — Progress Engine
- **Домен-владелец:** Progress
- **Последующая задача:** R03 — формализовать, реализовать и протестировать существующий baseline
- **Связанные документы:** разделы 11-14 в `PRODUCT.md` и разделы 17-18 в `ARCHITECTURE.md`

## Область действия и полномочия

В этом файле записан уже принятый алгоритм MathStart v3.1. Он не предлагает новый
алгоритм и не меняет его значения. R03 формализует, реализует и тестирует этот baseline;
R03 не изобретает алгоритм на замену.

Изменение формулы, значений событий, коэффициентов сложности, коэффициента повторения
или порогов статуса требует ADR и unit tests.

## UserSkillState

| Поле | Baseline |
| --- | --- |
| `mastery` | 0..100 |
| `confidence` | 0..100 |
| `evidence_count` | Количество свидетельств |
| `status` | `NOT_STARTED` \| `LEARNING` \| `WEAK` \| `MASTERED` |
| `last_evaluated_at` | Время последней оценки (UTC) |

## События знания v1

| Событие | Влияние на mastery | Влияние на confidence | Семантика baseline |
| --- | --- | --- | --- |
| `SELF_REPORTED_KNOWN` | инициализация mastery = 60 | confidence = 15 | Самоотчёт, не продемонстрированное знание |
| `CORRECT_FIRST_TRY` | delta mastery = +6 | свидетельство confidence = +5 | Самостоятельное решение без hint/reveal |
| `CORRECT_AFTER_HINT` | delta mastery = +3 | свидетельство confidence = +4 | Верное решение после подсказки |
| `WRONG_ATTEMPT` | delta mastery = -2 | свидетельство confidence = +3 | Слабое отрицательное свидетельство; типично для неверного `FINAL_ANSWER` |
| `MISCONCEPTION_DETECTED` | delta mastery = -5 | свидетельство confidence = +5 | Сильный сигнал конкретной подтверждённой ошибки |
| `ANSWER_REVEALED` | delta mastery = 0 | delta/свидетельство confidence = 0 | Раскрытие ответа не свидетельствует о знании |
| `DIAGNOSTIC_CORRECT` | delta mastery = +8 | свидетельство confidence = +8 | Верный результат диагностики |
| `DIAGNOSTIC_WRONG` | delta mastery = -6 | свидетельство confidence = +8 | Неверный результат диагностики |

## Расчёт mastery

```text
new_mastery =
clamp(
    old_mastery
    + base_delta * difficulty_coeff * repeat_coeff,
    0,
    100
)
```

| Сложность | `difficulty_coeff` |
| --- | --- |
| `easy` | 0.8 |
| `medium` | 1.0 |
| `hard` | 1.2 |

При повторном подтверждённом misconception отрицательный `repeat_coeff` может
увеличиваться, но не более чем до 1.5.

## Свидетельства, статусы и агрегация темы

- Confidence растёт в зависимости от количества и качества свидетельств.
- В MVP временного decay нет.
- `NOT_STARTED`: `evidence_count = 0`.
- `WEAK`: `mastery < 50` и `confidence >= 30`.
- `MASTERED`: `mastery >= 80`, `confidence >= 60` и не менее 3 недавних независимых верных попыток.
- `LEARNING`: любое другое состояние при наличии свидетельств.
- `TopicMastery` — взвешенное среднее `SkillMastery` с весами `topic_skills.importance`.

## Дополнительные правила

- После раскрытия ответа текущая попытка не может выполнить условие независимого верного ответа.
- Неверный `FINAL_ANSWER` без свидетельств по шагам/домену НЕ ДОЛЖЕН приводить к
  `MISCONCEPTION_DETECTED` на основании предполагаемой причины.
- Только Progress обновляет долгосрочное состояние знания через проверенные события знания.
  Создание событий должно оставаться объяснимым и идемпотентным.
