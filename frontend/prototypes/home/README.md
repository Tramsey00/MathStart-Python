# Главная и каталог MathStart — локальный React-прототип

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
Главная — index.html / landing.tsx; утверждённый навигационный каталог —
http://127.0.0.1:5173/materials.html (materials.html / main.tsx).
Главная содержит один прямой переход в каталог. Ссылки каталога с grade/subject
query parameters по-прежнему поддерживаются; неизвестные значения дают начальный выбор.
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

По последнему запросу главная переработана: удалены лозунги, дублирующий
выбор классов/предметов, квадрат суммы и разбор дробей. Остались конкретное
описание материалов, локальные фотографии, небольшой email/password preview
и один блок перехода в каталог. Общие header/footer упрощены.

Пользователь явно выбрал: сейчас только форма, подключение почты следующим
шагом. Поля проверяются, пароль можно показать/скрыть. Submit не отправляет
запросов, очищает форму и честно сообщает о preview. Пароли и почта не
сохраняются и не логируются. Реальный вход по логину доступен на :8121/account/.
OAuth, отправка писем, регистрация и изменения identity не добавлены.

Дополнительный приглушённый зелёный применён только в .landing-page;
общие Professional tokens/шрифты и каталог не перекрашивались.
Фотографии открываются одной короткой анимацией маски; на fine pointer есть
медленное приближение при наведении. Нет scroll-reveal, петель, parallax
и перехвата прокрутки. Reduced-motion отключает движение.
Режим light/dark сохраняется между страницами, отсутствие storage допустимо.
Авторы/лицензии фотографий указаны в images/README.md и подписи на странице.

Изучены без установки [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
и [Web Animation Design](https://github.com/vercel-labs/open-agents/blob/main/.agents/skills/web-animation-design/SKILL.md),
а также [Frontend Design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md).
Рекомендации по структуре/доступности/движению адаптированы к утверждённой теме;
их альтернативные палитры, шрифты и зависимости не применялись.

## Поведение и границы

Каталог читается из опубликованных curriculum/**/lesson.json и
site_content/catalog.json; исходный контент не изменяется. После изменения
контента сервер нужно перезапустить. По умолчанию выбран 7 класс / алгебра.
Вход, все темы и уроки ведут на существующий локальный сайт :8121.

Вводный текст, общая SVG-иллюстрация, каталог с поиском и окно тем сохранены.
Компактные строки показывают только номер, название раздела и число тем,
без превью первых тем. На desktop счётчик справа, на телефоне под названием.
Две колонки на широком экране; непарный последний раздел занимает всю ширину.
Высота зависит от названия, длинные названия не обрезаются.
Общие разделители, без повторяющихся кнопок и стрелок. Hover разделов не меняет
оформление; keyboard focus сохранён. Логотип и SVG не выделяются,
обычный текст доступен для копирования.

Повторный выбор предмета сворачивает его разделы без смены предмета.
Мобильное меню и окно тем поддерживают Escape и восстановление фокуса.
Окно закрывается нажатием на фон, но не нажатием внутри или перетаскиванием
из окна наружу. Поиск имеет очистку, Escape и компактное пустое состояние.

Освоение, XP и персональный прогресс не имитируются. Прототип не является
authoritative publication и не меняет backend/auth/SSG. Перенос в основной
продукт и подключение авторизации требуют отдельной задачи.
Тема описана в [theme-baseline](../../../docs/ux/theme-baseline.md),
история — в [audit](../../../docs/audits/ui-ux-home-prototype.md).
