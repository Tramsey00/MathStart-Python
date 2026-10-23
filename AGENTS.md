# MathStart: правила работы coding-агента

MathStart — образовательный сайт по математике. Перенос на FastAPI и React
в PR54 и консолидация PR55 завершены и приняты. Интеллектуальный учебный цикл
остаётся будущей программой. Стек и версии — в [ARCHITECTURE.md](ARCHITECTURE.md).

## Начало задания

Открой [единую очередь](docs/tasks/INDEX.md) и конкретную порученную карточку
`skills/tasks/.../SKILL.md`, затем нужные разделы [ARCHITECTURE.md](ARCHITECTURE.md)
и перечисленные в карточке источники. Для уроков используй
[стандарт переноса](docs/frontend/lesson-migration.md) и
[общий skill](skills/lesson-migration/SKILL.md). PRODUCT и domain contracts
читай по зависимости задания, не весь архив подряд. Текущие task skills
открываются явно по ссылке; каталог skills не обещает автообнаружение Codex.

Дизайн главной, каталога и учебной страницы утверждён. Не выбирать заново
палитру/шрифты/UI kits и не восстанавливать I02/I03 как образец нового UI.
MS-T001 проверяет стандарт на новом HTML-уроке о линейной функции y = kx + b.
Уже готовый React preview квадратичной функции — эталон; его runtime-интеграция
включена в MS-T006 без повторного выбора дизайна.
Старые ТЗ, 52 source cards, аудиты и персональные очереди доступны в Git и не
являются текущими заданиями. Карта действующих контрактов —
[specs/current-contracts.md](specs/current-contracts.md).

Проверь Git root, ветку, HEAD, dirty tree, remote и отношение к `origin/main`.
Сохрани чужие незакоммиченные изменения. Для MS-T001, MS-T002 и MS-T002A
действует исключение: работаем последовательно в общей ветке ui/ux, без
отдельного Issue и без новой ветки на каждую из этих трёх задач. Текущее
поручение подготовки MS-T000 продолжается в существующей agent-workflow.
Не переключать dirty checkout принудительно ради этого правила.

MS-T002A подготавливает запуск из чистого clone. После приёмки MS-T001/MS-T002
и проверки готовности локального запуска в MS-T002A пользователь отдельно
принимает этот результат и решает merge ui/ux → main. Затем проверяется clone
опубликованного main; только после него завершается приёмка всей MS-T002A и
открывается MS-T003. Публикация production сюда не входит.

Начиная с MS-T003, каждое явно порученное задание имеет GitHub Issue, отдельную
ветку от актуального origin/main после fetch и PR со ссылкой на Issue. Например,
ms-t003-grade-5. Префиксы codex/ и /codex не использовать. Если Issue/ветка/PR
задания уже существуют — продолжать их, не создавать дубли. В Issue указать scope
карточки, acceptance и ссылки на результат; assigned task включает создание
нужных Issue/ветки/PR, но не автоматический merge/закрытие Issue. Не создавать
всю очередь Issue заранее. Если GitHub недоступен, явно сообщить ограничение.
Реализация, проверки и fixes — в ветке задания основного checkout.
Не редактируй и не коммить в main, не используй reset --hard, force checkout,
force push или автоматический merge. Старые миграционные worktree и персональные
очереди завершены; не восстанавливай их для обычной работы.

## Карта

| Путь | Назначение |
| --- | --- |
| `backend/` | FastAPI, Content/Users/Staff, persistence, Alembic, schema/content CLI |
| `frontend/` | React/TypeScript, React Router prerender, account/staff, browser tests |
| `curriculum/`, `site_content/`, `static/` | Учебный контент, структура и ресурсы |
| `specs/` | Доменные/API-контракты, fixtures и preservation manifests |
| `docs/tasks/INDEX.md`, `skills/tasks/` | Единственная новая очередь и канонические задания |
| `scripts/`, `.github/workflows/` | Проверки продукта и CI |
| `deploy/` | Канонические images/Compose, [release](deploy/RELEASE.md), [recovery](deploy/RECOVERY.md) |
| `var/` | Игнорируемые окружения, приватные настройки и локальные отчёты |

