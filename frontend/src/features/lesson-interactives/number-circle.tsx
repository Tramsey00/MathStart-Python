import { useEffect, useId, useRef, useState } from 'react';
import { LessonDiagram } from '../../shared/lesson/lesson-diagram';
import { CIRCLE_PRESETS, CIRCLE_STEPS, STANDARD_STEPS, circlePoint, circleRadians, exactCoordinate } from './number-circle-math';

const CX = 218;
const CY = 188;
const RADIUS = 130;
const px = (x: number) => CX + RADIUS * x;
const py = (y: number) => CY - RADIUS * y;
const localeNumber = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 4, useGrouping: false });
const format = (number: number) => localeNumber.format(number === 0 ? 0 : number).replace('-', '−');
const standardPoints = STANDARD_STEPS.map(circlePoint);

function Radians({ step }: { step: number }) {
  const { numerator, denominator } = circleRadians(step);
  if (!numerator) return <math><mn>0</mn></math>;
  const top = <mrow>{Math.abs(numerator) !== 1 && <mn>{Math.abs(numerator)}</mn>}<mi>π</mi></mrow>;
  return <math><mrow>{numerator < 0 && <mo>−</mo>}
    {denominator === 1 ? top : <mfrac>{top}<mn>{denominator}</mn></mfrac>}
  </mrow></math>;
}

function Coordinate({ value, exact }: { value: number; exact: boolean }) {
  if (!exact) return <mn>{format(value)}</mn>;
  const { negative, magnitude, half } = exactCoordinate(value);
  const top = magnitude > 1 ? <msqrt><mn>{magnitude}</mn></msqrt> : <mn>{magnitude}</mn>;
  return <mrow>{negative && <mo>−</mo>}{half ? <mfrac>{top}<mn>2</mn></mfrac> : top}</mrow>;
}

function CirclePlot({ point }: { point: ReturnType<typeof circlePoint> }) {
  const x = px(point.x);
  const y = py(point.y);
  const angle = point.remainder * Math.PI / 12;
  const direction = Math.sign(point.remainder);
  const dx = -Math.sin(angle) * direction;
  const dy = -Math.cos(angle) * direction;
  const label = `Точка M: поворот ${format(point.degrees)}°, ${point.quadrant.toLowerCase()}`;
  return <LessonDiagram label="Числовая окружность">
    <svg viewBox="0 0 436 378" role="img" aria-label={label}>
      <path className="plot-axes" d="M39 188 H393 M218 361 V20" fill="none"/>
      <path d="M393 188 l-6 -3 v6z M218 20 l-3 6 h6z" fill="var(--lesson-muted)"/>
      <circle cx={CX} cy={CY} r={RADIUS} fill="none" stroke="var(--lesson-muted)"/>
      {standardPoints.map(p => <circle key={p.normalized} cx={px(p.x)} cy={py(p.y)} r="2.5" fill="var(--lesson-muted)"/>)}
      <g className="plot-ticks">
        <text x="401" y="193">x</text><text x="229" y="24">y</text><text x="205" y="207">O</text>
        <text x="362" y="211">A(1; 0)</text><text x="235" y="53">B(0; 1)</text>
        <text x="75" y="175" textAnchor="end">C(−1; 0)</text><text x="235" y="333">D(0; −1)</text>
        <text x="276" y="129">I</text><text x="151" y="129">II</text>
        <text x="150" y="254">III</text><text x="274" y="254">IV</text>
      </g>
      {point.remainder !== 0 && <>
        <path className="plot-curve" fill="none" d={`M${px(1)} ${CY} A${RADIUS} ${RADIUS} 0 ${Math.abs(point.remainder) > 12 ? 1 : 0} ${direction < 0 ? 1 : 0} ${x} ${y}`}/>
        <path fill="var(--lesson-accent)" d={`M${x} ${y} L${x - dx * 11 - dy * 4} ${y - dy * 11 + dx * 4} L${x - dx * 11 + dy * 4} ${y - dy * 11 - dx * 4} Z`}/>
      </>}
      <path className="plot-symmetry" fill="none" d={`M${x} ${CY} V${y} H${CX}`}/>
      <line x1={CX} y1={CY} x2={x} y2={y} stroke="var(--lesson-accent)"/>
      <circle className="plot-probe" cx={x} cy={y} r="5"/>
      <text className="plot-ticks" x={x + (point.x < 0 ? -13 : 13)} y={y + (point.y < 0 ? 21 : -12)}
        textAnchor={point.x < 0 ? 'end' : 'start'}>M</text>
    </svg>
  </LessonDiagram>;
}

