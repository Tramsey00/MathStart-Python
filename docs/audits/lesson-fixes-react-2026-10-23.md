# Исправления финального аудита React-пилота MathStart

23 октября 2026. Страница: `http://127.0.0.1:5173/materials/8-algebra-32`.

**D1–D4 закрыты. Обязательные проверки в области прототипа завершены без оставшихся failed/skipped/timed-out сценариев.** Это проверка отдельного React/TypeScript/Vite-пилота, не production-приёмка FastAPI/SSG MathStart.

История сохранена: [исходный отчёт](lesson-final-react-2026-10-23.md) и весь `lesson-final-2026-10-23/` не переписывались. Новые результаты находятся в [lesson-fixes-2026-10-23](lesson-fixes-2026-10-23/execution.md).

## Проверенный кандидат и сохранность работы

- Основной каталог `C:/Projects/MathStart-Python`, фактическая ветка **ui/ux**, HEAD **192d0fc315e35644eeb9bb713f58d7d15afb34a0**. Кандидат остаётся **dirty**; HEAD сам по себе его не идентифицирует.
- Перед исправлениями проверены все **311** файлов fingerprint предыдущего аудита: отличий не было. [Исходный manifest](lesson-fixes-2026-10-23/implementation-before.json), [Git до](lesson-fixes-2026-10-23/git-status-before.txt), [Git после](lesson-fixes-2026-10-23/git-status-after.txt).
- [Итоговый manifest и treeFingerprint](lesson-fixes-2026-10-23/implementation-sha256.json) описывают **314** фактических входных файлов. В нём перечислены семь изменённых файлов прежнего кандидата и три новых файла проверок. Канонический curriculum, authored SVG/MathML, theme.css, шрифты, dependency lock и прочие исходные inputs сохранены по хешам.
- Прочитаны обе AGENTS.md, verification skill и полный исходный отчёт. Использованы impeccable harden/craft-floor, ui-ux-pro-max и web-animation-design в рамках утверждённого дизайна.
- Все три субагента запущены с **gpt-6-luna / medium / fork_turns=none**, без вложенных агентов. Владение файлами было разделено. Основной агент просмотрел изменения, усилил проверки жестов, добавил browser-регрессии и выполнил совместную проверку. Независимый повторный read-only review не нашёл дополнительных actionable-дефектов.
- Не выполнялись branch switch/reset/clean/stash/commit/push. Прежняя незакоммиченная работа сохранена. Не переносился шаблон на другие уроки. Существующий Vite на 5173, PID 23676, переиспользован и оставлен работающим.

## Исправления и доказательства

| Замечание | Изменение | Фактическое подтверждение |
| --- | --- | --- |
| **D1: тёмный синий текст** | В `frontend/prototypes/home/lesson.css:15` и `:41` введён локальный `--lesson-accent-text`. Dark: **oklch(0.68 0.1879 259.7964)**, прежний blue hue/chroma сохранены, повышена светлота. Исходный `--lesson-accent`/primary и stroke графика не заменены. Текст коэффициентов, легенды, кнопок и hover использует текстовый токен. | Текст reset/коэффициентов/легенды на **#20262f — 5.0703:1**, вместо 4.1384. Reset hover — **5.6354:1**. Проверены все четыре ширины и обе темы. |
| **D2: светлый подвал** | В lesson.css добавлен локальный `--lesson-footer-muted: #505b6a`; `frontend/src/shared/lesson/lesson-shell.css:53` и `:63` используют его для описания/copyright. Фон **#e2e8f1**, структура и размеры сохранены. | **5.5970:1**, вместо 4.26395, для обоих текстов. |
| **D3: свайп менял x** | `frontend/src/shared/lesson/quadratic-graph.tsx:91`–117: pointerdown только запоминает начало; pointerup подтверждает primary-button tap в пределах 8 CSS px. Выход за порог движения отменяет выбор даже при возвращении указателя. pointercancel, lost capture и уход за SVG очищают pending tap. Следующий tap работает; правая/средняя кнопки не выбирают точку. | В обеих темах CDP touch-свайп дал `scrollY 1349 → 1430`, события pointerdown → pointercancel и **x: 0 → 0**. Отдельные browser-тесты проверили явный touchCancel и следующий успешный tap. Native x-slider, мышь, клавиатура и pan-y сохранены. |
| **D4: favicon 404** | В `frontend/prototypes/home/materials.html:2` добавлен такой же `rel=icon href="data:,"`, как у HTML урока. Новое оформление favicon не придумывалось. | Fresh catalogue context → поиск → урок → reload: **нет HTTP ≥400, Console errors или pageerror**. Отдельная Network/CDP-проба также дала пустой список ошибок и отсутствующий запрос к missing favicon. |

