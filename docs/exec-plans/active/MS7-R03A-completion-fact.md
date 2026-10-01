# EXEC PLAN MS7-R03A: CompletionFact addendum

- **Status:** Active — audit/design READY FOR REVIEW; implementation and human acceptance PENDING
- **Last updated:** 2026-10-02
- **Owner:** Руслан
- **Reviewer / Task Approver:** Владимир
- **Issue:** #18
- **Baseline:** `main` at `428ece726918f635549fc7dd8fdd352f799c3308`
- **Branch:** `ms7-r03a-completion-fact`
- **Milestone:** G1 contract closeout; not a repeat of G0
- **Relation:** FOLLOW-UP / ADDENDUM TO FROZEN R03
- **Primary decision:** D-021
- **Target contract:** `progress-v1.1`
- **Design ADR:** [ADR-0005 / D-021](../../adr/ADR-0005-completion-fact.md), Proposed
- **Audit trace:** [MS7-R03A](../../agent-traces/MS7-R03A.md)
- **Current stage:** repository audit and contract design only; no R03A implementation

## Current authorization and review readiness

The 2026-10-02 task request narrows this turn to audit + D-021 draft + plan +
trace. Only these three task-owned Markdown artifacts may change. Implementation
files below are a future sequence, not deliverables claimed to exist now.
Issue #18 stays open; no PR, push or merge is part of this stage. One scoped
documentation commit is permitted after all required checks and scope review.

Baseline main/origin/main is 428ece726918f635549fc7dd8fdd352f799c3308.
Starting HEAD is 870fd760dc1fdb25f33af54eacd97579259d49a0 on
ms7-r03a-completion-fact. The six pre-existing MS7-AUDIT/PREG0/G0Candidate
untracked plans/traces and all output/ and tmp/ are excluded from edits/staging.
The existing interpreter in tmp may be executed read-only with -B and
PYTHONDONTWRITEBYTECODE=1; no packages or files are added there.

## Goal

Define and verify CompletionFact semantics without reopening accepted R03 numerical Progress rules.

The task separates two concepts that are currently coupled in the R03 reference:

1. **ProgressEvent** — validated evidence that may project numerical `UserSkillState` according to the frozen R03 policy.
2. **CompletionFact** — authoritative immutable attempt-completion/history data that may affect recent-ten membership and therefore derived status inputs, but has no authority to create mastery/confidence deltas by itself.

The principal invariant is:

> A completed attempt may enter the last-ten-completed-attempts window without fabricating a ProgressEvent, penalty, misconception, or any other numerical evidence.

## Normative inputs

Read before implementation:

- `AGENTS.md`
- `PRODUCT.md`
- `ARCHITECTURE.md`
- `README.md`, `docs/architecture.md`
- ADR-0001, ADR-0002, ADR-0004 and ADR/spec/plan/trace templates
- `docs/adr/ADR-0003-knowledge-progress-semantics.md`
- `specs/progress/BASELINE-v1.md`
- `specs/progress/R03-progress-contract.md`
- `specs/progress/fixtures/progress-v1-cases.json`
- `scripts/r03_contract_reference.py`
- `tests/test_r03_contract.py`
- accepted MS7-R02A contract artifacts under `specs/api/`
- MathStart Technical Specification v7.1 G0 ACCEPTED task card for MS7-R03A

If any source conflicts with the accepted R03 contract or the R03A task card, stop and record the conflict rather than inventing new semantics.

Repository-source qualifications found by this audit:

- R03 is accepted/frozen; its completed plan records PR #7 merge and acceptance.
- R02A is present in baseline main, but ADR-0004, its spec, http-policy and
  candidate manifest retain Proposed/PENDING. Use its checked-in semantics as a
  design dependency; do not infer completed human acceptance from the merge.
- No v7.1 task-card/PDF is tracked. The historical Desktop PDF path recorded by
  R02A is unavailable in this session. The full supplied R03A request and local
  contracts suffice for a Proposed design; Vladimir must reconcile the canonical
  task card before accepting the implementation package.
