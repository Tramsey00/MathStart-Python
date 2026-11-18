import type { LessonDocument } from '../../src/shared/lesson/lesson-types';
export function convertLesson(html: string, metadata: Pick<LessonDocument, "slug" | "title" | "grade" | "subject" | "section">): LessonDocument;
export function cleanSectionTitle(title: string): string;
export function isPrerequisiteSection(title: string): boolean;
export function isSelfCheckSection(title: string): boolean;
