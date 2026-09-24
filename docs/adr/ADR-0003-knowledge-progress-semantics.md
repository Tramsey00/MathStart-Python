# ADR-0003: Pilot Knowledge Graph and ProgressEvent Semantics

- **Status:** Accepted
- **Date:** 2026-09-24
- **Decision owner:** Ruslan; backup Vladimir
- **Related issue:** https://github.com/Tramsey00/MathStart-Python/issues/6
- **Related plan:** `docs/exec-plans/active/R03-knowledge-progress-contract.md`
- **Related specs:** `specs/knowledge/R03-knowledge-graph.md`, `specs/progress/R03-progress-contract.md`
- **Supersedes:** the `KnowledgeEvent` name in current architecture wording; no event data or numerical rule is replaced

## Context

R01 preserved the exact MathStart v3.1 Progress Algorithm v1 in `specs/progress/BASELINE-v1.md`. R02 established the exercise, hint, reveal, and validation boundaries. R03 must make the pilot graph and event projection reproducible before Django persistence exists. The R03 human review approved the decisions below; this ADR records them for the final contract gate.

## Decision: objective pilot graph

The canonical graph version is `pilot-v1`. It contains exactly the ten stable Skill codes in `specs/knowledge/fixtures/pilot-skills-v1.json` and exactly the thirteen edges in `specs/knowledge/fixtures/pilot-dependencies-v1.json`. Every edge has weight 1.0 and points **prerequisite -> dependent**. The graph is a DAG. Duplicate edges, references to missing skills, self-edges, and cycles are invalid.

`basic_arithmetic` is an external prerequisite for entering the pilot. It is not one of the ten `pilot-v1` Skills and cannot be a `SkillDependency` endpoint. External entrance eligibility must be represented separately, with no dangling skill reference. `interaction_mode` remains Assessment metadata, never a Skill.

FR-16's pilot ancestor query traverses these stored edges backward from dependent to prerequisite through depth 2. It returns each code at minimum depth in deterministic `(depth, code)` order and rejects an unknown Skill. The stored edge direction remains prerequisite to dependent.

Topic and Skill are different concepts. R03 references the Content-owned topic abstraction, currently `ContentPage(page_type=topic)`, without creating another Topic model. Content owns eventual `TopicSkill` mapping. Exact Django FK/persistence design is deferred to a later implementation task.

## Decision: one canonical progress event

`ProgressEvent` is the sole current name for the persisted progress-evidence event. The old `KnowledgeEvent` wording in accepted historical material is superseded terminology, **not** a second event type, model, log, or source of truth. Only Progress may mutate `UserSkillState` through accepted, validated `ProgressEvent`s. An exercise view, Tutor, Analyzer, frontend, or LLM provider cannot write the projection directly.

Progress v1 keeps all numerical effects, the mastery formula, difficulty coefficients, repeat cap, and status thresholds in `specs/progress/BASELINE-v1.md` **unchanged**. This ADR adds no replacement formula. The R03 contract specifies the accepted operational rules:

- evidence_count includes accepted self-report, correct, wrong, misconception, and diagnostic events, but excludes `ANSWER_REVEALED`;
- confidence adds its baseline delta directly and is clamped to 0..100; difficulty and repeat multipliers apply only to mastery;
- status uses ordered precedence: no evidence, mastered threshold, weak threshold, then learning;
- self-report initializes to 60/15 at most once before assessed evidence; later/duplicate self-report cannot project;
- the recent window is the last ten completed attempts per user/skill; first-try and unassisted diagnostic correct attempts can qualify as independent;
- confirmed misconception repeat is keyed by user, skill, and misconception code, using 1.0, 1.25, then 1.5; an independent correct attempt for the skill resets the repeat state;
- numeric difficulty 1-2/3/4 and R02's easy/medium/hard strings normalize to the same baseline bands, with no default for invalid/missing assessed difficulty;
- each accepted event calculates, clamps, then uses Decimal `ROUND_HALF_UP` to two places before persisting the projection;
- `event_id` and the attempt/skill/event-kind/evidence-ref source tuple enforce idempotency; exact retry is a no-op and conflicting payload is rejected;
- one evidence unit emits one normalized negative `ProgressEvent`: a confirmed `MISCONCEPTION_DETECTED`, otherwise `WRONG_ATTEMPT`; a same-evidence pair is rejected, while raw Assessment/Analyzer facts may remain outside Progress;
- replay sorts by `(occurred_at, event_id, policy_version)`, applies each event using its recorded policy version, and reprojects a user/skill after a valid late event.

The canonical `UserSkillState` fields are `mastery`, `confidence`, `evidence_count`, `status`, `last_updated`, and `reducer_version`. R03 sets `reducer_version` to `progress-v1`, initializes `last_updated` to null, and sets it to the final projecting event's `occurred_at` in replay order. This follows the Technical Specification; the `last_evaluated_at` label in the older baseline transcription is not introduced as a second state field. An immutable Assessment `completed_at` fact may be before or after a `ProgressEvent`'s `occurred_at`; only timezone-aware normalization and same-attempt/skill consistency constrain it.

The same immutable event log must always replay to the same `UserSkillState`. R03's pure Python verifier tests this contract without Django models, database persistence, or a live LLM.

## Alternatives and consequences

Placing `basic_arithmetic` as an unseeded edge endpoint was rejected because it would violate referential integrity. Making it an eleventh pilot node was rejected by the approved ten-skill scope. Reversing edge direction would invert remediation queries. Keeping both `KnowledgeEvent` and `ProgressEvent` as separate current concepts was rejected because one action could be double counted or replayed inconsistently.

The contract now requires event identity, source facts, immutable policy version, deterministic ordering, and completed-attempt metadata. Later Django work must choose schema, transaction, concurrency, migration, and PostgreSQL details without changing these semantics. Repository-managed catalogue bootstrap must never overwrite historical student evidence.

## Verification and human gate

The R03 contract suite must cover the graph and every Progress rule above; the full repository verification remains required. This ADR does not claim runtime persistence verification. Final R03 human contract gate: ACCEPTED. R03 closure awaits PR merge into main. Official C-16 submission is a separate human gate.