Подробные замеры: [34 settled samples normal/hover/open](lesson-fixes-2026-10-23/contrast-states.json). Они получены независимо от Playwright-helper через canvas sRGB pixel conversion в Chrome и проверены против порога 4.5:1. Сам регрессионный spec преобразует CSS color-mix в sRGB и учитывает alpha/ancestor backgrounds. Иконка входа проверяется как нетекстовая графика с порогом 3:1; для текстовых надписей применяется 4.5:1.

### Дополнительные дефекты, найденные при проверке состояний

При проверке normal/hover/open обнаружились связанные с D1/D2 непроверенные ранее пары цветов. Они исправлены сразу:

- **Hover ссылок светлого подвала:** отдельный локальный `--lesson-footer-accent-text`, без изменения глобального primary. Итог **7.0712:1**.
- **Hover «Материалы» в тёмной шапке:** используется текстовый accent-token; итог **4.5582:1**. Тёмный footer link hover — **4.7033:1**.
- **Hover «Ответ и решение» в тёмной теме:** отдельная согласованная пара fill/text — светлее синий фон и прежний тёмный foreground, **5.0703:1**. Open/open-hover — **13.6638:1**. В светлой теме сохранён исходный белый hover-текст: **5.1686:1**, без уменьшения контраста относительно прежнего варианта.

Последняя правка перед фиксацией кандидата вернула именно исходный белый light-hover foreground, вместо слегка тонированного primary-foreground. После неё повторно прошли все восемь contrast cases, независимые численные замеры и сборка. Остальные исходники после совместного прогона не менялись; незатронутые проверки не дублировались.

## Актуализация тестов

Существующие сценарии не удалены. `quadratic.spec.ts` сохраняет прежние восемь сценариев и добавляет проверку canonical/alias/reload/query/fragment/каталога. Устаревшие требования заменены проверками согласованного поведения:

- Самопроверка управляется отдельной кнопкой «Ответ и решение». Нажатие вопроса не раскрывает её. Проверяются Enter/Space, expanded, controls, aria-hidden/inert и фокус.
- Названия соседних тем намеренно отсутствуют в видимом UI; содержательные aria-label и точные rel/href сохранены. Реальная клавиатурная активация проверяется через локальный Playwright interception. Запросы не доходят до protected/local backend на 8121.
- На основном адресе `/materials/8-algebra-32` проверены direct/reload, aliases и query/hash. Фиксированная route-запись с номером 32 сохранена.
- Проверка real Chrome zoom использует настоящий zoom profile и keyboard activation, чтобы координаты Playwright не зависели от масштаба. **Исходный timeout 45 s сохранён**, retries=0.
- Цветовая связь легенды и графика проверяется через предназначенные токены: legend text → accent-text, plotted root → accent. Проверка не заменена на «непустой цвет».

`frontend/tests/quadratic-source.test.tsx` исключает только старые summary-controls и текущую UI-кнопку из сравнения академического текста; содержимое ответов не исключается. Сохранены точные проверки секций, десяти ответов, таблицы, authored SVG; добавлено явное сравнение MathML.

Новые регрессии:

- `frontend/tests/quadratic-interaction.test.tsx`: четыре component-сценария для незавершённого/отменённого жеста, движения с возвратом, правой кнопки, lost capture/выхода за график, следующего успешного tap и остановки reset. Ожидаемые выбранные координаты проверяются точно, включая ненулевые значения.
- `frontend/prototypes/home/lesson-accessibility.spec.ts`: обе темы, normal/hover/open, шапка/подвал/ответ/reset/подписи на всех четырёх ширинах.
- `frontend/prototypes/home/lesson-regressions.spec.ts`: fresh-context favicon/console/navigation и настоящее CDP touch scroll/cancel/recovery на всех четырёх ширинах.

## Результаты команд текущего кандидата

Frontend-команды выполнены из `C:/Projects/MathStart-Python/frontend`, audit scripts — из корня. Ни один старый результат предыдущего аудита не засчитан как проверка исправлений.

