# Общая тема MathStart

Ранее пользователь выбрал Professional Theme как основу. 22.10.2026 началось
сравнение тем на том же макете: сейчас в отдельном React-прототипе активна
ExploreMiam. Это проба нового варианта, а не окончательное утверждение темы
для всего сайта. Внедрение во весь продукт ещё не выполнено.

## Активный кандидат: ExploreMiam

- [Страница темы](https://tweakcn.com/themes/cmnfqba56000104la8fufb2f1).
- [Registry export](https://tweakcn.com/r/themes/cmnfqba56000104la8fufb2f1),
  получен через HTTPS 22.10.2026.
- Активные файлы: `frontend/prototypes/home/theme.registry.json` и `theme.css`.
- Все эффективные значения CSS совпадают с export: 58 light / 57 dark.
- SHA-256 нормализованного JSON:
  `4dd7db3d4feebf01b096215918f2f2b254ff6a9c738a7add512072484486041c`.
- Основной акцент — фиолетовый, secondary — мятный. Основной шрифт Inter,
  формулы Merriweather Italic, radius `0.5rem`. Fira Code объявлен в export,
  но не используется/не загружается. Merriweather хранится локально с OFL.

## Сохранённый предыдущий вариант: Professional Theme

- [Professional Theme, Rachel Hong](https://tweakcn.com/themes/cmluajfgz000004l5afke7znm).
- [Registry export](https://tweakcn.com/r/themes/cmluajfgz000004l5afke7znm).
- Сохранённый исходник: `frontend/prototypes/home/themes/professional.registry.json`.
- Сохранённые переменные: `frontend/prototypes/home/themes/professional.css`.
- Оба файла совпадают побайтово с соответствующими файлами исходного `3346094`.
- 22.10.2026 исходник повторно сопоставлен с live export: JSON-объекты совпадают.
  Проверены все эффективные переменные: 58 light и 57 dark, включая theme aliases.
- SHA-256 нормализованного JSON (`JSON.stringify(JSON.parse(source))`, UTF-8):
  `99d42f9e91c1f4fb804f03ca5e68479fc20bf4452ba0299b8ce237626385c9e6`.

## Правила применения

Цвета брать по ролям `background/foreground`, `card/card-foreground`,
`primary/primary-foreground`, `muted`, `border`, `ring`, `sidebar-*`.
Не подбирать похожие hex-цвета вручную. Допустимы прозрачность и производные
`color-mix` из этих tokens для спокойных фонов/разделителей/иллюстраций.

Основной текст текущих вариантов — Inter (с кириллицей), локальный с OFL.
Serif/mono из экспорта загружать, когда они действительно используются:
у ExploreMiam формулы используют локальный Merriweather, mono не используется.
Базовый radius берётся из активной темы (`0.5rem` у ExploreMiam,
`0.375rem` у Professional Theme);
дополнительные размеры компонентов выводить из `--radius`, а не менять token.

Большие нейтральные поверхности/поля используют `muted/background/card`, а не
`secondary`: secondary у ExploreMiam — насыщенный мятный акцент. Дополнительный
акцент использован для второй группы долей в рисунке, без изменения математики.
Sidebar использует собственный token `sidebar`. Эти роли сохраняют баланс
нейтральной основы и небольших цветных акцентов при смене палитры.

Светлая и тёмная темы используют один набор семантических ролей. SVG наследуют
эти же цвета. Пропорция 60/30/10 — ориентир визуального баланса, не pixel assertion.

Тема не задаёт готовую раскладку страниц. Размеры текста, сетка, поля и
композиция проектируются под конкретный экран и проверяются отдельно.
Текущая общая поверхность каталога и тонкие разделители не должны превращаться
в рамку/тень вокруг каждого элемента. У учебных разделов нет заливки/смены
границы по hover; видимый keyboard focus и pointer cursor остаются.

После окончательного выбора применять общую основу при заданиях для public/catalogue/lesson,
account/auth и staff, проверяя контраст и соответствующие состояния/сценарии.
Принятие темы не утверждает будущие игровые механики, окончательный layout,
библиотеку компонентов или полную миграцию текущих authored CSS.

Новых UI dependencies в прототипе нет. shadcn/ui/Tailwind не объявляются
установленными по факту использования tweakcn. Фактический стек и версии
продукта остаются в `ARCHITECTURE.md`.
