import { readFileSync } from 'node:fs';
import { dirname, resolve, relative, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import Ajv2020 from 'ajv/dist/2020.js';
import type { PublicPageView } from './public-types';
import type { LessonDocument } from '../shared/lesson/lesson-types';

const repository = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const curriculum = resolve(repository, 'curriculum');
const schema = JSON.parse(readFileSync(resolve(repository, 'specs/migration/r02-v1/delivery-v1.schema.json'), 'utf8'));
const validate = new Ajv2020({ strict: false, validateFormats: false }).compile({ $ref: '#/$defs/LessonDocument', $defs: schema.$defs });

/** Developer preview only: never writes Content or replaces publication authority. */
export function currentLessonView(view: PublicPageView): PublicPageView {
  if (view.page.renderer_version !== 'react-v1' || !view.page.lesson_document) return view;
  const source = view.page.source?.path;
  if (!source) throw Error('Pinned lesson source required for development');
  const path = resolve(repository, dirname(source), 'content.json');
  const inside = relative(curriculum, path);
  if (inside.startsWith('..') || isAbsolute(inside)) throw Error('Development source escaped curriculum');
  const document: unknown = JSON.parse(readFileSync(path, 'utf8'));
  if (!validate(document)) throw Error('Current content.json does not satisfy LessonDocument');
  const lesson = document as LessonDocument;
  const original = view.page.lesson_document;
  if (['slug', 'grade', 'subject', 'section'].some(key => lesson[key as keyof LessonDocument] !== original[key as keyof LessonDocument])) {
    throw Error('Lesson identity changed; prepare a new Content release');
  }
  return { ...view, page: { ...view.page, title: lesson.title, lesson_document: lesson,
    seo: { ...view.page.seo, title: view.page.seo.title === original.title ? lesson.title : view.page.seo.title } } };
}
