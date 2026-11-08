# MS-T005 — активация семи тем геометрии

08.11.2026. Ветка ms-t005-grade-7, Draft PR #62, Issue #61.
Исходный HEAD `3449030af0462cf94f701e86a2cffaf0d75539ed`, clean tree. Backup: backup/ms-t005-before-geometry-activation-20261108-3449030.
Проверенный implementation SHA `531a3b1acaf1bfc94ea225fa5b6de147489e2af2`, tree `a2a21ec65f9d9e3b53e8d627a01d4fb8896e74f7`. Последующий commit добавляет только execution/status docs, без изменения runtime inputs.

## Изменения

- `5250931ed31566bd4933e239be8853433e74b70d`: только одна согласованная CSS-строка `.lesson-section .ms-img { max-width: 100%; height: auto; }` в runtime.css.
- Активация семи исходников через existing react-v1 и Content route registry, без изменения converter/validator/renderer/lesson.css/math helper:
  /materials/7-geometry-1, /materials/7-geometry-3, /materials/7-geometry-4,
  /materials/7-geometry-5, /materials/7-geometry-10, /materials/7-geometry-11,
  /materials/7-geometry-12.
- Новые content.json получены повторным convertLesson и точно совпали с read-only candidates предыдущего этапа. Менялись только семь новых content.json и их renderer metadata; исходные body.html/page.css/page.js не трогались.
- Динамический source preservation test дополнен точным сравнением img/code markup, помимо текста/формул/SVG/таблиц/ответов/якорей/ссылок.
- Все прежние 59 lesson.json/content.json проверены против исходного SHA, bytes совпали. Существующие route assignments сохранены как точный prefix; alias /materials/7-algebra-1 не менялся.

Итого **65 новых React-документов + принятый пилот = 66/75**. Все **12/12 геометрических тем** зарегистрированы через react-v1 в исходниках. Это не пользовательская приёмка и не публикация установленного snapshot.

## Найденный и согласованный CSS blocker

До изменения CSS прошли 48/56 offline browser cases; 8 failures относились только к geometry-11 (4 viewport × 2 theme). PNG загружались, но natural 1586×992 давал overflow: например, scrollWidth=1608 при viewport=320.
Агент сообщил точный необходимый общий файл и запросил разрешение. Пользователь явно ответил: «Разрешить runtime.css и завершить все 7 тем» на предложение только max-width:100% / height:auto.
Выполнена только эта узкая rule; остальные CSS/renderer не менялись. После изменения **56/56 cases PASS**; PNG сохраняют natural dimensions, на экране масштабируются пропорционально без viewport overflow. Исходный failing report сохранён отдельно, не объявлялся PASS.

## Медиа

| URL / файл | Bytes | Natural размер | SHA256 |
| --- | --- | --- | --- |
| `/media/uploads/2026/07/image-13.png` / `site_content/media/uploads/2026/07/image-13.png` | 806543 | 1586×992 | `bf9a36c7e724b96795765d476ef17ab98b489da679835cb15decd94cf4216b9a` |
| `/media/uploads/2026/07/image-14.png` / `site_content/media/uploads/2026/07/image-14.png` | 845656 | 1586×992 | `ca8352dea63c1cc1f36ff74977592a6f43d7000c8388657dfce08a3d2e48773b` |

Оба файла неизменны и присутствуют в site_content/media.json с совпадающими SHA256. Фактический assets_for для активированного React bundle находит их по исходным /media/ URL, повторно проверяя seed manifest и bytes. Source alt:
- image-14.png: «Как связаны стороны и углы треугольника»;
- image-13.png: «Три возможные ситуации для неравенства треугольника».
React SSR сохраняет исходные src/alt/классы, browser decode подтверждает natural 1586×992 и пропорции после уменьшения.

Проверка существующего http://127.0.0.1:8131 вернула URLError: installed origin недоступен. Его readiness не заявляется.
Для механизма доставки использован реальный create_app public media branch через ASGI TestClient, с assets_for bytes и fixture-pinned release / UnitOfWork injection **без БД**. Для обоих PNG: GET 200 с точными bytes, image/png, sha-based ETag, nosniff; HEAD 200 без body; conditional GET 304. Отсутствующий media URL — 404. Это component compatibility proof, не валидация реального publication gate или установленного release.
В browser offline origin изображения отдавались через interception из тех же проверенных seed bytes; source URL не менялись. Никакой новый server не запускался.

