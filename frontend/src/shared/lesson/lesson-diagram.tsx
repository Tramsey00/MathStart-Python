import { useEffect, useId, useRef, useState, type ReactNode } from 'react';

/** Keeps the authored SVG intact; enlargement belongs to its local viewport. */
export function LessonDiagram({ children, label }: { children: ReactNode; label: string }) {
  const [enlarged, setEnlarged] = useState(false);
  const viewport = useRef<HTMLDivElement>(null);
  const identity = useId();
  useEffect(() => {
    const element = viewport.current;
    if (element) element.scrollLeft = enlarged ? (element.scrollWidth - element.clientWidth) / 2 : 0;
  }, [enlarged]);
  return <div className="lesson-diagram" data-enlarged={enlarged}>
    <div className="lesson-diagram-tools"><button type="button" aria-pressed={enlarged} aria-controls={identity}
      aria-label={`${enlarged ? 'Показать целиком' : 'Увеличить'}: ${label}`}
      onClick={() => setEnlarged(value => !value)}>{enlarged ? 'Схема целиком' : 'Увеличить схему'}</button></div>
    <div className="lesson-diagram-viewport" ref={viewport} id={identity} role="region" aria-label={label}
      tabIndex={enlarged ? 0 : undefined} aria-describedby={enlarged ? `${identity}-help` : undefined}>{children}</div>
    <p className="lesson-diagram-help" id={`${identity}-help`} hidden={!enlarged}>Прокручивайте схему по горизонтали жестом или клавишами со стрелками.</p>
  </div>;
}
