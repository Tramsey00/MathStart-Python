"""Exact comparisons for N010 values and observable transition rules."""

from enum import StrEnum
from fractions import Fraction

from ._syntax import Ast, Binary, Equation, Expr, Kind, Number, Parser, Power, Unary, Variable, lex
from .model import EquationSolutions, LinearEquation, LinearExpression, ParseReason, ParseResult, ParseStatus


class Check(StrEnum):
    VALID = "VALID"
    WRONG = "WRONG"
    UNKNOWN = "UNKNOWN"
    UNSUPPORTED = "UNSUPPORTED"


class Form(StrEnum):
    SCALAR = "SCALAR"
    EXPRESSION = "EXPRESSION"
    EQUATION = "EQUATION"
    SOLUTION = "SOLUTION"
    EQUATION_OR_SOLUTION = "EQUATION_OR_SOLUTION"


class Rule(StrEnum):
    ADD_NEGATIVE = "add_negative"
    SUBTRACT_NEGATIVE = "subtract_negative"
    MULTIPLY_SIGN = "multiply_sign"
    DIVIDE_SIGN = "divide_sign"
    DISTRIBUTE_TO_BOTH_TERMS = "distribute_to_both_terms"
    COMBINE_ONLY_LIKE_TERMS = "combine_only_like_terms"
    ADD_TO_BOTH_SIDES = "add_to_both_sides"


type ComparableValue = Fraction | LinearExpression | tuple[EquationSolutions, Fraction | None]


def parse_check(parsed: ParseResult) -> Check:
    if parsed.parse_status == ParseStatus.OK and parsed.value is not None and parsed.reason is None:
        return Check.VALID
    if parsed.parse_status == ParseStatus.UNSUPPORTED and parsed.reason != ParseReason.WORKER_FAILURE:
        return Check.UNSUPPORTED
    return Check.UNKNOWN


def _solution_equation(value: LinearEquation) -> bool:
    if value.solution_kind != EquationSolutions.UNIQUE:
        return True
    left, right = value.left, value.right
    x = LinearExpression(Fraction(1), Fraction(0))
    return (left == x and not right.coefficient) or (right == x and not left.coefficient)


def comparison_value(parsed: ParseResult, form: Form) -> tuple[Check, ComparableValue | None]:
    status = parse_check(parsed)
    if status != Check.VALID:
        return status, None
    value = parsed.value
    if isinstance(value, LinearExpression):
        if form == Form.EXPRESSION:
            return Check.VALID, value
        if form == Form.SCALAR and not value.coefficient:
            return Check.VALID, value.constant
        if form in (Form.SOLUTION, Form.EQUATION_OR_SOLUTION) and not value.coefficient:
            return Check.VALID, (EquationSolutions.UNIQUE, value.constant)
    elif isinstance(value, LinearEquation):
        if (form in (Form.EQUATION, Form.EQUATION_OR_SOLUTION)
                or (form == Form.SOLUTION and _solution_equation(value))):
            return Check.VALID, (value.solution_kind, value.unique_solution)
    return Check.UNSUPPORTED, None


def compare(actual: ParseResult, expected: ParseResult, form: Form) -> Check:
    expected_status, expected_value = comparison_value(expected, form)
    if expected_status != Check.VALID:
        return Check.UNKNOWN
    actual_status, actual_value = comparison_value(actual, form)
    if actual_status != Check.VALID:
        return actual_status
    return Check.VALID if actual_value == expected_value else Check.WRONG


def _ast(parsed: ParseResult) -> Ast:
    # Only called on math text that already passed N010 in this analysis.
    assert parsed.raw is not None and parse_check(parsed) == Check.VALID
    return Parser(lex(parsed.raw)).parse()


def _number(node: Expr) -> Fraction | None:
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Unary) and isinstance(node.operand, Number):
        return -node.operand.value if node.operator == Kind.MINUS else node.operand.value
    return None


def _monomial(node: Expr) -> tuple[int, Fraction] | None:
    number = _number(node)
    if number is not None:
        return 0, number
    if isinstance(node, Variable):
        return 1, Fraction(1)
    if isinstance(node, Unary) and isinstance(node.operand, Variable):
        return 1, Fraction(-1 if node.operator == Kind.MINUS else 1)
    if isinstance(node, Binary) and node.operator == Kind.STAR and isinstance(node.right, Variable):
        coefficient = _number(node.left)
        if coefficient is not None:
            return 1, coefficient
    return None


