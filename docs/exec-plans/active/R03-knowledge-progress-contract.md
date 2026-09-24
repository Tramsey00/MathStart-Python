# EXEC PLAN R03: Knowledge Graph and Exact Progress Contract

- **Status:** Active (contract accepted; awaiting PR merge into main)
- **Owner:** Ruslan
- **Backup owner:** Vladimir
- **Created:** 2026-09-24
- **Last updated:** 2026-09-24
- **Related issue:** https://github.com/Tramsey00/MathStart-Python/issues/6
- **Related specs:** `specs/progress/BASELINE-v1.md`, `specs/exercises/R02-exercise-architecture.md`
- **Related ADRs:** `docs/adr/ADR-0001-preserve-django.md`, `docs/adr/ADR-0002-exercise-contract-architecture.md`; ADR-0003 Accepted
- **Window:** W1
- **Estimate:** 12 hours
- **Target milestone:** R03 / W1
- **Human gate required:** Contract gate ACCEPTED; PR merge into main pending; C-16 official submission remains a separate human gate

## 1. Objective and current authorization

Audit the accepted repository state and deliver a contract-first R03 phase. R03 defines the approved `pilot-v1` Skill prerequisite DAG and an exact, replayable Progress v1 contract while preserving every numerical value in `specs/progress/BASELINE-v1.md`. The 2026-09-24 human review and final corrections fixed the semantics in sections 5-6. Before contract work, preserve this plan and the audit trace in an initial R03 planning/audit commit. The contract phase in sections 7-9 is now authorized. Django models, migrations, services, runtime seed, database persistence and official C-16 submission remain outside this phase.

## 2. Current repository state

- The initial audit began at `a45ca2c` on `R02-exercise-architecture`, with local `main` at `0a5398d`. R02 was already merged into remote `main` as PR #5. The repository was then normalized without changing R01/R02 history: local `main` fast-forwarded to `origin/main` at `951ad487f75362081e7ec53f50b2efd9c97055b1`, and `R03-knowledge-progress` was created from it. The two R03 audit/plan files stayed untracked and intact on that branch.
- R01 and R02 have accepted human gates in their completed plans and traces. R02 is a specification-only addition; it introduced no Assessment, Knowledge, or Progress app.
- Current Django persistence is `content/models.py` plus `content/migrations/0001_initial.py`. `ContentPage(page_type=topic)` represents a topic. There is no `Skill`, `SkillDependency`, `ProgressEvent`, `UserSkillState`, or `TopicSkill` model. `config/settings.py` uses SQLite; `requirements.txt` pins Django 5.2.16. At audit time, architecture text still used the older `KnowledgeEvent` name; the contract-phase terminology update and accepted ADR-0003 establish `ProgressEvent` as its sole canonical replacement without a second persisted event type.
- Existing tests cover content quality, publication, and bootstrap, including bootstrap idempotency. No graph or Progress tests/fixtures exist. The seven R02 JSON fixtures are public exercise/exchange examples, not runtime seeds. GitHub Issue R03 is https://github.com/Tramsey00/MathStart-Python/issues/6.
- The configured `.venv` launcher points to an absent Python 3.10 executable. The bundled Python 3.12.14 with existing `.venv/Lib/site-packages` ran `scripts/verify_repo.py`: 6/6 checks passed, including 15 tests. The normal `python` command remains unavailable in `PATH`.

## 3. Accepted constraints and remaining contract work

