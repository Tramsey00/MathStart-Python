# MS-T005 — актуальные блокировки и список для Владимира

Повторная обработка всех 46 прежних legacy-тем выполнена на основе `9804073` с интегрированными `f5cfddd`/`65a51a1`. Предыдущие ошибки не использовались как доказательство текущего отказа.
Результат: 30 новых активированных источников, 1 валидный документ до решения URL, 15 converter/validator blockers. Всего по классу 58 новых React-документов + принятый пилот = 59/75; 16 ещё не активированы.
Общие исправления ниже **только предложены**, converter/validator/renderer/CSS/math helper не менялись. Этот файл — список для согласования, не поручение следующей задачи.

## Необходимые общие исправления для Владимира

| Область | Необходимое поведение и affected routes |
| --- | --- |
| SVG font-style | Сохранить font-style=italic на SVG text (geometry-1/3/4/10). Конвертер и server validator сейчас не допускают атрибут; нужен узкий SVG allowlist, без общего допуска style |
| SVG fill-opacity | Сохранить .85/0.9 на polygon (geometry-5/12), с проверкой конечного диапазона 0..1 в конвертере и validator |
| Inline code | Geometry-1 после первого SVG отказа содержит code с A ∈ a, C ∉ a, AB, a ∩ b = O. Поддержать семантический code и в converter, и в validator; не терять обозначения |
| Images | Geometry-11: img src/alt, image-14.png и image-13.png, строки 22/130. Сохранить сами ресурсы/URL/alt; backend уже поддерживает img, converter — нет |
| SVG gradients | Statistics-27: linearGradient#barGrad + stop, offset и stop-color, строки 250–252. Нужны converter и validator support для проверенных локальных SVG defs/references; не заменять диаграмму плоской заливкой |
| Root-level legacy navigation | Пропускать только известный .ms-nav до проверки root section shape; statistics-4/8/18/26. Не допускать произвольный root div молча |
| Meaningful root figures | Statistics-25: root .ms-figure со схемой монеты/кости, строка 68; statistics-26: root .ms-figure графика накопленной частоты, строка 76. Сохранить весь SVG, caption и исходный порядок; нужна явная поддержка в модели секций/конвертере, не удаление |
| Section headers/anchors | Statistics-26 theory: h2 вложен в ms-lab-header, строка 24. Обработать явно, сохранив existing theory ID. Нельзя применять заглушку вместо лабораторной работы |
| Terminal exercise variants | Распознать терминальные разделы Практические задания, Задания и проверка, Проверь исследование, Задания по результатам опыта, Итоговая самопроверка. Сохранить все задачи/ответы, назвать Самопроверка и исключить последующие учебные блоки по стандарту. Тогда lab-result / course-complete после них не требуют синтетического ID. Affected statistics-4/8/18/26/27 |
| Scoped chart dimensions in validator | Statistics-7/8: width:37.5%,62.5%,50%,75%,100%,83.333%,66.667%,33.333%; statistics-9: height:72px/96px/120px. Размеры кодируют данные; нужен узкий проверенный контракт конкретных диаграмм, не unrestricted inline CSS |

## Отдельные согласования пользователя / UI

- **URL**: /materials/7-algebra-1 занят permanent alias линейного пилота. Документ первой темы валиден, 11 составных дробей разметлены, но renderer и маршрут не активированы. Пользователь выбирает судьбу canonical/alias; номера не сдвигались.
- **CSS-диаграммы statistics-7/8/9**: после исправления validator понадобятся отдельно согласованные узкие runtime rules или эквивалентное представление со всеми данными. Нельзя снять blocker удалением width/height. Statistics-8 также использует собственную CSS-круговую диаграмму ms-pie-practice; сохранять её доли, не применять значения другого урока.
- **Statistics-25**: кроме root SVG есть legacy ms-coin/ms-die presentation. После общего исправления конвертера проверить доступность и визуальную эквивалентность перед активацией.
- Ручная визуальная/педагогическая приёмка и независимое review всех новых документов остаются PENDING. Публикация отдельно; локальная БД и snapshot не обновлялись.

