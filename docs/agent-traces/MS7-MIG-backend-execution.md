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
