import { useId, useMemo } from 'react';
import { CoefficientControl } from '../../shared/lesson/graph-controls';
import { formatNumber } from '../../shared/lesson/quadratic-math';
import { SQUARE_ROOT_TABLE_X, SQUARE_ROOT_WINDOW, squareRootCurve, squareRootFormula,
  squareRootProperties, squareRootValue } from './square-root-math';
import { useGradeEightGraphState } from './use-grade-eight-graph-state';
import './grade-eight-functions.css';

const initial = { k: 1, shift: 0, x: 0 } as const;
const plot = { left: 48, top: 20, width: 504, height: 320 };
const { xMin, xMax, yMin, yMax } = SQUARE_ROOT_WINDOW;
const sx = (x: number) => plot.left + (x - xMin) / (xMax - xMin) * plot.width;
const sy = (y: number) => plot.top + (yMax - y) / (yMax - yMin) * plot.height;
const visible = (y: number | null): y is number => y !== null && y >= yMin && y <= yMax;

/** Isolated subject component: registration with Content is a separate stage. */
export function SquareRootGraph({ id }: { id: string }) {
  const { state, change, reset, stopReset } = useGradeEightGraphState(initial);
  const identity = useId();
  const { k, shift: a, x } = state;
  const coefficients = { k, a };
  const y = squareRootValue(x, coefficients);
  const formula = squareRootFormula(coefficients);
  const coordinates = `x = ${formatNumber(x)}; y = ${y === null ? 'не определено' : formatNumber(y)}`;
  const curve = useMemo(() => squareRootCurve({ k, a })
    .map(([px, py], index) => `${index ? 'L' : 'M'}${sx(px)},${sy(py)}`).join(' '), [k, a]);

  return <div id={id} className="quadratic-lab grade-eight-functions square-root-lab" data-react-square-root="true"
    onCopy={event => event.preventDefault()} onCut={event => event.preventDefault()} onDragStart={event => event.preventDefault()}>
    <div className="quadratic-toolbar">
      <div className="quadratic-current" aria-live="polite">
        <math className="lesson-math" aria-label={formula}><mrow><mi>y</mi><mo>=</mo>
          {k === -1 ? <mo>−</mo> : k !== 1 && <><mn>{formatNumber(k, 1)}</mn><mo>·</mo></>}
          <msqrt><mi>x</mi></msqrt>
          {a !== 0 && <><mo>{a > 0 ? '+' : '−'}</mo><mn>{formatNumber(Math.abs(a), 1)}</mn></>}
        </mrow></math>
      </div>
      <button className="quadratic-reset" type="button" onClick={reset}>Вернуть y = √x</button>
    </div>
    <div className="quadratic-workspace">
      <figure className="quadratic-plot">
        <svg viewBox="0 0 580 378" role="img" aria-labelledby={`${identity}-title ${identity}-desc`}>
          <title id={`${identity}-title`}>{`График ${formula}`}</title>
          <desc id={`${identity}-desc`}>Окно: x от −2 до 18, y от −8 до 8. График определён при x ≥ 0.
            Табличные точки отмечены кружками; исследуемую точку выбирайте ползунком x.
            Значения и свойства функции приведены текстом рядом.</desc>
          <defs><clipPath id={`${identity}-clip`}><rect x={plot.left} y={plot.top} width={plot.width} height={plot.height}/></clipPath></defs>
          <rect className="plot-background" x={plot.left} y={plot.top} width={plot.width} height={plot.height}/>
          <g className="plot-grid">
            {Array.from({ length: 21 }, (_, i) => i - 2).map(n => <line key={`x${n}`} x1={sx(n)} x2={sx(n)} y1={plot.top} y2={plot.top + plot.height}/>)}
            {Array.from({ length: 17 }, (_, i) => i - 8).map(n => <line key={`y${n}`} x1={plot.left} x2={plot.left + plot.width} y1={sy(n)} y2={sy(n)}/>)}
          </g>
          <g className="plot-axes">
            <line x1={plot.left} x2={plot.left + plot.width} y1={sy(0)} y2={sy(0)}/>
            <line x1={sx(0)} x2={sx(0)} y1={plot.top} y2={plot.top + plot.height}/>
          </g>
          <g className="plot-ticks">
            {[-2, 2, 4, 6, 8, 10, 12, 14, 16, 18].map(n => <text key={`x${n}`}
              x={sx(n) + (n === -2 ? 4 : n === 18 ? -4 : 0)} y={sy(0) + 18}
              textAnchor={n === -2 ? 'start' : n === 18 ? 'end' : 'middle'}>{n}</text>)}
            {[-8, -6, -4, -2, 2, 4, 6, 8].map(n => <text key={`y${n}`} x={sx(0) - 10}
              y={sy(n) + (n === 8 ? 16 : n === -8 ? -8 : 4)} textAnchor="end">{formatNumber(n)}</text>)}
            <text x={sx(0) - 9} y={sy(0) + 18}>0</text>
            <text x={plot.left + plot.width - 8} y={sy(0) - 8} textAnchor="end">x</text>
            <text x={sx(0) + 9} y={plot.top + 16}>y</text>
          </g>
          <g clipPath={`url(#${identity}-clip)`}>
            <path className="plot-curve" d={curve} fill="none"/>
            {SQUARE_ROOT_TABLE_X.map(value => {
              const sampleY = squareRootValue(value, coefficients);
              return visible(sampleY) ? <circle className="grade-eight-sample" key={value} cx={sx(value)} cy={sy(sampleY)} r="4.5"/> : null;
            })}
            {visible(y) && <circle className="plot-probe" cx={sx(x)} cy={sy(y)} r="4"/>}
          </g>
        </svg>
        <figcaption className="quadratic-probe">
          <div className="quadratic-probe-label"><label htmlFor={`${identity}-x`}>Точка на графике</label>
            <output className="quadratic-probe-coordinates" htmlFor={`${identity}-x`} aria-live="polite">{coordinates}</output></div>
          <input id={`${identity}-x`} type="range" min={0} max={18} step={0.1} value={x}
            aria-label="Абсцисса исследуемой точки x" aria-valuetext={coordinates} aria-describedby={`${identity}-help`}
            onPointerDown={stopReset} onKeyDown={stopReset} onChange={event => change('x', Number(event.target.value))}/>
          <p id={`${identity}-help`}>Изменяйте x ползунком под графиком.
            {y === null ? ' Отрицательные x недопустимы.' : !visible(y) && ' Точка вне окна графика.'}</p>
        </figcaption>
      </figure>
      <div className="quadratic-data">
        <div className="quadratic-controls">
          <CoefficientControl name="k" value={k} min={-3} max={3} step={0.1} format={value => formatNumber(value, 1)}
            onInputStart={stopReset} onChange={value => change('k', value)}/>
          <CoefficientControl name="a" value={a} min={-5} max={5} step={0.1} format={value => formatNumber(value, 1)}
            onInputStart={stopReset} onChange={value => change('shift', value)}/>
        </div>
        <p className="graph-explanation">Параметр a задаёт сдвиг по вертикали. При k = 1 и a = 0 отображается базовая функция y = √x.</p>
        <dl className="quadratic-properties">{squareRootProperties(coefficients).map(([label, value]) =>
          <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
      </div>
    </div>
    <div className="lesson-table-scroll" tabIndex={0} role="region" aria-label="Таблица значений функции квадратного корня">
      <table className="quadratic-values"><caption>Значения функции y = k√x + a</caption>
        <thead><tr><th scope="col">x</th>{SQUARE_ROOT_TABLE_X.map(value => <th key={value} scope="col">{value}</th>)}</tr></thead>
        <tbody><tr><th scope="row">y</th>{SQUARE_ROOT_TABLE_X.map(value => {
          const result = squareRootValue(value, coefficients);
          return <td key={value}>{result === null ? 'не определено' : formatNumber(result)}</td>;
        })}</tr></tbody>
      </table>
    </div>
    <p className="graph-explanation">Кривая изменяется сразу после перемещения ползунков коэффициентов.
      Табличные точки показывают значения при x = 0, 1, 4, 9 и 16. Координаты исследуемой точки задаются ползунком x.</p>
  </div>;
}
