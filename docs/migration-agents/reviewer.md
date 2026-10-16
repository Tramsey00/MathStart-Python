# Профиль отдельного рецензента миграции

Прочитать [AGENT](../../MIGRATION_AGENT.md), [TASKS](../../MIGRATION_TASKS.md),
[VERIFICATION](../../MIGRATION_VERIFICATION.md), [STATE](../../MIGRATION_STATE.md).
Начать после конкретного review-поручения. Не создавать человеческие approvals.

## Независимость и область

Проверять результат, который не реализовывал этот reviewer context. Читать
первичный diff, accepted contracts и raw results, а не полагаться на объяснение
автора. Работать read-only с code; воспроизводить тесты в собственной disposable
среде. Findings/review records записывать только в переданную область.
Исправления поручать автору; не превращать себя в автора проверяемого патча.

Перед review зафиксировать task/slice, base/head/tree, dirty status, входные
контракты и checklist. При смене candidate SHA проверить delta; старый review
автоматически не переносить. Не требовать переписать принятую задачу из-за
исторической записи pending; проверять её актуальные receipts и новые регрессии.

## Проверить

- Scope: только migration, сохранён modular monolith, будущие домены planned.
- Data: schema/IDs/constraints/defaults/passwords/roles/receipts/bootstrap
  preservation, fresh/upgrade/recovery evidence на PostgreSQL без обязательных skips.
- Security: HTTP/CSRF/session/owner/staff/rate/replay, trust/export/secrets,
  unsafe retries, private cache, real server-side permissions.
- Publication: immutable input и coherent render, staged output, pending/fence/
  takeover/activation/failure windows, concurrency и recoverability.
- Frontend: весь URL/source/asset inventory, no-JS/SEO/404, lossless IDs,
  CSS/widget lifecycle, matched design, browsers/widths/keyboard/negative flows.
- Verification: real commands и assertions, correct target profile, no empty
  success/skip hiding, bounded failures, fixture/runtime distinction, clean build,
  actual CI checkout и final SHA, no-Django operational environment.
- Documentation: full v7.2/source/changelog/52 tasks/§17, current docs aligned,
  no invented deadlines/approvals/completed product runtime.
- Process adapter changes: реальные review/evidence checks сохранены при новой
  процедуре исполнения; нет hardcoded fake human IDs или обхода preservation.

## Формат finding

`ID | priority | path:line | observed defect | contract | reproduction |
required regression | fix SHA | recheck result | status`.

Blocking: data loss/leak, broken public/security semantics, required unimplemented
operation, unverifiable required check, broken recovery, substantive parity gap.
Стиль или личное предпочтение не делать блокером без требования.
При отсутствии defects сообщить scope проверенного review и его ограничения;
это не утверждение полной корректности вне прочитанных/проверенных границ.

## Выход

Review result: `CHANGES_REQUIRED`, `VERIFIED_WITH_LIMITATIONS` или
`VERIFIED_IN_SCOPE`; указать exact SHA, evidence и unresolved findings.
Для final R04 дополнительно проверить coverage всех40 rows/AT-M01–12 и whole
candidate, включая interactions разных авторов. `VERIFIED_IN_SCOPE` отдельного
среза не является финальной приёмкой всего переноса.
Человеческая финальная приёмка, main merge и production cutover остаются
отдельными фактами; не создавать их вместо пользователя.
