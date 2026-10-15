# MS7-MIG-V02 — Publication byte audit

Состояние: index подготовлен для дополнительного scoped evidence re-audit.
Публикация и human approval PENDING. `tested_implementation_sha=null`.
Commit, push и PR не выполнялись. Backend и тестовые исходники не менялись.

## Байты и причины

Исходно staged 123 файла, HEAD/base/merge-base
`0c03197e23f69a233c0fcf8bdffa336feca20b92`, ветка `ms7-mig-v02-content`.
Полный ordinary и `cr-at-eol` check: exit 2. Сначала обнаружены 58 различий
SHA256 working bytes / indexed blobs из-за автоматической LF-нормализации.

`F02-runtime.patch`: 72 CRLF, ни одного CRCRLF, NUL, ESC или другого управляющего
символа. Строки 10, 13, 31, 32 — `20 0D 0A` в working copy / `20 0A` в исходном
index. ASCII-пробел является marker пустой context-строки unified diff; это
реальный trailing whitespace файла patch, но не whitespace backend-кода.

Три raw-лога `verify-repo-command.txt` (root, initial archive, remediation):
по 194 LF, 194 CRLF, 196 CR, два CRCRLF на строках 68/79. Пробелов/табов перед
окончаниями этих строк, NUL, ESC и иных управляющих символов нет.
Root и archived log SHA256 совпадают:
`b350b6ec5e6bfb56e3064f210aa337a95a89a8edd0f714bd3706a8031db57b75`.
Remediation log имеет другой SHA256:
`da00309e1d91b592e91f52a20b7be8a9b7b4696d6c59adc91e46c4ecccf24ea2`.
Третий лог обнаружен сверх трёх первоначально указанных файлов.

Причина CRCRLF воспроизведена без БД: установленный Django
`BaseDatabaseCreation.log()` пишет `msg + os.linesep`; Windows `TextIOWrapper`
с `newline=None` преобразует уже добавленный CRLF в CRCRLF. Это исходные bytes
реального stdout/stderr evidence, а не редакторские хвостовые пробелы.

## Минимальное исправление patch

Удалены только четыре marker-пробела на пустых context-строках. Patch сохранён
как LF согласно root policy. Другой текст и номера hunks сохранены.
Обычный `git apply -p1 --check` и реальное применение в собственном disposable
scratch-каталоге завершились exit 0. Выходные байты равны текущему `app.py`.
Исходный archived `app.py` и текущий backend уже LF; их нормализация не требовалась.
Не использовались ignore-whitespace, reject, unidiff-zero или изменение backend.

Patch working SHA256 до:
`d8582e6d412b18286aec29e51f326e4ceee2cfb44f9d63d985a58014a105b0b2`;
исходный indexed blob:
`ca926a034f8820e35b13dd88c69b71ff199db23cdd590b8e9a754332d8ea88be`;
после, working/index:
`25eff3c55a118c5009e66586c1fc0f612a3f0a7c1c3916766cb854b22e204194`.

## Хранение raw evidence

Добавлен только V02-local `docs/acceptance/MS7-MIG-V02/.gitattributes`:
`-text` для 47 initial copies, двух original-audit copies и текущих raw
`*-command.txt`. Root attributes/CI/config не менялись. После точечного
`git add --renormalize` все 73 raw-файла имеют равные working/index байты.
Это предотвращает повреждение архивной побайтной идентичности при checkout.
Архивные manifests, snapshot, аудит, frozen evidence и raw-логи не редактировались.

Остались 20 разрешённых различий working/index SHA256 в current text-файлах:
только CRLF-to-LF, подтверждено сравнением байтов. Backend working/index hashes
совпадают с исходным staged snapshot этого задания. Старый workspace manifest
не переписан: его единственная новая working-byte дельта — допустимый patch fix.
Новая привязка всех publication bytes хранится отдельно в publication-manifest.json.

## Фактические итоговые проверки

| Проверка | Результат |
| --- | --- |
| `git diff --cached --check` | **FAIL, exit 2**, 3887 raw CR diagnostics |
| `git -c core.whitespace=cr-at-eol diff --cached --check` | **FAIL, exit 2**, 6 CRCRLF diagnostics: 3 logs × 2 lines |
| Ordinary check вне explicit hash-pinned raw allowlist | PASS, exit 0 |
| `cr-at-eol` check вне того же allowlist | PASS, exit 0 |
| Обычное применение F02 patch | PASS, exit 0; точное совпадение backend bytes |
| 47 archive + 2 original-audit copies | Working bytes и Git blobs совпадают с исходными SHA256 |
| Backend/frozen contracts | Без изменений; 60 frozen records повторно проверяются read-only verifier |
| Staged files | **128**: исходные 123 + attributes + 4 publication audit files |
| Credential signature / filename / URL scan | Секретов не обнаружено; synthetic test sentinels проверены |
| Gitleaks / detect-secrets | NOT RUN: не установлены |
| Backend suites / PostgreSQL smoke / verify_repo | NOT RERUN в этом задании; сохранены фактические прошлые результаты |

## Точная proposed publication policy

Полные whitespace checks остаются **FAIL**. Не изменять глобальную настройку
whitespace, не скрывать diff и не нормализовать raw evidence ради зелёного check.
Допуск предлагается только для **73 точных путей и SHA256** из
`publication-evidence.json::exact_evidence_allowlist`: фиксированные 49 immutable
copies и 24 raw command logs. Любая смена bytes, появление нового exempt path
или отличие diagnostics от записанных строк требует нового scoped review.

Для остальных staged paths выполняются оба обычных check с literal pathspec
exclusions. Проверка raw bytes обязательна одновременно с ними. В JSON сохранены
полные argv, exact path exclusions, строки diagnostics и hashes результатов.

Воспроизводимая read-only проверка из корня репозитория:

```powershell
python docs/acceptance/MS7-MIG-V02/publication-byte-audit/verify_publication.py
```

Exit 0 этого verifier означает соответствие предложенной локальной policy,
**не PASS полного whitespace check и не разрешение на публикацию**.
Он проверяет все staged bytes / working bytes, точный file set, SHA256 immutable
copies, baseline/frozen, unchanged backend и полный/filtered check, включая
неизменность каждой диагностической строки. Manifest исключает только себя
для устранения циклического hashing; никакого implementation commit не выдумано.

## Следующий gate

**Дополнительный scoped evidence re-audit требуется**: новый attributes policy,
raw Git blobs, минимальный patch fix/его применение, отдельный publication
manifest и предложенное whitespace exception. Этот gate PENDING; waiver не
считается одобренным самим автором. Независимый F01/F02 re-audit и Task Approval
также сохраняют PENDING. Backend runtime/code не менялись в этом задании.
