# Редактирование уроков

Откройте нужную тему через [указатель curriculum](../curriculum/INDEX.md).
Учебный материал хранится в `content.json`, метаданные и учебная принадлежность
в `lesson.json`. Для новой темы используйте действующие модели документа и
компоненты из [стандарта уроков](frontend/lesson-migration.md). Темы используют
общий renderer в `frontend/src/shared/lesson/`. Предметные интерактивы находятся
в `frontend/src/features/lesson-interactives/`.

- Сохраняйте section IDs, якоря, SVG/MathML, подписи и решения. Для внутренних
  ссылок используйте адрес из `site_content/material-routes.json` с нужными
  query и fragment. Порядок отображения темы не определяет её адрес.
- Используйте `selfCheck` для авторской самопроверки. Ответы остаются доступны
  гостям, без записи учебного прогресса.
- Регистрируйте изображения и PDF в `site_content/media.json` и сохраняйте
  проверяемые байты в `site_content/media/`.
- Для локальных правок используйте [штатный host-dev](local-development-host.md).
  Изменение маршрута, каталога или версии опубликованного материала требует
  [согласованной подготовки Content](../backend/READ_RUNTIME.md#обновление-публичного-выпуска-ms-t011).

Предыдущий HTML и карта пофайлового вывода доступны из [MS-T011](../skills/tasks/t011-rollout-finalization/SKILL.md).
