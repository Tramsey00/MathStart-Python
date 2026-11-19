"""Typed normalized values and server-side parse outcomes."""

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction


class ParseStatus(StrEnum):
    OK = "OK"
    INVALID = "INVALID"
    UNSUPPORTED = "UNSUPPORTED"
    NOT_REQUIRED = "NOT_REQUIRED"


class ParseReason(StrEnum):
    SYNTAX = "SYNTAX"
    UNSUPPORTED_SYNTAX = "UNSUPPORTED_SYNTAX"
    UNKNOWN_PROFILE = "UNKNOWN_PROFILE"
    OUTSIDE_PROFILE = "OUTSIDE_PROFILE"
    NONLINEAR = "NONLINEAR"
    VARIABLE_DENOMINATOR = "VARIABLE_DENOMINATOR"
    UNDEFINED = "UNDEFINED"
    REQUEST_LIMIT = "REQUEST_LIMIT"
    STEP_LIMIT = "STEP_LIMIT"
    LENGTH_LIMIT = "LENGTH_LIMIT"
    TOKEN_LIMIT = "TOKEN_LIMIT"
    NESTING_LIMIT = "NESTING_LIMIT"
    LITERAL_LIMIT = "LITERAL_LIMIT"
    POWER_LIMIT = "POWER_LIMIT"
    ARITHMETIC_LIMIT = "ARITHMETIC_LIMIT"
    TIMEOUT = "TIMEOUT"
    WORKER_FAILURE = "WORKER_FAILURE"


class EquationSolutions(StrEnum):
    UNIQUE = "UNIQUE"
    ALL = "ALL"
    NONE = "NONE"


@dataclass(frozen=True, slots=True)
class LinearExpression:
    """The exact form ax + b. A scalar has coefficient zero."""

    coefficient: Fraction
    constant: Fraction

    def render(self) -> str:
        if not self.coefficient:
            return str(self.constant)
        if self.coefficient == 1:
            variable = "x"
        elif self.coefficient == -1:
            variable = "-x"
        else:
            variable = f"{self.coefficient}*x"
        if not self.constant:
            return variable
        sign = "+" if self.constant > 0 else "-"
        return f"{variable} {sign} {abs(self.constant)}"


@dataclass(frozen=True, slots=True)
class LinearEquation:
    left: LinearExpression
    right: LinearExpression

    def render(self) -> str:
        return f"Eq({self.left.render()}, {self.right.render()})"

    @property
    def solution_kind(self) -> EquationSolutions:
        if self.left.coefficient != self.right.coefficient:
            return EquationSolutions.UNIQUE
        if self.left.constant == self.right.constant:
            return EquationSolutions.ALL
        return EquationSolutions.NONE

    @property
    def unique_solution(self) -> Fraction | None:
        if self.solution_kind == EquationSolutions.UNIQUE:
            return (self.right.constant - self.left.constant) / (self.left.coefficient - self.right.coefficient)
        return None


@dataclass(frozen=True, slots=True)
class ParseInput:
    text: str | None
    profile: str | None


@dataclass(frozen=True, slots=True)
class ParseResult:
    raw: str | None
    profile: str | None
    parse_status: ParseStatus
    value: LinearExpression | LinearEquation | None = None
    reason: ParseReason | None = None

    @property
    def normalized_repr(self) -> str | None:
        return self.value.render() if self.value is not None else None


@dataclass(frozen=True, slots=True)
class BatchResult:
    results: tuple[ParseResult, ...] = ()
    rejection: ParseReason | None = None


class ParseFailure(Exception):
    """Internal control flow. Only the reason code crosses the process boundary."""

    def __init__(self, reason: ParseReason):
        super().__init__(reason)
        self.reason = reason


def failed(item: ParseInput, reason: ParseReason) -> ParseResult:
    status = ParseStatus.INVALID if reason == ParseReason.SYNTAX else ParseStatus.UNSUPPORTED
    return ParseResult(item.text, item.profile, status, reason=reason)