- ARCHITECTURE 17.1/42.7 currently requires a ProgressEvent for every automatic
  progress change. D-021 explicitly proposes a reviewed exception for
  completion-derived window/status only, preserving the requirement for all
  numerical changes. No current root/frozen document is silently rewritten.
- Only root AGENTS.md was discovered outside the excluded user output/tmp trees.

## Frozen R03 invariants

R03 numerical policy is out of scope for change.

The implementation must preserve exactly:

- the eight accepted `ProgressEvent` kinds;
- mastery deltas;
- confidence deltas;
- difficulty coefficients;
- misconception repeat coefficients;
- exact Decimal arithmetic;
- per-event clamp and `ROUND_HALF_UP` behavior;
- evidence-count semantics;
- status thresholds and precedence;
- no time decay;
- reveal and independent-evidence rules;
- existing event identities and idempotency rules;
- Progress as the only owner of long-term numerical knowledge state.

No neutral completion may be converted to `WRONG_ATTEMPT`, `DIAGNOSTIC_WRONG`, or any synthetic event merely to make the attempt visible in history.

## Proposed D-021 contract boundary

[ADR-0005](../../adr/ADR-0005-completion-fact.md) is the complete normative
candidate. These are settled design proposals pending human review, not accepted
runtime behavior.

### CompletionFact identity

Select (user_id, skill_id, attempt_id), with native attempt_id -> owner and
bound-version skill-mapping verification. One terminal instant is shared across
skills of the same attempt. The six-field closed envelope is completion_version,
user_id, skill_id, attempt_id, completed_at and independent_correct.
completion_version is completion-v1; no fact_id or duplicate exercise-version
counter is needed. Canonical timestamps use R03's 0–6-digit aware RFC3339 parser,
UTC six-digit serialization. independent_correct is a required strict boolean.

Assessment produces native facts only for finalized assessed COMPLETED attempts.
The flag is compared against separately supplied trusted frozen Assessment
eligibility/correctness context, including R02A exposure/one-positive rules.
SUBMITTED/202, ABANDONED and SELF_CHECK REVIEWED do not create native facts.
Historical v1 reveal-only completion entries remain eligible for explicit import.

### Ordering

The recent-ten completed-attempt window is ordered by:

```text
(completed_at, attempt_id)
```

UTC normalization is mandatory. Equal timestamps use case-sensitive lexical
attempt_id order; native UUIDs are canonical lowercase. Take the last ten
distinct tuples for the selected user/skill, including independent=false facts,
and return IDs in ascending order. No time decay or positive-only filtering.

### Neutrality

A CompletionFact by itself must not change:

- mastery;
- confidence;
- evidence_count;
- numerical deltas;
- misconception counters;
- ProgressEvent history;
- `last_updated`.

It may change:

- recent-ten attempt membership;
- recent independent-correct count;
- derived status only where the already-frozen R03 status formula depends on that count.

### Late/backfilled facts

For a fixed valid event log, CompletionFact insertion cannot change any numerical
field, repeat counter/reset point, event delta/snapshot or event identity.
Use unchanged R03 replay for the numerical track. Native recent-window membership
comes only from the CompletionFact ledger; use unchanged status_for on that count.
An independent fact does not clear repeat counters. A qualifying event still
clears them in occurrence order even when its separate fact is delayed.

Fact/event delivery before or after one another has identical final output for
identical accepted inputs. Late facts can alter count/status; late events can
reproject numbers as frozen R03 requires. These are separate causes. An old fact
outside the last ten is stored without changing the window. There is no
completed_at-versus-occurred_at constraint.

### Duplicate and conflict behavior

- Exact retry of the same immutable CompletionFact: idempotent.
- Reuse of the same stable identity with different immutable payload: conflict/reject.
- Duplicate delivery must never duplicate recent-window membership.

