"""Independent R03A contract assertions; synthetic records, no product runtime."""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from scripts import r03_contract_reference as frozen
from scripts.r02a_contract_reference import ContractOracle
from scripts.r03a_contract_reference import (
    ContractError, IdentityConflict, NumericalReplay, completion_identity,
    completion_source_identity, import_progress_v1_completions,
    ingest_completion_fact, replay_completion_facts, replay_v1_1,
    validate_completion_fact,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "specs/progress/fixtures"
NUMERIC = ("mastery", "confidence", "evidence_count", "last_updated")
DIAGNOSTICS = ("ordered_event_ids", "applied_event_ids", "nonprojecting_event_ids")
EXPECTED_CASES = (
    "neutral-completed", "neutral-only", "equal-time-tiebreak", "late-neutral",
    "fact-before-event", "fact-after-event", "exact-duplicate", "conflicting-duplicate",
    "retry-no-second-entry", "event-and-fact", "conflicting-time", "neutral-eviction",
    "count-three-to-two", "mastered-to-learning", "numerical-neutrality", "late-independent",
    "malformed-no-wrong", "client-flag-rejected", "progress-v1-parity", "delivery-permutations",
    "timezone-duplicate", "owner-skill-binding", "lifecycle-boundary", "help-and-credit",
    "repeat-isolation", "event-reset-with-late-fact", "outside-window", "legacy-reveal-import",
    "final-result-conflict", "late-event-is-event", "scope-and-not-started", "immutable-conflict-order",
)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def authority_for(facts):
    """Explicit synthetic finalized source records, separate from incoming DTOs."""
    return {"context_version": "assessment-completion-v1", "records": [
        {"fact": copy.deepcopy(f), "attempt_state": "COMPLETED",
         "mapped_skill_ids": [f["skill_id"]]} for f in facts
    ]}


FORMATS = FormatChecker()


@FORMATS.checks("date-time", raises=(ValueError, TypeError))
def calendar_timestamp(value):
    if not isinstance(value, str):
        return True  # schema type check rejects nonstrings
    return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None


class CompletionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = load(FIXTURES / "completion-v1-cases.json")
        cls.cases = {c["id"]: c for c in cls.fixture["cases"]}
        cls.invalid = load(FIXTURES / "completion-v1-invalid.json")["cases"]
        cls.parity = load(FIXTURES / "progress-v1.1-parity.json")
        cls.schema = load(ROOT / "specs/progress/schemas/completion-fact-v1.schema.json")
        cls.validator = Draft202012Validator(cls.schema, format_checker=FORMATS)

    def case(self, name):
        case = copy.deepcopy(self.cases[name])
        data = copy.deepcopy(self.fixture["datasets"][case.pop("dataset")])
        data.update(case)
        return data

    def cache(self, data):
        return NumericalReplay(data["events"], "synthetic-student", "negative_numbers")

    def run_facts(self, data, facts=None, authority=None, cache=None):
        return replay_completion_facts(cache or self.cache(data),
                                       data["facts"] if facts is None else facts,
                                       authority=data["authority"] if authority is None else authority)

    def assert_neutral(self, before, after):
        for field in NUMERIC:
            self.assertEqual(before["state"][field], after["state"][field], field)
        for field in DIAGNOSTICS + ("legacy_snapshots",):
            self.assertEqual(before[field], after[field], field)

    def critical_transition(self, name):
        data = self.case(name)
        cache = self.cache(data)
        before = self.run_facts(data, cache=cache)
        mirror, after, duplicate = ingest_completion_fact(data["facts"], data["incoming"], cache,
                                                         authority=data["authority"])
        self.assertFalse(duplicate)
        self.assertEqual(len(mirror), 11)
        self.assert_neutral(before, after)
        return data, before, after

    def test_schema_and_literal_case_inventory(self):
        Draft202012Validator.check_schema(self.schema)
        expected_fields = {"completion_id", "user_id", "skill_id", "attempt_id", "outcome",
                           "independent_correct", "completed_at", "policy_version"}
        self.assertEqual(set(self.schema["required"]), expected_fields)
        self.assertEqual(set(self.schema["properties"]), expected_fields)
        self.assertFalse(self.schema["additionalProperties"])
        self.assertEqual(self.schema["properties"]["outcome"]["enum"],
                         ["CORRECT", "WRONG", "UNSUPPORTED", "INDETERMINATE"])
        self.assertEqual(self.schema["properties"]["policy_version"]["const"], "progress-v1.1")
        self.assertEqual(tuple(c["id"] for c in self.fixture["cases"]), EXPECTED_CASES)
        self.assertEqual([c["number"] for c in self.fixture["cases"]], list(range(1, 33)))
        methods = dir(type(self))
        for i, name in enumerate(EXPECTED_CASES, 1):
            self.assertIn(f"test_{i:02d}_" + name.replace("-", "_"), methods)
        for data in self.fixture["datasets"].values():
            for fact in data["facts"]:
                self.validator.validate(fact)
        self.assertEqual(len(self.invalid), 33)

    def test_01_neutral_completed(self):
        data = self.case("neutral-completed")
        self.assertEqual(data["reason"], "ALREADY_CREDITED")
        self.assertFalse(data["positive_credit_awarded"])
        self.assertEqual(data["facts"][0]["outcome"], "CORRECT")
        result = self.run_facts(data)
        self.assertEqual(result["recent_window"], {"attempt_ids": ["attempt-01"], "independent_correct_count": 0})
        self.assertEqual(result["applied_event_ids"], [])

    def test_02_neutral_only(self):
        result = self.run_facts(self.case("neutral-only"))
        self.assertEqual(result["state"], {"mastery": "0.00", "confidence": "0.00",
                         "evidence_count": 0, "status": "NOT_STARTED", "last_updated": None,
                         "reducer_version": "progress-v1.1"})
        self.assertEqual(result["recent_window"]["attempt_ids"], ["attempt-01"])

    def test_03_equal_time_tiebreak(self):
        data = self.case("equal-time-tiebreak")
        for facts in itertools.permutations(data["facts"]):
            self.assertEqual(self.run_facts(data, facts)["recent_window"]["attempt_ids"],
                             ["attempt-c", "attempt-a", "attempt-b"])

    def test_04_late_neutral(self):
        data = self.case("late-neutral")
        cache = self.cache(data)
        mirror, before, _ = ingest_completion_fact([], data["facts"][0], cache, authority=data["authority"])
        mirror, after, _ = ingest_completion_fact(mirror, data["facts"][2], cache, authority=data["authority"])
        self.assertEqual(after["recent_window"]["attempt_ids"], ["attempt-c", "attempt-b"])
        self.assert_neutral(before, after)

    def test_05_fact_before_event(self):
        data = self.case("fact-before-event")
        empty = NumericalReplay([], "synthetic-student", "negative_numbers")
        mirror, before, _ = ingest_completion_fact([], data["facts"][0], empty, authority=data["authority"])
        self.assertEqual(before["state"]["evidence_count"], 0)
        after = self.run_facts(data, mirror)
        self.assertEqual(after["state"]["mastery"], "6.00")
        self.assertEqual(after["state"]["evidence_count"], 1)
        self.assertEqual(after["recent_window"]["attempt_ids"], ["attempt-01"])

    def test_06_fact_after_event(self):
        data = self.case("fact-after-event")
        cache = self.cache(data)
        before = self.run_facts(data, [], cache=cache)
        self.assertEqual(before["completion_gaps"], ["attempt-01"])
        self.assertEqual(before["recent_window"]["attempt_ids"], [])
        _, after, _ = ingest_completion_fact([], data["facts"][0], cache, authority=data["authority"])
        self.assertEqual(after["completion_gaps"], [])
        self.assert_neutral(before, after)

    def test_07_exact_duplicate(self):
        data = self.case("exact-duplicate")
        cache = self.cache(data)
        fact = data["facts"][0]
        self.assertEqual(completion_identity(fact), "00000000-0000-0000-0000-000000000001")
        self.assertEqual(completion_source_identity(fact), ("attempt-01", "negative_numbers"))
        mirror, expected, duplicate = ingest_completion_fact([], fact, cache, authority=data["authority"])
        self.assertFalse(duplicate)
        for retry in data["retries"]:
            self.assertEqual(completion_identity(retry), completion_identity(fact))
            self.assertEqual(completion_source_identity(retry), completion_source_identity(fact))
            mirror, result, duplicate = ingest_completion_fact(mirror, retry, cache, authority=data["authority"])
            self.assertTrue(duplicate)  # exact retries satisfy both constraints
            self.assertEqual(result, expected)
            self.assertEqual(len(mirror), 1)

    def test_08_conflicting_duplicate(self):
        data = self.case("conflicting-duplicate")
        original = copy.deepcopy(data)
        for candidate in data["candidates"]:
            with self.subTest(candidate=candidate), self.assertRaises(IdentityConflict):
                ingest_completion_fact(data["facts"], candidate, self.cache(data), authority=data["authority"])
        self.assertEqual(data, original)

    def test_09_retry_no_second_entry(self):
        data = self.case("retry-no-second-entry")
        facts = data["facts"] + data["retries"]
        result = self.run_facts(data, facts)
        self.assertEqual(result["recent_window"]["attempt_ids"], ["attempt-01"])
        mirror, _, duplicate = ingest_completion_fact(facts, data["facts"][0], self.cache(data), authority=data["authority"])
        self.assertTrue(duplicate)
        self.assertEqual(len(mirror), 1)

    def test_10_event_and_fact(self):
        data = self.case("event-and-fact")
        data["events"].append(data["extra_event"])
        result = self.run_facts(data)
        self.assertEqual(result["recent_window"]["attempt_ids"], ["attempt-01"])
        self.assertEqual(result["state"]["evidence_count"], 2)
        self.assertEqual(result["state"]["confidence"], "8.00")

    def test_11_conflicting_time(self):
        data = self.case("conflicting-time")
        events_first = self.cache(data)
        existing = []
        with self.assertRaisesRegex(ContractError, "completion time"):
            ingest_completion_fact(existing, data["candidate"], events_first, authority=data["authority"])
        self.assertEqual(existing, [])
        facts_first, _, _ = ingest_completion_fact([], data["candidate"],
            NumericalReplay([], "synthetic-student", "negative_numbers"), authority=data["authority"])
        with self.assertRaisesRegex(ContractError, "completion time"):
            self.run_facts(data, facts_first)
        self.assertEqual(facts_first[0]["completed_at"], "2026-09-24T12:02:00.000000Z")

    def test_12_neutral_eviction(self):
        _, before, after = self.critical_transition("neutral-eviction")
        self.assertIn("attempt-01", before["recent_window"]["attempt_ids"])
        self.assertNotIn("attempt-01", after["recent_window"]["attempt_ids"])
        self.assertEqual(after["recent_window"]["attempt_ids"], [f"attempt-{i:02d}" for i in range(2, 12)])
        self.assertEqual(len(after["recent_window"]["attempt_ids"]), 10)

    def test_13_count_three_to_two(self):
        _, before, after = self.critical_transition("count-three-to-two")
        self.assertEqual(before["recent_window"]["independent_correct_count"], 3)
        self.assertEqual(after["recent_window"]["independent_correct_count"], 2)

    def test_14_mastered_to_learning(self):
        """Neutral #11 evicts oldest independent; 100.00/67.00/11/time unchanged."""
        _, before, after = self.critical_transition("mastered-to-learning")
        self.assertEqual(before["state"], {
            "mastery": "100.00", "confidence": "67.00", "evidence_count": 11,
            "status": "MASTERED", "last_updated": "2026-09-24T12:10:00.000000Z",
            "reducer_version": "progress-v1.1",
        })
        self.assertEqual(after["state"], dict(before["state"], status="LEARNING"))
        self.assertEqual(after["recent_window"]["independent_correct_count"], 2)

    def test_15_numerical_neutrality(self):
        data = self.case("numerical-neutrality")
        original = copy.deepcopy(data)
        with patch.object(frozen, "replay", wraps=frozen.replay) as reducer:
            cache = self.cache(data)
            self.assertEqual(reducer.call_count, 1)
            before = self.run_facts(data, cache=cache)
            _, after, _ = ingest_completion_fact(data["facts"], data["incoming"], cache,
                                                authority=data["authority"])
            self.assertEqual(reducer.call_count, 1)  # no numerical reapplication on fact delivery
        self.assert_neutral(before, after)
        self.assertEqual(data, original)  # no fake/changed event or DTO
        self.assertEqual(len(after["applied_event_ids"]), 11)

    def test_16_late_independent(self):
        data = self.case("late-independent")
        cache = self.cache(data)
        before = self.run_facts(data, data["facts_before"], cache=cache)
        _, after, _ = ingest_completion_fact(data["facts_before"], data["incoming"], cache, authority=data["authority"])
        self.assertEqual(before["recent_window"]["independent_correct_count"], 0)
        self.assertEqual(after["recent_window"]["independent_correct_count"], 1)
        self.assert_neutral(before, after)

    def test_17_malformed_no_wrong(self):
        data = self.case("malformed-no-wrong")
        cache = self.cache(data)
        original = cache.events
        for row in self.invalid:
            with self.subTest(case=row["id"]):
                if row["schema_invalid"]:
                    with self.assertRaises(ValidationError):
                        self.validator.validate(row["value"])
                else:
                    self.validator.validate(row["value"])
                with self.assertRaises(ContractError):
                    validate_completion_fact(row["value"])
                with self.assertRaises(ContractError):
                    ingest_completion_fact([], row["value"], cache, authority=data["authority"])
                self.assertEqual(cache.events, original)

    def test_18_client_flag_rejected(self):
        data = self.case("client-flag-rejected")
        self.validator.validate(data["candidate"])
        with self.assertRaisesRegex(ContractError, "authority"):
            self.run_facts(data, [data["candidate"]], authority={})
        with self.assertRaisesRegex(ContractError, "authority"):
            replay_v1_1([], [data["candidate"]], "synthetic-student", "negative_numbers")
        with self.assertRaisesRegex(ContractError, "authority"):
            self.run_facts(data, [data["candidate"]], authority=data["mismatch_authority"])

    def test_19_progress_v1_parity(self):
        source_path = FIXTURES / self.parity["source_fixture"]
        self.assertEqual(hashlib.sha256(source_path.read_bytes()).hexdigest(), self.parity["source_sha256"])
        source = load(source_path)
        self.assertEqual(self.parity["fixture_version"], "progress-v1.1-parity-v1")
        self.assertEqual({c["legacy_case_id"] for c in self.parity["cases"]}, {c["id"] for c in source["cases"]})
        for row in self.parity["cases"]:
            old = next(c for c in source["cases"] if c["id"] == row["legacy_case_id"])
            with self.subTest(case=old["id"]):
                events = copy.deepcopy(old["events"])
                legacy = frozen.replay(events, old["user_id"], old["skill_id"])
                facts, result = import_progress_v1_completions(events, old["user_id"], old["skill_id"], authority=row["authority"])
                self.assertEqual(legacy["state"], old["expected"])
                self.assertEqual(result["state"], dict(legacy["state"], reducer_version="progress-v1.1"))
                self.assertEqual(result["recent_window"], legacy["recent_window"])
                self.assertEqual(result["recent_window"]["attempt_ids"], row["expected_recent_ids"])
                self.assertEqual(result["recent_window"]["independent_correct_count"], row["expected_independent_count"])
                for field in DIAGNOSTICS:
                    self.assertEqual(result[field], legacy[field])
                self.assertEqual(result["legacy_snapshots"], legacy["snapshots"])
                self.assertEqual(result["completion_gaps"], [])
                self.assertEqual(events, old["events"])
                self.assertTrue(all(e["policy_version"] == "progress-v1" for e in events))
                self.assertEqual(replay_v1_1(events, facts, old["user_id"], old["skill_id"], authority=row["authority"]), result)
        self.assertEqual(self.parity["arithmetic_case_indices"], [0, 1, 2])
        for i in self.parity["arithmetic_case_indices"]:
            case = source["arithmetic_cases"][i]
            self.assertEqual(format(frozen.clamp_round(case["input"]), ".2f"), case["expected"])

    def test_20_delivery_permutations(self):
        data = self.case("delivery-permutations")
        expected = self.run_facts(data)
        for order in data["delivery_orders"]:
            events, facts = [], []
            for delivery in order:
                cache = NumericalReplay(events, "synthetic-student", "negative_numbers")
                if delivery == "event":
                    events = copy.deepcopy(data["events"])
                    result = replay_v1_1(events, facts, "synthetic-student", "negative_numbers", authority=data["authority"])
                else:
                    facts, result, _ = ingest_completion_fact(facts, data["facts"][0], cache, authority=data["authority"])
            self.assertEqual(result, expected)

    def test_21_timezone_duplicate(self):
        data = self.case("timezone-duplicate")
        facts, result, duplicate = ingest_completion_fact(data["facts"], data["candidate"], self.cache(data), authority=data["authority"])
        self.assertTrue(duplicate)
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0]["completed_at"], "2026-09-24T12:01:00.000000Z")
        self.assertEqual(result, self.run_facts(data))

    def test_22_owner_skill_binding(self):
        data = self.case("owner-skill-binding")
        for candidate in (data["foreign"], data["other_skill"]):
            with self.assertRaisesRegex(ContractError, "target user/skill"):
                ingest_completion_fact([], candidate, self.cache(data), authority=authority_for([candidate]))
        bad_mapping = copy.deepcopy(data["authority"])
        bad_mapping["records"][0]["mapped_skill_ids"] = ["equation_balance"]
        with self.assertRaisesRegex(ContractError, "mapping"):
            self.run_facts(data, authority=bad_mapping)
        with self.assertRaisesRegex(ContractError, "cross-skill"):
            self.run_facts(data, data["facts"] + [data["cross_skill"]], authority=authority_for(data["facts"]))

    def test_23_lifecycle_boundary(self):
        data = self.case("lifecycle-boundary")
        for state in data["states"]:
            bad = copy.deepcopy(data["authority"])
            bad["records"][0]["attempt_state"] = state
            with self.subTest(state=state), self.assertRaisesRegex(ContractError, "finalized"):
                self.run_facts(data, authority=bad)
        result = self.run_facts(data, data["neutral_facts"], authority=authority_for(data["neutral_facts"]))
        self.assertEqual(result["recent_window"]["independent_correct_count"], 0)
        self.assertEqual(result["recent_window"]["attempt_ids"], ["attempt-30", "attempt-31"])
        self.assertEqual(result["state"]["evidence_count"], 0)
        self.assertEqual(result["ordered_event_ids"], [])

    def test_24_help_and_credit(self):
        data = self.case("help-and-credit")
        integration = load(ROOT / "specs/api/fixtures/concurrency-v1.json")["cases"]
        for name in data["integration_cases"]:
            case = next(c for c in integration if c["case_id"] == name)
            oracle = ContractOracle(case["initial"])
            for action in case["actions"]:
                oracle.apply(action)
            facts = []
            for i, (attempt_id, attempt) in enumerate(oracle.attempts.items(), 100):
                if attempt["state"] != "COMPLETED":
                    continue
                facts.append(dict(data["facts"][0], completion_id=str(UUID(int=i)),
                                  attempt_id=attempt_id, user_id=oracle.owner,
                                  outcome=attempt["outcome"], independent_correct=attempt["independent"]))
            self.assertEqual(len(facts), oracle.completions)
            self.assertLessEqual(oracle.positive, 1)
            if "completed-before" in name:
                self.assertTrue(facts[0]["independent_correct"])
            elif "before-help" in name or "help-wins" in name or "before-reveal" in name or "reveal-wins" in name:
                self.assertFalse(facts[0]["independent_correct"])
            if "permanent-credit" in name or name == "second-positive-eligibility":
                self.assertEqual([f["outcome"] for f in facts], ["CORRECT", "CORRECT"])
                self.assertEqual([f["independent_correct"] for f in facts], [True, False])
            result = replay_v1_1([], facts, oracle.owner, "negative_numbers", authority=authority_for(facts))
            self.assertEqual(result["state"]["evidence_count"], 0)
            self.assertEqual(len(result["recent_window"]["attempt_ids"]), len(facts))

    def test_25_repeat_isolation(self):
        data = self.case("repeat-isolation")
        cache = self.cache(data)
        without = self.run_facts(data, [], cache=cache)
        with_fact = self.run_facts(data, cache=cache)
        self.assert_neutral(without, with_fact)
        self.assertEqual([s["state"]["mastery"] for s in with_fact["legacy_snapshots"]],
                         ["60.00", "55.00", "48.75", "41.25"])
        # Third misconception still uses -5*1.5 despite the earlier true fact.
        self.assertEqual(with_fact["state"]["mastery"], "41.25")

    def test_26_event_reset_with_late_fact(self):
        data = self.case("event-reset-with-late-fact")
        cache = self.cache(data)
        before = self.run_facts(data, [], cache=cache)
        after = self.run_facts(data, cache=cache)
        self.assert_neutral(before, after)
        self.assertEqual([s["state"]["mastery"] for s in before["legacy_snapshots"]],
                         ["60.00", "55.00", "48.75", "56.75", "51.75"])
        self.assertEqual(before["state"]["mastery"], "51.75")  # qualifying event resets to -5

    def test_27_outside_window(self):
        data = self.case("outside-window")
        before = self.run_facts(data)
        facts, after, _ = ingest_completion_fact(data["facts"], data["incoming"], self.cache(data), authority=data["authority"])
        self.assertEqual(len(facts), 11)
        self.assertEqual(after, before)

    def test_28_legacy_reveal_import(self):
        data = self.case("legacy-reveal-import")
        row = next(c for c in self.parity["cases"] if c["legacy_case_id"] == data["parity_case"])
        old = next(c for c in load(FIXTURES / "progress-v1-cases.json")["cases"] if c["id"] == data["parity_case"])
        facts, result = import_progress_v1_completions(old["events"], old["user_id"], old["skill_id"], authority=row["authority"])
        reveal = next(f for f in facts if f["attempt_id"] == data["reveal_attempt"])
        self.assertEqual(reveal["outcome"], "INDETERMINATE")  # explicit metadata, never inferred
        self.assertIn(data["reveal_attempt"], result["recent_window"]["attempt_ids"])
        with self.assertRaises(ContractError):
            import_progress_v1_completions(old["events"], old["user_id"], old["skill_id"],
                                          authority={"context_version": "legacy-completion-v1", "records": []})
        no_facts = replay_v1_1(old["events"], [], old["user_id"], old["skill_id"])
        self.assertEqual(no_facts["recent_window"]["attempt_ids"], [])
        self.assertEqual(len(no_facts["completion_gaps"]), 4)

    def test_29_final_result_conflict(self):
        data = self.case("final-result-conflict")
        with self.assertRaisesRegex(ContractError, "final-result"):
            self.run_facts(data, [data["candidate"]])
        true_fact = dict(data["candidate"], independent_correct=True)
        for event in (data["helped_event"], data["wrong_event"]):
            with self.assertRaisesRegex(ContractError, "final-result"):
                replay_v1_1([event], [true_fact], "synthetic-student", "negative_numbers", authority=authority_for([true_fact]))

    def test_30_late_event_is_event(self):
        data = self.case("late-event-is-event")
        before = self.run_facts(data)
        data["events"].append(data["incoming_event"])
        after = self.run_facts(data)
        self.assertEqual(after["state"]["evidence_count"], before["state"]["evidence_count"] + 1)
        self.assertEqual(after["state"]["confidence"], "8.00")
        self.assertEqual(after["state"]["last_updated"], before["state"]["last_updated"])
        self.assertNotEqual(after["ordered_event_ids"], before["ordered_event_ids"])

    def test_31_scope_and_not_started(self):
        data = self.case("scope-and-not-started")
        facts = data["facts"] + data["other_facts"]
        result = self.run_facts(data, facts, authority=authority_for(facts))
        self.assertEqual(result["recent_window"]["attempt_ids"], ["attempt-01"])
        independent = self.run_facts(data, [data["independent_only"]], authority=authority_for([data["independent_only"]]))
        self.assertEqual(independent["recent_window"]["independent_correct_count"], 1)
        self.assertEqual(independent["state"]["status"], "NOT_STARTED")
        self.assertEqual(independent["state"]["mastery"], "0.00")

    def test_32_immutable_conflict_order(self):
        data = self.case("immutable-conflict-order")
        fact = data["facts"][0]
        for candidate in data["candidates"]:
            for order in ([fact, candidate], [candidate, fact]):
                with self.assertRaises(IdentityConflict):
                    self.run_facts(data, order)

    def test_all_outcomes_are_history_without_automatic_numeric_effects(self):
        data = self.case("neutral-only")
        for outcome in ["CORRECT", "WRONG", "UNSUPPORTED", "INDETERMINATE"]:
            fact = dict(data["facts"][0], outcome=outcome)
            self.validator.validate(fact)
            result = self.run_facts(data, [fact], authority=authority_for([fact]))
            self.assertEqual(result["state"]["evidence_count"], 0)
            self.assertEqual(result["state"]["mastery"], "0.00")
            self.assertEqual(result["ordered_event_ids"], [])

    def test_full_window_fact_and_event_permutation_keeps_all_numerical_outputs(self):
        data = self.case("numerical-neutrality")
        facts = data["facts"] + [data["incoming"]]
        expected = self.run_facts(data, facts)
        for ordered_facts in (facts, facts[::-1], facts[4:] + facts[:4]):
            for events in (data["events"], data["events"][::-1]):
                result = replay_v1_1(events, ordered_facts, "synthetic-student", "negative_numbers", authority=data["authority"])
                self.assertEqual(result, expected)
        # >10 identical timestamps still use lexical attempt ID, not fact ID/order.
        tied = [dict(f, completed_at="2026-09-24T12:00:00Z") for f in facts]
        result = replay_v1_1([], tied[::-1], "synthetic-student", "negative_numbers", authority=authority_for(tied))
        self.assertEqual(result["recent_window"]["attempt_ids"], [f"attempt-{i:02d}" for i in range(2, 12)])

    def test_global_keys_cannot_hide_in_other_owner_or_skill_partition(self):
        data = self.case("neutral-only")
        fact = data["facts"][0]
        for candidate in (dict(fact, user_id="foreign"), dict(fact, skill_id="equation_balance"),
                          dict(fact, completion_id=str(UUID(int=99)), user_id="foreign")):
            with self.assertRaises(IdentityConflict):
                self.run_facts(data, [fact, candidate])

    def test_cross_skill_agreement_and_foreign_event_owner(self):
        data = self.case("event-and-fact")
        fact = data["facts"][0]
        second = dict(fact, completion_id=str(UUID(int=90)), skill_id="equation_balance")
        result = self.run_facts(data, [fact, second], authority=authority_for([fact, second]))
        self.assertEqual(result["recent_window"]["attempt_ids"], ["attempt-01"])
        data["events"][0]["user_id"] = "foreign"
        with self.assertRaisesRegex(ContractError, "owner"):
            self.run_facts(data, [fact], authority=authority_for([fact]))

    def test_cached_evidence_and_returned_results_are_detached(self):
        data = self.case("fact-after-event")
        cache = self.cache(data)
        result = self.run_facts(data, cache=cache)
        result["state"]["mastery"] = "99.00"
        result["legacy_snapshots"].clear()
        data["events"].clear()
        self.assertEqual(cache.result["state"]["mastery"], "6.00")
        self.assertEqual(len(cache.result["snapshots"]), 1)
        returned = cache.events
        returned[0]["event_kind"] = "WRONG_ATTEMPT"
        self.assertEqual(cache.events[0]["event_kind"], "CORRECT_FIRST_TRY")
        with self.assertRaises(FrozenInstanceError):
            cache.user_id = "foreign"

    def test_later_reveal_does_not_revoke_finalized_independence(self):
        data = self.case("fact-after-event")
        reveal = dict(data["events"][0], event_id="later-reveal", event_kind="ANSWER_REVEALED",
                      occurred_at="2026-09-24T12:02:00Z", reveal_used=True)
        reveal.pop("difficulty")
        data["events"].append(reveal)
        result = self.run_facts(data)
        self.assertEqual(result["recent_window"]["independent_correct_count"], 1)
        self.assertEqual(result["state"]["evidence_count"], 1)
        self.assertEqual(result["state"]["last_updated"], "2026-09-24T12:01:00.000000Z")

    def test_temporal_relationships_and_max_precision(self):
        data = self.case("fact-after-event")
        for stamp in ("2026-09-24T11:59:00.123456Z", "2026-09-24T12:05:00.123456Z"):
            fact = dict(data["facts"][0], completed_at=stamp)
            self.validator.validate(fact)
            events = [dict(data["events"][0], completed_at=stamp)]
            result = replay_v1_1(events, [fact], "synthetic-student", "negative_numbers", authority=authority_for([fact]))
            self.assertEqual(result["state"]["last_updated"], "2026-09-24T12:01:00.000000Z")
            self.assertEqual(validate_completion_fact(fact)["completed_at"], stamp)

    def test_bad_contexts_and_missing_legacy_outcome_fail_closed(self):
        data = self.case("neutral-only")
        for bad in ({}, {"context_version": [], "records": []},
                    dict(data["authority"], client_authority=True)):
            with self.assertRaises(ContractError):
                self.run_facts(data, authority=bad)
        row = copy.deepcopy(self.parity["cases"][0])
        del row["authority"]["records"][-1]["fact"]["outcome"]
        old = load(FIXTURES / "progress-v1-cases.json")["cases"][0]
        with self.assertRaises(ContractError):
            import_progress_v1_completions(old["events"], old["user_id"], old["skill_id"], authority=row["authority"])


if __name__ == "__main__":
    unittest.main()
