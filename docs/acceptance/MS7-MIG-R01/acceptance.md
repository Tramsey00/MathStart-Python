# MS7-MIG-R01: accepted snapshot and post-merge handoff

**Snapshot accepted and merged; MIG_BASE_SHA = 60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7.**
R01 baseline/ADR and independent Task Approvals are accepted for the merged snapshot.
The new post-merge record amendment awaits task PR review/intake into integration;
its containing HEAD is not automatically approved. No later task is started.

Canonical application source remains `8c11edadc8debc81432d1db1145feac504f09061`.
Snapshot PR46 merged accepted head `e510744fcd87a22956aa71d5e22f20235e2af1c1` on
08.10.2026 01:47:59 Europe/Moscow, resulting commit `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`.
PR CI37696561717 and resulting-main CI37698445057 SUCCESS; resulting tree
matches the tested merge-ref. [Post-merge provenance](post-merge-provenance-20261008.json).

Owner Ruslan explicitly reports receiving Ilya and Vladimir's confirmation of
the e510744 documentation update in their chat: “Да, они всё подтвердили в нашем чате”.
This is an owner report, not a fabricated public reviewer comment or API review.
Original GitHub approvals retain their daf4e603 SHA and timestamps.

| Human record | Person / timestamp Europe/Moscow | Exact head / decision |
| --- | --- | --- |
| [Baseline+ADR and independent Task Approval](https://github.com/Tramsey00/MathStart-Python/pull/46#issuecomment-6047568271) | 13baybars;08.10.2026 00:51:20 | daf4e603…; APPROVED in UI/content/visual/frontend consumer scope |
| [Owner baseline+ADR / D01–D09](https://github.com/Tramsey00/MathStart-Python/pull/46#issuecomment-6047773231) | Tramsey00;08.10.2026 01:05:10 | daf4e603…; APPROVED as owner, not independent self-approval |
| [Baseline+ADR and independent Task Approval](https://github.com/Tramsey00/MathStart-Python/pull/46#pullrequestreview-5449019477) | VladimirFrolov777;08.10.2026 01:13:03 | API state APPROVED,commit_id=daf4e603…; architecture/backend/API/PostgreSQL/data ownership scope |

The three original human records refer to
`daf4e6038761f8d1bf1c60f0976473d987cce230`.
[Final human receipt](final-human-acceptance-20261008.json) remains byte-exact
pre-merge history. Owner-reported e510744 confirmation and actual merge are
separate facts in [post-merge provenance](post-merge-provenance-20261008.json).

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

## Post-merge result and remaining records workflow

MIG-G0 baseline/ADR conditions accepted for the actual merged snapshot.
D01–D09 decisions and two independent Task Approvals retained; snapshot source
unchanged. [Integration branch](https://github.com/Tramsey00/MathStart-Python/tree/ms7-mig-react-fastapi)
was absent and created exactly at `60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`; no later main commit used.
R01 task branch `ms7-mig-r01-baseline` created from this integration input in
a separate worktree for records only. Task PR → integration uses Refs #28.

R01 status: **ACCEPTED_SNAPSHOT / POST_MERGE_RECORDS_REVIEW_PENDING**.
Core accepted snapshot and branch setup are finished. The active plan remains
active solely until this post-merge record amendment is reviewed and accepted
into integration. No automatic reviewer approval for the new containing HEAD.
No direct push to main, task/integration merge or Issue closure by this agent.
All18 migration Issues verified OPEN; final closure belongs to §10 final
integration→main workflow. [R02 input handoff](R02-input-handoff.md) records
inputs only and is not permission or evidence of R02/I01 implementation.

F01–F04 **MANDATORY / ASSIGNED13baybars / NOT IMPLEMENTED**:
correct no later than I03#42; verify I05#44; R02#29 records parity exceptions.
F04 must be readable at ordinary scale, no clipping/overlap; enlargement alone
insufficient. Criteria and evidence remain unchanged.
Vladimir independent F04 review **NOT GIVEN / SEPARATE AGREEMENT REQUIRED**;
not a new blocking R01 gate and no consent inferred.

R01 planned07.10, actual human acceptance/merge08.10 retained. Remaining target
dates including MIG-G4 13.10.2026 23:59 Europe/Moscow unchanged; checks/scope
not reduced. Staging/disposable delivery accepted; production needs its own decision.

## Historical acceptance snapshots

[Acceptance at reviewed daf4e603](acceptance-at-daf4e603.md) is preserved as
exact Git bytes and retains its original PENDING/partial wording.
[Earlier scoped D02/D03 receipt](ilya-20261007/current-decision.json),
[import validation](ilya-20261007/import-validation.json) and package HOLD/PENDING
reports remain historical. Final later human records above reconcile those
states; no earlier approval is invented. Original_result objects/frozen
contracts/source/runtime snapshots and import material bytes are unchanged.
Local FAIL_ENVIRONMENT remains separate from full successful reviewed-head CI.

[Exact pre-merge e510744 acceptance](acceptance-at-e510744.md) and
[pre-merge snapshot-review](snapshot-review-at-e510744.json) preserve their PENDING wording.

Current post-merge record amendment is [draft PR47](https://github.com/Tramsey00/MathStart-Python/pull/47) → integration, Refs #28. Review its exact live HEAD; original approvals and owner-reported e510744 confirmation do not automatically approve this amendment.
