# SPEC R03: Pilot Knowledge Graph `pilot-v1`

- **Status:** Accepted
- **Owner:** Ruslan; backup Vladimir
- **Related issue:** https://github.com/Tramsey00/MathStart-Python/issues/6
- **Related ADR:** `docs/adr/ADR-0003-knowledge-progress-semantics.md`
- **Related plan:** `docs/exec-plans/active/R03-knowledge-progress-contract.md`
- **Fixtures:** `fixtures/pilot-skills-v1.json`, `fixtures/pilot-dependencies-v1.json`

## Scope and ownership

Knowledge owns stable atomic Skills and directed prerequisite relations. Content owns Topics and eventual Topic-to-Skill mappings. An exercise `interaction_mode` selects UX/validation behavior and is not a Skill. This contract defines repository-managed pilot catalogue facts and pure validation; it creates no Django model, FK, migration, management command, or runtime seed.

The current Content-owned topic abstraction is `ContentPage` with `page_type=topic`. A future `TopicSkill` reference must point to that Content-owned abstraction and a stable Skill code/reference, without creating a duplicate Topic source. The exact FK and migration design belongs to a later implementation task.

## Canonical inventory

Graph version `pilot-v1` contains exactly these ten Skill codes:

1. `integer_number_line`
2. `negative_numbers`
3. `sign_rules_add_sub`
4. `sign_rules_mul_div`
5. `distributive_property`
6. `expand_parentheses`
7. `combine_like_terms`
8. `equation_balance`
9. `linear_one_step`
10. `linear_parentheses`

The code is the stable subject-domain identifier; a display name may change without changing graph identity. The fixture enumerates each code exactly once. A duplicate or unknown code is invalid. No interaction-mode code can be included as a Skill.

`basic_arithmetic` is a prerequisite for **entering** the pilot, not a `pilot-v1` node. It is represented in the skills fixture as `external_prerequisite` metadata with `scope = pilot_entry` and `representation = outside_skill_dependency`. It must not occur in the `skills` array or either endpoint of an edge. A later onboarding/diagnostic component may determine entrance eligibility through an explicit contract; this graph does not fabricate a Skill reference or student state for it.

## Approved edges

Each row is `prerequisite -> dependent`, with weight `1.0`:

| Prerequisite | Dependent |
| --- | --- |
| `integer_number_line` | `negative_numbers` |
| `negative_numbers` | `sign_rules_add_sub` |
| `negative_numbers` | `sign_rules_mul_div` |
| `sign_rules_add_sub` | `distributive_property` |
| `sign_rules_mul_div` | `distributive_property` |
| `distributive_property` | `expand_parentheses` |
| `sign_rules_add_sub` | `combine_like_terms` |
| `expand_parentheses` | `combine_like_terms` |
| `combine_like_terms` | `equation_balance` |
| `equation_balance` | `linear_one_step` |
| `linear_one_step` | `linear_parentheses` |
| `expand_parentheses` | `linear_parentheses` |
| `combine_like_terms` | `linear_parentheses` |

`pilot-v1` has exactly 13 unique edges. Its topological order need not be unique, but every valid order places each prerequisite before its dependent. There is no self-edge or cycle.

## Deterministic ancestor query

`ancestors(skill_id, max_depth=2)` queries the validated `pilot-v1` graph without reversing its stored edges. Lookup traverses from the dependent Skill toward its prerequisites. Depth 1 contains direct prerequisites; depth 2 contains prerequisites of those direct prerequisites. Return each Skill code once at its **minimum** depth as `(skill_code, depth)`, ordered first by ascending depth and then lexicographically by code. A Skill not in `pilot-v1` is rejected. For this pilot, `max_depth` may be 0, 1, or 2; 0 returns an empty result, and invalid or greater values are rejected. `basic_arithmetic` is external entrance metadata, so it is never returned as a Skill ancestor.

For `linear_parentheses`, depth 1 is `combine_like_terms`, `expand_parentheses`, `linear_one_step`; depth 2 is `distributive_property`, `equation_balance`, `sign_rules_add_sub` in the specified deterministic order. If a Skill is reachable by more than one path, the minimum depth wins.

## Validation contract

Validate the complete candidate graph before accepting it or using it for a future seed:

1. require matching `graph_version = pilot-v1` in both fixtures;
2. require exactly the ten approved unique Skill codes, with no `basic_arithmetic` or mode code;
3. require external prerequisite metadata exactly as above;
4. require all 13 approved edge pairs, each appearing once, each endpoint present in the Skill inventory, each weight numerically 1.0;
5. reject a duplicate edge, unknown/missing skill reference, self-edge, or cycle independently, with a clear failure reason;
6. return a deterministic topological traversal (sort ready nodes by code) for verification and future read use.

The generic DAG validator also handles intentionally invalid test graphs so duplicate/unknown/self-edge/cycle failures can be tested separately from the strict `pilot-v1` inventory check. An archived or inactive Skill must not be deleted when referenced by historical evidence; lifecycle and DB constraints are deferred to the implementation contract.

## Acceptance and verification

`scripts/r03_contract_reference.py` and `tests/test_r03_contract.py` must load the JSON fixtures and verify the exact inventory, edges, direction, weights, external prerequisite, invalid-graph cases, and depth-2 ancestor query. These files are specification fixtures, not runtime `seed_data/knowledge/` input yet. No R01/R02 source or historical evidence is rewritten.
