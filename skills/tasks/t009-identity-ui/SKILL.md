---
name: mathstart-t009-identity-ui
description: Выполнить MS-T009 — вход по логину, личный кабинет и защита аккаунта; только по отдельному поручению из реестра MathStart.
---

# MS-T009 — Вход по логину, личный кабинет и защита аккаунта

## Актуальная передача в PR — 16.11.2026

**Статус: READY_FOR_REVIEW.** Issue #68, ветка ms-t009-identity-ui,
[PR #69](https://github.com/Tramsey00/MathStart-Python/pull/69). Руслан согласовал
текущий интерфейс и поручил финальную очистку, обновление информации и отправку
в этот PR; решение о merge он принимает самостоятельно. Полная приёмка Identity,
независимое security/architecture review и production readiness этим не заявлены.

**Координаты.** Основной checkout C:/Projects/MathStart-Python, исходный HEAD
и опубликованный до передачи candidate a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
его tree 9ebce3b77133939e7e197d8c984cb48382ebd91e. После git fetch origin/main
4eddd0d6aaf9374a51bfd28456cff71b5349a6a1, исходная ветка +7/−0. Согласованный
локальный dirty candidate включён в передачу; точные итоговые SHA/tree публикуются
в PR после коммита. Старые hashes ниже относятся к своим этапам, не к этому tree.

**Итоговый интерфейс.** Главная — восстановленная орбита (11 витков, прежние
геометрия/цвета/пауза/reduced-motion). Auth — самостоятельные формы с единым
логотипом, плавной сменой режимов и локальными ошибками. ЛК — принятые класс,
аккаунт и безопасность, сохранение класса и ссылка материалов в mobile-шапке,
подтверждение нового пароля, реальные формы и защита. Каталог восстановлен к
прежней композиции/шрифтам/общему рисунку; сохранены короткие тексты, фон и
актуальная тёмная тема. Поиск снова плавно раскрывается влево в шапке, на mobile
полноширинно ниже неё; вступление при поиске обычное. Последняя правка сохранения
класса оставляет диски непрозрачными, без проступающей соединительной линии.
Общий подвал прежний. Монжа и рисунка слева в ЛК нет.

**Дополнительная очистка этой передачи.** Потребители проверены по frontend/src,
frontend/tests, site_content, curriculum и static до удаления:

| Файл | Выведено / причина / сохранённая замена |
| --- | --- |
| identity/identity.css | identity-footer, account-current-grade, account-grade-editor и media-правила без потребителей; действующие общий footer и orbit-grade-form сохранены |
| identity/account-details.css | повторный идентичный блок field-error; общий scoped блок и локальные destructive tokens сохранены |
| identity/auth-form.tsx | неиспользуемая неанимированная ветка PasswordField/animateToggle; все реальные вызовы уже использовали единый переход глаз |
| identity/account-page.tsx, password-change-form.tsx | убран лишний animateToggle у вызовов; обработчики и constraints прежние |
| identity/identity-icon.tsx | вариант arrow без потребителей; рабочие иконки сохранены |
| public-pages/materials-page.tsx | неиспользуемые локальные book/sun/moon; шапка использует свои общие иконки, рисунок сохранён |
| public-pages/site-shell.tsx | неиспользуемый re-export Brand и пустая константа site; фактический /account/ и SiteFooter сохранены |
| public-pages/orbit-shell.tsx | недостижимые !home ветки после раннего return; DOM шапки/подвала обоих режимов прежний |
| public-pages/orbit.css | избыточный :has(+ .orbit-learning), покрытый :has(~ .orbit-learning); результат скрытия тот же |
| tests/password-confirmation.test.tsx | устаревший способ mount заменён реальным ValidationScope; assertions совпадения, запрета отправки и ARIA сохранены |

Файлы целиком не удалялись: оставшиеся source/CSS реально используются. Шрифт
Golos Text, OFL, рабочие auth/validation/transition-компоненты и оба ранее untracked
теста сохранены и включены в Git. Чужие tmp/cache/config/releases/receipts не удалялись.
Предыдущая крупная карта очистки остаётся в исторической сводке ниже.

**Самопроверка.** Чтение diff, imports, CSS-потребителей, JSX-веток, constraints,
вызовов PasswordField, текущего контекста validation и git diff --check. Новых
QA-скриптов, suites, typecheck, build, smoke и browser-прогонов нет:
NOT_RUN_BY_USER_REQUEST. Старые тестовые receipts и прежний визуальный обзор
не подтверждают этот итоговый candidate. Backend/API/схема/данные не менялись.
Внешний вид при очистке не переоформлялся; отдельный review остаётся PENDING.

**Ограничения.** Реальная почтовая отправка не подключена (UnconfiguredMail).
Provider/sender, live delivery, production edge/TLS и deploy не входят в передачу.
Миграции и ранее реализованная security-логика сохранены; старые профильные PASS
относятся только к указанным в истории SHA. Issue не закрывать автоматически.
Merge/deploy не выполняются агентом. Следующая карточка не начинается.

## История поручений и кандидатов

Все записи ниже сохранены как история, включая отклонённые варианты и прежние
PENDING/NOT_PERFORMED. Текущее состояние и статус определяет сводка выше.


## Возврат анимации поиска, 16.11.2026

По прямому поручению возвращён прежний переход ширины280ms с
cubic-bezier(.2,.8,.2,1), opacity180ms ease-out и visibility280ms.
Вместо hidden используется inert: закрытое поле исключено из фокуса, но CSS
может завершить закрытие. Единый внутренний контур focus-within сохранён.
На mobile поле полноширинное с плавным появлением; reduced-motion отключает
переходы. Состояние и refs прежние, дополнительных таймеров/библиотек нет.
Менялись только materials-page.tsx/shell.css и эта запись. Самопроверка:
чтение CSS/JSX, inert/visibility, focus и media specificity. Ветка и HEAD
прежние, чужой dirty tree сохранён. Визуальная проверка не выполнялась.
Tests/build/typecheck/smoke/browser: NOT_RUN_BY_USER_REQUEST. Приёмка PENDING.


## Поиск в шапке и линия кругов при сохранении, 16.11.2026

По следующему поручению возвращено открытие поля поиска влево от лупы
в строке шапки, в текущей синей палитре. На телефоне сохраняется полная ширина
поля под шапкой, без сжатия до110px. Существующие state/refs/очистка/Escape/
наружное закрытие и единый focus-within контур сохранены. Менялись только
слот actions в materials-page.tsx и локальная геометрия shell.css.

Причина линии через круги в момент сохранения: opacity:.65 на всём disabled
orbit-grade-disc делала прозрачным его фон. В orbit.css opacity диска теперь1,
приглушаются только подписи strong/span. Непрозрачная поверхность продолжает
закрывать линию, выбранный цвет/контур/геометрия и disabled/required сохранены.
Новых анимаций и изменений API нет. Применены ранее прочитанные frontend-design,
impeccable и web-animation-design: текущая палитра, сохранение взаимодействий,
локальное исправление состояния без новой концепции.

Ветка ms-t009-identity-ui, HEAD a557ac1, dirty tree сохранён. Самопроверка:
чтение JSX, refs и CSS specificity/opacity/background. Рендер не наблюдался.
Tests/build/typecheck/smoke/browser: NOT_RUN_BY_USER_REQUEST. Приёмка PENDING,
commit/push/merge/deploy не выполнялись. Предыдущая запись о поиске отдельной
строкой на desktop заменена этим поручением; остальные решения сохранены.


## Текущее восстановление каталога по поручению 16.11.2026

Последняя визуальная переработка материалов отклонена. Остальные изменения
сайта пользователь принял; это не означает приёмку данного восстановления.
Эта запись имеет приоритет над описанием каталога в предыдущей сводке ниже.

Источник: полный вывод materials-page.tsx/style.css до заключительной доработки,
сохранённый в контексте этого чата; общий MathIllustration и соответствующие
активные CSS-правила также найдены в HEAD a557ac1. Использованы только эти
подтверждённые части истории ветки, не checkout main или файлов целиком.
Временная полная копия предыдущего прохода уже удалена; побайтное восстановление
всего прежнего dirty-файла не заявляется. Компонент и значения нужных правил
подтверждены прежним чтением исходников, включая viewBox580×330, четыре группы
общего рисунка, width48%/flex1 и mobile width100%/margin-top23px.

Возвращены прежняя композиция вступления (в том числе при поиске), размеры,
расположение, типографика Outfit/Merriweather, интервалы, поверхность и padding
списка разделов, оформление sidebar/выбранного предмета и общий рисунок с дробями,
уравнением, закономерностью и параболой. Отдельных рисунков предметов больше нет.
Сохранены короткие описания и служебные пояснения. Фон body и локальный
--background явно #e7f0f8, dark #141a31; текущие dark foreground/card/muted/
primary/ring/border/sidebar/accent токены сохранены целиком. Старые почти чёрные
токены не возвращались. Светлые поверхности и шрифты вновь используют прежнюю
тему каталога; фон задан отдельно от них и не сбрасывается старым shorthand.

Сохранены текущие OrbitHeader/SiteFooter, полноширинная строка поиска,
глобальная выборка catalogue.topics, очистка/empty state/Escape/focus, URL
параметры и ссылки на темы, menu dialog и мобильная доступность. ЛК и передача
сохранённого класса, auth/главная/orbit.css/shell.css и общие темы не менялись.
Мёртвые шапки, фильтры, формы, skeleton и анимации не возвращены; возвращены
только стили вновь действующего общего рисунка. Из реализации менялись только
materials-page.tsx и style.css. Backend/API/БД/curriculum не затронуты.

Git root/branch/HEAD/status/remote/отношение к origin/main проверены:
ms-t009-identity-ui, HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
tree9ebce3b77133939e7e197d8c984cb48382ebd91e, локальный origin/main +7/−0,
без нового fetch. Dirty tree сохранён. Применены ранее прочитанные
frontend-design/impeccable: refinement preserves и точечные локальные токены;
новых концепций/библиотек нет. Самопроверка: чтение истории, прежнего вывода,
JSX/CSS, потребителей и каскада фона/dark/media. Рендер не наблюдался.
Tests/typecheck/build/smoke/browser/detector: NOT_RUN_BY_USER_REQUEST.
Пользовательская приёмка восстановления PENDING. Commit/push/merge/deploy нет.
SHA256 текущих двух файлов:
- frontend/src/features/public-pages/materials-page.tsx: c2043fcdc51ce97f14f6d8c1e017236542092bf0e3d700b0030902f839fa8458
- frontend/src/features/public-pages/style.css: 1fc54e86e9157e7fe51618923e6fad163aa227b07d80fcb2444b282c725dbc04


## Актуальная сводка: заключительная доработка 16.11.2026

Прямое поручение после обзора главной, ЛК и материалов. Действующая главная
с восстановленной орбитой и общий подвал сохраняются; новый редизайн не выполнялся.
Разделы ниже фиксируют историю прежних кандидатов, а не приёмку этого результата.
Продолжены существующие Issue #68, ветка ms-t009-identity-ui и [PR #69](https://github.com/Tramsey00/MathStart-Python/pull/69).

**Координаты.** Основной checkout C:/Projects/MathStart-Python. Исходный и итоговый
HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92, Git tree
9ebce3b77133939e7e197d8c984cb48382ebd91e. Результат остаётся dirty, включая
исходные чужие изменения и untracked файлы. После git fetch origin:
origin/main 4eddd0d6aaf9374a51bfd28456cff71b5349a6a1, HEAD +7/−0.
PR открыт, его опубликованный head остаётся a557ac1; описание различает
локальный UI candidate и опубликованные коммиты. Описание PR обновлено через
GitHub connector под фактическую орбиту, auth, ЛК и эту доработку, без старых
утверждений о вкладках главной и skeleton. Commit/push/merge/deploy
не выполнялись; Issue не закрыт, другая карточка не начата.

**Результат.**
- Материалы: локальные токены main/sidebar/dialog из итоговых синих цветов ЛК,
  Golos Text для интерфейса. Light без большой белой панели, dark с синими
  поверхностями. Выбранный предмет выделен заливкой и начертанием без левой полосы;
  aria-current/expanded/controls сохранены. Классы, предметы, разделы, счётчики тем,
  dialog и topic.url используют прежние данные и структуру.
- Вступления сокращены до двух предложений, служебная копия обращается на «вы»
  без em dash. На mobile текст16px, компактный рисунок до300×135px.
  Один MathIllustration выбирает статичную схему по предмету: ½+⅓=⅚ с шестью
  равными частями, y=2x+1 с одинаковым масштабом осей, треугольник3:4:5,
  пример частот2/4/3. Без сеток и анимации; каждому SVG дано доступное описание.
- Поиск глобальный по catalogue.topics. Непустой нормализованный запрос заменяет
  hero и mobile grade picker компактным заголовком, явным «По всем классам и
  предметам», запросом, очисткой и результатами/empty state. Очистка возвращает
  прежний выбранный класс/предмет. Поле вынесено в полноценную строку под шапкой,
  лупа/Escape/возврат фокуса/наружное закрытие сохранены. Один focus-within контур
  по границе поля; внутренние outlines подавлены более специфичным локальным
  правилом, clipping/анимация ширины и скрытие логотипа при поиске удалены.
- ЛК: ссылка шапки и ссылка материалов в общем footer получают /materials?grade=
  <number>-klass только из grades, сопоставленных с user.selected_grade_id.
  Несохранённые radio не участвуют; без класса /materials. Каталог по-прежнему
  читает явные grade/subject/section/q, не подменяя их профилем. На390px в шапке
  доступна книга с сохранённым доступным именем «Материалы».
- Пояснение класса: «Выберите класс и сохраните изменения». Один h1 «Личный
  кабинет», заголовки разделов h2, вложенные настройки h3; CSS сохраняет размеры.
- Локальный destructive ЛК #a12636 / dark #ffb4be. Расчёт sRGB по CSS для базовой
  поверхности, наиболее насыщенной точки фонового пятна и поля: light6.40/5.70/7.16:1,
  dark10.25/6.68/8.46:1. Это расчёт значений, не browser/computed-style проверка.
  Invalid border/focus используют тот же цвет; сообщения и aria-связи сохранены.
- Radio имеют уникальные id, общий data-validation-group и одну FieldError у
  fieldset/legend. Required и нативный запрет submit сохранены. Invalid capture
  подавляет bubble и выводит ошибку группы; submit capture блокирует обработчик;
  выбор radio очищает общую ошибку. Серверная проверка и API не менялись.
  Пользователь не создавался, мутации аккаунта для просмотра не отправлялись.

**Карта выведенных остатков (файлы реализации не удалялись).**

| Файл / семейство | Почему выведено | Действующая замена / что сохранено |
| --- | --- | --- |
| auth-form.tsx: HomeIdentity, SessionPlaceholder | Единственный consumer placeholder находился внутри неиспользуемого HomeIdentity; imports/тестовых потребителей нет | Отдельная AuthPage, рабочие AuthForm и PasswordField сохранены |
| site-shell.tsx: LandingHeader | Нет imports/build/test consumers | OrbitHeader; SiteFooter и LessonFooter сохранены |
| materials-page.tsx: StrictMode, site; старая общая иллюстрация | Imports не использовались; прежний рисунок заменён по поручению | Один предметный MathIllustration, прежние catalogue данные и URL |
| landing.css: homepage-intro, home-intro-copy, home-class-surface, home-grades, home-subjects, home-footer, login-preview-note, identity-placeholder | Нет runtime/test/build consumers, включая media-ветки | Orbit home; действующие стили полей/кнопок/подсказок/ошибок оставлены |
| landing.css: email-login, login-description, identity-link, landing-main, materials-entry, materials-entry-link, open-access-note; связанные arms identity.css | Consumers отсутствуют после вывода HomeIdentity и прежней главной | Отдельный auth и текущая orbit-композиция; активные identity-page arms сохранены |
| style.css: topbar/topbar-brand/global-search/header-actions/all-topics/theme-button/login-button, section-filter/search-clear | Нет JSX, imports или прочих потребителей | OrbitHeader, полноразмерный поиск; icon-button/mobile-menu и каталог сохранены |
| style.css: illustration-grid/rule/curve/axis-label | Прежний SVG заменён, иных потребителей нет | Предметная статичная графика с действующими общими стилями |
| shell.css: catalogue-inline-search/expand и mobile/focus overrides | DOM заменён полноценной строкой; прежние правила сжимали поле и обрезали focus | catalogue-search-panel/field, один полный контур, без новой анимации |
| orbit.css: satellite/counter/revolve, action-icon, hero-bottom, motion/reduced-note и связанные hover/media/paused arms | Отсутствуют в действующем DOM/imports/tests | Спираль, traveller, field/light, кнопка на рисунке и её пауза сохранены |
| orbit.css: старые footer overrides, скрытые story/button псевдоэлементы, перекрытые палитры и фоны | Footer находится вне orbit-site; декор отключён; значения перекрывались итоговыми | Неизменённый общий LessonFooter и home-lesson-footer; итоговые home/account палитры собраны вместе |

CSS сгруппирован по общей шапке, главной, ЛК, wrapper подвала и брейкпоинтам.
При сведении каскада сохранены итоговые геометрия/шрифты/цвета/состояния;
учтён приоритет позднего padding-block14px у кругов над старым mobile padding12px.
Правки заголовков сопровождаются теми же CSS-размерами. Рисунок главной:
11 витков, прежние размеры/смещения/ручные цвета, 360s alternate, фазовая пауза,
field/light12s и reduced-motion. Новых hover-анимаций/библиотек нет.

**Защита принятого вида.** home-page.tsx побайтно совпадает с исходником этого
поручения, SHA256 1092e72037cf5ed16d99b75d14d85128529a5ed57f623edf69a6ec9523047059.
Общие lesson-shell.tsx/css, theme.css/base.css и public-design.css побайтно
не менялись в этом проходе. Footer DOM/стили и его wrapper сохранены; в ЛК
изменился только href материалов. Цвета каталога не наследуются footer/логотипом.
Сохранены account-details.css, auth-appearance.css, auth-mode-transition.tsx,
field-validation.tsx, password-change-form.tsx, orbit-shell.tsx/orbit.css,
Golos Text/OFL и все существующие тесты, включая untracked. Auth appearance,
mode transition, password-change-form и оба untracked test-файла побайтно прежние.
Монжа/вертикальную графику не возвращали. Backend/API/БД/миграции/curriculum
и содержимое уроков не менялись. Чужие var/.cache/config/releases/receipts сохранены.

**Самопроверка и ограничения.** Выполнены git root/branch/HEAD/status/remote/fetch,
отношение к main; Get-Content и rg по реальным imports, TSX, CSS, tests, build
inputs; ручное чтение diff к исходному dirty candidate, разбор CSS specificity,
shorthands/logical properties и media-порядка, математики SVG, native invalid/
submit guard и ARIA, расчёт контраста, сопоставление SHA256 защищённых файлов.
Область digest в frontend/src/features/: public-pages/{materials-page.tsx,
site-shell.tsx, orbit-shell.tsx, orbit.css, landing.css, style.css, shell.css}
и identity/{account-page.tsx, auth-form.tsx, field-validation.tsx,
account-details.css, identity.css} (всего12 implementation-файлов). Scoped digest = SHA256 от отсортированных строк
`path + NUL + file_SHA256 + LF`: исходный5cf65b089af00afa6ccd5fa11938fd562399763cf74f8239e619b6a2bba37fdc,
итоговый160f9b3786ecaa175b56e404c17301db86f5446b16f72dfa43b3f07fa6ef14a1.
Это digest локальных12 файлов, не Git tree и не опубликованный PR source.

Прочитаны настоящие frontend-design/impeccable, web-animation-design и
ui-ux-pro-max (a11y/mobile/forms). Impeccable context выполнен один раз;
craft-floor/polish прочитаны. Применены refinement-preserves, локальные токены,
короткая фактическая копия, явные состояния/labels/focus, мобильный приоритет
контента и сохранение существующей motion lifecycle. Для группы использованы
[MDN radio](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/radio)
и [W3C grouping](https://www.w3.org/WAI/tutorials/forms/grouping/).
Поручение пользователя приоритетнее требований skill о render/detect:
тесты/typecheck/build/smoke/browser/detector/новые QA-скрипты
**NOT_RUN_BY_USER_REQUEST**. Работа с исходниками штатного host-dev/HMR,
без prototype servers, перезапуска, release build или публикации.
Итоговый рендер desktop/mobile/light/dark, взаимодействия и ошибки в браузере
не наблюдались; пользовательская визуальная/человеческая приёмка и отдельное
review **PENDING**. Чтение кода не выдаётся за визуальную проверку.


## Локальный возврат со страницы восстановления — 15.11.2026

Источник горизонтальной полосы — border-top в .existing-login (landing.css),
применявшийся к «Вернуться ко входу». Только для mode=recover класс заменён
на существующий identity-forgot. Тем самым удалены сам разделитель и прежние
отступы existing-login, переиспользованы актуальные цвет/начертание/fit-content,
44px hit area, hover/active/focus-visible без underline/фоновой полосы.
CSS не менялся; «Не помню пароль», reset/verify и другие страницы сохранены.
Href=/auth?mode=login, логика/валидация/границы панели и поля прежние.
Применены ранее прочитанные frontend-design/impeccable: повторное использование
согласованного действия и разделение интервалом без декора.
Самопроверка Get-Content/rg, источник border и specificity общего класса.
Ветка ms-t009-identity-ui, чужие dirty-изменения сохранены. Изменены только
account-page.tsx и карточка. Визуальная проверка не проводилась.
Tests/build/typecheck/smoke/browser: NOT_RUN_BY_USER_REQUEST. Merge нет.

## Ошибки под полями вместо browser bubbles — 15.11.2026

Предыдущее field-validation.ts использовало setCustomValidity и нативный
popup. Заменено на field-validation.tsx с ValidationScope/контекстом ошибок,
FieldError и ValidationInput. Корни auth/ЛК используют Scope без лишней
обёртки. Native required/minLength/maxLength/type constraints сохранены:
invalid.preventDefault подавляет только системное окно, не разрешает submit.
Дополнительный submit capture проверяет ValidityState, существующий формат
логина регистрации и совпадение new/confirm, при ошибке preventDefault+
stopPropagation не допускают API handler. Проверка совпадения перенесена
из локального PasswordChangeForm в единый Scope; серверные проверки прежние.

Охвачены login/register/recover/reset, пароль/email/session формы ЛК.
В verify без полей новые правила не добавлены. Email не стал required.
FieldError после соответствующего поля, aria-invalid и aria-describedby
добавлены с сохранением прежних hint ID. Первое invalid input получает focus
после вывода ошибок. Ошибки не показываются до invalid/submit, пересчитываются
только для уже ошибочных полей при input/change; изменение new пересчитывает
ошибку confirm. Mode/reset очищают состояние, key форм не переносит ошибки.
Старый customValidity очищается при mount/mode/input (включая HMR-preserved
DOM), новые строки customError не устанавливаются, reportValidity и novalidate
не используются. Серверные общие ошибки/успехи не менялись.

Ошибки: текст12px/line-height1.5, отступ8px, текущий destructive, без отдельной
плашки/декора. Существующий aria-invalid contour сохранён. На главную оставлен
акцентом, пропорции компактнее: min180/height44/padding10x24/font500,
цвет #2b4068, отступ24. Forgot: margin10/padding8x14 с прежним44px hitheight,
без подложки/underline и с отдельным focus-visible.

Применены уже прочитанные frontend-design/impeccable (локальная иерархия,
не вводить новый визуальный слой), ui-ux-pro-max (ошибка у поля, focus,
сохранение hint связей, untouched без ошибок). Самопроверка исходников:
Get-Content/rg/imports, guard до handlers, invalid cancellation, aria,
mode/reset, удаление старого consumers/дублирующей mismatch ошибки.
Автотесты/typecheck/build/smoke/browser: NOT_RUN_BY_USER_REQUEST.
Визуальная проверка не проводилась. Ветка ms-t009-identity-ui, основной checkout,
HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92 до/после, dirty.
PR #69 подтверждён open connector. Чужие правки (в том числе параллельные
изменения карточки/главной) сохранены; merge/deploy не выполнялись.

## Восстановление последней фактической орбиты — 15.11.2026

Прямое поручение: отклонить Монжа и вернуть именно последнюю орбиту без
новых улучшений. Git log по home-page.tsx/orbit.css показал, что актуальная
орбита не была закоммичена: последнее изменение главной в Git — 0aab648,
где ещё прежний выбранный экран. Источник восстановления — полный вывод
Get-Content home-page.tsx, сохранённый в начале этого чата до первой замены
на MongeArtwork. Его параметры подтверждает исторический раздел
«Геометрия и экранная толщина без изменения ручных цветов» от14.11:
витков14→11. Ранние записи о14 витках не использованы как фактический код.
OrbitArtwork и генератор спирали возвращены из этого исходника.

Сохранены11 витков×144 отсчёта, x=(630−280t)cos(22πt),
y=(278−193t)sin(22πt); один spiralPath для линии и offsetPath точки.
Исходный viewBox−100 −100 1500 850, translate715/335 и rotate−26,
акцентные витки0/4/8, точкаr6/stroke2/--orb-warm. CSS орбиты сохранился
в orbit.css и не редактировался: desktop60%×470px,left16%/top156px,
scale1.05; прежние mobile правила; stroke1.1/.78, major1.6/.95,
desktop прибавка1/s. Итоговый каскад цветов сохранён, включая ручные
--orb-line #0004ff65 / dark #7e91e4 и точку #000000e4 / dark #fff.
360s на один проход от внешнего края внутрь, infinite alternate (720s
полный цикл), прежние плавные развороты2%/98%, колебание orbit-field12s.
Все эти значения взяты из прежнего кода, не подобраны заново.

Восстановлена нативная кнопка самой спирали, прозрачная эллиптическая
hit-area, action aria-label/aria-pressed и focus-visible. Существующие
paused/localStorage/offscreen/visibility обработчики HomePage сохранены;
пауза через animation-play-state продолжает прежнюю фазу. При reduced-motion
orbit-field/traveller/light статичны. Отдельная кнопка и фазы сборки/
затухания Монжа не возвращались. Применён прочитанный web-animation-design:
сверены CSS lifecycle, сохранение фазы и reduced-motion; приоритет — точный
найденный исходник. Новая концепция/внешнее исследование не выполнялись.

Потребители перед удалением проверены rg по репозиторию:
home-page.tsx импортировал только MongeArtwork, public-design.css — его CSS;
MongeArtwork импортировал только свою модель. Карта выведенных файлов:
- monge-artwork.tsx: единственный HomePage consumer заменён OrbitArtwork;
  удалены rAF, refs/scene clock, media/visibility/observer обработчики Монжа.
- monge-artwork.css: единственный @import из public-design.css удалён;
  стили заменены сохранившимся orbit.css, без его изменения.
- monge-geometry.ts: единственный consumer monge-artwork.tsx удалён;
  модель/пары/контакты/viewport отклонённой реализации выведены.
Файлы удалены полностью; повторный rg frontend не нашёл monge imports/
символов. Одновременно работающей скрытой анимации Монжа нет.

Изменены только home-page.tsx (генератор/OrbitArtwork и его вызов),
public-design.css (удалён один import), UI-контракт и эта карточка;
удалены перечисленные3 monge-файла. Header/footer/CTA/тексты/фон/правая
колонка, auth/ЛК/каталог/уроки и чужие незакоммиченные правки сохранены.
SHA256 orbit.css до/после одинаковый:
8f2fd48c5b8396d8fe7e6599120b56af72c64453f87c0ad1d2c811a903af44d6.
SHA256 восстановленного home-page.tsx:
1092e72037cf5ed16d99b75d14d85128529a5ed57f623edf69a6ec9523047059.
Исходный/итоговый HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
HEAD tree9ebce3b77133939e7e197d8c984cb48382ebd91e, результат dirty;
это восстановление незакоммиченного исходника, не checkout старого SHA.
Основная ветка ms-t009-identity-ui, root/status/remote проверены;
локальный origin/main +7/−0 без fetch, GitHub подтвердил PR#69 open.
Саморевью: git log, Get-Content, rg потребителей/остатков, CSS каскад,
сопоставление с сохранённым исходником, hashes/status. Итоговый экран и
плавность в браузере не наблюдались; ожидание цикла не выполнялось.
Tests/typecheck/build/smoke/browser QA: NOT_RUN_BY_USER_REQUEST.
Штатный host-dev/HMR, без перезапуска, guards/validators не менялись.
Саморевью COMPLETE, отдельное review/human acceptance PENDING;
commit/push/merge/deploy не выполнялись. Старые receipts ниже сохранены
как история, не подтверждение приёмки восстановления.

## Ещё больше, три цвета окружностей и контакты — 15.11.2026

Новое поручение исполнено в monge-geometry.ts, monge-artwork.tsx/css.
Широкий desktop: область58.5%×570px, left15.5%/top105px, примерно+19%
к предыдущему масштабу; постоянный viewBox45 15 590 490. Для1101–1259px
отдельное51%×480px, left22%/top140px сохраняет место у CTA. Tablet/mobile:
область шире на40px вместо24, mobile cap660px вместо600. Равномерное
вписывание и поворот−26° сохранены; viewport не меняется вслед за кадром.
Окружности: большая #3868ac, средняя #277d77, малая #9d642b;
dark #91b8ed/#83cbbf/#e8b779. Касательные #687d9b/#8298b8,
ось/пересечения #34445c/#eef1f7. Везде ограниченная согласованная палитра.

Добавлены12 контактов r3 (против r4.5 у внешних центров), окрашенных
по окружности. Координаты напрямую из Tangent.contacts=C+r·n, обновляются
вместе с остальной моделью через refs. Общий MONGE_PAIRS задаёт прежние
пары0/1,0/2,1/2 для геометрии и назначения цветов контактов: нет отдельного
ручного списка точек. Формулы касательных/пересечений/траектории не менялись.
Contacts плавно появляются1500–1850ms, когда касательные достигают обоих
контактов; новые таймеры отсутствуют. Остальные фазы27.25s, пауза и точное
продолжение/reduced-motion/observer/cleanup сохранены. Доступное описание
дополнено точками касания. Шапка/footer/тексты/CTA/фон/auth/ЛК не менялись.

Применены ранее прочитанные frontend-design/impeccable/craft-floor:
три согласованных оттенка, размером отделены контакты от пересечений,
масштаб зависит только от viewport и брейкпоинта. Саморевью Get-Content/rg:
порядок12 contacts и владельцев, CSS каскад light/dark/mobile, общая шкала,
источники координат, размеры и постоянные границы. Плавность/итоговый экран
в браузере не наблюдались. Tests/typecheck/build/smoke/browser/numeric QA:
NOT_RUN_BY_USER_REQUEST. Работа через существующие host-dev/HMR файлы.
Исходный/итоговый HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
HEAD tree9ebce3b77133939e7e197d8c984cb48382ebd91e, веткаms-t009-identity-ui;
root/status/remote/отношение к локальному origin/main(+7/−0) проверены,
fetch не выполнялся. Результат dirty, чужие правки сохранены;
уточнён UI-контракт, receipts прежних кандидатов не переписывались.
Саморевью COMPLETE, отдельное review/human acceptance PENDING;
commit/push/merge/deploy не выполнялись.

## Ещё крупнее и уточнение цветов рисунка — 15.11.2026

Пользователь одобрил остальное и поручил только дополнительное увеличение
и цвета. Из реализации изменён исключительно monge-artwork.css.
Desktop: width44→50%, height426→480px, top186→170px, left28→24%.
Это ещё около 13% равномерного увеличения при прежнем viewBox/повороте,
без подстройки к кадру. Tablet/mobile: область шире на24px, центрирована,
mobile max540→600px. По CSS сохраняется запас внутри отступов страницы;
равномерность обеспечивает прежний preserveAspectRatio.
Окружности — петрольный #246b78 / dark #82c8cf; касательные — спокойный
синий #566f96 / #829bbf; ось и точки — медный #b66636 / #efb778.
Толщина/окончания штрихов, математическая модель, диагональ, все фазы,
пауза, reduced-motion, observers, JSX, тексты/CTA/фон/chrome не менялись.
Применены ранее прочитанные frontend-design/impeccable/craft-floor:
один графический акцент, роли цвета, локальный масштаб без смены композиции.
Саморевью Get-Content/rg и Git status; тесты/typecheck/build/smoke/browser:
NOT_RUN_BY_USER_REQUEST. Итоговый экран/плавность не наблюдались.
Ветка ms-t009-identity-ui, исходный/итоговый HEAD
a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92, HEAD tree
9ebce3b77133939e7e197d8c984cb48382ebd91e, результат dirty; чужие правки
сохранены. Уточнён UI-контракт, старые receipts не переписаны.
Review/приёмка этой итерации PENDING, commit/push/merge/deploy не выполнялись.

## Масштаб, диагональ и сцена Монжа — уточнение 15.11.2026

Новое прямое поручение исполнено в трёх monge-файлах; главная, оболочка,
CTA/тексты/фон, auth/ЛК, каталог и уроки не редактировались. Математические
формулы касательных/контактов/гомотетии и траектории центров сохранены.
Все элементы помещены в одну SVG-группу rotate(-26 380 310). Постоянный
viewBox 30 15 620 490 вместо 760×620 даёт равномерное увеличение примерно
23–27% в действующем desktop/mobile размещении, без изменения размеров
по текущему кадру. По коду оценены аналитические габариты после поворота:
центры гомотетий и окружности укладываются в x=[53,627], y=[64,451];
отрезки лежат в их выпуклой оболочке. Синусоидальные координаты после
поворота имеют вид a+b·sin(t)+c·cos(t); амплитуда ограничена hypot(b,c).
Это статическая оценка диапазона, не новый численный/браузерный прогон.
Сохранены desktop область и mobile поток; SVG пропорционален и без маски.

Роли цвета: окружности #233f70 / dark #c9ddfa, касательные — спокойные
смеси действующих CTA-синих, ось/точки #bc4337 / dark #efb28b (ранее
использованные тёплые оттенки главной). Цвета заданы только на графике.
Удалены +12/+24 продления касательных: start — наиболее удалённый от
внешнего центра настоящий контакт, end — этот центр; оба контакта входят
в отрезок. Ось — между H_AB/H_BC без прежних ±36; при rA>rB>rC третий
центр H_AC является их выпуклой комбинацией. Linecap butt исключает выступ
штриха за расчётный конец. Фоновые накладки/маски не применяются.

