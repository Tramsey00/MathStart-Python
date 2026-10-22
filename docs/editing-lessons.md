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

В `body.html` находится фрагмент учебной страницы без общей React/SSG HTML-оболочки.

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

## Проверка и публикация

Target использует FastAPI/SQLAlchemy Content services. `manage.py` в текущем
checkout отсутствует; исторические команды запускаются только в pinned oracle
при специальных сравнениях. Авторские файлы сохраняются без нормализации.

Проверка всех файлов без БД:

```powershell
python -m backend.cli check-sources --source-root .
```

Дальнейшие команды требуют явно выбранной PostgreSQL/config среды из
[READ_RUNTIME](../backend/READ_RUNTIME.md), а запись — отдельной операторской
авторизации. Они не запускаются автоматически при редактировании файла.
Для одной темы подготовьте read-only preview с точным source SHA:

```powershell
$sourceSha = git rev-parse HEAD
python -m backend.content.publish prepare-sources --source-root . --source-sha $sourceSha --release-id lesson-preview --slug SLUG --dry-run
```

Без `--dry-run` подготовка требует новых `--input-root` и `--changes`, создаёт
immutable inputs/edition handoff. Несколько slugs передаются после `--slug`;
`--all` выбирает полный набор. Подготовка сама не активирует публикацию.
Затем actual locked frontend build, `plan` с проверенными digests, review плана,
`publish` отдельным процессом со stable owner/idempotency key и HTTP probes.
Точные обязательные arguments/roots — в [READ_RUNTIME](../backend/READ_RUNTIME.md)
и [release](../deploy/RELEASE.md); не заменяйте их fixture bootstrap.

`LessonPublication` сохраняет accepted published/source digests. Изменение
source-managed строки независимо от источника вызывает конфликт; автоматического
force overwrite нет. Повтор публикации не должен перезаписывать user history.
Резервируется согласованный PostgreSQL/media/release tuple по
[recovery](../deploy/RECOVERY.md), а не старый SQLite-only backup.

Проверка установленных источников и вывод нового индекса (read-only DB):

```powershell
python -m backend.cli check-lesson-sources --source-root . --slug SLUG
python -m backend.cli check-lesson-sources --source-root . --all
python -m backend.cli index-lessons --source-root . --output-root var/lesson-index-review
```

`index-lessons` пишет `INDEX.md` непосредственно в выбранный output-root. Сначала
сравните результат с отслеживаемым индексом; не перезаписывайте authored sources
или индекс автоматически. Для новой темы создайте обязательные lesson.json/body,
проверьте Grade/Subject/Section в site_content/catalog.json, затем обычный
reviewed publication path. Перенос существующих identity полей отдельно согласуется.

Полная проверка по [target-runtime](target-runtime.md) включает sources, HTTP
quality, URL/assets integrity, PostgreSQL/API и реальные frontend/browser checks:

```powershell
python scripts/verify_repo.py
```

Она требует подготовленного disposable runtime; pure subset его не заменяет.
Для пустой установки — schema preview/apply/check, explicit initial operator,
prepare-bootstrap/build/plan/publish по release runbook. Startup не делает seed/DDL.
Нельзя сбрасывать рабочую БД для проверки. Визуальный осмотр урока/формул/widgets
не заменяется только exit0 автоматической проверки.
