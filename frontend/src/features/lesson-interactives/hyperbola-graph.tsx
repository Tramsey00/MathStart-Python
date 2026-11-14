import { useId, useMemo } from 'react';
import { CoefficientControl } from '../../shared/lesson/graph-controls';
import { formatNumber } from '../../shared/lesson/quadratic-math';
import { HYPERBOLA_TABLE_X, HYPERBOLA_WINDOW, hyperbolaBranches, hyperbolaFormula,
  hyperbolaProperties, hyperbolaValue } from './hyperbola-math';
import { useGradeEightGraphState } from './use-grade-eight-graph-state';
import './grade-eight-functions.css';

const initial = { k: 1, shift: 0, x: 1 } as const;
const plot = { left: 48, top: 20, width: 504, height: 320 };
const { xMin, xMax, yMin, yMax } = HYPERBOLA_WINDOW;
const sx = (x: number) => plot.left + (x - xMin) / (xMax - xMin) * plot.width;
const sy = (y: number) => plot.top + (yMax - y) / (yMax - yMin) * plot.height;
const visible = (y: number | null): y is number => y !== null && y >= yMin && y <= yMax;
const ticks = [-10, -8, -6, -4, -2, 2, 4, 6, 8, 10];

/** Isolated subject component: registration with Content is a separate stage. */
export function HyperbolaGraph({ id }: { id: string }) {
  const { state, change, reset, stopReset } = useGradeEightGraphState(initial);
  const identity = useId();
  const { k, shift: b, x } = state;
  const coefficients = { k, b };
  const y = hyperbolaValue(x, coefficients);
  const formula = hyperbolaFormula(coefficients);
  const coordinates = `x = ${formatNumber(x)}; y = ${y === null ? 'не определено' : formatNumber(y)}`;
  const branches = useMemo(() => hyperbolaBranches({ k, b }).map(points => points
    .map(([px, py], index) => `${index ? 'L' : 'M'}${sx(px)},${sy(py)}`).join(' ')), [k, b]);

  return <div id={id} className="quadratic-lab grade-eight-functions hyperbola-lab" data-react-hyperbola="true"
    onCopy={event => event.preventDefault()} onCut={event => event.preventDefault()} onDragStart={event => event.preventDefault()}>
    <div className="quadratic-toolbar">
      <div className="quadratic-current" aria-live="polite">
        <math className="lesson-math" aria-label={formula}><mrow><mi>y</mi><mo>=</mo>
          {k === 0 ? <mn>{formatNumber(b, 1)}</mn> : <>
            {k < 0 && <mo>−</mo>}<mfrac><mn>{formatNumber(Math.abs(k), 1)}</mn><mi>x</mi></mfrac>
            {b !== 0 && <><mo>{b > 0 ? '+' : '−'}</mo><mn>{formatNumber(Math.abs(b), 1)}</mn></>}
          </>}
          {k === 0 && <><mo>,</mo><mi>x</mi><mo>≠</mo><mn>0</mn></>}
        </mrow></math>
      </div>
      <button className="quadratic-reset" type="button" onClick={reset}>Вернуть y = 1/x</button>
    </div>
    <div className="quadratic-workspace">
      <figure className="quadratic-plot">
        <svg viewBox="0 0 580 378" role="img" aria-labelledby={`${identity}-title ${identity}-desc`}>
          <title id={`${identity}-title`}>{`График ${formula}`}</title>
          <desc id={`${identity}-desc`}>Окно: x и y от −10 до 10. {k === 0
            ? `Прямая y = ${formatNumber(b)} с выколотой точкой (0; ${formatNumber(b)}). Вертикальной асимптоты нет.`
            : `Две отдельные ветви. Асимптоты x = 0 и y = ${formatNumber(b)} обозначены пунктиром.`}
            Таблица и свойства доступны текстом. Исследуемая точка выбирается только ползунком x.</desc>
          <defs><clipPath id={`${identity}-clip`}><rect x={plot.left} y={plot.top} width={plot.width} height={plot.height}/></clipPath></defs>
          <rect className="plot-background" x={plot.left} y={plot.top} width={plot.width} height={plot.height}/>
          <g className="plot-grid">{Array.from({ length: 21 }, (_, i) => i - 10).map(n => <g key={n}>
            <line x1={sx(n)} x2={sx(n)} y1={plot.top} y2={plot.top + plot.height}/>
            <line x1={plot.left} x2={plot.left + plot.width} y1={sy(n)} y2={sy(n)}/>
          </g>)}</g>
          <g className="plot-axes">
            <line x1={plot.left} x2={plot.left + plot.width} y1={sy(0)} y2={sy(0)}/>
            <line x1={sx(0)} x2={sx(0)} y1={plot.top} y2={plot.top + plot.height}/>
          </g>
          <g className="plot-ticks">{ticks.map(n => <g key={n}>
            <text x={sx(n) + (n === -10 ? 4 : n === 10 ? -4 : 0)} y={sy(0) + 18}
              textAnchor={n === -10 ? 'start' : n === 10 ? 'end' : 'middle'}>{formatNumber(n)}</text>
            <text x={sx(0) - 10} y={sy(n) + (n === 10 ? 16 : n === -10 ? -8 : 4)} textAnchor="end">{formatNumber(n)}</text>
          </g>)}<text x={sx(0) - 9} y={sy(0) + 18}>0</text>
            <text x={plot.left + plot.width - 8} y={sy(0) - 8} textAnchor="end">x</text>
            <text x={sx(0) + 9} y={plot.top + 16}>y</text>
          </g>
          <g clipPath={`url(#${identity}-clip)`}>
            {k !== 0 && <g className="plot-symmetry">
              <line x1={sx(0)} x2={sx(0)} y1={plot.top} y2={plot.top + plot.height}/>
              <line x1={plot.left} x2={plot.left + plot.width} y1={sy(b)} y2={sy(b)}/>
            </g>}
            {k === 0 ? <path className="plot-curve" fill="none"
              d={`M${sx(-10)},${sy(b)} H${sx(0) - 5} M${sx(0) + 5},${sy(b)} H${sx(10)}`}/>
              : branches.map((d, index) => <path className="plot-curve" fill="none" key={index} d={d}/>)}
            {k !== 0 && HYPERBOLA_TABLE_X.map(value => {
              const sampleY = hyperbolaValue(value, coefficients);
              return visible(sampleY) ? <circle className="grade-eight-sample" key={value} cx={sx(value)} cy={sy(sampleY)} r="4.5"/> : null;
            })}
            {visible(y) && <circle className="plot-probe" cx={sx(x)} cy={sy(y)} r="4"/>}
          </g>
          {k === 0 && <circle className="hyperbola-hole" cx={sx(0)} cy={sy(b)} r="5"/>}
          {k !== 0 && <text className="plot-ticks" x={plot.left + 8}
            y={Math.max(plot.top + 16, Math.min(plot.top + plot.height - 8, sy(b) - 8))}>y = {formatNumber(b, 1)}</text>}
        </svg>
        <figcaption className="quadratic-probe">
          <div className="quadratic-probe-label"><label htmlFor={`${identity}-x`}>Точка на графике</label>
            <output className="quadratic-probe-coordinates" htmlFor={`${identity}-x`} aria-live="polite">{coordinates}</output></div>
          <input id={`${identity}-x`} type="range" min={-10} max={10} step={0.1} value={x}
            aria-label="Абсцисса исследуемой точки x" aria-valuetext={coordinates} aria-describedby={`${identity}-help`}
            onPointerDown={stopReset} onKeyDown={stopReset} onChange={event => change('x', Number(event.target.value))}/>
          <p id={`${identity}-help`}>Изменяйте x ползунком под графиком.
            {y === null ? ' При x = 0 функция не определена: деление на нуль, в том числе при k = 0.'
              : !visible(y) && ' Точка вне окна графика.'}</p>
        </figcaption>
      </figure>
      <div className="quadratic-data">
        <div className="quadratic-controls">
          <CoefficientControl name="k" value={k} min={-10} max={10} step={0.1} format={value => formatNumber(value, 1)}
            onInputStart={stopReset} onChange={value => change('k', value)}/>
          <CoefficientControl name="b" value={b} min={-10} max={10} step={0.1} format={value => formatNumber(value, 1)}
            onInputStart={stopReset} onChange={value => change('shift', value)}/>
        </div>
        <p className="graph-explanation">Параметр k отвечает за форму и расположение ветвей, а b сдвигает гиперболу вверх или вниз.</p>
        <dl className="quadratic-properties">{hyperbolaProperties(coefficients).map(([label, value]) =>
          <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
      </div>
    </div>
    <div className="lesson-table-scroll" tabIndex={0} role="region" aria-label="Таблица значений гиперболы">
      <table className="quadratic-values"><caption>Значения функции y = k/x + b</caption>
        <thead><tr><th scope="col">x</th>{HYPERBOLA_TABLE_X.map(value => <th key={value} scope="col">{formatNumber(value)}</th>)}</tr></thead>
        <tbody><tr><th scope="row">y</th>{HYPERBOLA_TABLE_X.map(value => {
          const result = hyperbolaValue(value, coefficients);
          return <td key={value}>{result === null ? 'не определено' : formatNumber(result)}</td>;
        })}</tr></tbody>
      </table>
    </div>
    <p className="graph-explanation">Кривая перестраивается при перемещении ползунков коэффициентов.
      При k ≠ 0 пунктир показывает асимптоты x = 0 и y = b; кружки отмечают табличные точки.
      Координаты исследуемой точки задаются ползунком x.</p>
    <p className="graph-explanation">Для изучения гиперболы нас интересует случай k ≠ 0.
      При k = 0 получается прямая y = b с выколотой точкой (0; b): область определения по-прежнему x ≠ 0.</p>
  </div>;
}
