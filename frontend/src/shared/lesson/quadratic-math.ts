// Numeric/formatting behavior follows the existing quadratic lab, including a = 0.
export const EPSILON = 0.000001;
export type Coefficients = Readonly<{ a: number; b: number; c: number }>;
export const INITIAL_COEFFICIENTS: Coefficients = { a: 1, b: -4, c: 3 };
export const nearZero = (value: number) => Math.abs(value) < EPSILON;
export function cleanNumber(value: number) {
  const rounded = Math.round(value * 1e6) / 1e6;
  return nearZero(rounded) ? 0 : rounded;
}
export function valueAt(x: number, { a, b, c }: Coefficients) { return a * x * x + b * x + c; }
export type FunctionAnalysis =
  | { kind: 'quadratic'; discriminant: number; vertex: readonly [number, number]; roots: readonly number[] }
  | { kind: 'linear'; roots: readonly number[] }
  | { kind: 'constant'; roots: readonly number[] | 'all' };
export function analyzeFunction(coefficients: Coefficients): FunctionAnalysis {
  const { a, b, c } = coefficients;
  if (![a, b, c].every(Number.isFinite)) throw new TypeError('Finite coefficients required');
  if (nearZero(a)) return nearZero(b)
    ? { kind: 'constant', roots: nearZero(c) ? 'all' : [] }
    : { kind: 'linear', roots: [cleanNumber(-c / b)] };
  const discriminant = cleanNumber(b * b - 4 * a * c);
  const x = cleanNumber(-b / (2 * a));
  const roots = discriminant > EPSILON
    ? [cleanNumber((-b - Math.sqrt(discriminant)) / (2 * a)), cleanNumber((-b + Math.sqrt(discriminant)) / (2 * a))].sort((l, r) => l - r)
    : Math.abs(discriminant) <= EPSILON ? [x] : [];
  return { kind: 'quadratic', discriminant, vertex: [x, cleanNumber(valueAt(x, coefficients))], roots };
}
export function formatNumber(value: number, digits = 2): string {
  const rounded = cleanNumber(value).toFixed(digits);
  if (Number(rounded) === 0) return '0';
  return rounded.replace(/(\.\d*?)0+$/, '$1').replace(/\.$/, '').replace('.', ',').replace('-', '−');
}
export function polynomial({ a, b, c }: Coefficients): string {
  const parts: string[] = [];
  for (const [value, variable] of [[a, 'x²'], [b, 'x'], [c, '']] as const) {
    const v = cleanNumber(value);
    if (nearZero(v)) continue;
    const magnitude = variable && nearZero(Math.abs(v) - 1) ? '' : formatNumber(Math.abs(v), 1);
    parts.push(`${parts.length ? (v < 0 ? '− ' : '+ ') : (v < 0 ? '−' : '')}${magnitude}${variable}`);
  }
  return parts.join(' ') || '0';
}
