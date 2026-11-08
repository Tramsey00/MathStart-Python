---
name: mathstart-t003-grade-5
description: Выполнить MS-T003 — Полностью перенести 5 класс; только по отдельному поручению из реестра MathStart.
---

# MS-T003 — Полностью перенести 5 класс

> Решение пользователя 08.11.2026: только перенос по принятому стандарту
> и ручная приёмка. Автоматические проверки, smoke и gates не запускать;
> результат прогонов — NOT_RUN_BY_USER_REQUEST. Штатные guards не отключать.

Зависимости: MS-T002A (ACCEPTED 08.11.2026). Остальные классы MS-T003–MS-T008
не блокируют эту задачу; допускается параллельная работа разных исполнителей.
Статус — в [реестре](../../../docs/tasks/INDEX.md).
Карточка описывает будущий результат, не выдаёт наличие прототипа за готовность.

## Результат и входы

Все 35 опубликованных тем grade=5-klass в docs/tasks/lesson-inventory.json, по всем перечисленным предметам и разделам. Записи inventory — полный scope, не выборка удобных уроков.

Прочитай [архитектуру](../../../ARCHITECTURE.md), [стандарт переноса](../../../docs/frontend/lesson-migration.md),
[UI contract](../../../docs/ux/shared-ui-contract.md) и [проверки](../../../docs/frontend/testing-policy.md).
Не перечитывай прежние ТЗ/аудиты: они не являются входом этой задачи.

## Объём работы

1. Открыть весь inventory для 5-klass и сверить актуальный Content source. Изменившийся перечень сначала согласовать явно.
2. Выполнять перенос по разделам, используя один стандарт и общие блоки. Новый повторяемый блок добавлять один раз.
3. Назначить ещё null адреса однократно через Content registry, не из display order на каждом build.
4. Сохранить связи с темами ещё не перенесённых классов через общий resolver.
5. Сверить исходники и перенесённый материал всех 35 тем; передать пользователю для ручного просмотра, включая каждый особый график. Автоматизированный browser QA не запускать.
6. Удалять заменённые старые assets с пофайловым disposition после проверки потребителей. Частичный раздел не считать классом.
7. Передать полный список migrated/not-migrated; при готовности not-migrated пуст.

## Приёмка

Все 35 тем класса собраны через новый renderer, имеют устойчивые URL/redirects и доступны из каталога; ни одна тема/формула/таблица/ответ/media/anchor не потеряна; каждый уникальный interactive перенесён и вручную проверен, пользователь принял cohort.

Отдельно фиксируй реализацию, статическое review, ручную приёмку пользователя
и merge. Полноту тем/текста/формул/таблиц/ответов/media/anchors сверяй по исходникам;
не сокращай материал ради скорости. Ручной просмотр и приёмку не называй выполненными,
пока пользователь их не подтвердил; сообщи о непроверенных интерактивах.
Tests, typecheck, Playwright, backend suites, smoke, source/docs/preservation gates
и новые скрипты QA не запускать. Проверки: NOT_RUN_BY_USER_REQUEST, не PASS.
Не запускать release build после каждого урока. Необходимую подготовку изменённых
Content inputs выполнять по [инструкции](../../../docs/local-development-host.md)
со штатными планами/guards; это не разрешение на дополнительные QA-прогоны.
Результат — краткий список migrated/not-migrated, адресов и ограничений в карточке/PR;
временные outputs только в ignored var/ или frontend/.cache/.

## Параллельная работа

Работай с материалами своего класса. В общем `site_content/material-routes.json`
добавляй только назначения своих тем, сохраняя чужие записи и закреплённые номера.
Правку общего renderer, конвертера, lesson-компонентов или стилей сначала согласуй
с другими исполнителями; общую необходимую правку интегрировать отдельно и получить
в ветки классов. Не копируй shared-компоненты в частный вариант класса.
Используй свою локальную БД/config. Перед интеграцией PR учти обновления main
и разреши конфликты с сохранением всех тем. Порядок merge определяет пользователь.

## Границы

Сохрани чужой dirty tree, учебную математику и пользовательские данные. Не меняй
платформу публикации вне необходимых документированных adapters. Не трогай
protected acceptance DB. Не запускай следующую карточку автоматически. Merge,
production и provider/security решения требуют отдельного поручения человека.

