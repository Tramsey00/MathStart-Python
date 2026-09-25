from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema


class RunResultValidationError(RuntimeError):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def _load_schema(
    repo_root: Path,
) -> dict[str, Any]:
    schema_path = (
        repo_root
        / "specs"
        / "harness"
        / "run-result-v1.schema.json"
    )

    try:
        with schema_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            schema = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise RunResultValidationError(
            [f"cannot load RunResult schema: {exc}"]
        ) from exc

    if not isinstance(schema, dict):
        raise RunResultValidationError(
            ["RunResult schema root must be an object"]
        )

    return schema


def validate_run_result(
    repo_root: Path,
    result: dict[str, Any],
) -> None:
    schema = _load_schema(repo_root)

    validator = jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )

    schema_errors = sorted(
        validator.iter_errors(result),
        key=lambda error: list(error.absolute_path),
    )

    if not schema_errors:
        return

    errors: list[str] = []

    for error in schema_errors:
        location = ".".join(
            str(part)
            for part in error.absolute_path
        )

        prefix = (
            f"{location}: "
            if location
            else ""
        )

        errors.append(
            prefix + error.message
        )

    raise RunResultValidationError(errors)


def load_and_validate_run_result(
    repo_root: Path,
    result_path: Path,
) -> dict[str, Any]:
    try:
        with result_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            result = json.load(file)
    except FileNotFoundError as exc:
        raise RunResultValidationError(
            [
                "run result does not exist: "
                f"{result_path}"
            ]
        ) from exc
    except json.JSONDecodeError as exc:
        raise RunResultValidationError(
            [
                "run result is not valid JSON: "
                f"{exc}"
            ]
        ) from exc
    except OSError as exc:
        raise RunResultValidationError(
            [
                "cannot read run result: "
                f"{exc}"
            ]
        ) from exc

    if not isinstance(result, dict):
        raise RunResultValidationError(
            ["RunResult root must be a JSON object"]
        )

    validate_run_result(
        repo_root,
        result,
    )

    return result