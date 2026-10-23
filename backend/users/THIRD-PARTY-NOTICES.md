# Зависимости и данные для совместимости паролей

Данные common-passwords.txt.gz скопированы побайтно из Django5.2.16's
django/contrib/auth/common-passwords.txt.gz, чтобы сохранить принятый список проверки.
Авторские права на Django принадлежат Django Software Foundation и отдельным участникам;
лицензия — BSD3-clause. Список представляет собой приведённый к нижнему регистру список без дубликатов
из набора Royce Williams20,000-common-password, как указано Django.
Точный текст исходной лицензии Django сохранён в DJANGO-LICENSE.txt.
Сервис проверки паролей target не импортирует runtime-код Django.

argon2-cffi25.1.0 и argon2-cffi-bindings25.1.0 распространяются по MIT; bcrypt4.3.0 —
по Apache2.0. Они закреплены только для проверки уже существующих принятых форматов hash;
обязательные зависимости: cffi2.0.0(MIT) и pycparser2.23(BSD3-clause).
Для новых паролей сохраняется принятый формат PBKDF2-SHA256 и1,000,000 итераций.
