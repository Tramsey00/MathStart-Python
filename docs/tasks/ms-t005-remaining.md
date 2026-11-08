# MS-T005 — оставшиеся 9 тем

После активации семи geometry sources на основании 3449030 зарегистрированы 66/75 тем. Семь геометрических blockers из прежнего списка разрешены и не являются текущими.

Ниже 8 статистических тем и 1 URL-решение. Их source blockers взяты из карты повторной обработки 46 тем; в текущем geometry-only этапе они заново не конвертировались. История и прежние строки остаются в [followups предыдущего этапа](ms-t005-converter-followups.md).

## /materials/7-algebra-1 — Числовые выражения. Алгебраические выражения

Source: `curriculum/7-klass/algebra/01-matematicheskie-modeli/01-chislovye-vyrazheniya-algebraicheskie-vyrazheniya`. Статус `PREPARED_BLOCKED_URL`.
- Proposed /materials/7-algebra-1 is the preserved permanent alias of the linear pilot; user URL decision required

## /materials/7-statistics-4 — Практическая работа «Таблицы»

Source: `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/04-prakticheskaya-rabota-tabliczy`. Статус `BLOCKED_DEPENDENCY`.
- Unreviewed lesson root block: div
- Terminal exercise section has a variant heading; converter must preserve all tasks/answers and apply the self-check-last rule before removing subsequent educational blocks
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/04-prakticheskaya-rabota-tabliczy/body.html:112`: root block is div; converter requires a section with direct h2 and stable id.

## /materials/7-statistics-7 — Чтение и построение диаграмм

Source: `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm`. Статус `BLOCKED_DEPENDENCY`.
- Unsupported authored layout style
- CSS-only data diagram also requires a separately agreed scoped renderer/CSS solution; do not remove dimensions or drawn data
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:47`: server validator rejects layout style width:37.5%.
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:48`: server validator rejects layout style width:62.5%.
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:49`: server validator rejects layout style width:50%.
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:50`: server validator rejects layout style width:75%.
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:51`: server validator rejects layout style width:100%.
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/07-chtenie-i-postroenie-diagramm/body.html:52`: server validator rejects layout style width:50%.

## /materials/7-statistics-8 — Практическая работа «Диаграммы»

Source: `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy`. Статус `BLOCKED_DEPENDENCY`.
- Unreviewed lesson root block: div
- CSS-only data diagram also requires a separately agreed scoped renderer/CSS solution; do not remove dimensions or drawn data
- Terminal exercise section has a variant heading; converter must preserve all tasks/answers and apply the self-check-last rule before removing subsequent educational blocks
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:128`: root block is div; converter requires a section with direct h2 and stable id.
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:80`: server validator rejects layout style width:100%.
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:80`: server validator rejects layout style width:83.333%.
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:80`: server validator rejects layout style width:66.667%.
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:80`: server validator rejects layout style width:50%.
- `curriculum/7-klass/veroyatnost-i-statistika/01-predstavlenie-dannyh/08-prakticheskaya-rabota-diagrammy/body.html:80`: server validator rejects layout style width:33.333%.

## /materials/7-statistics-9 — Числовые наборы. Среднее арифметическое

Source: `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe`. Статус `BLOCKED_DEPENDENCY`.
- Unsupported authored layout style
- CSS-only data diagram also requires a separately agreed scoped renderer/CSS solution; do not remove dimensions or drawn data
- `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe/body.html:55`: server validator rejects layout style height:72px.
- `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe/body.html:56`: server validator rejects layout style height:96px.
- `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe/body.html:57`: server validator rejects layout style height:120px.
- `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe/body.html:58`: server validator rejects layout style height:96px.
- `curriculum/7-klass/veroyatnost-i-statistika/02-opisatelnaya-statistika/01-chislovye-nabory-srednee-arifmeticheskoe/body.html:59`: server validator rejects layout style height:96px.

## /materials/7-statistics-18 — Практическая работа «Случайная изменчивость»

Source: `curriculum/7-klass/veroyatnost-i-statistika/03-sluchajnaya-izmenchivost/04-prakticheskaya-rabota-sluchajnaya-izmenchivost`. Статус `BLOCKED_DEPENDENCY`.
- Missing section heading or anchor
- Terminal exercise section has a variant heading; converter must preserve all tasks/answers and apply the self-check-last rule before removing subsequent educational blocks
- `curriculum/7-klass/veroyatnost-i-statistika/03-sluchajnaya-izmenchivost/04-prakticheskaya-rabota-sluchajnaya-izmenchivost/body.html:133`: section lacks id.
- `curriculum/7-klass/veroyatnost-i-statistika/03-sluchajnaya-izmenchivost/04-prakticheskaya-rabota-sluchajnaya-izmenchivost/body.html:143`: root block is div; converter requires a section with direct h2 and stable id.

## /materials/7-statistics-25 — Монета и игральная кость в теории вероятностей

Source: `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/03-moneta-i-igralnaya-kost-v-teorii-veroyatnostej`. Статус `BLOCKED_DEPENDENCY`.
- Unreviewed lesson root block: div
- `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/03-moneta-i-igralnaya-kost-v-teorii-veroyatnostej/body.html:68`: root block is div; converter requires a section with direct h2 and stable id.

## /materials/7-statistics-26 — Практическая работа «Частота выпадения случайного события»

Source: `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13`. Статус `BLOCKED_DEPENDENCY`.
- Missing section heading or anchor
- Terminal exercise section has a variant heading; converter must preserve all tasks/answers and apply the self-check-last rule before removing subsequent educational blocks
- `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13/body.html:21`: section has no direct h2.
- `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13/body.html:76`: root block is div; converter requires a section with direct h2 and stable id.
- `curriculum/7-klass/veroyatnost-i-statistika/05-veroyatnost-i-chastota-sluchajnogo-sobytiya/04-prakticheskaya-rabota-chastota-vypadeniya-sluchajnogo-so-451fbe13/body.html:232`: root block is div; converter requires a section with direct h2 and stable id.

## /materials/7-statistics-27 — Обобщение, систематизация знаний

Source: `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij`. Статус `BLOCKED_DEPENDENCY`.
- Unsupported source tag: linearGradient
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:606`: section lacks id.
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:250`: converter does not support tag linearGradient.
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:251`: converter does not support tag stop.
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:251`: converter does not support attribute offset.
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:251`: converter does not support attribute stop-color.
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:252`: converter does not support tag stop.
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:252`: converter does not support attribute offset.
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:252`: converter does not support attribute stop-color.
- `curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html:465`: Terminal self-check heading is Итоговая самопроверка; exact converter predicate does not recognize it, so subsequent ms-course-complete is not excluded by the standard.

Для Владимира/согласования остаются meaningful root figures/navigation/nested headings, terminal self-check variants, SVG gradient definitions и безопасный контракт data-encoded размеров CSS-диаграмм. Общие изменения не поручаются автоматически. URL /materials/7-algebra-1 решает пользователь; существующий alias не менялся. Публикация и human acceptance отдельно.
