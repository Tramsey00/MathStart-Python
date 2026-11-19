"""Synthetic authoring and private storage contracts for the N008 importer."""

from copy import deepcopy
import unittest
from uuid import UUID

from backend.assessment.analysis import ExerciseValidation, analyze_submission
from backend.assessment.checker_spec import CheckerSpecError
from backend.assessment.package import BankError, EQUATIONS, digest, validate_row, validation_data
from backend.assessment.templates import TEMPLATES
from backend.solution_analyzer.model import SubmittedSolution, SubmittedStep, Verdict


VERSION = UUID(int=7)
ATTEMPT = UUID(int=8)


def equation_row(schema="equation-final-v1", *, answer="2x+6=10", variants=(), checker=None):
    row = {
        "code": "synthetic_equation", "version": 1, "topic": EQUATIONS,
        "schema": schema, "difficulty": 1, "statement": "Synthetic exercise",
        "primary": "equation_balance", "secondary": [], "provenance": "synthetic",
        "answer": answer, "variants": list(variants), "solution": ["synthetic editorial text"],
    }
    if checker is not None:
        row["checker"] = checker
    return row


def v2(mode="TRANSFORMED_EQUATION", *, initial="2(x+3)=10"):
    checker = {"version": 2, "equation_answer_mode": mode}
    if initial is not None:
        checker["initial_state"] = {
            "schema_version": 1, "kind": "EQUATION", "parser_profile": "algebra_linear_v1", "text": initial,
        }
    return checker


def from_row(row):
    private = validation_data(row)
    return ExerciseValidation.from_storage(
        version_id=VERSION, schema_code=row["schema"],
        **{key: value for key, value in private.items() if key != "canonical_solution"},
    )


