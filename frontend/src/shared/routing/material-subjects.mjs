import subjects from '../../../../site_content/material-subjects.json' with { type: 'json' };

const publicCodes = new Set(['algebra', 'geometry', 'statistics', 'math']);
if (!subjects || subjects.version !== 1 || Object.keys(subjects).length !== 2 ||
    !subjects.codes || typeof subjects.codes !== 'object' || Array.isArray(subjects.codes)) {
  throw new Error('Unsupported material subject registry');
}
const entries = Object.entries(subjects.codes);
if (entries.length !== publicCodes.size || new Set(entries.map(([, code]) => code)).size !== publicCodes.size ||
    entries.some(([identity, code]) => !/^[a-z]+(?:-[a-z]+)*$/.test(identity) || !publicCodes.has(code))) {
  throw new Error('Invalid material subject codes');
}
const codes = Object.freeze({ ...subjects.codes });
const labels = Object.freeze({ algebra: 'Алгебра', geometry: 'Геометрия', statistics: 'Вероятность и статистика', math: 'Математика' });

export function materialSubjectCode(identity) {
  if (typeof identity !== 'string' || !Object.hasOwn(codes, identity)) {
    throw new TypeError('Unknown Content subject identity');
  }
  return codes[identity];
}

export function isMaterialSubjectCode(code) {
  return publicCodes.has(code);
}

export function materialSubjectLabel(identity) {
  return labels[materialSubjectCode(identity)];
}
