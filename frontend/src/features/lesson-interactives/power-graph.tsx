import { useEffect, useId, useRef, useState } from 'react';
import { POWER_DEFAULT_PRESET, POWER_PRESETS, POWER_TABLE_X, RATIONAL_POWER_TABLE_X, powerBranches, powerProperties, powerValue, type PowerMode } from './power-math';

const format = (value: number | null) => value === null ? 'не определено'
  : String(Number(value.toPrecision(10))).replaceAll('-', '−').replace('.', ',');

function FractionalExponent({ numerator, denominator }: { numerator: number; denominator: number }) {
  return <mrow>{numerator < 0 && <mo>−</mo>}
    <mfrac><mn>{Math.abs(numerator)}</mn><mn>{denominator}</mn></mfrac>
  </mrow>;
}

function Exponent({ numerator, denominator }: { numerator: number; denominator: number }) {
  return denominator === 1 ? <>{format(numerator)}</>
    : <math><FractionalExponent numerator={numerator} denominator={denominator}/></math>;
}

export function PowerGraph({ id, mode }: { id: string; mode: PowerMode }) {
  const identity = useId();
  const rational = mode === 'rational';
  const negative = mode === 'negative';
  const initial = rational ? POWER_DEFAULT_PRESET : negative ? -2 : 2;
  const [selection, setSelection] = useState(initial);
  const [x, setX] = useState(1);
  const [reference, setReference] = useState(false);
  const [n, d] = rational ? POWER_PRESETS[selection] : [selection, 1];
  const xStep = rational ? 0.25 : 0.05;
  const tableX = rational ? RATIONAL_POWER_TABLE_X : POWER_TABLE_X;
  const resetFrame = useRef<number | null>(null);
  function stopReset() {
    if (resetFrame.current !== null) cancelAnimationFrame(resetFrame.current);
    resetFrame.current = null;
  }
  useEffect(() => stopReset, []);
  function reset() {
    stopReset();
    setReference(false);
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setSelection(initial);
      setX(1);
      return;
    }
    const start = performance.now();
    const frame = (now: number) => {
      const progress = Math.min((now - start) / 360, 1);
      const eased = 1 - (1 - progress) ** 3;
      const steps = Math.round(Math.abs(initial - selection) * eased);
      setSelection(selection + Math.sign(initial - selection) * steps);
      const units = rational ? 4 : 20;
      setX(Math.round((x + (1 - x) * eased) * units) / units);
      resetFrame.current = progress < 1 ? requestAnimationFrame(frame) : null;
    };
    resetFrame.current = requestAnimationFrame(frame);
  }
  const xLimit = rational ? 3 : negative ? 4 : 2.25;
  const yLimit = rational ? 3 : negative ? 6 : 7;
  const y = powerValue(x, n, d);
  const exponentLabel = d === 1 ? format(n) : `${format(n)} делённое на ${d}`;
  const description = n < 0
    ? (d === 1 ? 'Две ветви, оси координат — асимптоты.' : 'Правая ветвь, оси координат — асимптоты.')
    : n === 0 ? 'Прямая y = 1 с выколотой точкой (0; 1).' : 'Функция проходит через начало координат.';
  const sx = (v: number) => 290 + 250 * v / xLimit;
  const sy = (v: number) => 189 - 155 * v / yLimit;
  const gridX = Array.from({ length: 2 * Math.floor(xLimit) + 1 }, (_, i) => i - Math.floor(xLimit));
  const gridY = Array.from({ length: 2 * yLimit + 1 }, (_, i) => i - yLimit);

  return <div id={id} className="quadratic-lab">
    <div className="quadratic-toolbar">
      <p className="quadratic-current" aria-live="polite">{d === 1 ? <>y = x<sup>{format(n)}</sup></>
        : <math aria-label={`y равно x в степени ${exponentLabel}`}><mrow><mi>y</mi><mo>=</mo>
          <msup><mi>x</mi><FractionalExponent numerator={n} denominator={d}/></msup>
        </mrow></math>}</p>
      <button className="quadratic-reset" type="button" onClick={reset}>
        {rational ? 'Вернуть y = x²' : `Вернуть n = ${format(initial)}`}
      </button>
    </div>
    <div className="quadratic-workspace">
      <figure className="quadratic-plot">
        <svg viewBox="0 0 580 378" role="img" aria-labelledby={`${identity}-title ${identity}-desc`}>
          <title id={`${identity}-title`}>График степенной функции</title>
          <desc id={`${identity}-desc`}>{`Показатель n = ${exponentLabel}. ${description}`}</desc>
          {gridX.map(v => <g key={v}>
            <line className={v ? 'plot-grid' : n < 0 ? 'plot-symmetry' : 'plot-axes'} x1={sx(v)} x2={sx(v)} y1="34" y2="344"/>
            {v !== 0 && <text className="plot-ticks" x={sx(v)} y="207" textAnchor={v === -xLimit ? 'start' : v === xLimit ? 'end' : 'middle'}>{format(v)}</text>}
          </g>)}
          {gridY.map(v => <g key={v}>
            <line className={v ? 'plot-grid' : n < 0 ? 'plot-symmetry' : 'plot-axes'} x1="40" x2="540" y1={sy(v)} y2={sy(v)}/>
            {v !== 0 && <text className="plot-ticks" x="298" y={Math.max(47, sy(v) - 3)}>{format(v)}</text>}
          </g>)}
          <text className="plot-ticks" x="526" y="181">x</text>
          <text className="plot-ticks" x="274" y="47">y</text>
          {rational && reference && <line className="plot-symmetry" x1={sx(-xLimit)} y1={sy(-xLimit)} x2={sx(xLimit)} y2={sy(xLimit)}/>}
          {powerBranches(n, xLimit, yLimit, d).map((branch, i) => <polyline key={i} className="plot-curve"
            fill="none" points={branch.map(([a, b]) => `${sx(a)},${sy(b)}`).join(' ')}/>)}
          {n === 0 && <circle className="plot-root" cx={sx(0)} cy={sy(1)} r="4"/>}
          {y !== null && Math.abs(y) <= yLimit && <circle className="plot-probe" cx={sx(x)} cy={sy(y)} r="4"/>}
        </svg>
        <figcaption className="quadratic-probe">
          <div className="quadratic-probe-label">
            <label htmlFor={`${identity}-x`}>Координата x</label>
            <output htmlFor={`${identity}-x`}>x = {format(x)}, y = {format(y)}</output>
          </div>
          <input id={`${identity}-x`} type="range" min={-xLimit} max={xLimit} step={xStep} value={x}
            onPointerDown={stopReset} onKeyDown={stopReset}
            onChange={event => { stopReset(); setX(Number(event.target.value)); }}/>
          {rational && y === null && <p>{x === 0 ? 'Нулевое основание здесь запрещено.' : 'Для дробного показателя отрицательное основание исключено.'}</p>}
          {negative && <p>Около x = 0 значения быстро возрастают по модулю. Точка x = 0 графику не принадлежит.</p>}
          {y !== null && Math.abs(y) > yLimit && <p>Точка вне окна графика.</p>}
        </figcaption>
      </figure>
      <div className="quadratic-data">
        <div className="coefficient-control">
          <label htmlFor={`${identity}-n`}>Показатель {rational ? 'p' : 'n'} <output htmlFor={`${identity}-n`}><Exponent numerator={n} denominator={d}/></output></label>
          <input id={`${identity}-n`} type="range" min={rational ? 0 : negative ? -10 : 1} max={rational ? POWER_PRESETS.length - 1 : negative ? -1 : 10} step={1} value={selection}
            aria-valuetext={rational ? exponentLabel : undefined}
            onPointerDown={stopReset} onKeyDown={stopReset}
            onChange={event => { stopReset(); setSelection(Number(event.target.value)); }}/>
        </div>
        {rational && <fieldset className="power-presets">
          <legend>Пресеты показателя</legend>
          {POWER_PRESETS.map(([numerator, denominator], index) =>
            <button key={index} type="button" className="quadratic-reset" aria-pressed={selection === index}
              aria-label={`Показатель ${format(numerator)}${denominator === 1 ? '' : ` делённое на ${denominator}`}`}
              onClick={() => { stopReset(); setSelection(index); }}>
              <Exponent numerator={numerator} denominator={denominator}/>
            </button>)}
        </fieldset>}
        {rational && <label><input type="checkbox" checked={reference}
          onChange={event => { stopReset(); setReference(event.target.checked); }}/> Сравнить с прямой y = x</label>}
        <dl className="quadratic-properties">{powerProperties(n, d, rational).map(([label, value]) =>
          <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
      </div>
    </div>
    <div className="lesson-table-scroll" tabIndex={0} role="region" aria-label="Таблица значений степенной функции">
      <table>
        <caption>Значения функции</caption>
        <thead><tr><th scope="col">x</th>{tableX.map(value => <th key={value} scope="col">{format(value)}</th>)}</tr></thead>
        <tbody><tr><th scope="row">y</th>{tableX.map(value => <td key={value}>{format(powerValue(value, n, d))}</td>)}</tr></tbody>
      </table>
    </div>
  </div>;
}