## Пофайловые текущие ошибки (все 16 оставшихся тем)

Ниже current retry, включая дополнительные неподдерживаемые элементы после первого отказа. Полный machine-readable inventory — ms-t005-migration-map.json.

### /materials/7-algebra-1 — Числовые выражения. Алгебраические выражения

Статус: `PREPARED_BLOCKED_URL`. Source: `curriculum/7-klass/algebra/01-matematicheskie-modeli/01-chislovye-vyrazheniya-algebraicheskie-vyrazheniya`.
- Proposed /materials/7-algebra-1 is the preserved permanent alias of the linear pilot; user URL decision required

### /materials/7-geometry-1 — Точки, прямые, отрезки и лучи. Измерение отрезков

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/geometriya/01-osnovy-geometrii/01-tochki-pryamye-otrezki-i-luchi-izmerenie-otrezkov`.
- Unsupported attribute: font-style
- `curriculum/7-klass/geometriya/01-osnovy-geometrii/01-tochki-pryamye-otrezki-i-luchi-izmerenie-otrezkov/body.html:71` — `text`, section `theory`: converter does not support attribute font-style.
  Element: `<text x="778" y="214" font-size="21" font-style="italic" font-weight="800" fill="#1d4ed8">a</text>`
- `curriculum/7-klass/geometriya/01-osnovy-geometrii/01-tochki-pryamye-otrezki-i-luchi-izmerenie-otrezkov/body.html:84` — `code`, section `theory`: converter does not support tag code.
  Element: `<code>A ∈ a</code>`
- `curriculum/7-klass/geometriya/01-osnovy-geometrii/01-tochki-pryamye-otrezki-i-luchi-izmerenie-otrezkov/body.html:89` — `code`, section `theory`: converter does not support tag code.
  Element: `<code>C ∉ a</code>`
- `curriculum/7-klass/geometriya/01-osnovy-geometrii/01-tochki-pryamye-otrezki-i-luchi-izmerenie-otrezkov/body.html:94` — `code`, section `theory`: converter does not support tag code.
  Element: `<code>AB</code>`
- `curriculum/7-klass/geometriya/01-osnovy-geometrii/01-tochki-pryamye-otrezki-i-luchi-izmerenie-otrezkov/body.html:99` — `code`, section `theory`: converter does not support tag code.
  Element: `<code>a ∩ b = O</code>`

### /materials/7-geometry-3 — Смежные и вертикальные углы. Перпендикулярные прямые

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/geometriya/01-osnovy-geometrii/03-smezhnye-i-vertikalnye-ugly-perpendikulyarnye-pryamye`.
- Unsupported attribute: font-style
- `curriculum/7-klass/geometriya/01-osnovy-geometrii/03-smezhnye-i-vertikalnye-ugly-perpendikulyarnye-pryamye/body.html:153` — `text`, section `lesson-section-3`: converter does not support attribute font-style.
  Element: `<text x="735" y="190" font-size="21" font-style="italic" font-weight="800" fill="#1d4ed8">a</text>`
- `curriculum/7-klass/geometriya/01-osnovy-geometrii/03-smezhnye-i-vertikalnye-ugly-perpendikulyarnye-pryamye/body.html:154` — `text`, section `lesson-section-3`: converter does not support attribute font-style.
  Element: `<text x="463" y="72" font-size="21" font-style="italic" font-weight="800" fill="#6d28d9">b</text>`

