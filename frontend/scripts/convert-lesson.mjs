// Explicit build-time conversion. Unknown source markup is a review error.
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
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
tags.add('ellipse');
function safeImageUrl(value) {
  // Match the backend URL policy, rejecting controls before trimming as well.
  if (/[\\\u0000-\u001f\u007f-\u009f]/.test(value)) return false;
  const url = value.trim();
  if (/^(?:javascript:|data:|vbscript:|\/\/)/i.test(url)) return false;
  return /^(?:\/|#|https:\/\/|mailto:)/i.test(url);
}

// Closed snapshots of the two reviewed lab containers, not of their sections.
// Include text, attributes, namespaces and child order so new instructional
// content cannot silently disappear behind an interactive replacement. Only
// comments, indentation and attribute order are insignificant for this review.
function gradeEightLabSnapshot(n) {
  if (n.nodeName === '#comment') return null;
  if (n.nodeName === '#text') {
    const value = n.value.replace(/\s+/g, ' ').trim();
    return value ? ['text', value] : null;
  }
  return [n.namespaceURI, n.tagName,
    Object.entries(attrs(n)).sort(([a], [b]) => a.localeCompare(b)),
    children(n).map(gradeEightLabSnapshot).filter(value => value !== null)];
}
// Authored transcription of closed, reviewed grade-eight sources only. This is
// not a general expression parser: parentheses and sup/sub in the source own
// grouping; no operations are evaluated, simplified or inferred from display.
const gradeEightAuthoredMath = new Map([
  ["8-klass/algebra/funkciya-modulya-i-kvadratnogo-kornya/modul-dejstvitelnogo-chisla-i-ego-geometricheskij-smysl", "8bf93305d532132dc7adc5467e71b50acd4bb4050cfd532deaaa789b06280355"],
  ["8-klass/geometriya/chetyrehugolniki/mnogougolniki-i-parallelogramm-opredeleniya-svojstva-i-priznaki", "ee20d002851ca092389c5f5c4461740f9124591717509e6286aaa13ff51536c1"],
  ["8-klass/geometriya/chetyrehugolniki/trapecziya-srednyaya-liniya-trapeczii", "95f7168b640cfe4ee85a68b15f2d03c98cefef7a5a4f0f5396507540e74ab81c"],
  ["8-klass/algebra/algebraicheskie-drobi/ponyatie-algebraicheskoj-drobi", "adc58f40393f2eabf9a2cfee257623cb812d84face507beb23181ebe0b781f6e"],
  ["8-klass/algebra/algebraicheskie-drobi/primenenie-osnovnogo-svojstva-algebraicheskoj-drobi", "d50ca6fe837f1b06ba9feb41405498dbed0b5ebadb1570c08c2787574e21f884"],
  ["8-klass/algebra/algebraicheskie-drobi/kak-skladyvat-i-vychitat-algebraicheskie-drobi-s-ravnymi-znamenatelyami", "f2bcd25f04eed40045a8eb8f6386318fcd1dcc0aec48a4ddf628ca070b5cf912"],
  ["8-klass/algebra/algebraicheskie-drobi/kak-skladyvat-i-vychitat-algebraicheskie-drobi-s-raznymi-znamenatelyami", "05ed378b0f597565aa3e335f818d40d7d325b3e242f20a893e17f84a14377954"],
  ["8-klass/algebra/algebraicheskie-drobi/kak-umnozhat-delit-i-vozvodit-v-stepen-algebraicheskie-drobi", "1740e30e2eab30b2da0033d995fe16e5b5a083bb6a6f4e81e9cee9edfe790cdf"],
  ["8-klass/algebra/algebraicheskie-drobi/uproshhenie-raczionalnyh-vyrazhenij", "263b578c1d26c2ba41d618ea386dc16bc8fc6e045972bde74cd8193e3d1aae10"],
  ["8-klass/algebra/algebraicheskie-drobi/reshenie-raczionalnyh-uravnenij", "1882f039e3e9d217636b9ec38f0616f0a6cb5f4253dc256d6a7d5373c7ad4124"],
  ["8-klass/algebra/dejstvitelnye-chisla/ponyatie-kvadratnogo-kornya", "15ff6e4be19d21e0dc558d81d999f39c4845f719054f83af09a5baf6be154230"],
  ["8-klass/algebra/neravenstva/ponyatie-stepeni-s-otriczatelnym-czelym-pokazatelem", "45b949a1444b6276e4e5fa8aed0b1a6a12ff7d583688caf58ffa397540a62578"],
  ["8-klass/veroyatnost-i-statistika/opisatelnaya-statistika-rasseivanie-dannyh/otkloneniya-dispersiya-chislovogo-nabora", "ac52153ed1bc30f5306327c7348ae9708d2b3644671e0e4af397d91ad44b91c9"],
]);
function transcribeGradeEightMath(root, meta) {
  const identity = [meta.grade, meta.subject, meta.section, meta.slug].join('/');
  const digest = gradeEightAuthoredMath.get(identity);
  if (!digest) return;
  if (createHash('sha256').update(JSON.stringify(gradeEightLabSnapshot(root))).digest('hex') !== digest) {
    throw Error('Unreviewed grade-eight authored mathematics; review the source before transcribing it');
  }
  const mathNode = (tagName, childNodes = [], attributes = {}) => {
    const node = { nodeName: tagName, tagName, namespaceURI: 'http://www.w3.org/1998/Math/MathML',
      attrs: Object.entries(attributes).map(([name, value]) => ({ name, value })), childNodes };
    childNodes.forEach(child => { child.parentNode = node; });
    return node;
  };
  const token = (tag, value) => mathNode(tag, [{ nodeName: '#text', value }]);
  const row = values => mathNode('mrow', values);
  function leaf(value) {
    const nodes = [];
    const tokens = value.match(/\d+(?:[.,]\d+)?|x\u0304|[A-Za-z]|[()+.·−…√]/gu) ?? [];
    if (tokens.join('') !== value.replace(/\s+/g, '')) throw Error('Unreviewed authored mathematical leaf');
    for (let i = 0; i < tokens.length; i++) {
      const part = tokens[i];
      if (part === '√') {
        const radicand = tokens[++i];
        if (!['49', '64'].includes(radicand)) throw Error('Unreviewed authored radical');
        nodes.push(mathNode('msqrt', [token('mn', radicand)]));
      } else nodes.push(token(/^\d/.test(part) ? 'mn' : /^[A-Za-z]/.test(part) ? 'mi' : 'mo', part));
    }
    return nodes;
  }
  function scriptBase(values) {
    const last = values.pop();
    if (!last) throw Error('Authored script has no base');
    if (last.tagName !== 'mo' || text(last) !== ')') return last;
    const group = [last];
    let depth = 1;
    while (values.length) {
      const node = values.pop(); group.unshift(node);
      if (node.tagName === 'mo' && text(node) === ')') depth++;
      if (node.tagName === 'mo' && text(node) === '(' && --depth === 0) return row(group);
    }
    throw Error('Unbalanced authored script base');
  }
  function sequence(source) {
    const result = [];
    for (const child of children(source)) {
      if (child.nodeName === '#comment') continue;
      if (child.nodeName === '#text') { result.push(...leaf(child.value)); continue; }
      if (child.tagName === 'sup' || child.tagName === 'sub') {
        if (Object.keys(attrs(child)).length) throw Error('Unreviewed authored script attributes');
        const base = scriptBase(result);
        result.push(mathNode(child.tagName === 'sup' ? 'msup' : 'msub', [base, row(sequence(child))]));
      } else if (has(child, 'ms-frac')) result.push(fraction(child));
      else if (has(child, 'ms-abs')) result.push(absolute(child));
      else if (child.tagName === 'span' && attrs(child).class === 'ms-power'
          && Object.keys(attrs(child)).length === 1) result.push(...sequence(child));
      else if (child.namespaceURI === 'http://www.w3.org/1998/Math/MathML') {
        result.push(child.tagName === 'math' ? row(children(child)) : child);
      } else throw Error('Unreviewed authored mathematical structure');
    }
    return result;
  }
  function fraction(source) {
    const parts = children(source).filter(n => n.nodeName !== '#comment' && !(n.nodeName === '#text' && !n.value.trim()));
    // One reviewed A^n/B^n formula ends with sentence punctuation inside the
    // legacy wrapper. Keep the period after the fraction, never in its denominator.
    const trailingPeriod = parts.length === 3 && parts[2].nodeName === '#text' && parts[2].value.trim() === '.';
    if (trailingPeriod) parts.pop();
    const [numerator, denominator] = parts;
    if (source.tagName !== 'span' || attrs(source).class !== 'ms-frac'
        || Object.keys(attrs(source)).length !== 1 || parts.length !== 2
        || parts.some(n => n.tagName !== 'span' || Object.keys(attrs(n)).length !== 1)
        || !['ms-num', 'ms-frac-num'].includes(attrs(numerator).class)
        || !['ms-den', 'ms-frac-den'].includes(attrs(denominator).class)) {
      throw Error('Unreviewed authored fraction structure');
    }
    const top = sequence(numerator), bottom = sequence(denominator);
    if (!top.length || !bottom.length) throw Error('Empty authored fraction part');
    const value = mathNode('mfrac', [row(top), row(bottom)]);
    return trailingPeriod ? row([value, token('mo', '.')]) : value;
  }
  function absolute(source) {
    const parts = children(source).filter(n => n.nodeName !== '#comment' && !(n.nodeName === '#text' && !n.value.trim()));
    if (attrs(source).class !== 'ms-abs' || Object.keys(attrs(source)).length !== 1
        || parts.length !== 1 || attrs(parts[0]).class !== 'ms-abs-value'
        || Object.keys(attrs(parts[0])).length !== 1) throw Error('Unreviewed authored absolute value');
    return row([token('mo', '|'), ...sequence(parts[0]), token('mo', '|')]);
  }
  function visit(parent) {
    parent.childNodes = children(parent).map(child => {
      if (has(child, 'ms-frac') || has(child, 'ms-abs') || has(child, 'ms-power')) {
        const value = has(child, 'ms-frac') ? fraction(child)
          : has(child, 'ms-abs') ? absolute(child) : row(sequence(child));
        const replacement = mathNode('math', [value],
          { class: 'lesson-math', display: 'inline' });
        replacement.parentNode = parent;
        return replacement;
      }
      if (child.tagName !== 'svg' && child.tagName !== 'math') visit(child);
      return child;
    });
  }
  visit(root);
}
function gradeEightCourseSelfCheck(root, meta) {
  if (meta.slug !== 'obobshhenie-sistematizacziya-znanij-2') return null;
  const section = children(root).find(n => attrs(n).id === 'lesson-section-8');
  if (meta.grade !== '8-klass' || meta.subject !== 'veroyatnost-i-statistika'
      || meta.section !== 'obobshhenie-sistematizaciya-znanij'
      || createHash('sha256').update(JSON.stringify(gradeEightLabSnapshot(root))).digest('hex')
        !== 'f834b657c345662003fdcaf14b7593ce8145dcee8cddf6dafee32a3f34ac2f25'
      || section?.tagName !== 'section'
      || text(children(section).find(n => n.tagName === 'h2')).trim() !== 'Самопроверка по всему курсу'
      || children(section).filter(n => has(n, 'ms-task')).length !== 8) {
    throw Error('Unreviewed grade-eight course self-check');
  }
  // The migration standard ends material at self-check and removes all legacy
  // navigation. The following lesson-section-9 and root ms-nav are therefore
  // excluded by the existing afterSelfCheck boundary, not a root-div allowlist.
  return section;
}
function reviewedGradeEightLab(root, sectionId, labId, digest, name) {
  const find = n => [n, ...children(n).flatMap(find)].filter(node => attrs(node).id === labId);
  const matches = find(root);
  const source = matches[0];
  const section = source?.parentNode;
  if (matches.length !== 1 || source.tagName !== 'div'
      || source.namespaceURI !== 'http://www.w3.org/1999/xhtml'
      || section?.tagName !== 'section' || section.parentNode !== root
      || attrs(section).id !== sectionId || attrs(section).class !== 'ms-section'
      || createHash('sha256').update(JSON.stringify(gradeEightLabSnapshot(source))).digest('hex') !== digest) {
    throw Error(`Unreviewed ${name} lab structure/content (${labId}); review its preservation map before replacing it`);
  }
  return { source, node: { kind: 'interactive', name, id: labId } };
}
function gradeEightLessonLab(root, meta) {
  if (meta.slug === 'funkcziya-kvadratnogo-kornya-eyo-svojstva-i-grafik') {
    if (meta.grade !== '8-klass' || meta.subject !== 'algebra'
        || meta.section !== 'funkciya-modulya-i-kvadratnogo-kornya') throw Error('Square-root lesson identity mismatch');
    return reviewedGradeEightLab(root, 'theory', 'ms-root-lab-832',
      'a77feb84ece1835ec6da623c52f419bd8e9e76c0d8a51c41ee4d8d6209183169', 'square-root');
  }
  if (meta.slug === 'funkcziya-y-k-x-i-eyo-svojstva-giperbola') {
    if (meta.grade !== '8-klass' || meta.subject !== 'algebra'
        || meta.section !== 'kvadratichnaya-funkciya-y-ax2-funkciya-y-k-x') throw Error('Hyperbola lesson identity mismatch');
    return reviewedGradeEightLab(root, 'interactive-lab', 'ms-hyperbola-lab-621',
      '4c4db9ebab4f7f79c4d13bd07e739a0fdad163b0df45a2718e477cc5c49b8b8a', 'hyperbola');
  }
  return null;
}
// Browser scheduling hints are not lesson content. Omit them only on the
// fingerprinted PNG of this lesson; all other image attributes use convert().
function normalizeGradeEightCircleImage(root, meta) {
  if (meta.slug !== 'czentralnye-i-vpisannye-ugly-dugi-hordy-sekushhie-i-kasatelnye') return;
  if (meta.grade !== '8-klass' || meta.subject !== 'geometriya'
      || meta.section !== 'okruzhnost') throw Error('Circle angles lesson identity mismatch');
  const find = n => [n, ...children(n).flatMap(find)].filter(node => node.tagName === 'img');
  const images = find(root);
  const image = images[0];
  const wrapper = image?.parentNode;
  const figure = wrapper?.parentNode;
  const section = figure?.parentNode;
  if (images.length !== 1 || image.namespaceURI !== 'http://www.w3.org/1999/xhtml'
      || wrapper?.tagName !== 'div' || attrs(wrapper).class !== 'ms-image-wrap'
      || figure?.tagName !== 'div' || attrs(figure).class !== 'ms-figure'
      || section?.tagName !== 'section' || attrs(section).id !== 'lesson-section-5'
      || attrs(section).class !== 'ms-section' || section.parentNode !== root
      || createHash('sha256').update(JSON.stringify(gradeEightLabSnapshot(image))).digest('hex')
        !== 'f9c7b7a235f021588f6a62c5bf81eb46b24fff52051719405a695d21cc8ffbf2') {
    throw Error('Unreviewed circle angles PNG structure/attributes; review the image before normalizing it');
  }
  // Mutate only the fresh parse tree, never the authored body.html file.
  image.attrs = image.attrs.filter(attribute => !['decoding', 'loading'].includes(attribute.name));
}
// Materialize the three CSS-generated labels before the general attribute guard.
// Only this reviewed source identity/container may bypass raw data-label markup.
function gradeEightIrrationalAxis(root, meta) {
  if (meta.slug !== 'ponyatie-irraczionalnogo-chisla') return null;
  if (meta.grade !== '8-klass' || meta.subject !== 'algebra'
      || meta.section !== 'dejstvitelnye-chisla') throw Error('Irrational lesson identity mismatch');
  const find = n => [n, ...children(n).flatMap(find)].filter(node => has(node, 'ms-interval-visual'));
  const matches = find(root);
  const source = matches[0];
  const section = source?.parentNode;
  if (matches.length !== 1 || source.tagName !== 'div'
      || source.namespaceURI !== 'http://www.w3.org/1999/xhtml'
      || section?.tagName !== 'section' || section.parentNode !== root
      || attrs(section).id !== 'lesson-section-5' || attrs(section).class !== 'ms-section-soft'
      || createHash('sha256').update(JSON.stringify(gradeEightLabSnapshot(source))).digest('hex')
        !== '9d4703de6c34133dfec75af27939641b6cbf92d09f3605b3095e3cb185b8ad07') {
    throw Error('Unreviewed irrational number axis structure/content; review labels and positions before replacing it');
  }
  const literal = value => ({ kind: 'text', text: value });
  const element = (tag, children = [], attrs = {}) => ({ kind: 'element', tag, attrs, children });
  const span = (classes, children = []) => element('span', children, { class: classes });
  const axis = children(source).find(n => n.tagName === 'div');
  const marks = children(axis).filter(n => n.tagName === 'span');
  const labels = marks.map(n => attrs(n)['data-label']);
  return { source, node: element('div', [
    element('div', [span('ms-g8-line'), span('ms-g8-tick ms-g8-pos-0'),
      span('ms-g8-point ms-g8-pos-162'), span('ms-g8-tick ms-g8-pos-100')],
    { class: 'ms-g8-plot', 'aria-hidden': 'true' }),
    span('ms-g8-label ms-g8-pos-0', [literal(labels[0])]),
    span('ms-g8-label ms-g8-point-label ms-g8-pos-162', [
      element('math', [element('msqrt', [element('mn', [literal('10')])])],
        { class: 'lesson-math', display: 'inline', 'aria-label': 'квадратный корень из 10' }),
      literal(labels[1].slice('√10'.length)),
    ]),
    span('ms-g8-label ms-g8-pos-100', [literal(labels[2])]),
  ], { class: 'ms-g8-root-axis', role: 'group', 'aria-label': 'Числовая ось от 3 до 4 с отмеченным квадратным корнем из 10' }) };
}
// The reviewed grade-eight figures contain one direct SVG and no caption.
// Keep the authored wrapper; other figure shapes require their own adapter.
function isBareSvgFigure(n) {
  if (n.namespaceURI !== 'http://www.w3.org/1999/xhtml'
      || n.tagName !== 'figure' || attrs(n).class !== 'ms-figure') return false;
  const parts = children(n).filter(c => c.nodeName !== '#comment'
    && !(c.nodeName === '#text' && !c.value.trim()));
  return parts.length === 1 && parts[0].tagName === 'svg'
    && parts[0].namespaceURI === 'http://www.w3.org/2000/svg';
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
  if (n.tagName === 'ellipse' && n.namespaceURI !== 'http://www.w3.org/2000/svg') throw Error('Unsupported source ellipse namespace');
  if (!tags.has(n.tagName) && !isBareSvgFigure(n)) throw Error(`Unsupported source tag: ${n.tagName}`);
  for (const [key, value] of Object.entries(a)) {
    const svgAttribute = key === 'marker-start'
      ? n.tagName === 'line' && /^url\(#[A-Za-z0-9_-]+\)$/.test(value)
      : key === 'dy' ? n.tagName === 'tspan' && /^[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)$/.test(value) && Number.isFinite(Number(value))
      : key === 'font-style' ? n.namespaceURI === 'http://www.w3.org/2000/svg' && n.tagName === 'text' && value === 'italic'
      : key === 'fill-opacity' ? n.namespaceURI === 'http://www.w3.org/2000/svg' && ['polygon', 'circle', 'ellipse', 'path'].includes(n.tagName)
        && /^(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)$/.test(value) && value === value.trim()
        && Number.isFinite(Number(value)) && Number(value) >= 0 && Number(value) <= 1
      : key === 'data-net-face' ? n.namespaceURI === 'http://www.w3.org/2000/svg' && n.tagName === 'rect' && value === 'true'
      : key === 'data-hidden-edges' && n.tagName === 'path' && value === 'true';
    const imageAttribute = n.tagName === 'img' && (key === 'src' || key === 'alt');
    const gradientAttribute = n.tagName === 'stop' && (key === 'offset' || key === 'stop-color');
    if (!attributes.has(key.toLowerCase()) && !key.startsWith('aria-') && !svgAttribute && !imageAttribute && !gradientAttribute) throw Error(`Unsupported attribute: ${key}`);
    if (/^on/i.test(key) || /(?:javascript:|expression\(|@import|url\(\s*[^#])/i.test(value)) throw Error('Active source markup');
    if (key === 'href' && !/^(?:\/(?!\/)|#|https:\/\/)/.test(value)) throw Error('Unsupported source link');
    if (key === 'src' && !safeImageUrl(value)) throw Error('Unsupported source image URL');
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
  const courseSelfCheck = gradeEightCourseSelfCheck(root, meta);
  transcribeGradeEightMath(root, meta);
  normalizeGradeEightCircleImage(root, meta);
  const gradeEightLab = gradeEightLessonLab(root, meta);
  const irrationalAxis = gradeEightIrrationalAxis(root, meta);
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
    if (!heading && attrs(n).id === 'theory') {
      const laboratory = nestedLaboratoryHeading(n);
      heading = laboratory.heading;
      sectionNodes = laboratory.nodes;
    }
    if (!heading || !attrs(n).id) throw Error('Missing section heading or anchor');
    const title = cleanSectionTitle(text(heading));
    if (isPrerequisiteSection(title)) continue;
    const selfCheck = isSelfCheckSection(title) || n === courseSelfCheck;
    sections.push({ id: attrs(n).id, title: selfCheck ? 'Самопроверка' : title,
      nodes: normalizeMathNotation(sectionNodes.map(source => source === gradeEightLab?.source
        ? gradeEightLab.node : source === irrationalAxis?.source
          ? irrationalAxis.node : convert(source)).filter(Boolean)) });
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