| Area | Accepted contract | Gap for R03 |
| --- | --- | --- |
| Topic / Skill | `PRODUCT.md` section 12 and `ARCHITECTURE.md` sections 9, 11: separate concepts; Content owns `TopicSkill`; Knowledge owns Skill and dependencies | Define the reference contract against the Content-owned topic abstraction. Exact DB persistence/FK remains for a later task; do not create a duplicate Topic model |
| Modes | ADR-0002: `interaction_mode` is exercise behavior, never a skill | Seed/spec validation must exclude modes as skills |
| Graph | Human review approved exactly ten skills and thirteen weighted edges for `pilot-v1`; `basic_arithmetic` is external | Encode and executably validate references, direction, uniqueness, self-edge and cycle rejection; no runtime seed yet |
| Progress | `BASELINE-v1.md` fixes event effects, formula, coefficients and thresholds; review approved the exact evidence/replay rules below | Write the normative contract and golden cases; no Django projection exists yet |
| Difficulty | Baseline defines easy=.8, medium=1.0, hard=1.2; R02 fixtures use category strings | Normalize numeric 1-4 and existing strings to the approved bands; reject missing/invalid assessed difficulty, with no silent default |
| Evidence | ADR-0002 requires observable hint/reveal facts and no unsupported diagnosis | Specify validated event intake and one-penalty behavior; Assessment persistence remains outside the contract phase |
| Naming | Human review selects `ProgressEvent` as the sole event term | Update current normative documents in the contract phase; leave completed R01/R02 history intact and supersede historical wording through ADR-0003 |

## 4. Numerical baseline to preserve verbatim

`SELF_REPORTED_KNOWN` initializes mastery=60 and confidence=15. Mastery base deltas / confidence evidence are: `CORRECT_FIRST_TRY` +6/+5, `CORRECT_AFTER_HINT` +3/+4, `WRONG_ATTEMPT` -2/+3, `MISCONCEPTION_DETECTED` -5/+5, `ANSWER_REVEALED` 0/0, `DIAGNOSTIC_CORRECT` +8/+8, `DIAGNOSTIC_WRONG` -6/+8. Mastery uses `clamp(old + base_delta * difficulty_coeff * repeat_coeff, 0, 100)`. Difficulty coefficients are easy=.8, medium=1.0, hard=1.2. Repeated confirmed misconception coefficient is capped at 1.5. `NOT_STARTED` has evidence_count=0; `WEAK` requires mastery<50 and confidence>=30; `MASTERED` requires mastery>=80, confidence>=60, and at least three recent independent correct attempts; other states with evidence are `LEARNING`. Topic mastery is a weighted mean by `topic_skills.importance`; MVP has no time decay. These numbers and thresholds are not proposed for revision.

## 5. Approved Knowledge Graph semantics for the contract phase

Canonical graph version: `pilot-v1`. The only pilot nodes are `integer_number_line`, `negative_numbers`, `sign_rules_add_sub`, `sign_rules_mul_div`, `distributive_property`, `expand_parentheses`, `combine_like_terms`, `equation_balance`, `linear_one_step`, and `linear_parentheses`. `basic_arithmetic` is an external prerequisite for entering the pilot: it is neither a `pilot-v1` node nor a `SkillDependency` edge endpoint. The contract must state how that external condition is represented without a dangling graph reference.

Every approved edge below has weight `1.0` and points from prerequisite to dependent:

```text
integer_number_line -> negative_numbers
negative_numbers -> sign_rules_add_sub
negative_numbers -> sign_rules_mul_div
sign_rules_add_sub -> distributive_property
sign_rules_mul_div -> distributive_property
distributive_property -> expand_parentheses
sign_rules_add_sub -> combine_like_terms
expand_parentheses -> combine_like_terms
combine_like_terms -> equation_balance
equation_balance -> linear_one_step
linear_one_step -> linear_parentheses
expand_parentheses -> linear_parentheses
combine_like_terms -> linear_parentheses
```

The pilot is a DAG. Contract validation rejects duplicate edges, unknown/missing skill references, self-edges and cycles. `interaction_mode` is exercise metadata, never a Skill. R03 defines Topic references against the Content-owned topic abstraction; exact database persistence/FK is deferred. No duplicate Topic model is proposed.

