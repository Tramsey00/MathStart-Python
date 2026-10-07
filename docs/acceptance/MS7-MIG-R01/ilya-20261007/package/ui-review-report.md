# R01 — UI/content review [участник UI-review]

Source: `8c11edadc8debc81432d1db1145feac504f09061` (PR27). Сервер: http://127.0.0.1:8002/.
Дата evidence: 2026-10-07 UTC; точные timestamps в manifests. Это baseline/review,
не I01 и не финальный review/approval PR46. Human gates остаются людям.

## Результат

Снято 18 primary viewport screenshots (6 маршрутов × 3 ширины), 18 supplementary
full-page screenshots и 65 отдельных interaction/content screenshots.
Один ранний diagnostic screenshot с неприменённым viewport сохранён и исключён из baseline.
Полный список файлов: [screenshot-index.md](./screenshot-index.md); hashes/metadata: [all-screenshots.json](./all-screenshots.json).

63 групп функциональных проверок PASS, 0 FAIL; дополнительно одна наблюдательная
проверка перехода на anonymous /account/ без submit/auth review. Это группы browser
наблюдений, не новый E2E test suite и не утверждение, что UI не имеет дефектов.
Найдены F01–F03 P2 и F04 P3. Исходники не исправлялись.

## Окружение и metadata

- Codex in-app browser, session/tab 4. Воспроизведение desktop browser с изменением viewport,
  без touch/device emulation.
- **Microsoft Edge WebView2 runtime 154.0.4258.53; version obtained from User-Agent,
  separate Codex in-app browser version unavailable/unconfirmed.** User-Agent/version
  сообщил пользователь; независимое получение UA из DOM API недоступно.
- Read-only Windows executable metadata ранее показали running WebView2 .53;
  EdgeUpdate registry показывает installed runtime .62. Связь процесса с IAB не доказана.
  Эти наблюдения не заменяют сведения о browser session: [browser-evidence.json](./browser-evidence.json).
- CSS viewports: **360×800**, **768×1024**, **1440×1000**, DPR=1. innerWidth/innerHeight/DPR
  проверены через read-only DOM до/после primary capture. JPEG raster отдельно:
  345×767, 753×1004, 1425×990. API возвращает resampled JPEG; это не 1:1 pixel export.
- Full-page captures служат обзором контента и могут содержать trailing blank raster area;
  initial-fold comparison опирается на viewport captures. Производные review-crops/atlas
  служат навигацией/QA; исходные screenshots сохранены отдельно.
- Initial state: anonymous, URL без query/hash, default widget values, page top,
  содержание урока открыто, authored solutions закрыты; на home/catalogue native details закрыты.
  Отдельные expanded/reset/pointer states имеют собственные имена и metadata.

## Source → published и безопасность

Ранее выполненные fresh-install smoke и parity повторно не запускались: содержательного
нового drift не обнаружено. [source-published-parity.json](./source-published-parity.json): 279/279 pages exact,
263/263 publication digests; [disposable-http-check.json](./disposable-http-check.json): 6 required routes HTTP200,
HTTP hashes равны rendered views, 15 static CSS/JS совпадают после LF normalization.

Disposable: `ms6_v01_smoke_ilya_r01_20261007_8c11edad`, role `ms7_r01_ilya`,
`127.0.0.1:55447`, отдельные runtime/volume. Browser использовал только port8002.
Server работает с PGOPTIONS default_transaction_read_only=on; write commands не запускались.
Working `mathstart:5432` в этом UI этапе не подключалась и не изменялась. Ранее проверенный
unchanged fingerprint после smoke сохранён в [working-db-after-smoke.json](./working-db-after-smoke.json).
Нового fingerprint probe в этом этапе нет.

Archive source 1026 файлов повторно сравнен SHA256: 0 изменений,
[final-source-preservation.json](./final-source-preservation.json). `git status -sb`: `## main...origin/main`,
`git rev-parse HEAD`: exact source SHA. Все новые artifacts только в ignored var/
[участник UI-review]; общие R01 docs, working DB, исходники, commits и remote не изменялись.
React/FastAPI/scaffold не создавались.

## Browser checks

