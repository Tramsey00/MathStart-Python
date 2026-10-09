# TRACE MS7-MIG-V01: SQLAlchemy models, Alembic and upgrade profiles

- Date: 2026-10-09, Europe/Moscow
- Task ID: MS7-MIG-V01
- Owner: Владимир; reviewer / Task Approver: Руслан
- Coding agent / surface: Codex desktop, Windows PowerShell
- Issue: https://github.com/Tramsey00/MathStart-Python/issues/34
- Spec: migration v1.1 / accepted user intake R02 at `8d958ae…`
- Plan: [active V01](../exec-plans/active/MS7-MIG-V01.md)
- ADR: [0006](../adr/ADR-0006-react-fastapi-migration.md)
- PR / commit: none created; HEAD unchanged
- Human review status: Pending; initial stop and current continuation below

## 1. Task and inputs

User requested target SQLAlchemy2/Alembic persistence, fresh twice and A/B/C
upgrade preservation on disposable PG, UoW/repositories/locks, protocol schema,
failure tests and evidence. Explicitly stop on architectural/contract conflict;
no commit/push/PR without separate permission. Required root sources/skill,
ownership/V01 card/R01 decisions, R02 mapping/platform/auth/protocol/handoff,
real models/migrations, historical V01/V02/grades records inspected.

## 2. Initial repository state

Exact path `C:/Projects/MathStart-Python-V01`; branch `ms7-mig-v01-schema`;
starting/current local HEAD `8d958aeeb17da46839722441425ccbb5889e2ab7`;
initial tree clean. MIG_BASE_SHA is separately
`60b341fbd00f4c8dadd54ae9a3e5811869a9b0f7`. User's accepted intake supersedes
historical PROPOSED status for task initiation; those records were not rewritten.
Baseline20 tables /114 physical columns /67 constraints /70 indexes. No backend
target existed. Python3.12.10 available; Django/SQLAlchemy/Alembic/psycopg absent.

## 3. Changes and observable actions

Added partial backend models with exact-copy R02 snapshot; separate resolved
runtime/test dependency locks; database config, UoW, repository, ordered locks
and collector; two Alembic revisions and guarded migration adapter/CLI; unit
and real PostgreSQL tests with unchanged Django migrations as source fixtures.
Added this trace, active V01 plan and dedicated finding/report/evidence. Existing
tracked files, frozen contracts/history and root/frontend/CI remain unchanged.
Changed-file inventory and digests are in the dedicated V01 file manifest.

Local default TEMP ACL prevented ensurepip; isolated task TEMP and auto-reviewed
escalation resolved venv installation. Default network DNS prevented pip;
auto-reviewed scoped installation resolved the pinned lock. Incorrect `almbic`
spelling in one failed attempt was corrected in the generated resolved lock;
that failed command was never considered installation evidence.

Docker initially unavailable; launched installed Desktop hidden, then scoped
Docker access. Created new labelled tmpfs container on127.0.0.1:55441 using local
postgres:16-bookworm. No production/shared DB or existing container changed.
Tests independently created/dropped new UUID-named synthetic databases; final
read-only query found zero remaining `test_ms7_mig_v01_%` databases.

## 4. Commands and actual results

Python3.12.10; SQLAlchemy2.0.46 / Alembic1.18.4 / psycopg3.3.6 / Django5.2.16
installed from real pip report. Docker client/server29.8.0; Compose5.5.1;
PostgreSQL16.15 (Debian16.15-1.pgdg12+2).

