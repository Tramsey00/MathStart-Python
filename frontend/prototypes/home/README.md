# Главная MathStart — локальный React-прототип

Проба выбранного пользователем направления, не внедрение в публичный сайт и не
закрытие полной задачи MS-N001. Ветка `ui/ux`, исходный main `1a015f7`.

- Структура: [Math Learning Website UI](https://www.figma.com/community/file/1652599323840288360/math-learning-website-ui),
  Ayush Kumbhar’s team, CC BY 4.0. Адаптация: русский язык, классы/предметы/разделы
  MathStart, поиск и мобильная навигация; исходные иллюстрации/код не копировались.
- Тема: [Professional Theme](https://tweakcn.com/themes/cmluajfgz000004l5afke7znm),
  Rachel Hong. Полный исходный экспорт сохранён в `theme.registry.json`;
  `theme.css` — его light/dark/theme cssVars без ручной подмены цветов.
- React/Vite берутся из существующего lock. shadcn, Tailwind и Next.js не установлены:
  для пробы используются CSS-переменные темы и обычные React-компоненты.
- Inter (Latin/Cyrillic) хранится локально с OFL. Моноширинный шрифт объявлен
  экспортом, но в этом макете не используется и не загружается.

## Запуск

Из `frontend/` после установки существующих locked dependencies:

```powershell
node node_modules/vite/bin/vite.js --config prototypes/home/vite.config.mjs
```

Открыть http://127.0.0.1:5173/. Порт отдельный, БД/контейнеры не запускаются.
Нужен Node из диапазона `frontend/package.json`. Остановка: Ctrl+C.

Проверки из `frontend/`:

```powershell
node node_modules/typescript/bin/tsc -p prototypes/home/tsconfig.json
node node_modules/vite/bin/vite.js build --config prototypes/home/vite.config.mjs
node node_modules/@playwright/test/cli.js test --config prototypes/home/playwright.config.ts
```

Browser checks используют установленный Chrome; сервер запускается автоматически,
если порт свободен. Результаты, build и screenshots — в игнорируемом `frontend/.cache/`.
Этот отдельный конфиг не входит в существующий product CI и не заменяет его.

## Границы

Каталог строится только из опубликованных `lesson.json` и `site_content/catalog.json`.
Исходники читаются при запуске/build; после правок контента перезапустить сервер.
Проба не является authoritative publication и не обходит gateway основного сайта.
Тексты, счётчики тем и ссылки настоящие; процент освоения, XP, тесты, рейтинг и
персональный прогресс не имитируются. Тема/класс/поиск в памяти до обновления.
По умолчанию 7 класс / алгебра для сравнения с выбранным образцом.

Вход, все темы и уроки ведут на существующий локальный сайт :8121. Если он не
запущен, эти переходы недоступны. Новая форма входа в этот прототип не входит.
Прототип адаптирован под 360/768/1440; desktop sidebar превращается в native
modal dialog с Escape и восстановлением фокуса. 60/30/10 — ориентир баланса:
белая основа, вспомогательные поверхности, синий акцент. Это не измеренные доли
пикселей. Доступность и человеческая визуальная приёмка ещё требуют оценки.

После просмотра отдельно решить: сохраняем ли выбранную структуру, начальный
экран/класс, плотность карточек, цвета и меню. Перенос на `/`, библиотека компонентов,
SSG/no-JS, поисковые URL, auth и rollout требуют следующего явного поручения.
