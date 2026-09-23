# MathStart

MathStart — образовательный сайт по математике на Django.

Учебные материалы хранятся в файловых исходниках, публикуются в базу данных и отображаются через единую систему шаблонов, стилей и интерактивных компонентов.

## Основные части проекта

| Каталог | Назначение |
| --- | --- |
| `config/` | Настройки Django, URL-конфигурация и запуск проекта. |
| `content/` | Модели, представления, сервисы публикации, проверки и management-команды. |
| `curriculum/` | Источник истины для 263 учебных тем. |
| `site_content/` | Источник структуры сайта, неучебных страниц, редиректов и seed-media. |
| `templates/` | Django-шаблоны страниц и компонентов. |
| `static/mathstart/` | Общие CSS и JavaScript-ресурсы сайта. |
| `media/` | Runtime-хранилище медиафайлов Django. |
| `docs/` | Техническая документация проекта. |
| `var/` | Локальные резервные копии и отчёты проверок. |

## Источники данных

Схема базы данных определяется Django-миграциями.

Учебные темы находятся в `curriculum/`.

Каталог классов, предметов и разделов, структурные страницы сайта, редиректы и исходные медиафайлы находятся в `site_content/`.

Рабочий `db.sqlite3` и runtime-каталог `media/` не являются источниками истины и могут быть восстановлены из файлов проекта.

## Установка

Создайте и активируйте виртуальное окружение:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Установите зависимости:

```powershell
pip install -r requirements.txt
```

Создайте локальный `.env` на основе `.env.example`:

```powershell
Copy-Item .env.example .env
```

Примените миграции:

```powershell
python manage.py migrate
```

Восстановите содержимое сайта:

```powershell
python manage.py bootstrap_site
```

Запустите сервер:

```powershell
python manage.py runserver
```

## Восстановление пустой базы

Полное состояние MathStart восстанавливается двумя командами:

```powershell
python manage.py migrate
python manage.py bootstrap_site
```

`bootstrap_site` восстанавливает:

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
| Redirect | 280 |

Команда идемпотентна: повторный запуск на синхронизированном проекте не создаёт дубликатов.

Проверка bootstrap без записи:

```powershell
python manage.py bootstrap_site --dry-run
```

## Работа с уроками

Исходники уроков находятся в `curriculum/`.

Публикация одной темы:

```powershell
python manage.py publish_lessons --slug SLUG --dry-run
python manage.py publish_lessons --slug SLUG
```

Публикация всего каталога:

```powershell
python manage.py publish_lessons --all --dry-run
python manage.py publish_lessons --all
```

Проверка соответствия файлов базе:

```powershell
python manage.py check_lesson_sources --all
```

Обновление указателя уроков:

```powershell
python manage.py index_lessons
```

Подробная инструкция находится в [`docs/editing-lessons.md`](docs/editing-lessons.md).

## Проверки проекта

Системная проверка Django:

```powershell
python manage.py check
```

Тесты:

```powershell
python manage.py test
```

Проверка учебных исходников:

```powershell
python manage.py check_lesson_sources --all
```

Проверка качества HTML и SVG:

```powershell
python manage.py check_content_quality
```

Проверка целостности сайта:

```powershell
python manage.py check_site_integrity
```

Проверка состояния моделей:

```powershell
python manage.py makemigrations --check --dry-run
```

## Документация

Архитектура проекта:

[`docs/architecture.md`](docs/architecture.md)

Редактирование и публикация уроков:

[`docs/editing-lessons.md`](docs/editing-lessons.md)

Общие стили и ресурсы учебных страниц:

[`docs/lesson-theme.md`](docs/lesson-theme.md)

Каталог всех учебных тем:

[`curriculum/INDEX.md`](curriculum/INDEX.md)