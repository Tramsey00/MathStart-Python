# Дополнение о доставке/публикации Content v1.0.2

PROPOSED. DTO публичного content — снимок доставки для V02/V04/I02/I03, отдельный
от замороженного TopicDTO и публичного exercise contract. Дополнительный read adapter V02
`GET /api/v1/content/pages/{slug}/` описан отдельным OAS; он не реализован.
Publisher/build consumers напрямую используют тот же проверенный DTO.

## Доверие, точные поля и SEO

ContentDelivery содержит delivery_version, существующий integer id, slug, page_type,
title, nullable grade_id/subject_id/section_id, order, body_html, is_published
со значением const true, seo{title,description,canonical_path}, created_at/updated_at,
source{path,source_digest,render_digest}, assets в порядке загрузки.
Обязательны все поля, дополнительные поля закрыты; см. [schema](delivery-v1.schema.json).
Digests — SHA256 в нижнем регистре, 64 символа; source — точные байты Git/files,
render — точные байты опубликованного payload, assets — точные байты; digest снимка
publication остаётся неизменённым алгоритмом `content.services.publishing.digest`,
его нельзя смешивать с этими hashes. Доверие основано на артефакте/digest publisher,
прошедшем review, и никогда только на поле DTO.

В LessonHost попадает только созданный автором/проверенный publisher HTML/math/SVG.
Сохранять IDs, anchors, SVG geometry/text/ARIA, formulas, legacy self-check answers в details,
разметку template components, порядок стилей и scripts. Экранировать любой текст user/LLM;
ввод не исполняется и не повышает уровень доверия. Legacy details — намеренно публичная
авторская самопроверка; assessed answer_key/validation_spec/canonical_solution и private
reveal/exchange fixtures никогда не входят в build/manifest/bundle. Используется закрытый
allowlist публичного экспорта, а не SELECT* из таблиц ContentPage/user/session.
Private detail staff может содержать неопубликованный авторский content, но имеет собственные
DTO/auth/no-store и никогда не попадает в публичный snapshot.

SEO воспроизводит fallback ContentPage.meta_title/meta_description из source;
custom metadata обрабатывается через baseline strip. Язык Russian, UTF-8 viewport,
canonical абсолютный и с доверенным origin по get_absolute_url: для home `/`, прочим slug
`/<slug>/`. Alias главной `/glavnaya/` сохраняет 200 с canonical `/`. Head/footer/header,
поиск/filters/order каталога из content.services.catalogue и текущие tokens сохраняются.
Выполняется pre-render каждого опубликованного URL; unknown/unpublished дают 404,
SPA wildcard 200 запрещён. Sitemap использует published pages, updated_at,
priority/frequency из baseline content/sitemaps.py; robots разрешает public, запрещает /admin/,
содержит абсолютный sitemap. Redirect применяется только после route 404: активный точный old_path,
постоянный 301/временный 302; без self-loop, работающая страница имеет приоритет,
архивные redirects сохраняются. Массовая смена slug запрещена.

Публичные GET/HEAD обслуживают активированный release; baseline публичные page views также
принимают другие methods без mutation. Сохранять их read-only 200 через handler активированного
snapshot gateway для остальных methods, включая OPTIONS, при этом unsafe methods всё ещё проходят
CSRF checks; нельзя молча менять baseline на default target 405. Account — только GET
(в baseline HEAD даёт 405), private no-store, без SSG. Debug fixture gallery доступна только через
GET/в development; в nondebug — 404. API limits рассматриваются отдельно.

## Assets и lifecycle

Каждый упорядоченный asset задаёт storage_key/public URL, kind style/script/media,
sha256, load order и script lifecycle none/mount_dispose/full_document.
Сохранять все 263 lesson sources/97 local CSS/7 local JS и shared assets/media.
Content source manifest независим от rendered snapshots/runtime text. Import сохраняет
существующие media keys и seed hashes; allowlist public paths запрещает traversal,
абсолютные filesystem paths и private paths. CSP/asset MIME/loader policy проверяются
в реализации V02/I03; произвольные загруженные scripts запрещены. Общие math dependencies
загружаются раньше local scripts. Для каждой семьи scripts реализуется
`mount(root,config)->dispose` либо явно проверенная full-document navigation.
Dispose отменяет observers/timers/RAF/listeners; queries ограничиваются root; прежний lesson CSS
удаляется; тестируются StrictMode remount, back/forward и повторный resize. Один widget
не подтверждает все семьи scripts. Никакого redesign/reset/library.

## Контракт операции публикации

