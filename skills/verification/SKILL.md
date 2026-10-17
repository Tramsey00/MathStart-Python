# Проверка миграции

Единственная инструкция и критерии — [MIGRATION.md](../../MIGRATION.md), раздел
«Проверка результата». Это skill проверки, не отдельное задание или новый task gate.
Порядок: narrow reproducer/preflight -> affected unit/integration -> full final run.
Команда приёмки: `python scripts/verify_repo.py --profile target`; default пока legacy.
Pure/--list/PENDING/skip не доказывают target readiness. Missing required check — blocker.
Только owned disposable data. Actual versions/exits/raw logs/CI SHA и cleanup фиксировать
честно. Не повторять unchanged prerequisite FAIL и full QA после docs-only changes.
Reviewer проверяет риски/delta, не дублирует весь QA без причины. Secrets/PII не выводить.