### /materials/7-geometry-4 — Треугольник и его элементы. Медиана, биссектриса и высота

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/geometriya/02-treugolniki/01-treugolnik-i-ego-elementy-mediana-bissektrisa-i-vysota`.
- Unsupported attribute: font-style
- `curriculum/7-klass/geometriya/02-treugolniki/01-treugolnik-i-ego-elementy-mediana-bissektrisa-i-vysota/body.html:81` — `text`, section `lesson-section-3`: converter does not support attribute font-style.
  Element: `<text x="763" y="239" font-size="21" font-style="italic" font-weight="800" fill="#1d4ed8">a</text>`

### /materials/7-geometry-5 — Три признака равенства треугольников

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/geometriya/02-treugolniki/02-tri-priznaka-ravenstva-treugolnikov`.
- Unsupported attribute: fill-opacity
- `curriculum/7-klass/geometriya/02-treugolniki/02-tri-priznaka-ravenstva-treugolnikov/body.html:48` — `polygon`, section `lesson-section-5`: converter does not support attribute fill-opacity.
  Element: `<polygon points="180,270 700,270 420,100" fill="#eff6ff" fill-opacity=".85" stroke="#2563eb" stroke-width="6" stroke-linejoin="round"/>`
- `curriculum/7-klass/geometriya/02-treugolniki/02-tri-priznaka-ravenstva-treugolnikov/body.html:48` — `polygon`, section `lesson-section-5`: converter does not support attribute fill-opacity.
  Element: `<polygon points="180,270 700,270 420,430" fill="#f7f4ff" fill-opacity=".85" stroke="#7c3aed" stroke-width="6" stroke-linejoin="round"/>`

### /materials/7-geometry-10 — Сумма углов треугольника. Внешний угол

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/geometriya/04-sootnosheniya-v-treugolnike/01-summa-uglov-treugolnika-vneshnij-ugol`.
- Unsupported attribute: font-style
- `curriculum/7-klass/geometriya/04-sootnosheniya-v-treugolnike/01-summa-uglov-treugolnika-vneshnij-ugol/body.html:67` — `text`, section `theory`: converter does not support attribute font-style.
  Element: `<text x="762" y="137" font-style="italic">a</text>`

### /materials/7-geometry-11 — Соотношения между сторонами и углами. Неравенство треугольника

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/geometriya/04-sootnosheniya-v-treugolnike/02-sootnosheniya-mezhdu-storonami-i-uglami-neravenstvo-treu-7d5b3dc2`.
- Unsupported source tag: img
- `curriculum/7-klass/geometriya/04-sootnosheniya-v-treugolnike/02-sootnosheniya-mezhdu-storonami-i-uglami-neravenstvo-treu-7d5b3dc2/body.html:22` — `img`, section `theory`: converter does not support tag img.
  Element: `<img class="ms-img" src="/media/uploads/2026/07/image-14.png" alt="Как связаны стороны и углы треугольника">`
- `curriculum/7-klass/geometriya/04-sootnosheniya-v-treugolnike/02-sootnosheniya-mezhdu-storonami-i-uglami-neravenstvo-treu-7d5b3dc2/body.html:22` — `img`, section `theory`: converter does not support attribute src.
  Element: `<img class="ms-img" src="/media/uploads/2026/07/image-14.png" alt="Как связаны стороны и углы треугольника">`
- `curriculum/7-klass/geometriya/04-sootnosheniya-v-treugolnike/02-sootnosheniya-mezhdu-storonami-i-uglami-neravenstvo-treu-7d5b3dc2/body.html:22` — `img`, section `theory`: converter does not support attribute alt.
  Element: `<img class="ms-img" src="/media/uploads/2026/07/image-14.png" alt="Как связаны стороны и углы треугольника">`
- `curriculum/7-klass/geometriya/04-sootnosheniya-v-treugolnike/02-sootnosheniya-mezhdu-storonami-i-uglami-neravenstvo-treu-7d5b3dc2/body.html:130` — `img`, section `lesson-section-8`: converter does not support tag img.
  Element: `<img class="ms-img" src="/media/uploads/2026/07/image-13.png" alt="Три возможные ситуации для неравенства треугольника">`
- `curriculum/7-klass/geometriya/04-sootnosheniya-v-treugolnike/02-sootnosheniya-mezhdu-storonami-i-uglami-neravenstvo-treu-7d5b3dc2/body.html:130` — `img`, section `lesson-section-8`: converter does not support attribute src.
  Element: `<img class="ms-img" src="/media/uploads/2026/07/image-13.png" alt="Три возможные ситуации для неравенства треугольника">`