DB/files/assets/SSG не могут commit атомарно. V04 владеет durable journal и DB transaction;
I02/I03 — renderer сборки; V05 — active pointer reverse proxy. Operation UUID и idempotency key,
ожидаемый active release и ожидаемые source/published digests привязываются к замороженному plan;
journal содержит очищенные status/timestamps, previous/next release, digest manifest,
затронутые paths, stage, failure code и resume cursor. Credentials и private DTO не хранятся.
Schema journal в delivery-v1.schema.json задаёт допустимые стадии, но НЕ является table migration.

Последовательность: VALIDATED -> STAGED -> DB_COMMITTED -> ACTIVATING -> ACTIVATED -> COMPLETE.
Каждый переход регулируется протоколом P1 ниже и durable authority платформы.
До записей выполняются preflight source validation/неизменность identity/conflicts.
Assets и полный public HTML/catalogue/sitemap/redirect manifest размещаются в operation-specific
директории; проверяются все hashes и отсутствие private export. Durable pending slot уже захвачен;
затем захватываются короткие gate/domain locks в порядке платформы; повторно проверяются ожидаемый
active release/текущие snapshots; ContentPage+LessonPublication+DB revision и journal DB_COMMITTED
фиксируются вместе. Activation compare-and-swaps PostgreSQL active descriptor на соответствующий
release/manifest под актуальными owner/fence/lease (P1). Затем проверяются public probes и записывается
COMPLETE. Успех не сообщается до завершённого activation. Повтор того же key/plan возвращает ту же
operation; другой key/body либо неожиданный release/digest приводит к 409/conflict.

После ошибки DB edition и public active edition могут временно различаться; public reads ОБЯЗАНЫ
последовательно использовать snapshot/manifest active edition и никогда не смешивать свежий DB title
со старым SSG body. Staff показывает pending edition отдельно. Для этого нужны release snapshot/
activation representation V04 и проверенная дополнительная schema V01. Если выбранное хранилище
не может согласованно отдавать active snapshot, публичный сервис во время переключения должен быть
недоступен с 503, а не отдавать смешанный успешный результат; до заявления о parity необходимо одобрить
альтернативную ADR delivery.

Unpublish немедленно удаляет URL из следующего active manifest/catalogue/sitemap, сохраняя DB row/history;
прямой запрос получает 404, если явно сохранённый redirect не применим. До окончательного успеха
инвалидировать/purge cache entries и проверить прогретый cache и уже открытую навигацию.
Freshness измеряется при завершении operation: все probes видят тот же новый release; числовой SLA
здесь не выдумывается. Параллельные publish/unpublish сериализуются на activation gate.

| Сбой | Наблюдаемый результат и восстановление |
| --- | --- |
| До staging / конфликт validation | Нет изменений DB/public; ненулевой результат или безопасный conflict; исправить source и создать новую operation. |
| Частичный сбой assets/renderer | FAILED_PRECOMMIT после доказательства отсутствия commit; предыдущая публичная версия цела; retry — новая operation с совпадающим проверенным source. |
| После staging, до DB commit | Rollback DB; предыдущая active версия цела; текущий владелец или takeover продолжает ту же immutable staged operation, без заявления об успехе. |
| После DB commit, до activation | RECOVERY_REQUIRED; journal+DB долговечны, старый public snapshot цел; продолжить вперёд с точным manifest под gate. |
| Pointer переключён, подтверждение/journal update потеряно | Проверить pointer+digest; идемпотентно отметить ACTIVATED/COMPLETE после public probes, никогда повторно не применять DB write. |
| Cache purge/health сбой после activation | RECOVERY_REQUIRED/ненулевой результат; сохранить оба manifests; исправить/purge вперёд под текущим fence; rollback требует отдельного решения человека и не может молча освободить pending. |
| Устаревший expected release при конкуренции | 409; не перезаписывать победившую operation и не очищать её journal. |

Cleanup разрешает абсолютные targets внутри директории operation; удаляются только принадлежащие
ей незадействованные staging после доказательства retention/recovery. Нельзя удалять рабочие media,
source или paths другой operation. Dry-run проверяет/подготавливает данные в изолированном operation root
с явными filesystem side effects, но без DB publication или записи active pointer; если команда target
использует SQL rollback, это должно быть точно обозначено. Baseline bootstrap dry-run пишет SQL,
затем выполняет rollback, тогда как publish dry-run проводит preflight без сохранения; этот исторический
факт сохраняется.

## Исключения baseline

