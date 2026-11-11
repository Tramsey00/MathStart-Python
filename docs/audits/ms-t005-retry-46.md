# MS-T005 — повторная обработка 46 тем

08.11.2026. Ветка ms-t005-grade-7, Issue #61, Draft PR #62.
Input HEAD `9804073f1db5d9399caeccd121ced6a5a45bd2bc`, исходное дерево чистое.
Резервная локальная ветка: backup/ms-t005-before-retry-20261108-9804073.
Проверенный implementation SHA `e994c591d240fbb56a78003f3564f2b553ccc4d4`, tree `c81f2b86d6f5eb56e0c69e6a3b554ac483d09e20`; последующий commit меняет только отчёт/status и диагностический section ID в карте, не учебные документы/маршруты/renderer.

## Результат

Все 46 прежних блокировок повторно обработаны неизменённым convertLesson:
- 24 темы сразу прошли converter + server validation после общих dy исправлений;
- 8 упёрлись в составные дроби. Для них вручную заданы 68 точных MathML substitutions: numerator/denominator, grouping, powers, subscripts, minus, multiplication и authored values сохранены без вычисления/упрощения;
- после MathML 6 из 8 активированы (56 составных дробей); первая тема алгебры (11 дробей) подготовлена до решения URL; Среднее арифметическое (1 дробь) раскрыла ещё один blocker — height заданных столбцов не допускается validator. Её невалидный candidate остался только в ignored var/, source metadata не менялись;
- итого **30 новых активированных тем**, 1 дополнительный prepared/URL-blocked документ, 15 текущих converter/validator blockers.
Всего по классу **58 новых React-документов + 1 принятый пилот = 59/75**. Осталось 16: 1 URL, 15 implementation dependencies. Новый общий код, renderer/CSS/Math helper не писались.

[Актуальная карта](../tasks/ms-t005-migration-map.json) содержит все 75 тем, текущие причины с line/element/file и историю предыдущих отказов.
[Явная MathML-карта](../tasks/ms-t005-mathml-overrides.json) содержит точные старые HTML/ranges и новые mfrac/msup/msub trees. Временные reviewed copies применялись только для вызова существующего convertLesson; body.html и общая реализация не редактировались. Это scoped authored notation, не альтернативный конвертер. Для заблокированного статистического урока записана подготовленная формула, не объявлено наличие валидного content.json.
[Отдельный список для Владимира и решений пользователя](../tasks/ms-t005-converter-followups.md) перечисляет все 16 тем и все обнаруженные последующие ошибки, а не только первую.

## Проверки exact implementation

| Команда / scope | Результат |
| --- | --- |
| node var/ms-t005-retry/retry.mjs + Python validate_lesson_document | Повторная попытка всех 46 original blockers, вывод сохранён; исторические причины не использовались вместо запуска |
| Явные MathML substitutions + existing convertLesson | Все 8 candidate conversions успешны; 7/8 проходят server schema, 1 останавливается на неизменённых chart heights. Из 7 валидных 6 активированы, 1 URL-blocked |
| `node node_modules/vitest/vitest.mjs run tests/grade-7-preservation.test.tsx tests/svg-title.test.tsx tests/linear-lesson.test.tsx tests/material-routes.test.ts tests/lesson-navigation.test.tsx --reporter=json --outputFile=../var/ms-t005-retry/preservation.json` (frontend cwd) | **74 PASS**, 5 files, 0 failed/pending: все 58 новые renderer documents, exact source text/table cells/SVG/answers/anchors/links, inventory/hash всех 75, routes/navigation, SVG hydration и existing pilot |
| MathML equivalence case в том же suite | Проверяет все 68 original source slices, порядок и буквальный текст numerator/denominator с только representation normalization Unicode super/sub digits; для 67 реально записанных дробей дополнительно сравнивает точный mfrac tree с React SSR. Исходные ограничения и prose проверены общим source comparison |
| `node node_modules/typescript/bin/tsc --noEmit` (frontend cwd) | **PASS**; full wrapper не повторялся, его прежний unrelated generation failure не объявляется исправленным |
| load_sources + load_material_routes + apply_material_redirects | **PASS**: 279 bundles, 62 assignments всего, 59 grade-7 canonical routes / 60 direct redirects; первая algebra тема не получила маршрут, alias пилота сохранён |
| `node var/ms-t005-retry/browser.mjs` | **186/186 offline Playwright PASS**, Edge 157.0.4341.42: 30 новых активных документов + 1 URL-blocked source preview × 320/360/1440 px × light/dark, JS disabled/reduced motion. SVG/MathML bounds, no object corruption, no-JS answers/native anchors и no overflow |
| Визуальная самопроверка | Просмотрены PNG math fragments algebra-18/statistics-13/statistics-16; ручная пользовательская приёмка не заявляется |
| git diff --check, protected files / all other grades / source payload diff | **PASS**; общий converter, validator, lesson.css, runtime.css, renderer, math helper, body.html/page.css/page.js и media не менялись |
| .venv/var/local | 3928/2656 entries: file paths/sizes/mtime_ns совпали до и после; ни окружение, ни БД/config не менялись |

Offline HTML получен source-level renderToString(LessonPage) с существующим runtime CSS и fonts; это не React Router release build или HTTP/runtime приёмка. Export: `node node_modules/vitest/vitest.mjs run --config ../var/ms-t005-retry/vitest.config.mjs --reporter=dot` из frontend. Raw scripts/logs/candidates/PNGs только в ignored var/ms-t005-retry; секреты/PII не выводились.
Установленный Content snapshot не обновлялся. Активация означает lesson.json/route registration в исходниках; новые URL не объявлены опубликованными. Server lifecycle/build/publication/release checks не запускались.

## Границы результата

Первая тема /materials/7-algebra-1 сохраняет legacy metadata и не получила assignment. После будущего решения URL можно использовать уже подготовленный валидный документ.
Все 15 прочих блокировок свежие; список включает SVG font-style/fill-opacity, inline code/images, SVG gradient defs, meaningful root figures, root navigation, nested h2, terminal self-check variants и data-encoded dimensions. Данные не вырезались ради прохождения converter.
Исходные исключения prerequisites/последующих учебных блоков остаются по принятому стандарту; preserved source payloads не удалялись. Новые React documents не записывают mastery и не заменяют legacy self-checks будущим assessed API.
Независимое review **PENDING**, human visual/pedagogical acceptance **PENDING**, MS-T005 целиком **INCOMPLETE**, merge **NOT PERFORMED**. Следующая задача не начинается.
