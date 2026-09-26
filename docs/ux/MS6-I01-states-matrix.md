# MS6-I01: States matrix

- **Status:** Draft for review
- **Scope:** future UI behavior against accepted R02/R03 contracts; not an implementation or API specification.

| SC | Route / screen path | Start and primary action | Required visible states | Persistence, privacy, and next route | Future dependency |
| --- | --- | --- | --- | --- | --- |
| SC-01 | Sign in/register -> Profile -> Grade -> Onboarding | Student selects grade and one of Start from beginning / Diagnostic / Familiar topics | selected, validation error, save pending, save retry; self-report labelled as self-assessment | Grade changes catalogue navigation only; history is not reset. Start from beginning shows all skills `NOT_STARTED`. | I03, V02, V08 |
| SC-02 | Catalogue -> Subject -> Section -> Topic -> Exercise entry | Guest/student opens theory then selects a mode-aware exercise | published/unavailable exercise, media fallback, read-only guest, activity-only notice | Stable topic URL; refresh retains no invented mastery change. Student is directed to auth only for personal actions. | I04, V03, V04 |
| SC-03 | Topic -> `FINAL_ANSWER` -> submit -> result | Student enters raw math text and submits | draft, preview, processing, correct, wrong, indeterminate, unsupported, recoverable request error/retry | A recoverable transport retry reuses the same submission identity and preserves raw input. After completed mathematical evaluation, correction starts a new `Attempt`; the evaluated attempt is read-only. Wrong final has no specific misconception label. | I05, V10 |
| SC-04 | Topic -> `STEP_BY_STEP` -> validate -> feedback -> practice/diagnostic | Student edits ordered typed lines beginning from a separate source condition | draft, line error, `first_error`, confirmed, uncertain, unsupported, conflict, frozen history | `first_error` focuses a line. Confirmed negative evidence is shown once; low confidence directs to diagnostic, weak prerequisite can direct to practice. | I06, I10, V05, V10, V12 |
| SC-05 | Any exercise -> Hint -> continue solving or Reveal confirmation -> Reveal result | Student requests one of bounded help levels 1--3; level 0 means no help used. Reveal remains a separate explicit action. | help level, continue solving, help processing/retry, confirm reveal, reveal processing, revealed | Hint/reveal is server-confirmed. Exposure and independent-evidence eligibility persist for the user + immutable `exercise_version` across attempts; a new `Attempt` does not restore independent positive eligibility for that version. | I09, V06 |
| SC-06 | Topic -> `STRUCTURED_SOLUTION` -> submit | Student completes a public-schema-rendered form | required field, field error, partial save, pending, unknown field/version blocking state | Two schemas can yield distinct forms; public schema never exposes correctness. Server field error receives focus. | I07, R02, V04 |
| SC-07 | Practice start -> Practice item -> complete/leave -> Origin topic | Student sees target, reason, item counter, current independent-correct streak, and may leave | no candidate, repeat ineligible, active item, completion reason, seven-item limit, abandon, return | Stop after 3 consecutive independent correct results on different eligible exercise versions, OR mastery >= 70 and confidence >= 60 after at least one assessed item; always stop at 7 items. Selected item/session remains stable on refresh/back. Leaving retains history; return uses origin fallback if archived. | I13, R11, V12 |
| SC-08 | Exercise/Tutor action -> failure/retry/refresh/two tabs | Student encounters Tutor outage or network loss | validation available, Tutor unavailable with prepared help, request pending, retry-safe result, conflict/no-access | Refresh and retry reconcile with server state; a duplicate request must not appear as a second event. Known foreign attempt ID returns generic no-access state. | I09, I12, I14, V10, V13 |

## Cross-cutting state distinctions

| State | Trigger | Student can do | Student cannot infer |
| --- | --- | --- | --- |
| `confirmed` | Validated transition/field supports a controlled result | Read the identified location and choose practice/help | A permanent diagnosis or a global skill judgment |
| `uncertain` | Suspicion exists without confirmation | Recheck work, seek help, run diagnostic | A named misconception |
| `unsupported` | Parser/schema cannot assess safely | Keep raw input, use supported format, ask for help | That their mathematics is wrong |
| `indeterminate` | Validation completed without a reliable correct/wrong conclusion | Preserve work and choose the offered safe next step | A wrong answer or a named misconception |
| `hint` | Server accepted hint request | Read bounded hint and continue | The complete revealed solution |
| `reveal_confirm` | Student selected reveal but has not confirmed persistence | Confirm or cancel | Any answer content |
| `revealed` | Server persisted exposure for the user + exercise version | Read disclosed content and continue learning | That a new `Attempt` restores independent positive-evidence eligibility for this exercise version. |
| `outage` | Tutor/provider fails | Continue deterministic exercise work; use prepared local hint where supplied | That answer validation or saved progress failed |
| `not_started` | Server reports `NOT_STARTED` / no assessed evidence | See «Ещё не проверено» and choose an available starting action | That the learner does not know the skill |

## Required UX-state baseline

Every applicable interactive surface documents `empty`, `loading/processing`, `success`, `recoverable error`, `unsupported`, and `offline/degraded`. A surface may mark a state `not applicable` only with a design reason; omission is not evidence that the state cannot occur. `Indeterminate` remains separate from `wrong` and `unsupported`. All server-changing retries reuse the appropriate request identity and do not imply new evidence.