| Command / scope | Result |
| --- | --- |
| venv ensurepip/default network dependency attempt | ENVIRONMENT FAIL; resolved with task TEMP/scoped escalation |
| pip dry-run report + backend/requirements-test.lock installation | PASS, exit0 |
| `var/ms7-mig-v01-venv/Scripts/python.exe -m pip check` | PASS, exit0 |
| first `python -m unittest backend.tests.test_unit -v` | FAIL:9 pass/1 fail; deferred-FK test timing corrected |
| `python -m unittest backend.tests.test_unit backend.tests.test_postgres -v` | FAIL:16 methods,15 error subcases;10 unit methods passed; PG guard/fixture errors fixed |
| focused PG fresh-twice + A/B/C methods | FAIL:2 methods,2 errors (fresh columns and A CHECK); B/C subcases returned normally |
| schema diagnostic on separate fresh/A disposable DBs | PASS execution, exit0; proves type conflict and reparsed CHECK difference, not acceptance |
| `git diff --check` | PASS, exit0; tracked diff empty, new-file audit separate |
| `python scripts/verify_repo.py` | NOT RUN after contract stop; no bootstrapped baseline runtime |

Commands above used the isolated venv interpreter; PG calls used the reserved
container administration URL without printing credentials/hashes. Only new
synthetic fixtures contain explicitly labelled test credential data.

## 5. Finding and stop

**B01:** R02 model metadata says integer/AutoField for three auth M2M IDs;
physical schema, sequences, platform prose and unchanged Django fixtures say
bigint. Initial target builder selected model types and correctly failed strict
fresh comparison. [Finding](../acceptance/MS7-MIG-V01/finding-B01.md) contains
exact columns, observed evidence and minimal proposed physical-type precedence.
No accepted semantics/digests were edited. User was informed; implementation
stopped before that resolution was applied.

Fresh/A CHECK deparse difference is separately an introduced implementation
issue; B/C retain their physical CHECK and passed focused subcase assertions.
No complete PG suite or V01 acceptance PASS is claimed.

## 6. Remaining verification / human gate

B01 decision; fresh/A repair; full rollback/unknown/drift/constraint PG rerun;
complete protocol drift detection; real ordered-lock and collector races;
backend-only dependency fresh install; standalone guarded CLI; canonical
baseline verification; full historical links and MS6-V02 identification; final
independent review/CI remain outstanding. No live HTTP/auth/publisher, production
stamp, cutover or later-task readiness claimed. Ruslan's gate remains pending.

## 7. Continuation — 2026-10-09 Europe/Moscow

The user instructed preservation of all prior uncommitted files and reported
Ruslan's written R02-owner approval for BIGINT only on the three B01 M2M PKs.
Exact branch/HEAD unchanged. All33 initial files were present; the prior31-file
hash manifest matched with zero missing/changed files. A local byte-preserving
copy exists at `var/ms7-mig-v01-resume-input`; prior verification/report/manifests
remain historical. No implementation restart, reset, clean, commit/push/PR.

New versioned addendum/evidence records source SHA and user-reported provenance;
no external owner message/signature/review was independently retrieved or invented.
Backend machine-readable override changes only three `id` SQL types. Regression
checks all other column types and neighboring INTEGER FK columns; fresh/A/B/C
fixtures use auth join identities exceeding2147483647.

CHECK investigation in new marked PG16.15 DB/TEMP tables reproduced the exact
deparse roundtrip difference. Original IN expression produces the frozen catalog
definition, with42 equivalent PostgreSQL CHECK acceptance combinations. Builder
emits the original expression; comparator has no equivalence/ignore relaxation.
A CHECK(true) mutation must fail pre-stamp. Frozen files/Django migrations remain
unchanged. See check-canonicalization-v1.json/md.

Post-repair suite18/18 PASS, then expanded/final suite22/22 PASS (27.285s final,
zero skips). Added protocol catalog drift negatives, unknown orphan sequence/
view/schema refusal, empty/uncalled sequence tests, real PG collector/defaults/
timestamp and two-connection row-lock tests. Fixed generic receipt/profile/
publication row locking to enforce existing R02 stable ordering. Source fixture
credentials derive from explicitly reserved admin URL to support owner CI handoff.

