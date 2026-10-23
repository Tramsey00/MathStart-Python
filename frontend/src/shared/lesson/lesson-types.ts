export type LessonNode = { kind: 'text'; text: string } | { kind: 'graph' } |
  { kind: 'element'; tag: string; attrs: Record<string, string>; children: LessonNode[] };
export interface LessonSectionData { id: string; title: string; nodes: LessonNode[] }
export interface LessonTopic { slug: string; title: string; order: number }
export interface LessonData {
  slug: string; title: string; subtitle: string; grade: string; subject: string;
  section: string; sections: LessonSectionData[]; previous: LessonTopic | null; next: LessonTopic | null;
}
