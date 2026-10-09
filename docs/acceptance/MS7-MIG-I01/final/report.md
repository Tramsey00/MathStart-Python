# MS7-MIG-I01 — final verification checkpoint

Дата: 09.10.2026, Europe/Moscow. Владелец:13baybars.
Issue: https://github.com/Tramsey00/MathStart-Python/issues/40.
Task остаётся INCOMPLETE до публикации exact implementation SHA, CI и независимой приёмки.

Accepted input / текущий HEAD: `8d958aeeb17da46839722441425ccbb5889e2ab7`.
MIG_BASE provenance: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
Canonical appearance: `8c11edadc8debc81432d1db1145feac504f09061`.
Ветка ms7-mig-i01-foundation; отдельный task-worktree. HEAD не содержит ещё не закоммиченную реализацию; точные текущие байты привязаны [manifest](content-manifest.json).

## Результаты

|Проверка|Фактический результат|
|---|---|
|Clean npm ci --no-fund|exit0;217 installed/218 audited;0 vulnerabilities|
|generate:api; typecheck; native ESM validators|exit0;17 historical+24 R02 pins;37 operations;16 DTO validators; route typegen+tsc|
|Frontend unit/component/security|88 PASS,0 FAIL,10 файлов|
|Historical dispatcher JS|5 PASS,0 FAIL, исходный файл неизменён|
|Production build + graph/artifact/export guards|exit0;47 client modules,12 artifacts;debug/fixture/private exports отсутствуют|
|npm ls / npm audit --audit-level=low|exit0/exit0,0 vulnerabilities|
|Isolated Python setup|Python3.14.7;17 locked dependencies --no-deps;pip check exit0|
|python scripts/verify_repo.py|exit0;8/8 checks PASS, только SQLite compatibility|
|Django suite внутри verify_repo|107 run:99 PASS,8 SKIP,0 FAIL; skips требуют PostgreSQL|
|R03 / Harness внутри verify_repo|18 PASS /73 PASS,0 FAIL|
|Отдельные неизменённые contract suites|R02A30;R03A41;UI7; migrationR02 20+11+32=63 PASS,0 FAIL|
|Browser gallery parity|3/3 live SQLite Django/React full-page JPEG pairs byte-identical|
|Keyboard/CSS isolation/overflow|PASS на360×800,768×1024,1440×1000;console warnings/errors[]|
|Git/whitespace/source/frozen history|[Аудит](source-scope-audit.json);tracked diff пустой;unplanned files отсутствуют|
|Evidence links/hashes/privacy|[Проверка](evidence-validation.json);[inventory](changed-files.txt)|

Все версии/полные argv/cwd/выводы/exit codes: [frontend](frontend-commands.json),
[repository](repository-commands.json), [contract/model](additional-contract-commands.json).
Node24.21.0/npm11.19.0;React/DOM19.2.8,React Router7.18.4,Vite7.3.7,
TypeScript5.9.3,Vitest4.1.11. Точные зависимости в неизменённых package.json/lock.
Локальный Python3.14.7 отличается от Python3.12 в baseline CI; это не запуск CI.

## Scope / требования

[Матрица Issue40](requirements-matrix.md) и [§17 mapping](old-to-new-evidence.json).
React Router framework mode:src/app,ssr:false,prerender:[];anonymous index only.
Original CSS/fonts/SVG/cascade сохранены;public/account/staff/debug boundaries.
Gallery содержит весь исходный approved synthetic pack/four states/slots, никакой оценки
математики/прогресса. Strict dispatcher/runtime validators reject malformed input.
В API foundation:canonical generated types,eight-operation transport,fresh CSRF,
safe typed errors,abort/timeouts/latest-read guards,unknown sent-mutation outcome,
без автоматических mutation retries. Реальный target API/full account/staff/P1/P2
не реализован и не проверен. Transport пока исключён tree-shaking из пустых production routes.
I02 selective SSG/catalogue/SEO, I03 LessonHost/widgets, I04 account/staff остаются downstream.

Ни приложение Django,ни authored HTML/CSS/JS,models/migrations/backend dependencies,
accepted contracts,root CI,ни historical approvals/evidence не менялись.
Working PostgreSQL и R01 baseline не использовались. Создана только новая собственная
SQLite DB/runtime/venv внутри ignored var task-worktree: [изоляция](repository-isolation.json).
До setup доказаны sqlite engine,точный новый путь,отсутствие существующей DB,media/static
внутри нового runtime; .env не создавался/копировался.730 source materials неизменны.
[Reproducible isolated runner](verify_repository.py) отказывается использовать существующее
окружение/DB или .env; повтор требует нового безопасного fresh пути.
Ни DB/env/browser profiles,ни зависимости/cache/build не входят в candidate inventory.

## Browser / visual

[Индекс10 финальных screenshots](screenshot-index.md), [raw observations](browser-evidence.json).
Текущий Chromium/Google Chrome155.0.8059.27 из User-Agent Client Hints;
отдельная версия Codex IAB недоступна/не подтверждена.
React http://127.0.0.1:5171/__ui__/foundation/ сравнивался с
http://127.0.0.1:8003/__ui__/foundation/ — новым task-local Django SQLite экземпляром.
Это live comparison gallery+shell на unchanged accepted input, не R01 PostgreSQL
и не whole-site/full public-page или target runtime parity.
Ранние checkpoint1/2 source-derived empty-shell snapshots сохранены с прежней квалификацией.

