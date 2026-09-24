"""Executable R03 graph and Progress v1 contract checks; no Django required."""

from __future__ import annotations

import copy
import json
import unittest
from decimal import Decimal
from pathlib import Path

from scripts.r03_contract_reference import (
    ASSESSED_KINDS,
    EVENT_KINDS,
    ContractError,
    IdentityConflict,
    PILOT_CODES,
    PILOT_EDGES,
    ancestors,
    clamp_round,
    event_order,
    ingest_event,
    normalize_difficulty,
    replay,
    status_for,
    validate_event,
    validate_graph,
    validate_pilot_graph,
)


ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_FIXTURES = ROOT / "specs" / "knowledge" / "fixtures"
PROGRESS_FIXTURE = ROOT / "specs" / "progress" / "fixtures" / "progress-v1-cases.json"

# Independent contract expectations: fixture and reference must both match them.
EXPECTED_PILOT_CODES = frozenset({
    "integer_number_line", "negative_numbers", "sign_rules_add_sub",
    "sign_rules_mul_div", "distributive_property", "expand_parentheses",
    "combine_like_terms", "equation_balance", "linear_one_step",
    "linear_parentheses",
})
EXPECTED_PILOT_EDGES = frozenset({
    ("integer_number_line", "negative_numbers"),
    ("negative_numbers", "sign_rules_add_sub"),
    ("negative_numbers", "sign_rules_mul_div"),
    ("sign_rules_add_sub", "distributive_property"),
    ("sign_rules_mul_div", "distributive_property"),
    ("distributive_property", "expand_parentheses"),
    ("sign_rules_add_sub", "combine_like_terms"),
    ("expand_parentheses", "combine_like_terms"),
    ("combine_like_terms", "equation_balance"),
    ("equation_balance", "linear_one_step"),
    ("linear_one_step", "linear_parentheses"),
    ("expand_parentheses", "linear_parentheses"),
    ("combine_like_terms", "linear_parentheses"),
})
EXPECTED_EVENT_KINDS = frozenset({
    "SELF_REPORTED_KNOWN", "CORRECT_FIRST_TRY", "CORRECT_AFTER_HINT",
    "WRONG_ATTEMPT", "MISCONCEPTION_DETECTED", "ANSWER_REVEALED",
    "DIAGNOSTIC_CORRECT", "DIAGNOSTIC_WRONG",
})


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def make_event(
    kind: str,
    event_id: str,
    minute: int,
    *,
    user_id: str = "student",
    skill_id: str = "negative_numbers",
    attempt_id: str | None = None,
    evidence_ref: str = "answer-1",
    difficulty: int | str = 3,
    completed: bool = True,
    **extra,
) -> dict:
    stamp = f"2026-09-24T12:{minute:02d}:00Z"
    event = {
        "event_id": event_id,
        "user_id": user_id,
        "skill_id": skill_id,
        "event_kind": kind,
        "occurred_at": stamp,
        "policy_version": "progress-v1",
    }
    if kind != "SELF_REPORTED_KNOWN":
        event.update(
            attempt_id=attempt_id or f"attempt-{event_id}",
            evidence_ref=evidence_ref,
        )
        if completed:
            event["completed_at"] = stamp
        if kind != "ANSWER_REVEALED":
            event["difficulty"] = difficulty
    if kind == "CORRECT_AFTER_HINT":
        event["hint_used"] = True
    if kind == "ANSWER_REVEALED":
        event["reveal_used"] = True
    if kind == "MISCONCEPTION_DETECTED":
        event.update(
            misconception_code="missing_distribution",
            confirmed=True,
            source_kind="STEP",
        )
    event.update(extra)
    return event


