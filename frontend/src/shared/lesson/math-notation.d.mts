import type { LessonNode } from './lesson-types';
type MathNode = Extract<LessonNode, { tag: string }>;
export function mathToken(tag: 'mn' | 'mi' | 'mo' | 'mtext', text: string | number): MathNode;
export function mathExpression(children: LessonNode[], options?: { display?: 'inline' | 'block'; label?: string; attrs?: Record<string, string> }): MathNode;
export function fractionNode(numerator: LessonNode[], denominator: LessonNode[]): MathNode;
export function rootNode(radicand: LessonNode[], index?: LessonNode[]): MathNode;
export function powerNode(base: LessonNode[], exponent: LessonNode[]): MathNode;
export function mixedNumberNode(whole: string | number, numerator: string | number, denominator: string | number, attrs?: Record<string, string>): MathNode;
export function normalizeMathNotation(nodes: readonly LessonNode[]): LessonNode[];
