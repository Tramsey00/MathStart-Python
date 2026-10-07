# ADR-0006: Proposed React / FastAPI platform migration

- Status: **Proposed — MIG-G0 PENDING**
- Date: 2026-10-07, Europe/Moscow
- Owner: Руслан / Tramsey00
- Independent R01 reviewers / approvers: Владимир / VladimirFrolov777 and Илья / 13baybars
- Gate: separate baseline/ADR decisions from all three people; no signature is supplied by this ADR
- Issue: [MS7-MIG-R01 #28](https://github.com/Tramsey00/MathStart-Python/issues/28)
- Specification: [exact migration addendum v1.1](../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md)
- Plan: [active R01](../exec-plans/active/MS7-MIG-R01.md)
- Inventory / decisions: [baseline inventory](../acceptance/MS7-MIG-R01/inventory.md), [human acceptance](../acceptance/MS7-MIG-R01/acceptance.md)
- Supersession: **none yet**. On accepted MIG-G0, supersede only ADR-0001's backend/frontend/ORM/migration platform selection. Preserve its history and domain/evidence invariants, ADR-0002/0003 and frozen contracts.

## Context and authority

The running version is Django 5.2.16 / DRF 3.18.1 with Django Templates,
PostgreSQL and explicit SQLite compatibility. The migration addendum is a
proposed platform replacement program, not evidence of a working target runtime.
R01 is limited to snapshot, inventory, decisions, records and Issue registration.
No React/FastAPI scaffold, target dependency, Alembic migration or new CI is
introduced. ADR-0006 was unused in both local and live remote ADR listings
(0001–0005) on 2026-10-07; merged/proposed 0004/0005 approvals are separately
reconciled in the evidence index.

Fresh remote main and local main equal
`8c11edadc8debc81432d1db1145feac504f09061`. PR27 already contains the earlier
lesson/catalogue fixes. Preserve that input rather than replay its branch.
Source and sanitized runtime manifests show 263 topics, 97 lesson CSS and seven
lesson JS files; source/runtime digests are distinct. Working DB has 281 pages,
279 published and two retained retired pages; fresh source installation has
279 pages. Thirteen structural body payloads differ only in CRLF/LF, with exact
hashes and scope decisions recorded. Runtime is never overwritten to hide drift.

## Proposed decision

Current R01 evidence clarification (2026-10-08): the working DB counts and
13 LF/CRLF-only variants above belong to Ruslan's original audit. Ilya's
working DB has substantive drift in five specifically checked payloads;
his separate disposable 8c11edad baseline has exact source/published parity.
See the [three-source index](../acceptance/MS7-MIG-R01/ilya-20261007/README.md).
His D02/D03 UI/content scoped decision and the owner's D02 source-freeze choice
retain F01–F04 with mandatory follow-up; they do not accept this proposed ADR,
collective MIG-G0 or final R01 Task Approval. No runtime/source repair occurs.

Retain one modular Python monolith and one primary PostgreSQL 16+ database.
React + TypeScript provides existing UI with existing CSS/tokens, using Vite
and React Router framework mode. FastAPI + Pydantic is the single serving
backend after cutover, using SQLAlchemy 2, psycopg, Alembic and Uvicorn. Use
short synchronous transactions and a Session per unit of work; do not share
Sessions between threads/tasks. Compatible pinned locks are future V01/I01
deliverables. No Redis, Celery, microservices, global CSS reset, new UI library,
permanent Node SSR server or new educational domain is required by this change.

Domain boundaries remain Content (including topic mappings) → Knowledge;
Knowledge does not depend on Content. Only Progress owns long-term projection
changes through validated evidence. Assessment owns attempts/completion facts;
Progress owns its mirror/replay. Four modes, typed ordered steps, stable skill
codes, DAG edge direction, raw/normalized separation, deterministic validation,
answer secrecy, recorded hint/reveal and full-reveal independence restrictions
remain. Wrong final answers do not identify a misconception; unsupported input
is not an error diagnosis. LLM schema/confidence gates and isolated provider SDKs
remain. Content bootstrap never overwrites runtime evidence. Existing references
do not establish Knowledge/Assessment/Progress persistence or live AI runtime.

### Public HTML and publication freshness

Generate public HTML from the complete published URL manifest, including
metadata, canonical links, reviewed authored HTML/math/SVG and asset hashes.
Preserve source paths, slugs, redirects, sitemap, robots and unknown/unpublished
404 behavior; no wildcard SPA 200. Account/staff are private, with no-store and
no personal SSG export. Node is a build/publish tool, not a required serving
process. Lesson scripts need named mount/dispose or tested full-document
navigation; this ADR does not implement those adapters.

Publish/unpublish stages assets/render in an operation-specific root, records
an operation journal, commits the DB operation and explicitly activates a
matching release manifest. DB and files/SSG are separate resources. Failure
must have a nonzero/safe outcome and resumable recovery; catalogue/sitemap and
HTML must reflect the active release. V04/I02/I03 own the implementation and
failure tests after accepted R02 contracts. If freshness cannot be proven,
change the ADR explicitly before accepting deployment.

### Authentication, security and staff scope

Keep one HTTPS origin, opaque PostgreSQL-backed sessions, HttpOnly/Secure/
SameSite cookies, login rotation, logout/expiry/revocation, CSRF bootstrap/header
and Origin/Host checks. No browser JWT/localStorage credentials. Preserve
encoded passwords and validators through a compatible independent adapter and
synthetic vectors; the working DB has zero users, which does not waive compatibility
tests for deployed upgrade profiles. Unsupported algorithms block cutover.
Propose one explicit re-login at session transition without resetting passwords;
all three gate participants must accept it. Retain receipts/identities,
uniqueness, ≥7-day replay retention and secure anonymous-scope bridge, including
lost acknowledgement. Do not clear receipts to avoid compatibility work.
Preserve shared worker-safe login rate and a reviewed proxy IP trust policy.

Keep **every operation in the admin inventory**: seven Content models remain
view-only list/detail/search/filter; User and Group administration includes
creation, edits, active/staff/superuser flags, password change, groups/direct
permission assignments, group permission editing, history and guarded deletion
including delete-selected. Existing PROTECT restrictions apply. Permission has
no standalone registered admin CRUD; permissions are operated through User/
Group selectors. StudentProfile/IdentityReceipt/LoginWindow are not registered.
No operation is silently replaced by CLI or excluded because the working DB is
empty. A deletion or privilege operation may be excluded only by an explicit
MIG-G0 scope decision. V02/V03 own staff APIs/authorization/audit; I02/I04 own
minimal equivalent UI. Content stays source-managed; this is not a new CMS.

Владимир owns backend security/schema/hash/session/receipt/staff authorization;
Илья owns safe UI/forms/password cleanup and private export boundaries; Руслан
owns contract/security audit, CI and evidence integration. A button is not
authorization; preserve server-side role/permission checks and prevent secret
disclosure. Production writer/credential/deployment decisions remain separate.

### DDL, write ownership and SQLite

Before cutover, Django migrations exclusively own current auth/content/users/
Django tables and Django services/CLI/admin exclusively own their live writes.
Future FastAPI shadow reads production only; all test writes use disposable data.
Владимир alone owns the writable Alembic chain, schema mapping and reviewed
fresh/upgrade profiles. Preserve IDs, UUIDs, PK/FK/UNIQUE/CHECK/index/sequence,
defaults/timezones, Grade epoch and historical migrations; Django on_delete
must not be assumed equal to SQL FK behavior. Alembic stamp is forbidden until
schema equivalence/rehearsal and human review. Never run Django and Alembic DDL
against the same owned tables. At domain cutover, drain writers and revoke
legacy writes before activating target routes/CLI/admin. Archive unused history
tables; dropping them is not required. R01 changes no schema or DDL owner in
the running application.

**Explicit compatibility proposal:** PostgreSQL is mandatory for target
acceptance and operational use; retain opt-in SQLite compatibility for local
non-concurrency development as §15 V01 requires, with no fallback on PG errors.
SQLite cannot prove PostgreSQL locking/migration/auth races. This is a proposed
decision, pending MIG-G0; do not remove current SQLite support in R01.

### Snapshot, integration and rollback

Create `ms7-mig-baseline` from fresh remote main in an isolated worktree. Its
only local intake is the unchanged recovery trace; R01 adds exact input,
manifests, inventory, proposed ADR/plan and review records. Snapshot draft PR
targets main. Source preservation in Git is distinct from visual/content
approval. Independent reviews, current-head checks and accepted snapshot merge
are required before `MIG_BASE_SHA` is assigned. Candidate SHA is tracked in PR/
head records; **MIG_BASE_SHA = PENDING**.

After human-accepted snapshot merge, Руслан creates `ms7-mig-react-fastapi`
from the resulting MIG_BASE_SHA, then `ms7-mig-r01-baseline` from the accepted
integration input. R01 documents may be prepared on the snapshot beforehand;
that branch is not an accepted integration baseline. Feature branches, runtime
roots, ports and DB names are reserved in the ownership map, not created by
registration. Root docs/verify/CI owner Руслан; backend/DDL owner Владимир;
frontend/routes/lock owner Илья. Reviewed main intake requires repeated checks.
Task PR → integration uses Refs #Issue; Issues remain open until the accepted
final integration → main workflow. Never self-merge or force-push.

R01 rollback closes/abandons the proposed docs/snapshot without changing the
original checkout or DB. Future cutover rollback needs compatible app/assets,
DB/media backup, writer switch, receipt/session reconciliation and measured
restore. After target writes, prefer forward repair when legacy cannot safely
read them; do not promise a destructive DB restore without reconciliation and
human decision. Public deployment requires a separate explicit approval and
accepted runbook; host is unresolved, proposed staging-only delivery boundary
must be accepted separately.

## Alternatives and consequences

Keeping the accepted Django platform avoids this migration effort but does
not implement the requested migration addendum. A dual live writer platform
risks duplicate evidence and competing DDL and is rejected. A compulsory SSR
service or CMS broadens operational/UI scope and is rejected by the addendum.
The proposed port preserves current behavior and modular ownership at the cost
of verified content/admin/auth/publication adapters, cutover rehearsal and new
target evidence. A successful build alone will not establish parity.

## Verification, human gate and status history

R01 runs the unchanged Django baseline on disposable PostgreSQL, fresh migrate/
bootstrap/static smoke, pure/Harness/UI suites, source/frozen hashes, route/admin/
schema inventory, links, delta/secrets review and current snapshot PR CI. See
the [trace](../agent-traces/MS7-MIG-R01.md) for commands and results. Future
target tests belong to their registered tasks. No historical proof is rewritten.

MIG-G0 requires separate records by Руслан, Владимир and Илья for exact
baseline and this ADR. R01 needs independent Владимир and Илья Task Approval.
R02A/R03A independent contract acceptance reconciliation verified on 07.10.2026; D08 CLOSED with live URLs in current R01 evidence. Original snapshots stay intact. Grades historical approvals also have live URLs. The request to execute R01 is not approval by others.

- 2026-10-07: Proposed. No platform supersession, migration implementation,
  accepted MIG_BASE_SHA, production cutover or completed gate is claimed.