| Команда | Итог | Свежие evidence |
| --- | --- | --- |
| `npm test` | **Exit 0, 200/200**, 24/24 test files; 0 skipped | [лог](lesson-fixes-2026-10-23/npm-test.log), [JSON](lesson-fixes-2026-10-23/npm-test.json) |
| `npm run typecheck` | **Exit 0**, contracts, route typegen, TS, 4 measured assertions | [лог](lesson-fixes-2026-10-23/frontend-typecheck.log) |
| `node node_modules/typescript/bin/tsc -p prototypes/home/tsconfig.json` | **Exit 0**, без диагностик | [пустой stdout/stderr](lesson-fixes-2026-10-23/pilot-typecheck.log) |
| `node node_modules/vite/bin/vite.js build --config prototypes/home/vite.config.mjs` | **Exit 0**, 47 modules. Повтор после последнего CSS-уточнения также exit 0 | [первый лог](lesson-fixes-2026-10-23/build.log), [окончательная сборка](lesson-fixes-2026-10-23/build-final.log) |
| `node node_modules/@playwright/test/cli.js test --config prototypes/home/playwright.config.ts --output .cache/lesson-fixes-playwright` | **Exit 0, 84/84**, 0 skipped/flaky/failed, 3.2 min | [лог](lesson-fixes-2026-10-23/playwright.log), [JSON](lesson-fixes-2026-10-23/playwright.json) |
| Тот же CLI, `lesson-regressions.spec.ts --output .cache/lesson-fixes-regressions` | **Exit 0, 8/8**, 37.5 s | [лог](lesson-fixes-2026-10-23/playwright-regressions.log), [JSON](lesson-fixes-2026-10-23/playwright-regressions.json) |
| Тот же CLI, `lesson-accessibility.spec.ts --output .cache/lesson-fixes-contrast-final` | **Exit 0, 8/8** повторно после последнего CSS-уточнения, 25.0 s | [лог](lesson-fixes-2026-10-23/playwright-contrast-final.log), [JSON](lesson-fixes-2026-10-23/playwright-contrast-final.json) |
| `node docs/audits/lesson-fixes-2026-10-23/run-audit.mjs` | **Exit 0, 28/28**, errors=[] | [лог](lesson-fixes-2026-10-23/browser-audit.log), [JSON](lesson-fixes-2026-10-23/browser-audit.json) |
| `node docs/audits/lesson-fixes-2026-10-23/run-supplement.mjs` | **Exit 0, 11/11**, плюс два before/after observations; resources/console=[] | [лог](lesson-fixes-2026-10-23/supplement.log), [JSON](lesson-fixes-2026-10-23/supplement.json) |
| `node docs/audits/lesson-fixes-2026-10-23/contrast-states.mjs` | **Exit 0**, 34 samples ≥4.5:1, errors=[] | [лог](lesson-fixes-2026-10-23/contrast-states.log), [JSON](lesson-fixes-2026-10-23/contrast-states.json) |
| `node docs/audits/lesson-fixes-2026-10-23/capture-review.mjs` | **Exit 0**, 80 окончательных viewport captures | [лог](lesson-fixes-2026-10-23/capture-review.log), [метаданные](lesson-fixes-2026-10-23/capture-review.json) |
| `impeccable.cmd detect --json …` для изменённых UI-файлов | **Exit 0, []** | [detector.json](lesson-fixes-2026-10-23/detector.json) |

В основной матрице было 84 случая; затем к final inventory добавлены восемь browser-регрессий, выполненных отдельно на всех четырёх ширинах. Сверка final inventory с фактически пройденными test identities подтверждает **92/92 уникальных сценария**, без пропущенных случаев. Повтор восьми contrast cases не прибавляется к уникальному количеству. Это два основных запуска и один точечный повтор, а не вымышленный единый CLI-запуск на 92 теста. [Inventory](lesson-fixes-2026-10-23/playwright-inventory.json), [сверка покрытия](lesson-fixes-2026-10-23/playwright-coverage.json).

Во время разработки у субагентов были фокусные неуспешные попытки: sandbox EPERM временного Vitest-кеша, недоступная sandbox health-check проба занятого 5173, draft selectors/цветовой helper и координатная/размерная погрешность тестов. Они устранены и не выдаются за PASS. Основание результата — выполненные основным агентом общие команды, текущие assertions и отдельные финальные browser/evidence-прогоны выше. Допуск **0.01 px** для вычисленного размера 43.999999 px отражает floating point, а не уменьшение принятой зоны 44 px.

## Что повторно проверено в браузере

Chrome **155.0.8059.85**, Windows, Node **24.19.0**, npm **11.17.0**; зависимости не обновлялись.