Compare canonical six-field payloads after timestamp normalization; semantic
timezone equivalents are duplicates. Changed version is a payload conflict,
not a second identity namespace. Conflicting inline event/fact completion times
and native final-result eligibility contradictions fail atomically. Existing
ProgressEvent event/source/evidence identities and duplicate-log rejection
remain unchanged.

Native events retain their frozen inline completion attestations/validation.
Those fields supply no native history entries; missing separately delivered
facts are reported as completion_gaps. There is no automatic inline fallback.

### Parity

For every accepted `progress-v1` fixture where no separate neutral completion is introduced, `progress-v1.1` must reproduce the same numerical projection results.

Parity must be executable, not prose-only. Keep the v1 entry points/result,
including reducer_version=progress-v1, literally unchanged. An explicitly named
legacy adapter materializes facts from a validated v1 log and reproduces its
independence logic without retrofitting R02A credit/UUID rules.
Native reducer_version becomes progress-v1.1, while all events retain their
recorded policy_version=progress-v1. Compare every other canonical state field,
recent IDs/count, event IDs/order and numerical snapshots. No such R03A parity
implementation is claimed for the design stage.

## Repository audit findings

Line references below are from the unchanged baseline files at this audit.

| Site | Observed coupling / constraint | Addendum boundary |
| --- | --- | --- |
| scripts/r03_contract_reference.py:222 utc_instant | Aware RFC3339, at most six digits, normalized UTC microseconds | Reuse exactly; reject overprecision rather than truncating |
| :244 validate_event, :264, :275, :277 | No self-report completion; normalize inline time; correct/diagnostic kinds require it | Preserve frozen event validator; add separate fact validation |
| :304 source_identity; :310 evidence_unit | Unique attempt/skill/kind/evidence source; user/skill/attempt/evidence unit | Do not reuse a fact as an event/evidence unit |
| :316 event_order | occurred_at, event_id, policy_version | Facts never join numerical event order |
| :320 status_for | Ordered NOT_STARTED/MASTERED/WEAK/LEARNING thresholds | Supply fact-derived recent count without changing formula |
| :330 _recent_attempts | Sort event-populated dictionary, nonnull completion only, last ten, count bools | New ledger supplies dictionary; never merge two entries for one attempt |
| :341 _state_dict | Status implicitly reads that event-populated dictionary; reducer version hardcoded v1 | Native final status/version assembled separately |
| :359 replay, :415–420 | Attempt dictionary created only inside event loop; inline times must agree | Native ledger exists independently; inline time is a consistency attestation |
| :453–457 independent branch | Correct event marks independent history AND clears all repeat counts | Preserve event reset; separate the history source |
| :458 snapshots; :463 final output | Per-event and final status derive from current event completion dictionary | Preserve legacy snapshots; never label them native completion history |
| :476 ingest_event | Exact event retry canonicalized; source conflicts rejected; replay after valid late event | Add separate fact ingestion without fabricating any event |
| tests/test_r03_contract.py:68–104 make_event | Defaults completed=True and copies event stamp into completion | Keep helper/tests unchanged; new R03A factories are separate |
| tests/test_r03_contract.py:204, :221, :237 | Three golden streams, six-field state/version/time and diagnostic independence | Literal v1 oracle plus additive parity comparisons |
| tests/test_r03_contract.py:311, :334, :359 | Repeat reset, last-ten/incomplete/reveal completion and reveal-before-positive guards | Test facts cannot change counters, and preserve legacy reveal membership |
| tests/test_r03_contract.py:373, :406, :429 | Late occurrence replay, both time relationships, same-attempt time consistency, evidence conflicts | Preserve all unchanged; add fact-specific equivalents |
| specs/progress/R03-progress-contract.md:83 | Explicit event-free completion integration gap | D-021 addresses this exact gap |
| scripts/r02a_contract_reference.py:154–167 | Attempts/exposure/receipts are serial in-memory state; no completion envelope/time ledger | Do not treat its completion count as runtime persistence |
| :201 create; :243 draft; :247–256 submit | One owned version-bound attempt, full draft replacement, immutable submitted snapshot | Facts reference the original attempt/version; corrections get new IDs |
| :267–281 finalize | COMPLETED retry stable; available/independent/positive decided from exposure; completions increment once | Server finalized eligibility is native fact authority; no credit from fact ingestion |
| :214–233 receipt replay | Exact result before state/revision checks; help source uniqueness survives receipt expiry | Completion identity is permanent, independent of HTTP receipt lifetime |
| tests/test_r02a_contract.py:650–787 | 32 serial scenarios, help races, immutable snapshot, second credit, expiry and owner checks | Reuse semantics, add trusted producer fixtures rather than edit R02A |
| specs/api/schemas/dto-v1.schema.json Attempt / Eligibility / AssessmentResult | COMPLETED has timestamp/result; SUBMITTED has no result/time; independent and positive award are different fields | Envelope is internal; no OpenAPI/schema edit in this stage |

