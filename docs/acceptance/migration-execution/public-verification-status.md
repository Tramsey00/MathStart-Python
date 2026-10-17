# Public and identity migration checkpoint

Current authority: MIGRATION.md. Overall status: **IN_PROGRESS**. The combined
candidate is not READY_FOR_HUMAN_ACCEPTANCE; final independent review has not run.

Exact `62197b3d25251b7f157af203cccb2aa65135b173` passed
[push CI39035330261](https://github.com/Tramsey00/MathStart-Python/actions/runs/39035330261):
167 frontend tests,40 source/read/golden/content-inspection tests,18 Chrome360
scenarios with zero skips,29 PostgreSQL identity/staff tests. The full source
inventory, fresh synthetic preparation/build/initial activation, source guard,
startup and cleanup passed within that declared scope. Artifact12101498432 was
downloaded and matched SHA256
`028bdf09a1adc54181f042be6844fed611280ced701651ad4f42347c92ae1f00`.

The subsequent recovery/revocation runtime `ebe27f0003f50618ac12589e9405f7485acf5c2d`
passed32 affected PG tests and2 revoked-cookie/session delta tests locally.
Its integrated [push CI39035893192](https://github.com/Tramsey00/MathStart-Python/actions/runs/39035893192)
completed SUCCESS:167 frontend,40 source/read/golden/content-command tests,18 Chrome360 cases/zero skips,32 PG identity/staff, source guard/startup/cleanup PASS. Artifact12102715584 matched SHA256 `fce62c58e52b4daef8227362ebb4ea9ad3559661cf2358f2d6eee0795b70b22d`. Its [exact-SHA receipt](i02-verification/ci-ebe27f0-result.json) and provenance are retained. Later checkpoint commits change docs/evidence only.
The earlier45a4a31 andc1dd872 results remain historical exact-checkout evidence.

Content CLI now compares263 source lessons including metadata/HTML/CSS/JS with
PG, inspects actual HTTP quality, and reports site references/media integrity.
The seven local regressions and extended subprocess case preserve report file
side effects, nonzero failures and DB digest; no Django is installed/imported.
Fixture HTTP tests establish command wiring, not rendered target acceptance.
[Commands and remaining runtime limitations](../../../backend/READ_RUNTIME.md).

General CI pure/legacy passed; full target remains **SKIPPED/PENDING**, not PASS,
because the concrete command map is incomplete. Mandatory target/fresh/upgrade
profiles, full browser/visual/interactivity matrix and operational rehearsals are
still required. Publisher takeover/recovery and legacy cutover/F-proof import,
remaining admin parity, deployment configs and full versioned product documents
remain engineering work. Final independent review follows combined readiness.

[Candidate record](public-verifier-candidate.json),
[CI receipt](i02-verification/ci-62197b3-result.json),
[browser receipt](i02-verification/ci-62197b3-browser-receipt.json),
[checkout provenance](i02-verification/ci-62197b3-public-provenance.json).
Raw artifact ZIPs and job logs remain under ignored var/. Owned local PostgreSQL
containers and HTTP fixtures were removed;8131/8132/55441 have no listeners.
The original database container on5432 remains running and untouched. No main
merge, Issue closure, human acceptance or production deployment was performed.

## Historical verifier checkpoint

The following is the preserved earlier scoped record, not the current execution instruction.

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
