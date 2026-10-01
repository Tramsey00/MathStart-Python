# ADR-0005 (D-021): Immutable CompletionFact beside frozen ProgressEvent

- **Status:** Proposed
- **Date:** 2026-10-02
- **Owner:** Руслан
- **Reviewer / Task Approver:** Владимир
- **Related task:** [MS7-R03A / Issue #18](https://github.com/Tramsey00/MathStart-Python/issues/18)
- **Relation:** FOLLOW-UP / ADDENDUM TO FROZEN R03
- **Target reducer:** progress-v1.1; event numerical policy remains progress-v1
- **Inputs:** [ADR-0003](ADR-0003-knowledge-progress-semantics.md),
  [R03](../../specs/progress/R03-progress-contract.md),
  [baseline](../../specs/progress/BASELINE-v1.md),
  [R02A](../../specs/api/MS7-R02A-http-eligibility.md)
- **Plan / audit:** [MS7-R03A](../exec-plans/active/MS7-R03A-completion-fact.md)
- **Human approval:** PENDING; this draft authorizes no runtime implementation

## 1. Context and evidence

The accepted R03 contract explicitly identifies the event-free Assessment
completion path as an integration gap. Its pure reference has no independent
completion input. validate_event() normalizes inline completed_at and requires
it for correct/diagnostic results. replay() creates its attempt dictionary only
while visiting events. _recent_attempts() and _state_dict() then derive history
and status from that dictionary. An independent correct event both marks
history and clears misconception repeat counters. ingest_event() accepts only
events. The exact source/test map is in the task plan.

R02A finalizes immutable submitted work and eligibility on the server. A second
correct attempt for an already credited user/version remains completed and
CORRECT, without another positive event. UNSUPPORTED/INDETERMINATE and other
neutral assessed completions likewise need history without fabricated penalties.
These facts must be representable even if no ProgressEvent exists.

R03 is accepted/frozen. R02A is present in baseline main at 428ece7, but its
ADR/spec/policy/manifest still record Proposed/PENDING. This draft uses its
repository terminology without claiming its human gate is accepted. The v7.1
task card is named in the active plan but not stored in Git; the historical PDF
path in the R02A trace was unavailable during this audit. The supplied R03A task
request defines this stage; Vladimir must reconcile upstream acceptance and the
canonical task card before accepting the implementation contract.

## 2. Proposed decision and ownership

Assessment owns authoritative terminal attempt, bound immutable exercise
version, submitted snapshot, help/exposure and finalized eligibility facts.
It produces one immutable CompletionFact per relevant user/skill/attempt.
Progress validates and consumes those facts through its service boundary and
alone derives UserSkillState and recent history. Progress does not import
Assessment ORM models; producer verification uses supplied validated context.
Tutor, Analyzer, frontend and provider code cannot author completion eligibility.

Keep two separate immutable inputs:

- ProgressEvent log: numerical evidence, existing identities and frozen reducer;
- CompletionFact ledger: completed-attempt membership and independent-correct
  status input, with no numerical event authority.

This is an internal contract addendum. There is no new event kind, endpoint,
DTO change, app, dependency or schema migration in the audit/design stage.

## 3. Identity and minimal envelope

The domain identity is the ordered tuple (user_id, skill_id, attempt_id).
Completion time, independent_correct and completion_version are immutable
payload, never identity components.

| Candidate | Assessment |
| --- | --- |
| attempt_id + skill_id | Sufficient with a globally unique owned Attempt, but implicit user scoping obscures the per-user Progress boundary |
| user_id + skill_id + attempt_id | Selected: explicit projection scope; one fact per skill for a multi-skill attempt; direct duplicate/conflict key |
| fact_id + source identity | A second identifier still needs source uniqueness and permits retry duplication without it; no current consumer needs it |

R02A's server UUID Attempt has one owner and one immutable ExerciseVersion
binding. The triple is not permission to reuse an attempt under another user:
native ingestion must verify attempt_id -> owner against Assessment context.
The same attempt's per-skill facts must have the same terminal completion instant.
Skills must belong to that attempt's bound version's skill mapping. A correction
has a new attempt_id; previous_attempt_id never merges the two attempts.

The exact proposed closed envelope has six required fields, no optional fields:

    {
      "completion_version": "completion-v1",
      "user_id": "student-1",
      "skill_id": "negative_numbers",
      "attempt_id": "attempt-neutral-1",
      "completed_at": "2026-10-02T09:00:00.000000Z",
      "independent_correct": false
    }

| Field | Validation and purpose |
| --- | --- |
| completion_version | Exactly completion-v1 in this revision; completion schema version, separate from event policy_version and exercise contract_version |
| user_id | Nonempty stable string; must equal the authoritative Attempt owner |
| skill_id | Nonempty stable Skill reference, using the existing R03 code convention; must be known and mapped by the bound version |
| attempt_id | Nonempty stable string in pure/reference and historical data; native R02A producer uses the canonical lowercase UUID from the server Attempt |
| completed_at | Required aware RFC3339 instant, 0–6 fractional digits, normalized to UTC with exactly six digits and Z, using R03 utc_instant semantics |
| independent_correct | Strict boolean, required, no truthy coercion or missing-value default; copied from verified finalized Assessment eligibility/correctness |

Unknown fields, missing fields, unsupported versions, malformed/calendar-invalid
or overprecise timestamps, wrong ownership/mapping and inconsistent authority
fail closed before committing any ledger/projection change.

No fact_id, event_id, evidence_ref, source_kind, difficulty, answer payload,
misconception data or receipt key is needed. attempt_id already identifies the
immutable version/snapshot/finalization source. Source provenance and source
schema/digest belong to the separately verified Assessment/import context,
not a caller-written authority flag in the envelope. completion_version supplies
the one additional version needed for a standalone completion record.

## 4. Authority, lifecycle and R02A terminology

Native facts are emitted only after an assessed Attempt reaches COMPLETED and
its outcome/eligibility/completed_at have been finalized. SUBMITTED, a HTTP 202,
STARTED, ABANDONED, and SELF_CHECK REVIEWED do not emit native CompletionFacts.
REVIEWED remains history in Assessment; it is not renamed COMPLETED. Historical
progress-v1 reveal-only completion entries are preserved by the compatibility
adapter in section 8.

For each mapped skill, independent_correct is true only when supported validated
CORRECT work for that skill has the server's frozen independent eligibility.
That eligibility includes R02A's user/version exposure, no earlier help/reveal,
and no prior positive credit, decided under finalization serialization. Unassisted
supported diagnostics can qualify; helped diagnostics cannot. Repeated credited
correct work, revealed work, UNSUPPORTED and INDETERMINATE completions use false.
False means ineligible for the window's independent-correct count, not WRONG.

Help during SUBMITTED participates in finalization; help after COMPLETED cannot
rewrite its decision. Reading current mutable Exposure during a retry must not
replace the stored completed eligibility. CompletionFact neither awards nor
reserves positive credit, and cannot bypass the permanent user/version guard.

A native ingestion API is internal and requires separately supplied trusted
Assessment context establishing owner, bound version/mapping, completed state,
frozen instant and per-skill verdict/eligibility. It compares every fact field
with those immutable records. A JSON source_kind=ASSESSMENT or an authority=true
marker supplied by a client proves nothing. Pure tests model this context with
synthetic server records; they prove validation logic, not authentication or
PostgreSQL transactions. No public CompletionFact write API is proposed.

## 5. Ordering, history and derived status

For one user/skill, deduplicate by identity, select all completed facts, sort
ascending by (UTC completed_at, attempt_id), and take the last ten. Return
attempt_ids in that same ascending order. Identifier comparison is deterministic
case-sensitive lexical string order as in the R03 reference, not database locale
collation; native UUIDs use their canonical lowercase representation.

Count each retained fact's true independent_correct once. A fact appears once
regardless of how many events, evidence units or HTTP receipts its attempt has.
No elapsed-time decay, filtering out neutral attempts, or positive-only window
is permitted. Per-user and per-skill windows remain separate.

Only Progress recomputes status using the frozen precedence:

1. evidence_count == 0 -> NOT_STARTED;
2. mastery >= 80.00 and confidence >= 60.00 and recent independent count >= 3
   -> MASTERED;
3. mastery < 50.00 and confidence >= 30.00 -> WEAK;
4. otherwise -> LEARNING.

Neutral eviction can therefore change MASTERED to LEARNING while numerical
knowledge remains unchanged. A neutral-only ledger keeps 0.00/0.00, count 0,
last_updated null and NOT_STARTED even though history has entries. An
authority-validated independent fact with no delivered event can add an
independent history entry but cannot initialize numerical evidence.

## 6. Combined replay, late facts and numerical isolation

Native progress-v1.1 replay takes two explicitly separate inputs: the complete
accepted event log and the complete accepted CompletionFact ledger, plus the
trusted producer context needed to validate native facts. Delivery order is not
a reducer input.

Proposed reference sequence:

1. Validate/canonicalize both inputs and all identity/authority/coexistence
   constraints without mutating accepted state. Completion retries coalesce;
   invalid/conflicting combinations reject the proposed ingestion atomically.
2. Run the unchanged R03 numerical replay on the unchanged events, ordered by
   (occurred_at, event_id, policy_version). Use each recorded progress-v1 policy.
   Retain numerical values, repeat/reset behavior, projecting/nonprojecting
   event identities and last_updated from that replay.
3. Independently derive the recent window from CompletionFacts alone. Inline
   event completed_at is not a second native history source.
4. Combine numerical values with that independent count through the unchanged
   status_for formula. The six canonical state fields remain; native
   reducer_version is progress-v1.1, while event policy_version stays progress-v1.

For a fixed valid event log, adding a valid fact cannot change mastery,
confidence, evidence_count, last_updated, any per-event numerical delta/snapshot,
misconception counters/reset points, or the ProgressEvent log. The numerical
reducer must not read CompletionFact.independent_correct to clear repeat counters.
Resets continue at the existing independent correct ProgressEvent in occurrence
order, including when its separate fact is delayed. No fact-specific projecting
timestamp or synthetic ANSWER_REVEALED event is introduced.

A late fact re-derives final history/count/status from the full ledger. Its
completed_at may be earlier or later than event occurred_at; no relation between
the two timestamps is imposed. An old fact outside the last ten is retained but
does not change the window. A fact arriving before or after its event yields the
same final combined projection for the same complete inputs.

A genuine late/backfilled event still replays the numerical event log exactly
as frozen R03 requires, and can change numerical state. That change belongs to
the event, not to delivery of its CompletionFact.

Native final outputs are state (six canonical fields), recent_window
(attempt_ids, independent_correct_count), the three existing event-ID diagnostics
(ordered/applied/nonprojecting), and completion_gaps (sorted attempt IDs with
inline completion attestations but no separately delivered fact). The gap
diagnostic is not a new UserSkillState field and grants no history membership.
Historical event snapshots returned by the v1 reference remain compatibility
diagnostics; they must not be advertised as v1.1 completion history snapshots.
A historical/as-of completion ledger is outside this contract.

## 7. Duplicate/conflict and ProgressEvent coexistence

Canonicalize timestamps before comparison. Exact same identity and all six
canonical fields equal -> idempotent no-op for the ledger, returning its current
derived projection. Offset/Z variants of the same instant are exact canonical
duplicates. Same identity with changed time or independent flag -> conflict;
never overwrite the original. Version is not a new identity namespace: an
unsupported version fails validation, and a different registered version under
the same identity must conflict. Batch replay of completion deliveries coalesces
exact retries too.

Keep ProgressEvent identities unchanged: globally unique event_id, unique
(attempt_id, skill_id, event_kind, evidence_ref), and the existing evidence-unit
and negative-penalty checks. R03's immutable-log replay rejects duplicate events;
its ingestion API deduplicates exact event retries. Completion duplicate rules
must not weaken this distinction or alter event payloads during ingestion.

For a shared user/skill/attempt:

- inline nonnull ProgressEvent.completed_at must equal CompletionFact.completed_at
  after UTC normalization; disagreement rejects the combined candidate;
- missing inline completion metadata on a permitted negative/reveal event is not
  a disagreement; a separate valid fact may provide history membership;
- correct/diagnostic events retain frozen R03's required inline completion
  attestation and eligibility validation. Removing it would silently change
  accepted event validation/identity and is not this proposal;
- native producer context must reject a final-result eligibility contradiction,
  such as CORRECT_FIRST_TRY with a false CompletionFact verdict or an independently
  true fact with a helped final result. Intermediate wrong-step evidence alone
  does not determine the terminal verdict;
- a later reveal does not revoke the completed independent flag. Producer context
  establishes finalization/help order; do not infer it from delivery order or
  impose a completion-versus-occurrence constraint;
- an event without its separate fact may project numerically, but occupies no
  native recent entry until the fact arrives. completion_gaps makes delay visible.

No fallback from inline event metadata is allowed in native mode. This permits
late independent facts to change the window without re-running a different
numerical policy. There is one completion ledger entry and one history source.

## 8. Explicit progress-v1 compatibility

Preserve all frozen files, constants, event envelopes and immutable identities.
Keep the old replay/ingest entry points and their full progress-v1 output
unchanged. Their six-field state, window, event lists and snapshots remain the
literal legacy fixture oracle, including reducer_version=progress-v1.

A separately named legacy import adapter validates the whole log with that
oracle and materializes one completion-v1 fact per tuple with a nonnull inline
completed_at. It checks normalized same-attempt times and derives independence
exactly from accepted R03 event-order eligibility: unhelped/unrevealed
CORRECT_FIRST_TRY or DIAGNOSTIC_CORRECT, with no invalid earlier reveal.
Absence of completion metadata creates no fact. Preserve reveal-only completions
and R03 synthetic string identifiers; do not retrofit R02A UUID/version/credit
rules onto old evidence. Import provenance is explicitly legacy_progress_v1 in
trusted adapter context, not a fabricated Assessment verdict.

Then replay the unchanged events plus that explicit imported ledger through
progress-v1.1. With no extra neutral facts, require parity for mastery,
confidence, evidence_count, status, last_updated, recent IDs/count, event ordering,
event application and numerical snapshots. The deliberate metadata difference
is native reducer_version=progress-v1.1. The unchanged legacy entry point still
passes every original expected six-field fixture literally. Never rewrite an
event's policy_version or payload to disguise this version distinction.

Exact imported/native completion agreement coalesces. A native fact that
disagrees with an already accepted historical completion is a conflict requiring
reconciliation, not an overwrite or a new numerical interpretation. Native
mode never invokes the importer implicitly; otherwise a missing late fact would
silently repopulate history and hide the integration boundary.

## 9. Frozen and affected architectural invariants

All eight event kinds, deltas, difficulty bands/coefficients, misconception
repeat coefficients/reset rules, evidence_count semantics, status thresholds
and precedence, exact Decimal per-event clamp/ROUND_HALF_UP, no time decay,
reveal/misconception/independent-evidence semantics, and event identity/penalty
rules remain unchanged. Only Progress owns long-term projections.

ARCHITECTURE sections 17.1 and 42.7 currently state that every automatic progress
change has a ProgressEvent. D-021 proposes this narrowly explicit refinement:
every numerical knowledge-state change requires validated ProgressEvent evidence;
recent-window and its consequent status change can instead be explained by
immutable validated CompletionFacts. No other projection writer is introduced.
After acceptance, current architecture/operating wording needs a scoped note
linking D-021. Frozen R03 and historical ADRs must not be rewritten. The current
draft records the conflict rather than claiming the broader invariant already
permits status-only completion changes.

## 10. Alternatives and consequences

Rejected: a neutral ProgressEvent kind, fake WRONG/DIAGNOSTIC_WRONG/reveal,
filtered positive-only window, merging deliveries into event occurrence order,
CompletionFact-driven misconception reset, caller-authored independence,
automatic inline fallback, identity containing completed_at, overwriting duplicate
payloads, and receipt-only deduplication. Each either changes frozen numerical
semantics, conceals neutral completions, or makes retries/order untrustworthy.

Deferred: removing inline completion attestations from future event envelopes,
extra fact IDs, public write DTOs, queues and physical ORM schema. They are not
needed to close this history-input gap and require their own reviewed contracts.

Benefits: neutral and delayed history is expressible, retries are deterministic,
numeric replay remains independently reproducible, and eligibility is auditable.
Costs: two validated inputs must be delivered/reconciled; status may change with
unchanged last_updated, and clients must understand last_updated as the last
numerical projection event, not the last history/status refresh. The current
R03A implementation contract remains unimplemented; no executable parity claim
is made for this design alone.

## 11. Future V08 persistence, security and rollback

No schema or persisted-data impact in this audit. For V08, Assessment must retain
the immutable completed snapshot, eligibility/version source and completion
instant; Progress may store a validated immutable completion ledger/read
projection with FK/ownership checks and permanent domain uniqueness. The physical
location and redundant owner representation require a reviewed Django design.
Any ledger uses unique user/skill/attempt plus authoritative Attempt ownership
and cross-skill completion consistency; a second per-attempt source must not be
able to disagree silently.

Future work needs additive reviewed migrations, conflict-reporting backfill,
clean PostgreSQL migration/fresh-install checks and concurrency tests for
finalization, one-positive reservation, event/fact delivery and projection.
Keep short atomic transactions; computation/provider calls remain outside locks.
Late delivery may reconcile a gap but must not lose the durable source record.
HTTP receipt expiry cannot erase completion identity, snapshot or positive-credit
guards. Bootstrap never touches attempts, events or completions.

Protect owner scopes and validation secrets; preserve raw submitted work in
Assessment. Store only necessary references/verdict in completion records.
Never log credentials or expose private authority context through an error.
Malformed/unauthorized facts fail without creating negative evidence. No live LLM
or new dependency is needed for pure contract verification.

Current rollback reverts only the three task-owned documentation artifacts.
Future rollback must retain the event log and completion ledger/provenance, can
rebuild a progress-v1 projection through its explicit compatibility entry point,
and must disclose that event-free neutral entries will be absent from that old
window. Do not delete historical facts or mutate numerical evidence to imitate
v1.1 status; prefer forward fixes for persisted conflicting evidence.

## 12. Verification, human gate and follow-up

The plan defines the exact future schema/spec/reference/test files and fixture
matrix, including neutral eviction 3 -> 2, late independent facts, event repeat
isolation, authority rejection, conflicts and delivery permutations.
For this stage, run canonical verify_repo.py, unchanged R03/R02A suites, diff
whitespace/scope checks and document-link review. Record actual versions and
limitations in [the trace](../agent-traces/MS7-R03A.md). Existing checks prove the
unchanged repository baseline, not the proposed CompletionFact implementation.

**Reviewer / Task Approver:** Владимир.
**Decision:** PENDING. **Review date:** not recorded.
Review identity/envelope, native authority and COMPLETED-only membership,
event-driven repeat reset, explicit compatibility/version distinction, and the
status-only architectural refinement. Reconcile R02A acceptance and the canonical
v7.1 task card. Draft readiness and a documentation commit are not acceptance.
Do not mark this ADR Accepted, move the active plan, close Issue #18, create/merge
a PR or treat this candidate as frozen upstream.

After design review, implement the pure progress-v1.1 addendum and executable
parity package in the plan's sequence. V08 and R11 remain downstream of their
separate required human gates.

## Status history

- 2026-10-02 — Proposed after repository audit; audit/design READY FOR REVIEW,
  implementation and human approval PENDING.
