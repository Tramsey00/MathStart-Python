"""Verify the final answer and walk only the continuous verified prefix."""

from collections.abc import Mapping
from dataclasses import dataclass
from uuid import UUID

from backend.math_validation.model import ParseInput, ParseReason, ParseResult
from backend.math_validation.parser import parse_batch
from backend.math_validation.profiles import MAX_REQUEST_BYTES, MAX_STEPS
from backend.math_validation.validators import (
    Check, Form, compare, comparison_value, equation_transformed, expanded_equation, observed_rule,
)
from .model import (
    RULE_TAXONOMY, AnalysisResult, Answer, Classification, EvidenceKind, EvidenceRef,
    SubmittedSolution, SubmittedStep, Verdict, valid_id,
)


class AnalysisUnavailable(Exception):
    """A worker failure leaves a submitted operation eligible for retry."""


@dataclass(frozen=True, slots=True)
class CheckPlan:
    version_id: UUID
    profile: str
    final_form: Form | None
    fields: tuple[tuple[str, Form], ...]
    keys: tuple[Answer, ...]
    transition_form: Form | None = None
    transition_step_type: str | None = None
    initial_state: str | None = None
    allowed_skills: frozenset[str] = frozenset()
    integer_key: bool = False
    requires_transformation: bool = False


_VERDICTS = {
    Check.VALID: Verdict.CORRECT,
    Check.WRONG: Verdict.WRONG,
    Check.UNKNOWN: Verdict.INDETERMINATE,
    Check.UNSUPPORTED: Verdict.UNSUPPORTED,
}


def _fields(payload: Mapping[str, str], names: tuple[str, ...]) -> bool:
    return (isinstance(payload, Mapping) and len(payload) == len(names) and payload.keys() == set(names)
            and all(isinstance(value, str) for value in payload.values()))


def _bound_steps(submission: SubmittedSolution, plan: CheckPlan) -> tuple[SubmittedStep, ...] | None:
    if (not valid_id(submission.attempt_id) or not valid_id(submission.exercise_version_id)
            or submission.exercise_version_id != plan.version_id
            or not isinstance(submission.steps, (tuple, list))):
        return None
    steps = tuple(submission.steps)
    seen = set()
    for position, step in enumerate(steps, 1):
        if (not isinstance(step, SubmittedStep) or type(step.step_no) is not int or step.step_no != position
                or not valid_id(step.step_id) or step.step_id in seen):
            return None
        seen.add(step.step_id)
    return steps


def _parse(texts: list[str], profile: str, *, retry_worker_failure: bool) -> dict[str, ParseResult] | None:
    if (sum(map(len, texts)) > MAX_REQUEST_BYTES
            or sum(len(text.encode("utf-8", errors="surrogatepass")) for text in texts) > MAX_REQUEST_BYTES):
        return None
    # A final statement may repeat the same raw field as the final payload.
    distinct = tuple(dict.fromkeys(texts))
    batch = parse_batch(tuple(ParseInput(text, profile) for text in distinct))
    if batch.rejection is not None:
        return None
    if retry_worker_failure and any(
        result.reason in (ParseReason.WORKER_FAILURE, ParseReason.TIMEOUT) for result in batch.results
    ):
        raise AnalysisUnavailable('Deterministic math worker unavailable')
    return dict(zip(distinct, batch.results, strict=True))


def _check_against(actual: ParseResult, expected: list[ParseResult], form: Form) -> Check:
    checks = [compare(actual, key, form) for key in expected]
    if Check.UNKNOWN in checks:
        return Check.UNKNOWN
    if Check.VALID in checks:
        return Check.VALID
    if Check.UNSUPPORTED in checks:
        return Check.UNSUPPORTED
    return Check.WRONG


