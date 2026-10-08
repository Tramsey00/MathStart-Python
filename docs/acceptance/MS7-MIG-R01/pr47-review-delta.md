# PR47 — current delta for Vladimir and Ilya

- R01 post-merge records: actual resulting MIG_BASE_SHA `60b341f`, distinct canonical
  source `8c11edad`, preserved daf4e603 own approvals and explicit owner report of
  e510744 documentation confirmation; no automatic approval of this new HEAD.
- Integration created exactly at MIG_BASE_SHA, R01 task records PR47→integration.
  Plan/trace/provenance/manifests and R02 input handoff; no later implementation.
- F01–F04 mandatory assigned to 13baybars, fix by I03, verify I05, F04 readable at
  ordinary scale without overlap/clipping; enlargement insufficient; no separate
  Vladimir independent F04 agreement invented.
- The failed attempt changing pinned ci.yml branch filters is retained in history
  and actual FAIL receipts. It failed strict R02A whole-file pin, not waived.
- Original .github/workflows/ci.yml restored byte-exact from accepted `60b341f`,
  SHA256 matches untouched historical manifest. Main-only triggers preserved.
- New .github/workflows/migration-ci.yml: name Migration baseline verification,
  only integration PR/push, full jobs block byte-identical to accepted ci.yml.
  Same PostgreSQL/env/Python/locks/install/connection/fresh smoke/verify/R02A/R03A.
  No reusable conversion, new check, skip, continue-on-error or exception.
  This is transitional current baseline CI; full target verification remains R03.
- Local R02A 30, I02 frozen-upstream 7 and R03A 41 PASS. Exact new-head migration
  CI results/checkout external PR47; require SUCCESS and independent final review.
  App/working DB/dependencies/API/contracts/MIG_BASE_SHA/integration unchanged.

[Current correction](migration-ci-correction-20261008.json),
[historical failed final filter head](ci-trigger-failed-final-head.json),
[current acceptance](acceptance.md),
[post-merge provenance](post-merge-provenance-20261008.json).

[First successful corrected CI receipt](migration-ci-first-success.json): https://github.com/Tramsey00/MathStart-Python/actions/runs/37753830717 (exact head 939bd131…, all baseline stages PASS). Final containing-head CI and independent reviews remain required.
