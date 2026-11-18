"""Pilot v1 public input templates. Field metadata describes input shape only."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Template:
    mode: str
    parser: str | None
    checker: str
    fields: tuple[tuple[str, str], ...] = ()
    step_type: str | None = None

    def public_contract(self):
        input_schema, step_schema = self.schemas()
        return {'input_schema': input_schema, 'step_schema': step_schema, 'parser_profile': self.parser,
                'reveal_policy': {'allowed': True, 'confirmation_required': True},
                'allowed_help_actions': ['REVEAL']}

    def schemas(self):
        fields = [{'name': name, 'label': label, 'input_type': 'math_text', 'required': True}
                  for name, label in self.fields]
        input_schema = {'type': 'object', 'fields': fields} if fields else None
        if not self.step_type:
            return input_schema, None
        step_schema = {
            'type': 'ordered_steps', 'allowed_step_types': [self.step_type, 'FINAL_STATEMENT'],
            'ordering': {'field': 'step_no', 'direction': 'ascending'},
        }
        if self.mode == 'STRUCTURED_SOLUTION':
            names = [name for name, _ in self.fields]
            step_schema['serialization'] = [
                {'step_type': self.step_type, 'payload_fields': names[:-1]},
                {'step_type': 'FINAL_STATEMENT', 'payload_fields': names[-1:]},
            ]
        return input_schema, step_schema


ANSWER = (('answer', 'Ответ'),)
TEMPLATES = {
    'self-check-v1': Template('SELF_CHECK', None, 'display_only'),
    'integer-final-v1': Template('FINAL_ANSWER', 'arithmetic_v1', 'integer_exact', ANSWER),
    'equation-final-v1': Template('FINAL_ANSWER', 'algebra_linear_v1', 'equation_state', ANSWER),
    'expression-final-v1': Template('FINAL_ANSWER', 'algebra_linear_v1', 'linear_expression', ANSWER),
    'arithmetic-steps-v1': Template('STEP_BY_STEP', 'arithmetic_v1', 'integer_transitions',
                                  step_type='MATH_EXPRESSION'),
    'expression-steps-v1': Template('STEP_BY_STEP', 'algebra_linear_v1', 'expression_transitions',
                                  step_type='MATH_EXPRESSION'),
    'equation-steps-v1': Template('STEP_BY_STEP', 'algebra_linear_v1', 'equation_transitions',
                                step_type='EQUATION_STATE'),
    'coordinate-move-v1': Template('STRUCTURED_SOLUTION', 'arithmetic_v1', 'coordinate_move_fields', (
        ('start', 'Начальная координата'), ('displacement', 'Перемещение со знаком'),
        ('end', 'Конечная координата'),
    ), 'STRUCTURED_FIELDS'),
    'equation-parentheses-v1': Template('STRUCTURED_SOLUTION', 'algebra_linear_v1', 'linear_parentheses_fields', (
        ('expanded_equation', 'Уравнение после раскрытия скобок'),
        ('isolated_term_equation', 'Уравнение после переноса'),
        ('solution', 'Значение x'),
    ), 'STRUCTURED_FIELDS'),
}
DIFFICULTY_BANDS = {1: 'easy', 2: 'easy', 3: 'medium', 4: 'hard'}