Рабочие БД Руслана и Ильи, а также disposable source reference Ильи остаются раздельными;
CRLF/LF и расхождения пяти payload не нормализуются. Legacy unpublished materialy/pamyatki
сохраняются при upgrade. [Матрица F01–F04](parity-matrix-v1.json) копирует принятые
положительные критерии Ильи: 13baybars исправляет к I03 и проверяет в I05; обязательны все
360/768/1440, F04 проверяется при обычном масштабе (одного увеличения недостаточно).
R02 не выполняет UI исправления и не заявляет новые browser-проверки.

## B02 Полная сборка public и передача каталога

[Контракт public build](public-build-contract-v1.json) определяет предлагаемый формат
frontend/build. V04 формирует release-root/index.json (PublicBuildIndex) и
release-root/pages/<id>.json (ContentDelivery) для КАЖДОЙ опубликованной страницы. I02 может
перечислить все routes до rendering и не должен самостоятельно определять slugs.
Активированный `/_content/index.json` атомарно разрешается в один полный release с no-store;
page files загружаются относительно неизменяемого корня `/_content/releases/<release_id>/`
и проверяются до использования. Build читает те же артефакты напрямую. Эти static delivery paths
предложены, но не являются дополнительными реализованными APIs или заявлением о target runtime.
Asset URLs/digests берутся из упорядоченных per-page Asset arrays; весь их набор сверяется с index.

Index содержит все published page IDs/slugs/types/canonical paths, упорядоченные catalogue grade/
subject/section ID/title/slug/order relations и ordered topic ID/title/slug/order/relations/URL,
home aliases, сохранённые активные fallback redirects, метаданные sitemap и system URLs.
Для каждой страницы существует проверенный Delivery reference. HOME имеет canonical `/` и alias
`/<home-slug>/` со статусом 200; в sitemap входят только canonical page URLs, в порядке ID.
Account/admin/private APIs и unpublished pages не попадают в public files. URLs, delivery paths,
IDs и relations уникальны/полны; каждому topic соответствует published topic page.
Build с отсутствующими/повторными/чужими IDs, невалидными relations, path traversal или private fields
завершается ошибкой до activation. Publication вместе удаляет unpublished entries из всех новых
page/index/catalogue/sitemap assets, сохраняя их историю в private DB.

Catalogue adapter воспроизводит catalogue_context и templates/includes/catalogue:
строки topics сортируются по grade order/ID, subject order/ID, section order/ID, topic order,
title и ID с baseline PG ordering/NULL/collation. Экспортируется уже отсортированный topic list,
чтобы frontend не повторял database collation. Параметры — строки QueryDict: повторные q/grade/subject
используют ПОСЛЕДНЕЕ значение; неизвестные параметры игнорируются. grade, отсутствующий среди topic grades,
сбрасывается в пустое значение. Доступные topics фильтруются по grade; доступные subjects
дедуплицируются по slug с сохранением первой упорядоченной сущности (subject IDs локальны для grade).
Некорректный subject сбрасывается в пустое значение в этом доступном наборе. q использует Python
str.strip и Unicode casefold substring только по TITLE topic, сохраняя исходные titles; нет transliteration/
normalization/search по body. Пустой q показывает устойчивую группировку по реальным grade/subject/section
entities, выбранные filters открывают details; непустой q показывает плоский список и context labels.
Сохранять fallback labels, count, состояние отсутствия результатов/reset. Filters не меняют grade choices
и не пересортировывают matches. Fixtures включают unknown/cross-grade filters и Unicode negatives;
будущий JS casefold должен проходить их и supplementary Unicode vectors, а не только lower().

Полный реальный disposable baseline index отдельно записан в
review-baseline-public-index.json (279 published pages, 263 topics, 1 home alias);
это свидетельство принятого source profile, а не развёрнутый target release. В другом source profile
числа могут отличаться: перечислять реальные опубликованные строки и никогда не фиксировать counts
или молча экспортировать две сохранённые unpublished pages.

## B06 Read-only наблюдаемость publication

`GET /api/v1/staff/pages/{id}/publication_state/` возвращает закрытый private
PublicationObservableStateResponse при active staff и разрешении ContentPage view ИЛИ change.
Отсутствующая page — 404; нет прав — 401/403; private,no-store. Результат читает activation generation
до и после согласованного снимка journal/DB revision/gate. Возвращать 200 только если pointer descriptor
и gate generation/operation/lease-derived ownership совпадают при обоих чтениях и относятся к проверенным
неизменяемым snapshots; повторить sample не более 3 раз, после чего вернуть 503 вместо смешанного ответа.
Отсутствующий/непроверяемый active snapshot можно показать разрешённому staff как UNAVAILABLE,
а public requests возвращают 503. Чтение не меняет journal/pointer/DB и не возобновляет publication.