FR-16 additionally requires `ancestors(skill_id, max_depth=2)`: traverse from dependent toward prerequisites over the stored prerequisite-to-dependent edges, return each code at minimum depth in deterministic `(depth, code)` order, and reject unknown skills. The pilot supports depths 0 through 2 without adding nodes or edges.

## 6. Approved Progress semantics for the contract phase

**Canonical event.** Use `ProgressEvent` throughout new and current normative contracts; it is the sole persisted progress-event concept. `UserSkillState` is its per-user/skill projection. Historical R01/R02 wording must not result in a second model or event stream. The event contract records `event_id`, user/skill, `event_kind`, source/attempt/evidence reference, `occurred_at`, recorded policy version, difficulty where assessed, and the validated facts needed for hint/reveal, independent correct work and misconception identity.

**Evidence count and status.** Count accepted evidence-bearing `ProgressEvent`s of types `SELF_REPORTED_KNOWN`, `CORRECT_FIRST_TRY`, `CORRECT_AFTER_HINT`, `WRONG_ATTEMPT`, `MISCONCEPTION_DETECTED`, `DIAGNOSTIC_CORRECT`, and `DIAGNOSTIC_WRONG`. `ANSWER_REVEALED` does not increment `evidence_count`. Evaluate status in this precedence: (1) `evidence_count == 0` -> `NOT_STARTED`; (2) mastery >= 80, confidence >= 60, and at least three recent independent correct attempts -> `MASTERED`; (3) mastery < 50 and confidence >= 30 -> `WEAK`; (4) otherwise `LEARNING`.

**Canonical state fields.** `UserSkillState` includes `mastery`, `confidence`, `evidence_count`, `status`, `last_updated`, and `reducer_version`. For R03, `reducer_version = progress-v1`; `last_updated` starts null and then equals `occurred_at` of the final projecting event in replay order. The older `last_evaluated_at` baseline-transcription label is not introduced as a second current field.

**Projection arithmetic.** Preserve all event values and the mastery formula in section 4 and `specs/progress/BASELINE-v1.md`. `new_confidence = clamp(old_confidence + confidence_delta, 0, 100)`; difficulty and repeat multipliers never apply to confidence. `repeat_coeff` differs from 1.0 only for `MISCONCEPTION_DETECTED`. For each accepted event calculate, clamp to 0..100, then `ROUND_HALF_UP` to two decimal places and persist the projection. Normative arithmetic uses decimal values, not binary float.

**Self-report and reveal.** `SELF_REPORTED_KNOWN` applies at most once per user/skill, only before any assessed event, initializing mastery=60 and confidence=15. The planned intake contract rejects a duplicate or late self-report without appending a projecting event; its error response must be specified. `ANSWER_REVEALED` adds no mastery/confidence, does not count as evidence, and prevents independent first-try evidence for the same attempt.

**Difficulty.** Normalize 1 or 2 -> `EASY` -> 0.8, 3 -> `MEDIUM` -> 1.0, 4 -> `HARD` -> 1.2. Existing R02 strings `easy`/`medium`/`hard` normalize to the same bands. Do not rewrite R02 fixtures for this mapping. Missing or invalid difficulty on an assessed event has no silent default and must be rejected with a contract-defined error.

**Recent independent work.** The recent window is the last 10 completed attempts for the user/skill. An independent correct result belongs to a distinct completed attempt and precedes any hint/reveal. `CORRECT_FIRST_TRY` qualifies; `DIAGNOSTIC_CORRECT` qualifies only without help/reveal; `CORRECT_AFTER_HINT` does not qualify. Incomplete attempts do not occupy the window. The contract-level fixtures must make ordering and per-skill membership explicit.

`completed_at` is an immutable Assessment completion fact normalized from timezone-aware RFC 3339. It can be before or after `ProgressEvent.occurred_at`; only same-attempt/skill consistency is required, with no temporal ordering constraint between the two facts.

