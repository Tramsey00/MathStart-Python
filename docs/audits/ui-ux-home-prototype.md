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

## Итерация по обратной связи: меню, классы и фон

22.10.2026, исходный HEAD `f6ac78b6186f691ebe6bc844f80e941f197883ac`, чистая `ui/ux`.
Пользователь попросил сворачивание списка, новый выбор класса, удаление лишних
точек, различимые фон/карточки и более читаемое левое меню при сохранении темы.

Изменены только `main.tsx`, `style.css`, `home.spec.ts`, README прототипа и этот
audit. `theme.registry.json`/`theme.css`, контент, зависимости и product routes
не изменены. CSS дополнительно развёрнут из сжатых строк для чтения/ревью.

- Выбор предмета отделён от состояния раскрытия. Повторное нажатие сворачивает
  список без смены предмета; `aria-expanded`/уникальный `aria-controls` отражают
  состояние, hidden содержимое действительно исключено из раскладки/навигации.
- Native select заменён React-панелью 3×2. Все классы видны, выбранный отмечен.
  Tab/Enter/Space, повторный click, Escape, outside pointer и focus-leave работают;
  Escape/выбор возвращают focus. Мобильный Escape сначала закрывает picker.
- Рабочий фон — secondary/background с малозаметной точечной сеткой. Карточки
  и меню выделены поверхностями, границами/тенями из темы. Меню шире; текст
  разделов крупнее и использует sidebar-foreground. Light/dark поддержаны.
- Декоративные точки бренда/h1 и финальные точки кратких UI-подписей убраны.
  Внутренняя пунктуация и авторские названия тем не менялись.
- Экран остаётся экспериментальной главной в виде учебного каталога; отдельная
  презентационная главная и выбор окончательного начального экрана не утверждены.

Повторены TypeScript, standalone Vite build и browser matrix. Набор расширен до
18 сценариев на 360/768/1440 с проверкой сворачивания, закрытия picker, смены
класса и focus. Первый расширенный прогон: 16 PASS / 2 FAIL из-за неверного
test locator после штатного закрытия всего мобильного меню при клике на его
навигационную ссылку. Outside-click проверка исправлена на нейтральный заголовок
внутри меню. Эти failures не маскировались retries/skips.
Итоговый прогон: **18 PASS**, exit 0, retries/skipped/flaky 0; TypeScript и Vite
build — PASS, exit 0. `git diff --check` — PASS. Candidate SHA фиксируется в PR.
Общие runtime ограничения предыдущей итерации остаются; несвязанные suites не
перезапускались. Отдельное ревью и человеческая приёмка остаются незавершёнными.

## Итерация: меньше рамок и вспомогательных блоков

22.10.2026, чистая `ui/ux`, исходный HEAD `1a9ac2b`. Пользователь попросил убрать
все элементы первых трёх скриншотов, уменьшить блочность и исправить знак математики.

Изменения — `main.tsx`, `style.css`, `home.spec.ts`, README прототипа и этот audit:

- Удалены отметка «Пример нового дизайна», sidebar-tip «В своём темпе», весь
  блок других предметов и прежний footer со служебными подписями. Атрибуция
  Figma остаётся в README/источниках проекта, не выводится прежним footer.
- Hero без фоновой карточки/рамки/тени. Разделы — открытая двухколоночная
  раскладка с тонкими нижними разделителями (на телефоне одна колонка).
  Убраны декоративная сетка фона, обрамление счётчиков, лишние границы/тени.
- Панель классов заменена открытым рядом шести кнопок с подчёркиванием
  выбранного. Desktop — sidebar, mobile — также над заголовком. Удалены
  старые popover effects, обработчики и неиспользуемые CSS-правила.
- Математический ± заменён собственным SVG с центровкой в общем icon slot.
  Предметы по-прежнему сворачиваются. Поиск, темы и переходы сохранены.
- Исходные theme export/CSS, зависимости, product routes, auth, публикация,
  авторский контент и исторические receipts не менялись.

Проверки на финальном коде: TypeScript PASS; Vite build PASS;
Playwright **18/18 PASS**, 360/768/1440, retries/skipped/flaky 0, exit 0.
Popover-сценарий заменён сценарием нового UI: шесть видимых классов,
mouse/Tab/Enter, сохранение focus, смена данных, синхронный mobile выбор.
Также проверяется отсутствие удалённых блоков. Остальные пользовательские
сценарии сохранены. Light/dark и mobile screenshots просмотрены, SVG проверен
в браузере на 5 классе. `git diff --check` — PASS.
Полный product runtime не запускался; прежние ограничения этой ветки остаются.
Окончательный дизайн/главная ещё не приняты пользователем.

## Итерация: различимость поверхностей без отдельных карточек

22.10.2026, исходный чистый HEAD `32c35f0`, та же `ui/ux`. После снятия рамок
пользователь отметил, что элементы сливаются. Изменён только `style.css` и этот
audit: весь каталог получил единую поверхность card/card-foreground с внутренними
отступами. У отдельных разделов рамки и тени не возвращались. Заголовкам явно
задан card-foreground, номера и переходы выделены primary, описание предмета
контрастнее. На 360 px внутренние отступы меньше. Использованы существующие
tokens темы; registry export, контент, JSX/поведение, dependencies и routes прежние.

Проверки: standalone Vite build PASS, 18/18 browser scenarios PASS на
360/768/1440, retries/skipped/flaky 0, exit 0; `git diff --check` PASS.
Просмотрены light/dark desktop и mobile screenshots. TypeScript и общие product
suites повторно не запускались: изменения CSS и отчёта, без изменения typed code
или product runtime. Предыдущие ограничения full verification остаются.

## Итерация: содержание верхнего блока и небольшие разделители

22.10.2026, исходная чистая `ui/ux`, HEAD `44708f4`. Пользователь отметил пустоту
hero и разрешил небольшое разделение учебных разделов.

Изменены `main.tsx`, `style.css`, `vite.config.mjs`, `env.d.ts`, `home.spec.ts`,
README прототипа и этот audit. Сохранены theme export, контент, product routes,
backend и зависимости. Нового authored учебного материала не создавалось.

- Вместо одинакового для всех предметов графика — первая тема выбранного курса:
  фактические название, авторское вступление и ссылка. Порядок определяется
  каталогом; это не оценка знаний/персональная рекомендация. Общие слоганы убраны.
- Read-only build plugin дополнительно читает `ms-subtitle` первого урока
  каждого курса и выдаёт plain text с декодированием обычных/numeric entities.
  React экранирует текст; raw HTML/script/styles не вставляются. При отсутствии
  подходящего вступления блок опускается. Проверены 12 исходных курсов.
- Hero использует ширину двух текстовых колонок; на телефоне они идут подряд.
  Мёртвые правила декоративного графика удалены.
- Между соседними колонками каталога тонкая вертикальная линия, существующие
  горизонтальные разделители сохранены. Hover — слабый secondary tint, без
  рамки/тени каждой карточки. На телефоне вертикальная линия отключена.
- Browser suite расширен сценарием настоящего вступления/ссылки и смены курса.
  Первый прогон: 18 PASS / 3 FAIL из-за старого test locator «первый h2»:
  первым h2 теперь является заголовок урока. Locator поиска исправлен на
  конкретное доступное имя «Найденные темы», проверки не ослаблялись.

TypeScript и standalone Vite build — PASS, exit 0. Финальный browser matrix:
**21/21 PASS**, 360/768/1440, retries/skipped/flaky 0, exit 0. Просмотрены
desktop/mobile/light/dark screenshots. `git diff --check` PASS.
Существующие full runtime ограничения ветки сохраняются.
