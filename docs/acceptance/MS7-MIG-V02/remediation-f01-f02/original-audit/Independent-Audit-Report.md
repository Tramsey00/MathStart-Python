# MS7-MIG-V02 — Independent Audit Report

Дата: 13.10.2026, Europe/Moscow. Независимый READ-ONLY аудит. Human Task Approval Руслана не выдаётся.

## 1. Exact source snapshot

Branch `ms7-mig-v02-content`; HEAD и merge-base с `origin/ms7-mig-react-fastapi`: `0c03197e23f69a233c0fcf8bdffa336feca20b92` (V02_BASE_SHA). Merge-base с immutable MIG_BASE_SHA: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`. HEAD — исходный baseline, implementation commit отсутствует.

Все 47 новых файлов untracked. Обычный git diff не показывает их реализацию. Tracked diff, включая staged, пуст. Все файлы доступны для чтения и скопированы для проверки. Независимый полный список с SHA256/размером: `independent-source-snapshot.json` рядом с отчётом. В нём 47 файлов; исходный workspace manifest хеширует 46 и исключает себя. Все 46 размеров и SHA256 совпадают; SHA256 самого manifest: `0a2a37d7141e1b1e4662a4042bb59018995bc20e4b63a1d02b586ee24c266435`. Повторная проверка после аудита не обнаружила drift.

## 2. Actual implemented route inventory

Реальный `runtime.application()` создаёт FastAPI app с 32 зарегистрированными GET operations; registry точно совпадает с routes.json. Независимые HTTP calls вызвали все 32: 31 вернул 200 на разрешённом синтетическом principal/release; publication_state вернул ожидаемый fail-closed 503 без V04 provider.

* `/api/v1/grades/`: GradeListResponse.
* `/api/v1/content/pages/{slug}/`: ContentDeliveryResponse.
* Для каждого ресурса `grades`, `subjects`, `sections`, `pages`, `publications`, `media_assets`, `redirects`, `users`, `groups`: `/api/v1/staff/{resource}/`, `/api/v1/staff/{resource}/{id}/`, `/api/v1/staff/{resource}/{id}/history/` — 27 operations. Closed resource-specific DTO/list envelopes; history — StaffHistoryDTOListResponse.
* `/api/v1/staff/users/{id}/group_choices/`: StaffGroupChoiceListResponse.
* `/api/v1/staff/permission_choices/`: PermissionChoiceListResponse.
* `/api/v1/staff/pages/{id}/publication_state/`: PublicationObservableStateResponse при подключённом валидном provider; 503 без него.

Дополнительно catch-all обслуживает публичные страницы, home alias, sitemap/robots, assets, active/retained immutable build paths и redirect fallback. Это не дополнительные domain GET operations. Реальные repositories/UoW используются; routers подключены, Django normal runtime отсутствует. Staff authentication, HTML renderer и edition observer — явные integration ports, а не фиктивный success.

## 3. Content/catalogue/release parity

На новой PostgreSQL базе после fresh smoke независимо выполнен public_baseline_projection: 279 страниц, 263 темы, совпадающие SEO и порядок с настоящим Django comparator; исходные source bytes доступны и хешируются. SQL только SELECT/READ ONLY, activation не выполняется. Это доказывает metadata/source/order parity, но не полный rendered HTML/browser/asset lifecycle.

Closed schemas, published=true, completeness catalogue/page relations, canonical home URL и alias, index SHA256, body render digest, asset SHA256 и filesystem containment проверяются. Отсутствующий/повреждённый active release даёт 503; raw latest DB fallback отсутствует. Запрос получает один выбранный immutable release. Тест с изменённой pending DB page сохранил прежнюю активную выдачу. Обнаружено ограничение valid asset union — F01 ниже.

## 4. Grades cursor/keyset parity

Реальный PK отделён от номера класса; canonical slug 1..12-klass. Default20/max100; SELECT limit(size+1), порядок created_at/id, без offset. Изменения title/order и удаление уже выданной строки не сдвигают позицию. Невалидный stored grade даёт безопасный 503. Старый и новый signer сравниваются с настоящим Django signing в обе стороны, включая exact bytes, zlib, keyring и отсутствие max_age. Strict cursor scope/page_size/id/timestamp проверки отклоняют bool, tampering, чужой salt/scope, naive timestamp и лишние поля. GET не создаёт профиль/evidence.

## 5. HTTP transport safety

HTTP-level probes: malformed/repeated queries400; unsupported Grades HEAD/POST/CONNECT/BREW400; invalid slug400; неизвестные API/публичные пути404 при валидном release; отсутствие auth401, insufficient permissions403; повреждённый backend/release503. Auto307/422 отсутствуют; только исторический slashless Grades301. API envelopes, UUID request_id, UTF-8 JSON и private,no-store сохранены; internal exception text не отдаётся.

Malformed/duplicate/nonfinite/invalid UTF-8/oversized GET bodies игнорируются и дают200 на Grades согласно явному R02 auth-v1 baseline contract. Это не transport defect: GET не парсит JSON. Raw parser MIME/shape/duplicate/limit validation проверена helper-тестами, но не подключена к mutation HTTP endpoint в V02. Поэтому HTTP-level enforcement raw JSON на будущих writes — NOT VERIFIED. 409/429 не являются действующими outcomes этих read operations; приписывать им PASS нельзя.

## 6. Routing/redirect/media safety

Публичная существующая страница имеет приоритет над redirect. Unknown/draft404; missing active authority503; sitemap/robots берут published active snapshot и доверенный origin. Encoded traversal отрицательные запросы404; digest mismatch503; private пути и неразрешённые assets не выдаются. Assets используют extension/kind allowlist, digest и nosniff; Content-Type выводится из kind/extension. Независимая проверка реального MIME содержимого всех production assets не выполнена.

Обычный Unicode redirect301/302 работает. Missing static/media redirect fallback нарушен — F02 ниже. Default HTML renderer отсутствует и возвращает503 для существующей страницы; безопасная integration boundary, не SPA200. Полная gateway/React/SEO rendering интеграция остаётся за I02/I03/V05.

## 7. Staff permission security

Девять resources соответствуют R01 inventory. V02 требует trusted AuthenticatedIdentity; перечитывает DB active/staff/superuser и effective direct/group permission codes. View OR change соответствует ModelAdmin. Auth/permission precedes private object lookup и ID validation. Независимо: anonymous/inactive401; ordinary/insufficient staff403 на list/detail/history, включая несуществующие объекты; x-role/x-user-id не дают доступа. Superuser получает все nine resources. Default отсутствующий V03 provider закрыт.

DTO не содержит password/session/receipts; history sanitizes message. Staff sorting/filter/search/page-size/cursor revision проверены, включая PostgreSQL Django oracle. User group_choices требует change_user и не открывает Group administration. Staff writes не реализованы; Content mutations403 после authorization. Реальные сессии/revocation/CSRF/object-permission расширения вне baseline не доказаны.

## 8. V01/SQLAlchemy/PostgreSQL correctness

PostgreSQL16.15 dedicated local disposable container; V02 tests создали новые UUID базы на15441 и удалили только собственные test DB. Baseline smoke создал отдельную `ms6_v01_smoke_v02_00cc6f159b5d4c28b81cd12a2b3fefbb`, оставленную для просмотра. Production/shared рабочие базы не изменялись. Native Django redirect probe использовал только эту disposable базу, запись внутри rollback transaction.

Normal target operations SET TRANSACTION READ ONLY; V01 UoW autoflush=False, rollback/close на выходе, без locks/commit/DDL в startup. Отдельный SQL capture собственных GET probes: DML отсутствует. Alembic/V01 tracked code не изменён. SQLite только explicit compatibility, без fallback. Runtime factory запущена в окружении без установленного/импортированного Django.

## 9. Independent tests and exact results

Все PASS ниже получены повторным запуском, а не из implementation report.

| Проверка | Результат |
| --- | --- |
| V02 unittest test_unit/test_http/test_postgres | PASS41, 0 skips:9 unit,15 SQLite HTTP,17 PG |
| V01 unittest test_unit/test_postgres/test_remediation, Linux temporary copy | PASS34, 0 skips:11 unit,23 PG |
| R02 test_migration_r02_*.py | PASS63 |
| R02A test_r02a_contract.py | PASS30 |
| R03A test_r03a_contract.py | PASS41 |
| fresh_install_smoke.py --disposable | PASS |
| scripts/verify_repo.py | PASS8/8; Django109, R0318, Harness73 |
| public_baseline_projection | PASS279 pages/263 topics |
| Runtime application without Django | PASS32 registered operations |
| Test venv pip check | PASS |
| Runtime venv pip check | NOT RUN: pip отсутствует |
| Independent all-route/auth/method/traversal/no-DML probes | Expected statuses confirmed |
| Independent shared asset order / missing asset redirect repros | FAIL contract parity, F01/F02 |

Windows Python3.12.10; Linux Python3.12.15; FastAPI0.115.12, SQLAlchemy2.0.46, Django5.2.16, httpx0.28.1, psycopg3.3.6; Docker client/server29.8.0; Compose5.5.1. Initial sandbox PG attempt was interrupted and is not PASS. Initial R02 errors from long Windows temp path and absent Git metadata were environmental; final short-path copy with its own Git metadata passed63. No implementation validation was weakened.

Assertions are meaningful (real SQL/digests/Django signer/admin ordering/permissions/pending release), but do not cover F01/F02: shared fixture asset always has identical order; missing-asset cases have no corresponding active redirect. Full279-page comparator uses empty assets and cannot prove complete asset families. All nine history routes are callable, but most fixture histories are empty; broad populated history/race coverage remains limited.

Raw logs/probe scripts are under `C:\Temp\mathstart-v02-audit-20261013\var` and at that temporary copy root. V01 output is retained in this audit chat's tool result; original implementation logs were not overwritten.

## 10. Frozen contracts and ownership

60 frozen HEAD blobs independently compared with V02_BASE_SHA and current checkout SHA256: no changes. All47 files fall within V02 backend/tests/evidence/plan/trace ownership. Frontend/root CI/frozen contracts/V01/Alembic/historical approvals unchanged. Original workspace manifest remains byte-identical after audit.

## 11. §17 evidence quality

All three original_result objects (R02A, Grades PR24, historical Content baseline) match R01 index literally. All nine retained command-log SHA256 values match verification.json. Implementation SHA is null; publication/CI/approval pending; baseline HEAD is not represented as published implementation SHA. Existing pending/proposed labels are preserved, and integrations are explicitly NOT VERIFIED. Those hashes validate consistency, not prior execution authenticity; this audit supplies independent new executions. Live GitHub reviews/CI receipts were not re-fetched.

## 12. Findings

### F01 — P2, blocking: per-page asset order breaks the entire valid release

Exact source: `C:\Projects\MathStart-Python-V02\backend\content\releases.py:111`.

Contract: R02 content-v1.md Assets and lifecycle; Asset.order describes load order within each page; public-build-contract assets are the union of per-page descriptors. No accepted contract requires a URL's page-local order to be globally equal.

Reproduction: valid synthetic release references the same `/static/theme.css` with identical storage_key/kind/sha256/lifecycle on home and topic. Change only topic's order0->1; ContentDelivery schema still valid, per-page ordering unique/sorted, asset bytes/digest unchanged. GET `/api/v1/content/pages/topic/` becomes503. `assets[url][0] != asset` compares order as part of shared identity. Because every load scans every page, this also denies unrelated public pages/index/SEO from the release.

Impact: valid publisher artifacts cause release-wide availability loss; no private-data leak observed.

Minimal fix: compare shared asset identity/content fields independently of page-local order, preserving original per-page descriptors. Retain conflict checks for different bytes/digest/kind/storage authority. Add a multi-page varying-order HTTP regression.

### F02 — P2, blocking: missing asset bypasses accepted redirect fallback

Exact source: `C:\Projects\MathStart-Python-V02\backend\infrastructure\http\app.py:217` (redirect handling only at239–244).

Contract: R02 content-v1.md Redirect only after route404, active exact old_path,301/302; historical content/middleware.py applies fallback to every route404.

Reproduction: valid index contains active redirect `/static/old.css` -> `/static/theme.css`, permanent=true; old asset absent, target present. GET old URL returns404 with no Location; target returns200. Same case through real Django RedirectFallbackMiddleware with a real DB Redirect returns301 `/static/theme.css`. `/media/` uses the same failing branch. Ordinary `/old.html` control returns301.

Impact: retained static/media URLs lose redirect compatibility; valid historical links fail. No authorization bypass observed.

Minimal fix: centralize fallback for eligible public404 results after route resolution, using the already pinned release and existing path checks; keep working asset/page precedence and never redirect503. Add301/302 static/media and unknown/no-rule regressions.

No confirmed P1 or separate P3 implementation defects in this audit. Absence of V03/V04/I02 alone is not a finding where the boundary fails closed.

## 13. NOT VERIFIED

Original114-page v7.1 PDF bytes with supplied SHA256 and original60-page migration PDF were not available in inspected attachment/input locations. Local extracted spec.txt/migration.txt and repository migration v1.1/contracts were read; extraction is not independent proof of original PDF hash. Full live GitHub PR24/48/51 approval/CI provenance not re-fetched. Real V03 sessions/CSRF/rotation/revocation, V04 production staged metadata/source trust/activation/recovery, I02/I03/V05 full HTML/gateway/browser/assets/lifecycle, final published commit/CI/human gates, performance and deployment remain unverified.

## 14. Required fixes and handoffs

V02 owner: fix F01/F02, add independent contract regressions, rerun V02/PG checks and rebind evidence to changed source bytes. No fixes were made by this read-only audit. Provide original normative PDFs if exact-hash verification is required at the publication gate. Ruslan: review the concrete updated snapshot and future published SHA/CI; this report does not replace Task Approval. V03/V04/I02/I03/V05 own the documented safe integration ports and full downstream acceptance.

## 15. Verdict

**CHANGES REQUIRED**. Two reproducible blocking P2 parity defects remain despite green supplied regression suites. The audited snapshot is not ready for publication. Repository implementation/evidence/history were not edited; no commit/push/merge/reset/clean/PR/review was performed.
