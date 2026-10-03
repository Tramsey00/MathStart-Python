"""Offline UI fixture checks against the unchanged accepted R02A package."""
import copy
import hashlib
import json
import unittest

from jsonschema import ValidationError

from content.ui_foundation import ROOT, SLOTS, dispatch_exercise, load_fixture_pack, validate_fixture_pack, validators


class UIFixtureContractTests(unittest.TestCase):
    def setUp(self):
        self.pack = load_fixture_pack()

    def test_provenance_and_frozen_upstream_digests(self):
        fixture_validator, exercise_validator = validators()
        fixture_validator.check_schema(fixture_validator.schema)
        exercise_validator.check_schema(exercise_validator.schema)
        self.assertTrue(self.pack["fixture_only"])
        self.assertEqual(self.pack["fixture_version"], 1)
        self.assertEqual(self.pack["provenance"]["openapi_sha256"], hashlib.sha256(
            (ROOT / "specs/api/openapi-v1.json").read_bytes()).hexdigest())
        manifest = json.loads((ROOT / "specs/api/candidate-manifest-v1.json").read_text())
        for path, digest in manifest["artifacts"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest, path)

    def test_four_modes_dispatch_without_forms_and_four_distinct_states(self):
        for exercise in self.pack["exercises"]:
            self.assertEqual(dispatch_exercise(exercise), SLOTS[exercise["interaction_mode"]])
            # Reviewed prose describes only synthetic modes; no actual task/solution data.
            self.assertEqual(exercise["statement"], f"Синтетическое описание режима {exercise['interaction_mode']}. Здесь нет математического задания или результата.")
            self.assertEqual(exercise["allowed_help_actions"], [])
        self.assertEqual({s["state"] for s in self.pack["states"]}, {"ordinary", "loading", "error", "empty"})

    def test_rejects_wrong_fixture_versions_missing_marks_and_duplicate_states(self):
        for mutate in [lambda p: p.update(fixture_version=2), lambda p: p.update(fixture_only=False),
                       lambda p: p["states"].__setitem__(1, copy.deepcopy(p["states"][0])),
                       lambda p: p["provenance"].update(openapi_sha256="0" * 64)]:
            bad = copy.deepcopy(self.pack)
            mutate(bad)
            with self.assertRaises(ValidationError):
                validate_fixture_pack(bad)

    def test_rejects_private_keys_in_public_data_at_multiple_depths(self):
        for key in ["answer", "answer_key", "canonical_solution", "checker", "validation_spec", "accepted_variants"]:
            for target in ["exercise", "input", "pack", "state"]:
                bad = copy.deepcopy(self.pack)
                obj = {"exercise": bad["exercises"][1], "input": bad["exercises"][1]["input_schema"],
                       "pack": bad, "state": bad["states"][0]}[target]
                obj[key] = "private sentinel"
                with self.subTest(key=key, target=target), self.assertRaises(ValidationError):
                    validate_fixture_pack(bad)

    def test_missing_unknown_and_inconsistent_descriptors_fail_safely(self):
        valid = self.pack["exercises"][1]
        bad = [None, {}, {**valid, "interaction_mode": "UNKNOWN"}, {**valid, "input_schema": None},
               {**valid, "version": 2}, {**valid, "difficulty": "hard"},
               {**valid, "exercise_version": {**valid["exercise_version"], "exercise_id": "00000000-0000-4000-8000-000000000999"}},
               {**valid, "input_schema": {"type": "array", "fields": []}}]
        for item in bad:
            self.assertEqual(dispatch_exercise(item), "unsupported")

    def test_accepted_public_exercise_shapes_dispatch_without_copying_them_to_browser(self):
        upstream = json.loads((ROOT / "specs/api/fixtures/public-exercises-v1.json").read_text())
        for exercise in upstream:
            self.assertEqual(dispatch_exercise(exercise), SLOTS[exercise["interaction_mode"]])

    def test_new_exercise_version_and_enum_object_metadata_are_slots_not_guessed_forms(self):
        item = copy.deepcopy(self.pack["exercises"][1])
        item["version"] = item["contract_version"] = 7
        item["exercise_version"]["version"] = item["exercise_version"]["contract_version"] = 7
        item["input_schema"]["fields"] = [{"name": "choice", "input_type": "enum", "required": True},
                                           {"name": "part", "input_type": "object", "required": False}]
        self.assertEqual(dispatch_exercise(item), "final-answer")


if __name__ == "__main__":
    unittest.main()
