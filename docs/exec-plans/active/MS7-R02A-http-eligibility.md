# EXEC PLAN MS7-R02A: HTTP and eligibility addendum

- **Status:** Active — READY_FOR_THIRD_REVIEW; third review and human acceptance PENDING
- **Owner:** Руслан
- **Reviewer / Task Approver:** Владимир
- **Created / updated:** 2026-09-30 / 2026-10-01
- **Milestone:** G1 contract closeout, not a repeat of G0
- **Relation:** FOLLOW-UP / ADDENDUM TO FROZEN R02
- **Issue / PR:** not created; existing Issue not confirmed (GitHub CLI unavailable)

## Goal and baseline

Deliver one versioned machine-readable HTTP contract covering every §11 route,
with DTOs and deterministic revision, exposure and retry fixtures. Reach READY
FOR HUMAN REVIEW without implementing downstream runtime or claiming acceptance.

G0, initial HEAD, local origin/main and remote main (verified with `git ls-remote
origin refs/heads/main`) are all `fc4e907149da026e4710c3e453d8065c0106e4b9`.
Initial branch: `main`; scoped branch: `codex/ms7-r02a-http-eligibility`.
Historic branches use task names; the desktop's default `codex/` prefix is used
for this new scoped task. No baseline advancement or conflicting tracked edits.
Pre-existing untracked MS7-AUDIT, MS7-PREG0, MS7-G0Candidate plans/traces and
`output/`, `tmp/` are preserved. No reset, force-push, push or merge is authorized.

## Inputs and discovery

Canonical normative input: user's
`C:/Users/Tramsey/Desktop/MathStart_Technical_Specification_v7.1_G0_ACCEPTED_2026-09-30.pdf`,
especially §§4–11,15–17,20–22,25–27,30,32. Extracted locally for read-only review.
The pasted request authorizes implementation through review readiness only.

Repository inputs: `AGENTS.md`, `PRODUCT.md`, `ARCHITECTURE.md`, `README.md`,
`docs/architecture.md`, ADR-0001/0002/0003; frozen
`specs/exercises/R02-exercise-architecture.md`, completed R02 plan and R02 trace;
all seven JSON files under `specs/exercises/fixtures/`; R03 progress baseline,
contract and tests; I01 API-needs and states matrix; spec/ADR/plan/trace templates;
`requirements.txt`, `requirements.lock`, `config/settings.py`, current content
models/migrations and URLs; `scripts/verify_repo.py`, verification skill,
existing JSON schemas, contract/reference tests and canonical Harness tests.
No nested AGENTS.md found. R02 accepted/frozen; I01 handoff is conceptual and
does not override it. New artifacts do not alter any historical R02/R03 input.

Conventions: specs own versioned JSON fixtures, pure reference helpers live in
scripts, unittest contract suites in tests; JSON Schema 2020-12 and jsonschema
4.26.0 already locked. OpenAPI-specific validator is not installed. Use OAS 3.1
JSON (valid JSON-compatible YAML) to avoid adding a YAML dependency, the official
vendored structural schema plus local schema/ref/operation checks. DTOs share
one versioned schema bundle with named $defs; one canonical OpenAPI file only.

## Gaps and implementation sequence

R02 deliberately defers HTTP, exact revisions, persistence and cross-attempt
eligibility. There is no existing canonical OpenAPI. No blocking contract conflict
found: D-022/023 are the explicitly scoped v7.1 additions to accepted R02.

1. Create proposed ADR-0004 and `specs/api/MS7-R02A-http-eligibility.md`.
2. Add `specs/api/openapi-v1.json`, reusable `schemas/dto-v1.schema.json`,
   official OAS structural schema and versioned operation-policy JSON.
3. Add valid/invalid HTTP fixtures and ordered concurrency scenarios under
   `specs/api/fixtures/`; deterministic UUIDs/timestamps, no PII.
4. Add bounded pure contract reference/validator and tests, no ORM or endpoints.
5. Run task tests, frozen R02 compatibility, R03 and full canonical verification;
   self-review diff; calculate candidate SHA-256 and update trace/this plan.

## Inherited decisions and additions

Keep four modes, four step types, six R02 step fields, public exercise names,
server-owned normalization and contract_version's single-counter meaning.
version is an additive alias of contract_version, validated equal; API artifact
version is separate metadata. Existing ContentPage topic IDs remain compatible.
New resource IDs are UUIDs. ExerciseVersion binding remains authoritative after
archival; no new attempt on archived versions.

