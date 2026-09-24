# SPEC R03: ProgressEvent and UserSkillState Contract v1

- **Status:** Accepted
- **Owner:** Ruslan; backup Vladimir
- **Related issue:** https://github.com/Tramsey00/MathStart-Python/issues/6
- **Numerical authority:** `specs/progress/BASELINE-v1.md` (unchanged)
- **Related ADR:** `docs/adr/ADR-0003-knowledge-progress-semantics.md`
- **Related exercise contract:** `specs/exercises/R02-exercise-architecture.md`
- **Fixture:** `fixtures/progress-v1-cases.json`
- **Reference/checks:** `scripts/r03_contract_reference.py`, `tests/test_r03_contract.py`

## Boundary and terminology

`ProgressEvent` is the sole current progress-evidence event name. Earlier `KnowledgeEvent` wording in historical artifacts is superseded terminology, not a second persisted type. Only Progress accepts validated evidence and changes long-term `UserSkillState`. Assessment supplies attempt/hint/reveal and validation facts; Analyzer supplies only confidence-gated, controlled misconception evidence. A wrong final result alone cannot identify a misconception. Unsupported parsing is not an assessed wrong attempt or misconception. Tutor, frontend and LLM provider code cannot write the projection.

This contract and its reference code are pure, versioned domain examples. They do not create Django models, migrations, services, database rows, endpoints, or runtime seed data. Later persistence must enforce the same invariants transactionally and protect historical events from bootstrap.

## Event envelope and validation

An accepted `ProgressEvent` has these immutable fields:

| Field | Meaning |
| --- | --- |
| `event_id` | Globally unique, stable string identity; also a deterministic order component |
| `user_id`, `skill_id` | Student and stable Skill reference; the reference fixture uses Skill code as `skill_id` |
| `event_kind` | One of the eight baseline kinds below |
| `occurred_at` | Timezone-aware UTC instant, serialized as RFC 3339 with `Z` |
| `policy_version` | Recorded projection policy, `progress-v1` in this phase |
| `attempt_id` | Required for attempt-derived assessed/reveal events; absent for self-report |
| `evidence_ref` | Stable validated source evidence identity; required for attempt-derived events |
| `difficulty` | Required for assessed events; numeric 1-4 or R02 string easy/medium/hard |
| `misconception_code`, `confirmed` | Controlled code and true confirmation required only for `MISCONCEPTION_DETECTED` |
| `source_kind` | Supporting source class; a misconception needs a validated step, domain, or structured-field source, not a wrong final answer alone |
| `independent_evidence_rule` | If two different negative evidence units in one attempt both project, both records must carry `distinct_validated_steps` from Assessment |
| `hint_used`, `reveal_used` | Server-validated attempt facts, never trusted from a client assertion |
| `completed_at` | Optional immutable Assessment completion fact for that attempt/skill; timezone-aware RFC 3339 and normalized to UTC, see recent-window rule |

The eight kinds are `SELF_REPORTED_KNOWN`, `CORRECT_FIRST_TRY`, `CORRECT_AFTER_HINT`, `WRONG_ATTEMPT`, `MISCONCEPTION_DETECTED`, `ANSWER_REVEALED`, `DIAGNOSTIC_CORRECT`, and `DIAGNOSTIC_WRONG`. No additional R03 event kind is introduced. All accepted events require a supported recorded policy version. A missing field, invalid enum, malformed time, nonfinite number, unsupported policy, or inconsistent hint/reveal/first-try fact is rejected before changing the immutable log or projection.

For an attempt-derived event, Progress verifies source facts produced by Assessment/validation; the reference fixture supplies those facts directly. Correct and diagnostic result events require a completed attempt fact. `CORRECT_FIRST_TRY` requires no hint/reveal. `CORRECT_AFTER_HINT` requires a hint and no reveal. A full reveal before later purported independent correct work on the same attempt makes that work ineligible. Positive evidence copied after full reveal is rejected. `MISCONCEPTION_DETECTED` requires a controlled, confirmed code and a separate supporting evidence reference; an isolated wrong `FINAL_ANSWER` cannot supply it.

