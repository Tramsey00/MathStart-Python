// Explicit build-time conversion. Unknown source markup is a review error.
import { readFileSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { parseFragment } from 'parse5';
import { normalizeMathNotation } from '../src/shared/lesson/math-notation.mjs';

const children = n => n.childNodes ?? [];
const attrs = n => Object.fromEntries((n.attrs ?? []).map(a => [a.name, a.value]));
const has = (n, c) => (attrs(n).class ?? '').split(/\s+/).includes(c);
const text = n => n.nodeName === '#text' ? n.value : children(n).map(text).join('');
export const cleanSectionTitle = title => title.replace(/^\s*\d+[.)]\s*/, '').trim();
export const isPrerequisiteSection = title => /^Что нужно знать перед темой$/iu.test(cleanSectionTitle(title));
export const isSelfCheckSection = title => /^(?:Задания для самопроверки|Самопроверка)$/iu.test(cleanSectionTitle(title));
const tags = new Set('div p span strong em b i br h3 h4 ul ol li a table thead tbody tfoot tr th td caption sup sub svg g rect circle line path polyline polygon text tspan defs marker title desc math mi mn mo mrow msup msub mfrac msqrt mroot mspace mtext semantics annotation small clipPath'.split(' '));
const attributes = new Set('class id role style href title scope colspan rowspan xmlns viewBox viewbox width height x y x1 y1 x2 y2 cx cy r rx ry d points fill stroke stroke-width stroke-linecap stroke-linejoin stroke-dasharray font-size font-weight font-family text-anchor dominant-baseline transform opacity marker-end refX refY markerWidth markerHeight markerUnits orient mathvariant display encoding clip-path'.toLowerCase().split(' '));
function convert(n) {
  if (n.nodeName === '#text') return { kind: 'text', text: n.value };
  if (n.nodeName === '#comment') return null;
  if (!n.tagName) throw Error(`Unsupported source node: ${n.nodeName}`);
  const a = attrs(n);
  if (['ms-nav', 'ms-lesson-nav', 'ms-quadratic-number', 'ms-next-topic'].some(name => has(n, name))) return null;
  if (a.id === 'ms-quadratic-lab-660') return { kind: 'interactive', name: 'quadratic', id: a.id };
  if (a.id === 'ms-linear-lab-723') {
    // Instructional prose remains document content, outside the replacement UI.
    return { kind: 'element', tag: 'div', attrs: {}, children: [
      { kind: 'interactive', name: 'linear', id: a.id },
      ...children(n).filter(c => c.tagName === 'p').map(convert),
    ] };
  }
  if (!tags.has(n.tagName)) throw Error(`Unsupported source tag: ${n.tagName}`);
  for (const [key, value] of Object.entries(a)) {
    if (!attributes.has(key.toLowerCase()) && !key.startsWith('aria-')) throw Error(`Unsupported attribute: ${key}`);
    if (/^on/i.test(key) || /(?:javascript:|expression\(|@import|url\(\s*[^#])/i.test(value)) throw Error('Active source markup');
    if (key === 'href' && !/^(?:\/(?!\/)|#|https:\/\/)/.test(value)) throw Error('Unsupported source link');
  }
  if (has(n, 'ms-task')) {
    const answer = children(n).find(c => has(c, 'ms-answer'));
    if (!answer) throw Error('Missing self-check answer');
    const summary = children(answer).find(c => c.tagName === 'summary');
    return { kind: 'selfCheck', attrs: a, disclosure: text(summary).includes('решение') ? 'solution' : 'answer',
      question: children(n).filter(c => c !== answer).map(convert).filter(Boolean),
      answer: children(answer).filter(c => c !== summary).map(convert).filter(Boolean) };
  }
  const kind = n.tagName === 'p' ? 'paragraph' : has(n, 'ms-note') || has(n, 'ms-rule-box') ? 'note'
    : has(n, 'ms-example') || has(n, 'ms-math-box') ? 'example' : n.tagName === 'table' ? 'table' : n.tagName === 'svg' ? 'figure' : 'element';
  return { kind, tag: n.tagName, attrs: a, children: children(n).map(convert).filter(Boolean) };
}
export function convertLesson(directory) {
  const meta = JSON.parse(readFileSync(join(directory, 'lesson.json'), 'utf8')).page;
  const root = children(parseFragment(readFileSync(join(directory, 'body.html'), 'utf8'))).find(n => has(n, 'ms-lesson-page'));
  if (!root) throw Error('Missing authored lesson root');
  const hero = children(root).find(n => has(n, 'ms-hero'));
  let afterSelfCheck = false;
  const sections = [];
  for (const n of children(root)) {
    // Самопроверка целиком завершает материал, независимо от названий следующих блоков.
    if (afterSelfCheck) break;
    if (!n.tagName || n === hero || has(n, 'ms-lesson-toc')) continue;
    if (n.tagName !== 'section') throw Error(`Unreviewed lesson root block: ${n.tagName}`);
    const heading = children(n).find(c => c.tagName === 'h2');
    if (!heading || !attrs(n).id) throw Error('Missing section heading or anchor');
    const title = cleanSectionTitle(text(heading));
    if (isPrerequisiteSection(title)) continue;
    const selfCheck = isSelfCheckSection(title);
    sections.push({ id: attrs(n).id, title: selfCheck ? 'Самопроверка' : title,
      nodes: normalizeMathNotation(children(n).filter(c => c !== heading).map(convert).filter(Boolean)) });
    if (selfCheck) afterSelfCheck = true;
  }
  return { version: 'lesson-document-v1', slug: meta.slug, title: meta.title,
    subtitle: text(children(hero).find(n => has(n, 'ms-subtitle'))).replace(/\s+/g, ' ').trim(),
    grade: meta.grade, subject: meta.subject, section: meta.section, sections };
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const directory = resolve(process.argv[2]);
  writeFileSync(join(directory, 'content.json'), JSON.stringify(convertLesson(directory), null, 2) + '\n');
}
