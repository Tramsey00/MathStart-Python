# MS-T005 — SVG Linear Gradient: интеграция и статический разбор

Дата: 08.11.2026. Новый scoped execution record. Исторические reports/receipts/logs
и прежние подтверждения не переписаны; их PASS не подтверждает текущий candidate.

## Git и scope

Checkout: `C:/Users/User/PycharmProjects/MathStart-host-check`, ветка `ms-t005-grade-7`.
Вход: `b9086ff07fcc65c3cb530471f94d3ff26524b61a`, рабочее дерево чистое.
Origin: `https://github.com/Tramsey00/MathStart-Python.git`.
Существующая работа сохранена на месте; ignored runtime-файлы не перемещались.
Backup: `backup/ms-t005-before-svg-gradient-20261108-b9086ff` на входном HEAD.

Выполнены `git fetch origin 193c378525f5e2a736eed26c812758b855324ed9`,
ручное чтение полного `git show` и затем
`git cherry-pick -x 193c378525f5e2a736eed26c812758b855324ed9`.
Результат: **`1be06c90952c774565780f15211cc69acfacf5b4`**, конфликтов не было.
Не переносились диапазон коммитов, вся ветка или PR #63.

Итоговый implementation diff относительно входа прочитан вручную:

| Файл | Изменение |
| --- | --- |
| frontend/scripts/convert-lesson.mjs | 21 добавление, 1 удаление: SVG namespace/parent/attributes/children guards для linearGradient/stop, допуск stop attributes |
| backend/content/sources.py | 30 добавлений, 7 удалений: передача parent_tag при обходе, узкая проверка gradient/stop |

Итого **51 добавление, 8 удалений**, только два разрешённых общих файла.
Дополнительных изменений реализации нет. Предыдущие terminal titles b57b692 →
85b30aa и chart dimensions ee2c1d3 → 05e42b9 сохранены в текущих исходниках.
Прежние SVG font-style/fill-opacity, HTML code/img, URL и MathML правила
не удалены/не заменены этим diff. Сохранение проверено чтением diff/исходников,
без исполнения converter или validator. Документация добавляется отдельным commit.

## Статический разбор statistics-27

Source:
`curriculum/7-klass/veroyatnost-i-statistika/06-obobshhenie-sistematizaciya-znanij/01-obobshhenie-sistematizacziya-znanij/body.html`.

- :185–255 — SVG `viewBox="0 0 460 340"`, role img и авторская aria-label диаграммы частот от 14 до 20. Точная структура не редактировалась.
- :249–254 — `defs > linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1" > stop`. Есть одно определение barGrad в исходнике и семь `fill="url(#barGrad)"` в том же SVG. Defs расположен после столбцов; порядок сохраняется. Ссылка локальная, без внешнего URL.
- :251–252 — stops `offset="0%" stop-color="#60a5fa"` и `offset="100%" stop-color="#2563eb"`. По исходникам соответствуют новым узким ограничениям converter/validator: SVG namespace/контекст, требуемые родители, только указанные атрибуты, координаты 0/1, hex6 и крайние offsets. Gradient допускает только stop и whitespace (converter также пропускает comments); stop не содержит содержательных children.
- Не добавляются gradientUnits/gradientTransform/href/style, произвольные stop offsets или цвета. Новые правила не являются общей поддержкой всех SVG gradients.

Семь исходных столбцов (общие width=32, rx=9, baseline y+height=290):

| body.html | Значение/подпись X | Частота/подпись над столбцом | x | y | height |
| --- | --- | --- | --- | --- | --- |
| 213–215 | 14 | 1 | 108 | 232.5 | 57.5 |
| 218–220 | 15 | 3 | 151 | 117.5 | 172.5 |
| 223–225 | 16 | 3 | 194 | 117.5 | 172.5 |
| 228–230 | 17 | 1 | 237 | 232.5 | 57.5 |
| 233–235 | 18 | 1 | 280 | 232.5 | 57.5 |
| 238–240 | 19 | 2 | 323 | 175 | 115 |
| 243–245 | 20 | 1 | 366 | 232.5 | 57.5 |