## GitHub и ветка

Перед реализацией создать или продолжить GitHub Issue этого задания и отдельную ветку от актуального origin/main после fetch; без codex/ и /codex. Изменения передаются через PR со ссылкой на Issue. Не создавать дубли и не выполнять merge/закрытие Issue автоматически. Подробности — AGENTS.md.

## MS-T003 — рабочий результат 08.11.2026 (не готов к review)

Issue: https://github.com/Tramsey00/MathStart-Python/issues/60
Baseline: `cf8690794644fe5f90c42d5aae2c1c5f7ca9b888`.
Branch: `ms-t003-grade5-migration`, isolated worktree in ignored `var/worktrees/`.
Host-check stays on `ui/ux`; its configuration, database, publication and processes were not changed.

Implementation: IN_PROGRESS; source comparison: INCOMPLETE; independent review:
NOT_STARTED; human acceptance: PENDING; merge: NOT_PERFORMED.
Tests/typecheck/Playwright/backend/smoke/source/docs/preservation gates/release build:
NOT_RUN_BY_USER_REQUEST. Conversion commands below are document authoring, not QA.

### Authoring completed so far

29 new `content.json` drafts generated; existing /materials/5-math-12 pilot reused
unchanged. Drafts are NOT activated: lesson.json renderer flags and route assignments
remain unchanged until the full source comparison and resolution of shared blockers.
No draft is claimed migrated or runtime-ready. Frozen HTML/media were not changed or
removed. Commands: existing `node frontend/scripts/convert-lesson.mjs <directory>`;
for five fraction lessons, explicit authored MathML prepared in ignored var/tmp and
passed through the same converter. The root-checkout converter/math helper are byte
identical to the baseline (Git diff showed no difference).

Explicit math authoring: fraction operands `a · n`, `b · n`, `a : n`, `b : n`,
`a · c + b`, `a + b`, `a − b`, `?`, `1 · 2`, `3 · 2`, `2 · 3`, `4 · 2`,
`8 · 3`, `20 · 5`, `5 · 2`, `7 · 5`, `6 : 3` use MathML mfrac/mrow/mi/mn/mo/mtext.
No arithmetic was evaluated or simplified; shared math helper unchanged.
In «Признаки делимости», the second h2 inside an existing section is authored as h3
in the document (text «Признаки делимости на 2, 5 и 10» retained). Its existing
outer section and anchor are preserved; original HTML remains frozen.
All prerequisite sections and instructional blocks after self-check are excluded by
the accepted standard, not a new content decision. Per-topic exact exclusion/anchor
mapping and full source comparison remain to be completed before review.

### Shared blockers — approval pending, no shared changes made

1. `frontend/scripts/convert-lesson.mjs`: permit authored SVG `marker-start`, `dy`,
   and passive `data-hidden-edges` without removing attributes or altering geometry.
2. `backend/content/sources.py`: allow only numeric SVG tspan/text `dy` to preserve
   the triangle drawing; retain existing active-markup, URL and publication guards.
   Backend already permits marker-start and data-* attributes.
3. No renderer, CSS, schema migration or private copy of a shared component proposed.

Affected topics: formulas/equations (marker-start), triangle area (dy), all three
rectangular-parallelepiped topics (data-hidden-edges). Existing converter cannot
produce these documents. Removing the attributes would violate SVG preservation.
The converter/validator are shared with MS-T005; coordinate and integrate the shared
change separately before completing the class. No contact with Ilya was sent.

### Next steps

Resolve shared changes with Vladimir/Ilya; finish these five documents; complete
per-topic source/media/math/answer/anchor comparison; activate only reviewed class-5
renderer metadata and permanent routes; prepare Content through the approved plans
and guards in a separate environment; commit/push and open Draft PR linked to #60.
Runtime/manual visual review is not performed; addresses below are proposed numbers,
not published URLs. Issue is open. Draft PR has not been opened because the class is
not complete and the user requested it after completion.

