# MathStart: текущий FastAPI/React runtime

Это versioned руководство текущего runtime. Корневые инструкции описывают текущую платформу; исходные версии и
исторические digest manifests сохранены в Git. См. [oracle](legacy-oracle.md). [MIGRATION.md](../MIGRATION.md) фиксирует итог
технически завершённого переноса и ожидающую human acceptance, а не поручение
начать миграцию заново. Target и независимое техническое review завершены;
ordinary mandatory CI проверяет actual latest PR HEAD. Все required jobs, включая
target/release/image/combined, должны иметь SUCCESS без skipped acceptance:
[актуальные checks](https://github.com/Tramsey00/MathStart-Python/pull/54/checks).
После этого технический статус READY_FOR_HUMAN_ACCEPTANCE; human acceptance
остаётся отдельным решением. Документ не разрешает production deployment или merge main.

| Исторический источник | Текущее применение |
| --- | --- |
| AGENTS.md, старые active plans/role queues | MIGRATION.md и AGENTS.override.md: итог миграции, human acceptance; новая работа только по поручению пользователя. |
| README.md | Окружения и команды ниже, [release](../deploy/RELEASE.md), [recovery](../deploy/RECOVERY.md). Корневой Compose включает deploy/compose.yaml; старый Dockerfile удалён. |
| PRODUCT.md | Перенос существующего сайта и границы продукта ниже; [полный v7.2](specifications/technical-spec-v7.2-draft.md) сохраняет будущие требования. |
| ARCHITECTURE.md, docs/architecture.md | ADR-0006 и текущие границы runtime/content ниже; старые domain contracts остаются обязательными. |
| verification skill | [skills/verification/SKILL.md](../skills/verification/SKILL.md), реальные registry commands; skip/empty/missing не равны PASS. |

## Существующий продукт и будущая программа

Переносятся публичная главная, каталог классов/предметов/разделов, поиск GET,
страницы уроков и authored HTML/math/SVG/CSS/JS; identity/profile/onboarding,
все девять зарегистрированных staff resources и существующие content commands.
Учебные темы и исходные адреса сохраняются, включая существующий10 класс.
Исторический ориентир263 темы не заменяет полный actual source/URL/assets manifest.

Onboarding сохраняет START_ZERO/SELF_REPORT/DIAGNOSTIC как выбор пользователя.
Он не запускает новую диагностику, не меняет mastery и не создаёт assessed
evidence. Существующие self-checks остаются legacy self-checks. Knowledge,
Assessment/Progress persistence, Analyzer/Tutor/adaptive practice и live Product
AI остаются будущими функциями. Четыре exercise modes, математические reference
oracles, typed steps, exact Decimal/replay и ownership Progress сохранены как
контракты; наличие их pure tests не означает реализации будущего runtime.

## Окружения и архитектура

Target: Python3.12+, FastAPI/Pydantic, SQLAlchemy2/psycopg/Alembic/Uvicorn,
PostgreSQL16+, React/TypeScript/Vite/React Router. Совместимые точные зависимости
зафиксированы в backend/frontend locks; не обновлять их на latest для установки.
Dockerfile использует pinned Python/Node/PostgreSQL/Nginx bases. Node нужен только
для build/publish, постоянный Node SSR server отсутствует.

Создать отдельное target окружение; пути ниже относительны Git root:

```text
python -m venv .venv-target
```

Далее использовать `.venv-target/Scripts/python.exe` на Windows или
`.venv-target/bin/python` на POSIX вместо `python`:

```text
python -m pip install --no-deps -r backend/infrastructure/http/requirements.lock
python -m pip check
python -c "import importlib.util; assert not importlib.util.find_spec('django'); assert not importlib.util.find_spec('rest_framework')"
```

Для backend QA добавить locked `backend/tests/v04/requirements.lock`. Исторический
Django golden comparator использует [отдельный pinned checkout и venv](legacy-oracle.md),
requirements.lock берётся только из него; interpreter передаётся явно. Не устанавливать Django в target ради comparator.
Frontend: Node24/npm11 с package-lock.json, принятый Docker builder Node24.21.0 /
npm11.19.0. Из frontend выполнить `npm ci`, `npm run typecheck`, `npm test`.
Public build требует проверенного immutable input и явного build config;
`npm run dev` не является установленным сайтом или production evidence.

Backend остаётся одним модульным монолитом. Каждая unit of work владеет короткой
SQLAlchemy Session; sessions не разделяются между threads/tasks. Старые table,
column/PK/FK/UUID/check/index/sequence identities и applied Django history
сохраняются. Новая схема — additive Alembic; startup не делает DDL и не seed-ит
auth/content. Ошибка PostgreSQL не включает SQLite fallback. Явный opt-in SQLite
для ограниченной разработки не доказывает PostgreSQL concurrency или acceptance.

Identity использует совместимые encoded password hash algorithms/validators,
opaque PostgreSQL sessions и owner-bound receipts. Регистрация UI ограничена30,
backend150; вход сохраняет старые длинные username. Пароли не сохраняются в
browser storage, public SSG, fixtures/evidence или argv. Session rotation,
logout/expiry/revocation, CSRF/Origin/Host и privacy проверяются сервером.
Доступные кнопки staff — только presentation hints; каждый API авторизует заново.
User creation сохраняет combined add/change permission, deletion — PROTECT и
предварительное owner/permission/revision-bound подтверждение.

## Content, public HTML и publication authority

Reviewed curriculum/site_content sources готовятся без Django в immutable input
с полным index/pages/assets inventory и receipt/digests. Node генерирует полный
HTML body/head для всех public URLs до активации. В runtime каждый запрос pin-ит
один authoritative release; renderer не перечитывает latest посреди ответа.
Public HTML не требует JS; LessonHost сохраняет authored markup и dependencies,
используя проверенный lifecycle/full-document navigation. Private account/staff
получают anonymous verified shell с no-store и реальные API после входа.

Publication — отдельный операторский процесс. Ordinary plan/publish/unpublish
используют PostgreSQL journal/gate, owner/generation lease/fencing, staging,
единственный domain commit, verified descriptor activation и реальные HTTP probes.
Pending/failure/uncertain result не становятся success. Recovery после commit
движется вперёд и не повторяет domain patch; precommit abort доказывает прежнее
состояние. Старые releases и unpublished rows сохраняются. Автоматический GC
чужих либо operation paths не реализован.

Порядок обычной свежей установки:

1. Подготовить отдельные private env/keys и owned PostgreSQL/public volumes.
   Собрать candidate API/edge/Node-builder из одного committed checkout.
2. Запустить только PostgreSQL; выполнить `backend.release_migrate preview`,
   review точного плана, `apply --maintenance --reviewed-plan-sha256`, `check`.
3. В fresh unused identity DB явно создать первого оператора через
   `backend.users.operator --maintenance`; импортированные пользователи не
   сбрасываются этим инструментом. Секреты вводятся non-echo prompts либо private env.
4. Выполнить `backend.content.publish prepare-bootstrap` с full source SHA,
   уникальным release ID, новым input root и edition file. Это подготовка, не SQL publish.
5. Собрать actual frontend этим же locked builder из exact input/receipt digests
   и с настоящим public origin; сохранить output manifest SHA256.
6. Создать ordinary publication plan с edition/output digest. Запустить API/edge:
   начальный503 ожидаем до согласованной публикации, edge нужен для HTTP probes.
7. Выполнить ordinary publish отдельным процессом с reviewed plan, stable owner
   и idempotency key. Дождаться COMPLETE, readiness, настоящего login и admin shell.
   Повторный matching bootstrap должен предложить ноль изменений без side effects.

Точные команды и mount layout: [backend/READ_RUNTIME.md](../backend/READ_RUNTIME.md),
[deploy/RELEASE.md](../deploy/RELEASE.md). Clean-clone rehearsal выполняет именно
этот обычный путь, не synthetic activation helper:

```text
python scripts/verify_installation.py --disposable --runtime-root var/install-<new-run>
```

Он требует Docker и свободные loopback55443/18125, создаёт собственные labelled
resources и удаляет только их. Результат c205ef1 — scoped PASS813 public probes,
actual login/readiness/sources/repeat bootstrap и cleanup; это не final target.
Synthetic_setup prepare/activate-initial используется только для controlled QA
fixtures. Не применять его вместо обычной установки или поверх existing authority.

Existing `update_public_pages` имеет отдельный target action
`backend.content.publish prepare-public-update`: только четыре public pages,
существующий POWER lesson, два retirement flags, четыре redirects и один PDF.
Reviewed media manifest целиком включён в immutable delivery главной: все29
public media URL доступны независимо от прямых ссылок в HTML/CSS, hash-verified.
Dry-run не пишет файлы/SQL/sequences; normal prepare сохраняет exclusive public-only
backup до immutable inputs. Затем обычные build/plan/publish и recovery authority.
Точные команды и границы: [READ_RUNTIME.md](../backend/READ_RUNTIME.md#scoped-update-of-installed-public-pages).

## Edge, maintenance и восстановление

Target stack — deploy/compose.yaml, optional compose.tls.yaml. API/edge работают
non-root с read-only roots/cap-drop; только edge публикует loopback port, DB/API
остаются во внутренней сети. Все static/media/public/private запросы проходят
authority gateway, прямого Nginx filesystem alias нет. API volume read-only;
отдельный publisher получает writable public volume и immutable handoffs.

Compose запускает два API worker с доверенным forwarded peer ровно по заданному
edge IP. Nginx заменяет X-Forwarded-For/Proto, очищает Forwarded/X-Real-IP.
Не использовать `--forwarded-allow-ips '*'` и не открывать API напрямую. Raw API
image по умолчанию отключает proxy headers; это безопасный direct-mode default,
а не корректная конфигурация распределённых client IP budgets за произвольным proxy.
TLS, внешний ingress/firewall, private secrets, backup retention/off-host storage
и operator ownership задаются человеком перед настоящим deployment.

Maintenance останавливает ingress/API/publishers и legacy writers. NOLOGIN не
дренирует существующие подключения. Перед adoption нужны sole-role drain,
reviewed schema plan и durable identity cutover binding; simultaneous legacy/
target writes или DDL на общих owned tables запрещены. HMAC/checkpoint привязан
к фактическим DB/role OIDs, rows/history/sequences и signing verifier key.

Backup — согласованный tuple PostgreSQL/WAL/roles, полный mutable media root,
immutable public inputs/frontend, manifests/receipts/digests, verifier keys и
cutover provenance. Текущий reviewed public manifest сохраняет все29 source media,
включая файлы без прямой ссылки в HTML. Резервировать весь mutable media root,
в том числе файлы вне reviewed seed. [Recovery runbook](../deploy/RECOVERY.md) описывает
реально проверенный physical restore с OID сохранением и distinct compatible app
switch до/после synthetic target writes. Отдельный pre-admission legacy-cluster return
прошёл scoped rehearsal34 assertions с actual Django, physical snapshot и новым
cutover/F-login. Он контролирует только owned lifecycle, не внешние записи;
операторская проверка ingress/writer fencing и admission history остаётся обязательной. После target writes старый snapshot
нельзя выдавать за безопасный rollback: сохранять current data/WAL, использовать
compatible application switch или reviewed forward recovery.

## Проверка и передача

Основные реальные commands из Git root:

```text
python scripts/verify_repo.py --profile pure
python scripts/verify_repo.py --profile target --list
python scripts/verify_target.py --runtime-root var/target-<new-run> --legacy-python <separate installed interpreter>
```

`verify_target.py` требует явный MATHSTART_DISPOSABLE=1 и private
MATHSTART_DATABASE_URL на dedicated loopback PostgreSQL55441. Он создаёт свои
дочерние DB, immutable fixture/build, ASGI и legacy comparator, выполняет все16
registry commands и fresh/upgrade A/B/C. Environment secrets не печатать.
Группы/allow-dirty дают только scoped development evidence. На кандидате1d9e4d3
normal PR CI39164124957 прошёл все девять jobs, включая target/image/combined:
320 backend,181 frontend units,1269 browser cases,0 skipped. Counts не заменяют
exact IDs/negative cases. Этот результат не присваивается более позднему SHA.
Полный target включает actual Chrome/Edge/Firefox на360/768/1440, source/
assets inventory, no-JS/SEO, math/widget/lifecycle/private/keyboard/responsive
и matched visual review. Скриншоты без просмотра не означают visual PASS.

Existing workflow_dispatch `full_target=true` запускает полный managed target
без поддельного REVIEWED. Успешный CI с target SKIPPED не закрывает migration.
Остальные image/install/recovery/document checks сохраняют свои recorded SHA и
scope; финальная проверка должна описывать согласованный combined candidate.
Общий QA и одно independent review миграции завершены; [итог и evidence](../MIGRATION.md)
сохраняют exact SHA. Точечное обслуживание проверяется по diff и зависимостям,
а обязательный CI — на новом кандидате. Draft PR сохраняет фактическое состояние
и human acceptance вопросы. Merge main, production, Issue closure и сообщения людям требуют
отдельного человеческого решения.
