# Public block verifier candidate

Status: WIP / REVIEW_PENDING. Scope: I02/I03 and their initial synthetic serving
dependency; this does not complete R03, full V04, or the overall migration.

The portable driver installs no dependencies and requires a newly created empty
reserved PostgreSQL database, an installed no-Django target interpreter, a
separate locked legacy interpreter, npm dependencies and browser binaries.
It prepares fresh immutable inputs, builds all public pages, validates initial
synthetic activation, runs renderer/read tests, then owns both target and legacy
HTTP process trees for the nine-project browser check. Cookies and signing keys
are private fixtures and are not uploaded by the workflow.

Run from the combined checkout after installing the documented locks:

```text
python scripts/verify_public_block.py --runtime-root var/public-check-UNIQUE --legacy-python PATH_TO_SEPARATE_LEGACY_PYTHON --port 8111 --legacy-port 8112
```

Set MATHSTART_DATABASE_URL and MATHSTART_DISPOSABLE=1 without logging credentials.
The driver creates a fresh in-memory synthetic signing key and ignored staff
cookie fixture. A successful driver run does not complete manual visual review
or independent review. Dirty runs are explicitly marked and cannot be relabelled
as exact clean-candidate evidence.

Eight real lifecycle tests passed in Windows owner context, 22.872 seconds,
including both origins, browser failure/timeout/descendant cleanup, pre-existing
listener refusal and startup failure. The full combined driver and CI are pending
the independently reviewed backend serving fix and frontend browser matrix.
Do not merge this WIP into integration merely to preserve it.
