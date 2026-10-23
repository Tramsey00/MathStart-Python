---
name: mathstart-t001-lesson-pilot
description: Выполнить MS-T001 — Перенести новый HTML-урок по стандарту в основной React/SSG runtime; только по отдельному поручению из реестра MathStart.
---

# MS-T001 — Перенести новый HTML-урок по стандарту в основной React/SSG runtime

Зависимости: MS-T000. Статус — в [реестре](../../../docs/tasks/INDEX.md).
Карточка описывает будущий результат, не выдаёт наличие прототипа за готовность.

## Результат и входы

Новый пилот: **Линейная функция y = kx + b. График линейной функции**, 7 класс,
algebra. Этот урок ещё не перенесён на новый React-шаблон.

Точный источник — [папка урока](../../../curriculum/7-klass/algebra/02-linejnaya-funkciya-y-kx-b/03-linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii/),
slug — `linejnaya-funkcziya-y-kx-b-grafik-linejnoj-funkczii`. Запись уже есть в
[inventory](../../../docs/tasks/lesson-inventory.json); assigned_path пока null.
Назначить устойчивый URL при реализации через Content, не выводить его номер
из текущего порядка тем.

Квадратичная функция y = ax² + bx + c уже собрана в React preview и служит
визуальным эталоном и источником общих компонентов. Не повторять её визуальный
перенос в MS-T001. Её подключение к основному renderer/Content/FastAPI проверяется
в MS-T006 вместе с 8 классом; текущий preview и назначенный URL сохраняются.

Используй [общий skill переноса](../../lesson-migration/SKILL.md),
[архитектуру](../../../ARCHITECTURE.md), [стандарт переноса](../../../docs/frontend/lesson-migration.md),
[UI contract](../../../docs/ux/shared-ui-contract.md) и [проверки](../../../docs/frontend/testing-policy.md).
Не перечитывай прежние ТЗ/аудиты: они не являются входом этой задачи.

## Объём работы

1. Ввести validated content.json/renderer_version и один authoritative route mapping в Content.
2. Выделить из React-эталона общие layout и blocks; обобщить source adapters и registry интерактивов без привязки к квадратичной функции.
3. Подключить selective hydration через текущие prepare/build/publication, не обходя verified release.
4. Перенести новый линейный урок целиком. Текущий источник содержит 13 учебных секций, 13 самопроверок, 4 таблицы, 3 авторских SVG-схемы и интерактив y = kx + b. Сохранить все блоки, включая предварительные знания и экспресс-анализ; точный состав сверить перед переносом.
   Линейный график реализовать отдельным React interactive с чистой математикой: коэффициенты k/b, направление, пересечения с осями, координаты и reset к k=1, b=0. Не подменять его квадратичным графиком и не копировать оболочку урока.
5. Сохранить legacy renderer для неперенесённых страниц. Не публиковать заново все классы.
6. Проверить текст/формулы/ответы, redirects, no-JS article, touch/keyboard/reset, light/dark и reflow.
7. Поправить стандарт по реальному пилоту; очистить заменённые assets только после проверки потребителей.

## Приёмка

Новый урок «Линейная функция y = kx + b. График линейной функции» перенесён из HTML через общий skill; явно назначенный canonical URL обслуживается основным Content/FastAPI release; SSG содержит материал без JS; React-интерактивность работает без hydration mismatch; все секции, самопроверки, формулы, таблицы, SVG и старые адреса/якоря сохранены; стандарт подтверждён на новом уроке и принят пользователем.

Отметь реализацию, проверки, отдельное review и human acceptance раздельно.
Выбирай проверки по области изменения; не ослабляй семантические/API/security
assertions ради нового внешнего вида. Список неисполненных пунктов и ограничения
передай явно. Результат/команды фиксируй кратко в задаче или PR; временные outputs
в var/ либо frontend/.cache/, без новых tracked audit folders и массовых captures.

## Границы

Сохрани чужой dirty tree, учебную математику и пользовательские данные. Не меняй
платформу публикации вне необходимых документированных adapters. Не трогай
protected acceptance DB. Не запускай следующую карточку автоматически. Merge,
production и provider/security решения требуют отдельного поручения человека.

## GitHub и ветка

Работать в ui/ux без отдельного Issue и без новой ветки на каждую задачу. Исключение действует только для MS-T001, MS-T002, MS-T002A. Готовность локального запуска проходит review в MS-T002A, затем пользователь решает merge ui/ux в main. Проверка clone опубликованного main завершает MS-T002A и открывает MS-T003.

## Выполнение 24.10.2026 — кандидат для проверки

Исходный HEAD подготовки: b29a7ccdd07784cfcfd19278cbe59b30c83cd4ea.
Согласованный пакет MS-T000: 406995b4005d9b78525f3e985e9345a5437a5e67;
ui/ux перенесена fast-forward, main не изменялся. Приёмка MS-T000 явно дана
пользователем 24.10.2026 и записана в реестре.

Реализация пилота: content.json lesson-document-v1, 13 секций/13 самопроверок/
4 таблицы/3 SVG/1 linear interactive; общий LessonPage, header/footer,
содержание, disclosure и controls. Учебный текст, клетки таблиц и SVG сверены
с source. Назначен `/materials/7-algebra-1` через Content registry, legacy slug
и aliases переводятся непосредственно на canonical. Квадратичный preview
сохранён; новый renderer не включён для других уроков.

Самопроверка до managed runtime: npm test — 214 PASS; проверки новой линейной
математики, жестов, полного текста/таблиц/SVG и hydration — 6 PASS в составе
набора. backend test_lesson_document — 6 PASS; repository_history — 5 PASS.
Первый запуск Vitest/TemporaryDirectory в sandbox завершился EPERM;
повтор вне sandbox прошёл. Typecheck и docs/provenance gates завершаются
отдельно. Runtime, отдельное review и визуальная приёмка пока PENDING.

Полный managed target выполняется только на собственных disposable ресурсах:
PostgreSQL 16 127.0.0.1:55441, target и отдельный pinned legacy oracle в
var/t001-qa; рабочий стек не используется. Результаты и failures сохраняются
в игнорируемом var/t001-qa. Host Node 24.19/npm 11.17 удовлетворяют engines;
CI builder использует pinned Node 24.21/npm 11.19. Полный CI не подменяется
локальным быстрым профилем. Статус визуальной приёмки — HUMAN_PENDING.