Единая сцена 27250 ms: окружности плавно появляются 0–900; касательные
строятся 750–1850 от дальней точки касания к внешнему центру; точки
появляются 1800–2150; ось строится 2050–2600. Далее все 24 s занимает
полный цикл геометрического движения, с нулевой скоростью на краях
через smoothstep общей фазы. Общее затухание 26600–27250, затем новая
сборка без пустой паузы; сброс скрыт нулевыми длинами/opacity.
Построение отрезков — линейная интерполяция вдоль вычисленных линий;
нет dash-компенсации при non-scaling-stroke или независимых таймеров.
Текущая общая elapsed хранится в ref; пауза/продолжение сохраняют даже
сборку и затухание. Reduced-motion принудительно показывает целые
отрезки/окружности/точки и opacity=1, не сбрасывая сохранённую фазу.
Первый вход с сохранённой паузой тоже показывает собранную конфигурацию.
Observer/visibility, native button, aria-pressed/описание/focus и cleanup
сохранены; React state на каждом кадре не обновляется.

Применены ранее прочитанные frontend-design, impeccable/animate/craft-floor,
web-animation-design; ui-ux-pro-max — поиск responsive chart aspect ratio
(Horizontal Scroll применим без маски) и education learning (разделение
ролей цвета; готовые палитры не переносились), рекомендации dark-mode /
breakpoint consistency. Прямой brief приоритетнее требований skill о QA.
Запрос официальных SVG-источников завершился transport error; реализация
не зависит от недоступной документации и не добавляет зависимостей.

Фактически выполнено саморевью исходников Get-Content/rg: формулы контактов,
концы отрезков и выпуклость, единое преобразование/постоянные границы,
фазы/reduced-motion/cleanup/пауза, CSS cascade/desktop/mobile. Плавность и
итоговый экран в браузере не наблюдались. Тесты, численные повторные прогоны,
typecheck/build/smoke/browser QA/detector: NOT_RUN_BY_USER_REQUEST.
Исторический receipt 97 фаз ниже не выдаётся за проверку этой итерации.
Работа через файлы существующего host-dev/HMR, без перезапуска/сборки.

Изменены monge-geometry.ts, monge-artwork.tsx, monge-artwork.css;
уточнены текущий UI-контракт и эта карточка, старые receipts сохранены.
Ветка ms-t009-identity-ui; исходный/итоговый HEAD
a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92, HEAD tree
9ebce3b77133939e7e197d8c984cb48382ebd91e, результат dirty.
Git root/branch/status/remote проверены, локальный origin/main +7/−0 без fetch;
GitHub подтвердил PR #69 open. Чужие правки сохранены. Саморевью COMPLETE,
отдельное review/human acceptance PENDING; commit/push/merge/deploy не выполнялись.

## Геометрическая анимация главной по MP4 — 15.11.2026

Прямое поручение пользователя: заменить спираль главной построением из MP4,
самостоятельно выбрать адаптацию. Остальные решения главной сохранены;
auth/ЛК, каталог, уроки, backend/API/БД этой итерацией не изменялись.
Видео прочитано локальным FFmpeg (H.264, 720×1280, 42.10 s, 59.94 fps):
обзор с шагом 3 s, затем 42 кадра с шагом 1 s; изучены обзор и контактные
листы вступления 0.5–11.5 s и движения 24.5–35.5 s. Сначала прорисованы
окружности, затем пары общих внешних касательных средней/малой,
большой/средней, большой/малой окружностей и отмеченные пересечения;
позже — общая прямая. В основной фазе меняются центры, радиусы постоянны.
Это анализ кадров, не просмотр плавности. Курсор/подсветка не перенесены.
Определена теорема Монжа; первичный источник — Thomas Banchoff, Brown:
https://www.math.brown.edu/tbanchof/gc/mongepappus/MP.html .

Модель monge-geometry.ts: единичные нормали касательных из n·(B−A)=rA−rB,
контакты C+r·n, независимый центр гомотетии (rA·B−rB·A)/(rA−rB) каждой пары.
Прямая определяется двумя пересечениями; третье не подгоняется под неё.
Радиусы 112/58/28, синусоидальные движения центров с общей фазой 24 s;
позиции и скорости совпадают на стыке цикла. Законченное построение видно
сразу. MongeArtwork обновляет 13 SVG-элементов через refs/rAF, без React
state на каждом кадре. Пауза сохраняет elapsed и существующий storage key;
native button поддерживает Enter/Space, имя, aria-pressed, описание и focus.
Reduced-motion оставляет законченный кадр, включая изменение настройки;
observer самого рисунка и visibilitychange останавливают rAF вне видимости.
Cleanup отменяет кадр, disconnect observer и снимает оба listener.

SVG прозрачен, без карточки, подписей или панели. Итоговые цвета CTA:
#233f70/#c9ddfa, dark #c9ddfa/#344c78/#edf3ff, точки — существующий --orb-warm;
касательные — смеси синих, окружности и ось выразительнее. Фон, шрифты,
тексты, CTA /materials, обе колонки, header/footer сохранены. Только размеры
и положение графики адаптированы к desktop/mobile; preserveAspectRatio
сохраняет окружности круглыми, non-scaling-stroke — экранную толщину линий.
Специфичность локальных правил учитывает повторный импорт orbit.css.
Старый JS рисунка удалён после rg потребителей: только home-page.tsx;
общий orbit.css и оболочка этой итерацией не редактировались.

Прочитаны и применены frontend-design, impeccable/context/animate/craft-floor,
web-animation-design, ui-ux-pro-max (поиск pause animation reduced motion:
Reduced Motion, Excessive Motion, Duration Timing), skills/verification.
Приоритет — прямой brief и testing-policy; Impeccable detector не запускался.
Impeccable сообщил устаревший формат PRODUCT.md: отдельное обновление возможно
через init, в этой задаче PRODUCT.md не переписывался.

Разрешённая численная самопроверка действующей mongeFrame:
`node var/tmp/t009-monge/check-geometry.mjs`, 97 фаз за 24 s. Максимальные
ошибки в единицах SVG: касание 9.95e−14; принадлежность пересечения обеим
касательным 6.73e−14; коллинеарность 1.73e−13; контакты/радиусы 1.11e−13.
Проверены одинаковый знак расстояний (внешние касательные), контакты внутри
рисуемых отрезков, конечность и границы координат. Минимальные зазоры:
между окружностями 29.81, между точками 31.59, до края viewBox 48.85.
Кадры 0/24000 ms строго одинаковы; разница односторонних скоростей на шве
(шаг 1 ms) ≤1.42e−6 SVG/ms. Assertions не ослаблялись. Это проверка модели,
не визуальная приёмка. Временный декодер, кадры и скрипт удалены из
var/tmp/t009-monge; исходный MP4 не изменён, зависимости сайта не добавлены.

Саморевью: imports HomePage/PublicDesignHost/OrbitShell и CSS bundle,
rg/Get-Content, каскад desktop/mobile, доступность и cleanup. Штатный
`npm.cmd --prefix frontend run dev:host` из sandbox получил Docker permission
denied; повтор с доступом к хосту остановился на занятых 8131/8132.
Read-only проверка владельцев подтвердила процессы MathStart; их не
останавливал. Итоговый экран и плавность в браузере не наблюдались.
Tests/typecheck/build/smoke/browser QA/detector: NOT_RUN_BY_USER_REQUEST.

Изменены home-page.tsx (замена artwork), public-design.css (один import),
добавлены monge-geometry.ts, monge-artwork.tsx/css; уточнены UI-контракт и
эта карточка. Исходный/итоговый Git HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
HEAD tree 9ebce3b77133939e7e197d8c984cb48382ebd91e; результат dirty.
Scoped candidate SHA256 пяти implementation-файлов:
f55b4567cee03e9a4f2396e8149a5537a7843f69bce8e5a0d443609f3ad74c0a
(SHA256 UTF-8 manifest: по отсортированным repo paths строки
«sha256(bytes)  path\n»; home-page, monge-artwork.css/tsx, monge-geometry.ts,
public-design.css). Это fingerprint файлов, не Git tree.
Ветка ms-t009-identity-ui, основной checkout; remote проверен, локальный
origin/main +7/−0 без fetch; GitHub подтвердил PR #69 open. Issue #68 и
все чужие dirty-правки сохранены, включая параллельное уточнение auth.
Саморевью COMPLETE; отдельное review/human acceptance PENDING;
commit/push/merge/deploy NOT_PERFORMED, дубликатов Issue/PR нет.

## Акцент возврата и компактное восстановление — 15.11.2026

Изменены только два действия в auth-appearance.css. На главную — насыщенная
заливка #233f70 с белым текстом, цвета из итогового CTA главной, в dark
#344c78; hover/active #344c78/#405b8a/#2b4068. Вместо полной ширины —
fit-content с min190px (ограничен100%), height46px, radius8px, margin-top28px,
без обводки/теней/стрелки. Основной submit остаётся широким над действием
восстановления, возврат меньше и отдельно ниже. Href и логика не менялись.

