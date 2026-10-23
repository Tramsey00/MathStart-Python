# Финальная проверка React-пилота учебной страницы — 23 октября 2026

**Результат: кандидат не получает итоговый PASS.** Подтверждены два нарушения контраста текста и один дефект touch-взаимодействия. Дополнительно найден 404 favicon каталога. Существующие тесты не зелёные: часть ожиданий относится к предыдущему интерфейсу. Это аудит отдельного Vite-прототипа, не production-приёмка MathStart.

Проверен `http://127.0.0.1:5173/materials/8-algebra-32`. Основной повторный browser audit: 16:21–16:23 МСК; дополнительные проверки и окончательные снимки — в той же сессии 23.10.2026. Chrome **155.0.8059.85**, Windows, headless Playwright, Node **24.19.0**, npm **11.17.0**. Диапазону Node/npm из package.json версии соответствуют; установленный npm отличается от поля packageManager `11.19.0`, зависимости не переустанавливались.

## Кандидат и границы работы

- Рабочий каталог: `C:/Projects/MathStart-Python`, фактическая ветка **ui/ux**.
- HEAD: **192d0fc315e35644eeb9bb713f58d7d15afb34a0**, кандидат **dirty**, включая незакоммиченные и untracked файлы самого урока. Один HEAD не идентифицирует проверенную реализацию.
- [Git до проверки](lesson-final-2026-10-23/git-status-before.txt), [Git после](lesson-final-2026-10-23/git-status-after.txt), [исходный diff stat](lesson-final-2026-10-23/git-diff-stat-before.txt), [SHA-256 фактических build inputs и тестов](lesson-final-2026-10-23/implementation-sha256.json). Manifest включает все curriculum/lesson.json, которые читает virtual catalogue, канонический урок, prototype, общие lesson-компоненты, fonts и dependency lock. Это fingerprint на момент завершения аудита, не заявление о чистом коммите.
- Прочитаны обе AGENTS.md, verification skill, README/runtime/release/recovery, PRODUCT/архитектурные границы и три актуальные записи lesson-shell/motion/url. Применены установленные impeccable audit, ui-ux-pro-max и web-animation-design. Субагенты не запускались.
- Код реализации, учебные источники и существующие тесты **не редактировались**. Добавлены только этот отчёт и audit evidence/scripts. Ветка не переключалась; reset/clean/stash/commit/push в рабочем репозитории не выполнялись. Созданный аудитом Chrome-профиль перенесён из evidence в игнорируемый `frontend/.cache/lesson-final-initial-zoom-profile`; прежние файлы пользователя не перемещались.
- Сервер уже слушал 5173, PID 23676. Первичная sandbox HTTP-проба получила запрет сокета; пробный Vite-запуск завершился `Port 5173 is already in use`. После разрешённого локального доступа существующий сервер ответил **200**. Его не останавливали и не заменяли. `npm run dev` не использовался.
- Защищённые/production стеки, DB, миграции и live LLM не запускались. Полный `verify_repo.py` / target lifecycle не входил в этот scoped prototype audit и не запускался; прежняя production-readiness не переносится на этот dirty-кандидат.

## Реальные дефекты

### P1 · D1 — мелкий синий текст в тёмной теме не достигает 4.5:1

**Воспроизведение:** открыть новый URL → включить тёмную тему → подождать завершения смены цветов → перейти к интерактивному графику. Проверить «Сбросить коэффициенты», значения `a/b/c`, легенду «График» / «Корни». Внизу урока тот же эффект у «Следующая тема». Воспроизводится на всех четырёх ширинах; основной замер выполнен на 1440 px в установившемся состоянии.

**Факт:** `--lesson-accent` = `oklch(0.6232 0.1879 259.7964)` на поверхности **#20262f**, расчёт через преобразование CSS-цвета в sRGB в самом браузере: **4.1384:1**. Размер затронутых подписей 13–14 px, порог обычного текста WCAG 1.4.3 AA — 4.5:1. Это измеренная доступность, не предложение изменить утверждённую палитру целиком.

**Места:** `frontend/prototypes/home/lesson.css:14` (accent alias), `:191` (reset), `:217` (output), `:230` (легенда), `:307` (следующая тема); исходный dark primary — `frontend/prototypes/home/theme.css:82`. Рекомендация для отдельного согласованного исправления: подобрать локальный lesson text-color с достаточным контрастом, сохранив Professional Theme, характер акцента и размеры кнопок. Команда скила: `$impeccable harden`.

