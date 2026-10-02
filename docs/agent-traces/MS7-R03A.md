# TRACE MS7-R03A: CompletionFact audit, corrected design and contract implementation

- **Date:** 2026-10-02 (Europe/Moscow client date)
- **Task ID:** MS7-R03A
- **Owner:** Руслан
- **Reviewer / Task Approver:** Владимир
- **Surface:** Codex desktop; audit/design and pure contract implementation, no live Harness task-run claim
- **Issue:** [#18](https://github.com/Tramsey00/MathStart-Python/issues/18)
- **ADR:** [ADR-0005 / D-021](../adr/ADR-0005-completion-fact.md), Proposed
- **Plan:** [active MS7-R03A](../exec-plans/active/MS7-R03A-completion-fact.md)
- **Human approval:** PENDING
- **PR / CI:** not created or run in this stage
- **Initial audit/design commit:** 1ec5bb507444c442b585720787335c8a17fe09e1
- **Correction commit:** 2f50918d5dbf8224105f666371c5e8b88dacf11b;
  docs(r03a): align CompletionFact design with canonical v7.1
- **Current stage:** Contract candidate READY FOR INDEPENDENT REVIEW; no runtime persistence

## 1. Original task and correction request

The attached full request asked for an exact R03/R02A repository audit,
CompletionFact identity/envelope/authority/replay/compatibility design, Proposed
D-021, updated active plan, future fixture matrix and this observable trace.
It expressly excluded R03A implementation, frozen numerical changes, runtime
models/migrations/API/frontend/dependencies, downstream V08/R11, Issue closure,
PR creation and merge. It permitted one scoped documentation commit if all
required checks passed.

The request was read from the user attachment:
C:/Users/Tramsey/.codex/attachments/89b3c669-71a1-4b07-a933-57038c298043/Вставленный текст.txt.
No approval is inferred from draft readiness or baseline main containing R02A.

The subsequent 2026-10-02 user request explicitly requires correction of commit
1ec5bb507444c442b585720787335c8a17fe09e1 in only ADR-0005, active plan and this
trace. Its supplied canonical v7.1 requirements govern ownership, dual identity,
mandatory outcome/policy, Progress mirror flow, already permitted status-only
replay, nonblocking R02A housekeeping and corrected §20 calendar. No R03A
runtime/reference/schema/fixture/test implementation or PR is authorized.
The separate correction commit has the exact subject recorded above.

## 2. Original audit state and correction baseline

    Branch: ms7-r03a-completion-fact
    HEAD: 870fd760dc1fdb25f33af54eacd97579259d49a0
    HEAD subject: docs(r03a): bootstrap CompletionFact execution plan
    origin/main: 428ece726918f635549fc7dd8fdd352f799c3308
    main baseline subject: MS7-R02A: define HTTP eligibility contract (#15)
    Tracked working tree / index: no initial changes

Correction starting state:

    Branch: ms7-r03a-completion-fact
    HEAD: 1ec5bb507444c442b585720787335c8a17fe09e1
    Tracked working tree / index: clean

Pre-existing untracked paths reported in both passes by git status --short:

- docs/agent-traces/MS7-AUDIT-specification.md
- docs/agent-traces/MS7-G0Candidate-correction.md
- docs/agent-traces/MS7-PREG0-correction.md
- docs/exec-plans/active/MS7-AUDIT-specification.md
- docs/exec-plans/active/MS7-G0Candidate-correction.md
- docs/exec-plans/active/MS7-PREG0-correction.md
- output/
- tmp/

These paths were excluded from edits/staging. The existing interpreter under
tmp/ms7-r02a/venv was used with bytecode disabled; no environment creation,
dependency installation, user-file deletion, git clean/reset or branch switch
was performed. Search found root AGENTS.md and no nested instructions outside
the excluded output/tmp trees.

## 3. Inspected repository inputs

Fully read mandatory sources, using bounded reads/compact JSON to retain all
OpenAPI components and all 37 operations:

- AGENTS.md, PRODUCT.md, ARCHITECTURE.md, README.md, docs/architecture.md
- docs/adr/ADR-0001-preserve-django.md, ADR-0002-exercise-contract-architecture.md,
  ADR-0003-knowledge-progress-semantics.md, ADR-0004-http-eligibility-addendum.md
- specs/progress/BASELINE-v1.md, R03-progress-contract.md,
  fixtures/progress-v1-cases.json (three golden streams and arithmetic cases)
- scripts/r03_contract_reference.py, tests/test_r03_contract.py
- specs/exercises/R02-exercise-architecture.md
- specs/api/MS7-R02A-http-eligibility.md, http-policy-v1.json, openapi-v1.json
- scripts/r02a_contract_reference.py, tests/test_r02a_contract.py
- docs/exec-plans/active/MS7-R03A-completion-fact.md
- skills/verification/SKILL.md and ADR/exec-plan/trace templates

Also inspected repository inventories/conventions in specs/progress, scripts,
tests, docs/agent-traces and docs/exec-plans/completed; relevant sections of
R03-knowledge-progress-audit.md, completed R02/R03 plans, MS7-R02A trace/plan,
completed/README.md; R02A DTO definitions for version identity, Attempt,
Exposure, Eligibility, AssessmentResult, create/submit and public ProgressEvent;
scripts/verify_repo.py, config/settings.py, content model/migration inventory and
initial definitions, and relevant test runtime/report paths.

The canonical v7.1 task card is referenced by the active plan but is not tracked.
Test-Path on the historical R02A Desktop PDF path returned False. No PDF content
was read or claimed verified. This original observation does not block the
correction: the user's current canonical requirements are explicit. Corrected
§20 supplies deadline 05.10.2026; old Target deadline 02.10 is superseded and is
not current calendar authority. No PDF inspection is inferred.

## 4. Observable audit findings

The plan contains the full function/test line map. Main findings:

1. R03 validate_event at 244/275–279 normalizes event.completed_at and requires it
   for correct/diagnostic events. No separate completion input exists.
2. replay at 415–420 creates attempts only while visiting events and checks
   normalized same-attempt/skill completion consistency.
3. _recent_attempts at 330 sorts that event-created dictionary by completed_at
   and attempt_id, retaining ten; _state_dict at 341 uses its independent count
   for status. A no-event completion cannot enter it.
4. Independent correct at 453–457 both marks history and clears repeat_counts.
   A fact-driven reset would change subsequent numerical deltas.
5. ingest_event at 476 canonicalizes exact retries, enforces event/source
   conflicts and replays after late events. Completion needs separate ingestion.
6. Existing tests bind completion to make_event's completed=True default and
   exercise diagnostics, repeats, reveal/incomplete attempts, late occurrence,
   timestamp consistency and source/evidence identities.
7. R02A's oracle creates version-bound attempts, freezes submitted drafts and
   finalizes eligibility/one-positive under exposure semantics. Its completions
   counter has no authoritative completion timestamp/envelope or Progress replay.
8. R02A neutral repeated CORRECT and unsupported/indeterminate completion cannot
   be represented by inventing WRONG, DIAGNOSTIC_WRONG or reveal events.
9. R02A is in main but its checked-in ADR/spec/policy/manifest remain
   Proposed/PENDING. These are stale-marker housekeeping, not an R03A blocker;
   its direct CONTRACT dependency is frozen R03. No acceptance is fabricated.
10. ARCHITECTURE 17.1/42.7 uses broad every-progress-change-has-event wording.
    Canonical v7.1 already permits completion-derived status-only replay. Broad
    wording needs later explanatory alignment, not a new architectural exception
    or unresolved decision; root/frozen documents stay outside this correction.

No Assessment/Progress runtime table, producer or endpoint was found in the
content-only model/migration inventory.

## 5. Corrected design semantics

The initial proposal in 1ec5bb5 used a user/skill/attempt triple, a six-field
envelope without outcome, and completion_version in place of policy_version.
Those design choices are superseded by this correction:

- Assessment owns authoritative immutable CompletionFact. Progress owns mirror/
  replay, imports no Assessment ORM and accepts the immutable DTO through a
  trusted service boundary: Assessment CompletionFact -> immutable DTO ->
  Progress completion mirror. Recent-ten comes only from the mirror.
- Assessment target fields: immutable completion_id, attempt, skill, outcome,
  independent flag, completed_at, policy_version; UNIQUE(attempt, skill).
- Two constraints together: globally unique immutable completion_id and permanent
  (attempt_id, skill_id) source uniqueness. Exact entire canonical payload is an
  idempotent no-op. Reuse either key with any different immutable payload conflicts,
  including new ID/same source, same ID/new source or changed owner/outcome/policy.
- Proposed DTO adds user_id for owner binding without replacing either constraint.
  It has eight required fields; outcome remains mandatory for neutral facts.
  Neutrality means no numerical projection authority, not missing outcome.
- CompletionFact policy_version is explicitly progress-v1.1. ProgressEvent's
  frozen policy_version remains progress-v1; native reducer_version is
  progress-v1.1. completion_version is no longer an envelope field.
- ProgressEvent log remains the sole numerical evidence stream. Its ordering,
  deltas, repeat resets, counts and timestamps remain unchanged. Recent-ten sorts
  mirror records by UTC completed_at / lexical attempt_id, including neutral facts.
- Canonical status-only replay is already permitted: neutral eviction may change
  recent independence 3 -> 2 and MASTERED -> LEARNING while mastery, confidence,
  evidence_count and last_updated remain unchanged. No unresolved architecture
  decision is attached to this permission.
- Literal legacy replay remains unchanged. Canonical mirror compatibility requires
  explicit trusted authoritative ID/outcome context; events alone cannot safely
  supply these fields. Missing context retains legacy replay, without fake facts.
- R02A stale PENDING markers are housekeeping, not blockers; direct CONTRACT
  dependency is frozen R03. Corrected §20 deadline is 05.10.2026; old card
  Target deadline 02.10 is not current calendar authority.
- ADR stays Proposed; package review and implementation remain PENDING. The plan's
  32 future cases include dual-key conflict and mandatory-field coverage, but no
  executable R03A files were added.

## 6. Files changed in each pass

Correction modifies exactly these three existing files:

- docs/adr/ADR-0005-completion-fact.md
- docs/exec-plans/active/MS7-R03A-completion-fact.md
- docs/agent-traces/MS7-R03A.md

No file is added/deleted in correction. The following additions/modification
refer to the original audit commit only:

Added:

- docs/adr/ADR-0005-completion-fact.md
- docs/agent-traces/MS7-R03A.md

Modified:

- docs/exec-plans/active/MS7-R03A-completion-fact.md

Deleted: none. All changes are audit/design documentation. Frozen R03/R02/R02A,
OpenAPI, runtime code, tests, schema, dependencies and user files are excluded.

## 7. Original audit commands, environment and evidence

Executed baseline commands from C:/Projects/MathStart-Python:

    git status --short
    git branch --show-current
    git rev-parse HEAD
    git rev-parse origin/main
    git log -3 --oneline
    rg --files / rg -n (scoped inventories and completion/identity references)

Actual interpreter observations:

- system python: Python 3.12.10, project packages not installed there;
- .venv/Scripts/python.exe: Python 3.10.11, below target; not used for acceptance;
- existing tmp/ms7-r02a/venv/Scripts/python.exe: Python 3.12.14, selected for checks;
- Django 5.2.16, jsonschema 4.26.0, psycopg 3.3.6, pip 25.0.1;
- git version 2.47.0.windows.1;
- configured backend PostgreSQL, reported server_version_num=160015 (16.15).

No packages/backend/settings were changed. version_report.py and pip check
provided these sanitized version/configuration observations.
media/ and staticfiles/ were copied to an isolated runtime outside the repo:

    C:/Users/Tramsey/AppData/Local/Temp/mathstart-r03a-audit-dd978dcb66dc4b70a883a3f26e157a95/

PYTHONDONTWRITEBYTECODE=1 and DJANGO_RUNTIME_ROOT pointing there were set for
test subprocesses. Commands used the existing interpreter with -B:

    python scripts/verify_repo.py
    python -m unittest discover -s tests -p test_r03_contract.py -v
    python -m unittest discover -s tests -p test_r02a_contract.py -v
    python -m pip check
    python scripts/version_report.py

Here python means the explicit selected executable above. It was not the bare
system 3.12.10 interpreter. No migrations/bootstrap or backend fallback were run.
Django tests used their separate PostgreSQL test database; content checks read
the configured migrated site and wrote only isolated runtime reports.

Logs: verify-repo.log, r03.log, r02a.log and design-example.log in that directory.
The design-example log runs only unchanged R03 make_event/replay/status_for:
one self-report + three hard independent diagnostics + seven easy helped
correct events produces 100.00/67.00, evidence_count 11, time
2026-09-24T12:10:00.000000Z, independent count 3 and MASTERED. Calling frozen
status_for with the same numbers/count and recent independent count 2 yields
LEARNING. This establishes the numerical baseline/status consequence, not an
executed CompletionFact eviction implementation.

## 8. Original audit verification results (commit 1ec5bb5)

| Check | Actual result |
| --- | --- |
| Required branch/HEAD/origin-main commands | PASS; exactly the supplied baseline |
| pip check in selected existing environment | PASS; no broken requirements |
| version_report.py | Python/package versions reported; PostgreSQL connection OK, 16.15 |
| verify_repo.py | PASS, exit 0; 8/8 configured checks |
| Django system check | PASS; no issues |
| Migration consistency | PASS; No changes detected, no connection warning |
| Lesson/source/content/integrity | PASS; 263 lessons, 281 pages, 840 SVG, zero findings |
| Django suite inside canonical gate | PASS; 24 tests, no skips, PostgreSQL |
| Existing R03 suite (standalone and canonical) | PASS; 18 tests, unchanged |
| Existing R02A suite (standalone) | PASS; 30 tests, unchanged |
| Harness suite inside canonical gate | PASS; 73 tests |
| Frozen status example | PASS; existing formula gives MASTERED at 3 and LEARNING at 2 |
| Original git diff --check / scope / document links | PASS at initial commit; 11 local links and then-six-field sample checked, 32 cases enumerated. This historical sample check does not validate the corrected canonical DTO |
| R03A schema/reference/fixtures/tests/parity | NOT IMPLEMENTED; future stage, no pass claim |
| Fresh-install PostgreSQL smoke / CompletionFact concurrency | NOT RUN; no schema/runtime change and no such implementation |
| Candidate GitHub CI | NOT RUN; no PR/push created by this stage |

## 9. Observable incidents and limitations

| Incident | Classification / result |
| --- | --- |
| exec_command and node_repl startup failed with apply deny-read ACLs | Windows sandbox/environment failure; approved escalated exec_command allowed read-only audit and checks. No automatic approval-review rejection was returned. |
| One orchestration loop tried to store an absent completed-session ID | Tool reporting error after the three subprocesses had launched. Canonical session was resumed and suite logs/results were read; no test result was invented. |
| Bare system Python lacks project packages; normal .venv is 3.10 | Environment mismatch; used the already installed 3.12.14 environment read-only, with pip check passing |
| Historical v7.1 PDF absent; R02A stale PENDING markers | Original observation; current user-supplied canonical correction governs. Stale markers are nonblocking housekeeping; no acceptance fabricated |

No in-scope implementation failure occurred because no runtime implementation
was authorized. No frozen validation/test was weakened. R03A design behavior
remains prose until its future executable package and review.

## Original documentation scope review (commit 1ec5bb5)

New ADR/trace files were included in the review diff with git add -N on those
two exact paths. git diff --check passed with the new content included.
The complete command required by the request was executed and its output saved
as scoped-review.diff in the isolated evidence directory:

    git diff 428ece726918f635549fc7dd8fdd352f799c3308 -- docs/adr docs/exec-plans/active docs/agent-traces
    git diff --stat
    git diff --name-only
    git diff --cached --name-only

Both the current working diff and the baseline-scoped diff contain exactly the
ADR, active plan and this trace. The substantive cached diff was empty at review
time. No frozen/runtime/dependency/test or unrelated untracked file entered the
diff. A local read-only documentation guard checked all 11 local links, the
six-field closed-envelope example, 32 consecutive future fixture IDs, unchanged
branch/HEAD/origin-main and pending implementation/human gates; PASS recorded
in document-scope-review.log. Intent-to-add is for diff review, not acceptance.

The original documentation commit used subject
docs(r03a): define CompletionFact contract design and was created as
1ec5bb507444c442b585720787335c8a17fe09e1. Its six-field/triple design is now
superseded. Historical evidence above is retained as original observations,
not correction verification or canonical implementation evidence.

## 10. Acceptance and remaining work

Audit findings, an explicit D-021 proposal, future fixtures/file sequence and the
observable trace are available for independent review. The plan stays active.
Implementation must next add the scoped addendum/schema/fixtures/pure reference/
R03A tests, prove literal legacy and native numerical parity, retain existing
R03/R02A suites and run canonical verification. V08 persistence, locking and
fresh-install evidence remain downstream.

Vladimir must review identity/envelope, trusted independence, native
COMPLETED-only membership versus legacy reveal entries, repeat-reset isolation,
explicit compatibility/version behavior and the corrected canonical package.
Status-only replay permission is already settled, and R02A stale markers are
nonblocking housekeeping. Direct CONTRACT dependency remains frozen R03.

**Human review:** PENDING; no review date or acceptance recorded.
**Final stage status:** audit/design READY FOR REVIEW; full task INCOMPLETE.
No plan move, Issue closure, PR creation, push or merge is authorized by this
status. Completion of the required human and implementation gates is outstanding.

## 11. Correction verification and scope (2026-10-02)

The correction starts from 1ec5bb507444c442b585720787335c8a17fe09e1 on the
existing branch with a clean tracked tree/index. The protected untracked paths
from section 2 remain excluded. Only the three authorized documents are edited.
No schema, fixture, reference, runtime or test implementation is performed.

Required current checks:

    git diff --check
    python scripts/verify_repo.py
    python -m unittest discover -s tests -p test_r03_contract.py -v
    git diff --stat

Here python is the existing tmp/ms7-r02a/venv/Scripts/python.exe invoked with -B
and PYTHONDONTWRITEBYTECODE=1. Canonical verification reuses the isolated runtime
media/static copy from section 7 with DJANGO_RUNTIME_ROOT outside the repository.
No original-pass result substitutes for this correction rerun.

Current version_report.py observations: Python 3.12.14, Django 5.2.16,
jsonschema 4.26.0, psycopg 3.3.6, pip 25.0.1; PostgreSQL connection OK with
server_version_num=160015 (16.15). pip check: no broken requirements, exit 0.
No dependency/settings/backend changes or migration/bootstrap were performed.

Correction logs in the section 7 isolated directory:

    C:/Users/Tramsey/AppData/Local/Temp/mathstart-r03a-audit-dd978dcb66dc4b70a883a3f26e157a95/verify-correction.log
    C:/Users/Tramsey/AppData/Local/Temp/mathstart-r03a-audit-dd978dcb66dc4b70a883a3f26e157a95/r03-correction.log

| Current correction check | Actual result |
| --- | --- |
| git diff --check | PASS, exit 0 |
| python scripts/verify_repo.py | PASS, exit 0; all 8 configured checks |
| Canonical Django / R03 / Harness suites | PASS; 24 / 18 / 73 tests respectively |
| python -m unittest discover -s tests -p test_r03_contract.py -v | PASS, exit 0; 18 tests |
| version_report.py / pip check | PASS, exit 0; actual versions above, PostgreSQL reachable |
| In-memory documentation guard | PASS, exit 0; 11 local links, eight required DTO fields, exact progress-v1.1 completion policy, 32 future cases, expected HEAD and empty index before staging |
| git diff --stat / --name-only / status | Exactly three authorized modified documents; protected untracked paths excluded |
| R03A implementation/parity / migration/fresh-install / PR CI | NOT IMPLEMENTED or NOT RUN; no such result claimed |

The documentation guard creates no repository test/helper file. The original
Windows sandbox startup failure recurred; approved escalated commands enabled
verification. No automatic approval-review rejection was returned. Final scoped
diff/whitespace review and exact-path staging precede the separate commit.

Correction commit subject: docs(r03a): align CompletionFact design with canonical v7.1.
The commit SHA is reported after creation, without self-referential trace content.
Human acceptance remains PENDING and the full task remains INCOMPLETE.

## 12. Contract implementation authorization and baseline (2026-10-02)

The new user attachment at
C:/Users/Tramsey/.codex/attachments/2b00e215-4b5f-4048-81ea-ea00ac5eb177/Вставленный текст.txt
explicitly supersedes the earlier design-only scope: implement the pure R03A
addendum/schema/fixtures/reference/tests/parity, separate CI step and records;
verify, review scope, then create one local commit. No push/PR/merge, Issue
closure, ADR acceptance or Django/runtime/persistence implementation is allowed.

Baseline commands confirmed branch ms7-r03a-completion-fact, clean tracked tree/
index and HEAD 2f50918d5dbf8224105f666371c5e8b88dacf11b, with both design commits
present. origin/main remains 428ece726918f635549fc7dd8fdd352f799c3308.
The protected pre-existing untracked inventory in section 2 remains excluded.
No git clean/reset/branch switch or package install was performed.

Mandatory repository sources were reread, including corrected ADR-0005, frozen
R03 contract/fixtures/reference/tests, active plan/trace and R02A contract/policy/
OpenAPI/reference/tests. Compact OpenAPI reads retained all components and 37
operations. The verification skill, current CI, README/content architecture and
relevant model/migration boundaries were inspected. The historical unavailable
PDF observation remains; the explicit supplied canonical requirements govern.

## 13. Implemented artifacts and semantics

Added exactly seven files:

- specs/progress/R03A-completion-fact.md
- specs/progress/schemas/completion-fact-v1.schema.json
- specs/progress/fixtures/completion-v1-cases.json
- specs/progress/fixtures/completion-v1-invalid.json
- specs/progress/fixtures/progress-v1.1-parity.json
- scripts/r03a_contract_reference.py
- tests/test_r03a_contract.py

Modified exactly four existing files: this trace, the active R03A plan,
.github/workflows/ci.yml and specs/api/candidate-manifest-v1.json. The manifest
change is solely the derived workflow hash described below. No files deleted.
ADR-0005 remains Proposed and byte-unchanged; frozen R03 and R02A contracts,
OpenAPI, references, tests and historical fixtures remain unchanged.

The closed eight-field schema requires completion_id/user_id/skill_id/attempt_id/
outcome/independent_correct/completed_at/policy_version. completion_id is canonical
lowercase UUID; references are nonempty, flag is strict boolean, outcome is exactly
CORRECT/WRONG/UNSUPPORTED/INDETERMINATE, policy is progress-v1.1. Aware RFC3339
time has <=6 fractional digits and canonical UTC normalization. Domain validation
adds known skills and true-implies-CORRECT; shape validation alone grants no trust.

The mirror validates global immutable completion_id and permanent (attempt_id,
skill_id) source uniqueness before scope filtering. Exact whole canonical payload
retries coalesce; reuse of either key with any changed payload conflicts. Atomic
ingestion returns detached proposed data, preserving original inputs on rejection.
Cross-skill facts agree on attempt owner/time; incoming target user/skill is bound.

Assessment owns authoritative facts. The pure boundary requires explicit versioned
source records, exact immutable DTO agreement, COMPLETED lifecycle and mapped
skill. It compares supplied context only; genuine server auth/FKs/version binding
are V08 obligations. Progress imports no Assessment ORM. Native recent-ten uses
only the full mirror, sorted by UTC completed_at / lexical attempt_id; last ten
distinct sources include neutral facts and sum the independent flag once.

NumericalReplay validates/copies events and invokes the unchanged R03 reducer once.
Immutable JSON-backed cache results detach callers. Fact ingestion/replay reuse
that cache, calling only frozen status_for for derived status. Frozen event policy
remains progress-v1; native reducer_version is progress-v1.1. No duplicate numerical
constants, fake events or CompletionFact-driven misconception resets exist.
Late/permuted facts can change window/count/status while numerical state, event
IDs/order, deltas, repeat resets and last_updated remain fixed. Inline event/fact
time, owner and terminal result contradictions reject; inline events never add
native window entries. Missing DTOs produce completion_gaps diagnostics only.

Explicit import_progress_v1_completions requires legacy-completion-v1 source
metadata with authoritative IDs/outcomes and LEGACY_COMPLETION provenance; it
never infers an outcome from a reveal/wrong step. Literal v1 remains unchanged.
Parity metadata pins the historical fixture SHA and supplies equivalent mirrors.
legacy_snapshots are explicitly literal v1 diagnostics, not native as-of history.

## 14. Executable coverage and observed proofs

completion-v1-cases.json covers all 32 exact plan case IDs, with six concrete
shared datasets and explicit variants/delivery orders/authority. Invalid fixtures
contain 33 rows distinguishing schema and domain rejection. Parity covers all
three frozen streams plus all three arithmetic cases. Fixtures are synthetic.
The independent test suite contains 41 tests (32 named cases and nine additional
guards), including unchanged R02A serial-fixture composition without a second
eligibility algorithm.

- Dedicated neutral eviction: 100.00 mastery, 67.00 confidence, evidence_count 11,
  independent count 3 / MASTERED becomes count 2 / LEARNING; all four numerical
  fields including 2026-09-24T12:10:00.000000Z last_updated remain identical.
- Mocked frozen replay count stays one across fact ingestion; no new event or
  numerical application, immutable cached/input outputs are checked.
- A true fact between misconceptions leaves third repeat at 1.5; mastery snapshots
  60.00, 55.00, 48.75, 41.25. A qualifying diagnostic event resets repeat even
  with a delayed fact: 60.00, 55.00, 48.75, 56.75, 51.75.
- Explicit parity compares literal golden state, native numbers/status/time,
  equivalent window/count, event IDs/order/application, all historical snapshots
  and recorded progress-v1 event policy; only native reducer_version differs.
- Full ledger permutations, >10 same-time ties, owner/global key collisions,
  no-context/mapping/lifecycle rejection, authority mismatch, UTC equivalence,
  max precision and unsupported/indeterminate history are independently asserted.

## 15. Implementation verification and incident

All commands run from C:/Projects/MathStart-Python using the existing
tmp/ms7-r02a/venv/Scripts/python.exe with -B and PYTHONDONTWRITEBYTECODE=1.
DJANGO_RUNTIME_ROOT is the external directory from section 7. Actual versions:
Python 3.12.14, Django 5.2.16, jsonschema 4.26.0, psycopg 3.3.6, pip 25.0.1;
PostgreSQL reachable, server_version_num 160015 (16.15). No environment/dependency/
backend changes or migration/bootstrap were performed.

| Command | Actual result / external log filename |
| --- | --- |
| python -m unittest discover -s tests -p test_r03a_contract.py -v | PASS, exit 0; 41 tests; r03a-implementation.log |
| python -m unittest discover -s tests -p test_r03_contract.py -v | PASS, exit 0; 18 unchanged tests; r03-implementation.log |
| python -m unittest discover -s tests -p test_r02a_contract.py -v, initial | FAIL, exit 1; 30 tests, one workflow digest mismatch; r02a-implementation.log |
| Same R02A command, after derived hash refresh | PASS, exit 0; 30 unchanged tests; r02a-implementation-final.log |
| python scripts/verify_repo.py | PASS, exit 0; 8/8, Django 24 / R03 18 / Harness 73; canonical-implementation.log |
| python -m pip check | PASS, exit 0; no broken requirements; pip-implementation.log |
| python manage.py makemigrations --check --dry-run | PASS, exit 0; No changes detected; migrations-implementation.log |
| python scripts/version_report.py | PASS, exit 0; sanitized versions / PostgreSQL reachable; versions-implementation.log |

The explicitly authorized CI step changed ci.yml bytes, which R02A's candidate
manifest pins. The first run's other 29 tests passed. Refreshed only the derived
workflow hash from 72244a5f37d102bfb02ba56809643d1c0e94369cdf957492b5b99b8faed03117
to 1edf8fc5023a171d6bd4c173b7a30e717b197a4d939649729b16054bf48e3ea7.
All other hashes/data and CANDIDATE_FOR_REVIEW/PENDING markers remain intact.
No R02A semantics/test/OpenAPI was changed or weakened; final rerun passes.
CI adds only R03A CompletionFact contract beside R02A with the required unittest
command. Existing canonical CI checks remain unchanged; GitHub CI has NOT RUN.

Windows normal sandbox process startup remained unavailable (deny-read ACL helper
failure). Approved escalated execution enabled the checks; no automatic approval
review rejection occurred. Reports/logs stay external; protected output/tmp and
unrelated untracked files are neither edited nor staged.

## 16. Final scope review and pending acceptance

Pre-commit status/stat/whitespace and full git diff review include all new files
through exact-path intent-to-add. The complete diff is retained externally in
implementation-review.diff. The in-memory scope guard passed: exactly eleven
changed paths; eleven frozen/design/boundary files byte-identical; derived-only
manifest change; CI exactly two added lines; sixteen resolved local document
links; 32/33/3 fixture inventory; no substantive cached changes before staging.
New fixture line endings are normalized to repository LF without content changes.
Only those eleven paths are staged for the one authorized local commit:

    feat(r03a): implement CompletionFact progress v1.1 contract

The SHA is reported after creation without self-referential trace content.
Post-commit status/log must confirm protected untracked files only. No push/PR/
merge/Issue closure or Accepted marker. Human approval and final-SHA GitHub CI
remain PENDING; plan stays active, ADR stays Proposed. Local contract candidate
is READY FOR INDEPENDENT REVIEW; full MS7-R03A is not Accepted/Done.

Vladimir must review dual identities/canonical payload, authority context versus
future real provenance, native COMPLETED membership/legacy reveal preservation,
event/fact contradiction policy, completion gaps and durable delivery obligations,
repeat reset isolation, status-only time semantics and explicit parity/import.
V08 must still implement persistence/FKs, server binding, locking/concurrency,
reconciliation/backfill and migration/fresh-install proof. This pure contract
stage provides none of that PostgreSQL persistence evidence. Corrected deadline
05.10.2026, direct frozen R03 dependency and nonblocking R02A stale markers remain.
