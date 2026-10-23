export interface LinearCoefficients { k: number; b: number }
export const INITIAL_LINEAR: Readonly<LinearCoefficients> = Object.freeze({ k: 1, b: 0 });
export const linearValue = (x: number, { k, b }: LinearCoefficients) => k * x + b;
export const linearNumber = (n: number) => String(Math.round((Object.is(n, -0) ? 0 : n) * 100) / 100).replace('.', ',').replace('-', '−');
export function linearFormula({ k, b }: LinearCoefficients) {
  if (k === 0) return `y = ${linearNumber(b)}`;
  const term = k === 1 ? 'x' : k === -1 ? '−x' : `${linearNumber(k)}x`;
  return `y = ${term}${b > 0 ? ` + ${linearNumber(b)}` : b < 0 ? ` − ${linearNumber(-b)}` : ''}`;
}
export function analyzeLinear({ k, b }: LinearCoefficients): { direction: string; yIntercept: readonly [number, number]; xIntercept: number | 'all' | 'none' } {
  return { direction: k > 0 ? 'возрастает' : k < 0 ? 'убывает' : 'постоянная',
    yIntercept: [0, b] as const,
    xIntercept: k === 0 ? (b === 0 ? 'all' : 'none') : -b / k };
}
