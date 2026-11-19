"""Offline N011 goldens and safety checks through the Assessment entry point."""

from dataclasses import replace
import json
from pathlib import Path
import sys
from time import monotonic
import unittest
from unittest.mock import patch
from uuid import UUID

from backend.assessment.analysis import ExerciseValidation, analyze_submission
from backend.assessment.templates import TEMPLATES
from backend.knowledge.graph import graph_from_package
from backend.math_validation.model import ParseInput, ParseReason, ParseResult, ParseStatus
from backend.math_validation.parser import _worker_command, parse_batch
from backend.math_validation.profiles import MAX_STEPS
from backend.math_validation.validators import Check, Form, Rule, compare
from backend.solution_analyzer.model import (
    RULE_TAXONOMY, AnalysisResult, Classification, EvidenceKind, EvidenceRef,
    SubmittedSolution, SubmittedStep, Verdict,
)


ROOT = Path(__file__).resolve().parents[1]
ATTEMPT = UUID(int=100)
VERSION = UUID(int=200)
EQ = "equation-steps-v1"
ARITH = "arithmetic-steps-v1"
EXPR = "expression-steps-v1"
DIST = frozenset({"distributive_property"})


def read_fixture(path):
    return json.loads((ROOT / "specs" / path).read_text(encoding="utf-8"))


GRAPH = graph_from_package(read_fixture("knowledge/fixtures/pilot-skills-v1.json"),
                           read_fixture("knowledge/fixtures/pilot-dependencies-v1.json"))


def exercise(schema, key, *, initial=None, skills=(), variants=()):
    template = TEMPLATES[schema]
    return ExerciseValidation(
        VERSION, schema, template.checker, 1,
        {"required_fields": [name for name, _ in template.fields], "step_type": template.step_type},
        key, tuple(variants), frozenset(skills), initial,
    )


def attempt(schema, answer, steps=()):
    template = TEMPLATES[schema]
    if isinstance(answer, dict):
        names = [name for name, _ in template.fields]
        steps = (SubmittedStep(UUID(int=1), 1, "STRUCTURED_FIELDS", {n: answer[n] for n in names[:-1]}),
                 SubmittedStep(UUID(int=2), 2, "FINAL_STATEMENT", {names[-1]: answer[names[-1]]}))
        return SubmittedSolution(ATTEMPT, VERSION, answer, steps)
    typed_steps = tuple(SubmittedStep(UUID(int=i), i, template.step_type, {"expression": text})
                        for i, text in enumerate(steps, 1))
    if template.mode == "STEP_BY_STEP":
        if answer is not None:
            number = len(typed_steps) + 1
            typed_steps += (SubmittedStep(UUID(int=number), number, "FINAL_STATEMENT", {"answer": answer}),)
        return SubmittedSolution(ATTEMPT, VERSION, {}, typed_steps)
    return SubmittedSolution(ATTEMPT, VERSION, {"answer": answer})


