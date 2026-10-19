# MS7-MIG-R02 B01–B07/N01 response for independent re-review

PROPOSED revision1.0.1; no independent approval is inferred.
[Ilya CHANGES_REQUESTED](https://github.com/Tramsey00/MathStart-Python/pull/48#pullrequestreview-5461343942)
reviewed HEAD9cc9829a0b71cb73c4fe40d002e438572f381b48. Complete review/timeline
snapshot: [review intake](review-intake-20261008.json). At intake there was one
review, zero inline threads, no other reviewer comments. Recheck live PR at
publication. Accepted input c133f920fc14ab18a463e039f8e480e064ced81c and
MIG_BASE_SHA60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7 stay unchanged.

All rows also update [parity matrix](../../../specs/migration/r02-v1/parity-matrix-v1.json)
and [route map](../../../specs/migration/r02-v1/implemented-routes-v1.json).
Schema/OAS links below are separate proposed addenda; frozen canonical OAS is
untouched. Tests are [review suite](../../../tests/test_migration_r02_review.py).

| Finding | Change / files | Independent verification | Remaining question |
| --- | --- | --- | --- |
| B01 | [staff](../../../specs/migration/r02-v1/staff-v1.md), [OAS](../../../specs/migration/r02-v1/delivery-staff-v1.openapi.json): User-create availability/POST requires active staff AND add_user AND change_user. Group-create keeps add_group. | Original UserAdmin._add_view and parent _changeform_view reject add-only/change-only/neither; combined permission forwards to parent, AdminSite rejects inactive/nonstaff. Exact OAS gate checked. | No baseline/access-policy choice remains; independent re-review required. |
| B02 | [content](../../../specs/migration/r02-v1/content-v1.md), [build handoff](../../../specs/migration/r02-v1/public-build-contract-v1.json), [schema](../../../specs/migration/r02-v1/delivery-v1.schema.json): complete PublicBuildIndex plus every published Delivery file; frontend active-index/immutable-release mechanism; catalogue relations/order/grouping and q/grade/subject semantics. | Real read-only disposable index enumerates279 published pages/263 topics/1 home alias; exact published slug set compared with original lesson/page JSON sources. Export projection matches11 baseline catalogue queries; original catalogue_context validates Unicode casefold, strip, invalid filters and repeated-last QueryDict semantics. Negative duplicate/missing/foreign/private cases. | New static artifact format needs exact-head R02 approval; real target build/activation remains V04/I02/V05. No baseline behavior changed. |
| B03 | [staff](../../../specs/migration/r02-v1/staff-v1.md), [list policy](../../../specs/migration/r02-v1/staff-list-policy-v1.json), [OAS](../../../specs/migration/r02-v1/delivery-staff-v1.openapi.json), [schema](../../../specs/migration/r02-v1/delivery-v1.schema.json): filter__is_permanent is boolean; canonical URI true/false, native admin0/1 translates explicitly. | Both true/false schema positive cases and0/1/string/null negatives; original BooleanFieldListFilter builds matching permanent/temporary query predicates. | Wire adapter proposal requires re-review; no additional boolean meaning or rights change. |
| B04 | [staff](../../../specs/migration/r02-v1/staff-v1.md), [list policy](../../../specs/migration/r02-v1/staff-list-policy-v1.json), [OAS](../../../specs/migration/r02-v1/delivery-staff-v1.openapi.json), [schema](../../../specs/migration/r02-v1/delivery-v1.schema.json): sort=default or [-]field(,[-]field)*, nine allowlists, directions, native/default/relation ordering, deterministic unique/PK rule, NULL semantics, complete cursor binding. Group supports default only because __str__ isn't sortable. | Each allowlist/default/single direction checked against original ChangeList; mixed multi-sort and FK SQL-expression expansion checked independently. Unknown/empty/plus/duplicate/injected fields reject; binding mutations for actor/scope/resource/q/filters/sort/page_size reject. | Named wire/cursor contract needs exact-head review; actual target signer/keyset/concurrent edits remain V02/V03 tests. No newly sortable baseline column. |
| B05 | [staff](../../../specs/migration/r02-v1/staff-v1.md), [OAS](../../../specs/migration/r02-v1/delivery-staff-v1.openapi.json), [schema](../../../specs/migration/r02-v1/delivery-v1.schema.json): GET existing User {id}/group_choices under change_user returns group ID/name only, private/no-store. No group selector in baseline User-create form. General Group administration keeps existing gates. | Original UserAdmin M2M form queryset returns all groups ordered by name for change_user-only actor; same actor lacks all Group admin permissions. DTO rejects permissions; OAS narrow gate checked. | No access-policy choice remains. Missing User404 and real HTTP guard/no-write tests remain V03/I04 implementation obligations. |
| B06 | [content](../../../specs/migration/r02-v1/content-v1.md), [staff](../../../specs/migration/r02-v1/staff-v1.md), [OAS](../../../specs/migration/r02-v1/delivery-staff-v1.openapi.json), [schema](../../../specs/migration/r02-v1/delivery-v1.schema.json), [samples](../../../specs/migration/r02-v1/synthetic-review-exchanges-v1.json): private read-only page publication_state shows active/DB edition/pending/recovery, sampled revision, sanitized failure codes. Page view/change gate, no write/publish/resume capability. | Existing baseline directly serves DB ContentPage; no split active/pending layer exists. Six SYNTHETIC state samples validate precommit/committed/activation-failure/ACK-loss/unavailable paths; mismatched releases, false IN_SYNC, null recovery error and secret fields reject. OAS has GET only. | Proposed observable state needs reviewer acceptance; actual coherent sampling, read-only/no-store/auth and recovery races remain V04/V05/I02. Synthetic tests do not prove target runtime. |
| B07 | [content](../../../specs/migration/r02-v1/content-v1.md), [auth](../../../specs/migration/r02-v1/auth-v1.md), route family map: sitemap/robots ALL baseline methods, resolved-view CSRF before render/404, unresolved fallback after404 for all methods; distinct identity/grades/account precedence retained. |192 real requests with missing/valid CSRF/bad Origin, eight methods and12 paths, guarded PG READ ONLY and zero SQL writes. Positive/negative results asserted; HEAD body empty in observations. Both resolved and unresolved redirect paths recorded. | No behavior-change choice remains. Gateway/SSG implementation must preserve these cases in I02/V02/V05. |
| N01 | UI-01 baseline_reference points at real static/mathstart/js/ui/account.js. | Existing controller path and credential-clear/recovery symbols checked; all8 review rows exist. | None beyond independent re-review. |

Full [baseline observations](review-baseline-observations.json) and
[public index](review-baseline-public-index.json) are current isolated source
evidence. The source index contains catalogue/public metadata only; actual
ContentDelivery assets/bodies are future build outputs, not fabricated here.
The standalone combined suite has31 tests (20 existing +11 review); it is local
evidence, separate from unchanged baseline integration CI. Exact commands,
versions/log digests/results belong to [verification](verification.json).

F01–F04 and historical approvals/original_result/frozen pins remain unchanged.
13baybars fixes byI03, verifiesI05 at360/768/1440; F04 ordinary-scale readable
labels required. No UI/application/DDL/dependency/workflow/working DB changes.

Владимир: re-review combined create gate, form choices vs Group rights,
sort/cursor/NULL rules, per-family CSRF and observable snapshot coherence/privacy.
Илья: re-review complete index/page discovery/catalogue projection and filters,
all list sort parameters, narrow User-form selector, pending/recovery display,
all-method gateway responses and corrected controller reference.

Independent decisions at the new exact HEAD remain required. PR48 stays draft,
Issue29 open; no downstream task/merge/production action. V01/I01 await accepted
R02 CONTRACT and owner-recorded exact merged integration intake after checks.

## Protocol review continuation — 09.10.2026

PROPOSED revision1.0.2 responds to [Vladimir's full review5462501369](https://github.com/Tramsey00/MathStart-Python/pull/48#pullrequestreview-5462501369)
on6c1603b3ac55f3f0e8ef3b2bfb09298a42de5974. The [new live intake](review-intake-20261009.json)
contains both public reviews, complete timeline and zero inline threads. The user
reports Ilya confirmed B01–B07/N01 in scope; no newer public Ilya review was
observed, so no GitHub approval or acceptance is invented. Earlier tables/statuses
above are the previous review round; corrections remain and pass all31 prior tests.

| Blocker | Proposed decision and files | Checks / evidence | Remaining question |
| --- | --- | --- | --- |
| P1 durable publication ownership | [platform](../../../specs/migration/r02-v1/platform-v1.md) and [content](../../../specs/migration/r02-v1/content-v1.md): durable PostgreSQL pending slot owns the whole lifetime; monotone generation, lease-checked writes and same-operation CAS takeover; single authoritative DB active descriptor avoids a delayed filesystem pointer action. [Transition table](../../../specs/migration/r02-v1/publication-protocol-v1.json), [storage mapping](../../../specs/migration/r02-v1/protocol-storage-mapping-v1.json), closed [schema](../../../specs/migration/r02-v1/delivery-v1.schema.json), read-only [OAS](../../../specs/migration/r02-v1/delivery-staff-v1.openapi.json), [route](../../../specs/migration/r02-v1/implemented-routes-v1.json)/[parity](../../../specs/migration/r02-v1/parity-matrix-v1.json) and observable samples agree on ACTIVATING, committed facts, UNKNOWN, recovery and safe ownership. | [Protocol suite](../../../tests/test_migration_r02_protocols.py): both competing recovery orders, stale renew/commit/activate/complete/reconcile/cleanup, lease boundary, before/after activation ACK loss, pointer digest/operation mismatch, health failure, immutable key/plan and next-publication gate. Prior B06 schema/relational/secret/GET checks still pass. Model/synthetic only. | Exact-head approval of this proposed authority/activation representation; V01 DDL, V04 real PG/process/crash tests and V05 gateway visibility/cache proof remain. No baseline/access decision outside R02 is required; an incompatible storage implementation must present an explicit alternative, never silently weaken fencing. |
| P2 receipt bridge lifecycle | [auth](../../../specs/migration/r02-v1/auth-v1.md) explicit logout/switch/expiry/cutover/window transition table plus [machine lifecycle](../../../specs/migration/r02-v1/receipt-bridge-lifecycle-v1.json), private bridge schema and storage mapping. Logout/switch revoke bridge/ticket authority but retain receipt/facts; natural expiry/cutover detach with B/T/F owner proof, one accepted explicit login; current S is session+epoch-bound. Durable cutover checkpoint repeats read-only. No logout receipt replay/blind retry; unknown outcome GET reconciliation first. | Protocol model exercises all24 transition orders/repeats, expired/revoked/wrong-signature/ticket-only proof, different user/session, inactive owner/missing transfer, stale rebind epoch, same checkpoint after recovery, unknown/dual-writer checkpoint, immutable key/body and full lost-cookie replay. Existing baseline source assertions and full107 Django tests preserve logout200 completed:true/repeat401/user switch/replay semantics. No target cryptographic or race claim. | Exact-head lifecycle/proof review; V03 real populated migration, signing keys, sessions/rebind/revoke/cutover races remain. Deployment-specific key retention/lease/expiry values must be recorded by later owners; unprovable proof/key import blocks cutover. |

Local: verify_repo8/8 (Django107/R0318/Harness73), R02 standalone63,
unchanged R02A30/R03A41/I027, pip check and isolated PG version report PASS.
[Model evidence](protocol-model-evidence.json) and [verification](verification.json)
separate synthetic/model tests from real baseline checks and future target races.
Final containing HEAD/CI are external in PR48 to avoid a self-referential commit.
No app/UI/working DB/DDL/frozen/pin/historical approval modification, downstream
task, merge or Issue29 closure. Independent review remains the acceptance gate.
