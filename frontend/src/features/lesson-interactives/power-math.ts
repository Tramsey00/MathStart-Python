export type PowerMode = 'positive' | 'negative' | 'rational';

export const POWER_PRESETS = [[-3, 1], [-2, 1], [-1, 1], [-1, 2], [0, 1], [1, 2],
  [2, 3], [1, 1], [3, 2], [2, 1], [3, 1], [4, 1]] as const;
export const POWER_DEFAULT_PRESET = 9;
export const RATIONAL_POWER_TABLE_X = [-2, -1, 0, 0.25, 1, 2];

export const POWER_TABLE_X = [-2, -1, -0.5, 0, 0.5, 1, 2];

export function powerValue(x: number, n: number, d = 1): number | null {
  if ((x === 0 && n <= 0) || (d !== 1 && x < 0)) return null;
  const value = x ** (n / d);
  return Number.isFinite(value) ? value : null;
}

export function powerProperties(n: number, d = 1, extended = false): [string, string][] {
  if (n === 0) return [
    ['Чётность', 'Чётная'], ['Симметрия', 'Относительно оси Oy'],
    ['Область определения', 'ℝ ∖ {0}'], ['Область значений', '{1}'],
    ['Монотонность', 'Постоянна на области определения'],
    ['Нули', 'Нет'], ['Экстремумы', 'Наибольшее и наименьшее значение: 1'],
    ['Тип показателя', 'Нулевой показатель'],
  ];
  if (d !== 1) return [
    ['Чётность', 'Ни чётная, ни нечётная'], ['Симметрия', 'Нет'],
    ['Область определения', n > 0 ? '[0; +∞)' : '(0; +∞)'],
    ['Область значений', n > 0 ? '[0; +∞)' : '(0; +∞)'],
    ['Монотонность', n > 0 ? 'Возрастает на [0; +∞)' : 'Убывает на (0; +∞)'],
    ['Нули', n > 0 ? 'x = 0' : 'Нет'],
    ['Экстремумы', n > 0 ? 'Наименьшее значение: 0 при x = 0' : 'Нет наибольшего и наименьшего'],
    ['Тип показателя', n > 0 ? 'Положительный дробный' : 'Отрицательный дробный'],
    ...(n < 0 ? [['Асимптоты', 'x = 0 и y = 0'] as [string, string]] : []),
  ];
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
    ...(extended ? [
      ['Нули', n > 0 ? 'x = 0' : 'Нет'],
      ['Экстремумы', n > 0 && even ? 'Наименьшее значение: 0 при x = 0' : 'Нет наибольшего и наименьшего'],
      ['Тип показателя', n > 0 ? 'Натуральный' : 'Отрицательный целый'],
    ] as [string, string][] : []),
  ];
}

export function powerBranches(n: number, xLimit: number, yLimit: number, d = 1): [number, number][][] {
  if (n === 0) return [[[-xLimit, 1], [0, 1]], [[0, 1], [xLimit, 1]]];
  const edge = Math.min(xLimit, yLimit ** (d / n));
  const intervals: [number, number][] = n < 0
    ? (d === 1 ? [[-xLimit, -edge], [edge, xLimit]] : [[edge, xLimit]])
    : [[d === 1 ? -edge : 0, edge]];
  return intervals.map(([start, end]) => Array.from({ length: 241 }, (_, i) => {
    const x = start + (end - start) * i / 240;
    return [x, x ** (n / d)];
  }));
}
