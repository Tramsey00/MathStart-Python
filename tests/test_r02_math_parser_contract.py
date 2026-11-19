"""R02 parser goldens and resource limits without Assessment, DB, or LLM."""

from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
from time import monotonic
import unittest
from unittest.mock import patch

from backend.math_validation._syntax import Binary, Equation, Kind, Number, Parser, Unary, Variable, lex
from backend.math_validation.model import EquationSolutions, LinearEquation, LinearExpression
from backend.math_validation.model import ParseInput, ParseReason, ParseStatus
from backend.math_validation.parser import parse_batch, parse_expression
from backend.math_validation.profiles import MAX_CHARS, MAX_REQUEST_BYTES, MAX_STEPS


LINEAR = "algebra_linear_v1"
SCALAR = "algebra_scalar_v1"
FIXTURES = Path(__file__).resolve().parents[1] / "specs" / "exercises" / "fixtures"


class R02ParserTests(unittest.TestCase):
    def assert_abstained(self, result, status, reason):
        self.assertEqual((result.parse_status, result.reason), (status, reason), result.raw)
        self.assertIsNone(result.value)
        self.assertIsNone(result.normalized_repr)

    def test_typed_ast_preserves_precedence_and_equation_sides(self):
        parsed = Parser(lex("−2(x+3)=10")).parse()
        expected = Equation(
            Binary(
                Kind.STAR,
                Unary(Kind.MINUS, Number(Fraction(2))),
                Binary(Kind.PLUS, Variable(), Number(Fraction(3))),
            ),
            Number(Fraction(10)),
        )
        self.assertEqual(parsed, expected)

    def test_frozen_r02_exchange_fixtures(self):
        step = json.loads((FIXTURES / "step-submission.exchange-v1.json").read_text(encoding="utf-8"))
        submitted = step["request"]["submitted_step"]
        final = json.loads((FIXTURES / "final-answer-submission.exchange-v1.json").read_text(encoding="utf-8"))
        for expression, profile, expected in (
            (submitted["payload"]["expression"], LINEAR, step["response"]["step"]),
            (final["request"]["payload"]["answer"], SCALAR, final["response"]),
        ):
            with self.subTest(expression=expression):
                result = parse_expression(expression, profile)
                self.assertEqual(result.parse_status, expected["parse_status"])
                self.assertEqual(result.normalized_repr, expected["normalized_repr"])
                self.assertEqual(result.raw, expression)
        self.assertEqual(submitted["raw_text"], step["response"]["step"]["raw_text"])
        self.assertNotEqual(submitted["raw_text"], submitted["payload"]["expression"])

    def test_scalar_goldens(self):
        cases = (
            ("  −0,50 + 1/3  ", "arithmetic_v1", "-1/6"),
            ("0,1 + 0.2", SCALAR, "3/10"),
            ("3 / 6", "probability_fraction_v1", "1/2"),
            ("+001.250", SCALAR, "5/4"),
            ("-0,0", SCALAR, "0"),
            ("2--3", SCALAR, "5"),
            ("-(2 + 3) * −2", SCALAR, "10"),
            ("12/3/2", SCALAR, "2"),
            ("-(1/2)^(-2)", SCALAR, "-4"),
            ("-2^2 + (-2)^2", SCALAR, "0"),
            ("2(3+4)*(-2)", SCALAR, "-28"),
        )
        batch = parse_batch([ParseInput(text, profile) for text, profile, _ in cases])
        self.assertIsNone(batch.rejection)
        for result, (text, profile, expected) in zip(batch.results, cases, strict=True):
            with self.subTest(text=text):
                self.assertEqual((result.raw, result.profile), (text, profile))
                self.assertEqual(result.parse_status, ParseStatus.OK)
                self.assertEqual(result.value, LinearExpression(Fraction(0), Fraction(expected)))
                self.assertEqual(result.normalized_repr, expected)

    def test_linear_goldens(self):
        cases = (
            ("2(x + 3) = 10", "Eq(2*x + 6, 10)", EquationSolutions.UNIQUE, Fraction(2)),
            ("2x + 3 = x + 2", "Eq(2*x + 3, x + 2)", EquationSolutions.UNIQUE, Fraction(-1)),
            ("2x + 3 = 2(x + 1) + 1", "Eq(2*x + 3, 2*x + 3)", EquationSolutions.ALL, None),
            ("2x + 3 = 2x + 1", "Eq(2*x + 3, 2*x + 1)", EquationSolutions.NONE, None),
            ("(x−1)/2 = 0,1", "Eq(1/2*x - 1/2, 1/10)", EquationSolutions.UNIQUE, Fraction(6, 5)),
            ("−2(x+1)+x−1,5", "-x - 7/2", None, None),
        )
        results = parse_batch([ParseInput(text, LINEAR) for text, *_ in cases]).results
        for result, (text, expected, kind, solution) in zip(results, cases, strict=True):
            with self.subTest(text=text):
                self.assertEqual(result.parse_status, ParseStatus.OK)
                self.assertEqual(result.normalized_repr, expected)
                if kind is not None:
                    self.assertIsInstance(result.value, LinearEquation)
                    self.assertEqual(result.value.solution_kind, kind)
                    self.assertEqual(result.value.unique_solution, solution)
                else:
                    self.assertEqual(result.value, LinearExpression(Fraction(-1), Fraction(-7, 2)))

    def test_malformed_and_adversarial_inputs(self):
        invalid = (None, "", " \t", "2+", "()", "1//2", "2 3", "1,2,3", "2==3",
                   "2(", ")1(", "2^", "1\u200b2", "１+２", "1\x00+2", "__import__('os')",
                   "1_000", "x.__class__", "1+\ud800")
        results = parse_batch([ParseInput(text, LINEAR) for text in invalid]).results
        for text, result in zip(invalid, results, strict=True):
            with self.subTest(text=text):
                self.assert_abstained(result, ParseStatus.INVALID, ParseReason.SYNTAX)

    def test_unsupported_grammar_and_domains(self):
        cases = (
            ("sqrt(4)", ParseReason.UNSUPPORTED_SYNTAX), ("1e3", ParseReason.UNSUPPORTED_SYNTAX),
            ("x²", ParseReason.UNSUPPORTED_SYNTAX), ("x=y", ParseReason.UNSUPPORTED_SYNTAX),
            ("1=2=3", ParseReason.UNSUPPORTED_SYNTAX), ("x=1;x=2", ParseReason.UNSUPPORTED_SYNTAX),
            ("1/2x", ParseReason.UNSUPPORTED_SYNTAX), ("1/2(3)", ParseReason.UNSUPPORTED_SYNTAX),
            ("(2)x", ParseReason.UNSUPPORTED_SYNTAX), ("(2)(3)", ParseReason.UNSUPPORTED_SYNTAX),
            ("2^2x", ParseReason.UNSUPPORTED_SYNTAX), ("2^2^2", ParseReason.UNSUPPORTED_SYNTAX),
            ("2^(1+1)", ParseReason.UNSUPPORTED_SYNTAX), ("2^0.5", ParseReason.UNSUPPORTED_SYNTAX),
            ("2**3", ParseReason.UNSUPPORTED_SYNTAX), ("x*x", ParseReason.NONLINEAR),
            ("0*(x^2)", ParseReason.NONLINEAR), ("1/x", ParseReason.VARIABLE_DENOMINATOR),
            ("x^-1", ParseReason.VARIABLE_DENOMINATOR), ("1/(x−x+1)", ParseReason.VARIABLE_DENOMINATOR),
            ("1/(2-2)", ParseReason.UNDEFINED), ("0^0", ParseReason.UNDEFINED),
        )
        results = parse_batch([ParseInput(text, LINEAR) for text, _ in cases]).results
        for result, (text, reason) in zip(results, cases, strict=True):
            with self.subTest(text=text):
                self.assert_abstained(result, ParseStatus.UNSUPPORTED, reason)

    def test_profile_and_ordered_batch_statuses(self):
        batch = parse_batch([
            ParseInput("объяснение", None), ParseInput("1", "future_v2"),
            ParseInput("x−x", SCALAR), ParseInput("1=1", SCALAR),
            ParseInput("3", SCALAR), ParseInput("−", LINEAR),
        ])
        omitted, unknown, variable, equation, good, invalid = batch.results
        self.assertEqual(omitted.raw, "объяснение")
        self.assert_abstained(omitted, ParseStatus.NOT_REQUIRED, None)
        self.assert_abstained(unknown, ParseStatus.UNSUPPORTED, ParseReason.UNKNOWN_PROFILE)
        self.assert_abstained(variable, ParseStatus.UNSUPPORTED, ParseReason.OUTSIDE_PROFILE)
        self.assert_abstained(equation, ParseStatus.UNSUPPORTED, ParseReason.OUTSIDE_PROFILE)
        self.assertEqual(good.normalized_repr, "3")
        self.assert_abstained(invalid, ParseStatus.INVALID, ParseReason.SYNTAX)
        self.assertEqual(parse_batch([]).results, ())

    def test_expression_limit_boundaries(self):
        passing = (
            "1".ljust(MAX_CHARS), ("+" * 127) + "1", "(" * 16 + "1" + ")" * 16,
            "1234567890,12", "2^10", "2^−10", "999999999999^10",
        )
        failures = (
            ("1".ljust(MAX_CHARS + 1), ParseReason.LENGTH_LIMIT),
            (("+" * 128) + "1", ParseReason.TOKEN_LIMIT),
            ("(" * 17 + "1" + ")" * 17, ParseReason.NESTING_LIMIT),
            ("12345678901,12", ParseReason.LITERAL_LIMIT),
            ("0" * 13, ParseReason.LITERAL_LIMIT),
            ("2^11", ParseReason.POWER_LIMIT), ("2^−11", ParseReason.POWER_LIMIT),
            ("((999999999999^10)^10)^10", ParseReason.ARITHMETIC_LIMIT),
            ("((1/999999999999)^10)^10", None),
            ("(((1/999999999999)^10)^10)^10", ParseReason.ARITHMETIC_LIMIT),
        )
        items = [ParseInput(text, SCALAR) for text in passing]
        items.extend(ParseInput(text, SCALAR) for text, _ in failures)
        batch = parse_batch(items)
        for result in batch.results[:len(passing)]:
            self.assertEqual(result.parse_status, ParseStatus.OK, result.raw)
        self.assertEqual(batch.results[len(passing) - 1].value.constant, 999999999999 ** 10)
        for result, (text, reason) in zip(batch.results[len(passing):], failures, strict=True):
            with self.subTest(text=text):
                if reason is None:
                    self.assertEqual(result.parse_status, ParseStatus.OK)
                    self.assertEqual(result.value.constant, Fraction(1, 999999999999 ** 100))
                else:
                    self.assert_abstained(result, ParseStatus.UNSUPPORTED, reason)

    def test_batch_step_and_utf8_request_caps(self):
        batch = parse_batch([ParseInput("1", SCALAR)] * MAX_STEPS)
        self.assertEqual(len(batch.results), MAX_STEPS)
        self.assertTrue(all(item.parse_status == ParseStatus.OK for item in batch.results))
        batch = parse_batch([ParseInput("1", SCALAR)] * (MAX_STEPS + 1))
        self.assertEqual((batch.results, batch.rejection), ((), ParseReason.STEP_LIMIT))

        exact = "😀" * (MAX_REQUEST_BYTES // 4)
        batch = parse_batch([ParseInput(exact, None)])
        self.assertEqual(batch.results[0].parse_status, ParseStatus.NOT_REQUIRED)
        batch = parse_batch([ParseInput(exact + "1", None)])
        self.assertEqual((batch.results, batch.rejection), ((), ParseReason.REQUEST_LIMIT))


class IsolatedParserTests(unittest.TestCase):
    def run_worker_fixture(self, code, items):
        launches = []
        real_popen = subprocess.Popen

        def track_process(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            launches.append(process)
            return process

        command = [sys.executable, "-I", "-S", "-B", "-c", code]
        with patch("backend.math_validation.parser._worker_command", return_value=command), \
                patch("backend.math_validation.parser.subprocess.Popen", side_effect=track_process):
            started = monotonic()
            batch = parse_batch(items)
            elapsed = monotonic() - started
        self.assertEqual(len(launches), 1)
        self.assertIsNotNone(launches[0].poll(), "worker survived the parent call")
        return batch, elapsed

    def test_expression_timeout_reaps_a_worker_blocked_mid_frame(self):
        code = "import json, sys, time; json.load(sys.stdin); print('{', end='', flush=True); time.sleep(10)"
        batch, elapsed = self.run_worker_fixture(code, [ParseInput("1", SCALAR)])
        self.assertLess(elapsed, 2)
        self.assertEqual(batch.results[0].parse_status, ParseStatus.UNSUPPORTED)
        self.assertEqual(batch.results[0].reason, ParseReason.TIMEOUT)
        self.assertIsNone(batch.results[0].normalized_repr)
        self.assertEqual(parse_expression("2+2", SCALAR).normalized_repr, "4")

    def test_batch_timeout_stops_work_and_preserves_completed_prefix(self):
        code = """import json, sys, time
for _ in json.load(sys.stdin):
    time.sleep(0.11)
    print('{"terms":[["0","1"]]}', flush=True)
"""
        batch, elapsed = self.run_worker_fixture(code, [ParseInput("1", SCALAR)] * MAX_STEPS)
        self.assertGreater(elapsed, 1.8)
        self.assertLess(elapsed, 3.5)
        completed = sum(result.parse_status == ParseStatus.OK for result in batch.results)
        self.assertGreater(completed, 0)
        self.assertLess(completed, MAX_STEPS)
        for result in batch.results[completed:]:
            self.assertEqual(result.parse_status, ParseStatus.UNSUPPORTED)
            self.assertEqual(result.reason, ParseReason.TIMEOUT)
            self.assertIsNone(result.value)

    def test_worker_crash_is_safe_and_reaped(self):
        code = "import json, sys; json.load(sys.stdin); raise SystemExit(5)"
        batch, _ = self.run_worker_fixture(code, [ParseInput("1", SCALAR)])
        self.assertEqual(batch.results[0].parse_status, ParseStatus.UNSUPPORTED)
        self.assertEqual(batch.results[0].reason, ParseReason.WORKER_FAILURE)
        self.assertIsNone(batch.results[0].value)