def _distribution(before: Binary, after: Expr) -> bool:
    inner = before.right
    factor = _number(before.left)
    if (before.operator != Kind.STAR or factor in (None, 0, 1)
            or not isinstance(inner, Binary) or inner.operator not in (Kind.PLUS, Kind.MINUS)
            or not isinstance(after, Binary) or after.operator != inner.operator):
        return False
    for unchanged, scaled, candidate_unchanged, candidate_scaled in (
        (inner.left, inner.right, after.left, after.right),
        (inner.right, inner.left, after.right, after.left),
    ):
        a, b = _monomial(unchanged), _monomial(scaled)
        if (a is not None and b is not None and a[0] != b[0] and a[1] and b[1]
                and unchanged == candidate_unchanged
                and _monomial(candidate_scaled) == (b[0], b[1] * factor)):
            return True
    return False


def _observed_rules(before: Expr, after: Expr) -> tuple[Rule, ...]:
    if not isinstance(before, Binary):
        return ()
    left, right, operator = before.left, before.right, before.operator
    rules = []
    if _distribution(before, after):
        rules.append(Rule.DISTRIBUTE_TO_BOTH_TERMS)

    if operator == Kind.PLUS:
        a, b = _monomial(left), _monomial(right)
        if a and b and a[0] != b[0] and a[1] and b[1] and a[1] + b[1]:
            if _monomial(after) == (1, a[1] + b[1]):
                rules.append(Rule.COMBINE_ONLY_LIKE_TERMS)

    a, b = _number(left), _number(right)
    if a is not None and b is not None and b < 0 and isinstance(after, Binary):
        if after.operator == operator and after.left == left and _number(after.right) == -b:
            if operator == Kind.PLUS:
                rules.append(Rule.ADD_NEGATIVE)
            elif operator == Kind.MINUS:
                rules.append(Rule.SUBTRACT_NEGATIVE)
    if a and b and (a < 0 or b < 0):
        value = _number(after)
        if operator == Kind.STAR and value == -(a * b):
            rules.append(Rule.MULTIPLY_SIGN)
        elif operator == Kind.SLASH and value == -(a / b):
            rules.append(Rule.DIVIDE_SIGN)
    return tuple(rules)


def observed_rule(before: ParseResult, after: ParseResult, form: Form) -> Rule | None:
    """A rule is localized only on a proven mismatch with a single explicit pattern."""
    if compare(after, before, form) != Check.WRONG:
        return None
    a, b = _ast(before), _ast(after)
    if isinstance(a, Equation) and isinstance(b, Equation):
        if a.right == b.right:
            old, new = a.left, b.left
        elif a.left == b.left:
            old, new = a.right, b.right
        else:
            return None
        rules = _observed_rules(old, new)
        if (isinstance(new, Binary) and new.operator in (Kind.PLUS, Kind.MINUS)
                and new.left == old and _number(new.right)):
            rules += (Rule.ADD_TO_BOTH_SIDES,)
    elif not isinstance(a, Equation) and not isinstance(b, Equation):
        rules = _observed_rules(a, b)
    else:
        return None
    return rules[0] if len(rules) == 1 else None


def expanded_equation(parsed: ParseResult) -> bool:
    """Recognize expanded expressions conservatively from the accepted AST."""
    ast = _ast(parsed)
    if not isinstance(ast, Equation):
        return False

    def expanded(node: Expr, *, inside_operation: bool = False) -> bool:
        if isinstance(node, Binary):
            if node.operator in (Kind.PLUS, Kind.MINUS):
                return not inside_operation and expanded(node.left) and expanded(node.right)
            return (expanded(node.left, inside_operation=True)
                    and expanded(node.right, inside_operation=True))
        if isinstance(node, Unary):
            return expanded(node.operand, inside_operation=inside_operation or node.operator == Kind.MINUS)
        if isinstance(node, Power):
            return expanded(node.base, inside_operation=True)
        return True

    return expanded(ast.left) and expanded(ast.right)


def isolated_equation(parsed: ParseResult) -> bool:
    value = parsed.value
    if not isinstance(value, LinearEquation):
        return False
    left, right = value.left, value.right
    if not left.coefficient and not right.coefficient:
        return True
    return ((not left.constant and not right.coefficient)
            or (not right.constant and not left.coefficient))
