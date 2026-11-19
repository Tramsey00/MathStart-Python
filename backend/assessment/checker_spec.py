"""Private equation checker metadata shared by the bank and Assessment."""

from collections.abc import Mapping, Sequence
from enum import StrEnum

from backend.math_validation.model import ParseInput
from backend.math_validation.parser import parse_batch
from backend.math_validation.profiles import MAX_CHARS, MAX_STEPS
from backend.math_validation.validators import Check, Form, compare, comparison_value, equation_transformed

from .templates import Template


EQUATION_CHECKERS = frozenset({"equation_state", "equation_transitions"})


class EquationAnswerMode(StrEnum):
    """Server-owned answer semantics for equation checker version 2."""

    SOLUTION = "SOLUTION"
    EQUATION_STATE = "EQUATION_STATE"
    TRANSFORMED_EQUATION = "TRANSFORMED_EQUATION"


class CheckerSpecError(ValueError):
    """Fixed messages suitable for operator output without private values."""


def template_validation_spec(template: Template) -> dict[str, object]:
    return {"required_fields": [name for name, _ in template.fields], "step_type": template.step_type}


def split_equation_spec(template: Template, stored: Mapping[str, object]) -> tuple[dict[str, object], str | None]:
    """Validate stored v2 metadata and separate the authored anchor for N011."""
    if template.checker not in EQUATION_CHECKERS or not isinstance(stored, Mapping):
        raise CheckerSpecError("Equation checker v2 requires a supported equation template")
    mode = stored.get("equation_answer_mode")
    if mode not in (EquationAnswerMode.SOLUTION, EquationAnswerMode.TRANSFORMED_EQUATION):
        raise CheckerSpecError("Unknown bank equation answer mode")

    runtime_spec = {**template_validation_spec(template), "equation_answer_mode": mode}
    if set(stored) - {"initial_state"} != runtime_spec.keys() or any(
        stored[key] != value for key, value in runtime_spec.items()
    ):
        raise CheckerSpecError("Invalid stored equation checker shape")
    if "initial_state" not in stored:
        if template.step_type is not None or mode == EquationAnswerMode.TRANSFORMED_EQUATION:
            raise CheckerSpecError("Equation checker requires an authored initial state")
        return runtime_spec, None

    initial = stored["initial_state"]
    if (not isinstance(initial, Mapping)
            or initial.keys() != {"schema_version", "kind", "parser_profile", "text"}
            or type(initial["schema_version"]) is not int or initial["schema_version"] != 1
            or initial["kind"] != "EQUATION" or initial["parser_profile"] != template.parser):
        raise CheckerSpecError("Invalid initial state metadata")
    text = initial["text"]
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_CHARS or "\0" in text:
        raise CheckerSpecError("Invalid initial state expression")
    return runtime_spec, text


def validate_equation_references(
    template: Template, stored: Mapping[str, object], answer_key: str, variants: Sequence[str],
) -> None:
    runtime_spec, initial = split_equation_spec(template, stored)
    if len(variants) >= MAX_STEPS:
        raise CheckerSpecError("Equation checker exceeds the answer variant limit")
    references = (answer_key, *variants)
    texts = (*references, initial) if initial is not None else references
    unique = tuple(dict.fromkeys(texts))
    batch = parse_batch(tuple(ParseInput(text, template.parser) for text in unique))
    if batch.rejection is not None:
        raise CheckerSpecError("Equation checker exceeds the reference parse budget")
    parsed = dict(zip(unique, batch.results, strict=True))
    start = parsed[initial] if initial is not None else None
    transformed = runtime_spec["equation_answer_mode"] == EquationAnswerMode.TRANSFORMED_EQUATION
    answer_form = Form.EQUATION_STATE if transformed else Form.SOLUTION
    equivalence_form = Form.EQUATION if transformed else Form.EQUATION_OR_SOLUTION
    if start is not None and comparison_value(start, Form.EQUATION_STATE)[0] != Check.VALID:
        raise CheckerSpecError("Initial state must be a supported equation")
    for text in references:
        result = parsed[text]
        if comparison_value(result, answer_form)[0] != Check.VALID:
            raise CheckerSpecError("Equation checker reference does not match the answer mode")
        if not transformed and compare(result, parsed[answer_key], Form.SOLUTION) != Check.VALID:
            raise CheckerSpecError("Solution variant conflicts with the answer key")
        if start is not None and (compare(result, start, equivalence_form) != Check.VALID
                                  or (transformed and not equation_transformed(start, result))):
            raise CheckerSpecError("Equation checker reference conflicts with the initial state")