- **360×800, 768×1000, 1440×1000, 1920×1000**, каждая ширина в обеих темах. `scrollWidth === innerWidth`; читаемость формул/таблиц, раскрытые короткий и длинный ответы, статичные SVG, подвал и TOC просмотрены на свежих снимках. Professional Theme/QraftHive и утверждённая компоновка сохранены.
- **Real browser zoom 200%**: actual DPR=2, outer/inner 720/351, 768/375, 1440/711, 1920/951; visualViewport.scale=1. CSS zoom/pageScaleFactor не использовались. Обе темы, длинное решение, клавиатура и reset; page overflow нет.
- **Содержание**: Enter/кнопка, Escape/крестик/desktop backdrop, initial focus, Tab/Shift+Tab trap, возврат фокуса, body scroll lock/unlock, все восемь section anchors и active background; быстрые повторные open/Escape без зависания. На 360 dialog занимает всю ширину, внешней зоны backdrop нет.
- **Самопроверка**: все десять задач, question click не раскрывает, Enter/Space раскрывают отдельной кнопкой; controls/id, expanded/hidden/inert, скрытый ответ исключён из Tab; короткие/длинные решения и 12 быстрых переключений без остаточного состояния. Белая подложка в light сохранена.
- **График**: крайние коэффициенты, линейный/постоянный случаи, корни и таблица, click/tap и keyboard slider. Hover и движение не меняют выбранный x. Copy/cut в lab отменяются; текст кнопок не выделяется.
- **Reset**: промежуточные значения действительно появляются, финал **a=1,b=−4,c=3,x=0**. Ручной coefficient/x input прерывает reset, валидный tap на графике также останавливает его. Reduced motion делает сброс мгновенным.
- **URL**: direct/reload, поиск и список раздела каталога, 302 aliases `/quadratic.html`, старого slug и trailing slash; query/fragment сохраняются. Номер 32 остаётся явной константой.
- **Контент**: actual DOM сравнение текста всех восьми оставленных секций, десяти ответов, MathML, authored table cells и outerHTML обоих SVG прошло. Разрешённое исключение recap section 9 сохранено.
- **Console/pageerror/favicon**: основной audit errors=[]; отдельный свежий каталог даёт пустые console/resources; JS pageerror не обнаружен.

## Motion review

| Before | After |
| --- | --- |
| Точка выбиралась на pointerdown, до определения scroll/cancel. | Выбор подтверждается завершённым tap; отменённый или перемещённый жест не выбирает точку. При этом pan-y и естественная page scroll сохранены. |
| Drawer/backdrop: 280 ms вход, 220 ms выход; disclosure: 240 ms natural-height/160 ms opacity; hover: 160 ms. | Тайминги/компоновка не переделаны. Вход/выход, быстрое повторение и конечные состояния проверены; зависаний нет. |
| Reset: rAF 360 ms, ручное управление могло прервать его. | Плавное возвращение коэффициентов/x сохранено; завершённый tap и ползунки прерывают reset. |
| Reduced motion отключал transitions и делал reset мгновенным. | Поведение подтверждено на четырёх ширинах. Скрытое содержимое остаётся inert и при отключённых анимациях. |

## Свежие визуальные evidence

Всего **107 PNG** в новом каталоге screenshots. Основной агент просмотрел репрезентативные текущие рендеры каждой ширины/темы, формулу, authored SVG, длинное решение, TOC и touch/zoom evidence.

- [360 dark — график](lesson-fixes-2026-10-23/screenshots/360-dark-lab.png)
- [360 light — подвал](lesson-fixes-2026-10-23/screenshots/360-light-footer.png)
- [360 — формула](lesson-fixes-2026-10-23/screenshots/360-light-formula.png), [authored SVG в dark](lesson-fixes-2026-10-23/screenshots/360-dark-diagram.png)
- [768 light — график](lesson-fixes-2026-10-23/screenshots/768-light-lab.png), [768 dark — верх](lesson-fixes-2026-10-23/screenshots/768-dark-top.png)
- [1440 dark — TOC](lesson-fixes-2026-10-23/screenshots/1440-dark-contents.png), [1440 light — длинный ответ](lesson-fixes-2026-10-23/screenshots/1440-light-answer-8.png)
- [1920 light — верх](lesson-fixes-2026-10-23/screenshots/1920-light-top.png), [1920 dark — график](lesson-fixes-2026-10-23/screenshots/1920-dark-lab.png)
- [После touch-свайпа x остаётся 0](lesson-fixes-2026-10-23/screenshots/touch-scroll-after-light.png)
- [Настоящий 200% zoom — узкое окно, длинное решение](lesson-fixes-2026-10-23/screenshots/zoom200-outer720-dark-long-solution.png)

## Открытые вопросы и ограничения

Открытых воспроизведённых дефектов в заданной области после исправлений не осталось. Вкусовые предложения исходного аудита, включая смену easing пары drawer/backdrop, не превращались в задачи и не реализовывались.

Проверки выполнены в Chrome с синтезированным CDP touch; физический телефон, Safari/Firefox/Edge, живой screen reader, FPS/CPU throttling и полный performance/network profiling не проверялись. Не заявляется полная WCAG-сертификация. Built prototype успешно собран, отдельный preview server не проверялся. Основной FastAPI/SSG runtime, production/protected stack, миграции, авторизация и live LLM не запускались и не менялись. Полный `verify_repo.py`/production gate не заменяется этим scoped результатом.
