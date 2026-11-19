"""Server-only N011 inputs and validated analysis results."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from uuid import UUID

from backend.math_validation.validators import Check, Rule


class Verdict(StrEnum):
    CORRECT = "CORRECT"
    WRONG = "WRONG"
    UNSUPPORTED = "UNSUPPORTED"
    INDETERMINATE = "INDETERMINATE"


class Classification(StrEnum):
    SIGN_ERROR = "SIGN_ERROR"
    DISTRIBUTIVE_PROPERTY = "DISTRIBUTIVE_PROPERTY"
    LIKE_TERMS = "LIKE_TERMS"
    EQUATION_BALANCE = "EQUATION_BALANCE"
    ARITHMETIC_ERROR = "ARITHMETIC_ERROR"
    OTHER = "OTHER"


RULE_TAXONOMY = MappingProxyType({
    Rule.ADD_NEGATIVE: (Classification.SIGN_ERROR, "sign_rules_add_sub"),
    Rule.SUBTRACT_NEGATIVE: (Classification.SIGN_ERROR, "sign_rules_add_sub"),
    Rule.MULTIPLY_SIGN: (Classification.SIGN_ERROR, "sign_rules_mul_div"),
    Rule.DIVIDE_SIGN: (Classification.SIGN_ERROR, "sign_rules_mul_div"),
    Rule.DISTRIBUTE_TO_BOTH_TERMS: (Classification.DISTRIBUTIVE_PROPERTY, "distributive_property"),
    Rule.COMBINE_ONLY_LIKE_TERMS: (Classification.LIKE_TERMS, "combine_like_terms"),
    Rule.ADD_TO_BOTH_SIDES: (Classification.EQUATION_BALANCE, "equation_balance"),
})


class EvidenceKind(StrEnum):
    FINAL_ANSWER = "FINAL_ANSWER"
    TRANSITION = "TRANSITION"
    STRUCTURED_FIELD = "STRUCTURED_FIELD"


type Answer = str | Mapping[str, str]


@dataclass(frozen=True, slots=True)
class SubmittedStep:
    step_id: UUID
    step_no: int
    step_type: str
    payload: Mapping[str, str]
    raw_text: str | None = None


@dataclass(frozen=True, slots=True)
class SubmittedSolution:
    attempt_id: UUID
    exercise_version_id: UUID
    payload: Mapping[str, str]
    steps: tuple[SubmittedStep, ...] = ()


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    kind: EvidenceKind
    attempt_id: UUID
    exercise_version_id: UUID
    step_id: UUID | None = None
    previous_step_id: UUID | None = None
    field_name: str | None = None
    rule: Rule | None = None

    def __post_init__(self):
        if (not isinstance(self.kind, EvidenceKind)
                or not valid_id(self.attempt_id) or not valid_id(self.exercise_version_id)
                or any(ref is not None and not valid_id(ref) for ref in (self.step_id, self.previous_step_id))):
            raise ValueError("Invalid evidence identity")
        if self.kind == EvidenceKind.TRANSITION:
            # A null previous step refers to the trusted original exercise state.
            if (self.step_id is None or self.previous_step_id == self.step_id or self.field_name is not None
                    or (self.rule is not None and not isinstance(self.rule, Rule))):
                raise ValueError("Invalid transition reference")
        elif self.kind == EvidenceKind.STRUCTURED_FIELD:
            if (self.step_id is None or not isinstance(self.field_name, str) or not self.field_name
                    or self.previous_step_id is not None or self.rule is not None):
                raise ValueError("Invalid structured field reference")
        elif any(ref is not None for ref in (self.previous_step_id, self.field_name, self.rule)):
            raise ValueError("Final answer evidence refers to a payload or final statement")

    def belongs_to(self, submission: SubmittedSolution) -> bool:
        if (self.attempt_id, self.exercise_version_id) != (submission.attempt_id, submission.exercise_version_id):
            return False
        if self.kind == EvidenceKind.FINAL_ANSWER and self.step_id is None:
            return bool(submission.payload)
        for index, step in enumerate(submission.steps):
            if step.step_id != self.step_id:
                continue
            if self.kind == EvidenceKind.FINAL_ANSWER:
                return (index == len(submission.steps) - 1 and step.step_type == "FINAL_STATEMENT"
                        and len(step.payload) == 1)
            if self.kind == EvidenceKind.STRUCTURED_FIELD:
                return (step.step_type in ("STRUCTURED_FIELDS", "FINAL_STATEMENT")
                        and self.field_name in step.payload and self.field_name in submission.payload)
            return (step.step_type in ("MATH_EXPRESSION", "EQUATION_STATE")
                    and self.previous_step_id == (submission.steps[index - 1].step_id if index else None))
        return False


def valid_id(value: object) -> bool:
    return isinstance(value, UUID) and value.int != 0


_RULE_FEEDBACK = {
    Classification.SIGN_ERROR: "Проверьте правило знаков в отмеченном шаге.",
    Classification.DISTRIBUTIVE_PROPERTY: "Проверьте, применили ли вы множитель к каждому слагаемому.",
    Classification.LIKE_TERMS: "Проверьте, какие слагаемые можно объединять.",
    Classification.EQUATION_BALANCE: "Проверьте, выполнили ли вы одно и то же действие с обеими частями равенства.",
}


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    verdict: Verdict
    final_verdict: Verdict | None = None
    prefix_status: Check | None = None
    blocking_step_id: UUID | None = None
    classification: Classification | None = None
    skill_codes: tuple[str, ...] = ()
    evidence_refs: tuple[EvidenceRef, ...] = ()
    schema_version: int = field(default=1, init=False)
    source: str = field(default="DETERMINISTIC", init=False)
    parser_version: str | None = None
    validator_version: str = field(default="deterministic-v1", init=False)
    taxonomy_version: str = field(default="taxonomy-v1", init=False)
    prompt_version: None = field(default=None, init=False)
    model_version: None = field(default=None, init=False)
    confidence: float = field(init=False)

    def __post_init__(self):
        if (not isinstance(self.verdict, Verdict)
                or (self.final_verdict is not None and not isinstance(self.final_verdict, Verdict))
                or (self.prefix_status is not None and not isinstance(self.prefix_status, Check))
                or (self.blocking_step_id is not None and (not valid_id(self.blocking_step_id)
                    or self.prefix_status not in (Check.UNKNOWN, Check.UNSUPPORTED)))
                or type(self.evidence_refs) is not tuple or len(self.evidence_refs) > 1
                or any(not isinstance(ref, EvidenceRef) for ref in self.evidence_refs)
                or type(self.skill_codes) is not tuple):
            raise ValueError("Invalid analysis result shape")
        proven = self.verdict in (Verdict.CORRECT, Verdict.WRONG)
        if proven != bool(self.evidence_refs):
            raise ValueError("A determinate verdict requires exactly one evidence unit")
        ref = self.evidence_refs[0] if proven else None
        if ref and ref.kind != EvidenceKind.FINAL_ANSWER:
            if self.verdict != Verdict.WRONG or self.prefix_status != Check.WRONG:
                raise ValueError("First defect requires a failed checked step")
        if self.classification is not None and (
                not isinstance(self.classification, Classification) or self.verdict != Verdict.WRONG
                or ref is None or ref.kind == EvidenceKind.FINAL_ANSWER):
            raise ValueError("Classification requires a proven localized defect")
        if ref and ref.rule is not None:
            code, skill = RULE_TAXONOMY[ref.rule]
            if self.classification != code or self.skill_codes != (skill,):
                raise ValueError("Rule, taxonomy and skill differ")
        elif self.classification not in (None, Classification.OTHER) or self.skill_codes:
            raise ValueError("Specific classification requires a verified rule")
        object.__setattr__(self, "confidence", 1.0 if proven else 0.0)

    @property
    def first_error_step_id(self) -> UUID | None:
        if self.verdict == Verdict.WRONG and self.evidence_refs[0].kind != EvidenceKind.FINAL_ANSWER:
            return self.evidence_refs[0].step_id
        return None

    @property
    def misconception_code(self) -> Classification | None:
        return self.classification if self.classification != Classification.OTHER else None

    @property
    def safe_feedback(self) -> str:
        if self.classification in _RULE_FEEDBACK:
            return _RULE_FEEDBACK[self.classification]
        if self.verdict == Verdict.CORRECT:
            return "Ответ верен."
        if self.verdict == Verdict.WRONG:
            if self.first_error_step_id is not None:
                return "Проверьте преобразование или поля в отмеченном шаге."
            return "Итоговый ответ неверен. Проверьте решение."
        if self.verdict == Verdict.UNSUPPORTED:
            return "Это выражение или преобразование пока не поддерживается проверкой."
        return "Недостаточно данных для надёжной проверки. Проверьте запись решения."
