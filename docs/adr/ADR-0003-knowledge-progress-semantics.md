# ADR-0003: Семантика пилотного графа знаний и ProgressEvent

- **Status:** Accepted
- **Date:** 2026-09-24
- **Decision owner:** Ruslan; backup Vladimir
- **Related issue:** https://github.com/Tramsey00/MathStart-Python/issues/6
- **Related plan:** `docs/exec-plans/active/R03-knowledge-progress-contract.md`
- **Related specs:** `specs/knowledge/R03-knowledge-graph.md`, `specs/progress/R03-progress-contract.md`
- **Supersedes:** the `KnowledgeEvent` name in current architecture wording; no event data or numerical rule is replaced

## Контекст

R01 сохранил алгоритм прогресса MathStart v3.1 Progress Algorithm v1 без изменений в `specs/progress/BASELINE-v1.md`. R02 установил границы упражнений, подсказок, раскрытия ответа и проверки. R03 должен обеспечить воспроизводимость пилотного графа и проекции событий до появления persistence в Django. Человек, проводивший ревью R03, одобрил приведённые ниже решения; этот ADR фиксирует их для итоговой проверки контракта.

## Решение: объективный пилотный граф

Каноническая версия графа — `pilot-v1`. Она содержит ровно десять стабильных Skill codes из `specs/knowledge/fixtures/pilot-skills-v1.json` и ровно тринадцать связей из `specs/knowledge/fixtures/pilot-dependencies-v1.json`. Вес каждой связи — 1.0; направление — **prerequisite -> dependent**. Граф является DAG. Дублирующиеся связи, ссылки на отсутствующие skills, связи навыка с самим собой и циклы недопустимы.

`basic_arithmetic` — внешнее предварительное условие для входа в пилот. Это не один из десяти Skills версии `pilot-v1`, и он не может быть конечной точкой `SkillDependency`. Внешнюю возможность входа необходимо представлять отдельно, без висячих ссылок на skill. `interaction_mode` остаётся метаданными Assessment и никогда не является Skill.

Запрос предков пилота из FR-16 проходит по сохранённым связям в обратном направлении — от dependent к prerequisite — на глубину 2. Он возвращает каждый код на минимальной глубине в детерминированном порядке `(depth, code)` и отклоняет неизвестный Skill. Направление сохранённых связей остаётся prerequisite -> dependent.

Topic и Skill — разные понятия. R03 ссылается на принадлежащую Content абстракцию темы, сейчас представленную как `ContentPage(page_type=topic)`, и не создаёт отдельную модель Topic. Будущая связь `TopicSkill` принадлежит Content. Точная схема Django FK/persistence отложена до последующей задачи реализации.

## Решение: одно каноническое событие прогресса

`ProgressEvent` — единственное актуальное название сохраняемого события-доказательства прогресса. Формулировка `KnowledgeEvent` в одобренных исторических материалах заменена и является лишь прежней терминологией, **а не** вторым типом события, моделью, журналом или источником истины. Только Progress может изменять `UserSkillState` посредством принятых и проверенных `ProgressEvent`. Просмотр упражнения, Tutor, Analyzer, frontend или LLM provider не могут напрямую записывать проекцию.

Progress v1 сохраняет **без изменений** все числовые эффекты, формулу mastery, коэффициенты сложности, предел повторов и пороги статусов из `specs/progress/BASELINE-v1.md`. Этот ADR не вводит заменяющую формулу. Контракт R03 задаёт принятые операционные правила:

- evidence_count includes accepted self-report, correct, wrong, misconception, and diagnostic events, but excludes `ANSWER_REVEALED`;
- confidence adds its baseline delta directly and is clamped to 0..100; difficulty and repeat multipliers apply only to mastery;
- status uses ordered precedence: no evidence, mastered threshold, weak threshold, then learning;
- self-report initializes to 60/15 at most once before assessed evidence; later/duplicate self-report cannot project;
- the recent window is the last ten completed attempts per user/skill; first-try and unassisted diagnostic correct attempts can qualify as independent;
- confirmed misconception repeat is keyed by user, skill, and misconception code, using 1.0, 1.25, then 1.5; an independent correct attempt for the skill resets the repeat state;
- numeric difficulty 1-2/3/4 and R02's easy/medium/hard strings normalize to the same baseline bands, with no default for invalid/missing assessed difficulty;
- each accepted event calculates, clamps, then uses Decimal `ROUND_HALF_UP` to two places before persisting the projection;
- `event_id` and the attempt/skill/event-kind/evidence-ref source tuple enforce idempotency; exact retry is a no-op and conflicting payload is rejected;
- one evidence unit emits one normalized negative `ProgressEvent`: a confirmed `MISCONCEPTION_DETECTED`, otherwise `WRONG_ATTEMPT`; a same-evidence pair is rejected, while raw Assessment/Analyzer facts may remain outside Progress;
- replay sorts by `(occurred_at, event_id, policy_version)`, applies each event using its recorded policy version, and reprojects a user/skill after a valid late event.

Канонические поля `UserSkillState`: `mastery`, `confidence`, `evidence_count`, `status`, `last_updated` и `reducer_version`. В R03 для `reducer_version` устанавливается `progress-v1`, `last_updated` изначально равен null, а затем получает `occurred_at` последнего проецирующего события в порядке replay. Это соответствует Technical Specification; метка `last_evaluated_at` из старой транскрипции baseline не вводится как второе поле состояния. Неизменяемый факт Assessment `completed_at` может быть раньше или позже `occurred_at` события `ProgressEvent`; ограничения задают только нормализация с часовым поясом и согласованность attempt/skill.

Один и тот же неизменяемый журнал событий всегда должен воспроизводить один и тот же `UserSkillState`. Чистая проверка на Python из R03 проверяет этот контракт без моделей Django, database persistence или работающего LLM.

## Альтернативы и последствия

Вариант с `basic_arithmetic` как незаведённой конечной точкой связи отклонён, поскольку он нарушал бы referential integrity. Вариант с ним как одиннадцатым узлом пилота отклонён утверждённым ограничением в десять skills. Обратное направление связей меняло бы на противоположное направление запросов на исправление пробелов. Сохранение `KnowledgeEvent` и `ProgressEvent` как двух отдельных актуальных понятий отклонено: одно действие могло бы учитываться дважды или воспроизводиться непоследовательно.

Контракт теперь требует идентификатор события, исходные факты, неизменяемую версию политики, детерминированный порядок и метаданные завершённой попытки. При дальнейшей работе с Django нужно выбрать схему, транзакции, concurrency, миграции и детали PostgreSQL, не меняя эту семантику. Bootstrap каталога, управляемый репозиторием, никогда не должен перезаписывать исторические данные об обучении.

## Проверка и решение человека

Набор проверок контракта R03 должен охватывать граф и каждое приведённое выше правило Progress; полная проверка репозитория остаётся обязательной. Этот ADR не заявляет о проверке persistence в runtime. Итоговый human contract gate R03: ACCEPTED. Закрытие R03 ожидает слияния PR в main. Официальная отправка C-16 требует отдельного решения человека.