class PilotGraphContractTests(unittest.TestCase):
    def setUp(self):
        self.skills = load_json(KNOWLEDGE_FIXTURES / "pilot-skills-v1.json")
        self.dependencies = load_json(KNOWLEDGE_FIXTURES / "pilot-dependencies-v1.json")

    def test_exact_inventory_direction_weights_and_dag(self):
        order = validate_pilot_graph(self.skills, self.dependencies)
        self.assertEqual(len(order), 10)
        self.assertEqual(set(order), EXPECTED_PILOT_CODES)
        self.assertEqual(PILOT_CODES, EXPECTED_PILOT_CODES)
        self.assertEqual({row["code"] for row in self.skills["skills"]}, EXPECTED_PILOT_CODES)
        edges = self.dependencies["edges"]
        self.assertEqual(len(edges), 13)
        self.assertEqual({(e["prerequisite"], e["dependent"]) for e in edges}, EXPECTED_PILOT_EDGES)
        self.assertEqual(PILOT_EDGES, EXPECTED_PILOT_EDGES)
        self.assertTrue(all(Decimal(str(e["weight"])) == Decimal("1.0") for e in edges))
        positions = {code: index for index, code in enumerate(order)}
        self.assertTrue(all(positions[a] < positions[b] for a, b in EXPECTED_PILOT_EDGES))

    def test_depth_two_ancestors_are_minimal_deterministic_and_reverse_traversed(self):
        self.assertEqual(ancestors("linear_parentheses", 0), ())
        self.assertEqual(ancestors("linear_parentheses", 1), (
            ("combine_like_terms", 1),
            ("expand_parentheses", 1),
            ("linear_one_step", 1),
        ))
        expected = (
            ("combine_like_terms", 1),
            ("expand_parentheses", 1),
            ("linear_one_step", 1),
            ("distributive_property", 2),
            ("equation_balance", 2),
            ("sign_rules_add_sub", 2),
        )
        self.assertEqual(ancestors("linear_parentheses"), expected)
        self.assertEqual(len({code for code, _ in expected}), len(expected))
        self.assertEqual(ancestors("integer_number_line"), ())
        for invalid in ("missing_skill", "basic_arithmetic", None, []):
            with self.assertRaisesRegex(ContractError, "unknown pilot skill"):
                ancestors(invalid)
        for invalid_depth in (-1, 3, True, "2"):
            with self.assertRaisesRegex(ContractError, "max_depth"):
                ancestors("linear_parentheses", invalid_depth)

    def test_basic_arithmetic_is_external_and_modes_are_not_skills(self):
        external = self.skills["external_prerequisite"]
        self.assertEqual(external, {
            "code": "basic_arithmetic",
            "scope": "pilot_entry",
            "representation": "outside_skill_dependency",
        })
        self.assertNotIn("basic_arithmetic", PILOT_CODES)
        self.assertTrue(all("basic_arithmetic" not in pair for pair in PILOT_EDGES))
        self.assertFalse({"SELF_CHECK", "FINAL_ANSWER", "STEP_BY_STEP", "STRUCTURED_SOLUTION"} & PILOT_CODES)
        bad = copy.deepcopy(self.skills)
        bad["skills"].append({"code": "basic_arithmetic"})
        with self.assertRaisesRegex(ContractError, "ten approved"):
            validate_pilot_graph(bad, self.dependencies)
        bad = copy.deepcopy(self.skills)
        bad["external_prerequisite"]["representation"] = "skill_dependency"
        with self.assertRaisesRegex(ContractError, "external"):
            validate_pilot_graph(bad, self.dependencies)

    def test_duplicate_unknown_self_edge_cycle_and_reversed_edge_rejected(self):
        codes = [row["code"] for row in self.skills["skills"]]
        edges = self.dependencies["edges"]
        duplicate = edges + [dict(edges[0])]
        with self.assertRaisesRegex(ContractError, "duplicate edge"):
            validate_graph(codes, duplicate)
        unknown = edges + [{"prerequisite": "basic_arithmetic", "dependent": "negative_numbers", "weight": 1.0}]
        with self.assertRaisesRegex(ContractError, "unknown skill"):
            validate_graph(codes, unknown)
        self_edge = edges + [{"prerequisite": "negative_numbers", "dependent": "negative_numbers", "weight": 1.0}]
        with self.assertRaisesRegex(ContractError, "self-edge"):
            validate_graph(codes, self_edge)
        cyclic = edges + [{"prerequisite": "linear_parentheses", "dependent": "integer_number_line", "weight": 1.0}]
        with self.assertRaisesRegex(ContractError, "cycle"):
            validate_graph(codes, cyclic)
        reversed_edges = copy.deepcopy(self.dependencies)
        reversed_edges["edges"][0]["prerequisite"], reversed_edges["edges"][0]["dependent"] = (
            reversed_edges["edges"][0]["dependent"], reversed_edges["edges"][0]["prerequisite"]
        )
        with self.assertRaises(ContractError):
            validate_pilot_graph(self.skills, reversed_edges)
        wrong_weight = copy.deepcopy(self.dependencies)
        wrong_weight["edges"][0]["weight"] = 0.9
        with self.assertRaisesRegex(ContractError, "weights"):
            validate_pilot_graph(self.skills, wrong_weight)


