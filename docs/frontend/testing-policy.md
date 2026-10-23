# Проверки по области изменения и карта тестов

24.10.2026. Политика выбора проверок для новой очереди. Не считать старый PASS
результатом нового candidate. Эта редакция не удаляет runtime/security tests
и не сужает обязательный CI: изменения набора выполняются в MS-T011 либо при
доказанной замене конкретного consumer внутри пилота/cohort/auth задачи.

## Профили работы

| Изменение | Локально | Перед приёмкой/интеграцией |
| --- | --- | --- |
| Только очередь/docs | check_workflow_docs, check_product_source, preservation и tests validators | Не запускать PG/browser только ради MD |
| Данные одной темы | schema/content preservation, ссылки, затронутая сборка | Representative UI, если изменился тип блока |
| Общий компонент/интерактив | typecheck, affected unit/component tests | Affected browser light/dark, mobile/desktop, keyboard; жесты для графика |
| Полный класс | все source/documents/URLs/anchors/media cohort, build | каждый уникальный interactive + representative pages, не одинаковый suite на каждый урок |
| Content publication/SSG/runtime boundary | targeted tests и реальная build/serve проверка | Mandatory managed target/combined gate по target-runtime |
| Identity/staff/schema | соответствующие API/PG/permission tests | auth/staff/browser/fresh-upgrade по scope |

Действующие команды npm test, npm run typecheck и verify_repo сохраняют своё
текущее значение. Избирательные команды не называть full PASS. При введении
новых fast/UI/tooling profiles обновить wrappers/CI и проверку полноты явно.
При прямом запуске Vitest verification-evidence.test.ts требует npm context;
его не включать случайно в targeted UI command. Полный typecheck включает API
generation и React Router typegen, а не только компиляцию одного файла.

## Решения по текущим тестам

| Файл/группа | Решение и условие |
| --- | --- |
| frontend/tests/shell.test.tsx | Переписать при замене SiteShell: убрать exact-Django DOM/SVG parity, сохранить links/landmarks/focus нового chrome |
| frontend/e2e/parity.spec.ts | Удалить из normal redesign gate после явной замены условия визуального parity; legacy comparator оставить только opt-in historical comparison |
| frontend/e2e/i02.spec.ts | Убрать old visual comparison после замены; HTTP redirects/assets404 перенести в единый route suite |
| frontend/prototypes/home/home.spec.ts | Переписать в MS-T002: expanding search вместо old field, нет section-filter, новые header/footer; полезные keyboard/grade/dialog scenarios сохранить |
| frontend/prototypes/home/landing.spec.ts | Перенести public scenarios в MS-T002, preview auth assertions заменить в MS-T009 |
| prototypes/home/quadratic*.spec + lesson-regressions/accessibility | В MS-T001 выделить проверки общих controls для нового линейного урока; специфичные для квадратичной функции сценарии перенести при её runtime-интеграции в MS-T006. Touch-cancel/zoom/contrast regressions сохранить |
| Новый линейный урок MS-T001 | Проверить полноту исходных блоков, линейную математику и реальные Content/SSG/URL переходы. Совпадение JSX квадратичного preview не доказывает перенос другого урока |
| tests/test_i03_account.js и test_i03_identity_api.js, i03_runtime_flow.js | Удалять вместе с old static account.js/identity-api.js только после отсутствия consumers и замены meaningful assertions в MS-T009 |
| tests/test_i02_schema_dispatch.js, frontend/tests/dispatcher.test.ts | Убрать сравнение с историческим dispatcher после его retirement; объединить fixtures/cases вокруг единственной текущей реализации, сохранить unsupported/raw/secrecy negatives |
| tests/test_i02_ui_contract.py, scripts/check-validators.mjs | Разделить текущую schema/security проверку и retired fixture gallery; нельзя удалить защиту public-data leakage из-за I02 в имени |
| frontend/tests/verification-evidence.test.ts | Отдельный tooling profile при изменении runners; дорогие temporary Git/npm runs не выполнять на каждой правке урока. Удалять только с retired verify:foundation |
| tests/test_migration_r03_frontend_receipts.py | Сохранить generic empty/failure/wrong-id/skip rejection; убрать исторические exact counts при пересборке profiles, не ослабляя полноту |
| frontend/tests/route-foundation.test.ts | Объединить с actual route contract, сохранить debug production exclusion |
| frontend/tests/api-types.test.ts | Negative TypeScript примеры сохранить в typecheck; пустой runtime assertion можно убрать с переносом файла в type-only suite |
| quadratic-math.test.ts | Сохранить чистую математику, не повторять все формулы во всех browser projects |
| quadratic-interaction.test.tsx и graph browser tests | Component: state/cancel; browser: actual touch/keyboard/reset. Разные уровни, не считать одинаковыми только по названиям |
| API, owner/CSRF/session/logout, staff-* tests | Сохранить при UI переносе; заменять selectors, не authorization semantics |
| publication, fresh/upgrade, restore, content/media, int64 contracts | Сохранить. Возраст и migration prefix не являются основанием для удаления |
| preserved-contracts и historical_sources tests | Сохранить explicit provenance/unknown-edit refusal; old52-task policy заменяется current queue validation |

Не удалять тест при работающем legacy consumer. У каждой выведенной проверки
должна быть причина: consumer удалён либо invariant проверяет названная замена.
Наличие TypeScript/React в названии нового файла не доказывает эквивалентность.

## Сокращение повторов

Один полный HTTP inventory вне browser matrix; не повторять 263 URL на девяти
viewport/browser projects. Все страницы проверять на полноту данных и build;
для одинакового компонента — representative UI и крайние content cases.
Dark/light, zoom200, reduced motion и touch проверять на соответствующих controls,
а не размножать каждый сценарий на каждую тему. Браузерный compatibility/release
набор остаётся отдельным, пока пользователь не примет изменение его требований.

Скриншоты успешных сценариев — только по запросу visual review. По умолчанию
failure trace/screenshot; outputs игнорируются Git. Агент читает краткий итог и
ошибки, не полный JSON успешного прогона. Не повторять неизменённый успешный
набор без нового diff, failure или неразрешённого concern.

Самопроверка не отдельное review. Открытые ошибки, skipped/timeout и отсутствие
среды указываются явно; локальный docs profile не объявляется runtime readiness.
