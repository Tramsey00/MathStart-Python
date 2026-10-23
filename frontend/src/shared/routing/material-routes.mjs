// A number is assigned once within (grade, subject), never from display order.
export function buildMaterialPath({ grade, subject, number }) {
  if (!Number.isSafeInteger(grade) || grade < 1 || !Number.isSafeInteger(number) || number < 1) {
    throw new TypeError('Material grade and number must be positive safe integers');
  }
  if (typeof subject !== 'string' || !/^[a-z]+(?:-[a-z]+)*$/.test(subject)) {
    throw new TypeError('Material subject must be a lowercase Latin code');
  }
  return `/materials/${grade}-${subject}-${number}`;
}

// Explicit assignments; reordering/renaming a lesson must not change its URL.
const assignments = [{
  slug: 'kvadratichnaya-funkcziya-y-ax2-bx-c', grade: 8, subject: 'algebra', number: 32,
}];
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
export const quadraticRoute = materialRoutes[0];
