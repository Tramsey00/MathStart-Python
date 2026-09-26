# MS6-I01: UI-facing API-needs handoff

- **To:** I02 and R02 owners/reviewers
- **Status:** Request for review; not a replacement for R02 and not an endpoint definition

## Public information the UX needs

| Surface | Needed public information | Contract guardrail |
| --- | --- | --- |
| Catalogue/topic | published navigation hierarchy, topic identity, availability of an exercise mode, media availability | Guest-readable theory stays separate from student data. |
| Exercise renderer | statement, mode, public input/step schema, parser/display profile when relevant, difficulty/difficulty level and safe skill metadata where the accepted public contract provides them, reveal policy, contract version | Never include answer key, canonical solution, accepted variants, or validation specification. Skill metadata must not disclose checker logic. |
| Draft/editor | attempt identity/version/revision, ordered public steps, raw text, server-provided parse/result status | Client does not assert normalized/authoritative status. |
| Result | `CORRECT`, `WRONG`, `INDETERMINATE`, and `UNSUPPORTED` distinctions; `first_error` location where available; confirmed vs uncertain evidence; safe explanation; allowed next action | Wrong final alone cannot create a named misconception; indeterminate is not displayed as wrong. |
| Help/reveal | bounded help level 1--3 (0 means none), server-confirmed help/reveal state, revealed content only in explicit reveal response, and safe public exposure/eligibility state for user + immutable `exercise_version` | Ordinary GET is not reveal; reveal persistence precedes disclosure; a new attempt must not appear to restore independent eligibility for an exposed version. |
| Progress/history | server-provided mastery, confidence, status, evidence count/coverage, self-report marker, `last_updated`, topic aggregate, and paginated own history | Client does not calculate authoritative mastery, confidence, aggregate, or status. |
| Practice/diagnostic | target/reason, item/session identity, counter, independent-correct streak, terminal/completion reason, origin-topic return reference, no-candidate/repeat states | Refresh/retry must reconcile a stable server session; stop criteria remain server-provided. |
| Tutor | bounded response state, approved/prepared hint, rate/timeout/outage state | Tutor cannot bypass reveal or disclose server-only checker data. |

## State/error vocabulary requested for alignment

The UI needs stable machine-readable distinctions for: authentication required, no access, validation error, processing/pending, indeterminate, unsupported input, input limit, already submitted, idempotency conflict, revision conflict, version mismatch, duplicate/retry-safe outcome, help unavailable, reveal confirmation required, revealed/exposed, no practice candidate, rate/timeout outage, and degraded service. The final spelling and envelopes belong to R02/V10/V12/V13; I01 does not define new envelopes.

## Review questions

1. Can R02 fixture versions represent every renderer state without introducing correctness secrets?
2. Which response owns `first_error`, confirmed/uncertain evidence presentation, and unsupported parsing presentation?
3. What optimistic/draft revision protocol will prevent two tabs from silently overwriting raw work?
4. Which server fact distinguishes help/reveal persistence from a merely displayed UI state?
5. Which safe public server fact tells the UI that the user + `exercise_version` is no longer eligible for new independent positive evidence after reveal/exposure?
