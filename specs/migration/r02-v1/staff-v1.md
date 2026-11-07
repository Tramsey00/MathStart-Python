# Дополнение о доставке/авторизации Staff v1.0.1

PROPOSED. Ровно девять регистраций/actions/fields/filter/search/permissions из
[admin-inventory R01](https://github.com/Tramsey00/MathStart-Python/blob/3a290a46d991e22269a17dde41e39f0637576071/docs/acceptance/MS7-MIG-R01/admin-inventory.json)
скопированы по ссылке в route map; ниже включены все операции.
Семь моделей Content остаются доступными только для просмотра даже superusers.
User/Group сохраняют полноценное существующее администрирование; для Permission нет
отдельного CRUD. StudentProfile, IdentityReceipt и LoginWindow не регистрируются и
не публикуются заново как staff CRUD.

Каждый staff request сначала аутентифицирует активного User: anonymous/inactive — 401,
nonstaff — 403; затем проверяются is_staff и permission соответствующей model
(superuser проходит model permission). Для View, как в Django ModelAdmin, достаточно view ИЛИ change;
для Content под управлением source запрещены add/change/delete вне зависимости от назначенных permissions.
Для detail/history применяется тот же gate просмотра. Permissions действий проверяются server-side
для каждого объекта, а не только скрытием controls. Для mutations обязательны CSRF и same-origin;
безопасные envelopes 400/403/404/409/503, private no-store. Неожиданные поля/relations DTO отклоняются.

| Ресурсы | Требуемые операции / DTO / permission |
| --- | --- |
| grades, subjects, sections, pages, publications, media_assets, redirects | list, detail, search, baseline list filters/order, чтение history; content.view_<model> ИЛИ content.change_<model>; поля строго как в инвентаризации, включая ContentPage.source_location. Все пути mutation запрещены, 403. |
| users | list/search/filter/detail/history, create, редактирование username/email/first_name/last_name/active/staff/superuser/last_login/date_joined, прямые permissions и groups, создание с usable/unusable password, смена password, защищённое удаление одного/выбранных записей. auth.view/change/add/delete_user в соответствии с действием. |
| groups | list/search/detail/history, create/edit name и назначения permissions, защищённое удаление одного/выбранных записей. auth.view/change/add/delete_group по действию. |
| permission selectors | только чтение при соответствующем объединённом gate создания User, auth.change_user или auth.add/change_group для формы; только id/name/codename/contenttype; отдельный зарегистрированный CRUD Permission admin отсутствует. |

Baseline UserAdmin разрешает staff actor с auth.change_user редактировать role flags,
groups/direct permissions и password (включая поля, дающие привилегии). Нельзя молча подменить
это политикой только для superuser или защитой от self-escalation и назвать baseline parity.
Для ужесточения требуется явное решение security scope и обновлённые положительные/отрицательные
ожидания до принятия V03. Текущий mapping сохраняет baseline permissions и делает этот риск
доступным для ревью. Создание staff user требует auth.add_user И auth.change_user, как в
Django UserAdmin._add_view и родительском add gate. Для создания Group требуется auth.add_group.
Edit/password User требует auth.change_user; удаление — auth.delete_user. Для смены permission
assignments Group требуется auth.change_group. Related object selectors и choices соответствуют
baseline forms.

Существующая форма UserAdmin password позволяет задать usable password и отключить password
authentication. При `usable_password=true` password1/2 должны совпадать и проходят baseline
password validators; при `false` требуется явный `confirm_disable=true` (подтверждение Django unset-password),
записывается unusable marker, поля password отбрасываются. Отключить password можно, только если у
существующего пользователя был usable password, как в baseline form; иначе безопасный state conflict.
Случайно снятое/пропущенное подтверждение disable принимать нельзя.
Также обязательна собственная смена password через admin site: активный staff может отправить
old_password/new_password1/new_password2 без auth.change_user. Проверить старый password, совпадение
новых и validators; сохранить текущую session через update_session_auth_hash и rotation,
аннулировав остальные sessions. Смена password другого пользователя не ротирует session actor.
В ответе не повторяются поля password, encoded password или session tokens. Это контракты adapters,
а не новые runtime endpoints.

StaffUserDTO содержит только безопасные id, username, names, email, role/active flags,
date_joined/last_login, group IDs/direct permission IDs, has_usable_password;
никогда encoded_password/session/receipt/key_digest. Password request имеет writeOnly и не повторяется
в ответе. Content detail состоит из закрытых типизированных полей каждой модели, а не произвольной
сериализации ORM. Предлагаемый private StaffRecordDTO переносит model+fields по model-specific schemas;
динамического словаря additionalProperties нет. Staff history DTO содержит timestamp, actor ID, action
и очищенную сводку изменений; исторические admin log rows/actor links/object IDs сохраняются;
plaintext password и raw request не записываются.

Любое одиночное/bulk удаление требует явного confirmation token, привязанного к показанным IDs
и текущей revision; permissions и PROTECT проверяются заранее в той же transaction.
Зависимости User/Profile/Receipt/Grade с PROTECT дают безопасный 409 STATE_CONFLICT
и ноль частичных удалений. Очистка Group/user associations совпадает с Django collector;
защищённая история ученика сохраняется. Search/filter/pagination должны сохранять baseline результаты
и поведение permissions, а не просто показывать жёстко заданную таблицу fixture. Сбой CSRF/session/
password revocation/audit не может вернуть успех. Текущий Content по-прежнему меняется через publication CLI.

Предлагается отдельный OAS для нового namespace `/api/v1/staff/...`, только как adapter.
Замороженный OAS с каноническими 37 operations не меняется. Нативные пути staff frontend
`/admin/` и model list/detail/forms сохраняют baseline navigation через route adapters,
новый CMS не добавляется. Redirect HTML login может зависеть от presentation;
JSON использует 401/403, никогда HTML login 302. Полные URL patterns admin и метаданные operations
указаны в implemented-routes-v1.json, включая password change/history/delete-selected.
CLI не заменяет эти принятые UI-возможности.

Контракт запросов списков: q точно сопоставляется с инвентаризированными search_fields;
именованный `filter__<inventoried list_filter>` сопоставляется с тем же model filter,
строгая проверка bool/ID/page_type выполняется без coercion. Неизвестные/repeated singleton params — 400.
Сохраняется default ordering из зарегистрированного ModelAdmin или model Meta;
исходный индекс столбца Django `o` через inventoried list_display сопоставляется с проверенным
списком упорядоченных полей frontend adapter. Произвольная SQL ordering string запрещена.
Пагинация Staff: default 20/max 100; cursor привязан к аутентифицированному staff, resource/search/filter/order
и page_size; сохраняются уникальный baseline ordering и добавление descending PK только когда
Django требует его для детерминированной сортировки. Keyset pagination избегает пропусков offset,
но не обещает неизменяемый snapshot при редактировании записей; согласованность mutations проверяется
позже. Это не связано с cursor анонимного grades.
GET preview удаления одного/нескольких перечисленных IDs возвращает private confirmation token,
привязанный к actor, IDs/current record digest/expiry; POST повторно проверяет его и permissions/PROTECT
под locks. Preview не меняет домен; заблокированное PROTECT удаление остаётся доступно для осмотра
без раскрытия записей неавторизованному actor.

## Поправки ревью B01/B03/B04/B05/B06

Кнопка/форма создания User и POST используют совместный gate add_user И change_user,
даже если общая кнопка add в Django видима. Пользователь с одним лишь add, одним лишь change,
без обоих, неактивный и nonstaff не могут создавать пользователя. Superuser действует как в baseline.

Wire значения Boolean query, включая filter__is_permanent и filter__is_active, должны быть ровно
singleton URI strings `true`/`false`, декодированными в JSON true/false. Значения 0/1, uppercase,
пустые и повторные возвращают 400. Нативный Django admin `is_permanent__exact=0/1` переводится явно;
temporary redirects остаются доступными для выбора. JSON Schema/OAS использует boolean,
никогда положительное integer/coercion.

Каждая из девяти list operations задаёт singleton sort. Грамматика:
`sort=default` ИЛИ `[-]field(,[-]field)*`. Минус означает descending, отсутствие — ascending.
Запрещены плюс, пробелы, пустые выражения, повторное поле (даже с противоположным знаком),
неизвестные колонки, внедрение relation или raw SQL. Пропущенный/default выбирает native ordering.
Допустимые поля ресурсов и default/effective orders заданы в
[staff-list-policy](staff-list-policy-v1.json) и OAS x-sort-contract. У Group нет native sort field
для колонки `__str__`: допустим только omit/default, с сортировкой baseline по name.
Другие поля соответствуют нативным колонкам list_display, включая FK sorting через Meta.ordering
связанной model, а не строку отображения. Explicit terms идут перед queryset ordering ModelAdmin;
сохраняется точное правило уникального ключа и descending PK, если он нужен. Сохраняются PostgreSQL
collation и ASC NULLS LAST / DESC NULLS FIRST; SQLite воспроизводит их для совместимости.
Нативные индексы `o` учитывают checkbox действия, только если actor имеет к нему доступ;
они преобразуются в названные поля/направления и никогда не становятся SQL fragments.

Cursor связывает actor ID, revision authorization-scope, resource, точное q, нормализованные
filters, раскрытые effective sort keys/directions и page_size. Он подписывает упорядоченные последние
значения с явными NULL markers. `authorization_scope_revision` — digest текущих active/staff/superuser
flags и отсортированных effective permission codes, пересчитываемый при авторизации; новая сохранённая
permission column не нужна. Несовпавшие/подделанные cursors — 400; изменение любого поля/direction/filter/
page-size начинает новый список. Multi-sort и ties должны совпадать с Django ordering, включая nullable
relations и смешанные направления.

`GET /api/v1/staff/users/{id}/group_choices/` возвращает только group id/name для существующей
формы редактирования User при active staff + auth.change_user. Проверяется наличие целевого User
(иначе 404); возвращаются все groups по name, как в baseline form queryset, private/no-store;
pagination не может молча исключить варианты. User с правом только view получает 403.
Разрешение Group view/change не требуется; доступ к group administration/list/detail/history/write
не предоставляется. В baseline форме создания нельзя назначать groups (add_fieldsets их не содержит);
варианты groups там не показываются. Существующие groups редактируемого User видны и доступны
для изменения с change_user. Нового создателя group или привилегированного popup нет.

GET состояния публикации доступен только для чтения с тем же ContentPage view/change gate;
см. content-v1.md. Он не даёт полномочий publisher action или администрирования Group.
