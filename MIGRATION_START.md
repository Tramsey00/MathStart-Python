# Продолжение миграции по одной задаче

Последний порядок пользователя: одна задача на отдельно инициированный запуск.
Сейчас только MS7-MIG-I02 и необходимые исправления verifier/зависимостей.
I03 и другие задачи не продолжать автоматически; весь существующий код сохранить.
Один основной исполнитель; постоянную команду backend/frontend/reviewer не запускать.
Один отдельный reviewer после готовности кандидата (GPT-6.1 Sol / medium): exact
base/head/diff, контракты, результаты и открытые findings без истории чата;
correctness, security и test gaps. Исправления проверять по delta. Полный повтор
только при существенном изменении или новой конкретной проблеме. Полная итоговая
cross-browser/visual matrix принадлежит I05; assertions сохранить. R03 target
с неизменным пустым command map не повторять, оставить pending. После docs-only
изменений не повторять полные проверки при прежних code/config/inputs.
Полные логи хранить в файлах; долгие процессы не опрашивать часто. После двух
безуспешных циклов одной причины — checkpoint и конкретный блокер.
После проверки, commit, push, remote SHA и короткого MIGRATION_HANDOFF.md
остановиться. Архитектура, данные и обязательные критерии сохраняются.
Не выполнять main merge, закрытие Issues и production deployment.
Все новые имена — без брендовых приписок.

Рабочий checkout: C:/Projects/MathStart-Python/migration-execution/integration.
Перед продолжением прочитать MIGRATION_STATE.md, MIGRATION_HANDOFF.md,
MIGRATION_AGENT.md, MIGRATION_TASKS.md, MIGRATION_VERIFICATION.md и task-ledger.
Проверить GitHub/refs, dirty files, owned процессы и последние receipts.
Не повторять bootstrap или реализацию с нуля. Исходная активация сохранена
в24d06112bcd6abcd1abad9b052de14a0a7b49e8e. Этот порядок заменяет прежнее
поручение всей программы и блоков по три задачи.
