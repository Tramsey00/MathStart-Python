# V01 final Independent Task Approval packet — exact PR51 candidate

Historical candidate evidence (2026-10-11). Current I01/V01 acceptance is
**ACCEPTED_INTEGRATION** under human receipts and external merges; see
[current joint-input handoff](accepted-integration-ci-20261012.md). Earlier pending
snapshots below do not describe current acceptance.

Prepared by R03 on 2026-10-11 Europe/Moscow. Decision owner: Руслан.
**CI evidence complete.** Initially prepared with Independent Task Approval
pending; the later external owner decision is recorded below. R03 itself does
not issue approval, merge authorization or ACCEPTED_INTEGRATION.

## Candidate and checkout provenance

| Reference | Exact SHA |
| --- | --- |
| PR51 live HEAD and actual target checkout | `393d98890649c6c7c47908424ba0d076b5b5e56e` |
| Candidate tree | `4a9dde548e42c05e1e9fa68aa063272d5d8700d1` |
| Reviewed implementation (backend unchanged) | `1f97d762c4089efb2e4ef6d8c7ebe0bdcbe161f4` |
| Accepted integration input/base | `8d958aeeb17da46839722441425ccbb5889e2ab7` |
| Immutable MIG_BASE_SHA | `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7` |
| R03 workflow branch HEAD used by target run | `a6b683211e554507cc1bb5801d5368d73f316c61` |
| Actual R03 workflow checkout (PR49 merge ref) | `66818293d03d6a7edfa4c77440f6d9179e8ea367` |
| R03 workflow tree | `0164b93d5228c40d32ac7986059affbca364dae7` |
| Observed PR51 merge ref / earlier legacy checkout | `5ddadb133dc21bdce4ca361d52e3680c3d2c8007` |

The target job checks out PR51 HEAD explicitly, while workflow code comes from
PR49. Live PR API head/base match the candidate pins before any target commands.
R03 merge parents are accepted base8d958ae and workflow heada6b6832; merge tree
equals workflow head tree. PR51 merge ref is only observed in target intake;
it is separately the actual checkout of the earlier baseline run.
Raw [candidate provenance](postgres-pr51-ci/run-38156436658/candidate-provenance.json)
and [workflow provenance](postgres-pr51-ci/run-38156436658/workflow-provenance.json)
retain all exact references. A later R03 evidence-only publication commit does
not inherit the earlier workflow checkout SHA or change the tested V01 candidate.

## Actual GitHub target result