**Evidence:** [тёмный график 1440](lesson-final-2026-10-23/screenshots/1440-dark-lab.png), [тёмный низ 1920](lesson-final-2026-10-23/screenshots/1920-dark-footer.png), [численные замеры: observations → contrast](lesson-final-2026-10-23/browser-audit.json).

### P1 · D2 — вторичный текст светлого подвала ниже AA-контраста

**Воспроизведение:** светлая тема → конец страницы → описание под логотипом «Материалы по школьной математике» и copyright. Проверить в DevTools computed foreground/background.

**Факт:** текст **#626d7c** на **#e2e8f1** даёт **4.26395:1** вместо 4.5:1. Описание — 14 px desktop / 13 px mobile, copyright — 12 px. Основные ссылки подвала этим замечанием не затронуты.

**Места:** `frontend/prototypes/home/lesson.css:11` и `:20`; `frontend/src/shared/lesson/lesson-shell.css:53`, `:63`. Категория: accessibility/theming, WCAG 1.4.3 AA. Для отдельного исправления достаточно локально уточнить цвет вторичного текста подвала без изменения его структуры или фона. Команда: `$impeccable harden`.

**Evidence:** [светлый подвал 1440](lesson-final-2026-10-23/screenshots/1440-light-footer.png), [светлый подвал 360](lesson-final-2026-10-23/screenshots/360-light-footer.png), [contrast JSON](lesson-final-2026-10-23/browser-audit.json).

### P2 · D3 — вертикальная touch-прокрутка графика меняет выбранную точку

**Воспроизведение:** Chrome touch emulation, viewport 360×800, `hasTouch/isMobile` → открыть урок с начальным `x = 0` → довести график до середины экрана → начать вертикальный свайп вверх внутри правой части графика, без намерения выбрать точку. В обеих темах страница прокручивается, а выбранная абсцисса меняется.

**Факт:** в light прогоне `scrollY: 1349 → 1457`, в dark `1349 → 1430`; **x: 0 → 5.4**, `y = 10.56`, появляется «Точка вне окна графика». Зарегистрированы `pointerdown(touch)` и затем **pointercancel**, без подтверждающего pointerup. Обновление уже произошло на pointerdown и не отменяется. Пользователь теряет исследуемую точку при обычном чтении страницы.

**Место:** `frontend/src/shared/lesson/quadratic-graph.tsx:88`–92; `frontend/prototypes/home/lesson.css:195` разрешает `touch-action: pan-y`. Категория: touch/interaction. Рекомендация: подтверждать выбор tap/click после отделения его от scroll/cancel, сохранив вертикальную прокрутку и клавиатурный ползунок. Не добавлять запрет page scroll поверх графика. Команда: `$impeccable harden`.

**Evidence:** [до свайпа](lesson-final-2026-10-23/screenshots/touch-scroll-before-light.png), [после свайпа](lesson-final-2026-10-23/screenshots/touch-scroll-after-light.png), [dark после](lesson-final-2026-10-23/screenshots/touch-scroll-after-dark.png), [supplement.json — before/after и pointercancel](lesson-final-2026-10-23/supplement.json), [воспроизводящий script](lesson-final-2026-10-23/run-supplement.mjs). Это синтезированный touch в Chrome, не физический телефон.

### P3 · D4 — 404 favicon при проверяемом переходе через каталог

**Воспроизведение:** новый browser context → открыть `/materials.html?grade=8-klass&subject=algebra` → Console/Network. Браузер запрашивает **/favicon.ico**, сервер отвечает **404**, Console показывает `Failed to load resource`.

**Место:** `frontend/prototypes/home/materials.html:2`: явный icon link отсутствует. Сам HTML урока содержит `href="data:,"` и такую ошибку на прямом открытии не вызывает. Это низкоприоритетный дефект каталога в проверяемом navigation flow, не ошибка вычислений или pageerror урока. Воспроизводится в отдельном свежем контексте. Возможное отдельное исправление — явно задать icon каталога. Команда: `$impeccable polish`.

**Evidence:** [supplement resources/console с точным URL](lesson-final-2026-10-23/supplement.json). Наличие этого console error не скрыто фильтром; проверка «no console errors» осталась FAIL. JavaScript pageerror в основном audit не зафиксирован.

## Что подтверждено текущим рендером

