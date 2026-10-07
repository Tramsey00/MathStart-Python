# PR47 — delta for Vladimir and Ilya

- Post-merge R01 records pin actual PR46 resulting MIG_BASE_SHA
  60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7, preserve separate source8c11edad,
  human reviewed daf4e603 and owner-reported e510744 confirmation.
- Integration originates exactly at MIG_BASE_SHA; R01 task records PR47 targets it.
  Plan/trace/provenance/manifests and R02 input handoff added; no later task starts.
- F01–F04 mandatory assigned13baybars, correction by I03, verify I05;
  F04 ordinary-scale readability, enlargement alone insufficient. No independent
  Vladimir F04 consent invented; original evidence/criteria preserved.
- Newly owner-authorized CI change is exactly two arrays:
  pull_request branches and push branches now [main, ms7-mig-react-fastapi].
  Existing jobs, commands, checks, PostgreSQL, dependency lock and pins unchanged.
  This runs current Django baseline for §9 integration workflow; target R03
  verification still future.
- BLOCKER: historical specs/api/candidate-manifest-v1.json pins entire ci.yml.
  New file digest differs; strict unchanged R02A test fails1/30. No historical
  proof/pin/test rewritten, no skip. Review human compatibility decision before
  accepting this amendment; actual new-head CI required, not old green CI.
- Independent approval required on final exact PR47 HEAD and its checks.
  Earlier approvals and owner-reported e510744 agreement do not approve this
  new post-merge/CI amendment. No PR merge or migration Issue closure by agent.

[Trigger/pin audit](ci-trigger-adjustment-20261008.json),
[current acceptance](acceptance.md),
[post-merge provenance](post-merge-provenance-20261008.json).
