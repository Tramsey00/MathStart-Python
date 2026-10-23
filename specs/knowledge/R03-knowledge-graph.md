# SPEC R03: Pilot Knowledge Graph `pilot-v1`

- **Status:** Accepted
- **Owner:** Ruslan; backup Vladimir
- **Related issue:** https://github.com/Tramsey00/MathStart-Python/issues/6
- **Related ADR:** `docs/adr/ADR-0003-knowledge-progress-semantics.md`
- **Related plan:** `docs/exec-plans/active/R03-knowledge-progress-contract.md`
- **Fixtures:** `fixtures/pilot-skills-v1.json`, `fixtures/pilot-dependencies-v1.json`

## Область действия и владение

Knowledge владеет стабильными атомарными Skills и направленными отношениями предварительных условий. Content владеет Topics и будущими связями Topic-to-Skill. `interaction_mode` упражнения определяет поведение UX/validation и не является Skill. Контракт задаёт факты каталога пилота под управлением repository и чистую валидацию; он не создаёт Django model, FK, migration, management command или runtime seed.

Текущая абстракция темы под владением Content — `ContentPage` с `page_type=topic`. Будущая ссылка `TopicSkill` должна указывать на эту абстракцию Content и стабильный код/reference Skill, не создавая дублирующий источник Topic. Конкретная схема FK/migration относится к последующей задаче реализации.

## Канонический перечень

Версия графа `pilot-v1` содержит ровно следующие десять кодов Skill:

1. `integer_number_line`
2. `negative_numbers`
3. `sign_rules_add_sub`
4. `sign_rules_mul_div`
5. `distributive_property`
6. `expand_parentheses`
7. `combine_like_terms`
8. `equation_balance`
9. `linear_one_step`
10. `linear_parentheses`

Код — стабильный идентификатор предметной области; отображаемое имя может меняться без изменения идентичности графа. Fixture перечисляет каждый код ровно один раз. Повторный или неизвестный код недопустим. Код режима взаимодействия нельзя включать как Skill.

`basic_arithmetic` — предварительное условие **для входа** в пилот, а не узел `pilot-v1`. В fixture навыков он представлен метаданными `external_prerequisite` со значениями `scope = pilot_entry` и `representation = outside_skill_dependency`. Он не должен присутствовать в массиве `skills` или на любом конце ребра. Будущий компонент onboarding/diagnostic может определять право входа по явному контракту; этот граф не создаёт для него фиктивную ссылку Skill или состояние учащегося.

## Утверждённые рёбра

Каждая строка задаёт `prerequisite -> dependent` с весом `1.0`:

| Предварительное условие | Зависимый навык |
| --- | --- |
| `integer_number_line` | `negative_numbers` |
| `negative_numbers` | `sign_rules_add_sub` |
| `negative_numbers` | `sign_rules_mul_div` |
| `sign_rules_add_sub` | `distributive_property` |
| `sign_rules_mul_div` | `distributive_property` |
| `distributive_property` | `expand_parentheses` |
| `sign_rules_add_sub` | `combine_like_terms` |
| `expand_parentheses` | `combine_like_terms` |
| `combine_like_terms` | `equation_balance` |
| `equation_balance` | `linear_one_step` |
| `linear_one_step` | `linear_parentheses` |
| `expand_parentheses` | `linear_parentheses` |
| `combine_like_terms` | `linear_parentheses` |

В `pilot-v1` ровно 13 уникальных рёбер. Топологический порядок может быть неоднозначным, но в каждом допустимом порядке предварительное условие стоит раньше зависимого навыка. Саморёбер и циклов нет.

## Детерминированный запрос предков

Запрос `ancestors(skill_id, max_depth=2)` выполняется по проверенному графу `pilot-v1`, не меняя направления сохранённых рёбер. Поиск идёт от зависимого Skill к его предварительным условиям. На глубине 1 находятся непосредственные предварительные условия; на глубине 2 — предварительные условия этих непосредственных предшественников. Возвращайте каждый код Skill один раз на его **минимальной** глубине в виде `(skill_code, depth)`: сначала по возрастанию глубины, затем лексикографически по коду. Skill, отсутствующий в `pilot-v1`, отклоняется. Для этого пилота `max_depth` может быть равен 0, 1 или 2; значение 0 возвращает пустой результат, а недопустимые и большие значения отклоняются. `basic_arithmetic` — внешние метаданные входа, поэтому он никогда не возвращается как предок Skill.

Для `linear_parentheses` глубина 1 содержит `combine_like_terms`, `expand_parentheses`, `linear_one_step`; глубина 2 содержит `distributive_property`, `equation_balance`, `sign_rules_add_sub` в указанном детерминированном порядке. Если Skill достижим несколькими путями, выбирается минимальная глубина.

## Контракт проверки

Перед принятием графа-кандидата или его использованием для будущего seed полностью проверьте его:

1. требовать совпадения `graph_version = pilot-v1` в обоих fixtures;
2. требовать ровно десять одобренных уникальных кодов Skill; `basic_arithmetic` и код режима не допускаются;
3. требовать внешние метаданные предварительного условия в точности как описано выше;
4. требовать все 13 одобренных пар рёбер, каждая встречается один раз, обе вершины есть в перечне Skill, числовой вес каждой равен 1.0;
5. отдельно отклонять повтор ребра, неизвестную/отсутствующую ссылку skill, self-edge или cycle с ясным описанием причины отказа;
6. возвращайте детерминированный топологический обход (сортируйте готовые узлы по коду) для проверки и будущего чтения.

Универсальный валидатор DAG также обрабатывает намеренно недопустимые тестовые графы, чтобы ошибки повтора/неизвестного кода/саморебра/цикла проверялись отдельно от строгой проверки перечня `pilot-v1`. Архивный или неактивный Skill нельзя удалять, если на него ссылаются исторические свидетельства; жизненный цикл и ограничения БД определяются будущим контрактом реализации.

## Приёмка и проверка

`scripts/r03_contract_reference.py` и `tests/test_r03_contract.py` должны загружать JSON fixtures и проверять точный перечень, рёбра, их направление и веса, внешнее предварительное условие, случаи недопустимых графов и запрос предков глубины 2. Пока эти файлы являются fixtures спецификации, а не входом runtime `seed_data/knowledge/`. Исходники R01/R02 и исторические свидетельства не переписываются.