| № | Тема | Исходник | Статус | Адрес |
| --- | --- | --- | --- | --- |
| 1 | Числовые и буквенные выражения | `curriculum/5-klass/matematika/01-naturalnye-chisla/01-5-klass-chislovye-i-bukvennye-vyrazheniya` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-1 |
| 2 | Определение координатного луча | `curriculum/5-klass/matematika/01-naturalnye-chisla/02-5-klass-koordinatnyy-luch` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-2 |
| 3 | Округление чисел. Прикидка и оценка результатов вычислений | `curriculum/5-klass/matematika/01-naturalnye-chisla/03-5-klass-okruglenie-chisel-prikidka` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-3 |
| 4 | Законы арифметических действий. Вычисления с многозначными числами | `curriculum/5-klass/matematika/01-naturalnye-chisla/04-5-klass-zakony-arifmeticheskih-deystviy` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-4 |
| 5 | Сравнение натуральных чисел | `curriculum/5-klass/matematika/01-naturalnye-chisla/05-5-klass-sravnenie-naturalnyh-chisel` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-5 |
| 6 | Решение текстовых задач арифметическим способом | `curriculum/5-klass/matematika/01-naturalnye-chisla/06-5-klass-tekstovye-zadachi-arifmeticheskiy-sposob` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-6 |
| 7 | Формулы. Уравнения. Упрощение выражений | `curriculum/5-klass/matematika/01-naturalnye-chisla/07-5-klass-formuly-uravneniya-uproshchenie-vyrazheniy` | BLOCKED_SHARED_APPROVAL | /materials/5-math-7 |
| 8 | Математический язык и математическая модель | `curriculum/5-klass/matematika/01-naturalnye-chisla/08-5-klass-matematicheskiy-yazyk-model` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-8 |
| 9 | Делимость натуральных чисел | `curriculum/5-klass/matematika/02-razlozhenie-chisla-na-prostye-mnozhiteli/01-5-klass-delimost-naturalnyh-chisel` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-9 |
| 10 | Признаки делимости | `curriculum/5-klass/matematika/02-razlozhenie-chisla-na-prostye-mnozhiteli/02-5-klass-priznaki-delimosti` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-10 |
| 11 | Простые и составные числа. Разложение натурального числа на простые множители | `curriculum/5-klass/matematika/02-razlozhenie-chisla-na-prostye-mnozhiteli/03-5-klass-prostye-i-sostavnye-chisla` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-11 |
| 12 | Деление с остатком. Понятие обыкновенной дроби | `curriculum/5-klass/matematika/03-obyknovennye-drobi/01-5-klass-ponyatie-obyknovennoy-drobi` | ACCEPTED_PILOT_REUSED | /materials/5-math-12 |
| 13 | Основное свойство дроби. Сокращение дробей | `curriculum/5-klass/matematika/03-obyknovennye-drobi/02-osnovnoe-svojstvo-drobi-sokrashhenie-drobej` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-13 |
| 14 | Правильные и неправильные дроби. Смешанные числа. Понятие, запись и чтение | `curriculum/5-klass/matematika/03-obyknovennye-drobi/03-pravilnye-i-nepravilnye-drobi-smeshannye-chisla-ponyatie-5c2ab626` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-14 |
| 15 | Сравнение обыкновенных дробей | `curriculum/5-klass/matematika/03-obyknovennye-drobi/04-sravnenie-obyknovennyh-drobej` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-15 |
| 16 | Сложение и вычитание обыкновенных дробей и смешанных чисел | `curriculum/5-klass/matematika/03-obyknovennye-drobi/05-slozhenie-i-vychitanie-obyknovennyh-drobej-i-smeshannyh-ee005929` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-16 |
| 17 | Умножение и деление обыкновенной дроби на натуральное число | `curriculum/5-klass/matematika/03-obyknovennye-drobi/06-umnozhenie-i-delenie-obyknovennoj-drobi-na-naturalnoe-ch-ef032d25` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-17 |
| 18 | Нахождение части от целого и числа по его части | `curriculum/5-klass/matematika/03-obyknovennye-drobi/07-nahozhdenie-chasti-ot-czelogo-i-chisla-po-ego-chasti` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-18 |
| 19 | Понятие десятичной дроби. Представление десятичной дроби в виде обыкновенной дроби и наоборот | `curriculum/5-klass/matematika/04-desyatichnye-drobi/01-ponyatie-desyatichnoj-drobi-predstavlenie-desyatichnoj-d-b71f2061` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-19 |
| 20 | Десятичные дроби. Сравнение | `curriculum/5-klass/matematika/04-desyatichnye-drobi/02-desyatichnye-drobi-sravnenie` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-20 |
| 21 | Десятичные дроби. Сложение и вычитание | `curriculum/5-klass/matematika/04-desyatichnye-drobi/03-desyatichnye-drobi-slozhenie-i-vychitanie` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-21 |
| 22 | Десятичные дроби. Умножение | `curriculum/5-klass/matematika/04-desyatichnye-drobi/04-desyatichnye-drobi-umnozhenie` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-22 |
| 23 | Степень с натуральным показателем | `curriculum/5-klass/matematika/04-desyatichnye-drobi/05-stepen-s-naturalnym-pokazatelem` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-23 |
| 24 | Десятичные дроби. Среднее арифметическое, деление на натуральное число | `curriculum/5-klass/matematika/04-desyatichnye-drobi/06-desyatichnye-drobi-srednee-arifmeticheskoe-delenie-na-na-2b7d66e9` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-24 |
| 25 | Десятичные дроби. Деление на десятичную дробь | `curriculum/5-klass/matematika/04-desyatichnye-drobi/07-desyatichnye-drobi-delenie-na-desyatichnuyu-drob` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-25 |
| 26 | Округление десятичных дробей | `curriculum/5-klass/matematika/04-desyatichnye-drobi/08-okruglenie-desyatichnyh-drobej` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-26 |
| 27 | Начальные геометрические понятия: прямая, отрезок, луч, ломаная, прямоугольник | `curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/01-nachalnye-geometricheskie-ponyatiya-pryamaya-otrezok-luc-32a7b967` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-27 |
| 28 | Угол. Измерение углов | `curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/02-ugol-izmerenie-uglov` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-28 |
| 29 | Биссектриса угла. Свойство биссектрисы угла | `curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/03-bissektrisa-ugla-svojstvo-bissektrisy-ugla` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-29 |
| 30 | Треугольник. Площадь треугольника | `curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/04-treugolnik-ploshhad-treugolnika` | BLOCKED_SHARED_APPROVAL | /materials/5-math-30 |
| 31 | Свойство углов треугольника | `curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/05-svojstvo-uglov-treugolnika` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-31 |
| 32 | Геометрические понятия: окружность и круг | `curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/06-geometricheskie-ponyatiya-okruzhnost-i-krug` | DRAFT_SOURCE_REVIEW_PENDING | /materials/5-math-32 |
| 33 | Прямоугольный параллелепипед. Определение, свойства | `curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/07-pryamougolnyj-parallelepiped-opredelenie-svojstva` | BLOCKED_SHARED_APPROVAL | /materials/5-math-33 |
| 34 | Прямоугольный параллелепипед. Развёртка | `curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/08-pryamougolnyj-parallelepiped-razvyortka` | BLOCKED_SHARED_APPROVAL | /materials/5-math-34 |
| 35 | Прямоугольный параллелепипед. Объём | `curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/09-pryamougolnyj-parallelepiped-obyom` | BLOCKED_SHARED_APPROVAL | /materials/5-math-35 |