Причина плашки восстановления: .auth-surface .identity-forgot display:block
и локальный .auth-page .identity-forgot:hover с background:var(--muted)
и radius12px. Локальное hover-правило заменено сменой цвета, сам элемент
получил inline-flex/fit-content/44px hit height, font550, прозрачный фон,
без border/shadow/underline. Focus после pointer-click не рисует outline;
keyboard focus-visible остаётся общим правилом auth. Исключены эти две
ссылки из общего color-селектора auth-surface a, чтобы он не перекрывал
контрастный белый текст возврата. Другие ссылки/ЛК не менялись.
Применены ранее прочитанные frontend-design/impeccable: масштаб/расположение
как иерархия действий, контрастная заливка вместо бледности, отдельные
pointer/keyboard состояния. Самопроверка rg/Get-Content CSS-источников,
специфичности/состояний, git branch/status. Ветка ms-t009-identity-ui,
результат dirty, чужие правки (включая новые monge-файлы) не затронуты.
Визуальная проверка не проводилась. Tests/build/typecheck/smoke/browser:
NOT_RUN_BY_USER_REQUEST. Merge не выполнялся.

## Только иконка глаза и заметный возврат — 15.11.2026

Причина остававшегося голубого круга — общий .password-toggle:before с
radius50% и .password-toggle:hover:before с фоновой заливкой в account-details.
Оба правила полностью удалены в источнике для auth/ЛК. Остались прозрачный
button43px, border0/box-shadow:none, прямоугольный radius8px для keyboard
focus-visible, смена цвета иконки на hover. Псевдоэлемента больше нет,
круг не маскируется. SVG/aria/переключение/150ms/reduced-motion/границы полей
не менялись. Поиск rg подтвердил отсутствие других password-toggle pseudo
и hover-background в identity/orbit; landing задаёт прозрачную основу.

На главную: в том же месте формы, теперь на всю её внутреннюю ширину,
высота50px, padding12px24px, подпись15px, заметная заливка --auth-action
из итогового CTA главной, контрастный текст/граница, radius10px; hover/active
теми же токенами. Прямой href=/ сохранён. Основной submit остаётся отдельным
главным действием с другим контуром и начертанием.
Изменены account-details.css, auth-appearance.css и эта карточка.
Применены ранее прочитанные frontend-design/impeccable (ясная иерархия,
устранение источника декора), web-animation-design (единый150ms переход
не изменён). Формы/сценарии/валидация/backend/другие страницы не редактировались.
Ветка ms-t009-identity-ui, HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
результат dirty, чужие правки сохранены. Самопроверка Get-Content/rg/status,
каскад hover/focus/pseudo и размер hit area. Визуальная проверка не проводилась.
Tests/build/typecheck/smoke/browser: NOT_RUN_BY_USER_REQUEST.
Merge/deploy не выполнялись.

## Шесть уточнений панели, переключения и безопасности — 15.11.2026

Внешняя auth-surface: радиус 8px вместо 22, без новой тени/рамок.
На главную — явное вторичное действие href=/ с тонированной поверхностью,
границей, 46px высотой и читаемой подписью14px, основной submit сохраняет
иерархию. Глаз: общий button получил radius8px и box-shadow:none,
focus:not(:focus-visible) без outline, keyboard focus — прямоугольный 2px
с внутренним offset -4. У псевдокруга только мягкая hover-заливка без border;
150ms затухание иконок/33px подложка/43px hit width сохранены.

Маршруты: app/routes.ts содержит один /auth внутри AccountLayout/Outlet;
key по location нет. Обычные href двух режимов заменены React Router Link
с теми же query и safeReturn. Навигация остаётся link+aria-current, без
имитации tablist с неполной клавиатурной моделью. Direct URL/reload/history
по прежним адресам, без серверных изменений. Активная подложка переключателя
двигается transform за220ms. Новый AuthModeTransition: только одна форма,
key=mode удаляет старые парольные DOM-поля, сохраняемые пароли отсутствуют.
WAAPI opacity/4px за200ms и измеренная высота за220ms; ResizeObserver
подстраивает высоту под ошибки/шрифты/переносы. Повторные переключения отменяют
старую анимацию, начиная с показанной высоты; очередь не создаётся.
Фон/логотип/навигация вне меняющегося содержимого, верх панели стабилен.
Focus переключателя сохраняется; если удалено сфокусированное содержимое,
фокус передаётся заголовку без прокрутки. Reduced-motion отключает movement,
включая изменение настройки во время перехода. Cleanup cancel обеих WAAPI,
disconnect observer, remove media change listener. Таймеров нет.

В ЛК PasswordChangeForm: current→new интервал32px, внутри new/confirm18px,
подсказка15–128 остаётся у new; confirm fresh сохраняет min/max и autocomplete,
showHint=false убирает только дубликат подсказки/несуществующий aria-describedby.
Ошибка несовпадения и required/server validation сохранены. Тонкий border-left
возвращён в исходное account-main правило, mobile border0 уже предусмотрен;
профильный горизонтальный разделитель не возвращался.

Прочитаны реальные frontend-design, impeccable/craft-floor,
web-animation-design, ui-ux-pro-max. Применены refinement, согласованное
прерываемое движение ease-in-out/ease-out, reduced-motion, visible focus,
одна доступная форма (поиск keyboard focus form navigation).
Самопроверка исходников/маршрутов/CSS/cleanup через Get-Content/rg/status,
все изменения только в identity-файлах, account-правиле orbit.css и карточке.
Backend/API/security/schema не менялись. Основной checkout ms-t009-identity-ui,
исходный/итоговый HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
HEAD tree 9ebce3b77133939e7e197d8c984cb48382ebd91e, dirty;
локальный origin/main +7/-0 без fetch. PR #69 подтверждён open connector.
Чужие изменения сохранены. Tests/build/typecheck/smoke/browser:
NOT_RUN_BY_USER_REQUEST. Визуально результат/движение не наблюдались,
приёмка не заявляется. Merge/deploy не выполнялись.

## Восемь уточнений ЛК и auth — 15.11.2026

Удалён JSX account-materials (divider/CTA/подпись) и все его CSS-потребители:
account-page.tsx, identity.css, orbit.css; общие identity-button правила
сохранены. Убраны профильный border-bottom и разделительная border-left
основной области в исходных правилах, размеры/интервалы двух колонок сохранены.
Шапка и ссылка материалов в ней не менялись.

«Заполните поле» — нативная required-валидация, строки в реализации нет.
Новый field-validation.ts подключён к корням auth/ЛК через capture invalid/
input/change/reset: setCustomValidity задаёт конкретные сообщения по name
(username/password/current/new/confirm/email), длины из min/max, формат email.
Сообщения своевременно очищаются, браузер сам показывает и связывает ошибку
с полем, второго слоя нет. Required/API/server не отключены, email остаётся
необязательным. Radio не получает customError, семантика группы сохранена.

Auth использует реальный Brand из shared/ui/brand.tsx; существующее правило
Orbit для Outfit и --primary #2d62de распространено на .auth-page .brand,
вес/трекинг берутся из Brand CSS, размер 26px как в header. Никакой копии
логотипа. Возврат — вторичная ссылка href=/ внизу центральной формы, без
стрелки и оторванного левого расположения. Forgot без underline в normal/hover,
вместо него спокойный фон; keyboard focus сохранён.

Глаз: удалены отдельные определения auth/orbit, общий стиль в account-details
для обоих корней: 43px hit width, 33px hover disk без border, SVG 19px/1.6,
переход opacity150ms, reduced-motion и keyboard focus сохранены.
Фокус полей: прежние broad focus-селекторы исключают .login-field input,
единственное общее правило рисует 2px outline с offset -2 по существующей
границе, без внешнего зазора/изменения размеров. Ошибка имеет собственный цвет,
forced-colors использует Highlight. Landing-правило сохранено для страниц
за пределами identity, shared header/home/footer не переоформлялись.

Прочитаны frontend-design, impeccable/craft-floor, web-animation-design,
ui-ux-pro-max: сохранение композиции, единая семантика состояний, native
validation, видимый focus и прерываемое затухание. Реальное интернет-чтение:
https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/setCustomValidity
(очистка customError), https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance
(контрастный индикатор внутри контура),
https://design-system.service.gov.uk/components/back-link/
(сохранение обычной ссылки с href; расположение выбрано по текущему brief).
Визуальный просмотр внешнего iCloud отклонён auto-review как дополнительный
браузерный прогон/повтор ранее блокированного просмотра. Обходов после отказа
нет, текстовые страницы не выдаются за визуальное исследование.

Самопроверка исходников Get-Content/rg/diff: imports/потребители, required,
очистка validity, radio exclusion, border/outline/cascade и локальность CSS.
Основной checkout ms-t009-identity-ui, HEAD до/после
 a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92, dirty; origin/main +7/-0
по локальному ref без fetch. PR #69 подтверждён open connector.
Визуальная проверка нового результата не проводилась. Tests/build/typecheck/
smoke/local browser: NOT_RUN_BY_USER_REQUEST. Merge/deploy нет.

## Удаление рисунка и оформление auth — 15.11.2026

Удалён account-geometry.tsx: единственный потребитель IdentityShell,
его import/элемент удалены. Из account-details.css удалены только геометрия,
keyframes, pause, responsive/reduced-motion рисунка и position:relative
оболочки. Других потребителей rg не обнаружил. Уведомление и глаз сохранены.

Добавлен auth-appearance.css, подключён после identity.css. Только .auth-page:
центральная композиция сохранена, поверхность тонированная без тени, вкладки,
поля/границы/focus/ошибки/autofill, кнопки и ссылки согласованы в обеих темах.
Источник — последние .orbit-home и .orbit-materials-action в orbit.css,
включая ручные значения #e7f0f8c4/#e2f4fad7 и CTA #c9ddfa/#233f70,
dark #141a31/#344c78/#edf3ff. Синие CTA использованы вместо фиолетового
primary главной. Голос Text уже подключён проектом. Все существующие режимы
AuthPage используют общую поверхность, новые сценарии не добавлены.
PasswordField animateToggle включён в AuthForm и reset, CSS перехода 150ms
переиспользован через ограниченный :is(.orbit-account,.auth-page), reduced-motion
сохранён. Логика API/валидации/сессий не менялась.

Использованы уже прочитанные frontend-design, impeccable, ui-ux-pro-max,
web-animation-design: сохранение структуры, состояния форм, focus, короткий
прерываемый переход. Обязательное внешнее визуальное исследование НЕ выполнено:
открытие https://github.com/login отклонено browser auto-review, который
трактовал его как запрещённый дополнительный браузерный прогон. Обходов нет.
Доступный визуальный источник — приложенный пользователем скриншот auth;
текст/код внешнего сайта не выдавался за визуальный просмотр.

Самопроверка исходников Get-Content/rg, consumers/imports и локальность CSS,
сохранение обработчиков. Тесты/build/typecheck/smoke/local browser:
NOT_RUN_BY_USER_REQUEST. Визуально новый результат не проверен.
Ветка ms-t009-identity-ui, HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
результат dirty; чужие изменения сохранены, merge/deploy нет.

## Вертикальное построение, статус и показ пароля — 15.11.2026

Реализовано отдельное поручение без изменения композиции ЛК.
AccountGeometry — SVG в существующем левом поле, абсолютный относительно
.orbit-account, inset 22px/28px, ширина ограничена реальным gutter минус
22px и 120px. На ширине <1360px скрывается целиком, полезная область не
сдвигается. Окружности/дуги связаны общей вертикальной касательной и
секущими; локальные оси пунктирные, точечной сетки нет. SVG без растягиваемого
viewBox: нижний статичный pattern повторяется в CSS-пикселях через 480px,
круги остаются кругами при длинных формах. Края обрезаны в собственном
контейнере, низ растворяется прозрачной маской до конца основной области,
footer не затрагивается. Нет отдельной подложки, свечения или нового пятна.

Один диаметр верхней окружности с отмеченным концом вращается линейно
за 16 секунд; основная графика статична. Нативная кнопка поверх этого
фрагмента управляет animation-play-state, aria-pressed, доступным именем
и title; Enter/Space штатные, focus видим. SVG aria-hidden/focusable=false,
pointer-events:none; действия принимает только локальная кнопка паузы.
Reduced-motion отключает анимацию и ненужную кнопку, оставляет законченный
диаметр под углом 32deg. Без JS-таймеров/RAF/обработчиков окна и подписок:
анимационные ресурсы принадлежат DOM/CSS и удаляются при unmount.
Цвета — текущие синие --primary/--ring ЛК и итогового CTA главной;
статичные линии ослаблены до 32%, один движущийся акцент до 65%.

У account-feedback только реальное «Класс сохранён.» получает data-tone
success: компактная тонированная поверхность вместо белой, мягкая граница,
спокойный текст. Существующий successful API branch, role=status и таймер
исчезновения 4500ms не менялись; прочие сообщения/ошибки сохраняют прежний
контраст и оформление. Предварительного успеха и переноса focus нет.

PasswordField получил opt-in animateToggle, включённый только в ЛК, в том
числе для подтверждения пароля. Два aria-hidden SVG меняются opacity за
150ms, постоянные DOM-слои не создают очереди при повторных нажатиях.
Тип поля/aria-label/aria-pressed меняются сразу; pointerdown не забирает
focus ввода, клавиатурное переключение остаётся нативным. Reduced-motion
отключает transition. Auth использует прежнюю ветку SVG без opt-in.
Разбор контура: landing.css задаёт кнопке border:0, граница поля 1px и
focus-visible — отдельные слои. Компактный 33px псевдокруг получил тонкую
границу цвета разделителей с 70% вкладом и приглушённый hover-фон 65%; hit
area шириной 43px и keyboard focus не уменьшались.

Изменены account-page.tsx, auth-form.tsx (opt-in общего PasswordField),
password-change-form.tsx, account-правила orbit.css; добавлены
account-geometry.tsx и account-details.css; обновлена эта карточка.
Формы/API/owner guard/busy/blocked/retryAt/подтверждение/очистка секретов,
круги классов, меню, фон, header и точный footer главной сохранены.
Применены прочитанные frontend-design, impeccable/craft-floor,
web-animation-design и ui-ux-pro-max (поиск pause decorative animation
reduced motion: одиночное движение, остановка, reduced-motion).

Исходники/импорты/потребители/CSS-каскад, размеры gutter и границы footer,
opt-in auth, status и отсутствие таймеров рисунка просмотрены через
Get-Content/rg/git diff/status. PR #69 подтверждён open через connector.
Ветка ms-t009-identity-ui, основной checkout; исходный/итоговый HEAD
 a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92, tree
9ebce3b77133939e7e197d8c984cb48382ebd91e; результат dirty, чужие правки
сохранены. Локальный origin/main +7/-0, fetch не выполнялся.
Тесты/build/typecheck/smoke/browser: NOT_RUN_BY_USER_REQUEST.
Визуально результат и движение не наблюдались. Пользовательская приёмка
не заявляется, merge/deploy не выполнялись.

## Один контур выбранного класса и заметное меню — 15.11.2026

Две точечные правки по последнему поручению. Причина двойного контура:
собственный 1px border .orbit-grade-disc и исходное checked-правило,
окрашивавшее все стороны внешнего ::before через border-color. Дуга
превращалась в полное второе кольцо. В самом исходном checked-правиле
заменено создание кольца на content:none для декоративного псевдоэлемента.
Удалены три лишних checked-transform правила для него. Нового маскирующего
переопределения не добавлено. Мягкая заливка, единственный border, размеры,
семантика и сохранение класса не менялись. Hover-вращение дуг остальных
классов и reduced-motion сохранены; focus-visible остаётся 3px с отступом
7px и не зависит от удалённой декорации. Единственный JSX-потребитель
orbit-grade — account-page.tsx (подтверждено rg).

Подложка активного меню усилена в существующих токенах до 55% голубого
#c9ddfa (dark: 55% #344c78), начертание 550. Форма/размеры и читаемый текст,
иконки, hover/focus сохранены для всех разделов; новых индикаторов нет.
Изменены только orbit.css и эта карточка. Использованы ранее прочитанные
frontend-design/impeccable; параметры существующей анимации не менялись.
Шапка/фон/footer/формы/защита и чужие dirty-правки сохранены.

Самопроверка исходников: Get-Content/rg по источнику border/::before,
checked/focus/hover/reduced-motion, потребителям и активным токенам;
Git status/branch/root/HEAD/remote/rev-list. Ветка ms-t009-identity-ui,
HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92 до/после, результат dirty;
локальный origin/main +7/-0 без fetch. Merge/deploy не выполнялись.
Визуальная проверка не проводилась. Тесты/build/typecheck/smoke/browser:
NOT_RUN_BY_USER_REQUEST. Приёмка не заявляется.

## Приглушение акцентов и точный подвал главной — 15.11.2026

По последнему поручению сохранена композиция, выполнены четыре уточнения.
Вклад фонового пятна снижен до 65% исходного цвета (примерно на треть),
граница растворения смягчена до 82%; расположение и палитра главной сохранены.
Выбранный класс использует отдельную мягкую смесь #c9ddfa/#e7f0f8 с текстом
#233f70, в dark — #344c78/#141a31 с #edf3ff. Это цвета итогового CTA/фона
главной из последних правил orbit.css; исходная главная не изменена.
Круги уменьшены 90→79px и 79→69px, цифры 21/20px, подпись 11.5px,
дуги -3px, сетка/соединительная линия согласованы с меньшим размером.
Нет scale, дополнительных размеров или padding выбранного круга.
Native radio, отдельное сохранение, hover-вращение 35deg, focus,
reduced-motion и touch-условия сохранены. Активное меню всех разделов
получило смешанную с основным фоном подложку без тени; размеры не менялись.

Подвал ЛК использует тот же LessonFooter из shared/lesson/lesson-shell.tsx
и ту же обёртку home-lesson-footer, что главная. Удалён дополнительный класс
account-lesson-footer и оба локальных селектора, делавшие обёртку и вложенный
.lesson-footer прозрачными. Подвал находится вне .orbit-site/.orbit-account,
их токены и Orbit-overrides к нему не применяются. Родитель оболочки задаёт
только account-page-base/spot и раскладку; цвета/шрифты footer не задаёт.
Штатные фон, типографика, контейнер, отступы и responsive правила главной
сохранены без локальной адаптации; приоритет точного footer выше бесшовности.

Изменены только account-правила orbit.css, обёртка footer в orbit-shell.tsx
и эта карточка. Текущие формы/обработчики/подтверждение пароля/защита не
редактировались; предыдущие удаления декора и компактный глаз сохранены.
Применены уже прочитанные frontend-design/impeccable; рекомендации
web-animation-design учтены при сохранении анимации на меньшей геометрии.

Самопроверка исходников: Get-Content/rg, каскад selected/nav/theme,
реальные footer imports/обёртки/потребители и отсутствие локальных footer
переопределений; git status/branch/rev-parse/remote/rev-list/diff.
Основной checkout, ms-t009-identity-ui; PR #69 подтверждён open через connector.
Исходный/итоговый HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
HEAD tree 9ebce3b77133939e7e197d8c984cb48382ebd91e, результат dirty.
Локальный origin/main +7/-0 без fetch. Чужие изменения сохранены.
Визуальная проверка не проводилась. Тесты, сборка, typecheck, smoke и
браузерные прогоны: NOT_RUN_BY_USER_REQUEST. Merge/deploy не выполнялись.

## Уточнение фона, движения и подвала ЛК — 15.11.2026

Выполнены семь новых пунктов пользователя без редизайна. Мягкое пятно
вверху справа восстановлено на единой account-page-shell: radial-gradient
с плавным растворением, основной фон #e7f0f8 / #141a31 и пятно #c9ddfa /
#344c78. Внутренние поверхности страницы и подвала прозрачны; стык не
маскируется полосами/отрицательными отступами. Оболочка flex/min-height
сохраняет нормальное расположение короткого и длинного содержимого.

Палитра берётся из конечных .orbit-home и .orbit-materials-action в orbit.css.
Предыдущий перенос --primary #4f22f1 давал запрещённый теперь фиолетовый:
акценты, SVG currentColor, дуги, focus, границы и вторичные действия заменены
синим #233f70 / голубым #c9ddfa из видимой кнопки главной. Нейтральные
поверхности получены смешением этих цветов с фоном/белым. Главная не изменена.

Восстановлено исходное поведение .orbit-grade-disc из сохранённого orbit.css:
200ms ease для заливки/границы, 240ms ease для дуги и поворот до 35deg при
hover:fine. Геометрия hit area не движется. Reduced-motion отключает переходы
и hover-поворот; disabled не анимируется. Размер кругов 103→90px и 90→79px,
цифры 26→23px (mobile 22px), дуга -4px, сетка компактнее. Radio-логика и
подтверждённый класс не изменены. Галочки/точки/стрелки не возвращались.
Подложка password-toggle теперь отдельный центрированный псевдоэлемент
33px вместо окраски всей кнопки шириной 43px; hit area, svg, aria, focus
и переключение видимости сохранены, auth не затронут.

Подвал: тот же LessonFooter и home-lesson-footer, что в текущем OrbitShell
главной; вынесен из .orbit-site, чтобы получить штатные типографику,
ссылки и отступы вместо прежних Orbit-overrides. Только фон подвала ЛК
прозрачен. Главная ветка shell, шапка и общий компонент footer не менялись.
Изменены orbit-shell.tsx, account-scoped правила orbit.css и эта карточка.
Backend/API/формы/защита/подтверждение пароля не менялись.

Использованы прочитанные frontend-design, impeccable, web-animation-design,
ui-ux-pro-max (сохранение touch spacing, radio и focus). Самопроверка:
Get-Content и rg по реальным импортам, footer, hover/focus, исходным правилам,
каскаду и потребителям; git status/branch/rev-parse/remote/rev-list/diff.
PR #69 подтверждён open через GitHub connector. Ветка ms-t009-identity-ui,
исходный/итоговый HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
HEAD tree 9ebce3b77133939e7e197d8c984cb48382ebd91e; результат dirty.
Локальный origin/main: +7/-0, fetch не выполнялся, чужие изменения сохранены.
Тесты/build/typecheck/smoke/browser: NOT_RUN_BY_USER_REQUEST.
Визуальная проверка и приёмка не заявляются; merge/deploy не выполнялись.

