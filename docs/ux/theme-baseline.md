# Общая тема MathStart

22.10.2026 пользователь завершил сравнение и выбрал первую палитру
**Professional Theme со шрифтами QraftHive**. Структура учебного экрана сохранена.
Внедрение во всём продукте остаётся отдельной будущей задачей.

В последней итерации пользователь разрешил третий цвет **только главной**:
приглушённый зелёный `#176f56` (dark `#79c7ab`) и его прозрачные производные.
Он задан локальными --home-support/--home-support-soft на .landing-page,
не заменяет shared tokens и не действует в утверждённом каталоге.

Это утверждённая основа для следующих косметических правок. Правило закреплено
также в `frontend/prototypes/home/AGENTS.md`: палитру и шрифты менять только
по явному запросу пользователя. Плотность и расположение компонентов могут
меняться в рамках этой основы. Theme CSS и файлы шрифтов в этой итерации
не менялись относительно `90aef2b`.

Контрольные SHA-256 утверждённых файлов:

- theme.css: `d15b103843bdb6cee935e6effb4e9c1c58385008fa5f25432b9d1610953195fa`.
- Outfit: `fc7287273e66929776e2ba54f144fe699080bec29f61bf649d70d871468aeade`.
- Merriweather: `afff81272b7653417bb6f8bef57add055b1f9fda36f27eba5f32b40752bd08da`.

## Палитра

- [Professional Theme, Rachel Hong](https://tweakcn.com/themes/cmluajfgz000004l5afke7znm).
- [Исходный registry](https://tweakcn.com/r/themes/cmluajfgz000004l5afke7znm)
  сохранён в `frontend/prototypes/home/theme.registry.json`.
- SHA-256 нормализованного исходного JSON:
  `99d42f9e91c1f4fb804f03ca5e68479fc20bf4452ba0299b8ce237626385c9e6`.
- `theme.css` содержит исходные theme/light/dark tokens Professional;
  единственное намеренное отличие — три font stacks из QraftHive.
- Синий primary используется для действий, выделенного предмета/класса и SVG.
  Второй набор долей имеет тот же цвет с прозрачностью 0.3.
- Поверхности используют background/card/muted/sidebar, разделители — border.
  Радиус исходной темы `0.375rem` сохранён.

## Шрифты

[Источник — QraftHive 1.0](https://tweakcn.com/themes/cmjgjiw79000304ji6e76e30k).

- sans: `Outfit, ui-sans-serif, sans-serif, system-ui`.
- serif: `Merriweather, ui-serif, serif`.
- mono: `JetBrains Mono, ui-monospace, monospace` (не используется/не загружается).
- Outfit variable и Merriweather Italic локальные, с OFL в каталоге fonts.
  Outfit получен из Google Fonts `ofl/outfit/Outfit[wght].ttf`.
- В Outfit нет кириллицы; русский текст использует системный sans-serif через
  исходный fallback QraftHive.

## Завершение эксперимента

ExploreMiam/QraftHive CSS и registry, архивная копия Professional, страница
сравнения, URL-переключатель и неиспользуемый Inter удалены из актуальных файлов.
История вариантов и завершённых дизайн-аудитов остаётся в Git.
По следующему запросу пользователя добавлена новая главная на
`http://127.0.0.1:5173/`; утверждённый каталог перенесён на `/materials.html`.
Обе страницы используют тот же неизменённый theme.css и локальные шрифты.
Главная имеет отдельные компоненты/расположение; каталог сохраняет принятые
hero, сетку разделов, поиск и диалоги. Шапка главной и общий подвал добавлены
в рамках этой задачи, без экспериментальных цветовых тем.

## Общие пути после фиксации шаблона, 23.10.2026

Тема теперь находится в frontend/src/shared/styles/theme.css, шрифты/OFL —
frontend/src/shared/styles/fonts/, подключения и reset — в base.css.
Тема и шрифты перенесены без изменения bytes; исторические хеши выше сохраняются.
Общие правила компонентов: [shared-ui-contract](shared-ui-contract.md).

## Математическая запись, утверждённое дополнение 25.10.2026

Пользователь утвердил единый вид дробей и корней и добавил смешанные числа
и дробные степени. Только для математической разметки используется локальный
STIX Two Math v2.13b171; он дополняет Professional Theme / QraftHive.
Основные sans/serif stacks, Outfit и Merriweather и их лицензии не заменяются.

- Font: `frontend/src/shared/styles/fonts/stix-two-math.woff2`.
- Лицензия: `frontend/src/shared/styles/fonts/STIX-OFL.txt` (SIL OFL).
- Закреплённый источник: [STIX v2.13b171](https://github.com/stipub/stixfonts/releases/tag/v2.13b171),
  `fonts/static_otf_woff2/STIXTwoMath-Regular.woff2`.
- Подключение — lesson.css, без CDN и новых JS-библиотек. Формулы используют
  MathML и класс lesson-math; SVG остаются авторскими рисунками.
- Принятые формы и общие helpers — раздел «Единая математическая запись»
  [стандарта переноса](../frontend/lesson-migration.md).