Created separate target-only venv from backend runtime lock (Django not installed).
pip check PASS. Two fresh PG DBs plus A/B/C upgrades and each check command pass:
10 target-only CLI subprocesses; no Django available/imported. New baseline DB
and runtime `var/ms7-mig-v01-baseline-07929ff0151140ac88a78c6749b977d7` ran migrate,
bootstrap twice, collectstatic, verify_repo8/8 and R02 migration63/63, all exit0.
verify_repo Django discovery:129 tests,118 executed/11 target PG skips because
its child lacks the admin URL; separate V01 run executes all22 with zero skips.
R03 pure18, Harness73 PASS; standalone R02A30 + R03A41 =71 PASS.

Docker initially stopped; launched Desktop hidden and validated exact saved
container ID/label/localhost55441 before starting. First immediate readiness
probe failed while PostgreSQL initialized; subsequent PG tests/readiness confirmed
16.15. No production/shared DB or prior user credentials accessed. Final cleanup
and scope/digest results are in verification-v2.json.

Root workflows still install only root lock: new backend test imports require
target dependencies and explicit target PG verification. Prepared concrete
R03-owned CI patch without applying it. Plain LF patch check failed against
checked-out CRLF context; `git apply --check --ignore-space-change` succeeded.
The patch is proposed/unexecuted; Linux/CI and independent review remain pending.

Current result: locally verified implementation, ready for Ruslan's independent
DDL/schema/Task Approval review. Production stamp/cutover/session/publication
lifecycle and post-setval connection-loss reconciliation remain outside proven
local results. No complete human acceptance is claimed.

Final continuation audit: all 33 prior files remain; only six existing backend
source/test files plus this trace and the active plan were modified. Original
initial evidence files are byte-preserved. Accepted R02 Git digests and checkout
digests have zero mismatches; baseline snapshot copy is byte-identical. Python
AST, new-file whitespace, both pip checks and tracked git diff/check pass. The
evidence audit initially assumed UTF-8 for a Windows baseline log and failed to
decode it; diagnostic reading was corrected, retaining raw binary log hashes.
The final audit passes; no failed test was relabeled or omitted.

The standalone proposed-catalog capture now refuses an existing reference before
DB access and can generate DDL before its reference exists. Its overwrite guard
was checked: refusal and unchanged snapshot bytes. Normal fresh installation
still requires the exact reference. Final read-only query on the confirmed
owned container found zero task test DBs; only that container was stopped.
Current manifest, delta, report and original-result links are separate v2 files.

## 8. Independent audit F1/F2/F3 remediation — v3

User supplied three blocking P2 findings and authorized scoped remediation,
preserving all53 existing untracked files, no reset/clean/commit/push/PR. Exact
HEAD/branch remained8d958aeeb17da46839722441425ccbb5889e2ab7/ms7-mig-v01-schema.
All52 v2 manifest hashes matched at intake; all53 files byte-copied to ignored
`var/ms7-mig-v01-remediation-input`. Full audit/probes/results were available
and copied byte-for-byte to the dedicated independent-audit-v3 directory.
The initial copy command failed PowerShell quoting before writing; a saved
Python helper copied/verifies the originals. Audit material was not edited.

Reproduced the unchanged code with the independent probes in new marked PG
databases: F1 Django old dates false/false/false vs target true/true/true;
F2 COMMIT/DatabaseUnavailable with SQLSTATE40P01; F3 malformed nullable/no-PK/
extra-column tracking accepted, unknown revision CLI check exit0. Probe exit0
means defects reproduced, not acceptance. Separate raw v3 logs/results retained.

F1: ordinary ORM mapper pre-insert overrides every auto_now_add/auto_now field;
ordinary full update applies only auto_now. Restricted saves suppress autoflush
and apply pre-save only to included columns; bulk/Core writes stay explicit.
New import_historical requires PK/auto timestamp values and uses Core insertion
without ordinary mapper hooks. Differential real-Django PG test covers all7
auto fields, page/publication update_fields/full saves, bulk, transient save,
normal Session autoflush and historical timestamp preservation.