def _check_final(
    plan: CheckPlan, actual: ParseResult, keys: list[ParseResult], start: ParseResult | None,
) -> Check:
    if plan.final_form is None:
        return Check.UNKNOWN
    result = _check_against(actual, keys, plan.final_form)
    if (plan.requires_transformation and start is not None
            and compare(actual, start, Form.EQUATION) == Check.VALID
            and not equation_transformed(start, actual)):
        # Restating the original does not demonstrate the requested change,
        # even when normalization yields identical sides to the approved key.
        return Check.UNKNOWN
    return result


def _final(
    plan: CheckPlan, submission: SubmittedSolution, check: Check, *,
    prefix: Check | None = None, statement: SubmittedStep | None = None,
) -> AnalysisResult:
    verdict = _VERDICTS[check]
    refs = ()
    if check in (Check.VALID, Check.WRONG):
        ref = EvidenceRef(EvidenceKind.FINAL_ANSWER, submission.attempt_id, plan.version_id,
                          step_id=statement.step_id if statement else None)
        if not ref.belongs_to(submission):
            return _gap(plan, check, Check.UNKNOWN)
        refs = (ref,)
    return AnalysisResult(verdict, final_verdict=verdict, prefix_status=prefix,
                          evidence_refs=refs, parser_version=plan.profile)


def _gap(plan: CheckPlan, final: Check, prefix: Check, step: SubmittedStep | None = None) -> AnalysisResult:
    return AnalysisResult(
        _VERDICTS[prefix], final_verdict=_VERDICTS[final], prefix_status=prefix,
        blocking_step_id=step.step_id if step is not None else None, parser_version=plan.profile,
    )


def _defect(plan: CheckPlan, submission: SubmittedSolution, final: Check, ref: EvidenceRef) -> AnalysisResult:
    if not ref.belongs_to(submission):
        return _gap(plan, final, Check.UNKNOWN)
    code, skills = Classification.OTHER, ()
    if ref.rule is not None:
        code, skill = RULE_TAXONOMY[ref.rule]
        skills = (skill,)
    return AnalysisResult(
        Verdict.WRONG, final_verdict=_VERDICTS[final], prefix_status=Check.WRONG,
        classification=code, skill_codes=skills, evidence_refs=(ref,), parser_version=plan.profile,
    )


def _step_field(step: SubmittedStep, plan: CheckPlan) -> str | None:
    if step.step_type == plan.transition_step_type and _fields(step.payload, ("expression",)):
        return step.payload["expression"]
    if step.step_type == "FINAL_STATEMENT" and _fields(step.payload, ("answer",)):
        return step.payload["answer"]
    return None


def _trace(
    plan: CheckPlan, submission: SubmittedSolution, steps: tuple[SubmittedStep, ...],
    actual: dict[str, ParseResult], start: ParseResult | None, final: Check, statement: SubmittedStep | None,
) -> AnalysisResult:
    assert plan.transition_form is not None
    if start is None or comparison_value(start, plan.transition_form)[0] != Check.VALID:
        return _gap(plan, final, Check.UNKNOWN)
    previous_id = None
    previous = start
    transformed = False
    for step in steps:
        text = _step_field(step, plan)
        if text is None:
            return _gap(plan, final, Check.UNKNOWN, step)
        if step.step_type == "FINAL_STATEMENT":
            if step is not statement or previous_id is None:
                return _gap(plan, final, Check.UNKNOWN, step)
            if final in (Check.UNKNOWN, Check.UNSUPPORTED):
                return _gap(plan, final, final, step)
            break
        current = actual[text]
        check = compare(current, previous, plan.transition_form)
        if check != Check.VALID:
            if check != Check.WRONG:
                return _gap(plan, final, check, step)
            rule = observed_rule(previous, current, plan.transition_form)
            # N009 has no marker for arithmetic work on a subexpression.
            # An exact scalar mismatch alone cannot establish its operand scope.
            if plan.transition_form == Form.SCALAR and rule is None:
                return _gap(plan, final, Check.UNKNOWN, step)
            if rule is not None and RULE_TAXONOMY[rule][1] not in plan.allowed_skills:
                rule = None
            ref = EvidenceRef(EvidenceKind.TRANSITION, submission.attempt_id, plan.version_id,
                              step.step_id, previous_id, rule=rule)
            return _defect(plan, submission, final, ref)
        if plan.transition_form == Form.EQUATION and not transformed:
            transformed = equation_transformed(previous, current)
        previous, previous_id = current, step.step_id
    if plan.transition_form == Form.EQUATION and not transformed:
        return _gap(plan, final, Check.UNKNOWN)
    return _final(plan, submission, final, prefix=Check.VALID, statement=statement)


