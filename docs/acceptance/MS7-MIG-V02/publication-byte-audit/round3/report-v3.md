# MS7-MIG-V02 — Publication Gate Remediation Round 3

**READY FOR INDEPENDENT RE-AUDIT.** Owner exception и Human Task Approval PENDING.
`tested_implementation_sha=null`; `publication_status=PENDING_PUBLICATION`.

## 1. Точная причина нового P2

V2 `if path != MANIFEST` исключал вместе с циклическим self hash также проверки
mode/ожидаемых attributes. Blob SHA256/OID не содержит mode Git tree и effective
attributes. Поэтому прежние bytes +100755 или info attributes -text проходили
даже при synthetic reviewed byte anchor. Initial139 index metadata было корректным;
это не заменяло необходимый rejecting negative probe.

## 2. Изменённые файлы

Только12 новых append-only файлов `publication-byte-audit/round3/`: intake.json,
source-imports.json,exception-policy.json,verify_publication_v3.py,
test_publication_v3.py,report-v3.md,owner-handoff.md,owner-handoff-bindings.json,
probe-results.json,checkout-results.json,verification.json,publication-manifest-v3.json.
Все previous139 файлов и их raw working/Git blob bytes/OIDs/modes/attributes
сохранены. Root/V02-local .gitattributes не менялись. Backend/tests/root CI untouched.

## 3. Исправление manifest mode/attributes

Expected mode100644 измерен в staged old manifest и независимо подтверждён
re-audit. Expected effective metadata получена из staged attributes; не берётся
из mutable self manifest. Separately pinned v3 policy фиксирует normal/raw profiles.
Для всех151 paths, включая manifest и derived handoff, до hash-record branch
проверяются фактический Git mode,13 attributes и полный declared attribute map.
Проверяются cached index/tree attributes и working consistency. Небезопасные
filter/working-tree-encoding/ident/crlf/export/diff/merge/binary/whitespace/encoding
и неизвестные attributes отклоняются. Root и local attributes inputs закреплены
OID/SHA256/size/mode/full metadata. Проверки других paths/raw40 не ослаблены.

## 4. Независимое CLI reproduction до и после

Отдельный unchanged v2 runner и139-file scratch index:5 воспроизведений реально
вернули0 вместо secure1 — mode local/anchored/tree и -text local/anchored.
Новые v3 CLI probes выполнялись отдельно от тестовых assertions с теми же
операциями и **legacy byte-only anchor format**: оба вернули1,
FIXED_MODE/FIXED_ATTRIBUTES при unchanged reviewed blob bytes. V3 metadata
anchor tests подтверждают то же; правильные restored metadata проходят fixture.
Каждый probe сохраняет exact OID/SHA/size/mode/attributes snapshot, actual exit,
expected result и argv. Source index/production code не менялся в probes.

## 5. Negative test matrix

30 scoped cases:6 positives exit0,23 expected negatives exit1 и1 external-pin
simulation. Дополнительно2 separate exact-source reproduction после fix exit1.
Mode100755 local/anchor/tree, -text/eol/filter/encoding/ident/export-subst/unknown
attributes, policy/verifier/local/root attributes input changes — FAIL.
Changed .gitattributes с прежним manifest SHA — FAIL; rebound manifest — FAIL.
Manifest byte mutation — FAIL, включая rebound in-scope handoff + reviewed anchor.
Policy entry — FAIL. Новая whitespace вне40 после rebinding — FAIL. Derived
handoff content/mode mutations — FAIL. Restored metadata/mode — PASS local и
correct synthetic metadata anchor. Joint replacement не считается independently
secure; outside-code before-execution pin проверен только как simulation.
Первый test harness ошибочно ожидал root-only diagnostic для basename pattern
.gitattributes; guard уже отклонял изменение. Исправлено exact /.gitattributes,
полный final probe run прошёл. Verifier при этой корректировке не изменялся.

## 6. Clean-checkout results

Actual checkout-index в новом Git root по source index, read-only object
alternates, root/local attributes: false,true,input — PASS/0 proposal conformance.
Raw73 точные; normalized text допускает CRLF→LF без обязательных старых working
hashes. Никакого commit/reset/clean или DB. Windows execution; cross-OS NOT RUN.