class DeterministicAnalysisTests(unittest.TestCase):
    def assert_neutral(self, result, verdict):
        self.assertEqual(result.verdict, verdict)
        self.assertIsNone(result.first_error_step_id)
        self.assertIsNone(result.misconception_code)
        self.assertEqual(result.skill_codes, ())
        self.assertEqual(result.evidence_refs, ())
        self.assertEqual(result.confidence, 0)

    def test_golden_matrix(self):
        fixture = read_fixture("exercises/analysis/deterministic-analysis-v1.json")
        for case in fixture["cases"]:
            with self.subTest(case=case["id"]):
                schema = case["schema"]
                result = analyze_submission(
                    exercise(schema, case["key"], initial=case.get("initial"), skills=case.get("skills", ())),
                    attempt(schema, case["answer"], case.get("steps", ())), graph=GRAPH,
                )
                self.assertEqual(result.schema_version, fixture["schema_version"])
                self.assertEqual(result.verdict, case["verdict"])
                self.assertEqual(result.final_verdict, case.get("final_verdict", case["verdict"]))
                self.assertEqual(result.prefix_status, case.get("prefix"))
                self.assertEqual(result.misconception_code, case.get("code"))
                for attribute, key in (("first_error_step_id", "first_error"), ("blocking_step_id", "blocked_at")):
                    expected = UUID(int=case[key]) if key in case else None
                    self.assertEqual(getattr(result, attribute), expected)
                if result.verdict in (Verdict.INDETERMINATE, Verdict.UNSUPPORTED):
                    self.assert_neutral(result, result.verdict)

    def test_exact_comparisons_and_no_all_solution_distinction(self):
        texts = ("1/3", "2/6", "0,33333333333", "x/2+0,5x", "x",
                 "2x+3=1", "-x=1", "x=x", "2=2", "x=x+1", "3=4")
        parsed = dict(zip(texts, parse_batch(tuple(ParseInput(text, "algebra_linear_v1") for text in texts)).results,
                          strict=True))
        for left, right, form in (
            ("1/3", "2/6", Form.SCALAR), ("x/2+0,5x", "x", Form.EXPRESSION),
            ("2x+3=1", "-x=1", Form.EQUATION), ("x=x", "2=2", Form.EQUATION),
            ("x=x+1", "3=4", Form.EQUATION),
        ):
            with self.subTest(left=left, right=right):
                self.assertEqual(compare(parsed[left], parsed[right], form), Check.VALID)
        self.assertEqual(compare(parsed["1/3"], parsed["0,33333333333"], Form.SCALAR), Check.WRONG)
        self.assertEqual(compare(parsed["x=x"], parsed["x=x+1"], Form.EQUATION), Check.WRONG)

    def test_final_equation_form_and_accepted_variants(self):
        schema = "equation-final-v1"
        solved = exercise(schema, "x=2")
        self.assertEqual(analyze_submission(solved, attempt(schema, "4/2")).verdict, Verdict.CORRECT)
        self.assert_neutral(analyze_submission(solved, attempt(schema, "2x=4")), Verdict.UNSUPPORTED)
        equation_only = exercise(schema, "2x=4")
        self.assertEqual(analyze_submission(equation_only, attempt(schema, "x+5=7")).verdict, Verdict.CORRECT)
        self.assert_neutral(analyze_submission(equation_only, attempt(schema, "2")), Verdict.UNSUPPORTED)
        state = exercise(schema, "2x=4", variants=("2",))
        self.assertEqual(analyze_submission(state, attempt(schema, "x+5=7")).verdict, Verdict.CORRECT)
        self.assertEqual(analyze_submission(state, attempt(schema, "2")).verdict, Verdict.CORRECT)
        integer = exercise("integer-final-v1", "15", variants=("20",))
        self.assertEqual(analyze_submission(integer, attempt("integer-final-v1", "40/2")).verdict, Verdict.CORRECT)

    def test_first_error_with_verified_predecessor_and_correct_final(self):
        config = exercise(EQ, "2", initial="2(x+3)=10", skills={"equation_balance"})
        submitted = attempt(EQ, "2", ["2x+6=10", "(2x+6)-6=10", "2x+50=3", "x=2"])
        result = analyze_submission(config, submitted, graph=GRAPH)
        self.assertEqual((result.verdict, result.final_verdict), (Verdict.WRONG, Verdict.CORRECT))
        self.assertEqual(result.first_error_step_id, UUID(int=2))
        self.assertEqual(result.misconception_code, Classification.EQUATION_BALANCE)
        self.assertEqual(result.evidence_refs, (
            EvidenceRef(EvidenceKind.TRANSITION, ATTEMPT, VERSION, UUID(int=2), UUID(int=1),
                        rule=Rule.ADD_TO_BOTH_SIDES),
        ))
        self.assertEqual(result.confidence, 1)

    def test_first_generic_error_prevents_later_rule_diagnosis(self):
        config = exercise(EQ, "2", initial="2(x+3)=10", skills={"equation_balance", *DIST})
        submitted = attempt(EQ, "5", ["2x+7=10", "(2x+7)-7=10", "x=5"])
        result = analyze_submission(config, submitted, graph=GRAPH)
        self.assertEqual(result.first_error_step_id, UUID(int=1))
        self.assertEqual(result.classification, Classification.OTHER)
        self.assertIsNone(result.misconception_code)
        self.assertEqual(len(result.evidence_refs), 1)
        self.assertIsNone(result.evidence_refs[0].rule)

    def test_wrong_final_after_correct_trace_has_final_evidence_only(self):
        config = exercise(EQ, "2", initial="2(x+3)=10", skills=DIST)
        result = analyze_submission(config, attempt(EQ, "7", ["2x+6=10", "2x=4"]), graph=GRAPH)
        self.assertEqual((result.verdict, result.prefix_status), (Verdict.WRONG, Check.VALID))
        self.assertIsNone(result.misconception_code)
        self.assertIsNone(result.first_error_step_id)
        self.assertEqual(result.evidence_refs,
                         (EvidenceRef(EvidenceKind.FINAL_ANSWER, ATTEMPT, VERSION, step_id=UUID(int=3)),))

    def test_explicit_final_statement_and_ambiguous_order(self):
        config = exercise(ARITH, "1/3", initial="1/2-1/6")
        submitted = attempt(ARITH, "3/9", ["1/3"])
        good = analyze_submission(config, submitted)
        self.assertEqual(good.verdict, Verdict.CORRECT)
        conflict = SubmittedStep(UUID(int=3), 3, "FINAL_STATEMENT", {"answer": "1/2"})
        unknown = analyze_submission(config, replace(submitted, steps=(*submitted.steps, conflict)))
        self.assert_neutral(unknown, Verdict.INDETERMINATE)
        self.assertEqual(unknown.blocking_step_id, UUID(int=2))
        self.assertEqual(unknown.final_verdict, Verdict.INDETERMINATE)
        sole_final = analyze_submission(config, attempt(ARITH, "1/3"))
        self.assert_neutral(sole_final, Verdict.INDETERMINATE)
        self.assertEqual(sole_final.final_verdict, Verdict.CORRECT)

    def test_frozen_r02_step_and_n009_empty_top_level_payload(self):
        exchange = read_fixture("exercises/fixtures/step-submission.exchange-v1.json")
        frozen_step = exchange["request"]["submitted_step"]
        config = ExerciseValidation(
            VERSION, EQ, "equation_transitions", 1, {"required_fields": [], "step_type": "EQUATION_STATE"},
            "x=2", initial_state="2(x+3)=10",
        )
        step = SubmittedStep(UUID(int=1), frozen_step["step_no"], frozen_step["step_type"],
                             frozen_step["payload"], frozen_step["raw_text"])
        submitted = SubmittedSolution(ATTEMPT, VERSION, {}, (step,))
        result = analyze_submission(config, submitted)
        self.assert_neutral(result, Verdict.INDETERMINATE)
        self.assertEqual(result.prefix_status, Check.VALID)
        self.assertEqual(result.final_verdict, Verdict.INDETERMINATE)
        final = SubmittedStep(UUID(int=2), 2, "FINAL_STATEMENT", {"answer": "4/2"})
        self.assertEqual(analyze_submission(config, replace(submitted, steps=(step, final))).verdict, Verdict.CORRECT)
        self.assert_neutral(analyze_submission(config, replace(submitted, payload={"answer": "2"})),
                            Verdict.INDETERMINATE)

    def test_taxonomy_bindings_and_observable_operations(self):
        known = {node.code for node in GRAPH.skills if node.active}
        self.assertTrue({skill for _, skill in RULE_TAXONOMY.values()} <= known)
        cases = (
            (ARITH, "5-(-2)", "5-2", "7", Rule.SUBTRACT_NEGATIVE),
            (ARITH, "5+(-2)", "5+2", "3", Rule.ADD_NEGATIVE),
            (ARITH, "-3*4", "12", "-12", Rule.MULTIPLY_SIGN),
            (ARITH, "12/(-3)", "4", "-4", Rule.DIVIDE_SIGN),
            (EXPR, "2(x-5)", "2x-5", "2x-10", Rule.DISTRIBUTE_TO_BOTH_TERMS),
            (EXPR, "2x+3", "5x", "2x+3", Rule.COMBINE_ONLY_LIKE_TERMS),
            (EQ, "x+3=7", "(x+3)-3=7", "4", Rule.ADD_TO_BOTH_SIDES),
        )
        for schema, start, step, key, rule in cases:
            with self.subTest(rule=rule):
                code, skill = RULE_TAXONOMY[rule]
                result = analyze_submission(exercise(schema, key, initial=start, skills={skill}),
                                            attempt(schema, key, [step]), graph=GRAPH)
                self.assertEqual(result.misconception_code, code)
                self.assertEqual(result.skill_codes, (skill,))
                self.assertEqual(result.evidence_refs[0].rule, rule)
                self.assertIsNone(result.evidence_refs[0].previous_step_id)

    def test_safety_matrix_has_zero_false_strong_negatives(self):
        eq = exercise(EQ, "2", initial="2(x+3)=10", skills=DIST)
        trace = attempt(EQ, "3", ["2x+3=10"])
        collected = []

        def safe(config, submission, verdict, graph=GRAPH):
            result = analyze_submission(config, submission, graph=graph)
            self.assertEqual(result.verdict, verdict)
            collected.append(result)
            return result

        for text, verdict in (
            ("x^2=4", Verdict.UNSUPPORTED), ("1/x=4", Verdict.UNSUPPORTED),
            ("2^11=4", Verdict.UNSUPPORTED), ("2+=", Verdict.INDETERMINATE),
            ("__import__('x')", Verdict.INDETERMINATE), ("2".ljust(513), Verdict.UNSUPPORTED),
        ):
            with self.subTest(text=text[:18]):
                result = safe(eq, attempt(EQ, "3", [text, "2x+3=10"]), verdict)
                self.assertIsNone(result.first_error_step_id)
                self.assertEqual(result.evidence_refs, ())
        for skills in (frozenset(), frozenset({"expand_parentheses"}), frozenset({"basic_arithmetic"}),
                       frozenset({"distributive_property", "client_rule"})):
            result = safe(replace(eq, skill_codes=skills), trace, Verdict.WRONG)
            self.assertEqual(result.classification, Classification.OTHER)
        safe(eq, trace, Verdict.WRONG, graph=None)
        disabled_graph = replace(GRAPH, skills=tuple(
            replace(node, active=False) if node.code in DIST else node for node in GRAPH.skills
        ))
        safe(eq, trace, Verdict.WRONG, graph=disabled_graph)
        safe(replace(eq, initial_state=None), trace, Verdict.INDETERMINATE)
        safe(replace(eq, initial_state="x=3"), trace, Verdict.INDETERMINATE)
        safe(replace(eq, accepted_variants=("sqrt(4)",)), trace, Verdict.INDETERMINATE)
        safe(replace(eq, checker_type="unknown"), trace, Verdict.UNSUPPORTED)
        safe(replace(eq, validation_spec={"rule": "fake"}), trace, Verdict.INDETERMINATE)
        safe(eq, replace(trace, exercise_version_id=UUID(int=999)), Verdict.INDETERMINATE)
        safe(eq, replace(trace, attempt_id=UUID(int=0)), Verdict.INDETERMINATE)
        repeated = replace(trace.steps[0], step_no=3)
        safe(eq, replace(trace, steps=(*trace.steps, repeated)), Verdict.INDETERMINATE)
        fake_step = replace(trace.steps[0], payload={"expression": "2x+3=10", "rule": "fake"})
        safe(eq, replace(trace, steps=(fake_step,)), Verdict.INDETERMINATE)
        unknown_step = replace(trace.steps[0], step_type="UNKNOWN_OPERATION")
        later = replace(trace.steps[0], step_id=UUID(int=2), step_no=2)
        unsupported = safe(eq, replace(trace, steps=(unknown_step, later)), Verdict.INDETERMINATE)
        self.assertEqual(unsupported.blocking_step_id, UUID(int=1))
        safe(exercise(EXPR, "5x", initial="2x+3x", skills={"combine_like_terms"}),
             attempt(EXPR, "6x", ["6x"]), Verdict.WRONG)
        safe(exercise(ARITH, "5", initial="2+3", skills={"sign_rules_add_sub"}),
             attempt(ARITH, "6", ["6"]), Verdict.INDETERMINATE)
        safe(exercise(EQ, "4", initial="x+3=7", skills={"equation_balance"}),
             attempt(EQ, "7", ["x=7"]), Verdict.WRONG)
        self.assertEqual(len(collected), 25)
        self.assertEqual(sum(result.misconception_code is not None for result in collected), 0)
        self.assertTrue(all(result.skill_codes == () for result in collected))

    def test_result_shape_rejects_inconsistent_references(self):
        config = exercise(EQ, "2", initial="2(x+3)=10", skills=DIST)
        submitted = attempt(EQ, "5", ["2x+3=10", "x=5"])
        result = analyze_submission(config, submitted, graph=GRAPH)
        ref = result.evidence_refs[0]
        self.assertTrue(ref.belongs_to(submitted))
        for wrong_ref in (
            replace(ref, step_id=UUID(int=999)),
            replace(ref, attempt_id=UUID(int=999)),
            replace(ref, exercise_version_id=UUID(int=999)),
            replace(ref, step_id=UUID(int=2)),
            replace(ref, previous_step_id=UUID(int=2)),
        ):
            self.assertFalse(wrong_ref.belongs_to(submitted))
        for changes in (
            {"skill_codes": ("basic_arithmetic",)}, {"classification": Classification.ARITHMETIC_ERROR},
            {"evidence_refs": ()}, {"evidence_refs": (ref, ref)}, {"prefix_status": Check.UNKNOWN},
            {"evidence_refs": (replace(ref, rule=Rule.ADD_TO_BOTH_SIDES),)},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace(result, **changes)
        with self.assertRaises(ValueError):
            replace(ref, previous_step_id=ref.step_id)
        with self.assertRaises(ValueError):
            replace(ref, rule="future_rule")
        with self.assertRaises(ValueError):
            AnalysisResult(Verdict.INDETERMINATE, classification=Classification.SIGN_ERROR)

    def test_safe_feedback_uses_no_answer_key_or_student_prose(self):
        cfg = exercise("integer-final-v1", "93822717")
        wrong = analyze_submission(cfg, attempt("integer-final-v1", "5"))
        self.assertNotIn("93822717", wrong.safe_feedback)
        cfg = exercise(EQ, "2", initial="2(x+3)=10", skills=DIST)
        draft = attempt(EQ, "5", ["2x+3=10"])
        submitted = replace(draft, steps=(replace(draft.steps[0], raw_text="<script>private</script>"), draft.steps[1]))
        result = analyze_submission(cfg, submitted, graph=GRAPH)
        self.assertEqual(result.misconception_code, Classification.DISTRIBUTIVE_PROPERTY)
        self.assertNotIn("private", result.safe_feedback)
        self.assertNotIn("2x+3", result.safe_feedback)

    def test_structured_coordinate_and_variant_integrity(self):
        schema = "coordinate-move-v1"
        key = {"start": "-2", "displacement": "3", "end": "1"}
        variant = {"start": "1", "displacement": "1", "end": "2"}
        config = exercise(schema, key, variants=(variant,))
        self.assertEqual(analyze_submission(config, attempt(schema, {
            "start": "−4/2", "displacement": "+3", "end": "2/2",
        })).verdict, Verdict.CORRECT)
        mismatch = analyze_submission(config, attempt(schema, {**key, "displacement": "4"}))
        self.assertEqual(mismatch.first_error_step_id, UUID(int=1))
        self.assertEqual(mismatch.evidence_refs[0].field_name, "displacement")
        self.assertEqual(mismatch.evidence_refs[0].kind, EvidenceKind.STRUCTURED_FIELD)
        self.assertIsNone(mismatch.misconception_code)
        mixed = analyze_submission(config, attempt(schema, {**key, "end": "2"}))
        self.assertEqual(mixed.verdict, Verdict.WRONG)
        self.assertEqual(mixed.final_verdict, Verdict.CORRECT)
        self.assertIsNone(mixed.misconception_code)
        self.assert_neutral(analyze_submission(config, attempt(schema, {**key, "start": "2+"})),
                            Verdict.INDETERMINATE)
        broken_key = exercise(schema, {**key, "end": "2"})
        self.assert_neutral(analyze_submission(broken_key, attempt(schema, key)), Verdict.INDETERMINATE)

    def test_structured_equations_and_serialization(self):
        schema = "equation-parentheses-v1"
        key = {"expanded_equation": "2x+6=10", "isolated_term_equation": "2x=4", "solution": "2"}
        config = exercise(schema, key)
        best = {"expanded_equation": "10=3+3+x+x", "isolated_term_equation": "4=2x", "solution": "x=4/2"}
        self.assertEqual(analyze_submission(config, attempt(schema, best)).verdict, Verdict.CORRECT)
        for field, text, verdict in (
            ("expanded_equation", "2(x+3)=10", Verdict.UNSUPPORTED),
            ("isolated_term_equation", "2x+6=10", Verdict.INDETERMINATE),
        ):
            with self.subTest(field=field):
                result = analyze_submission(config, attempt(schema, {**key, field: text}))
                self.assert_neutral(result, verdict)
                self.assertEqual(result.blocking_step_id, UUID(int=1))
        bad = analyze_submission(config, attempt(schema, {**key, "isolated_term_equation": "2x=5"}))
        self.assertEqual(bad.evidence_refs[0].field_name, "isolated_term_equation")
        self.assertIsNone(bad.misconception_code)
        snapshot = attempt(schema, best)
        conflict = replace(snapshot.steps[0], payload={**snapshot.steps[0].payload, "expanded_equation": "x=2"})
        self.assert_neutral(analyze_submission(config, replace(snapshot, steps=(conflict, snapshot.steps[1]))),
                            Verdict.INDETERMINATE)

    def test_structured_balance_accepts_reviewed_intermediate_before_x_is_isolated(self):
        schema = "equation-parentheses-v1"
        # Synthetic analogues. Both approved intermediate states are equivalent
        # to the original but still have a constant beside the variable term.
        for initial, key, answer in (
            (
                "3(x-1)=x+5",
                {"expanded_equation": "3x-3=x+5", "isolated_term_equation": "2x-3=5", "solution": "4"},
                {"expanded_equation": "x+5=3x-3", "isolated_term_equation": "5=3x-3-x", "solution": "8/2"},
            ),
            (
                "2(x+3)=4x-2",
                {"expanded_equation": "2x+6=4x-2", "isolated_term_equation": "6=2x-2", "solution": "4"},
                {"expanded_equation": "x+x+6=4x-2", "isolated_term_equation": "4x-2-2x=12/2", "solution": "x=4"},
            ),
        ):
            with self.subTest(initial=initial):
                result = analyze_submission(exercise(schema, key, initial=initial), attempt(schema, answer))
                self.assertEqual((result.verdict, result.final_verdict, result.prefix_status),
                                 (Verdict.CORRECT, Verdict.CORRECT, Check.VALID))

    def test_structured_balance_requires_each_stage_and_keeps_approved_variants_together(self):
        schema = "equation-parentheses-v1"
        initial = "3x-3=x+5"
        key = {"expanded_equation": "3x=x+8", "isolated_term_equation": "2x=8", "solution": "4"}
        variant = {"expanded_equation": "3x-8=x", "isolated_term_equation": "2x-8=0", "solution": "x=4"}
        config = exercise(schema, key, initial=initial, variants=(variant,))
        self.assertEqual(analyze_submission(config, attempt(schema, variant)).verdict, Verdict.CORRECT)
        unsafe = (
            {**key, "expanded_equation": initial},
            {**key, "isolated_term_equation": initial},
            {**key, "isolated_term_equation": key["expanded_equation"]},
            {**key, "isolated_term_equation": variant["isolated_term_equation"]},
            {**key, "expanded_equation": "x=4", "isolated_term_equation": "x=4"},
            {**key, "isolated_term_equation": "4x=16"},
        )
        for answer in unsafe:
            with self.subTest(answer=answer):
                result = analyze_submission(config, attempt(schema, answer))
                self.assert_neutral(result, Verdict.INDETERMINATE)
                self.assertEqual(result.final_verdict, Verdict.CORRECT)
        # Even a degenerate trusted key cannot turn copying the same state
        # into completion of two distinct required stages.
        copy = unsafe[4]
        self.assert_neutral(analyze_submission(exercise(schema, copy), attempt(schema, copy)),
                            Verdict.INDETERMINATE)
        repeated_key = {"expanded_equation": initial, "isolated_term_equation": "2x=8", "solution": "4"}
        self.assert_neutral(analyze_submission(exercise(schema, repeated_key, initial=initial),
                                              attempt(schema, repeated_key)), Verdict.INDETERMINATE)

    def test_equation_trace_restatement_alone_is_not_a_transformation(self):
        config = exercise(EQ, "4", initial="3x-3=x+5")
        restated = ["3x-3=x+5", "5+x=3x-3"]
        result = analyze_submission(config, attempt(EQ, "4", restated))
        self.assert_neutral(result, Verdict.INDETERMINATE)
        self.assertEqual(result.final_verdict, Verdict.CORRECT)
        solved = analyze_submission(config, attempt(EQ, "4", [*restated, "2x-3=5", "2x=8"]))
        self.assertEqual(solved.verdict, Verdict.CORRECT)
        like_terms = exercise(EQ, "4", initial="2x+x=12")
        self.assertEqual(analyze_submission(like_terms, attempt(EQ, "4", ["3x=12"])).verdict,
                         Verdict.CORRECT)

    def test_unscoped_arithmetic_fragment_stops_localization(self):
        for initial, part, next_state, key in (
            ("(-3)*4*5", "(-3)*4", "(-12)*5", "-60"),
            ("24/(-2)/3", "-12", "(-12)/3", "-4"),
        ):
            with self.subTest(initial=initial):
                config = exercise(ARITH, key, initial=initial, skills={"sign_rules_mul_div"})
                result = analyze_submission(config, attempt(ARITH, key, [part, "12*5", next_state]), graph=GRAPH)
                self.assert_neutral(result, Verdict.INDETERMINATE)
                self.assertEqual(result.blocking_step_id, UUID(int=1))
                self.assertEqual(result.final_verdict, Verdict.CORRECT)
                full = analyze_submission(config, attempt(ARITH, key, [next_state, key]), graph=GRAPH)
                self.assertEqual(full.verdict, Verdict.CORRECT)
        config = exercise(ARITH, "-60", initial="(-3)*4*5", skills={"sign_rules_mul_div"})
        typed_as_equation = analyze_submission(config, attempt(ARITH, "60", ["(-3)*4=-12"]), graph=GRAPH)
        self.assert_neutral(typed_as_equation, Verdict.UNSUPPORTED)
        self.assertEqual(typed_as_equation.final_verdict, Verdict.WRONG)

    def test_parser_statuses_have_no_deterministic_wrong(self):
        expected = ParseResult("2", "arithmetic_v1", ParseStatus.OK)
        for status, reason, check in (
            (ParseStatus.INVALID, ParseReason.SYNTAX, Check.UNKNOWN),
            (ParseStatus.NOT_REQUIRED, None, Check.UNKNOWN),
            (ParseStatus.UNSUPPORTED, ParseReason.TIMEOUT, Check.UNSUPPORTED),
            (ParseStatus.UNSUPPORTED, ParseReason.WORKER_FAILURE, Check.UNKNOWN),
        ):
            with self.subTest(status=status, reason=reason):
                parsed = ParseResult(None, "arithmetic_v1", status, reason=reason)
                actual_key = parse_batch((ParseInput("2", "arithmetic_v1"),)).results[0]
                self.assertEqual(compare(parsed, actual_key, Form.SCALAR), check)
                self.assertEqual(compare(parsed, expected, Form.SCALAR), Check.UNKNOWN)

    def test_step_and_batch_limits(self):
        config = exercise(ARITH, "2", initial="2")
        steps = ["2" + ("+0" * i) for i in range(MAX_STEPS)]
        self.assertEqual(analyze_submission(config, attempt(ARITH, "1+1", steps[:-1])).verdict, Verdict.CORRECT)
        prefix = analyze_submission(config, attempt(ARITH, None, steps))
        self.assert_neutral(prefix, Verdict.INDETERMINATE)
        self.assertEqual(prefix.prefix_status, Check.VALID)
        self.assert_neutral(analyze_submission(config, attempt(ARITH, "2", steps)),
                            Verdict.UNSUPPORTED)

    def test_expired_parser_process_yields_neutral_result(self):
        command = [sys.executable, "-I", "-S", "-B", "-c", "import time; time.sleep(10)"]
        config = exercise("integer-final-v1", "2")
        with patch("backend.math_validation.parser._worker_command", side_effect=(_worker_command(), command)):
            start = monotonic()
            result = analyze_submission(config, attempt("integer-final-v1", "3"))
        self.assertLess(monotonic() - start, 2.5)
        self.assert_neutral(result, Verdict.UNSUPPORTED)
