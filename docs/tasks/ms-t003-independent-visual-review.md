# MS-T003 — пакет независимого визуального ревью 35 тем 5-го класса

Автор: **Владимир**. Независимый проверяющий: **Илья (MS-T005)**.
PR: [#63](https://github.com/Tramsey00/MathStart-Python/pull/63), Issue: [#60](https://github.com/Tramsey00/MathStart-Python/issues/60).
Дата подготовки: 11.11.2026. Статус независимого ревью: **NOT_STARTED, 0/35**.

## 1. Зафиксированная версия и границы

**Source SHA для checkout, подготовки Content и ревью: `a833f3b0e0e5e0b764206d52c96acf970a8ebb72`.**
Это фактический опубликованный HEAD PR #63 перед документационным коммитом пакета.
Коммит самого пакета добавляется после этого SHA и не меняет приложение.
Не подставляйте новый HEAD ветки вместо source SHA: при изменении кандидата нужен новый явно согласованный источник.

В source включены:
- [dd6ab73ce0755c01cdb06ae5c9409fdedbd87dad](https://github.com/Tramsey00/MathStart-Python/commit/dd6ab73ce0755c01cdb06ae5c9409fdedbd87dad) — общий React-renderer: 5 алгоритмов, 23 шага, существующие ms-proof-step/ms-step-number;
- [a833f3b0e0e5e0b764206d52c96acf970a8ebb72](https://github.com/Tramsey00/MathStart-Python/commit/a833f3b0e0e5e0b764206d52c96acf970a8ebb72) — правило «Смысловые группы и перенос строк».

Владимир сообщил: первичный просмотр всех 35 страниц — `35/35 USER_VISUAL_REVIEWED, NO_ISSUES_REPORTED`;
локальное исправление алгоритмов затем отдельно визуально проверено им и устраивает его.
Это не независимое ревью Ильи, не полная сверка с исходниками и не окончательная приёмка Русланом.
Ранее открытый R1 (столбики, №4) независимо проверить именно в новом собранном артефакте;
предыдущий просмотр через DevTools/HMR не выдаётся за приёмку этого артефакта.

Порядок работы: [обязательный регламент взаимного ревью Руслана](https://github.com/Tramsey00/MathStart-Python/blob/507c561a0a3f233923e3d02c6d9ce0913f233e1b/docs/frontend/testing-policy.md#взаимное-ручное-ревью-уроков).
Он опубликован отдельно от проверяемого source; его отсутствие в старом файле кандидата не отменяет регламент.
Автоматические tests/typecheck/Playwright/smoke/gates и новые QA-скрипты: **NOT_RUN_BY_USER_REQUEST**.
Выпуск, merge и закрытие Issue не входят в ревью. Итоговая приёмка и решение о merge — за Русланом.

## 2. Все 35 тем — рабочая таблица Ильи

Источник списка: [inventory](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/docs/tasks/lesson-inventory.json),
[постоянные маршруты](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/site_content/material-routes.json), реальные lesson.json/content.json.
Все 35 назначений и lesson.json имеют renderer_version=react-v1; у каждого есть content.json.
Порядок — постоянные номера курса 1–35, пять разделов. Это сведения исходников, не результат запуска у Ильи.

**Ссылки http://127.0.0.1:8131 ниже относятся к компьютеру Ильи после его собственной подготовки.**
Это не доступ к серверу Владимира. До публикации/запуска они могут не открываться.
Название темы в таблице — ссылка на замороженный исходный body.html в GitHub, не на живой legacy-сайт.

Результаты: `NOT_REVIEWED` → `OK` / `ISSUE` / `BLOCKED`.
`OK` ставится только после фактического просмотра широкого и узкого вариантов и проверки относящихся к теме интерактивов.

| № | Название темы | URL | Результат ревью | Комментарий |
| --- | --- | --- | --- | --- |
| 1 | [Числовые и буквенные выражения](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/01-naturalnye-chisla/01-5-klass-chislovye-i-bukvennye-vyrazheniya/body.html) | [/materials/5-math-1](http://127.0.0.1:8131/materials/5-math-1) | NOT_REVIEWED | — |
| 2 | [Определение координатного луча](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/01-naturalnye-chisla/02-5-klass-koordinatnyy-luch/body.html) | [/materials/5-math-2](http://127.0.0.1:8131/materials/5-math-2) | NOT_REVIEWED | — |
| 3 | [Округление чисел. Прикидка и оценка результатов вычислений](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/01-naturalnye-chisla/03-5-klass-okruglenie-chisel-prikidka/body.html) | [/materials/5-math-3](http://127.0.0.1:8131/materials/5-math-3) | NOT_REVIEWED | — |
| 4 | [Законы арифметических действий. Вычисления с многозначными числами](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/01-naturalnye-chisla/04-5-klass-zakony-arifmeticheskih-deystviy/body.html) | [/materials/5-math-4](http://127.0.0.1:8131/materials/5-math-4) | NOT_REVIEWED | — |
| 5 | [Сравнение натуральных чисел](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/01-naturalnye-chisla/05-5-klass-sravnenie-naturalnyh-chisel/body.html) | [/materials/5-math-5](http://127.0.0.1:8131/materials/5-math-5) | NOT_REVIEWED | — |
| 6 | [Решение текстовых задач арифметическим способом](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/01-naturalnye-chisla/06-5-klass-tekstovye-zadachi-arifmeticheskiy-sposob/body.html) | [/materials/5-math-6](http://127.0.0.1:8131/materials/5-math-6) | NOT_REVIEWED | — |
| 7 | [Формулы. Уравнения. Упрощение выражений](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/01-naturalnye-chisla/07-5-klass-formuly-uravneniya-uproshchenie-vyrazheniy/body.html) | [/materials/5-math-7](http://127.0.0.1:8131/materials/5-math-7) | NOT_REVIEWED | — |
| 8 | [Математический язык и математическая модель](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/01-naturalnye-chisla/08-5-klass-matematicheskiy-yazyk-model/body.html) | [/materials/5-math-8](http://127.0.0.1:8131/materials/5-math-8) | NOT_REVIEWED | — |
| 9 | [Делимость натуральных чисел](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/02-razlozhenie-chisla-na-prostye-mnozhiteli/01-5-klass-delimost-naturalnyh-chisel/body.html) | [/materials/5-math-9](http://127.0.0.1:8131/materials/5-math-9) | NOT_REVIEWED | — |
| 10 | [Признаки делимости](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/02-razlozhenie-chisla-na-prostye-mnozhiteli/02-5-klass-priznaki-delimosti/body.html) | [/materials/5-math-10](http://127.0.0.1:8131/materials/5-math-10) | NOT_REVIEWED | — |
| 11 | [Простые и составные числа. Разложение натурального числа на простые множители](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/02-razlozhenie-chisla-na-prostye-mnozhiteli/03-5-klass-prostye-i-sostavnye-chisla/body.html) | [/materials/5-math-11](http://127.0.0.1:8131/materials/5-math-11) | NOT_REVIEWED | — |
| 12 | [Деление с остатком. Понятие обыкновенной дроби](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/03-obyknovennye-drobi/01-5-klass-ponyatie-obyknovennoy-drobi/body.html) | [/materials/5-math-12](http://127.0.0.1:8131/materials/5-math-12) | NOT_REVIEWED | — |
| 13 | [Основное свойство дроби. Сокращение дробей](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/03-obyknovennye-drobi/02-osnovnoe-svojstvo-drobi-sokrashhenie-drobej/body.html) | [/materials/5-math-13](http://127.0.0.1:8131/materials/5-math-13) | NOT_REVIEWED | — |
| 14 | [Правильные и неправильные дроби. Смешанные числа. Понятие, запись и чтение](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/03-obyknovennye-drobi/03-pravilnye-i-nepravilnye-drobi-smeshannye-chisla-ponyatie-5c2ab626/body.html) | [/materials/5-math-14](http://127.0.0.1:8131/materials/5-math-14) | NOT_REVIEWED | — |
| 15 | [Сравнение обыкновенных дробей](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/03-obyknovennye-drobi/04-sravnenie-obyknovennyh-drobej/body.html) | [/materials/5-math-15](http://127.0.0.1:8131/materials/5-math-15) | NOT_REVIEWED | — |
| 16 | [Сложение и вычитание обыкновенных дробей и смешанных чисел](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/03-obyknovennye-drobi/05-slozhenie-i-vychitanie-obyknovennyh-drobej-i-smeshannyh-ee005929/body.html) | [/materials/5-math-16](http://127.0.0.1:8131/materials/5-math-16) | NOT_REVIEWED | — |
| 17 | [Умножение и деление обыкновенной дроби на натуральное число](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/03-obyknovennye-drobi/06-umnozhenie-i-delenie-obyknovennoj-drobi-na-naturalnoe-ch-ef032d25/body.html) | [/materials/5-math-17](http://127.0.0.1:8131/materials/5-math-17) | NOT_REVIEWED | — |
| 18 | [Нахождение части от целого и числа по его части](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/03-obyknovennye-drobi/07-nahozhdenie-chasti-ot-czelogo-i-chisla-po-ego-chasti/body.html) | [/materials/5-math-18](http://127.0.0.1:8131/materials/5-math-18) | NOT_REVIEWED | — |
| 19 | [Понятие десятичной дроби. Представление десятичной дроби в виде обыкновенной дроби и наоборот](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/04-desyatichnye-drobi/01-ponyatie-desyatichnoj-drobi-predstavlenie-desyatichnoj-d-b71f2061/body.html) | [/materials/5-math-19](http://127.0.0.1:8131/materials/5-math-19) | NOT_REVIEWED | — |
| 20 | [Десятичные дроби. Сравнение](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/04-desyatichnye-drobi/02-desyatichnye-drobi-sravnenie/body.html) | [/materials/5-math-20](http://127.0.0.1:8131/materials/5-math-20) | NOT_REVIEWED | — |
| 21 | [Десятичные дроби. Сложение и вычитание](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/04-desyatichnye-drobi/03-desyatichnye-drobi-slozhenie-i-vychitanie/body.html) | [/materials/5-math-21](http://127.0.0.1:8131/materials/5-math-21) | NOT_REVIEWED | — |
| 22 | [Десятичные дроби. Умножение](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/04-desyatichnye-drobi/04-desyatichnye-drobi-umnozhenie/body.html) | [/materials/5-math-22](http://127.0.0.1:8131/materials/5-math-22) | NOT_REVIEWED | — |
| 23 | [Степень с натуральным показателем](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/04-desyatichnye-drobi/05-stepen-s-naturalnym-pokazatelem/body.html) | [/materials/5-math-23](http://127.0.0.1:8131/materials/5-math-23) | NOT_REVIEWED | — |
| 24 | [Десятичные дроби. Среднее арифметическое, деление на натуральное число](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/04-desyatichnye-drobi/06-desyatichnye-drobi-srednee-arifmeticheskoe-delenie-na-na-2b7d66e9/body.html) | [/materials/5-math-24](http://127.0.0.1:8131/materials/5-math-24) | NOT_REVIEWED | — |
| 25 | [Десятичные дроби. Деление на десятичную дробь](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/04-desyatichnye-drobi/07-desyatichnye-drobi-delenie-na-desyatichnuyu-drob/body.html) | [/materials/5-math-25](http://127.0.0.1:8131/materials/5-math-25) | NOT_REVIEWED | — |
| 26 | [Округление десятичных дробей](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/04-desyatichnye-drobi/08-okruglenie-desyatichnyh-drobej/body.html) | [/materials/5-math-26](http://127.0.0.1:8131/materials/5-math-26) | NOT_REVIEWED | — |
| 27 | [Начальные геометрические понятия: прямая, отрезок, луч, ломаная, прямоугольник](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/01-nachalnye-geometricheskie-ponyatiya-pryamaya-otrezok-luc-32a7b967/body.html) | [/materials/5-math-27](http://127.0.0.1:8131/materials/5-math-27) | NOT_REVIEWED | — |
| 28 | [Угол. Измерение углов](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/02-ugol-izmerenie-uglov/body.html) | [/materials/5-math-28](http://127.0.0.1:8131/materials/5-math-28) | NOT_REVIEWED | — |
| 29 | [Биссектриса угла. Свойство биссектрисы угла](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/03-bissektrisa-ugla-svojstvo-bissektrisy-ugla/body.html) | [/materials/5-math-29](http://127.0.0.1:8131/materials/5-math-29) | NOT_REVIEWED | — |
| 30 | [Треугольник. Площадь треугольника](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/04-treugolnik-ploshhad-treugolnika/body.html) | [/materials/5-math-30](http://127.0.0.1:8131/materials/5-math-30) | NOT_REVIEWED | — |
| 31 | [Свойство углов треугольника](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/05-svojstvo-uglov-treugolnika/body.html) | [/materials/5-math-31](http://127.0.0.1:8131/materials/5-math-31) | NOT_REVIEWED | — |
| 32 | [Геометрические понятия: окружность и круг](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/06-geometricheskie-ponyatiya-okruzhnost-i-krug/body.html) | [/materials/5-math-32](http://127.0.0.1:8131/materials/5-math-32) | NOT_REVIEWED | — |
| 33 | [Прямоугольный параллелепипед. Определение, свойства](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/07-pryamougolnyj-parallelepiped-opredelenie-svojstva/body.html) | [/materials/5-math-33](http://127.0.0.1:8131/materials/5-math-33) | NOT_REVIEWED | — |
| 34 | [Прямоугольный параллелепипед. Развёртка](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/08-pryamougolnyj-parallelepiped-razvyortka/body.html) | [/materials/5-math-34](http://127.0.0.1:8131/materials/5-math-34) | NOT_REVIEWED | — |
| 35 | [Прямоугольный параллелепипед. Объём](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika/05-vvedenie-v-geometriyu/09-pryamougolnyj-parallelepiped-obyom/body.html) | [/materials/5-math-35](http://127.0.0.1:8131/materials/5-math-35) | NOT_REVIEWED | — |


## 3. Откуда брать эталоны и исходники

Содержимое сохраняется по исходным HTML и их CSS: тексты, все формулы, числа, ответы,
полные решения, подписи SVG, медиа, порядок и оставленные anchors.
Внешний вид соответствует принятой системе MathStart, а не старой палитре/карточкам.
Не требуйте пиксельного совпадения legacy-дизайна с новым интерфейсом.

- [Замороженные исходные материалы всего 5-го класса](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/curriculum/5-klass/matematika): у каждой темы body.html, lesson.json, при наличии page.css/page.js; отдельные ссылки body.html — в таблице.
- [Общие исходные стили](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/static/mathstart/css) помогают понять связь элементов, но не подключаются поверх нового UI.
- [Стандарт переноса](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/docs/frontend/lesson-migration.md), в том числе «Действующие решения пользователя» и «Смысловые группы и перенос строк».
- [Общий UI-контракт](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/docs/ux/shared-ui-contract.md).
- [Утверждённая тема и шрифты](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/docs/ux/theme-baseline.md).
- **Эталонный урок: [8-algebra-32](http://127.0.0.1:8131/materials/8-algebra-32)** — на том же локальном сайте после подготовки. Сравнивать оболочку, типографику, примеры, диаграммы, содержание и поведение; не копировать математику или предметный состав.

Живой дореформенный сайт с этими страницами в пакете не подтверждён. Старые URL могут
перенаправлять на новые React-страницы и не являются независимым legacy-эталоном.
HTML по GitHub показывает исходную разметку, а не готовый браузерный рендер.
Не устанавливайте Django/DRF в target и не используйте исходную Django DB.
Если нужен исполняемый legacy-эталон, это отдельное согласование по [pinned oracle](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/docs/legacy-oracle.md), не часть запуска ниже.

## 4. Подготовка собственного окружения Ильи — Windows

Это инструкция будущих действий Ильи/его Codex, **не отчёт об их выполнении автором**.
При поручении агенту сохраняются две обязательные остановки перед применением планов.
Не копировать var/, .venv, node_modules, БД, credentials или frontend builds Владимира.
Не менять рабочую MS-T005 и её БД. Для первого независимого просмотра — отдельный полный clone.

### 4.1. Получение точного source

Выберите новую короткую папку **вне любого каталога `var`**: например C:/Projects/MathStart-T003-review.
На кандидате исходный Vite deny `**/var/**` блокирует вложенные worktree; локальный обход Владимира в пакет не включён и не нужен в обычном clone.
Если папка уже существует, не пересоздавать её и не стирать данные: сначала установить её SHA и владельца конфигурации.

```powershell
Set-Location C:/Projects
$sourceSha = 'a833f3b0e0e5e0b764206d52c96acf970a8ebb72'
git clone --no-checkout -c http.version=HTTP/1.1 -c core.longpaths=true -c core.autocrlf=false https://github.com/Tramsey00/MathStart-Python.git MathStart-T003-review
Set-Location C:/Projects/MathStart-T003-review
git fetch origin refs/pull/63/head
git switch --detach $sourceSha
git rev-parse HEAD
git status --short
```

Ожидается точно source SHA выше и чистое дерево. Если команда завершилась ошибкой,
SHA отличается или дерево неожиданно изменено — остановиться. Не rebase/merge/reset и не подменять источник плавающим main.
Документ пакета открыт через GitHub отдельно: его отсутствие в checkout source SHA нормально.

### 4.2. Требования и зависимости — только если эта копия ещё не подготовлена

Следовать [штатному руководству Windows host-dev](https://github.com/Tramsey00/MathStart-Python/blob/a833f3b0e0e5e0b764206d52c96acf970a8ebb72/docs/local-development-host.md#требования).
Нужны Windows LongPathsEnabled=1 (проверить до подготовки), Git long paths, Python 3.12,
Node 24.x/npm 11.x и Docker Desktop Linux Engine. Не менять настройки Windows автоматически.

```powershell
Get-ItemPropertyValue -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled
python --version
node --version
npm.cmd --version
docker version
Get-NetTCPConnection -State Listen -LocalPort 8131,8132,55452 -ErrorAction SilentlyContinue
```

8131/8132 нужны штатному сайту. 55452 — пример отдельного свободного порта новой БД;
если занят — согласовать другой до init. Не завершать неизвестные процессы. Свой MS-T005
при необходимости штатно остановить из его папки, сохранив данные; одновременно оба режима на 8131 не работают.
Проверить существующие Docker containers/volumes (`docker ps -a`, `docker volume ls`), ничего не удалять.

В новом checkout выполнить только один раз locked установку:

```powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --no-deps -r requirements.lock
& .\.venv\Scripts\python.exe -m pip check
npm.cmd --prefix frontend ci --no-audit --no-fund
```

Это установка зависимостей, не разрешение на тесты. Не использовать shallow clone:
build inputs читают исторические Git pins. Не повторять установку при готовом окружении.

### 4.3. Своя PostgreSQL и schema-preview — ПЕРВАЯ ОБЯЗАТЕЛЬНАЯ ОСТАНОВКА

Все дальнейшие команды — из C:/Projects/MathStart-T003-review.

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py init --pg-port 55452
& .\.venv\Scripts\python.exe scripts/team_local.py schema-preview
```

Init создаёт собственные container/volume/roles/credentials в ignored var/local/team.
Нельзя использовать существующую БД MS-T005 или host-check.
**ОСТАНОВИТЬСЯ:** показать человеку полный var/local/team/schema.json, напечатанный штатной
командой SHA256, profile=FRESH, исходные таблицы=0, target head, срок действия,
локальный порт/контейнер/volume и принадлежность checkout.
План обычно действует 30 минут; до apply повторно проверить срок и неизменность.
SHA256 подтверждает лично человек. Не применять по одному факту появления файла.
Не публиковать приватные планы, DSN и credentials на GitHub.

Только после личного подтверждения точного SHA256 и разрешения человека:

```powershell
$schemaSha256 = Read-Host 'Лично подтверждённый SHA256 schema plan'
& .\.venv\Scripts\python.exe scripts/team_local.py schema-apply --reviewed-plan-sha256 $schemaSha256
```

Нужны штатные APPLIED и CHECKED, Alembic head v01_0002 на этом кандидате.
Истёкший/изменённый план или неопределённый результат — остановиться, сохранить журнал;
новый план согласовать отдельно. Не повторять FRESH apply и не выполнять recovery наугад.

### 4.4. Content inputs — ВТОРАЯ ОБЯЗАТЕЛЬНАЯ ОСТАНОВКА

При готовой схеме и чистом source SHA, один раз:

```powershell
git rev-parse HEAD
git status --short
& .\.venv\Scripts\python.exe scripts/team_local.py content
```

Команда выполняет штатную необходимую подготовку inputs и frontend build, затем
создаёт publication plan; это не отдельные QA/release builds после каждой темы.
Подготавливается общий Content кандидата, а scope визуального ревью — 35 страниц таблицы.
**ОСТАНОВИТЬСЯ ДО PUBLISH:** человек смотрит полный var/local/team/publication.json и
лично подтверждает напечатанный штатной командой SHA256. Сверить initial install,
previous=null, origin http://127.0.0.1:8131, release_id новой установки, список изменений
и Prepared source SHA — строго a833f3b0e0e5e0b764206d52c96acf970a8ebb72.
Чужие hashes из переписки MS-T003/MS-T005 не подходят к новой установке.
Использовать штатный digest плана, не заменять его произвольным hash форматированного JSON.

При ошибке content сохранить журналы, не повторять автоматически. Если inputs/планы
уже существуют, установить состояние, не перезаписывать и не повторять команду вслепую.

### 4.5. Публикация — только после второго подтверждения

Временный gateway штатной публикации требует свободного 8131. Встроенный
finish_cold_publication способен выполнить bounded renew → warmup → renew → resume
после PUBLIC_VERIFICATION_FAILED, только при всех его ownership/release/generation guards.
Перед запуском человек должен разрешить именно штатный вызов с этим встроенным
механизмом; не отключать guards и не запускать дополнительные ручные recovery/retry.

```powershell
$publicationSha256 = Read-Host 'Лично подтверждённый SHA256 publication plan'
& .\.venv\Scripts\python.exe scripts/team_local.py publish --reviewed-plan-sha256 $publicationSha256
```

Успех — только COMPLETE, не warmup и не один HTTP 200. При ошибке/отказе встроенного
продолжения остановиться, сохранить operation_id, phase и очищенные логи; не повторять publish/recover.

### 4.6. Сверка версии перед браузером

```powershell
git rev-parse HEAD
git status --short
Get-Content var/local/team/logs/source-sha.log
$reviewPlan = Get-Content var/local/team/publication.json -Raw | ConvertFrom-Json
$reviewPlan | Select-Object release_id,origin,previous
$reviewReceipt = Get-Content (Join-Path 'var/local/team/inputs' ($reviewPlan.release_id + '/receipt.json')) -Raw | ConvertFrom-Json
$reviewReceipt.source_sha
$operationId = Read-Host 'Operation ID завершённой публикации'
& .\.venv\Scripts\python.exe -B -c "import sys; sys.path.insert(0,'scripts'); import team_local as t; print(t.cli('backend.content.publish',['status','--operation-id',sys.argv[1]],'review-status-readonly',t.read_json(t.LOCAL/'schema-env.json')))" $operationId
```

Последняя команда — штатный CLI status с настройками только этой БД, без изменения
БД или recovery. Пароли не выводятся и не передаются в аргументах.
Обязательно записать в результаты:
- HEAD = Prepared source SHA = receipt.source_sha = a833f3b0e0e5e0b764206d52c96acf970a8ebb72;
- release_id плана = active.release_id отдельной локальной БД;
- operation.phase = COMPLETE, error_code=null, activation_status=APPLIED;
- operation_id и generation совпадают с активным descriptor;
- собственные checkout, контейнер и порт БД. Не копировать секретные конфиги в отчёт.

Если что-либо не совпало — ревью BLOCKED, не считать открывшийся сайт правильной версией.

### 4.7. Открытие и штатная остановка

```powershell
Set-Location C:/Projects/MathStart-T003-review
npm.cmd --prefix frontend run dev:host
```

Дождаться **«Host-dev готов»**, затем открыть http://127.0.0.1:8131/materials и URL таблицы.
Проверить полноценный React-урок с общими шапкой/footer и боковым «Содержанием»;
отдельный HTML-макет не подходит. Первые адреса: /materials/5-math-2 и /materials/5-math-4.
Работающий сервер оставляет терминал занятым.
Остановка Ctrl+C или из второго PowerShell **этого же checkout**:

```powershell
npm.cmd --prefix frontend run dev:host:stop
```

Данные/volume сохраняются. При последующих обычных запусках не повторять init/schema/content/publish.
Если нужно проверить именно собранные CSS/renderer артефакты без HMR, после остановки dev:

```powershell
& .\.venv\Scripts\python.exe scripts/team_local.py db-start
& .\.venv\Scripts\python.exe scripts/lesson_server.py --env-file var/local/team/private-env.json
```

Это тот же опубликованный release на 8131; остановка Ctrl+C. Не работать одновременно с Vite.
Не запускать новый build ради переключения режима. Для проверки R1 предпочтительно
отдельно посмотреть собранную версию после подтверждённой публикации source SHA.

## 5. Чек-лист ручного ревью

Илья смотрит **все 35 тем**, а не только исправленные примеры. На каждой странице:

- [ ] Полноценная общая оболочка, шапка, footer, sidebar «Содержание», отсутствие старого дублирующего UI.
- [ ] Заголовки и иерархия текста, исходные названия и порядок секций.
- [ ] Все номера/символы стоят у первой строки своего пункта; продолжения выровнены по началу текста.
- [ ] Заголовок и пояснение/термин и определение визуально принадлежат одной группе; внутри группы меньше отступ, чем между группами.
- [ ] Длинные строки переносятся, нет слипшегося текста, лишних пустых строк или обрезания.
- [ ] Формулы, MathML-дроби, смешанные числа, показатели, знаки операций и смысловые переносы сохранены.
- [ ] Примеры, списки чисел, все задания, ответы и раскрываемые полные решения на месте.
- [ ] Таблицы и карточки читаются; необходимая широкая таблица прокручивается без горизонтального scroll всей страницы.
- [ ] Все SVG/изображения, подписи точек, размеры, координаты, вероятности и линии видимы, не обрезаны.
- [ ] Внутренние ссылки и anchors, каждый пункт «Содержания», переходы между темами/разделами работают.
- [ ] Уникальные интерактивы, выбор параметров и раскрытие решений сохраняют исходный смысл.
- [ ] Широкий экран около 1200 px и узкий около 390 px, масштаб браузера 100%; указать точные размеры viewport. В Edge: F12 → Ctrl+Shift+M → Responsive.

Дополнительно проверить:

| Темы | Место особого внимания |
| --- | --- |
| 2 | «Алгоритм» (4 шага) и «Алгоритм построения точки» (4 шага), итог 8 |
| 3 | Алгоритм округления, 6 шагов |
| 4 | «Алгоритм выбора способа», 5 шагов; столбики 7004 − 2589, 326 × 7, 428 × 36; 1284 сдвинуто влево на разряд относительно 2568, итог 15408 |
| 5 | Алгоритм сравнения по разрядам, 4 шага |
| 7 | SVG и стрелки с marker-start; уравнения/формулы |
| 10 | Дополнительный подзаголовок «Признаки делимости на 2, 5 и 10»; карточки «на 2/5/10» |
| 11 | Число/термин и пояснение в ms-card |
| 12–18 | Составные дроби, MathML, ответы и решения |
| 19–26 | Десятичная запись, таблицы и последовательности вычислений |
| 29–32 | Геометрия SVG, dy, подписи, биссектриса и площадь треугольника |
| 33–35 | data-hidden-edges; в №34 все 30 rect и исходная развёртка; в №35 a/b/c с пояснениями |

Исправление алгоритмов ограничено полным div.ms-rule-box из text/br с номерами строго 1..N.
Другие структуры не преобразуются. Независимо пересмотреть все **5 блоков / 23 шага**, даже
при положительном результате автора. Статус автора не переносить в таблицу Ильи.

При сравнении с источником учитывать утверждённые исключения стандарта:
prerequisite и учебные блоки после терминальной самопроверки исключены по решению пользователя;
сама самопроверка сохраняется целиком со всеми заданиями/ответами/решениями.
Иные потери не оправдываются этим правилом; сомнение записать конкретным замечанием.

## 6. Единый формат замечаний и итог

Копировать для каждой ошибки в комментарий PR #63; добавить строки ISSUE/BLOCKED в таблицу.

```text
Замечание: T003-RV-001
Source SHA: a833f3b0e0e5e0b764206d52c96acf970a8ebb72
Проверяющий: Илья
Тема: ID и название
URL: /materials/5-math-N#исходный-anchor (если есть)
Место: название раздела или элемента
Проблема: что отображается неправильно
Ожидаемый результат: как должно выглядеть; ссылка на стандарт/исходник
Скриншот: при необходимости, без секретов и личных данных
Ширина экрана: широкий/мобильный, точный viewport и масштаб
Режим: host-dev или опубликованный FastAPI release
```

При блокировке запуска указать точный этап, ошибку и очищенный журнал; не раскрывать DSN,
пароли, cookies, токены и содержимое приватных конфигураций.
Итог Ильи: source SHA, режим, release_id, число просмотренных/OK/ISSUE/BLOCKED,
таблица всех 35 тем, список замечаний, непроверенные интерактивы и ограничения.
Результаты фиксировать в PR #63, не считать само наличие PR или COMPLETE приёмкой уроков.
После отдельных исправлений — тот же проверяющий смотрит затронутые URL на новом SHA.
Руслан смотрит выборку и исправленные места, принимает результат и отдельно решает merge.
