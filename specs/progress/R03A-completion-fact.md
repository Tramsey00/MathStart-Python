# SPEC MS7-R03A: CompletionFact / progress-v1.1 addendum

- **Status:** Implemented contract candidate; independent human acceptance PENDING
- **Owner:** Руслан; reviewer / Task Approver: Владимир
- **Last updated:** 2026-10-02
- **Issue:** [#18](https://github.com/Tramsey00/MathStart-Python/issues/18)
- **ADR:** [ADR-0005 / D-021](../../docs/adr/ADR-0005-completion-fact.md), Proposed
- **Plan:** [active MS7-R03A](../../docs/exec-plans/active/MS7-R03A-completion-fact.md)
- **Trace:** [MS7-R03A](../../docs/agent-traces/MS7-R03A.md)
- **Direct CONTRACT dependency:** [frozen R03](R03-progress-contract.md)
- **Numerical authority:** [BASELINE-v1](BASELINE-v1.md), unchanged
- **Canonical authority:** task owner's supplied v7.1 requirements; corrected §20
  deadline 05.10.2026 supersedes old card Target deadline 02.10

## 1. Goal and scope

A completed attempt can enter recent-ten without fabricating ProgressEvent,
negative evidence or misconception. This is an additive pure contract package:
schema, synthetic fixtures, reference and tests. There are no Django models,
migrations, DB tables, runtime services, HTTP endpoints, auth/frontend changes,
provider calls or dependencies. Exercise modes and frozen R02/R02A/R03 contracts,
OpenAPI, references, tests and historical fixtures remain unchanged. The R02A
candidate manifest refreshes only its derived CI workflow hash for the authorized
new step, retaining every other hash and pending acceptance marker.
The historical missing PDF observation and R02A stale PENDING
markers are nonblocking housekeeping; no PDF inspection or acceptance is inferred.

## 2. Ownership and immutable boundary

Assessment owns authoritative CompletionFact. Progress owns completion mirror/
replay and never imports Assessment ORM:

    Assessment CompletionFact -> immutable DTO -> Progress completion mirror

Assessment target fields are immutable completion_id, attempt, skill, outcome,
independent flag, completed_at and policy_version, with UNIQUE(attempt, skill).
The DTO uses attempt_id/skill_id references and names the flag independent_correct.
Supplemental user_id binds the owner; it replaces neither identity constraint.
This internal DTO has no public write API or answer/validation secret payload.

The schema is [completion-fact-v1.schema.json](schemas/completion-fact-v1.schema.json).
The implementation-stage request's preferred descriptive filename supersedes the
plan's earlier completion-v1.schema.json placeholder. Fixture filenames stay as
planned. Schema artifact version v1 is distinct from the recorded policy field;
completion_version is not an envelope field.

| Required immutable field | Contract |
| --- | --- |
| completion_id | Globally unique canonical lowercase UUID, assigned by Assessment and never regenerated on delivery/retry |
| user_id | Nonempty owner reference |
| skill_id | Nonempty Skill reference; the pilot oracle checks frozen pilot codes |
| attempt_id | Nonempty immutable source reference; native server UUID/FK binding belongs to V08, synthetic legacy references remain supported |
| outcome | Exactly CORRECT, WRONG, UNSUPPORTED or INDETERMINATE |
| independent_correct | Strict boolean; true requires CORRECT and separately verified frozen eligibility |
| completed_at | Aware RFC3339, uppercase T/Z or signed valid offset, at most six fractional digits; valid calendar; UTC canonical microseconds |
| policy_version | Exactly progress-v1.1 |

The schema is closed (additionalProperties=false), has all eight required fields,
and checks shape/enum/precision. Use a date-time format checker for calendar
validation. Tests provide a local datetime checker, without network/optional
format packages. The domain oracle reuses frozen utc_instant, additionally rejects
invalid RFC3339 offset ranges and checks known skills, independence and identities.
It never silently truncates time precision or defaults a missing flag/outcome.

CompletionFact policy_version=progress-v1.1; frozen ProgressEvent
policy_version=progress-v1; native final state reducer_version=progress-v1.1.
No other numerical policy is registered or silently substituted.

## 3. Dual identity, conflict and atomic ingestion

Both global completion_id uniqueness and permanent (attempt_id, skill_id) source
uniqueness apply before projection filtering. A user/policy/receipt namespace
cannot hide collisions. Facts of an attempt across skills must agree on owner
and terminal instant. Source identity outlives receipt expiry.

Compare all canonical fields after UTC normalization:

- same complete canonical payload -> idempotent no-op, one mirror entry;
- reused completion_id with changed source/payload -> IdentityConflict;
- reused attempt/skill with a new completion_id or any changed immutable field
  -> IdentityConflict;
- unsupported policy/malformed DTO -> ContractError, no accepted change.

Different timestamp spellings of the same instant can be exact canonical retries.
Never overwrite accepted facts. ingest_completion_fact returns a detached proposed
mirror, projection and duplicate flag; rejection leaves caller inputs unchanged.
For target ingestion the candidate's user/skill must match NumericalReplay scope.
Full replay may contain other scopes; both constraints remain global before
selecting the user's skill. There is at most one recent entry per attempt/skill.

## 4. Authority and lifecycle

validate_completion_fact checks shape/domain content only and grants no authority.
Nonempty mirror replay/ingestion requires separately supplied trusted context:

    {
      "context_version": "assessment-completion-v1",
      "records": [
        {
          "fact": "<full authoritative eight-field DTO object>",
          "attempt_state": "COMPLETED",
          "mapped_skill_ids": ["negative_numbers"]
        }
      ]
    }

The fact placeholder above denotes an object, not a wire string. Exact DTO
agreement with the source record, completed state and explicit bound-version
mapping are required. Unknown context fields/version, missing authority, changed
owner/outcome/independence/time/policy or unmapped skill fail closed. Context is
fixture/service input, not extra persisted CompletionFact fields or proof of
client authentication. The pure oracle can compare supplied records only; V08
must establish genuine server provenance, authorization, FK/owner binding,
version/snapshot and transactional finalization. Client flags cannot grant it.

Native assessed COMPLETED attempts produce facts. STARTED, SUBMITTED/202,
ABANDONED and SELF_CHECK REVIEWED do not. CORRECT, WRONG, UNSUPPORTED and
INDETERMINATE are outcomes, not lifecycle states. R02A integration fixes eligibility
under exposure/positive-credit finalization: pending help affects the result,
later help cannot revoke it, repeated credited CORRECT stays neutral. The test
package composes unchanged R02A serial fixtures to check those recorded decisions;
it implements no second eligibility algorithm, source producer or credit award.

## 5. Recent-ten and status

Build recent-ten exclusively from the Progress mirror. Select user/skill facts,
order ascending by (canonical UTC completed_at, case-sensitive lexical attempt_id),
take the final ten, return IDs ascending and sum true independent_correct once
per retained source. Neutral facts occupy slots. No positive-only filter, event
double counting or time decay is allowed. Old out-of-window facts remain retained.

Outcome is required regardless of neutrality. Neutrality means no numerical
projection authority; even a true independent CORRECT fact alone cannot change
numbers. UNSUPPORTED/INDETERMINATE and repeated CORRECT create history without
fake WRONG/DIAGNOSTIC_WRONG events.

Use unchanged frozen status_for:

1. evidence_count == 0 -> NOT_STARTED;
2. mastery >= 80, confidence >= 60, recent independent >= 3 -> MASTERED;
3. mastery < 50, confidence >= 30 -> WEAK;
4. otherwise LEARNING.

Canonical v7.1 already permits status-only replay. A newer neutral fact may evict
an independent attempt and change MASTERED -> LEARNING, preserving mastery,
confidence, evidence_count and last_updated byte-for-byte for a fixed event log.
Fact-only history retains zero numbers/count, null time and NOT_STARTED.

## 6. Numerical replay and late delivery

NumericalReplay(events, user_id, skill_id) validates/copies the complete event log
and calls frozen R03 replay once. Immutable JSON-backed cache content detaches
caller inputs/results. Its result includes literal v1 diagnostics/snapshots.
No numerical constants or algorithm are copied into R03A.

replay_v1_1 constructs that cache and combines it with the full validated mirror.
replay_completion_facts and ingest_completion_fact reuse a NumericalReplay;
late fact ingestion never invokes numerical replay. They validate authority and
coexistence, derive recent-ten and update only final status/reducer_version.
A genuine late event explicitly constructs a new cache under frozen event order
(occurred_at, event_id, policy_version), then recombines the mirror.

For fixed events, any valid fact delivery/permutation preserves numerical values,
evidence_count, last_updated, all event IDs, numerical snapshots/deltas and repeat
reset points. Independent facts never clear misconception counters. Qualifying
ProgressEvent alone still resets them in occurrence order even with a delayed fact.

Late facts can enter/evict from recent-ten and change independent count/status.
There is no relation required between completed_at and occurred_at. Complete
accepted sets yield identical output regardless of delivery order; conflicting
sets reject in both orders rather than claiming a successful common projection.

Native output contains six-field state, recent_window, ordered/applied/
nonprojecting_event_ids, legacy_snapshots and completion_gaps. legacy_snapshots
is explicitly literal v1 compatibility diagnostic data, not native history or
as-of completion snapshots. completion_gaps lists scoped attempts with inline
completion attestation but no mirror record; it supplies no window membership.

## 7. ProgressEvent coexistence

Frozen event envelopes, identities, validator and duplicate-log rejection remain
unchanged. Nonnull inline completion time must match its separate fact after UTC
normalization; missing time on allowed negative/reveal events is not a conflict.
Events retain frozen required inline attestations, which cannot populate native
recent-ten. Missing fact delivery can coexist with numerical projection.

Check owner agreement for a shared attempt. CORRECT_FIRST_TRY and unassisted
DIAGNOSTIC_CORRECT require matching CORRECT/true final fact; helped correct
requires CORRECT/false; DIAGNOSTIC_WRONG requires WRONG/false. Wrong intermediate
steps do not identify final outcome. A later reveal cannot revoke finalized
independence. Contradictions reject atomically without fabricated events.

## 8. Explicit legacy import and executable parity

The frozen v1 entry points/results remain literal historical oracles. Native
replay never silently imports inline completion. import_progress_v1_completions
requires context_version=legacy-completion-v1 with explicit source DTOs, mapping
and attempt_state=LEGACY_COMPLETION. That state is compatibility provenance,
not a new native lifecycle state or outcome. Stable ID/outcome come from this
explicit versioned metadata, never from a wrong step, reveal or false flag.

The importer validates frozen replay, matches supplied source DTOs to nonnull
inline completion sources/times/owners and frozen event-derived independence,
then mirrors them. Missing metadata fails; callers can explicitly retain the
unchanged v1 entry point instead. Extra context rows grant no implicit history.
Legacy synthetic IDs/credit semantics are not retrofitted to native R02A rules.

[progress-v1.1-parity.json](fixtures/progress-v1.1-parity.json) pins the frozen
fixture's SHA-256 and all three case IDs, with explicit authoritative synthetic
metadata, including reveal-only INDETERMINATE. This outcome is supplied, not
inferred. All three arithmetic cases also remain in executable parity coverage.
Tests compare literal old expected state, native numbers/status/time, equivalent
window/count, event IDs/order/application and every legacy snapshot. Only native
reducer_version differs; completion_gaps is empty for equivalent delivered sets.
No event payload or recorded event policy is rewritten.

## 9. Artifacts, tests and gate

- [completion-v1-cases.json](fixtures/completion-v1-cases.json): all 32 named plan
  cases, shared synthetic datasets and explicit variants/delivery/context inputs.
- [completion-v1-invalid.json](fixtures/completion-v1-invalid.json): 33 malformed
  shape/domain cases; schema_invalid distinguishes shape from domain rejection.
- Parity file above: three frozen streams and three arithmetic cases.
- [Pure reference](../../scripts/r03a_contract_reference.py) and
  [independent assertions](../../tests/test_r03a_contract.py).

Required checks: R03A, unchanged R03 and R02A suites; verify_repo.py; pip check;
makemigrations --check --dry-run; git diff --check and scoped review. CI adds an
R03A contract step beside existing R02A without changing canonical selection.
Configuration/local checks are not a GitHub CI pass or PostgreSQL persistence
proof. Trace records actual results and any failures, not inferred acceptance.

Acceptance requires all plan cases, dual-key/owner isolation, required outcomes,
UTC ordering, <=10 window, late permutations, no fake events, cached numerical
neutrality, explicit 100.00/67.00/11 MASTERED -> LEARNING eviction, repeat/reset
isolation and full frozen fixture parity. Independent human gate remains PENDING;
ADR stays Proposed, plan stays active, Issue stays open. No push/PR/merge occurs
in this authorized stage. V08 provenance/FKs, durable delivery, locking, backfill
and migration/fresh-install evidence remain downstream limitations.
