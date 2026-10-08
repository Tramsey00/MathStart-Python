MS7-MIG-R01: post-merge records and the owner-authorized narrow extension of existing baseline CI triggers. No later migration task implementation.

Refs #28

Current full HEAD: `f0c913e1eb7acfcde175a06cc6ab57d778acd828`
Base/integration and MIG_BASE_SHA: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`
Canonical application source: `8c11edadc8debc81432d1db1145feac504f09061`

**Acceptance blocker: historical whole-file CI pin.** Existing strict R02A suite compares current ci.yml against the digest in unchanged specs/api/candidate-manifest-v1.json. The two authorized filter changes alter this digest. No historical manifest/pin/test rewritten, check relaxed or skip introduced. A separate human compatibility decision and authorized corrective scope are required before CI can be green.

Scope/delta for Vladimir and Ilya:
- Record actual PR46 resulting commit, merge/CI provenance, accepted source and distinct reviewed/input/merge-ref identities; integration created exactly at MIG_BASE_SHA.
- Preserve original daf4e603 approvals; owner explicitly reports both reviewers confirmed e510744 documentation in their chat. This report is not a fabricated public review and does not approve the new PR47 HEAD.
- Current R01 acceptance/ADR/plan/trace/index/manifests/R02 input handoff; historical PENDING/HOLD, imported232 files, source/runtime/frozen contracts preserved.
- F01–F04 mandatory assigned13baybars, correct no later than I03#42 and verify I05#44; R02#29 records parity exceptions. F04 ordinary-scale readability mandatory, enlargement alone insufficient. No separate Vladimir F04 consent invented.
- Exactly two existing ci.yml arrays add ms7-mig-react-fastapi to pull_request base filters and push branch filters while keeping main. Complete jobs suffix byte-identical: locks, PostgreSQL setup, commands and all checks unchanged. This enables §9 existing Django baseline checks; full target verification remains R03 and has not started.

CI:
- First integration-trigger head e64d9a4b2682ee5b206f9d88f11fff2867071686: [run37701885197](https://github.com/Tramsey00/MathStart-Python/actions/runs/37701885197) **FAIL**.
- Actual checkout/tested merge-ref `4a62032c033543ef4a282981a8d97585a579ca33` confirmed by job113067016184 git log.
- Fresh PostgreSQL smoke PASS; verify_repo PASS8/8 (Django107, R03reference18, Harness73). R02A FAIL1/30,exit1 on ci.yml pin. R03A NOT RUN, normal step skipped after previous failure, no skip flag. Observed Python3.12.14/Django5.2.16/PostgreSQL160015.
- Final current HEAD `f0c913e1eb7acfcde175a06cc6ab57d778acd828`: [run37702653809](https://github.com/Tramsey00/MathStart-Python/actions/runs/37702653809) **FAIL**, [job113069525484](https://github.com/Tramsey00/MathStart-Python/actions/runs/37702653809/job/113069525484). Actual checkout/tested merge-ref `6ca3c96b8f098c52cece863eefec65ef6c1db819` verified in job git log; merge-ref parents are exact base60b341f and final headf0c913e. Fresh PostgreSQL smoke and verify_repo PASS8/8 (Django107/R03reference18/Harness73); R02A FAIL1/30 on unchanged historical ci.yml pin,exit1. R03A NOT RUN after failure. Observed Python3.12.14/Django5.2.16/PostgreSQL160015. First-head results and old snapshot SUCCESS are separate history, not substituted for final checks.
- Scope/links/source/record hashes PASS:1022 other input files exact with explicitly authorized workflow exception;305 exact Git record blobs/33,732,402bytes, excluding manifest itself. Historical CI pin/test/source manifest and jobs unchanged.
- Previously merged snapshot CI remains SUCCESS at its own60b341f; it is not claimed as this amendment CI.

Human provenance remains distinct:
[Ilya baseline/ADR + Task Approval](https://github.com/Tramsey00/MathStart-Python/pull/46#issuecomment-6047568271),
[Ruslan baseline/ADR + D01–D09](https://github.com/Tramsey00/MathStart-Python/pull/46#issuecomment-6047773231),
[Vladimir baseline/ADR + Task Approval](https://github.com/Tramsey00/MathStart-Python/pull/46#pullrequestreview-5449019477).
Original GitHub records are daf4e603; e510744 confirmation is an explicit owner report. No final-head approval transfer.

Records:
- [Short reviewer delta](https://github.com/Tramsey00/MathStart-Python/blob/f0c913e1eb7acfcde175a06cc6ab57d778acd828/docs/acceptance/MS7-MIG-R01/pr47-review-delta.md)
- [Trigger audit and exact pin conflict](https://github.com/Tramsey00/MathStart-Python/blob/f0c913e1eb7acfcde175a06cc6ab57d778acd828/docs/acceptance/MS7-MIG-R01/ci-trigger-adjustment-20261008.json)
- [Observed first-trigger checkout/step/log receipt](https://github.com/Tramsey00/MathStart-Python/blob/f0c913e1eb7acfcde175a06cc6ab57d778acd828/docs/acceptance/MS7-MIG-R01/ci-integration-trigger-first-run.json)
- [Current acceptance](https://github.com/Tramsey00/MathStart-Python/blob/f0c913e1eb7acfcde175a06cc6ab57d778acd828/docs/acceptance/MS7-MIG-R01/acceptance.md)
- [Post-merge provenance](https://github.com/Tramsey00/MathStart-Python/blob/f0c913e1eb7acfcde175a06cc6ab57d778acd828/docs/acceptance/MS7-MIG-R01/post-merge-provenance-20261008.json)

Remaining: resolve historical pin compatibility under separately agreed scope, obtain successful exact final-head CI and independent Vladimir/Ilya amendment acceptance, then authorized integration intake. Active R01 plan retained; no automatic completion. No app/working DB/MIG_BASE_SHA/integration change, R02/I01/R03 implementation, merge or migration Issue closure. R01 delay/history and future calendar/checks remain unchanged.
