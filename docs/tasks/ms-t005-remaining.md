# MS-T005 — локально 75/75, source blockers отсутствуют

74 MIGRATED + 1 REUSED_PILOT; обе последние темы statistics-25/26 активированы
локально после новой штатной конвертации непосредственно из оригинальных
body.html, встроенной валидации (2/2 OK) и ручной сверки содержимого.
[Текущий локальный отчёт](../audits/ms-t005-final-two-local.md).

Владимир передал d919429 (root SVG figure) и 7ab82ee (nested laboratory h2).
Перенесены только они через cherry-pick -x, без конфликтов. Старые локальные
адаптеры сохранены адресным stash, не использовались и не коммитились.
Предыдущие 73 документа, общие validator/renderer/CSS/math helper не менялись.

Source blockers: **0**. Это не завершение визуальной/педагогической приёмки.
Independent review и human acceptance PENDING; browser visual acceptance
PENDING_NOT_PERFORMED. Tests/typecheck/Playwright/smoke/QA/gates —
**NOT_RUN_BY_USER_REQUEST**, не PASS. Штатная конвертация/встроенная валидация
только двух тем выполнены по явному поручению.

## Что остаётся

- Согласовать локальный candidate и отдельное разрешение на push. **Push не выполнен**;
  удалённая ветка и Draft PR #62 остаются на 39545fd (73/75 source activations).
- Независимое review и ручной браузерный просмотр двух новых тем: монета/кость,
  все SVG attrs/подписи, пять точек графика и линия 0,5, lab header, 18 полных решений,
  якоря, порядок разделов, светлая/тёмная тема и мобильная ширина.
- Визуальная/педагогическая приёмка всего класса ещё не завершена; остальные
  непроверенные элементы перечислены в предыдущих execution records, в частности
  [шесть статистических тем](../audits/ms-t005-six-statistics-activation.md).

Snapshot, публикация, build, merge и закрытие Issue #61 не выполнялись.
Адреса алгебры 1/8 сохранены, 37 не создавать. БД/.venv/var/local и host-dev
процессы/config не менялись. Исторические receipts/audits не переписаны.
