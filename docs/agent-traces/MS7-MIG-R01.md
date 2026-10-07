# TRACE MS7-MIG-R01: source snapshot, proposed platform decision and ownership

- Date: 2026-10-07, Europe/Moscow
- Owner: Руслан / Tramsey00; agent surface: Codex desktop
- Issue: https://github.com/Tramsey00/MathStart-Python/issues/28
- Spec: [exact canonical migration input](../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md)
- Plan: [active R01 plan](../exec-plans/active/MS7-MIG-R01.md)
- ADR: [ADR-0006 Proposed](../adr/ADR-0006-react-fastapi-migration.md)
- Snapshot branch: `ms7-mig-baseline` → main; candidate head/CI/merge-ref in external snapshot PR
- Human review: **Pending; R01 INCOMPLETE; MIG-G0 PENDING; MIG_BASE_SHA=PENDING**

## 1. Authorized task and inputs

Prepare only R01 audit, baseline manifests, platform ADR, plan, 18 organizational
Issues/ownership/dependencies, verified unchanged Django snapshot and draft PR.
Preserve original checkout, recovery trace, output/tmp. Registering the other
17 tasks does not authorize executing them. No downstream agent or task was
started. User authorization is not Vladimir/Ilya approval.

Read AGENTS→PRODUCT→ARCHITECTURE; ADR0001 and relevant ADR0002–0005;
README/docs/architecture; verification skill; relevant contracts, current and
historical plans/acceptance/traces; actual settings/routes/models/migrations/
publication/admin/tests/Harness/CI. Read entire attached migration input,
especially §§2–11/R01/§17; later cards only for registration/ownership/calendar.
Original Desktop Markdown was copied without edits; [provenance and SHA256](../../specs/migration/README.md).

## 2. Observable initial state

Fresh `git fetch origin --prune`; original local main and live remote main both
`8c11edadc8debc81432d1db1145feac504f09061`, ahead/behind 0/0. Original staged/
unstaged clean; only untracked recovery trace, output/, tmp/. PR27 already
merged; its fixes were not replayed. Git preservation is separate from visual
approval; PR27 reviews/comments were empty. Input main CI run 37595359404 and
PR27 run 37594222581 successful, but those do not establish new candidate CI.

Fresh remote input created a separate worktree with
`git worktree add -b ms7-mig-baseline C:/Projects/MathStart-Python/tmp/ms7-mig-r01/snapshot origin/main`.
No integration/task branch exists until accepted resulting MIG_BASE_SHA.
Remote account/I03 and grades code/migrations are present in input. Numbers
ADR0001–0005 occupied locally/remotely; next free ADR0006 remains Proposed.

## 3. Artifacts and factual audit

[Records index](../acceptance/MS7-MIG-R01/README.md) links source/runtime/delta/
admin/route/model/command/test/Issue/evidence manifests and checks. Source:
1026 tracked Git blobs with exact path/size/SHA256/commit, including 263 lesson
JSON, 97 lesson CSS, 7 lesson JS, 16 site JSON and 13 templates. Original and
fresh checkout hashes are distinct because Git line-ending conversion is
recorded. Five existing root files change narrowly; all other input code,
contracts, manifest pins and historical ADR/proofs remain exact source bytes.

Unchanged local recovery trace SHA256
`a09b34978f8fd8595b0b064d263b8dce15f4e9d0e545d26ca4d134e866d13cd1`
included as evidence. Original private preservation manifest covers 18,568
output/tmp files; bulk QA/runtime files excluded from snapshot. On-disk old
output references audited individually; missing entries are not presumed to exist.

Working PostgreSQL was examined only using verified
`BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY`, isolation/read-only SHOW,
schema/aggregate SELECTs and ROLLBACK. No migrate/bootstrap/publish/stamp/write.
22 migrations applied, including content0002/users0001/users0002. Aggregates:
6 grades,12 subjects,63 sections,281 pages (279 published),263 publications,
29 media,282 redirects; user/profile/session/receipt aggregates zero. No PII,
working secrets, session keys or DB dump recorded. 263 topic renderer/runtime/
publication digests agree; 13 structural HTML LF/CRLF differences and two
retired unpublished records retained for human byte/scope decision.

All nine admin registrations explicitly inventoried: seven source-managed
Content registrations view-only, User/Group full current CRUD/password/history/
delete-selected/permissions behavior. Permission is not independently registered.
No unknown staff operation silently replaced with CLI. Planned OpenAPI/domain
reference contracts remain distinct from implemented routes/runtime persistence.

## 4. GitHub and §17 evidence