## Уточнение блокеров и минимальное предложение — 08.11.2026

По прямому указанию Владимира общие изменения НЕ СОГЛАСОВАНЫ. До отдельного
подтверждения не изменять convert-lesson.mjs, backend/content/sources.py, renderer,
components, CSS и math helper. Владимир ожидает ответ Ильи по MS-T005.
Это описание предложения, не реализация и не разрешение на общую правку.

### Первоначальные 11 остановок и текущий статус

Номера соответствуют полному inventory, пути источников приведены в таблице выше.
Линии относятся к frozen body.html baseline cf869079. Конвертер прерывает создание
документа с ошибкой; он не пропускает эти конструкции молча. Первоначальный отказ
показывает первую встретившуюся проблему, а не доказательство отсутствия других.

| № | Тема | Конструкция и строки body.html | Причина | Текущее решение |
| --- | --- | --- | --- | --- |
| 7 | Формулы. Уравнения. Упрощение выражений | line marker-start=url(#ms-arrow-r2-d009-1-0-start), :77; второй marker-start :80 | Атрибут отсутствует в converter allowlist; без него исчезают начальные стрелки размерных линий SVG | BLOCKED_SHARED_APPROVAL; исходный рисунок/атрибуты не удалять |
| 10 | Признаки делимости | Второй h2 в той же секции, :195, «3. Признаки делимости на 2, 5 и 10» | convert() не принимает вложенный h2; основной заголовок секции обрабатывается отдельно | Черновик: подзаголовок h3, тот же текст без цифрового префикса; исходник и внешний anchor сохранены. Общая правка не требуется |
| 13 | Основное свойство дроби. Сокращение дробей | (a · n)/(b · n) :170; (a : n)/(b : n) :175; ?/32 :811 | simpleToken допускает число/одну букву, отклоняет составные операнды и ? | Черновик: явные mfrac/mrow/mi/mo/mtext; без вычисления. Общая правка не требуется |
| 14 | Правильные и неправильные дроби. Смешанные числа. Понятие, запись и чтение | (a · c + b)/c :520 | Составной числитель | Черновик: явная MathML; общий helper не меняется |
| 16 | Сложение и вычитание обыкновенных дробей и смешанных чисел | (a + b)/c :67; (a − b)/c :166; (1 · 2)/(3 · 2) :283 | Составные числители/знаменатель | Черновик: явная MathML; общий helper не меняется |
| 17 | Умножение и деление обыкновенной дроби на натуральное число | (a · n)/b :69; (2 · 3)/7 :156; a/(b · n) :349; 3/(4 · 2) :416; (a : n)/b :447; (6 : 3)/7 :512; 5/(8 · 3) :582 | Составные операнды | Черновик: явная MathML, исходный порядок операций сохранён |
| 19 | Понятие десятичной дроби. Представление десятичной дроби в виде обыкновенной дроби и наоборот | (3 · 2)/(5 · 2) :524; (7 · 5)/(20 · 5) :549 | Составные операнды | Черновик: явная MathML, без сокращения/вычисления |
| 30 | Треугольник. Площадь треугольника | tspan dy=0/dy=30 :71 и :164 | dy отсутствует в converter и backend allowlists; удаление совмещает строки подписи, меняя авторский SVG | BLOCKED_SHARED_APPROVAL |
| 33 | Прямоугольный параллелепипед. Определение, свойства | path data-hidden-edges=true :73, :234 | converter запрещает этот пассивный data-атрибут | BLOCKED_SHARED_APPROVAL; сама пунктирная геометрия задаётся d/stroke-dasharray, атрибут также сохраняется |
| 34 | Прямоугольный параллелепипед. Развёртка | path data-hidden-edges=true :65 | Та же allowlist | BLOCKED_SHARED_APPROVAL |
| 35 | Прямоугольный параллелепипед. Объём | path data-hidden-edges=true :75, :149, :220 | Та же allowlist | BLOCKED_SHARED_APPROVAL |

Итого: 11 первоначальных отказов = 6 разрешённых на уровне документов + 5 текущих
блокеров. Шесть черновиков не являются проверенными/принятыми страницами.

### Точные участки предлагаемой общей правки

`frontend/scripts/convert-lesson.mjs`:
- :16 — allowlist атрибутов; :32–36 — их проверка в convert().
- Минимальное расширение: marker-start только на SVG line со значением локальной
  ссылки `url(#<id>)`, по форме уже используемых fragment ids; dy только на tspan
  с конечным числовым десятичным значением (в этих исходниках только строки 0 и 30);
  data-hidden-edges только на SVG path, строго строка true.
- Не разрешать произвольные data-* в конвертере, произвольные URL, CSS, теги,
  события или неизвестные атрибуты. Проверки активной разметки и href сохранить.
- :15 (tags), :39–47 (семантические узлы), :49–72 (sections/self-check) менять
  не требуется. Вложенный h2 и составные дроби разрешаются authoring-ом документов,
  не ослаблением общих guards и не копией конвертера.

`backend/content/sources.py`, validate_lesson_document → element(), :177–194:
- :180/:183 — текущий allowlist; :184–188 — существующие специальные ограничения;
  :189–194 — общая проверка элемента/атрибутов.
- Добавить dy в допустимые атрибуты только вместе с отдельным ограничением:
  tag=tspan, строка с одним конечным десятичным числом без единиц, списков, URL,
  CSS и экспоненты; в текущем source нужны 0 и 30. Не добавлять dy одной строкой
  в allowlist без проверки значения и владельца.
- marker-start уже разрешён backend (:180), data-* уже разрешены (:191).
  Для них расширение backend не нужно. Новые публикационные bypass/fallback
  и изменения `_safe_lesson_url`, schema/version/DDL не нужны.

Общий renderer уже передаёт attrs в React (source-renderer.tsx, renderNode),
сохраняет SVG/MathML subtree через preserveMarkup. Новые компоненты, CSS, math helper
и дополнительные интерактивы для перечисленных конструкций не требуются.

### Обратная совместимость и пересечение с MS-T005

- Это добавление трёх узких допустимых случаев; существующие допустимые документы
  и алгоритмы конвертации не переписываются. Форма lesson-document-v1 сохраняется;
  отсутствующие атрибуты не получают defaults. Новый renderer_version не нужен.
- Не регенерировать пилоты, 7 класс или весь curriculum. После согласования
  повторно преобразовать только пять остановленных источников 5 класса.
- Существующие опубликованные immutable releases, source digests, DB/config,
  historical receipts, маршруты других классов и авторская геометрия не меняются.
- Илья может менять те же allowlists. Перед реализацией сверить его предложение,
  интегрировать общую правку отдельно по согласованному порядку и получить её
  в ветку класса. Автоматический merge не выполнять. Связь с Ильёй ведёт Владимир.
- Аддитивность установлена чтением кода, runtime-совместимость не проверена.
  Возможные последующие source-specific отказы разбираются отдельно, а не обходятся.
- После разрешения автопроверок отдельно назначаются positive/negative cases для
  новых attrs и существующие пилоты; сейчас эти прогоны не запускать и новые
  QA-скрипты не создавать. Статус всех автопроверок: NOT_RUN_BY_USER_REQUEST.

### Независимая работа с первыми темами

Продолжен разбор содержания первых трёх исходников и общей композиции. Зафиксирована
следующая карта состава; это не результат полной preservation-проверки и не
визуальная приёмка:

| № | Оставленные учебные секции/anchors | Исключения по действующему решению |
| --- | --- | --- |
| 1 | theory; lesson-section-2…lesson-section-6 (самопроверка) | lesson-section-7 «Краткий итог» и его legacy navigation |
| 2 | theory; lesson-section-2…lesson-section-8 (самопроверка) | lesson-section-9 «Краткий итог» и его legacy navigation |
| 3 | theory; lesson-section-3…lesson-section-8 (самопроверка) | lesson-section-1 «Что нужно знать перед темой»; lesson-section-9 «Мини-итог» и legacy navigation |

В №2 координатные лучи — авторские статические SVG, не новый интерактив; координаты,
подписи, единичный отрезок и текстовые алгоритмы не следует превращать в controls.
В №3 сохраняются таблица округления, SVG округления 347 до 350, знаки ≈ и все
авторские вычисления. Математические формулировки не исправлялись по догадке.
Runtime metadata/routes пока не активированы, существующая публикация не менялась.

## Согласованный общий fix — результат 08.11.2026

Владимир разрешил минимальные изменения двух общих файлов после согласования
с Ильёй. Это последующее решение заменяет запрет общих изменений выше только
для marker-start, dy и data-hidden-edges. Остальные общие файлы не менялись.

Общий fix выделен в commit `f5cfddd` относительно исходного main
`cf8690794644fe5f90c42d5aae2c1c5f7ca9b888` (2 файла, +12/-1).
Точный patch: `git diff cf869079 f5cfddd -- frontend/scripts/convert-lesson.mjs backend/content/sources.py`.
Локальный handoff diff сохранён в ignored `var/handoff/ms-t003-shared-svg.diff`.

- Конвертер допускает marker-start только на line с локальным url(#id), dy
  только на tspan как конечное десятичное число, data-hidden-edges только на path
  со строкой true. Другие неизвестные атрибуты и активная разметка по-прежнему
  отклоняются. Allowlist произвольных data-* не добавлен.
- Backend допускает dy только на tspan, только строковое десятичное конечное
  число; NaN/Infinity, единицы, списки и CSS отклоняются. Существующие URL/layout
  guards сохранены. marker-start/data-* уже поддерживались backend.
- Семантика старых допустимых входов не меняется; immutable releases и пилоты
  не регенерировались. Новая возможность применяется только при наличии attrs.
- Возможное влияние на 7 класс: общий конвертер/валидатор теперь допускают эти
  три конструкции в установленных пределах. 7-классные материалы, пути, renderer,
  CSS и math helper не менялись. Совместимость установлена чтением diff, а не
  тестами или ручным browser review; Илье нужно независимо оценить свои материалы.

Команда авторинга: `node frontend/scripts/convert-lesson.mjs <topic-directory>`
только для пяти отсутствовавших документов, без тестов/QA. Для запуска конвертера
использованы уже установленные frontend dependencies через ignored junction
`frontend/node_modules` к зависимостям host-check; settings/venv/DB/var не копировались.
Первая попытка до подключения dependencies не нашла parse5 и не создала документы.

Созданы ещё четыре content.json: №7, №30, №33, №35. Их актуальный статус —
DRAFT_SOURCE_REVIEW_PENDING (заменяет BLOCKED_SHARED_APPROVAL в таблице выше).
Итого 33 новых черновика + принятый пилот №12; полная сверка и runtime activation
не завершены. Новых runtime URL/redirects пока нет, маршруты и lesson.json неизменны.

### Новый, не согласованный blocker: тема №34

«Прямоугольный параллелепипед. Развёртка» после разрешения data-hidden-edges
останавливается на `Unsupported attribute: data-net-face`.
Frozen source: `curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/08-pryamougolnyj-parallelepiped-razvyortka/body.html`.
`data-net-face="true"` находится на 30 SVG rect: строки 70–75, 146–151,
212–217, 283–288, 349–354. Это пассивная метка граней; удаление атрибутов ради
прохода конвертера не выполнялось, геометрия и frozen HTML не изменялись.

Нужно отдельное подтверждение Владимира на дополнительный случай в
frontend/scripts/convert-lesson.mjs: key=data-net-face, tag=rect, value='true'.
Backend уже принимает data-*, поэтому его дополнительная правка не требуется.
Это дополнение НЕ реализовано. Тема №34: BLOCKED_ADDITIONAL_SHARED_APPROVAL.
Другие будущие отказы пока неизвестны; полный success для этой темы не заявляется.

### Готовый текст для передачи Илье

Илья, согласованный SVG fix выделен отдельно:
https://github.com/Tramsey00/MathStart-Python/commit/f5cfddd
Исходный main: cf8690794644fe5f90c42d5aae2c1c5f7ca9b888.
Точный diff: git diff cf869079 f5cfddd -- frontend/scripts/convert-lesson.mjs backend/content/sources.py
Изменены только два общих файла: узкая поддержка marker-start на line с url(#id),
конечного десятичного dy на tspan и data-hidden-edges=true на path; backend dy
проверяется отдельно. Renderer, UI, CSS, math helper и материалы 7 класса не менялись.
Автоматические проверки: NOT_RUN_BY_USER_REQUEST. Просьба независимо посмотреть
совместимость с MS-T005; результат этой проверки пока не заявлен.
Дополнительно в теме о развёртке найден data-net-face=true на rect. Его поддержка
не добавлена и ожидает отдельного подтверждения Владимира.

Текст подготовлен для пользователя; сообщения Илье инструментами не отправлялись.
Полный перенос MS-T003 ещё не закончен; Draft PR будет подготовлен после устранения
блокера и завершения переноса, согласно поручению. Commit/push не означают review
или приёмку. Tests/typecheck/Playwright/backend/smoke/source/docs/preservation gates
и release build: NOT_RUN_BY_USER_REQUEST. Merge/закрытие Issue: NOT_PERFORMED.
