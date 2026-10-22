# Главная MathStart — локальный React-прототип

Выбранный вариант: палитра **Professional Theme**, шрифты **QraftHive**.
Ветка ui/ux; это отдельный прототип, ещё не внедрение в публичный сайт.
Страница сравнения и экспериментальные темы удалены.

- [Professional Theme, Rachel Hong](https://tweakcn.com/themes/cmluajfgz000004l5afke7znm).
  Исходный экспорт — theme.registry.json; theme.css отличается только
  font stacks, которые пользователь выбрал из QraftHive.
- [QraftHive 1.0](https://tweakcn.com/themes/cmjgjiw79000304ji6e76e30k):
  Outfit variable для интерфейса, Merriweather Italic для формул, локально с OFL.
  Outfit не содержит кириллицы: русский текст использует системный fallback.
  Mono объявлен, но не используется и не загружается.
- Структура: [Math Learning Website UI](https://www.figma.com/community/file/1652599323840288360/math-learning-website-ui),
  Ayush Kumbhar’s team, CC BY 4.0. Адаптация к русскому каталогу MathStart;
  исходные иллюстрации/код не копировались.
- React/Vite используют существующие зависимости; новые UI-библиотеки не установлены.

## Запуск

Из frontend/ после установки locked dependencies:

```powershell
node node_modules/vite/bin/vite.js --config prototypes/home/vite.config.mjs
```

Открыть http://127.0.0.1:5173/. БД и контейнеры не запускаются.
Остановка: Ctrl+C. Нужен Node из диапазона frontend/package.json.

## Проверки

Из frontend/:

```powershell
node node_modules/typescript/bin/tsc -p prototypes/home/tsconfig.json
node node_modules/vite/bin/vite.js build --config prototypes/home/vite.config.mjs
node node_modules/@playwright/test/cli.js test --config prototypes/home/playwright.config.ts
```

Chrome: 360/768/1440/1920. Сервер запускается автоматически, если порт свободен.
Build, результаты и снимки — в игнорируемом frontend/.cache/.
Это проверки прототипа, они не заменяют product target gate.

## Поведение и границы

Каталог читается из опубликованных curriculum/**/lesson.json и
site_content/catalog.json; исходный контент не изменяется. После изменения
контента сервер нужно перезапустить. По умолчанию выбран 7 класс / алгебра.
Вход, все темы и уроки ведут на существующий локальный сайт :8121.

Вводный текст, общая SVG-иллюстрация, каталог с поиском и окно тем сохранены.
Компактные строки в две колонки на desktop, в одну на телефоне, общие
разделители, без повторяющихся кнопок и стрелок. Hover разделов не меняет
оформление; keyboard focus сохранён. Логотип и SVG не выделяются,
обычный текст доступен для копирования.

Повторный выбор предмета сворачивает его разделы без смены предмета.
Мобильное меню и окно тем поддерживают Escape и восстановление фокуса.
Окно закрывается нажатием на фон, но не нажатием внутри или перетаскиванием
из окна наружу. Поиск имеет очистку, Escape и компактное пустое состояние.

Освоение, XP и персональный прогресс не имитируются. Прототип не является
authoritative publication и не меняет backend/auth/SSG. Перенос в основной
продукт, шапка и подвал требуют отдельной задачи.
Тема описана в [theme-baseline](../../../docs/ux/theme-baseline.md),
история — в [audit](../../../docs/audits/ui-ux-home-prototype.md).
