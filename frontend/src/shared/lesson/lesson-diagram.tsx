import type { ReactNode } from 'react';

/** Authored illustrations remain visible without enlargement controls. */
export function LessonDiagram({ children, label }: { children: ReactNode; label: string }) {
  return <div className="lesson-diagram" role="group" aria-label={label}>
    <div className="lesson-diagram-viewport">{children}</div>
  </div>;
}
