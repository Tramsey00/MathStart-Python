# MS7-MIG-R01: current human acceptance and snapshot handoff

**Human records accepted at reviewed HEAD daf4e6038761f8d1bf1c60f0976473d987cce230.
Current documentation amendment requires reviewers' confirmation at new exact HEAD.
R01 INCOMPLETE pending that confirmation and snapshot workflow; MIG_BASE_SHA=PENDING.**

Canonical application source8c11edadc8debc81432d1db1145feac504f09061 unchanged.
ADR-0006 platform decision accepted by the three participants in their scopes
on reviewed revision; target implementation is not accepted or started.
MIG-G0 human baseline/ADR conditions recorded; current snapshot confirmation
and accepted merge remain pending. New current HEAD/CI/tested merge-ref in [PR46](https://github.com/Tramsey00/MathStart-Python/pull/46).

| Human record | Person / timestamp Europe/Moscow | Exact head / decision |
| --- | --- | --- |
| [Baseline+ADR and independent Task Approval](https://github.com/Tramsey00/MathStart-Python/pull/46#issuecomment-6047568271) | 13baybars;08.10.2026 00:51:20 | daf4e603…; APPROVED in UI/content/visual/frontend consumer scope |
| [Owner baseline+ADR / D01–D09](https://github.com/Tramsey00/MathStart-Python/pull/46#issuecomment-6047773231) | Tramsey00;08.10.2026 01:05:10 | daf4e603…; APPROVED as owner, not independent self-approval |
| [Baseline+ADR and independent Task Approval](https://github.com/Tramsey00/MathStart-Python/pull/46#pullrequestreview-5449019477) | VladimirFrolov777;08.10.2026 01:13:03 | API state APPROVED,commit_id=daf4e603…; architecture/backend/API/PostgreSQL/data ownership scope |

Full reviewed head for all three:
`daf4e6038761f8d1bf1c60f0976473d987cce230`.
Live author/date/body/commit/CI evidence and scope in
[final human receipt](final-human-acceptance-20261008.json). Old approvals retain
that SHA; no automatic transfer to the documentation commit. Reviewers must
confirm [this short amendment list](final-review-changes.md) at new full HEAD
and its successful CI before ready-for-merge.

## D01–D09 human conditions at reviewed head

| ID | Recorded decision / remaining implementation obligations |
| --- | --- |
| D01 | ACCEPTED source snapshot, preserved authored content/CSS/JS, prior account/grades and historical evidence; PR27 already in source, no replay. |
| D02 | ACCEPTED original source with known F01–F04; agreed13baybars correction no later than I03, verification I05; no source fix in R01. |
| D03 | ACCEPTED canonical source/disposable parity, three distinct environments: Ruslan working DB audit, Ilya substantive working drift, Ilya disposable baseline. Working DBs unchanged. |
| D04 | ACCEPTED platform decision/modular monolith/invariants/design/URLs/SEO/SSG freshness/recovery/private-data boundaries; future implementation subject to task gates. |
| D05 | ACCEPTED complete inventoried staff/admin scope, including seven Content view-only models and User/Group password/roles/permissions/history/guarded deletion; no hidden exclusion or CLI blanket replacement. |
| D06 | ACCEPTED explicit backend/schema/Alembic owner Vladimir, frontend Ilya, contracts/verification/integration Ruslan; single DDL/write owner, controlled writer transfer; PostgreSQL acceptance, opt-in SQLite local compatibility only. |
| D07 | ACCEPTED one re-login, no password reset, password/session/CSRF/receipt compatibility and scoped security responsibilities; implementation verification later. |
| D08 | CLOSED from actual07.10.2026 original R02A/R03A independent comments; historical absence/pending preserved without backdating. |
| D09 | ACCEPTED participant calendar/staging-disposable boundary; Vladimir D09 agreement additionally reported by Ruslan in the current direct user message, not a separate Vladimir-authored comment. Remaining target dates and MIG-G4 13.10.2026 23:59 Moscow retained; R01 delay beyond07.10 recorded; checks/scope not reduced. |

[D08 receipt](acceptance-reconciliation-20261007.json) remains exact.
[Inventory](inventory.md), [source manifest](source-manifest.json),
[three environments](ilya-20261007/README.md), [follow-up criteria](ilya-20261007/follow-up-F01-F04.md),
[ADR-0006](../../adr/ADR-0006-react-fastapi-migration.md) and
[active plan](../../exec-plans/active/MS7-MIG-R01.md) remain review inputs.

## Remaining current-head and merge conditions

Both independent R01 approvals and all three baseline/ADR records exist at daf4e603.
The documentation amendment records those facts and agreed F01–F04 criteria;
it is not already approved. Confirm new full HEAD and CI with reviewers.
PR stays draft/unmerged under this instruction. No migration Issue closure.
Separate optional Vladimir F04 independent review agreement **PENDING / NOT GIVEN**;
it is not falsely required as a new R01 approval or assigned without consent.
F01–F04 **MANDATORY / ASSIGNED / NOT IMPLEMENTED**; their resolution belongs to I03/I05.

After reviewers' confirmation and successful current checks, an authorized
human may mark ready and merge snapshot. Read actual resulting main commit,
verify merge/accepted input/current checks, record resulting MIG_BASE_SHA.
Then create ms7-mig-react-fastapi from that exact resulting commit and
ms7-mig-r01-baseline from accepted integration input under §10, tracking
worktrees/input SHA. These steps are not performed now; subsequent tasks still
require their own dependencies and acceptance. Issues remain open until final
migration integration→main workflow; do not infer closure from this snapshot.

## Historical acceptance snapshots

[Acceptance at reviewed daf4e603](acceptance-at-daf4e603.md) is preserved as
exact Git bytes and retains its original PENDING/partial wording.
[Earlier scoped D02/D03 receipt](ilya-20261007/current-decision.json),
[import validation](ilya-20261007/import-validation.json) and package HOLD/PENDING
reports remain historical. Final later human records above reconcile those
states; no earlier approval is invented. Original_result objects/frozen
contracts/source/runtime snapshots and import material bytes are unchanged.
Local FAIL_ENVIRONMENT remains separate from full successful reviewed-head CI.
