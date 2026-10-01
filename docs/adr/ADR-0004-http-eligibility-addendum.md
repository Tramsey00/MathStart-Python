# ADR-0004: HTTP, immutable revisions and cross-attempt eligibility

- **Status:** Proposed
- **Date:** 2026-09-30
- **Primary owner:** Руслан
- **Reviewer / Task Approver:** Владимир
- **Baseline:** MathStart Technical Specification v7.1 · G0 ACCEPTED
- **Related task:** MS7-R02A, G1 contract closeout
- **Spec:** `../../specs/api/MS7-R02A-http-eligibility.md`
- **Plan:** `../exec-plans/active/MS7-R02A-http-eligibility.md`
- **Supersedes:** none; ADR-0002 and R02 remain accepted/frozen

## Context

R02 establishes four exercise modes, public/server separation, typed ordered
steps and version binding. It deliberately defers concrete HTTP/revision and
persistence protocols. v7.1 assigns D-022/023 to an independently accepted
addendum before clients. Accepted I01 describes the needed UX distinctions but
does not define endpoint semantics. No runtime implementation is part of R02A.

## Proposed decision

Use one OAS 3.1 JSON artifact for every §11 route, a reusable JSON Schema
2020-12 bundle, machine-readable operation policy and valid/invalid fixtures.
Retain R02 names, modes/types and single version counter; add equal `version`
alias, UUID immutable ExerciseVersion identity, numeric difficulty and safe skill
and help metadata. Keep dynamic student payload untrusted and shape-validated.
New resource UUIDs do not replace existing ContentPage IDs/slugs.

D-022 adds full-draft expected_revision replacement, immutable SUBMITTED
snapshots and new previous_attempt_id-linked corrections. Exposure is shared by
user+version and serializes help/submit/finalization. Help committed before
eligibility finalization disqualifies independence; completed decisions are not
revoked by later help. Hint/reveal history survives new attempts. A permanent
user/version guard permits at most one positive event; neutral completions remain
history without inventing negative evidence. No new Progress formula or event.

D-023 adds Session+CSRF, typed success/error envelopes, safe owner 404,
stable cursor pagination, mutation receipts/digests and explicit conflict/retry
behavior. Exact retries replay prior operation/result before state/revision
checks; changed digest conflicts. Receipt retention >=7 days is independent of
permanent domain uniqueness. 202 is restricted to an identifiable persisted
SUBMITTED attempt with canonical GET status route. Unsupported/fallback remain
successful business states as §11 requires.

## Rationale and alternatives

This boundary permits backend/frontend implementation from one artifact rather
than inferred fixtures. JSON avoids a new YAML dependency; existing locked
jsonschema validates official OAS structure and public schemas offline. A single
bundle with named definitions avoids competing schema ownership. Generated wire
fixtures plus manually specified scenario expectations test the actual artifacts.

Reopening frozen R02 is rejected because its accepted scope is correct. A
receipt-only dedupe scheme is rejected because expiry would allow repeated
credit. Per-attempt exposure is rejected because new attempts would evade help.
Freezing independence irrevocably at pending submit is rejected because reveal
before finalization could otherwise evade eligibility. A new service/queue/DRF
stack is deferred to scoped downstream work.

## Consequences and preserved invariants

Published version, submitted order, completion eligibility and positive-credit
facts need durable constraints/transactions in V04–V06/V08. Schema validates
shape, not mathematical truth or secrecy of free prose. Only Progress owns
long-term projections; all R03 numerical rules remain unchanged. Help is recorded
before disclosure; full reveal content exists only in the explicit reveal shape.
LLM/provider output cannot promote independence or author progress.

No schema or persisted-data impact in this task. Runtime implementation requires
additive reviewed Django migrations and PostgreSQL concurrency/fresh-install
evidence; the reference oracle establishes legal serial outcomes only. Existing
content and historical evidence are untouched. Rollback reverts task-owned
contract/check files without touching content or evidence.

## Verification and security

Task suite validates OpenAPI structure, refs, all routes, public field allowlists,
auth/CSRF/owner constraints, version/revision/digest preconditions, receipt expiry,
race outcomes and one-positive. Run unchanged canonical verify_repo.py, existing
R03 tests and scoped diff review. Separate CI step adds the contract suite without
changing the eight established checks. Health has explicit non-sensitive fields;
foreign 404 reveals no revision; fixtures use synthetic identities. Publication
and reviewed hint-bank gates remain necessary for answer-equivalent text.

## Human gate and follow-up

**Reviewer / Task Approver:** Владимир. **Decision:** PENDING.
**Review date:** not recorded. No approval, CI or merge is inferred.
Accept the proposed D-022/023 contract and exact OpenAPI digest before V02/I02.
Downstream: MS7-V02/V03/V04/V05/V06, MS7-I02, MS7-R09/R10/R11/R12.
R03A owns CompletionFact/replay addendum; this ADR does not implement it.

## Status history

- 2026-09-30 — Proposed for MS7-R02A review against canonical v7.1.
