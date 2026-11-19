"""Evaluate the whitelist AST with exact, bounded affine arithmetic."""

from dataclasses import dataclass
from fractions import Fraction

from ._syntax import Binary, Equation, Expr, Kind, Number, Parser, Power, Unary, Variable, lex
from .model import LinearEquation, LinearExpression, ParseFailure, ParseReason
from .profiles import MAX_RATIONAL_BITS, Profile


@dataclass(frozen=True, slots=True)
class Term:
    coefficient: Fraction
    constant: Fraction
    has_variable: bool

    def linear(self) -> LinearExpression:
        return LinearExpression(self.coefficient, self.constant)


ZERO = Fraction(0)


def _bits(value: Fraction) -> int:
    return max(value.numerator.bit_length(), value.denominator.bit_length())


def _bounded(value: Fraction) -> Fraction:
    if _bits(value) > MAX_RATIONAL_BITS:
        raise ParseFailure(ParseReason.ARITHMETIC_LIMIT)
    return value


def _evaluate(node: Expr, profile: Profile) -> Term:
    match node:
        case Number(value):
            return Term(ZERO, value, False)
        case Variable():
            if not profile.linear:
                raise ParseFailure(ParseReason.OUTSIDE_PROFILE)
            return Term(Fraction(1), ZERO, True)
        case Unary(operator, operand):
            term = _evaluate(operand, profile)
            if operator == Kind.MINUS:
                return Term(-term.coefficient, -term.constant, term.has_variable)
            return term
        case Power(base, exponent):
            term = _evaluate(base, profile)
            if exponent == 1:
                return term
            if term.has_variable:
                reason = ParseReason.VARIABLE_DENOMINATOR if exponent < 0 else ParseReason.NONLINEAR
                raise ParseFailure(reason)
            if not term.constant and exponent <= 0:
                raise ParseFailure(ParseReason.UNDEFINED)
            if (_bits(term.constant) - 1) * abs(exponent) >= MAX_RATIONAL_BITS:
                raise ParseFailure(ParseReason.ARITHMETIC_LIMIT)
            return Term(ZERO, _bounded(term.constant ** exponent), False)
        case Binary(operator, left, right):
            lhs = _evaluate(left, profile)
            rhs = _evaluate(right, profile)
            return _combine(operator, lhs, rhs)
    raise AssertionError("Unknown parser AST node")


def _combine(operator: Kind, lhs: Term, rhs: Term) -> Term:
    a, b = lhs.coefficient, lhs.constant
    c, d = rhs.coefficient, rhs.constant
    if operator == Kind.PLUS:
        coefficient, constant = a + c, b + d
    elif operator == Kind.MINUS:
        coefficient, constant = a - c, b - d
    elif operator == Kind.STAR:
        if a and c:
            raise ParseFailure(ParseReason.NONLINEAR)
        coefficient, constant = a * d + b * c, b * d
    else:
        assert operator == Kind.SLASH
        if rhs.has_variable:
            raise ParseFailure(ParseReason.VARIABLE_DENOMINATOR)
        if not d:
            raise ParseFailure(ParseReason.UNDEFINED)
        coefficient, constant = a / d, b / d
    return Term(_bounded(coefficient), _bounded(constant), lhs.has_variable or rhs.has_variable)


def normalize(text: str, profile: Profile) -> LinearExpression | LinearEquation:
    ast = Parser(lex(text)).parse()
    if isinstance(ast, Equation):
        if not profile.linear:
            raise ParseFailure(ParseReason.OUTSIDE_PROFILE)
        value = LinearEquation(_evaluate(ast.left, profile).linear(), _evaluate(ast.right, profile).linear())
        solution = value.unique_solution
        if solution is not None:
            _bounded(solution)
        return value
    return _evaluate(ast, profile).linear()
