# Общие компоненты учебных страниц

Правила и API: [shared UI contract](../../../../docs/ux/shared-ui-contract.md).

Компоненты экспортируются из index.ts. Общие CSS — lesson.css и lesson-shell.css.
Тема/шрифты — ../styles, Brand/theme hook — ../ui, назначенные URL — ../routing.
Здесь не должно быть импортов из prototypes/home, Vite virtual modules или backend.
QuadraticGraph и quadratic-math являются предметным виджетом, а не универсальным
рендером графиков всех уроков. Новый виджет требует своего проверяемого контракта.

Нынешний потребитель — quadratic.tsx в прототипе. Подключение к FastAPI/React SSG
публикации выполняется отдельно; не удалять canonical content или build adapter
до появления проверенной замены.
