# Дополнение MS7-V02: mapping runtime каталога Grade (Issue 23)

- **Статус:** Реализовано; ожидается ревью и приёмка
- **Владелец:** Владимир
- **Reviewer / Task Approver:** Руслан
- **Потребитель:** Илья, MS7-I03
- **Дата:** 2026-10-04
- **Issue:** https://github.com/Tramsey00/MathStart-Python/issues/23
- **План:** [план API grades](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/exec-plans/active/MS7-V02-grades-api.md)

## Полномочия и область действия

Документ описывает adapter legacy model для уже принятого R02A
`GET /api/v1/grades/`; он не заменяет OpenAPI, схемы DTO или HTTP policy.
Эти замороженные файлы и их manifest digests не меняются. Каталог и DTO adapter
принадлежат Content. Общие HTTP helpers находятся в infrastructure;
у Content нет business-зависимости от Users. Существующие V02 imports и байты
identity responses сохраняются через compatibility exports.

## Persistence и mapping DTO

| Поле wire-протокола | Источник в существующей model | Правило |
| --- | --- | --- |
| `id` | `Grade.pk` | Настоящий database ID; не подменять номером класса. |
| `number` | `Grade.slug` | Канонический `<number>-klass`, целое 1..12. Каталог repository использует это соглашение. |
| `title` | `Grade.title` | Существующий непустой title, сериализованный как UTF-8. |

Display `order` и выделение PK не определяют смысловой номер учебного года. Slug,
description, display order и timestamp не являются полями публичного DTO. Строка
с неподдерживаемым slug или пустым title безопасно завершает запрос ответом 503 по контракту;
service не пропускает её и не выдумывает номер. Администраторы должны сохранять канонические
catalogue slugs. Эта задача не меняет данные каталога и не выполняет bootstrap.

Пользователь явно согласился 2026-10-04 добавить `Grade.created_at` после обнаружения,
что порядок R02A нельзя точно реализовать на старой schema. Additive migration
`0002_grade_created_at` сохраняет все существующие IDs, поля и ссылки. Старые строки
получают общий UTC tracking epoch `2026-10-04T00:00:00Z`: исходное время создания не записывалось.
Для их относительного порядка используется существующая развязка по ID. Новые строки используют
Django `auto_now_add`; обычное редактирование и повторный bootstrap сохраняют timestamp.
Не интерпретировать legacy epoch как восстановленное историческое время создания.
Перед merge проверить migration; для заполненного timestamp column предпочтительны исправления вперёд,
а не откат.

## Pagination и ошибки

Keyset pagination по возрастанию `(created_at,id)`, default `page_size=20`, максимум 100;
один ограниченный запрос получает не более `page_size+1` строк. Offset pagination нет.
Подписанный непрозрачный cursor связывает public route, protocol salt, позицию и page size.
У анонимного каталога нет private owner или filters. При переходе к следующей странице передавать
тот же `page_size`. Изменение title/order не перемещает строки; удаление уже показанной строки
не сдвигает следующую страницу. Новые более поздние строки могут появиться на последующих страницах;
это не snapshot каталога.

Поддерживаются только `cursor` и `page_size`. Повторные/неизвестные parameters, неверный размер,
некорректный/слишком большой/подделанный/cross-route cursor и смена page-size возвращают
безопасный R02A `400 INVALID_REQUEST`. Ошибка базы или строка без mapping возвращает
`503 SERVICE_UNAVAILABLE` с `retryable=true`, без сведений о строке/SQL. Анонимные и вошедшие
пользователи используют общий public catalogue cursor scope.

Endpoint поддерживает только GET. Он не создаёт authentication session, profile,
onboarding state, receipt, attempt или evidence. `GradeListResponse` содержит `data`,
`meta.request_id`, `meta.version=http-v1` и обязательную pagination с `next_cursor`,
`page_size`, `has_more`.

## Передача I03

Загрузить `/api/v1/grades/`, показывать `title`, сохранять каждый полученный `id` как value
варианта и передавать его как `selected_grade_id` существующему profile/onboarding API.
Продолжать загрузку страниц через `meta.pagination.next_cursor`, пока `has_more=false`.

Синтетический пример (IDs зависят от базы данных):

```json
{
  "data": [{"id": 70, "number": 5, "title": "5 класс"}],
  "meta": {
    "request_id": "00000000-0000-4000-8000-000000000001",
    "version": "http-v1",
    "pagination": {"next_cursor": null, "page_size": 20, "has_more": false}
  }
}
```

Интеграционный тест намеренно использует `id=70` для 5-го класса, получает его через API
и успешно отправляет с START_ZERO, DIAGNOSTIC и SELF_REPORT через V02, включая настоящие CSRF checks.
Числовая инициализация знания не меняется.

## Проверка и приёмка

Тесты охватывают DTOs, анонимное/пустое чтение, ограниченную pagination, одинаковые timestamps,
редактирование/удаление/новые строки, подпись query, безопасные ошибки, отсутствие writes и
интеграцию V02. Проверка upgrade сохраняет значения и ссылки Grade/Subject/User/StudentProfile.
Bootstrap regression проверяет стабильность timestamp. Фактические команды/результаты и версии
интерпретатора/базы указываются в task trace. До закрытия Issue необходимы ревью Руслана, merge
и передача результата I03.