**Misconception repeat.** Track repeat state by `(user, skill, misconception_code)`. The first, second, and third or later confirmed occurrence uses coefficients 1.0, 1.25, and 1.5. Other wrong events do not increment it. An independent correct attempt for the skill resets the misconception repeat state. Only `MISCONCEPTION_DETECTED` receives a repeat multiplier; the contract must demonstrate the reset across codes for the affected skill.

**Idempotency and single penalty.** `event_id` is unique. `(attempt_id, skill_id, event_kind, evidence_ref)` is also unique for attempt-derived events. Exact duplicate delivery is a no-op returning the existing result; the same identity with conflicting payload is a conflict. For one `(user_id, skill_id, attempt_id, evidence_ref)` unit, emit `MISCONCEPTION_DETECTED` if a specific misconception is confirmed; otherwise emit `WRONG_ATTEMPT`. The two kinds together for that unit are rejected as an invalid `ProgressEvent` combination. A raw wrong fact may remain in Assessment/Analyzer data, but it is not a second Progress event. Two negative events in one attempt require different evidence references and both must carry `independent_evidence_rule = distinct_validated_steps`.

**Ordering and replay.** The normative deterministic total-order key is `(occurred_at, event_id, policy_version)`, explicitly including all three fields from the Technical Specification. Apply each immutable event using its recorded `policy_version`. A valid late/backfilled event triggers reprojection of the affected user/skill from that ordered log. Replaying the same immutable log must yield the same `UserSkillState`, independent of delivery order. The contract must specify timestamp normalization and event identity validation without changing the approved order.

## 7. Exact authorized file set for the contract phase

| File | Proposed change |
| --- | --- |
| `specs/knowledge/R03-knowledge-graph.md` | Create normative `pilot-v1` inventory, 13 edges/weights, external prerequisite and Content-owned Topic reference contract |
| `specs/knowledge/fixtures/pilot-skills-v1.json` | Create exactly ten versioned pilot Skill examples |
| `specs/knowledge/fixtures/pilot-dependencies-v1.json` | Create the 13 approved directed edges with weight 1.0 |
| `specs/progress/R03-progress-contract.md` | Create normative `ProgressEvent`/`UserSkillState`, projection, replay, error and idempotency contract; refer to unchanged baseline |
| `specs/progress/fixtures/progress-v1-cases.json` | Create golden event streams and expected per-event/final states |
| `scripts/r03_contract_reference.py` | Create pure Python reference graph validation and decimal Progress projection; no Django/DB dependency |
| `tests/test_r03_contract.py` | Create standard-library `unittest` contract suite covering the section 9 matrix |
| `scripts/verify_repo.py` | Add the contract suite to the existing verification entry point after it exists |
| `skills/verification/SKILL.md` | Document the real contract check and exact command/results, without claiming unconfigured tooling |
| `docs/adr/ADR-0003-knowledge-progress-semantics.md` | Create required ADR for accepted graph, external prerequisite, event/replay/idempotency, difficulty and one-penalty semantics; state that Progress v1 numbers are unchanged |
| `AGENTS.md` | Align current repository map to sole `ProgressEvent` term |
| `PRODUCT.md` | Align current product-level event terminology without changing numerical baseline or product scope |
| `ARCHITECTURE.md` | Align current architecture event name/flow to `ProgressEvent` and record ADR-0003 precedence; preserve domain ownership |
| `docs/exec-plans/active/EXEC-PLAN-TEMPLATE.md` | Align future plan template's event term |
| `docs/agent-traces/TRACE-TEMPLATE.md` | Align future trace template's event term |
| `docs/submission/C-16-draft.md` | Create draft package: project title, short description, public GitHub URL, missing full-name/group checklist, and official-submission gate before 2026-10-09 |
| `docs/exec-plans/active/R03-knowledge-progress-contract.md` | Record accepted contract results, verification and review status |
| `docs/agent-traces/R03-knowledge-progress-audit.md` | Append observable contract-phase actions/results and review outcome |

