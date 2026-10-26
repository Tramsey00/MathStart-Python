# §17 Контракты framework adapters v1.0.0

PROPOSED; original_result, исторические task IDs, scopes, approvals, исходные PR,
замороженные manifests/pins/tests и байты сохранены. Новые ссылки на framework
находятся только здесь. [Индекс old-to-new](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R02/old-to-new-evidence.json)
связывает исходный вход со свидетельствами R02 и будущими обязательствами по реализации.
Исторические формулировки о pending R02A/R03A не означают текущий отказ: квитанция R01 D08
подтвердила комментарии Владимира от 07.10; никакое одобрение не переносится задним числом на R02.

| Original | Контракт для framework | Сохраняемые полномочия / требуемые будущие доказательства |
| --- | --- | --- |
| R02 | public DTO -> React mode dispatcher; server validation -> изолированный Python service, HTTP controller только для orchestration; без допущений о Django serializer/model | Ровно четыре режима и типизированные упорядоченные шаги; input_schema для UI и step_schema для представления, разделение raw/normalized, hint/reveal/secret, immutable bound version. I01 dispatcher остаётся только для fixture; заявление о наличии assessed runtime не делается. |
| R03 | Content topic read/reference adapter использует существующий ContentPage ID; будущие Knowledge repository и Progress evidence/replay service | 10 skills/13 рёбер prerequisite->dependent, external basic_arithmetic, Decimal ROUND_HALF_UP после каждого события, глобальные identity/replay ordering и один штраф. Таблицы ORM в будущем не создаются. Content владеет TopicSkill -> Knowledge; Knowledge не импортирует Content. |
| MS7-R02A | строгая граница FastAPI raw-body и мост cookie/session/CSRF; отдельное дополнение о доставке content/staff; явная регистрация routes | Канонические 37 операций, ограничения DTO/status, owner404, revisions, receipts/exposure/permanent source identity; сейчас реализованы только 8 API operations. Нет перехода владения OAS генератору и поведения default422/307/coercion. |
| MS7-R03A | авторитетный Assessment CompletionFact -> immutable internal DTO -> Progress mirror/replay; будущие SQLAlchemy units of work | Двойная уникальность global completion_id и attempt+skill, immutable owner/outcome/time/independent flag, доверенный server context, нейтральная история не меняет числовые показатели; нет публичного write API и выдуманного runtime. |

Будущие зависимости: content -> knowledge для mapping под владением Content; knowledge
не зависит от content; math_validation — чистый модуль; progress -> users/knowledge;
assessment -> users/content/knowledge/math_validation/solution_analyzer/progress;
solution_analyzer -> math_validation/knowledge/llm/progress service;
adaptive_practice -> чтение progress/knowledge/assessment;
ai_tutor -> чтение content/knowledge/progress/assessment/llm; llm -> infrastructure.
DAG зависимостей и проверка отрицательных циклов входят в package verifier. Это принятое
направление домена, представленное контрактом, а не импортами отсутствующих apps.

Будущий assessed acquisition: раскрытие owner/version до попытки; точный replay до revision/state;
неизменяемый снимок черновика/version/порядка шагов; постоянный guard положительного credit после финализации;
помощь, зафиксированная до финализации, лишает независимости, последующая помощь не отменяет
завершённые решения. Двойные identity R03A проверяются до scope filtering; факты требуют
полномочий server Assessment и lifecycle COMPLETED, никогда client independent_correct.
Нейтральный результат остаётся в истории; на числа влияет только проверенный ProgressEvent.
Для синтетического сравнения напрямую используйте замороженные чистые oracle; реализовывать
здесь скопированную формулу запрещено.

Байты raw input/Unicode/порядок массива сохраняются при передаче до нормализации;
неподдерживаемый синтаксис -> UNSUPPORTED, а не WRONG/misconception. Один неверный финальный ответ
не позволяет определить misconception. Синтетические обмены не выполняют target HTTP, блокировки базы данных,
renderer или LLM. Реальные тесты identity/content текущей миграции и последующие API/PG/browser-тесты V/I
являются независимыми дополнительными свидетельствами.

Старые verification IDs сопоставлены с будущими adapters в матрице: Django check ->
config/startup/routes; migration check -> metadata/Alembic drift/one head/reviewed
SQL; source/quality/integrity сохраняют полный смысл; fresh smoke -> target
fresh+bootstrap дважды+assets/SSG; текущие Node semantic tests -> React lifecycle/
browser evidence. Это передача в R03, а не переписывание Harness/CI в R02.
