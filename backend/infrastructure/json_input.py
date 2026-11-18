"""Strict UTF-8 JSON decoding shared by operator packages and HTTP."""
import json


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate key")
        value[key] = item
    return value


def decode_json(raw):
    def reject_constant(_):
        raise ValueError("Nonfinite value")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=reject_constant)
