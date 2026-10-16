# MS7-MIG backend execution trace

Date:2026-10-16. Agent: GPT-6.1 Sol, high, backend role.
Input:`24d06112bcd6abcd1abad9b052de14a0a7b49e8e`;
checkout:`C:/Projects/MathStart-Python/migration-execution/backend`;
branch:`ms7-mig-backend-execution`. Human review pending.

## Observable first increment

Read migration package/backend role, repository architecture/verification,
ADR0006 and preserved V01/V02 source/contracts/evidence. Four untracked source
renderer/bootstrap files existed from the interrupted same-role checkpoint;
they were inspected and retained. Added immutable writer and explicit target CLI.

Task-labeled Docker container `ms7exec_backend_pg` runs PostgreSQL16.15,
image postgres:16, loopback55432. Python3.12.14, SQLAlchemy2.0.46, psycopg3.3.6.
No-Django target environment:var/venv. Separate legacy oracle:var/legacy-venv,
Django5.2.16/asgiref3.12.1/sqlparse0.6.0/tzdata2026.3.

Actual real PG fresh migration succeeded on the uniquely reserved disposable
`test_ms7_mig_v01_ms7exec_backend_build_20261016`; bootstrap ran twice successfully,
279 pages each time. Source inventory:263 topics and16 structural/static pages.
First export failed because runtime media was absent: corrected asset lookup to
the reviewed site_content/media seed manifest with required sha256 verification.
No source/runtime bytes were modified to hide the failure.

`python -m backend.cli build-inputs --source-root . --output-root var/build-inputs
--release-id ms7exec-public-20261016 --source-sha
24d06112bcd6abcd1abad9b052de14a0a7b49e8e` succeeded with279 pages,263 topics,
123 unique assets. Index digest:
`7c65edcc6423edd6f5b6e4a7cd18f09fecd1ccaceb4b36112bdc84e7172779d3`.
Every DTO/page/asset passed accepted ReleaseStore validation before directory
finalization. Source SHA, full file hashes/sizes and source-file inventory are in
the artifact receipt. Frontend received root/release/digest immediately.

## Tests and current limits

`python -m unittest backend.tests.v04.test_build -v` passed7 tests in103.322s with
an explicit PG test URL and separate legacy Python path. An additional trusted
receipt regression was then added and will be run against the committed slice.
Required negative cases cover malformed source/path escape,
immutable overwrite, runtime edit rejection, corruption/missing assets/pages.
The oracle compares every rendered topic against unchanged Django templates.

Preserved V02 HTTP/asset SQLite cases passed47 assertions; the attempted combined
V02 command also produced1 import error because its signer oracle test imports
Django, and23 PG cases skipped without the V02-specific environment. This is an
environment/invocation failure, not full V02 verification. Target venv remains
free of Django. Both target and legacy environments passed pip check.

Source seed bootstrap currently fails closed on runtime content edits, while
full publication reconciliation/force behavior remains a later V04 increment.
H-BUILD-INPUTS is a candidate interface; it does not activate a release or claim
V04 completion. Identity/staff writes, full CLI inventory, recovery, operational
restore, R04 and V06 remain unverified. No historical approvals were rewritten.

## Independent H-BUILD review corrections

Reviewer reproduced HBUILD-01: a coherent alternate grade/subject/section triple
was exported even though reviewed source identity was unchanged. Writer now
compares all three related slugs before export, and a real PG regression changes
the tenth-grade topic to the valid first-grade triple and requires rejection.

Reviewer reproduced HBUILD-02: READ COMMITTED read-only transactions could mix
delivery metadata and a later concurrently committed catalogue edition. Every
PG writer entry now requires REPEATABLE READ or SERIALIZABLE; CLI starts
REPEATABLE READ READ ONLY. Regression uses a real second connection to commit
a Grade label change while the first snapshot is held and requires the original
coherent catalogue. Both new regressions passed in40.991s. A source checkout
guard additionally proves the supplied source commit exists, source paths have
no tracked diff against it and no untracked source additions. Full post-fix
verification is pending the next exact-SHA run.