| Область | Выполненная проверка и результат |
| --- | --- |
| 360×800, 768×1000, 1440×1000, 1920×1000 | Все восемь light/dark комбинаций отрисованы и сфотографированы. `documentElement.scrollWidth === innerWidth` во всех восьми. Прочитаны верх, формула, таблица, SVG, график, короткие/длинные ответы, подвал и содержание. Локальный вынос lab на 6 px и отступы breadcrumbs не образуют page overflow. |
| Визуальное соответствие | Белая светлая шапка, тёмная шапка, общий lesson shell, содержание вне шапки, нейтральная reading surface и Professional/QraftHive сохранены. На 1440/1920 график и вычисленные данные видны рядом. На 768 и телефоне естественный вертикальный поток. Причин для редизайна структуры не найдено. |
| Формулы, таблица, SVG | Текущие формулы и длинные расчёты не обрезаются на 360. Authored SVG сохранены с белым внутренним полем и исходными цветами в обеих темах; это сохранение источника, не новый зелёный UI-акцент. На узком размере схемы можно увеличить; синтезированный горизонтальный touch-pan работает. Подписи исходной схемы мелкие в fit-mode, предусмотрено увеличение. |
| Настоящий browser zoom 200% | Chrome profile `partition.default_zoom_level`, без CSS zoom, transform или pageScaleFactor. В обоих theme: outer/inner = 720/351, 768/375, 1440/711, 1920/951, DPR=2, visualViewport.scale=1; разница с половиной outer обусловлена scrollbar. Page overflow нет. Проверены длинное решение, клавиатура и управление, в основном zoom-прогоне также TOC/anchor и reset. |
| Содержание | Enter открывает dialog; initial focus на крестике, Tab и Shift+Tab замыкаются. Escape, крестик и доступный desktop backdrop закрывают; фокус возвращается trigger. Wheel фона не прокручивает body, overflow восстанавливается. На 360 panel занимает всю ширину: внешнего backdrop для нажатия нет, доступна кнопка закрытия. |
| Переходы содержания | Пройдены все 8 ссылок. URL hash, focus секции и aria-current соответствуют цели; heading top после перехода в основном 1440-прогоне находится между 76 и 160 px. Активный пункт отличается фоном, номера с точками. |
| Самопроверка | Проверены все 10 задач: нажатие текста не раскрывает ответ; отдельная кнопка работает с Enter и Space; controls указывает на существующий уникальный id, expanded/aria-hidden/inert меняются согласованно. После закрытия высота 0, visibility hidden, Tab не входит в ответ. Длинные решения раскрываются до естественной высоты. Белый фон ответов в light сохранён. |
| График / математика | Клавиатура Arrow/Home/End для a и выбранного x; диапазоны a ±4, b/c ±10, x ±10. Проверены [-4,-10,-10], [4,10,10], линейный [0,2,-4], постоянные [0,0,3] и [0,0,0], D=0 и отсутствие корней. Таблица сопоставлена с непосредственным ax²+bx+c. |
| Выбранная точка и reset | Click меняет x, последующий hover сохраняет его. Reset даёт промежуточные значения и возвращает **a=1,b=-4,c=3,x=0**. Ручной ввод коэффициента и x останавливает незавершённый reset; спустя 450 ms значения не перезаписываются. При reduced motion reset мгновенный. Исключение touch-scroll — D3. |
| Быстрые действия / reduced motion | 8 коротких open/Escape циклов и 12 Enter/Space раскрытий не оставляют dialog, scroll lock или ненулевой скрытый ответ. Reduced motion проверен на всех четырёх ширинах: переходы dialog/ответа отсутствуют, конечные состояния корректны. |
| Имена, фокус, копирование | У проверенных видимых button/input/link есть доступные имена. Keyboard :focus-visible даёт outline 2 px; есть свежий снимок. Кнопки `user-select:none`, текст вопроса `text`; copy/cut в lab отменены в runtime. SVG имеют доступные имена. Это не полноценный screen-reader certification. |
| URL | Прямое открытие/reload 200. `/quadratic.html`, старый slug с/без `/` и новый URL с `/` проходят 302 на **/materials/8-algebra-32**, сохраняя `?audit=1&source=test#lesson-section-8`. Поиск и список нужного раздела каталога открывают этот же путь. В lesson-routes.mjs номер записан явно, runtime пересчёта нет. |
| Сохранность | В actual browser DOM тексты всех 8 оставленных секций совпали с каноническим HTML после удаления только UI-controls/React-lab. Все 10 ответов, MathML, клетки исходной таблицы и outerHTML обоих authored SVG совпали. Разрешённое исключение recap section 9 сохранено. |