- `curriculum/7-klass/geometriya/04-sootnosheniya-v-treugolnike/02-sootnosheniya-mezhdu-storonami-i-uglami-neravenstvo-treu-7d5b3dc2/body.html:130` — `img`, section `lesson-section-8`: converter does not support attribute alt.
  Element: `<img class="ms-img" src="/media/uploads/2026/07/image-13.png" alt="Три возможные ситуации для неравенства треугольника">`

### /materials/7-geometry-12 — Прямоугольные треугольники. Расстояния и построение треугольника

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/geometriya/04-sootnosheniya-v-treugolnike/03-pryamougolnye-treugolniki-rasstoyaniya-i-postroenie-treu-75214192`.
- Unsupported attribute: fill-opacity
- `curriculum/7-klass/geometriya/04-sootnosheniya-v-treugolnike/03-pryamougolnye-treugolniki-rasstoyaniya-i-postroenie-treu-75214192/body.html:301` — `polygon`, section `lesson-section-10`: converter does not support attribute fill-opacity.
  Element: `<polygon points="220,310 650,310 459.2,164.4" fill="#eff6ff" fill-opacity="0.9" stroke="#2563eb" stroke-width="6" stroke-linejoin="round" />`

### /materials/7-statistics-4 — Практическая работа «Таблицы»

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/04-prakticheskaya-rabota-tabliczy`.
- Unreviewed lesson root block: div
- Terminal exercise section has a variant heading; converter must preserve all tasks/answers and apply the self-check-last rule before removing subsequent educational blocks
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/04-prakticheskaya-rabota-tabliczy/body.html:112` — `div`, section `None`: root block is div; converter requires a section with direct h2 and stable id.
  Element: `<div class="ms-nav">     <a class="ms-btn ms-btn-secondary" href="/izvlechenie-i-interpretacziya-tablichnyh-dannyh/">Предыдущая тема</a>     <a class="ms-btn ms-btn-secondary" href="/7-klass-veroyatnost-i-statistika/">К темам вероятности и статистики</a>     <a class="ms-btn" href="/graficheskoe-pre`

### /materials/7-statistics-7 — Чтение и построение диаграмм

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm`.
- Unsupported authored layout style
- CSS-only data diagram also requires a separately agreed scoped renderer/CSS solution; do not remove dimensions or drawn data
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:47` — `div`, section `theory`: server validator rejects layout style width:37.5%.
  Element: `<div class="ms-bar-fill" style="width:37.5%"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:48` — `div`, section `theory`: server validator rejects layout style width:62.5%.
  Element: `<div class="ms-bar-fill" style="width:62.5%"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:49` — `div`, section `theory`: server validator rejects layout style width:50%.
  Element: `<div class="ms-bar-fill" style="width:50%"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:50` — `div`, section `theory`: server validator rejects layout style width:75%.
  Element: `<div class="ms-bar-fill" style="width:75%"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:51` — `div`, section `theory`: server validator rejects layout style width:100%.
  Element: `<div class="ms-bar-fill" style="width:100%"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:52` — `div`, section `theory`: server validator rejects layout style width:50%.
  Element: `<div class="ms-bar-fill" style="width:50%"></div>`