| Область | Фактически проверено | Итог |
| --- | --- | --- |
| Header/navigation | 6 routes × 3 viewports: Tab MathStart → Все темы → Личный кабинет; Shift+Tab назад; focus-visible | PASS18, outline3px |
| Home | CTA Enter → #classes, Enter/Space disclosure классов, переход Все темы | PASS3 |
| Catalogue | GET q=степенн + grade10, поиск без результатов, reset263, native details Space | PASS3 |
| Lessons | На четырёх уроках × 3: contents Enter/Space, первый authored solution Enter, focus, root overflow | PASS12 |
| Linear PR27 | k/b ArrowRight; Home/End; k=0; formula, direction, Oy/Ox; reset Space; pointer readout/guides; leave без reset | PASS; все3 ширины |
| Power PR27 | Все12 presets Enter, aria-pressed, числовая таблица при x=2; p/x sliders endpoints; negative/zero domain; reference Space; reset Enter; pointer/leave | PASS; все3 ширины |
| Circle | Все8 presets Enter: координаты равны cos/sin; slider шаги/endpoints; ±2π сохраняют точку; approximate/exact readout; reset Space | PASS; все3 ширины |
| Circle mobile | grid1column на360, graph перед controls; на768/1440 две колонки | PASS |
| SVG viewer | Обычный урок: Enter enlarge, Space restore, aria-expanded; root overflow | PASS3, inline viewer, не modal |
| Visual/content | Hero/header/footer, type/spacing, SVGs, fractions/radicals, visible math and representative solution, graph changes PR27 | Findings ниже |
| Root horizontal overflow | Все18 initial states и проверенные expanded/control states | Не найден |
| Console | Доступный CUA log error/warn | 0 entries; не полный HAR/network audit |

Pointer checks включали движение указателя при locator click на graph и уход к
неизменяющему состояние заголовку/formula; readout/guides/return-to-slider state проверены.
Отдельное hover-only движение без click и физические touch gestures API не предоставил;
они не объявляются проверенными. Это review одного browser surface, не cross-browser
или полный WCAG audit. Mathematical checks репрезентативны и не заменяют полный экспертный
аудит всех задач сайта. Малые подписи SVG отдельно отмечены в F04.

## Findings — без исправлений

### F01 — P2: Заголовки содержания уроков переполняют две узкие колонки

Маршруты:

- http://127.0.0.1:8002/linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii/
- http://127.0.0.1:8002/10-klass-stepennye-funkcii-i-grafiki-2-0/
- http://127.0.0.1:8002/10-klass-chislovaya-okruzhnost-2-0/
- http://127.0.0.1:8002/polozhitelnye-i-otriczatelnye-chisla-opredelenie-koordinatnoj-pryamoj/

Viewport: 360×800; слой: CSS/layout.

Шаги:

1. Открыть любой из четырёх обязательных уроков на 360×800.
2. Прокрутить к открытому Содержанию урока.
3. Сравнить длинные названия с границами карточек.

Длинные слова выходят за карточки, перекрывают стрелки/соседние карточки и обрезаются внешним overflow:hidden. В обычном уроке ширина текстового span около 28px; scrollWidth длинных слов 88–127px. На 768/1440 не воспроизведено.

Source files: `static/mathstart/css/lesson-contents.css`.

Evidence: [screenshots/linear-function-360-toc-clipping.jpg](./screenshots/linear-function-360-toc-clipping.jpg), [screenshots/power-functions-360-toc-clipping.jpg](./screenshots/power-functions-360-toc-clipping.jpg), [screenshots/number-circle-360-toc-clipping.jpg](./screenshots/number-circle-360-toc-clipping.jpg), [screenshots/ordinary-number-line-360-toc-clipping.jpg](./screenshots/ordinary-number-line-360-toc-clipping.jpg).

### F02 — P2: 12 presets степенной функции сжаты в один ряд и перекрываются

Маршруты:

- http://127.0.0.1:8002/10-klass-stepennye-funkcii-i-grafiki-2-0/

Viewport: 360×800; слой: CSS/layout/pointer.

Шаги:

1. Открыть степенные функции на 360×800.
2. Перейти к интерактиву.
3. Посмотреть строку выбора показателя p.

Grid сохраняет 12 колонок. Кнопки шириной 12.33px при высоте 62px, формулы перекрывают друг друга. Keyboard/aria-pressed корректны, но визуальный выбор и pointer targets неудобны. На 768/1440 перекрытие не воспроизведено.

Source files: `static/mathstart/css/widgets/power-functions.css`.

Evidence: [screenshots/power-functions-360-reset.jpg](./screenshots/power-functions-360-reset.jpg).

### F03 — P2: Длинные значения таблицы степенной функции выходят за ячейку

Маршруты:

- http://127.0.0.1:8002/10-klass-stepennye-funkcii-i-grafiki-2-0/

Viewport: 360×800; слой: CSS/content legibility.

Шаги:

1. Открыть степенные функции на 360×800 с default p=2.
2. Прокрутить к таблице под графиком.
3. Прочитать значение при x=0,25.

0,0625 имеет ширину 37.86px в ячейке 31.67px; выходит в соседнюю карточку и визуально частично перекрывается её фоном. Данные в DOM правильные. На 768/1440 дефект не воспроизведён.

Source files: `static/mathstart/css/widgets/power-functions.css`.

Evidence: [screenshots/power-functions-360-table-clipping.jpg](./screenshots/power-functions-360-table-clipping.jpg).

### F04 — P3: Мелкие подписи SVG окружности на мобильной ширине

Маршруты:

- http://127.0.0.1:8002/10-klass-chislovaya-okruzhnost-2-0/

Viewport: 360×800; слой: SVG/readability.

Шаги:

