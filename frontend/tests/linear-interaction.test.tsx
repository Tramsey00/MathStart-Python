import { createEvent, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { LinearGraph } from '../src/features/lesson-interactives/linear-graph';
afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); });
function pointer(target: Element, type: 'pointerDown' | 'pointerUp' | 'pointerMove' | 'pointerCancel', options = {}) {
  const values = { pointerId: 1, button: 0, isPrimary: true, clientX: 400, clientY: 180, ...options };
  const event = createEvent[type](target, values);
  Object.entries(values).forEach(([key, value]) => Object.defineProperty(event, key, { value })); fireEvent(target, event);
}
it('keeps cancelled and scrolling gestures from selecting a point', () => {
  render(<LinearGraph id="linear"/>);
  const graph = screen.getByRole('img', { name: /График y/ });
  vi.spyOn(graph, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 580, height: 378 } as DOMRect);
  const probe = screen.getByLabelText('Абсцисса исследуемой точки x') as HTMLInputElement;
  pointer(graph, 'pointerDown'); pointer(graph, 'pointerCancel'); pointer(graph, 'pointerUp'); expect(probe.value).toBe('0');
  pointer(graph, 'pointerDown'); pointer(graph, 'pointerMove', { clientY: 210 }); pointer(graph, 'pointerMove'); pointer(graph, 'pointerUp'); expect(probe.value).toBe('0');
  pointer(graph, 'pointerDown'); pointer(graph, 'pointerUp'); expect(probe.value).toBe('0');
  fireEvent.change(probe, { target: { value: '2.4' } }); expect(probe.value).toBe('2.4');
  expect(graph.querySelector('.plot-symmetry')).toBeNull();
});
it('resets with reduced motion and cancels animated reset on new coefficient input', () => {
  let frame: FrameRequestCallback | undefined;
  vi.stubGlobal('requestAnimationFrame', vi.fn((cb: FrameRequestCallback) => { frame = cb; return 1; }));
  const cancel = vi.fn(); vi.stubGlobal('cancelAnimationFrame', cancel);
  vi.stubGlobal('matchMedia', () => ({ matches: false }));
  render(<LinearGraph id="linear"/>);
  const k = screen.getByRole('slider', { name: 'Коэффициент k' }) as HTMLInputElement;
  fireEvent.change(k, { target: { value: '-2' } }); fireEvent.click(screen.getByRole('button', { name: 'Сбросить значения' }));
  expect(frame).toBeDefined(); fireEvent.change(k, { target: { value: '3' } }); expect(cancel).toHaveBeenCalled(); expect(k.value).toBe('3');
  vi.stubGlobal('matchMedia', () => ({ matches: true })); fireEvent.click(screen.getByRole('button', { name: 'Сбросить значения' })); expect(k.value).toBe('1');
});
