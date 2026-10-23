import { createEvent, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { QuadraticGraph } from '../src/shared/lesson/quadratic-graph';

function graph() {
  const svg = screen.getByRole('img', { name: /График y/ });
  vi.spyOn(svg, 'getBoundingClientRect').mockReturnValue({
    x: 0, y: 0, left: 0, top: 0, right: 580, bottom: 378, width: 580, height: 378,
    toJSON: () => ({}),
  });
  return svg;
}

function pointer(target: Element, type: 'pointerDown' | 'pointerUp' | 'pointerMove' | 'pointerCancel', options: Record<string, number> = {}) {
  const values = { pointerId: 1, isPrimary: true, clientX: 390, clientY: 180, ...options };
  const event = createEvent[type](target, values);
  Object.entries(values).forEach(([key, value]) => Object.defineProperty(event, key, { value, configurable: true }));
  fireEvent(target, event);
}

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe('quadratic graph inspection gesture', () => {
  it('selects only after a completed stationary tap and allows the next tap after cancel', () => {
    render(<QuadraticGraph />);
    const svg = graph();
    const probe = screen.getByLabelText('Абсцисса исследуемой точки x') as HTMLInputElement;
    expect(probe.value).toBe('0');

    pointer(svg, 'pointerDown');
    expect(probe.value).toBe('0');
    pointer(svg, 'pointerCancel');
    expect(probe.value).toBe('0');
    pointer(svg, 'pointerUp');
    expect(probe.value).toBe('0');

    pointer(svg, 'pointerDown');
    pointer(svg, 'pointerUp', { clientX: 392, clientY: 182 });
    expect(probe.value).toBe('3.7');
  });

  it('permanently cancels a gesture after it moves beyond the tap slop', () => {
    render(<QuadraticGraph />);
    const svg = graph();
    const probe = screen.getByLabelText('Абсцисса исследуемой точки x') as HTMLInputElement;

    pointer(svg, 'pointerDown', { clientX: 390, clientY: 180 });
    pointer(svg, 'pointerMove', { clientX: 420, clientY: 180 });
    pointer(svg, 'pointerMove', { clientX: 390, clientY: 180 });
    pointer(svg, 'pointerUp', { clientX: 390, clientY: 180 });
    expect(probe.value).toBe('0');

    pointer(svg, 'pointerDown', { clientX: 390, clientY: 180 });
    pointer(svg, 'pointerUp', { clientX: 390, clientY: 180 });
    expect(probe.value).toBe('3.6');
  });

  it('ignores non-primary buttons and clears interrupted gestures for the next tap', () => {
    render(<QuadraticGraph />);
    const svg = graph();
    const probe = screen.getByLabelText('Абсцисса исследуемой точки x') as HTMLInputElement;

    pointer(svg, 'pointerDown', { button: 2 });
    pointer(svg, 'pointerUp', { button: 2 });
    expect(probe.value).toBe('0');

    for (const ending of ['pointerCancel', 'lostPointerCapture', 'pointerOut'] as const) {
      pointer(svg, 'pointerDown', { clientX: 390, clientY: 180 });
      const event = createEvent[ending](svg, { pointerId: 1, relatedTarget: null });
      Object.defineProperty(event, 'pointerId', { value: 1 });
      fireEvent(svg, event);
      pointer(svg, 'pointerUp', { clientX: 390, clientY: 180 });
      expect(probe.value, ending).toBe('0');
    }
    pointer(svg, 'pointerDown', { clientX: 390, clientY: 180 });
    pointer(svg, 'pointerUp', { clientX: 390, clientY: 180 });
    expect(probe.value).toBe('3.6');
  });

  it('interrupts a coefficient reset only when the graph tap completes', () => {
    const cancel = vi.fn();
    vi.stubGlobal('requestAnimationFrame', vi.fn(() => 123));
    vi.stubGlobal('cancelAnimationFrame', cancel);
    vi.spyOn(performance, 'now').mockReturnValue(0);
    vi.stubGlobal('matchMedia', () => ({ matches: false }));
    render(<QuadraticGraph />);
    const svg = graph();
    fireEvent.change(document.querySelector<HTMLInputElement>('input[aria-label="Коэффициент c"]')!, { target: { value: '5' } });
    fireEvent.click(screen.getByRole('button', { name: 'Сбросить коэффициенты' }));
    expect(cancel).not.toHaveBeenCalled();

    pointer(svg, 'pointerDown');
    expect(cancel).not.toHaveBeenCalled();
    pointer(svg, 'pointerUp');
    expect(cancel).toHaveBeenCalledWith(123);
  });
});