This file set is authorized for the contract phase after the initial planning/audit commit. `specs/progress/BASELINE-v1.md`, the seven accepted R02 fixtures, accepted ADR-0001/0002, completed R01/R02 plans/traces, content source, models, migrations, runtime seed, and database data remain unchanged in this phase. Historical documents may retain the old event wording as a record of their accepted context; ADR-0003 and updated current normative documents establish `ProgressEvent` as the single current name. No second persisted event type is introduced.

## 8. Execution sequence

1. **Knowledge contract and ADR.** Create ADR-0003, `specs/knowledge/R03-knowledge-graph.md`, and two graph fixtures. Confirm exactly ten nodes, thirteen edges, weight 1.0, no `basic_arithmetic` node/edge, and Content-owned Topic references. Record the unchanged Progress v1 numerical authority in ADR-0003.
2. **Progress contract and golden cases.** Create `specs/progress/R03-progress-contract.md` and `progress-v1-cases.json` using the approved section 6 semantics. Specify field validation, invalid-event responses and versioned replay. Cross-check every number with `BASELINE-v1.md` and hint/reveal semantics with R02.
3. **Executable contract verification.** Add pure Python reference logic and `unittest` tests. Cover every row of section 9; run without Django models, database persistence, PostgreSQL or live LLM. Register the command in `scripts/verify_repo.py` and document it in `skills/verification/SKILL.md` only once it runs.
4. **Current terminology and C-16 draft.** Update current normative root docs/templates to `ProgressEvent`; do not rewrite historical R01/R02 artifacts. Create the C-16 draft with public GitHub URL and explicit placeholders for missing full names/groups. Do not submit it officially.
5. **Verification and trace.** Run the contract suite, JSON parsing/graph checks, `git diff --check`, and the full `scripts/verify_repo.py` in a configured Python 3.12+ environment. Record actual interpreter, results, failures and scope in the R03 trace. Inspect the complete diff for numerical baseline, R01/R02, migration, model, service and seed changes.
6. **Human gates.** Present ADR/spec/fixtures/tests/C-16 draft for review. Keep this plan active until the accepted contract PR is merged into main; then record merge evidence before moving it to `completed/`. Official C-16 submission is a separate human action/gate before 2026-10-09.

Django model, migration, service, app configuration, Content `TopicSkill` persistence and runtime seed work require a later implementation plan and approval. Do not edit applied migrations or let content bootstrap overwrite user evidence.

## 9. Executable fixture/test matrix

All cases below must execute through `tests/test_r03_contract.py` and be covered by the fixture/reference paths in section 7. Do not defer them all to future Django tests.

| Area | Required executable cases |
| --- | --- |
| Graph | Independent literal expectations for exactly ten codes and thirteen edges; direction and 1.0 weights; valid topological order; duplicate edge; unknown skill; self-edge; cycle; `basic_arithmetic` only as external entrance prerequisite and no dangling graph edge; `interaction_mode` excluded; deterministic depth-2 ancestors with minimum depth and unknown-skill rejection |
| Events | Independent literal expectation for all eight `ProgressEvent` kinds, unchanged base effects, evidence_count membership, reveal zero and no count, wrong-final-answer misconception guard |
| Difficulty/confidence | Inputs 1,2,3,4 and R02 strings; missing/invalid assessed difficulty rejection; confidence additive and unscaled by difficulty/repeat |
| Arithmetic/status | Clamp at 0/100; per-accepted-event decimal `ROUND_HALF_UP` to two places; status precedence and exact 50/80 mastery and 30/60 confidence boundaries |
| Self-report | One pre-assessment initialization; duplicate and post-assessment rejection without projection/count change |
| Misconception | Same-code 1.0/1.25/1.5/1.5; distinct code keyed separately; other wrong does not increment; independent correct resets state for the skill; repeat multiplier applies only to misconception event |
| Recent window | Last 10 versus 11 completed attempts per skill; distinct independent correct attempts; first-try and unassisted diagnostic correct qualify; hinted/revealed and incomplete attempts do not qualify |
| Replay | Deterministic `(occurred_at, event_id, policy_version)` order, equal timestamps, reordered delivery, valid late event reprojection, apply each recorded policy version, identical canonical `UserSkillState` fields from the same immutable log; `last_updated` null initially and `reducer_version=progress-v1`; completion before and after event occurrence valid, conflicting completion fact rejected |
| Idempotency/penalty | Duplicate `event_id`; duplicate source tuple; same identity/conflicting payload; reject same-evidence wrong plus misconception ProgressEvents; separate evidence only under explicit rule |

