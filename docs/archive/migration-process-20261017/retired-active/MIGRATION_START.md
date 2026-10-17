# Старт или продолжение общей задачи

Передать следующий текст в новом чате, открытом в рабочем migration checkout.
Если открыт исходный проект, указанный путь ниже приведёт к существующему checkout.

```text
Продолжи единую миграцию MathStart до проверенного release-кандидата.
Рабочий checkout: C:/Projects/MathStart-Python/migration-execution/integration.
Прочитай там AGENTS.md, MIGRATION_AGENT.md и MIGRATION_STATE.md; это действующие
инструкции. Прежние ограничения «только I02», «по одной/две/три задачи» и
постоянная команда агентов отменены. Сохрани весь существующий код и dirty fixes.

Работай одним основным исполнителем по всему объёму migration ТЗ. Не начинай
I02/V04 или bootstrap заново. Законченные R/V/I — контроль полноты, не повод
останавливаться или ждать нового поручения. Будущие учебные функции не реализуй.
Используй один отдельный final reviewer после готовности кандидата; раньше
делегируй лишь конкретный существенный риск с коротким контекстом.

Начни с actual Git/dirty inventory и узкой проверки сохранённого Linux venv fix.
Дальше самостоятельно выбирай работу по реальным dependencies. Проверки:
reproducer -> unit/integration -> full final matrix. Не повторяй неизменный
prerequisite FAIL и не выдавай skipped target за завершённую миграцию.
Сохраняй короткий актуальный STATE и существующие ledgers. Не читай весь архив
на каждом продолжении. При лимите/внешнем блокере зафиксируй точный next step.

Разрешаю scoped commits, push migration refs, disposable tests и draft final PR.
Все новые имена без брендовых приписок. Не выполняй force-push/main merge,
закрытие Issues, production writes/deployment или сообщения другим людям/чатам.
Финиш: READY_FOR_HUMAN_ACCEPTANCE с фактическим CI,review,запуском,docs/rollback
и отдельным списком HUMAN_PENDING действий. Не объявляй MIG-G4 до их исполнения.
```

В другом клоне заменить только checkout path на его Git root; остальной процесс тот же.
