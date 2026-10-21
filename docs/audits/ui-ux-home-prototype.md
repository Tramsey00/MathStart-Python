# UI/UX: первая проба главной MathStart

22.10.2026, Europe/Moscow. Статус: самопроверка прототипа завершена;
ожидаются оценка пользователя и отдельное ревью. Не ACCEPTED.

## Основание и база

Пользователь поручил реализацию тестовой главной в ветке `ui/ux` и подтвердил:
Professional Theme `cmluajfgz000004l5afke7znm`, структуру Figma
`1652599323840288360`. Это один экспериментальный экран; полная MS-N001–005
не объявляется выполненной. Перенос на product routes и auth redesign не входят.

Начальный чистый checkout: `docs-and-workflow-cleanup`, HEAD
`afce9559149011be1b7c660dd79871dbc044f7f7`. После успешного `git fetch origin`
`origin/main` остался `1a015f7513933901e8bb252e94c660e4383b6b0e`.
`ui/ux` создана от этого main. Очистка PR56 сюда не переносилась. Инструкции
пользователя из чата имеют приоритет над старым указанием main в базовом AGENTS.

## Изменения и пофайловая карта

Все изменения — новые файлы. Существующие tracked product/source/CI, historical
approvals, preservation digests и авторский контент не менялись.

| Новые файлы относительно `frontend/prototypes/home/` | Назначение |
| --- | --- |
| `index.html` | Отдельный HTML-вход, noindex, русский язык |
| `main.tsx` | React: навигация, классы/предметы/разделы, поиск, dialogs, темы |
| `style.css` | Раскладка, responsive, focus/reduced-motion, local font faces |
| `theme.registry.json` | Точный публичный registry export выбранной темы |
| `theme.css` | CSS-переменные theme/light/dark из экспорта |
| `vite.config.mjs` | Изолированный Vite, read-only каталог опубликованных источников |
| `env.d.ts` | Типы виртуального каталога |
| `tsconfig.json` | Проверка типов прототипа |
| `playwright.config.ts` | Отдельный Chrome-прогон 360/768/1440 |
| `home.spec.ts` | Проверки сценариев, overflow, focus, themes, screenshots |
| `fonts/inter-latin.woff2` | Локальный Inter, Latin, Google Fonts v20 |
| `fonts/inter-cyrillic.woff2` | Локальный Inter, Cyrillic, Google Fonts v20 |
| `fonts/OFL.txt` | Официальная лицензия Inter |
| `README.md` | Запуск, источники, атрибуция и ограничения |

Дополнительный новый файл — этот `docs/audits/ui-ux-home-prototype.md`.

Экспорт https://tweakcn.com/r/themes/cmluajfgz000004l5afke7znm получен
22.10.2026. Палитра не восстанавливалась по картинке. Структура адаптирована по
https://maize-secure-26235742.figma.site/; атрибуция Ayush Kumbhar’s team / CC BY 4.0
есть в прототипе и README. Исходный код/иллюстрации Figma не копировались.
Inter — fonts.gstatic.com, лицензия — google/fonts/ofl/inter/OFL.txt;
внешние font requests в браузере не нужны.

Стек: существующие React 19.2.8, Vite 7.3.7, TypeScript 5.9.3,
Playwright 1.58.2. Локальный Node v24.19.0, npm 11.17.0.
Новых зависимостей/lock edits нет. CSS-переменные работают с обычными React
компонентами; Tailwind, shadcn и Next.js не устанавливались. Product SSG не менялся.

## Проверки

Из Git root, кроме явно указанного cwd:

- `node frontend/node_modules/typescript/bin/tsc -p frontend/prototypes/home/tsconfig.json`:
  PASS, exit 0; повтор после accessibility fix.
- `node frontend/node_modules/vite/bin/vite.js build --config frontend/prototypes/home/vite.config.mjs`:
  PASS, exit 0; повтор после последнего code fix. Build — `frontend/.cache/home-prototype-build/`.
- cwd `frontend/`: `node node_modules/@playwright/test/cli.js test --config prototypes/home/playwright.config.ts`:
  финальный PASS, exit 0, **12 passed**, 360/768/1440, retries 0, skipped 0.
  Проверены все классы/предметы, длинные заголовки, document overflow;
  раздел/ссылки тем/Escape/возврат focus; поиск/empty/reset/filter;
  две темы/local fonts/отсутствие failed requests/screenshots.
- Первый browser прогон: 1 FAIL / 11 PASS. На телефоне скрытый «класс» исчезал
  из accessible name. Исправлено `aria-label={item.title}`. Affected повтор:
  4 PASS; финальный полный повтор: 12 PASS.
- `scripts/check_migration_preservation.py`, bundled Python 3.12 с
  `PYTHONPATH=var/docs-cleanup/venv/Lib/site-packages`: PASS, exit 0,
  preserved_files 843, explicit_dispositions 1627. Baseline hashes не менялись.
- `git diff --check`: PASS, exit 0.
- Визуально просмотрены desktop light/dark и screenshots 360/1440.
  Browser JSON/results/screenshots — в игнорируемом `frontend/.cache/`.

Общая portable проверка `scripts/verify_repo.py --profile pure` на базовом main
не PASS. Bundled Python без пакетов первоначально дал 2/6 PASS (нет jsonschema).
С существующими locked site-packages: **5/6 PASS**, одна ошибка старого Harness
manifest suite при подготовке pinned oracle: локальный git clone вернул exit 128.
Лог — `var/home-prototype-pure.log`. Проверки не ослаблялись; Harness не удалялся.
Полный target/PostgreSQL/install/recovery/combined gate не запускался:
изолированный прототип без product runtime/schema/SSG changes.
Production readiness, CI PASS и отдельное ревью не заявляются.

## Передача

Просмотр: http://127.0.0.1:5173/, server bound to loopback. Вход/уроки ведут на
существующий local site :8121; его доступность/auth flow не проверялись.
Нет fake mastery/XP/tests/reviews. Default — 7 класс / алгебра для сравнения с
референсом. Состояние только в памяти. Ориентир 60/30/10 — баланс композиции,
не измеренные доли пикселей. Размеры текста, плотность, начальный экран и
направление требуют оценки пользователя.

Следующий этап — обратная связь и отдельное ревью. Product `/`, SSG/no-JS,
auth и rollout требуют нового поручения. Автоматического merge/приёмки/следующей
задачи нет. Проверяемый candidate — commit этой пофайловой карты и исходников;
его SHA фиксируется при передаче отдельно, без самоссылки файла на собственный SHA.
