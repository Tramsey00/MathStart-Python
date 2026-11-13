export type PowerMode = 'positive' | 'negative';

export const POWER_TABLE_X = [-2, -1, -0.5, 0, 0.5, 1, 2];

export function powerValue(x: number, n: number): number | null {
  return x === 0 && n < 0 ? null : x ** n;
}

export function powerProperties(n: number): [string, string][] {
  const even = n % 2 === 0;
  return [
    ['Чётность', even ? 'Чётная' : 'Нечётная'],
    ['Симметрия', even ? 'Относительно оси Oy' : 'Относительно начала координат'],
    ['Область определения', n < 0 ? 'ℝ ∖ {0}' : 'ℝ'],
    ['Область значений', n < 0 ? (even ? '(0; +∞)' : 'ℝ ∖ {0}') : (even ? '[0; +∞)' : 'ℝ')],
    ['Монотонность', n < 0
      ? (even ? 'Возрастает на (−∞; 0), убывает на (0; +∞)' : 'Убывает на (−∞; 0) и на (0; +∞)')
      : (even ? 'Убывает на (−∞; 0], возрастает на [0; +∞)' : 'Возрастает на ℝ')],
    ['Четверти', even ? 'I и II' : 'I и III'],
    ...(n < 0 ? [['Асимптоты', 'x = 0 и y = 0'] as [string, string]] : []),
  ];
}

export function powerBranches(n: number, xLimit: number, yLimit: number): [number, number][][] {
  const edge = Math.min(xLimit, yLimit ** (1 / n));
  const intervals: [number, number][] = n < 0 ? [[-xLimit, -edge], [edge, xLimit]] : [[-edge, edge]];
  return intervals.map(([start, end]) => Array.from({ length: 241 }, (_, i) => {
    const x = start + (end - start) * i / 240;
    return [x, x ** n];
  }));
}
