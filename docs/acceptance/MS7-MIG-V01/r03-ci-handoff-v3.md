# V01 -> R03 CI handoff v3 after F1/F2/F3 remediation

Root workflows remain owned by Руслан and were not edited. The adjacent
[proposed patch](r03-ci-handoff-v3.patch) supersedes the v2 proposal for review;
it installs backend dependencies and runs all three target test modules,
including the 12 new remediation/sequence/B01 methods. Current target
collection is 34 methods (11 unit + 23 PostgreSQL).

The dependency and disposable service changes remain those of v2: keep root
requirements, add backend runtime lock, keep baseline5432 and add the reserved
localhost55441 mapping, set the target admin URL only for the explicit target
step. Credentials are the existing synthetic disposable CI values. No root
file, live service, secret, GitHub workflow run or PR was changed by this task.

The new F1 subprocess uses the installed Django baseline and reserved marked
database; F2 uses two independent sessions and a bounded barrier; F3 invokes
the CLI in subprocesses and verifies nonzero exits with unchanged schema/data.
No tests require the Windows-specific runtime helper to execute in CI. The
separate target-only runtime venv still provides local absence-of-Django proof;
the patch does not claim that isolation test in Linux CI.

The baseline runner omits the target admin URL in its child to separate evidence:
Django discovery includes 23 explicit target PG skips; the explicit target suite
runs those methods without skips. Root-lock-only CI still needs this dependency
handoff before discovered backend tests can import. Applying/testing the patch
and a green GitHub CI run remain owner work; this artifact is not acceptance.

LF diff against the CRLF checkout requires the read-only applicability check
`git apply --check --ignore-space-change docs/acceptance/MS7-MIG-V01/r03-ci-handoff-v3.patch`.
No whitespace conversion or patch application to root workflows is authorized.
