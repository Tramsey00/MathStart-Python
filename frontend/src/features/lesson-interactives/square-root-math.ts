import { formatNumber } from '../../shared/lesson/quadratic-math';

export interface SquareRootCoefficients { k: number; a: number }
export const SQUARE_ROOT_TABLE_X = [0, 1, 4, 9, 16] as const;
export const SQUARE_ROOT_WINDOW = { xMin: -2, xMax: 18, yMin: -8, yMax: 8 } as const;

// Domain checks precede evaluation; a negative x must not be clamped to zero.
export function squareRootValue(x: number, { k, a }: SquareRootCoefficients): number | null {
  if (![x, k, a].every(Number.isFinite) || x < 0) return null;
  const y = k * Math.sqrt(x) + a;
  return Number.isFinite(y) ? y : null;
}

export function squareRootFormula({ k, a }: SquareRootCoefficients): string {
  const term = k === 1 ? '√x' : k === -1 ? '−√x' : `${formatNumber(k, 1)}·√x`;
  return `y = ${term}${a > 0 ? ` + ${formatNumber(a, 1)}` : a < 0 ? ` − ${formatNumber(-a, 1)}` : ''}`;
}

export function squareRootProperties({ k, a }: SquareRootCoefficients): [string, string][] {
  const shift = formatNumber(a, 1);
  return [
    ['Область определения', '[0; +∞)'],
    ['Множество значений', k > 0 ? `[${shift}; +∞)` : k < 0 ? `(−∞; ${shift}]` : `{${shift}}`],
    ['Изменение функции', k > 0 ? 'Возрастает' : k < 0 ? 'Убывает' : 'Постоянна'],
    ['Начальная точка', `(0; ${shift})`],
  ];
}

export function squareRootCurve(coefficients: SquareRootCoefficients): [number, number][] {
  const points: [number, number][] = [];
  for (let i = 0; i <= 420; i++) {
    const x = SQUARE_ROOT_WINDOW.xMax * i / 420;
    const y = squareRootValue(x, coefficients);
    if (y !== null) points.push([x, y]);
  }
  return points;
}
