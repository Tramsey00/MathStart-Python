"""Validate against immutable contracts, without coercion or network resolution."""
import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError, validators

ROOT = Path(__file__).resolve().parents[3]
DELIVERY_SCHEMA = "specs/migration/r02-v1/delivery-v1.schema.json"


@lru_cache(maxsize=1)
def lesson_node_discriminator():
    definitions = document(DELIVERY_SCHEMA)["$defs"]
    branches = definitions["LessonNode"]["oneOf"]
    by_kind = {}
    for index, branch in enumerate(branches):
        definition = definitions[branch["$ref"].removeprefix("#/$defs/")]
        kind = definition["properties"]["kind"]
        for label in kind.get("enum", [kind.get("const")]):
            if "kind" not in definition["required"] or not isinstance(label, str) or label in by_kind:
                return branches, None
            by_kind[label] = index
    return branches, by_kind


def one_of_for_delivery(validator, branches, instance, schema):
    """Check exclusive membership without expanding every rejected subtree."""
    lesson_branches, by_kind = lesson_node_discriminator()
    if branches is lesson_branches and by_kind is not None and isinstance(instance, dict):
        kind = instance.get("kind")
        index = by_kind.get(kind) if isinstance(kind, str) else None
        if index is None:
            yield ValidationError("Unknown lesson node kind")
        else:
            yield from validator.descend(instance, branches[index], schema_path=index)
        return
    matches = 0
    for branch in branches:
        if next(validator.descend(instance, branch), None) is None:
            matches += 1
            if matches > 1:
                break
    if matches != 1:
        yield ValidationError("Exactly one delivery schema branch must match")


DeliveryValidator = validators.extend(Draft202012Validator, {"oneOf": one_of_for_delivery})


@lru_cache(maxsize=None)
def document(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def validator(name, delivery=False):
    path = DELIVERY_SCHEMA if delivery else "specs/api/schemas/dto-v1.schema.json"
    bundle = document(path)
    schema_validator = DeliveryValidator if delivery else Draft202012Validator
    return schema_validator({"$defs": bundle["$defs"], "$ref": "#/$defs/" + name}, format_checker=FormatChecker())


def validate(value, name, delivery=False):
    if not validator(name, delivery).is_valid(value):
        from .transport import unavailable
        raise unavailable()
    return value
