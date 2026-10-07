# TRACE MS7-MIG-R01: source snapshot, proposed platform decision and ownership

- Date: 2026-10-07, Europe/Moscow
- Owner: Руслан / Tramsey00; agent surface: Codex desktop
- Issue: https://github.com/Tramsey00/MathStart-Python/issues/28
- Spec: [exact canonical migration input](../../specs/migration/MathStart_Migration_React_FastAPI_2026-10-07_v1.1.md)
- Plan: [active R01 plan](../exec-plans/active/MS7-MIG-R01.md)
- ADR: [ADR-0006 Proposed](../adr/ADR-0006-react-fastapi-migration.md)
- Snapshot branch: `ms7-mig-baseline` → main; candidate head/CI/merge-ref in external snapshot PR
- Draft snapshot PR: https://github.com/Tramsey00/MathStart-Python/pull/46 (attached to this Codex chat)
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
recorded. Three existing root files change narrowly; all other input code,
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
Initial audit snapshot: R02A PR15/Issue16 and R03A PR20/Issue18 CI/merge/closure were real, but explicit Vladimir approval was not located then. That original finding is preserved. Current 07.10.2026 independent reconciliation comments are now verified; D08 CLOSED (see follow-up below), without backdating. Grades PR24 actual Ilya review
and Ruslan 06.10 Task Approval/migration review comment located and linked.
I03 PR26 approvals/security review and CI located. Task Approval, green CI,
merge, closed Issue and Global Gate remain separate fields/facts.

## 5. Changed files and commands

Added exact specs/migration input/provenance, ADR0006, active plan, this trace,
unchanged recovery trace and docs/acceptance/MS7-MIG-R01 manifests/docs/task
audit utilities/selected sanitized logs. Narrow current-status links added to
AGENTS/README. PRODUCT/ARCHITECTURE restored exactly after initial CI exposed their frozen Harness pins. `.gitattributes` pins exact external spec
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
platform/SSG/admin/auth/DDL/SQLite scope; D08 R02A/R03A reconciliation CLOSED by verified 07.10.2026 participant records, while other decisions remain pending,
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

## 9. Snapshot publication receipt

Initial committed/pushed candidate `31d629f2d90c1b53b264edd2f1814fb09f66cc68`;
draft PR46 base `8c11edadc8debc81432d1db1145feac504f09061`; initial
merge-ref candidate `fab0ea1cb3bc8b6970a7b86867e1068d0697465b` exists, but
no initial candidate workflow/check runs were present in live searches.
The first job logs later confirmed that exact merge-ref was tested and failed due to two hash-pinned document edits; no source/application failure. 44 committed record blobs and
exact input/recovery Git bytes validated PASS. See
[snapshot receipt](../acceptance/MS7-MIG-R01/snapshot-review.json).
R01 Issue28 now links PR46; later17 Issues unchanged and open. Subsequent
record-only commit is verified against the same frozen input; exact current
head/merge-ref/CI is published externally in PR46 body, not self-embedded.

Initial snapshot CI run37602901512 failed at Harness (7/8 checks PASS,73 tests/1 error): R01 status paragraphs changed historically pinned PRODUCT/ARCHITECTURE. Both restored to exact input Git bytes; historical MS6-R04 pins and tests untouched. Source validator tightened to only three existing root changes. A narrow non-escalated Harness rerun encountered Windows sandbox temp cleanup permissions (environment failure); isolated authorized rerun/full baseline recorded separately. See ci-first-head.json and current PR head checks.

Correction verification: authorized isolated Harness exit0/73tests; full verify_repo exit0/8of8,Django107/R0318/Harness73. Sanitized corrected logs/commands committed under R01 evidence. Final preservation/source/frozen checks pass with1023 input files exact, only three scoped root changes. Exact second/final head and tested merge-ref CI recorded externally in PR46 after additive push; first failure retained, no pins/tests rewritten.

## 10. D08 acceptance reconciliation follow-up — 2026-10-07

