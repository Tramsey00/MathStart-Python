# Редактирование уроков

Учебные темы MathStart редактируются в файловых исходниках внутри `curriculum/`.

## Найти тему

Полный указатель находится в [`../curriculum/INDEX.md`](../curriculum/INDEX.md).

Уроки сгруппированы по классу, предмету и разделу. Ссылка в указателе ведёт в `body.html`; остальные файлы темы находятся в том же каталоге.

Структура урока:

```text
curriculum/
└── класс/
    └── предмет/
        └── раздел/
            └── урок/
                ├── lesson.json
                ├── body.html
                ├── page.css
                └── page.js
```

`lesson.json` и `body.html` обязательны. `page.css` и `page.js` создаются только при необходимости.

## Что хранится в файлах

| Файл | Назначение |
| --- | --- |
| `lesson.json` | Метаданные страницы и формат исходника. |
| `body.html` | Учебный текст, формулы, таблицы, задания, решения, SVG и разметка интерактивов. |
| `page.css` | CSS, специфичный только для конкретного урока. |
| `page.js` | JavaScript, специфичный только для конкретного урока. |

Если локальный CSS или JavaScript больше не нужен, соответствующий файл можно удалить. Следующая публикация очистит поле `page_css` или `page_js` у опубликованной страницы.

## `lesson.json`

Пример:

```json
{
  "schema_version": 2,
  "format": "themed_html",
  "page": {
    "slug": "...",
    "page_type": "topic",
    "grade": "...",
    "subject": "...",
    "section": "...",
    "title": "...",
    "order": 1,
    "seo_title": "",
    "seo_description": "",
    "is_published": true
  }
}
```

Поддерживаемые значения `format`:

```text
themed_html
component_html
html
```

В текущем каталоге 260 уроков используют `themed_html`, а 3 урока — `component_html`.

`themed_html` используется для готовой учебной HTML-разметки, для которой содержание формируется по разделам урока.

`component_html` используется для страниц, часть структуры которых собирается через общие компоненты MathStart.

`html` поддерживается для HTML без дополнительной сборки renderer'ом.

## Идентификационные поля

Для уже опубликованного управляемого урока следующие поля считаются идентификационными:

```text
slug
page_type
grade
subject
section
```

Обычная публикация не изменяет их.

Через `lesson.json` можно изменять:

```text
title
order
seo_title
seo_description
is_published
```

Содержимое страницы изменяется через `body.html`, `page.css` и `page.js`.

## Редактирование `body.html`

В `body.html` находится фрагмент учебной страницы без общей HTML-оболочки Django.

Для формата `themed_html` разделы урока, участвующие в содержании, должны иметь уникальные `id`:

```html
<h2 id="linear-function">
  Линейная функция
</h2>
```

Содержание страницы формируется автоматически при чтении исходника.

Для SVG в `body.html` остаются сама разметка, геометрия, координаты, линии, точки и подписи.

## Локальный CSS

`page.css` предназначен только для оформления, специфичного для одной темы, например:

```text
размер уникального SVG
позиционирование подписей схемы
специальная компоновка собственного интерактива
локальная подсветка конкретного объекта
```

Общие карточки, таблицы, примеры, задания, математическая разметка и типографика оформляются в `static/mathstart/`.

Для повторно используемых элементов применяйте существующие общие классы и модификаторы. Не дублируйте общие компоненты в локальном `page.css`.

Подробнее: [`lesson-theme.md`](lesson-theme.md).

## Локальный JavaScript

JavaScript конкретной темы хранится в `page.js` без тегов `<script>`.

Если один и тот же интерактив требуется нескольким страницам, его реализацию следует хранить в `static/mathstart/js/widgets/`, а не копировать в каждый урок.

## Проверка и публикация одной темы

Сначала выполните dry-run:

```powershell
python manage.py publish_lessons --slug SLUG --dry-run
```

Если проверка прошла успешно, опубликуйте тему:

```powershell
python manage.py publish_lessons --slug SLUG
```

После публикации проверьте соответствие базы исходнику:

```powershell
python manage.py check_lesson_sources --slug SLUG
```

И проверьте страницу в браузере на запущенном сайте.

В стандартной SQLite-конфигурации перед фактической записью изменений создаётся резервная копия базы в `var/backups/`.

## Несколько тем и весь каталог

Несколько тем можно выбрать одной командой:

```powershell
python manage.py publish_lessons --slug SLUG_1 SLUG_2 SLUG_3 --dry-run
python manage.py publish_lessons --slug SLUG_1 SLUG_2 SLUG_3
```

Проверка и публикация всего каталога:

```powershell
python manage.py publish_lessons --all --dry-run
python manage.py publish_lessons --all
python manage.py check_lesson_sources --all
```

Если в выбранном наборе обнаружена ошибка или конфликт, запись изменений не выполняется частично.

## Контроль конфликтов

`LessonPublication` связывает опубликованную страницу с `lesson.json` и хранит `published_digest` последней принятой версии.

Если содержимое управляемого урока в базе изменено независимо от файлового исходника и не совпадает ни с последней принятой публикацией, ни с текущим исходником, публикация останавливается.

Автоматического принудительного перезаписывания такого конфликта нет.

Правильное содержимое должно быть зафиксировано в `curriculum/`, после чего публикацию можно повторить:

```powershell
python manage.py publish_lessons --slug SLUG --dry-run
python manage.py publish_lessons --slug SLUG
```

## Добавление новой темы

Для новой темы:

1. Создайте каталог урока в нужном классе, предмете и разделе внутри `curriculum/`.
2. Добавьте обязательные `lesson.json` и `body.html`.
3. При необходимости добавьте `page.css` и `page.js`.
4. Убедитесь, что `grade`, `subject` и `section` уже существуют в `site_content/catalog.json`.
5. Выполните публикацию новой темы по её `slug`.
6. Обновите указатель уроков.

Команды:

```powershell
python manage.py publish_lessons --slug SLUG --dry-run
python manage.py publish_lessons --slug SLUG
python manage.py check_lesson_sources --slug SLUG
python manage.py index_lessons
```

Если страницы с таким `slug` ещё нет в базе, публикация создаст новый `ContentPage` и `LessonPublication` после успешной проверки исходника и каталога.

## Указатель уроков

`curriculum/INDEX.md` генерируется командой:

```powershell
python manage.py index_lessons
```

Файл не следует редактировать вручную как основной каталог тем: после изменений структуры или названий его нужно пересоздать командой.

## Полная проверка после значительных изменений

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py check_lesson_sources --all
python manage.py check_content_quality
python manage.py check_site_integrity
python manage.py test
```

## Пустая база

Схема и всё содержимое сайта восстанавливаются из файлов проекта:

```powershell
python manage.py migrate
python manage.py bootstrap_site
```

После bootstrap учебные темы должны совпадать с исходниками:

```powershell
python manage.py check_lesson_sources --all
```