D-022: full draft PUT and submit require expected_revision; successful mutations
advance revision, submitted order/raw payload freeze into digest. Corrections
create previous_attempt_id-linked attempts. Exposure is keyed by user+version;
help/reveal/submit/finalization serialize. Assistance received before finalization
prevents independent credit; pending submit alone never immunizes later help.
Only a completed independent result survives subsequent help without revocation.
At most one credited positive event per user+version, even after receipt expiry.
SELF_CHECK review remains unassessed. Neutral completion is not WRONG.

D-023: Session+CSRF, safe owner 404, success/error envelopes, cursor ordering and
limits; explicit mutation idempotency; digest includes owner, concrete canonical
route+operation, body and revision; same digest replays persisted result, changed
digest conflicts; receipts >=7 days, permanent source uniqueness separate.
202 permitted for submitted attempts only, with operation_id and canonical GET
status route; no queue claim. 200 UNSUPPORTED/DEGRADED are business results.

## Scope and design limits

DTOs define public wire contracts, not full future database entities. Public
input metadata has bounded shape-only extension; raw structured payload is
untrusted data validated against each published exercise's public shape at runtime.
Minimal downstream session/progress/tutor shapes use explicit state, policy and
references. No parser/validator implementation, CompletionFact schema/reducer,
Django/DRF endpoints, models, migrations, authentication changes, frontend,
provider, live LLM, deployment, dependency additions or unrelated cleanup.

## Verification and security

Run configured Python version and package checks; `python -m unittest discover
-s tests -p test_r02a_contract.py -v`; existing R03 suite; `python
scripts/verify_repo.py`; `git diff --check`. Task suite validates official OpenAPI
structure, references, all routes, public shapes, required headers/preconditions,
safe errors, fixture schemas, serial race outcomes, R02 fields, one-positive and
receipt-expiry behavior. Recursively inspect ordinary public DTOs and examples
for secret equivalents, health allowlist, owner-safe errors and untrusted text.
No PostgreSQL locking proof is claimed for a contract-only task.

## Rollback and human gate

Rollback consists of removing/reverting only task-owned added files and check
integration if any; preserve all user files/content/evidence and frozen inputs.
No persistence change. Vladimir must approve ADR D-022/023, public schemas,
fixtures and the exact OpenAPI digest. Keep plan active until that approval.
Final-SHA applicable green CI and explicit merge authorization remain required.

## Acceptance checklist

- [x] Baseline and frozen dependency read; scoped branch; no contract blocker.
- [x] Every §11 endpoint and reusable DTO covered (37 operations, 90 definitions).
- [x] D-022 revision/exposure/one-positive scenarios and D-023 retries pass.
- [x] R02 names/enums/version semantics and public secrecy preserved.
- [x] Valid/invalid fixtures and structural/reference checks pass.
- [x] Canonical and applicable tests executed; limitations recorded.
- [x] Candidate OpenAPI digest and trace, self-reviewed scoped diff ready.
- [ ] Vladimir's independent acceptance (PENDING).
- [ ] Final SHA applicable CI / merge gate (PENDING).

## Result and remaining handoff

Contract artifacts, proposed ADR-0004, pure oracle and task tests are complete
for third review. Thirty-two scenario linearizations and typed request/response examples
cover the task's positive/negative routes. Candidate OpenAPI SHA-256:
`133aae117333e66b40662ec4fdb47fc02ee08e7aeecbbd9cbb200d5468ca7362`.
The candidate manifest pins external schemas/policy/fixtures as well as OpenAPI;
acceptance must review the whole package, not mutable refs behind one digest.

Configured task environment: isolated `tmp/ms7-r02a/venv`, Python 3.12.14,
complete existing requirements.lock installed with --no-deps; pip check PASS.
Latest canonical verify_repo.py passed 8/8 on the unchanged configured PostgreSQL
backend: Django 24 tests without skips, R03 18, Harness 73. R02A passes 30 tests
and all 32 scenarios; exact commands/scope evidence are in trace section 12.
PostgreSQL 16.15 connection diagnostics pass. Earlier SQLite verification and the
second-review PostgreSQL outage are historical; future R02A locking/fresh-install
evidence is not claimed.

CI integration is a separate task-suite step in `.github/workflows/ci.yml`;
the existing eight canonical checks and Harness assumptions are unchanged.
No dependency/config/runtime behavior change. The original .venv has a Python
3.10 ABI mismatch under bundled Python 3.12 and was preserved; the clean locked
task environment resolves verification without editing it. Bootstrap authoring
surface is Codex desktop, pre-G1, not an accepted live MathStart Harness run.

