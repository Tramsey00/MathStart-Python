# Уроки MathStart

Автоматически формируемый указатель исходников учебных тем.

Уроки сгруппированы по классу, предмету и разделу. Ссылка открывает `body.html`; в каталоге той же темы находится `lesson.json` с метаданными страницы и, при необходимости, локальные `page.css` и `page.js`.

Указатель обновляется командой:

```powershell
python manage.py index_lessons
```

После этого идёт существующий список уроков без ручных изменений.

---

# 4. `docs/architecture.md`

Этот файл сейчас лучше полностью заменить. В нём одновременно присутствуют две версии таблицы каталогов и утверждения, которые больше не соответствуют текущей публикации. :chatgpt-content-reference{index="7"}

Готовый вариант:

# Архитектура MathStart

MathStart использует Django как runtime-приложение и файловые исходники как воспроизводимое описание содержимого сайта.

Рабочая база данных является проекцией этих исходников и не является единственным местом хранения контента.

## Источники истины

| Данные | Источник |
| --- | --- |
| Схема базы данных | `content/migrations/` |
| Учебные темы | `curriculum/` |
| Классы, предметы и разделы | `site_content/catalog.json` |
| Неучебные страницы | `site_content/pages/` |
| Redirect | `site_content/redirects.json` |
| Метаданные media | `site_content/media.json` |
| Исходные media-файлы | `site_content/media/` |
| Общие CSS и JavaScript | `static/mathstart/` |
| Django-шаблоны | `templates/` |

## Runtime-модель

Запрос страницы проходит следующий путь:

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
Django template
    ↓
HTML response
    ↓
Browser