## Scope narrowed to I02/I03 by the user

HBUILD-01's additional same-slug cross-grade case was corrected in
`cd62406c6e0ff029c6e4445e8f015243731fd194` by validating subject->grade and
section->subject IDs. Reviewer independently verified3 cases and closed the
finding; HBUILD-02's repeatable snapshot correction remains verified in scope.

V03 work was preserved separately as incomplete checkpoint
`fdac6e68b4c7c55ed0effe6e2107bff45dd3416b` onms7-mig-backend-execution. It is
excluded from the necessary-runtime branchms7-mig-i02-backend-runtime, based on
cd62406. It does not establish V03 acceptance. No V05/V06/fullV04 expansion is
performed in the narrowed run.

Necessary read-runtime commit:`dd95ab108ad9a9e8e7bd20a26678632b5e2bf8f5`,
tree`f68490230b85654eaa5f17ebe0aa65864d9ebdcc`. It adds a reservation-guarded
empty synthetic PG setup, unchanged Alembic fresh, bootstrap twice, immutable
input build and synthetic staff/group/media/opaque-session fixture. It provides
the V02+PublicRenderer factory and readonly session verification; no identity
write module or new hash dependency is included. Target test lock is
backend/tests/v04/requirements.lock, free of Django.

After interruption the owned PG container was observed exited. A focused
cd62406 author test failed before any cases with a connection error. Restarting
the verified task-labeled container lost its tmpfs synthetic DBs; reviewer was
informed and recreated their own DB. Existing artifacts/failures were retained.
A fresh distinct DBtest_ms7_mig_v01_ms7exec_backend_i02_20261016 was then created
and portable prepare succeeded. New releasems7exec-i02-public-20261016 has279
pages,263topics,123assets; input digest
`3d9a389bba5adcb6c097526fa440ad72b1efdd167536a661155b08e4e6dd435f`,
receipt`db059ce5e13fe0bd12904254348122ee15c6f7acd199c0e04f05969ec7db6eab`.
Frontend received this fresh input for a new build; older artifacts are
preliminary evidence only.

Readonly session suite passed4/4 on real PG16.15 (0.421s initial run), covering
zero SQL writes, expiry/revocation/auth-hash mismatch/inactive user, missing/bad/
oversize tokens and signing verifier key ring. Exactdd95ab1 rerun and repeat
prepare refusal (expected exit1 on nonempty DB) are retained in
docs/acceptance/MS7-MIG-V04/i02-read-runtime-20261016-01. Initial activation and
combined HTTP/browser verification await the new frontend artifact; no complete
I02/I03 or publication acceptance is claimed by this record.

## Sol medium continuation: necessary public read corrections

Preserved the interrupted tracked changes and the untracked historical raw
receipts without overwriting earlier runs. Source candidate
`5b7f3be20598e1117408fd23df5ecb34b3550280` (tree
`a751cc3681c998b378ef5e44f0d68b307de1d796`) wires the independently reviewed
READRT-01 boundary to a read-only CSRF verifier. It accepts matching raw or
Django-masked cookie/header tokens, checks exact Origin and HTTPS Referer, and
preserves B07 unsafe public reads and error precedence. It also commits the
previously prepared initial synthetic activation preflight: PostgreSQL16,
trusted input receipt/origin, exact URL/redirect/private coverage and all279
authored page bodies. This remains an initial synthetic fixture operation.

The old serving process and signing configuration were unavailable after the
role change. With explicit coordinator authorization, only the exclusively
reserved synthetic staff session was rekeyed; the existing private cookie was
retained. Random signing configuration is stored in ignored
`var/i02-runtime/private-env.json`, never in this trace or Git. No production
or historical evidence data was changed. The frontend retained its earlier
connection-refused browser failures as environment failures.