Live connector/API audited branches, main SHA, relevant historical PR heads,
merges, reviews/comments, CI, ADRs and collaborator permissions. No gh assumed.
All 18 canonical IDs absent before registration; Issues #28–45 created once,
exact card scope/dependencies/checks/§17/calendar/approvers transferred; actual
assignment returned and independently fetched. [Issue map](../acceptance/MS7-MIG-R01/issue-branch-owner-map.json)
contains real URLs and acyclic resolved dependencies, future reserved isolation
paths only. R#28–33 Руслан, V#34–39 Владимир, I#40–45 Илья. All remain OPEN;
later17 remain PLANNED, no environment or implementation created for them.

[Old-to-new index](../acceptance/MS7-MIG-R01/old-to-new-evidence.json) retains
original_result/platform_disposition/migration_follow_up/target_evidence/current_status.
Historical R01 PR2/Issue1 merge/closure and repository acceptance preserved.
R02A PR15/Issue16 and R03A PR20/Issue18 CI/merge/closure are real, but explicit
original Vladimir approval not located in searched reviews/comments/repository
records; pending, no retrospective signature. Grades PR24 actual Ilya review
and Ruslan 06.10 Task Approval/migration review comment located and linked.
I03 PR26 approvals/security review and CI located. Task Approval, green CI,
merge, closed Issue and Global Gate remain separate fields/facts.

## 5. Changed files and commands

Added exact specs/migration input/provenance, ADR0006, active plan, this trace,
unchanged recovery trace and docs/acceptance/MS7-MIG-R01 manifests/docs/task
audit utilities/selected sanitized logs. Narrow current-status links added to
AGENTS/PRODUCT/ARCHITECTURE/README. `.gitattributes` pins exact external spec
bytes. No deletion, source lesson/application/dependency/migration/CI/Harness
change. No accepted historical document rewritten as target-platform proof.

Important commands: git fetch/worktree; read-only audit; existing version/pip
check; disposable PostgreSQL fresh-install smoke; unchanged verify_repo 8/8;
R02A/R03A/I02 pure suites; actual HTTP smoke; original preservation/source/
frozen pin/doc-link/secret audit; candidate git diff --check; explicit staged
allowlist commit/push and draft PR. [Verification matrix and exact logs](../acceptance/MS7-MIG-R01/verification.md)
record interpreters, commands and exits. Snapshot PR/head record contains exact
commit, tested merge-ref and current CI, avoiding a containing-commit self-pin.

## 6. Incidents and corrections

Sandbox-restricted initial Docker/PostgreSQL attempts were rerun with authorized
access; working audit stayed read-only. Incorrect Cyrillic transport decoding
in first Issue repaired in place; final18 exact bodies/titles checked. HTTP QA
Unicode URL error corrected via iri_to_uri. Intermediate /glavnaya/ expected
301 error traced to omitted existing published slug route; source middleware
only redirects 404. Explicit route precedence preserved, final572 checks pass.
No application test skipped/weakened, no source behavior changed for green.
Initial document audit reported its own output missing before first creation;
the task utility now establishes that generated path before checking links.
Original preservation and frozen/source checks passed in that first execution.
Default staged whitespace check initially rejected exact imported CRLF input
and captured Windows stdout. Exported logs normalize CR only; private raw logs
remain unchanged with raw/export hashes. Final staged check explicitly uses
cr-at-eol while retaining blank-at-eol/blank-at-eof/space-before-tab validation.
It exits 0; immutable specification bytes and content checks remain intact.

## 7. Verification and reviewable decisions

Python3.12.10/Django5.2.16/PG16.15. Full verification exit0,8/8; Django107,
R0318,Harness73; extra R02A30/R03A41/I027 pass; fresh22 migrations/bootstrap
twice/static/content pass. HTTP279 canonical+282 rules+11services=572 pass.
Source/preservation/link/safety output: [validation](../acceptance/MS7-MIG-R01/validation.json).
Target runtime/tests/CI NOT RUN/NOT CONFIGURED; no live LLM or deployment.

[Acceptance decisions D01–D09](../acceptance/MS7-MIG-R01/acceptance.md) cover
exact source/local delta and PR27 visual acceptance, runtime byte differences,
platform/SSG/admin/auth/DDL/SQLite scope, R02A/R03A missing original approval,
calendar and hosting boundary. Required three separate baseline/ADR records
plus independent R01 Task Approvals by Vladimir/Ilya are intentionally unsigned.
Main protection/rulesets were absent during audit; spec review gates still apply.

## 8. Final status and stop boundary

**INCOMPLETE, human acceptance PENDING.** Concrete candidate snapshot artifacts
are prepared for review. Current candidate checks and draft PR are required;
resulting MIG_BASE_SHA, integration/task branch creation, Accepted ADR revision,
completed-plan move and MIG-G0 require actual independent reviews and authorized
human merge. No self-merge or downstream work. Preserve all historical proofs
and original runtime. Harness unchanged; R01 audit utilities are scoped records,
not a platform verification rewrite.
