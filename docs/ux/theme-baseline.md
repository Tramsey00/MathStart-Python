# Общая тема MathStart

22.10.2026 пользователь завершил сравнение и выбрал первую палитру
**Professional Theme со шрифтами QraftHive**. Структура учебного экрана сохранена.
Внедрение во всём продукте остаётся отдельной будущей задачей.

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
История вариантов остаётся в Git и хронологическом audit.
Единственная страница прототипа — `http://127.0.0.1:5173/`.
