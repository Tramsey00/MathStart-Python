# I02/I03 synthetic read runtime

This scoped adapter composes accepted V02 with `frontend.rendering.PublicRenderer`
and read-only PostgreSQL opaque session validation. It has no login, account or
staff mutations and does not implement full V03/V04 publication/recovery.

Install `backend/infrastructure/http/requirements.lock` in the target environment.
For tests also install `backend/tests/v04/requirements.lock`. Neither requires
Django. The legacy golden oracle remains a separate environment.

Run from the combined repository root. Set these environment variables without
printing their values:

- `MATHSTART_DATABASE_URL`: PostgreSQL/psycopg connection to a newly created empty
  synthetic DB named `test_ms7_mig_v01_<unique suffix>`.
- `MATHSTART_DISPOSABLE=1`.
- `MATHSTART_HTTP_SIGNING_KEY`: disposable private signing key, retained for the
  synthetic session lifetime; optional JSON-array `MATHSTART_HTTP_SIGNING_FALLBACK_KEYS`.
- `MATHSTART_PUBLIC_ORIGIN`: exact HTTP origin, e.g. local port8121.

```text
python -m backend.content.synthetic_setup prepare --disposable --runtime-root var/i02-runtime --release-id i02-public-<unique suffix> --source-sha <reviewed commit>
```

The command checks the DB name and emptiness before reserving the accepted V01
marker, applies unchanged Alembic fresh migrations, bootstraps twice and compares
the preserved source edition, creates only synthetic staff/group/media/session
fixtures, then builds immutable public inputs under `var/i02-runtime/releases/`.
Its `prepare-result.json` contains release/input/receipt digests and paths.
`private-staff-cookie.json` contains a synthetic opaque cookie: keep it ignored,
do not print or attach its contents. This is a test fixture, not a login endpoint.

Build React output from those exact fresh inputs using `frontend.build_public`.
Use the exact `MATHSTART_PUBLIC_ORIGIN`; capture the trusted output manifest digest.
Then:

```text
python -m backend.content.synthetic_setup activate-initial --disposable --runtime-root var/i02-runtime --release-id <release> --receipt-digest <trusted input receipt digest> --artifact-root <new frontend output> --artifact-digest <trusted output manifest digest>
```

This one-time synthetic setup verifies the complete input/output inventory and
DB edition before installing the initial descriptor in one SQL transaction.
It refuses existing publication authority. It is not publish/retry/takeover,
does not replace an active release and is not production cutover evidence.

For the read server set:

- `MATHSTART_RELEASE_ROOT` to `var/i02-runtime/releases`.
- `MATHSTART_PUBLIC_ARTIFACT_ROOT` to the frontend output root, or a parent with
  per-release subdirectories.
- `MATHSTART_PUBLIC_ARTIFACT_DIGESTS` to the trusted JSON mapping from release ID
  to output manifest SHA256.

```text
python -m uvicorn backend.content.public_runtime:application --factory --host 127.0.0.1 --port 8121 --no-access-log
```

Public documents/API/assets pin the authoritative DB release. Explicit native
staff read URLs serve only the verified anonymous shell with private/no-store;
their API reads authenticate the opaque session, expiry/revocation/auth-hash and
current DB permissions. Private data never enters the public artifact. Unknown
staff URLs remain404. Generated frontend assets must be in the trusted output
manifest. Corrupt/missing files fail closed. There is no constant Node server.

The staff publication-state observer supports the coherent initial synthetic
edition only. Any pending publication or DB drift fails closed; it does not
claim to observe a full publication/recovery implementation.

For browser tests set `MATHSTART_STAFF_COOKIE_FILE` to the ignored private cookie
file. For the focused PG session tests use the same DB/signing/cookie environment:

```text
python -m unittest backend.tests.v04.test_read_runtime -v
```

Stop the owned Uvicorn process after checks. Retain or drop only the newly named
reserved synthetic DB and its own var subtree according to the run ledger.
Root portable verification/CI owns combined lifecycle and final exact-SHA runs.
