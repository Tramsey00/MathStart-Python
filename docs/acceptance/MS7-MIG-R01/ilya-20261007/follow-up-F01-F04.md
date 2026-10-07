# F01–F04: обязательный follow-up, без исправлений в R01

Исходный baseline сохраняется: `8c11edadc8debc81432d1db1145feac504f09061`.
Выбор владельца Руслана записан из прямого запроса; [собственный комментарий Ильи](https://github.com/Tramsey00/MathStart-Python/pull/46#issuecomment-6046690988)
принимает D02 с известными F01–F04 и обязательным follow-up. Это исключение
для исходного snapshot; дефекты не должны автоматически переходить в final React.
Результаты, severity, routes, reproduction и исходные screenshots взяты из
[неизменённого отчёта](package/ui-review-report.md) и [его JSON](package/ui-review-summary.json).

Текущее состояние всех четырёх: **MANDATORY / ASSIGNED / NOT IMPLEMENTED**.
Tracking owner — Руслан / Tramsey00, владелец R01. Согласованный исполнитель —
Илья / 13baybars: собственный финальный комментарий и подтверждение Руслана.
Исправления не позже I03, проверка в I05 до итогового UI/content freeze.

| Finding | Severity / route / source | Screenshot | Ожидаемый результат |
| --- | --- | --- | --- |
| F01: содержание обрезается в двух колонках | P2; четыре lesson routes из JSON; `static/mathstart/css/lesson-contents.css` | [linear](package/screenshots/linear-function-360-toc-clipping.jpg), [power](package/screenshots/power-functions-360-toc-clipping.jpg), [circle](package/screenshots/number-circle-360-toc-clipping.jpg), [number line](package/screenshots/ordinary-number-line-360-toc-clipping.jpg) | На 360×800 все подписи читаются внутри карточек без overlap/clipping; содержимое и keyboard links сохранены. |
| F02: 12 presets перекрываются | P2; `/10-klass-stepennye-funkcii-i-grafiki-2-0/`; `static/mathstart/css/widgets/power-functions.css` | [presets](package/screenshots/power-functions-360-reset.jpg) | Все 12 формул читаются и различимы на 360×800; pointer, keyboard, aria-pressed и математика корректны. |
| F03: значение таблицы выходит за ячейку | P2; тот же route/source | [table](package/screenshots/power-functions-360-table-clipping.jpg) | При p=2 и x=0,25 значение 0,0625 полностью видно в своей ячейке без перекрытия; данные не меняются. |
| F04: мелкие SVG подписи | P3; `/10-klass-chislovaya-okruzhnost-2-0/`; lesson-local `page.css` и `body.html`, точные пути в JSON | [lab](package/screenshots/number-circle-360-reset.jpg), [12-part diagram](package/screenshots/number-circle-360-svg4-viewport.jpg) | На 360×800 SVG-подписи лаборатории и схем 8/12 частей читаемы при обычном масштабе без clipping/overlap. Увеличение само по себе недостаточно; углы, координаты, text readout, controls и математика сохранены; regression768/1440. |

**Воспроизведение:** на 360×800 открыть указанные routes в исходном baseline.
F01 — прокрутить к открытому содержанию и сравнить длинные подписи с границами
карточек. F02 — перейти к интерактиву степенной функции и строке p presets.
F03 — оставить default p=2, прокрутить к таблице и прочитать x=0,25.
F04 — перейти к лаборатории окружности и схемам 8/12 частей, прочитать SVG подписи.
Точные исходные steps/наблюдения/source paths и полные критерии:
[follow-up JSON](follow-up-F01-F04.json). На 768/1440 F01–F03 не воспроизведены
в данном review; target исправление требует повторных проверок всех трёх ширин.

Связи с уже зарегистрированными задачами:
[R02 #29](https://github.com/Tramsey00/MathStart-Python/issues/29) — parity matrix с
явным baseline exception и ожидаемым исправлением;
[I03 #42](https://github.com/Tramsey00/MathStart-Python/issues/42) — согласованная
реализация при переносе LessonHost/widgets;
[I05 #44](https://github.com/Tramsey00/MathStart-Python/issues/44) — browser,
keyboard/readability и проверка закрытия findings. Live проверка: OPEN,
assignees соответственно Tramsey00/13baybars/13baybars.
Илья /13baybars выполняет проверки в I05. Возможная отдельная независимая
math/content проверка F04 Владимиром требует отдельного согласования:
его согласия нет, оно не приписывается. Новый численный pixel/font threshold
не установлен; обычный масштаб обязателен, увеличение не заменяет читаемость.

Новые Issues/назначения не создавались. Проверки исправлений **NOT RUN**.
R02/I01/I03/I05 не начинались; их HARD gates и календарь из ТЗ сохраняются.


Согласование: [финальный комментарий Ильи](https://github.com/Tramsey00/MathStart-Python/pull/46#issuecomment-6047568271), exact reviewed HEAD daf4e6038761f8d1bf1c60f0976473d987cce230.
Историческая assignment-PENDING запись сохранена в [prior JSON](follow-up-F01-F04-at-daf4e603.json). Реализация/проверки findings не выполнены этим оформлением.