Эти данные согласуются с показанным в source упорядоченным набором из 12 значений.
Фон #ffffff/#f9fafb, сетка #e5e7eb, оси #374151, частоты #1d4ed8,
X-подписи #374151 и Y-подписи #4b5563, координаты/размеры/viewBox не менялись.
Это сопоставление исходника, а не доказательство сохранности нового content.json.

## Совместимость с существующим renderer — только чтение

`frontend/src/shared/lesson/lesson-types.ts` задаёт generic tag:string/attrs/children.
`source-renderer.tsx` рекурсивно передаёт тег в createElement без отдельного списка
разрешённых SVG-тегов; для svg включается preserveMarkup, наследуемый потомками.
Поэтому defs, case-sensitive linearGradient, stop и порядок children по этому коду
не отбрасываются. id и fill остаются прежними; stop-color преобразуется в stopColor.
Теги gradient/stop не попадают в ветви интерактивов, таблиц, self-check или title.
`lesson-diagram.tsx` добавляет обёртку, не переписывая SVG definitions/references.

В прочитанных lesson.css/runtime.css правила масштабирования ms-svg задают width
100% / height auto и не меняют этот gradient или fill семи rect. Authored цвета
остаются фиксированными, включая белый фон. Контраст/масштабирование в светлой и
тёмной теме, реальный DOM/SSR, локальная ссылка и отсутствие ID-collision при
монтировании должны быть отдельно проверены в разрешённом будущем этапе.
Renderer/CSS не изменялись. По статическому чтению отдельная правка renderer для
этого градиента не выявлена; исполненной проверки совместимости нет.

## Нерешённые вопросы

1. **Дроби :492/:494/:582/:584**: ms-frac с ms-frac-num/ms-frac-den;
   `frontend/src/shared/lesson/math-notation.mjs:61–63` ищет ms-num/ms-den и
   иначе бросает Incomplete legacy fraction. Это прогноз по исходникам, не
   наблюдённый новый запуск. Исходные выражения: 200/12, 2/3 (смешанное 16 2/3),
   3/6 = 1/2. Нужна отдельно порученная эквивалентная поформульная MathML-адаптация;
   shared helper и учебный источник на этом этапе не менялись.
2. Terminal title :465 «7. Итоговая самопроверка» поддержан предыдущим fix.
   Нужно фактически подтвердить сохранность всех заданий/ответов и согласованную
   границу исключения последующего раздела :606; новый gradient fix не доказывает это.
3. Реальная конвертация/валидация документа и визуальное сравнение семи столбцов,
   градиента, подписей, геометрии, доступности и дробей ещё не выполнены.
4. Остальные семь тем статистики не пересматривались заново: вопросы структуры
   figures/nested heading (25/26), оформления bar/pie/equalizer (7/8/9), MathML (9),
   фактической конвертации/валидации и terminal preservation (4/8/18/26) остаются
   в [актуальном списке](../tasks/ms-t005-remaining.md).

## Результат и ограничения

**NOT_RUN_BY_USER_REQUEST:** tests, typecheck, Playwright, smoke, validators,
gates, QA-скрипты, повторная конвертация. Фактическая валидация, SSR/browser и
визуальная проверка не объявляются успешными. Штатные validation guards сохранены.

67/75 source activations неизменны: 66 MIGRATED + 1 REUSED_PILOT;
все восемь оставшихся тем BLOCKED_DEPENDENCY, включая statistics-27.
Активация, build, publication, snapshot update, merge — NOT_PERFORMED.
Маршруты алгебры 1/8 и все redirects, renderer/CSS/helper, учебные материалы
всех классов, БД, .venv и var/local не менялись. Issue #61 не закрывается.
Independent review и human acceptance PENDING.

Следующие действия — отдельное поручение: адаптация дробей, фактическая
конвертация и штатная валидация, затем проверка сохранности и визуального
результата перед любой активацией. Не удалять задания/ответы/SVG/данные.