All current R03 attempt/fact creation sites are replay's attempts.setdefault
and the event factories/golden fixture rows; there is no CompletionFact producer.
Repository-wide search found completion metadata only in these Progress contracts,
R02A DTO/examples/oracle and design records. Existing content/models.py and its
0001_initial migration contain content entities, not Assessment/Progress tables.
No runtime model, migration or endpoint is asserted to exist.

Every R03 progress test using make_event inherits its completion default.
Explicit completion-sensitive tests are diagnostic independence (237), repeat
reset (311), recent ten (334), reveal/incomplete rejection (359), occurrence
ordering/time precision (373), completion consistency (406), and evidence
idempotency/penalties with shared completion time (429).

## Expected artifacts

| Stage | Exact files |
| --- | --- |
| This audit/design | docs/adr/ADR-0005-completion-fact.md; this active plan; docs/agent-traces/MS7-R03A.md |
| Future addendum/schema | specs/progress/R03A-completion-fact.md; specs/progress/schemas/completion-v1.schema.json |
| Future fixtures | specs/progress/fixtures/completion-v1-cases.json; completion-v1-invalid.json; progress-v1.1-parity.json in the same directory |
| Future pure oracle | scripts/r03a_contract_reference.py |
| Future additive tests | tests/test_r03a_contract.py |
| After D-021 acceptance only | Scoped explanatory notes in ARCHITECTURE.md and AGENTS.md for numerical versus completion-derived status ownership |

Future schema uses the six-field closed envelope. Authority fixture records
remain separate from it. Parity fixtures pin source v1 fixture/case IDs and
expected results, rather than recopying/changing frozen constants.
The expected pure functions are validate_completion_fact,
ingest_completion_fact, replay_v1_1 and import_progress_v1_completions.
They call/import the unchanged R03 reference for numerical behavior and the
literal legacy entry point. Naming or boundary changes discovered during
implementation must return to this plan/spec for review.

Prefer additive files. Do not rewrite frozen R03 artifacts unless a narrowly scoped compatibility note is required and independently reviewed.

## Implementation sequence

1. **Repository audit**
   - inspect R03 replay and recent-window derivation;
   - map every place where `completed_at` currently enters through `ProgressEvent`;
   - identify which current tests encode coupling that R03A must supersede additively;
   - inspect R02A attempt/finalization terminology for naming consistency.

2. **ADR D-021**
   - define ownership, identity, ordering, neutrality, replay, duplicates/conflicts, compatibility and rollback;
   - explicitly state that no numerical R03 rule changes.
   - current result: Proposed draft ready for Vladimir; reconcile upstream
     acceptance/task card and the explicit architectural status exception first.

3. **progress-v1.1 addendum**
   - define CompletionFact envelope/schema and relation to ProgressEvent;
   - define combined replay inputs and outputs;
   - define recent-window behavior with neutral attempts;
   - define late facts and deterministic replay.

