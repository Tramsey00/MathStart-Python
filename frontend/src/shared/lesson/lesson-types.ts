export type LessonNode = { kind: 'text'; text: string } | { kind: 'graph' } |
  { kind: 'interactive'; name: 'linear'; id: string } |
  { kind: 'selfCheck'; attrs: Record<string, string>; question: LessonNode[]; answer: LessonNode[]; disclosure: 'answer' | 'solution' } |
  { kind: 'element' | 'paragraph' | 'note' | 'example' | 'table' | 'figure'; tag: string; attrs: Record<string, string>; children: LessonNode[] };
export interface LessonSectionData { id: string; title: string; nodes: LessonNode[] }
export interface LessonTopic { slug: string; title: string; order: number }
export interface LessonData {
  slug: string; title: string; subtitle: string; grade: string; subject: string;
  section: string; sections: LessonSectionData[]; previous: LessonTopic | null; next: LessonTopic | null;
}
export interface LessonDocument extends Omit<LessonData, 'previous' | 'next'> { version: 'lesson-document-v1' }
