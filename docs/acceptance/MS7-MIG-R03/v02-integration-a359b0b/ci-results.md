# R03 guards on accepted a359b0b — Linux CI results

Approved V02 implementation remains `8256cbf4b38e97fc1169fea85f2d558950543be8`.
Accepted squash and actual suite checkout are `a359b0bf270560d5b45d0a89e1ca1e9cfddffdb6`,
tree `74c3014516ec3a2110d2cfec13c8e7afb8ae5024`.
R03 code head `b541bf0be2bada6ada81e6cb15f60155f93b3c3f`.

| New evidence | Outcome | Actual workflow checkout |
| --- | --- | --- |
| [Frontend38801486277](https://github.com/Tramsey00/MathStart-Python/actions/runs/38801486277), job116651355161 | SUCCESS,112 tests +5 historical dispatcher tests,10 required commands | `2935a86c5003ef3da83e854efd404f6448bec7c3` (PR synthetic merge/event checkout; PR head b541bf0 separately retained) |
| [V01 PostgreSQL38801476734](https://github.com/Tramsey00/MathStart-Python/actions/runs/38801476734), job116651322932 | SUCCESS,34/all23 PG,0 skips; fresh×2, upgradesA/B/C,57 fixture DBs cleaned | `b541bf0be2bada6ada81e6cb15f60155f93b3c3f` (push) |
| [Global R0338801476735](https://github.com/Tramsey00/MathStart-Python/actions/runs/38801476735) | FAILURE: verify/pure SUCCESS; target prerequisite PENDING/empty command map, downstream NOT_RUN | b541bf0 (push) |
| [Owner post-merge baseline38796031561](https://github.com/Tramsey00/MathStart-Python/actions/runs/38796031561) | SUCCESS, baseline only on a359b0b | a359b0b |

Frontend locked install/generation/pins/typecheck/validators/tests/dispatcher/
production guards/build/audit PASS at actual a359b0b. Node24.21.0/npm11.19.0.
Frozen workflows/captures and accepted human receipts/tree/ancestry checked.
V01 uses its unchanged22-package test lock, separate Python3.12.15 environment
and owned PostgreSQL16.15 tmpfs service on55441. Exact34 IDs and all23 PG cases,
every recorded subcase PASS,0 skips. Fresh×2/upgradeA/B/C and negative cases,
timestamp/concurrency evidence retained. Empty before/after DB inventories,
57 distinct marked fixtures cleaned, exact owned service stopped and GitHub
post-job container removal SUCCESS. [Independent reconciliation](ci-reconciliation.json)
checks all reported counts, exits, complete source snapshots, lock/environment,
actual checkout/tree and original ZIP digests/member streams.

## Resolved R03 guard adaptations and retained refusals

[First V0138800500641](https://github.com/Tramsey00/MathStart-Python/actions/runs/38800500641)
at control260c60a stopped before suites: old R03 snapshot compared all backend to
historical V01 implementation and saw accepted V02 additions. No target case ran.
The snapshot now compares the explicitly accepted combined input, retaining
all original source/lock/handoff/matrix pins and clean-checkout checks.

[Second V0138800895139](https://github.com/Tramsey00/MathStart-Python/actions/runs/38800895139)
at controlbeb0696 passed intake but unchanged owner v5 helper made the same old
all-backend prerequisite assertion. Observed cases=[]; suite NOT_RUN, not34 failures.
The historical helper is preserved byte-for-byte. R03 now uses a separate accepted
input adapter for unchanged owner modules/matrix: exact owner-controlled config,
full accepted tree/preservation, source pins, reserved endpoint/explicit disposable
acknowledgement,34 unique exact IDs/23 PG and0 skips, strict results/subtests/fixture
receipt validation. It emits `R03_V01_ACCEPTED`, never a false unchanged-v5 receipt.
Legacy mode still invokes the original helper. Original V01/V02 files, locks,
tests and helper digests are unchanged.15 PostgreSQL adapter/observer guard tests
and12 accepted-input provenance regressions pass in Linux CI. No permissive
backend delta/automatic pins or skips were introduced.

Earlier frontend38800500604 SUCCESS at260c60a is retained separately. Global
38800500925 and38800895058 retain verify/pure PASS, target prerequisite FAILURE
and downstream NOT_RUN. These CI results do not revoke accepted V02 or assert
full R03/I02 acceptance. R03 remains INCOMPLETE.

## Original raw artifacts

| Artifact | Original ZIP SHA256 |
| --- | --- |
| [Frontend12004342356](https://github.com/Tramsey00/MathStart-Python/actions/runs/38801486277/artifacts/12004342356) | `ec8aed5a431eb62e243768fe5a449d9e8b467b834db8d8e51b35f7f3912ade04` |
| [V0112004746600](https://github.com/Tramsey00/MathStart-Python/actions/runs/38801476734/artifacts/12004746600) | `8f0f38ead4902731af45235cfc3d0a6e61211dd0097fe01931fa435f05c465bd` |
| Earlier frontend12003218574 | `ae8748967674d040cbf2879d2acd460604f14340731841739eeeb9657e53fd5f` |
| First refusal12003918089 | `58d18a43fd64b5536fddc018c17a70c523099fe8a3f033be00c00c4acc907d3e` |
| Second refusal12004077318 | `e9eb0edba2e685fa0ff09d10c3f4dbf9fa59fd89110d44e8c5efd15947199ba3` |

All five original ZIPs are retained locally beside this document and match GitHub
digest/size. Every member has SHA256/size in reconciliation; no ZIP member was
rewritten. First refusal decoded job log is separately labelled decoded text.
Original V02 runs remain tied to8256cbf (or76d8eac for older evidence), and
original controls1b75c6e/anchor5a9a/control0effadc remain historical. **No V02 suite
was rerun on a359b0b**. Baseline and current frontend/V01 results are distinct.