4. **Fixtures**
   - neutral completion;
   - same timestamp / attempt-id tiebreak;
   - late completion;
   - exact duplicate;
   - conflicting duplicate;
   - neutral fact evicting an older independent-correct attempt from the last ten;
   - progress-v1 parity corpus.

5. **Pure reference implementation**
   - no Django/ORM/API/runtime persistence;
   - keep policy dispatch explicit;
   - do not mutate existing accepted numerical constants.

6. **Tests**
   - task-specific R03A suite;
   - existing R03 suite must pass unchanged;
   - assertions must prove numerical neutrality, not merely expected status/window output.

7. **Verification**
   - task suite;
   - existing R03 suite;
   - existing R02A suite;
   - canonical `python scripts/verify_repo.py`;
   - `git diff --check`;
   - scoped review for frozen/runtime/dependency drift.

8. **Trace and human gate**
   - record exact commands/results and limitations;
   - keep plan active until Vladimir independently accepts D-021 and the reviewed `progress-v1.1` package;
   - only then move plan to completed and allow downstream tasks to treat R03A as accepted.

## Required task-specific tests

The following named future fixture matrix is required before implementation
acceptance. These are planned cases, not newly executed tests. Unless a case
explicitly delivers a ProgressEvent, assert equality of mastery, confidence,
evidence_count, last_updated, numerical snapshots/repeat state and event log
before/after fact ingestion.

| # / case ID | Setup / expected assertion |
| --- | --- |
| 01 neutral-completed | Valid COMPLETED CORRECT/ALREADY_CREDITED authority, false fact: history enters with no second positive event |
| 02 neutral-only | Empty event log + one false fact: window contains attempt; numerical zeros/count 0/null time and NOT_STARTED |
| 03 equal-time-tiebreak | Facts attempt-a/attempt-b at same normalized time, reversed deliveries: ascending IDs a,b |
| 04 late-neutral | Deliver newer facts then older neutral fact: order follows completed_at, not arrival |
| 05 fact-before-event | Authoritative fact first, then its valid event: one entry and normal single event delta |
| 06 fact-after-event | Event first reports completion gap and no native entry; fact later fills it without numerical change |
| 07 exact-duplicate | Same canonical tuple/payload retried: duplicate=true, ledger size/result unchanged |
| 08 conflicting-duplicate | Same tuple with changed time/flag: conflict; accepted state/log unchanged. A version change is rejected, never treated as a second identity |
| 09 retry-no-second-entry | Several completion retries and unrelated event deliveries retain one recent entry |
| 10 event-and-fact | Multiple valid events/evidence units plus same-attempt fact: one history entry, existing event counts preserved |
| 11 conflicting-time | Inline event completion instant and separate fact differ: reject atomically in both delivery orders |
| 12 neutral-eviction | Ten entries start with an independent attempt; newer false fact evicts that ID |
| 13 count-three-to-two | Three independent + seven false entries; neutral #11 leaves exactly two independent |
| 14 mastered-to-learning | At mastery>=80/confidence>=60, case 13 changes MASTERED to LEARNING by frozen status_for only |
| 15 numerical-neutrality | Case 14 preserves every listed numerical field, last_updated, repeat counters, event IDs/order/deltas |
| 16 late-independent | Server-authorized true fact backfilled inside last ten increases recent count; alone no numerical/reset effect |
| 17 malformed-no-wrong | Missing fields, bad bool/calendar/time/precision/version/extra field fail with no synthetic WRONG or other event |
| 18 client-flag-rejected | Identical true envelope without separate trusted authority, or mismatching frozen verdict, is rejected |
| 19 progress-v1-parity | All three frozen golden streams, arithmetic and original contract scenarios; legacy full result exact, native differs only in reducer_version when importing same facts |
| 20 delivery-permutations | Permute valid event/fact deliveries and exact fact retries; complete sets give identical native final result/diagnostics |
| 21 timezone-duplicate | Z and +03:00 denote same microsecond instant: canonical idempotent duplicate; seventh fractional digit rejected |
| 22 owner-skill-binding | Foreign owner, unknown/unmapped skill, reused native attempt owner or inconsistent cross-skill completion instant rejected |
| 23 lifecycle-boundary | SUBMITTED/202, ABANDONED and SELF_CHECK REVIEWED cannot emit native facts; UNSUPPORTED/INDETERMINATE COMPLETED can emit false |
| 24 help-and-credit | Help before/during pending finalization false; help after completed independent result preserves true; repeated credited CORRECT stays false/no event |
| 25 repeat-isolation | Two same-code misconceptions, true fact without positive event, then third misconception: coefficient stays 1.5; fact never resets it |
| 26 event-reset-with-late-fact | Independent correct event between misconceptions clears repeat counters in occurrence order even before separate fact delivery |
| 27 outside-window | Older backfilled fact outside last ten changes neither window/count/status nor numerical state |
| 28 legacy-reveal-import | Preserve reveal-only v1 completion and absence of incomplete entries; no native implicit fallback |
| 29 final-result-conflict | Native true fact + helped/wrong final diagnostic, or false fact + independent first-try final result: reject; intermediate step wrong alone is not a terminal verdict |
| 30 late-event-is-event | Backfilled ProgressEvent can change numbers/last_updated per v1; distinguish this from late fact-only neutrality |
| 31 scope-and-not-started | Facts for other user/skill do not enter selected window; even true fact-only history retains NOT_STARTED with evidence_count 0 |
| 32 immutable-conflict-order | Same conflicting identity set is rejected in either order; preserve first accepted ledger, never claim identical successful projections for invalid inputs |

