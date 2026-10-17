# Password compatibility dependencies and data

The common-passwords.txt.gz data is copied byte-for-byte from Django5.2.16's
django/contrib/auth/common-passwords.txt.gz to preserve the accepted validation
list. Django is copyright Django Software Foundation and individual contributors,
licensed under the BSD3-clause license. The list is the lowercased/deduplicated
Royce Williams20,000-common-password dataset, as attributed by Django.
The exact upstream Django license is retained in DJANGO-LICENSE.txt.
No Django runtime code is imported by the target password service.

argon2-cffi25.1.0 and argon2-cffi-bindings25.1.0 are MIT licensed; bcrypt4.3.0 is
Apache2.0 licensed. They are pinned only to verify existing accepted hash formats,
with cffi2.0.0(MIT) and pycparser2.23(BSD3-clause) as required dependencies.
New passwords retain the accepted PBKDF2-SHA256 format and1,000,000 iterations.
