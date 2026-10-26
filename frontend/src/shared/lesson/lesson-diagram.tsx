import type { ReactNode } from 'react';

/** Authored illustrations remain visible without enlargement controls. */
export function LessonDiagram({ children, label, frame = true }: { children: ReactNode; label: string; frame?: boolean }) {
  return <div className="lesson-diagram" data-frame={frame ? 'shared' : 'existing'} role="group" aria-label={label}>
    <div className="lesson-diagram-viewport">{children}</div>
  </div>;
}