F2: initial ordered deleted/CASCADE/SET_NULL union still reproduced40P01; this
partial fix's 9-test run had1 error, and two focused diagnostics failed. Added
full FK reference closure before locking, in the same accepted R02 table/key
order. A subsequent9-test run had1 failure: no40P01, but the second transaction
reported DeletionPlanChanged when already-unneeded reference locks disappeared.
Revalidation now requires unchanged mutation sets and all current lock needs
within the held superset; new lock needs/mutation changes still require outer
rollback/restart. No SKIP LOCKED, FK relaxation or automatic retry was added.
Both crossed Grade deletions now COMMIT, with canonical lock tokens and all
page FKs NULL. Tests also cover dependency unlink/retarget, new PROTECT and
injected SET_NULL rollback, followed by explicit outer retries. R02 order and
frozen bytes are unchanged; no protocol amendment was needed.

F3: exact tracking columns/types/nullability/default/PK/index/identity, revision
graph and expected revision cardinality are proved before stamp. Canonical
empty legacy tracking is allowed after proof; target proof requires one
v01_0002 row. Unknown/base-only/multiple/empty/missing target states, malformed
tracking and valid-head schema drift are refused; CLI subprocess exits1 and
inventory/data/tracking rows stay unchanged. No automatic repairs/stamps.

First complete target suite33/33 PASS (57.787s), zero skips:11 unit +22 real PG methods,
including11 new remediation/sequence/B01 methods. Prior remediation10/10 PASS
(29.566s) also retained. B01 actual INSERT RETURNING IDs exceed int4/max and
superuser/role/password/data preservation passes on fresh/A/B/C. CHECK exact
catalog/truth-table and drift refusal pass without normalization changes.
Real pg_terminate_backend immediately after setval/before COMMIT reports a
DBAPI failure; schema/data/history roll back, sequences only advance and outer
retry succeeds. AFTER-COMMIT acknowledgement-loss reconciliation is not proven.

Runtime-only venv CLI10/10 PASS (fresh twice/A/B/C/check), Django absent/imported
none. New baseline runtime6a4af3b999fd42c4a9a684ae47b645b6 ran migrate, bootstrap
twice, collectstatic, verify_repo8/8 and R02 migration63/63, all exit0. Django
discovery140:118 executed/22 explicit target-PG skips; separate target run has
zero skips. R03 pure18/Harness73 and standalone R02A/R03A71 PASS. Both pip checks,
frozen/diff/scope/AST/JSON/manifests and proposed CI patch applicability audited.

V3 output paths prevent rewriting v1/v2 evidence. Updated CI proposal includes
the new test module; root workflows remain unchanged/unapplied. F1/F2/F3 local
verdict FIXED, ready for independent re-audit, not human Task Approval/CI.
Production/shared data, deployed variants, full V02–V04 lifecycle, Linux/CI and
distinct MS6-V02 history remain unverified. Final cleanup/digests are recorded
in verification-v3.json; no destructive Git or unauthorized external writes.

Final source review added actual-acquired-row proof: OrderedLocks returns rows
actually obtained by FOR UPDATE. Collector compares current needs with those
sets rather than requested IDs. A focused disposable case removes and recreates
a referenced PK after its SELECT FOR UPDATE returned no row; revalidation now
requires safe outer restart. Focused tests2/2 PASS. Final expanded target34/34
PASS (62.914s), zero skips:11 unit +23 PG methods,12 new remediation methods.
Original complete33-test raw log and first baseline result were copied before
rerun. Runtime-only CLI10/10 rerun PASS; repeated baseline runtime
7eeb10898cca46c5b3a2a86eba1c9520 passes all6 setup/verification commands,
verify_repo8/8 and R02 migration63/63. Django discovery141:118 executed/23 target
PG skips; R03/Harness18/73 PASS. Final read-only cleanup query found zero test
DBs, and only the validated owned container was stopped. Prior v1/v2/audit
evidence remains unchanged; v3 records the first and final complete runs.