1. Открыть окружность на 360×800.
2. Перейти к лаборатории и схемам 8/12 частей.
3. Прочитать подписи координат/углов внутри SVG.

SVG лаборатории около 203px шириной, статические схемы около 199px. Подписи мелкие; координаты и угол дополнительно показаны обычным текстом. Одноколоночная компоновка и controls работают.

Source files: `curriculum/10-klass/algebra/04-sinus-kosinus-tangens-kotangens/01-10-klass-chislovaya-okruzhnost-2-0/page.css`, `curriculum/10-klass/algebra/04-sinus-kosinus-tangens-kotangens/01-10-klass-chislovaya-okruzhnost-2-0/body.html`.

Evidence: [screenshots/number-circle-360-reset.jpg](./screenshots/number-circle-360-reset.jpg), [screenshots/number-circle-360-svg4-viewport.jpg](./screenshots/number-circle-360-svg4-viewport.jpg).

P2 = содержательная проблема мобильной читаемости/управления; P3 = менее значимое
наблюдение читаемости. Это pre-existing source-baseline findings, не внесённые миграцией.
За пределами перечисленных findings новые блокирующие ошибки header, графиков,
математических вычислений, solution disclosures или desktop/tablet layout не выявлены.

## D02 — рекомендация

**Не рекомендую безоговорочную visual/content приёмку PR27**, пока F01–F03 не получат
явное человеческое решение. Нужны либо согласованные known-defect exceptions для baseline
с отдельными follow-ups в `static/mathstart/css/lesson-contents.css` и
`static/mathstart/css/widgets/power-functions.css`, либо последующая согласованная коррекция
и новый accepted SHA. Зафиксировать текущий source snapshot и screenshots технически можно;
это не означает, что mobile UI не имеет дефектов. F04 отдельно не блокирует.

## D03 — рекомендация в зоне [участник UI-review]

**Canonical Git source + disposable source/published parity можно принять**:
fresh process воспроизводим, exact comparisons проходят, рабочая БД сохранена.
При этом [drift-report.md](./drift-report.md) обязательно должен оставаться отдельным evidence
рабочей БД [участник UI-review]. Он доказывает содержательные различия только конкретных пяти payloads
(HTML/CSS/JS и metadata каталога), а не соответствие всей БД старому commit.

Строка D03 в R01 описывает отдельный runtime manifest [координатор R01] (13 LF/CRLF variants,
zero substantive normalized field differences). Она **не описывает рабочую БД [участник UI-review]**.
Рекомендация D03 применима только при явном разделении этих сред/наблюдений и приложении
наших материалов. Универсальное утверждение «working DB [участник UI-review] имеет только LF/CRLF drift»
принять нельзя. Source baseline не заменяется рабочей БД и она не синхронизируется.

Определения D02/D03 прочитаны read-only из exact candidate
`43b4fa10aec2af589c51857d037e973215557255` для согласования терминов:
[r01-decision-context.json](./r01-decision-context.json). Final review PR46 не выполнялся; CI/прочие решения
этого PR данным отчётом не оцениваются. Общие документы [координатор R01] не редактировались.
Ни D02/D03, ни R01/MIG-G0, ни PR46 не утверждены агентом от имени участников.

## Команды, exit codes и trace

- Предыдущие setup/smoke/parity commands и exit0: [commands.json](./commands.json),
  [fresh-smoke-summary.md](./fresh-smoke-summary.md), [command-07.log](./command-07.log), [command-08.log](./command-08.log).
- Текущая UI automation: documented CUA DOM/locator/screenshot APIs; shell exit code
  к ним не применяется. Результаты: [ui-checks.json](./ui-checks.json), [visual-inventory.json](./visual-inventory.json).
- Python/Pillow artifact tools: bundled Python3.12.14, Pillow12.3.0;
  `make_review_crops.py`, source-preservation/hash audit и `finalize_ui_review.py` exit0.
- `git status -sb` / `git rev-parse HEAD`: exit0, clean exact baseline.
- Canonical `verify_repo.py`/test suites в этом browser-only этапе не запускались;
  их прежние результаты не выдаются за новый UI или cross-browser PASS.
- Browser internal version URL был заблокирован policy: обход не выполнялся.
  Browser metadata ограничение явно зафиксировано и по указанию пользователя review продолжен.
- Диагностические stale selectors/двусмысленный MathStart locator исправлены через
  свежий DOM и scope основной navigation. Ошибочная ожидаемая фраза `не пересекает`
  в linear assertion уточнена до фактического `нет пересечения`; UI дефекта там нет.
  Отдельный ранний SVG screenshot с неполной отрисовкой текста сохранён; повторное
  read-only наблюдение и `number-circle-360-svg6-verified.jpg` подтверждают полный heading.

Никаких screenshots рабочей БД, bootstrap/publish/migrate/cleanup/commit/push
в этом этапе не выполнялось. Сервер disposable оставлен для дальнейшего review;
временный browser viewport override сброшен.