Локальный сайт: [local-development](docs/local-development.md).
Проверки: [target-runtime](docs/target-runtime.md).
Принятая история: [maintenance](docs/maintenance.md).

## Реализация и инварианты

Один исполнитель, одно активное задание. Обязательных субагентов, постоянных
frontend/backend/review-агентов, персональных владельцев и распределения моделей
нет. Порядок backend/frontend выбирай по зависимостям. Не начинай следующую
карточку автоматически. Новые функции, интерфейс и игровые механики выполняются
только по отдельно порученному заданию и принятым решениям.

Перед правками проверь реальные imports и build inputs. Сохраняй данные,
авторский контент/медиа/формулы, URL/якоря, контракты и dirty fixes.
Работай связными scoped изменениями, не ослабляй проверки ради PASS.

- Модульный монолит и владение данными обязательны. Content владеет TopicSkill
  и зависит от Knowledge; обратной зависимости для этих связей нет.
- Только Progress изменяет долгосрочное знание через валидированные ProgressEvent.
  Чтение, XP/награды, Tutor, Analyzer, frontend и LLM не увеличивают mastery напрямую.
- Детерминированная математика первична. Raw input хранится отдельно от
  нормализованного; неподдерживаемый ввод не означает misconception.
- Влияющий на домен LLM output проходит schema/domain/confidence validation.
  Malformed/low-confidence output не создаёт сильный отрицательный сигнал.
  SDK — в infrastructure, prompts — versioned; обычные tests без live LLM.
- Ответы/validation secrets серверные до явного reveal. Неверный final answer
  сам по себе не доказывает misconception. Hints/reveals записываются;
  полный reveal исключает CORRECT_FIRST_TRY. Legacy self-check HTML — отдельно
  сохранённая совместимость, а не будущий assessed API.
- Сохраняй четыре режима и typed ordered steps. Изменение семантики требует
  спецификации, проверок и архитектурного ревью.
- Skill codes стабильны; Topic отличается от Skill. Prerequisite → dependent,
  без self-edges/cycles. Bootstrap не перезаписывает пользовательскую историю.
- Schema changes — reviewed Alembic migrations и fresh/upgrade PostgreSQL checks.
  Applied history не редактируется; startup не делает DDL/content/operator seed.
- Секреты, cookies и персональные данные не попадают в Git и отчёты.

Собственный Engineering Harness выведен из проекта. Codex, эти инструкции,
task skills и проверки продукта используются без него.
Legacy Django/DRF — только [отдельный pinned oracle](docs/legacy-oracle.md)
при явно необходимых сравнениях. Не устанавливай их в target окружение.
Не используй защищённый acceptance stack или исходную Django DB для tests.

## Проверки, ревью и завершение

Используй [verification skill](skills/verification/SKILL.md).
Выбор scope — [политика проверок](docs/frontend/testing-policy.md). Не запускать
весь runtime ради правки Markdown или одной кнопки. Существующий full entry:
`python scripts/verify_repo.py`; portable subset:
`python scripts/verify_repo.py --profile pure`. Pure не доказывает runtime readiness.
Полный managed lifecycle и disposable PostgreSQL/browser prerequisites — в
[target-runtime](docs/target-runtime.md). Empty, missing, skipped, timed-out и
flaky checks не равны PASS. Install/recovery и combined CI gate сохраняются;
старые результаты не подтверждают новый candidate.

Для существенной работы оставь краткий результат в карточке или PR: исходный и проверенный SHA/tree, изменения, команды/результаты, ограничения,
findings и исправления. Unknown preservation edits/deletions запрещены;
явно выведенные файлы требуют пофайловой карты, historical receipts/approvals
не переписываются.

Порядок: реализация → самопроверка → PR → отдельное ревью → исправления и
необходимая перепроверка → человеческая приёмка → решение пользователя о merge.
Самопроверка не заменяет отдельное ревью. PASS, создание PR и merge не означают
человеческую приёмку; статусы отражаются раздельно в реестре. Архитектурные и
production/provider/security решения принимает человек. Автоматическое слияние
запрещено. После передачи результата текущего поручения остановись.
