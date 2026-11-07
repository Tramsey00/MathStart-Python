# SPEC MS7-R03A: Дополнение CompletionFact / progress-v1.1

- **Статус:** Реализуемый кандидат контракта; ожидается независимая человеческая приёмка
- **Владелец:** Руслан; reviewer / Task Approver: Владимир
- **Последнее обновление:** 2026-10-02
- **Issue:** [#18](https://github.com/Tramsey00/MathStart-Python/issues/18)
- **ADR:** [ADR-0005 / D-021](../../docs/adr/ADR-0005-completion-fact.md), Proposed
- **План:** [активная MS7-R03A](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/exec-plans/active/MS7-R03A-completion-fact.md)
- **Trace:** [MS7-R03A](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/agent-traces/MS7-R03A.md)
- **Прямая CONTRACT dependency:** [замороженный R03](R03-progress-contract.md)
- **Числовой норматив:** [BASELINE-v1](BASELINE-v1.md), без изменений
- **Канонические полномочия:** требования v7.1, предоставленные владельцем задачи; исправленный срок §20 05.10.2026 заменяет старый Target deadline 02.10

## 1. Цель и scope

Завершённая attempt может войти в recent-ten без выдумывания ProgressEvent,
отрицательного evidence или misconception. Это additive пакет чистого контракта:
schema, synthetic fixtures, reference и tests. Django models, migrations, DB tables,
runtime services, HTTP endpoints, изменения auth/frontend, вызовы providers или dependencies
не добавляются. Режимы exercises и замороженные контракты R02/R02A/R03, OpenAPI,
references, tests и исторические fixtures остаются без изменений. Manifest candidate R02A
обновляет только hash производного CI workflow для разрешённого нового шага, сохраняя все
остальные hashes и маркер pending acceptance.
Историческое наблюдение об отсутствующем PDF и устаревшие маркеры PENDING R02A —
неблокирующая уборка; выводов об осмотре PDF или приёмке не делается.

## 2. Владение и неизменяемая граница

Assessment владеет авторитетным CompletionFact. Progress владеет зеркалом/replay completion
и не импортирует ORM Assessment:

    Assessment CompletionFact -> immutable DTO -> Progress completion mirror

Целевые поля Assessment неизменяемы: completion_id, attempt, skill, outcome,
independent flag, completed_at и policy_version; UNIQUE(attempt, skill).
В DTO используются ссылки attempt_id/skill_id и имя флага independent_correct.
Дополнительный user_id связывает владельца; он не заменяет ни одно из ограничений identity.
Этот internal DTO не имеет публичного write API или payload с answer/validation secrets.

Schema: [completion-fact-v1.schema.json](schemas/completion-fact-v1.schema.json).
Предпочтительное описательное имя файла из запроса этапа реализации заменяет placeholder
`completion-v1.schema.json` в прежнем плане. Имена fixtures остаются как запланировано.
Версия schema artifact v1 отличается от записываемого поля policy; completion_version
не является полем envelope.

| Обязательное неизменяемое поле | Контракт |
| --- | --- |
| completion_id | Глобально уникальный канонический UUID в нижнем регистре; назначается Assessment и никогда не генерируется повторно при доставке/retry |
| user_id | Непустая ссылка на владельца |
| skill_id | Непустая ссылка Skill; pilot oracle сверяет код с замороженным перечнем pilot |
| attempt_id | Непустая неизменяемая ссылка source; native server UUID/FK binding относится к V08, synthetic legacy references остаются поддержанными |
| outcome | Только CORRECT, WRONG, UNSUPPORTED или INDETERMINATE |
| independent_correct | Строгий boolean; true требует CORRECT и отдельно подтверждённую frozen eligibility |
| completed_at | RFC3339 с timezone, заглавной T/Z либо валидным signed offset, не более шести дробных знаков; корректная календарная дата; канонические UTC microseconds |
| policy_version | Только progress-v1.1 |

Schema закрыта (`additionalProperties=false`), содержит все восемь обязательных fields
и проверяет форму/enum/точность. Для календарной проверки использовать format checker date-time.
Tests предоставляют локальный datetime checker без сетевых/необязательных format packages.
Domain oracle повторно использует замороженный `utc_instant`, дополнительно отклоняет
неверные диапазоны RFC3339 offset и проверяет известные skills, independence и identities.
Точность времени не обрезается молча; отсутствующий flag/outcome не получает значения по умолчанию.

CompletionFact имеет policy_version=progress-v1.1; замороженный ProgressEvent —
policy_version=progress-v1; native final state reducer_version=progress-v1.1.
Другие числовые policies не регистрируются и не подставляются молча.

## 3. Двойная identity, конфликт и атомарный приём

До фильтрации при проекции действуют оба ограничения: глобальная уникальность completion_id
и постоянная уникальность source `(attempt_id, skill_id)`. Namespace user/policy/receipt
не может скрыть совпадения. Факты одной attempt по разным skills должны иметь одинаковые owner
и terminal instant. Source identity сохраняется дольше expiry receipt.

Сравнивать все канонические поля после нормализации UTC:

- тот же полный канонический payload -> идемпотентный no-op, одна запись mirror;
- повторный completion_id с изменённым source/payload -> IdentityConflict;
- повторные attempt/skill с новым completion_id либо любым изменённым неизменяемым полем -> IdentityConflict;
- неподдерживаемая policy/некорректный DTO -> ContractError, принятые данные не меняются.

Различные текстовые представления одного момента времени могут быть точным каноническим retry.
Принятые факты никогда не перезаписываются. `ingest_completion_fact` возвращает отделённые
от исходника предложенные mirror, projection и флаг duplicate; при отказе входы вызывающего
не меняются. Для target ingestion user/skill candidate должен совпадать с scope NumericalReplay.
Полный replay может включать другие scopes; оба ограничения всё равно глобальны до выбора
skill пользователя. На одну attempt/skill допускается не более одной записи recent.

## 4. Полномочия и lifecycle

`validate_completion_fact` проверяет только форму/domain content и не предоставляет полномочий.
Для непустого mirror replay/ingestion необходим отдельно переданный trusted context:

    {
      "context_version": "assessment-completion-v1",
      "records": [
        {
          "fact": "<full authoritative eight-field DTO object>",
          "attempt_state": "COMPLETED",
          "mapped_skill_ids": ["negative_numbers"]
        }
      ]
    }

Placeholder fact выше обозначает объект, а не wire string. Требуются точное совпадение DTO
с исходной записью, состояние завершения и явный mapping связанной версии. Неизвестные поля/
версия context, отсутствующие полномочия, изменённые owner/outcome/independence/time/policy
или unmapped skill приводят к отказу fail-closed. Context — вход fixture/service, не дополнительные
сохранённые поля CompletionFact и не доказательство аутентификации client. Pure oracle может
сравнить только переданные records; V08 должен установить подлинную server provenance,
authorization, FK/owner binding, version/snapshot и транзакционную finalization.
Client flags не могут это разрешить.

Native assessed attempts в состоянии COMPLETED создают facts. STARTED, SUBMITTED/202,
ABANDONED и SELF_CHECK REVIEWED — нет. CORRECT, WRONG, UNSUPPORTED и INDETERMINATE —
outcomes, а не lifecycle states. Интеграция R02A фиксирует eligibility при finalization
под exposure/positive-credit: ожидающая помощь влияет на результат, последующая помощь не
отменяет его, повторный засчитанный CORRECT остаётся нейтральным. Пакет tests объединяет
неизменённые serial fixtures R02A для проверки записанных решений; он не реализует второй
алгоритм eligibility, producer источника или выдачу credit.

## 5. Recent-ten и status

Recent-ten строится исключительно из mirror Progress. Выбрать факты user/skill,
отсортировать по возрастанию `(completed_at канонический UTC, attempt_id лексикографический
с учётом регистра)`, взять последние десять, вернуть IDs по возрастанию и однократно просуммировать
true `independent_correct` для каждого оставшегося source. Нейтральные facts занимают места.
Фильтр только положительных ответов, двойной подсчёт событий и временной decay запрещены.
Старые facts вне окна сохраняются.

Outcome обязателен независимо от нейтральности. Нейтральность означает отсутствие полномочий
менять числовую проекцию; даже сам по себе факт независимого CORRECT не меняет числа.
UNSUPPORTED/INDETERMINATE и повторный CORRECT создают историю без фиктивных WRONG/
DIAGNOSTIC_WRONG events.

Использовать неизменённый `status_for`:

1. `evidence_count == 0` -> NOT_STARTED;
2. `mastery >= 80`, `confidence >= 60`, recent independent >= 3 -> MASTERED;
3. `mastery < 50`, `confidence >= 30` -> WEAK;
4. иначе LEARNING.

Канонический v7.1 уже допускает replay, меняющий только status. Более новый нейтральный fact
может вытеснить независимую attempt и изменить MASTERED -> LEARNING, сохранив mastery,
confidence, evidence_count и last_updated побайтно при фиксированном логе events.
Только история facts сохраняет нулевые числовые значения/count, null time и NOT_STARTED.

## 6. Числовой replay и доставка задним числом

`NumericalReplay(events, user_id, skill_id)` проверяет/копирует полный лог events и один раз
вызывает замороженный R03 replay. Immutable JSON-backed cache отделяет содержимое от входов/
результатов вызывающего. Его результат включает буквальные v1 diagnostics/snapshots.
Числовые константы/алгоритм в R03A не копируются.

`replay_v1_1` строит этот cache и объединяет его с полным проверенным mirror.
`replay_completion_facts` и `ingest_completion_fact` используют `NumericalReplay`;
позднее получение fact не запускает numerical replay. Они проверяют authority/coexistence,
вычисляют recent-ten и обновляют только итоговый status/reducer_version.
Подлинное позднее событие явно создаёт новый cache с замороженным порядком events
`(occurred_at, event_id, policy_version)`, затем объединяет его с mirror.

Для фиксированных events любая допустимая доставка/permutation facts сохраняет числовые значения,
`evidence_count`, `last_updated`, все event IDs, numerical snapshots/deltas и точки repeat reset.
Независимые facts никогда не очищают misconception counters. Только qualifying ProgressEvent
сбрасывает их в порядке occurred, даже если fact пришёл с задержкой.

Факты, полученные позднее, могут войти в/вытеснить из recent-ten и изменить independent count/status.
Между completed_at и occurred_at не требуется взаимного порядка. Полные принятые наборы дают
идентичный результат при любом порядке доставки; конфликтующие наборы отклоняются в любом
порядке, а не объявляются общей успешной проекцией.

Native output содержит шестипольное state, `recent_window`,
`ordered/applied/nonprojecting_event_ids`, `legacy_snapshots` и `completion_gaps`.
`legacy_snapshots` — явно буквальные v1 compatibility diagnostics, а не native history или
snapshots состояния на момент completion. `completion_gaps` перечисляет scoped attempts
с inline completion attestation, но без записи в mirror; эти сведения не дают членство в окне.

## 7. Сосуществование с ProgressEvent

Замороженные event envelopes, identities, validator и отклонение duplicate event log не меняются.
Ненулевое inline completion time должно совпадать с отдельным fact после нормализации UTC;
отсутствующее время у допустимых negative/reveal events не считается конфликтом.
Events сохраняют требуемые замороженным контрактом inline attestations, которые не могут
наполнить native recent-ten. Отсутствие доставки fact может сосуществовать с числовой проекцией.

Для общей attempt проверяется совпадение owner. `CORRECT_FIRST_TRY` и самостоятельный
`DIAGNOSTIC_CORRECT` требуют соответствующего итогового fact CORRECT/true; верный ответ с help
требует CORRECT/false; `DIAGNOSTIC_WRONG` требует WRONG/false. Неверные промежуточные шаги
не определяют итоговый outcome. Более поздний reveal не отменяет зафиксированную independence.
Противоречия атомарно отклоняются, события не выдумываются.

## 8. Явный legacy import и parity исполнения

Замороженные v1 entry points/results остаются буквальными историческими oracle.
Native replay не импортирует inline completion автоматически. `import_progress_v1_completions`
требует context_version=legacy-completion-v1 с явными source DTOs, mapping и
`attempt_state=LEGACY_COMPLETION`. Это состояние обозначает происхождение совместимости,
а не новое native lifecycle state или outcome. Stable ID/outcome берутся из этих явных
версионированных metadata, никогда из неверного шага, reveal или false flag.

Importer проверяет frozen replay, сопоставляет переданные source DTO с ненулевыми inline
completion sources/times/owners и independence, выведенной из frozen events, затем зеркалирует их.
Недостающая metadata приводит к отказу; вызывающий может явно оставить неизменённую v1 entry point.
Дополнительные строки context не дают неявной истории. Legacy synthetic IDs/credit semantics
не подгоняются задним числом под native правила R02A.

[progress-v1.1-parity.json](fixtures/progress-v1.1-parity.json) закрепляет SHA-256 замороженного
fixture и все три case IDs, с явными authoritative synthetic metadata, включая reveal-only
INDETERMINATE. Этот outcome передаётся, а не выводится. Все три арифметических случая также
остаются в executable parity coverage. Tests сверяют буквальное старое ожидаемое state,
native числа/status/time, эквивалентное окно/count, IDs/order/application events и каждый
legacy snapshot. Отличается только native `reducer_version`; для эквивалентных полученных наборов
`completion_gaps` пуст.

## 9. Artifacts, tests и gate

- [completion-v1-cases.json](fixtures/completion-v1-cases.json): все 32 именованных cases плана,
  общие synthetic datasets и явные variants/delivery/context inputs.
- [completion-v1-invalid.json](fixtures/completion-v1-invalid.json): 33 cases некорректной
  формы/domain; `schema_invalid` разделяет отказ формы и domain.
- Файл parity выше: три замороженных потока и три арифметических случая.
- [Pure reference](../../scripts/r03a_contract_reference.py) и
  [независимые assertions](../../tests/test_r03a_contract.py).

Обязательные checks: R03A, неизменённые suites R03 и R02A; verify_repo.py; pip check;
makemigrations --check --dry-run; git diff --check и scoped review. CI добавляет шаг контракта
R03A рядом с существующим R02A, не меняя канонический selection. Configuration/local checks
не являются успешным GitHub CI или доказательством PostgreSQL persistence. Trace записывает
фактические результаты и ошибки, не выводы о приёмке.

Для приёмки нужны все cases, изоляция dual-key/owner, обязательные outcomes, UTC ordering,
окно <=10, поздние permutations, отсутствие фиктивных events, нейтральность cached numerical,
явная проверка вытеснения `100.00/67.00/11 MASTERED -> LEARNING`, изоляция repeat/reset и полный
frozen fixture parity. Независимый human gate остаётся PENDING; ADR остаётся Proposed, plan активен,
Issue открыт. На этом разрешённом этапе push/PR/merge не выполняются. Provenance/FKs V08,
долговечная доставка, locking, backfill и свидетельства migration/fresh-install остаются
ограничениями downstream.
