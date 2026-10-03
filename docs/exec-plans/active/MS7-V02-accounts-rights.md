# EXEC PLAN MS7-V02: Accounts and rights

- **Status:** Active; implementation prepared, acceptance INCOMPLETE
- **Owner:** Владимир
- **Reviewer / Task Approver:** Руслан
- **Milestone gate:** G3
- **Created:** 2026-10-01
- **Updated:** 2026-10-03
- **Issue:** https://github.com/Tramsey00/MathStart-Python/issues/17
- **Branch:** `ms7-v02-accounts-rights`
- **Trace:** [MS7-V02](../../agent-traces/MS7-V02.md)
- **Human acceptance:** PENDING; retain in active/ until Руслан approves

## CURRENT STATUS — 2026-10-03

- Final reviewed implementation SHA: `b3254c1de9d9ffd32e65618da9ab98f87dbaa330`.
- Current reviewed evidence/docs PR head: `ff8b7da28324170c2691299e8bf81b2f00e23818`.
- Evidence/status cleanup: DONE, committed and reviewed at ff8b7da. Runtime/
  tests/migrations/requirements/contracts are unchanged from implementation SHA.
- Implementation commit and push: DONE; [PR #19](https://github.com/Tramsey00/MathStart-Python/pull/19)
  created and OPEN.
- Current remote CI: VERIFIED / SUCCESS, [Actions run 37040393259](https://github.com/Tramsey00/MathStart-Python/actions/runs/37040393259)
  on reviewed evidence/docs head ff8b7da, including PostgreSQL smoke, canonical verification
  and R02A compatibility per Руслан's repeated-review evidence supplied by user.
- Runtime re-review: no blocking auth/profile/onboarding findings reported.
  Human review gate / Task Approval Руслана / G3 remain PENDING.
- Browser/manual product E2E: NOT VERIFIED. Plan stays ACTIVE, not COMPLETE/DONE.
- Implementation-code SHA b3254c1 and reviewed evidence/docs head ff8b7da are
  distinct. This synchronization records existing evidence; no new commit SHA is
  assigned and formal Руслан Task Approval / G3 remain PENDING.

## Objective and authority

Implement server-side student identity, sessions, profile and onboarding using
the seven Identity operations in merged MS7-R02A. Normative baseline: MathStart
Technical Specification v7.1 G0 ACCEPTED, 2026-09-30; SHA-256
`66affda527d03686b087d48d22ed64faa27df27889a03ab277e50c8fd8021c4c`.
User confirms MS6-V01 frozen/accepted and R02A accepted/merged. Historical
candidate/PENDING annotations remain untouched. No new requirements from v6.

## Preconditions and discovery

- [x] Expected directory/branch; initially clean; HEAD = origin/main = remote
  main = merge-base `428ece726918f635549fc7dd8fdd352f799c3308`.
- [x] AGENTS, PRODUCT, ARCHITECTURE, relevant ADRs 0001 through 0004, setup,
  content pipeline, verification skill, V01 frozen infrastructure inspected.
- [x] Actual R02A prose/OpenAPI/policy/schemas/fixtures/examples/reference and
  acceptance/evidence inspected; all 17 manifest pins verified.
- [x] v7.1 PDF obtained, digest verified, relevant sections read before code edits.
- [x] Existing standard User/session/CSRF/password settings, Content Grade,
  URLs/models/tests/migrations inspected. No identity/profile app existed.
- [x] Issue #17 supplied; discovery report preceded implementation.

## Scope and ownership

Users -> standard Django auth/session and Content Grade. DRF is the accepted
ARCHITECTURE API layer. Implement canonical /api/v1/ identity paths, closed
R02A DTOs, UTF-8 JSON, envelopes, sessions and real CSRF including anonymous
mutations. PATCH only selected_grade_id. START_ZERO / DIAGNOSTIC / SELF_REPORT
persist the selected path/completion. No diagnostic assessment, self-report
knowledge initialization, Attempts, Progress mutation, future UUID HTTP
resources, UI or live LLM runtime. Foreign UUID protection is verified at the
owned profile service boundary; absent future resource APIs are not claimed.

Keep standard User/content/history; client owner/role/verdict/progress is never
authoritative. GET creates no profile/receipt/auth session/domain evidence.

## Implementation sequence and files

1. Discovery/scope reconciliation: complete; no unresolved contract contradiction.
2. Users models/additive migrations: included in reviewed implementation commit.
3. Transaction services, strict schema validation and DRF endpoints: implemented
   in reviewed SHA b3254c1de9d9ffd32e65618da9ab98f87dbaa330.
   Private authentication precedes CSRF/payload errors. Actual URL callbacks
   retain Django CSRF checks, including anonymous register/login.
4. API/security/ownership/retry and real PostgreSQL concurrency tests: added.
5. Compatibility passed; PostgreSQL targeted/full/canonical retests passed
   2026-10-02 after exact replay correction. User's final standalone fresh-install
   smoke in a new disposable PostgreSQL environment also PASS; human acceptance
   remains pending.
6. Implementation committed/pushed, PR #19 OPEN, evidence cleanup completed and
   reviewed at docs head ff8b7da. Current CI run 37040393259 SUCCESS; formal human
   review gate / Task Approval / G3 pending.

Modified: config/settings.py, config/urls.py, requirements.txt, requirements.lock.
Added: users app/http/services/views/urls/models, migrations, tests, plan/trace.
DRF 3.18.1 pinned; existing dependency versions retained. Implementation commit,
push and PR already exist per CURRENT STATUS. No additional staging/commit/push/
PR operation or branch switch is authorized for this documentation cleanup.

## Migrations and historical data

0001_initial adds UUID StudentProfile (OneToOne User, protected nullable Grade,
consistent mode/completion), IdentityReceipt (private scope/digests/response,
unique scope/operation/key, >=7-day retention) and LoginWindow (IP HMAC,
unique shared counter, 10/300 seconds, transactional row locks).
0002_backfill_profiles batches empty profiles for existing users without
changing credentials/roles/content/existing profiles. Old migrations unchanged.
Backfill reverse is a no-op; prefer forward fixes. Never drop populated identity
tables to roll back. Migration review by Руслан is pending.

Fresh SQLite migration and isolated pre-V02 upgrade test passed, preserving
credentials/roles/inactive users/content/existing profile state on rerun.
PostgreSQL fresh test-chain/upgrade and six concurrency cases executed and passed
2026-10-02. User's final standalone fresh-install smoke on a completely new
disposable Compose project/database PASS: both users migrations, migrate --check,
consistency, two bootstraps, identities/content/media/static and content checks.
Bootstrap sources/pipeline unchanged; setup used only ignored var/ storage.

## Verification and remaining work

- [x] check: exit 0; makemigrations --check --dry-run: exit 0, no changes.
- [x] PostgreSQL users tests: exit 0; 50 PASS, zero skips.
- [x] R02A suite: exit 0, 30 tests, frozen artifact pins valid.
- [x] PostgreSQL canonical verify_repo: exit 0, 8/8; Django 74 (zero skips),
  R03 18, Harness 73.
- [x] Locked install/pip check; Linux CPython 3.12 wheel resolution passed.
- [x] Tracked/new-file whitespace and protected baseline/artifact checks clean.
- [x] PostgreSQL targeted tests: 50 PASS, no skips; full suite: 74 PASS, no skips;
  canonical: 8/8 PASS. Upgrade, fresh test-chain, security/concurrency and both
  existing publication integration cases executed. Exact commands in trace.
- [x] Standalone fresh-install smoke: user-reported manual PASS on a completely
  new disposable Compose project and PostgreSQL DB after fix. Both users
  migrations/migrate --check PASS; makemigrations no changes; second bootstrap
  0 new/changed objects; collectstatic 167 copied/483 post-processed; 263 matched
  lessons; quality 281 pages/840 SVG/0 problems; integrity 281 materials/263
  topics/29 media/1685 references, all error counters 0. Detailed source/results
  recorded in trace; this manual smoke was not executed by the agent.
- [x] Final implementation commit: `b3254c1de9d9ffd32e65618da9ab98f87dbaa330`.
- [x] Push: performed.
- [x] PR #19: created and OPEN.
- [x] Evidence/status cleanup: completed, committed and reviewed at docs PR head
  `ff8b7da28324170c2691299e8bf81b2f00e23818`; implementation-code SHA unchanged.
- [x] Current remote CI: VERIFIED / SUCCESS, Actions run 37040393259 on reviewed
  evidence/docs head; PostgreSQL smoke/canonical/R02A checks passed per supplied
  review evidence.
- [ ] Formal human review gate / Task Approval Руслана / G3 acceptance.

Current NOT VERIFIED: browser/manual product E2E (not reported executed).
Remote CI and standalone PostgreSQL fresh-install smoke are verified, not pending.

## Risks and human gate

PostgreSQL tests now provide executed migration/upgrade/concurrency proof. Identity
receipts retain action identity after their minimum replay window. Rate limiting
uses server REMOTE_ADDR; deployment proxy configuration needs review without
silently trusting forwarded headers. Evidence contains no credentials/tokens.

Stop for accepted-contract contradictions, breaking API, custom User,
destructive migration or changes to role/trust/security semantics.
Руслан must review resulting auth/security/migrations before acceptance.
This plan stays ACTIVE. **INCOMPLETE** for human acceptance; Руслан gates pending.

## Exact replay follow-up — 2026-10-02

Initial user PostgreSQL run: 71 tests/7 failures. Agent independently reproduced
the 7 failures in five methods. JSONField/jsonb reordered stored response object
keys; common JSON serializer preserved insertion order. Minimal production fix:
sort object keys recursively for initial and replay responses. No migration,
schema change, relaxed byte assertion or altered digest/ownership/security gate.
Three added regression methods expose the defect on SQLite before fix and pass
on both backends after fix. Historical FAIL and actual retests preserved in trace.

Final manual fresh-install verification was supplied by the user on 2026-10-02
and recorded without changing code/tests/contracts or human acceptance status.

## Historical CI evidence

Actions run [36932755014](https://github.com/Tramsey00/MathStart-Python/actions/runs/36932755014)
on implementation SHA b3254c1 was VERIFIED / SUCCESS per the earlier review.
It remains historical evidence; current CI is run 37040393259 on reviewed
evidence/docs head ff8b7da. Historical PostgreSQL FAIL remains preserved in trace.
