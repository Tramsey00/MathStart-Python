from __future__ import annotations

import json
from pathlib import Path

import jsonschema


def validate_schema_file(path: Path) -> None:
    with path.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    jsonschema.Draft202012Validator.check_schema(schema)