class EquationCheckerBankTests(unittest.TestCase):
    def test_legacy_validation_payload_and_digest_do_not_change(self):
        row = equation_row(answer="unparsed legacy value", variants=("other legacy text",))
        validate_row(row)
        expected = {
            "checker_type": "equation_state", "checker_version": 1,
            "answer_key": row["answer"], "accepted_variants": row["variants"],
            "validation_spec": {"required_fields": ["answer"], "step_type": None},
            "canonical_solution": row["solution"],
        }
        self.assertEqual(validation_data(row), expected)
        self.assertEqual(digest(validation_data(row)), digest(expected))
        self.assertEqual(from_row(row).checker_version, 1)
        self.assertIsNone(from_row(row).initial_state)

    def test_transform_metadata_round_trips_without_mutating_source_or_public_shape(self):
        row = equation_row(checker=v2(initial=" 2(x+3)=10 "))
        copy = deepcopy(row)
        validate_row(row)
        private = validation_data(row)
        self.assertEqual(row, copy)
        self.assertEqual(private["checker_version"], 2)
        self.assertEqual(private["validation_spec"]["initial_state"], row["checker"]["initial_state"])
        template = TEMPLATES[row["schema"]]
        self.assertNotIn("checker", template.public_contract())
        self.assertNotIn("initial_state", template.public_contract())
        self.assertNotIn("equation_answer_mode", template.public_contract())
        other = deepcopy(row)
        other["checker"]["initial_state"]["text"] = "10=2(x+3)"
        validate_row(other)
        self.assertNotEqual(digest(validation_data(other)), digest(private))
        exercise = from_row(row)
        self.assertEqual(exercise.initial_state, " 2(x+3)=10 ")
        self.assertNotIn("initial_state", exercise.validation_spec)
        good = SubmittedSolution(ATTEMPT, VERSION, {"answer": "10=6+x+x"})
        repeated = SubmittedSolution(ATTEMPT, VERSION, {"answer": "2(x+3)=10"})
        self.assertEqual(analyze_submission(exercise, good).verdict, Verdict.CORRECT)
        result = analyze_submission(exercise, repeated)
        self.assertEqual(result.verdict, Verdict.INDETERMINATE)
        self.assertFalse(result.evidence_refs)

    def test_solution_mode_supports_exact_roots_with_or_without_optional_final_anchor(self):
        for initial in (None, "2(x+3)=10"):
            with self.subTest(stored_anchor=initial is not None):
                row = equation_row(answer="2", variants=("x=4/2",), checker=v2("SOLUTION", initial=initial))
                validate_row(row)
                exercise = from_row(row)
                for answer, verdict in (("6/3", Verdict.CORRECT), ("x=2", Verdict.CORRECT), ("3", Verdict.WRONG)):
                    result = analyze_submission(exercise, SubmittedSolution(ATTEMPT, VERSION, {"answer": answer}))
                    self.assertEqual(result.verdict, verdict)
                    self.assertIsNone(result.misconception_code)

    def test_step_mode_requires_an_anchor_and_uses_the_published_reference(self):
        schema = "equation-steps-v1"
        with self.assertRaisesRegex(BankError, "authored initial state"):
            validate_row(equation_row(schema, answer="2", checker=v2("SOLUTION", initial=None)))
        row = equation_row(schema, answer="2x=4", checker=v2())
        validate_row(row)
        for formula, verdict in (("2x+6=10", Verdict.CORRECT), ("1/x=2", Verdict.UNSUPPORTED)):
            exercise = from_row(row)
            steps = (
                SubmittedStep(UUID(int=1), 1, "EQUATION_STATE", {"expression": formula}),
                SubmittedStep(UUID(int=2), 2, "FINAL_STATEMENT", {"answer": "4=2x"}),
            )
            result = analyze_submission(exercise, SubmittedSolution(ATTEMPT, VERSION, {}, steps))
            self.assertEqual(result.verdict, verdict)
            self.assertEqual(result.final_verdict, Verdict.CORRECT)
            self.assertIsNone(result.misconception_code)

    def test_rejects_unknown_metadata_versions_shapes_and_modes(self):
        valid = v2()
        for checker in (
            None, [], {}, {**valid, "version": True}, {**valid, "version": 1}, {**valid, "version": 3},
            {**valid, "equation_answer_mode": "EQUATION_STATE"}, {**valid, "unexpected": "private_sentinel"},
            {**valid, "initial_state": None}, {**valid, "initial_state": {"text": "private_sentinel"}},
            {**valid, "initial_state": {**valid["initial_state"], "schema_version": True}},
            {**valid, "initial_state": {**valid["initial_state"], "parser_profile": "arithmetic_v1"}},
        ):
            with self.subTest(index=type(checker).__name__), self.assertRaises(BankError) as raised:
                row = equation_row()
                row["checker"] = checker
                validate_row(row)
            self.assertNotIn("private_sentinel", str(raised.exception))
        ordinary = equation_row("integer-final-v1", answer="2", checker=v2("SOLUTION", initial=None))
        with self.assertRaisesRegex(BankError, "supported equation template"):
            validate_row(ordinary)

    def test_rejects_malformed_inconsistent_or_untransformed_references(self):
        for row in (
            equation_row(checker=v2(initial=None)),
            equation_row(checker=v2(initial="private_sentinel")),
            equation_row(checker=v2(initial="2")),
            equation_row(answer="2(x+3)=10", checker=v2()),
            equation_row(answer="2x+7=10", checker=v2()),
            equation_row(variants=("2(x+3)=10",), checker=v2()),
            equation_row(answer="x^2=4", checker=v2()),
            equation_row(answer="3", checker=v2("SOLUTION")),
            equation_row(answer="2", variants=("3",), checker=v2("SOLUTION", initial=None)),
            equation_row(answer="2", variants=("2",) * 40, checker=v2("SOLUTION")),
        ):
            with self.assertRaises(BankError) as raised:
                validate_row(row)
            self.assertNotIn("private_sentinel", str(raised.exception))

    def test_invalid_stored_shape_does_not_become_a_runtime_checker(self):
        private = validation_data(equation_row(checker=v2()))
        stored = {**private["validation_spec"], "unexpected": "private_sentinel"}
        with self.assertRaises(CheckerSpecError) as raised:
            ExerciseValidation.from_storage(
                version_id=VERSION, schema_code="equation-final-v1",
                checker_type="equation_state", checker_version=2, validation_spec=stored, answer_key="2x+6=10",
            )
        self.assertNotIn("private_sentinel", str(raised.exception))
