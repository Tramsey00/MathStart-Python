"""Offline fixture-only UI contract. No models, assessment or student evidence."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "specs" / "ui"
DTO_URI = "urn:mathstart:api:dto:v1"
SLOTS = {
    "SELF_CHECK": "self-check",
    "FINAL_ANSWER": "final-answer",
    "STEP_BY_STEP": "ordered-steps",
    "STRUCTURED_SOLUTION": "structured-solution",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validators():
    wire = read_json(ROOT / "specs/api/schemas/dto-v1.schema.json")
    registry = Registry().with_resource(DTO_URI, Resource.from_contents(wire))
    fixture = Draft202012Validator(
        read_json(UI / "ui-state-fixtures-v1.schema.json"),
        registry=registry, format_checker=FormatChecker(),
    )
    exercise = Draft202012Validator(
        {"$defs": wire["$defs"], "$ref": "#/$defs/PublicExerciseDTO"},
        format_checker=FormatChecker(),
    )
    return fixture, exercise


def validate_exercise(exercise, validator=None):
    """Wire shape and immutable identity checks, never mathematical validation."""
    if validator is None:
        validator = validators()[1]
    validator.validate(exercise)
    identity = exercise["exercise_version"]
    if not (exercise["version"] == exercise["contract_version"]
            == identity["version"] == identity["contract_version"]
            and exercise["id"] == identity["exercise_id"]):
        raise ValidationError("Inconsistent public exercise identity/version aliases")
    band = {1: "easy", 2: "easy", 3: "medium", 4: "hard"}[exercise["difficulty_level"]]
    if exercise["difficulty"] != band:
        raise ValidationError("Inconsistent public difficulty band/level")


def dispatch_exercise(exercise):
    try:
        validate_exercise(exercise)
    except (ValidationError, TypeError, KeyError):
        return "unsupported"
    return SLOTS[exercise["interaction_mode"]]


def validate_fixture_pack(pack):
    fixture_validator, exercise_validator = validators()
    fixture_validator.validate(pack)
    if {item["state"] for item in pack["states"]} != {"ordinary", "loading", "error", "empty"}:
        raise ValidationError("Fixture pack must cover the four foundation states")
    if len({item["state"] for item in pack["states"]}) != len(pack["states"]):
        raise ValidationError("Duplicate state fixture")
    if {item["interaction_mode"] for item in pack["exercises"]} != set(SLOTS):
        raise ValidationError("Fixture pack must cover the four accepted modes")
    if len({item["id"] for item in pack["exercises"]}) != len(pack["exercises"]):
        raise ValidationError("Duplicate exercise fixture")
    for exercise in pack["exercises"]:
        validate_exercise(exercise, exercise_validator)
    return pack


def load_fixture_pack():
    # Fixed allowlist of one reviewed repository file. No request path or DB input.
    return validate_fixture_pack(read_json(UI / "fixtures/ui-states-v1.json"))
