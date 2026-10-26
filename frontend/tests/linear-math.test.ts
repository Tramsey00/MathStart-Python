import { describe, expect, it } from 'vitest';
import { analyzeLinear, INITIAL_LINEAR, linearFormula, linearNumber, linearValue } from '../src/features/lesson-interactives/linear-math';
describe('linear function mathematics', () => {
  it('retains the authored initial line and handles both slope directions', () => {
    expect(linearFormula(INITIAL_LINEAR)).toBe('y = x');
    expect(linearValue(4, { k: 3, b: -2 })).toBe(10);
    expect(analyzeLinear({ k: -2, b: 4 })).toEqual({ direction: 'убывает', yIntercept: [0, 4], xIntercept: 2 });
    expect(analyzeLinear({ k: 0.5, b: -3 }).xIntercept).toBe(6);
  });
  it('distinguishes a constant line from the coincident x axis', () => {
    expect(analyzeLinear({ k: 0, b: 1 }).xIntercept).toBe('none');
    expect(analyzeLinear({ k: 0, b: 0 }).xIntercept).toBe('all');
    expect(linearFormula({ k: 0, b: 0 })).toBe('y = 0');
    expect(linearFormula({ k: -1, b: -0.5 })).toBe('y = −x − 0,5');
    expect(linearNumber(-0)).toBe('0');
  });
});
