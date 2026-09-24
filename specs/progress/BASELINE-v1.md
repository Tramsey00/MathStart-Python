# Progress Algorithm v1 — MathStart v3.1 baseline

- **Status:** Baseline transcribed
- **Source:** MathStart Technical Specification v3.1, section 12 — Progress Engine
- **Owner domain:** Progress
- **Follow-up task:** R03 — formalize, implement, and test this existing baseline
- **Related documents:** `PRODUCT.md` sections 11-14 and `ARCHITECTURE.md`
  sections 17-18

## Scope and authority

This file records the already approved MathStart v3.1 algorithm. It does not
propose a new algorithm or modify its values. R03 formalizes, implements, and
tests this baseline; R03 does not invent a replacement algorithm.

Changing the formula, event values, difficulty coefficients, repeat coefficient,
or status thresholds requires an ADR and unit tests.

## UserSkillState

| Field | Baseline |
| --- | --- |
| `mastery` | 0..100 |
| `confidence` | 0..100 |
| `evidence_count` | Count of evidence |
| `status` | `NOT_STARTED` \| `LEARNING` \| `WEAK` \| `MASTERED` |
| `last_evaluated_at` | Last evaluation timestamp (UTC) |

## Knowledge events v1

| Event | Mastery effect | Confidence effect | Baseline semantics |
| --- | --- | --- | --- |
| `SELF_REPORTED_KNOWN` | initialization mastery = 60 | confidence = 15 | Self-report, not demonstrated knowledge |
| `CORRECT_FIRST_TRY` | mastery delta = +6 | confidence evidence = +5 | Independent solution without hint/reveal |
| `CORRECT_AFTER_HINT` | mastery delta = +3 | confidence evidence = +4 | Correct solution after hint |
| `WRONG_ATTEMPT` | mastery delta = -2 | confidence evidence = +3 | Weak negative evidence; typical event for an incorrect `FINAL_ANSWER` |
| `MISCONCEPTION_DETECTED` | mastery delta = -5 | confidence evidence = +5 | Strong signal of a specific confirmed error |
| `ANSWER_REVEALED` | mastery delta = 0 | confidence delta/evidence = 0 | Reveal is not evidence of knowledge |
| `DIAGNOSTIC_CORRECT` | mastery delta = +8 | confidence evidence = +8 | Correct diagnostic result |
| `DIAGNOSTIC_WRONG` | mastery delta = -6 | confidence evidence = +8 | Incorrect diagnostic result |

## Mastery calculation

```text
new_mastery =
clamp(
    old_mastery
    + base_delta * difficulty_coeff * repeat_coeff,
    0,
    100
)
```

| Difficulty | `difficulty_coeff` |
| --- | --- |
| `easy` | 0.8 |
| `medium` | 1.0 |
| `hard` | 1.2 |

For a repeated confirmed misconception, negative `repeat_coeff` may increase
up to 1.5.

## Evidence, statuses, and topic aggregation

- Confidence grows from the quantity and quality of evidence.
- There is no time decay in the MVP.
- `NOT_STARTED`: `evidence_count = 0`.
- `WEAK`: `mastery < 50` and `confidence >= 30`.
- `MASTERED`: `mastery >= 80`, `confidence >= 60`, and at least 3 recent
  independent correct attempts.
- `LEARNING`: all other states with evidence.
- `TopicMastery` is the weighted average of `SkillMastery` using
  `topic_skills.importance`.

## Additional rules

- After answer reveal, the current attempt cannot satisfy the independent-correct
  condition.
- A wrong `FINAL_ANSWER` without step/domain evidence MUST NOT create
  `MISCONCEPTION_DETECTED` from an assumed cause.
- Only Progress updates long-term knowledge state through validated knowledge
  events. Event creation must remain explainable and idempotent.
