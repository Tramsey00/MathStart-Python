import { formatNumber } from '../../shared/lesson/quadratic-math';

export interface HyperbolaCoefficients { k: number; b: number }
export const HYPERBOLA_TABLE_X = [-4, -2, -1, 1, 2, 4] as const;
export const HYPERBOLA_WINDOW = { xMin: -10, xMax: 10, yMin: -10, yMax: 10 } as const;

export function hyperbolaValue(x: number, { k, b }: HyperbolaCoefficients): number | null {
  // No epsilon exclusion: every finite nonzero x belongs to the domain, even for k = 0.
  if (![x, k, b].every(Number.isFinite) || x === 0) return null;
  const y = k / x + b;
  return Number.isFinite(y) ? y : null;
}

export function hyperbolaFormula({ k, b }: HyperbolaCoefficients): string {
  if (k === 0) return `y = ${formatNumber(b, 1)}, x ≠ 0`;
  return `y = ${formatNumber(k, 1)}/x${b > 0 ? ` + ${formatNumber(b, 1)}` : b < 0 ? ` − ${formatNumber(-b, 1)}` : ''}`;
}

export function hyperbolaProperties({ k, b }: HyperbolaCoefficients): [string, string][] {
  const shift = formatNumber(b, 1);
  return [
    ['Область определения', 'x ≠ 0'],
    ['Множество значений', k === 0 ? `{${shift}}` : `y ≠ ${shift}`],
    ['Изменение функции', k === 0 ? 'Постоянна на каждом промежутке области определения'
      : k > 0 ? 'Убывает на (−∞; 0) и (0; +∞)' : 'Возрастает на (−∞; 0) и (0; +∞)'],
    // The agreed k = 0 correction: x = 0 is a hole, not a vertical asymptote.
    [k === 0 ? 'Выколотая точка' : 'Асимптоты', k === 0 ? `(0; ${shift})` : `x = 0, y = ${shift}`],
    ['Расположение ветвей', k === 0 ? `Прямая y = ${shift} без точки (0; ${shift})`
      : k > 0 ? 'I и III четверти относительно центра' : 'II и IV четверти относительно центра'],
    ['Центр симметрии', `(0; ${shift})`],
  ];
}

/** Clip the two monotone branches analytically to the source window.
 * The endpoints come from y = ±10, not an arbitrary exclusion around x = 0.
 * The constant case is drawn separately with an open point by HyperbolaGraph.
 */
export function hyperbolaBranches({ k, b }: HyperbolaCoefficients): [number, number][][] {
  if (![k, b].every(Number.isFinite) || k === 0) return [];
  const { xMin, xMax, yMin, yMax } = HYPERBOLA_WINDOW;
  const branches: [number, number][][] = [];
  for (const side of [-1, 1]) {
    const outerX = side < 0 ? xMin : xMax;
    const outerY = hyperbolaValue(outerX, { k, b });
    if (outerY === null) continue;
    const tendsUp = k * side > 0;
    if (tendsUp ? outerY > yMax : outerY < yMin) continue;
    const startY = Math.max(yMin, Math.min(yMax, outerY));
    const startX = startY === outerY ? outerX : k / (startY - b);
    const endX = k / ((tendsUp ? yMax : yMin) - b);
    const points: [number, number][] = [];
    for (let i = 0; i <= 700; i++) {
      const x = startX + (endX - startX) * i / 700;
      const y = hyperbolaValue(x, { k, b });
      if (y !== null) points.push([x, y]);
    }
    branches.push(points);
  }
  return branches;
}