User supplied two actual VladimirFrolov777 acceptance comment URLs. Live connector/API verified author, creation/update times, explicit acceptance, original PR head/merge SHA and successful historical CI. R02A: [comment6042594492](https://github.com/Tramsey00/MathStart-Python/pull/15#issuecomment-6042594492), head917cdc4ef72b6996254809b77d7aa5b0f251831e, merge428ece726918f635549fc7dd8fdd352f799c3308,19:49:02 Europe/Moscow. R03A: [comment6042793058](https://github.com/Tramsey00/MathStart-Python/pull/20#issuecomment-6042793058), head908a9aed6ca2f1319dabbf094e2432427d86a36d, mergefa0d87033113a30abc6e9de2acc174b01e98d9db,20:06:07 Europe/Moscow.

D08 CLOSED on these current independent records. [Reconciliation receipt](../acceptance/MS7-MIG-R01/acceptance-reconciliation-20261007.json) pins exact decoded comment-body hashes and separates participant-reported tests from agent metadata verification. The old-to-new index keeps original_result objects unchanged, adds current reconciliation and keeps new R01/platform approval PENDING. Initial github-audit/source/runtime snapshots, historical traces, schemas, fixtures and frozen pins remain unchanged. R02A non-blocking LF/CRLF documentation discrepancy is recorded; no normalization performed.

Updated current R01 acceptance/index/trace, related proposed ADR status paragraph/active plan/index/receipt/verification and regenerated record/validation manifests. Only R01 records; original checkout/DB untouched. Same branch ms7-mig-baseline and draft PR46; no new PR, merge, Issue closure or later task execution. Pre-follow-up candidate2af105c515c4e296613834118c15609efcdb6710 and remote/main8c11edadc8debc81432d1db1145feac504f09061 verified. New head and actual tested merge-ref/CI are externally recorded in PR46; earlier green run does not prove this update. R01 INCOMPLETE; MIG-G0/MIG_BASE_SHA PENDING; D01–D07/D09 and independent R01/baseline/ADR decisions remain separate.

## 11. Ilya evidence import — 2026-10-08 Europe/Moscow

Only R01 follow-up authorized. Original checkout main and remote/main8c11edadc8debc81432d1db1145feac504f09061;
existing worktree ms7-mig-baseline local/remote43b4fa10aec2af589c51857d037e973215557255
clean before changes; draft PR46 open/unmerged. Fetch verified current refs.
ZIP input C:/Users/Tramsey/Desktop/r01-evidence-8c11edad.zip SHA256
63d0bca0618dee6016669e07706612edd9f1ef50be26de4c238eb043935e9313 matches.
Path safety/symlink/encryption/size/ratio/CRC checked before publication;
231 manifest payload hashes and228 export provenance entries verified. Import
232 files/31,057,740 bytes unchanged;190 JPEG decoded, no EXIF/extra metadata.
Text/JSON review and credential scans no findings. 127 relative report/screenshot
links resolved; atlas + four finding screenshots inspected. See [import receipt](../acceptance/MS7-MIG-R01/ilya-20261007/import-receipt.json).
First image validation with project interpreter exited1 because Pillow is not
installed there; no dependency installed. Existing bundled Python/Pillow retry
and full package validation/import exited0.

Live comment6046690988 author13baybars, created/updated2026-10-07T20:56:12Z
(23:56:12 Moscow): D03 accepted in UI/content only; D02 known F01–F04
baseline with mandatory follow-up; final Task Approval requires imported evidence,
reviewed new exact HEAD and green CI; I01 not started. [Current scoped receipt](../acceptance/MS7-MIG-R01/ilya-20261007/current-decision.json)
retains exact decoded body hash and scope. Owner's direct request freezes
canonical source with findings; no other participant decision inferred.

Three-source index: Ruslan original working DB audit13 LF/CRLF-only structural
variants; Ilya working DB substantive drift five payloads; Ilya disposable
exact-source279/279 pages and263 publication digests PASS. Python app3.14.7/
Django5.2.16/PG16.15 reported by Ilya; artifact tools3.12.14/Pillow12.3.0.
His63 functional groups PASS +1 observation, single browser surface, limited
version linkage and resampled JPEG are attributed evidence, not new cross-browser/
touch/full accessibility/pixel-exact/verify_repo results from this import.

Current acceptance/index/verification/plan/trace/README/snapshot receipt updated;
package manifest/export provenance/HOLD/PENDING reports preserved exact.
Source manifest/runtime snapshots/github initial audit/frozen contracts unchanged.
F01–F03 P2,F04 P3 recorded with original routes/repro/source/screenshots and
expected target outcomes. Tracking ownerTramsey00; proposed finding-specific
implementation13baybars and verification allocation PENDING. Live existing
R02#29/I03#42/I05#44 OPEN with canonical assignees verified; no Issue mutation
or downstream execution. No application/UI/CSS/JS/DB/dependency/migration/Harness/
CI change. Same draft PR46; new exact HEAD/actual tested merge-ref/current CI
recorded externally in PR body, avoiding containing-commit self-pins.

Independent package Git blob/source/frozen/history/local preservation/link/safety
validation and staged record manifest results follow in committed validation
receipts. R01 INCOMPLETE; MIG-G0/MIG_BASE_SHA PENDING; D08 CLOSED;
D02/D03 partial only. Final R01 Task Approvals and other human decisions required.

Evidence-import verification results: source/frozen/local preservation/link/
safety validator exit0 PASS,1023 exact original input files and18568 original
output/tmp files preserved. Initial import Git check found ignored .log/two
report JSON absent from index; scoped package force-add includes all232 members.
Original long Windows revision paths made the first input-tree check exit1;
the R01 utility now compares batched Git tree/index object IDs, preserving all
checks rather than changing source/validation criteria.

New local canonical verify_repo exit1 **FAIL_ENVIRONMENT**, four checks pass
(backend,migration command,R03,Harness73), four PostgreSQL-dependent checks
fail with ConnectionTimeout at own disposable55437. Docker ps/ps-a show no
matching earlier R01 container. makemigrations exit0 includes missing migration
history warning, so does not prove local database consistency. No working DB
fallback/setup/bootstrap/migrate/recreation or skip flag used.
See [bounded result receipt](../acceptance/MS7-MIG-R01/ilya-20261007/local-verification.json)
for trace, or the corresponding same-folder receipt for verification. Current
head full isolated CI remains required; previous green is not this run.

Staged whitespace audit first flagged own new blank lines and14 pre-existing
trailing spaces in imported command-05.log. Own blank lines fixed; original
log bytes preserved as required. Own/current documents use full whitespace
check excluding only exact imported package; package SHA256/Git blobs separately
validate every byte, with original whitespace findings left visible.

Final import audit: `validate_ilya_import.py --ref INDEX --archive <supplied ZIP>` exit0 PASS; all232 ZIP members equal checkout and staged Git blob bytes/OIDs,231 package hashes/228 provenance exports verified,165 relative links valid, original_result objects and D08/source/runtime/initial GitHub/first CI snapshots preserved. See [exact result](../acceptance/MS7-MIG-R01/ilya-20261007/import-validation.json). Own whitespace check excludes only the unchanged external package;14 original command-05.log trailing spaces remain observed, not repaired.

## 12. Final human acceptance documentation — 08.10.2026 Europe/Moscow

Existing clean ms7-mig-baseline worktree local/remote daf4e6038761f8d1bf1c60f0976473d987cce230;
main/source8c11edad unchanged. Live PR46 draft/open/unmerged/mergeable clean;
CI37688709748 success. Verified13baybars comment6047568271 at00:51:20 Moscow,
Tramsey00 comment6047773231 at01:05:10, VladimirFrolov777 review5449019477
at01:13:03, API APPROVED commit_id=daf4e603. Exact body hashes/source/scope
stored in [final human receipt](../acceptance/MS7-MIG-R01/final-human-acceptance-20261008.json).
Three baseline/ADR decisions and two independent Task Approvals recorded at
that exact reviewed revision. No new-head approval inferred.

D09 Vladimir agreement recorded only as direct Ruslan user report, with remaining
target dates/staging-disposable boundary; no Vladimir-authored D09 comment.
R01 delay planned07.10→human records08.10 preserved; MIG-G4 remains13.10 23:59
Moscow, no check/scope reductions. F01–F04 assignment agreed13baybars, correction
by I03/verification I05; F04 ordinary-scale readability, enlargement alone
insufficient, regression360/768/1440. Optional Vladimir independent F04 check
requires separate agreement, not given.

Updated current acceptance/ADR status/follow-up/owner map/index/plan/trace/root
current-status links; exact earlier acceptance/follow-up snapshots retained.
Package imports, source manifest, runtime/initial audit/old original_results,
ADR0001 and frozen schemas/proofs unchanged. Active plan remains active.
New record commit requires reviewer confirmation at new HEAD+CI; short list in
[final-review-changes](../acceptance/MS7-MIG-R01/final-review-changes.md).
R01 workflow/snapshot merge/MIG_BASE_SHA remain pending. No application/working
DB change, branch creation, merge, Issue closure or later task implementation.
Database-free record/import/source/preservation checks and staged blob manifest
verified before commit; new full CI and actual tested merge-ref recorded externally
in PR46, retaining original approval SHA and avoiding containing-commit self-pins.

Optional current original-ZIP audit exited1 FileNotFoundError: previous Desktop
path absent. Rerun validates committed package bytes/provenance/Git blobs,
without --archive; prior successful archive hash record unchanged. No original
archive recreation, package modification or claim of fresh archive verification.

Final database-free checks exit0 PASS:232 exact imported files/Git blobs,231
package entries/228 provenance entries,168 relative participant evidence links;
original_result objects/source/runtime/frozen snapshots and earlier scoped/import
receipts unchanged.1023 input files and18568 original output/tmp preserved.
See [current import audit](../acceptance/MS7-MIG-R01/final-acceptance-import-validation.json). Own whitespace changes checked before commit.