### /materials/7-statistics-8 — Практическая работа «Диаграммы»

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy`.
- Unreviewed lesson root block: div
- CSS-only data diagram also requires a separately agreed scoped renderer/CSS solution; do not remove dimensions or drawn data
- Terminal exercise section has a variant heading; converter must preserve all tasks/answers and apply the self-check-last rule before removing subsequent educational blocks
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:128` — `div`, section `None`: root block is div; converter requires a section with direct h2 and stable id.
  Element: `<div class="ms-nav">     <a class="ms-btn ms-btn-secondary" href="/chtenie-i-postroenie-diagramm/">Предыдущая тема</a>     <a class="ms-btn ms-btn-secondary" href="/7-klass-veroyatnost-i-statistika/">К темам вероятности и статистики</a>     <a class="ms-btn" href="/chislovye-nabory-srednee-arifmetic`
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:80` — `div`, section `lesson-section-3`: server validator rejects layout style width:100%.
  Element: `<div class="ms-bar-fill" style="width:100%"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:80` — `div`, section `lesson-section-3`: server validator rejects layout style width:83.333%.
  Element: `<div class="ms-bar-fill" style="width:83.333%"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:80` — `div`, section `lesson-section-3`: server validator rejects layout style width:66.667%.
  Element: `<div class="ms-bar-fill" style="width:66.667%"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:80` — `div`, section `lesson-section-3`: server validator rejects layout style width:50%.
  Element: `<div class="ms-bar-fill" style="width:50%"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:80` — `div`, section `lesson-section-3`: server validator rejects layout style width:33.333%.
  Element: `<div class="ms-bar-fill" style="width:33.333%"></div>`

### /materials/7-statistics-9 — Числовые наборы. Среднее арифметическое

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe`.
- Unsupported authored layout style
- CSS-only data diagram also requires a separately agreed scoped renderer/CSS solution; do not remove dimensions or drawn data
- `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe/body.html:55` — `div`, section `lesson-section-3`: server validator rejects layout style height:72px.
  Element: `<div class="ms-equalizer-bar" style="height:72px"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe/body.html:56` — `div`, section `lesson-section-3`: server validator rejects layout style height:96px.
  Element: `<div class="ms-equalizer-bar" style="height:96px"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe/body.html:57` — `div`, section `lesson-section-3`: server validator rejects layout style height:120px.
  Element: `<div class="ms-equalizer-bar" style="height:120px"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe/body.html:58` — `div`, section `lesson-section-3`: server validator rejects layout style height:96px.
  Element: `<div class="ms-equalizer-bar" style="height:96px"></div>`
- `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe/body.html:59` — `div`, section `lesson-section-3`: server validator rejects layout style height:96px.
  Element: `<div class="ms-equalizer-bar" style="height:96px"></div>`

### /materials/7-statistics-18 — Практическая работа «Случайная изменчивость»

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/veroyatnost-i-statistika/03-sluchajnaya-izmenchivost/04-prakticheskaya-rabota-sluchajnaya-izmenchivost`.
- Missing section heading or anchor
- Terminal exercise section has a variant heading; converter must preserve all tasks/answers and apply the self-check-last rule before removing subsequent educational blocks
- `curriculum/7-klass/veroyatnost-i-statistika/03-sluchajnaya-izmenchivost/04-prakticheskaya-rabota-sluchajnaya-izmenchivost/body.html:133` — `section`, section `None`: section lacks id.
  Element: `<section class="ms-lab-result">     <h2>Лабораторный вывод</h2>     <div class="ms-lab-fields">       <div class="ms-lab-field"><strong>Что обнаружено</strong><span>Отдельные поездки различаются, но большая часть значений сосредоточена около 21–23 минут.</span></div>       <div class="ms-lab-field">`
- `curriculum/7-klass/veroyatnost-i-statistika/03-sluchajnaya-izmenchivost/04-prakticheskaya-rabota-sluchajnaya-izmenchivost/body.html:143` — `div`, section `None`: root block is div; converter requires a section with direct h2 and stable id.
  Element: `<div class="ms-nav">     <a class="ms-btn ms-btn-secondary" href="/gruppirovka-gistogrammy/">Предыдущая тема</a>     <a class="ms-btn ms-btn-secondary" href="/7-klass-veroyatnost-i-statistika/">К темам вероятности и статистики</a>     <a class="ms-btn" href="/vvedenie-v-teoriyu-grafov/">Следующая те`

### /materials/7-statistics-25 — Монета и игральная кость в теории вероятностей

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/03-moneta-i-igralnaya-kost-v-teorii-veroyatnostej`.
- Unreviewed lesson root block: div
- `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/03-moneta-i-igralnaya-kost-v-teorii-veroyatnostej/body.html:68` — `div`, section `None`: root block is div; converter requires a section with direct h2 and stable id.
  Element: `<div class="ms-figure">       <p class="ms-figure-title">Две простые вероятностные модели</p>       <div class="ms-svg-wrap">         <svg class="ms-svg" viewBox="0 0 920 520" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Математическая монета с двумя исходами и правильная игральная кост`

