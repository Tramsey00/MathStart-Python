# История исходного пилота

Источник: `lesson-migration.md` на `b5718c7f3f0b4a9ecaa659958bec27bd87e2e67f`.
Исторический раздел сохранён ниже; текущие требования — в [стандарте](lesson-migration.md).

## 11. Историческая запись исходного пилота MS-T001

Этот раздел фиксирует исходное назначение и candidate до пользовательских
корректировок. Текущий URL и требуемое поведение определены в разделе 1; ниже
оставлены только provenance-сведения исходного выполнения.

Линейному уроку явно назначен `/materials/7-algebra-1`. Номер 1 назначен как
постоянный идентификатор, не вычисляется из display order. Старый slug и известные
redirects ведут непосредственно к canonical с сохранением query; fragment
сохраняется браузером. Назначение квадратичного preview 8-algebra-32 сохранено,
его renderer остаётся legacy до MS-T006.

`frontend/scripts/convert-lesson.mjs` преобразует HTML в черновик content.json,
отказывается от неизвестной активной разметки и сохраняет semantic nodes:
paragraph, note, example, selfCheck, table, figure, interactive, inline/structure
nodes. Пилот содержит 13 секций, 13 самопроверок, 4 таблицы, 3 авторских SVG и
один linear interactive. Предварительные знания и экспресс-анализ сохранены.
Полная проверка сравнивает текст каждого раздела, клетки таблиц, SVG и anchors
с замороженным источником. Учебное пояснение под графиком осталось документом.

В переходный период body.html/page.css/page.js пилота сохранены как замороженный
источник сравнения и совместимости publication snapshots; не редактировать их
независимо от content.json. Удаление возможно после human acceptance и проверки
всех потребителей. Для новой React редакции учебный canonical — content.json.

LessonPage собирает общий chrome, содержание и секции. LinearGraph использует
отдельную чистую математику, а CoefficientControl разделяется с QuadraticGraph.
Исходные диапазоны сохранены: k от −3 до 3, b от −6 до 6, шаг 0,5; окно x от −8
до 8, y от −16 до 16. Reset возвращает k=1, b=0, учитывает reduced motion и
отменяется новым вводом. Swipe/pointercancel не выбирают точку.

SSG оставляет Router hydration только для react-v1. Legacy документы сохраняют
прежний renderer и полный document lifecycle. Ссылки урока обычные; переходы
утилизируют listeners/RAF вместе с документом. В initial render нет чтения storage
и времени; сохранённая тема применяется после hydration. Без JS содержание
использует native details, а решения доступны без inert/aria-hidden. CSS нового
урока подключается отдельно от legacy site.css. Сервер проверяет реальную статью,
а не вхождение документа в сериализованный hydration payload.

Статусы реализации, проверок, отдельного review и визуальной приёмки находятся
в карточке MS-T001 и реестре. Этот раздел сам по себе не означает PASS или приёмку.

Дополнение по review пилота: prepare/build проверяет source_path и published
source digest каждого react-v1 документа; неизбранный source нельзя публиковать
только за счёт изменения content.json. Строгая проверка всех nodes/attrs/URLs и
соответствия title/grade/subject/section повторяется при чтении immutable release.
Frozen CSS/JS учитываются compatibility_assets_digest без исполнения в React.
Canonical redirects выводятся только для опубликованных страниц, а quality check
читает pinned release через настоящий UnitOfWork, не текущий live registry.
