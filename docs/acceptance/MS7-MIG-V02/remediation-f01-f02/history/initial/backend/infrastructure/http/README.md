# V02 read adapters

This is a shadow-read application, with no domain mutations or DDL at startup.
Historical frozen OpenAPI/DTOs are authoritative. Generated FastAPI docs are disabled.
Factory `create_app(engine, signer, ...)` creates one V01 UoW per operation.
PG transactions explicitly READ ONLY; no autoflush/commit/row locks for reads.

Install in an isolated Python3.12+ venv:

```text
python -m pip install --no-deps -r backend/infrastructure/http/requirements.lock
python -m pip check
```

`python -m backend.infrastructure.http.runtime` requires explicit
MATHSTART_DATABASE_URL (postgresql+psycopg), MATHSTART_HTTP_SIGNING_KEY,
MATHSTART_PUBLIC_ORIGIN; optional MATHSTART_HTTP_SIGNING_FALLBACK_KEYS JSON list,
MATHSTART_RELEASE_ROOT. Do not inherit a working .env or use production data for
tests. Bind localhost8202; access logging disabled. SQLite is only the V01 explicit
compatibility choice, with no fallback from PostgreSQL failures.
No secrets have defaults. Use the retained legacy signing verifier keyring at cutover.
Anonymous grades preserve Django JSONSerializer/TimestampSigner (including compressed
old tokens), salt, route/size/position scope and lack of max_age. Never expire an old
cursor by inventing a new policy. Staff cursors reuse this verified cryptographic
implementation with a separate domain salt and bind DB-derived actor permission revision.

V03 `authenticate(request)` returns AuthenticatedIdentity only after server session
verification; default None denies. V02 rereads flags and direct/group permissions.
Client role headers, cookies or user IDs are never converted into identity here.
`csrf_check` is a trusted V03/gateway proof port; absent proof denies unsafe resolved
public views. Normal startup supplies neither identity nor CSRF proof. Session/hash/
rotation/revocation/Origin/Host acceptance remains V03/V05.

V04 writes immutable <release-root>/<release_id>/index.json, pages/<id>.json and
allowlisted assets plus PostgreSQL descriptor/journal. V02 validates the closed
index/page schemas, cross-references, exact index/body/assets hashes and root bounds.
Reviewed immutable publisher storage is trusted; V02 does not promote arbitrary
filesystem files to reviewed artifacts. Public source_digest provenance is preserved,
not falsely compared to a different checkout edition. Integrity of all page metadata
and original source artifacts must be established by V04's full staged hash inventory.
Missing/inconsistent active snapshot returns503; no latest-DB fallback. Retained
immutable routes require a committed APPLIED journal, never directory enumeration.

I02/V05 `render_page(page, catalogue_context, canonical_url)` supplies reviewed HTML;
default absent returns503. V02 does not create React/SSG output. Catalogue consumes
already PostgreSQL-ordered topics, last query values and Python strip/casefold.
Direct public routes pin one active release; redirects only after actual404.
HEAD is empty, arbitrary public verbs retain CSRF precedence, and Grades is GET only.
Only the existing slashless Grades path has explicit301. Other unsupported API paths
return404, method errors400, Content writes403 after staff authorization.

V04 `observe_publication(uow, page_id)` supplies the immutable active/DB edition facts.
V02 samples DB authority before/after, retries at most3, validates schema, owner/fence/
lease-derived scope and state relations; absent provider503. This is a boundary,
not proof of a working V04 activation or edition pipeline.

API responses use JSON UTF8 and private,no-store. Staff/delivery meta.version is
migration-r02-v1, historical grades http-v1. Internal exceptions are mapped to a
fixed safe503. History preserves IDs/actors/timestamps/actions in action_time/id
order; raw historical messages are not echoed, avoiding password/request leakage.
No permission to write, delete, publish or activate is conferred by a GET.

Explicit tests:

```text
python -m pip install --no-deps -r backend/tests/v02/requirements.lock
python -m unittest backend.tests.v02.test_unit backend.tests.v02.test_http backend.tests.v02.test_postgres -v
```

MATHSTART_V02_TEST_ADMIN_URL must identify dedicated localhost15441/postgres;
fixture DBs use the V01 rehearsal prefix/marker to preserve fresh()'s guard.
Tests create new UUID databases and never attach to pre-existing data. Linux test
containers can run unchanged V01 tests on localhost55441 in the PG network namespace
when Windows excludes that host port. Root verification/workflows are unchanged;
Ruslan owns wiring these explicit target commands into shared CI.