class ProgressContractTests(unittest.TestCase):
    def test_golden_fixture_cases_and_all_event_kinds(self):
        fixture = load_json(PROGRESS_FIXTURE)
        self.assertEqual(fixture["fixture_version"], "progress-v1")
        seen = set()
        for case in fixture["cases"]:
            seen.update(event["event_kind"] for event in case["events"])
            result = replay(case["events"], case["user_id"], case["skill_id"])
            state = result["state"]
            for field, expected in case["expected"].items():
                self.assertEqual(state[field], expected, f"{case['id']}: {field}")
            self.assertEqual(set(state), set(case["expected"]))
            self.assertEqual(result["recent_window"]["independent_correct_count"],
                             case["expected_recent_independent_correct_count"])
        self.assertEqual(seen, EXPECTED_EVENT_KINDS)
        self.assertEqual(EVENT_KINDS, EXPECTED_EVENT_KINDS)
        self.assertEqual(len(ASSESSED_KINDS), 6)

    def test_canonical_state_fields_initial_and_replayed(self):
        initial = replay([], "student", "negative_numbers")["state"]
        self.assertEqual(initial, {
            "mastery": "0.00", "confidence": "0.00", "evidence_count": 0,
            "status": "NOT_STARTED", "last_updated": None,
            "reducer_version": "progress-v1",
        })
        self.assertNotIn("last_evaluated_at", initial)
        first = make_event("SELF_REPORTED_KNOWN", "initial-1", 1)
        reveal = make_event("ANSWER_REVEALED", "initial-2", 2)
        direct = replay([first, reveal], "student", "negative_numbers")["state"]
        reordered = replay([reveal, first], "student", "negative_numbers")["state"]
        self.assertEqual(direct, reordered)
        self.assertEqual(direct["last_updated"], "2026-09-24T12:01:00.000000Z")
        self.assertEqual(direct["reducer_version"], "progress-v1")

    def test_diagnostic_event_effects_and_independence(self):
        correct = make_event("DIAGNOSTIC_CORRECT", "d1", 1, difficulty=4)
        wrong = make_event("DIAGNOSTIC_WRONG", "d2", 2, difficulty=1)
        result = replay([correct, wrong], "student", "negative_numbers")
        state = result["state"]
        self.assertEqual((state["mastery"], state["confidence"], state["evidence_count"]), ("4.80", "16.00", 2))
        self.assertEqual(result["recent_window"]["independent_correct_count"], 1)
        helped = make_event("DIAGNOSTIC_CORRECT", "d3", 3, hint_used=True)
        result = replay([correct, wrong, helped], "student", "negative_numbers")
        self.assertEqual(result["recent_window"]["independent_correct_count"], 1)

    def test_difficulty_normalization_and_invalid_rejection(self):
        for value, expected in [
            (1, ("EASY", Decimal("0.8"))), (2, ("EASY", Decimal("0.8"))),
            (3, ("MEDIUM", Decimal("1.0"))), (4, ("HARD", Decimal("1.2"))),
            ("easy", ("EASY", Decimal("0.8"))),
            ("medium", ("MEDIUM", Decimal("1.0"))),
            ("hard", ("HARD", Decimal("1.2"))),
        ]:
            self.assertEqual(normalize_difficulty(value), expected)
        for invalid in (None, 0, 5, True, "3", "unknown"):
            with self.assertRaisesRegex(ContractError, "difficulty"):
                normalize_difficulty(invalid)
        bad = make_event("WRONG_ATTEMPT", "bad", 1)
        del bad["difficulty"]
        with self.assertRaisesRegex(ContractError, "difficulty"):
            replay([bad], "student", "negative_numbers")

    def test_confidence_is_unscaled_by_difficulty_or_repeat(self):
        events = [
            make_event("SELF_REPORTED_KNOWN", "s", 0),
            make_event("MISCONCEPTION_DETECTED", "e1", 1, difficulty=1),
            make_event("MISCONCEPTION_DETECTED", "e2", 2, difficulty=4),
        ]
        result = replay(events, "student", "negative_numbers")
        self.assertEqual([x["state"]["confidence"] for x in result["snapshots"]], ["15.00", "20.00", "25.00"])
        self.assertEqual(result["state"]["mastery"], "48.50")  # 60 - 4 - 5*1.2*1.25

    def test_decimal_round_half_up_and_clamp(self):
        fixture = load_json(PROGRESS_FIXTURE)
        for case in fixture["arithmetic_cases"]:
            self.assertEqual(format(clamp_round(case["input"]), ".2f"), case["expected"])
        with self.assertRaisesRegex(ContractError, "finite"):
            clamp_round("NaN")
        with self.assertRaisesRegex(ContractError, "finite"):
            clamp_round(float("inf"))

    def test_status_precedence_and_exact_boundaries(self):
        self.assertEqual(status_for(Decimal("90"), Decimal("90"), 0, 3), "NOT_STARTED")
        self.assertEqual(status_for(Decimal("80"), Decimal("60"), 3, 3), "MASTERED")
        self.assertEqual(status_for(Decimal("79.99"), Decimal("60"), 3, 3), "LEARNING")
        self.assertEqual(status_for(Decimal("80"), Decimal("59.99"), 3, 3), "LEARNING")
        self.assertEqual(status_for(Decimal("80"), Decimal("60"), 3, 2), "LEARNING")
        self.assertEqual(status_for(Decimal("49.99"), Decimal("30"), 1, 0), "WEAK")
        self.assertEqual(status_for(Decimal("50"), Decimal("30"), 1, 0), "LEARNING")
        self.assertEqual(status_for(Decimal("49.99"), Decimal("29.99"), 1, 0), "LEARNING")

    def test_self_report_once_before_assessed_and_reveal_no_gain(self):
        self_report = make_event("SELF_REPORTED_KNOWN", "s", 0)
        reveal = make_event("ANSWER_REVEALED", "r", 1)
        result = replay([self_report, reveal], "student", "negative_numbers")
        state = result["state"]
        self.assertEqual((state["mastery"], state["confidence"], state["evidence_count"], state["status"]),
                         ("60.00", "15.00", 1, "LEARNING"))
        self.assertIn("r", result["nonprojecting_event_ids"])
        with self.assertRaisesRegex(ContractError, "self-report allowed once"):
            replay([self_report, make_event("SELF_REPORTED_KNOWN", "s2", 2)], "student", "negative_numbers")
        with self.assertRaisesRegex(ContractError, "self-report allowed once"):
            replay([make_event("WRONG_ATTEMPT", "w", 0), make_event("SELF_REPORTED_KNOWN", "s3", 2)],
                   "student", "negative_numbers")
        # A backfilled self-report ordered before an assessed event is replayable.
        state = replay([make_event("WRONG_ATTEMPT", "w", 2), self_report], "student", "negative_numbers")["state"]
        self.assertEqual(state["mastery"], "58.00")

    def test_misconception_repeat_code_scope_hint_and_reset(self):
        events = [make_event("SELF_REPORTED_KNOWN", "s", 0)]
        for minute, event_id, code in [(1, "m1", "code-a"), (2, "m2", "code-b"),
                                        (3, "m3", "code-a"), (4, "m4", "code-a"),
                                        (5, "m5", "code-a")]:
            events.append(make_event("MISCONCEPTION_DETECTED", event_id, minute,
                                     misconception_code=code))
        result = replay(events, "student", "negative_numbers")
        # Separate code-b starts at 1.0; code-a continues 1.0, 1.25, 1.5, 1.5.
        self.assertEqual([x["state"]["mastery"] for x in result["snapshots"]],
                         ["60.00", "55.00", "50.00", "43.75", "36.25", "28.75"])
        events.append(make_event("WRONG_ATTEMPT", "w", 6))
        events.append(make_event("CORRECT_AFTER_HINT", "h", 7))
        events.append(make_event("MISCONCEPTION_DETECTED", "m6", 8,
                                 misconception_code="code-a"))
        result = replay(events, "student", "negative_numbers")
        self.assertEqual(result["state"]["mastery"], "22.25")  # -2 +3 -7.5
        events.append(make_event("DIAGNOSTIC_CORRECT", "dc", 9))
        events.append(make_event("MISCONCEPTION_DETECTED", "m7", 10,
                                 misconception_code="code-a"))
        result = replay(events, "student", "negative_numbers")
        self.assertEqual(result["state"]["mastery"], "25.25")  # +8 then reset to -5

    def test_recent_window_ten_completed_distinct_attempts(self):
        events = [make_event("CORRECT_FIRST_TRY", f"c{i:02d}", i, attempt_id=f"c-attempt-{i}")
                  for i in range(1, 16)]
        events += [make_event("WRONG_ATTEMPT", f"w{i:02d}", i, difficulty=1,
                              attempt_id=f"w-attempt-{i}") for i in range(16, 24)]
        result = replay(events, "student", "negative_numbers")
        state = result["state"]
        self.assertEqual((state["mastery"], state["confidence"]), ("77.20", "99.00"))
        self.assertEqual(result["recent_window"]["independent_correct_count"], 2)
        self.assertEqual(state["status"], "LEARNING")
        # Three new independent correct attempts bring the last-ten count to 3.
        events += [make_event("CORRECT_FIRST_TRY", f"n{i}", i,
                              attempt_id=f"n-attempt-{i}") for i in range(24, 27)]
        result = replay(events, "student", "negative_numbers")
        state = result["state"]
        self.assertEqual(result["recent_window"]["independent_correct_count"], 3)
        self.assertEqual(state["status"], "MASTERED")
        self.assertEqual(len(result["recent_window"]["attempt_ids"]), 10)
        incomplete = make_event("WRONG_ATTEMPT", "inc", 27, completed=False)
        result2 = replay(events + [incomplete], "student", "negative_numbers")
        self.assertEqual(result2["recent_window"]["attempt_ids"], result["recent_window"]["attempt_ids"])
        revealed = make_event("ANSWER_REVEALED", "rev", 28)
        result3 = replay(events + [revealed], "student", "negative_numbers")
        self.assertIn(revealed["attempt_id"], result3["recent_window"]["attempt_ids"])

    def test_reveal_and_wrong_final_cannot_create_unsupported_evidence(self):
        reveal = make_event("ANSWER_REVEALED", "r", 1, attempt_id="same", completed=False)
        after = make_event("CORRECT_FIRST_TRY", "c", 2, attempt_id="same")
        with self.assertRaisesRegex(ContractError, "after full reveal"):
            replay([reveal, after], "student", "negative_numbers")
        bad_misconception = make_event("MISCONCEPTION_DETECTED", "m", 3,
                                        source_kind="FINAL_ANSWER")
        with self.assertRaisesRegex(ContractError, "wrong final answer"):
            validate_event(bad_misconception)
        with self.assertRaisesRegex(ContractError, "confirmed"):
            validate_event(make_event("MISCONCEPTION_DETECTED", "m2", 4, confirmed=False))
        with self.assertRaisesRegex(ContractError, "completed attempt"):
            validate_event(make_event("CORRECT_FIRST_TRY", "incomplete", 5, completed=False))

    def test_total_order_reordered_delivery_late_event_and_recorded_version(self):
        self_report = make_event("SELF_REPORTED_KNOWN", "a", 0)
        wrong = make_event("WRONG_ATTEMPT", "b", 1)
        correct = make_event("CORRECT_FIRST_TRY", "c", 2)
        direct = replay([self_report, wrong, correct], "student", "negative_numbers")
        reordered = replay([correct, self_report, wrong], "student", "negative_numbers")
        self.assertEqual(direct, reordered)
        self.assertEqual(direct["ordered_event_ids"], ["a", "b", "c"])
        log, before, duplicate = ingest_event([self_report], correct)
        self.assertFalse(duplicate)
        self.assertEqual(before["state"]["mastery"], "66.00")
        log, after, duplicate = ingest_event(log, wrong)
        self.assertFalse(duplicate)
        self.assertEqual(after["state"]["mastery"], "64.00")
        self.assertEqual(after["state"], direct["state"])
        self.assertEqual(after["state"]["last_updated"], "2026-09-24T12:02:00.000000Z")
        self.assertEqual(after["state"]["reducer_version"], "progress-v1")
        same_time_a = make_event("WRONG_ATTEMPT", "aaa", 3)
        same_time_b = make_event("WRONG_ATTEMPT", "bbb", 3)
        result = replay([same_time_b, same_time_a], "student", "negative_numbers")
        self.assertEqual(result["ordered_event_ids"], ["aaa", "bbb"])
        self.assertEqual(len(event_order(validate_event(same_time_a))), 3)
        timezone_event = make_event("WRONG_ATTEMPT", "tz", 4)
        timezone_event["occurred_at"] = "2026-09-24T15:04:00+03:00"
        self.assertEqual(validate_event(timezone_event)["occurred_at"], "2026-09-24T12:04:00.000000Z")
        too_precise = make_event("WRONG_ATTEMPT", "precision", 5)
        too_precise["occurred_at"] = "2026-09-24T12:05:00.0000001Z"
        with self.assertRaisesRegex(ContractError, "RFC 3339"):
            validate_event(too_precise)
        unknown_policy = make_event("WRONG_ATTEMPT", "p", 5, policy_version="progress-v2")
        with self.assertRaisesRegex(ContractError, "policy_version"):
            replay([unknown_policy], "student", "negative_numbers")

    def test_completion_fact_may_precede_or_follow_event_and_must_be_consistent(self):
        completion_before = make_event("CORRECT_FIRST_TRY", "before", 1,
                                       attempt_id="before-attempt",
                                       completed_at="2026-09-24T11:59:00Z")
        completion_after = make_event("CORRECT_FIRST_TRY", "after", 2,
                                      attempt_id="after-attempt",
                                      completed_at="2026-09-24T12:05:00Z")
        self.assertLess(validate_event(completion_before)["completed_at"],
                        validate_event(completion_before)["occurred_at"])
        self.assertGreater(validate_event(completion_after)["completed_at"],
                           validate_event(completion_after)["occurred_at"])
        result = replay([completion_after, completion_before], "student", "negative_numbers")
        self.assertEqual(result["recent_window"]["attempt_ids"], ["before-attempt", "after-attempt"])
        self.assertEqual(result["recent_window"]["independent_correct_count"], 2)
        consistent_reveal = make_event("ANSWER_REVEALED", "same-timezone", 3,
                                       attempt_id="after-attempt",
                                       completed_at="2026-09-24T15:05:00+03:00")
        replay([completion_after, consistent_reveal], "student", "negative_numbers")
        conflicting_reveal = dict(consistent_reveal, event_id="different-time",
                                  completed_at="2026-09-24T12:06:00Z")
        with self.assertRaisesRegex(ContractError, "conflicting completion time"):
            replay([completion_after, conflicting_reveal], "student", "negative_numbers")

    def test_idempotency_conflicts_and_one_penalty_per_evidence(self):
        wrong = make_event("WRONG_ATTEMPT", "w", 1, attempt_id="same", evidence_ref="step-1")
        log, result, duplicate = ingest_event([], wrong)
        self.assertFalse(duplicate)
        log2, same, duplicate = ingest_event(log, copy.deepcopy(wrong))
        self.assertTrue(duplicate)
        self.assertEqual(len(log2), 1)
        self.assertEqual(same["state"], result["state"])
        changed = dict(wrong, difficulty=4)
        with self.assertRaises(IdentityConflict):
            ingest_event(log, changed)
        new_id = dict(wrong, event_id="new-id")
        with self.assertRaises(IdentityConflict):
            ingest_event(log, new_id)
        misconception = make_event("MISCONCEPTION_DETECTED", "m", 2,
                                   attempt_id="same", evidence_ref="step-1",
                                   completed_at=wrong["completed_at"])
        # The wrong Assessment fact may remain outside Progress, but two
        # negative ProgressEvents for one unit invalidate the event log.
        for pair in ([wrong, misconception], [misconception, wrong]):
            with self.assertRaisesRegex(ContractError, "same evidence unit"):
                replay(pair, "student", "negative_numbers")
        with self.assertRaisesRegex(ContractError, "same evidence unit"):
            ingest_event([wrong], misconception)
        result = replay([misconception], "student", "negative_numbers")
        self.assertEqual((result["state"]["mastery"], result["state"]["confidence"],
                          result["state"]["evidence_count"]), ("0.00", "5.00", 1))
        self.assertNotIn("w", result["nonprojecting_event_ids"])
        separate = dict(wrong, event_id="w2", attempt_id="other")
        result = replay([misconception, separate], "student", "negative_numbers")
        self.assertEqual(result["state"]["evidence_count"], 2)
        self.assertEqual(result["state"]["confidence"], "8.00")
        distinct_same_attempt = make_event(
            "MISCONCEPTION_DETECTED", "different-step", 2,
            attempt_id="same", evidence_ref="step-2",
            completed_at=wrong["completed_at"],
        )
        with self.assertRaisesRegex(ContractError, "explicit distinct-evidence"):
            replay([wrong, distinct_same_attempt], "student", "negative_numbers")
        wrong_marked = dict(wrong, independent_evidence_rule="distinct_validated_steps")
        misconception_marked = dict(distinct_same_attempt,
                                    independent_evidence_rule="distinct_validated_steps")
        result = replay([make_event("SELF_REPORTED_KNOWN", "s", 0),
                         wrong_marked, misconception_marked], "student", "negative_numbers")
        self.assertEqual((result["state"]["mastery"], result["state"]["evidence_count"]),
                         ("53.00", 3))
        second_wrong = dict(wrong, event_id="second-wrong", evidence_ref="step-3")
        with self.assertRaisesRegex(ContractError, "explicit distinct-evidence"):
            replay([wrong, second_wrong], "student", "negative_numbers")
        both_wrong_marked = dict(second_wrong, independent_evidence_rule="distinct_validated_steps")
        self.assertEqual(replay([wrong_marked, both_wrong_marked],
                                "student", "negative_numbers")["state"]["evidence_count"], 2)
        second_misconception = dict(misconception_marked, event_id="second-misconception",
                                   evidence_ref="step-4")
        self.assertEqual(replay([misconception_marked, second_misconception],
                                "student", "negative_numbers")["state"]["evidence_count"], 2)


if __name__ == "__main__":
    unittest.main()
