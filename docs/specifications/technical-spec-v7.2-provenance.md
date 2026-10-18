# ТЗ v7.2: источники и редакторская сверка

Сверка18 октября2026 завершает перенос источника в рабочую редакцию; статус
редакции остаётся DRAFT / HUMAN_PENDING до общей проверки кандидата и независимого
review. Будущая продуктовая программа не реализуется в рамках MIGRATION.md.
Исторический G0 v7.1 сохранён и не переносится как approval новой редакции.

| Артефакт | SHA256 |
| --- | --- |
| [Полный v7.1,114 страниц](sources/technical-spec-v7.1.pdf) | `e477bf8c351c6b9453448080ed2e7283ad2b40cca82931906a5650d757d70acd` |
| [Рабочий v7.2,32 главы](technical-spec-v7.2-draft.md) | `c6be84b2932f1e79821c11f18fd5fa1463507793ace30ecbc47804d45478c6f8` |
| [52 исходные карточки и disposition](../acceptance/migration-execution/product-task-disposition-draft.json) | `dc25307bfb1b7f143ff565b1bb474e8a74faef3b2dfaa88f9d889f80ba404c0e` |

[Подробная сверка](../acceptance/migration-execution/product-source-audit.json)
содержит68 конкретных исправлений расположения ≤/≥/→ с номерами страниц source.
В этих исправлениях слова и численные значения не менялись: строки сопоставлены
по тексту с геометрическим извлечением PDF; исходные расположения знаков сохранены
рядом для аудита. Дополнительно визуально просмотрены страницы6/13/14/15/16/24/25/85:
квоты упражнений, направление13 рёбер, правила статусов, математические лимиты,
context budget, evaluation/performance и dependency semantics.

Первичное механическое сравнение дало2448/2822 совпадающих содержательных строк
и374 несовпадающих. Это диагностический результат, а не процент приёмки. Разобраны
все несовпадения; основные группы изменений перечислены ниже. Перенос строк и
сдвинутые glyphs не являются изменением требования.

| Источник | Решение в новой редакции |
| --- | --- |
| Обложка, главы1/2/31/32 | Разделены исторический G0/старый main и новая редакция; текущий SHA и readiness определяются evidence, без присвоения старых approvals. |
| Framework и file areas, в том числе страницы7/10/23/29/57/68–78 | ADR-0006: FastAPI/Pydantic, SQLAlchemy/Alembic, React/TypeScript и Node только в build; старые contracts/model identities/data/math сохранены. |
| Страницы6/15/16/24/25 и повторения FR/NFR/cards | Восстановлены точные ≤/≥ и →. Future Analyzer/Tutor/Progress/eval quotas остаются future. Локальные80 sequential HTTPS запросов не выданы за future200 ordinary/10 concurrent или30 AI/2 concurrent. |
| Календарь37–42, сроки карточек45–78, историческая доска в главе32 | Сохранены в полном PDF и исходных card bodies. Действующий перенос выполняется единым заданием; персональные очереди/даты отменены пользователем. Новые сроки/назначения не созданы. |
| Dependency/card поля45–85 | Все52 canonical IDs и115 явных рёбер сверены отдельно по типам: HARD60, CONTRACT24, HANDOFF6, INTEGRATION25. SOFT — неблокирующая guidance; отдельных task edges в source нет. |
| Source опечатки MS7R07/MS7I15/MS7V06 в описательном DAG/downstream тексте | Это ссылки на canonical MS7-R07/MS7-I15/MS7-V06, не дополнительные карточки. Canonical52-card ID set и типы рёбер не менялись. Исходные написания сохраняются в source excerpts. |
| Холодная установка в главе26 | Девять шагов и четыре review corrections оформлены как ordered lists; номер сложности4 и поле16 карточки перестали быть ложными заголовками глав. Чистая установка существующего сайта имеет отдельное реальное evidence. |

Реестр восстанавливает полный body каждой карточки непосредственно между её
заголовком и следующим заголовком PDF, включая исторические calendar fields.
Прежние частичные excerpts опускали часть этих строк; теперь исключения не
маскируются как дословная полнота. Running page heads/footers могут присутствовать
в raw excerpt, а PDF остаётся каноническим источником layout. Для каждой карточки
сохранены original_result/acceptance reconciliation, platform disposition,
платформенный эквивалент и scoped target evidence там, где он уже существует.
47 future equivalents остаются PLANNED; их пустое runtime evidence не является
провалом существующего сайта и не заменяется фиктивной реализацией.

Scoped CI c205ef1, clean installation c205ef1 и новый admin presentation delta
относятся только к указанным состояниям. Final combined target, девять browser
projects, полный visual review, оставшиеся operations и независимый reviewer
ещё не закрыты. После их завершения ссылки/evidence должны быть обновлены до
передачи кандидата человеку; этот документ не присваивает READY/COMPLETE.

Воспроизводимая scoped сверка из Git root (полная Git history нужна для сравнения
с сохранённым953fe97):

```text
python docs/acceptance/migration-execution/check_product_source.py
```

Она проверяет source SHA,32 главы/52 IDs/115 typed edges, original result и
acceptance objects,68 glyph-only corrections и hashes provenance. Это233
документных assertions; она не запускает и не подменяет runtime target QA.
Актуальное применение frozen AGENTS/PRODUCT/ARCHITECTURE/README изложено в
[руководстве target runtime](../target-runtime.md), исходные bytes сохранены.