## Точечная доработка восстановленного ЛК — 15.11.2026

По новому поручению композиция сохранена. Выполнены пять изменений:
палитра внутренней части согласована с итоговым каскадом главной в orbit.css;
удалён псевдоэлемент точки активной навигации; удалены галочка и подложка
выбранного класса, круги уменьшены с 125 до 103 CSS px (на узких экранах
до 90 px), согласованы цифры, дуги и сетка; удалены стрелки обеих кнопок
класса и круг стрелки материалов, отступы сделаны симметричными; уточнён
локальный SVG выхода с единой толщиной 1.6 и стрелкой за пределы двери.

Источник цветов — последний блок .orbit-home «Original Orbit colours» и
последние .orbit-materials-action/hover/active, а не перекрытые исторические
правила. Light: фон #e7f0f8c4/#e2f4fad7, текст #252943/#5c6381,
акцент #4f22f1, CTA #c9ddfa с текстом #233f70. Dark: #141a31/#1e294d,
текст #eef0ff/#b9c2e1, акцент #b5bfff, CTA #344c78/#edf3ff. Поверхности
#fafbff/#1d2542 наследуются главной от .orbit-site; границы и focus также
взяты из действующих токенов. Все новые правила ограничены .orbit-account;
переменные главной, header/footer и auth не менялись. Hover мгновенный,
вращение дуг и бегущая заливка кнопок внутри ЛК отключены; reduced-motion
общего сайта сохранён. Новых анимаций нет.

Изменены account-page.tsx (только декоративная разметка), identity-icon.tsx
(только logout), orbit.css (только оформление ЛК), эта карточка.
Сохранены native radio/required/defaultChecked и клавиатурная семантика,
отдельное сохранение класса, actual user/state, API, формы, подтверждение
пароля, owner guard, busy/blocked/retryAt, ошибки, почта и сеансы.
Использованы frontend-design, impeccable (refinement/craft-floor),
ui-ux-pro-max (поиск radio touch target spacing: интервалы и reflow),
web-animation-design для устранения существующего hover-движения.

Основной checkout C:/Projects/MathStart-Python, ветка ms-t009-identity-ui;
исходный и итоговый HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
HEAD tree 9ebce3b77133939e7e197d8c984cb48382ebd91e; результат незакоммичен.
Git root/branch/status/remote/rev-list прочитаны; локальный origin/main:
7 впереди, 0 позади (без fetch). GitHub connector подтвердил PR #69 open.
Чужие dirty-изменения сохранены, новых задач/merge/deploy нет.
Самопроверка исходников: Get-Content, rg по imports/потребителям и
декоративным элементам, git diff/status; разобран каскад и специфичность
новых селекторов, просмотрены обработчики и responsive правила.
Визуальная проверка не проводилась. Тесты, сборки, typecheck, smoke и
браузерные прогоны: NOT_RUN_BY_USER_REQUEST. Приёмка не заявляется.

## Восстановление по скриншоту — 15.11.2026

Пользователь прекратил эксперименты и поручил вернуть прежнюю визуальную
систему ЛК. Скриншот с подписью «Всё для занятий. И немного настроек.» является
целевым ориентиром; красная обводка кнопки является пометкой, не частью UI.
Требования нового дизайна, прежние эстетические запреты и обязательная
математическая анимация отменены для восстановления.

Источник оформления найден в сохранённом локальном
frontend/src/features/public-pages/orbit.css: .orbit-account и вложенные
account-* правила, включая обе темы, исходную ширину/отступы, боковое меню,
скругления и поля. CSS не переписывался. Структура боковой навигации и
разметка account/security взяты выборочно из Git HEAD a557ac1; прежняя
локальная orbit-разметка выбора класса восстановлена по ранее прочитанной
версии account-page.tsx в этом чате. Это не полный checkout Git-версии:
нынешние обработчики и актуальная функциональность сохранены.

Изменения: account-page.tsx вновь использует .orbit-account, прежний заголовок
и подпись, профиль, иконки, меню и account-layout; восстановлены все три раздела.
Сохранены текущие owner guard/accountRead, API, busy/blocked/retryAt, ошибки,
почта восстановления, управление сеансами, PasswordChangeForm с подтверждением
нового пароля и очисткой всех password-полей. Skeleton не восстановлен.
Геометрическая анимация и GradeChoice последнего варианта удалены.

Карта выведенного файла: frontend/src/features/identity/account-workspace.css
был создан в отклонённых итерациях этого чата; единственный import в
account-page.tsx удалён, потребителей в frontend больше нет. Файл удалён,
его оформление заменено существующими исходными правилами orbit.css.
Header/footer/OrbitShell, главная, каталог, уроки, auth, backend, миграции
и БД в этом восстановлении не менялись. Остальные dirty-правки сохранены.

Ветка ms-t009-identity-ui, основной checkout, исходный и итоговый HEAD
 a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92 (изменения незакоммичены).
Git root/remote/status/rev-list/log прочитаны; относительно локального
origin/main 7 впереди / 0 позади, fetch не выполнялся. Исходный HEAD tree
9ebce3b77133939e7e197d8c984cb48382ebd91e.
Самопроверка исходников: Get-Content, git show и rg, импорты/потребители,
сохранение обработчиков и подтверждения пароля. Восстановление внешнего
вида в браузере не проверялось. Тесты, build, typecheck, smoke и дополнительные
браузерные прогоны: NOT_RUN_BY_USER_REQUEST. Новая задача, merge и deploy
не выполнялись; пользовательская приёмка не заявляется.

## Отклонённый вариант: раскрывающийся рабочий лист — 15.11.2026

Поручение пользователя: предыдущая композиция снова отклонена, требуется новая
организация кабинета без промежуточного выбора макета. Визуальные запреты и
границы сохранены. Ветка ms-t009-identity-ui, основной checkout; исходный и
итоговый HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92. HEAD tree
9ebce3b77133939e7e197d8c984cb48382ebd91e; результат dirty, чужие изменения
сохранены. GitHub connector подтвердил PR #69 OPEN. Git root/remote/ветка
прочитаны, отношение к локальному origin/main 7 впереди / 0 позади;
fetch не выполнялся. Issue/PR не дублировались, merge не выполнялся.

Рассмотрены три структуры: (1) раскрывающийся рабочий лист с выбором класса
сразу в содержимом; (2) постоянная панель действий и выдвижные настройки;
(3) единая длинная страница с якорями. Выбрана первая: все разделы видимы,
есть явное раскрытие на месте, нет наложений и отдельных мобильных режимов
панели. Вторая требовала управления оверлеем и скрывала формы; третья
постоянно занимала страницу редкими password/session действиями. Главная
причина отказа от прежних решений: меню, класс и иллюстрация оставались тремя
независимыми блоками, независимо от цвета.

Новая система: строки «Мой класс», «Аккаунт», «Безопасность» образуют один
лист. Открыт один раздел, можно свернуть все. Ссылки ?section=account/security
сохранены. Выбор класса всегда видим в открытом учебном разделе; radio-шкала
отмечает сохранённый класс словом «Ваш» и полной доступной подписью. Draft
отделён от сохранённого значения. При изменении появляются действующие
«Сохранить выбор» и «Отменить»; материалы ведут именно в сохранённый класс.
Первый вход без класса поддержан. Успех занимает короткую строку без постоянного
резерва; прежний таймер 4,5 с очищает только подтверждённое сохранение.

Настройки также пересобраны: информация о почте слева, форма справа;
пароль и отзыв сеансов двумя различимыми группами без карточек. На телефоне
всё выстраивается последовательно. Поля, подтверждение нового пароля,
ошибки, autocomplete, owner guard, API и busy/blocked/retryAt сохранены.
Никаких backend/schema/DB изменений. Шапка/footer и остальные страницы
в этом проходе не редактировались.

Палитра: нейтральный фон #e3dfd8, текст #292a33, винный акцент #842c47;
тёмная тема #282b34 / #eeece9 / #eda6af. Golos Text из существующего
локального font-face. Акцент связывает раскрытый раздел, выбранный radio,
действия и геометрию. Целиком заменён account-workspace.css, все селекторы
под .ms-workspace, прежние tab/dissection правила удалены из этого файла.

Математический мотив теперь поперечный, между шкалой класса и строкой
действий: сдвиг прямоугольника в параллелограмм с сохранением b, h и площади.
CSS skewX от 0 к +32°, затем через 0 к -32°, цикл 7 с, cubic-bezier(.45,0,.55,1).
Рисунок занимает около 69% ширины полосы; SVG растягивается адаптивно,
изменение площади за цикл отсутствует (детерминант сдвига 1). Неподвижный
контур позволяет сравнить исходную форму. Фигура не пересекает поля и кнопки.
Пауза доступна кнопкой с aria-pressed, продолжение с текущей позиции;
reduced-motion отключает keyframes и оставляет статичный сдвиг 18°.
Hover-анимаций, дополнительных библиотек и новых сетевых ассетов нет.

Скиллы: frontend-design — три структуры, единый принцип листа и типографика;
impeccable/Operate/craft-floor — выбор знакомых раскрывающих контролов и
согласованные формы; web-animation-design — один мотив на transform, easing,
пауза/reduced-motion; ui-ux-pro-max — выборочный поиск accordion/keyboard/focus,
явные labels, цели 44px+, focus без перекрывающих панелей.
Новое исследование: GOV.UK Accordion (https://design-system.service.gov.uk/components/accordion/default/)
открыт и раздел раскрыт, состояние подтверждено accessibility tree. Math is Fun
https://www.mathsisfun.com/geometry/parallelogram.html открыт через поиск сайта,
прочитаны структура примера и описание площади. Первый guessed URL дал 404.
Снимки обоих источников браузер вернуть не смог, включая повторный видимый
пример GOV.UK после чтения troubleshooting. Поэтому это исследование структуры
и взаимодействия, НЕ подтверждённое визуальное исследование экранов.
Эстетическое качество этих источников и их анимация не заявляются изученными.

Самопроверка исходников: JSX, реальные импорты/маршруты, формы, контролируемый
draft, область CSS, отсутствующие DOM targets у закрытых разделов (aria-controls
указывается только при раскрытии), крайние размеры сдвига и запас viewBox,
обе группы цветовых tokens, адаптивные правила. Команды: Get-Content, rg,
git status/rev-parse/remote/rev-list, Get-FileHash. Результат SHA256:
account-page.tsx 10847DB45DA555E24EF96ACA03BB666D85477F9B387A43BDFBC862D6CA9C6004;
account-workspace.css 0085A3E92F47BD984D2A795D2E3210506C1FCC997C886BEF04DECCA8FE69DC7D.
Тесты, build, typecheck, smoke, detector и локальные браузерные прогоны:
NOT_RUN_BY_USER_REQUEST. Рендер и движение результата не наблюдались,
плавность/визуальное качество не подтверждены. Независимое ревью и приёмка
PENDING, следующая карточка не начата.

## Отклонённый вариант: геометрическое преобразование — 14.11.2026

Зелёный вариант отклонён пользователем вместе с композицией. Новое поручение
полностью заменяет его визуальное направление. Основной checkout и ветка
ms-t009-identity-ui, исходный и итоговый HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
HEAD tree 9ebce3b77133939e7e197d8c984cb48382ebd91e. Новый результат остаётся
незакоммиченным поверх исходных dirty-правок. Git root/remote/ветка проверены;
локальный origin/main: впереди 7, позади 0, fetch в этом проходе не выполнялся.
GitHub connector подтвердил существующий PR #69 OPEN; дубликаты не создавались.

Композиция: заголовок и пользователь в одной строке, горизонтальная навигация,
открытая рабочая область с сохранённым классом/переходом к материалам слева
и крупным преобразованием четырёх треугольников справа. Бокового меню,
цветного баннера и старого чертежа нет. Смена класса раскрывается отдельно,
при первом входе открыта. Выбор класса компактной полосой настоящих radio.
Статус подтверждённого сохранения без заливки/рамки, очищается через 4,5 с;
ошибки и security notices автоматически не скрываются.

Цвет: фон #e8ebf0, текст #202c45, синий #2c4fb2; тёмный фон #202838,
текст #e9edf6, действие #b1c5ff. Голос интерфейса Golos Text. Медный акцент
только в геометрии. Формы аккаунта и безопасности оформлены общей локальной
системой полей, подписей и кнопок без внешних панелей. Обе темы и мобильные
правила описаны в CSS; длинные логины/email переносятся.

Анимация: SVG из четырёх равных треугольников, CSS translate/rotate,
цикл 9 с с cubic-bezier(.65,0,.35,1), начало без взаимодействия.
Пауза через animation-play-state и кнопку с aria-pressed; продолжение
с текущей позиции. prefers-reduced-motion полностью отключает движение,
остаётся собранный квадрат; управляющая кнопка скрыта. На телефоне фигура
остаётся под действиями, а не исчезает. Изменений размеров в keyframes нет,
hover-анимаций, дополнительных библиотек и запросов за ассетами нет.

Применение скиллов: frontend-design — пересборка композиции и пропорций,
impeccable/Operate и craft-floor — компактность форм и сдержанный chrome,
web-animation-design — единый мотив, easing, пауза и reduced motion,
ui-ux-pro-max — выборочный поиск reduced motion/excessive motion,
подписи radio, touch targets, видимый focus.
Визуальные источники этого прохода:
- https://linear.app/docs/account-preferences — открыт и увеличен настоящий
  screenshot Preferences. Применены группировка и плотность форм; интерактивные
  настройки внутри самого Linear не открывались.
- https://polypad.amplify.com/p (переход с mathigon.org/polypad) — просмотрены
  рабочая область и раскрытие Tangram. Применены читаемые составные фигуры
  и разделение инструментов/содержимого; палитра и оболочка не копировались.
  Чужая анимация в этих источниках не изучалась; движение спроектировано по
  геометрии и web-animation-design.

Реализация: account-page.tsx (внутренняя разметка, GeometryStudy, таймер
подтверждённого сохранения), целиком заменён account-workspace.css.
Стили только под .ms-workspace; старые workspace-sidebar/course правила
удалены из локального файла, orbit-account/account-* не используются.
Обработчики API, owner guard, busy/blocked/retryAt, поля подтверждения
пароля и их очистка сохранены. Общая оболочка/header/footer, auth, остальные
страницы и backend в этом проходе не редактировались.

Самопроверка исходников: JSX и imports, потребители CSS, охват селекторов,
формы, состояния ошибок/disabled/focus, очистка таймера, pause/reduced-motion,
адаптивные правила и размер viewBox с запасом на поворот. Команды чтения:
Get-Content, rg, git status/rev-parse/remote/rev-list/diff; чтение PR connector.
Тесты, typecheck, build, smoke, detector и локальный браузерный просмотр:
NOT_RUN_BY_USER_REQUEST. Анализ текущего отклонённого экрана выполнен по
разметке/CSS и конкретным замечаниям пользователя, не по новому screenshot.
Рендер и фактическое движение новой анимации не наблюдались; визуальное
качество и runtime-плавность не подтверждены. Независимое ревью и человеческая
приёмка PENDING. Merge/deploy не выполнялись, следующая карточка не начата.

## Новое поручение: внутренняя композиция ЛК — 14.11.2026

Пользователь разрешил перепроектировать только внутреннюю часть действующего
ЛК. Шапка/footer, главная, каталог, уроки и отдельная авторизация вне scope.
История предыдущих решений сохраняется; окончательная приёмка и merge за пользователем.
Исходный HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92, существующая dirty-ветка
ms-t009-identity-ui. Обработчики AccountPage и PasswordChangeForm прочитаны:
сохранены owner guard, API calls, busy/blocked/retryAt, подтверждение пароля,
обработка неизвестного результата, редиректы и реальные статусы почты.

Выбрана горизонтальная навигация вместо бокового меню, компактная строка профиля,
одна рабочая поверхность; выбор класса прямоугольными radio-плитками, материалы
справа на desktop и ниже на телефоне. Формы имеют ограниченную читаемую ширину.
Сравнивались sidebar-настройки, сетка одинаковых карточек и горизонтальная рабочая
область; последняя соответствует трём разделам без лишнего chrome.
Применены frontend-design, Impeccable/Operate и craft-floor, web-animation-design,
UI/UX Pro Max (подписи, touch targets, focus, адаптивная навигация).
Taste Skill в установленном каталоге не обнаружен и не применялся.

Источники: https://linear.app/docs/account-preferences (визуально изучен скриншот
настроек и его увеличение); https://www.notion.com/help/account-settings
(документация группировки настроек); https://supahero.io/ (галерея теперь ссылается
на screensdesign). Интерактивные настройки за авторизацией не проверялись.
Графический источник — приложенная пользователем «Сборка»: компактная статичная
композиция из арки, четверти круга и ступеней. Постоянного движения нет;
только цветовые реакции 160ms, отключаемые reduced-motion.

Реализация: локальный account-workspace.css, подключённый существующим компонентом;
в JSX изменено только вступление с декоративным SVG. Доменная логика не изменена.
Стили ограничены .orbit-account; обе темы. Сохранено для штатного HMR.
Самопроверка исходников выполнена; runtime/браузерные прогоны, тесты и сборка:
NOT_RUN_BY_USER_REQUEST. Визуальная приёмка реализации не заявляется.

## Упрощение поверхности и пропорций CTA — 14.11.2026

После замечания пользователя пересмотрены силуэт и визуальный вес кнопки
по frontend-design и Impeccable. Убраны градиент и видимая рамка; ширина теперь
определяется надписью и padding26px, минимум высоты56px, радиус22px, вес550.
Светлая тема: спокойная синяя заливка с тёмной надписью; тёмная: приглушённая
синяя поверхность со светлой надписью вместо яркого светлого прямоугольника.
Текст, ссылка, место, мгновенные состояния и keyboard focus сохранены.
Изменены только локальные стили CTA, сохранено для штатного HMR.
Браузерные прогоны, тесты и сборка: NOT_RUN_BY_USER_REQUEST.
Визуальная проверка реализации не заявляется.

## Уточнение тональной кнопки — 14.11.2026

Пользователь отметил тональный вариант как более удачный и поручил доработку.
Сохранены надпись, центрирование и светлая синяя поверхность. По frontend-design
и Impeccable уточнена поверхность: небольшой перепад светлоты сверху вниз,
тонкий согласованный край без тени; размер минимум 260×60px, радиус 16px.
Отдельные значения для обеих тем, мгновенные hover/press и keyboard focus.
Только локальные стили кнопки; ссылка, место и остальная страница сохранены.
Файлы сохранены для штатного HMR. Браузерные прогоны, тесты и сборка:
NOT_RUN_BY_USER_REQUEST; визуальная проверка этой итерации не заявляется.

## Тональное действие вместо тёмной кнопки — 14.11.2026

Сатиновая синяя кнопка со стрелкой отклонена пользователем. Повторно прочитаны
frontend-design и Impeccable, включая polish и craft-floor. Выбран ранее
рассмотренный подход tonal Material: самостоятельная светлая синяя поверхность,
тёмно-синяя надпись «Открыть материалы», без стрелки, стекла, градиента и тени.
Центрированная подпись, радиус 16px, минимум 248×58px; отдельные цвета обеих
тем и мгновенные hover/press, существующий keyboard focus. Ссылка /materials
и место кнопки сохранены. Изменены только CTA и его локальные стили;
ручная палитра страницы не затронута. Файлы сохранены для штатного HMR.
Браузерные прогоны, тесты и сборка: NOT_RUN_BY_USER_REQUEST.
Визуальная проверка этой итерации не выполнялась; приёмка не заявляется.

## Пересмотр CTA после отклонения стекла — 14.11.2026

Стеклянная кнопка пользователем отклонена. Повторно применены frontend-design
и Impeccable/polish: проблема признана концептуальным несоответствием,
а не поводом добавлять блики. Удалены стекло, backdrop-filter, прозрачность,
световые слои и тени. Новое действие «Выбрать тему» → /materials: плотная
глубокая синяя поверхность с небольшим сатиновым перепадом светлоты,
радиус14px, минимум256×60px. Короткая надпись слева, неподвижная контурная
стрелка справа без отдельного круга/фона. Синий связан с логотипом, белая
надпись контрастна обеим темам. Hover/press мгновенные, focus сохранён.
Решение использует иерархию действия и пропорции вместо оптических украшений.
Остальная страница и ручные цвета не изменены. Штатный HMR; без локальных
браузерных прогонов, тестов/build. Визуальная проверка реализации не заявляется.

## Тонированная стеклянная поверхность CTA — 14.11.2026

