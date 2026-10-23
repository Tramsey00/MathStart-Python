---
name: mathstart-verification
description: Выполнить staged проверки MathStart с честным portable/runtime evidence на actual candidate.
---

# Проверки MathStart

Используй текущее поручение, contracts и docs/target-runtime.md. Работай в основном
checkout в ветке задания; актуальность main проверяется перед созданием ветки.
Выбери scope по [политике](../../docs/frontend/testing-policy.md): сначала affected
checks; mandatory coherent-candidate CI gate — при интеграции/runtime/release,
а не после каждой строки документации. Значение существующих full команд не сужать.

Default: `python scripts/verify_repo.py` —15 product checks.
Portable: `--profile pure` —5 suites; pure/--list не доказывают runtime readiness.
Empty/skipped/flaky/missing/timeout fail. Собственный Engineering Harness удалён;
общие routing/privacy regressions и bounded diagnostic redaction сохранены.

Документы/очередь: scripts/check_workflow_docs.py; current source reconciliation:
scripts/check_product_source.py; сохранность: scripts/check_migration_preservation.py.
Не обновляй массово trusted hashes. Только явные пофайловые scope dispositions,
неизменные historical receipts/approvals и source bytes в Git.

Используй только owned disposable PostgreSQL/resources. Legacy comparisons —
только явно необходимый отдельный pinned oracle из docs/legacy-oracle.md,
никогда Django/DRF в target. Operating DB и protected acceptance stack не tests.
Не выводи secrets/cookies/PII.

Связывай результаты с actual SHA/tree/input digests/commands/exit/results;
старый CI не подтверждает новый candidate. Запиши failed/NOT_RUN/environment
limitations. Самопроверка не отдельное ревью и не человеческая приёмка.
После review findings исправь причину и повтори affected checks без дублирования
успешного неизменённого QA. Отдельное review выполняется в следующем шаге
процесса; не создавай обязательных субагентов или автоматической оркестрации.
