# Главная, каталог и учебный пилот MathStart

Утверждённый Professional Theme + QraftHive. Общий UI-контракт:
[docs/ux/shared-ui-contract.md](../../../docs/ux/shared-ui-contract.md).
Это самостоятельный React/Vite-прототип, не основной FastAPI/React SSG runtime.

## Запуск

Из frontend с установленными locked dependencies:

```powershell
node node_modules/vite/bin/vite.js --config prototypes/home/vite.config.mjs
```

Не запускать второй сервер на занятом 5173. npm run dev открывает другую оболочку.

- Главная: http://127.0.0.1:5173/
- Каталог: http://127.0.0.1:5173/materials.html
- Пилот: http://127.0.0.1:5173/materials/8-algebra-32
- Прежние /quadratic.html и длинный slug перенаправляются на новый адрес.

## Общие источники

- frontend/src/shared/styles/theme.css — Professional light/dark tokens;
  base.css и fonts/ — reset, шрифты и OFL.
- frontend/src/shared/ui/brand.tsx и use-site-theme.ts — логотип и theme state.
- frontend/src/shared/lesson/ — оболочка, заголовок, содержание, самопроверка,
  навигация, диаграммы, рендер материала, общие lesson CSS и предметный график.
- frontend/src/shared/routing/material-routes.mjs — формат и явный реестр URL.

Все три страницы используют общую тему/базу/логотип. style.css, landing.css и
shell.css содержат специфику главной/каталога; их компоновка не заменяется уроком.
site-shell.tsx остаётся адаптером прежней оболочки этих двух страниц и re-export
общего Brand/theme hook для совместимости. Новым страницам следует импортировать
их непосредственно из shared.

## Согласованное поведение

Панель содержания отдельно от белой светлой шапки; активная строка выделена
только фоном, номера с точками. Самопроверка открывается только кнопкой справа,
ответ на белой подложке light. Соседние темы показываются компактными кнопками
без названий под ними. Подвал — логотип, классы и навигация, без кнопки Наверх.
Анимации и reduced motion определены в общем CSS; плавный reset графика и tap
без изменения точки от swipe находятся в QuadraticGraph.

Весь учебный текст, MathML, таблицы и authored SVG читаются из canonical curriculum.
Повторный recap и Далее исключены только из проекции урока, не из источника.
Текущий adapter lesson-source.mjs и quadratic.html необходимы до SSG-интеграции.
Старые page.css/page.js используются основной публикацией и не удаляются.

## Оставшиеся prototype adapters

| Файл | Назначение |
| --- | --- |
| index.html / landing.tsx | Главная |
| materials.html / main.tsx | Каталог с чтением canonical inventory |
| quadratic.html / quadratic.tsx | Композиция и подключение пилота |
| lesson-source.mjs / .d.mts | Build-only чтение исходного HTML |
| vite.config.mjs / env.d.ts | Virtual catalogue/lesson, dev/preview aliases и build inputs |
| theme.registry.json | Атрибуция исходной темы, не runtime-зависимость |

## Границы и проверки

Остальные уроки и настоящий кабинет продолжают вести на локальный runtime 8121.
Форма email/password главной — только preview: не отправляет и не сохраняет
данные, не создаёт сессию. Серверная интеграция identity — отдельная задача.
Чтение не повышает mastery; Tutor/Progress/интеллектуальная практика не имитируются.

Тесты: home.spec.ts, landing.spec.ts, quadratic.spec.ts, lesson-accessibility.spec.ts,
lesson-regressions.spec.ts и frontend/tests/quadratic-*. Обязательны сохранность
материала, математика, gestures, фокус, оба theme, zoom и reduced motion.
Финальная проверка до extraction: docs/audits/lesson-fixes-react-2026-10-23.md.
Новые результаты extraction хранятся отдельно; прежние manifests не переписывать.

Источник темы и лицензии: [theme-baseline](../../../docs/ux/theme-baseline.md).
Шаблон готов к последующей интеграции, но текущий prototype build не является
production-публикацией. AGENTS/скилы и Git-операции main — следующий этап.