def _phase(parsed: ParseResult, field: str, form: Form) -> Check:
    status, _ = comparison_value(parsed, form)
    if status != Check.VALID:
        return status
    if field == "expanded_equation" and not expanded_equation(parsed):
        return Check.UNSUPPORTED
    return Check.VALID


def _structured(
    plan: CheckPlan, submission: SubmittedSolution, steps: tuple[SubmittedStep, ...],
    actual: dict[str, ParseResult], keys: list[dict[str, ParseResult]], start: ParseResult | None,
) -> AnalysisResult:
    (final_field, final_form) = plan.fields[-1]
    final_value = actual[submission.payload[final_field]]
    final = _check_against(final_value, [key[final_field] for key in keys], final_form)
    remaining = keys
    for field, form in plan.fields[:-1]:
        current = actual[submission.payload[field]]
        status = _phase(current, field, form)
        if status != Check.VALID:
            return _gap(plan, final, status, steps[0])
        if (form == Form.EQUATION_STATE and start is not None
                and compare(current, start, Form.EQUATION) == Check.VALID
                and not equation_transformed(start, current)):
            return _gap(plan, final, Check.UNKNOWN, steps[0])
        matching = [key for key in remaining if compare(current, key[field], form) == Check.VALID]
        if not matching:
            if form == Form.EQUATION_STATE and any(
                compare(current, key[field], Form.EQUATION) == Check.VALID for key in remaining
            ):
                return _gap(plan, final, Check.UNKNOWN, steps[0])
            ref = EvidenceRef(EvidenceKind.STRUCTURED_FIELD, submission.attempt_id, plan.version_id,
                              steps[0].step_id, field_name=field)
            return _defect(plan, submission, final, ref)
        remaining = matching
    final_with_prefix = _check_against(final_value, [key[final_field] for key in remaining], final_form)
    if final_with_prefix == Check.WRONG and final == Check.VALID:
        # Valid fields from distinct accepted variants cannot form a new key.
        ref = EvidenceRef(EvidenceKind.STRUCTURED_FIELD, submission.attempt_id, plan.version_id,
                          steps[-1].step_id, field_name=final_field)
        return _defect(plan, submission, final, ref)
    return _final(plan, submission, final_with_prefix, prefix=Check.VALID, statement=steps[-1])


def _coherent_key(plan: CheckPlan, key: dict[str, ParseResult], start: ParseResult | None) -> bool:
    if any(_phase(key[name], name, form) != Check.VALID for name, form in plan.fields):
        return False
    if plan.fields[0][1] == Form.SCALAR:
        start, displacement, end = (comparison_value(key[name], Form.SCALAR)[1] for name, _ in plan.fields)
        return start + displacement == end
    expanded, isolated, solution = (key[name] for name, _ in plan.fields)
    _, intermediate = comparison_value(isolated, Form.EQUATION)
    _, final = comparison_value(solution, Form.SOLUTION)
    return (compare(expanded, isolated, Form.EQUATION) == Check.VALID
            and compare(expanded, isolated, Form.EQUATION_STATE) == Check.WRONG
            and intermediate == final
            and (start is None or compare(expanded, start, Form.EQUATION) == Check.VALID))


