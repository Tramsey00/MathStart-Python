# Исторические внешние controls публикации V02 R03 — retired gate

**ИСТОРИЧЕСКИЙ / RETIRED.** Этот документ описывает старый gate для фиксированного
candidate, а не текущий runtime или ожидающую выполнения задачу. Принятая миграция
и завершённые PR54/PR55 записаны в [maintenance](../../../../docs/maintenance.md).
Одобренные controls и их hashes остаются без изменений.

Эти controls относятся к историческому этапу R03. Они фиксируют уже одобренное Русланом
решение об исключении **ровно 40** после независимого восстановления исходных 151 files.
Они не дают Task Approval V02 или разрешения на публикацию/merge.

- Принятый BASE: `0c03197e23f69a233c0fcf8bdffa336feca20b92`.
- Неизменяемый MIG_BASE: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
- Проверенное подготовленное дерево: `dbad1e853dff354c5d3255755afb5cc32e0ad279`.
- Source ZIP SHA256: `57cad8b19e75bda674ce1ac9ddcf9c92a6b57daa2a3b4bd1f39e528c1a77cd0a`.
- Exception-set SHA256: `fa62cf5f4c9b3aaf91864b9face548a5f45759390fb7bedd9cdef5ae6e7c2e18`.
- Owner anchor: `owner-approval-v3.json`, SHA256
  `5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7`.
- SHA256 одобренных pins:
  `eb32a3245275649e9a69c67ea17001cfd4b8ff0cd7a30e63bcac325692c9c591`.
- SHA256 точного verifier v3:
  `54da54d7a54f9ca714a393577a31a74e948c373bbee4c92045110958c59a56a5`.

`trusted-controls.zip` побайтно сохраняет все шесть исходных control files,
включая исторические пробелы/метки pending. Удалённый gate размещал их во внешней
директории владельца и непосредственно перед исполнением проверял каждый digest.
Digest pins и digest конкретного anchor являются константами bootstrap R03.
Ни один из них не пересчитывается по candidate. Отдельный JSON anchor — реальная
запись ограниченного решения пользователя по policy, без синтетического `_fixture`.
Исходный review готовности artifacts/gate относился к тому историческому этапу.

## Исторический replay и восстановление

Этот gate и его выделенные workflows/controllers удалены при cleanup `467866e`.
В текущем checkout нет команды запуска удалённых controllers. Для исторического изучения
восстановите нужную цепочку на `1d9e4d39aa103ccc049dd9569c2354893af30a75`, последнем
дереве исходников до удаления, по действующему [restoration index](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/migration-execution/cleanup-20261019/restoration-index.json).
Его исходные 65 entries определяют удалённые controllers/source snapshot по этому SHA.
Дополнительные entries artifacts используют cleanup `467866e` как собственный source SHA.
Восстанавливайте только нужные исторические paths в отдельном checkout для расследования,
затем следуйте [исходному описанию gate на его ревизии источника](https://github.com/Tramsey00/MathStart-Python/blob/1d9e4d39aa103ccc049dd9569c2354893af30a75/specs/migration/r03-v1/v02-publication/README.md).
Сверьте каждый восстановленный blob с каноническим размером/SHA256 из индекса.
Это руководство по восстановлению, а не указание возобновить публикацию или миграцию.

Исходный replay использовал отдельный закреплённый owner checkout и изолированный candidate,
Python 3.12 из стандартной библиотеки/Git и не использовал DB. Изменённые executable/config/
attributes/alternates отклонялись до запуска. Исходное staged представление сохраняло
HEAD на BASE и `implementation_sha` null; последующие проверки published commit связывали
единственные parent/tree. Полные результаты whitespace обычного/cr-at-eol оставались FAIL/2,
scoped checks — PASS/0 ровно с 40 exclusions, все 73 raw files были закреплены.
Это исторические наблюдения и границы доверия, а не новые одобрения.

## Отрицательные свидетельства

Suite атакует фактически восстановленный package. Между случаями она восстанавливает
исходные bytes и одобренный index. Production bootstrap первым делом отклоняет изменённые trees.
Отдельные probes нижнего уровня запускают неизменённый внешний verifier на изменённых trees
только для фиксации точной причины отказа; они не могут выдать production approval.
Замены executable/control отклоняются до запуска verifier; marker исполнения проверяется
на отсутствие. Новые whitespace также сохраняются как фактический scoped FAIL/2 raw output.

Result, argv, stdout/stderr, exit codes, mutation hashes, versions и evidence manifest
сохраняются даже при сбое. После всех атак положительный контроль запускается заново.
Старая метка INCOMPLETE описывала предпосылки на тот момент. Она не является текущим статусом
миграции: полный target/recovery/combined и независимое техническое ревью позднее успешно
прошли на точных SHA, указанных в [maintenance](../../../../docs/maintenance.md).
Затем миграцию приняли и слили в PR54; этот retired gate не открывает принятое решение заново.