export function NumberCircle({ id }: { id: string }) {
  const sliderId = useId();
  const { min, max, initial, turn } = CIRCLE_STEPS;
  const [step, setStep] = useState<number>(initial);
  const resetFrame = useRef<number | null>(null);
  const point = circlePoint(step);

  function stopReset() {
    if (resetFrame.current !== null) cancelAnimationFrame(resetFrame.current);
    resetFrame.current = null;
  }

  useEffect(() => stopReset, []);

  function select(next: number) {
    stopReset();
    if (next >= min && next <= max) setStep(next);
  }

  function reset() {
    stopReset();
    if (step === initial || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setStep(initial);
      return;
    }
    const start = performance.now();
    const frame = (now: number) => {
      const progress = Math.min((now - start) / 360, 1);
      const eased = 1 - (1 - progress) ** 3;
      setStep(Math.round(step + (initial - step) * eased));
      resetFrame.current = progress < 1 ? requestAnimationFrame(frame) : null;
    };
    resetFrame.current = requestAnimationFrame(frame);
  }

  return <div id={id} className="quadratic-lab">
    <div className="quadratic-toolbar">
      <p className="quadratic-current">t = <Radians step={step}/></p>
      <button className="quadratic-reset" type="button" onClick={reset}>Вернуть t = <Radians step={initial}/></button>
    </div>
    <div className="quadratic-workspace">
      <div>
        <CirclePlot point={point}/>
        <p aria-live="polite"><math aria-label={point.exact ? 'Точные координаты M' : 'Приближённые координаты M'}>
          <mrow><mi>M</mi>{!point.exact && <mo>≈</mo>}<mo>(</mo><Coordinate value={point.x} exact={point.exact}/>
            <mo>;</mo><Coordinate value={point.y} exact={point.exact}/><mo>)</mo></mrow>
        </math> · {point.exact ? 'точные координаты' : 'округлено до 4 знаков'}</p>
      </div>
      <div className="quadratic-data">
        <div className="coefficient-control">
          <label htmlFor={sliderId}>Угол поворота <output htmlFor={sliderId}>{format(point.degrees)}°</output></label>
          <input id={sliderId} type="range" min={min} max={max} step={1} value={step}
            aria-valuetext={`${format(point.degrees)} градусов`}
            onPointerDown={stopReset} onKeyDown={stopReset} onChange={event => select(Number(event.target.value))}/>
        </div>
        <fieldset className="power-presets">
          <legend>Стандартные углы</legend>
          {CIRCLE_PRESETS.map(k => <button className="quadratic-reset" key={k} type="button"
            aria-label={`Угол ${k * 15} градусов`} aria-pressed={step === k} onClick={() => select(k)}><Radians step={k}/></button>)}
        </fieldset>
        <div className="power-presets" role="group" aria-label="Полный оборот">
          <button className="quadratic-reset" type="button" disabled={step - turn < min} onClick={() => select(step - turn)}>−2π</button>
          <button className="quadratic-reset" type="button" disabled={step + turn > max} onClick={() => select(step + turn)}>+2π</button>
        </div>
        <dl className="quadratic-properties">
          <div><dt>Угол от 0 до 2π</dt><dd><Radians step={point.normalized}/></dd></div>
          <div><dt>Положение точки</dt><dd>{point.quadrant}</dd></div>
          <div><dt>Полные обороты</dt><dd>{format(point.turns)}</dd></div>
          <div><dt>Направление</dt><dd>{point.direction}</dd></div>
        </dl>
      </div>
    </div>
  </div>;
}
