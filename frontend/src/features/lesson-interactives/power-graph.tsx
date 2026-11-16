import { useEffect, useId, useRef, useState } from 'react';
import { POWER_TABLE_X, powerBranches, powerProperties, powerValue, type PowerMode } from './power-math';

const format = (value: number | null) => value === null ? 'не определено'
  : String(Number(value.toPrecision(10))).replaceAll('-', '−').replace('.', ',');

export function PowerGraph({ id, mode }: { id: string; mode: PowerMode }) {
  const identity = useId();
  const negative = mode === 'negative';
  const initial = negative ? -2 : 2;
  const [n, setN] = useState(initial);
  const [x, setX] = useState(1);
  const resetFrame = useRef<number | null>(null);
  function stopReset() {
    if (resetFrame.current !== null) cancelAnimationFrame(resetFrame.current);
    resetFrame.current = null;
  }
  useEffect(() => stopReset, []);
  function reset() {
    stopReset();
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setN(initial);
      setX(1);
      return;
    }
    const start = performance.now();
    const frame = (now: number) => {
      const progress = Math.min((now - start) / 360, 1);
      const eased = 1 - (1 - progress) ** 3;
      const steps = Math.round(Math.abs(initial - n) * eased);
      setN(n + Math.sign(initial - n) * steps);
      setX(Math.round((x + (1 - x) * eased) * 20) / 20);
      resetFrame.current = progress < 1 ? requestAnimationFrame(frame) : null;
    };
    resetFrame.current = requestAnimationFrame(frame);
  }
  const xLimit = negative ? 4 : 2.25;
  const yLimit = negative ? 6 : 7;
  const y = powerValue(x, n);
  const sx = (v: number) => 290 + 250 * v / xLimit;
  const sy = (v: number) => 189 - 155 * v / yLimit;
  const gridX = Array.from({ length: 2 * Math.floor(xLimit) + 1 }, (_, i) => i - Math.floor(xLimit));
  const gridY = Array.from({ length: 2 * yLimit + 1 }, (_, i) => i - yLimit);

  return <div id={id} className="quadratic-lab">
    <div className="quadratic-toolbar">
      <p className="quadratic-current" aria-live="polite">y = x<sup>{format(n)}</sup></p>
      <button className="quadratic-reset" type="button" onClick={reset}>
        Вернуть n = {format(initial)}
      </button>
    </div>
    <div className="quadratic-workspace">
      <figure className="quadratic-plot">
        <svg viewBox="0 0 580 378" role="img" aria-labelledby={`${identity}-title ${identity}-desc`}>
          <title id={`${identity}-title`}>График степенной функции</title>
          <desc id={`${identity}-desc`}>{`Показатель n = ${format(n)}. ${negative ? 'Две ветви, оси координат — асимптоты.' : 'Функция проходит через начало координат.'}`}</desc>
          {gridX.map(v => <g key={v}>
            <line className={v ? 'plot-grid' : negative ? 'plot-symmetry' : 'plot-axes'} x1={sx(v)} x2={sx(v)} y1="34" y2="344"/>
            {v !== 0 && <text className="plot-ticks" x={sx(v)} y="207" textAnchor={v === -xLimit ? 'start' : v === xLimit ? 'end' : 'middle'}>{format(v)}</text>}
          </g>)}
          {gridY.map(v => <g key={v}>
            <line className={v ? 'plot-grid' : negative ? 'plot-symmetry' : 'plot-axes'} x1="40" x2="540" y1={sy(v)} y2={sy(v)}/>
            {v !== 0 && <text className="plot-ticks" x="298" y={Math.max(47, sy(v) - 3)}>{format(v)}</text>}
          </g>)}
          <text className="plot-ticks" x="526" y="181">x</text>
          <text className="plot-ticks" x="274" y="47">y</text>
          {powerBranches(n, xLimit, yLimit).map((branch, i) => <polyline key={i} className="plot-curve"
            fill="none" points={branch.map(([a, b]) => `${sx(a)},${sy(b)}`).join(' ')}/>)}
          {y !== null && Math.abs(y) <= yLimit && <circle className="plot-probe" cx={sx(x)} cy={sy(y)} r="4"/>}
        </svg>
        <figcaption className="quadratic-probe">
          <div className="quadratic-probe-label">
            <label htmlFor={`${identity}-x`}>Координата x</label>
            <output htmlFor={`${identity}-x`}>x = {format(x)}, y = {format(y)}</output>
          </div>
          <input id={`${identity}-x`} type="range" min={-xLimit} max={xLimit} step={0.05} value={x}
            onPointerDown={stopReset} onKeyDown={stopReset}
            onChange={event => { stopReset(); setX(Number(event.target.value)); }}/>
          {negative && <p>Около x = 0 значения быстро возрастают по модулю. Точка x = 0 графику не принадлежит.</p>}
          {y !== null && Math.abs(y) > yLimit && <p>Точка вне окна графика.</p>}
        </figcaption>
      </figure>
      <div className="quadratic-data">
        <div className="coefficient-control">
          <label htmlFor={`${identity}-n`}>Показатель n <output htmlFor={`${identity}-n`}>{format(n)}</output></label>
          <input id={`${identity}-n`} type="range" min={negative ? -10 : 1} max={negative ? -1 : 10} step={1} value={n}
            onPointerDown={stopReset} onKeyDown={stopReset}
            onChange={event => { stopReset(); setN(Number(event.target.value)); }}/>
        </div>
        <dl className="quadratic-properties">{powerProperties(n).map(([label, value]) =>
          <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
      </div>
    </div>
    <div className="lesson-table-scroll" tabIndex={0} role="region" aria-label="Таблица значений степенной функции">
      <table>
        <caption>Значения функции</caption>
        <thead><tr><th scope="col">x</th>{POWER_TABLE_X.map(value => <th key={value} scope="col">{format(value)}</th>)}</tr></thead>
        <tbody><tr><th scope="row">y</th>{POWER_TABLE_X.map(value => <td key={value}>{format(powerValue(value, n))}</td>)}</tr></tbody>
      </table>
    </div>
  </div>;
}
