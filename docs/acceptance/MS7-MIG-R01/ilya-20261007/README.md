# Evidence Ильи — импорт R01, 08.10.2026 Europe/Moscow

Canonical application source: `8c11edadc8debc81432d1db1145feac504f09061`.
Предыдущий candidate документов: `43b4fa10aec2af589c51857d037e973215557255`.
Новый exact HEAD/tested merge-ref/CI публикуются в [PR46](https://github.com/Tramsey00/MathStart-Python/pull/46).
**MIG_BASE_SHA PENDING; R01 INCOMPLETE; MIG-G0 PENDING; ADR-0006 Proposed.**

[Текущая scoped запись](current-decision.json) основана на live-комментарии
[13baybars, 07.10.2026 23:56:12 Europe/Moscow](https://github.com/Tramsey00/MathStart-Python/pull/46#issuecomment-6046690988):
D03 принят в UI/content зоне; D02 принят как исходный baseline с F01–F04 и
обязательным follow-up. Руслан напрямую выбрал сохранить тот же source SHA
с findings, без исправления исходников. Коллективные D02/D03 остаются PARTIAL /
PENDING; это не финальные Task Approval R01, MIG-G0 или принятие ADR.

## Три независимых источника

| Источник | Наблюдение / предел | Доступное evidence |
| --- | --- | --- |
| Рабочая БД Руслана, исходный аудит R01 | 263 topics совпадают с source/publication; 13 структурных body HTML LF/CRLF variants, normalized substantive drift не обнаружен; два retired unpublished records сохранены. Это только данный runtime. | [schema/aggregate manifest](../runtime-data-manifest.json), [rendered digests](../rendered-runtime-digests.json) |
| Рабочая БД Ильи, отдельный read-only аудит | Пять конкретных опубликованных payloads имеют substantive drift HTML/CSS/JS и metadata: home, catalogue, linear, power, circle. Не доказано соответствие всей БД старому commit. БД не синхронизировалась; fingerprint совпал до/после preflight/smoke. | [drift report](package/drift-report.md), [before](package/working-db-before.json), [after smoke](package/working-db-after-smoke.json) |
| Disposable baseline Ильи из exact canonical source | Fresh-install PASS; 279/279 pages exact, 263/263 publication digests, missing/unexpected/mismatches 0; шесть routes и 15 CSS/JS HTTP PASS. UI снимался здесь на port8002, DB port55447 с отдельным volume/runtime. | [fresh smoke](package/fresh-smoke-summary.md), [commands/exit codes](package/commands.json), [parity](package/source-published-parity.json), [HTTP](package/disposable-http-check.json) |

Фраза «13 LF/CRLF различий без содержательного drift» не относится к рабочей
БД Ильи. Новых запросов к любой рабочей/его disposable БД при импорте нет.
Python приложения Ильи **3.14.7**, Django5.2.16/PG16.15; artifact tools
Python3.12.14/Pillow12.3.0. Основной локальный R01 baseline Python3.12.10
отдельный; версии CI требуют собственного current-head результата.

## Отчёты и ограничения

- [UI/content report](package/ui-review-report.md), [summary](package/ui-review-summary.json),
  [63 functional PASS + одна observational group](package/ui-checks.json).
- [Screenshot index](package/screenshot-index.md), [baseline atlas](package/baseline-overview.jpg),
  [all screenshot metadata/hashes](package/all-screenshots.json),
  [viewport metadata](package/viewport-baseline-manifest.json).
- [Обязательный F01–F04 follow-up](follow-up-F01-F04.md).
- [Browser provenance](package/browser-evidence.json),
  [historical preflight](package/preflight-summary.md), [original export README](package/README-EXPORT.md).

Один Codex in-app browser surface. CSS viewports 360×800,768×1024,1440×1000,
DPR1; JPEG resampled, primary raster 345×767,753×1004,1425×990. 101 evidence
screenshots (18 primary +18 supplementary full-page +65 interaction/content);
один ранний diagnostic сохранён и исключён из baseline. Review crops/atlas —
производные навигационные материалы, не дополнительные baseline screenshots.
WebView2 .53 подтверждён user-provided UA и running executable metadata;
installed registry .62, связь executable с сессией не доказана. Отдельная
версия IAB неизвестна. Cross-browser/touch/full accessibility/exact pixel
comparison и новый canonical verify_repo в browser-only review **NOT RUN**.

HOLD/PENDING и будущие действия в импортированных preflight/UI reports —
исторические выводы до последующего человеческого решения. Они сохранены
без редактирования. Current decision отдельно объясняет их статус; 63 PASS
не означает отсутствие визуальных defects или завершённый E2E suite.

## Байты, provenance и доступ из PR

[Import receipt](import-receipt.json) включает каждый ZIP member, SHA256/size
и ожидаемый Git blob OID, включая package manifest без его собственного
self-digest. Archive SHA256:
`63d0bca0618dee6016669e07706612edd9f1ef50be26de4c238eb043935e9313`.
232 files,31,057,740 member bytes; исходный ZIP23,865,527 bytes проверен и
остаётся на Desktop, без изменений. Все его members импортированы exact,
без повторного privacy/line-ending преобразования; узкий -text атрибут
сохраняет эти байты в Git. ZIP не дублируется в repository.

[Package manifest](package/PACKAGE-MANIFEST.json),
[export provenance](package/EXPORT-PROVENANCE.json) и
[export privacy review](package/SECURITY-PRIVACY-REVIEW.json) сохранены.
Upstream export ранее заменил narrative names на роли и абсолютные пути на
portable references; исходные/export hashes разделены. Original unexported
файлы не выдаются за доступные в repository. Adjacent external ZIP manifest/
.sha256, упомянутые в export README, не предоставлены; import receipt
независимо проверяет весь ZIP и все members, включая PACKAGE-MANIFEST.

Все screenshot/report ссылки относительные и доступны из PR; localhost URLs —
исторический контекст, не опубликованный review server. SOURCE_AT_8c11edad —
reference к [canonical Git source](https://github.com/Tramsey00/MathStart-Python/tree/8c11edadc8debc81432d1db1145feac504f09061),
не отсутствующий дублированный source каталог.
Воспроизводимая проверка exact imports/Git blobs/current links/historical
preservation: [utility](../tools/validate_ilya_import.py) и
[результат](import-validation.json). Package manifest не включает себя;
общий record manifest также исключает себя.