Репрезентативные снимки: [360 light верх](lesson-final-2026-10-23/screenshots/360-light-top.png), [360 формула](lesson-final-2026-10-23/screenshots/360-light-formula.png), [360 dark SVG](lesson-final-2026-10-23/screenshots/360-dark-diagram.png), [768 light график](lesson-final-2026-10-23/screenshots/768-light-lab.png), [768 dark верх](lesson-final-2026-10-23/screenshots/768-dark-top.png), [1440 dark содержание](lesson-final-2026-10-23/screenshots/1440-dark-contents.png), [1920 light длинное решение](lesson-final-2026-10-23/screenshots/1920-light-answer-8.png), [200% узкое окно / длинное решение](lesson-final-2026-10-23/screenshots/zoom200-outer720-dark-long-solution.png), [клавиатурный фокус](lesson-final-2026-10-23/screenshots/1440-light-focus-answer.png), [ссылка из каталога](lesson-final-2026-10-23/screenshots/catalogue-section-route.png).

## Проверка анимаций

| Before | After |
| --- | --- |
| Текущий вход TOC: transform 280 ms, backdrop background-color 280 ms. Выход: discrete display/overlay удерживают panel до конца; после закрытия display:none. Быстрый разворот сокращает duration перехода по правилам CSS. | Функционального зависания не найдено. Сохранить поддержку выхода и корректное восстановление фокуса/scroll lock. |
| Panel использует cubic-bezier(.2,.8,.2,1) на входе и (.4,0,.8,.2) на выходе; backdrop использует ease-out. Длительности обычного входа/выхода 280/220 ms. | Необязательно: при следующей настройке motion сравнить одинаковый easing пары. Разные кривые подтверждены, но самостоятельного пользовательского дефекта от них не доказано. |
| Ответ: grid-template-rows и margin-top 240 ms, opacity 160 ms; hidden/inert выставляются согласованно. Анимация естественной высоты вызывает layout. | Короткие и длинные ответы, включая повторные действия, работают. Не заменять реализацию только из-за общей рекомендации «transform only»; сначала нужен performance trace на целевом устройстве. |
| Button hover/active: transitions 160 ms, scale .98; стрелки переходов смещаются на 3 px только при hover-capable media. Reset коэффициентов — rAF 360 ms с cubic ease-out и округлением до 0.1. | Текущее поведение не оставляет застрявших состояний; ручное управление прерывает reset. 360 ms не объявлено дефектом только из-за общей рекомендации скила <300 ms. |
| Reduced motion выключает CSS animations/transitions, включая hover/active transforms, и делает reset мгновенным. Touch tap/слайдеры/ответы работоспособны. | Сохранить. Touch-scroll отмену выбора отдельно исправлять по D3. |

Численные CSSTransition observations находятся в [browser-audit.json](lesson-final-2026-10-23/browser-audit.json), test `normal motion`. Frame-rate на физическом устройстве не измерялся; отсутствие заметного сбоя в локальном рендере не является performance-сертификатом.

## Команды и фактические результаты

Все frontend-команды выполнялись из `C:/Projects/MathStart-Python/frontend`, audit scripts — из корня. Логи сохранены без приватных env/cookies. Snapshot скриншотов — **106 PNG**, [окончательный capture pass](lesson-final-2026-10-23/capture-review.json).

