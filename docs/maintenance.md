# Принятые миграция и консолидация

PR [54](https://github.com/Tramsey00/MathStart-Python/pull/54) принят и слит
merge commit 3a290a46d991e22269a17dde41e39f0637576071.
[Main Migration](https://github.com/Tramsey00/MathStart-Python/actions/runs/39276711652)
и [Harness](https://github.com/Tramsey00/MathStart-Python/actions/runs/39276711485)
завершились успешно. Это не означает production deployment или завершение
будущих продуктовых gates.

Основной checkout и обычная платформа: main, FastAPI/SQLAlchemy/Alembic,
PostgreSQL и React. Действующие входы: [локальный запуск](local-development.md),
[release](../deploy/RELEASE.md), [recovery](../deploy/RECOVERY.md),
[проверки](target-runtime.md), [oracle](legacy-oracle.md) и
[текущие задачи](tasks/INDEX.md). Будущая программа описана, но не реализована.

Исторические планы, traces, approvals, raw evidence и исходный PDF ТЗ
восстанавливаются по точному SHA/path из истории main, прежде всего
3a290a46d991e22269a17dde41e39f0637576071. Старые hashes/results не переписываются.
[Preservation manifest](../specs/migration/post-django-preservation.json)
перечисляет каждый выведенный или перемещённый файл. Сохранённые текущие
content/contracts/assets проверяются по фактическим bytes; неизвестные правки
и удаления отклоняются. Активный inventory, 40 parity rows и карта 12 сценариев
с negative cases остаются в specs/migration. Старый source registry из 52 карточек
доступен в Git b29a7ccdd07784cfcfd19278cbe59b30c83cd4ea по пути
specs/product/task-dispositions-v7.2.json.

Консолидация [PR55](https://github.com/Tramsey00/MathStart-Python/pull/55) слита
как `12450dfd39b51166aa5a40955ce78e40169a1cb4`, candidate —
`1ee38b286f7c0be5dd04a96113563e7b19168840`.
[Post-merge Migration](https://github.com/Tramsey00/MathStart-Python/actions/runs/39325149624)
прошла все девять jobs, включая target/image-recovery/combined, без skipped;
[post-merge Harness](https://github.com/Tramsey00/MathStart-Python/actions/runs/39325149945)
тоже прошёл. Проверки candidate и diff review сохраняют отдельные SHA/scope
от CI принятой миграции. Выведено ровно 1477 исторических оригиналов по решению
пользователя: 60,801,077 canonical blob bytes. Шесть активных inputs/verifiers
перенесены в scripts/specs. Исторические helpers требуют явных отдельных sources,
а текущие contracts/content проверяются как реальные файлы. Относительные ссылки
документации разрешаются локально либо в проверенные historical blobs.

Локальная консолидация вывела 24 зарегистрированных worktrees и 16 старых локальных
веток после проверок Git/patch/уникальных sources. Уникальная работа, private
settings, проверенные SQLite backups, пять физически восстановленных PostgreSQL
backups и проверенный Git bundle хранятся в едином внешнем backup с ограниченным
доступом, указанном в var/local/README.md. Воспроизводимые working copies,
окружения и logs не архивировались. Старые Docker resources удалены по точной
identity; два target data volumes продолжает использовать mathstart-local.
Два anonymous volumes с неустановленным назначением и общие base images/build
cache не тронуты. Физическое освобождение диска не измерялось; logical file bytes
и Docker accounting не являются такой метрикой.

Постоянный локальный сайт, существующий operator и опубликованный content
сохранены; см. [локальный запуск](local-development.md). Migration Issues 28–45
закрыты после сверки scope с PR54, его actual review и успешным main CI.
Пользователь принял платформенную адаптацию v7.2 20.10.2026; это не означает
приёмку полного product draft, будущих gates или production rollout.
Завершённые root entry point и override instructions являются только историей:
[прежний MIGRATION.md](https://github.com/Tramsey00/MathStart-Python/blob/12450dfd39b51166aa5a40955ce78e40169a1cb4/MIGRATION.md) и
[прежний AGENTS.override.md](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/AGENTS.override.md).
Эти точные Git revisions сохраняют исходный контекст, не создавая новую очередь.
Cosmetic UX issue 52 остаётся отложенной задачей; production и будущие функции
не входят в эту поддержку.

## 24.10.2026: очистка задач и источников

Поручение пользователя заменяет выбор визуального направления полноценными
задачами runtime migration. MS-T000 готовит очередь, стандарт и карту тестов;
MS-T001 и следующие остаются PLANNED. Перенос уроков, замена Identity и production
acceptance не заявляются. Старые спецификации, UX wireframes, task cards и audit
outputs удалены из checkout с точной пофайловой Git provenance в
specs/maintenance/repository-cleanup.json. Требования к будущей математике, API
и security сохранены в specs/product/learning-requirements.md.
Текущие входы — tasks/INDEX.md и frontend/lesson-migration.md. Учебный content/media,
backend Identity и runtime tests сохранены. Testing policy связывает будущие
удаления с выведенными consumers и не разрешает массово снимать защиту.
Проверка подготовки относится к документам, mappings и изменённым checkers,
а не к полной production readiness.

На предыдущем dirty candidate agent-workflow прошли: 601 проверка очереди/docs,
611 проверок requirements, preservation, 12 focused validator/retirement tests
и portable pure 5/5 групп. Первые проверки нашли проблему direct-script import
и устаревшее ожидание для moved document; обе исправлены до итогового прогона.
Frontmatter/name/placeholder checks прошли для 33 skills. Внешний quick_validate
не запустился из-за отсутствия PyYAML; зависимости не устанавливались.
Full target/PG/browser/production проверки не запускались. Commit, push, merge
main и выполнение Task 1 не проводились. Эти результаты относятся к прежнему
candidate и не заменяют проверку последующих переводов и workflow-изменений.

## Локальная передача команде перед классами

MS-T001, MS-T002 и MS-T002A выполняются в ui/ux без отдельных Issue/веток.
MS-T002A сначала подтверждает запуск из чистого clone ui/ux; готовность локального
запуска проходит review и человеческую приёмку перед решением о merge. После
merge проверяется clone опубликованного main и завершается MS-T002A. MS-T003
начинается только с проверенного опубликованного baseline. Далее каждое задание имеет GitHub Issue,
отдельную ветку от origin/main без codex/ и PR. Публичный deploy не требуется.

## Перевод и проверка уточнённой очереди

Оставшиеся проектные Markdown переведены на русский; проверка охватывает все 98
действующих документов. Technical terms, команды, identifiers, code blocks,
исторические receipts и исходные лицензии сохранены. I02/I03 явно обозначены
как исторический UI. Для переводов зафиксированы точные source/after hashes;
числа, code и ссылки будущих требований сверены с исходными разделами ТЗ в Git.
Субагенты GPT-6 Luna medium выполнили перевод отдельных групп; отдельное review
обнаружило и помогло устранить цикл приёмки MS-T002A/merge. Review адаптера
provenance не выявило обхода проверки явно разрешённых изменений.

На dirty tree ветки agent-workflow при HEAD
b29a7ccdd07784cfcfd19278cbe59b30c83cd4ea прошли: 612 проверок очереди/docs,
622 проверки источников, preservation, 10 Python tests валидаторов,
10 frontend tests сохранности и npm run check:contracts. Portable pure прошёл
5/5 групп в существующем var/docs-cleanup/venv. Первый pure-прогон системным
Python завершился FAIL из-за отсутствия jsonschema; код ради этого не менялся,
зависимости не устанавливались. Повтор использует подготовленное окружение.

Добавлена команда dev:design и документирован отдельный preview на 5173.
Проверена её справка; чистый clone и полный новый runtime ещё не проверены —
это результат будущей MS-T002A. Full target/PG/browser/production не запускались.
Изменения остаются локальными: commit, push, merge и выполнение MS-T001 не проводились.

## Уточнение учебного пилота MS-T001

По уточнению пользователя пробный перенос проверяет новый HTML-урок
«Линейная функция y = kx + b. График линейной функции» (7 класс). Квадратичная
функция уже собрана в React preview и остаётся эталоном; её runtime-интеграция
закреплена за MS-T006 без повторного выбора дизайна. Карточки, реестр, стандарт,
общий skill и карта тестов согласованы с этим разделением. URL линейного урока
назначается при реализации; существующий /materials/8-algebra-32 сохранён.

Область проверки этой правки — очередь, ссылки, источники и preservation через
check_workflow_docs.py, check_product_source.py и check_migration_preservation.py.
Проверки runtime/БД/browser для изменения описаний не требуются и не запускались.
Реализация урока, изменение его исходников и commit/push не выполнялись.
