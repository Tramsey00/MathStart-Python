# EXEC PLAN MS7-R03A: CompletionFact addendum

- **Status:** Active — BOOTSTRAPPED; contract design and implementation PENDING
- **Owner:** Руслан
- **Reviewer / Task Approver:** Владимир
- **Issue:** #18
- **Baseline:** `main` at `428ece726918f635549fc7dd8fdd352f799c3308`
- **Branch:** `ms7-r03a-completion-fact`
- **Milestone:** G1 contract closeout; not a repeat of G0
- **Relation:** FOLLOW-UP / ADDENDUM TO FROZEN R03
- **Primary decision:** D-021
- **Target contract:** `progress-v1.1`

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
- `docs/adr/ADR-0003-knowledge-progress-semantics.md`
- `specs/progress/BASELINE-v1.md`
- `specs/progress/R03-progress-contract.md`
- `specs/progress/fixtures/progress-v1-cases.json`
- `scripts/r03_contract_reference.py`
- `tests/test_r03_contract.py`
- accepted MS7-R02A contract artifacts under `specs/api/`
- MathStart Technical Specification v7.1 G0 ACCEPTED task card for MS7-R03A

If any source conflicts with the accepted R03 contract or the R03A task card, stop and record the conflict rather than inventing new semantics.

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

## Contract questions D-021 must settle

The ADR/spec must answer these explicitly.

### CompletionFact identity

Define one stable immutable identity sufficient for exact retry detection and conflicting duplicate rejection.

At minimum the contract must bind:

- user;
- skill;
- attempt;
- `completed_at`;
- whether the completed attempt is independently correct for recent-window purposes.

The exact field set and identity key must be justified and versioned.

### Ordering

The recent-ten completed-attempt window is ordered by:

```text
(completed_at, attempt_id)
```

UTC normalization is mandatory. Equal timestamps must remain deterministic through `attempt_id`.

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

A valid CompletionFact arriving after other events/facts triggers deterministic re-derivation of the affected recent window.

Late completion data must not cause numerical Progress events to be invented or reinterpreted.

### Duplicate and conflict behavior

- Exact retry of the same immutable CompletionFact: idempotent.
- Reuse of the same stable identity with different immutable payload: conflict/reject.
- Duplicate delivery must never duplicate recent-window membership.

### Parity

For every accepted `progress-v1` fixture where no separate neutral completion is introduced, `progress-v1.1` must reproduce the same numerical projection results.

Parity must be executable, not prose-only.

## Expected artifacts

The task may refine exact names during implementation, but the expected repository shape is:

- `docs/adr/ADR-0005-completion-fact.md`
- `docs/exec-plans/active/MS7-R03A-completion-fact.md` (this file)
- `docs/agent-traces/MS7-R03A.md`
- `specs/progress/R03A-completion-fact.md`
- versioned neutral/late/parity fixtures under `specs/progress/fixtures/`
- pure reference/check code under `scripts/`
- task-specific tests under `tests/`

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
   - canonical `python scripts/verify_repo.py`;
   - `git diff --check`;
   - scoped review for frozen/runtime/dependency drift.

8. **Trace and human gate**
   - record exact commands/results and limitations;
   - keep plan active until Vladimir independently accepts D-021 and the reviewed `progress-v1.1` package;
   - only then move plan to completed and allow downstream tasks to treat R03A as accepted.

## Required task-specific tests

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

## Acceptance checklist

- [x] Issue created and task scope recorded.
- [x] Scoped branch created from the accepted MS7-R02A main baseline.
- [x] Active execution plan created.
- [ ] Repository coupling audit completed.
- [ ] ADR D-021 drafted.
- [ ] `progress-v1.1` addendum drafted.
- [ ] Neutral/late/parity fixtures added.
- [ ] Pure reference/replay implementation added.
- [ ] R03A task tests pass.
- [ ] Existing R03 tests pass unchanged.
- [ ] Canonical repository verification passes.
- [ ] Trace records exact final evidence.
- [ ] Vladimir independently accepts the contract package.
- [ ] Final-SHA CI/merge gate completed.
- [ ] Plan moved to completed only after acceptance.

## Downstream handoff

After human acceptance, the accepted R03A package becomes input to the downstream tasks named by v7.1, primarily **MS7-R11** and **MS7-V08**.

Until acceptance, downstream work may inspect the candidate but must not treat it as frozen upstream authority.