### /materials/7-statistics-26 — Практическая работа «Частота выпадения случайного события»

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13`.
- Missing section heading or anchor
- Terminal exercise section has a variant heading; converter must preserve all tasks/answers and apply the self-check-last rule before removing subsequent educational blocks
- `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13/body.html:21` — `section`, section `theory`: section has no direct h2.
  Element: `<section id="theory" class="ms-section">     <div class="ms-lab-header ms-lab-header--overview">       <div>         <h2>1. Цель и оборудование</h2>         <p class="ms-text">Цель работы — сравнить наблюдаемую частоту орла с теоретической вероятностью 1/2 и проследить, как накопленная частота меняе`
- `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13/body.html:76` — `div`, section `None`: root block is div; converter requires a section with direct h2 and stable id.
  Element: `<div class="ms-figure">       <p class="ms-figure-title">Как менялась накопленная частота орла</p>       <div class="ms-svg-wrap">         <svg class="ms-svg" viewBox="0 0 920 560" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Линейный график накопленной частоты орла после 10, 20, 30, 40`
- `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13/body.html:232` — `div`, section `None`: root block is div; converter requires a section with direct h2 and stable id.
  Element: `<div class="ms-nav">     <a class="ms-btn ms-btn-secondary" href="/moneta-i-igralnaya-kost-v-teorii-veroyatnostej/">Предыдущая тема</a>     <a class="ms-btn ms-btn-secondary" href="/7-klass-veroyatnost-i-statistika/">К темам вероятности и статистики</a>     <a class="ms-btn" href="/obobshhenie-siste`

### /materials/7-statistics-27 — Обобщение, систематизация знаний

Статус: `BLOCKED_DEPENDENCY`. Source: `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij`.
- Unsupported source tag: linearGradient
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:606` — `section`, section `None`: section lacks id.
  Element: `<section class="ms-course-complete">     <h2>Что вы теперь умеете</h2>      <p>       Вы можете читать и строить таблицы и диаграммы, описывать числовые       данные с помощью среднего, медианы и размаха, исследовать частоты,       работать с гистограммами, анализировать графы, находить простейшие  `
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:250` — `linearGradient`, section `lesson-section-3`: converter does not support tag linearGradient.
  Element: `<linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">                 <stop offset="0%" stop-color="#60a5fa"/>                 <stop offset="100%" stop-color="#2563eb"/>               </linearGradient>`
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:251` — `stop`, section `lesson-section-3`: converter does not support tag stop.
  Element: `<stop offset="0%" stop-color="#60a5fa"/>`
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:251` — `stop`, section `lesson-section-3`: converter does not support attribute offset.
  Element: `<stop offset="0%" stop-color="#60a5fa"/>`
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:251` — `stop`, section `lesson-section-3`: converter does not support attribute stop-color.
  Element: `<stop offset="0%" stop-color="#60a5fa"/>`
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:252` — `stop`, section `lesson-section-3`: converter does not support tag stop.
  Element: `<stop offset="100%" stop-color="#2563eb"/>`
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:252` — `stop`, section `lesson-section-3`: converter does not support attribute offset.
  Element: `<stop offset="100%" stop-color="#2563eb"/>`
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:252` — `stop`, section `lesson-section-3`: converter does not support attribute stop-color.
  Element: `<stop offset="100%" stop-color="#2563eb"/>`
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:465` — `h2`, section `lesson-section-7`: Terminal self-check heading is Итоговая самопроверка; exact converter predicate does not recognize it, so subsequent ms-course-complete is not excluded by the standard.
  Element: `<h2>7. Итоговая самопроверка</h2>`
