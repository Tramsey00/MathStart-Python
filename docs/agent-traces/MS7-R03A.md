# TRACE MS7-R03A: CompletionFact repository audit and D-021 design

- **Date:** 2026-10-02 (Europe/Moscow client date)
- **Task ID:** MS7-R03A
- **Owner:** Руслан
- **Reviewer / Task Approver:** Владимир
- **Surface:** Codex desktop; repository audit/design, no live Harness task-run claim
- **Issue:** [#18](https://github.com/Tramsey00/MathStart-Python/issues/18)
- **ADR:** [ADR-0005 / D-021](../adr/ADR-0005-completion-fact.md), Proposed
- **Plan:** [active MS7-R03A](../exec-plans/active/MS7-R03A-completion-fact.md)
- **Human approval:** PENDING
- **PR / CI:** not created or run in this stage
- **Commit:** permitted scoped documentation commit only after verification/scope review;
  its SHA is reported to the user and available through this file's Git history

## 1. Task and source request

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

## 2. Initial repository state and protected files

    Branch: ms7-r03a-completion-fact
    HEAD: 870fd760dc1fdb25f33af54eacd97579259d49a0
    HEAD subject: docs(r03a): bootstrap CompletionFact execution plan
    origin/main: 428ece726918f635549fc7dd8fdd352f799c3308
    main baseline subject: MS7-R02A: define HTTP eligibility contract (#15)
    Tracked working tree / index: no initial changes

Pre-existing untracked paths reported by git status --short:

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
was read or claimed verified. This is a canonical-source reconciliation
limitation for the human gate, not a substituted or invented normative source.

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
   Proposed/PENDING. Merge presence alone does not record its human acceptance.
10. ARCHITECTURE 17.1/42.7 uses broad every-progress-change-has-event wording.
    D-021 records the required narrow numerical-versus-window/status refinement
    explicitly for human review; frozen/root documents were left unchanged.

No Assessment/Progress runtime table, producer or endpoint was found in the
content-only model/migration inventory.

## 5. Proposed decisions recorded

- Identity: (user_id, skill_id, attempt_id), with native server owner/version/
  skill-mapping verification and same-attempt cross-skill instant consistency.
- Closed six-field completion-v1 envelope: completion_version, user_id, skill_id,
  attempt_id, completed_at, independent_correct. No unnecessary fact ID,
  difficulty, numerical event identity or answer/version duplication.
- Native authority: finalized assessed COMPLETED Attempt and frozen server
  eligibility; no client-declared independent truth. Pending/abandoned/REVIEWED
  states are distinct and excluded from native completed-attempt membership.
- Numerical track: unchanged R03 events/ordering/repeat resets. A fact cannot
  change numerical values, evidence count, last_updated, deltas or event log.
- History track: CompletionFact only, sort UTC completed_at / lexical attempt_id,
  include neutral entries, count each attempt once. Late facts can change final
  status through unchanged status_for; no numerical or repeat mutation.
- Coexistence: reject inline-time/fact conflicts; keep frozen inline event
  attestations for event validation without using them as native history.
  Report missing separate completions as diagnostic gaps.
- Compatibility: preserve literal legacy replay; explicit validated v1 import,
  no automatic fallback or retroactive R02A credit restrictions. Native
  reducer_version=progress-v1.1 is the declared metadata distinction; event
  policy_version remains progress-v1.
- ADR is Proposed. The active plan describes 32 future fixture cases and exact
  additive implementation files; none of them was implemented in this stage.

## 6. Files changed

Added:

- docs/adr/ADR-0005-completion-fact.md
- docs/agent-traces/MS7-R03A.md

Modified:

- docs/exec-plans/active/MS7-R03A-completion-fact.md

Deleted: none. All changes are audit/design documentation. Frozen R03/R02/R02A,
OpenAPI, runtime code, tests, schema, dependencies and user files are excluded.

## 7. Commands, environment and evidence

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

## 8. Verification results

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
| git diff --check / scoped diff / document links | PASS; only the three task-owned docs, 11 local links resolve, six-field sample parses and 32 future cases are enumerated |
| R03A schema/reference/fixtures/tests/parity | NOT IMPLEMENTED; future stage, no pass claim |
| Fresh-install PostgreSQL smoke / CompletionFact concurrency | NOT RUN; no schema/runtime change and no such implementation |
| Candidate GitHub CI | NOT RUN; no PR/push created by this stage |

## 9. Observable incidents and limitations

| Incident | Classification / result |
| --- | --- |
| exec_command and node_repl startup failed with apply deny-read ACLs | Windows sandbox/environment failure; approved escalated exec_command allowed read-only audit and checks. No automatic approval-review rejection was returned. |
| One orchestration loop tried to store an absent completed-session ID | Tool reporting error after the three subprocesses had launched. Canonical session was resumed and suite logs/results were read; no test result was invented. |
| Bare system Python lacks project packages; normal .venv is 3.10 | Environment mismatch; used the already installed 3.12.14 environment read-only, with pip check passing |
| Historical v7.1 PDF path absent and upstream acceptance artifacts pending | Human-source/acceptance reconciliation outstanding; no acceptance fabricated |

No in-scope implementation failure occurred because no runtime implementation
was authorized. No frozen validation/test was weakened. R03A design behavior
remains prose until its future executable package and review.

## Final documentation scope review

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

The documentation commit allowed by the task uses the exact subject
docs(r03a): define CompletionFact contract design. Its eventual identity is
reported in the final user report and this file's Git history; no self-referential
commit SHA, human approval or CI result is invented in this pre-commit record.

## 10. Acceptance and remaining work

Audit findings, an explicit D-021 proposal, future fixtures/file sequence and the
observable trace are available for independent review. The plan stays active.
Implementation must next add the scoped addendum/schema/fixtures/pure reference/
R03A tests, prove literal legacy and native numerical parity, retain existing
R03/R02A suites and run canonical verification. V08 persistence, locking and
fresh-install evidence remain downstream.

Vladimir must review identity/envelope, trusted independence, native
COMPLETED-only membership versus legacy reveal entries, repeat-reset isolation,
explicit compatibility/version behavior, and the architectural status refinement;
reconcile R02A acceptance and canonical v7.1 task-card requirements.

**Human review:** PENDING; no review date or acceptance recorded.
**Final stage status:** audit/design READY FOR REVIEW; full task INCOMPLETE.
No plan move, Issue closure, PR creation, push or merge is authorized by this
status. Completion of the required human and implementation gates is outstanding.
