# Provenance полной рабочей редакции v7.2

20.10.2026, Europe/Moscow. [Полное ТЗ](technical-spec-v7.2-draft.md) остаётся
единственным current Markdown документом32 глав. **DRAFT_HUMAN_PENDING**:
принятие платформы/PR54/55 и G0 v7.1 не утверждают эту продуктовую редакцию.
Текущее поручение разрешает документационную очистку и вывод собственного Harness,
не реализацию новых features и не production rollout.

| Источник | SHA256 |
| --- | --- |
| Текущий полный Markdown v7.2 | `e3a2d4167f8565c629c33efd7cf86caae3eeef59f7775cd05ccf1a98245b3fc7` |
| Текущий52-card source registry + отдельные workflow fields | `058cfa22bb350cbc4ad0b9848d4fd4d58660af6c594629dc19f7ab55d291ae02` |
| Полный предыдущий v7.2 на HEAD 1a015f7513933901e8bb252e94c660e4383b6b0e | `1160bcdd0d690e968273aa0de48c50227bd6a87eb2c048fb569cb694654ee7dc` |
| Historical114-page v7.1 PDF | `e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd` |
| Historical v7.2 до status-only introduction update | `c6be84b2932f1e79821c11f18fd5fa1463507793ace30ecbc47804d45478c6f8` |
| Consolidated v7.2 на PR55 merge12450dfd39b51166aa5a40955ce78e40169a1cb4 | `aac2ba4f43a3c20b6315d38400263e7f4d1160ebba9866d417465e57d6de3cde` |

Оригинальный PDF/audit получаются из literal Git
`3a290a46d991e22269a17dde41e39f0637576071`, пути
`docs/specifications/sources/technical-spec-v7.1.pdf` и
`docs/acceptance/migration-execution/product-source-audit.json`.
Original bytes/size/hash проверяются прежним preservation manifest. Исторические
hashes, receipts, approvals и полные source_card_text не обновлены.

## История и явное изменение объёма

18.10: полная source reconciliation114 страниц/52 карточек/115 typed edges,
68 исправлений только геометрии glyphs; не новый runtime результат.
19.10: status guidance после принятой миграции и завершённой консолидации.
20.10: текущее поручение пользователя, [аудит](../audits/docs-and-workflow-cleanup.md),
[новая очередь](../tasks/INDEX.md).

- Сохранено: полный domain/product/API/math/Progress/AI/security/ops scope,
  product limits/eval denominators и immutable original results. §§6–11 полной
  текущей редакции сверяются целиком с предыдущим HEAD.
- Изменено: actual stack/architecture/administration/publication/testing descriptions,
  процесс одного исполнителя/ветки/отдельного review/приёмки, active dependencies.
- Добавлено: redesign/design system, три направления и library decision, отдельно
  проектируемая геймификация,24 task skills с acceptance/checks/stop conditions.
- Снято с плана: собственный Engineering Harness и8 исключительно его future
  tasks, G1/D-026/027/OD-12–14/NFR-19/AT-13 и mixed Harness-only obligations.
  Номера не переиспользуются, снятое не помечается выполненным.

52 source rows сохраняют **все прежние поля** без изменения, включая115 source
HARD60/CONTRACT24/HANDOFF6/INTEGRATION25 edges. Поля current_status и
platform_disposition теперь явно historical migration snapshot. Только новые
workflow_disposition/tasks/reason определяют актуальную судьбу. Карточки не
теряются при переносе подробностей в canonical task skills.

## Проверка

```powershell
python scripts/check_product_source.py
python scripts/check_workflow_docs.py
python scripts/check_migration_preservation.py
```

Source checker проверяет оригинальный PDF, historical complete card hashes/edges/
approvals против pinned sources, glyph repairs и отсутствие выдуманного future
evidence. Current checks отдельно проверяют32 главы/52 disposition IDs, неизменность
полных domain chapters, actual hashes, queue/skills/bidirectional mapping,
dependencies/no cycles, imports/retirement и local links. Historical и current
scope разделены, ни один не заменяет runtime/CI/отдельное review/human acceptance.
Полная Git history обязательна. Actual результаты нового candidate — в аудите,
старые green runs относятся только к своим SHA.