Concrete status example to verify with the unchanged v1 oracle: one self-report,
three hard unassisted DIAGNOSTIC_CORRECT events, then seven easy
CORRECT_AFTER_HINT events on distinct version-bound attempts yield
mastery=100.00, confidence=67.00, evidence_count=11 and last_updated at event #10.
The ten completions have three independent entries and MASTERED. A newer neutral
fact evicts the earliest independent entry, making the count two and status
LEARNING; the four numerical/time fields and repeat state remain identical.

At minimum, the final suite must prove:

1. A neutral completion enters recent-ten history with zero numerical mutation.
2. Same `completed_at` facts are ordered deterministically by `attempt_id`.
3. A late/backfilled CompletionFact deterministically changes recent-window membership.
4. Exact duplicate delivery is idempotent.
5. Conflicting duplicate identity is rejected.
6. A neutral late completion can evict an older independent-correct attempt from the ten-attempt window.
7. That eviction may change the frozen status result if and only if the existing status formula dictates it.
8. The same operation does not alter mastery, confidence, evidence_count, misconception counters or `last_updated`.
9. Existing `progress-v1` fixtures retain identical numerical outputs under the v1.1 compatibility path.
10. Neutral completion cannot produce fake negative evidence.
11. CompletionFact and ProgressEvent for the same attempt/skill can coexist without double-counting the attempt in the recent window.
12. Conflicting completion times for one immutable completion identity are rejected.

## Security / trust checks

- Client assertions alone cannot grant independent-correct status.
- CompletionFact must be treated as authoritative server/domain evidence, not arbitrary frontend input.
- Neutral facts must never acquire numerical projection authority.
- A malformed/unsupported fact must fail closed without generating a negative ProgressEvent.
- No PII or secrets in fixtures.

## Out of scope

- Django models or migrations.
- PostgreSQL persistence/locking implementation.
- API endpoints or DRF serializers.
- Auth/session/CSRF changes.
- Frontend.
- Analyzer/Tutor/LLM implementation.
- New Progress formulas, thresholds, event kinds or deltas.
- Broad refactoring of the accepted R03 code.
- Downstream MS7-R11 or MS7-V08 implementation.

