# V02 exact-candidate service / CLI / receipt handoff

Candidate PR53: `76d8eac6387a5fde5432a0e8130a881cb6d7ba82`, single parent
`0c03197e23f69a233c0fcf8bdffa336feca20b92`, tree
`dbad1e853dff354c5d3255755afb5cc32e0ad279`. This is a technical handoff for
independent review, not an accepted-input or Task Approval receipt.
Owner: Владимир; R03 orchestration/receipt owner and V02 Task Approver: Руслан.
Илья reviews the applicable consumer boundary; full I02 delivery remains I02.
The source contracts are V02's task card in migration v1.1 and unchanged
`backend/infrastructure/http/README.md`, HTTP implementation and owner tests.

## Service and inputs

Use a fresh exact-candidate checkout and Python3.12+ in a new runtime venv:

```sh
python -m venv /external/runtime-venv
/external/runtime-venv/bin/python -I -m pip install --no-deps -r backend/infrastructure/http/requirements.lock
/external/runtime-venv/bin/python -I -m pip check
/external/runtime-venv/bin/python -B -m backend.infrastructure.http.runtime
```

For the last command set explicit `MATHSTART_DATABASE_URL` (postgresql+psycopg),
`MATHSTART_HTTP_SIGNING_KEY` and `MATHSTART_PUBLIC_ORIGIN`. Keep real values out
of receipts/logs; CI uses disposable synthetic credentials only. Optional inputs:
`MATHSTART_HTTP_SIGNING_FALLBACK_KEYS` (JSON list of legacy verifier keys) and
`MATHSTART_RELEASE_ROOT` (reviewed immutable release directory). Do not inherit
a working `.env`. Runtime binds `127.0.0.1:8202`, disables access logging and
generated API docs. No DDL/bootstrap/activation occurs at service startup.
R03's isolated `-I` service probe runs this exact module with `runpy` and an
explicit candidate path; its argv/stdout/stderr and PID cleanup are retained.

Runtime lock pins and actual installed distribution set are checked independently
against approved snapshot bytes. No Django/DRF package or import is permitted in
the runtime environment. Legacy native comparators run only in separate test
environments. The exact service check observes grades200, unauthenticated staff401
and public `/`503 when renderer/release ports are absent; this last result is
the documented safe default, not working React/SSG browser evidence.

## Explicit test command and disposable environment

V02's README three-module example covers the original41 cases. For current F01/F02
review include the fourth unchanged owner module to execute all86:

```sh
python -m venv /external/v02-test-venv
/external/v02-test-venv/bin/python -I -m pip install --no-deps -r backend/tests/v02/requirements.lock
/external/v02-test-venv/bin/python -I -m pip check
/external/v02-test-venv/bin/python -B -m unittest backend.tests.v02.test_unit backend.tests.v02.test_http backend.tests.v02.test_postgres backend.tests.v02.test_asset_regressions -v
```

Set `MATHSTART_V02_TEST_ADMIN_URL` to a dedicated localhost15441 PostgreSQL16
`postgres` database; fixture credentials must match the owner's synthetic legacy
comparator configuration. Tests create only UUID-named databases, with their
expected disposable prefix/marker. Do not point at application/production data.
R03 uses a freshly allocated `postgres:16-bookworm` Docker service with tmpfs,
checks actual service ID/port/major version, empty before/after and stops/removes
only that service. V01 uses a separate venv from `backend/requirements-test.lock`
and a second service on55441, never the V02 test service. Its exact34/all23 PG
tests include fresh install×2, profiles A/B/C and failure/rollback cases.

The R03 worker observes these unchanged suites and rejects missing/extra/duplicate
cases, loader errors, skips, expected failures, unexpected successes and test
failures. V02 IDs must exactly match remediation `test-matrix.json`; V01 IDs
must exactly match accepted `target-ci-cases-v5.json`. No owner tests/locks or
fixtures are patched. Dedicated runtime-service evidence is separate from the
Django-containing native comparator environment.

## Receipt fields and review criteria

Руслан/R03 retains workflow SHA, actual orchestrator checkout, publication control
revision, approved anchor/decision digest, implementation and actual candidate
checkout SHA/tree/parent, raw live PR HEAD before/after, owner/base/draft state,
lock digests/installed versions, exact case IDs/results/skips, command argv and
stream hashes, Content279/263 comparison, native F02 probes, DB/service cleanup,
original GitHub artifact SHA256, every-member inventory and manifest reconciliation.
See [review packet](review-packet.md) for actual runs and artifact receipts.
Receipt PASS requires an unchanged live HEAD and all applicable checks passing;
human Task Approval is a separate exact-HEAD record by Руслан.

## Consumer handoff to Илья

For review use exact PR53 SHA, R02 frozen schema/operation registry and the new
published/task receipts, preserving original wire fields and stable IDs. Confirm:

- Grades distinguishes PK from number, preserves signed keyset and key rotation;
  client displays safe errors without exposing signing material or private data.
- ContentDelivery manifest/page DTO, SEO/canonical origin, public visibility,
  asset identity versus page-local order, status/method/redirect precedence and
  UTF8/encoded Locations agree with the existing transport contract.
- Catalogue consumes PostgreSQL order and last query values without inventing
  normalization; unknown/unpublished routes do not become SPA200.
- Staff reads/history/selectors consume exact DTOs and revision-bound cursors;
  browser role headers/IDs are never authentication. Default staff access denies.
- `create_app(..., render_page=...)` is I02/V05's reviewed HTML port. Record any
  boundary incompatibility with exact operation, expected/actual and candidate
  SHA. Acknowledgement must describe its scope and tested consumer SHA/browser
  if used; prior Grades PR24 acknowledgement is historical, not new V02 approval.

V03 owns trusted `authenticate`/`csrf_check` ports and sessions/writes. V04 owns
immutable release index/pages/assets, descriptor/APPLIED journal, complete staged
hash inventory and `observe_publication`; activation/content CLI is not provided
by V02. I02/V05 own renderer/gateway integration. Missing providers fail503;
synthetic renderer tests verify only the V02 boundary. Full I02 browser/SSG smoke
and V04 content CLI remain downstream/R03 dependencies, not additional V02 task
acceptance criteria (V02 card has INTEGRATION: -).

No message/approval is sent on behalf of any owner by this document. Илья's
applicable consumer acknowledgement and Руслан's final Independent Task Approval
must be human records; publication exception approval does not grant them.
