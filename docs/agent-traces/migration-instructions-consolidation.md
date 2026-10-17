# Trace: одно ТЗ для оставшейся миграции

Date:2026-10-17 Europe/Moscow. Scope: instructions/documentation only.
Human review: pending. Application migration implementation was not started here.

## Поручение и результат

Пользователь уточнил: нужен один самостоятельный Markdown-документ с общей
задачей и оставшейся функциональностью, без отдельных заданий по старым кодам.
Подготовлен `MIGRATION.md` в исходном project root и рабочем integration checkout;
bytes копий совпадают. Документ продолжает уже написанный код и dirty fixes,
объединяет backend/frontend/publication/operations/documentation/verification,
задаёт одного исполнителя и финальное отдельное review.

Пять прежних MIGRATION_*.md и три role profiles удалены из активного набора.
Оригинальные и промежуточные инструкции сохранены побайтно в
`docs/archive/migration-process-20261017/` и `retired-active/` с manifests.
Старые планы подготовки помечены historical; execution plan и verification
skill направляют в единственное ТЗ. Existing machine task ledger сменил только
процесс, сохранив все18 IDs/statuses/Issue references и13 оставшихся записей.

AGENTS.override.md — короткая точка входа. Оригинальные AGENTS.md и pinned
PRODUCT/ARCHITECTURE/README/content architecture сохранены побайтно. Никакие
frozen manifests, tests или preservation guards не ослаблялись.

## Исходная работа и сохранность

Execution root: `C:/Projects/MathStart-Python/migration-execution/integration`.
HEAD:a46daa9; remote observed:b8a9382. Коммиты/refs/PR/БД не изменялись.
Existing незакоммиченные verifier/comparator/browser/CI corrections сохранены.
12 dirty code/workflow/test files проверены по SHA256 до финальной проверки;
приложение, dependencies и pipelines этим изменением не редактировались.
Only process JSON metadata changed alongside Markdown. Исторические evidence не удалялись.

## Проверки и исправления подготовки

Первый pure run:4/6 PASS,2 failures из-за byte-pinned документации, временно
изменённой в ходе упрощения. PRODUCT/ARCHITECTURE и остальные baseline документы
восстановлены из verified archive; вход инструкции перенесён в локальный override.
Повтор требовался из-за устранённого конкретного failure, а не для повторения
неизменного pipeline. Test/guard code и expected hashes оставлены прежними.

При архивации индекс столкнулся с именем source README.md; отдельный INDEX.md
устранил конфликт. Полнота41 архивных hash entries затем проверена.

| Проверка | Фактический результат |
| --- | --- |
| UTF-8/Markdown links/fences и отсутствие task labels в новом ТЗ | PASS |
| Archive manifests |41 hash entries PASS |
| Dirty code/workflow/test bytes |12 files SHA256 PASS |
| Historical document bytes и user AGENTS | PASS |
| Task statuses/counts |18 сохранены,13 remaining; acceptance не изменена |
| `python scripts/verify_repo.py --profile pure` после восстановления pins |6/6 PASS, exit0 |
| Full target/PG/browser runtime | NOT_RUN: actual migration не выполнялась |

Raw QA: `var/instruction-consolidation/pure.log` и `pure-restored.log`;
статическая проверка: родительский `tmp/unified-instructions-qa/validation.json`.
Python3.12.14 использован из existing target environment. Новые packages не ставились.

## Граница передачи

Подготовлен единый документ и его короткая автоматическая точка входа.
Изменения локальные, не закоммичены/не опубликованы этим поручением.
Само приложение не объявляется готовым; final human gate/main/production pending.
Следующий execution запускается явным пользовательским поручением прочитать
и выполнить MIGRATION.md в существующем migration checkout.

## Финальная очистка точек входа

Два прежних backend/frontend execution plans заменены историческими ссылками.
В product draft исправлены удалённые process pointers и прежняя модель
команды; добавлена явная граница DRAFT_REFERENCE_ONLY. Полные исходные
версии этих трёх файлов сохранены в final-cleanup/ с SHA256 manifest.
Индексы active plans/traces/archive разъясняют их исторический статус.
Сохранённые frozen plans/contracts/evidence не переписывались.

В ledger убраны прежние настройки постоянных subagents и ограничения
области одного запуска. Статусы и technical receipts сохранены.
Финальная статическая проверка:45 архивных hashes,12 protected files,
18 coverage records/13 remaining и10 links PASS. После очистки планов
и draft `python scripts/verify_repo.py --profile pure` снова6/6 PASS;
raw log: `var/instruction-consolidation/pure-final-cleanup.log`.
