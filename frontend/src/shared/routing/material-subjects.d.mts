export type MaterialSubjectCode = 'algebra' | 'geometry' | 'statistics' | 'math';
export function materialSubjectCode(identity: string): MaterialSubjectCode;
export function isMaterialSubjectCode(code: unknown): code is MaterialSubjectCode;