Данные содержат page_id, observed_at, state, состояние страницы в active release и DB edition,
и nullable pending operation со следующим release/digest/stage/time, безопасным enumerated failure code,
fence_generation, ownership (LEASED/TAKEOVER_ELIGIBLE), db_committed и activation_status.
Ownership определяется по времени DB; owner identity и lease secret не раскрываются. Не возвращаются
filesystem paths, raw plan, idempotency key, actor identity, credential, publisher body или resume cursor.
Текущий baseline напрямую отдаёт ContentPage и не имеет слоя pending activation; эквивалентное наблюдение —
IN_SYNC/current DB. Новые состояния описывают предложенное разделение публикации DB/assets/SSG
и требуют реальных свидетельств V04/V05.

IN_SYNC: active и DB edition совпадают по release/digest/published state, pending null.
Завершённые и FAILED_PRECOMMIT operations терминальны, не pending; их private journal history и CLI failure
outcome сохраняются. Этот GET описывает текущие editions и нетерминальную operation, а не новую
администрацию journal/history.
PENDING: validated/staged operation оставляет active и DB старыми; после DB_COMMITTED DB edition уже
следующий release, а active остаётся предыдущим. Activation меняет active на новый; ACK journal может
оставаться pending до завершения public probes.
RECOVERY_REQUIRED: `pending.stage=RECOVERY_REQUIRED` с безопасным failure code; DB edition и active
показываются раздельно (старый active после неудачного activation либо новый после ошибки ACK/cache).
UNAVAILABLE: active pointer отсутствует или snapshot нельзя проверить; active null, public requests 503.
При `page_published=false` в соответствующей edition digest/path страницы должны быть null.
Реляционные инварианты (равенство IN_SYNC, committed DB == pending next, согласованность observed generation)
проверяются service сверх JSON Schema. Staff UI показывает эти read-only facts, не выдумывая завершение
и не предлагая новый CMS.

## B07 HTTP methods и приоритет CSRF

Sitemap/robots — views без декораторов, как home/page_detail: safe GET/HEAD/OPTIONS/TRACE читают 200;
любой unsafe method с корректным CSRF также читает 200, отсутствующий token/неверный Origin возвращает 403
ДО rendering или page 404. У HEAD нет body. Замена этих путей на method 405 запрещена.
RedirectFallback выполняется только после фактического 404 для ВСЕХ methods. Для несуществующего
resolved `/<slug>/` CSRF проверяется для unsafe requests первым: 403 без redirect; корректный token
разрешает 404 и lookup. У unresolved legacy URL (например, вложенный путь .html) нет view CSRF hook;
его 404 может стать 301/302 даже для unsafe запроса без CSRF. Сохраняются приоритет active exact match,
работающего view и защита self-loop. Legacy redirect paths содержат кириллический Unicode;
сохранять точное совпадение decoded request.path и сериализацию UTF-8 URI без normalization/double encoding.
Static/media/account/identity/grades имеют собственное поведение methods; см. mapping семейства routes.
Gateway/SSG должны сохранять эти ответы, а не только GET navigation.

## P1 Таблица переходов и окна отказа

[Машиночитаемая таблица transitions](publication-protocol-v1.json) и authority P1 платформы
совместно являются нормативными. Все строки требуют текущий неистёкший owner token, кроме явно
read-only; UUID operation обозначает весь plan, а не страницу. Новая логическая operation не может
сосуществовать с нетерминальной pending. Команды — внутренние результаты publisher/CLI,
не новые staff HTTP APIs. Ошибки возвращают ненулевой код; HTTP adaptation использует безопасный
409 STATE_CONFLICT для BUSY/FENCED/conflict и 503 SERVICE_UNAVAILABLE для неизвестного/недоступного
storage. Обычные ошибки не раскрывают private owner/token/paths.

