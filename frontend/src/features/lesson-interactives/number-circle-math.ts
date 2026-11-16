export const CIRCLE_STEPS = { min: -48, max: 48, initial: 4, turn: 24 } as const;
export const CIRCLE_PRESETS = [0, 2, 3, 4, 6, 12, 18, 24] as const;
export const STANDARD_STEPS = [0, 2, 3, 4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22] as const;

export function circleRadians(step: number) {
  const gcd = (a: number, b: number): number => b ? gcd(b, a % b) : a;
  const divisor = gcd(Math.abs(step), 12);
  return { numerator: step / divisor, denominator: 12 / divisor };
}

export function circlePoint(step: number) {
  const turn = CIRCLE_STEPS.turn;
  const normalized = ((step % turn) + turn) % turn;
  const angle = normalized * Math.PI / 12;
  const zeroOnAxis = (value: number) => Math.abs(value) < 1e-12 ? 0 : value;
  const x = zeroOnAxis(Math.cos(angle));
  const y = zeroOnAxis(Math.sin(angle));
  return {
    x, y, normalized, degrees: step * 15,
    turns: Math.trunc(step / turn),
    remainder: step % turn,
    exact: normalized % 2 === 0 || normalized % 3 === 0,
    quadrant: x === 0 || y === 0 ? 'На координатной оси'
      : x > 0 ? (y > 0 ? 'I четверть' : 'IV четверть') : (y > 0 ? 'II четверть' : 'III четверть'),
    direction: step === 0 ? 'Без поворота' : step > 0 ? 'Против часовой стрелки' : 'По часовой стрелке',
  };
}

export function exactCoordinate(value: number): { negative: boolean; magnitude: 0 | 1 | 2 | 3; half: boolean } {
  const negative = value < 0;
  const absolute = Math.abs(value);
  if (absolute === 0 || absolute === 1) return { negative, magnitude: absolute, half: false };
  if (Math.abs(absolute - 0.5) < 1e-10) return { negative, magnitude: 1, half: true };
  if (Math.abs(absolute - Math.SQRT1_2) < 1e-10) return { negative, magnitude: 2, half: true };
  if (Math.abs(absolute - Math.sqrt(3) / 2) < 1e-10) return { negative, magnitude: 3, half: true };
  throw Error('Coordinate is not from a standard angle');
}
