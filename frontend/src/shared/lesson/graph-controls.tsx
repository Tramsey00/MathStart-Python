import { useId } from 'react';
export function CoefficientControl({ name, value, min, max, step, onChange, onInputStart, format }: {
  name: string; value: number; min: number; max: number; step: number;
  onChange: (value: number) => void; onInputStart: () => void; format: (n: number) => string;
}) {
  const id = useId();
  return <div className="coefficient-control"><label htmlFor={id}><span><span className="coefficient-word">Коэффициент </span>{name}</span><output htmlFor={id}>{format(value)}</output></label>
    <input id={id} aria-label={`Коэффициент ${name}`} type="range" min={min} max={max} step={step} value={value}
      onPointerDown={onInputStart} onKeyDown={onInputStart} onChange={event => onChange(Number(event.target.value))}/>
    <div className="coefficient-scale" aria-hidden="true"><span>{format(min)}</span><span>0</span><span>{format(max)}</span></div></div>;
}