Сплошная фиолетовая кнопка отклонена. Пользователь явно разрешил стекло,
градиент/блик, скругления и небольшую тень только для этого CTA. Применены
frontend-design и Impeccable. Визуально изучены официальные страницы
[Apple Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons),
[Apple Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
и [Material Buttons](https://m3.material.io/components/buttons/overview), включая
иллюстрации Apple и сравнение elevated/filled/tonal/outlined/text Google.
Сравнены плотное iOS-действие, tonal Material и тонированная стеклянная поверхность.
Выбрано последнее: на спокойном фоне чистое размытие не дало бы материала,
поэтому поверхность формируют собственный световой градиент, верхний блик,
контрастный край и лёгкая смещённая тень. Это веб-интерпретация, не нативный
Liquid Glass. Текст «Открыть материалы» и реальный href/materials сохранены.
Радиус18px, область248×60px minimum, вес550; без иконки/круга/стрелки.
Отдельные local CTA tokens обеих тем, без изменения цветов остальной страницы.
Fallback непрозрачный по умолчанию; @supports включает полупрозрачность и blur,
prefers-reduced-transparency возвращает плотную поверхность. Hover/press
мгновенные, focus сохранён, анимации не добавлены. Правки только CSS кнопки.
Штатный HMR; локальные браузерные прогоны/тесты/build/ожидание цикла не выполнялись.
Визуальная проверка реализации не заявляется.

## Законченное решение основной кнопки — 14.11.2026

По поручению изменён только CTA главной на прежнем месте: «Открыть материалы»
→ /materials, без иконки, плотная заливка текущим --primary, умеренный радиус12px,
минимум248×60px с ограничением шириной родителя. Никаких кругов/стрелок/теней
или hover-анимаций. Цвет текста --primary-foreground в обеих темах, мгновенный
hover/press через разные оттенки заливки; keyboard outline3px/offset5px сохранён.
Ручные токены страницы не изменены. Остальной контент/геометрия/ЛК не тронуты.

Явно применены frontend-design и Impeccable. Короткое визуальное исследование:
[Zed в Supahero](https://supahero.io/hero/zed), [оригинал Zed](https://zed.dev/),
[оригинал Figma](https://www.figma.com/). В галерее Zed — компактное залитое
основное действие рядом со вторичным; на текущем оригинале также ясно различим
вес filled/secondary. На Figma — текстовое filled-действие без обязательной
иконки. Карточка Figma в Supahero открыта, но изображение не отобразилось и
как визуальное подтверждение не используется.
Сравнены контурное действие, текстовая ссылка и залитая кнопка. Выбрана залитая:
чёткий центр действия на мягком фоне, без конкуренции с тонкой орбитальной
графикой; убраны книга/длинная подпись, изменены силуэт и пропорции.
Штатный HMR. Локальные браузерные прогоны, тесты/build, detector и ожидание
цикла NOT_RUN_BY_USER_REQUEST; визуальная проверка реализации не заявляется.

## Фокус поиска в шапке «Материалов» — 14.11.2026

Источник боковых синих полос: общий .orbit-site input:focus-visible имел
большую специфичность, чем прежнее отключение input outline в поиске;
outline3px/offset5px обрезался overflow:hidden раскрывающегося контейнера.
Локально в .orbit-header-only .catalogue-search-field убрана внутренняя
обводка input при focus. Единственный focus-visible индикатор перенесён на
контейнер через :has(input:focus-visible), outline2px с внутренним offset-2px:
не обрезается, не меняет размеры. Обычная рамка focus-within сохранена.
Глобальные outline не отключены, поведение поиска не менялось.
Штатный HMR; без браузерных прогонов, тестов/build по поручению пользователя.

## Общая шапка главной и «Материалов» — 14.11.2026

Оформление шапки главной подключено в каталог через OrbitHeader — общий
адаптер существующего LessonHeader. showCatalogueLink=false скрывает ссылку
текущего раздела. Существующие leading/actions каталога переданы без изменения:
лупа, refs, раскрытие/очистка поиска, Escape, outside dismiss, focus и меню
сохранены. Theme/AuthLink остаются общими. Оформление ограничено обёрткой
шапки orbit-header-only; токены не затрагивают содержимое каталога/фильтры.
Для главной contained-вариант возвращает прежнюю разметку без новой обёртки.
Каталог сохраняет sticky-поведение, верхний отступ fixed sidebar согласован
с новой высотой шапки98px/80px. Учебные страницы и ЛК не переделаны.
Штатный HMR, без браузерных прогонов, тестов/build по поручению пользователя.

## Пауза на спирали и общий подвал урока — 14.11.2026

Отдельный нижний контрол и его строка удалены. Тот же SVG помещён в нативный
button с aria-label действия/aria-pressed пользовательской паузы; Tab и
Enter/Space работают нативно, focus видим. Прозрачная эллиптическая область
вокруг спирали принимает мышь/касание, остальной прямоугольник SVG пропускает
нажатия. Размер viewport/положение/scale/геометрия/цвета не изменены.
Сохраняется animation-play-state вместо сброса animation, localStorage паузы,
offscreen и prefers-reduced-motion. Нижний padding70→24, min-height656→636:
место под удалённую кнопку убрано, необходимая высота движения рисунка оставлена.

Подвал уже использовал LessonFooter. Источник: shared/lesson/lesson-shell.tsx
и lesson-shell.css, контекст типографики lesson.css (17px/1.85, --font-sans).
Причина увеличения: Orbit переопределял footer-main padding-block45px сверх
общего footer-inner44px/20px, max-width, inline-padding, шрифт и theme tokens.
Только на главной общий footer вынесен из .orbit-site, поэтому использует
реальные общие стили и root tokens без этих переопределений. Контекст шрифта
урока задан родителю; shared margin-top16px имеет поверхность footer, а не
промежуточную светлую полосу. Компонент не скопирован; ЛК остаётся как был.
Штатный HMR. Браузерные прогоны, тесты/build и ожидание цикла не выполнялись
по поручению пользователя. Визуальная проверка не заявляется.

## Геометрия и экранная толщина без изменения ручных цветов — 14.11.2026

Текущее поручение ограничено геометрией и stroke. Существующее форматирование
и ручные цвета сохранены. Внешние полуоси600/265→630/278 (около5%), внутренние
346/95→350/85. Число витков14→11: реальный шаг увеличен, а не только масштаб
готового рисунка. При desktop масштабе около0.54–0.58 дополнительный чистый
просвет после утолщения составляет примерно2px на широких сторонах спирали;
у концов эллипса он отличается вследствие эллиптической геометрии.
Один массив координат задаёт путь линии/точки; размер точки и timing сохранены.
Desktop stroke = прежний SVG stroke + 1/s, где s учитывает ширину60% hero,
max-width1380px, viewBox1500×850, высоту470px и внешний scale1.05. Это добавляет
один экранный CSS px к обычным и акцентным линиям, адаптируясь к desktop ширине.
Mobile stroke и размеры SVG сохранены. Тексты/кнопка/центр/наклон не сдвигались.
Штатный HMR; без браузерных прогонов, тестов/build и ожидания цикла.
Визуальная проверка не заявляется.

## Небольшое раздвижение и подъём композиции — 14.11.2026

По текущему поручению на desktop от1101px левый блок целиком сдвинут на12px
влево, верхний отступ hero68→44px, top орбиты180→156px и правой колонки230→206px.
Hero min-height680→656px. На широком viewport от1500px колонка дополнительно
сдвинута вправо right1%→0 внутри центрированного max-width1380px контейнера;
на меньших ширинах прежний отступ сохранён для защиты края экрана.
SVG целиком увеличен на5% относительно центра спирали; path и точка находятся
внутри общего масштаба. Геометрия/наклон/темп не менялись. Mobile, палитра,
фон, тексты/типографика, форма CTA, шапка/footer и ЛК сохранены.
Штатный HMR, без ожидания цикла, браузерных прогонов, тестов/build.

## Два небольших смещения — 14.11.2026

По текущему поручению малая ось спирали увеличена примерно на8%:
ry245→88 заменены на265→95; длинная ось, центр, наклон и контейнер сохранены.
Линия и offset-path точки используют один обновлённый массив координат.
Правая колонка только при min-width1101px сдвинута вправо: right2.5%→1%,
top230px и ширина25%/max330px сохранены. Цвета и остальные элементы не менялись.
Штатный HMR; без браузерных прогонов, ожидания цикла, тестов/build.

## Возврат только исходной сиреневой палитры — 14.11.2026

Прямое поручение со скриншотом отменяет запрет фиолетового для этой правки.
Точные light/dark значения восстановлены из сохранившихся исходных переменных
.orbit-site в начале orbit.css, но применены только на .orbit-home:
light #f1f3fc/#252943, линии #7989cc, точка #f2b799, акцент #4655c6;
dark #141a31/#eef0ff, линии #7e91e4, точка #f2c3a6, акцент #b5bfff.
Восстановлены мягкие общие фоновые слои #e2e6fa/#dce0ff и #1e294d/#283568.
Контур/текст/состояния текущей кнопки согласованы с этими акцентами;
форма, размеры и надпись кнопки сохранены. Геометрия/положение/размер орбиты,
оба текстовых блока, спиральная траектория/пауза/reduced-motion, адаптивность
и нулевой margin перед footer не менялись. Капсула и подпись классов не возвращены.
ЛК и другие страницы не перекрашивались. Файлы целиком не откатывались.
Штатный HMR; браузерные прогоны/тесты/build/ожидание цикла не выполнялись
по поручению пользователя. Визуальная проверка не заявляется.

## Графическое цветовое поле — 14.11.2026

Тёмная световая версия отклонена («Плохо. Еще»). Вместо пятен применена
графическая диагональная композиция: светлая нейтральная область текста,
синие плоскости в нижней правой области, насыщенная синяя спираль и
красно-оранжевая точка. В dark сохранена структура плоскостей с отдельными
контрастными значениями. Форма/текст CTA сохранены, цвет контура согласован.
Остальная вёрстка и анимация не менялись. Правки через HMR без браузерных
прогонов, тестов/build; результат визуально не проверялся.

## Композиционный фон вместо перебора заливок — 14.11.2026

По замечанию пользователя одноцветные замены признаны недостаточными.
Малиновая заливка заменена пространственной системой: чернильная основа,
широкий диагональный свет вдоль длинной оси орбиты и локальный тёплый
отражённый свет у нижнего края. Светлые стальные линии и медно-светлая точка
поддерживают рисунок; область основного текста спокойнее. Все слои общие
для main. Dark имеет более глубокую основу и приглушённый свет, контраст текста
сохранён подбором светлых значений. Форма CTA/композиция/геометрия/поведение
не изменены. Штатный HMR; браузерные прогоны/тесты/build не запускались.

## Замена янтарной палитры — 14.11.2026

По короткому поручению «Меняй палитру» заменена только цветовая система главной:
малиново-красная направленная поверхность, светлый текст, тёмная винно-чернильная
орбита и светлая точка; dark — глубокая винная поверхность, светлые линии,
ледяной маркер. Контур CTA осветлён для читаемости, форма и поведение сохранены.
Геометрия, расположение, анимация и остальные страницы не менялись.
Штатный HMR, без браузерных прогонов/тестов/build; NOT_RUN_BY_USER_REQUEST.

## Поперечное расширение и подъём колонки — последующее поручение 14.11.2026

Малая ось спирали увеличена: ry168→48 заменены на245→88 при прежней длинной
оси rx600→346 и наклоне. Видимая линия и траектория точки получают одни новые
координаты. Desktop правая колонка целиком поднята с top300 до230px,
сдвинута вправо right4%→2.5%, ширина25%/max330px сохранена. Mobile остаётся
последовательным. Остальные тексты, CTA, шапка/footer и ЛК не переделаны.

Почти белая поверхность с бледными красными линиями отклонена. Применена
насыщенная янтарная поверхность с направленным переходом к охре, тёмная
чернильная орбита и синий маркер. В dark — глубокая бронзовая поверхность,
контрастные светлые линии и светло-синий маркер. Усилены насыщенность линий,
толщина и opacity. Это полная локальная система main, без размытого пятна.
Применены frontend-design и Impeccable. Текущий HMR; дополнительные браузерные
прогоны, тесты/build и ожидание цикла NOT_RUN_BY_USER_REQUEST. Визуальная
проверка не заявляется. Пауза/reduced-motion и чистый стык footer сохранены.

## Диагональная спираль и стык footer — последующее поручение 14.11.2026

По двум скриншотам изменены только палитра, протяжённость спирали и стык footer.
Вместо серого фона с жёлтым пятном — светлая ахроматическая поверхность с
диагональным переходом к холодной нейтральной глубине; цвет сосредоточен в
кирпично-красных линиях спирали и синей точке в гармонии с логотипом. В dark:
угольная поверхность, светлые красно-медные линии и светло-синий маркер.
Размытый световой слой выключен; повторных фонов секций нет.

Геометрия rx361→208 заменена на600→346, ry190→54 на168→48 при прежнем
наклоне: спираль действительно вытянута по диагонали, а не просто перемещена.
Один массив координат по-прежнему задаёт видимый path и offset-path точки.
Расширен viewBox, согласован desktop размер контейнера; mobile SVG ограничен
100% доступной ширины с новым aspect-ratio. Пауза, reduced-motion и 360s
в сторону сохранены. Применены frontend-design, Impeccable, web-animation-design.

Причина промежуточной полосы найдена в shared/lesson/lesson-shell.css:
.lesson-footer имеет margin-top:16px, показывающий фон оболочки. Обнулён
только через .orbit-home + .lesson-footer; shared footer/ЛК не менялись,
внутренние отступы и состав подвала сохранены.
Штатный host-dev/HMR. Браузерные прогоны, тесты/build и ожидание цикла:
NOT_RUN_BY_USER_REQUEST. Визуальная проверка итерации не заявляется.

## Подъём композиции по скриншоту — 14.11.2026

По приложенному скриншоту на широком desktop орбита вынесена из нижнего ряда
в центральную область hero (top180px, left23%, width50%, height430px), что
увеличивает её относительно прежнего узкого grid-слота и поднимает выше.
Правая колонка поднята на top300px, справа4%, width25% до330px, отдельно
от области иллюстрации. Hero min-height680px. На ширинах до1100px сохранена
потоковая композиция, на телефоне последовательный порядок без наложений.
Главный текст/описание/CTA, шапка/footer/ЛК не переделывались.

Персиковая палитра отклонена. Новая система: нейтральная серебристая основа,
локальный приглушённый золотой свет в области спирали, синие линии и янтарная
точка. Dark — нейтральный графит, тот же локальный тёплый акцент, светло-синие
линии. Это общие слои main без повторения по секциям. Логотип сохранён.
Геометрия/траектория/темп/пауза/reduced-motion сохранены. Применены
frontend-design и Impeccable. Штатный HMR; дополнительные браузерные прогоны,
тесты/build и ожидание цикла NOT_RUN_BY_USER_REQUEST. Визуальная проверка
нового результата не заявляется; приёмка остаётся за пользователем.

## Композиция с правой колонкой — последующее поручение 14.11.2026

Точечно удалена только подпись классов внизу hero. Единственный блок «Есть тема.
Будет понимание» с прежними абзацами перенесён внутрь основной композиции:
desktop — читаемая правая колонка 280–330px, уменьшенная спираль ниже вводного
текста в соседней широкой области. Прежняя нижняя секция удалена без дублирования.
На mobile последовательность: заголовок/описание/CTA, спираль, пояснения, пауза.
Геометрия path, наклон, точка на общем пути, timing, pause и reduced-motion
сохранены; изменён только внешний размер SVG и его размещение в layout.

Новая локальная палитра: светлая коралловая поверхность с тёплым светом,
сине-стальные линии и медная точка; dark — тёплый угольный фон, светлые
стальные линии и золотистый маркер. Фон единый на main, логотип прежний синий.
Контурная форма CTA сохранена. Применены frontend-design и Impeccable.
Скриншот со стрелкой в текущем сообщении недоступен; размещение выполнено
по текстовому указанию «ближе к центру и ниже» с отдельными областями grid.
Изменения в штатном host-dev/HMR; браузерные прогоны, ожидание цикла,
дополнительные проверки/тесты/build не выполнялись: NOT_RUN_BY_USER_REQUEST.
Визуальная проверка этой итерации не заявляется. ЛК/auth и backend не менялись.

## Только фон и основная кнопка — последующее уточнение 14.11.2026

Предыдущие фон/CTA не понравились пользователю. Точечно изменены home CSS
и разметка только ссылки материалов: общий небесно-синий фон с более насыщенной
правой частью, в dark глубокий синий; слои остаются общими для hero/story.
Цвета текста и самой спирали/точки, геометрия и анимационные правила сохранены.
CTA «К учебным материалам» — контурное действие с небольшой иконкой раскрытой
книги, почти прямыми углами и большей областью нажатия; мгновенная заливка
hover/press, без теней/анимации/вложенного круга/стрелки. Focus сохранён.
Применены frontend-design и Impeccable с учётом конкретных замечаний.
Правки сохранены в текущем host-dev для штатного HMR. По прямому поручению
новые браузерные просмотры, ожидание цикла, дополнительные проверки, тесты,
build и detector НЕ выполнялись: NOT_RUN_BY_USER_REQUEST.
Новая визуальная приёмка не заявляется. Остальная страница и ЛК не менялись.

## Четыре локальные доработки главной — 14.11.2026

Текущее поручение: новая палитра только внутри главной, меньшая точка,
замена CTA и немного более свободная спираль. Это не новая концепция сайта
и не возобновление отклонённого большого списка. ЛК/auth, шапка, footer,
шрифты, остальные тексты и backend сохранены. История ниже не удаляется.
Исходный HEAD и проверяемая основа: a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92,
ветка ms-t009-identity-ui, поверх существующего dirty tree; новые правки локальны.

Визуально изучены реальные страницы и изображения галереи:
- [Dropbox в Supahero](https://supahero.io/hero/dropbox-brand-guidelines)
  и [оригинал](https://brand.dropbox.com/): чистый брендовый синий,
  контрастные цветовые пары. Многоцветную мозаику в MathStart не переносим.
- [Zed в Supahero](https://supahero.io/hero/zed) и [текущий оригинал](https://zed.dev/):
  архивный пример с синим на светлой поверхности; текущая страница визуально
  отличается и сочетает синие/красные действия с нейтральной основой.
- Вне галереи: поиск и просмотр [CERN Design Guidelines](https://design-guidelines.web.cern.ch/),
  отделение контрастного текста от научной графики. Это ориентир ясности,
  не источник готовой палитры MathStart.
Дополнительно открыта карточка Superlist, но оригинал не загрузился;
не используется как подтверждённый визуальный референс.

Выбор: холодный нейтральный #f0f2f4, тёмный текст #202e43, синий CTA #245bce,
сине-стальные линии #6486b7 и маленький киноварный маркер #bc4337.
Общий мягкий свет hero/story остаётся одним слоем на main. В dark: #151c26,
#edf2f8, #9dbfff, #7196c7, #ef8273 соответственно. Переменные ограничены
.orbit-home и не перекрашивают ЛК, шапку, footer или другие страницы.
Расчёт контраста CTA: light 6.06:1, dark 8.20:1; пояснения относительно
наиболее насыщенного фонового света: 4.89:1 / 6.10:1.

CTA «Выбрать тему» ведёт в существующий /materials: прямоугольник с радиусом
6px, высота не менее 54px, без круга/стрелки/теней/hover-анимации; мгновенные
hover/press и keyboard outline. Точка r8→r6. Спираль 18→14 непрерывных витков
при прежних rx361→208 / ry190→54 и наклоне; шаг увеличен примерно на 2–3px
при desktop масштабе. Один вычисленный path используется линией и движением.
Desktop сдвиг дополнительно 18px вправо. На узком телефоне SVG помещён целиком,
чтобы прежнее обрезание слева не скрывало точку. Остальная композиция сохранена.
Темп 360s в каждую сторону, плавные концы, pause/offscreen/reduced-motion сохранены.

Явно применены frontend-design, Impeccable и web-animation-design.
Автотесты, build и автоматический design detector: NOT_RUN_BY_USER_REQUEST.
Ручной просмотр через существующий host-dev/HMR http://127.0.0.1:8131/:
1280×900 и 390×844, обе темы, общий фон до footer, keyboard focus,
пауза/продолжение. Наблюдение длилось более полного 12-минутного цикла
без ускорения: контрольные кадры наружного/среднего/внутреннего участков,
внутренний разворот и возвращение к следующему проходу; это выборочные
визуальные кадры во времени, не покадровая видеопроверка. Точка на линии,
наложения на текст, горизонтальный scroll и шов hero/story не обнаружены.
Пауза удерживает точное offset-distance, продолжение без сброса. Reduced-motion
сохранён в CSS; системное предпочтение устройства не менялось.
Независимое ревью/приёмка PENDING, merge нет.

## Непрерывная спираль и замедление точки — 14.11.2026

Локально заменена только геометрия иллюстрации/траектория: один открытый path
из 18 вытянутых витков в прежних пределах rx361→208 / ry190→54, прежние
translate/rotate/viewBox. Видимая линия и offset-path точки используют один d;
акцентные участки повторяют ту же кривую. CSS offset-distance даёт движение
по длине, с коротким торможением у концов и alternate обратно по той же линии.
Цвет/размер точки, положение рисунка, фон, тексты, layout и ЛК не переделаны.
Пауза/offscreen и reduced-motion подключены к новому traveller. Библиотек нет.

Первый темп 72 s в одну сторону отклонён пользователем прямо во время просмотра
как слишком быстрый. Немедленно замедлено в пять раз: 360 s внутрь, 360 s обратно.
Через HMR осмотрены desktop 1280×900 и mobile390×844, прохождение по видимой линии,
пауза/возобновление. Desktop наблюдался дольше исходного полного 144-s цикла;
mobile просмотр исходного темпа был прерван замечанием пользователя.
После замедления выполнен выборочный просмотр, новый полный 12-минутный цикл
не прослежен целиком; полная проверка обоих экранов в конечном темпе не заявляется.
Автотесты/сборка NOT_RUN_BY_USER_REQUEST. Применён web-animation-design.

## Две локальные правки главной — 14.11.2026

Текущее поручение после восстановления: только немного раздвинуть текст/орбиту
без изменения размеров и сделать непрерывный общий фон hero + нижних пояснений.
Сделано в home-page.tsx/orbit.css: единый фоновый слой на main, без повторной
заливки и разделительной линии; desktop текст/CTA левее, SVG прежнего размера
правее. Mobile композиция сохранена. Цвета, содержимое, анимационные keyframes,
нижний layout, footer и ЛК не переделывались. Осмотр через существующий HMR:
light/dark, 1280×900, промежуточные 900×900 и mobile 390×844, несколько фаз движения
и граница секций при прокрутке; видимого наложения/шва/горизонтального скролла
не обнаружено. Тесты/сборка NOT_RUN_BY_USER_REQUEST. Старый большой список
замечаний не возобновлён. Финальная приёмка остаётся за пользователем.

## Решение о восстановлении предыдущего оформления — 14.11.2026

Проверка восстановления: ручной просмотр через существующий host-dev/HMR
http://127.0.0.1:8131/ и /account/ на широком экране; подтверждены большая
орбитальная иллюстрация/сиреневый фон/капсула главной, круги класса и прежнее
меню ЛК в обеих темах. В разделе безопасности присутствует сохранённое поле
подтверждения пароля. Мутации аккаунта не отправлялись. Автопрогоны:
NOT_RUN_BY_USER_REQUEST. Новая переделка не начиналась.


Последняя визуальная итерация (нейтрально-графитовая палитра, уменьшенные орбиты,
прямоугольные действия и плоский редактор класса) отклонена пользователем.
По прямому поручению восстановлена «Орбита» непосредственно перед этой итерацией:
сиреневый фон и прежняя тёмная тема, большая орбитальная графика, кнопки-капсулы
с внутренним кругом/стрелкой, круги выбора класса, прежнее меню и расположение
пояснений. Новое оформление не разрабатывается. Это восстановление НЕ означает
финальную приёмку. История решений ниже сохранена; последние эстетические
ограничения отклонённой итерации не применяются к этому восстановлению.

Восстановление выполнено по точной истории операций текущего чата: исходный
CSS оставался целиком перед помеченным блоком переопределений; удалён только
этот блок, обратными заменами возвращены разметка home/account и начальные цвета
root. Приблизительная реконструкция и откат всей ветки не применялись.
Подтверждение нового пароля, доступная ошибка/клиентская проверка и очистка
поля сохранены как явно разрешённая функциональная правка. Остальные добавления
предыдущих этапов, backend, миграции, данные, каталог и уроки не изменены.
Ветка ms-t009-identity-ui, HEAD a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92;
правки остаются локальными, reset/merge/deploy не выполнялись.

## Приоритетное решение 14.11.2026: сдержанная «Орбита», без капсул и hover-анимаций

Пользователь не принял предыдущий рабочий вариант. Это решение выше прежних
эстетических разрешений: фиолетовый/лиловый/сиреневый и ранее отклонённый зелёный
исключены. Существующие логотип и Golos Text сохраняются. Нейтральные поверхности,
синие действия и небольшой иной акцент, без очередной пастельной заливки.
Слоган и орбитальная идея сохранены; пояснения «Есть тема. Будет понимание»
включить в hero на общей поверхности. Иллюстрация меньше, текст левее и вне
всего диапазона движения, включая промежуточные ширины и телефон.
Капсулы с кругом/стрелкой отклонены; действия с небольшим радиусом, без
декоративных кругов, повсеместных стрелок/теней и ЛЮБЫХ hover-анимаций.
Мгновенный hover и видимый keyboard focus сохраняются. Движение иллюстрации,
пауза и reduced-motion разрешены, точка небольшая и не персиковая.
«Мой класс» переработать полностью: сохранённое значение, отдельный понятный
редактор, переход к материалам и честный результат сохранения. Не круги,
скруглённые карточки или шкала достижений. Активное меню без капсул/теней/точек,
левой цветной полосы, горизонтального разделителя аккаунта и вертикальной линии.
Выход остаётся спокойной кнопкой со значком, без стрелки и disabled-вида.
Добавить «Повторите новый пароль», autocomplete=new-password, доступную ошибку
возле поля и запрет отправки при несовпадении. Подтверждение не расширяет API.
Серверные проверки/лимиты/проверка текущего пароля/поведение сессий сохраняются.
Геймификация только отдельным подписанным проектом будущего состояния с условными
значениями; никаких XP/наград/кнопок «Скоро» в рабочем сайте.
Дополнительно запрещены жёсткие градиенты, Lucide, белый фон страницы, радуга,
три карточки преимуществ, эмодзи, glass, em dash в текстах интерфейса, Inter/Geist/
Space Grotesk, фейковые отзывы, бенто, терминал, «это не X, это Y», списки с
галочками, три тарифа, большие скругления, фиолетовый с чёрным, радиальные сферы,
точечные сетки, sparkle-значки, анимированные стрелки, неон и типовые пастели.
Auth отдельно, без skeleton; каталог/уроки/backend/миграции не переделывать.
Merge и финальная приёмка только пользователем.

### Реализация этого уточнения, 14.11.2026

Рабочее дерево поверх a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92
(tree 9ebce3b77133939e7e197d8c984cb48382ebd91e), существующая ветка/PR #69.
Предыдущие dirty-изменения сохранены. Нового commit/push/merge нет.
Главная теперь объединяет пояснения и hero на нейтральной поверхности;
графика ограничена правой областью desktop, на mobile имеет отдельную область
внутри той же композиции. Синий CTA, графитовая тёмная тема, янтарная точка.
Кнопки без кругов/стрелок/hover-движения; небольшие радиусы, мгновенные состояния.
Меню выделяется весом и подчёркиванием, без точек/капсул/теней и разделительных
линий. Новый «Мой класс»: крупное сохранённое значение и материалы, ниже плоский
редактор с нативными radio и отдельной командой сохранения. Черновик явно
отмечается несохранённым, ссылка материалов использует только сохранённый класс.
Добавлен PasswordChangeForm с подтверждением и связанной доступной ошибкой.
Существующий API получает только current_password/new_password, подтверждение
не добавляется в DTO; все три поля очищаются после отправки, включая показанное.

Узкая команда (cwd frontend):
`node node_modules/vitest/vitest.mjs run tests/password-confirmation.test.tsx`
— 1 file / 2 tests PASS, 03:13 МСК: совпадение передаёт обработчик;
несовпадение показывает aria-invalid/связанную ошибку и не вызывает обработчик.
Synthetic значения, никаких реальных паролей/сетевых мутаций. Остальные suites,
QA уроков/typecheck/release build NOT_RUN_BY_USER_REQUEST.

Ручной браузерный просмотр: home light/dark; 1280/900/390 px; отсутствие
пересечения текста с областью графики, положение графики между кадрами;
пауза/возобновление; account learning mobile dark и desktop light;
security mobile dark и desktop light/dark; account settings desktop light;
клавиша ArrowRight в radio-группе, честное несохранённое состояние;
сохранение исходного класса подтверждено сообщением сервера «Класс сохранён».
Личные данные в сводку не переносились. Пароль/почта/выход не отправлялись.
Самокритика исправила слитые слова после скрытого br, оставшийся mobile
разделитель меню, сброс статуса черновика при возврате сохранённого выбора.
Reduced-motion сохранён в CSS, эмуляция системной настройки не выполнялась;
полный проход всех сочетаний viewport/section/theme и длительное наблюдение
всего цикла анимации не заявляются. Это самопросмотр, не независимое ревью.

Референсы: Supahero просмотрен как каталог; Footer Design при повторном
текстовом открытии вернул ошибку, прежний состав footer сохранён.
Оригинал https://www.are.na/ открыт и визуально изучен: ясные прямоугольные
действия и типографическая иерархия без декоративной панели. Чужой бренд не
переносился. Применены frontend-design, Impeccable, web-animation-design,
выборочная UI/UX Pro Max рекомендация нативной keyboard navigation.

Отдельный набросок будущей геймификации передан inline в чате как проект:
небольшой игровой статус у аккаунта в header, правая колонка активности
внутри ЛК. Условные числа подписаны. В рабочем интерфейсе нет XP/наград,
заглушек «Скоро» или новой модели прогресса. Backend/схема/каталог/уроки
не изменены, mail provider по-прежнему не подключён. Human acceptance PENDING.

## Решение Руслана — 13.11.2026

Статус CHANGES_REQUESTED: Руслан отклонил внешний вид реализации PR #69
13.11.2026. Требуется переделка по уточнению ниже. Backend не откатывать;
старые receipts относятся к прежнему candidate, не подтверждают новый UI.
Зависимость — принятая MS-T002A. Разрешена отдельная работа параллельно
MS-T003–MS-T008; ожидание приёмки всех классов снято для этой карточки.
Материалы, URL тем, renderer и вычисления уроков не менять. Общие header/auth
entry points согласовывать с исполнителями переноса, при интеграции сохранять
изменения обеих сторон. Приёмка классов остаётся отдельной.

## Выбор Руслана 14.11.2026: «Орбита», доработка и перенос в рабочий сайт

Выбрано направление Б «Орбита» из frontend/.cache/ms-t009-worlds/b.html.
Это разрешение доработать вариант и затем сразу применить его к главной и ЛК
в существующей реализации MS-T009. Дополнительного выбора макета не ждать.
Прежнее требование остановиться после предпросмотра для этой итерации отменено.
Выбор направления не означает финальную приёмку или разрешение merge.

Обязательные правки перед переносом:
1. Уйти от зелёной/мятной/петрольной палитры, включая текст, фон, кнопки и footer.
   Подобрать один или несколько согласованных акцентов к синему логотипа.
2. Сделать фон выразительнее и менее пустым: авторская графика, глубина,
   мягкий перелив/свет или другое цельное решение; обе темы и мобильный вид.
3. Переработать все кнопки обеих страниц: силуэт, пропорции, состояния и движение.
   Банальное увеличение/подпрыгивание при наведении не использовать как основу.
4. Ссылки и кнопки шапки без подчёркивания при наведении; focus сохраняется.
5. Переключатель темы — только иконка луны/солнца без видимой подписи,
   с доступным названием и адекватной областью нажатия. Не менять системный курсор.
6. Шапку отделить от hero очень легко и плавно, без тяжёлой панели/резкой полосы.
7. В ЛК раздел «Мой класс» сделать интереснее: не просто ряд одинаковых ячеек
   с цифрами. Сохранить понятный выбор/смену/сохранение класса и переход к материалам.
8. Реальную анимацию орбит/фона реализовать и проверить на рабочем сайте;
   выяснить, почему на предпросмотре движение не было заметно. Не обещать, что
   перенос сам исправит паузу. Сохранить reduced-motion и контроль движения.
9. Уменьшить крупную декоративную точку на орбите и согласовать её с рисунком.
10. Удалить повторную кнопку «Перейти в каталог». Сохранить основной CTA
    «Открыть материалы» и штатную навигацию; не множить одинаковые действия.
    Главный слоган оставить «Разобраться в математике. Тема за темой».
    Дополнительные тексты: «Есть тема. Будет понимание», «Вспомнить правило перед
    уроком. Разобрать пример после школы. Вернуться к тому, что пока не получилось.»;
    для ЛК «Всё для занятий. И немного настроек.» Встроить естественно, без набивки.
11. К «Войти» добавить аккуратный выразительный значок аккаунта, согласованный
    с шапкой; для вошедшего сохранить понятный переход в ЛК.
12. Фон и новая палитра — существенная часть работы, не косметическая перекраска
    прежнего зелёного. Сохранить спокойный пространственный характер «Орбиты».
13. Типографику взять из «Сборки» (a.html/style.css того же каталога): Golos Text,
    включая заголовки; убрать Literata из заголовков/цифр этой реализации.
    Логотип MathStart и его шрифт не менять. Сверить реальные определения макета.

Продолжать применять frontend-design, Impeccable и web-animation-design;
дополнительно искать motion/button/background референсы на Supahero и исходных
сайтах, Footer Design использовать с сохранением состава существующего подвала.
Taste Skill — дополнительный изучаемый источник; не утверждать, что он установлен.
Motion for React подключать только при необходимости выбранного движения.
Перенести оформление в настоящие React-компоненты, реальные данные и действия;
не встраивать макет через iframe/сырой HTML, не оставлять демо-аккаунт и отключённые
кнопки. Удалить только собственные временные файлы после переноса.
Не менять каталог/уроки, backend/миграции ради UI; auth остаётся отдельной страницей.
Без skeleton/технических экранов загрузки. Следовать политике узких проверок MS-T009,
без массовых suites, QA уроков и проверок при запуске. Визуально осмотреть настоящий
сайт через штатный host-dev/HMR: обе темы, desktop/mobile, движение и состояния кнопок.

### Рабочий перенос «Орбиты» — 14.11.2026, ручной просмотр НЕ ЗАВЕРШЁН

Решение применено локально через штатный host-dev/HMR:
http://127.0.0.1:8131/ и /account/. Новые серверы, iframe и демонстрационные
обработчики не используются. Ветка `ms-t009-identity-ui`, существующие Issue #68
и PR #69. Исходный HEAD `a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92`, tree
`9ebce3b77133939e7e197d8c984cb48382ebd91e`; после fetch origin/main отношение
7 ahead / 0 behind. Проверяется рабочее дерево поверх этого HEAD, новый commit
и push ещё не сделаны. Локальные требования карточки и UI-контракта сохранены.

Результат: главная без auth/выбора классов, слоган и одобренный дополнительный
текст, единственный основной CTA, пространственные орбиты и световой фон.
Палитра светлой темы: #f1f3fc / #252943 / #4655c6, тёмной:
#141a31 / #eef0ff / #b5bfff; тёплая точка #f2b799/#f2c3a6. Зелёного в новых
tokens нет. Golos Text загружен локально из официального Google Fonts вместе
с OFL; исходный Outfit логотипа сохранён. Библиотеки не добавлены.
Полноценный LessonFooter переиспользован с прежним составом. Header использует
LessonHeader/AuthLink, icon-only theme toggle и локально scoped оформление
без hover-подчёркивания. Кнопки имеют общую систему контурных/залитых поверхностей,
реакцию внутреннего значка/света и focus, без подъёма/масштабирования всей кнопки.

ЛК использует серверные данные и прежние perform/logout, Retry-After и блокировку
неизвестного результата; select заменён нативной radio-группой орбитальных классов
с явным сохранением. Адрес материалов строится по сохранённому классу, не черновику.
Почта, пароль, отзыв сеансов и выход сохранены; auth остаётся отдельной страницей.
Skeleton убраны без отключения проверки доступа. Настройки аккаунта теперь
привязаны к user ID, поздний ответ прежнего запроса игнорируется.
Общий механизм темы читает явный выбор или системное предпочтение, записывает
только явный выбор, реагирует на смену системной темы/событие storage;
ранний статический script в head применяет тему до оформления страницы.

Движение исходного макета при повторном открытии было включено (кнопка
«Остановить движение»), положение графики между кадрами менялось. Постоянная
пауза или ошибка запуска не подтверждена. Прежние 18 s/9° были слишком слабыми;
в рабочем варианте поле движется 12 s с большей амплитудой, малая точка обходит
орбиту за 24 s. Явная пауза сохраняется отдельно; offscreen/hidden ставят движение
на паузу, CSS reduced-motion отключает его. Путь reduced-motion в браузере
в этой итерации НЕ ПОДТВЕРЖДЁН.

Применены frontend-design, Impeccable animate/delight/polish/craft-floor,
web-animation-design, выборочная рекомендация UI/UX Pro Max о нативной клавиатурной
навигации. Исследованы Supahero, Footer Design и оригинальный
[Raycast](https://www.raycast.com/) (световое поле и контраст действия);
его бренд/изображения не копировались. Саморевью исправило явный SSR CSS input,
унаследованный catalogue margin у main, порядок подключения оформления,
привязку ответа настроек к владельцу и начальную поверхность до загрузки route.

Фактически выполнено: desktop light/dark главной; desktop dark «Мой класс»;
работающий theme toggle; смена класса клавишей ArrowRight, серверное сохранение,
обновление страницы и подтверждённый сохранённый выбор/адрес материалов.
После этого отправлен возврат исходного класса; итоговый ответ этой операции
из-за прерывания браузерной проверки не подтверждён. Пароль/почта/выход не
отправлялись. Консоль просмотрена, ошибок React в полученном фрагменте не было.

Профильные проверки разрешённого privacy/auth scope:
`node node_modules/vitest/vitest.mjs run tests/account-owner.test.tsx tests/identity-ui.test.tsx`
(cwd frontend): **2 files / 5 tests PASS**, 14.11.2026 02:39 МСК.
Два новых теста проверяют скрытие email прежнего владельца при смене сессии
и отбрасывание позднего ответа; три существующих — generic auth error/очистку
пароля, unknown outcome без слепого повтора и Retry-After. Только synthetic
данные и mocked API, без рабочей БД. После этого менялись только artwork/CSS
и начальная поверхность root, а не проверенные обработчики.
Полные suites, typecheck, release build, QA уроков: NOT_RUN_BY_USER_REQUEST.

Блокер просмотра: при открытии native Chrome для эмуляции reduced-motion
Computer Use остановлен защитой, потому что не смог достаточно уверенно
определить URL окна Windows. Управление браузером после отказа не продолжалось.
Поэтому ещё НЕ подтверждены: итоговые mobile/layouts всех разделов, account/security
формы обеих тем, реальный переход в каталог после сохранения, pause/reduced-motion,
полный hover/focus/press проход и отсутствие переполнений. Это не PASS и не
завершённая ручная проверка. Mail provider остаётся неподключённым; доставляемость
не заявляется. Backend/миграции/данные/каталог/уроки не переделаны.
Независимое ревью и human acceptance PENDING; merge/deploy NOT_PERFORMED.

## Последнее решение 14.11.2026: полная смена визуального направления главной и ЛК

Руслан отклонил и следующие макеты «Геометрия смысла» / «Открытый учебник».
Сохраняется слоган «Разобраться в математике. Тема за темой»; остальная композиция
не принята. Этот раздел приоритетнее всех прежних эстетических ограничений ниже.
Текущее поручение — обновить требования и подготовить промпт, без реализации.
Следующий исполнитель сначала показывает новые макеты, затем ждёт выбора.

- Главная и ЛК имеют полную свободу визуального перепроектирования: можно менять
  композицию, навигационную структуру ЛК, палитру, фон, типографику, кнопки,
  пропорции, поверхности и способ выбора класса. Прежнее обязательство сохранить
  sidebar и прежние сетки снято. Рабочие функции и доступность сохраняются.
- Логотип MathStart оставить существующим. Подвал сохранить примерно прежним
  по составу и узнаваемой структуре, с адаптацией к новому оформлению и обеим темам.
  Не навязывать новый бренд или изменение каталога/уроков ради этой переделки.
- Убрать из следующих вариантов повторяющийся график y = x² − 4x + 3,
  ползунок и обязательный учебный демо-блок. Не подменять их другой обязательной
  школьной иллюстрацией в той же сетке. Реальное демо на главной НЕ обязательно;
  реальность продукта можно показать иначе, без вымышленных функций и показателей.
- Разрешены авторские рисунки, математические мотивы, иллюстративный фон,
  мягкие переливы цвета/света, контролируемое фоновое движение и качественные
  интерактивные анимации. Прежние запреты градиентов, фонового движения и
  hover-анимаций не блокируют обоснованный новый замысел. Старый антишаблонный
  список служит предупреждением о банальных решениях, не жёстким каталогом запретов.
  Не переносить все эффекты одновременно: выбрать цельный художественный подход.
- Фон и движение не мешают чтению, форме и работе с клавиатуры/на телефоне.
  Без мигания и перехвата прокрутки; предусмотреть reduced-motion и остановку
  длительного автоматического движения. В ЛК важнее удобство ежедневных действий.
- Раскрытый стандартный select выбора класса на последнем скриншоте отклонён
  визуально; это не отдельное модальное окно. Для шести классов выбрать более
  подходящий контроль, например прямой выбор с понятным активным состоянием.
  Не заменять его декоративным самописным dropdown без удобства клавиатуры.
- Сохраняются: обе темы и переключатель в шапке; отсутствие встроенной авторизации
  и сетки классов на главной; auth на отдельной странице без общей шапки/footer;
  отсутствие skeleton и технических сообщений загрузки; backend, данные и защита.
  Действия аккаунта: выбор/смена класса и переход к материалам, настройки,
  необязательная подтверждённая почта восстановления, пароль и выход.
- Следующий показ: две действительно разные визуальные концепции, каждая с
  законченной главной и ЛК, desktop/mobile и обеими темами. Варианты должны
  различаться композицией и характером графики/движения, не только цветами.
  Предпросмотр анимированный и осмотрен в браузере, не только статичные снимки.

Инструменты следующего прохода: frontend-design для нового замысла;
Impeccable new-work/critique и animate для оценки и доработки;
web-animation-design для режиссуры движения. Повторно изучить Taste Skill
https://github.com/Leonxlnx/taste-skill/tree/main/skills/taste-skill как дополнительный
источник композиций и motion-приёмов (локально не установлен). Motion for React
https://motion.dev/docs/react — библиотека, не скилл с однозначным названием;
использовать при необходимости согласованных эффектов, не устанавливать пакеты
«animation» наугад. Искать визуальные и motion-референсы на https://supahero.io/
и https://www.footer.design/, открывать исходные сайты и смотреть именно движение.
Текстовый просмотр галереи не подтверждает визуальную оценку анимаций.

### Новый показ 14.11.2026: «Сборка» и «Орбита», выбор PENDING

По отдельному поручению подготовлены только два интерактивных визуальных
предложения; рабочая реализация не переделана. Продолжены ветка
`ms-t009-identity-ui`, Issue #68 и PR #69 без дублей. Исходные HEAD
`a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92`, tree
`9ebce3b77133939e7e197d8c984cb48382ebd91e`. При старте dirty только
UI-контракт и эта карточка: исходные локальные требования сохранены.
Отношение HEAD к локальному origin/main: 7 ahead / 0 behind; новый fetch
не выполнялся, актуальность remote main этим проходом не заявляется.

«Сборка»: лиловый/кобальтовый мир с коралловыми и жёлтыми модулями,
Golos Text, модульная графическая полоса, короткая сборка при появлении
и медленное движение одного элемента. ЛК с верхней навигацией и прямым
выбором класса. «Орбита»: зелёный/петрольный мир, Literata для заголовков,
Golos Text для действий, панорамная геометрическая линия с медленным
поворотом; ЛК с узкой навигацией и компактной полосой классов.
Логотип использует исходный Outfit из проекта; сохранены слоган,
описание/классы/навигация/copyright полного footer.

Явно прочитаны frontend-design, Impeccable new-work/craft-floor,
web-animation-design. Taste Skill изучен как внешний репозиторий,
не установлен. Открыты Motion React docs, Supahero (переезд в ScreensDesign),
Footer Design; оригиналы визуально просмотрены:
[Lusion](https://lusion.co/) — один живой графический акцент,
[Playdate](https://play.date/) — цельный цвет и ясные действия,
[Ordinary Folk](https://www.ordinaryfolk.co/) — типографическая композиция,
[ggdesign](https://ggdesign.it/) — выразительный первый экран.
Чужие изображения/бренд не перенесены. Motion не добавлен: достаточно CSS.
Impeccable context/concept-seed выполнены; seed работал без сетевого каталога.
Его опрос/отдельный сервер и механический detector не выполнялись по
приоритетному поручению самостоятельно показать два варианта без отдельных
серверов и автоматических прогонов. PRODUCT.md не переписывался.

Самокритика и исправления: исходный круг справа в «Сборке» делал два варианта
слишком похожими — заменён полной модульной полосой; сокращён пустой промежуток
mobile hero; увеличены touch areas навигации ЛК; исправлен порядок загрузки
шрифтов. Оба варианта вручную осмотрены через существующий host-dev origin:
широкая область около 1265 px и область 390 px, light/dark home/account,
формы recovery email/password, footer, выбор класса, переключение страниц/тем,
остановка движения. Дополнительно «Орбита» открыта в узком browser viewport.
Для radio сохранено нативное управление клавиатурой; reduced-motion отключает
анимации в CSS. Это самопросмотр автора, не независимое ревью или приёмка.

Исходники предпросмотров — `frontend/.cache/ms-t009-worlds/` (build.py,
style.css, interaction.js, a.html, b.html), оставлены до выбора, чтобы варианты
можно было открыть и доработать. Inline-предпросмотры переданы в текущем чате.
Ссылки на материалы ведут в существующий каталог; формы и выход макета
не отправляют запросы и не изображают успешную мутацию. Личные данные,
сохранённый класс и сеанс не читаются и не подменяются. Нет графика/ползунка,
учебного демо, auth/классов на главной или технических loading states.
Backend, маршруты приложения, зависимости, миграции, данные, каталог и уроки
не изменены. Автопрогоны/build/QA уроков: `NOT_RUN_BY_USER_REQUEST`.
Независимое ревью и human choice PENDING; commit/push/merge/publication
не выполнялись. После показа работа остановлена для выбора Руслана.

## Приоритетное уточнение 14.11.2026: отклонённые макеты и следующий показ

Руслан не принял направления «Живая математика» / «От примера к правилу»
и оформление ЛК из последнего показа. Запись ниже «выбор ожидается» является
историей итерации, не требованием выбрать один из отклонённых вариантов.
Текущее поручение здесь только исследование/обновление требований; сайт не менять.

Причины и требования к следующему проектированию:
- Большой график на почти сплошном тёмно-синем фоне не считать полноценным
  визуальным решением главной. Демо должно поддерживать композицию, а не превращать
  первый экран в учебную лабораторию. Не закреплять параболу как единственный hero.
- ЛК сохранить с боковой навигацией, но уйти от тяжёлого сочетания серо-синих
  прямоугольных поверхностей, одинаковых рамок и ощущения административной формы.
  Запрет больших мягких скруглений не означает, что всё нужно заключить в рамки.
- Обязательно вернуть в шапку главной и ЛК видимый работающий переключатель
  светлой/тёмной темы. Использовать общий механизм темы приложения, сохранять выбор
  между маршрутами/перезагрузкой, учитывать системную тему при отсутствии выбора,
  избегать вспышки неверной темы. Два направления дизайна не заменяют две темы.
  Показать оба режима каждой композиции, включая формы, footer и focus.
- Анимации разрешены выборочно: переход раздела ЛК, смена состояния, раскрытие
  реального математического демо, аккуратное появление ключевого элемента.
  Не использовать движение как компенсацию слабой композиции. Без scroll hijacking,
  фонового бесконечного движения, анимированных стрелок и hover-анимаций.
  prefers-reduced-motion обязателен; важное содержимое доступно без анимации.
- Удаление auth-формы/выбора классов с главной, прежний полноценный footer,
  ограничения на шаблонные приёмы и сохранность backend остаются в силе.

### Последнее уточнение: фоновые операции без экранов загрузки

Решение Руслана 14.11.2026 отменяет прежнее требование skeleton, включая
трактовку пункта «нет скелетон-лоадеров» в более раннем списке.
На главной, auth и в ЛК не показывать серые полосы/плашки, skeleton, отдельные
экраны загрузки, «Проверяем сессию», «Загружаем данные» или служебные селекторы
состояний. Проверки сессии, запросы, серверные guards и обработка ошибок остаются.
Публичная страница отображается независимо от проверки сессии; навигация имеет
устойчивую геометрию и понятный нейтральный переход к аккаунту до определения статуса.
При обновлении сохранять уже показанные подтверждённые данные того же пользователя,
если это безопасно. При первом входе в приватный раздел сначала подтвердить доступ
и подготовить данные, затем показывать раздел; не подставлять вымышленного ученика,
не показывать чужой кеш, не обходить авторизацию ради отсутствия ожидания.
Сетевую задержку нельзя устранить одним оформлением: не маскировать её ложным успехом
или бесконечно пустым экраном. При длительном сбое показать краткую понятную ошибку
и доступное действие повтора. Во время отправки защищать от повторной отправки,
сохранять ввод и композицию формы; не выводить технические стадии операции.
В макетах показывать полноценный интерфейс, без демонстрационных загрузочных экранов.
Исторические receipts о skeleton ниже описывают отклонённую итерацию, не требования.

### Обязательное применение инструментов и исследование

frontend-design установлен 14.11.2026 в пользовательские skills; использовать
его как основной источник проектирования. Impeccable использовать затем для
critique/polish, web-animation-design для выбранных эффектов; UI/UX Pro Max
выборочно для форм/контраста. В начале указать реальные прочитанные SKILL.md.
Не объявлять применение на основании одного упоминания названия.

Дополнительно рассмотрены:
- https://github.com/Leonxlnx/taste-skill/tree/main/skills/taste-skill
  (design-taste-frontend): дополнительный источник композиционных идей; не установлен.
  Автовыбор палитр/шрифтов и иные defaults не отменяют ограничения пользователя.
  Не подключать второй конкурирующий дизайн-процесс автоматически.
- https://motion.dev/docs/react : Motion for React является библиотекой.
  В проекте пока отсутствует. Для простого движения достаточно CSS; новую зависимость
  обосновывать конкретным эффектом после принятия макета. Непонятные пакеты
  с общими именами «motion react» / «animation» не устанавливать по совпадению названия.

До нового показа обязательно исследовать https://supahero.io/ (галерея hero,
сайт сообщает о переходе в ScreensDesign) и https://www.footer.design/.
Отобрать 3–5 конкретных подходящих экранов, открыть оригинальные сайты и
дополнительные источники за пределами образовательной категории. Нужны композиция,
ритм, типографика и оформление действий, а не копирование чужого бренда.
Состав прежнего footer сохраняется; его повторный полный редизайн не разрешён
одним фактом изучения галереи. Для ЛК изучить именно рабочие интерфейсы/настройки.
Ссылки и краткое «что применяем / что исключаем» оставить в одной сводке карточки.
Если доступен только текст страницы, не называть это визуальным исследованием.

В новом показе: две продуманные композиции главной и оформление ЛК с сохранённой
структурой; реальные русские тексты, desktop/mobile, обе темы, работающий переключатель.
Макеты сначала осмотреть в браузере. Если file:// заблокирован, использовать
доступный просмотр артефакта или основной dev-origin без нового отдельного сервера.
Не заявлять визуальную проверку выполненной по исходникам или расчёту контраста.
Если просмотр недоступен, явно сообщить ограничение; не передавать такой вариант
как проверенный. Панели переключения макетов/состояний не входят в продуктовый UI.
После показа остановиться для выбора Руслана. Отдельная публикация Sites не нужна.

### Новый показ 14.11.2026: исследование и макеты, выбор PENDING

Ветка `ms-t009-identity-ui`, исходный HEAD
`a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92`. GitHub-поиск по открытому PR
подтвердил существующий [PR #69](https://github.com/Tramsey00/MathStart-Python/pull/69).
Его описание ещё относится к прежней реализации. Новые ветки/PR не создавались.
Незакоммиченные уточнения карточки и UI-контракта сохранены; рабочий UI,
backend, миграции, данные и материалы не изменены. Это показ для выбора,
не реализация и не приёмка.

Просмотрены в браузере галереи [Supahero](https://supahero.io/) и
[Footer Design](https://www.footer.design/), затем пять конкретных экранов:

| Экран | Применимый приём | Что не переносим |
| --- | --- | --- |
| [Mathigon, главная](https://mathigon.org/) | Математический объект сразу объясняет предмет сайта | Фрактальный фон, многоцветность, чужие иллюстрации |
| [GeoGebra, главная](https://www.geogebra.org/) | Ясный основной переход к материалам до входа | Белый фон, персонажи, предметные chips |
| [Brilliant Math](https://brilliant.org/math/) | Продуктовое действие показано рядом с объяснением | Отзывы, показатели, игровые обещания, фоновая анимация |
| [Craft, главная](https://www.craft.do/) | Центрированное вступление и широкий показ продукта ниже | Коллаж, большие радиусы, тени, набор карточек |
| [Linear Profile, опубликованные экраны настроек](https://linear.app/docs/profile) | Короткие группы полей и спокойная иерархия действий | Чужие функции профиля, email-login, дополнительная структура меню |

Linear изучен по скриншотам в официальной справке, без входа в закрытый кабинет.
Zed вернул Error 1102; его дизайн не считается изученным. Галерея footer
не использована как основание замены прежнего состава подвала MathStart.

Два новых направления: «Геометрия смысла» (асимметричная типографика,
предметный чертёж и небольшой интерактив ниже вступления) и «Открытый учебник»
(центрированное вступление, широкая витрина конкретного урока, затем демо).
Оба имеют светлую/тёмную тему и desktop/mobile. ЛК сохраняет боковое меню и
один раздел; согласованные оформления отличаются поверхностью навигации,
но не составом функций. Нет skeleton, селектора загрузки, auth-форм и выбора
класса в основном содержании главной. Полный footer содержит бренд, описание,
шесть классов, навигацию и copyright.

Настоящие источники: тройка 3, 4, 5 и 9 + 16 = 25 из
`/materials/8-geometry-6` (открыт и подтверждён в host-dev), демо
`y = x² − 4x + 3` с ползунком из `/materials/8-algebra-32`.
При будущей интеграции переиспользовать имеющийся QuadraticGraph,
не переносить временную копию математического виджета в runtime.

Прочитаны пользовательские SKILL.md frontend-design, impeccable,
web-animation-design, ui-ux-pro-max. frontend-design определил композиции;
Impeccable применён для авторской критической оценки и polish, не заявляется
формальный двухагентный critique или независимое ревью. UI/UX Pro Max:
целевой поиск labels/touch spacing, без генерации конкурирующей дизайн-системы.
Motion-библиотека не добавлена; только краткое появление выбранного раздела
по клику, отключённое для reduced-motion и клавиатурного перехода.

Ручной браузерный просмотр через существующий origin 8131 и Vite /@fs:
desktop 1280×900, mobile 390×844, обе композиции и темы, разделы ЛК,
изменение x (0,1 → 2,61), выбор 8 класса и корректный URL материалов.
Исправлены чрезмерный размер заголовка второго направления, наличие регистрации
в mobile-шапке, иерархия подзаголовков ЛК и высота mobile-навигации.
Это просмотр макетов, не повторная проверка auth/backend. На момент перехода
к следующему макету автоматическая проверка разрешений временно остановилась
из-за лимита использования; после сообщения Руслана «Продолжай работу»
обычный браузерный просмотр успешно возобновлён. Обход не применялся.
Автотесты, typecheck, сборки и массовый QA уроков: NOT_RUN_BY_USER_REQUEST.

Работа темы показана в предпросмотре: системная настройка при отсутствии выбора,
переключение и сохранение выбора; preview изолирован от рабочего аккаунта.
Текущий use-site-theme ещё требует доработки системной настройки и ранней
инициализации после выбора макета. Общий механизм приложения пока не изменён.
ЛК показывает незаполненное состояние и обозначение места логина, без
вымышленного пользователя или персональных данных. Изменения почты/пароля/
сеансов отключены в макете, класс меняет только локальный выбор и ссылку.

Повторный поиск legal routes в site_content/frontend/src не нашёл действующих
страниц условий/конфиденциальности. Ложные ссылки и утверждённые юридические
тексты не добавлялись. До публикации нужны оператор, контакты, юрисдикция,
возрастные правила, лицензия контента, подрядчики, cookie/analytics,
сроки хранения/удаления и порядок обращений. Предыдущие рабочие проекты
остаются черновиками, не действующими документами.

Временные исходники и preview: `frontend/.cache/ms-t009-nov14/`.
Новый сервер и Sites не использовались. После показа ожидается явный выбор;
merge, закрытие Issue и следующая карточка не выполнялись.

## Последнее уточнение: новое направление главной и оформление ЛК

Решение Руслана 13.11.2026 после просмотра a557ac1. Этот раздел приоритетнее
предыдущего выбора «Вкладки» для главной, требований добавить выбор класса
и уменьшить footer. Текущее поручение: только исследование и требования, без реализации.

- Полностью убрать с главной встроенную авторизацию: поля логина/пароля,
  форму регистрации/восстановления и правую карточку входа. Не заменять её
  карточкой «С возвращением» для вошедшего. В навигации оставить переходы
  на отдельную /auth (вход/регистрация), для вошедшего — в /account/.
  Проверка сессии для навигации остаётся фоновой.
- Удалить с главной целиком блок «Какой класс вы изучаете?» с шестью кнопками
  классов и списком предметов (так понято «это удалить» на присланном скриншоте).
  Каталог и выбор класса в ЛК сохранить. Не заменять блок другой сеткой классов.
- Вернуть прежний полноценный footer до коммита 0aab648, ориентир 82136a8:
  бренд/описание, ссылки классов, навигация и copyright. Восстановить компонент/
  стили адресно, сохраняя новое поведение аккаунта. Не откатывать файлы целиком
  вместе с backend или другими изменениями. Прежнее требование компактного footer отменено.
- Главной нужен новый полноценный визуальный замысел. Разрешено менять фон,
  цвета, композицию, кнопки и типографическую иерархию, с узнаваемостью MathStart
  и гармоничным переходом к каталогу/урокам. Не ограничиваться перекраской старого hero.
- В ЛК пользователю нравится расположение: сохранить боковое меню и отдельный
  выбранный раздел. Переработать визуальное оформление, поверхности, поля,
  пропорции, кнопки и плотность. Не устраивать новый выбор структуры навигации.
- Auth сохраняет согласованную самостоятельную композицию без шапки/footer;
  эта итерация сосредоточена на главной и ЛК. Backend/данные/защита сохраняются.

### Обязательные ограничения новой главной и ЛК

Не использовать: жёсткие градиенты; Lucide; чисто белый фон страницы; радужную
раскраску; повсеместные тени; три карточки преимуществ в ряд; эмодзи; «жидкое
стекло»; длинное тире em dash в интерфейсных текстах; Inter/Geist/Space Grotesk;
цветные полосы слева; фейковые отзывы; бенто-сетки; декоративное окно терминала;
фразу «это не X, это Y»; списки с галочками; три тарифа; мягкие большие скругления;
сочетание фиолетового с чёрным; декоративные радиальные сферы; точечные сетки;
значки с блёстками; анимированные стрелки; hover-анимации; неон; типовые пастельные палитры.
Предпочесть чёткую геометрию; hover/focus могут мгновенно менять состояние для
понятной обратной связи, без движения/масштабирования/анимации. Не убирать focus.
Не заменять один шаблон другим (например, обязательной бежевой газетной темой).
Ограничения локальны для этих поверхностей: формулы/контент и стили уроков не менять.

Фразы из списка «нет реальных демо продукта»,
«нет условий использования», «нет политики конфиденциальности» означают
устранить отсутствие, а не запретить эти элементы:
- Предложить реальный фрагмент существующего урока/интерактива, математически
  корректный и ведущий к настоящему материалу. Не обещать будущие AI/прогресс.
  Переиспользовать имеющееся решение; крупную новую учебную механику не создавать.
- Фоновые операции оформлять по последнему уточнению 14.11.2026 выше:
  без skeleton и технических экранов; сохранять серверную защиту и обработку ошибок.
- Проверить действующие страницы условий и конфиденциальности. Ссылки должны
  вести на настоящий текст. Если документов нет, подготовить черновики и список
  недостающих фактов для Руслана; не выдумывать оператора/контакты/сроки хранения,
  не выдавать шаблон за юридически утверждённый документ. Публикация после согласования.

### Инструменты, источники и следующий этап

Рекомендуемые роли, без установки всех инструментов одновременно:
1. frontend-design от anthropics/skills (установлен 14.11.2026) для создания
   отличающихся визуальных направлений. https://github.com/anthropics/skills/tree/main/skills/frontend-design
2. Уже установленный Impeccable для shape/critique/polish; его defaults не отменяют запреты выше.
3. Уже установленный UI/UX Pro Max для целевых проверок форм, контраста,
   кириллицы и responsive. Его каталог палитр не является готовым дизайн-решением.

Источники предметных идей: https://mathigon.org/ (математика как взаимодействие),
https://brilliant.org/math/ (показ учебного опыта и визуализаций).
https://www.desmos.com/ полезен как кандидат на визуальное исследование продукта;
в текущем текстовом просмотре его интерфейс не был доступен для оценки.
Это ориентиры, не разрешение копировать их дизайн, отзывы, иллюстрации или claims.
Агент следующего этапа обязан дополнительно искать в интернете современные
решения главных образовательных сайтов и личных кабинетов, не ограничиваясь
этими ссылками или каталогами скиллов. Отобрать несколько релевантных примеров,
сохранить ссылки в одной сводке и объяснить применимые решения и ограничения.
Затем визуально изучить доступные реальные страницы
и указать, какой конкретный приём применим, а что противоречит ограничениям.
Закрытые кабинеты не объявлять изученными без доступа.

Сначала разработать два действительно разных визуальных направления главной
и согласованное оформление ЛК с прежней боковой навигацией. Показать реалистичные
desktop/mobile макеты с русским текстом, настоящим содержанием и состояниями.
Различаться должны композиция/характер, а не только оттенок или тип меню.
Остановиться для выбора Руслана; после выбора реализовать в основном runtime.
Не публиковать через Sites и не создавать новый сервер для показа без поручения.
Результаты исследования и решение хранить в этой карточке/PR, временные макеты
в ignored cache. Не создавать новые tracked отчёты для каждого варианта.

### Исследование и новые макеты — 13.11.2026, выбор ожидается

Исходный SHA `a557ac1d8bf5239d6a2ac7ee2192c60e23c43e92`, ветка
ms-t009-identity-ui. Локальные уточнения этой карточки и UI-контракта сохранены.
Этот этап не меняет runtime, backend, миграции, DB или учебные материалы.
Sites не использовался, новый сервер не запускался.

Визуально изучены живые страницы [GeoGebra](https://www.geogebra.org/),
[NRICH](https://nrich.maths.org/), [Brilliant Math](https://brilliant.org/math/)
и опубликованный снимок Settings в
[справке Khan Academy Reimagined](https://support.khanacademy.org/hc/en-us/articles/46937973575437-How-do-I-change-my-settings-in-Khan-Academy-Reimagined).
Закрытый кабинет Khan Academy не открывался. GeoGebra: понятное основное действие
и доступ к материалам до входа; тематическую раскраску/сетки и иллюстрации не копировать.
NRICH: прямое объяснение назначения и открытый учебный ресурс; объёмную ролевую
навигацию/видеоблок не переносить. Brilliant: учебное действие видно до регистрации;
показатели, отзывы, анимации, тени и будущие функции не переносить. Khan Academy:
постоянная боковая навигация, ограниченная ширина форм, группировка по задаче;
не переносить их функции прогресса/AI и дополнительный уровень вкладок.

Предложены «Живая математика» (тёмно-синяя цельная поверхность, широкий
действующий график как главный учебный опыт) и «От примера к правилу»
(светлая стальная поверхность, крупная типографика, разбор нулей функции рядом
с графиком). Различаются порядком чтения, масштабом и композицией. ЛК один:
выбранное боковое меню, сдержанные геометрические поверхности и один раздел.
Desktop и mobile доступны в макетах; state selector показывает skeleton/ошибку.

Демо использует исходные коэффициенты QuadraticGraph / quadratic-math.ts:
y = x² − 4x + 3, вершина (2; −1), нули 1 и 3. Ползунок x и вычисление значения
повторяют существующую учебную механику. В production переиспользовать компонент,
не заводить вторую учебную реализацию. Ссылка ведёт на /materials/8-algebra-32.
Footer воспроизводит состав SiteFooter/LessonFooter из 82136a8: описание,
шесть классов, навигацию и copyright. Позже восстановить его адресно в HomePage.

frontend-design среди установленных skills не найден; ничего не устанавливалось.
Прочитаны Impeccable (shape, craft-floor, critique, polish) и UI/UX Pro Max;
последний применён выборочно к контрасту и touch spacing, без генерации новой
дизайн-системы. Критическая оценка выполнена автором, не является полным
двухагентным critique или независимым ревью. По ней исправлены цвет бренда на
footer, короткая mobile-подпись кабинета и высоты skeleton по разделам.
Расчёт основных текстовых пар: 5,70–12,13:1; учебные контрольные точки сверены.
Список запретов просмотрен по исходникам. Браузерный просмотр локального
макета не выполнен: file URL заблокирован политикой браузера; обход не применялся.
Автотесты, typecheck, build и QA уроков: NOT_RUN_BY_USER_REQUEST.

Страницы условий/конфиденциальности в site_content/frontend и подходящие документы
по именам файлов не найдены; наличие вне репозитория не исключено. В ignored cache
подготовлены рабочие проекты и список недостающих фактов: оператор, контакты,
юрисдикция, возрастные условия, лицензия контента, подрядчики/страны, cookie/analytics,
сроки хранения/удаления и канал обращений. В макетах ссылки явно помечены «проект»
и открывают текст с возвратом; не ведут на выдуманные production страницы.
Публикация документов требует согласования. Макеты и рабочие тексты:
frontend/.cache/ms-t009-next/. Выбор Руслана PENDING; реализация не начата.

## Предыдущая итерация UI — замечания Руслана 13.11.2026

Этот раздел имеет приоритет над прежними требованиями о неизменной композиции
главной и синей квадратной кнопке. Реализация на 82136a8 визуально не принята.
В этом чате меняются только требования; реализация переделки — отдельное поручение.

1. **Сессия без технических экранов.** На главной и в ЛК не показывать
   «Проверяем сессию…», диагностические окна и служебные статусы обычного restore.
   Проверка и серверная защита выполняются. До результата сохранять устойчивую
   геометрию без skeleton по уточнению 14.11.2026;
   не мелькать формой гостя/чужими данными и не открывать private UI
   до подтверждения. Длительный сбой обрабатывать коротким понятным сообщением
   и повтором там, где действие действительно недоступно; не скрывать ошибки навсегда.
2. **Более содержательная главная.** Сейчас hero сразу переходит в огромный
   footer. Добавить полезное содержание: удобный выбор класса/предмета и
   краткое объяснение работы с имеющимися материалами, с настоящими ссылками.
   Сохранить узнаваемый MathStart, но разрешено изменить композицию и пропорции.
   Сделать footer компактнее; не заполнять высоту пустыми spacer/min-height,
   выдуманными отзывами, статистикой, обещаниями AI или недоступными функциями.
   Состав новых блоков представить в визуальном варианте перед реализацией.
3. **Кнопки входа и профиля переделать.** Отвергнуты обе ярко-синие квадратные
   плитки со скруглениями и белой стрелкой/контуром человека (скрины 4–5).
   Предложить спокойную навигацию с понятными «Войти» / «Личный кабинет» либо
   компактным профилем. Состояния гостя и вошедшего различимы, переходы сохраняются.
   Не распространять редизайн на все кнопки уроков; общий auth entry согласовать.
4. **Полностью пересобрать ЛК.** Отвергнута длинная страница из широких строк:
   описание слева, растянутые поля справа, много пустоты, якоря сверху и
   повторяющиеся синие кнопки. Нужны новая композиция, навигация и иерархия действий.
   Допустимы локальные отличия от общей системы при сохранении узнаваемых
   цветов/типографики MathStart. Рассмотреть компактную навигацию разделов
   и показ выбранного раздела вместо всех настроек подряд. Не утверждать
   конкретную схему без показа пользователю. Состав функций остаётся прежним.
5. **Auth — самостоятельный экран.** На входе/регистрации нет общей шапки,
   меню материалов, кнопки профиля и footer. Допустима одна ссылка «На главную».
   Центральная компактная панель с формой и лёгким фоном; допустим мягкий
   градиент в близких MathStart цветах. Новый референс: светлая панель на
   цветном фоне, собранные поля и основное действие. Цвета, огромный круглый
   значок, тени, email-login и Remember me из картинки не обязательны.
   Декор не вытесняет форму; подписи контрастны, mobile/клавиатура не обрезают её.
   Переключение вход/регистрация и восстановление остаются частью auth-сценария.

### Выбранное направление — 13.11.2026

После просмотра трёх визуальных вариантов Руслан выбрал:
- главная — «Вкладки», целиком убрать блок «Как заниматься с материалами»;
- вход/регистрация — «Вкладки», добавить контурные значки в поля логина и
  пароля, увеличить отступ между полем логина, подсказкой и следующим полем;
- личный кабинет — «Боковое меню», показывать только выбранный раздел.

Этот выбор разрешает реализацию выбранного направления в действующих routes.
Отмена блока «Как заниматься с материалами» приоритетнее пункта 2 выше.
Палитра, Outfit, backend, миграции, данные и защиты сохраняются.
Выбор направления не означает приёмку реализации. Актуальный candidate,
результаты ручного просмотра и ограничения — в PR #69; receipts прежнего
candidate ниже относятся только к указанному в них SHA.

### Как применять Impeccable при переделке

Явно прочитать установленный skill Impeccable и применить этап проектирования
(shape), затем критическую оценку (critique) и финальную доработку (polish).
Skill помогает агенту принимать решения и смотреть результат; это не готовая
тема и не гарантия хорошего дизайна. Требования Руслана приоритетнее его defaults.
Интернет-исследование по разделу ниже сохраняется.

Сначала показать Руслану визуальный вариант главной, auth и ЛК (desktop и
основную mobile-композицию) с кратким объяснением изменений. На этом этапе
остановиться для выбора/поправок; не выдавать текстовое описание за макет.
После принятия направления реализовать его в существующих feature/routes
и осмотреть реальные экраны в браузере. Не создавать новый prototype server,
дублирующий auth или tracked папку макетов; временное хранить в ignored cache.
Применить проверки только в разрешённом scope. Сохранить backend, данные,
миграции и защиту; не выполнять общий откат из-за отклонения дизайна.

## Входы и исследование

Применяй эту task skill явно. Прочитай [очередь](../../../docs/tasks/INDEX.md),
[архитектуру](../../../ARCHITECTURE.md), [карту контрактов](../../../specs/current-contracts.md),
[UI-контракт](../../../docs/ux/shared-ui-contract.md),
[политику проверок](../../../docs/frontend/testing-policy.md) и
[карту папок](../../../docs/repository-map.md).
Старые I02/I03 fixtures и controllers не являются образцом дизайна.

Перед проектированием обязательно изучи в интернете актуальные рекомендации
по доступным формам входа/регистрации, восстановлению доступа и личным кабинетам
образовательных сайтов. Для безопасности используй OWASP, для web-поведения —
MDN/W3C. Визуальные примеры оценивай по пригодности для школьника и MathStart.
В одной сводке PR укажи несколько полезных ссылок и применённые решения.
Применяй доступный профильный UI skill. Исследование не разрешает менять бренд,
вводить UI kit, копировать чужие assets или устанавливать ненужные плагины.

Ориентиры из вложений Руслана описаны здесь, чтобы новый чат не зависел от Temp:
- Главная MathStart: светлая поверхность; слева крупный заголовок про математику
  5–10 классов и CTA материалов, справа компактная форма; в шапке материалы,
  тема и кнопка аккаунта. Сохраняется узнаваемость MathStart; композиция главной,
  высота footer и кнопки пересматриваются по замечаниям 13.11.2026 ниже.
- Референс отдельного входа: компактная центральная форма, заголовок,
  логин/пароль, действия входа/регистрации и восстановление. Это ориентир
  композиции, не готовый skin. Стеклянный/размытый фон, низкий контраст,
  email-вход, английские надписи и watermark Freepik не переносить.
  Использовать существующие MathStart tokens, светлую/тёмную темы и читаемые labels.

## Авторизация, главная и навигация

Вход только по **логину и паролю**, без email-login, OAuth и обязательной почты.
Существующие user IDs, логины, хеши и данные сохраняются. Не менять регистр/
нормализацию старых логинов без проверки коллизий и отдельного решения.
Новые ограничения регистрации согласовать между UI/API; старые допустимые
логины продолжают работать. Пароль не обрезать и не trim-ить.

Одна отдельная страница `/auth` с двумя адресуемыми режимами:
`/auth?mode=login` и `/auth?mode=register`. Прямое открытие, refresh и Back работают.
Неизвестный mode выбирает вход. ЛК остаётся `/account/`.

| Состояние / действие | Результат |
| --- | --- |
| Гость нажимает кнопку со стрелкой в шапке | `/auth?mode=login` |
| Гость нажимает новую «Зарегистрироваться» на главной | Та же страница, `/auth?mode=register` |
| Вошедший нажимает кнопку в шапке | `/account/`; стрелка заменена иконкой пользователя с доступным именем «Личный кабинет» |
| Вошедший открывает `/auth` или ссылку регистрации | Переход в ЛК после подтверждения сессии сервером |
| Гость открывает `/account/` | Вход с безопасным возвратом в ЛК |
| Успешный вход | Допустимый внутренний адрес возврата, если задан; иначе ЛК |
| Успешная регистрация | ЛК с выбором класса |

Настоящие ссылки, aria-label/title и видимый focus обязательны. До проверки
сессии — нейтральное состояние без ложного утверждения о входе; ошибка сети
не равна подтверждённому выходу. Шапки главной/каталога/уроков используют одно
auth-поведение. Возврат разрешён только на проверенные внутренние пути:
исключить внешние/protocol-relative адреса и циклы на auth.

**Главную переработать по последнему уточнению выше.** Встроенные формы
входа/регистрации/восстановления и правую auth-карточку удалить полностью.
В навигации оставить ссылки на отдельную /auth с нужным режимом, для вошедшего
переход в ЛК. Карточку приветствия вместо формы не показывать.
Материалы остаются доступны гостю.

## Формы и личный кабинет

Отдельная страница входа/регистрации и ЛК проектируются заново внутри принятой
системы MathStart. Формы находятся только на отдельной auth-странице;
общий API client и существующий auth backend переиспользуются.
Предусмотреть labels, autocomplete, password managers/paste, показ пароля,
клавиатуру, mobile, loading, ошибки полей/сети и время повторной попытки.
Ошибка входа — «Неверный логин или пароль», без раскрытия существования аккаунта.
Не выводить operation IDs, receipts и технические кнопки replay; при неизвестном
результате сохранить безопасное восстановление состояния без слепого повтора мутации.

Первый ЛК:
1. «Моё обучение»: выбор/смена класса, переход к материалам выбранного класса.
2. «Настройки аккаунта»: логин, добавление/подтверждение/смена/удаление почты восстановления.
3. «Безопасность»: смена пароля с текущим паролем, выход со всех устройств, обычный выход.

Прогресс, достижения, XP, история решений и диагностика — позже, с их backend.
Не показывать фиктивные показатели и неработающие функции. Существующие onboarding
данные сохранить; выбор класса не пишет mastery и не имитирует диагностику/
самооценку. Отразить текущий этап onboarding в контракте, не удаляя будущие сценарии.
Кабинет — понятные разделы, умеренные отступы, без декоративной сетки карточек вокруг полей.

## Необязательная почта и восстановление

Регистрация требует только логин и пароль; почту предложить добавить в ЛК.
Она не используется для входа. До подтверждения адрес не участвует в восстановлении.
Объяснить: без подтверждённой почты самостоятельное восстановление по email невозможно.
Не обещать несуществующую поддержку/контрольные вопросы. Старые email из БД
не считать подтверждёнными автоматически.

Подтверждение и сброс — разные случайные одноразовые токены с ограниченным TTL,
привязанные к пользователю, назначению и нужному адресу; в БД безопасные digests.
Повторное/конкурентное погашение и истечение безопасно обрабатываются.
Ссылки строить из доверенной конфигурации origin, не Host запроса.
GET ссылки не меняет пароль и не погашает её сам: учесть email scanners.
Не передавать токены в логи/аналитику/Referer и сторонние ресурсы reset-страницы.
Ответ восстановления одинаков для известных/неизвестных аккаунтов; письмо
получает только подтверждённый адрес. Смена/удаление адреса требуют повторной
аутентификации; новый адрес работает после подтверждения, старые токены отзываются.
Сброс пароля отзывает старые сеансы/recovery-токены; смена пароля безопасно
отзывает прежние сеансы с явно описанным поведением текущего устройства.
Правила уникальности/коллизий email определить в контракте до миграции,
без автоматического объединения пользователей по адресу.

Provider, отправитель, секреты и live-отправка ещё не выбраны/не разрешены.
Реализовать интерфейс доставки и локальный fake для проверок; не выдавать fake
за реальную доставку. Публичное завершение восстановления требует настройки
и проверки настоящей доставки после решения Руслана. Указать этот остаток явно.
Недоступность почты не блокирует обычный вход. Не заводить платные сервисы самостоятельно.

## Backend и защита

Backend менять разрешено по необходимости: Identity service/API, DTO, reviewed
Alembic migrations, сессии, лимиты и доставка почты. Сохранить модульный монолит,
пользователей и данные, CSRF/Origin/Host, owner checks, rotation/logout/expiry/
revocation, idempotency/conflict/retry и границы приватных данных. Auth заново не писать.
Исходники для анализа: backend/users/{service,security,passwords,http}.py,
frontend/src/app/routes/account-foundation.tsx и shared/api.
Baseline: 10 login-запросов за 300 секунд по IP в PostgreSQL, включая успешные;
регистрация этот лимит не использует. Это описание текущего кода, не целевая политика.

Обязательно:
- Серверные лимиты по IP и логину против перебора, массовой регистрации и
  злоупотребления подтверждением/восстановлением; временные ограничения,
  Retry-After и понятный UI. Учесть общий школьный IP, распределённые атаки
  и намеренную блокировку чужого аккаунта. «3 попытки» не является требованием:
  предложить конкретные окна/пороги с обоснованием.
- Общие атомарные счётчики между worker-ами, устойчивость к concurrency/
  перезапуску, очистка старых записей; client IP доверять только через известный proxy.
- Политика новых паролей по актуальным рекомендациям, ограничение размера до
  дорогого hashing, сохранение входа со старыми паролями; без периодической смены без причины.
- Текущий пароль для чувствительных действий, отзыв всех сеансов, защита от
  подмены владельца профиля, чужих tokens и session fixation.
- Безопасные cookies/HTTPS в production, CSRF на browser mutations, no-store
  для приватных ответов, защитные headers и ограничения тела на edge/API.
  CSP учитывать существующие уроки/интерактивы, не ломать их глобальной политикой.
- Минимальный журнал событий безопасности с ограниченным хранением, без паролей,
  cookies, полных тел запросов и секретных ссылок; без новой платформы мониторинга.

Новые security/API решения и численные параметры кратко оформить в актуальном
contract addendum/ADR по применимости. CAPTCHA, MFA, Redis и новый auth provider
не обязательны; не добавлять без обоснования и согласования расширения scope.

## Проверки и приёмка

Для реализации MS-T009 разрешён узкий набор проверок изменённой авторизации:
регистрация/вход/выход, CSRF/owner/privacy, лимиты/concurrency, смена пароля,
отзыв сеансов, подтверждение/recovery с fake mail, одноразовость/expiry токенов,
безопасный возврат, restore/conflict/retry. При изменении БД — PostgreSQL fresh/upgrade.
Переиспользовать профильные tests, дополнить существенные новые случаи.
Перед прогонами прочитать verification skill и runtime-инструкцию по применимости.
Это исключение не включает полный suite, массовый QA уроков, startup tests или
live-отправку. При текущей редакции карточки прогоны не нужны.
UI вручную просмотреть в основном host-dev на desktop/mobile, в обеих темах,
с клавиатурой, для гостя/вошедшего/истёкшей сессии и ошибок сети.

Приёмка: маршруты и кнопки соответствуют таблице; главная содержательно расширена с сохранением узнаваемого стиля;
формы/ЛК работают с реальной Identity; защиты действуют на сервере; старые
пользователи и учебные страницы сохранены; нет второй реализации auth.
Удалить выведенные формы/controllers/styles только после проверки потребителей;
поведенческие/security assertions сохранить. Отсутствие настоящей почты явно
отделить от готовности локального сценария; непроверенное не называть PASS.
Самопроверка, независимое ревью, проверки, человеческая приёмка и merge раздельны.

## Организация и передача

Реализация — отдельное поручение, Issue → ветка от актуального origin/main → PR.
Сначала проверить существующие Issue/ветку/PR и продолжить без дублей.
Если требования ещё локальные, сохранить эту редакцию и связанные файлы до
switch: не потерять их при переходе на main. Обычный checkout, без новых клонов.
Auth/account feature отдельно от generic layout; общий API client и backend/users
переиспользуются. Private данные не попадают в SSG/browser storage.
Временное — var/tmp/ms-t009/ или frontend/.cache/; удалить своё после использования.
Одна сводка в карточке/PR: SHA, изменения, источники исследования, проверки,
ограничения, ревью. Не создавать отчёт на каждый шаг.
Не трогать protected acceptance DB, не запускать следующую карточку,
не выполнять merge, закрытие Issue или production deployment самостоятельно.

## Сводка реализации — 13.11.2026

[Issue #68](https://github.com/Tramsey00/MathStart-Python/issues/68),
[PR #69](https://github.com/Tramsey00/MathStart-Python/pull/69),
ветка ms-t009-identity-ui, основной checkout. Исходный main:
`4eddd0d6aaf9374a51bfd28456cff71b5349a6a1`. Семь исходных dirty-файлов
ms-t009-spec сохранены и включены в commit `583000cf04f38897e23f65696393bd1edec4991a`.
Проверенный код после исправления саморевью:
`ba247f4418aaf9f687bee239f748edd8b2bfcc1f`, tree
`9c67a0467aff11e9396180b8748171a4bd50172a`.
Последующее изменение этой сводки/статусов — документационное.

Реализованы единые login/register формы на главной и /auth, серверная сессия
в общей навигации и /account/ с классом, recovery email и безопасностью.
Email-preview на главной выведен; локальная функция EmailLogin имела только
одного потребителя в home-page.tsx и заменена HomeIdentity. Старый account route
сохранил путь и экспортирует новый feature; старые UI assets/fixtures/controllers
сохранены для оставшихся compatibility/test потребителей. Файлы учебных
материалов и renderer не изменены. Общий LessonHeader меняет только auth entry;
loginHref prop сохранён для совместимости интеграции веток классов. При проверке
GitHub не обнаружены открытые параллельные PR; никаких чужих веток/правок не
перезаписывали. При интеграции общей навигации требуется сохранить обе стороны.

[Identity addendum](../../../specs/api/identity-t009.md) фиксирует новые API,
onboarding stage, пароли, адреса/коллизии, лимиты, TTL, доставку и rollout.
Модуль Identity и общий API client расширены; auth backend не дублируется.
Additive v01_0003 не меняет старые таблицы или применённые v01_0001/0002.

Профильные проверки (совокупно **20 backend + 5 frontend**, все PASS):
- `python -m unittest backend.tests.v03.test_account_security` — новые PG
  scenarios: password/revocation, verified-only recovery, одноразовость,
  expiry/concurrent consume, owner/CSRF/closed DTO, email uniqueness,
  legacy login, IP/account budgets, proxy trust, отказ provider без enumeration.
  Фактически выполнялись 12 сценариев, затем отдельно добавленный 13-й audit
  concurrency после исправления; полные suites не запускались.
- Семь явно выбранных методов PostgreSQLIdentityTests: register/login/rotation/
  profile/logout, receipt conflict/replay, lost body/cookies recovery, CSRF/Host/
  Origin, strict JSON, expired session и concurrent same-proof registration.
  Запускались через unittest.TestSuite с перечисленными именами, не весь класс.
- `node node_modules/vitest/vitest.mjs run tests/account-security.test.ts tests/identity-ui.test.tsx`
  (cwd frontend): 5 PASS — безопасный return, generic login error, password
  clearing, unknown outcome reconciliation/no blind replay и Retry-After.
- PostgreSQL16 disposable fresh v01_0003 с exact physical comparison и upgrade
  v01_0002 → v01_0003 с неизменными synthetic user ID/login/hash/email — PASS.
  Рабочая/защищённая acceptance БД для тестов не использовалась.

Ручной просмотр штатного host-dev: default/1280×900 desktop и 390×844 mobile;
login light/dark, mobile register/account dark, desktop account/home light;
регистрация → ЛК, сохранение класса/refresh и правильный materials query,
login generic error/success, logout, guest account return, вошедший /auth → ЛК,
истечение только synthetic review sessions → вход, клавиатурный Tab/focus,
API ECONNREFUSED → нейтральная ошибка → успешное восстановление после autoreload.
Recovery при ненастроенной почте честно показывает недоступность доставки.
Это ручной просмотр автором, не независимое ревью и не человеческая приёмка.

Host-dev оставлен работающим: http://127.0.0.1:8131/ и /auth?mode=login.
Локальная схема отдельно обновлена signed TARGET_0002 plan
`1967ebab52ba795ce1cf50b90be8b811fe9ecfaa92206207b99c09b4c47565bc`;
APPLIED/CHECKED. План сохранён в ignored var/local/team; startup не запускает
DDL/tests/seed. Content publication и production deployment не выполнялись.
Временные scripts/config и собственная disposable DB удалены после проверок;
планы и существующие runtime данные сохранены.

Саморевью выявило и исправило: SQL погашения verify token, запрет GET mutations
при AllMethodRoute, grade.number вместо отсутствующего slug, восстановление
select после async options, uniform recovery response при provider failure,
и audit на том же соединении при concurrent failed login (без вложенной UoW).
Профильные затронутые проверки повторены; assertions не ослаблены.

Ограничения: mail provider/sender/live delivery не подключены; fake только в tests.
Предложение — Unisender Go transactional HTTPS API, sender на домене MathStart,
SPF/DKIM/DMARC, tracking off, secret только runtime. Выбор и контролируемая live
проверка остаются за Русланом. Durable mail queue/retry не реализована; loss
процесса может потребовать новый запрос после окна лимита. Production edge/TLS,
новая immutable SSG publication и реальная доставляемость не проверены.
Полные suites, общий typecheck и массовый QA уроков: NOT_RUN_BY_USER_REQUEST.
Независимое security/architecture review PENDING; human acceptance PENDING;
merge NOT_PERFORMED. Следующая карточка не начата, Issue не закрыт.