| Исходное состояние / событие | Долговечный переход и эффекты | Повтор / отказ |
| --- | --- | --- |
| IDLE / новый claim | Проверить active==DB, expected release/source; атомарно выделить generation, journal VALIDATED и pending slot. | Тот же key+plan разрешает исходную operation; изменённый plan — 409. Другая operation — BUSY. |
| VALIDATED / stage | Проверить все неизменяемые артефакты; STAGED. Domain DB не меняется. | Те же hashes дают STAGED; изменённые/отсутствующие hashes — conflict. Crash оставляет pending; takeover продолжает. |
| VALIDATED или STAGED / precommit failure | Доказать db_committed=false и отсутствие activation; атомарно выставить FAILED_PRECOMMIT и освободить pending. | Вернуть сохранённую terminal failure; retry требует новую operation. |
| STAGED / commit | Проверить plan/source/active и fence; domain mutation+DB edition+journal DB_COMMITTED/db_committed=true в одной transaction. | Повтор той же committed operation возвращает DB_COMMITTED; второй mutation нет. При потере ACK сначала читать journal/DB. |
| DB_COMMITTED / намерение activation | До попытки descriptor CAS сохранить ACTIVATING, activation_status=UNKNOWN. Public продолжает отдавать предыдущий snapshot. | Намерение неизменно. Crash до CAS оставляет operation pending; следующая публикация запрещена. |
| ACTIVATING / activate | Короткая fenced transaction сравнивает полный previous active descriptor и устанавливает next+manifest+current generation; journal ACTIVATED/APPLIED коммитится вместе. | Совпадающий целиком operation/release/digest descriptor возвращает ALREADY_ACTIVATED; посторонний pointer — conflict, его не перезаписывают. |
| После commit / activation failure или неопределённый ответ | RECOVERY_REQUIRED; db_committed остаётся true. UNKNOWN никогда не означает rollback или завершение. | Согласовать authoritative DB descriptor под текущим владением; не повторять DB mutation и не выполнять speculative external activation. |
| RECOVERY_REQUIRED / reconcile | Точные next operation/release/digest: APPLIED -> ACTIVATED. Точный previous descriptor: NOT_APPLIED -> DB_COMMITTED для нового fenced intent. Чужой/отсутствующий/повреждённый descriptor: остаться RECOVERY_REQUIRED и fail closed. | Повторное чтение даёт тот же результат; записывать изменения можно только с текущим token. APPLIED от старого поколения ТОЙ ЖЕ operation — допустимая durable history, но не полномочие старого owner. |
| ACTIVATED / purge+health | Проверить все public URL/catalogue/sitemap/unpublish/cache behavior для точного active release. Сохранить COMPLETE и освободить pending только после перепроверки current fence/descriptor. | Повтор COMPLETE возвращает сохранённый результат и не переключает старый release поверх более поздней operation. Сбой -> RECOVERY_REQUIRED/APPLIED; slot сохраняется. |
| Любой нетерминальный этап / истечение lease, crash, surrender | Slot/journal остаются. CAS takeover увеличивает fence; до commit сохраняется стадия; после commit -> RECOVERY_REQUIRED/OWNER_LOST с сохранением фактов commit/activation; перед продолжением нужен reconcile. | Проигравший конкурентный claim; старый owner fenced при renew, commit, activate, acknowledge, cleanup и release. |

UNKNOWN охватывает потерю соединения до/после commit activation transaction.
Поскольку descriptor и факт activation находятся в одной DB transaction, recovery может
определить, зафиксирован ли next или остался previous, не доверяя worker ACK.
Во время activation gateway закрепляет целиком previous либо next release; отсутствующие файлы
или непроверяемый descriptor дают 503, а не смешанный 200. Takeover и activation конкурируют за
ОДНУ строку lock: первым зафиксированный commit определяет durable outcome; takeover первым
блокирует старый activation через fence. Истечение lease посреди transaction перепроверяется при
защищённой descriptor/domain SQL mutation; statement под gate — точка линеаризации (platform P1).

Journal `db_committed` монотонен; recovery может изменить stage, но не сбросить его.
`activation_status`: NOT_STARTED до intent, UNKNOWN пока результат не подтверждён,
NOT_APPLIED после подтверждения previous, APPLIED после подтверждения matching next.
Recovery cause codes включают OWNER_LOST, ACTIVATION_UNKNOWN и POINTER_CONFLICT.
Observable GET не захватывает claim, не запускает reconcile и не продлевает lease. Он возвращает pending,
даже если lease истёк; ownership=TAKEOVER_ELIGIBLE всё ещё блокирует следующую публикацию.
Committed pending должен совпадать с DB edition; при ACTIVATING active ещё может быть старым,
а recovery после lost-ACK — уже новым. COMPLETE/FAILED_PRECOMMIT никогда не являются pending.
Read-only sampling согласованности охватывает active и pending fencing state; новые поля — безопасные
private observations, а не capability. RECOVERY_REQUIRED может быть precommit при db_committed=false;
только committed pending обязан совпадать с DB edition. Lease status вычисляется из gate, не timestamp journal.
Runtime concurrency, видимость gateway и crash injection остаются обязанностями V04/V05.
