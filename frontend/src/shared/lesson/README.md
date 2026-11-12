# Общие компоненты учебных страниц

Правила и API: [shared UI contract](../../../../docs/ux/shared-ui-contract.md).

Компоненты экспортируются из index.ts. Общие CSS — lesson.css и lesson-shell.css.
Тема/шрифты — ../styles, Brand/theme hook — ../ui, назначенные URL — ../routing.
Здесь не должно быть импортов из prototypes/home, Vite virtual modules или backend.
QuadraticGraph и quadratic-math являются предметным виджетом, а не универсальным
рендером графиков всех уроков. Новый виджет требует своего проверяемого контракта.

Основной потребитель — React/SSG приложение frontend/src/app/ и shared/lesson/lesson-page.tsx.
Учебные документы берутся из curriculum через Content; в dev опубликованные
React-темы используют текущий content.json через dev-only проекцию.
Прототип не является текущим сайтом. Материалы и контракты публикации сохраняются.
