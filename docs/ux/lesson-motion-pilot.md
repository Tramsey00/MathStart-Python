# Анимации учебной страницы, 2026-10-23

Основание: пользователь согласовал структуру и попросил плавное открытие/закрытие
содержания, hover кнопок и раскрытие решений, с исследованием примеров в интернете.
Изменения локальны для lesson-preview-page, без новых библиотек, агентов и скилов.

## Поведение

- Нативный dialog сохранён. @starting-style и discrete transitions для display /
  overlay удерживают панель и backdrop до завершения выхода. Открытие 280 ms,
  закрытие 220 ms; панель сдвигается слева, затемнение меняется вместе с ней.
  Без поддержки этих CSS-возможностей штатное закрытие dialog не блокируется.
- Ответ раскрывается CSS grid 0fr/1fr за 240 ms с изменением opacity. Внутренний
  clip допускает естественную высоту длинного решения. Closed content inert и
  aria-hidden, после окончания сворачивания visibility:hidden. Отдельная кнопка
  сохраняет aria-controls/expanded; нажатие вопроса ответ не открывает.
- Фон, цвет и рамка кнопок плавно меняются за 160 ms. Стрелки переходов смещаются
  по направлению на 3 px при hover, нажатие даёт scale .98. Старый hover входа
  сохранён. Формулы, график и параграфы не получают анимаций появления.
- prefers-reduced-motion отключает transitions/animations и смещения в обоих
  режимах. Декоративное движение не требуется для открытия или закрытия.

## Источники

- https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog#animating_dialogs
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/interpolate-size
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion
- https://m1.material.io/motion/duration-easing.html
- https://m3.material.io/styles/motion

interpolate-size не выбран из-за ограниченной поддержки. Базовые длительности
подобраны для этой страницы; это не буквальная реализация M3 spring system.

## Фактический просмотр

Chrome 360/1440 × 900, normal/reduced motion; свежие screenshots и observations
в frontend/.cache/lesson-motion-preview/. При обычном движении обнаружены активные
transitions при открытии/закрытии, после выхода dialog display:none, focus вернулся
на trigger. Для ответа после открытия height > 0 / inert false, после закрытия
height 0 / inert true / visibility hidden. При reduced motion активных transitions
нет, конечные состояния те же. На этих размерах нет pageerror и overflow.
Просмотрены screenshots открытых ответов desktop/phone. Это целевой браузерный
просмотр, не полный тестовый прогон: Vitest, TypeScript, build, Playwright suite,
Safari, физический телефон и target runtime в этом проходе не запускались.
HEAD 192d0fc315e35644eeb9bb713f58d7d15afb34a0, текущий кандидат dirty ui/ux.
Предыдущие результаты не подтверждают новую ревизию. Без коммита и push.

## Фиксация общих компонентов

Текущий контракт: [shared-ui-contract](shared-ui-contract.md). Описанные выше
пути prototypes/home/lesson.css и lesson-routes.mjs относятся к прежнему
кандидату; общие стили/URL перенесены в frontend/src/shared/lesson/lesson.css
и frontend/src/shared/routing/material-routes.mjs. Эта запись сохранена как
история решений, а не действующая инструкция копировать прототип.
