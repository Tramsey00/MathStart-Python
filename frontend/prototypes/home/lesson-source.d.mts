import type { LessonData } from '../../src/shared/lesson/lesson-types';
export const quadraticSlug: string;
export function readQuadraticLesson(repository: string, catalogue: { topics: Array<{
  title: string; slug: string; grade: string; subject: string; section: string; order: number;
}> }): LessonData;
