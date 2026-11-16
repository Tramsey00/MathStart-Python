# MS-T010 staff update concurrency addendum, 16.11.2026

Руслан явно разрешил expected_revision и 409 при устаревшей форме в текущем чате.
Independent review и human acceptance PENDING. Frozen R02/R02A/delivery bytes
не меняются. Машиночитаемое расширение: staff-t010.json; backend validator и
frontend generator объединяют его с baseline только для указанных operations.

GET /api/v1/staff/users/{id}/ и groups/{id}/ возвращают прежний DTO плюс
expected_revision. Поле является непрозрачным подписанным token, связанным с
actor, authorization scope revision, resource, id и SHA256 снимка показанных полей.
В User снимок также включает внутренний digest password revision. Пароли/хэши/сырой
внутренний digest не возвращаются отдельно. Tokens не отображаются и не логируются.
GET сохраняет view OR change permission. Новый token создаётся из показанного DTO,
а не из повторно прочитанного набора полей, который мог измениться между запросами.

PUT этих двух ресурсов требует прежние поля плюс expected_revision (1..8192 chars).
Пропуск/неверный тип/лишние поля: 400 INVALID_REQUEST. Подделка, другой actor/resource/
id/scope или изменившийся снимок: 409 STATE_CONFLICT, ноль мутаций и audit rows.
Сравнение выполняется после server authorization/session validation под существующим
staff authorization lock и row locks, до любых изменений полей/relations/audit.
Таким образом два сохранения одной версии сериализуются: первое успешное изменение
делает второе stale. Семантика ETag по содержимому, без новой монотонной DB version.
No-op не обещает смену версии. Существующий delete preview protocol не меняется.

Успешный PUT сохраняет прежний DTO response. Форма повторно читает detail для новой
версии. При 409 обычный ввод остаётся, UI предлагает загрузить запись заново;
автоматического повторения PUT или подмены версии нет. Password operations, create,
lists/history, Content view-only и все model permissions/CSRF/no-store сохраняются.
Изменений схемы БД и migrations нет. Новый deployment должен включать frontend и
backend расширение вместе; старые формы без version получают 400, а не overwrite.
