# MS7-MIG-V01 — SQLAlchemy models, Alembic and upgrade profiles

V01 adds target persistence alongside the runnable Django baseline. Historical
Django migrations and frozen R02 remain preserved. B01 is limited to BIGINT PK
for `auth_group_permissions.id`, `auth_user_groups.id` and
`auth_user_user_permissions.id`; related FK remain INTEGER.

Reviewed published implementation: `1f97d762c4089efb2e4ef6d8c7ebe0bdcbe161f4`.
Accepted integration input: `8d958aeeb17da46839722441425ccbb5889e2ab7`.
Immutable MIG_BASE_SHA: `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
The new evidence commit/PR HEAD is **PENDING**, with no future SHA assigned.
This text is a proposal for owner publication; it has not been posted to GitHub.
Links to new evidence use the task branch and become live only after authorized
publication; replace that branch reference with the actual evidence commit SHA
when it exists. Existing historical links are pinned to implementation SHA.

- Original [independent audit](https://github.com/Tramsey00/MathStart-Python/blob/1f97d762c4089efb2e4ef6d8c7ebe0bdcbe161f4/docs/acceptance/MS7-MIG-V01/independent-audit-v3/MS7-MIG-V01-INDEPENDENT-AUDIT-REPORT.md):
  **NOT READY**, F1–F3. Checked input HEAD `8d958…` plus 53 untracked files;
  all original failures and findings are retained.
- Developer remediation: F1/F2/F3 **FIXED locally**; B01/CHECK regressions present.
  [v3](https://github.com/Tramsey00/MathStart-Python/blob/1f97d762c4089efb2e4ef6d8c7ebe0bdcbe161f4/docs/acceptance/MS7-MIG-V01/implementation-report-v3.md) and [v4](https://github.com/Tramsey00/MathStart-Python/blob/1f97d762c4089efb2e4ef6d8c7ebe0bdcbe161f4/docs/acceptance/MS7-MIG-V01/implementation-report-v4.md) retain
  execution records and limitations. v4 local self-checks ran on `d5dc9…` plus
  uncommitted CI changes subsequently published as `1f97…`: legacy 109 PASS
  without SQLAlchemy/Alembic, verify_repo 8/8, target 34 PASS including 23 PG,
  zero skips. These are historical local results, not new target GitHub CI.
- Actual [positive independent technical re-audit](https://github.com/Tramsey00/MathStart-Python/blob/ms7-mig-v01-schema/docs/acceptance/MS7-MIG-V01/independent-reviews-v5/final-f1-f2-f3/MS7-MIG-V01-FINAL-INDEPENDENT-AUDIT.md):
  **READY to prepare publication**, checked `8d958…` plus 71 untracked files,
  34 target PASS/zero skips and independent F2 two-order controls. All 34 audited
  backend files match `d5dc9…` blobs exactly or by LF/CRLF only; three differ at
  current `1f97…`. It is not an exact-current-SHA audit or human Task Approval.
- Subsequent [independent CI remediation technical review](https://github.com/Tramsey00/MathStart-Python/blob/ms7-mig-v01-schema/docs/acceptance/MS7-MIG-V01/independent-reviews-v5/ci-remediation-review-transcript.md):
  **READY in CI-fix scope**, checked `d5dc9…` plus 5 modified/15 new files;
  one nonblocking P3 concerning fixed legacy helper evidence output. It executed
  discovery/unit/contract checks, but did not rerun full legacy/PG suites.
  [Review provenance](https://github.com/Tramsey00/MathStart-Python/blob/ms7-mig-v01-schema/docs/acceptance/MS7-MIG-V01/independent-review-provenance-v5.json) separates those scopes.
- [Current GitHub legacy CI](https://github.com/Tramsey00/MathStart-Python/actions/runs/38054413732):
  **SUCCESS**, run head SHA `1f97d762c4089efb2e4ef6d8c7ebe0bdcbe161f4`.
  Root dependencies/Django/PostgreSQL baseline only. Job API confirms Verify
  repository success; raw log test counts/checkout merge SHA are NOT VERIFIED.
- Target SQLAlchemy/Alembic PostgreSQL CI: **PENDING** — [R03 handoff v5](https://github.com/Tramsey00/MathStart-Python/blob/ms7-mig-v01-schema/docs/acceptance/MS7-MIG-V01/r03-ci-handoff-v5.md)
  requires an isolated locked environment, disposable PG16, 34 tests including
  all 23 PostgreSQL cases with zero skips at the actual PR candidate HEAD.
- Ruslan owner review was relayed by the user for `1f97…`: no new blocking code
  defects reported, evidence corrections required. [Source record](https://github.com/Tramsey00/MathStart-Python/blob/ms7-mig-v01-schema/docs/acceptance/MS7-MIG-V01/owner-review-intake-v5.json)
  does not claim a GitHub review URL. Independent human Task Approval: **PENDING**.

[Publication manifest](https://github.com/Tramsey00/MathStart-Python/blob/ms7-mig-v01-schema/docs/acceptance/MS7-MIG-V01/publication-manifest-v1.json) verifies 86 exact Git blobs
at the published implementation commit. [Historical comparison](https://github.com/Tramsey00/MathStart-Python/blob/ms7-mig-v01-schema/docs/acceptance/MS7-MIG-V01/publication-comparison-v1.json)
retains 36 FAIL from checkout-vs-blob digests, all explained by LF→CRLF.
[Current §17 index](https://github.com/Tramsey00/MathStart-Python/blob/ms7-mig-v01-schema/docs/acceptance/MS7-MIG-V01/old-to-new-evidence-v4.json) preserves original results and
approvals while adding platform disposition, exact implementation identity,
current status, current evidence/CI and pending gates. No old record was rewritten.

**V01 remains INCOMPLETE.** Target CI and independent owner Task Approval must
close before acceptance/merge. After an authorized evidence commit/publication,
record the actual new PR HEAD separately and obtain CI/review on that candidate.