## 10. Human gates and ADR

- **Semantic review:** Completed on 2026-09-24 with the required corrections recorded in sections 5-6.
- **Revised-plan gate:** Approved with final metadata and replay corrections. An initial planning/audit commit precedes contract-file work.
- **ADR-0003:** Required in the contract phase. It must document `pilot-v1`, edge meaning, `basic_arithmetic`, `ProgressEvent` semantics, replay, idempotency, difficulty normalization and one-penalty rule, and explicitly preserve the numerical Progress v1 baseline.
- **R03 contract gate:** The first contract review required depth-2 ancestors, canonical `UserSkillState` fields, normalized single-negative ProgressEvents, valid completion timing on both sides of occurrence, and independent literal test expectations. These corrections are implemented, verified and ACCEPTED by the final human contract review. R03 remains active until its PR is merged into main.
- **C-16 official submission:** Separate human gate before 2026-10-09. The contract phase creates only a draft/checklist; missing full names and groups remain placeholders until supplied.

## 11. Risks, dependencies and remaining blockers

- **Planning baseline:** Issue #6 exists; `R03-knowledge-progress` started at the same commit as updated local and remote `main`. The intact R03 audit/plan files were preserved in planning commit `37417a1` before contract work.
- **Contract review gate:** ACCEPTED: the completed ADR/spec/fixture/test package is approved for commit and PR. Merge into main remains pending.
- **Terminology dependency:** The audit found older event wording in `ARCHITECTURE.md`, `PRODUCT.md`, `AGENTS.md` and templates. The contract-phase edits and accepted ADR-0003 reconcile it without rewriting accepted R01/R02 history; final contract acceptance is recorded.
- **Persistence dependency:** The exact Topic FK and user-evidence schema are deferred; no duplicate Topic model or invented migration is allowed here. Assessment attempts and PostgreSQL readiness also remain later implementation work.
- **Submission information:** Full names and groups are not in the repository. They block a complete official C-16 submission, not the draft checklist. The deadline and official gate must be visible in that draft.
- **Environment:** The local `.venv` launcher points to absent Python 3.10. Contract verification must run with an available Python 3.12+ and report the exact command/interpreter. Legacy self-check `<details>` content remains outside the new reveal contract.

## 12. Verification and current gate

Planning/audit commit `37417a1` preceded contract work. After the first contract human-review corrections, the suite ran with bundled Python 3.12.14 and passed 18 tests. All 10 JSON fixtures parsed. The full `scripts/verify_repo.py` run passed 7/7 checks: Django check; migration consistency (`No changes detected`); 263 lesson sources; content quality; site integrity; 15 Django tests; and 18 R03 contract tests. `git diff --check` passed with the new files included as Git intent-to-add. The normal project `.venv` launcher still references absent Python 3.10, so verification used the bundled interpreter with the project's site-packages. Exact commands and results are recorded in the trace. These checks verify the pure contract and existing Django baseline; they do not verify PostgreSQL, runtime Knowledge/Progress behavior, or database persistence. The final human contract gate is **ACCEPTED**. Commit and PR creation are authorized. **Keep R03 active until the PR is merged into main**, then record merge evidence and complete the plan.
