import registry from '../../../../site_content/material-routes.json' with { type: 'json' };
import { isMaterialSubjectCode } from './material-subjects.mjs';
// A number is assigned once within (grade, subject), never from display order.
export function buildMaterialPath({ grade, subject, number }) {
  if (!Number.isSafeInteger(grade) || grade < 1 || !Number.isSafeInteger(number) || number < 1) {
    throw new TypeError('Material grade and number must be positive safe integers');
  }
  if (!isMaterialSubjectCode(subject)) {
    throw new TypeError('Material subject must be algebra, geometry, statistics or math');
  }
  return `/materials/${grade}-${subject}-${number}`;
}

// Explicit assignments; reordering/renaming a lesson must not change its URL.
if (registry.version !== 1 || !Array.isArray(registry.assignments)) throw Error('Unsupported Content route registry');
const assignments = registry.assignments;
const paths = new Set();
const slugs = new Set();
export const materialRoutes = Object.freeze(assignments.map(assignment => {
  const path = buildMaterialPath(assignment);
  if (paths.has(path) || slugs.has(assignment.slug)) throw new Error('Duplicate material route assignment');
  paths.add(path);
  slugs.add(assignment.slug);
  return Object.freeze({ ...assignment, path });
}));
export function materialPathForSlug(slug) {
  return materialRoutes.find(route => route.slug === slug)?.path;
}
// The adapter and prototype server still serve only this one assigned lesson.
export const quadraticRoute = materialRoutes.find(route => route.slug === 'kvadratichnaya-funkcziya-y-ax2-bx-c');