## Numerical baseline, unchanged

| Event | Mastery | Confidence |
| --- | ---: | ---: |
| `SELF_REPORTED_KNOWN` | initialize to 60 | initialize to 15 |
| `CORRECT_FIRST_TRY` | +6 | +5 |
| `CORRECT_AFTER_HINT` | +3 | +4 |
| `WRONG_ATTEMPT` | -2 | +3 |
| `MISCONCEPTION_DETECTED` | -5 | +5 |
| `ANSWER_REVEALED` | 0 | 0 |
| `DIAGNOSTIC_CORRECT` | +8 | +8 |
| `DIAGNOSTIC_WRONG` | -6 | +8 |

For assessed events:

```text
new_mastery = clamp(old_mastery + base_delta * difficulty_coeff * repeat_coeff, 0, 100)
new_confidence = clamp(old_confidence + confidence_delta, 0, 100)
```

Normalize numeric 1 or 2 -> `EASY`/0.8; 3 -> `MEDIUM`/1.0; 4 -> `HARD`/1.2. Normalize R02 strings `easy`, `medium`, `hard` to the same bands. There is no missing/invalid assessed-difficulty default. Confidence uses no difficulty or repeat multiplier. `repeat_coeff` is 1.0 for every event except confirmed misconception. The baseline has no time decay. Topic mastery remains the Content-owned topic-skill importance-weighted average and is outside this per-skill projection reference.

Use exact Decimal arithmetic. **After each accepted projecting event**, calculate both values, clamp each to `[0, 100]`, then `ROUND_HALF_UP` each to two decimal places before updating `UserSkillState`. Binary float is not normative. Self-report initializes 60.00/15.00; reveal leaves the state unchanged. Per-event rounding is part of replay, not only final display formatting.

## Evidence count, status and time

`UserSkillState` is unique by `(user, skill)`. Its canonical fields are `mastery`, `confidence`, `evidence_count`, `status`, `last_updated`, and `reducer_version`. Its initial values are `0.00`, `0.00`, `0`, `NOT_STARTED`, `null`, and `progress-v1`, respectively. The older `last_evaluated_at` label in the baseline transcription is not a second R03 field; the Technical Specification's canonical name is `last_updated`. `reducer_version` identifies the projection reducer used to build the state and is `progress-v1` for R03. Count each accepted projecting `SELF_REPORTED_KNOWN`, `CORRECT_FIRST_TRY`, `CORRECT_AFTER_HINT`, `WRONG_ATTEMPT`, `MISCONCEPTION_DETECTED`, `DIAGNOSTIC_CORRECT`, and `DIAGNOSTIC_WRONG` once. `ANSWER_REVEALED` is accepted as a zero-effect attempt fact but does not increment the count or update time. A duplicate or rejected event does not increment the count. `last_updated` is the `occurred_at` of the final projecting event in normative replay order, so the same immutable log reproduces all six canonical fields exactly.

The pure reference returns the six-field `state` plus a separate `recent_window` diagnostic (`attempt_ids`, `independent_correct_count`) so tests can inspect status inputs. The diagnostic is derived from replay and is not an additional `UserSkillState` field.

Calculate status in this exact precedence:

1. `evidence_count == 0` -> `NOT_STARTED`;
2. mastery >= 80.00, confidence >= 60.00, and at least three recent independent correct attempts -> `MASTERED`;
3. mastery < 50.00 and confidence >= 30.00 -> `WEAK`;
4. otherwise -> `LEARNING`.

Self-report alone counts once and leaves the status `LEARNING`, not demonstrated mastery. A repeated or post-assessment self-report is rejected without a new projecting event. “Before assessed” is interpreted in the normative replay order, not network arrival order; a valid backfilled self-report before the first assessed event may reproject the state. The same user/skill may never have two accepted self-reports.

## Recent ten completed attempts

