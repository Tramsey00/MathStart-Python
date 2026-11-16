import { useEffect, useRef, useState } from 'react';

interface GraphState { k: number; shift: number; x: number }

// Local reset lifecycle for the two grade-eight labs; no plotting abstraction.
export function useGradeEightGraphState(initial: Readonly<GraphState>) {
  const [state, setState] = useState<GraphState>(initial);
  const resetFrame = useRef<number | null>(null);
  function stopReset() {
    if (resetFrame.current !== null) cancelAnimationFrame(resetFrame.current);
    resetFrame.current = null;
  }
  useEffect(() => stopReset, []);

  function change(key: keyof GraphState, value: number) {
    stopReset();
    if (Number.isFinite(value)) setState(current => ({ ...current, [key]: value }));
  }

  function reset() {
    stopReset();
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setState(initial);
      return;
    }
    const from = state;
    const started = performance.now();
    // Keep animated input states on the agreed 0.1 control grid. Function values
    // are calculated from those inputs without rounding intermediate arithmetic.
    const interpolate = (a: number, b: number, t: number) => Math.round((a + (b - a) * t) * 10) / 10;
    const frame = (now: number) => {
      const progress = Math.min((now - started) / 360, 1);
      if (progress === 1) {
        setState(initial);
        resetFrame.current = null;
        return;
      }
      const eased = 1 - (1 - progress) ** 3;
      setState({ k: interpolate(from.k, initial.k, eased), shift: interpolate(from.shift, initial.shift, eased),
        x: interpolate(from.x, initial.x, eased) });
      resetFrame.current = requestAnimationFrame(frame);
    };
    resetFrame.current = requestAnimationFrame(frame);
  }
  return { state, change, reset, stopReset };
}