def analyze(plan: CheckPlan, submission: SubmittedSolution, *, retry_worker_failure: bool = False) -> AnalysisResult:
    """Run pure analysis from one immutable Assessment snapshot and its private checker."""
    unverified = AnalysisResult(Verdict.INDETERMINATE, parser_version=plan.profile)
    unsupported = AnalysisResult(Verdict.UNSUPPORTED, parser_version=plan.profile)
    if not isinstance(submission.steps, (tuple, list)):
        return unverified
    if len(submission.steps) > MAX_STEPS:
        return unsupported
    steps = _bound_steps(submission, plan)
    names = tuple(name for name, _ in plan.fields)
    if not names and plan.transition_form is None:
        names = ("answer",)
    if steps is None or not _fields(submission.payload, names):
        return unverified

    student = list(submission.payload.values())
    statement = None
    if plan.fields:
        groups = (names[:-1], names[-1:])
        if len(steps) != 2 or (steps[0].step_type, steps[1].step_type) != ("STRUCTURED_FIELDS", "FINAL_STATEMENT"):
            return unverified
        if any(step.payload != {name: submission.payload[name] for name in group}
               for step, group in zip(steps, groups, strict=True)):
            return unverified
    elif plan.transition_form is not None:
        if not steps:
            return unverified
        student.extend(text for step in steps if (text := _step_field(step, plan)) is not None)
        statements = [step for step in steps if step.step_type == "FINAL_STATEMENT"]
        if len(statements) == 1 and statements[0] is steps[-1]:
            statement = statements[0]
    elif steps or plan.final_form is None:
        return unverified

    if not plan.keys or len(plan.keys) > MAX_STEPS:
        return unverified
    if plan.fields:
        if not all(_fields(key, names) for key in plan.keys):
            return unverified
        expected = [key[name] for key in plan.keys for name in names]
    else:
        if not all(isinstance(key, str) for key in plan.keys):
            return unverified
        expected = list(plan.keys)
    if plan.initial_state is not None:
        if not isinstance(plan.initial_state, str):
            return unverified
        expected.append(plan.initial_state)

    parsed_keys = _parse(expected, plan.profile, retry_worker_failure=retry_worker_failure)
    if parsed_keys is None:
        return unverified
    start = parsed_keys.get(plan.initial_state)
    if plan.fields:
        structured_keys = [{name: parsed_keys[key[name]] for name in names} for key in plan.keys]
        if not all(_coherent_key(plan, key, start) for key in structured_keys):
            return unverified
        parsed_student = _parse(student, plan.profile, retry_worker_failure=retry_worker_failure)
        if parsed_student is None:
            return unsupported
        return _structured(plan, submission, steps, parsed_student, structured_keys, start)

    final_keys = [parsed_keys[key] for key in plan.keys]
    # Legacy equation checkers can still verify mathematical consistency for
    # transitions. This comparison never selects a final answer mode.
    key_form = plan.final_form or Form.EQUATION_OR_SOLUTION
    for key in final_keys:
        check, value = comparison_value(key, key_form)
        if check != Check.VALID or (plan.integer_key and value.denominator != 1):
            return unverified
    if plan.requires_transformation and (
        start is None or any(compare(key, start, Form.EQUATION) != Check.VALID
                             or not equation_transformed(start, key) for key in final_keys)
    ):
        return unverified
    if start is not None and plan.transition_form is not None:
        anchor_form = (Form.EQUATION_OR_SOLUTION if plan.transition_form == Form.EQUATION
                       else plan.transition_form)
        anchor_status, _ = comparison_value(start, plan.transition_form)
        if anchor_status == Check.VALID and any(
            compare(key, start, anchor_form) != Check.VALID for key in final_keys
        ):
            return unverified
    parsed_student = _parse(student, plan.profile, retry_worker_failure=retry_worker_failure)
    if parsed_student is None:
        return unsupported
    if plan.transition_form is not None:
        answer = _step_field(statement, plan) if statement is not None else None
        final = Check.UNKNOWN if answer is None else _check_final(plan, parsed_student[answer], final_keys, start)
        return _trace(plan, submission, steps, parsed_student, start, final, statement)
    final = _check_final(plan, parsed_student[submission.payload["answer"]], final_keys, start)
    return _final(plan, submission, final)
