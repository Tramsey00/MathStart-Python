import type { LessonDocument } from '../src/shared/lesson/lesson-types';
export function convertLesson(directory: string): LessonDocument;
export function cleanSectionTitle(title: string): string;
export function isPrerequisiteSection(title: string): boolean;
export function isSelfCheckSection(title: string): boolean;
export function isFinalRecapSection(title: string): boolean;
