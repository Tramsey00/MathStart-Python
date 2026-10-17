# Public and identity migration checkpoint

Current authority: MIGRATION.md. Overall status: **IN_PROGRESS**, not READY_FOR_HUMAN_ACCEPTANCE.

Clean push CI [39029833587](https://github.com/Tramsey00/MathStart-Python/actions/runs/39029833587)
tested exact checkout `45a4a316e5826151124fbf77f19d6d3aa1b411f2` with unchanged source.
The downloaded artifact12100316135 matched SHA256
`34046163a86648af619ac058e3cc8470623d83149f9f00ef4007da705ab25e0c`.
Its receipts retain actual argv/cwd/exits, source/tree identity, release digests,
versions and process cleanup. Verified scope:157 frontend tests,33 source/read/golden
tests,18 Chrome360 public/account/staff scenarios, and24 PostgreSQL identity/staff tests.
Python3.12.15,Node24.21.0,npm11.19.0,PostgreSQL16.15. This includes fresh synthetic
preparation/build/initial activation; it does not substitute for the complete target
fresh/upgrade/operational acceptance profiles.

General CI [39029833597](https://github.com/Tramsey00/MathStart-Python/actions/runs/39029833597)
passed pure and legacy groups. Full target was **SKIPPED** because the concrete
command map remains PENDING. There is no full-target PASS.

Local browser delta used runtime45a4a31 and verified unchanged artifact a287bc6:
18/18 passed with source guard and owned startup/cleanup. It is labelled
PASS_BROWSER_DELTA_ONLY and is not presented as a new complete build.
Canonical local lifecycle/provenance16/16 passed with unbuffered logging;
earlier failures and diagnostic runs are retained under ignored var/.

Receipts: [candidate record](public-verifier-candidate.json),
[CI run](i02-verification/ci-45a4a31-result.json),
[browser receipt](i02-verification/ci-45a4a31-browser-receipt.json),
[checkout provenance](i02-verification/ci-45a4a31-public-provenance.json).
Owned local ASGI/legacy/browser processes and disposable PostgreSQL container were removed;
Windows reports no listeners on8131/8132/55441. The original5432 container remains running.
Private cookies/signing keys/traces are excluded. Raw downloaded ZIP and selected
logs are retained locally in ignored var/ci-public-45a4a31*, not copied into Git.

Remaining engineering:complete bridge lifecycle/cutover and baseline admin parity,
full publisher/recovery/CLI, concrete target registry, production-oriented local
configs and disposable backup/restore/performance/cutover rehearsal, full source
product-document mapping, nine-project browser/visual matrix and final independent
review. Main, Issues and production were not changed.

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