[Run38156436658 / attempt1](https://github.com/Tramsey00/MathStart-Python/actions/runs/38156436658),
job114520274435: **SUCCESS**. Parallel R03 push
[run38156434420](https://github.com/Tramsey00/MathStart-Python/actions/runs/38156434420)
also succeeded on the same exact candidate and workflow implementation.

| Required evidence | Actual result |
| --- | --- |
| Separate target-test lock/venv | 22 exact packages, locked install, pip check and freeze PASS |
| Python / PostgreSQL | 3.12.15 / 16.15; server_version_num160015 |
| Explicit unchanged v5 gate | 34 PASS = 11 unit + all23 PostgreSQL; 0 errors/failures/skips/expected failures |
| Fresh install twice | Two distinct marked databases; both fixture contexts cleaned |
| Upgrade A/B/C | All three actual profile events and successful subtests |
| Required negative/control coverage | All existing cases PASS; 40 successful subtests |
| Fixture lifecycle | 57 distinct marked databases created/cleaned; final non-template DB inventory empty |
| Service lifecycle | Exact job-owned ID/image/health/port verified; tmpfs data, no volume; stop0 then GitHub rm succeeded |
| Source and historical preservation | All106 backend/V01-history hashes unchanged and independently match exact candidate Git blobs |
| Frozen baseline workflows | Both candidate workflow blobs match accepted input; existing R03 baseline/frontend workflows untouched |
| R03 evidence regressions / input preservation | 11 PASS / 1370 preserved files PASS |

Fresh database names and all34 actual test IDs/results/timestamps, database events
and subtests are in [test observations](postgres-pr51-ci/run-38156436658/test-observations.json).
Raw [target gate output](postgres-pr51-ci/run-38156436658/target-suite.log) reports
the exact candidate and `tests=34 PG_collected=23 skips=0 failures=0 errors=0 status=PASS`.
[Execution](postgres-pr51-ci/run-38156436658/execution.json) records command argv,
times and exits; [before](postgres-pr51-ci/run-38156436658/postgres-before.json)
and [after](postgres-pr51-ci/run-38156436658/postgres-after.json) include actual
versions/installed packages and empty DB inventories.

The required negatives remain unchanged: three rollback injection stages; ten
baseline schema/head defects; six additive-protocol drift defects; seven malformed
empty tracking structures; seven unknown/ambiguous/inapplicable target head states;
constraints/deferred FK/JSON NULL/PROTECT; real ordered-lock/delete races and
sequence disconnect/retry. B01 exercises FRESH/A/B/C as four subtests. CHECK truth
table, real-Django F1 timestamps, F2 concurrency and F3 positive controls passed.
F1/F2 new diagnostic JSON is retained under `owner-diagnostics/`; original local,
negative-audit, re-audit and self-check records remain historical and unchanged.
This run does not claim additional two-order independent probes outside its34 cases.

## Raw receipts and lifecycle proof

[Artifact11707839998](https://github.com/Tramsey00/MathStart-Python/actions/runs/38156436658/artifacts/11707839998)
ZIP SHA256 `5e3c0186b51c0702c3dc6fb23ff8233de89630ed5458d0bc8d7b24d6db1893a6`
matches the Actions digest. All18 member files are saved byte-for-byte in this
repository with an [artifact manifest](postgres-pr51-ci/run-38156436658/artifact-manifest.json).
The separate [job receipt](postgres-pr51-ci/run-38156436658/ci-job-receipt.json)
retains API steps and decoded log excerpts proving tmpfs creation and final
container removal after upload. [Service cleanup](postgres-pr51-ci/run-38156436658/service-cleanup.json)
records successful stop and Running=false. No persistent volume needed deletion.
New [versioned V01 record](../MS7-MIG-V01/r03-target-ci-v6.json) supersedes the
pending target-CI status as new evidence, without rewriting owner history.

Earlier R03 configuration failures and first successful suite with qualified
storage proof remain in the [trace](../../agent-traces/MS7-MIG-R03-postgres-pr51-ci.md)
and separate run directories. They are not replaced by the final PASS receipt.

## Baseline and human decision

Earlier current-candidate [baseline run38137695565](https://github.com/Tramsey00/MathStart-Python/actions/runs/38137695565)
was independently re-read: head393d988, actual merge checkout5ddadb1, SUCCESS,
fresh legacy smoke, verify_repo8/8, Django109/R0318/Harness73/R02A30/R03A41 PASS.
It is separate historical Django evidence; the new target run supplies the
previously missing explicit SQLAlchemy/Alembic PostgreSQL CI gate.

Published implementation/B01/CHECK/F1–F3 reviews,86-blob publication manifest and
§17 evidence index are available on exact
[PR51 candidate](https://github.com/Tramsey00/MathStart-Python/pull/51).
The user's previously confirmed owner evidence findings remain closed; R03 does
not recreate that owner review or issue approval on the owner's behalf.

Руслан can now assess the final candidate and issue an explicit Independent Task
Approval bound to393d988. Until that human decision, V01 remains INCOMPLETE /
AWAITING INDEPENDENT TASK APPROVAL. No production/cutover/deployed variant, load
or post-commit acknowledgement-loss verification is claimed. Recorded P3 helper
evidence-output follow-up remains nonblocking and unchanged. No merge or Issue
closure performed. Wider R03/V02/I02 gates and I01 hover/UX review remain separate.

## Later external decision — observed after evidence publication

At2026-10-11T16:45:45Z, `Tramsey00` published
[Independent Task Approval5484103844](https://github.com/Tramsey00/MathStart-Python/pull/51#pullrequestreview-5484103844)
APPROVED on exact393d988. That receipt cites baseline38137695565 and the first
successful target suite38155839568 and permits integration; the final tmpfs
run38156436658 additionally supplies the stronger storage-lifecycle proof on
the same candidate, without changing backend/test bytes.

GitHub records an external squash merge by `Tramsey00` at16:46:09Z into
`4a1b8b05709e7c5485194ca5551aee0824333660`, parent8d958ae, tree4a9dde54 equal
the verified candidate tree. This is a subsequent external state change, not
an action performed by R03. The human receipt declares ACCEPTED_INTEGRATION
after merge and keeps Issue34 open until final main integration.
The earlier pending-decision text above describes the packet's preparation state;
the later actual decision has this separate provenance.

R03 records-only commit4e20b54 triggered a later run38156928889. During the
external integration change its PR49 checkout moved to a new merge ref;
the existing event/checkout provenance guard refused linkage before target
commands. That run is FAILURE / target NOT_RUN, with owned service cleanup
SUCCESS. It is not substitute target evidence and does not invalidate the
previous exact-candidate run. Closed PR51 cannot satisfy the adapter's open-PR
intake; the guard remains unchanged. No post-merge/integration target verification
is claimed. Full state and decoded log excerpts:
[new external-state record](../MS7-MIG-V01/r03-target-ci-external-state-v7.json).
No agent merge, approval, Issue closure or wider R03/I01 acceptance occurred.
