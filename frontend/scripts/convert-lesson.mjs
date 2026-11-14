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
export const isSelfCheckSection = title => /^(?:Задания для самопроверки|Самопроверка|Практические задания|Задания и проверка|Проверь исследование|Задания по результатам опыта|Итоговая самопроверка)$/iu.test(cleanSectionTitle(title));
const tags = new Set('div p span code strong em b i br h3 h4 ul ol li a table thead tbody tfoot tr th td caption sup sub svg g rect circle line path polyline polygon text tspan defs marker title desc math mi mn mo mrow msup msub mfrac msqrt mroot mspace mtext semantics annotation small clipPath'.split(' '));
const attributes = new Set('class id role style href title scope colspan rowspan xmlns viewBox viewbox width height x y x1 y1 x2 y2 cx cy r rx ry d points fill stroke stroke-width stroke-linecap stroke-linejoin stroke-dasharray font-size font-weight font-family text-anchor dominant-baseline transform opacity marker-end refX refY markerWidth markerHeight markerUnits orient mathvariant display encoding clip-path'.toLowerCase().split(' '));
tags.add('img');
tags.add('linearGradient');
tags.add('stop');
function safeImageUrl(value) {
  // Match the backend URL policy, rejecting controls before trimming as well.
  if (/[\\\u0000-\u001f\u007f-\u009f]/.test(value)) return false;
  const url = value.trim();
  if (/^(?:javascript:|data:|vbscript:|\/\/)/i.test(url)) return false;
  return /^(?:\/|#|https:\/\/|mailto:)/i.test(url);
}
const html = n => n?.namespaceURI === 'http://www.w3.org/1999/xhtml';
const svg = n => n?.namespaceURI === 'http://www.w3.org/2000/svg';
const parts = n => children(n).filter(c => c.nodeName !== '#comment' && !(c.nodeName === '#text' && !c.value.trim()));

function isNamedTableRegion(n, a) {
  const [table] = parts(n);
  return html(n) && n.tagName === 'div' && has(n, 'ms-table-wrap') && a.tabindex === '0'
    && a.role === 'region' && !!a['aria-label']?.trim() && parts(n).length === 1
    && html(table) && table.tagName === 'table';
}

function staticSourceTag(n) {
  if (!html(n)) return n.tagName;
  if (n.tagName === 'aside' && ['v2-rule ms-rule-box', 'v2-note ms-note', 'ms-rule-box', 'ms-note'].includes(attrs(n).class)) return 'div';
  if (n.tagName === 'article' && ['v2-example ms-example', 'ms-card'].includes(attrs(n).class)) return 'div';
  return n.tagName;
}

function isAuthoredFigure(n) {
  if (!html(n) || n.tagName !== 'figure' || !has(n, 'ms-figure')) return false;
  const blocks = parts(n);
  if (attrs(n).class === 'v2-figure ms-figure' && blocks.length === 2) {
    const [drawing, caption] = blocks;
    return svg(drawing) && drawing.tagName === 'svg'
      && html(caption) && caption.tagName === 'figcaption';
  }
  const [title, wrapper, caption] = blocks;
  const drawing = wrapper ? parts(wrapper) : [];
  return blocks.length === 3 && html(title) && title.tagName === 'p' && has(title, 'ms-figure-title')
    && html(wrapper) && wrapper.tagName === 'div' && has(wrapper, 'ms-svg-wrap')
    && drawing.length === 1 && svg(drawing[0]) && drawing[0].tagName === 'svg'
    && html(caption) && caption.tagName === 'figcaption';
}

const circleSteps = /^(?:0|2|3|4|6|8|9|10|12|14|15|16|18|20|21|22)$/;

function isCircleTask(n) {
  if (!html(n) || n.tagName !== 'article' || attrs(n).class !== 'v2-task ms-task'
      || n.parentNode?.tagName !== 'section' || attrs(n.parentNode).id !== 'practice') return false;
  const blocks = parts(n);
  const [label, question, answer] = blocks;
  const [summary, ...solution] = answer ? parts(answer) : [];
  return blocks.length === 3 && html(label) && label.tagName === 'div' && attrs(label).class === 'v2-task-label'
    && html(question) && question.tagName === 'p' && html(answer) && answer.tagName === 'details'
    && attrs(answer).class === 'v2-answer ms-answer' && Object.keys(attrs(answer)).length === 1
    && html(summary) && summary.tagName === 'summary' && Object.keys(attrs(summary)).length === 0
    && children(summary).every(node => node.nodeName === '#text') && /^Разбор задания (?:[1-9]|1[0-2])$/u.test(text(summary))
    && solution.length > 0;
}

function circleSectionHeading(section) {
  const [wrapper] = parts(section);
  if (!html(wrapper) || wrapper.tagName !== 'div' || attrs(wrapper).class !== 'v2-section-heading'
      || Object.keys(attrs(wrapper)).length !== 1) return null;
  const blocks = parts(wrapper);
  const [label, heading] = blocks;
  if (blocks.length !== 2 || !html(label) || label.tagName !== 'span'
      || attrs(label).class !== 'ms-section-number' || Object.keys(attrs(label)).length !== 1
      || !/^(?:0[1-9]|10|✓)$/u.test(text(label)) || !html(heading) || heading.tagName !== 'h2'
      || Object.keys(attrs(heading)).length !== 0
      || [...children(label), ...children(heading)].some(node => node.nodeName !== '#text')) {
    throw Error('Unsupported number circle section heading');
  }
  return { heading, nodes: children(section).filter(node => node !== wrapper) };
}

function convert(n) {
  if (n.nodeName === '#text') return { kind: 'text', text: n.value };
  if (n.nodeName === '#comment') return null;
  if (!n.tagName) throw Error(`Unsupported source node: ${n.nodeName}`);
  const a = attrs(n);
  if (n.tagName === 'linearGradient' || n.tagName === 'stop') {
    const gradient = n.tagName === 'linearGradient';
    const allowed = gradient ? ['id', 'x1', 'y1', 'x2', 'y2'] : ['offset', 'stop-color'];
    if (n.namespaceURI !== 'http://www.w3.org/2000/svg'
        || n.parentNode?.tagName !== (gradient ? 'defs' : 'linearGradient')
        || Object.keys(a).some(key => !allowed.includes(key))) throw Error('Unsupported source SVG gradient');
    if (gradient) {
      if (!/^[A-Za-z0-9_-]+$/.test(a.id ?? '') || a.id !== a.id.trim()
          || ['x1', 'y1', 'x2', 'y2'].some(key => key in a && !['0', '1'].includes(a[key]))
          || children(n).some(c => c.nodeName !== '#comment' && !(c.nodeName === '#text' && !c.value.trim())
            && c.tagName !== 'stop')) throw Error('Unsupported source linear gradient');
    } else if (!['0%', '100%'].includes(a.offset)
        || !/^#[0-9A-Fa-f]{6}$/.test(a['stop-color'] ?? '') || a['stop-color'] !== a['stop-color'].trim()
        || children(n).some(c => c.nodeName !== '#comment' && !(c.nodeName === '#text' && !c.value.trim()))) {
      throw Error('Unsupported source gradient stop');
    }
  }
  if (['ms-nav', 'ms-lesson-nav', 'ms-quadratic-number', 'ms-next-topic'].some(name => has(n, name))) return null;
  if (n.tagName === 'div' && a.id === 'ms-power-lab-935' && has(n, 'ms-power-lab')) {
    return { kind: 'interactive', name: 'power-positive', id: a.id };
  }
  if (n.tagName === 'div' && a.id === 'ms-negative-power-lab-936' && has(n, 'ms-negative-lab')) {
    return { kind: 'interactive', name: 'power-negative', id: a.id };
  }
  if (html(n) && n.tagName === 'div' && a.id === 'power-lab-v2' && a.class === 'ms-graph-lab'
      && a['data-ms-power-lab'] === 'true' && Object.keys(a).length === 3) {
    return { kind: 'interactive', name: 'power-rational', id: a.id };
  }
  if (html(n) && n.tagName === 'div' && a.id === 'circle-lab-v2' && a.class === 'v2-lab'
      && Object.keys(a).length === 2 && n.parentNode?.tagName === 'section'
      && attrs(n.parentNode).id === 'interactive-lab') {
    return { kind: 'interactive', name: 'number-circle', id: a.id };
  }
  if (a.id === 'ms-quadratic-lab-660') return { kind: 'interactive', name: 'quadratic', id: a.id };
  if (a.id === 'ms-linear-lab-723') {
    // Instructional prose remains document content, outside the replacement UI.
    return { kind: 'element', tag: 'div', attrs: {}, children: [
      { kind: 'interactive', name: 'linear', id: a.id },
      ...children(n).filter(c => c.tagName === 'p').map(convert),
    ] };
  }
  if (n.tagName === 'code' && n.namespaceURI !== 'http://www.w3.org/1999/xhtml') throw Error('Unsupported source code namespace');
  if (n.tagName === 'img' && n.namespaceURI !== 'http://www.w3.org/1999/xhtml') throw Error('Unsupported source image namespace');
  const circleTask = isCircleTask(n);
  const tag = circleTask ? 'div' : staticSourceTag(n);
  if (!tags.has(tag) && !isAuthoredFigure(n)
      && !(tag === 'figcaption' && isAuthoredFigure(n.parentNode))) throw Error(`Unsupported source tag: ${n.tagName}`);
  for (const [key, value] of Object.entries(a)) {
    const svgAttribute = key === 'marker-start'
      ? n.tagName === 'line' && /^url\(#[A-Za-z0-9_-]+\)$/.test(value)
      : key === 'dy' ? n.tagName === 'tspan' && /^[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)$/.test(value) && Number.isFinite(Number(value))
      : key === 'font-style' ? n.namespaceURI === 'http://www.w3.org/2000/svg' && n.tagName === 'text' && value === 'italic'
      : key === 'fill-opacity' ? n.namespaceURI === 'http://www.w3.org/2000/svg' && n.tagName === 'polygon'
        && /^(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)$/.test(value) && value === value.trim()
        && Number.isFinite(Number(value)) && Number(value) >= 0 && Number(value) <= 1
      : key === 'data-net-face' ? n.namespaceURI === 'http://www.w3.org/2000/svg' && n.tagName === 'rect' && value === 'true'
      : key === 'data-hidden-edges' && n.tagName === 'path' && value === 'true';
    const imageAttribute = n.tagName === 'img' && (key === 'src' || key === 'alt');
    const gradientAttribute = n.tagName === 'stop' && (key === 'offset' || key === 'stop-color');
    const staticAttribute = key === 'tabindex' ? isNamedTableRegion(n, a)
      : key === 'data-angle-step' ? svg(n) && tag === 'circle' && circleSteps.test(value) && value === value.trim()
      : svg(n) && tag === 'path' && (key === 'data-function' ? !!value.trim()
        : key === 'data-power' && /^(?:2|3),1$/.test(value));
    if (!attributes.has(key.toLowerCase()) && !key.startsWith('aria-') && !svgAttribute && !imageAttribute && !gradientAttribute && !staticAttribute) throw Error(`Unsupported attribute: ${key}`);
    if (/^on/i.test(key) || /(?:javascript:|expression\(|@import|url\(\s*[^#])/i.test(value)) throw Error('Active source markup');
    if (key === 'href' && !/^(?:\/(?!\/)|#|https:\/\/)/.test(value)) throw Error('Unsupported source link');
    if (key === 'src' && !safeImageUrl(value)) throw Error('Unsupported source image URL');
  }
  if (has(n, 'ms-task')) {
    const answer = children(n).find(c => has(c, 'ms-answer'));
    if (!answer) throw Error('Missing self-check answer');
    const summary = children(answer).find(c => c.tagName === 'summary');
    return { kind: 'selfCheck', attrs: a, disclosure: circleTask || text(summary).includes('решение') ? 'solution' : 'answer',
      question: children(n).filter(c => c !== answer).map(convert).filter(Boolean),
      answer: children(answer).filter(c => c !== summary).map(convert).filter(Boolean) };
  }
  const kind = n.tagName === 'p' ? 'paragraph' : has(n, 'ms-note') || has(n, 'ms-rule-box') ? 'note'
    : has(n, 'ms-example') || has(n, 'ms-math-box') ? 'example' : n.tagName === 'table' ? 'table' : n.tagName === 'svg' ? 'figure' : 'element';
  return { kind, tag, attrs: a, children: children(n).map(convert).filter(Boolean) };
}
function isPracticeSelfCheck(section, title, heading) {
  if (attrs(section).id !== 'practice' || title !== 'Проверьте себя') return false;
  const blocks = parts(section).filter(node => node !== heading);
  const tasks = blocks.filter(node => has(node, 'ms-task'));
  if (!tasks.length || blocks.some(node => !has(node, 'ms-task') && node.tagName !== 'p')
      || tasks.some(task => {
        const content = parts(task);
        const answer = content.at(-1);
        const [summary, ...solution] = answer ? parts(answer) : [];
        return !html(task) || task.tagName !== 'div' || content.length < 2
          || content.filter(node => has(node, 'ms-answer')).length !== 1
          || !html(answer) || answer.tagName !== 'details' || !has(answer, 'ms-answer')
          || Object.keys(attrs(answer)).some(key => key !== 'class')
          || !html(summary) || summary.tagName !== 'summary' || Object.keys(attrs(summary)).length !== 0
          || !text(summary).trim() || !solution.length;
      })) throw Error('Unsupported practice self-check structure');
  return true;
}

function nestedLaboratoryHeading(n) {
  const parts = node => children(node).filter(c => c.nodeName !== '#comment' && !(c.nodeName === '#text' && !c.value.trim()));
  const exact = (node, tag, className) => node?.tagName === tag
    && node.namespaceURI === 'http://www.w3.org/1999/xhtml'
    && Object.keys(attrs(node)).length === (className === undefined ? 0 : 1)
    && attrs(node).class === className;
  const [header] = parts(n);
  const headerParts = header ? parts(header) : [];
  const [intro, badge] = headerParts;
  const introParts = intro ? parts(intro) : [];
  const [heading, goal, equipment] = introParts;
  const badgeParts = badge ? parts(badge) : [];
  if (attrs(n).id !== 'theory' || attrs(n).class !== 'ms-section' || Object.keys(attrs(n)).length !== 2
      || parts(n).length !== 1 || !exact(header, 'div', 'ms-lab-header ms-lab-header--overview')
      || headerParts.length !== 2 || !exact(intro, 'div') || introParts.length !== 3
      || !exact(heading, 'h2') || cleanSectionTitle(text(heading)) !== 'Цель и оборудование'
      || children(heading).some(c => c.nodeName !== '#text' && c.nodeName !== '#comment')
      || !exact(goal, 'p', 'ms-text') || !exact(equipment, 'div', 'ms-chip-row')
      || parts(equipment).length !== 4 || parts(equipment).some(c => !exact(c, 'span', 'ms-chip'))
      || !exact(badge, 'div', 'ms-lab-badge') || badgeParts.length !== 2
      || !exact(badgeParts[0], 'strong') || text(badgeParts[0]).trim() !== '50'
      || !exact(badgeParts[1], 'span')) throw Error('Unreviewed nested laboratory heading structure');
  const introCopy = { ...intro, childNodes: children(intro).filter(c => c !== heading) };
  const headerCopy = { ...header, childNodes: children(header).map(c => c === intro ? introCopy : c) };
  return { heading, nodes: children(n).map(c => c === header ? headerCopy : c) };
}
function convertRootFigure(n) {
  const parts = node => children(node).filter(c => c.nodeName !== '#comment' && !(c.nodeName === '#text' && !c.value.trim()));
  const exact = (node, tag, className) => node?.tagName === tag
    && node.namespaceURI === 'http://www.w3.org/1999/xhtml'
    && Object.keys(attrs(node)).length === 1 && attrs(node).class === className;
  const [caption, wrapper] = parts(n);
  const drawing = wrapper && parts(wrapper);
  if (!exact(n, 'div', 'ms-figure') || parts(n).length !== 2
      || !exact(caption, 'p', 'ms-figure-title') || !text(caption).trim()
      || children(caption).some(c => c.nodeName !== '#text' && c.nodeName !== '#comment')
      || !exact(wrapper, 'div', 'ms-svg-wrap') || drawing.length !== 1
      || drawing[0].tagName !== 'svg' || drawing[0].namespaceURI !== 'http://www.w3.org/2000/svg') {
    throw Error('Unreviewed lesson root figure structure');
  }
  return convert(n);
}
export function convertLesson(directory) {
  const meta = JSON.parse(readFileSync(join(directory, 'lesson.json'), 'utf8')).page;
  const root = children(parseFragment(readFileSync(join(directory, 'body.html'), 'utf8'))).find(n => has(n, 'ms-lesson-page'));
  if (!root) throw Error('Missing authored lesson root');
  const hero = children(root).find(n => has(n, 'ms-hero'));
  let afterSelfCheck = false;
  let lastSection;
  const sections = [];
  for (const n of children(root)) {
    // Самопроверка целиком завершает материал, независимо от названий следующих блоков.
    if (afterSelfCheck) break;
    if (!n.tagName || n === hero || has(n, 'ms-lesson-toc')) continue;
    if (n.tagName === 'div' && has(n, 'ms-figure')) {
      const blocks = children(root).filter(c => c.nodeName !== '#comment' && !(c.nodeName === '#text' && !c.value.trim()));
      const index = blocks.indexOf(n);
      const previous = blocks[index - 1], next = blocks[index + 1];
      if (previous?.tagName !== 'section' || next?.tagName !== 'section'
          || previous !== lastSection || !sections.length) {
        throw Error('Root figure must follow a retained section and precede a section');
      }
      sections.at(-1).nodes.push(convertRootFigure(n));
      continue;
    }
    if (n.tagName !== 'section') throw Error(`Unreviewed lesson root block: ${n.tagName}`);
    let heading = children(n).find(c => c.tagName === 'h2');
    let sectionNodes = children(n).filter(c => c !== heading);
    if (!heading && meta.slug === '10-klass-chislovaya-okruzhnost-2-0') {
      const nested = circleSectionHeading(n);
      if (nested) ({ heading, nodes: sectionNodes } = nested);
    }
    if (!heading && attrs(n).id === 'theory') {
      const laboratory = nestedLaboratoryHeading(n);
      heading = laboratory.heading;
      sectionNodes = laboratory.nodes;
    }
    if (!heading || !attrs(n).id) throw Error('Missing section heading or anchor');
    const title = cleanSectionTitle(text(heading));
    if (isPrerequisiteSection(title)) continue;
    const selfCheck = isSelfCheckSection(title) || isPracticeSelfCheck(n, title, heading);
    sections.push({ id: attrs(n).id, title: selfCheck ? 'Самопроверка' : title,
      nodes: normalizeMathNotation(sectionNodes.map(convert).filter(Boolean)) });
    lastSection = n;
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