Vladimir must independently review ADR-0004/D-022/D-023, schemas, examples,
scenario outcomes and package digests. No issue, PR, commit, push, merge, CI
success or human acceptance was invented. Keep this plan active. Temporary
authoring scripts, isolated venv/PDF extraction and full review patch remain
under task-owned `tmp/ms7-r02a/`, outside the intended repository diff.

## 2026-10-01 — corrections after independent pre-commit review

The initial readiness assessment was superseded by NOT_READY_TO_COMMIT: the
review found help-action duplication after receipt expiry and ten inconsistent
HTTP resource identities. The user authorized only these blockers and required
another independent review before any commit, push or PR.

- [x] Separate permanent help-source digest/observation from expiring HTTP
  receipts in the pure oracle; preserve exact help retry, conflict and owner gates.
- [x] Add hint/reveal expiry scenarios and regressions for repeated expiry,
  original hint level, different digest/route, owner 404 and unchanged submit/credit.
- [x] Audit all 37 exchanges. Correct identity/reference fields in 17 examples,
  including the ten reviewed mismatches, topic/grade/exposure/origin/skill references
  and the matching messages-list example. Preserve DTOs and route templates.
- [x] Verify semantic assertions reject the saved old inputs: three help
  regressions fail on the old oracle; 16 old exchanges fail identity checks.
- [x] After content validation, refresh only four changed artifact hashes.
  OpenAPI/DTO/policy/ADR/business-result bytes and their hashes are unchanged.
- [x] R02A 25 tests / 32 scenarios, reference checker, pip check and canonical
  8/8 pass. Canonical invokes Django 24 (two unchanged PostgreSQL skips), R03 18,
  and Harness 73. Runtime reports/database copy are outside the repository.
- [x] Independent second review returned NOT_READY_TO_COMMIT; its requested
  corrections and latest verification are recorded below. No commit/push/PR.

Candidate-manifest SHA-256 after this first correction (historical):
`f930f344e3b8efdc5eb6757a1fba6da9157080c7b3b6e4cad3ee05d8d81276d2`.
Detailed correction evidence and excluded files are in the trace. The plan stays
active; accepted digest, approval, final-SHA CI and acceptance remain PENDING.

## 2026-10-01 — second-review nested identity and onboarding corrections

The user authorized only these two blockers and the associated verification and
records. Preserve the OpenAPI digest and all frozen/runtime/dependency inputs.

- [x] Build canonical relationship maps from existing public/HTTP fixtures,
  checking version IDs in both directions and known nested resource bindings.
- [x] Reject the reviewed attempt.exercise_version.exercise_id and exercise.topic
  substitutions; audit all 37 exchanges, session items, exposure, previous
  attempts, practice origin/target and conversation/message references.
- [x] Keep unshown resource bindings unproven; no fabricated existence/relations.
- [x] Correct successful START_ZERO onboarding mode/completion using the existing
  contract/DTO fields; add lost-mode/wrong-mode/false-completion regressions.
- [x] Prove new regressions fail before correction; reject saved old inputs after
  correction and confirm expected failures when the old guard is restored in memory.
- [x] R02A 30/30 (original 25 plus five added tests), 32 scenarios, reference
  checker, pip check and canonical 8/8 PASS. Canonical runs Django 24 without
  skips, R03 18 and Harness 73; migration consistency reports no changes.
- [x] Keep PostgreSQL configuration unchanged. Connection is now available;
  diagnostics identify server 16.15. Previous outage remains recorded honestly.
- [x] Refresh only the two changed artifact pins after content verification;
  all 17 pins match. OpenAPI remains
  133aae117333e66b40662ec4fdb47fc02ee08e7aeecbbd9cbb200d5468ca7362.
- [x] Scope: only tests, HTTP exchanges, manifest, trace and this plan changed;
  no staging/commit/push/PR; outside-repository runtime/report evidence.
- [ ] Independent third review and human acceptance (PENDING).
- [ ] Applicable final-SHA CI and explicit subsequent workflow authorization.

Latest candidate-manifest SHA-256:
`1b4a4b43df6052db5d91840cb2e748745cafb0529a766272d5a29b2b88e6dbac`.
Current status is READY_FOR_THIRD_REVIEW, not ACCEPTED or COMPLETE. Latest
commands, hashes, evidence directory and limitations are in trace section 12.