The window is the **last ten distinct completed attempts for the user/skill**, ordered by `(completed_at, attempt_id)` with UTC times. An event's `completed_at` is an authoritative immutable Assessment completion fact; absence means the attempt is not yet counted in this window. Multiple events for one attempt/skill must agree on its completion time after UTC normalization. `completed_at` may be before or after the event's `occurred_at`: evidence can be produced, normalized, analyzed, or backfilled at a different time. No ordering constraint between these two facts is imposed. This completion fact is required in the replay input for any completed pilot attempt that participates in Progress status; an Assessment completion path with no ProgressEvent completion fact is an integration gap to resolve before persistence, not a reason to fabricate a wrong event.

A completed attempt qualifies as independently correct if it has `CORRECT_FIRST_TRY` or `DIAGNOSTIC_CORRECT` before any hint/reveal for that attempt. It must be a distinct attempt ID. Unassisted `DIAGNOSTIC_CORRECT` qualifies; helped diagnostics, `CORRECT_AFTER_HINT`, and revealed work do not. A later reveal does not retroactively erase a correct result that preceded it. Only the ten most recent completed attempts are inspected for the baseline requirement of at least three independent correct attempts. The projection derives the window from immutable event completion facts; no time decay is applied.

## Misconception repeat and single penalty

For `(user, skill, misconception_code)`, successive confirmed `MISCONCEPTION_DETECTED` events use 1.0, 1.25, then 1.5 for the third and later. Other wrong events neither increment nor reset that code's counter. An independent correct completed attempt for the skill resets **all** misconception-code counters for that user/skill. Hint-assisted correct work does not reset them. The repeat multiplier affects only the misconception's negative mastery delta, not confidence.

An evidence unit is `(user_id, skill_id, attempt_id, evidence_ref)`. For one unit, emit **one normalized negative `ProgressEvent`**: `MISCONCEPTION_DETECTED` if a specific misconception is confirmed, otherwise `WRONG_ATTEMPT`. A pair of these kinds with the same unit is an invalid event-log combination and is rejected; the underlying wrong Assessment/Analyzer fact may remain outside Progress, but it is not a second `ProgressEvent`. Different completed attempts are separate evidence by attempt identity. Within one attempt, two different negative units may both project only when their `evidence_ref` values differ and **both** records carry the explicit Assessment rule `independent_evidence_rule = distinct_validated_steps`; the reference rejects an unmarked pair. A wrong `FINAL_ANSWER` alone remains `WRONG_ATTEMPT`, never a fabricated misconception.

## Idempotency, ordering and replay

`event_id` is globally unique. For attempt-derived events, `(attempt_id, skill_id, event_kind, evidence_ref)` is also unique. A retry with the exact same identity and payload returns the existing result without appending or reprojecting. Reuse of either identity with conflicting payload is a conflict, not a new event. Self-report has its own once-per-user/skill guard. A later Django implementation must enforce these identities and the event/projection write atomically under concurrency; this reference verifies logical behavior, not DB locking.

The **normative total-order key is `(occurred_at, event_id, policy_version)`**. UTC normalization is required; accepted timestamp precision is at most six fractional digits, so the reference never silently truncates an ordering difference. Ordering must not depend on input timezone formatting. `event_id` is unique, but `policy_version` remains an explicit third key as required by the Technical Specification. Each immutable event is applied using its own recorded `policy_version`. The current reference registers `progress-v1`; an unregistered policy fails clearly rather than silently using the newest policy. A valid late/backfilled event causes reprojection of the affected user/skill from the complete ordered immutable log. Replaying the same log in any delivery order yields the same `UserSkillState`, including mastery, confidence, evidence count, status, `last_updated` and `reducer_version`.

## Contract-level acceptance

`tests/test_r03_contract.py` must exercise all eight kinds, exact deltas, difficulty, confidence, Decimal rounding/clamp, status boundaries, self-report, recent ten attempts, repeat/reset, reveal, source idempotency, rejection of a same-evidence negative pair, both valid temporal relationships between completion and occurrence, and deterministic late-event replay of every canonical state field. The pilot codes, edges, and event kinds have independent literal test expectations. `scripts/verify_repo.py` runs that pure suite alongside existing checks. This spec does not claim PostgreSQL, Django persistence, API, or runtime Knowledge/Progress verification. Final human contract gate: ACCEPTED. R03 remains active until its PR is merged into main.
