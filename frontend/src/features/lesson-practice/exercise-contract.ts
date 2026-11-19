import type { Attempt } from '../../shared/api/attempt-client';
import { dispatchExercise, type PublicExercise } from '../../shared/exercise/dispatcher';

export type Draft = Attempt['draft'];
export type StepType = Exclude<Draft['steps'][number]['step_type'], 'STRUCTURED_FIELDS'>;
type StructuredForm = { mode: 'structured-solution'; fields: {name: string; label: string}[] };
export type ExerciseForm = StructuredForm | { mode: 'self-check' } | { mode: 'final-answer' } | { mode: 'ordered-steps'; types: StepType[] };
const structuredFields = [
  ['start', 'displacement', 'end'],
  ['expanded_equation', 'isolated_term_equation', 'solution'],
];

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
  if (slot === 'self-check') return { mode: slot };
  if (slot === 'final-answer') {
    const fields = exercise.input_schema?.fields;
    const field = fields?.[0];
    return fields?.length === 1 && field?.name === 'answer' && field.input_type === 'math_text'
      && field.required && exercise.step_schema === null ? { mode: slot } : null;
  }
  const schema = exercise.step_schema;
  if (slot === 'structured-solution') {
    const fields = exercise.input_schema?.fields;
    const names = fields?.map(field => field.name);
    const parts = schema?.serialization;
    if (!fields || !names || !structuredFields.some(known => sameNames(known, names))
        || fields.some(field => field.input_type !== 'math_text' || !field.required || !field.label)
        || schema?.ordering?.field !== 'step_no' || schema.ordering.direction !== 'ascending'
        || !sameNames(schema.allowed_step_types, ['STRUCTURED_FIELDS', 'FINAL_STATEMENT'])
        || parts?.length !== 2 || parts[0]?.step_type !== 'STRUCTURED_FIELDS'
        || parts[1]?.step_type !== 'FINAL_STATEMENT'
        || !sameNames(parts[0].payload_fields, names.slice(0, 2))
        || !sameNames(parts[1].payload_fields, names.slice(2))) return null;
    return { mode: slot, fields: fields.map(field => ({ name: field.name, label: field.label! })) };
  }
  if (slot !== 'ordered-steps' || !schema || exercise.input_schema !== null || schema.serialization
      || schema.step_fields || schema.ordering?.field !== 'step_no' || schema.ordering.direction !== 'ascending') return null;
  const types = schema.allowed_step_types;
  if (types.length !== 2 || !types.includes('FINAL_STATEMENT')) return null;
  const workingType = types.find(type => type === 'MATH_EXPRESSION' || type === 'EQUATION_STATE');
  return workingType ? { mode: slot, types: [workingType, 'FINAL_STATEMENT'] } : null;
}

function sameNames(a: readonly string[], b: readonly string[]) {
  return a.length === b.length && a.every((value, index) => value === b[index]);
}

export function structuredDraft(form: StructuredForm, payload: Draft['payload']): Draft {
  return { payload, steps: [form.fields.slice(0, 2), form.fields.slice(2)].map((fields, index) => ({
    step_no: index + 1,
    step_type: index === 0 ? 'STRUCTURED_FIELDS' : 'FINAL_STATEMENT',
    payload: Object.fromEntries(fields.filter(({name}) => Object.hasOwn(payload, name)).map(({name}) => [name, payload[name]])),
    raw_text: null,
  })) };
}

export function completeDraft(form: ExerciseForm, draft: Draft) {
  if (form.mode === 'final-answer') return typeof draft.payload.answer === 'string' && Boolean(draft.payload.answer.trim());
  if (form.mode === 'self-check') return false;
  if (form.mode === 'structured-solution') return form.fields.every(({name}) => {
    const value = draft.payload[name];
    return typeof value === 'string' && Boolean(value.trim());
  });
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
