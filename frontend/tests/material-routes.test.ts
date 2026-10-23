import { describe, expect, it } from 'vitest';
import { buildMaterialPath, materialPathForSlug } from '../src/shared/routing/material-routes.mjs';

describe('assigned material URLs', () => {
  it('uses grade, subject and the assigned number without a title or section', () => {
    expect(buildMaterialPath({ grade: 5, subject: 'math', number: 1 })).toBe('/materials/5-math-1');
    expect(buildMaterialPath({ grade: 10, subject: 'algebra', number: 32 })).toBe('/materials/10-algebra-32');
  });
  it('keeps the approved pilot assignment and does not invent URLs for other lessons', () => {
    expect(materialPathForSlug('kvadratichnaya-funkcziya-y-ax2-bx-c')).toBe('/materials/8-algebra-32');
    expect(materialPathForSlug('unassigned-topic')).toBeUndefined();
  });
  it('rejects invalid numbers and subject codes rather than producing ambiguous paths', () => {
    for (const grade of [0, -1, 8.5, Number.NaN]) expect(() => buildMaterialPath({ grade, subject: 'algebra', number: 1 })).toThrow();
    for (const number of [0, -2, 1.5, Number.POSITIVE_INFINITY]) expect(() => buildMaterialPath({ grade: 8, subject: 'algebra', number })).toThrow();
    for (const subject of ['Algebra', '../algebra', 'algebra1', '', 'алгебра']) expect(() => buildMaterialPath({ grade: 8, subject, number: 1 })).toThrow();
  });
});
