# R01 / MIG-G0 human acceptance record

**Status: PENDING. MIG_BASE_SHA = PENDING. ADR-0006 Proposed. R01 INCOMPLETE.**

Owner: Руслан / Tramsey00. Independent R01 Task Approvers: Владимир /
VladimirFrolov777 and Илья / 13baybars. Snapshot branch `ms7-mig-baseline`
targets main; input `8c11edadc8debc81432d1db1145feac504f09061`. Exact candidate
head, tested merge-ref and latest CI are in the snapshot PR/head record. That
head is a candidate, not an accepted resulting migration baseline.

Review [ADR-0006](../../adr/ADR-0006-react-fastapi-migration.md),
[inventory](inventory.md), [source manifest](source-manifest.json),
[runtime manifest](runtime-data-manifest.json), [rendered comparison](rendered-runtime-digests.json),
[delta](local-delta.json), [Issue map](issue-branch-owner-map.json),
[old-to-new index](old-to-new-evidence.json), [verification](verification.md)
and [trace](../../agent-traces/MS7-MIG-R01.md). Historical acceptance and new
platform acceptance are separate facts. The user request authorizes execution;
it does not supply other participants' signatures or a baseline/ADR decision.

## Concrete decisions required before MIG-G0

| ID | Reviewable decision | Required people / current evidence |
| --- | --- | --- |
| D01 | Accept exact current source input plus unchanged local recovery evidence and R01 records; preserve remote I03/identity/grades and all authored lesson CSS/JS. No replay of PR27. | All three; source hashes/delta and current PR checks prepared; PENDING. |
| D02 | Accept PR27 visual/content fixes as migration baseline, or name specific files requiring later agreed correction. Git preservation/merge without reviews is not independent visual approval. | All three, especially Илья visual and Владимир independent review; PR27 reviews empty; PENDING. |
| D03 | Accept canonical Git source bytes plus recorded working-runtime byte differences: 13 structural body_html LF/CRLF variants, zero substantive normalized field differences; keep DB/runtime unchanged, retain two retired unpublished pages. | All three; exact/normalized/original comparisons in rendered JSON; PENDING. No automatic bootstrap repair. |
| D04 | Accept proposed platform ADR: minimal React/TS/Vite/Router SSG + FastAPI/SQLAlchemy/Alembic, public publish/unpublish freshness journal/activation, private no-store, modular-monolith and evidence invariants. | All three; ADR0006 Proposed; PENDING. |
| D05 | Accept complete staff/admin scope: seven Content view-only models, all current User/Group CRUD/password/role/direct/group permission/history/delete-selected operations and PROTECT; Permission has no independent registered CRUD. Any exclusion must name operation and approved scope change. | All three; nine registrations and exact fields/actions/permissions inventoried; PENDING. No CLI blanket substitute. |
| D06 | Accept one DDL owner Владимир and explicit legacy→target writer transfer; no shared-table Django/Alembic overlap/stamp without review; PostgreSQL required, opt-in SQLite local compatibility retained without fallback or PG acceptance claims. | All three; no current DDL or live writer change; PENDING. |
| D07 | Accept auth/session cutover proposal: one re-login, no password reset; compatible hash vectors, receipts/scope bridge/retention, roles/constraints and CSRF preserved; reviewed proxy/shared rate and security responsibilities. | All three; future implementation/tests delegated to registered tasks only; PENDING. |
| D08 | Reconcile original R02A/R03A contract acceptance at exact reviewed heads without backdating historical records. | **CLOSED 07.10.2026** — VladimirFrolov777 explicitly accepts [R02A head917cdc4](https://github.com/Tramsey00/MathStart-Python/pull/15#issuecomment-6042594492) and [R03A head908a9ae](https://github.com/Tramsey00/MathStart-Python/pull/20#issuecomment-6042793058); author/head/merge/CI verified live. Separate R01/MIG-G0 records remain PENDING. |
| D09 | Confirm calendar/capacity and unresolved hosting boundary: reproducible staging/disposable delivery required; public production host/deployment remains separately approved. Registration/reservations are not implementation authorization. | All three; Europe/Moscow dates in plan/spec; PENDING. |

Grades historical backend/migration acceptance is located in
[Руслан's actual 06.10 comment](https://github.com/Tramsey00/MathStart-Python/pull/24#issuecomment-6015016626)
and [Илья's consumer review](https://github.com/Tramsey00/MathStart-Python/pull/24#pullrequestreview-5406384114).
R01 records those statements; it does not author them retrospectively. No grades
approval remains fabricated/missing in this audit. Frozen manifests stay intact.

D08 closure is based on current independent acceptance reconciliation records by Владимир: 07.10.2026 at 19:49:02 and 20:06:07 Europe/Moscow. See [verified receipt](acceptance-reconciliation-20261007.json). Earlier absent-approval findings remain preserved in original snapshots; neither comment claims an earlier approval. R02A's non-blocking LF/CRLF documentation note remains recorded without changing pinned artifacts. **Only D08 is closed; D01–D07/D09 and all R01/MIG-G0 records below remain pending.**

## Separate human records — intentionally unsigned

| Gate record | Person | Exact reviewed candidate SHA / ADR | Decision / timestamp / URL |
| --- | --- | --- | --- |
| MIG-G0 baseline + ADR | Руслан / Tramsey00 | PENDING | PENDING — no new decision recorded |
| MIG-G0 baseline + ADR | Владимир / VladimirFrolov777 | PENDING | PENDING — no signature supplied |
| MIG-G0 baseline + ADR | Илья / 13baybars | PENDING | PENDING — no signature supplied |
| Independent R01 Task Approval (architecture/contracts/backend) | Владимир / VladimirFrolov777 | PENDING | PENDING |
| Independent R01 Task Approval (UI/content/visual) | Илья / 13baybars | PENDING | PENDING |
| Snapshot approval/checks/merge | Independent reviewers + authorized human merger | Candidate in PR; resulting main PENDING | PENDING |

Each person may use this record format in their own PR comment/review; it is a
template, not a decision:

```text
Person/login:
Gate: MIG-G0 baseline+ADR and/or independent MS7-MIG-R01 Task Approval
Candidate full SHA:
ADR-0006 file/revision reviewed:
Inventory/manifest/CI run and tested merge-ref reviewed:
Decisions D01–D09 accepted / specific changes requested:
Review scope and positive/negative evidence:
Outstanding blockers:
Decision: APPROVED / CHANGES_REQUESTED / PENDING
Timestamp (Europe/Moscow) and own review/comment URL:
```

Self-check/agent review is not independent human acceptance. A merge must not
bypass required review even though main currently has no enforced protection.
After accepted snapshot merge, record resulting MIG_BASE_SHA, then create
integration/task branches; that dependent step is outside this preparation's
accepted state. Keep 18 Issues open; final migration workflow owns their closure.
Keep the active plan in active until all required human evidence is present.
