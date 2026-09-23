# Архитектура MathStart

MathStart — Django-приложение, в котором файловые исходники описывают структуру и содержимое сайта, а база данных служит runtime-представлением этих данных.

## Источники истины

| Данные | Источник |
| --- | --- |
| Схема базы данных | `content/migrations/` |
| Учебные темы | `curriculum/` |
| Классы, предметы и разделы | `site_content/catalog.json` |
| Структурные и информационные страницы | `site_content/pages/` |
| Редиректы | `site_content/redirects.json` |
| Метаданные медиафайлов | `site_content/media.json` |
| Исходные медиафайлы | `site_content/media/` |
| Общие CSS и JavaScript | `static/mathstart/` |
| Django-шаблоны | `templates/` |

Рабочие `db.sqlite3`, `media/`, `staticfiles/` и `var/` являются локальными runtime-каталогами и не используются как источник истины.

## Runtime страницы

Обычный запрос страницы проходит по цепочке:

```text
HTTP request
    ↓
config/urls.py
    ↓
content/urls.py
    ↓
content/views.py
    ↓
ContentPage
    ↓
content/services/lesson_theme.py
    ↓
templates/page_detail.html
    ↓
HTML response
```

Посетитель получает только опубликованные записи `ContentPage`. Файлы из `curriculum/` и `site_content/` не читаются при каждом HTTP-запросе: они используются при публикации и bootstrap.

Если обычная маршрутизация вернула 404, `RedirectFallbackMiddleware` проверяет активные записи `Redirect` и при наличии правила возвращает постоянный или временный редирект.

## Модель данных

Приложение `content` использует семь основных моделей:

| Модель | Назначение |
| --- | --- |
| `Grade` | Класс обучения. |
| `Subject` | Предмет внутри класса. |
| `Section` | Раздел внутри предмета. |
| `ContentPage` | Опубликованная страница сайта или учебная тема. |
| `LessonPublication` | Связь учебной темы с файловым исходником и контрольная сумма последней принятой публикации. |
| `MediaAsset` | Метаданные runtime-медиафайла и необязательная связь со страницей. |
| `Redirect` | Правило перенаправления URL. |

`ContentPage` содержит HTML страницы, локальные CSS и JavaScript, SEO-поля, статус публикации и связи с каталогом.

## Учебные темы

Каждая учебная тема находится в отдельном каталоге внутри `curriculum/`:

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

Чтение исходников выполняет `content/services/lesson_sources.py`. В зависимости от поля `format` итоговый HTML может дополнительно собираться сервисом `content/services/lesson_components.py`.

Публикацию выполняет `content/services/publishing.py`:

```text
lesson.json + body.html + page.css/page.js
                ↓
        чтение и валидация
                ↓
        подготовка snapshot
                ↓
        проверка конфликтов
                ↓
          одна транзакция
                ↓
ContentPage + LessonPublication
```

Для существующего управляемого урока идентификационными считаются поля:

```text
slug
page_type
grade
subject
section
```

Обычная публикация не изменяет эти поля. Название, порядок, SEO, статус публикации, HTML, CSS и JavaScript обновляются из файлового исходника.

Если в базе ещё нет страницы с указанным `slug`, публикация может создать новый `ContentPage`, если соответствующие класс, предмет и раздел уже существуют в каталоге.

`LessonPublication.published_digest` используется для защиты от конфликтов. Если содержимое страницы в базе изменено независимо от последней принятой файловой версии, публикация останавливается и не перезаписывает изменения автоматически.

При публикации изменений в стандартной SQLite-конфигурации создаётся резервная копия базы в `var/backups/`.

## Структура сайта

`site_content/` содержит воспроизводимое описание данных, не относящихся к отдельным учебным темам:

```text
site_content/
├── catalog.json
├── redirects.json
├── media.json
├── media/
└── pages/
    └── <slug>/
        ├── page.json
        ├── body.html
        ├── page.css
        └── page.js
```

`catalog.json` описывает классы, предметы и разделы.

`pages/` содержит структурные и информационные страницы. `page.css` и `page.js` для них также являются необязательными.

`redirects.json` описывает правила `Redirect`.

`media.json` содержит метаданные и SHA-256 для seed-media из `site_content/media/`.

## Bootstrap

Команда:

```powershell
python manage.py bootstrap_site
```

синхронизирует каталог, структурные страницы и редиректы, публикует все учебные темы, проверяет соответствие уроков файловым исходникам, копирует недостающие seed-media в runtime-хранилище и синхронизирует записи `MediaAsset`.

Команда идемпотентна: повторный запуск на синхронизированном проекте не создаёт дубликатов.

Проверка без сохранения изменений:

```powershell
python manage.py bootstrap_site --dry-run
```

Текущее содержимое проекта:

| Объект | Количество |
| --- | ---: |
| Классы | 6 |
| Предметы | 12 |
| Разделы | 63 |
| Учебные темы | 263 |
| Структурные и информационные страницы | 18 |
| Всего `ContentPage` | 281 |
| `LessonPublication` | 263 |
| `MediaAsset` | 29 |
| `Redirect` | 280 |

Пустая база восстанавливается командами:

```powershell
python manage.py migrate
python manage.py bootstrap_site
```

## Медиафайлы

`site_content/media/` хранит версионируемые seed-media.

`media/` — runtime-хранилище Django. При bootstrap отсутствующие файлы копируются из seed-media с проверкой SHA-256. Если runtime-файл уже существует, но отличается от ожидаемого содержимого, bootstrap завершается ошибкой.

## Статические ресурсы и оформление

Общие ресурсы находятся в `static/mathstart/`.

Основной набор CSS учебной страницы:

```text
site.css
lesson.css
lesson-math.css
lesson-components.css
lesson-diagrams.css
lesson-contents.css
```

Для неучебных страниц дополнительно используется `site-pages.css`.

Специализированные интерактивы могут подключать ресурсы из `static/mathstart/css/widgets/` и `static/mathstart/js/widgets/`.

Локальные `page.css` и `page.js` хранят только особенности конкретной страницы.

Подробнее: [`lesson-theme.md`](lesson-theme.md).

## Django Admin

Данные `Grade`, `Subject`, `Section`, `ContentPage`, `LessonPublication`, `MediaAsset` и `Redirect` доступны в Django Admin для просмотра.

Добавление, изменение и удаление этих объектов через admin отключены. Изменения вносятся в `curriculum/` или `site_content/`, после чего публикуются соответствующей management-командой.

## Проверки

Основные проверки проекта:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py check_lesson_sources --all
python manage.py check_content_quality
python manage.py check_site_integrity
```

`check_lesson_sources` проверяет соответствие опубликованных учебных тем файловым исходникам.

`check_content_quality` проверяет HTML и SVG опубликованных страниц.

`check_site_integrity` проверяет структуру страниц, связи, внутренние URL и ресурсы сайта и записывает полный отчёт в `var/reports/`.
