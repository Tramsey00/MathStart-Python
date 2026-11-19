"""Whitelist lexer and typed AST for the v1 pilot grammar."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
import re

from .model import ParseFailure, ParseReason
from .profiles import MAX_ABS_POWER, MAX_LITERAL_DIGITS, MAX_NESTING, MAX_TOKENS


class Kind(StrEnum):
    NUMBER = "number"
    VARIABLE = "x"
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    CARET = "^"
    OPEN = "("
    CLOSE = ")"
    EQUAL = "="
    END = "end"


@dataclass(frozen=True, slots=True)
class Token:
    kind: Kind
    text: str


_OPERATORS = {kind.value: kind for kind in Kind if len(kind.value) == 1 and kind != Kind.VARIABLE}
_OPERATORS["−"] = Kind.MINUS
_NUMBER = re.compile(r"[0-9]+(?:[.,][0-9]+)?")
_IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
_SIGNS = (Kind.PLUS, Kind.MINUS)


def lex(text: str) -> list[Token]:
    tokens = []
    position = 0
    nesting = 0
    while position < len(text):
        char = text[position]
        if char in " \t\r\n":
            position += 1
            continue
        if len(tokens) == MAX_TOKENS:
            raise ParseFailure(ParseReason.TOKEN_LIMIT)

        number = _NUMBER.match(text, position)
        if number:
            literal = number.group()
            digits = literal.replace(".", "").replace(",", "")
            if len(digits) > MAX_LITERAL_DIGITS:
                raise ParseFailure(ParseReason.LITERAL_LIMIT)
            tokens.append(Token(Kind.NUMBER, literal))
            position = number.end()
            continue

        identifier = _IDENTIFIER.match(text, position)
        if identifier:
            if identifier.group() != "x":
                raise ParseFailure(ParseReason.UNSUPPORTED_SYNTAX)
            tokens.append(Token(Kind.VARIABLE, "x"))
            position = identifier.end()
            continue

        if char in "²³⁰¹⁴⁵⁶⁷⁸⁹×÷≤≥≠√<>;:[]{}" or text.startswith("**", position):
            raise ParseFailure(ParseReason.UNSUPPORTED_SYNTAX)
        kind = _OPERATORS.get(char)
        if kind is None:
            raise ParseFailure(ParseReason.SYNTAX)
        if kind == Kind.OPEN:
            nesting += 1
            if nesting > MAX_NESTING:
                raise ParseFailure(ParseReason.NESTING_LIMIT)
        elif kind == Kind.CLOSE:
            nesting -= 1
            if nesting < 0:
                raise ParseFailure(ParseReason.SYNTAX)
        tokens.append(Token(kind, char))
        position += 1

    if nesting:
        raise ParseFailure(ParseReason.SYNTAX)
    tokens.append(Token(Kind.END, ""))
    return tokens


@dataclass(frozen=True, slots=True)
class Number:
    value: Fraction


@dataclass(frozen=True, slots=True)
class Variable:
    pass


@dataclass(frozen=True, slots=True)
class Unary:
    operator: Kind
    operand: Expr


@dataclass(frozen=True, slots=True)
class Binary:
    operator: Kind
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class Power:
    base: Expr
    exponent: int


@dataclass(frozen=True, slots=True)
class Equation:
    left: Expr
    right: Expr


type Expr = Number | Variable | Unary | Binary | Power
type Ast = Expr | Equation


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    @property
    def current(self) -> Kind:
        return self.tokens[self.index].kind

    def take(self, kind: Kind) -> Token:
        if self.current != kind:
            raise ParseFailure(ParseReason.SYNTAX)
        token = self.tokens[self.index]
        self.index += 1
        return token

    def parse(self) -> Ast:
        result: Ast = self.sum()
        if self.current == Kind.EQUAL:
            self.take(Kind.EQUAL)
            result = Equation(result, self.sum())
            if self.current == Kind.EQUAL:
                raise ParseFailure(ParseReason.UNSUPPORTED_SYNTAX)
        self.take(Kind.END)
        return result

    def sum(self) -> Expr:
        result = self.product()
        while self.current in _SIGNS:
            operator = self.take(self.current).kind
            result = Binary(operator, result, self.product())
        return result

    def product(self) -> Expr:
        factor = result = self.unary()
        previous_operator = None
        while True:
            if self.current in (Kind.STAR, Kind.SLASH):
                operator = self.take(self.current).kind
            elif self.current in (Kind.VARIABLE, Kind.OPEN):
                # R02 examples attest number–x and number–parenthesis.
                # A slash followed by juxtaposition has competing readings.
                coefficient = factor
                while isinstance(coefficient, Unary):
                    coefficient = coefficient.operand
                if (not isinstance(coefficient, Number)
                        or self.tokens[self.index - 1].kind != Kind.NUMBER
                        or previous_operator == Kind.SLASH):
                    raise ParseFailure(ParseReason.UNSUPPORTED_SYNTAX)
                operator = Kind.STAR
            else:
                if self.current == Kind.NUMBER and self.tokens[self.index - 1].kind == Kind.CLOSE:
                    raise ParseFailure(ParseReason.UNSUPPORTED_SYNTAX)
                return result
            factor = self.unary()
            result = Binary(operator, result, factor)
            previous_operator = operator

    def unary(self) -> Expr:
        if self.current in _SIGNS:
            operator = self.take(self.current).kind
            return Unary(operator, self.unary())
        base = self.atom()
        if self.current != Kind.CARET:
            return base
        self.take(Kind.CARET)
        exponent = self.exponent()
        if self.current == Kind.CARET:
            raise ParseFailure(ParseReason.UNSUPPORTED_SYNTAX)
        return Power(base, exponent)

    def exponent(self) -> int:
        parenthesized = self.current == Kind.OPEN
        if parenthesized:
            self.take(Kind.OPEN)
        sign = self.take(self.current).kind if self.current in _SIGNS else Kind.PLUS
        if self.current in (Kind.VARIABLE, Kind.OPEN):
            raise ParseFailure(ParseReason.UNSUPPORTED_SYNTAX)
        literal = self.take(Kind.NUMBER).text
        if not literal.isdecimal():
            raise ParseFailure(ParseReason.UNSUPPORTED_SYNTAX)
        value = int(literal)
        if value > MAX_ABS_POWER:
            raise ParseFailure(ParseReason.POWER_LIMIT)
        if parenthesized:
            if self.current in (*_SIGNS, Kind.STAR, Kind.SLASH, Kind.CARET):
                raise ParseFailure(ParseReason.UNSUPPORTED_SYNTAX)
            self.take(Kind.CLOSE)
        return -value if sign == Kind.MINUS else value

    def atom(self) -> Expr:
        if self.current == Kind.NUMBER:
            return Number(Fraction(self.take(Kind.NUMBER).text.replace(",", ".")))
        if self.current == Kind.VARIABLE:
            self.take(Kind.VARIABLE)
            return Variable()
        self.take(Kind.OPEN)
        result = self.sum()
        self.take(Kind.CLOSE)
        return result