На трёх размерах совпали22 элемента geometry/computed CSS/leaf text;3 JPEGpairs byte-identical.
Skip/Tab/Enter,visible focus,retry focus before hiding,field error Space/pointer,raw input,
loading aria-busy,four slots/unsupported проверены;horizontal overflow отсутствует.
Root не получает gallery tokens/foundation styles,header/footer styles равны.
Визуальный просмотр360/1440 не выявил in-scope дефектов;768 совпадает с Django reference.
Dedicated hover transition NOT_RUN: доступный API не предоставляет hover.
Pointer activation не считается проверкой hover. Независимый reviewer проверяет hover вручную.

## Найденное и исправленное

В финальной стадии функциональный код и dependency manifests не менялись;
сгенерированные артефакты совпали с checkpoint2.
В текущем §17 index добавлены явно platform_disposition/current_status.
Original_result,исторические approvals,checkpoint1/2 оставлены без изменений.

Ошибки постановки browser проверки исправлены без app change:
переключение viewport в двух вкладках сначала затронуло только reference;
provisional captures отброшены,проверка повторена последовательно с innerWidth/Height assertions.
selectOption сам не гарантирует focus;retry Tab/Enter повторён с явным focus selector
и подтверждением activeElement=demo-retry до Enter. Raw initial observations сохранены.
Ранее исправленный checkpoint2 abort-body дефект и две RED regression cases сохранены
в историческом evidence; финальный clean88-test suite подтверждает исправление.
Сейчас нет FAIL в выполненных тестах;Docker diagnostic exit1 — инфраструктурное ограничение.

npm ci предупредил,что esbuild0.28.2 postinstall пока не покрыт allowScripts.
Installation/native build/production checks прошли; manifests/install policy не менялись.
React Router future-v8 notices advisory, future flags не включались.

Автоматическая approval-проверка отклонила новый npm entry point в package.json как
ненужное для verification изменение. Ничего не было записано;команды выполнены
напрямую и сохранены в evidence,manifest unchanged.

## Ограничения / gates / handoffs

1. [PostgreSQL verification NOT_RUN](infrastructure.json):Docker Linux daemon недоступен.
   Нужен работающий daemon либо отдельно разрешённый изолированный PostgreSQL16+,
   отдельные fresh role/DB/test DB/runtime с проверкой подключения до записи.
   Working5432 и R01 использовать нельзя. SQLite99 PASS/8 SKIP не доказывают locking/concurrency.
2. Dedicated hover — независимый manual browser check. Gallery evidence не утверждает
   R01 full-site/page parity. Lesson widgets/formulas/math и F01–F04 — I03/I05.
3. Production gateway404/method/CSRF/cache/redirect parity — V05 deployment evidence;
   local preview tests не заменяют gateway proof.
4. Full target API/P1/P2/session/receipt/recovery/concurrency/browser-cutover NOT_RUN.
   R02 model suites подтверждают только contracts/synthetic models.
5. Current exact implementation commit/PR CI/tested merge-ref пока отсутствуют.
   Root migration-ci сохраняется baseline-only;frontend CI handoff владельцу R03/Руслану,
   не объявлять baseline CI проверкой frontend или целевого runtime.
6. Независимые Руслан UX/integration и Владимир API/security Task Approvals обязательны;
   я не утверждаю собственный результат. [PR draft/review plan](pr-draft.md).
   Accepted calendar/deadline08.10 не переписан;фактическая verification09.10.

F01–F04 unchanged:13baybars fixes no later than I03,mandatory I05 verification before
UI/content freeze. F04:readable360×800 ordinary scale without clipping/overlap,
preserve angles/coordinates/text readout/controls/math;regression768/1440.
Нового pixel/font threshold нет. Independent math/content check может выполнить Владимир.

Rollback после публикации:revert foundation commit(s),сохранив старые source/styles/contracts
и runtime. Оригинальная Django система не заменена и не требует rollback БД.

## Финальный gate

Локальный foundation объём реализован и проверки прошли в указанных пределах.
Пакет подготовлен к разрешению commit/push/PR→ms7-mig-react-fastapi,Refs#40.
Это не завершённая приёмка:implementation SHA/CI/PG-specific evidence/hover/reviews pending.
Никаких commit/push/PR/merge/Issue mutations не выполнялось.

Evidence recorder correction:initial exit1 was a Git CRLF-to-LF conversion warning, not trailing whitespace. Process-local core.safecrlf=false suppresses that warning; no config or original command log was modified. Windows command-length limit was handled by bounded documentation writes.

## Authorized publication preflight — 2026-10-09

Owner accepted this verification checkpoint and authorized commit/push/PR, not independent I01 acceptance. Integration remains exact accepted input; no conflicting remote task branch/PR; login13baybars. Inventory175 files (33 screenshots) passed scoped privacy/security audit. For Git publication, only physical CRLF in final repository-commands.json/repository-isolation.json wrappers was normalized to LF per existing .gitattributes. Parsed JSON and embedded raw outputs are identical. Historical checkpoint1/2 unchanged. Manifest refreshed; code/tests need no rerun for this formatting-only change. Final recorder is a pre-commit checkpoint tool; after publication validate current hashes against the Git tree rather than refreshing historical capture records.
