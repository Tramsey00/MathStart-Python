import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { CoefficientControl } from './graph-controls';
import { analyzeFunction, formatNumber, INITIAL_COEFFICIENTS, polynomial, valueAt, type Coefficients } from './quadratic-math';

const plot = { left: 48, top: 20, width: 504, height: 320 };
const sx = (x: number) => plot.left + (x + 10) / 20 * plot.width;
const sy = (y: number) => plot.top + (10 - y) / 20 * plot.height;
const visible = (x: number, y: number) => x >= -10 && x <= 10 && y >= -10 && y <= 10;

export function QuadraticGraph() {
  const [coefficients, setCoefficients] = useState<Coefficients>(INITIAL_COEFFICIENTS);
  const [selectedX, setSelectedX] = useState(0);
  const resetFrame = useRef<number | null>(null);
  function stopReset() {
    if (resetFrame.current !== null) cancelAnimationFrame(resetFrame.current);
    resetFrame.current = null;
  }
  useEffect(() => () => {
    if (resetFrame.current !== null) cancelAnimationFrame(resetFrame.current);
  }, []);
  function resetCoefficients() {
    stopReset();
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setCoefficients(INITIAL_COEFFICIENTS);
      setSelectedX(0);
      return;
    }
    const from = { ...coefficients };
    const fromX = selectedX;
    const started = performance.now();
    const interpolate = (start: number, end: number, eased: number) => Math.round((start + (end - start) * eased) * 10) / 10;
    const frame = (now: number) => {
      const progress = Math.min((now - started) / 360, 1);
      const eased = 1 - (1 - progress) ** 3;
      if (progress === 1) {
        setCoefficients(INITIAL_COEFFICIENTS);
        setSelectedX(0);
        resetFrame.current = null;
        return;
      }
      setCoefficients({
        a: interpolate(from.a, INITIAL_COEFFICIENTS.a, eased),
        b: interpolate(from.b, INITIAL_COEFFICIENTS.b, eased),
        c: interpolate(from.c, INITIAL_COEFFICIENTS.c, eased),
      });
      setSelectedX(interpolate(fromX, 0, eased));
      resetFrame.current = requestAnimationFrame(frame);
    };
    resetFrame.current = requestAnimationFrame(frame);
  }
  const inspectedX = selectedX;
  const identity = useId();
  const analysis = analyzeFunction(coefficients);
  const inspectedY = valueAt(inspectedX, coefficients);
  const coordinates = `x = ${formatNumber(inspectedX)}; y = ${formatNumber(inspectedY)}`;
  const curve = useMemo(() => {
    let pen = false;
    const commands: string[] = [];
    for (let i = 0; i <= 800; i++) {
      const x = -10 + i / 40, y = valueAt(x, coefficients);
      if (y < -12 || y > 12) { pen = false; continue; }
      commands.push(`${pen ? 'L' : 'M'}${sx(x).toFixed(2)},${sy(y).toFixed(2)}`);
      pen = true;
    }
    return commands.join(' ');
  }, [coefficients]);
  const pointLabel = (point: readonly [number, number]) => `(${formatNumber(point[0])}; ${formatNumber(point[1])})`;
  const roots = analysis.roots === 'all' ? 'Любое действительное x' : analysis.roots.length
    ? analysis.roots.map((root, index) => `x${analysis.roots.length > 1 ? (index === 0 ? '₁' : '₂') : ''} = ${formatNumber(root)}`).join(', ')
    : 'Действительных корней нет';
  const properties = [
    ['Тип графика', analysis.kind === 'quadratic' ? 'Парабола' : analysis.kind === 'linear' ? 'Линейная функция' : 'Постоянная функция'],
    ['Вершина', analysis.kind === 'quadratic' ? `V${pointLabel(analysis.vertex)}` : 'Вершины нет'],
    ['Ось симметрии', analysis.kind === 'quadratic' ? `x = ${formatNumber(analysis.vertex[0])}` : analysis.kind === 'constant' ? 'Любая прямая x = k' : 'Оси симметрии нет'],
    ['Направление', analysis.kind === 'quadratic' ? (coefficients.a > 0 ? 'Ветви вверх' : 'Ветви вниз') : analysis.kind === 'linear' ? (coefficients.b > 0 ? 'Прямая возрастает' : 'Прямая убывает') : 'Горизонтальная прямая'],
    ['Дискриминант', analysis.kind === 'quadratic' ? `D = ${formatNumber(analysis.discriminant)}` : 'Не применяется'],
    ['Корни', roots],
    ['Пересечение с Oy', pointLabel([0, coefficients.c])],
    ['Множество значений', analysis.kind === 'quadratic' ? coefficients.a > 0 ? `[${formatNumber(analysis.vertex[1])}; +∞)` : `(−∞; ${formatNumber(analysis.vertex[1])}]` : analysis.kind === 'linear' ? 'ℝ' : `{${formatNumber(coefficients.c)}}`],
  ];
  return <div className="quadratic-lab" id="ms-quadratic-lab-660" data-react-quadratic="true" onCopy={event => event.preventDefault()} onCut={event => event.preventDefault()} onDragStart={event => event.preventDefault()}>
    <div className="quadratic-toolbar"><p className="quadratic-current" aria-live="polite">y = {polynomial(coefficients)}</p><button className="quadratic-reset" type="button" onClick={resetCoefficients}>Сбросить коэффициенты</button></div>
    <div className="quadratic-workspace">
      <figure className="quadratic-plot"><svg viewBox="0 0 580 378" role="img" aria-labelledby={`${identity}-title ${identity}-desc`}>
        <title id={`${identity}-title`}>{`График y = ${polynomial(coefficients)}`}</title>
        <desc id={`${identity}-desc`}>Координатная плоскость от −10 до 10 по обеим осям. Свойства функции и таблица значений доступны текстом рядом с графиком. Коэффициенты изменяются ползунками.</desc>
        <defs><clipPath id={`${identity}-clip`}><rect x={plot.left} y={plot.top} width={plot.width} height={plot.height}/></clipPath></defs>
        <rect className="plot-background" x={plot.left} y={plot.top} width={plot.width} height={plot.height}/>
        {Array.from({ length: 21 }, (_, index) => index - 10).map(n => <g className="plot-grid" key={n}>
          <line x1={sx(n)} x2={sx(n)} y1={plot.top} y2={plot.top + plot.height}/><line x1={plot.left} x2={plot.left + plot.width} y1={sy(n)} y2={sy(n)}/>
        </g>)}
        <g className="plot-axes"><line x1={plot.left} x2={plot.left + plot.width} y1={sy(0)} y2={sy(0)}/><line x1={sx(0)} x2={sx(0)} y1={plot.top} y2={plot.top + plot.height}/></g>
        <g className="plot-ticks">{[-10, -8, -6, -4, -2, 2, 4, 6, 8, 10].map(n => <g key={n}><text x={sx(n)} y={sy(0) + 18} textAnchor={n === -10 ? "start" : n === 10 ? "end" : "middle"}>{n}</text><text x={sx(0) - 10} y={sy(n) + (n === 10 ? 14 : n === -10 ? -5 : 4)} textAnchor="end">{n}</text></g>)}<text x={sx(0) - 9} y={sy(0) + 18}>0</text><text x="546" y={sy(0) - 8} textAnchor="end">x</text><text x={sx(0) + 9} y="34">y</text></g>
        <g clipPath={`url(#${identity}-clip)`}>
          {analysis.kind === 'quadratic' && <line className="plot-symmetry" x1={sx(analysis.vertex[0])} x2={sx(analysis.vertex[0])} y1={plot.top} y2={plot.top + plot.height}/>}
          <path className="plot-curve" d={curve} fill="none"/>
          {analysis.kind === 'quadratic' && visible(...analysis.vertex) && <circle className="plot-vertex" cx={sx(analysis.vertex[0])} cy={sy(analysis.vertex[1])} r="5"/>}
          {analysis.roots !== 'all' && analysis.roots.filter(x => visible(x, 0)).map((x, index) => <circle className="plot-root" key={index} cx={sx(x)} cy={sy(0)} r="4.5"/>)}
          {visible(0, coefficients.c) && <circle className="plot-intercept" cx={sx(0)} cy={sy(coefficients.c)} r="4.5"/>}
          {visible(inspectedX, inspectedY) && <circle className="plot-probe" cx={sx(inspectedX)} cy={sy(inspectedY)} r="4"/>}
        </g>
      </svg><figcaption className="quadratic-probe">
        <div className="quadratic-probe-label"><label htmlFor={`${identity}-probe`}>Точка на графике</label><span className="quadratic-probe-coordinates">{coordinates}</span></div>
        <input id={`${identity}-probe`} type="range" min="-10" max="10" step="0.1" value={inspectedX}
          aria-label="Абсцисса исследуемой точки x" aria-valuetext={coordinates} aria-describedby={`${identity}-probe-help`}
          onPointerDown={stopReset} onChange={event => { stopReset(); setSelectedX(Number(event.target.value)); }}/>
        <p id={`${identity}-probe-help`}>Изменяйте x ползунком под графиком.{!visible(inspectedX, inspectedY) && <span className="quadratic-probe-outside"> Точка вне окна графика.</span>}</p>
      </figcaption></figure>
      <div className="quadratic-data"><div className="quadratic-controls">{(['a', 'b', 'c'] as const).map(key => <CoefficientControl key={key} name={key} value={coefficients[key]} min={key === 'a' ? -4 : -10} max={key === 'a' ? 4 : 10} step={0.1} format={value => formatNumber(value, 1)} onInputStart={stopReset} onChange={value => { stopReset(); setCoefficients(current => ({ ...current, [key]: value })); }}/>)}</div>
    <dl className="quadratic-properties">{properties.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
    <div className="lesson-table-scroll"><table className="quadratic-values"><caption>Значения функции</caption><thead><tr><th scope="col">x</th>{[-2, 0, 1, 2, 3, 4].map(x => <th scope="col" key={x}>{x}</th>)}</tr></thead><tbody><tr><th scope="row">y</th>{[-2, 0, 1, 2, 3, 4].map(x => <td data-x={x} key={x}>{formatNumber(valueAt(x, coefficients))}</td>)}</tr></tbody></table></div>
    <p className="graph-explanation">При a = 0 квадратный член исчезает. Для сравнения здесь можно построить и прямую.</p></div>
    </div>
    <p className="quadratic-legend"><span className="legend-curve">График</span><span className="legend-vertex">Вершина</span><span className="legend-root">Корни</span><span className="legend-intercept">Пересечение с Oy</span><span className="legend-symmetry">Ось симметрии — пунктир</span></p>
  </div>;
}
