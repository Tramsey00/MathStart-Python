# Руслан / R03 — точный metadata trust-anchor handoff v3

P01 external anchor: PENDING / NOT CLOSED. Human Task Approval: PENDING.
Этот пакет является предложением для review. Agent-generated bindings не approval.

## Exact inputs, modes, attributes, SHA256 и object IDs

**Фактический итоговый** `owner-handoff-bindings.json::inputs` содержит verifier,
policy, publication manifest, root `.gitattributes` и V02-local `.gitattributes`:
exact paths, raw Git blob SHA256/OID/bytes, Git mode,13 проверяемых effective
attributes и полный declared attribute map. JSON пересчитывается после final
staging, поэтому manifest SHA/OID в нём относятся к текущему итоговому index.

Expected control mode100644 взят из actual139 snapshot и independent re-audit,
не угадан. Control attributes: text=auto,eol=lf; filter,working-tree-encoding,
ident,crlf,diff,whitespace,merge,binary,export-ignore,export-subst,encoding —
unspecified. Полный effective map ровно {text:auto,eol:lf}. Raw73 имеют -text.
Состав40 exclusions и его digest указаны в том же JSON; полные SHA/OID/size/
line/reason pins находятся в exception-policy.json. Никакие wildcard exclusions
не добавлены. Любая новая metadata требует отдельного review/repin.

## Non-circular binding

Manifest содержит149 byte records; все151 paths включены в exact set и mode/
attribute checks. Self manifest не содержит собственного digest. Дополнительный
derived handoff output не хешируется внутри manifest (иначе SHA manifest в
handoff создал бы цикл), но его bytes обязаны точно совпасть с canonical
recomputation actual Git inputs. Mode/attributes этого output также фиксированы.
Это не ослабляет прежние139 records. Все три verifier/policy/manifest tuples
в external anchor теперь включают **bytes и Git metadata**, не только digests.

## Owner-controlled independent gate

1. Independently review exact staged snapshot, metadata negatives и policy40.
   Decide whether retained raw full FAIL/2 is acceptable. Не принимать pins из
   candidate JSON как уже approved и не пересчитывать их с автоматическим approval.
2. Скопировать vetted standalone v3 executable в owner-controlled R03/CI scope,
   закрепить его digest до исполнения. Он импортирует только standard library.
   Pin reviewed policy/manifest byte+metadata tuples, applicable attributes files,
   exact40 paths/digest и отдельно digest owner approval artifact вне candidate.
3. Owner artifact schema: version=MS7-MIG-V02-owner-metadata-anchor-v3,
   owner=Ruslan, decision=APPROVED, inputs=independently reviewed five-input tuple,
   exception_set_sha256, exception_paths. Не использовать `_fixture` или synthetic
   probe anchors для реального approval. Старый byte-only v2 anchor недопустим.
4. Owner controls Python/Git binaries, root/ref/base, clean checkout и config/env.
   Exclude untrusted PYTHONPATH/startup, Git fsmonitor/external diff/filter drivers,
   system/global/info attributes. Effective metadata всё равно сверяется с pins.
   `--local-proposal` запрещён для publication gate. P01 нельзя закрыть task self-check.

Проверяемая команда на **опубликованном reviewed candidate SHA**:

```text
python -I -B OWNER_CONTROLLED/verify_publication_v3.py --root CLEAN_CHECKOUT --ref REVIEWED_CANDIDATE_SHA --owner-anchor OWNER_CONTROLLED_APPROVAL_JSON --owner-anchor-sha256 INDEPENDENT_APPROVED_ANCHOR_DIGEST
```

При отсутствии anchor обычный запуск возвращает3 OWNER_EXCEPTION_APPROVAL_PENDING.
Локальный режим только для review:

```text
python -I -B docs/acceptance/MS7-MIG-V02/publication-byte-audit/round3/verify_publication_v3.py --local-proposal
```

Root gate должен повторить source P2 chmod100755 и info attributes -text,
eol/filter/encoding/ident/export-subst/unknown attributes, staged .gitattributes
изменение вместе с manifest, изменённые bytes/OID/size/paths/policy, новый whitespace
вне40 и joint verifier/policy replacement. Повторить checkout false/true/input;
before-execution external pins должны отвергнуть изменённый executable.
Mode/attrs negatives должны FAIL даже с прежними bytes и correct anchor.

Проверять candidate commit/tree metadata, а не только blob SHA256. Новая .gitattributes
или любой неразрешённый effective attribute, mode, path, exception/diagnostic или
pin mismatch означает FAIL. Synthetic anchored positives являются только fixtures.
Full whitespace checks остаются FAIL/2; scoped PASS не заменяет owner exception
decision. Task Approval оценивается отдельно после real candidate SHA/current CI.
Root workflows/registry не изменены; ни одного сообщения/approval от имени Руслана.
