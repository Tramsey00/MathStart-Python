# MS-T008 — сводка переноса 10-го класса

Текущая поставка: **0/13 активировано**, первая партия **0/5**. Штатный конвертер запущен без правок на временных копиях исходников первых пяти тем. Все пять остановились до записи документа. Штатная Content-валидация ожидает готовых документов. Автоматический QA — `NOT_RUN_BY_USER_REQUEST`.

Постоянные адреса зафиксированы в порядке inventory. В текущем registry нет назначений 10-го класса, поэтому все 13 адресов свободны. Legacy-пути уникальны и следуют текущему resolver `/<slug>/`. После активации каждого документа штатный registry должен сформировать redirect с соответствующего legacy-пути на canonical. До активации сохраняется текущая legacy-поставка.

| Тема | Canonical | Legacy | Статус | Решения в исходнике |
| --- | --- | --- | --- | ---: |
| Натуральные числа. Повторение | `/materials/10-algebra-1` | `/10-klass-naturalnye-chisla-povtorenie/` | NOT_MIGRATED / BLOCKED | 8 |
| Натуральные числа. Повторение 2.0 | `/materials/10-algebra-2` | `/10-klass-naturalnye-chisla-povtorenie-2-0/` | NOT_MIGRATED / BLOCKED | 12 |
| Рациональные числа. Повторение | `/materials/10-algebra-3` | `/10-klass-racionalnye-chisla-povtorenie/` | NOT_MIGRATED / BLOCKED | 8 |
| Рациональные числа. Повторение 2.0 | `/materials/10-algebra-4` | `/10-klass-racionalnye-chisla-povtorenie-2-0/` | NOT_MIGRATED / BLOCKED | 12 |
| Иррациональные числа. Повторение | `/materials/10-algebra-5` | `/10-klass-irracionalnye-chisla-povtorenie/` | NOT_MIGRATED / BLOCKED | 8 |
| Понятие корня n-й степени из действительного числа | `/materials/10-algebra-6` | `/10-klass-ponyatie-kornya-n-stepeni/` | NOT_MIGRATED | 8 |
| Функция корня n-й степени | `/materials/10-algebra-7` | `/10-klass-funkciya-kornya-n-stepeni/` | NOT_MIGRATED | 8 |
| Свойства корня n-й степени. Преобразование иррациональных выражений | `/materials/10-algebra-8` | `/10-klass-svoystva-kornya-n-stepeni/` | NOT_MIGRATED | 8 |
| Способы упрощения выражений, содержащих радикалы | `/materials/10-algebra-9` | `/10-klass-uproshchenie-vyrazheniy-s-radikalami/` | NOT_MIGRATED | 8 |
| Понятие степени с рациональным показателем, свойства степеней | `/materials/10-algebra-10` | `/10-klass-stepen-s-racionalnym-pokazatelem/` | NOT_MIGRATED | 8 |
| Свойства степенных функций и их графики | `/materials/10-algebra-11` | `/10-klass-stepennye-funkcii-i-grafiki/` | NOT_MIGRATED | 8 |
| Свойства степенных функций и их графики 2.0 | `/materials/10-algebra-12` | `/10-klass-stepennye-funkcii-i-grafiki-2-0/` | NOT_MIGRATED | 12 |
| Числовая окружность на координатной плоскости 2.0 | `/materials/10-algebra-13` | `/10-klass-chislovaya-okruzhnost-2-0/` | NOT_MIGRATED | 12 |

## Блокировки раздела «Действительные числа»

Ниже первый отказ конвертера по каждой теме. Последующие ограничения пока неизвестны.

- [Исходник «Натуральные числа. Повторение»](../../curriculum/10-klass/algebra/01-deistvitelnye-chisla/01-10-klass-naturalnye-chisla-povtorenie/body.html#L9) — `tabindex="0"` у `div.ms-table-wrap`, строка 9.
- [Исходник «Натуральные числа. Повторение 2.0»](../../curriculum/10-klass/algebra/01-deistvitelnye-chisla/01-10-klass-naturalnye-chisla-povtorenie-2-0/body.html#L9) — `aside.v2-rule.ms-rule-box`, строка 9.
- [Исходник «Рациональные числа. Повторение»](../../curriculum/10-klass/algebra/01-deistvitelnye-chisla/02-10-klass-racionalnye-chisla-povtorenie/body.html#L9) — `tabindex="0"` у `div.ms-table-wrap`, строка 9.
- [Исходник «Рациональные числа. Повторение 2.0»](../../curriculum/10-klass/algebra/01-deistvitelnye-chisla/02-10-klass-racionalnye-chisla-povtorenie-2-0/body.html#L9) — `aside.v2-rule.ms-rule-box`, строка 9.
- [Исходник «Иррациональные числа. Повторение»](../../curriculum/10-klass/algebra/01-deistvitelnye-chisla/03-10-klass-irracionalnye-chisla-povtorenie/body.html#L9) — `figure.ms-figure`, строка 9.

Для `tabindex="0"` сохранить фокусируемую область прокрутки таблицы, `role="region"` и доступное имя. Для `aside` сохранить смысловую группу и семантику примечания. Для `figure` сохранить SVG, подпись и их связь. Согласовать узкую поддержку с Владимиром перед повтором.

## Границы переноса первой партии

Сохранить терминальную секцию `#practice` со всеми 48 заданиями и решениями. Исключить только согласованные prerequisite и legacy-навигацию, а также итоговые секции после самопроверки. У исходных версий натуральных, рациональных и иррациональных чисел итоговая секция имеет ID `lesson-section-9`. У версий 2.0 итоговый блок «Что важно запомнить» без ID. После разблокировки отдельно сверить вложенные дроби, дробные степени и корни, таблицы, SVG и все оставляемые якоря.