## Risks and remaining review questions

| Risk / unresolved authority | Required review or mitigation |
| --- | --- |
| Two inputs delivered separately | Native completion_gaps diagnostic; durable source/delivery/reconciliation obligations belong to V08 |
| Accidentally reading facts in numerical reducer | Treat unchanged R03 replay as numerical oracle; cases 15/25/26 prove reset/delta isolation |
| Automatic legacy fallback hides missing facts | Explicit named import only; native events cannot populate history |
| UUID/credit rules retroactively change v1 | Keep legacy entry points and import semantics unchanged; exact parity before adding neutral facts |
| Status moves while last_updated stays fixed | Document last_updated as numerical event time; no new state timestamp in this envelope |
| R02A human acceptance is undocumented in baseline artifacts | Vladimir reconciles the accepted package/digest; this audit does not mark it accepted |
| Canonical v7.1 task card unavailable locally | Vladimir cross-checks D-021 with canonical source; no claimed PDF inspection |
| Broad architecture ProgressEvent wording | Vladimir explicitly approves the numeric-only refinement before root-doc notes/implementation acceptance |
| REVIEWED versus COMPLETED history | Approve native COMPLETED-only membership and explicit preservation of old reveal-only completions |
| Conflicting historical/native verdict | Reject and reconcile; never overwrite accepted payload or numerical evidence |

No algorithm/identity/envelope choice is left implicit in the proposal. Remaining
questions concern human acceptance, canonical-source reconciliation and future
physical persistence design; they are not invitations to change frozen numbers.

## Audit-stage verification (2026-10-02)

Existing isolated interpreter tmp/ms7-r02a/venv/Scripts/python.exe reports Python
3.12.14; Django 5.2.16, jsonschema 4.26.0, psycopg 3.3.6, pip 25.0.1.
The configured PostgreSQL server reports 160015 (16.15). No dependency/backend
change or database migration/bootstrap was performed. Runtime copies/reports and
logs are outside the repo; exact commands/path are in the trace.

- verify_repo.py: PASS 8/8, exit 0.
- Existing R03 suite: PASS 18 tests; unchanged.
- Existing R02A suite: PASS 30 tests; unchanged.
- pip check: PASS, no broken requirements.
- Document links, whitespace and scoped diff: PASS for all three task-owned
  documents, including new files via Git intent-to-add. Full diff against the
  supplied main baseline has exactly those three paths. No inferred R03A
  implementation/parity or fresh-install/CI pass.

## Acceptance checklist

- [x] Issue created and task scope recorded.
- [x] Scoped branch created from the accepted MS7-R02A main baseline.
- [x] Active execution plan created.
- [x] Repository coupling audit completed.
- [x] ADR D-021 drafted (Proposed; human approval PENDING).
- [ ] `progress-v1.1` addendum drafted.
- [ ] Neutral/late/parity fixtures added.
- [ ] Pure reference/replay implementation added.
- [ ] R03A task tests pass.
- [x] Existing R03 tests pass unchanged (18 tests).
- [x] Existing R02A tests pass unchanged (30 tests).
- [x] Canonical repository verification passes (8/8 in audit stage).
- [x] Audit-stage trace records exact evidence; implementation evidence remains pending.
- [ ] Vladimir independently accepts the contract package.
- [ ] Final-SHA CI/merge gate completed.
- [ ] Plan moved to completed only after acceptance.

**Current result:** audit/design READY FOR REVIEW. Full MS7-R03A is INCOMPLETE;
the addendum/schema/fixtures/reference/tests and all remaining human/CI gates
are still pending. This plan remains in active/.

## Downstream handoff

After human acceptance, the accepted R03A package becomes input to the downstream tasks named by v7.1, primarily **MS7-R11** and **MS7-V08**.

Until acceptance, downstream work may inspect the candidate but must not treat it as frozen upstream authority.
