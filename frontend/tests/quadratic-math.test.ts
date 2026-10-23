import { describe, expect, it } from 'vitest';
import { analyzeFunction, formatNumber, INITIAL_COEFFICIENTS, polynomial, valueAt } from '../src/shared/lesson/quadratic-math';

describe('quadratic lesson mathematics', () => {
  it('retains the authored initial example and table', () => {
    expect(analyzeFunction(INITIAL_COEFFICIENTS)).toEqual({ kind: 'quadratic', discriminant: 4, vertex: [2, -1], roots: [1, 3] });
    expect([-2, 0, 1, 2, 3, 4].map(x => valueAt(x, INITIAL_COEFFICIENTS))).toEqual([15, 3, 0, -1, 0, 3]);
    expect(polynomial(INITIAL_COEFFICIENTS)).toBe('x² − 4x + 3');
  });
  it('orders roots for a negative leading coefficient', () => {
    expect(analyzeFunction({ a: -1, b: -2, c: 3 })).toEqual({ kind: 'quadratic', discriminant: 16, vertex: [-1, 4], roots: [-3, 1] });
  });
  it('distinguishes two, one and no real intersections', () => {
    expect(analyzeFunction({ a: 1, b: 0, c: -2 }).roots).toEqual([-1.414214, 1.414214]);
    expect(analyzeFunction({ a: 1, b: -4, c: 4 }).roots).toEqual([2]);
    expect(analyzeFunction({ a: 1, b: 0, c: 1 }).roots).toEqual([]);
  });
  it('keeps the original linear and constant comparisons at a = 0', () => {
    expect(analyzeFunction({ a: 0, b: 2, c: -4 })).toEqual({ kind: 'linear', roots: [2] });
    expect(analyzeFunction({ a: 0, b: 0, c: 3 })).toEqual({ kind: 'constant', roots: [] });
    expect(analyzeFunction({ a: 0, b: 0, c: 0 })).toEqual({ kind: 'constant', roots: 'all' });
  });
  it('formats signs, decimal coefficients and zero without misleading terms', () => {
    expect(polynomial({ a: -1, b: 0.1, c: -0 })).toBe('−x² + 0,1x');
    expect(polynomial({ a: 0, b: 0, c: 0 })).toBe('0');
    expect(formatNumber(-0)).toBe('0');
    expect(formatNumber(-0.001)).toBe('0');
    expect(formatNumber(1.50)).toBe('1,5');
  });
  it('rejects non-finite coefficients', () => {
    expect(() => analyzeFunction({ a: NaN, b: 0, c: 0 })).toThrow(TypeError);
    expect(() => analyzeFunction({ a: 1, b: Infinity, c: 0 })).toThrow(TypeError);
  });
});
