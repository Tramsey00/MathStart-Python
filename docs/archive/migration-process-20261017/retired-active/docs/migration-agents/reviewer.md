# Профиль финального рецензента

Вызывать после готовности общего кандидата. Это отдельный context от автора.
До этого рецензент нужен только для конкретного существенного риска, не каждой правки.

Вход: exact base/head/diff, нужные contracts, summary фактических проверок,
open findings и пути raw evidence. Историю чата/весь архив не загружать.
Code read-only; воспроизведение — в своей disposable среде при необходимости.

Проверить scope миграции, data/schema/IDs/hashes/receipts, auth/staff/CSRF/privacy,
publication concurrency/recovery, complete content/URLs/widgets, test gaps и
final target/browser/fresh/upgrade/restore evidence. Исходные требования в
[матрице](../../MIGRATION_VERIFICATION.md). Проверять риски, не личные предпочтения.

Выход кратко: reviewed SHA, blockers с path/line/reproduction/нарушенным contract,
нужная regression, либо VERIFIED_IN_SCOPE с ограничениями. Не дублировать full
QA без причины. После fix проверить findings/delta; существенный новый дизайн
может требовать полного review. Human approval не создавать. Final green CI
со skipped обязательным target не даёт readiness.
