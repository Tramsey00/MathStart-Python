# Pinned historical Django oracle

Post-Django source boundary starts at `1a87b044e8c5a7519b0ab57e22d2a35d57b4a986`.
That exact reviewed commit is also the oracle pin: its Django sources, golden
probes, root lock, settings, templates, manage.py and A/B/C fixtures already
passed the mandatory CI. It retains the baseline behavior and later verified
fixtures; no floating branch, download or generated successful response is used.
Accepted preservation input remains `8d958aeeb17da46839722441425ccbb5889e2ab7`.

## Prepare only for comparisons

From the current Git root, with a target Python that has no Django installed:

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

POSIX uses `bin/python`. The helper clones local Git objects without hardlinks,
enables Windows long paths, checks out detached ORACLE_SHA and rejects a changed
SHA/dirty checkout. Existing paths are not reset or cleaned. An optional
MATHSTART_LEGACY_CHECKOUT must still be a separate pristine checkout under var/.
The interpreter is an explicit separate venv; no combined-environment fallback.
CI explicitly prepares/verifies the pin before installing its historical lock.

`python scripts/legacy_oracle.py --run manage.py check` invokes real historical
Python in that checkout. Supply synthetic DJANGO_* settings and only newly owned
disposable DBs/runtime paths before any write. `--profile legacy` on the current
verifier delegates the unchanged old verifier, not the target interpreter.
The old baseline verification and fresh smoke are available the same way.

Current backend tests invoke historical fixture/timestamp/search/signing/index
and template probes there. Browser parity uses frontend/legacy_comparator.py as
a target-side read-only controller, with the actual historical server in the
oracle checkout. Password/session proofs use separate Django subprocesses.
Legacy return uses the same checkout for migrate/bootstrap/static/native HTTP,
then a fresh target cutover and F-login. No database or successful result is
substituted. Current source guards and owned-resource cleanup remain required.

Only this historical environment installs Django 5.2.16, DRF 3.18.1, asgiref,
sqlparse, WhiteNoise and python-dotenv (plus shared exact historical dependencies).
Target locks use FastAPI/SQLAlchemy/Alembic and do not depend on Django/DRF.
The source-only shell comparison reads the same pinned template Git blob; it
does not prepare an oracle or install Django on ordinary frontend startup.

## Preservation

[Explicit dispositions](../specs/migration/post-django-preservation.json) list
every removed/moved baseline path and changed current platform instruction.
Original size/hash are pinned to the source commit. The verifier checks those
Git blobs, requires removed paths absent, moved shared modules byte-identical,
and current approved adapters at their reviewed hashes. Every other accepted
file is compared to the actual current tree. Unknown changes/deletions fail.
Old approvals/manifests/digests are not rewritten; explicit changed historical
pin consumers (CI and its contract test) have separate current hash checks.
Negative tests exercise current-content corruption and unknown deletions.
