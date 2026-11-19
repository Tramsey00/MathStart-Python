import type { Attempt } from '../../shared/api/attempt-client';
import { dispatchExercise, type PublicExercise } from '../../shared/exercise/dispatcher';

export type Draft = Attempt['draft'];
export type StepType = Exclude<Draft['steps'][number]['step_type'], 'STRUCTURED_FIELDS'>;
export type ExerciseForm = { mode: 'final-answer' } | { mode: 'ordered-steps'; types: StepType[] };

export const emptyDraft: Draft = { payload: {}, steps: [] };
export const maxSteps = 40;
export const maxText = 512;

export const stepLabels: Record<StepType, string> = {
  MATH_EXPRESSION: 'Выражение', EQUATION_STATE: 'Уравнение', FINAL_STATEMENT: 'Итоговый ответ',
};

export function stepField(type: StepType) {
  return type === 'FINAL_STATEMENT' ? 'answer' : 'expression';
}

export function exerciseForm(exercise: PublicExercise): ExerciseForm | null {
  const slot = dispatchExercise(exercise);
  if (slot === 'final-answer') {
    const fields = exercise.input_schema?.fields;
    const field = fields?.[0];
    return fields?.length === 1 && field?.name === 'answer' && field.input_type === 'math_text'
      && field.required && exercise.step_schema === null ? { mode: slot } : null;
  }
  const schema = exercise.step_schema;
  if (slot !== 'ordered-steps' || !schema || exercise.input_schema !== null || schema.serialization
      || schema.step_fields || schema.ordering?.field !== 'step_no' || schema.ordering.direction !== 'ascending') return null;
  const types = schema.allowed_step_types;
  if (types.length !== 2 || !types.includes('FINAL_STATEMENT')) return null;
  const workingType = types.find(type => type === 'MATH_EXPRESSION' || type === 'EQUATION_STATE');
  return workingType ? { mode: slot, types: [workingType, 'FINAL_STATEMENT'] } : null;
}

export function completeDraft(form: ExerciseForm, draft: Draft) {
  if (form.mode === 'final-answer') return typeof draft.payload.answer === 'string' && Boolean(draft.payload.answer.trim());
  return draft.steps.length > 0 && draft.steps.every(step => completeStep(form.types, step));
}

export function completeStep(types: StepType[], step: Draft['steps'][number]) {
  const type = types.find(type => type === step.step_type);
  const value = type && step.payload[stepField(type)];
  return typeof value === 'string' && Boolean(value.trim());
}

export function sameDraft(a: Draft, b: Draft) {
  return samePayload(a.payload, b.payload) && a.steps.length === b.steps.length && a.steps.every((step, index) => {
    const other = b.steps[index];
    return other && step.step_no === other.step_no && step.step_type === other.step_type
      && step.raw_text === other.raw_text && samePayload(step.payload, other.payload);
  });
}

function samePayload(a: Draft['payload'], b: Draft['payload']) {
  const names = Object.keys(a);
  return names.length === Object.keys(b).length && names.every(name => Object.hasOwn(b, name) && a[name] === b[name]);
}
