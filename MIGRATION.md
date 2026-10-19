# MathStart: итог миграции и человеческая приёмка

Перенос существующего MathStart на FastAPI/PostgreSQL и React/SSG завершён
технически. Статус — **READY_FOR_HUMAN_ACCEPTANCE / HUMAN_PENDING**.
Миграцию не требуется начинать заново или продолжать по старым карточкам.
Новая разработка и обслуживание выполняются только по отдельному поручению.
Human acceptance, merge main, закрытие Issues и production cutover не выполнены.

## Кандидат и доказательства

Проверенный исходный кандидат — `1d9e4d39aa103ccc049dd9569c2354893af30a75`,
ветка `ms7-mig-react-fastapi`, [draft PR №54](https://github.com/Tramsey00/MathStart-Python/pull/54).
Историческое полное задание доступно [в этом Git SHA](https://github.com/Tramsey00/MathStart-Python/blob/1d9e4d39aa103ccc049dd9569c2354893af30a75/MIGRATION.md);
его прежние поручения и персональные очереди не назначают новую работу.

Обязательные проверки этого кандидата завершились успешно, без skipped:

- [Migration CI 39164124957](https://github.com/Tramsey00/MathStart-Python/actions/runs/39164124957):
  все девять jobs, включая target, release-operations, image-recovery и combined.
- [Public/identity CI 39164125132](https://github.com/Tramsey00/MathStart-Python/actions/runs/39164125132):
  SUCCESS; [Harness CI 39164124841](https://github.com/Tramsey00/MathStart-Python/actions/runs/39164124841): SUCCESS.
- Actual PR checkout `877ef19b5adaa4c33139310c8e4d3184fc3079de` имел tree
  `701c864542070551ce0b7c099be058b2dbc9a70f`, равный tree кандидата.
  Target: 320 backend, 181 frontend unit, 1269 browser cases, 0 skipped;
  Chrome/Edge/Firefox × 360/768/1440. Fresh/upgrade A/B/C, ordinary clean-clone
  installation, physical recovery и legacy return/F-login прошли реальные проверки.
- [Независимое техническое review](docs/acceptance/migration-execution/review/final-review-20261018.md)
  не оставило нерешённых технических замечаний. Это не human Task Approval.

Результаты относятся к указанным SHA. После обслуживания текущего дерева
авторитетны [checks актуального HEAD PR](https://github.com/Tramsey00/MathStart-Python/pull/54/checks):
старый зелёный CI не присваивается новому SHA. Target SKIPPED не является PASS;
при необходимости существует явный `workflow_dispatch full_target=true`.

## Запуск и эксплуатация

- [Текущий runtime и архитектурные границы](docs/target-runtime.md).
- [Backend/runtime и content CLI](backend/READ_RUNTIME.md).
- [Установка, схема, оператор и публикация](deploy/RELEASE.md),
  [Compose](deploy/compose.yaml), [восстановление](deploy/RECOVERY.md).
- Локальное приёмочное окружение кандидата работает отдельно от исходной
  Django-БД. Его локальный README — `var/acceptance-1d9e4d3/README.md`;
  настройки и private-файлы не входят в Git. Не применять к нему disposable cleanup.

API не выполняет DDL/seed при старте. Схема устанавливается через reviewed
`preview/apply/check`, оператор создаётся явно, контент проходит обычные
`prepare-bootstrap/build/plan/publish`. Секреты хранятся вне Git и не выводятся
в логи. После target writes старый DB snapshot не является обычным rollback:
сохраняются current data/WAL, применяется совместимый app switch/forward recovery.

## Сохранённые требования и границы

Сохранены [исходное продуктовое ТЗ](docs/specifications/sources/technical-spec-v7.1.pdf),
[v7.2 draft](docs/specifications/technical-spec-v7.2-draft.md),
[его provenance](docs/specifications/technical-spec-v7.2-provenance.md),
[52-card disposition](docs/acceptance/migration-execution/product-task-disposition-draft.json),
[40 parity mappings](docs/acceptance/migration-execution/parity-ledger.json),
[итоговый mapping audit](docs/acceptance/migration-execution/i02-verification/ci-42f6249-mapping-audit.json)
для 12 acceptance scenarios и 139 named negatives. Historical receipts сохраняют
собственные SHA, результаты и digests.

Будущие Knowledge/Assessment/Progress/Analyzer/Tutor/adaptive practice/AI функции
продуктового ТЗ не реализованы в рамках переноса. Исходные AGENTS/PRODUCT/ARCHITECTURE/README и прежняя Django-платформа
сохраняются в Git. Текущие инструкции/entry points обновлены по отдельному
post-Django поручению; контент и контракты проверяются по принятому baseline
с [явными dispositions](specs/migration/post-django-preservation.json).
Косметическая доводка отложена: новые pixel-perfect/spacing критерии не вводятся.
Действующие functional/browser/math/accessibility проверки не ослабляются.

## Проверка результата

Действующие entry points: `python scripts/verify_repo.py --profile pure` и
`python scripts/verify_target.py` с owned disposable данными по runbook.
Default verifier теперь target; исторический legacy запускается только из
отдельного pinned checkout/venv по [oracle runbook](docs/legacy-oracle.md). Все 16 registry checks, реальные browser projects и обязательный combined
gate сохраняются. Пустой набор, missing, timeout и skip не становятся PASS.
Для обслуживания сначала проверяются затронутые зависимости; неизменные полные
прогоны не повторяются без причины. Новому проверяемому SHA соответствуют его CI
и provenance. Review обслуживания ограничивается его diff и зависимостями.

## Состояние обслуживания перед merge

[Отчёт точечной чистки](docs/acceptance/migration-execution/cleanup-20261019/report.md)
фиксирует исходный SHA, retired-цепочку, оставленные потребители и проверки.
[Индекс восстановления](docs/acceptance/migration-execution/cleanup-20261019/restoration-index.json)
содержит точные пути, размеры и SHA256 удалённых процессных файлов и ZIP.
Новых архивов с их копиями нет; Git-история не переписана. Приёмочный runtime
не перестраивается из-за чистки. Его человеческая приёмка всё ещё ожидается.

Человек отдельно подтверждает перенос и адаптированное ТЗ, ingress/writer
fencing/admission, dedicated roles/secrets/TLS и off-host backup/retention,
затем отдельно решает main merge и production cutover.

## Post-Django: краткая запись продолжения

Отдельное пользовательское поручение начато от
`1a87b044e8c5a7519b0ab57e22d2a35d57b4a986`; это также точный historical oracle pin.
Текущие изменения: Django-only paths удалены явно, shared quality/UI helpers
перенесены byte-for-byte, comparisons/legacy return изолированы в pinned checkout,
default/CI/setup/docs переключены на target, preservation разделён на current
retained bytes и historical provenance. [План и проверки](docs/exec-plans/active/post-django.md).
Адресные73 и57 тестов, frontend181/0skip и pure6 checks/232 cases PASS;
dependency/link/source/diff checks PASS. Локальный Docker daemon недоступен;
PostgreSQL/installation PASS локально не заявляется. Следующий шаг — commit/push,
обязательный CI нового SHA и ограниченное независимое review (ещё не завершены).
Приёмочный runtime1d9e4d3 не затронут и
не доказывает готовность post-Django кандидата. Main/production не изменялись.
