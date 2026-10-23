# Фиксация общих компонентов и очистка UI-прототипов

23 октября 2026. Пользователь принял структуру/стиль страницы и попросил закрепить
общие компоненты, правила адаптации и URL, удалить промежуточные файлы. Слияние
main, новая ветка и работа над AGENTS/skills обозначены следующим этапом.

## Реализация

Текущий контракт: [shared-ui-contract](../ux/shared-ui-contract.md).

- Professional Theme и шрифты/OFL перенесены из prototypes/home в
  frontend/src/shared/styles. Font faces и базовые стили выделены в base.css;
  prototype style.css импортирует их, а не содержит копию. Все три страницы
  используют одну тему. Байты theme/fonts/licenses сохранены.
- Brand и useSiteTheme выделены в shared/ui; прежний site-shell реэкспортирует
  их для совместимости. Brand использует низкую специфичность базовых правил,
  чтобы контекстные размеры mobile/оболочек продолжали работать.
- Общий lesson.css перемещён в shared/lesson. Убраны устаревшие стили summary,
  старых reveal-actions и невидимых названий тем. lesson-page — публичный класс
  страницы; lesson-preview-page сохранён совместимым алиасом. Flex-контейнер
  принадлежит LessonPageShell, а не прототипному #root.
- Добавлены LessonHeading с параметрами breadcrumb/title/subtitle и index.ts
  общих компонентов. Пилот использует их; подписи класса и предмета читаются
  из каталога. Оформление и поведение компонентов не переделывались.
- Реестр URL перенесён в shared/routing/material-routes.mjs. Общий formatter
  проверяет grade/subject/number, реестр проверяет дубликаты, lookup не создаёт
  адреса незарегистрированных тем. Назначение /materials/8-algebra-32 сохранено.
  Сортировка каталога не участвует в построении URL. Три новых unit cases
  проверяют формат, сохранение назначенного пути и отказ для неверных данных.
- README прототипа обновлён по фактической реализации; прежние UX-записи
  помечены историческими и ссылаются на текущий контракт.

Общие части предназначены для последующего переиспользования. Новые страницы
собираются из подходящих компонентов и передают контекст данными. Основной
runtime и его существующие Button/Field/SiteShell не переписаны без интеграции.
Canonical curriculum, математические вычисления, graph gestures/reset, API и
identity не менялись. Рабочие quadratic.html, lesson-source.mjs и Vite inputs
остались: пока они обслуживают единственный действующий согласованный пилот.

## Очистка

[Cleanup manifest](shared-ui-finalization-2026-10-23/cleanup-manifest.json):
удалены **117** временных объектов, **4562** файла, **427409936 bytes** (~407.6 MiB).
Это черновые снимки home/landing, промежуточные quadratic/lesson helper runs,
копии browser profiles и корневой node_modules, содержавший только .vite cache.
Удаление выполнялось нативным PowerShell по проверенным абсолютным путям внутри
workspace, с отказом на reparse points. Никаких glob-delete исходного дерева.
Добавлено игнорирование /node_modules/ для предотвращения повторного попадания
корневого кеша в Git. Последние build/test caches могут создаваться вновь.

Итоговые и исторические аудиты, их source manifests и raw evidence в docs/audits,
critique-записи .impeccable, authored content/media, лицензии и рабочие зависимости
frontend/node_modules сохранены. Это не удаление всего каталога prototypes:
он ещё нужен до подключения основного React/SSG route.

## Проверка нового кандидата

- npm test: **203/203 PASS**, 25 test files, без skipped. Сохранность текста,
  ответов/MathML/таблиц/authored SVG проверяется существующим source suite.
- npm run typecheck: **PASS**, существующие API/staff checks сохранены.
- tsc -p prototypes/home/tsconfig.json --noEmit: **PASS**.
- Vite prototype build: **PASS**, 50 modules.
- Полный настроенный prototype Playwright: **92/92 PASS**, 200.1 s,
  expected 92 / skipped 0 / unexpected 0 / flaky 0, retries=0.
  Главная, каталог и урок на четырёх ширинах, обе темы, gestures, контраст,
  анимации/reduced motion, настоящий Chrome zoom и URL/alias/reload.
- git diff --check: **PASS**. Новых UI-зависимостей нет.
- [Preservation](shared-ui-finalization-2026-10-23/preservation.json) подтверждает
  неизменность theme/fonts/OFL и исходников quadratic-math/quadratic-graph.

Сравнены свежие до/после снимки home/catalogue/lesson на 360/1440, light/dark.
8 из 12 пар совпадают побайтно по RGB pixels. Оставшиеся отличия локализованы
в областях theme/hover контролов и полей формы; captures не ожидали окончания
всех цветовых transitions, поэтому полный pixel-equality не заявляется.
Просмотрены сопоставленные рендеры: структура и размеры чтения сохранены.
Численные показатели контраста и оба theme дополнительно покрыты Playwright.

[Command results](shared-ui-finalization-2026-10-23/command-results.json),
[Vitest JSON](shared-ui-finalization-2026-10-23/vitest.json),
[Playwright JSON](shared-ui-finalization-2026-10-23/playwright.json),
[сравнение captures](shared-ui-finalization-2026-10-23/visual-comparison.json),
[скриншоты](shared-ui-finalization-2026-10-23/screenshots/).
Первичная попытка pixel comparison с Pillow не выполнилась: библиотека отсутствует.
Зависимости ради этого не устанавливались; сравнение выполнено bundled PNG decoder
Playwright. Промежуточный перенос Brand сначала перекрывал mobile font size;
специфичность исправлена до итоговых typecheck/build/unit/browser прогонов.

Кандидат: dirty ui/ux, HEAD 192d0fc315e35644eeb9bb713f58d7d15afb34a0.
[Новый manifest 882 inputs](shared-ui-finalization-2026-10-23/implementation-sha256.json)
задаёт treeFingerprint d8c05a94d51ecb4b42e3b850a697fd080823dfdb401f2928985e87f6a399fc70.
Предыдущие отчёты/хеши не переписаны и относятся к своим кандидатам.

Ограничения: Chrome с синтезированным touch; без physical phone/Safari/live SR.
Полный target/production gate, standalone built preview, FastAPI/SSG-интеграция
не выполнялись. Commit/push/main merge/branch switch не выполнялись.
AGENTS.md и установленные skills в этой задаче не редактировались.
