# Зафиксированный исторический Django oracle

Граница post-Django source начинается с `1a87b044e8c5a7519b0ab57e22d2a35d57b4a986`.
Тот же проверенный commit является oracle pin: его Django sources, golden probes,
root lock, settings, templates, manage.py и fixtures A/B/C уже прошли обязательный
CI. Он сохраняет исходное поведение и поздние проверенные fixtures; плавающая
ветка, загрузка чужого ответа или сгенерированный успешный результат не используются.
Принятый preservation input остаётся `8d958aeeb17da46839722441425ccbb5889e2ab7`.

## Подготовка только для сравнений

Из текущего Git root, используя target Python без установленного Django:

```powershell
python scripts/legacy_oracle.py --prepare
$oracle = Join-Path (Get-Location) 'var/legacy-oracle/1a87b044e8c5a7519b0ab57e22d2a35d57b4a986'
py -3.12 -m venv var/oracle-env
$legacy = Join-Path (Get-Location) 'var/oracle-env/Scripts/python.exe'
& $legacy -m pip install --no-deps -r "$oracle/requirements.lock"
# Existing hash-comparison coverage also needs these exact already-used pins:
& $legacy -m pip install --no-deps argon2-cffi==25.1.0 argon2-cffi-bindings==25.1.0 bcrypt==4.3.0 cffi==2.0.0 pycparser==2.23
& $legacy -m pip check
$env:MATHSTART_LEGACY_PYTHON = $legacy
```

На POSIX используется bin/python. Helper клонирует локальные Git objects без
hardlinks, включает Windows long paths, выбирает detached ORACLE_SHA и отвергает
изменённый SHA/dirty checkout. Существующие пути не сбрасываются и не очищаются.
Необязательный MATHSTART_LEGACY_CHECKOUT всё равно должен быть отдельным чистым
checkout внутри var/. Интерпретатор задаётся явно из отдельного venv; fallback
на общее окружение запрещён. CI явно готовит и проверяет pin до установки
исторического lock.

`python scripts/legacy_oracle.py --run manage.py check` запускает настоящий
исторический Python в том checkout. До записи задай synthetic DJANGO_* settings
и только новые собственные disposable БД/runtime paths. --profile legacy текущего
verifier передаёт работу неизменённому старому verifier, а не target interpreter.
Проверка старого baseline и fresh smoke доступны тем же способом.

Текущие backend tests запускают там исторические fixture/timestamp/search/signing/
index и template probes. Browser parity использует frontend/legacy_comparator.py
как target-side read-only controller, а настоящий исторический сервер — в oracle
checkout. Password/session proofs используют отдельные Django subprocesses.
Legacy return использует тот же checkout для migrate/bootstrap/static/native
HTTP, затем новый target cutover и F-login. БД и успешный результат не подменяются.
Текущие source guards и очистка собственных ресурсов остаются обязательными.

Только в историческом окружении устанавливаются Django 5.2.16, DRF 3.18.1,
asgiref, sqlparse, WhiteNoise и python-dotenv, а также общие exact historical
зависимости. Target locks используют FastAPI/SQLAlchemy/Alembic и не зависят
от Django/DRF. Source-only сравнение оболочки читает тот же pinned template Git
blob: обычный frontend startup не готовит oracle и не устанавливает Django.

## Сохранность

[Явная карта](../specs/migration/post-django-preservation.json) перечисляет каждый
удалённый/перемещённый baseline path и изменённую текущую platform instruction.
Исходные размер/hash привязаны к source commit. Verifier проверяет Git blobs,
отсутствие выведенных путей, byte-identical перенесённые shared modules и текущие
принятые adapters по проверенным hashes. Остальные принятые файлы сравниваются
с фактическим текущим деревом. Неизвестные изменения/удаления дают FAIL.
Старые approvals/manifests/digests не переписываются; явно изменённые consumers
исторических pins, включая CI и его contract test, имеют отдельные current hash
проверки. Negative tests проверяют порчу текущего содержимого и неизвестные удаления.