Exact5b7f3be read suite passed9 tests in130.421s while browser work was also
running; raw bytes, hashes and metadata are under
`docs/acceptance/MS7-MIG-V04/i02-read-runtime-20261016-02/`.
An earlier invocation failed3 HTTP test imports because the consumer-owned
frontend Python package was absent from PYTHONPATH. The corrected invocation
adds the frontend checkout explicitly; target Python remains separate from
the legacy oracle. Author environment pip check passed.

Browser timeouts exposed synchronous release validation in auxiliary async
middleware. Coordinator authorized the necessary serving correction, without
changing the accepted ReleaseStore or caching DB publication authority.
Candidate `ef7a2b2a0c13e41b67f5bb21af9607c69e1331de` (tree
`71eb7f8590479eae894e001df262301c3d409e41`) offloads auxiliary reads to the
Starlette thread pool and retains at most two privately copied parsed releases.
Every cache hit re-reads and hashes the index, every page and every asset against
the fully validated bytes; size/mtime do not substitute for byte integrity.
DB pending/retention/descriptor authority is still read by active_release on
each operation. Tests cover same-size/same-mtime tampering and missing files in
all three file families, mutation isolation, descriptor switches, invalid fence
types, cache bounds and a blocked asset read concurrent with another request.

The13 focused tests passed in15.182s on real PostgreSQL. Exactef7a2b2 combined
run collected83 cases:60 passed,23 skipped,0 failed in16.849s. All13 new cases
and47 preserved V02 HTTP/SQLite asset cases passed. The23 inherited V02 PG asset
cases skipped because their separate V02-specific DB environment was not
supplied; this is not full V02 acceptance. Exact raw result is retained under
`docs/acceptance/MS7-MIG-V04/i02-read-runtime-20261016-03/`. Independent review
of READRT-01 and the cache/offload candidate is pending; browser acceptance,
full publication/identity, clean final integration and human acceptance remain
unclaimed.

## Independent read review and applicable V02 PostgreSQL regressions

Reviewer medium independently verified sourceef7a2b2 on a fresh owned PG fixture
and independently built React artifact:13 tests passed,0 skips in10.634s;
all279 initial activation pages passed; five preflight negatives performed zero
SQL writes; ten real ASGI probes passed, including permission revocation403 and
same-size HTML tamper503. READRT-01 was closed and the source slice was reported
VERIFIED_IN_SCOPE. Combined I02/I03 and human acceptance are separate gates.

The frozen V02 PG guard permits only loopback15441. After confirming no listener,
created `ms7exec_backend_v02_medium_20261016`, labeled
`mathstart.task=migration-execution-backend-v02-medium`, on that port. Never
changed the guard or reused the shared55432 staff DB. PostgreSQL16.15 executed
22 V02 asset/redirect/security cases in the no-Django target environment:
22 passed,0 skips in13.349s. The remaining real Django comparator first failed
because the backend's minimal legacy environment lacked python-dotenv; this
failure is preserved in run01. Repeated only that case using the frontend's
configured separate legacy interpreter with target libraries on PYTHONPATH:
1 passed,0 skips in3.779s (run02). Target environment remains without Django.
These fresh PG results supplement, rather than rewrite, the23 historical skips
in the combined run. Raw receipts are under
`i02-v02-pg-assets-20261016-01/` and `i02-v02-pg-assets-20261016-02/`.

Each frozen test dropped its newly created marked UUID DB. Post-run query found
zero remaining V02 UUID databases. Rechecked the owned container label, then
stopped and removed only that container. Shared55432 remained running.

Restarted the independently reviewed ef7a2b2 public runtime on8121 with access
logging disabled; initial robots request returned200. The earlier process
stop failed, and automatic approval review initially rejected a force-stop due
to insufficient current ownership proof. Fresh TCP owner plus exact executable,
command and parent verification established the same owned Uvicorn PID;
the reviewed stop then succeeded. No rejection was bypassed. Frontend was
informed before restart and received readiness afterward; browser runs remain
frontend-owned. No shared DB mutation is running during its matrix.
