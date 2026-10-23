import { useEffect, useId, useRef, useState, type PointerEvent } from 'react';
import { CoefficientControl } from '../../shared/lesson/graph-controls';
import { analyzeLinear, INITIAL_LINEAR, linearFormula, linearNumber, linearValue, type LinearCoefficients } from './linear-math';

// The source's mathematical viewport and coefficient ranges remain unchanged.
const plot = { left: 48, top: 20, width: 504, height: 320 };
const sx = (x: number) => plot.left + (x + 8) / 16 * plot.width;
const sy = (y: number) => plot.top + (16 - y) / 32 * plot.height;
const visible = (x: number, y: number) => x >= -8 && x <= 8 && y >= -16 && y <= 16;
export function LinearGraph({ id }: { id: string }) {
  const [coefficients, setCoefficients] = useState<LinearCoefficients>(INITIAL_LINEAR);
  const [selectedX, setSelectedX] = useState(0);
  const resetFrame = useRef<number | null>(null);
  const pointer = useRef<{ id: number; x: number; y: number } | null>(null);
  const identity = useId();
  function stopReset() { if (resetFrame.current !== null) cancelAnimationFrame(resetFrame.current); resetFrame.current = null; }
  useEffect(() => stopReset, []);
  function reset() {
    stopReset();
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { setCoefficients(INITIAL_LINEAR); setSelectedX(0); return; }
    const from = coefficients, fromX = selectedX, start = performance.now();
    const frame = (now: number) => {
      const progress = Math.min((now - start) / 360, 1), eased = 1 - (1 - progress) ** 3;
      if (progress === 1) { setCoefficients(INITIAL_LINEAR); setSelectedX(0); resetFrame.current = null; return; }
      setCoefficients({ k: from.k + (1 - from.k) * eased, b: from.b * (1 - eased) });
      setSelectedX(fromX * (1 - eased)); resetFrame.current = requestAnimationFrame(frame);
    };
    resetFrame.current = requestAnimationFrame(frame);
  }
  const analysis = analyzeLinear(coefficients), y = linearValue(selectedX, coefficients);
  const coordinates = `x = ${linearNumber(selectedX)}; y = ${linearNumber(y)}`;
  function chooseX(event: PointerEvent<SVGSVGElement>) {
    const box = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - box.left) * 580 / box.width - plot.left) / plot.width * 16 - 8;
    if (x >= -8 && x <= 8) { stopReset(); setSelectedX(Math.round(x * 10) / 10); }
  }
  const properties = [
    ['Поведение', analysis.direction], ['Пересечение Oy', `(0; ${linearNumber(coefficients.b)})`],
    ['Пересечение Ox', analysis.xIntercept === 'all' ? 'Вся ось Ox' : analysis.xIntercept === 'none' ? 'Нет пересечения' : `(${linearNumber(analysis.xIntercept)}; 0)`],
  ];
  return <div className="quadratic-lab linear-lab" id={id} data-react-linear="true">
    <div className="quadratic-toolbar"><p className="quadratic-current" aria-live="polite">{linearFormula(coefficients)}</p><button className="quadratic-reset" type="button" onClick={reset}>Сбросить значения</button></div>
    <div className="quadratic-workspace"><figure className="quadratic-plot"><svg viewBox="0 0 580 378" role="img" aria-labelledby={`${identity}-title ${identity}-desc`}
      onPointerDown={event => { if (event.button === 0 && event.isPrimary !== false && pointer.current === null) pointer.current = { id: event.pointerId, x: event.clientX, y: event.clientY }; }}
      onPointerMove={event => {
        if (pointer.current && Math.hypot(event.clientX - pointer.current.x, event.clientY - pointer.current.y) > 8) pointer.current = null;
        if (event.pointerType === 'mouse' && event.buttons === 0) chooseX(event);
      }}
      onPointerUp={event => { const start = pointer.current; pointer.current = null; if (start?.id === event.pointerId && Math.hypot(event.clientX - start.x, event.clientY - start.y) <= 8) chooseX(event); }}
      onPointerCancel={() => { pointer.current = null; }} onPointerLeave={() => { pointer.current = null; }} onLostPointerCapture={() => { pointer.current = null; }}>
      <title id={`${identity}-title`}>{`График ${linearFormula(coefficients)}`}</title><desc id={`${identity}-desc`}>Координатная плоскость: x от −8 до 8, y от −16 до 16. Коэффициенты и координаты точки доступны ползунками и текстом.</desc>
      <defs><clipPath id={`${identity}-clip`}><rect x={plot.left} y={plot.top} width={plot.width} height={plot.height}/></clipPath></defs>
      <rect className="plot-background" x={plot.left} y={plot.top} width={plot.width} height={plot.height}/>
      <g className="plot-grid">{Array.from({ length: 17 }, (_, i) => i - 8).map(n => <g key={n}><line x1={sx(n)} x2={sx(n)} y1={plot.top} y2={plot.top + plot.height}/><line x1={plot.left} x2={plot.left + plot.width} y1={sy(n * 2)} y2={sy(n * 2)}/></g>)}</g>
      <g className="plot-axes"><line x1={plot.left} x2={plot.left + plot.width} y1={sy(0)} y2={sy(0)}/><line x1={sx(0)} x2={sx(0)} y1={plot.top} y2={plot.top + plot.height}/></g>
      <g className="plot-ticks">{[-8, -4, 4, 8].map(n => <g key={n}><text x={sx(n)} y={sy(0) + 18} textAnchor="middle">{n}</text><text x={sx(0) - 10} y={sy(n * 2) + (n === 8 ? 14 : 0)} textAnchor="end">{n * 2}</text></g>)}<text x="565" y={sy(0) - 6}>x</text><text x={sx(0) + 9} y="17">y</text><text x={sx(0) - 12} y={sy(0) + 18}>0</text></g>
      <g clipPath={`url(#${identity}-clip)`}>
        <path className="plot-curve" d={`M${sx(-8)},${sy(linearValue(-8, coefficients))} L${sx(8)},${sy(linearValue(8, coefficients))}`} fill="none"/>
        <circle className="plot-intercept" cx={sx(0)} cy={sy(coefficients.b)} r="4.5"/>
        {typeof analysis.xIntercept === 'number' && visible(analysis.xIntercept, 0) && <circle className="plot-root" cx={sx(analysis.xIntercept)} cy={sy(0)} r="4.5"/>}
        {visible(selectedX, y) && <><path className="plot-symmetry" d={`M${sx(selectedX)},${sy(0)} V${sy(y)} H${sx(0)}`} fill="none"/><circle className="plot-probe" cx={sx(selectedX)} cy={sy(y)} r="4"/></>}
      </g>
    </svg><figcaption className="quadratic-probe"><div className="quadratic-probe-label"><label htmlFor={`${identity}-probe`}>Точка на графике</label><span className="quadratic-probe-coordinates">{coordinates}</span></div>
      <input id={`${identity}-probe`} aria-label="Абсцисса исследуемой точки x" aria-valuetext={coordinates} type="range" min="-8" max="8" step="0.1" value={selectedX} onPointerDown={stopReset} onChange={event => { stopReset(); setSelectedX(Number(event.target.value)); }}/>
      <p>Выберите x ползунком или нажмите на график.{!visible(selectedX, y) && <span> Точка вне окна графика.</span>}</p></figcaption></figure>
      <div className="quadratic-data"><div className="quadratic-controls linear-controls">{(['k', 'b'] as const).map(name => <CoefficientControl key={name} name={name} value={coefficients[name]} min={name === 'k' ? -3 : -6} max={name === 'k' ? 3 : 6} step={0.5} format={linearNumber} onInputStart={stopReset} onChange={value => { stopReset(); setCoefficients(current => ({ ...current, [name]: value })); }}/>)}</div>
        <dl className="quadratic-properties">{properties.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
      </div></div>
    <p className="quadratic-legend"><span className="legend-curve">график функции</span><span className="legend-intercept">точка (0; b)</span><span className="legend-root">пересечение с осью Ox</span></p>
  </div>;
}
