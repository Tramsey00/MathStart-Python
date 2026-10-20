# Общий стиль и ресурсы страниц MathStart

Оформление учебных страниц MathStart централизовано.

Все уроки используют общий набор CSS и JavaScript из `static/mathstart/`. В исходнике конкретной темы хранятся только её содержимое и действительно локальные особенности.

## Корневой элемент урока

Учебная страница использует:

```html
<div class="ms-lesson-page" ...>
```

или эквивалентный семантический элемент с классом:

```text
ms-lesson-page
```

Способ сборки страницы обозначается через:

```html
data-lesson-layout="themed"
```

или:

```html
data-lesson-layout="components"
```

Layout описывает способ подготовки содержимого, а не отдельную визуальную тему.

## Общие CSS

| Файл | Назначение |
| --- | --- |
| `static/mathstart/css/site.css` | Основная оболочка сайта, навигация и общие правила интерфейса. |
| `static/mathstart/css/lesson.css` | Базовая структура и оформление учебной страницы. |
| `static/mathstart/css/lesson-math.css` | Дроби, степени, корни и другая математическая разметка. |
| `static/mathstart/css/lesson-components.css` | Учебные компоненты, алгоритмы, доказательства, результаты и служебные блоки. |
| `static/mathstart/css/lesson-diagrams.css` | Диаграммы, легенды и схемы. |
| `static/mathstart/css/lesson-contents.css` | Содержание и навигационные элементы урока. |
| `static/mathstart/css/site-pages.css` | Оформление неучебных страниц сайта. |
| `static/mathstart/css/widgets/` | Стили специализированных интерактивных компонентов. |

Общие элементы должны оформляться именно здесь, а не дублироваться в `page.css` отдельных тем.

## Общий JavaScript

| Файл | Назначение |
| --- | --- |
| `static/mathstart/js/lesson-navigation.js` | Навигация по разделам урока и управление переходами. |
| `static/mathstart/js/lesson-diagrams.js` | Поведение и масштабирование схем. |
| `static/mathstart/js/math.js` | Общая математическая логика, используемая интерактивами. |
| `static/mathstart/js/widgets/` | Повторно используемые интерактивные компоненты. |

Специализированные ресурсы подключаются только тогда, когда странице требуется соответствующий функциональный элемент.

## Общие компоненты

Повторно используемая разметка находится в:

```text
templates/lessons/components/
```

Общие классы обеспечивают одинаковое оформление одних и тех же смысловых элементов на всех страницах.

Примеры базовых классов:

```text
.ms-example
.ms-task
.ms-card
.ms-card-grid
.ms-table
.ms-note
.ms-good
.ms-frac
```

Для вариантов компонента следует использовать существующий модификатор или добавить новый общий модификатор, если он нужен нескольким страницам.

## Карточки и сетки

Карточка:

```html
<article class="ms-card">
  ...
</article>
```

Сетка:

```html
<div class="ms-card-grid ms-columns-3">
  ...
</div>
```

Количество колонок задаётся общими классами:

```text
ms-columns-2
ms-columns-3
ms-columns-4
ms-columns-5
ms-columns-6
```

Смысловые варианты:

```text
ms-card--success
ms-card--error
```

Не создавайте локальную копию компонента только для изменения количества колонок или стандартного состояния.

## Локальный `page.css`

`page.css` нужен только тогда, когда конкретная страница имеет визуальную особенность, которую нельзя выразить общими компонентами.

Подходящие случаи:

```text
размер уникального SVG
позиционирование подписей схемы
специальная компоновка собственного интерактива
локальная подсветка конкретного математического объекта
```

Локальные правила необходимо ограничивать контейнером конкретного компонента.

Не следует переопределять в `page.css` глобальные:

```text
.ms-lesson-page
.ms-example
.ms-task
.ms-table
.ms-card
```

Если одно и то же правило требуется нескольким урокам, его следует перенести в общий CSS.

## `body.html`

В `body.html` находятся:

```text
учебный текст
математическая разметка
таблицы
примеры
задания
решения
SVG
разметка интерактивов
```

Для SVG в HTML сохраняются геометрия, координаты, линии, точки и текстовые подписи.

Общие цвета, типографика и повторно используемые правила размещаются в общих CSS-файлах.

## `page.js`

JavaScript конкретной темы хранится в:

```text
curriculum/.../page.js
```

Файл не содержит тегов `<script>`.

Если интерактив используется повторно, его реализацию следует вынести в `static/mathstart/js/widgets/`.

## `themed_html`

Для `themed_html` учебная HTML-разметка находится в `body.html`.

Содержание страницы формируется по учебным разделам.

Каждый заголовок раздела, участвующий в содержании, должен иметь уникальный `id`.

Пример:

```html
<h2 id="linear-function">
  Линейная функция
</h2>
```

## `component_html`

Для `component_html` часть итоговой разметки собирается через общие компоненты.

Этот формат подходит страницам, где требуется более структурированная сборка разделов и учебных блоков.

Оформление остаётся тем же общим оформлением MathStart.

## Ресурсы страницы

Подготовка markup выполняется `backend/content/sources.py` и
`backend/content/components.py`; shared resource delivery входит в immutable
input/build и frontend LessonHost lifecycle. Общие styles/widgets — в
`static/mathstart/`. Исторического `content/services/lesson_theme.py` в target нет.

## Публикация и контроль качества

Изменение lesson.json/body/page.css/page.js проходит source preview и обычный
prepare/build/plan/publish; точные commands —
[редактирование уроков](editing-lessons.md#проверка-и-публикация).
Изменение общих CSS/JS требует нового проверенного immutable asset/frontend
artifact и активации через тот же authority protocol. `collectstatic` и
development server не являются текущим deployment path.

Сохранить bytes/URL/anchors/math/SVG и поведение widgets; scoped CSS не должен
менять другие уроки. Реальные content-quality/site-integrity и browser/visual
checks из [target-runtime](target-runtime.md) обязательны по scope. При принятом
редизайне semantic checks сохраняются, visual references обновляются явно.

## Связанные документы

Редактирование уроков:

[`editing-lessons.md`](editing-lessons.md)

Архитектура:

[`architecture.md`](architecture.md)