| Команда | Exit / результат | Evidence |
| --- | --- | --- |
| `node node_modules/typescript/bin/tsc -p prototypes/home/tsconfig.json` | **0**, без диагностик | [typecheck.log](lesson-final-2026-10-23/typecheck.log) — пустой stdout/stderr при успешном exit |
| `npm run typecheck` | **0**; contract generation, route typegen и TypeScript, 4 measured assertions | [frontend-typecheck.log](lesson-final-2026-10-23/frontend-typecheck.log) |
| `node node_modules/vite/bin/vite.js build --config prototypes/home/vite.config.mjs` | **0**, 47 modules, 2.92 s | [build.log](lesson-final-2026-10-23/build.log) |
| `npm test` | **1**; **194 passed / 2 failed**, 196 tests, 22/23 files passed, 0 skipped | [npm-test.log](lesson-final-2026-10-23/npm-test.log), [полный JSON](lesson-final-2026-10-23/npm-test.json) |
| `node node_modules/@playwright/test/cli.js test --config prototypes/home/playwright.config.ts --timeout 12000` | **1**; **60 passed / 12 failed**, 72 cases, 0 skipped, 4.1 min | [playwright-existing.log](lesson-final-2026-10-23/playwright-existing.log), [JSON](lesson-final-2026-10-23/playwright-existing.json) |
| Тот же CLI, `quadratic.spec.ts --project chrome-360 --grep 'real Chrome page zoom'`, исходный timeout 45 s | **1**, 1 timeout 45.1 s | [playwright-zoom-default.log](lesson-final-2026-10-23/playwright-zoom-default.log), [JSON](lesson-final-2026-10-23/playwright-zoom-default.json) |
| `impeccable.cmd detect --json frontend/prototypes/home/quadratic.tsx frontend/prototypes/home/lesson.css frontend/src/shared/lesson` | **0**, **[]**, source detector | [detector.json](lesson-final-2026-10-23/detector.json) |
| `node docs/audits/lesson-final-2026-10-23/run-audit.mjs` | **1**; **25 PASS / 3 FAIL** из 28 сценариев | [browser-audit.log](lesson-final-2026-10-23/browser-audit.log), [JSON](lesson-final-2026-10-23/browser-audit.json) |
| `node docs/audits/lesson-final-2026-10-23/run-supplement.mjs` | **1**; **9 PASS / 2 FAIL**, плюс 2 observations. Оба FAIL воспроизводят D3 в light/dark | [supplement.log](lesson-final-2026-10-23/supplement.log), [JSON](lesson-final-2026-10-23/supplement.json) |
| `node docs/audits/lesson-final-2026-10-23/run-catalogue.mjs` | **0**, 2/2 перехода: поиск и authored section list | [catalogue-recheck.log](lesson-final-2026-10-23/catalogue-recheck.log), [JSON](lesson-final-2026-10-23/catalogue-recheck.json) |
| `node docs/audits/lesson-final-2026-10-23/capture-review.mjs` | **0**, 80 окончательных viewport screenshots, без изменения страницы | [capture-review.log](lesson-final-2026-10-23/capture-review.log) |

Build output: quadratic JS **110.55 kB / gzip 25.38 kB**, общий site-shell JS **195.35 / 61.68 kB**; quadratic CSS **28.87 / 5.80 kB**. Локальные fonts — Outfit 110.88 kB, Merriweather Italic 595.65 kB. Это описание фактического артефакта, не измерение загрузки на слабой сети. Vite production build успешно создан, но built preview отдельно не обслуживался и не проверялся.

### Ошибки тестов и инструментария отдельно от дефектов страницы

1. `frontend/tests/quadratic-source.test.tsx:30`–32 удаляет старый `.lesson-reveal-action`, но не текущую `.lesson-answer-toggle`. Поэтому сравнение академического текста включает десять новых подписей «Ответ и решение». Это **устаревшая нормализация теста**, не потеря/подмена учебного текста. Независимое сравнение actual DOM без UI-кнопок прошло.
2. `frontend/tests/quadratic-source.test.tsx:39` требует десять `details`, которых по согласованному поведению больше нет. Assertion падает раньше следующих сравнений SVG/ответов; эти проверки в данном тесте **не считаются пройденными**. Их содержание отдельно проверено браузерным audit.
3. Все 12 падений большого Playwright-прогона находятся в трёх случаях `quadratic.spec.ts` на четырёх ширинах. В первом — поиск `.self-check details` (`:38`); в refined-case — `summary` (`:155`), далее в том же тесте устаревшие требования `.lesson-topic-title` (`:171`). Zoom-case содержит те же старые `summary/details` (`:342`). Прогон с 12 s timeout намеренно ограничивал ожидание отсутствующих селекторов; его нельзя называть полным запуском с исходными timeout. Отдельный повтор zoom-case с 45 s также timeout: текущий тест не даёт завершённого результата; точный зависший locator не был выведен, поэтому причина этого timeout не утверждается только по предположению. Новые zoom-проверки прошли независимо.
4. Первичный прямой `vitest run` не выполнил тесты: EPERM rename временного Vite-кеша, 23 failed suites / 0 tests. [Лог](lesson-final-2026-10-23/vitest.log). После разрешённого запуска вне этого ограничения прямой Vitest дал 182 passed / 2 failed и дополнительную suite-error «Run regression tests through npm test». [Повтор](lesson-final-2026-10-23/vitest-retry.log). Штатный `npm test` устранил ошибку контекста запуска; итоговые 194/2 приведены выше. Ни один из первых запусков не засчитан как PASS.
5. Первый вспомогательный browser pass имел слишком общий/неверный selector каталога и преждевременное чтение цветов при смене темы. [Начальный JSON](lesson-final-2026-10-23/browser-audit-initial.json) / [лог](lesson-final-2026-10-23/browser-audit-initial.log) сохранены, его transient dark contrast не используется. Во втором pass после ожидания установившегося theme остались реальные D1/D2; selector `.section-card` всё ещё совпадал с двумя разными разделами. Этот третий FAIL основного audit — **ошибка audit harness**, а не каталога. Точный selector отдельного recheck подтвердил оба перехода. Финальный run-audit script уточнён для будущего воспроизведения; итог исходного прогона 25/3 не переписан задним числом.
6. Вторая реальная ошибка основного browser pass — console favicon 404 (D4); первая — contrast (D1/D2). Pageerror в этом прогоне отсутствует. Снимки формул/вопросов дополнительно пересняты с отступом под sticky UI, чтобы нужный элемент не скрывала шапка. Окончательные файлы находятся в screenshots, capture metadata — отдельно.