## Проверки

| Проверка / команда | Результат |
| --- | --- |
| node var/ms-t005-geometry/reconvert.mjs + validate_lesson_document | **7/7 PASS**, документы идентичны прошлым candidates |
| Temporary preactivation SSR/source suite | **8 PASS** (7 source comparisons + export): весь текст, таблицы, self-check answers, full SVG включая font-style/fill-opacity, code markup, img src/alt, retained IDs и ссылки |
| `node node_modules/vitest/vitest.mjs run tests/grade-7-preservation.test.tsx tests/svg-title.test.tsx tests/linear-lesson.test.tsx tests/material-routes.test.ts tests/lesson-navigation.test.tsx --reporter=json --outputFile=../var/ms-t005-geometry/final-vitest.json` (frontend cwd) | **81 PASS**, 5 files, 0 failed/pending; все 65 новых documents плюс существующий пилот/route/navigation/SVG hydration checks |
| node node_modules/typescript/bin/tsc --noEmit | **PASS**, прямой noEmit; прежний unrelated wrapper generation failure не переоценивался |
| python -B -m unittest backend.tests.v04.test_build.SourceTests.test_complete_source_set_and_authored_assets -v | **1 PASS**, штатная read-only проверка 279 bundles/263 topics и всех reviewed media с negative duplicate/traversal/hash cases |
| load_sources / load_material_routes / apply_material_redirects | **PASS**: 279 bundles, 69 assignments всего, 66 grade-7 canonicals, 67 direct redirects; geometry 12/12 |
| ASGI media-handler compatibility | 2 × GET200/HEAD200/conditional304 с byte/hash/header checks, missing404; fixture authority, no DB |
| node var/ms-t005-geometry/browser.mjs | После CSS fix **56/56 PASS**, Edge 157.0.4341.42: 7 тем × 320/360/768/1440 px × light/dark, JS disabled/reduced motion; actual source CSS/fonts, decoded PNG, preserved aspect ratio, computed italic/opacity, SVG bounds, no-JS answers/native contents anchors и no overflow |
| git diff --check / scope/hash checks | **PASS**: прежние 59 документов, authored source/media bytes, other grades и protected shared files неизменны; единственное согласованное shared изменение — image rule runtime.css |
| .venv / var/local | 3928/2656 file entries: paths/sizes/mtime_ns совпали до/после; DB/environment/config не менялись |

Temporary preactivation export/test command: `node node_modules/vitest/vitest.mjs run --config ../var/ms-t005-geometry/vitest.config.mjs --reporter=json --outputFile=../var/ms-t005-geometry/preactivation-fixed.json` из frontend. Browser input — renderToString(LessonPage) с реальными CSS/fonts, а не React Router release build. После metadata activation CSS/content.json не менялись, и финальный suite проверил их вместе с authoritative source registry.
Raw candidates/reports/PNG находятся в ignored var/ms-t005-geometry; browser-before-responsive.json содержит первоначальные 8 ошибок. PNG mobile preview просмотрен агентом; ручная пользовательская приёмка не заявляется. Секреты/PII не выводились.

## Ограничения и оставшиеся задачи

[Карта всех 75 тем](../tasks/ms-t005-migration-map.json) обновлена, [оставшиеся 9 тем](../tasks/ms-t005-remaining.md) перечислены отдельно. Это 8 статистических тем и первая тема алгебры до URL-решения; эти девять в данном этапе повторно не конвертировались.
Source activation не обновляет установленный immutable Content snapshot. Полная HTTP route/reload/Back/no-JS publication проверка не выполнялась: origin недоступен и публикация/build запрещены. Media-handler fixture не выдаётся за production/runtime readiness.
Independent review **PENDING**, human visual/pedagogical acceptance **PENDING**, MS-T005 целиком **INCOMPLETE**, merge **NOT PERFORMED**. Release build, публикация и server lifecycle не запускались. Следующая задача не начинается.
