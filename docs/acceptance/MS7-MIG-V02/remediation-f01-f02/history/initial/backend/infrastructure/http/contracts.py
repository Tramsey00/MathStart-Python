"""Validate against immutable contracts, without coercion or network resolution."""
import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]


@lru_cache(maxsize=None)
def document(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def validator(name, delivery=False):
    path = "specs/migration/r02-v1/delivery-v1.schema.json" if delivery else "specs/api/schemas/dto-v1.schema.json"
    bundle = document(path)
    return Draft202012Validator({"$defs": bundle["$defs"], "$ref": "#/$defs/" + name}, format_checker=FormatChecker())


def validate(value, name, delivery=False):
    if not validator(name, delivery).is_valid(value):
        from .transport import unavailable
        raise unavailable()
    return value