Существующие unit/Playwright-тесты в этом аудите не актуализировались и не ослаблялись ради PASS. Их обновление должно сохранять проверки академического содержания, управления, фокуса, навигации и zoom, но проверять согласованную кнопку и отсутствие видимых названий соседних тем.

## Оценка impeccable и ограничения

**Implementation integrity verdict:** система визуально связная и соответствует учебной reading surface. Detector не выдал замечаний, но он не обнаружил реальные contrast/touch проблемы; его `[]` не заменяет браузер. Context launcher прочитал PRODUCT, не нашёл DESIGN.md/surface brief и сообщил legacy product schema. Это ограничение разрешения design context/документации, не разрешение на редизайн и не автоматически исправленная drift-запись.

| Dimension | Балл 0–4 | Основание |
| --- | ---: | --- |
| Accessibility | 2 | Keyboard/ARIA/reveal работают, есть подтверждённые AA-contrast failures |
| Performance | 3 | Сборка и локальные интеракции работоспособны; оценка предварительная, без device/network profiling |
| Theming | 3 | Согласованные light/dark поверхности, локальные дефекты контраста |
| Responsive | 3 | Восемь рендеров и real zoom без page overflow; D3 touch-scroll |
| Implementation integrity | 4 | Канонический материал, явно закреплённый URL и общие компоненты, detector [] |
| **Итого** | **15/20** | Эвристическая оценка качества; не положительный gate и не production acceptance |

Не проверялись Safari/WebKit, Firefox/Edge, физические телефоны, assistive technology с живым screen reader, низкопроизводительное устройство/CPU throttling, пиксельный anti-alias контраст каждого authored SVG, built preview и основной FastAPI/SSG runtime. HTML contrast scanner использует computed colors и непрозрачные ancestor backgrounds; существенные D1/D2 дополнительно сопоставлены с фактическими tokens/surfaces. Восемь theme/viewport renders не означают полную WCAG-сертификацию.

## Необязательные предложения и следующий отдельный этап

- При следующем motion-polish можно сравнить одинаковые easing у drawer/backdrop; сейчас это рекомендация, не дополнительный дефект.
- Обновить устаревшие описания самопроверки в prototype README и первоначальную часть lesson-shell note: они всё ещё описывают предыдущую структуру, тогда как последние уточнения и реализация соответствуют пользовательским решениям. Это документация, не основание возвращать старый UI.
- Выбранную пользователем кнопку высотой 33 px не предлагается увеличивать автоматически: generic 44 px из скила не отменяет согласованное решение и не тождественен нормативному AA минимуму 24 px. Белые authored SVG в dark также не предлагается перекрашивать.

Предлагаемый порядок после отдельного согласования: D1/D2/D3 через `$impeccable harden`, затем точная актуализация тестов, затем D4 и `$impeccable polish`, после — повтор затронутых сценариев `$impeccable audit`. Эти действия **не выполнены**. На этапе отчёта работа остановлена.
