"""Server-only N008/N009 interface to deterministic analysis, outside a transaction."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from backend.knowledge.graph import PILOT_VERSION, PilotGraphRead
from backend.math_validation.profiles import MAX_STEPS
from backend.math_validation.validators import Form
from backend.solution_analyzer.deterministic import CheckPlan, analyze
from backend.solution_analyzer.model import AnalysisResult, Answer, SubmittedSolution, Verdict

from .templates import TEMPLATES


@dataclass(frozen=True, slots=True)
class ExerciseValidation:
    version_id: UUID
    schema_code: str
    checker_type: str
    checker_version: int
    validation_spec: Mapping[str, object]
    answer_key: Answer
    accepted_variants: Sequence[Answer] = ()
    skill_codes: frozenset[str] = frozenset()
    # The caller may provide the original reviewed math state independently of
    # the canonical solution. That solution may start at a transformed state.
    initial_state: str | None = None


_FINAL_FORMS = {
    "integer_exact": Form.SCALAR,
    "linear_expression": Form.EXPRESSION,
    "equation_state": None,
    "integer_transitions": Form.SCALAR,
    "expression_transitions": Form.EXPRESSION,
    "equation_transitions": None,
}
_TRANSITION_FORMS = {
    "integer_transitions": Form.SCALAR,
    "expression_transitions": Form.EXPRESSION,
    "equation_transitions": Form.EQUATION,
}
_STRUCTURED_FORMS = {
    "coordinate_move_fields": (
        ("start", Form.SCALAR), ("displacement", Form.SCALAR), ("end", Form.SCALAR),
    ),
    "linear_parentheses_fields": (
        ("expanded_equation", Form.EQUATION_STATE),
        ("isolated_term_equation", Form.EQUATION_STATE),
        ("solution", Form.SOLUTION),
    ),
}


class EquationAnswerMode(StrEnum):
    """Server-owned answer semantics for equation checker version 2."""

    SOLUTION = "SOLUTION"
    EQUATION_STATE = "EQUATION_STATE"
    TRANSFORMED_EQUATION = "TRANSFORMED_EQUATION"


def analyze_submission(
    exercise: ExerciseValidation, submission: SubmittedSolution, *, graph: PilotGraphRead | None = None,
) -> AnalysisResult:
    """Join an owned submitted snapshot to its authoritative version and active skills.

    This interface accepts no client-provided result, rule, skill, or evidence.
    The caller owns authorization, immutable snapshot validation and persistence.
    """
    template = TEMPLATES.get(exercise.schema_code) if isinstance(exercise.schema_code, str) else None
    if (template is None or template.parser is None or type(exercise.checker_version) is not int
            or exercise.checker_type != template.checker
            or (template.checker not in _FINAL_FORMS and template.checker not in _STRUCTURED_FORMS)):
        return AnalysisResult(Verdict.UNSUPPORTED)
    equation_checker = template.checker in ("equation_state", "equation_transitions")
    if exercise.checker_version != 1 and not (equation_checker and exercise.checker_version == 2):
        return AnalysisResult(Verdict.UNSUPPORTED)
    expected_spec = {
        "required_fields": [name for name, _ in template.fields], "step_type": template.step_type,
    }
    mode = None
    final_form = _FINAL_FORMS.get(template.checker, Form.SCALAR)
    if exercise.checker_version == 2:
        raw_mode = exercise.validation_spec.get("equation_answer_mode") if isinstance(
            exercise.validation_spec, Mapping
        ) else None
        try:
            mode = EquationAnswerMode(raw_mode)
        except ValueError:
            return AnalysisResult(Verdict.INDETERMINATE, parser_version=template.parser)
        expected_spec["equation_answer_mode"] = mode.value
        final_form = Form.SOLUTION if mode == EquationAnswerMode.SOLUTION else Form.EQUATION_STATE
    if (exercise.validation_spec != expected_spec
            or not isinstance(exercise.accepted_variants, (tuple, list))
            or len(exercise.accepted_variants) >= MAX_STEPS):
        return AnalysisResult(Verdict.INDETERMINATE, parser_version=template.parser)

    known = frozenset()
    linked = exercise.skill_codes
    if graph is not None and graph.graph_version == PILOT_VERSION and isinstance(linked, frozenset):
        active = frozenset(node.code for node in graph.skills if node.active)
        if linked <= active:
            known = linked
    return analyze(CheckPlan(
        version_id=exercise.version_id,
        profile=template.parser,
        final_form=final_form,
        fields=_STRUCTURED_FORMS.get(template.checker, ()),
        keys=(exercise.answer_key, *exercise.accepted_variants),
        transition_form=_TRANSITION_FORMS.get(template.checker),
        transition_step_type=template.step_type,
        initial_state=exercise.initial_state,
        allowed_skills=known,
        integer_key=template.checker == "integer_exact",
        requires_transformation=mode == EquationAnswerMode.TRANSFORMED_EQUATION,
    ), submission)