## 7. Git blob/mode/attributes verification

Exact151 path set,149 hash/OID/size records + self manifest + derived handoff.
Metadata проверяется для **всех151**. Self bytes externally reviewed/pinned;
handoff bytes строго равны canonical actual-input recomputation, что устраняет
цикл manifest-handoff hashing без неконтролируемого metadata исключения.
Anchor v3 содержит tuples SHA256/OID/size/mode/all attributes для5 trusted inputs.
Default без independently approved artifact остаётся owner-pending, exit3.

## 8. 40-path exception preservation

Exact40 exception entries/digests/paths/OIDs/line reasons равны Round2 policy;
raw73 сохранены. Никаких новых exemptions или suppression attributes. Unknown
diagnostics outside40 запрещены. P03 CLOSED per independent re-audit сохраняется.

## 9. Backend/frozen identity

28 active backend/source/test paths byte-identical positive independent snapshot;
60 frozen records и весь previous139 snapshot неизменны. Initial47, negative
audit, positive runtime re-audit, raw logs и historical manifests не переписаны.
Новый negative publication audit импортирован losslessly в source-imports.json
с checked SHA/size/base64 и verbatim escaped UTF8. F01/F02 остаются independently
CLOSED. Runtime86/V0134/PG/verify_repo NOT RERUN: evidence-only remediation.

## 10. Actual full/scoped whitespace exit codes

| Check | Actual |
| --- | --- |
| Full ordinary | **FAIL/2**,3887 diagnostics,40 paths |
| Full cr-at-eol | **FAIL/2**,6 CRCRLF diagnostics,3 paths |
| Scoped ordinary outside exact40 | PASS/0 |
| Scoped cr-at-eol outside exact40 | PASS/0 |

Historical FAIL preserved, never relabelled PASS. Exception approval absent.

## 11. Publication manifest и exact SHA256

publication-manifest-v3.json — current canonical blob/mode/attribute binding.
**Exact final manifest SHA256 и Git OID** находятся в
owner-handoff-bindings.json::inputs[manifest path], которые пересчитываются после
final staging. SHA не встраивается в хешируемый report, чтобы избежать цикла.
В final response отдельно приводится тот же фактически измеренный SHA256.
Full set151; control output bytes проверяются вычислением, self metadata fixed.

## 12. Ruslan/R03 trust-anchor handoff

owner-handoff.md + owner-handoff-bindings.json дают exact5 input paths, SHA/OID/
bytes/modes/13 attributes/full maps,40 paths/digest, commands, negatives,
published candidate --ref recipe и reject rules. Root gate должен самостоятельно
зафиксировать code/policy/manifest/metadata и execution context вне mutable task.
Old v2 byte-only anchor недостаточен. Не принимать generated bindings за approval.
Root workflows не изменены; fake approval/сообщение Руслану не создавались.

## 13. Остаточные blockers

Manifest mode/attributes P2: **LOCALLY_FIXED**, independent Round3 closure PENDING.
P01 external anchor: **PENDING / NOT CLOSED** until Ruslan deployment/approval.
P02: **CLOSED**; P03: **CLOSED** per supplied independent re-audit.
Human Task Approval: **PENDING**. Actual candidate commit/current CI и cross-OS
NOT VERIFIED. Ни один synthetic fixture не является реальным approval.

## 14. Рекомендация

**READY FOR INDEPENDENT RE-AUDIT**, not ACCEPTED/published. Owner exception
approval and Human Task Approval remain PENDING. All added files task-owned;
current stage151, unstaged0/untracked0 after final binding. Commit/push/merge/
rebase/reset/clean/PR не выполнялись. Production/working DB не использовались.

Final bound index and all three fresh checkout profiles passed actual local
conformance; ordinary no-anchor gate returned3. Full whitespace remains2/2,
scoped0/0. Source139/backend28/frozen60/archive47 exact. Staged signature scan
found no secrets; specialized universal scanner NOT RUN. Final receipts in
verification.json; actual final manifest SHA/OID in derived handoff bindings.
